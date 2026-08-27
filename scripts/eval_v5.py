#!/usr/bin/env python3
"""
Score the detectors against v5 sensitivity truth.

Three detectors on identical blocks:
  utilisation      rank by share of time busy          (what the PDFs propose)
  active_period    rank by longest uninterrupted run   (Roser 2001)
  effective_ct     rank by work-time / availability    (what we converged on)

Reported separately for the TWO REGIMES, because averaging them hides the
result. A healthy balanced line genuinely has no dominant constraint, so a
low score there is not a failure - it is the correct answer to an ill-posed
question. A faulted line does have one, and that is where detection matters.

Metrics:
  top-1 / top-2   did we name the right station
  regret          cars per block lost by acting on our pick instead of the
                  true best - the operationally honest metric, because naming
                  the second-best station when it is worth 4 of 5 cars is not
                  a failure in any sense a plant manager cares about
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.bottleneck import BottleneckDetector          # noqa: E402
from twin.detect import Detector                        # noqa: E402
from twin.events import load_run                        # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "v5")
FLOW = os.path.join(BASE, "flow")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
BLOCK_MIN = 60
ORDER = ["utilisation", "active_period", "effective_ct"]


def block_pick(fn, b):
    votes = {}
    for at in range(b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60, 300):
        p = fn(at)
        if p:
            votes[p] = votes.get(p, 0) + 1
    if not votes:
        return None, None
    o = sorted(votes, key=votes.get, reverse=True)
    return o[0], (o[1] if len(o) > 1 else None)


def summarise(df, title):
    if df.empty:
        print(f"\n{title}: no blocks")
        return
    t = pd.DataFrame({
        "top-1 %": 100 * df.groupby("method").top1.mean(),
        "top-2 %": 100 * df.groupby("method").top2.mean(),
        "regret (cars/block)": df.groupby("method").regret.mean(),
    }).reindex(ORDER)
    n = len(df) // len(ORDER)
    print(f"\n{title}  (n={n} blocks)")
    print(t.round(2).to_string())


def main(limit=None):
    truth = pd.read_csv(os.path.join(BASE, "truth", "sensitivity.csv"))
    man = pd.read_csv(os.path.join(FLOW, "run_manifest.csv"))
    kind = dict(zip(man.run, man.fault_kind))
    runs = [r for r in truth.run.unique() if r.startswith("L1")]
    if limit:
        runs = runs[:limit]
    rows = []

    for k, tag in enumerate(runs):
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        run = load_run(rd, k)
        new, old = Detector(run), BottleneckDetector(run)
        pickers = {
            "effective_ct": lambda at: (lambda v: v.constraint if v else None)(new.verdict(at)),
            "active_period": lambda at: (old.rank("active_period", at) or [None])[0],
            "utilisation": lambda at: (old.rank("utilisation", at) or [None])[0],
        }
        for _, tr in truth[truth.run == tag].iterrows():
            vec = np.array([float(x) for x in str(tr.gain_vector).split(";")])
            best = float(vec.max())
            if best <= 0:
                continue
            for name, fn in pickers.items():
                p1, p2 = block_pick(fn, int(tr.block))
                if p1 is None:
                    continue
                i = int(p1[1:]) - 1
                got = float(vec[i]) if 0 <= i < len(vec) else 0.0
                rows.append(dict(run=tag, block=int(tr.block), method=name,
                                 faulted=kind.get(tag, "none") != "none",
                                 margin=float(tr.margin), top1=int(p1 == tr.primary),
                                 top2=int(p1 == tr.primary or p2 == tr.primary),
                                 regret=best - got, best=best))
        if (k + 1) % 15 == 0:
            print(f"  ...{k+1}/{len(runs)} runs", flush=True)

    res = pd.DataFrame(rows)
    os.makedirs(RESULTS, exist_ok=True)
    res.to_csv(os.path.join(RESULTS, "eval_v5.csv"), index=False)

    print("\n" + "=" * 74)
    print("DETECTOR EVALUATION vs v5 SENSITIVITY TRUTH")
    print("=" * 74)
    summarise(res, "ALL BLOCKS")
    summarise(res[res.faulted], "FAULTED RUNS  (a real constraint exists)")
    summarise(res[~res.faulted], "NO-FAULT RUNS  (balanced line, diffuse by nature)")
    summarise(res[res.margin >= 2], "STRONG CONSTRAINT ONLY  (margin >= 2 cars)")

    print(f"\nmean gain available to a perfect picker: "
          f"{res.groupby(['run','block']).best.first().mean():.2f} cars/block")
    print("regret is measured against that ceiling.")
    print(f"\nwritten: results/eval_v5.csv")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else None)
