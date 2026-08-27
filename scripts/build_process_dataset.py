#!/usr/bin/env python3
"""
Build the v3 process & quality telemetry dataset.

Outputs (dataset/v3/process/):
  <family>.csv                 observed telemetry, Open-Protocol-style fields,
                               one file per tool family (schemas differ)
  quality_results.csv          end-of-line inspection events, joined by VIN
  maintenance_log.csv          scheduled bench checks + unscheduled services,
                               with as-found / as-left capability (Cmk)
  material_lots.csv            fastener lot per VIN range; two lots are bad
  holdout/<family>.csv         held-out all-healthy tools, separate seed -
                               calibrate detectors HERE, never on the main set
  firewall/<family>.csv        evaluation firewall: Wiener-process damage,
                               never to be used during development
  hidden/ground_truth.csv      per-tool truth (condition, onset, defects,
                               defects the controller passed as OK)
  hidden/op_truth_<family>.csv per-operation true value + true defect flag
  hidden/imperfection_log.csv  every injected drop/duplicate/null/spike/skew

Design notes worth defending later:
  - The controller's OK/NOK verdict is computed on the MEASURED value while
    defect truth is computed on the TRUE value. Sensor-fault tools therefore
    pass bad parts as OK, which is the phenomenon the whole detection layer
    exists to catch - and `defects_passed_ok` in the ground truth counts
    exactly how many.
  - Every timestamp carries its controller's clock skew. Real plants never
    have synchronised clocks; a twin that assumes they do breaks on contact.
  - Scheduled maintenance appears in the log whether or not anything was
    adjusted, exactly like a real calibration bench records a no-adjustment
    verification visit.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.tools import FAMILIES, ToolSpec, generate_tool          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "dataset", "v3", "process")
N_OPS = 20000
TAKT_S = 60.0
EOL_STATION = 41
EOL_CATCH_P = 0.72
T0 = pd.Timestamp("2026-06-01 06:00:00")
SHIFT_LEN_OPS = 480                    # one 8-hour shift of line time
BREAKS_AT = (120, 270, 390)            # ops into each shift: tea, lunch, tea

MAIN_SEED, HOLDOUT_SEED, FIREWALL_SEED = 30260815, 99260815, 55260815

# ------------------------------------------------- rosters (family, condition)
MAIN_ROSTER = (
    [("nutrunner", c) for c in
     ["healthy"] * 4 + ["gradual_wear", "gradual_wear", "spread_only",
      "sudden_shift", "sensor_bias", "sensor_bias", "overtorque",
      "intermittent", "pure_transducer_drift", "pure_transducer_drift",
      "lubrication_loss", "post_calibration_reset"]] +
    [("spotweld", c) for c in
     ["healthy"] * 3 + ["gradual_wear", "gradual_wear", "spread_only",
      "sensor_bias", "pure_transducer_drift", "lubrication_loss",
      "post_calibration_reset"]] +
    [("adhesive", c) for c in
     ["healthy"] * 2 + ["gradual_wear", "spread_only", "sudden_shift",
      "overtorque", "intermittent_connector"]] +
    [("pressfit", c) for c in
     ["healthy"] * 2 + ["gradual_wear", "sudden_shift", "sensor_bias",
      "lubrication_loss", "batch_material_shift"]]
)
# batch_material_shift also silently affects every nutrunner via the lot table.

TARGET_RANGES = dict(nutrunner=(18, 95), spotweld=(140, 220),
                     adhesive=(8.0, 14.0), pressfit=(6.0, 18.0))
TOL_RANGES = dict(nutrunner=(0.08, 0.15), spotweld=(0.10, 0.16),
                  adhesive=(0.10, 0.18), pressfit=(0.09, 0.14))


def ambient_profile(rng, n_ops, station):
    """Shared environment: daily cycle + post-break warm-up transients."""
    tsec = (np.arange(n_ops) + station) * TAKT_S
    day = 1.6 * np.sin(2 * np.pi * (tsec % 86400) / 86400 - 1.1)
    warm = np.zeros(n_ops)
    for i in range(n_ops):
        into_shift = i % SHIFT_LEN_OPS
        for b in BREAKS_AT:
            if 0 <= into_shift - b < 25:      # 25-op warm-up after each break
                warm[i] -= 1.8 * np.exp(-(into_shift - b) / 8.0)
    return day + warm


FASTENER_TYPES = ("M8x1.25", "M10x1.5", "M12x1.75")


def build_lot_table(rng, n_ops):
    """Fastener lots, per fastener TYPE.

    A lot is a delivery of one part number, so it reaches only the stations
    that consume that part - not the whole plant. That matters: it makes
    material-vs-tool discrimination a real inference problem (which tools
    share this lot?) rather than a trivial "everything moved at once".

    The lot id is carried in the observed telemetry because a real MES
    records which lot was loaded. The *badness* of a lot is not observed.
    """
    rows = {}
    shifts = {}
    for ti, ftype in enumerate(FASTENER_TYPES):
        s = np.zeros(n_ops)
        ids = np.empty(n_ops, dtype=object)
        v, k = 0, 0
        bad_ks = set(rng.choice(np.arange(2, 14), size=2, replace=False).tolist())
        while v < n_ops:
            ln = int(rng.integers(900, 1500))
            lot_id = f"LOT{2600 + ti * 100 + k}"
            bad = k in bad_ks
            shift = float(rng.uniform(0.25, 0.45)) if bad else 0.0
            rows.setdefault(ftype, []).append(dict(
                fastener_type=ftype, lot_id=lot_id,
                op_from=v, op_to=min(v + ln, n_ops) - 1,
                hardness_shift_frac=round(shift, 3), is_bad=int(bad)))
            s[v:v + ln] = shift
            ids[v:v + ln] = lot_id
            v += ln
            k += 1
        shifts[ftype] = (s, ids)
    flat = pd.DataFrame([r for v in rows.values() for r in v])
    return flat, shifts


def build_set(seed, roster, outdir, firewall=False, with_lots=True,
              with_imperfections=True):
    rng = np.random.default_rng(seed)
    os.makedirs(outdir, exist_ok=True)
    hidden = os.path.join(outdir, "hidden")
    os.makedirs(hidden, exist_ok=True)

    stations = rng.choice(np.arange(1, 41), size=len(roster), replace=False)
    stations.sort()
    lot_df, lot_frac = (build_lot_table(rng, N_OPS) if with_lots
                        else (pd.DataFrame(), None))

    frames = {f: [] for f in FAMILIES}
    op_truth = {f: [] for f in FAMILIES}
    truths, maint_rows, imperf_rows, eol_pool = [], [], [], []

    for i, (fam, cond) in enumerate(roster):
        st = int(stations[i])
        target = float(rng.uniform(*TARGET_RANGES[fam]))
        tolp = float(rng.uniform(*TOL_RANGES[fam]))
        onset = int(rng.integers(5000, 15000)) if cond != "healthy" else -1
        wear = int(rng.integers(2200, 4800)) if cond != "healthy" else -1
        n_serv = N_OPS // int(rng.integers(1800, 2400))
        service_ops = sorted(int(rng.integers(1500, N_OPS - 500))
                             for _ in range(max(n_serv, 2)))
        if cond == "post_calibration_reset":
            # a maintenance visit must actually land after the drift starts,
            # otherwise the condition silently degenerates into gradual_wear
            service_ops = sorted(set(service_ops + [onset + int(0.45 * wear)]))
        skew = float(rng.uniform(-3, 3))
        t = ToolSpec(tool_id=f"{fam[:2].upper()}-{st:02d}{chr(65 + i % 26)}",
                     family=fam, station_id=st, condition=cond, target=target,
                     tol_pct=tolp, onset_op=onset, wear_ops=wear,
                     program_id=f"{FAMILIES[fam]['program_prefix']}{100 + i}",
                     clock_skew_s=skew, service_ops=service_ops)

        amb = ambient_profile(rng, N_OPS, st)
        ftype = FASTENER_TYPES[i % len(FASTENER_TYPES)]
        lot_s, lot_ids = lot_frac[ftype] if lot_frac else (np.zeros(N_OPS), None)
        uses_fasteners = fam in ("nutrunner", "pressfit")
        lshift = (lot_s * target * tolp
                  if (with_lots and uses_fasteners) else np.zeros(N_OPS))

        ch, true_prim, tdef, nok, truth, imperf = generate_tool(
            rng, t, N_OPS, amb, lshift, firewall=firewall)
        truths.append(truth)
        imperf_rows += imperf

        op = np.arange(N_OPS)
        tol = target * tolp
        df = pd.DataFrame(dict(
            timestamp=T0 + pd.to_timedelta((op + st) * TAKT_S + skew, unit="s"),
            vin=[f"VIN{200000 + k}" for k in op],
            station_id=st, tool_id=t.tool_id, program_id=t.program_id,
            target=round(target, 2), spec_low=round(target - tol, 2),
            spec_high=round(target + tol, 2)))
        # the MES knows which fastener lot is loaded; it does NOT know
        # whether that lot is bad. Carrying the id makes material-vs-tool
        # attribution a solvable inference rather than a guess.
        if with_lots and uses_fasteners and lot_ids is not None:
            df["fastener_type"] = ftype
            df["fastener_lot"] = lot_ids
        for name, arr in ch.items():
            df[name] = np.round(arr, 3)
        df["result_status"] = np.where(nok, "NOK", "OK")
        df["batch_counter"] = op % 250
        frames[fam].append(df)

        op_truth[fam].append(pd.DataFrame(dict(
            vin=df.vin, tool_id=t.tool_id,
            true_value=np.round(true_prim, 3), true_defective=tdef)))

        # per-defect EOL pool (caught with p at true EOL arrival time)
        d_ops = np.flatnonzero(tdef)
        if d_ops.size:
            caught = rng.random(d_ops.size) < EOL_CATCH_P
            eol_pool.append(pd.DataFrame(dict(
                vin=[f"VIN{200000 + k}" for k in d_ops], tool_id=t.tool_id,
                caught=caught,
                t_eol=T0 + pd.to_timedelta((d_ops + EOL_STATION) * TAKT_S, unit="s"))))

        # maintenance log: every scheduled visit records as-found/as-left
        x = df[FAMILIES[fam]["primary"]].values
        for s_op in service_ops:
            seg = x[max(0, s_op - 500):s_op]
            seg = seg[~np.isnan(seg)]
            sd = seg.std(ddof=1) if len(seg) > 30 else np.nan
            mu = seg.mean() if len(seg) > 30 else np.nan
            cmk = min(target + tol - mu, mu - (target - tol)) / (3 * sd) if sd and sd > 0 else np.nan
            adjusted = truth["reset_ops"] and str(s_op) in truth["reset_ops"].split(";")
            maint_rows.append(dict(
                tool_id=t.tool_id, family=fam, service_op=s_op,
                timestamp=T0 + pd.to_timedelta((s_op + st) * TAKT_S, unit="s"),
                kind="calibration" if adjusted else "scheduled_check",
                as_found_cmk=round(float(cmk), 3) if cmk == cmk else "",
                as_left_cmk=round(float(rng.uniform(1.45, 1.75)), 3) if adjusted else "",
                technician_shift=int(rng.integers(1, 4))))

    # ---------------------------------------------------------------- write
    for fam, lst in frames.items():
        if not lst:
            continue
        big = pd.concat(lst, ignore_index=True).sort_values(["timestamp", "tool_id"])
        if with_imperfections:
            n = len(big)
            drop = rng.random(n) < 0.002
            dup = rng.random(n) < 0.0005
            for idx in np.flatnonzero(drop)[:20000]:
                pass
            imperf_rows += [dict(tool_id="*", channel="*", kind="row_dropped",
                                 start_op=-1, len_ops=int(drop.sum())),
                            dict(tool_id="*", channel="*", kind="row_duplicated",
                                 start_op=-1, len_ops=int(dup.sum()))]
            big = pd.concat([big[~drop], big[dup]], ignore_index=True) \
                .sort_values(["timestamp", "tool_id"])
        big.to_csv(os.path.join(outdir, f"{fam}.csv"), index=False)
        pd.concat(op_truth[fam], ignore_index=True).to_csv(
            os.path.join(hidden, f"op_truth_{fam}.csv"), index=False)

    pd.DataFrame(truths).to_csv(os.path.join(hidden, "ground_truth.csv"), index=False)
    pd.DataFrame(maint_rows).to_csv(os.path.join(outdir, "maintenance_log.csv"), index=False)
    if with_lots and len(lot_df):
        # OBSERVED: lot ids, types and windows (the MES has these).
        lot_df.drop(columns=["hardness_shift_frac", "is_bad"]).to_csv(
            os.path.join(outdir, "material_lots.csv"), index=False)
        # HIDDEN: which lots were actually out of spec, and by how much.
        lot_df.to_csv(os.path.join(hidden, "material_lots_truth.csv"), index=False)
    if imperf_rows:
        pd.DataFrame(imperf_rows).to_csv(
            os.path.join(hidden, "imperfection_log.csv"), index=False)

    if eol_pool:
        e = pd.concat(eol_pool, ignore_index=True)
        # OBSERVED: end-of-line only knows what it CAUGHT. True defect counts
        # would be information leakage - they live in hidden/ only.
        caught = e[e.caught].groupby("vin").agg(
            defects_found=("tool_id", "count"), t_eol=("t_eol", "first"),
            defect_codes=("tool_id", lambda s: ";".join(sorted(set(s))))).reset_index()
        caught["eol_result"] = "FAIL"
        caught.sort_values("t_eol").to_csv(
            os.path.join(outdir, "quality_results.csv"), index=False)
        # HIDDEN: full truth per vehicle, caught or not
        full = e.groupby("vin").agg(
            true_defective_joints=("tool_id", "count"),
            caught_joints=("caught", "sum"), t_eol=("t_eol", "first")).reset_index()
        full.sort_values("t_eol").to_csv(
            os.path.join(hidden, "eol_truth.csv"), index=False)

    tdf = pd.DataFrame(truths)
    return tdf


if __name__ == "__main__":
    print("=== main set (%d tools x %d ops) ===" % (len(MAIN_ROSTER), N_OPS))
    t1 = build_set(MAIN_SEED, MAIN_ROSTER, OUT)
    print(t1[["tool_id", "family", "condition", "true_onset_op",
              "total_true_defects", "total_controller_nok",
              "defects_passed_ok"]].to_string(index=False))

    print("\n=== held-out healthy set (16 tools) ===")
    hold = [(f, "healthy") for f in
            ["nutrunner"] * 6 + ["spotweld"] * 4 + ["adhesive"] * 3 + ["pressfit"] * 3]
    build_set(HOLDOUT_SEED, hold, os.path.join(OUT, "holdout"),
              with_lots=False, with_imperfections=False)
    print("written")

    print("\n=== evaluation firewall set (12 tools, Wiener damage) ===")
    fw = [("nutrunner", c) for c in
          ["healthy", "healthy", "gradual_wear", "gradual_wear", "sensor_bias",
           "pure_transducer_drift", "spread_only", "lubrication_loss"]] + \
         [("spotweld", "gradual_wear"), ("spotweld", "healthy"),
          ("pressfit", "gradual_wear"), ("adhesive", "healthy")]
    t3 = build_set(FIREWALL_SEED, fw, os.path.join(OUT, "firewall"),
                   firewall=True, with_lots=False)
    print(t3[["tool_id", "condition", "total_true_defects",
              "defects_passed_ok"]].to_string(index=False))
    print("\ndone.")
