"""Genealogy containment: which vehicles carry the suspect joint?

Complexity 4 of the brief: "a defect introduced early in the line may not
surface until a much later inspection point, by which time many downstream
units may carry the same undetected issue - making root-cause tracing after
the fact especially difficult."

Detection alone does not answer that. Knowing a tool started drifting is
useless to a plant unless you can also say WHICH CARS went through it since,
and WHERE THOSE CARS ARE NOW. This module answers both, from the VIN thread
the plant already records.

Three things here are load-bearing:

1. ONSET IS READ BACKWARDS OFF THE CUSUM ACCUMULATOR. This only became
   possible when drift_cusum was fixed to carry state (defect #5). A
   memoryless z-score has no history to walk back through, so it can tell you
   that something is wrong now but not when it started - and "when" is
   precisely what sizes the containment list.

2. THE LIST IS PARTITIONED BY WHERE THE CAR IS. A suspect vehicle still on
   the line is a rework instruction; one that has left the plant is a
   customer event, and those differ in cost by orders of magnitude. A single
   undifferentiated count would be useless to the person who has to act.

3. REPAIR AND RECALIBRATE ARE DISTINGUISHED, BECAUSE THEY ARE OPPOSITE.
   A worn tool produces real defects and must be serviced. A drifted
   transducer produces false rejections and must only be recalibrated -
   servicing it scraps good parts and fixes nothing. Both present as "the
   torque reading moved". The separation comes from asking whether a
   MECHANICALLY COUPLED channel moved with it: real wear shows up in motor
   current, a lying sensor does not.

Everything is computed causally - nothing reads past `at_s`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

CUSUM_K = 0.5          # slack, in sigma
CUSUM_ALARM = 5.0      # decision interval
MIN_BASELINE = 40      # readings needed before a baseline means anything


@dataclass
class ToolVerdict:
    station: str
    tool_id: str
    alarm: bool
    cusum: float
    onset_t_s: float | None
    n_since_onset: int
    channels: dict            # per-channel drift in sigma
    classification: str       # "wear" | "sensor" | "unclear" | "healthy"
    action: str
    why: str
    confidence: str


def _cusum_series(x: np.ndarray, base_mu: float, base_sd: float) -> np.ndarray:
    """TWO-SIDED tabular CUSUM (C+ and C-), returned as max(|C+|, |C-|).

    One-sided was a real bug, caught by scoring against the hidden truth: it
    detected nothing at all, because tool wear drives torque DOWN, not up. An
    upward-only accumulator is blind to the most common failure mode there is.
    Kept as a series so onset stays recoverable by walking back to the last
    point where both accumulators were at rest.
    """
    sd = max(base_sd, 1e-6)
    hi = np.zeros(len(x))
    lo = np.zeros(len(x))
    for i in range(1, len(x)):
        z = (x[i] - base_mu) / sd
        hi[i] = max(0.0, hi[i - 1] + z - CUSUM_K)
        lo[i] = max(0.0, lo[i - 1] - z - CUSUM_K)
    return np.maximum(hi, lo)


def _drift_sigma(v: np.ndarray, n_base: int) -> float:
    """How far the recent window has moved from the early baseline, in sigma."""
    if len(v) < n_base + 10:
        return 0.0
    base = v[:n_base]
    mu, sd = float(np.nanmean(base)), float(np.nanstd(base))
    if not np.isfinite(sd) or sd < 1e-9:
        return 0.0
    recent = v[-min(40, len(v) - n_base):]
    return float((np.nanmean(recent) - mu) / sd)


def assess_tool(readings: pd.DataFrame, at_s: float) -> ToolVerdict | None:
    """One tool, judged on everything known by `at_s` and nothing later."""
    g = readings[readings.t_s <= at_s].sort_values("t_s")
    if len(g) < MIN_BASELINE + 20:
        return None

    station = str(g.station_id.iloc[0])
    tool_id = str(g.tool_id.iloc[0])

    # Accumulate on BOTH the result channel and the mechanical one. A sensor
    # fault shows only in torque; an early mechanical change can show in
    # current before the joint result moves at all. Watching one channel
    # would miss whichever fault the other one carries.
    best_series, cusum, driver = None, 0.0, "torque"
    for name, col in (("torque", "torque_nm"), ("current", "current_a")):
        if col not in g.columns:
            continue
        v = g[col].to_numpy(dtype=float)
        b = v[:MIN_BASELINE]
        s = _cusum_series(v, float(np.nanmean(b)), float(np.nanstd(b)))
        if float(s[-1]) > cusum:
            cusum, best_series, driver = float(s[-1]), s, name
    if best_series is None:
        return None
    alarm = cusum >= CUSUM_ALARM

    # --- onset: walk back to the last time the accumulator was at rest ------
    onset_t = None
    n_since = 0
    if alarm:
        i = len(best_series) - 1
        while i > 0 and best_series[i] > 0:
            i -= 1
        onset_t = float(g.t_s.iloc[i])
        n_since = int((g.t_s > onset_t).sum())

    # --- which channels moved -----------------------------------------------
    ch = {}
    for name, col in (("torque", "torque_nm"), ("current", "current_a"),
                      ("angle", "angle_deg"), ("temp", "temp_c")):
        if col in g.columns:
            ch[name] = round(_drift_sigma(g[col].to_numpy(dtype=float),
                                          MIN_BASELINE), 2)

    # --- wear vs sensor: does a mechanically coupled channel agree? ---------
    t_mv = abs(ch.get("torque", 0.0)) > 1.0
    c_mv = abs(ch.get("current", 0.0)) > 1.0
    a_mv = abs(ch.get("angle", 0.0)) > 1.0

    if not alarm:
        cls, action, why, conf = ("healthy", "no action",
                                  "no accumulated drift against this tool's own baseline",
                                  "n/a")
    elif not t_mv and (c_mv or a_mv):
        cls, action, why, conf = (
            "mechanical_change",
            "INSPECT - the joint result has not moved yet",
            "motor current and/or angle have shifted while torque has not. "
            "Something mechanical is changing before it reaches the joint, "
            "which is the earliest point at which anything is visible", "medium")
    elif t_mv and (c_mv or a_mv):
        cls, action, why, conf = (
            "wear", "SERVICE the tool - real defects are being produced",
            "torque moved AND a mechanically coupled channel moved with it, "
            "so the joint really is changing", "high")
    elif t_mv and not c_mv and not a_mv:
        cls, action, why, conf = (
            "sensor", "RECALIBRATE only - do NOT service",
            "torque moved but motor current and angle did not; the process is "
            "mechanically unchanged, so the transducer is lying and any NOKs "
            "here are FALSE REJECTS of good parts", "high")
    else:
        cls, action, why, conf = (
            "unclear", "inspect before acting",
            "drift is present but the channel pattern does not separate a worn "
            "tool from a drifted sensor", "low")

    return ToolVerdict(station=station, tool_id=tool_id, alarm=alarm,
                       cusum=round(cusum, 1), onset_t_s=onset_t,
                       n_since_onset=n_since, channels=ch,
                       classification=cls, action=action, why=why,
                       confidence=conf)


def containment(scans: pd.DataFrame, station: str, onset_t_s: float,
                at_s: float, exit_station: str | None) -> dict:
    """Every vehicle through `station` since onset, partitioned by where it is.

    Bands exist because the cost of a suspect unit depends entirely on how far
    it has travelled. Rework on the line is minutes; a unit that has left is a
    different conversation.
    """
    sc = scans[scans.t_s <= at_s]
    through = sc[(sc.station_id == station) & (sc.event == "out")
                 & (sc.t_s > onset_t_s)]
    vins = list(dict.fromkeys(through.vin.tolist()))
    if not vins:
        return {"total": 0, "on_line": [], "completed": [], "bands": []}

    completed = set()
    if exit_station:
        done = sc[(sc.station_id == exit_station) & (sc.event == "out")]
        completed = set(done.vin) & set(vins)
    on_line = [v for v in vins if v not in completed]
    comp = [v for v in vins if v in completed]

    return {
        "total": len(vins),
        "on_line": on_line,
        "completed": comp,
        "bands": [
            {"band": "still on the line", "n": len(on_line),
             "action": "hold and rework in place - cheapest to fix",
             "vins": on_line[:12]},
            {"band": "completed the line", "n": len(comp),
             "action": "quarantine before dispatch; re-test the joint",
             "vins": comp[:12]},
        ],
    }


def stop_or_continue(buffers: pd.DataFrame, station: str, at_s: float,
                     is_constraint: bool, window_s: int = 900) -> dict:
    """Stop this station now, or wait for the next planned break?

    The intuitive answer - "never stop the bottleneck" - is wrong, and this
    is the correction that came out of the Complexity 4 review. What decides
    is the ESCAPE ROUTE: whether the buffer downstream can absorb the stop.

    A station with room downstream can pause for a few minutes and the line
    never notices, whether or not that station is currently the constraint.
    A station whose downstream buffer is already full has nowhere to put the
    units it is holding, so a stop propagates immediately and every minute is
    a car. Bottleneck status correlates with that, but it is not the thing
    itself - which is why using it as the rule gets cases wrong.

    So the same drifting tool genuinely gets opposite correct answers at
    different moments of the same shift, decided by buffer state.
    """
    # B(i+1) sits downstream of S(i)
    try:
        idx = int(station[1:])
    except ValueError:
        return {"decision": "unknown", "why": "unparseable station id"}
    bid = f"B{idx:02d}"

    b = buffers[(buffers.buffer_id == bid) & (buffers.t_s <= at_s)
                & (buffers.t_s > at_s - window_s)]
    if b.empty:
        return {"decision": "WAIT FOR THE NEXT BREAK", "buffer": bid,
                "headroom": None, "level": None, "capacity": None,
                "is_constraint": is_constraint,
                "why": "no downstream buffer telemetry in this window, so we "
                       "cannot show there is an escape route - and without "
                       "evidence the safe answer is to wait",
                "note": "decided by the escape route, not by bottleneck status"}

    b = b.sort_values("t_s")
    level = float(b.level.iloc[-1])
    cap = float(b.capacity.iloc[-1])
    headroom = max(0.0, cap - level)
    frac = headroom / cap if cap > 0 else 0.0

    if frac >= 0.5:
        dec = "STOP NOW - it is effectively free"
        why = (f"{bid} is {level:.0f}/{cap:.0f}, so {headroom:.0f} units of "
               f"headroom absorb a short stop before anything downstream "
               f"notices")
    elif frac > 0:
        dec = "STOP SOON - a short pause only"
        why = (f"{bid} is {level:.0f}/{cap:.0f}; there is some room but not "
               f"much, so keep the stop brief")
    else:
        dec = "WAIT FOR THE NEXT BREAK"
        why = (f"{bid} is full at {level:.0f}/{cap:.0f} - there is no escape "
               f"route, so a stop propagates immediately and every minute "
               f"costs vehicles")
    return {"decision": dec, "headroom": round(headroom, 1),
            "level": round(level, 1), "capacity": round(cap, 1),
            "buffer": bid, "is_constraint": is_constraint, "why": why,
            "note": "decided by the escape route, not by bottleneck status"}


def assess_all(readings: pd.DataFrame, scans: pd.DataFrame, at_s: float,
               exit_station: str | None, buffers: pd.DataFrame | None = None,
               constraint: str | None = None) -> list:
    """Every instrumented tool on the line, with containment where alarmed."""
    out = []
    if readings is None or readings.empty:
        return out
    for st, g in readings.groupby("station_id"):
        v = assess_tool(g, at_s)
        if v is None:
            continue
        row = {
            "station": v.station, "tool_id": v.tool_id, "alarm": v.alarm,
            "cusum": v.cusum, "onset_t_s": v.onset_t_s,
            "n_since_onset": v.n_since_onset, "channels": v.channels,
            "classification": v.classification, "action": v.action,
            "why": v.why, "confidence": v.confidence, "containment": None,
        }
        if v.alarm and v.onset_t_s is not None:
            row["containment"] = containment(scans, v.station, v.onset_t_s,
                                             at_s, exit_station)
            if buffers is not None:
                row["stop_or_continue"] = stop_or_continue(
                    buffers, v.station, at_s, v.station == constraint)
        out.append(row)
    # alarms first, then by accumulated evidence
    out.sort(key=lambda r: (not r["alarm"], -r["cusum"]))
    return out
