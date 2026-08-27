"""Persist what the loop emits, so a long run leaves evidence behind.

Until this existed the twin was amnesiac: frames went to the browser and were
dropped, the ledger lived in memory, and a restart erased the lot. That is
fine for a demo and useless for the thing the brief actually asks for -
predictive claims validated against real outcomes OVER TIME. You cannot show
a precision that survived forty shifts if you threw thirty-nine of them away.

Three streams, all append-only JSONL so a crash truncates at most one line
and nothing needs rewriting:

  frames.jsonl   one compact row per tick - the record stream the three
                 views claim to share, now actually on disk
  alerts.jsonl   every alert as raised, with its five contract fields
  shifts.jsonl   one row per completed shift

Frames are deliberately COMPACT. A full frame carries the whole ranking and
runs 2-3 KB; at 300x that is ~7 MB an hour, which turns a week of running
into something nobody will open. We keep the head of the ranking and the
fields any later analysis needs, and drop the tail - the full ranking is
always recoverable by replaying the run, because the loop is deterministic.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict


class LiveSink:
    """Append-only JSONL writer for a running loop."""

    def __init__(self, out_dir: str, enabled: bool = True):
        self.dir = out_dir
        self.enabled = enabled
        self.n_frames = 0
        self.n_alerts = 0
        self.n_shifts = 0
        self._alerts_written = 0
        if enabled:
            os.makedirs(out_dir, exist_ok=True)

    def _append(self, name: str, obj: dict) -> None:
        if not self.enabled:
            return
        with open(os.path.join(self.dir, name), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, separators=(",", ":")) + "\n")

    # ------------------------------------------------------------- frames
    def frame(self, f: dict) -> None:
        """One compact row per tick."""
        if not self.enabled or f.get("shift_change") or f.get("done"):
            return
        row = {
            "t": f.get("t_s"), "shift": f.get("shift_no"), "run": f.get("run"),
            "clock": f.get("clock"), "constraint": f.get("constraint"),
            "margin": f.get("margin"), "conf": f.get("confidence"),
            "units_out": f.get("units_out"), "moves": f.get("shifts_so_far"),
            "persist_min": f.get("persistence_min"),
            "ms": f.get("compute_ms"),
            # head of the ranking only - the tail is recoverable by replay
            "top": [{"s": r["station"], "ect": r["effective_ct"],
                     "blk": r["blocked"], "srv": r["starved"],
                     "cus": r["cusum"]} for r in (f.get("ranking") or [])[:3]],
            "forming": [{"s": x["station"], "min": x["minutes"],
                         "dark": x.get("dark", False)}
                        for x in (f.get("forming") or [])],
            "presc": (f.get("prescription") or {}).get("signature"),
        }
        self._append("frames.jsonl", row)
        self.n_frames += 1

    # ------------------------------------------------------------- alerts
    def alerts(self, ledger) -> None:
        """Write any alerts raised since the last call."""
        if not self.enabled:
            return
        new = ledger.alerts[self._alerts_written:]
        for a in new:
            d = asdict(a) if not isinstance(a, dict) else dict(a)
            self._append("alerts.jsonl", d)
            self.n_alerts += 1
        self._alerts_written = len(ledger.alerts)

    # ------------------------------------------------------------- shifts
    def shift(self, shift_no: int, run: str, last_frame: dict,
              ledger) -> None:
        self._append("shifts.jsonl", {
            "shift": shift_no, "run": run,
            "units_out": last_frame.get("units_out"),
            "constraint_moves": last_frame.get("shifts_so_far"),
            "alerts_total": len(ledger.alerts),
            "suppressed_total": ledger.suppressed,
            "confirmed": ledger.confirmed, "overridden": ledger.overridden,
            "precision": ledger.precision,
        })
        self.n_shifts += 1

    def status(self) -> dict:
        return {"enabled": self.enabled, "dir": self.dir,
                "frames": self.n_frames, "alerts": self.n_alerts,
                "shifts": self.n_shifts}
