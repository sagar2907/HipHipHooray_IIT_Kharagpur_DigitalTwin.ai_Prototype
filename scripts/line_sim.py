#!/usr/bin/env python3
"""
Assembly line flow simulator and event-log generator.

Produces the FLOW half of the DigitalTwin.ai dataset: the event streams a
real plant emits (boundary scans, station states, buffer levels) plus the
hidden ground truth (fault injections, dark-station scans, per-minute
bottleneck labels) that makes warning lead time measurable.

Line model
  - 20-station serial spine (S01..S20), buffer capacity 2-5 between them.
  - A 3-station subassembly feeder (A01..A03) merging at S12: S12 cannot
    start a vehicle unless a subassembly is available. This makes topology
    matter - starving A01 eventually starves the spine at S12.
  - 3 product variants with station-specific time multipliers.
  - Lognormal cycle times, per-station means randomized per run (52-58 s
    at a 60 s takt), so the natural bottleneck differs run to run.
  - Background failures: per-station random breakdowns (MTBF 2-4 h,
    MTTR 3-8 min lognormal).
  - 1-second tick resolution; stations updated downstream-first so a
    release frees buffer space within the same tick.

Fault injection (the prediction target)
  degrade_ramp   one station's mean cycle time ramps up 10-30% over
                 20-40 minutes starting at a known onset  (drift)
  degrade_step   the same but instantaneous                (step)
  station_down   a forced 10-25 minute stoppage            (breakdown)
  none           no injected fault (false-alarm measurement runs)

Dark stations
  3 spine stations per run emit NOTHING in the observed files - no scans,
  no states. Their events exist only in hidden/ for validating virtual
  sensing. Buffer levels remain observed (PLC counters exist even where
  station controllers do not expose tags).

Ground truth bottleneck label
  Roser's active-period criterion computed with full knowledge: per
  minute, the spine station with the longest average uninterrupted active
  (working-or-down) period in the trailing 10-minute window.

Outputs (dataset/line/):
  run_manifest.csv                     one row per run: config + fault + KPIs
  runs/run_NN/unit_scan.csv            vin, station, event(in|out), t_s   [observed]
  runs/run_NN/station_state.csv        station, state, t_s (transitions)  [observed]
  runs/run_NN/buffer_level.csv         buffer, level, capacity, t_s       [observed]
  runs/run_NN/hidden/unit_scan_full.csv       includes dark stations
  runs/run_NN/hidden/station_state_full.csv   includes dark stations
  runs/run_NN/hidden/bottleneck_truth.csv     minute, primary, secondary
"""

import os
import numpy as np
import pandas as pd
from collections import deque

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "line")
SHIFT_S = 8 * 3600
N_SPINE = 20
MERGE_AT = 12                 # S12 consumes one subassembly per vehicle
N_SUB = 3
WINDOW_S = 600                # bottleneck truth window

RUN_PLAN = (["degrade_ramp"] * 8 + ["degrade_step"] * 6 +
            ["station_down"] * 6 + ["none"] * 8)


class Station:
    def __init__(self, name, rng, mean_ct, sigma):
        self.name = name
        self.rng = rng
        self.mean_ct = mean_ct          # may be changed by fault injection
        self.sigma = sigma
        self.unit = None                # (vin, variant)
        self.remaining = 0.0
        self.state = "starved"
        self.down_left = 0.0
        self.mtbf = rng.uniform(2, 4) * 3600
        self.mttr_mu = rng.uniform(3, 8) * 60

    def sample_ct(self, variant_mult):
        mu = np.log(self.mean_ct * variant_mult)
        return float(self.rng.lognormal(mu, self.sigma))

    def fail_check(self, dt=1.0):
        if self.state == "working" and self.rng.random() < dt / self.mtbf:
            self.down_left = float(self.rng.lognormal(np.log(self.mttr_mu), 0.35))
            return True
        return False


