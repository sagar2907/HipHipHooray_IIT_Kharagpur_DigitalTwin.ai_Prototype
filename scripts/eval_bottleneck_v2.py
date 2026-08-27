#!/usr/bin/env python3
"""
Score bottleneck detectors against SENSITIVITY ground truth.

The label for a 30-minute block is the station whose 10% speed-up actually
produced the most extra cars in that block, measured with common random
numbers. No detector can recompute that from the event log, so unlike the
active-period label it is a real test.

Detectors see observed logs only; dark stations are absent from their input
but can still be the true answer, so the dark-station penalty is measured.

Reported per method:
  top-1        named the right station first
  top-2        right station in its top two
  top-1 vis    restricted to blocks whose answer is a visible station
  ceiling      share of blocks whose answer is visible at all
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.bottleneck import BottleneckDetector          # noqa: E402
from twin.events import load_run                        # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "dataset", "line_v2")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
METHODS = ("active_period", "utilisation", "least_idle")
BLOCK_MIN = 30


def block_verdict(det: BottleneckDetector, method: str, block: int):
    """Aggregate the detector's per-minute verdicts across a 30-min block.

    The detector emits a verdict every minute; the label is per block. We
    take the station most often named primary inside the block, which is
    the fair aggregation - and also what an operator would perceive.
    """
    start, end = block * BLOCK_MIN * 60, (block + 1) * BLOCK_MIN * 60
    votes: dict[str, int] = {}
    second: dict[str, int] = {}
    for at in range(max(start, det.window_s), end, 60):
        r = det.rank(method, at)
        if not r:
            continue
        votes[r[0]] = votes.get(r[0], 0) + 1
        if len(r) > 1:
            second[r[1]] = second.get(r[1], 0) + 1
    if not votes:
        return None, None
    p = max(votes, key=votes.get)
    pool = {k: v for k, v in second.items() if k != p}
    s = max(pool, key=pool.get) if pool else None
    return p, s


def main():
    man = pd.read_csv(os.path.join(BASE, "run_manifest.csv"))
    truth = pd.read_csv(os.path.join(BASE, "sensitivity_truth.csv"))
    rows = []

    for _, r in man.iterrows():
        rid = int(r.run_id)
        run = load_run(os.path.join(BASE, "runs", f"run_{rid:02d}"), rid)
        det = BottleneckDetector(run)
        dark = set(str(r.dark_stations).split(";"))
        t = truth[truth.run_id == rid]

        for _, tr in t.iterrows():
            if tr.gain_primary <= 0:
                continue          # no station improves output: nothing to find
            for m in METHODS:
                p, s = block_verdict(det, m, int(tr.block))
                if p is None:
                    continue
                rows.append(dict(
                    run_id=rid, block=int(tr.block), fault_kind=r.fault_kind,
                    method=m, true=tr.primary, pred=p, pred2=s,
                    true_is_dark=tr.primary in dark,
                    top1=int(p == tr.primary),
                    top2=int(p == tr.primary or s == tr.primary),
                    gain=tr.gain_primary))

    res = pd.DataFrame(rows)
    os.makedirs(RESULTS, exist_ok=True)
    res.to_csv(os.path.join(RESULTS, "bottleneck_eval_v2.csv"), index=False)

    print("=" * 76)
    print("BOTTLENECK DETECTION vs SENSITIVITY GROUND TRUTH")
    print(f"{man.shape[0]} shifts, {res.block.nunique()} blocks/shift, "
          f"{len(res)//len(METHODS)} scored blocks")
    print("=" * 76)

    vis = res[~res.true_is_dark]
    agg = pd.DataFrame({
        "top-1": res.groupby("method").top1.mean(),
        "top-2": res.groupby("method").top2.mean(),
        "top-1 (visible only)": vis.groupby("method").top1.mean(),
    }).reindex(list(METHODS))
    print((100 * agg).round(1).to_string())

    ceiling = 1 - res[res.method == "active_period"].true_is_dark.mean()
    n_st = len(set(res.true) | set(res.pred))
    print(f"\nrandom-guess floor: {100/n_st:.1f}%   "
          f"visible-answer ceiling: {100*ceiling:.1f}%")

    print("\ntop-1 by fault type:")
    piv = res.pivot_table(index="fault_kind", columns="method", values="top1")
    print((100 * piv).round(1).reindex(columns=list(METHODS)).to_string())

    print("\ntop-1 by strength of the true constraint (cars gained per 30 min):")
    res["band"] = pd.cut(res.gain, [0, 1, 2, 4, 100],
                         labels=["1", "2", "3-4", "5+"])
    piv2 = res.pivot_table(index="band", columns="method", values="top1",
                           observed=True)
    print((100 * piv2).round(1).reindex(columns=list(METHODS)).to_string())

    with open(os.path.join(RESULTS, "bottleneck_eval_v2.txt"), "w") as f:
        f.write((100 * agg).round(1).to_string() + "\n\n")
        f.write((100 * piv).round(1).to_string() + "\n\n")
        f.write((100 * piv2).round(1).to_string() + "\n")
    print("\nwritten: results/bottleneck_eval_v2.{csv,txt}")


if __name__ == "__main__":
    main()
