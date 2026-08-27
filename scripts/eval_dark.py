#!/usr/bin/env python3
"""
Score the dark-station layer against hidden truth.

Question 1 - LOCALISATION. When the twin says "the constraint is inside this
dark block", is it? Scored against truth/sensitivity.csv, which names the
station whose speed-up actually produces more cars. The detector sees only
observed files; the dark stations emit nothing to it.

Question 2 - EXONERATION. Just as useful and far more common: when the twin
says the block is NOT the problem, is it right? A method that only ever says
"maybe it's in there" narrows nothing.

Question 3 - POSITION. Inside a consecutive dark block, does the
time-difference-of-arrival posterior put weight on the right station?
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.dark import find_dark_blocks, localise, position_within_block  # noqa: E402
from twin.detect import Detector                                          # noqa: E402
from twin.events import load_run                                          # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "v5")
FLOW = os.path.join(BASE, "flow")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def main(limit=60):
    man = pd.read_csv(os.path.join(FLOW, "run_manifest.csv"))
    truth = pd.read_csv(os.path.join(BASE, "truth", "sensitivity.csv"))
    runs = man[(man.n_shifts == 1) & (man.layout == "L1")].head(limit)
    rows, pos_rows = [], []

    for k, r in runs.iterrows():
        tag = r.run
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        run = load_run(rd, k)
        det = Detector(run)
        dark = set(str(r.dark_stations).split(";"))
        spine = [f"S{i:02d}" for i in range(1, 21)]
        blocks = find_dark_blocks(spine, dark)
        t = truth[truth.run == tag]
        if t.empty:
            continue
        # which station actually held the constraint most of the shift
        true_primary = t.primary.mode().iloc[0]

        # Compare LIKE WITH LIKE. The block figure is traversal time between
        # two scans - it contains transit and any waiting inside the block. So
        # the visible baseline must be scan-to-scan DWELL too, not the pure
        # processing time the detector reports. Comparing an inflated block
        # figure against clean processing time makes "the constraint is inside"
        # almost always true, which is the same bracketing confound this module
        # exists to warn about.
        p = run.scans.pivot_table(index=["vin", "station_id"], columns="event",
                                  values="t_s", aggfunc="first").reset_index()
        p = p.dropna(subset=["in", "out"])
        # The block figure is (downstream IN - upstream OUT) / n, so it spans
        # each station's dwell AND the transit gap that follows it. The only
        # matched baseline is the same quantity measured over one station:
        # this station's OUT to the next station's IN, plus its own dwell.
        # Equivalently: next station's IN minus this station's IN.
        p["si"] = p.station_id.str.extract(r"S(\d+)").astype(float)
        p = p.dropna(subset=["si"]).sort_values(["vin", "si"])
        p["next_in"] = p.groupby("vin")["in"].shift(-1)
        p["next_si"] = p.groupby("vin")["si"].shift(-1)
        step = p[(p.next_si == p.si + 1)].copy()
        step["interval"] = step["next_in"] - step["in"]
        visible = {s: float(g.interval.median())
                   for s, g in step.groupby("station_id")
                   if s not in dark and len(g) >= 20}
        if not visible:
            continue

        for b in blocks:
            loc = localise(run.scans, b, visible)
            if loc is None:
                continue
            truth_inside = true_primary in b.stations
            rows.append(dict(run=tag, block=";".join(b.stations), tier=b.tier,
                             said_inside=int(loc.constraint_inside),
                             truth_inside=int(truth_inside),
                             block_time=loc.mean_block_time,
                             slowest_visible=loc.slowest_visible_time,
                             confidence=loc.confidence))
            if b.tier == "C" and truth_inside:
                post = position_within_block(run.scans, run.states, b)
                best = max(post, key=post.get)
                pos_rows.append(dict(run=tag, block=";".join(b.stations),
                                     truth=true_primary, top_guess=best,
                                     p_on_truth=post.get(true_primary, 0.0),
                                     correct=int(best == true_primary),
                                     n_stations=len(b.stations)))
        if (k + 1) % 20 == 0:
            print(f"  ...{k+1} runs", flush=True)

    d = pd.DataFrame(rows)
    os.makedirs(RESULTS, exist_ok=True)
    d.to_csv(os.path.join(RESULTS, "dark_localisation.csv"), index=False)

    print("\n" + "=" * 72)
    print("DARK-STATION LOCALISATION  (detector never sees these stations)")
    print("=" * 72)
    print(f"dark blocks evaluated: {len(d)}  "
          f"(tier B single: {(d.tier=='B').sum()}, tier C consecutive: {(d.tier=='C').sum()})")
    tp = int(((d.said_inside == 1) & (d.truth_inside == 1)).sum())
    fp = int(((d.said_inside == 1) & (d.truth_inside == 0)).sum())
    fn = int(((d.said_inside == 0) & (d.truth_inside == 1)).sum())
    tn = int(((d.said_inside == 0) & (d.truth_inside == 0)).sum())
    print(f"\n              truth: inside   truth: elsewhere")
    print(f"said inside        {tp:5d}            {fp:5d}")
    print(f"said elsewhere     {fn:5d}            {tn:5d}")
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    exon = tn / max(tn + fn, 1)
    print(f"\nprecision when it says 'inside'   {prec:.2f}")
    print(f"recall of constraints inside dark {rec:.2f}")
    print(f"EXONERATION accuracy              {exon:.2f}  "
          f"({tn} blocks correctly cleared)")
    print(f"\nbase rate: the constraint is inside a dark block "
          f"{100*d.truth_inside.mean():.0f}% of the time")
    print("-> exoneration is the common case and the operationally useful one:")
    print("   clearing a block sends the supervisor to the instrumented stations.")

    if pos_rows:
        p = pd.DataFrame(pos_rows)
        p.to_csv(os.path.join(RESULTS, "dark_position.csv"), index=False)
        print("\n" + "=" * 72)
        print("POSITION INSIDE A CONSECUTIVE DARK BLOCK  (tier C)")
        print("=" * 72)
        print(f"cases: {len(p)}   top guess correct: {p.correct.mean():.2f}   "
              f"random would be {1/p.n_stations.mean():.2f}")
        print(f"mean probability placed on the true station: {p.p_on_truth.mean():.2f}")
    print("\nwritten: results/dark_*.csv")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else 60)
