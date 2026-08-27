#!/usr/bin/env python3
"""Fit the confidence calibrator on HELD-OUT runs and save it.

    python scripts/fit_calibration.py --fit-runs 30 --holdout-runs 20

Workstream C's gate is "calibration within +/-10 points". Before this,
`confidence` was an ordering score presented as if it were a probability -
measured at 0.997 claimed against a 10.6% hit rate (ECE 0.454). That is the
same failure we already killed once in the overtake-risk mechanism, so it does
not get to ship twice.

The runs used to FIT are disjoint from the runs used to REPORT, and both are
disjoint from the demo run. Calibrating on the shift you then demo would be
leakage, and the number would mean nothing.

Ground truth is the sensitivity label from truth/sensitivity.csv: the station
whose speed-up actually produces more cars. Being "right" means naming that
station.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.detect import Detector          # noqa: E402
from twin.events import load_run          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BASE = os.path.join(HERE, "..", "..", "digitaltwin.ai", "dataset", "v5")
RESULTS = os.path.join(HERE, "..", "results")
BLOCK_MIN = 60


def collect(tags, flow, truth):
    rows = []
    for k, tag in enumerate(tags):
        rd = os.path.join(flow, tag)
        if not os.path.exists(rd):
            continue
        det = Detector(load_run(rd, k))
        for _, tr in truth[truth.run == tag].iterrows():
            vec = np.array([float(x) for x in str(tr.gain_vector).split(";")])
            if vec.max() <= 0:
                continue
            b = int(tr.block)
            for at in range(b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60, 900):
                v = det.verdict(at)
                if v is None:
                    continue
                rows.append((v.confidence_raw, int(v.constraint == tr.primary)))
    return pd.DataFrame(rows, columns=["score", "hit"])


def ece(score, hit, n_bins=10):
    df = pd.DataFrame(dict(s=score, h=hit))
    if df.empty:
        return float("nan"), pd.DataFrame()
    df["b"] = pd.cut(df.s, np.linspace(0, 1.0001, n_bins + 1),
                     labels=False, include_lowest=True)
    g = df.groupby("b").agg(claimed=("s", "mean"), observed=("h", "mean"),
                            n=("h", "size")).dropna()
    return float((g.n / g.n.sum() * (g.claimed - g.observed).abs()).sum()), g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--fit-runs", type=int, default=30)
    ap.add_argument("--holdout-runs", type=int, default=20)
    ap.add_argument("--skip", type=int, default=20,
                    help="skip the first N runs so the demo run is excluded")
    ap.add_argument("--out", default=os.path.join(RESULTS, "calibration.json"))
    a = ap.parse_args()

    flow = os.path.join(a.base, "flow", "runs")
    tp = os.path.join(a.base, "truth", "sensitivity.csv")
    if not os.path.isdir(flow) or not os.path.exists(tp):
        sys.exit(f"dataset not found under {a.base}; regenerate with build_v5.py")

    truth = pd.read_csv(tp)
    all_l1 = [r for r in truth.run.unique() if r.startswith("L1")]
    pool = all_l1[a.skip:]
    fit_tags = pool[:a.fit_runs]
    hold_tags = pool[a.fit_runs:a.fit_runs + a.holdout_runs]
    print(f"fit on {len(fit_tags)} runs, report on {len(hold_tags)} held-out runs")
    print(f"(first {a.skip} runs excluded so the demo run is never calibrated on)")

    fit = collect(fit_tags, flow, truth)
    hold = collect(hold_tags, flow, truth)
    print(f"fit samples {len(fit)}, held-out samples {len(hold)}")

    e_before, _ = ece(hold.score, hold.hit)

    # monotone binning, same routine Detector.fit_calibration uses
    d = Detector.__new__(Detector)
    d._calibrator = None
    Detector.fit_calibration(d, list(zip(fit.score, fit.hit)))
    cal = np.array([d._calibrator(s) for s in hold.score])
    e_after, tab = ece(cal, hold.hit)

    print(f"\nECE before : {e_before:.3f}   (raw score treated as a probability)")
    print(f"ECE after  : {e_after:.3f}   ({100*(e_before-e_after)/e_before:.0f}% better)")
    gate = e_after <= 0.10
    print(f"GATE 'calibration within +/-10 points': {'PASS' if gate else 'FAIL'}"
          f"  (ECE {e_after:.3f} vs 0.100)")
    print(f"\nheld-out base rate {hold.hit.mean():.3f}, mean raw score {hold.score.mean():.3f}")

    # persist the fitted mapping as plain edges/probs so the loop needs no pickle
    df = pd.DataFrame(dict(score=fit.score, hit=fit.hit)).sort_values("score")
    n_bins = max(2, min(10, len(df) // 40))
    df["b"] = pd.qcut(df.score.rank(method="first"), n_bins, labels=False)
    g = df.groupby("b").agg(hi=("score", "max"), p=("hit", "mean")).reset_index()
    p = g.p.values.copy()
    for i in range(1, len(p)):
        if p[i] < p[i - 1]:
            p[i] = p[i - 1] = (p[i] + p[i - 1]) / 2

    out = {"edges": [float(x) for x in g.hi.values],
           "probs": [float(x) for x in p],
           "fit_runs": fit_tags, "holdout_runs": hold_tags,
           "n_fit": int(len(fit)), "n_holdout": int(len(hold)),
           "ece_before": round(float(e_before), 4),
           "ece_after": round(float(e_after), 4),
           "gate_within_10pts": bool(gate),
           "base_rate_holdout": round(float(hold.hit.mean()), 4)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwritten: {a.out}")


if __name__ == "__main__":
    main()
