#!/usr/bin/env python3
"""Test ranking-key variants for detect.py defect #6 (starved-share down-weight).

Scores each variant on the same blocks / same truth as eval_v5.py so the
numbers are directly comparable to the published 43.07 / 59.41 / 2.240.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from twin.detect import Detector          # noqa
from twin.events import load_run          # noqa

BASE = os.path.join(ROOT, "dataset", "v5")
FLOW = os.path.join(BASE, "flow")
BLOCK_MIN = 60

VARIANTS = {
    "current (eff_ct only)":   lambda r: r.effective_ct,
    "eff*(1-starved)":         lambda r: r.effective_ct * (1.0 - r.starved_share),
    "eff/(1+starved)":         lambda r: r.effective_ct / (1.0 + r.starved_share),
    "eff*(1-0.5*starved)":     lambda r: r.effective_ct * (1.0 - 0.5 * r.starved_share),
    "eff*(1-starved-blocked)": lambda r: r.effective_ct * (1.0 - r.starved_share - r.blocked_share),
}


def pick_with(det, key, at):
    rd = [x for x in det.read(at) if x.units >= 2]
    if len(rd) < 2:
        return None
    rd.sort(key=key, reverse=True)
    return rd[0].station


def block_pick(det, key, b):
    votes = {}
    for at in range(b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60, 300):
        p = pick_with(det, key, at)
        if p:
            votes[p] = votes.get(p, 0) + 1
    if not votes:
        return None
    return max(votes, key=votes.get)


def main(limit=40):
    truth = pd.read_csv(os.path.join(BASE, "truth", "sensitivity.csv"))
    runs = [r for r in truth.run.unique() if r.startswith("L1")][:limit]
    rows = []
    for k, tag in enumerate(runs):
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        det = Detector(load_run(rd, k))
        for _, tr in truth[truth.run == tag].iterrows():
            vec = np.array([float(x) for x in str(tr.gain_vector).split(";")])
            best = float(vec.max())
            if best <= 0:
                continue
            for name, key in VARIANTS.items():
                p = block_pick(det, key, int(tr.block))
                if p is None:
                    continue
                i = int(p[1:]) - 1
                got = float(vec[i]) if 0 <= i < len(vec) else 0.0
                rows.append(dict(run=tag, block=int(tr.block), variant=name,
                                 margin=float(tr.margin),
                                 top1=int(p == tr.primary),
                                 regret=best - got))
        if (k + 1) % 10 == 0:
            print(f"  ...{k+1}/{len(runs)}", flush=True)

    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "rank_variants.csv"), index=False)
    for lbl, sub in [("ALL BLOCKS", r), ("STRONG (margin>=2)", r[r.margin >= 2])]:
        n = sub.groupby(['run', 'block']).ngroups
        t = pd.DataFrame({
            "top1%": 100 * sub.groupby("variant").top1.mean(),
            "regret": sub.groupby("variant").regret.mean(),
        }).reindex(VARIANTS.keys()).round(3)
        print(f"\n--- {lbl} (n={n} blocks) ---")
        print(t.to_string())


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else 40)