class Recorder:
    def __init__(self):
        self.scans = []            # (vin, station, event, t)
        self.states = {}           # station -> list of (state, t_start)
        self.buffers = []          # (buffer, level, cap, t)

    def state(self, st, new, t):
        log = self.states.setdefault(st, [])
        if not log or log[-1][0] != new:
            log.append((new, t))

    def scan(self, vin, st, ev, t):
        self.scans.append((vin, st, ev, t))

    def buf(self, name, level, cap, t):
        self.buffers.append((name, level, cap, t))


def simulate(run_id, fault_kind, seed):
    rng = np.random.default_rng(seed)
    rec = Recorder()

    # ------------------------------------------------ randomized line config
    spine = [Station(f"S{i+1:02d}", rng, rng.uniform(52, 58), rng.uniform(0.06, 0.14))
             for i in range(N_SPINE)]
    subs = [Station(f"A{i+1:02d}", rng, rng.uniform(50, 56), rng.uniform(0.06, 0.12))
            for i in range(N_SUB)]
    caps = [int(rng.integers(2, 6)) for _ in range(N_SPINE - 1)]
    bufs = [deque() for _ in range(N_SPINE - 1)]            # B01..B19
    sub_caps = [int(rng.integers(2, 5)) for _ in range(N_SUB - 1)] + [4]
    sub_bufs = [deque() for _ in range(N_SUB)]              # after A01,A02,A03->merge
    var_mult = rng.normal(1.0, 0.05, size=(3, N_SPINE + N_SUB)).clip(0.85, 1.18)

    # ------------------------------------------------------- fault schedule
    fault = dict(kind=fault_kind, station="", onset_s=-1, magnitude=0.0,
                 ramp_s=0, duration_s=0)
    if fault_kind != "none":
        fs = int(rng.integers(2, N_SPINE))                   # S02..S19 index
        fault["station"] = spine[fs].name
        fault["onset_s"] = int(rng.uniform(1.5, 4.5) * 3600)
        if fault_kind == "degrade_ramp":
            fault["magnitude"] = float(rng.uniform(0.10, 0.30))
            fault["ramp_s"] = int(rng.uniform(20, 40) * 60)
        elif fault_kind == "degrade_step":
            fault["magnitude"] = float(rng.uniform(0.10, 0.30))
        elif fault_kind == "station_down":
            fault["duration_s"] = int(rng.uniform(10, 25) * 60)
        fault["_idx"] = fs
    base_means = [s.mean_ct for s in spine]

    dark = sorted(rng.choice(np.arange(1, N_SPINE - 1), 3, replace=False).tolist())
    dark_names = {spine[i].name for i in dark}

    vin_counter = [0]
    def new_vin():
        vin_counter[0] += 1
        return f"L{run_id:02d}V{vin_counter[0]:05d}"

    sub_counter = [0]
    def new_sub():
        sub_counter[0] += 1
        return f"L{run_id:02d}U{sub_counter[0]:05d}"

    completed = 0
    for st in spine + subs:
        rec.state(st.name, st.state, 0)

    # ------------------------------------------------------------ tick loop
    for t in range(SHIFT_S):
        # fault application
        if fault["onset_s"] == t and fault_kind == "station_down":
            s = spine[fault["_idx"]]
            s.down_left = float(fault["duration_s"])
        if fault_kind in ("degrade_ramp", "degrade_step") and fault["onset_s"] >= 0 \
                and t >= fault["onset_s"]:
            s = spine[fault["_idx"]]
            if fault_kind == "degrade_step":
                f = 1.0 + fault["magnitude"]
            else:
                f = 1.0 + fault["magnitude"] * min(1.0, (t - fault["onset_s"]) / fault["ramp_s"])
            s.mean_ct = base_means[fault["_idx"]] * f

        # ---- subassembly line, downstream-first (A03 -> A01)
        for i in range(N_SUB - 1, -1, -1):
            s = subs[i]
            out_buf, out_cap = sub_bufs[i], (sub_caps[i] if i < N_SUB - 1 else 4)
            if s.down_left > 0:
                s.down_left -= 1
                rec.state(s.name, "down", t)
                continue
            s.fail_check()
            if s.down_left > 0:
                rec.state(s.name, "down", t)
                continue
            if s.unit is not None:
                if s.remaining > 0:
                    s.remaining -= 1
                    rec.state(s.name, "working", t)
                else:
                    if len(out_buf) < out_cap:
                        out_buf.append(s.unit)
                        rec.buf(f"BA{i+1:02d}", len(out_buf), out_cap, t)
                        rec.scan(s.unit[0], s.name, "out", t)
                        s.unit = None
                    else:
                        rec.state(s.name, "blocked", t)
            if s.unit is None:
                src = sub_bufs[i - 1] if i > 0 else None
                if i == 0:
                    u = (new_sub(), 0)
                    s.unit = u
                elif src:
                    s.unit = src.popleft()
                    rec.buf(f"BA{i:02d}", len(src), sub_caps[i - 1], t)
                if s.unit is not None:
                    rec.scan(s.unit[0], s.name, "in", t)
                    s.remaining = s.sample_ct(var_mult[s.unit[1], N_SPINE + i])
                    rec.state(s.name, "working", t)
                else:
                    rec.state(s.name, "starved", t)

        # ---- spine, downstream-first (S20 -> S01)
        for i in range(N_SPINE - 1, -1, -1):
            s = spine[i]
            if s.down_left > 0:
                s.down_left -= 1
                rec.state(s.name, "down", t)
                continue
            s.fail_check()
            if s.down_left > 0:
                rec.state(s.name, "down", t)
                continue
            if s.unit is not None:
                if s.remaining > 0:
                    s.remaining -= 1
                    rec.state(s.name, "working", t)
                else:
                    if i == N_SPINE - 1:                      # exit the line
                        rec.scan(s.unit[0], s.name, "out", t)
                        s.unit = None
                        completed += 1
                    elif len(bufs[i]) < caps[i]:
                        bufs[i].append(s.unit)
                        rec.buf(f"B{i+1:02d}", len(bufs[i]), caps[i], t)
                        rec.scan(s.unit[0], s.name, "out", t)
                        s.unit = None
                    else:
                        rec.state(s.name, "blocked", t)
            if s.unit is None:
                got = None
                if i == 0:
                    got = (new_vin(), int(rng.integers(0, 3)))
                elif bufs[i - 1]:
                    if i == MERGE_AT - 1:                     # merge: need a sub too
                        if sub_bufs[-1]:
                            got = bufs[i - 1].popleft()
                            rec.buf(f"B{i:02d}", len(bufs[i - 1]), caps[i - 1], t)
                            sub_bufs[-1].popleft()
                            rec.buf(f"BA{N_SUB:02d}", len(sub_bufs[-1]), 4, t)
                    else:
                        got = bufs[i - 1].popleft()
                        rec.buf(f"B{i:02d}", len(bufs[i - 1]), caps[i - 1], t)
                if got is not None:
                    s.unit = got
                    rec.scan(s.unit[0], s.name, "in", t)
                    s.remaining = s.sample_ct(var_mult[s.unit[1], i])
                    rec.state(s.name, "working", t)
                else:
                    rec.state(s.name, "starved", t)

    # -------------------------------------------------- bottleneck truth
    spans = {}
    for name, log in rec.states.items():
        if not name.startswith("S"):
            continue
        sp = []
        for j, (st, ts) in enumerate(log):
            te = log[j + 1][1] if j + 1 < len(log) else SHIFT_S
            active = st in ("working", "down")
            if sp and sp[-1][2] == active and sp[-1][1] == ts:
                sp[-1] = (sp[-1][0], te, active)
            else:
                sp.append((ts, te, active))
        merged = []
        for a in sp:
            if merged and merged[-1][2] == a[2] and merged[-1][1] == a[0]:
                merged[-1] = (merged[-1][0], a[1], a[2])
            else:
                merged.append(list(a) if isinstance(a, tuple) else a)
                merged[-1] = tuple(merged[-1])
        spans[name] = [(a, b) for a, b, act in merged if act]

    truth_rows = []
    for minute in range(WINDOW_S // 60, SHIFT_S // 60):
        w0, w1 = minute * 60 - WINDOW_S, minute * 60
        scores = {}
        for name, sp in spans.items():
            lens = [min(b, w1) - max(a, w0) for a, b in sp if b > w0 and a < w1]
            if lens:
                scores[name] = float(np.mean(lens))
        if len(scores) >= 2:
            rank = sorted(scores, key=scores.get, reverse=True)
            truth_rows.append(dict(minute=minute, primary=rank[0],
                                   secondary=rank[1],
                                   avg_active_primary_s=round(scores[rank[0]], 1)))

    # ------------------------------------------------------------- write
    rd = os.path.join(BASE, "runs", f"run_{run_id:02d}")
    hd = os.path.join(rd, "hidden")
    os.makedirs(hd, exist_ok=True)

    scans = pd.DataFrame(rec.scans, columns=["vin", "station_id", "event", "t_s"])
    scans.to_csv(os.path.join(hd, "unit_scan_full.csv"), index=False)
    scans[~scans.station_id.isin(dark_names)].to_csv(
        os.path.join(rd, "unit_scan.csv"), index=False)

    st_rows = [(n, s, ts) for n, log in rec.states.items() for s, ts in log]
    st_df = pd.DataFrame(st_rows, columns=["station_id", "state", "t_s"]) \
        .sort_values(["t_s", "station_id"])
    st_df.to_csv(os.path.join(hd, "station_state_full.csv"), index=False)
    st_df[~st_df.station_id.isin(dark_names)].to_csv(
        os.path.join(rd, "station_state.csv"), index=False)

    pd.DataFrame(rec.buffers, columns=["buffer_id", "level", "capacity", "t_s"]) \
        .to_csv(os.path.join(rd, "buffer_level.csv"), index=False)
    pd.DataFrame(truth_rows).to_csv(
        os.path.join(hd, "bottleneck_truth.csv"), index=False)

    tr = pd.DataFrame(truth_rows)
    post = tr[tr.minute >= fault["onset_s"] // 60] if fault["onset_s"] > 0 else tr
    hit = (post.primary == fault["station"]).mean() if fault_kind != "none" and len(post) else np.nan
    return dict(run_id=run_id, seed=seed, fault_kind=fault_kind,
                fault_station=fault["station"], fault_onset_s=fault["onset_s"],
                fault_magnitude=round(fault["magnitude"], 3),
                fault_ramp_s=fault["ramp_s"], fault_duration_s=fault["duration_s"],
                dark_stations=";".join(sorted(dark_names)),
                jph=round(completed / (SHIFT_S / 3600), 1),
                vehicles_completed=completed,
                truth_bneck_is_fault_station_post_onset=round(hit, 3) if hit == hit else "",
                n_scan_events=len(scans), n_state_transitions=len(st_df),
                n_buffer_events=len(rec.buffers))


if __name__ == "__main__":
    os.makedirs(os.path.join(BASE, "runs"), exist_ok=True)
    manifest = []
    for rid, kind in enumerate(RUN_PLAN, start=1):
        m = simulate(rid, kind, seed=773000 + rid)
        manifest.append(m)
        print(f"run_{rid:02d}  {kind:13s} fault@{m['fault_station'] or '-':4s} "
              f"onset={m['fault_onset_s']:>6}  JPH={m['jph']:5.1f}  "
              f"truth-hit={m['truth_bneck_is_fault_station_post_onset']}", flush=True)
    mdf = pd.DataFrame(manifest)
    mdf.to_csv(os.path.join(BASE, "run_manifest.csv"), index=False)
    print("\n%d runs written. Mean JPH %.1f (no-fault: %.1f)" % (
        len(mdf), mdf.jph.mean(), mdf[mdf.fault_kind == "none"].jph.mean()))
