#!/usr/bin/env python3
"""
Ground-truth labels for the v3 flow dataset. Multiprocessing throughout.

Label sets (dataset/v3/truth/):

  sensitivity.csv       PER-BLOCK sensitivity: station i sped up 20% only
                        within the scored 30-min block, all other draws
                        common. Fixes the whole-shift contamination of the
                        v2 labels (a late block's label no longer inherits
                        eleven blocks of accumulated upstream difference).
                        4 replications averaged. Full marginal-value VECTOR
                        kept per block, not just the argmax - when nine
                        stations show gain, the vector is the honest answer.
  persistence.csv       constraint episodes (station, start block, length)
  forecast_labels.csv   for each block: the primary at t, t+1, t+2 blocks
                        ahead (30/60/90 min horizons on block granularity)
  intervention.csv      for faulted L1 runs: paired-CRN outcomes of
                        fix-at-onset vs fix-at-next-break vs no-fix,
                        4 replications, distributions not single runs

The sensitivity harness is the compute hog: per run,
(n_stations x n_blocks x reps) + baselines simulations. Parallelised over
runs with ProcessPoolExecutor.
"""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.calendar import SHIFT_S                                   # noqa: E402
from twin.layouts import LAYOUTS                                    # noqa: E402
from twin.plant import build_plant_config, simulate_plant           # noqa: E402

FLOW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "dataset", "v5", "flow")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "dataset", "v5", "truth")
# 60-minute blocks (was 30): twice the cars per block, so the integer car
# counts that decide the label carry roughly sqrt(2) less relative noise -
# and 60 min matches the longest forecast horizon we intend to report.
# Halving the block count also halves the compute.
BLOCK_MIN = 60
# 30% speed-up (was 20%): a larger perturbation lifts the measured gain well
# clear of the +/-1 car quantisation floor.
PERTURB = 0.70
N_REPS = 4


def block_counts(completions, block_min=BLOCK_MIN):
    m = len(completions) // block_min * block_min
    return completions[:m].reshape(-1, block_min).sum(axis=1)


