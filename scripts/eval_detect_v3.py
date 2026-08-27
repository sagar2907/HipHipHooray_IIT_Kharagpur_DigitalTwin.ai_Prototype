#!/usr/bin/env python3
"""
Score the new detector against v3 sensitivity ground truth.

Three methods compared on identical blocks:
  utilisation      rank by share of time busy        (what the PDFs propose)
  active_period    rank by longest uninterrupted run (Roser 2001)
  effective_ct     rank by work-time / availability  (what we converged on)

Two scores, because top-1 alone is a bad metric here:
  top-1 / top-2    did we name the right station
  REGRET           cars per block lost by acting on our pick instead of the
                   true best. If our pick is worth 4 cars and the best is
                   worth 5, we lost 1 - which top-1 records as total failure.

Also reported: performance restricted to blocks where a real constraint
exists (margin >= 0.5 cars). Scoring on blocks whose answer is a coin-flip
between tied stations measures nothing.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.bottleneck import BottleneckDetector          # noqa: E402
from twin.detect import Detector                        # noqa: E402
from twin.events import load_run                        # noqa: E402

FLOW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "dataset", "v3", "flow")
TRUTH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                     "dataset", "v3", "truth", "sensitivity.csv")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
BLOCK_MIN = 30


def block_pick(fn, b):
    """Most-voted station across the block, from per-5-min verdicts."""
    votes = {}
    for at in range(b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60, 300):
        p = fn(at)
        if p:
            votes[p] = votes.get(p, 0) + 1
    if not votes:
        return None, None
    order = sorted(votes, key=votes.get, reverse=True)
    return order[0], (order[1] if len(order) > 1 else None)


def main(limit=None):
    truth = pd.read_csv(TRUTH)
    man = pd.read_csv(os.path.join(FLOW, "run_manifest.csv"))
    runs = [r for r in truth.run.unique() if r.startswith("L1")]
    if limit:
        runs = runs[:limit]
    rows = []

    for k, tag in enumerate(runs):
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        run = load_run(rd, k)
        new = Detector(run)
        old = BottleneckDetector(run)
        t = truth[truth.run == tag]

        pickers = {
            "effective_ct": lambda at: (lambda v: v.constraint if v else None)(new.verdict(at)),
            "active_period": lambda at: (old.rank("active_period", at) or [None])[0],
            "utilisation": lambda at: (old.rank("utilisation", at) or [None])[0],
        }

        for _, tr in t.iterrows():
            vec = np.array([float(x) for x in str(tr.gain_vector).split(";")])
            best = float(vec.max())
            if best <= 0:
                continue                       # nothing to find in this block
            for name, fn in pickers.items():
                p1, p2 = block_pick(fn, int(tr.block))
                if p1 is None:
                    continue
                idx = int(p1[1:]) - 1
                got = float(vec[idx]) if 0 <= idx < len(vec) else 0.0
                rows.append(dict(
                    run=tag, block=int(tr.block), method=name,
                    pred=p1, true=tr.primary, margin=float(tr.margin),
                    top1=int(p1 == tr.primary),
                    top2=int(p1 == tr.primary or p2 == tr.primary),
                    regret=best - got, best_gain=best))
        if (k + 1) % 10 == 0:
            print(f"  ...{k+1}/{len(runs)} runs", flush=True)

    res = pd.DataFrame(rows)
    os.makedirs(RESULTS, exist_ok=True)
    res.to_csv(os.path.join(RESULTS, "detect_v3_eval.csv"), index=False)
    order = ["utilisation", "active_period", "effective_ct"]

    print("\n" + "=" * 72)
    print("ALL SCORED BLOCKS  (n=%d per method)" % (len(res) // 3))
    print("=" * 72)
    a = pd.DataFrame({
        "top-1 %": 100 * res.groupby("method").top1.mean(),
        "top-2 %": 100 * res.groupby("method").top2.mean(),
        "regret (cars/block)": res.groupby("method").regret.mean(),
    }).reindex(order)
    print(a.round(2).to_string())

    clear = res[res.margin >= 0.5]
    print("\n" + "=" * 72)
    print("BLOCKS WITH A REAL CONSTRAINT  (margin >= 0.5 cars, n=%d)"
          % (len(clear) // 3))
    print("=" * 72)
    b = pd.DataFrame({
        "top-1 %": 100 * clear.groupby("method").top1.mean(),
        "top-2 %": 100 * clear.groupby("method").top2.mean(),
        "regret (cars/block)": clear.groupby("method").regret.mean(),
    }).reindex(order)
    print(b.round(2).to_string())

    print("\nmean gain available to a perfect picker: %.2f cars/block"
          % res.groupby(["run", "block"]).best_gain.first().mean())
    print("so regret is measured against that ceiling.")
    with open(os.path.join(RESULTS, "detect_v3_eval.txt"), "w") as f:
        f.write(a.round(2).to_string() + "\n\n" + b.round(2).to_string() + "\n")
    print("\nwritten: results/detect_v3_eval.{csv,txt}")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else None)
