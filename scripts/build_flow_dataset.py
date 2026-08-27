#!/usr/bin/env python3
"""
Build the v3 flow dataset: 96 single shifts across 4 layouts + 6 multi-shift
sequences, from the plant simulator (src/twin/plant.py).

Per run (dataset/v3/flow/runs/<layout>_run_NN/):
  unit_scan.csv, station_state.csv, buffer_level.csv   observed (dark removed)
  andon_log.csv, rework_log.csv, calendar.csv          observed
  hidden/unit_scan_full.csv, station_state_full.csv    include dark stations
  hidden/fault.json                                    injected fault truth

Run matrix:
  L1: 60 runs - 30 faulted (6 per fault kind), 30 none (false-alarm CI)
  L2/L3/L4: 12 runs each - 6 faulted, 6 none (layout transfer)
  6x L1 sequences of 3 consecutive shifts (horizon-60 forecasting)
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.plant import build_plant_config, simulate_plant          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "dataset", "v4", "flow")
FAULTS = ("degrade_ramp", "degrade_step", "station_down",
          "material_starvation", "quality_hold")


def write_run(tag, cfg, res):
    rd = os.path.join(OUT, "runs", tag)
    hd = os.path.join(rd, "hidden")
    os.makedirs(hd, exist_ok=True)
    dark = set(res["dark"])

    sc = pd.DataFrame(res["scans"], columns=["vin", "station_id", "event", "t_s"])
    st = pd.DataFrame(res["states"], columns=["station_id", "state", "t_s"])
    sc.to_csv(os.path.join(hd, "unit_scan_full.csv"), index=False)
    st.to_csv(os.path.join(hd, "station_state_full.csv"), index=False)
    sc[~sc.station_id.isin(dark)].to_csv(os.path.join(rd, "unit_scan.csv"), index=False)
    st[~st.station_id.isin(dark)].to_csv(os.path.join(rd, "station_state.csv"), index=False)
    pd.DataFrame(res["buffers"], columns=["buffer_id", "level", "capacity", "t_s"]) \
        .to_csv(os.path.join(rd, "buffer_level.csv"), index=False)
    pd.DataFrame(res["andon"], columns=["station_id", "reason", "t_s", "dur_s"]) \
        .to_csv(os.path.join(rd, "andon_log.csv"), index=False)
    pd.DataFrame(res["rework"], columns=["vin", "event", "t_s"]) \
        .to_csv(os.path.join(rd, "rework_log.csv"), index=False)
    pd.DataFrame(res["calendar"]).to_csv(os.path.join(rd, "calendar.csv"), index=False)
    with open(os.path.join(hd, "fault.json"), "w") as fh:
        json.dump({k: v for k, v in cfg.fault.items()}, fh)


def main():
    os.makedirs(os.path.join(OUT, "runs"), exist_ok=True)
    manifest = []
    plan = ([("L1", k) for k in FAULTS for _ in range(6)] + [("L1", "none")] * 30 +
            [(L, k) for L in ("L2", "L3", "L4")
             for k in (list(FAULTS) + ["none"])[:12]
             for _ in ([1] if k in FAULTS else [1])])
    # L2-L4: 5 faults + 7 none each? Keep it simple and explicit instead:
    plan = ([("L1", k) for k in FAULTS for _ in range(6)] + [("L1", "none")] * 30)
    for L in ("L2", "L3", "L4"):
        plan += [(L, k) for k in FAULTS] + [(L, "none")] * 7

    rid = 0
    for layout, kind in plan:
        rid += 1
        seed = 5510000 + rid
        cfg = build_plant_config(seed, layout, kind, n_shifts=1)
        res = simulate_plant(cfg, record=True)
        tag = f"{layout}_run_{rid:03d}"
        write_run(tag, cfg, res)
        f = cfg.fault
        manifest.append(dict(
            run=tag, layout=layout, seed=seed, n_shifts=1, fault_kind=kind,
            fault_station=(f"S{f['idx']+1:02d}" if f["idx"] >= 0 else ""),
            fault_onset_s=f["onset_s"], fault_magnitude=round(f["magnitude"], 3),
            fault_duration_s=f["duration_s"],
            dark_stations=";".join(res["dark"]),
            jph=round(res["total"] / (cfg.horizon_s / 3600), 1),
            completed=res["total"], rework_visits=res["rework_visits"]))
        if rid % 12 == 0:
            print(f"...{rid}/{len(plan)} runs", flush=True)

    # multi-shift sequences for long-horizon forecast labels
    for s in range(6):
        rid += 1
        seed = 5560000 + s
        kind = FAULTS[s % len(FAULTS)]
        cfg = build_plant_config(seed, "L1", kind, n_shifts=3)
        res = simulate_plant(cfg, record=True)
        tag = f"L1_seq_{s+1:02d}"
        write_run(tag, cfg, res)
        f = cfg.fault
        manifest.append(dict(
            run=tag, layout="L1", seed=seed, n_shifts=3, fault_kind=kind,
            fault_station=f"S{f['idx']+1:02d}", fault_onset_s=f["onset_s"],
            fault_magnitude=round(f["magnitude"], 3),
            fault_duration_s=f["duration_s"],
            dark_stations=";".join(res["dark"]),
            jph=round(res["total"] / (cfg.horizon_s / 3600), 1),
            completed=res["total"], rework_visits=res["rework_visits"]))
        print(f"seq {s+1}/6 done", flush=True)

    m = pd.DataFrame(manifest)
    m.to_csv(os.path.join(OUT, "run_manifest.csv"), index=False)
    print("\n%d runs written" % len(m))
    print("JPH by layout (single shifts, no-fault vs fault):")
    ss = m[m.n_shifts == 1]
    print(ss.pivot_table(index="layout", columns=ss.fault_kind.eq("none"),
                         values="jph", aggfunc="mean").round(1).to_string())
    cons = sum(any(int(b[1:]) - int(a[1:]) == 1 for a, b in
                   zip(sorted(r.split(";")), sorted(r.split(";"))[1:]))
               for r in m.dark_stations)
    print(f"runs with consecutive dark pair: {cons}/{len(m)}")
    print(f"mean rework visits per shift: {ss.rework_visits.mean():.0f}")


if __name__ == "__main__":
    main()