def sensitivity_for_run(args):
    """Per-block sensitivity for one run.

    The perturbation is WINDOWED: station i runs 20% faster only for units
    started inside the scored block (simulate_plant's `perturb` argument).
    CRN guarantees the pre-block trajectory is identical to the baseline,
    so the within-block completion delta is the clean counterfactual."""
    tag, layout, seed, kind, n_shifts = args
    n = LAYOUTS[layout].n_spine
    rows = []
    reps = [seed] + [9200000 + seed % 100000 * 7 + r for r in range(1, N_REPS)]
    for rep_i, rs in enumerate(reps):
        cfg = build_plant_config(seed, layout, kind, n_shifts)
        if rep_i > 0:
            # fresh noise, same plant: rebuild on a derived seed, then copy
            # every structural field from the canonical config
            cfg2 = build_plant_config(rs, layout, kind, n_shifts)
            for f in ("mean_ct", "sigma", "caps", "feeder_ct", "variant_mult",
                      "mtbf", "mttr_mu", "dark", "fault", "changeover_at",
                      "pm_station"):
                setattr(cfg2, f, getattr(cfg, f))
            cfg = cfg2
        base = block_counts(simulate_plant(cfg)["completions"])
        n_blocks = len(base)
        for b in range(n_blocks):
            b0, b1 = b * BLOCK_MIN * 60, (b + 1) * BLOCK_MIN * 60
            for i in range(n):
                # nothing after b1 can influence the scored block, so the
                # simulation stops there - halves total compute
                r = simulate_plant(cfg, perturb=(i, b0, b1, PERTURB),
                                   stop_at_s=b1)
                g = block_counts(r["completions"][: b1 // 60])[b] - base[b]
                rows.append((tag, b, i, rep_i, float(g)))
    df = pd.DataFrame(rows, columns=["run", "block", "station", "rep", "gain"])
    agg = df.groupby(["run", "block", "station"]).gain.mean().reset_index()
    return agg


def sensitivity_all(man, workers):
    """Checkpointed: each run's result lands in truth/partial/<run>.csv the
    moment it finishes, and already-finished runs are skipped on restart.
    A killed job (app restart, power cut) costs at most one run's compute,
    not the whole campaign."""
    part_dir = os.path.join(OUT, "partial")
    os.makedirs(part_dir, exist_ok=True)
    todo_all = [(r.run, r.layout, int(r.seed), r.fault_kind, int(r.n_shifts))
                for _, r in man.iterrows() if r.n_shifts == 1]
    done = {f[:-4] for f in os.listdir(part_dir) if f.endswith(".csv")}
    todo = [t for t in todo_all if t[0] not in done]
    if done:
        print(f"  resuming: {len(done)} runs already checkpointed, "
              f"{len(todo)} to go", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(sensitivity_for_run, t): t[0] for t in todo}
        from concurrent.futures import as_completed
        for i, fut in enumerate(as_completed(futures)):
            res = fut.result()
            res.to_csv(os.path.join(part_dir, f"{futures[fut]}.csv"), index=False)
            print(f"  sensitivity {len(done)+i+1}/{len(todo_all)} runs", flush=True)
    return pd.concat(
        [pd.read_csv(os.path.join(part_dir, f"{t[0]}.csv")) for t in todo_all],
        ignore_index=True)


def labels_from_vectors(sens):
    rows = []
    for (run, block), g in sens.groupby(["run", "block"]):
        v = g.sort_values("station")
        gains = v.gain.values
        order = np.argsort(-gains)
        rows.append(dict(run=run, block=int(block),
                         primary=f"S{order[0]+1:02d}",
                         secondary=f"S{order[1]+1:02d}",
                         gain_primary=round(float(gains[order[0]]), 3),
                         gain_secondary=round(float(gains[order[1]]), 3),
                         margin=round(float(gains[order[0]] - gains[order[1]]), 3),
                         n_positive=int((gains > 0.05).sum()),
                         gain_vector=";".join(f"{x:.2f}" for x in gains)))
    return pd.DataFrame(rows)


def persistence_and_forecast(lab):
    """Persistence episodes, plus forecast labels at explicit horizons.

    Blocks are 60 minutes, so h1/h2/h3 are the 60/120/180-minute horizons.
    We also carry the future block's MARGIN, because a forecast that names the
    right station in a block where nothing dominates is not worth scoring -
    the horizon curve should be reported on blocks that had a real answer.
    """
    per, fc = [], []
    for run, g in lab.groupby("run"):
        g = g.sort_values("block").reset_index(drop=True)
        ep_start, cur = 0, g.primary.iloc[0]
        for i in range(1, len(g) + 1):
            if i == len(g) or g.primary.iloc[i] != cur:
                per.append(dict(run=run, station=cur, start_block=ep_start,
                                length_blocks=i - ep_start,
                                mean_margin=round(float(
                                    g.margin.iloc[ep_start:i].mean()), 3)))
                if i < len(g):
                    ep_start, cur = i, g.primary.iloc[i]
        for i in range(len(g)):
            row = dict(run=run, block=int(g.block.iloc[i]),
                       now=g.primary.iloc[i],
                       now_margin=float(g.margin.iloc[i]))
            for h in (1, 2, 3):
                j = i + h
                row[f"h{h}_primary"] = g.primary.iloc[j] if j < len(g) else ""
                row[f"h{h}_margin"] = float(g.margin.iloc[j]) if j < len(g) else np.nan
                row[f"h{h}_changed"] = (int(g.primary.iloc[j] != g.primary.iloc[i])
                                        if j < len(g) else -1)
            fc.append(row)
    return pd.DataFrame(per), pd.DataFrame(fc)


def intervention_outcomes(man, workers):
    """Paired-CRN comparison of intervention policies on faulted L1 runs.

    All three arms share ONE PlantConfig - identical random streams, andon
    schedule, everything - and differ only in the fault dict. Building a
    second config with a different fault kind would consume the RNG
    differently and silently unpair the comparison (found the hard way)."""
    import copy
    rows = []
    faulted = man[(man.layout == "L1") & (man.fault_kind != "none")
                  & (man.n_shifts == 1)].head(20)
    for _, r in faulted.iterrows():
        cfg = build_plant_config(int(r.seed), "L1", r.fault_kind, 1)
        f = cfg.fault
        base = simulate_plant(cfg)["total"]

        cfg_fix = copy.copy(cfg)                    # fault never happens
        cfg_fix.fault = dict(f, kind="none", idx=-1)
        fixed = simulate_plant(cfg_fix)["total"]

        cfg_b = copy.copy(cfg)                      # fault ends at next break
        nb = min((s for s, d in cfg.cal.breaks if s > f["onset_s"]),
                 default=SHIFT_S)
        if f["kind"] in ("degrade_ramp", "degrade_step"):
            cfg_b.fault = dict(f, end_s=nb)
        else:
            cfg_b.fault = dict(f, duration_s=min(f["duration_s"],
                                                 max(0, nb - f["onset_s"])))
        at_break = simulate_plant(cfg_b)["total"]

        rows.append(dict(run=r.run, fault_kind=r.fault_kind,
                         fault_station=r.fault_station,
                         cars_no_fix=base, cars_fix_at_onset=fixed,
                         cars_fix_at_break=at_break,
                         cost_of_waiting=fixed - at_break,
                         cost_of_never_fixing=fixed - base))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=max(os.cpu_count() - 2, 2))
    ap.add_argument("--subset", type=int, default=0,
                    help="only first N runs (validation pass)")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    man = pd.read_csv(os.path.join(FLOW, "run_manifest.csv"))
    if args.subset:
        man = man.head(args.subset)

    print(f"sensitivity: {len(man[man.n_shifts == 1])} runs, "
          f"{args.workers} workers")
    sens = sensitivity_all(man, args.workers)
    sens.to_csv(os.path.join(OUT, "sensitivity_raw.csv"), index=False)
    lab = labels_from_vectors(sens)
    lab.to_csv(os.path.join(OUT, "sensitivity.csv"), index=False)

    per, fc = persistence_and_forecast(lab)
    per.to_csv(os.path.join(OUT, "persistence.csv"), index=False)
    fc.to_csv(os.path.join(OUT, "forecast_labels.csv"), index=False)

    print("intervention outcomes (paired CRN)...")
    iv = intervention_outcomes(man, args.workers)
    iv.to_csv(os.path.join(OUT, "intervention.csv"), index=False)

    print("\nblocks labelled: %d | clear winner (margin>=0.5): %.0f%%" % (
        len(lab), 100 * (lab.margin >= 0.5).mean()))
    print("median stations with positive gain: %.0f" % lab.n_positive.median())
    print("median constraint episode length: %.1f blocks" %
          per.length_blocks.median())
    if len(iv):
        print("median cost of waiting for the break: %.0f cars" %
              iv.cost_of_waiting.median())
    print("done.")
