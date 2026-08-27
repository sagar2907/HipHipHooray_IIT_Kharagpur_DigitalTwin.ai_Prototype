#!/usr/bin/env python3
"""
Tool telemetry generator, version 2.

Fixes every realism gap the v1 audit identified, and widens the fault
taxonomy so detectors cannot overfit one failure signature.

What changed vs tool_fault_dataset.py (v1):

  1. PHYSICAL TIME. Vehicle v reaches station s at t0 + (v + s) * takt.
     A VIN is never at two stations at the same instant, so genealogy is
     physically coherent and end-of-line events happen when the vehicle
     actually reaches end of line.
  2. STOCHASTIC WEAR. Degradation is a gamma process (random damage
     increments whose rate accelerates with accumulated damage), not a
     deterministic curve. Every tool's damage path is different; no
     detector can implicitly memorise "the" curve.
  3. FAULT TAXONOMY. Seven condition types instead of three:
        healthy         in control throughout
        gradual_wear    mean drifts down, spread grows      (v1's mode)
        spread_only     spread grows, mean stays            (bearing wear)
        sudden_shift    step change, no precursor           (the nail)
        sensor_bias     sensor masks a real drift: measured torque looks
                        healthy while true torque falls - defects WITHOUT
                        a torque signal; only current/angle reveal it
        overtorque      calibration drifts UP, defects on the high side
        intermittent    sporadic bursts of bad fastenings   (loose socket)
  4. CONFOUNDED CHANNELS. Motor current and temperature carry a shared
     ambient daily cycle plus per-reading joint-friction noise that also
     moves torque and angle. Current is no longer a free  clean channel -
     multivariate detection must earn its lead honestly.
  5. HELD-OUT CALIBRATION SET. A separate all-healthy file, generated
     from a different seed, for threshold calibration. Calibrating and
     evaluating on the same readings (the v1 flaw) is now structurally
     impossible if you use the files as named.
  6. EOL AS AN EVENT LOG. quality_results.csv records what end-of-line
     inspection reports and WHEN (vehicle arrival at the EOL station),
     with a 72% per-joint catch rate. Joining it back to telemetry via
     VIN is the genealogy exercise a real plant faces.

Outputs (written to ../dataset/v2/):
  telemetry_v2.csv          24 tools x 12,000 ops = 288,000 rows
  ground_truth_v2.csv       hidden truth per tool
  quality_results.csv       end-of-line inspection events per vehicle
  healthy_calibration.csv   12 healthy tools x 12,000 ops, separate seed
"""

import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260814)
CAL_RNG = np.random.default_rng(99120816)   # held-out calibration set

TAKT_S = 60.0
N_OPS = 12000                # ~8.3 days of single-shift line time per tool
EOL_STATION = 41             # end-of-line inspection position
EOL_CATCH_P = 0.72
T0 = pd.Timestamp("2026-06-01 06:00:00")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "v2")
os.makedirs(OUT, exist_ok=True)

# --------------------------------------------------------------- tool table
# station, target torque (Nm), tolerance pct  - one tool per station, spread
# across the line so EOL lag differs per tool (EOL_STATION - station).
def build_tool_table(rng, conditions):
    tools = []
    stations = rng.choice(np.arange(1, 40), size=len(conditions), replace=False)
    stations.sort()
    for i, cond in enumerate(conditions):
        target = float(rng.uniform(18, 95))
        tol = float(rng.uniform(0.08, 0.15))
        onset = int(rng.integers(3000, 9000)) if cond != "healthy" else -1
        wear = int(rng.integers(1200, 2600)) if cond != "healthy" else -1
        tools.append(dict(tool_id=f"NR-{stations[i]:02d}{chr(65+i%26)}",
                          station_id=int(stations[i]), target_nm=round(target, 1),
                          tol_pct=round(tol, 3), condition=cond,
                          true_onset_op=onset, wear_ops=wear))
    return tools

CONDITIONS = (
    ["healthy"] * 8 +
    ["gradual_wear"] * 5 +
    ["spread_only"] * 3 +
    ["sudden_shift"] * 2 +
    ["sensor_bias"] * 2 +
    ["overtorque"] * 2 +
    ["intermittent"] * 2
)

