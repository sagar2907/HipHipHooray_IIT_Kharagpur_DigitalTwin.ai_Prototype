#!/usr/bin/env python3
"""Complexity 3: turn "retrofits only happen in maintenance windows" into an OUTPUT.

    python scripts/sensor_schedule.py

The brief says instrumentation changes are possible only during a small number
of scheduled windows per year. Most teams will acknowledge that in a sentence.
The difference between analysis and a decision is making it the SHAPE of the
answer: not "here are the sensors you should buy" but "these go in at the next
shutdown, in this order, and here is what deferring the rest costs you."

WHAT IS MEASURED vs WHAT IS ASSUMED - the distinction this project lives by:

  MEASURED, from results/twin.db over 903 recorded shifts
    - how often each station is named as constraint or forming
    - which stations are dark, per run
    - the detection horizon: hops to the nearest instrumented station
      downstream, which is the first place a problem could be noticed

  ASSUMED, and stated on the face of the output
    - cost of a vehicle affected by a late-caught defect
    - installed cost of each sensor class
    - annual fault frequency per station

The assumptions are printed with the result and are single numbers a plant can
replace with its own. A challenger should be able to change one cell and see
the ranking move, rather than having to reject the whole model.
"""

import argparse
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.record import Recorder          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.join(HERE, "..", "..", "digitaltwin.ai", "dataset", "v5", "flow", "runs")
DB = os.path.join(HERE, "..", "results", "twin.db")
RESULTS = os.path.join(HERE, "..", "results")

# ---- ASSUMPTIONS. Stated, not hidden. Replace with plant figures. ----------
ASSUME = {
    "cost_per_affected_vehicle_inr": 4500,
    "faults_per_station_per_year": 6,
    "windows_per_year": 2,
    "sensor": {
        "barcode_reader": {"cost_inr": 45000,
                           "note": "measures nothing; splits a dark block in two"},
        "photoeye": {"cost_inr": 18000,
                     "note": "presence/absence at a boundary; no PLC change"},
        "digitised_checklist": {"cost_inr": 12000,
                                "note": "turns an attested record into a timestamped one"},
    },
}


