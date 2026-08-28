#!/usr/bin/env python3
"""Complexity 6: does the twin survive a different line?

    python scripts/eval_transfer.py

The brief asks about extending "beyond a single line or plant", accounting for
variation in **layout, equipment vintage, and sensor maturity**. Two of those
three are answerable with data we already hold and code that already exists -
they had simply never been run.

TWO EXPERIMENTS

1. LAYOUT TRANSFER. Thresholds and the baseline are learned per station from
   that station's own early behaviour, so nothing is fitted to L1 globally.
   The question is therefore not "does a fitted model transfer" but the
   sharper one: does the METHOD hold when the topology changes? L1 is 20
   stations with one merge; L2 is 30 with two; L3 adds a parallel pair, which
   deliberately breaks the pure-series assumption most bottleneck detection
   relies on; L4 is 15.

2. SENSOR MATURITY. `Detector(run, use_states=False)` runs the entire pipeline
   from boundary scans alone - no PLC state tags at all - which is what a
   sensor-poor line actually looks like. Calibrate on a well-instrumented
   line, deploy on a poor one, and report the degradation honestly.

REPORTED HONESTLY

Regret is the headline, per our locked decision: on a constraint that moves
~20x a shift, top-1 is close to a coin flip and punishes correct behaviour on
the blocks where nothing dominates. Top-1/top-2 are reported alongside with
Wilson intervals, because a bare point estimate on n=96 blocks would be the
overclaim this project keeps deleting.
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.detect import Detector          # noqa: E402
from twin.events import load_run          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "..", "digitaltwin.ai", "dataset", "v5")
RESULTS = os.path.join(HERE, "..", "results")
BLOCK_MIN = 60


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def block_pick(det, b):
    """Majority vote across the block, exactly as eval_v5 scores it."""
    votes = {}
    for at in range(b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60, 300):
        v = det.verdict(at)
        if v:
            votes[v.constraint] = votes.get(v.constraint, 0) + 1
    if not votes:
        return None, None
    o = sorted(votes, key=votes.get, reverse=True)
    return o[0], (o[1] if len(o) > 1 else None)


def score(layout, truth, flow, use_states, limit=None):
    runs = [r for r in truth.run.unique() if r.startswith(layout)]
    if limit:
        runs = runs[:limit]
    rows = []
    for k, tag in enumerate(runs):
        rd = os.path.join(flow, tag)
        if not os.path.exists(rd):
            continue
        try:
            det = Detector(load_run(rd, k), use_states=use_states)
        except Exception:
            continue
        for _, tr in truth[truth.run == tag].iterrows():
            vec = np.array([float(x) for x in str(tr.gain_vector).split(";")])
            best = float(vec.max())
            if best <= 0:
                continue
            p1, p2 = block_pick(det, int(tr.block))
            if p1 is None:
                continue
            i = int(p1[1:]) - 1
            got = float(vec[i]) if 0 <= i < len(vec) else 0.0
            rows.append(dict(layout=layout, run=tag, block=int(tr.block),
                             top1=int(p1 == tr.primary),
                             top2=int(p1 == tr.primary or p2 == tr.primary),
                             regret=best - got, best=best,
                             margin=float(tr.margin)))
    return pd.DataFrame(rows)


def summarise(df, label):
    if df.empty:
        print(f"  {label:34} (no blocks)")
        return None
    n = len(df)
    t1, l1, h1 = wilson(int(df.top1.sum()), n)
    t2, l2, h2 = wilson(int(df.top2.sum()), n)
    print(f"  {label:34} n={n:4d}  "
          f"top1 {100*t1:5.1f}% [{100*l1:4.1f},{100*h1:4.1f}]  "
          f"top2 {100*t2:5.1f}%  regret {df.regret.mean():5.3f}  "
          f"ceiling {df.best.mean():5.3f}")
    return dict(label=label, n=n, top1=round(100 * t1, 1),
                top1_lo=round(100 * l1, 1), top1_hi=round(100 * h1, 1),
                top2=round(100 * t2, 1), regret=round(df.regret.mean(), 3),
                ceiling=round(df.best.mean(), 3),
                capture=round(100 * (1 - df.regret.mean() / df.best.mean()), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--l1-limit", type=int, default=24,
                    help="cap L1 runs so the reference is comparable in size")
    a = ap.parse_args()

    flow = os.path.join(a.base, "flow", "runs")
    truth = pd.read_csv(os.path.join(a.base, "truth", "sensitivity.csv"))
    out = []

    print("=" * 78)
    print("EXPERIMENT 1 — LAYOUT TRANSFER  (does the method survive a new topology?)")
    print("=" * 78)
    frames = {}
    for L, desc in (("L1", "20 stn, 1 merge  (reference)"),
                    ("L2", "30 stn, 2 merges"),
                    ("L3", "20 stn + PARALLEL pair"),
                    ("L4", "15 stn, 1 merge")):
        df = score(L, truth, flow, use_states=True,
                   limit=a.l1_limit if L == "L1" else None)
        frames[L] = df
        r = summarise(df, f"{L}  {desc}")
        if r:
            r["experiment"] = "layout"
            out.append(r)

    print()
    print("=" * 78)
    print("EXPERIMENT 2 — SENSOR MATURITY  (no PLC state tags at all)")
    print("=" * 78)
    for L in ("L1", "L2"):
        df = score(L, truth, flow, use_states=False,
                   limit=a.l1_limit if L == "L1" else None)
        r = summarise(df, f"{L}  scans only (use_states=False)")
        if r:
            r["experiment"] = "sensor_maturity"
            out.append(r)
        base = frames.get(L)
        if base is not None and not base.empty and df is not None and not df.empty:
            print(f"       -> regret {base.regret.mean():.3f} (instrumented) "
                  f"vs {df.regret.mean():.3f} (scans only)  "
                  f"degradation {df.regret.mean()-base.regret.mean():+.3f} cars/block")

    res = pd.DataFrame(out)
    os.makedirs(RESULTS, exist_ok=True)
    res.to_csv(os.path.join(RESULTS, "transfer_eval.csv"), index=False)
    print(f"\nwritten: results/transfer_eval.csv")


if __name__ == "__main__":
    main()
