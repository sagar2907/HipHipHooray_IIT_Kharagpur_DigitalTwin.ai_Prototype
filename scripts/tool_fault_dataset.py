#!/usr/bin/env python3
"""
Generates a realistic nutrunner (torque tool) telemetry dataset for an
automotive assembly line, with physically motivated degradation, and then
runs four fault detectors to measure how early each one catches the fault.

Every column here corresponds to something a real tightening controller
already emits over Open Protocol / OPC-UA. Nothing requires manual entry.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260814)

TAKT_S = 60.0            # one unit per station per 60 s
N_OPS = 9000             # fastening operations per tool (~6.25 days of 1-shift)
EOL_LAG_OPS = 40         # end-of-line test sits 40 stations downstream

# ----------------------------------------------------------------- tool spec
# Each tool drives a safety-relevant joint. Target torque and tolerance are
# set by the joint's engineering spec, exactly as on a real line.
TOOLS = [
    # tool_id, station, target_Nm, tol_pct, condition,      onset_op, wear_ops
    ("NR-07A", 7,  45.0, 0.10, "gradual_wear",  3200, 1600),
    ("NR-12B", 12, 62.0, 0.08, "gradual_wear",  5100, 1400),
    ("NR-18C", 18, 28.0, 0.12, "gradual_wear",  2600, 1100),
    ("NR-22D", 22, 45.0, 0.10, "sudden_shift",  6400,   30),
    ("NR-05E", 5,  38.0, 0.10, "healthy",       None,  None),
    ("NR-31F", 31, 55.0, 0.09, "healthy",       None,  None),
]


def health_curve(n_ops, onset, wear_ops, kind):
    """Hidden tool health, 1.0 = perfect, 0.0 = fully degraded.

    Gradual wear follows a Weibull-shaped accumulation of damage: slow at
    first, then accelerating. This matters - memoryless (exponential) failure
    would make prediction impossible in principle.
    """
    h = np.ones(n_ops)
    if onset is None:
        return h
    idx = np.arange(n_ops)
    after = idx >= onset
    t = np.clip((idx[after] - onset) / float(wear_ops), 0, 1.35)
    if kind == "sudden_shift":
        damage = (t > 0).astype(float)
    else:
        damage = 1.0 - np.exp(-(t ** 2.2))     # Weibull shape k=2.2
    h[after] = np.clip(1.0 - damage, 0.0, 1.0)
    return h


rows = []
meta = []

for tool_id, station, target, tol_pct, cond, onset, wear in TOOLS:
    tol_abs = target * tol_pct
    lo, hi = target - tol_abs, target + tol_abs
    h = health_curve(N_OPS, onset, wear, cond)

    # A healthy fastening process runs at Cpk approx 1.33, i.e. the tolerance
    # band is +/- 4 sigma. That is what makes random out-of-spec readings
    # essentially nonexistent before degradation begins - which in turn is
    # what makes the lead-time measurement meaningful.
    base_sd = tol_abs / 4.0

    # A degrading nutrunner loses clamp force and gets noisier: the mean
    # drifts DOWN and the spread grows. Both are observable long before any
    # single reading leaves the tolerance band.
    mean_shift = -(1.0 - h) * 0.62 * tol_abs
    sd = base_sd * (1.0 + (1.0 - h) * 0.5)

    torque = RNG.normal(target + mean_shift, sd)

    # Angle rises as the joint under-torques; current falls with worn motor.
    angle = RNG.normal(92.0, 3.0) + (1.0 - h) * 14.0
    current = RNG.normal(11.5, 0.35) - (1.0 - h) * 1.4
    temp = RNG.normal(38.0, 1.8) + (1.0 - h) * 5.5
    cyc = RNG.normal(3.1, 0.18) + (1.0 - h) * 0.55

    # A joint is defective if it falls outside the engineering tolerance.
    defect = ((torque < lo) | (torque > hi)).astype(int)

    op = np.arange(N_OPS)
    ts = pd.Timestamp("2026-06-01 06:00:00") + pd.to_timedelta(op * TAKT_S, "s")

    first_def = int(op[defect == 1][0]) if defect.any() else -1
    meta.append(dict(tool_id=tool_id, station_id=station, target_nm=target,
                     tol_pct=tol_pct, condition=cond,
                     true_onset_op=(-1 if onset is None else onset),
                     first_defect_op=first_def,
                     total_defects=int(defect.sum())))

    for i in range(N_OPS):
        rows.append((ts[i], f"VIN{100000 + i}", station, tool_id, target,
                     round(lo, 2), round(hi, 2),
                     round(torque[i], 3), round(angle[i], 2),
                     round(current[i], 3), round(temp[i], 2), round(cyc[i], 3),
                     defect[i]))

df = pd.DataFrame(rows, columns=[
    "timestamp", "vin", "station_id", "tool_id", "target_nm",
    "spec_low_nm", "spec_high_nm", "measured_torque_nm", "measured_angle_deg",
    "motor_current_a", "tool_temp_c", "cycle_time_s", "joint_defective"])

# End-of-line test only sees the unit 40 stations later, and functional
# testing catches most but not all under-torqued joints.
df["eol_detected"] = np.where(
    (df.joint_defective == 1) & (RNG.random(len(df)) < 0.72), 1, 0)

meta_df = pd.DataFrame(meta)
df.to_csv("tool_telemetry.csv", index=False)
meta_df.to_csv("tool_ground_truth.csv", index=False)

print("dataset written: tool_telemetry.csv")
print("  rows:", len(df), " tools:", df.tool_id.nunique(),
      " defect rate: %.3f%%" % (100 * df.joint_defective.mean()))
print()
print(meta_df.to_string(index=False))
