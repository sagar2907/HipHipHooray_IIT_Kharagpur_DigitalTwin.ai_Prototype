"""SQLite store for everything the running twin produces.

Why a database and not more JSONL: the questions we actually want to ask are
relational. "Which stations hold the line across every shift we have ever
run", "what fraction of forming warnings named a dark station", "how does
loop latency move with shift length" - those are one SQL line each and a
parsing chore against flat files. It is also one file to hand over, and it
survives a restart, which the in-memory ledger did not.

Design notes that matter:

* WAL mode, so the analysis side can read while the loop is still writing.
  Without it a long-running query blocks the plant loop, which is exactly
  backwards.
* One row per (frame, station) in `rankings`. That is the expensive table and
  the useful one - it is what makes constraint-occupancy and evidence
  queries possible after the fact.
* A `sessions` row per server start, so numbers can always be traced back to
  the run, speed and calibration that produced them. Mixing sessions
  silently would be the sort of provenance failure this project keeps
  deleting.
* Writes are batched and committed per tick. At a few hundred milliseconds
  per tick that is far below anything the loop notices.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS sessions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at    REAL,
  started_iso   TEXT,
  run           TEXT,
  speed         REAL,
  step_s        INTEGER,
  continuous    INTEGER,
  calibrated    INTEGER,
  ece_before    REAL,
  ece_after     REAL,
  base_rate     REAL,
  note          TEXT
);

CREATE TABLE IF NOT EXISTS frames (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    INTEGER,
  wall          REAL,
  t_s           INTEGER,
  shift_no      INTEGER,
  run           TEXT,
  clock         TEXT,
  constraint_st TEXT,
  margin        REAL,
  confidence    REAL,
  calibrated    INTEGER,
  cross_check   INTEGER,
  units_out     INTEGER,
  moves         INTEGER,
  persist_min   REAL,
  presc_station TEXT,
  presc_sig     TEXT,
  presc_action  TEXT,
  compute_ms    REAL,
  status        TEXT
);
CREATE INDEX IF NOT EXISTS ix_frames_session ON frames(session_id);
CREATE INDEX IF NOT EXISTS ix_frames_constraint ON frames(constraint_st);

CREATE TABLE IF NOT EXISTS rankings (
  frame_id      INTEGER,
  rank          INTEGER,
  station       TEXT,
  effective_ct  REAL,
  proc_time     REAL,
  availability  REAL,
  blocked       REAL,
  starved       REAL,
  cusum         REAL,
  units         INTEGER,
  provenance    TEXT
);
CREATE INDEX IF NOT EXISTS ix_rank_frame ON rankings(frame_id);
CREATE INDEX IF NOT EXISTS ix_rank_station ON rankings(station);

CREATE TABLE IF NOT EXISTS forming (
  frame_id      INTEGER,
  station       TEXT,
  minutes       REAL,
  dark          INTEGER
);
CREATE INDEX IF NOT EXISTS ix_forming_frame ON forming(frame_id);

CREATE TABLE IF NOT EXISTS alerts (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    INTEGER,
  at_s          REAL,
  shift_no      INTEGER,
  run           TEXT,
  station       TEXT,
  kind          TEXT,
  confidence    REAL,
  detail        TEXT,
  margin_s      REAL,
  evidence      TEXT,
  persistence_min REAL,
  action        TEXT,
  cost_vehicles REAL,
  cost_json     TEXT,
  outcome       TEXT
);
CREATE INDEX IF NOT EXISTS ix_alerts_session ON alerts(session_id);

CREATE TABLE IF NOT EXISTS shifts (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    INTEGER,
  shift_no      INTEGER,
  run           TEXT,
  units_out     INTEGER,
  constraint_moves INTEGER,
  alerts_total  INTEGER,
  suppressed    INTEGER,
  confirmed     INTEGER,
  overridden    INTEGER,
  precision_    REAL,
  ended_iso     TEXT
);

CREATE TABLE IF NOT EXISTS tool_assessments (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    INTEGER,
  at_s          INTEGER,
  shift_no      INTEGER,
  run           TEXT,
  station       TEXT,
  tool_id       TEXT,
  alarm         INTEGER,
  cusum         REAL,
  onset_t_s     REAL,
  classification TEXT,
  action        TEXT,
  contained_total INTEGER,
  contained_on_line INTEGER,
  contained_completed INTEGER,
  stop_decision TEXT,
  channels      TEXT
);
CREATE INDEX IF NOT EXISTS ix_tools_session ON tool_assessments(session_id);
"""