# ------------------------------------------------------------- damage model
def gamma_damage_path(rng, n_ops, onset, wear_ops):
    """Stochastic accumulated damage in [0, ~1.3], zero before onset.

    Increment rate accelerates with accumulated damage (feedback), which
    reproduces Weibull-like wear-out acceleration while keeping every
    path random. wear_ops sets the typical onset-to-failure span.
    """
    d = np.zeros(n_ops)
    if onset < 0:
        return d
    # scale chosen so E[damage] ~ 1 after ~wear_ops operations with feedback
    base = 1.0 / (wear_ops * 1.6)
    acc = 0.0
    for i in range(onset, n_ops):
        rate = base * (1.0 + 2.5 * acc)            # acceleration feedback
        acc += rng.gamma(shape=1.2, scale=rate / 1.2)
        d[i] = acc
    return np.clip(d, 0, 1.35)

# ------------------------------------------------------------ channel model
def generate_tool(rng, t, n_ops=N_OPS):
    """Returns a DataFrame of telemetry for one tool plus defect truth."""
    target, tol_pct = t["target_nm"], t["tol_pct"]
    tol = target * tol_pct
    lo, hi = target - tol, target + tol
    cond, onset, wear = t["condition"], t["true_onset_op"], t["wear_ops"]

    op = np.arange(n_ops)
    # physical timestamps: vehicle v is at station s at T0 + (v + s) * takt
    ts = T0 + pd.to_timedelta((op + t["station_id"]) * TAKT_S, unit="s")

    dmg = gamma_damage_path(rng, n_ops, onset if cond not in
                            ("sudden_shift", "intermittent") else -1, wear)

    base_sd = tol / 4.0                       # Cpk ~ 1.33 healthy
    # shared confounds ------------------------------------------------------
    day_phase = 2 * np.pi * ((op + t["station_id"]) * TAKT_S % 86400) / 86400
    ambient = 1.6 * np.sin(day_phase - 1.1)          # deg C daily swing
    friction = rng.normal(0, 1, n_ops)               # per-joint friction
    # friction raises torque needed and angle together, lowers effective
    # clamp - a shared latent factor across channels
    torque_noise = rng.normal(0, base_sd * 0.75, n_ops) + friction * base_sd * 0.66
    angle_noise = rng.normal(0, 2.2, n_ops) - friction * 1.4
    current_noise = rng.normal(0, 0.42, n_ops) + friction * 0.12

    true_shift = np.zeros(n_ops)      # shift of TRUE applied torque mean
    meas_bias = np.zeros(n_ops)       # sensor bias (measured - true)
    sd_mult = np.ones(n_ops)
    burst = np.zeros(n_ops, dtype=bool)

    if cond == "gradual_wear":
        true_shift = -dmg * 0.62 * tol
        sd_mult = 1.0 + dmg * 0.5
    elif cond == "spread_only":
        sd_mult = 1.0 + dmg * 1.15
    elif cond == "overtorque":
        true_shift = +dmg * 0.58 * tol
        sd_mult = 1.0 + dmg * 0.25
    elif cond == "sensor_bias":
        true_shift = -dmg * 0.70 * tol
        meas_bias = -true_shift * 0.85       # sensor masks 85% of the drift
        sd_mult = 1.0 + dmg * 0.30
    elif cond == "sudden_shift":
        after = op >= onset
        true_shift = np.where(after, -0.55 * tol, 0.0)
        dmg = np.where(after, 1.0, 0.0)
    elif cond == "intermittent":
        after = op >= onset
        # burst probability grows as the socket loosens
        p = np.where(after, np.minimum(0.001 + (op - onset) / (wear * 18.0), 0.08), 0)
        burst = rng.random(n_ops) < p
        dmg = np.where(after, np.minimum((op - onset) / float(wear), 1.0), 0.0)

    true_torque = target + true_shift + torque_noise * sd_mult
    true_torque[burst] -= rng.uniform(3.2, 6.0, burst.sum()) * base_sd
    measured = true_torque + meas_bias

    # secondary channels respond to the TRUE mechanical state (damage),
    # not to the sensor reading - which is what makes sensor_bias catchable
    angle = 92.0 + angle_noise + dmg * 13.0 + burst * rng.uniform(6, 14, n_ops)
    current = 11.5 + current_noise + 0.06 * ambient - dmg * 1.25
    temp = 38.0 + rng.normal(0, 1.6, n_ops) + ambient + dmg * 5.0
    cyc = np.maximum(rng.normal(3.1, 0.2, n_ops) + dmg * 0.5, 1.5)

    defect = ((true_torque < lo) | (true_torque > hi)).astype(int)

    df = pd.DataFrame(dict(
        timestamp=ts, vin=[f"VIN{200000 + i}" for i in op],
        station_id=t["station_id"], tool_id=t["tool_id"],
        target_nm=target, spec_low_nm=round(lo, 2), spec_high_nm=round(hi, 2),
        measured_torque_nm=np.round(measured, 3),
        measured_angle_deg=np.round(angle, 2),
        motor_current_a=np.round(current, 3),
        tool_temp_c=np.round(temp, 2),
        cycle_time_s=np.round(cyc, 3),
        joint_defective=defect))
    return df, defect

