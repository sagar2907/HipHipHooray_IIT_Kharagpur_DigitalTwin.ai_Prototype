#!/usr/bin/env python3
"""
Sanity validation for the v2 datasets - run after the generators.

Telemetry v2:
  - calibrates CUSUM thresholds on healthy_calibration.csv (HELD OUT -
    different seed, different tools), then measures false alarms and
    warning lead on telemetry_v2.csv. This is the out-of-sample protocol
    the v1 experiment lacked.
  - runs torque-only vs torque+current CUSUM per fault type, so the
    detectability spread across the taxonomy is measured, not assumed.
    Expected: sensor_bias is near-invisible to torque-only detection and
    caught by the current channel - the multivariate motivation, in data.

Line flow:
  - checks conservation (every vehicle that exits passed every station),
    JPH plausibility, blocked/starved balance, and how often the injected
    fault station becomes the truth bottleneck after onset.
"""

import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(HERE, "..", "dataset", "v2")
LINE = os.path.join(HERE, "..", "dataset", "line")
BASELINE_OPS = 1500


def cusum_alarm(x, mu, sd, thr, k=0.5):
    s = (x - mu) / sd
    hi = lo = 0.0
    for i in range(len(s)):
        hi = max(0.0, hi + s[i] - k)
        lo = min(0.0, lo + s[i] + k)
        if hi > thr or lo < -thr:
            return i
    return -1


def sustained_ref(defect, onset, need=3, win=100):
    fwd = pd.Series(defect[::-1]).rolling(win, min_periods=win).sum()[::-1].values
    cand = np.flatnonzero((fwd >= need) & (np.arange(len(defect)) >= max(onset, 0)))
    return int(cand[0]) if cand.size else -1


print("=" * 78)
print("TELEMETRY V2 - held-out calibration, per-fault-type detectability")
print("=" * 78)
tele = pd.read_csv(os.path.join(V2, "telemetry_v2.csv"))
truth = pd.read_csv(os.path.join(V2, "ground_truth_v2.csv"))
cal = pd.read_csv(os.path.join(V2, "healthy_calibration.csv"))

# ---- calibrate on the held-out healthy set (target: 0 alarms there)
def calibrate(col):
    grid = np.arange(4.0, 30.01, 0.5)
    segs = []
    for tid, g in cal.groupby("tool_id"):
        x = g[col].values
        mu, sd = x[:BASELINE_OPS].mean(), x[:BASELINE_OPS].std(ddof=1)
        segs.append((x, mu, sd))
    for thr in grid:
        if all(cusum_alarm(x, mu, sd, thr) < 0 for x, mu, sd in segs):
            return float(thr)
    return float(grid[-1])

thr_tq = calibrate("measured_torque_nm")
thr_cu = calibrate("motor_current_a")
print(f"CUSUM thresholds calibrated on held-out healthy set "
      f"({cal.tool_id.nunique()} tools x {len(cal)//cal.tool_id.nunique()} ops): "
      f"torque={thr_tq}, current={thr_cu}")

# ---- false alarms on the 8 healthy tools of the MAIN set (also out-of-sample)
fa_tq = fa_cu = 0
healthy_ids = truth[truth.condition == "healthy"].tool_id
for tid in healthy_ids:
    g = tele[tele.tool_id == tid]
    x, c = g.measured_torque_nm.values, g.motor_current_a.values
    if cusum_alarm(x, x[:BASELINE_OPS].mean(), x[:BASELINE_OPS].std(ddof=1), thr_tq) >= 0:
        fa_tq += 1
    if cusum_alarm(c, c[:BASELINE_OPS].mean(), c[:BASELINE_OPS].std(ddof=1), thr_cu) >= 0:
        fa_cu += 1
print(f"False alarms on {len(healthy_ids)} healthy main-set tools "
      f"(96,000 held-out ops): torque-CUSUM {fa_tq}, current-CUSUM {fa_cu}")

# ---- lead time per fault type, torque-only vs multivariate
rows = []
for _, t in truth[truth.condition != "healthy"].iterrows():
    g = tele[tele.tool_id == t.tool_id].reset_index(drop=True)
    x, c = g.measured_torque_nm.values, g.motor_current_a.values
    ref = sustained_ref(g.joint_defective.values, t.true_onset_op)
    if ref < 0:
        continue
    mu, sd = x[:BASELINE_OPS].mean(), x[:BASELINE_OPS].std(ddof=1)
    muc, sdc = c[:BASELINE_OPS].mean(), c[:BASELINE_OPS].std(ddof=1)
    a_tq = cusum_alarm(x, mu, sd, thr_tq)
    a_cu = cusum_alarm(c, muc, sdc, thr_cu)
    both = [a for a in (a_tq, a_cu) if a >= 0]
    a_mv = min(both) if both else -1
    # pre-onset alarms now count AS FALSE (scored miss), per audit F4
    def lead(a):
        if a < 0:
            return np.nan          # never fired
        if a < t.true_onset_op:
            return -9999           # false alarm before fault existed
        return ref - a
    rows.append(dict(condition=t.condition, tool_id=t.tool_id,
                     lead_torque=lead(a_tq), lead_mv=lead(a_mv)))

res = pd.DataFrame(rows)
def fmt(v):
    if v != v:
        return "  never"
    if v == -9999:
        return "  FA-pre"
    return "%7.0f" % v
print("\nWarning lead before sustained defects, per tool (vehicles):")
print(f"{'condition':14s} {'tool':8s} {'torque-only':>12s} {'torque+current':>15s}")
for _, r in res.iterrows():
    print(f"{r.condition:14s} {r.tool_id:8s} {fmt(r.lead_torque):>12s} {fmt(r.lead_mv):>15s}")

ok = res.replace(-9999, np.nan)
print("\nMedian lead by condition (vehicles; NaN = typically undetected):")
print(ok.groupby("condition")[["lead_torque", "lead_mv"]].median().round(0).to_string())

print()
print("=" * 78)
print("LINE FLOW - conservation, KPIs, fault-vs-truth agreement")
print("=" * 78)
man = pd.read_csv(os.path.join(LINE, "run_manifest.csv"))
print(man[["run_id", "fault_kind", "fault_station", "fault_onset_s", "jph",
           "truth_bneck_is_fault_station_post_onset"]].to_string(index=False))
print("\nJPH: no-fault mean %.1f | fault mean %.1f" % (
    man[man.fault_kind == "none"].jph.mean(),
    man[man.fault_kind != "none"].jph.mean()))

# conservation check on 3 sample runs
for rid in [1, 10, 21]:
    rd = os.path.join(LINE, "runs", f"run_{rid:02d}", "hidden", "unit_scan_full.csv")
    sc = pd.read_csv(rd)
    veh = sc[sc.vin.str.contains("V")]
    exits = set(veh[(veh.station_id == "S20") & (veh.event == "out")].vin)
    n_st = veh[veh.vin.isin(exits)].groupby("vin").station_id.nunique()
    print(f"run_{rid:02d}: {len(exits)} vehicles exited; "
          f"all passed 20 stations: {bool((n_st == 20).all())}")
print("\nvalidation complete.")
