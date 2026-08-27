#!/usr/bin/env python3
"""
Regenerate the line dataset with common random numbers, and compute
SENSITIVITY-BASED ground truth.

Why this replaces dataset/line/. The first version labelled the bottleneck
with the active-period formula. Scoring an active-period detector against
that is circular - the detector recomputes the label's own definition from
the label's own inputs, and scores 100% by identity.

Sensitivity truth is definitionally independent: the constraint is the
station whose speed-up actually produces more cars. We measure it by
re-running the shift with one station 10% faster, every other random draw
held identical, and counting the extra completions per 30-minute block.

Cost: (20 stations + 1 baseline) x N runs full-shift simulations.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.line import (N_SPINE, N_SUB, SHIFT_S, build_config,  # noqa: E402
                       reseed_streams, simulate)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "dataset", "line_v2")
BLOCK_MIN = 30
PERTURB = 0.80            # 20% faster - a 10% nudge gave integer car counts
                          # too coarse to separate first place from second
N_REPS = 4                # replications, averaged, to break integer ties
RUN_PLAN = (["degrade_ramp"] * 8 + ["degrade_step"] * 6 +
            ["station_down"] * 6 + ["none"] * 8)


def block_counts(completions, block_min=BLOCK_MIN):
    n = len(completions) // block_min * block_min
    return completions[:n].reshape(-1, block_min).sum(axis=1)


def main():
    os.makedirs(os.path.join(OUT, "runs"), exist_ok=True)
    manifest, truth_rows = [], []

    for rid, kind in enumerate(RUN_PLAN, start=1):
        cfg = build_config(seed=880000 + rid, fault_kind=kind)
        base = simulate(cfg, record=True)
        base_blocks = block_counts(base["completions"])

        # ---- sensitivity, averaged over replications of the same plant.
        # Within a replication the baseline and every perturbation share
        # one random stream (CRN), so the difference is caused by the
        # perturbation alone. Across replications the stream changes, so
        # averaging removes the luck of one particular shift.
        n_blocks = len(base_blocks)
        gains = np.zeros((N_SPINE, n_blocks))
        for rep in range(N_REPS):
            c = cfg if rep == 0 else reseed_streams(cfg, 4400000 + rid * 97 + rep)
            bb = block_counts(simulate(c)["completions"])
            for i in range(N_SPINE):
                ss = np.ones(N_SPINE + N_SUB)
                ss[i] = PERTURB
                gains[i] += (block_counts(simulate(c, speed_scale=ss)["completions"])
                             - bb) / N_REPS

        for b in range(n_blocks):
            col = gains[:, b]
            order = np.argsort(-col)
            best, second = int(order[0]), int(order[1])
            truth_rows.append(dict(
                run_id=rid, block=b,
                block_start_min=b * BLOCK_MIN,
                primary=f"S{best+1:02d}",
                secondary=f"S{second+1:02d}",
                gain_primary=round(float(col[best]), 3),
                gain_secondary=round(float(col[second]), 3),
                margin=round(float(col[best] - col[second]), 3),
                n_stations_with_gain=int((col > 0).sum()),
                baseline_cars=int(base_blocks[b])))

        # ---- write observed logs (dark stations removed)
        rd = os.path.join(OUT, "runs", f"run_{rid:02d}")
        hd = os.path.join(rd, "hidden")
        os.makedirs(hd, exist_ok=True)
        dark = set(base["dark"])

        sc = pd.DataFrame(base["scans"], columns=["vin", "station_id", "event", "t_s"])
        st = pd.DataFrame(base["states"], columns=["station_id", "state", "t_s"])
        bf = pd.DataFrame(base["buffers"], columns=["buffer_id", "level", "capacity", "t_s"])
        sc.to_csv(os.path.join(hd, "unit_scan_full.csv"), index=False)
        st.to_csv(os.path.join(hd, "station_state_full.csv"), index=False)
        sc[~sc.station_id.isin(dark)].to_csv(os.path.join(rd, "unit_scan.csv"), index=False)
        st[~st.station_id.isin(dark)].to_csv(os.path.join(rd, "station_state.csv"), index=False)
        bf.to_csv(os.path.join(rd, "buffer_level.csv"), index=False)
        pd.DataFrame([r for r in truth_rows if r["run_id"] == rid]).to_csv(
            os.path.join(hd, "sensitivity_truth.csv"), index=False)

        f = cfg.fault
        manifest.append(dict(
            run_id=rid, seed=cfg.seed, fault_kind=kind,
            fault_station=(f"S{f['idx']+1:02d}" if f["idx"] >= 0 else ""),
            fault_onset_s=f["onset_s"], fault_magnitude=round(f["magnitude"], 3),
            dark_stations=";".join(sorted(dark)),
            jph=round(base["total"] / (SHIFT_S / 3600), 1),
            vehicles_completed=base["total"]))
        print(f"run_{rid:02d} {kind:13s} JPH={manifest[-1]['jph']:5.1f} "
              f"dark={manifest[-1]['dark_stations']}", flush=True)

    pd.DataFrame(manifest).to_csv(os.path.join(OUT, "run_manifest.csv"), index=False)
    tr = pd.DataFrame(truth_rows)
    tr.to_csv(os.path.join(OUT, "sensitivity_truth.csv"), index=False)

    print("\n%d runs, %d labelled blocks (%d reps, %.0f%% perturbation)"
          % (len(manifest), len(tr), N_REPS, 100 * (1 - PERTURB)))
    print("blocks where >=1 station yields a gain: %.0f%%"
          % (100 * (tr.n_stations_with_gain > 0).mean()))
    print("median stations with any positive gain per block: %.0f"
          % tr.n_stations_with_gain.median())
    print("median gain of the top station: %.2f cars per 30 min"
          % tr.gain_primary.median())
    print("blocks where top exactly ties second: %.0f%%"
          % (100 * (tr.margin <= 0).mean()))
    print("blocks with a clear winner (margin >= 0.5 cars): %.0f%%"
          % (100 * (tr.margin >= 0.5).mean()))


if __name__ == "__main__":
    main()
