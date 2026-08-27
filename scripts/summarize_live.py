#!/usr/bin/env python3
"""Summarise what a long continuous run actually recorded.

    python scripts/summarize_live.py

Reads results/live/*.jsonl and reports the things a long run is FOR: how the
constraint distributes across many shifts, whether the alert rate stays inside
the ISA-18.2 budget once it is not one cherry-picked shift, how often we name a
station that has no sensors, and what the loop cost.

Writes results/live_summary.json, which is small enough to commit - the raw
frames are not.
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "results", "live")


def read(name):
    p = os.path.join(LIVE, name)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass          # a crash can truncate the final line; skip it
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results",
                                                  "live_summary.json"))
    a = ap.parse_args()

    frames = read("frames.jsonl")
    alerts = read("alerts.jsonl")
    shifts = read("shifts.jsonl")
    if not frames:
        sys.exit(f"nothing recorded yet in {LIVE}\n"
                 f"Start the server without --no-record and let it run.")

    live = [f for f in frames if f.get("constraint")]
    runs = {f.get("run") for f in frames if f.get("run")}
    n_shifts = len({(f.get("shift"), f.get("run")) for f in frames})

    occ = Counter(f["constraint"] for f in live)
    total_occ = sum(occ.values()) or 1

    forming_total = sum(len(f.get("forming") or []) for f in frames)
    forming_dark = sum(1 for f in frames for x in (f.get("forming") or [])
                       if x.get("dark"))

    presc = Counter(f.get("presc") for f in live if f.get("presc"))
    kinds = Counter(a.get("kind") for a in alerts)
    ms = [f["ms"] for f in frames if f.get("ms") is not None]

    per_shift = defaultdict(int)
    for al in alerts:
        per_shift[al.get("at_s", 0) // 28800] += 1
    mean_alerts = (len(alerts) / n_shifts) if n_shifts else 0

    summary = {
        "frames": len(frames), "alerts": len(alerts),
        "shifts_completed": len(shifts), "distinct_shifts_seen": n_shifts,
        "distinct_runs": len(runs),
        "sim_hours": round(len(frames) * 5 / 60, 1),
        "constraint_occupancy_pct": {
            s: round(100 * n / total_occ, 1)
            for s, n in occ.most_common(10)},
        "alerts_per_shift": round(mean_alerts, 1),
        "isa_18_2_budget_150": "WITHIN" if mean_alerts < 150 else "OVER",
        "alert_kinds": dict(kinds),
        "forming_warnings": forming_total,
        "forming_naming_a_dark_station": forming_dark,
        "forming_dark_pct": (round(100 * forming_dark / forming_total, 1)
                             if forming_total else 0.0),
        "prescription_signatures": dict(presc),
        "loop_ms": {"mean": round(sum(ms) / len(ms), 1) if ms else None,
                    "max": max(ms) if ms else None},
    }

    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)

    print(f"recorded: {len(frames)} frames, {len(alerts)} alerts, "
          f"{n_shifts} shifts across {len(runs)} runs "
          f"(~{summary['sim_hours']} simulated hours)")
    print()
    print("constraint occupancy across ALL recorded shifts:")
    for s, pct in list(summary["constraint_occupancy_pct"].items())[:8]:
        bar = "#" * int(pct)
        print(f"   {s}  {pct:5.1f}%  {bar}")
    print()
    print(f"alerts/shift  : {summary['alerts_per_shift']}  "
          f"({summary['isa_18_2_budget_150']} the ISA-18.2 budget of 150)")
    print(f"alert kinds   : {summary['alert_kinds']}")
    print(f"forming       : {forming_total} warnings, {forming_dark} of them "
          f"({summary['forming_dark_pct']}%) name a station with NO sensors")
    print(f"prescriptions : {summary['prescription_signatures']}")
    print(f"loop latency  : mean {summary['loop_ms']['mean']} ms, "
          f"max {summary['loop_ms']['max']} ms")
    print(f"\nwritten: {a.out}")


if __name__ == "__main__":
    main()