class Store:
    """Append-only SQLite store for a running loop."""

    def __init__(self, path: str, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        self.session_id = None
        self.n_frames = 0
        self.n_alerts = 0
        self.n_shifts = 0
        self.n_tools = 0
        self._alerts_written = 0
        self.db = None
        if not enabled:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # check_same_thread=False: the driver task and request handlers live on
        # the same event loop but not necessarily the same thread.
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(SCHEMA)
        self.db.commit()

    # ------------------------------------------------------------- session
    def open_session(self, run: str, speed: float, step_s: int,
                     continuous: bool, calibration: dict | None,
                     base_rate: float, note: str = "") -> int | None:
        if not self.enabled:
            return None
        cal = calibration or {}
        cur = self.db.execute(
            "INSERT INTO sessions (started_at, started_iso, run, speed, step_s,"
            " continuous, calibrated, ece_before, ece_after, base_rate, note)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), time.strftime("%Y-%m-%dT%H:%M:%S"), run, speed,
             step_s, int(continuous), int(bool(calibration)),
             cal.get("ece_before"), cal.get("ece_after"), base_rate, note))
        self.db.commit()
        self.session_id = cur.lastrowid
        return self.session_id

    # -------------------------------------------------------------- frames
    def frame(self, f: dict) -> None:
        if not self.enabled or f.get("shift_change") or f.get("done"):
            return
        p = f.get("prescription") or {}
        cur = self.db.execute(
            "INSERT INTO frames (session_id, wall, t_s, shift_no, run, clock,"
            " constraint_st, margin, confidence, calibrated, cross_check,"
            " units_out, moves, persist_min, presc_station, presc_sig,"
            " presc_action, compute_ms, status)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (self.session_id, time.time(), f.get("t_s"), f.get("shift_no"),
             f.get("run"), f.get("clock"), f.get("constraint"), f.get("margin"),
             f.get("confidence"), int(bool(f.get("confidence_is_calibrated"))),
             None if f.get("cross_check_agrees") is None
             else int(bool(f.get("cross_check_agrees"))),
             f.get("units_out"), f.get("shifts_so_far"),
             f.get("persistence_min"), p.get("station"), p.get("signature"),
             p.get("action"), f.get("compute_ms"), f.get("status")))
        fid = cur.lastrowid

        rows = [(fid, i, r["station"], r["effective_ct"], r["proc_time"],
                 r["availability"], r["blocked"], r["starved"], r["cusum"],
                 r["units"], r["provenance"])
                for i, r in enumerate(f.get("ranking") or [])]
        if rows:
            self.db.executemany(
                "INSERT INTO rankings (frame_id, rank, station, effective_ct,"
                " proc_time, availability, blocked, starved, cusum, units,"
                " provenance) VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)

        fm = [(fid, x["station"], x["minutes"], int(bool(x.get("dark"))))
              for x in (f.get("forming") or [])]
        if fm:
            self.db.executemany(
                "INSERT INTO forming (frame_id, station, minutes, dark)"
                " VALUES (?,?,?,?)", fm)

        self.db.commit()
        self.n_frames += 1

    # -------------------------------------------------------------- alerts
    def alerts(self, ledger, shift_no: int, run: str) -> None:
        if not self.enabled:
            return
        new = ledger.alerts[self._alerts_written:]
        for a in new:
            cost = a.cost_if_ignored or {}
            self.db.execute(
                "INSERT INTO alerts (session_id, at_s, shift_no, run, station,"
                " kind, confidence, detail, margin_s, evidence,"
                " persistence_min, action, cost_vehicles, cost_json, outcome)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (self.session_id, a.at_s, shift_no, run, a.station, a.kind,
                 a.confidence, a.detail, a.margin_s, json.dumps(a.evidence),
                 a.persistence_min, a.action, cost.get("vehicles"),
                 json.dumps(cost), a.outcome))
            self.n_alerts += 1
        if new:
            self.db.commit()
        self._alerts_written = len(ledger.alerts)

    def update_outcome(self, index: int, outcome: str, station: str) -> None:
        """Reflect a human confirm/override back into the store."""
        if not self.enabled:
            return
        self.db.execute(
            "UPDATE alerts SET outcome=? WHERE id=("
            " SELECT id FROM alerts WHERE session_id=? AND station=?"
            " ORDER BY id LIMIT 1 OFFSET ?)",
            (outcome, self.session_id, station, 0))
        self.db.commit()

    # -------------------------------------------------------------- shifts
    def shift(self, shift_no: int, run: str, last: dict, ledger) -> None:
        if not self.enabled:
            return
        self.db.execute(
            "INSERT INTO shifts (session_id, shift_no, run, units_out,"
            " constraint_moves, alerts_total, suppressed, confirmed,"
            " overridden, precision_, ended_iso) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (self.session_id, shift_no, run, last.get("units_out"),
             last.get("shifts_so_far"), len(ledger.alerts), ledger.suppressed,
             ledger.confirmed, ledger.overridden, ledger.precision,
             time.strftime("%Y-%m-%dT%H:%M:%S")))
        self.db.commit()
        self.n_shifts += 1

    # --------------------------------------------------------------- tools
    def tools(self, rows: list, at_s: int, shift_no: int, run: str) -> None:
        if not self.enabled or not rows:
            return
        for r in rows:
            ct = r.get("containment") or {}
            sc = r.get("stop_or_continue") or {}
            self.db.execute(
                "INSERT INTO tool_assessments (session_id, at_s, shift_no, run,"
                " station, tool_id, alarm, cusum, onset_t_s, classification,"
                " action, contained_total, contained_on_line,"
                " contained_completed, stop_decision, channels)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (self.session_id, at_s, shift_no, run, r["station"],
                 r.get("tool_id"), int(bool(r.get("alarm"))), r.get("cusum"),
                 r.get("onset_t_s"), r.get("classification"), r.get("action"),
                 ct.get("total"), len(ct.get("on_line") or []),
                 len(ct.get("completed") or []), sc.get("decision"),
                 json.dumps(r.get("channels") or {})))
            self.n_tools += 1
        self.db.commit()

    # -------------------------------------------------------------- status
    def status(self) -> dict:
        st = {"enabled": self.enabled, "path": self.path,
              "session_id": self.session_id, "frames": self.n_frames,
              "alerts": self.n_alerts, "shifts": self.n_shifts,
              "tool_assessments": self.n_tools}
        if self.enabled and os.path.exists(self.path):
            st["size_bytes"] = os.path.getsize(self.path)
            for t in ("frames", "rankings", "alerts", "shifts",
                      "tool_assessments", "sessions"):
                st[f"total_{t}"] = self.db.execute(
                    f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        return st

    def close(self) -> None:
        if self.db:
            self.db.commit()
            self.db.close()