# ------------------------------------------------------------------- build
def build(rng, conditions, vin_base_note=""):
    tools = build_tool_table(rng, conditions)
    frames, truth = [], []
    for t in tools:
        df, defect = generate_tool(rng, t)
        frames.append(df)
        d_ops = np.flatnonzero(defect)
        truth.append(dict(**t,
                          first_defect_op=int(d_ops[0]) if d_ops.size else -1,
                          total_defects=int(defect.sum()),
                          eol_lag_ops=EOL_STATION - t["station_id"]))
    return pd.concat(frames, ignore_index=True), pd.DataFrame(truth)

print("generating main set (24 tools x %d ops)..." % N_OPS)
tele, truth = build(RNG, CONDITIONS)
tele.to_csv(os.path.join(OUT, "telemetry_v2.csv"), index=False)
truth.to_csv(os.path.join(OUT, "ground_truth_v2.csv"), index=False)

# ------------------------------------------------- end-of-line event log
# The vehicle reaches EOL at t0 + (v + EOL_STATION) * takt. Each defective
# joint on it is caught with p=0.72, independently. One row per vehicle
# that reaches EOL with at least one defective joint OR at least one catch.
print("generating end-of-line quality event log...")
d = tele[tele.joint_defective == 1][["vin", "tool_id"]].copy()
d["caught"] = RNG.random(len(d)) < EOL_CATCH_P
g = d.groupby("vin").agg(defective_joints=("tool_id", "count"),
                         caught_joints=("caught", "sum"),
                         defect_codes=("tool_id", lambda s: ";".join(sorted(set(s)))))
g = g.reset_index()
vnum = g.vin.str.slice(3).astype(int) - 200000
g["timestamp_eol"] = T0 + pd.to_timedelta((vnum + EOL_STATION) * TAKT_S, unit="s")
g["eol_result"] = np.where(g.caught_joints > 0, "FAIL", "PASS")
g = g.sort_values("timestamp_eol")
g[["vin", "timestamp_eol", "eol_result", "defective_joints",
   "caught_joints", "defect_codes"]].to_csv(
    os.path.join(OUT, "quality_results.csv"), index=False)

# ------------------------------------------- held-out healthy calibration
print("generating held-out healthy calibration set (12 tools)...")
cal_tele, cal_truth = build(CAL_RNG, ["healthy"] * 12)
cal_tele.to_csv(os.path.join(OUT, "healthy_calibration.csv"), index=False)

# ------------------------------------------------------------------ report
print()
print("telemetry_v2.csv        %8d rows, %d tools" % (len(tele), tele.tool_id.nunique()))
print("healthy_calibration.csv %8d rows, %d tools (seed-independent)" % (len(cal_tele), cal_tele.tool_id.nunique()))
print("quality_results.csv     %8d vehicles with defects reaching EOL" % len(g))
print("overall defect rate: %.3f%%" % (100 * tele.joint_defective.mean()))
print()
print(truth[["tool_id", "station_id", "condition", "true_onset_op",
             "first_defect_op", "total_defects", "eol_lag_ops"]].to_string(index=False))
