"""Tool-family models for the v3 process dataset.

Four tool families, one generative skeleton. Every family follows the same
causal chain a real degrading tool follows:

    hidden damage path  ->  true process state  ->  channel readings
                                    |
                                    +->  defect truth (spec on the TRUE value)
                                    +->  controller verdict (spec on the MEASURED value)

That last split is deliberate and is the heart of the sensor-fault story:
a tightening controller judges OK/NOK on what its transducer *reports*, so a
biased sensor produces confident OK verdicts on genuinely bad joints.

Damage paths are stochastic (gamma process with acceleration feedback), so
no two tools share a curve. The evaluation-firewall variant swaps the gamma
process for a Wiener process with drift and different coupling constants -
structurally different maths, never used during development.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------- families
# primary: the channel carrying the engineering spec (defines defects).
# secondaries: name -> (mean, sd, damage_coef, ambient_coef, latent_coef)
#   damage_coef   shift at full damage, in units of the channel
#   ambient_coef  coupling to the shared ambient temperature cycle
#   latent_coef   coupling to the per-cycle latent factor (joint friction,
#                 part fit-up...) that also moves the primary channel
FAMILIES = {
    "nutrunner": dict(
        primary="torque_nm", program_prefix="PF",
        secondaries={
            "angle_deg":       (92.0, 2.6,  +13.0, 0.0,  -1.4),
            "current_a":       (11.5, 0.42, -1.25, 0.06, +0.12),
            "temp_c":          (38.0, 1.6,  +5.0,  1.0,  0.0),
            "cycle_s":         (3.1,  0.20, +0.5,  0.0,  0.0),
        }),
    "spotweld": dict(
        primary="resistance_uohm", program_prefix="WD",
        secondaries={
            "current_ka":      (9.5,  0.18, -0.6,  0.02, +0.05),
            "voltage_v":       (1.35, 0.05, +0.16, 0.0,  +0.02),
            "energy_j":        (2600, 90,   -170,  4.0,  +25.0),
            "cap_count":       (0.0,  0.0,  0.0,   0.0,  0.0),   # monotone counter
        }),
    "adhesive": dict(
        primary="bead_width_mm", program_prefix="AD",
        secondaries={
            "flow_mlps":       (4.2,  0.12, -0.55, 0.015, +0.03),
            "pressure_bar":    (58.0, 1.9,  +9.5,  0.25,  -0.4),
            "material_temp_c": (28.0, 0.9,  +1.2,  0.8,   0.0),
        }),
    "pressfit": dict(
        primary="peak_force_kn", program_prefix="PR",
        secondaries={
            "disp_at_peak_mm": (12.4, 0.22, +0.9,  0.0,  -0.06),
            "slope_kn_mm":     (3.9,  0.15, -0.5,  0.0,  +0.04),
            "cycle_s":         (4.6,  0.3,  +0.6,  0.0,  0.0),
        }),
}

CONDITIONS = (
    "healthy", "gradual_wear", "spread_only", "sudden_shift", "sensor_bias",
    "overtorque", "intermittent", "pure_transducer_drift", "lubrication_loss",
    "post_calibration_reset", "batch_material_shift", "intermittent_connector",
)


@dataclass
class ToolSpec:
    tool_id: str
    family: str
    station_id: int
    condition: str
    target: float                 # primary-channel target
    tol_pct: float
    onset_op: int                 # -1 for healthy / lot-driven conditions
    wear_ops: int
    program_id: str = ""
    clock_skew_s: float = 0.0     # this controller's clock offset
    service_ops: list[int] = field(default_factory=list)   # scheduled bench checks


def damage_path(rng, n_ops, onset, wear_ops, firewall=False):
    """Hidden accumulated damage in [0, ~1.35]; 0 before onset.

    Development maths: gamma increments whose rate grows with accumulated
    damage (wear accelerates wear). Firewall maths: reflected Wiener process
    with drift - different increment distribution, different acceleration
    shape, so a model fitted to one cannot have memorised the other.
    """
    d = np.zeros(n_ops)
    if onset is None or onset < 0:
        return d
    acc = 0.0
    if firewall:
        drift = 1.0 / (wear_ops * 1.3)
        vol = drift * 9.0
        for i in range(onset, n_ops):
            acc = max(0.0, acc + drift * (1.0 + 1.6 * min(acc, 1.35) ** 1.5)
                      + rng.normal(0, vol))
            acc = min(acc, 1.35)
            d[i] = acc
    else:
        base = 1.0 / (wear_ops * 1.6)
        for i in range(onset, n_ops):
            rate = base * (1.0 + 2.5 * acc)
            acc += rng.gamma(1.2, rate / 1.2)
            d[i] = acc
    return np.clip(d, 0.0, 1.35)


def generate_tool(rng, t: ToolSpec, n_ops: int, ambient: np.ndarray,
                  lot_shift: np.ndarray, firewall: bool = False):
    """Generate one tool's telemetry.

    ambient    per-op shared environment temperature deviation (deg C)
    lot_shift  per-op shift of the primary channel caused by the material
               lot in use (zeros except during bad lots; fastening only)

    Returns (dict of channel arrays, truth dict).
    """
    fam = FAMILIES[t.family]
    tol = t.target * t.tol_pct
    lo, hi = t.target - tol, t.target + tol
    base_sd = tol / 4.0                       # healthy Cpk ~ 1.33
    op = np.arange(n_ops)

    cond = t.condition
    two_stage = cond == "lubrication_loss"
    dmg = damage_path(rng, n_ops,
                      -1 if cond in ("sudden_shift", "intermittent",
                                     "intermittent_connector",
                                     "batch_material_shift") else t.onset_op,
                      t.wear_ops, firewall)

    # post-calibration reset: damage is zeroed at each service visit
    resets = []
    if cond == "post_calibration_reset":
        for s_op in t.service_ops:
            if s_op > t.onset_op and dmg[s_op] > 0.05:
                resets.append(s_op)
                tail = damage_path(rng, n_ops - s_op, 0, t.wear_ops, firewall)
                dmg[s_op:] = tail
                break                          # one mid-life reset is enough

    # ---- condition -> effect decomposition
    true_shift = np.zeros(n_ops)      # shift of the TRUE primary value
    meas_bias = np.zeros(n_ops)       # measured minus true
    sd_mult = np.ones(n_ops)
    sec_dmg = dmg.copy()              # damage as seen by secondary channels
    burst = np.zeros(n_ops, dtype=bool)

    if cond in ("gradual_wear", "post_calibration_reset"):
        true_shift = -dmg * 0.62 * tol
        sd_mult = 1.0 + dmg * 0.5
    elif cond == "spread_only":
        sd_mult = 1.0 + dmg * 1.15
    elif cond == "overtorque":
        true_shift = +dmg * 0.58 * tol
        sd_mult = 1.0 + dmg * 0.25
    elif cond == "sensor_bias":
        true_shift = -dmg * 0.70 * tol
        meas_bias = -true_shift * 0.85        # sensor hides 85% of the drift
        sd_mult = 1.0 + dmg * 0.30
    elif cond == "pure_transducer_drift":
        # the tool is HEALTHY: no mechanical damage anywhere. Only the
        # sensor's reading walks away from reality.
        sec_dmg = np.zeros(n_ops)
        meas_bias = -dmg * 0.55 * tol
    elif cond == "lubrication_loss":
        # stage 1: friction rises (current/temp up), primary holds.
        # stage 2 (damage > 0.45): mechanical wear begins on the primary.
        stage2 = np.clip((dmg - 0.45) / 0.9, 0, 1)
        true_shift = -stage2 * 0.6 * tol
        sd_mult = 1.0 + stage2 * 0.45
        sec_dmg = dmg * 1.15                  # secondaries lead the primary
    elif cond == "sudden_shift":
        after = op >= t.onset_op
        true_shift = np.where(after, -0.55 * tol, 0.0)
        sec_dmg = after.astype(float)
    elif cond == "intermittent":
        after = op >= t.onset_op
        p = np.where(after,
                     np.minimum(0.001 + (op - t.onset_op) / (t.wear_ops * 18.0),
                                0.08), 0.0)
        burst = rng.random(n_ops) < p
        sec_dmg = np.where(after, np.minimum((op - t.onset_op) / t.wear_ops, 1.0), 0.0)

    # ---- primary channel
    latent = rng.normal(0, 1, n_ops)          # joint friction / part fit-up
    noise = rng.normal(0, base_sd * 0.75, n_ops) + latent * base_sd * 0.66
    true_primary = t.target + true_shift + lot_shift + noise * sd_mult
    true_primary[burst] -= rng.uniform(3.2, 6.0, burst.sum()) * base_sd
    measured_primary = true_primary + meas_bias

    channels = {fam["primary"]: measured_primary}
    for name, (mu, sd, dcoef, acoef, lcoef) in fam["secondaries"].items():
        if name == "cap_count":               # electrode cap: monotone counter
            channels[name] = np.minimum(op % 400, 399).astype(float)
            continue
        x = (mu + rng.normal(0, sd, n_ops) + sec_dmg * dcoef
             + ambient * acoef + latent * lcoef)
        if burst.any() and name in ("angle_deg", "disp_at_peak_mm"):
            x[burst] += rng.uniform(6, 14, burst.sum())
        channels[name] = x

    # connector fault: one secondary channel suffers NULL/spike bursts
    imperfections = []
    if cond == "intermittent_connector":
        victim = [k for k in channels if k != fam["primary"]][0]
        n_ep = rng.integers(6, 12)
        for _ in range(n_ep):
            s = int(rng.integers(t.onset_op, n_ops - 60))
            ln = int(rng.integers(5, 45))
            kind = "null" if rng.random() < 0.7 else "spike"
            if kind == "null":
                channels[victim][s:s + ln] = np.nan
            else:
                channels[victim][s:s + ln] += rng.normal(0, 12 * np.nanstd(channels[victim][:500]), ln)
            imperfections.append(dict(tool_id=t.tool_id, channel=victim,
                                      kind=kind, start_op=s, len_ops=ln))

    true_defect = ((true_primary < lo) | (true_primary > hi)).astype(int)
    # the CONTROLLER's verdict uses the measured value - a biased sensor
    # cheerfully passes bad parts
    nok = ((measured_primary < lo) | (measured_primary > hi))

    truth = dict(tool_id=t.tool_id, family=t.family, station_id=t.station_id,
                 condition=cond, target=t.target, tol_pct=t.tol_pct,
                 true_onset_op=t.onset_op, wear_ops=t.wear_ops,
                 reset_ops=";".join(map(str, resets)),
                 first_true_defect_op=int(np.argmax(true_defect)) if true_defect.any() else -1,
                 total_true_defects=int(true_defect.sum()),
                 total_controller_nok=int(nok.sum()),
                 defects_passed_ok=int((true_defect & ~nok).sum()))
    return channels, true_primary, true_defect, nok, truth, imperfections
