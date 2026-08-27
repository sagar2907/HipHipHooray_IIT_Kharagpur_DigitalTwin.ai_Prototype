#!/usr/bin/env python3
"""Defect #7: is `confidence` calibrated? Measure, then fit, then re-measure.

Train/test split by RUN so no block from a calibration run is scored.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from twin.detect import Detector      # noqa
from twin.events import load_run      # noqa

BASE = os.path.join(ROOT, "dataset", "v5")
FLOW = os.path.join(BASE, "flow")
BLOCK_MIN = 60


def collect(runs, truth):
    rows = []
    for k, tag in enumerate(runs):
        rd = os.path.join(FLOW, "runs", tag)
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
                rows.append(dict(run=tag, score=v.confidence_raw,
                                 hit=int(v.constraint == tr.primary)))
    return pd.DataFrame(rows)


def ece(score, hit, n_bins=10):
    """Expected calibration error: mean |claimed - observed|, weighted."""
    df = pd.DataFrame(dict(s=score, h=hit))
    if df.empty:
        return float("nan"), pd.DataFrame()
    df["b"] = pd.cut(df.s, np.linspace(0, 1.0001, n_bins + 1), labels=False,
                     include_lowest=True)
    g = df.groupby("b").agg(claimed=("s", "mean"), observed=("h", "mean"),
                            n=("h", "size")).dropna()
    e = float((g.n / g.n.sum() * (g.claimed - g.observed).abs()).sum())
    return e, g


def main(limit=60):
    truth = pd.read_csv(os.path.join(BASE, "truth", "sensitivity.csv"))
    runs = [r for r in truth.run.unique() if r.startswith("L1")][:limit]
    split = len(runs) // 2
    tr_runs, te_runs = runs[:split], runs[split:]
    print(f"calibration runs: {len(tr_runs)}   held-out runs: {len(te_runs)}")

    train = collect(tr_runs, truth)
    test = collect(te_runs, truth)
    print(f"train samples {len(train)}, test samples {len(test)}")

    e0, g0 = ece(test.score, test.hit)
    print(f"\n=== BEFORE (raw score used as if it were a probability) ===")
    print(f"ECE = {e0:.3f}")
    print(g0.round(3).to_string())

    # fit on train only
    d = Detector.__new__(Detector)
    d._calibrator = None
    Detector.fit_calibration(d, list(zip(train.score, train.hit)))
    cal = np.array([d._calibrator(s) for s in test.score])
    e1, g1 = ece(cal, test.hit)
    print(f"\n=== AFTER (fitted on {len(tr_runs)} separate runs) ===")
    print(f"ECE = {e1:.3f}   (improvement {100*(e0-e1)/e0:.0f}%)")
    print(g1.round(3).to_string())

    print(f"\noverall observed hit rate on held-out: {test.hit.mean():.3f}")
    print(f"mean raw score claimed              : {test.score.mean():.3f}")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else 60)