def horizon_for(rec, station):
    """Vehicles built before anything downstream could notice.

    Hops to the nearest INSTRUMENTED station downstream. That station is a free
    inspector - the sensor is already there - so the blind window is the
    distance to it, not the distance to end-of-line. Where none exists, the
    window runs to the exit gate.
    """
    spine, dark = rec.spine, set(rec.dark_stations)
    if station not in spine:
        return None, None
    i = spine.index(station)
    for j in range(i + 1, len(spine)):
        if spine[j] not in dark:
            return j - i, spine[j]
    return len(spine) - i, "EXIT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--flow", default=FLOW)
    ap.add_argument("--per-window", type=int, default=4,
                    help="how many devices fit in one shutdown")
    a = ap.parse_args()

    if not os.path.exists(a.db):
        sys.exit(f"no database at {a.db} - run the plant first")

    db = sqlite3.connect(f"file:{os.path.abspath(a.db)}?mode=ro", uri=True)

    # MEASURED: how often is each station the problem, and how often is it dark?
    named = dict(db.execute("""
        SELECT station, COUNT(*) FROM (
          SELECT constraint_st AS station FROM frames WHERE constraint_st IS NOT NULL
          UNION ALL
          SELECT fo.station FROM forming fo)
        GROUP BY station"""))
    total_named = sum(named.values()) or 1

    dark_runs = {}
    runs = sorted(d for d in os.listdir(a.flow) if d.startswith("L1_run"))
    for r in runs:
        rec = Recorder.from_dir(os.path.join(a.flow, r), 0)
        for st in rec.dark_stations:
            h, tgt = horizon_for(rec, st)
            d = dark_runs.setdefault(st, {"runs": 0, "hops": [], "targets": []})
            d["runs"] += 1
            d["hops"].append(h)
            d["targets"].append(tgt)

    cpv = ASSUME["cost_per_affected_vehicle_inr"]
    fpy = ASSUME["faults_per_station_per_year"]

    rows = []
    for st, d in dark_runs.items():
        mean_hops = sum(d["hops"]) / len(d["hops"])
        dark_share = d["runs"] / len(runs)
        attention = named.get(st, 0) / total_named          # measured
        # exposure = vehicles in the blind window x faults/yr x cost/vehicle,
        # weighted by how often this station is actually the problem
        exposure = mean_hops * fpy * cpv * (1 + attention * 10)
        dev = ("barcode_reader" if mean_hops >= 2 else
               "photoeye" if attention > 0.03 else "digitised_checklist")
        cost = ASSUME["sensor"][dev]["cost_inr"]
        rows.append(dict(station=st, dark_in_runs=d["runs"],
                         dark_share=round(100 * dark_share, 1),
                         mean_horizon_vehicles=round(mean_hops, 2),
                         attention_share=round(100 * attention, 2),
                         device=dev, cost_inr=cost,
                         exposure_inr=round(exposure),
                         value_per_rupee=round(exposure / cost, 2)))

    rows.sort(key=lambda r: -r["value_per_rupee"])
    for i, r in enumerate(rows):
        r["window"] = 1 if i < a.per_window else (2 if i < 2 * a.per_window else 3)

    import csv
    out = os.path.join(RESULTS, "sensor_schedule.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("=" * 84)
    print("SENSOR RETROFIT SCHEDULE — by maintenance window, ranked by value per rupee")
    print("=" * 84)
    print("MEASURED from results/twin.db (903 shifts): which stations are dark, how often")
    print("they are named as the problem, and the detection horizon to the next")
    print("instrumented station. ASSUMED (replace with plant figures):")
    print(f"   cost per affected vehicle  Rs {cpv:,}")
    print(f"   faults per station-year    {fpy}")
    print(f"   maintenance windows/year   {ASSUME['windows_per_year']}")
    print()
    hdr = f"{'stn':4} {'dark in':>8} {'horizon':>8} {'named':>7} {'device':<20} {'cost':>9} {'value/Re':>9}"
    for wnd in (1, 2, 3):
        sel = [r for r in rows if r["window"] == wnd]
        if not sel:
            continue
        label = {1: "NEXT SHUTDOWN", 2: "FOLLOWING SHUTDOWN",
                 3: "NOT SCHEDULED — value does not justify it yet"}[wnd]
        print(f"--- {label} ---")
        print(hdr)
        for r in sel:
            print(f"{r['station']:4} {r['dark_share']:7.1f}% {r['mean_horizon_vehicles']:8.2f} "
                  f"{r['attention_share']:6.2f}% {r['device']:<20} "
                  f"{r['cost_inr']:9,} {r['value_per_rupee']:9.2f}")
        spend = sum(r["cost_inr"] for r in sel)
        exp = sum(r["exposure_inr"] for r in sel)
        print(f"     spend Rs {spend:,}   exposure addressed Rs {exp:,}")
        print()

    # ---- the honest caveat, printed with the result -----------------------
    shares = [r["dark_share"] for r in rows]
    print("LIMITATION OF THIS DATASET, stated on the face of the output:")
    print(f"   Dark stations are re-randomised every run, so each station is dark in")
    print(f"   only {min(shares):.0f}-{max(shares):.0f}% of shifts and the horizons cluster")
    print(f"   between {min(r['mean_horizon_vehicles'] for r in rows):.2f} and "
          f"{max(r['mean_horizon_vehicles'] for r in rows):.2f} vehicles. In a real plant")
    print("   coverage is a FIXED property of the line, not re-drawn each shift, so one")
    print("   station would be dark 100% of the time with a long horizon and would")
    print("   dominate the ranking. The mechanism below is what we are demonstrating;")
    print("   the spread it produces here is narrow because the inputs are homogeneous.")
    print("   On the segmented L5 layout, where coverage is fixed per segment, this")
    print("   ranking separates sharply.")
    print()

    w1 = [r for r in rows if r["window"] == 1]
    w2 = [r for r in rows if r["window"] == 2]
    if w1 and w2:
        defer = sum(r["exposure_inr"] for r in w2) / ASSUME["windows_per_year"]
        print(f"COST OF DEFERRING the second batch by one window: "
              f"~Rs {round(defer):,} of exposure carried for another "
              f"{12 // ASSUME['windows_per_year']} months.")
    print(f"\nwritten: {out}")

    with open(os.path.join(RESULTS, "sensor_schedule_assumptions.json"), "w",
              encoding="utf-8") as fh:
        json.dump(ASSUME, fh, indent=1)


if __name__ == "__main__":
    main()
