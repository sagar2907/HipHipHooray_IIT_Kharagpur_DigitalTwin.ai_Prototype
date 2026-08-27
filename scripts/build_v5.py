#!/usr/bin/env python3
"""
Build the v5 UNIFIED dataset.

What makes v5 different from everything before it: the tools live ON the line.

Until now `dataset/v3/process` (tool telemetry) and `dataset/v4/flow` (line
events) were separate universes with different VINs, different stations and
different clocks. That made the project's headline claim - the joint
stop-or-continue decision, where the same drifting tool gets opposite correct
answers depending on whether its station is currently the constraint -
literally untestable, because there was no way to join the two.

In v5 each flow run generates tool telemetry from that run's OWN vehicle
sequence and timestamps. The join key (run, station_id, vin) is exact, so you
can ask: "tool at S07 started drifting at 10:14 - was S07 the constraint at
10:14?" That question is the product.

Also new in v5:
  - conveyor transit time between stations (bracketing finally has a transit
    term to subtract, and it is a distribution, not a constant)
  - micro-stops: brief pauses that inflate cycle time and appear in NO
    downtime log, recoverable only from dwell anomalies
  - measurement-layer artifacts applied to OBSERVED files only: per-controller
    clock skew, dropped scans, duplicate scans, NULL bursts, temporary sensor
    dropouts. Truth files stay clean.

Layout:
  dataset/v5/flow/run_manifest.csv
  dataset/v5/flow/runs/<tag>/
      unit_scan.csv station_state.csv buffer_level.csv
      andon_log.csv rework_log.csv calendar.csv tool_readings.csv
      hidden/ unit_scan_full.csv station_state_full.csv microstops.csv
              tool_truth.csv fault.json artifacts.csv observability.csv
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.plant import build_plant_config, simulate_plant          # noqa: E402
from twin.tools import FAMILIES, ToolSpec, generate_tool           # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "v5", "flow")
T0 = pd.Timestamp("2026-06-01 06:00:00")
FAULTS = ("degrade_ramp", "degrade_step", "station_down",
          "material_starvation", "quality_hold")

# tool conditions drawn per run; healthy dominates as it would in a plant
TOOL_CONDITIONS = (["healthy"] * 5 + ["gradual_wear", "sensor_bias",
                                      "pure_transducer_drift", "spread_only",
                                      "lubrication_loss", "overtorque",
                                      "intermittent"])


# --------------------------------------------------------------- tools on line
def tools_for_run(rng, scans_full, stations, run_tag):
    """Generate tool telemetry driven by this run's real vehicle sequence.

    For each chosen station we take the actual VINs processed there and the
    actual out-scan times, then synthesise readings indexed to those events.
    """
    rows, truth = [], []
    outs = scans_full[scans_full.event == "out"]
    for k, st in enumerate(stations):
        g = outs[outs.station_id == st].sort_values("t_s")
        n_ops = len(g)
        if n_ops < 120:
            continue
        cond = str(rng.choice(TOOL_CONDITIONS))
        fam = "nutrunner"
        target = float(rng.uniform(28, 88))
        tolp = float(rng.uniform(0.08, 0.14))
        # A station sees only ~300 fastenings per shift, so real-world wear
        # timescales (days) would leave every fault still invisible at the end
        # of the run. Compress onset and wear span so the fault matures inside
        # the observation window. Deep failure-mode work still belongs on
        # dataset/v3/process, where each tool has 20,000 operations; these
        # line-tools exist to make the JOINT flow-vs-quality decision testable.
        onset = int(rng.integers(int(n_ops * 0.20), int(n_ops * 0.45))) if cond != "healthy" else -1
        wear = int(rng.integers(max(40, n_ops // 12), max(90, n_ops // 5))) if cond != "healthy" else -1
        tid = f"{run_tag}-T{st}"
        spec = ToolSpec(tool_id=tid, family=fam, station_id=int(st[1:]),
                        condition=cond, target=round(target, 1), tol_pct=round(tolp, 3),
                        onset_op=onset, wear_ops=wear,
                        program_id=f"PF{100+k}", clock_skew_s=0.0, service_ops=[])
        t_s = g.t_s.values.astype(float)
        # ambient follows the run's own clock, so warm-up after breaks lines up
        amb = 1.6 * np.sin(2 * np.pi * (t_s % 86400) / 86400 - 1.1)
        ch, true_prim, tdef, nok, tr, _ = generate_tool(
            rng, spec, n_ops, amb, np.zeros(n_ops))
        tol = target * tolp
        df = pd.DataFrame(dict(
            run=run_tag, station_id=st, tool_id=tid, program_id=spec.program_id,
            vin=g.vin.values, t_s=t_s,
            target_nm=round(target, 2), spec_low_nm=round(target - tol, 2),
            spec_high_nm=round(target + tol, 2)))
        for name, arr in ch.items():
            if name == "cap_count":
                continue
            df[name] = np.round(arr, 3)
        df["result_status"] = np.where(nok, "NOK", "OK")
        rows.append(df)
        tr.update(run=run_tag, station_id=st, n_ops=n_ops,
                  onset_t_s=float(t_s[onset]) if onset >= 0 else -1.0)
        truth.append(tr)
    if not rows:
        return pd.DataFrame(), pd.DataFrame()
    return pd.concat(rows, ignore_index=True), pd.DataFrame(truth)


# ------------------------------------------------------- measurement artifacts
def corrupt_observed(rng, scans, states, tools, stations):
    """Apply recording artifacts to OBSERVED data only.

    These are properties of the measurement chain, not the plant, so they are
    applied after simulation and the hidden truth files stay clean. This is
    also what makes Tier B honestly 'strongly estimated' rather than 'exact' -
    a bracketed time inherits the skew of two different controllers.
    """
    log = []
    # 1. per-controller clock skew: every station's clock is a bit off
    skew = {st: float(rng.uniform(-3, 3)) for st in stations}
    scans = scans.copy()
    states = states.copy()
    scans["t_s"] = scans.t_s + scans.station_id.map(skew).fillna(0.0)
    states["t_s"] = states.t_s + states.station_id.map(skew).fillna(0.0)
    for st, v in skew.items():
        log.append(dict(kind="clock_skew", target=st, detail=round(v, 3)))

    # 2. dropped scans - a packet never arrives
    drop = rng.random(len(scans)) < 0.002
    log.append(dict(kind="scans_dropped", target="*", detail=int(drop.sum())))
    # 3. duplicated scans - store-and-forward replays a message
    dup = rng.random(len(scans)) < 0.0005
    log.append(dict(kind="scans_duplicated", target="*", detail=int(dup.sum())))
    scans = pd.concat([scans[~drop], scans[dup]], ignore_index=True)

    # 4. late arrivals - a gateway flushes a backlog out of order
    n_late = int(0.001 * len(scans))
    if n_late:
        idx = rng.choice(len(scans), n_late, replace=False)
        scans.loc[idx, "t_s"] = scans.loc[idx, "t_s"] + rng.uniform(30, 180, n_late)
        log.append(dict(kind="late_arrivals", target="*", detail=n_late))
    scans = scans.sort_values("t_s").reset_index(drop=True)

    # 5. NULL bursts in tool channels during a network blip
    if len(tools):
        tools = tools.copy()
        chans = [c for c in ("measured_angle_deg", "motor_current_a", "tool_temp_c")
                 if c in tools.columns]
        for tid in tools.tool_id.unique():
            if rng.random() < 0.35 and chans:
                ch = str(rng.choice(chans))
                m = tools.tool_id == tid
                n = int(m.sum())
                if n > 200:
                    s = int(rng.integers(0, n - 100))
                    ln = int(rng.integers(20, 90))
                    ix = tools.index[m][s:s + ln]
                    tools.loc[ix, ch] = np.nan
                    log.append(dict(kind="null_burst", target=f"{tid}:{ch}", detail=ln))
    return scans, states, tools, pd.DataFrame(log)


def observability_table(stations, dark, dropouts):
    rows = []
    for st in stations:
        if st in dark:
            o, note = 0.0, "permanently dark - no state, no scans"
        elif st in dropouts:
            o, note = 0.55, "temporary sensor dropout during part of the shift"
        else:
            o, note = 1.0, "fully instrumented"
        rows.append(dict(station_id=st, observability=o, note=note))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------- one run
def build_run(rid, layout, kind, n_shifts, seed):
    cfg = build_plant_config(seed, layout, kind, n_shifts)
    res = simulate_plant(cfg, record=True)
    rng = np.random.default_rng(seed ^ 0x5EED)
    tag = f"{layout}_run_{rid:03d}" if n_shifts == 1 else f"{layout}_seq_{rid:03d}"

    sc = pd.DataFrame(res["scans"], columns=["vin", "station_id", "event", "t_s"])
    stt = pd.DataFrame(res["states"], columns=["station_id", "state", "t_s"])
    spine = sorted({s for s in sc.station_id.unique() if s.startswith("S")})
    dark = set(res["dark"])

    # tools sit on stations that are NOT dark (a dark station has no controller)
    cand = [s for s in spine if s not in dark]
    n_tools = min(len(cand), 6)
    tool_st = sorted(rng.choice(cand, n_tools, replace=False).tolist())
    tools, tool_truth = tools_for_run(rng, sc, tool_st, tag)

    # temporary dropout: a station that HAS sensors loses them for a while
    drop_st = set(rng.choice([s for s in cand if s not in tool_st] or cand,
                             min(2, len(cand)), replace=False).tolist())
    obs_sc = sc[~sc.station_id.isin(dark)].copy()
    obs_st = stt[~stt.station_id.isin(dark)].copy()
    for st in drop_st:
        a = float(rng.uniform(0.2, 0.6)) * cfg.horizon_s
        b = a + float(rng.uniform(0.1, 0.25)) * cfg.horizon_s
        obs_st = obs_st[~((obs_st.station_id == st) & (obs_st.t_s >= a) & (obs_st.t_s < b))]

    obs_sc, obs_st, tools_obs, artifacts = corrupt_observed(
        rng, obs_sc, obs_st, tools, spine)

    rd = os.path.join(OUT, "runs", tag)
    hd = os.path.join(rd, "hidden")
    os.makedirs(hd, exist_ok=True)
    obs_sc.to_csv(os.path.join(rd, "unit_scan.csv"), index=False)
    obs_st.to_csv(os.path.join(rd, "station_state.csv"), index=False)
    pd.DataFrame(res["buffers"], columns=["buffer_id", "level", "capacity", "t_s"]) \
        .to_csv(os.path.join(rd, "buffer_level.csv"), index=False)
    pd.DataFrame(res["andon"], columns=["station_id", "reason", "t_s", "dur_s"]) \
        .to_csv(os.path.join(rd, "andon_log.csv"), index=False)
    pd.DataFrame(res["rework"], columns=["vin", "event", "t_s"]) \
        .to_csv(os.path.join(rd, "rework_log.csv"), index=False)
    pd.DataFrame(res["calendar"]).to_csv(os.path.join(rd, "calendar.csv"), index=False)
    if len(tools_obs):
        tools_obs.to_csv(os.path.join(rd, "tool_readings.csv"), index=False)

    sc.to_csv(os.path.join(hd, "unit_scan_full.csv"), index=False)
    stt.to_csv(os.path.join(hd, "station_state_full.csv"), index=False)
    pd.DataFrame(res["microstops"], columns=["station_id", "t_s", "dur_s"]) \
        .to_csv(os.path.join(hd, "microstops.csv"), index=False)
    if len(tool_truth):
        tool_truth.to_csv(os.path.join(hd, "tool_truth.csv"), index=False)
    artifacts.to_csv(os.path.join(hd, "artifacts.csv"), index=False)
    observability_table(spine, dark, drop_st).to_csv(
        os.path.join(hd, "observability.csv"), index=False)
    with open(os.path.join(hd, "fault.json"), "w") as fh:
        json.dump(cfg.fault, fh)

    f = cfg.fault
    return dict(run=tag, layout=layout, seed=seed, n_shifts=n_shifts,
                fault_kind=kind,
                fault_station=(f"S{f['idx']+1:02d}" if f["idx"] >= 0 else ""),
                fault_onset_s=f["onset_s"],
                fault_magnitude=round(f["magnitude"], 3),
                fault_duration_s=f["duration_s"],
                dark_stations=";".join(sorted(dark)),
                dropout_stations=";".join(sorted(drop_st)),
                tool_stations=";".join(tool_st),
                n_microstops=len(res["microstops"]),
                jph=round(res["total"] / (cfg.horizon_s / 3600), 1),
                completed=res["total"], rework_visits=res["rework_visits"])


def main():
    os.makedirs(os.path.join(OUT, "runs"), exist_ok=True)
    plan = ([("L1", k) for k in FAULTS for _ in range(12)] +
            [("L1", "none")] * 60)
    for L in ("L2", "L3", "L4"):
        plan += [(L, k) for k in FAULTS] + [(L, "none")] * 7
    man, rid = [], 0
    for layout, kind in plan:
        rid += 1
        man.append(build_run(rid, layout, kind, 1, 6610000 + rid))
        if rid % 20 == 0:
            print(f"  ...{rid}/{len(plan)} runs", flush=True)
    for s in range(6):
        rid += 1
        man.append(build_run(rid, "L1", FAULTS[s % len(FAULTS)], 3, 6660000 + s))
        print(f"  seq {s+1}/6", flush=True)

    m = pd.DataFrame(man)
    m.to_csv(os.path.join(OUT, "run_manifest.csv"), index=False)
    ss = m[m.n_shifts == 1]
    print(f"\n{len(m)} runs written")
    print(f"JPH  no-fault {ss[ss.fault_kind=='none'].jph.mean():.1f}  "
          f"faulted {ss[ss.fault_kind!='none'].jph.mean():.1f}")
    print(f"mean micro-stops/shift {ss.n_microstops.mean():.0f}")
    print(f"runs with tools: {(m.tool_stations!='').sum()}")


if __name__ == "__main__":
    main()
