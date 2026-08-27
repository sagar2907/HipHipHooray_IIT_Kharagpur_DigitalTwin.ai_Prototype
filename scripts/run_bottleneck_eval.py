#!/usr/bin/env python3
"""
Score the bottleneck detectors against hidden ground truth.

Protocol
  - Detectors see ONLY the observed logs (dark stations absent).
  - Ground truth is computed with full knowledge, including dark stations.
  - Accuracy is reported three ways:
        overall            every labelled minute
        observable-only    minutes where the true bottleneck is a station
                           the detector can actually see
        dark               minutes where the true bottleneck is a dark
                           station - an upper bound on what virtual sensing
                           is worth, measured rather than asserted
  - top-2 accuracy is reported alongside top-1, because naming the
    constraint in a shortlist of two is still operationally useful.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.bottleneck import detect_all, shifting_summary          # noqa: E402
from twin.events import load_run                                   # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "line")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
METHODS = ("active_period", "utilisation", "least_idle")


def main():
    man = pd.read_csv(os.path.join(BASE, "run_manifest.csv"))
    rows, shift_rows = [], []

    for _, r in man.iterrows():
        rid = int(r.run_id)
        rd = os.path.join(BASE, "runs", f"run_{rid:02d}")
        run = load_run(rd, rid)
        truth = pd.read_csv(os.path.join(rd, "hidden", "bottleneck_truth.csv"))
        dark = set(str(r.dark_stations).split(";"))

        tl = detect_all(run, METHODS)
        for m in METHODS:
            j = truth.merge(tl[m], on="minute", suffixes=("_true", "_pred"))
            if j.empty:
                continue
            is_dark = j.primary_true.isin(dark)
            top1 = (j.primary_true == j.primary_pred)
            top2 = top1 | (j.primary_true == j.secondary_pred)
            rows.append(dict(
                run_id=rid, fault_kind=r.fault_kind, method=m,
                minutes=len(j),
                top1=top1.mean(), top2=top2.mean(),
                top1_observable=top1[~is_dark].mean() if (~is_dark).any() else np.nan,
                top1_dark=top1[is_dark].mean() if is_dark.any() else np.nan,
                dark_share=is_dark.mean()))
            s = shifting_summary(tl[m])
            shift_rows.append(dict(run_id=rid, method=m, **s))

    res = pd.DataFrame(rows)
    os.makedirs(RESULTS, exist_ok=True)
    res.to_csv(os.path.join(RESULTS, "bottleneck_eval.csv"), index=False)

    print("=" * 78)
    print("BOTTLENECK DETECTION - accuracy against hidden ground truth")
    print(f"{len(man)} shifts, detectors see observed logs only")
    print("=" * 78)
    agg = res.groupby("method").agg(
        top1=("top1", "mean"), top2=("top2", "mean"),
        top1_observable=("top1_observable", "mean"),
        top1_dark=("top1_dark", "mean")).reindex(list(METHODS))
    agg.columns = ["top-1", "top-2", "top-1 (visible)", "top-1 (dark)"]
    print((100 * agg).round(1).to_string())

    print()
    print("Accuracy by fault type (top-1, active period vs utilisation):")
    piv = res[res.method.isin(["active_period", "utilisation"])].pivot_table(
        index="fault_kind", columns="method", values="top1")
    print((100 * piv).round(1).to_string())

    print()
    dsh = res[res.method == "active_period"].dark_share.mean()
    print(f"Share of labelled minutes where the true constraint is a DARK "
          f"station: {100*dsh:.1f}%")
    print("Those minutes are unreachable without virtual sensing - this is the")
    print("measured size of the dark-station problem on this line, not a guess.")

    print()
    print("How much the constraint moved, as each detector saw it:")
    sh = pd.DataFrame(shift_rows).groupby("method").agg(
        switches=("switches", "median"), distinct=("distinct", "mean"),
        median_reign_min=("median_reign_min", "median")).reindex(list(METHODS))
    print(sh.round(1).to_string())

    with open(os.path.join(RESULTS, "bottleneck_eval.txt"), "w") as f:
        f.write((100 * agg).round(1).to_string() + "\n\n")
        f.write((100 * piv).round(1).to_string() + "\n\n")
        f.write(sh.round(1).to_string() + "\n")
    print(f"\nwritten: results/bottleneck_eval.csv, bottleneck_eval.txt")


if __name__ == "__main__":
    main()
