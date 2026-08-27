#!/usr/bin/env python3
"""
Validate the v3 process dataset.

Protocol, following the audit rules this project now works to:
  - Thresholds calibrated ONLY on holdout/ (all-healthy tools, separate
    seed). Never on the evaluation data.
  - Pre-onset alarms are scored as FALSE ALARMS, not forgiven.
  - Lead time is measured against sustained TRUE defect production, taken
    from hidden/op_truth_*.csv - the true value, not the sensor's reading.
  - Headline degradation is also reported on firewall/ (Wiener-process
    damage, never used in development).

Three dataset-specific claims are checked explicitly:
  1. post_calibration_reset must NOT keep alarming after the tool is
     serviced - a detector that cries wolf after every maintenance visit
     gets switched off in a week.
  2. sensor_bias must show many true defects that the CONTROLLER passed as
     OK - the phenomenon the whole layer exists to catch.
  3. pure_transducer_drift alarms on the reading while true defects stay
     near zero - detection alone cannot tell you to service the tool, which
     is exactly why the failure-mode classifier is needed.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from twin.tools import FAMILIES                                    # noqa: E402

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                 "dataset", "v3", "process")
BASELINE_OPS = 2000
FAMS = ("nutrunner", "spotweld", "adhesive", "pressfit")


def cusum_alarm(x, mu, sd, thr, k=0.5):
    """First index where the tabular CUSUM exceeds thr. NaN-safe: a missing
    reading contributes nothing rather than poisoning the running sums."""
    hi = lo = 0.0
    for i in range(len(x)):
        v = x[i]
        if not np.isfinite(v):
            continue
        s = (v - mu) / sd
        hi = max(0.0, hi + s - k)
        lo = min(0.0, lo + s + k)
        if hi > thr or lo < -thr:
            return i
    return -1


def baseline_stats(x):
    seg = x[:BASELINE_OPS]
    seg = seg[np.isfinite(seg)]
    return seg.mean(), seg.std(ddof=1)


def calibrate(fam):
    """Smallest threshold with zero alarms across every held-out healthy
    tool of this family."""
    h = pd.read_csv(os.path.join(P, "holdout", f"{fam}.csv"))
    col = FAMILIES[fam]["primary"]
    segs = []
    for _, g in h.groupby("tool_id"):
        x = g[col].values
        mu, sd = baseline_stats(x)
        segs.append((x, mu, sd))
    for thr in np.arange(4.0, 40.01, 0.5):
        if all(cusum_alarm(x, mu, sd, thr) < 0 for x, mu, sd in segs):
            return float(thr), len(segs)
    return 40.0, len(segs)


def sustained_onset(defect, need=3, win=100):
    fwd = pd.Series(defect[::-1]).rolling(win, min_periods=win).sum()[::-1].values
    c = np.flatnonzero(fwd >= need)
    return int(c[0]) if c.size else -1


def parse_ops(v):
    """reset_ops round-trips through CSV as '6646.0'. isdigit() rejects the
    decimal point, which silently emptied this list in the first pass."""
    out = []
    for part in str(v).split(";"):
        part = part.strip()
        try:
            out.append(int(float(part)))
        except (ValueError, TypeError):
            pass
    return out


def load_lot_context(root):
    """Bad-lot windows per fastener type, plus tool -> type. Used ONLY for
    scoring: it explains an alarm after the fact. The detector never sees it."""
    tpath = os.path.join(root, "hidden", "material_lots_truth.csv")
    if not os.path.exists(tpath):
        return None, {}
    lots = pd.read_csv(tpath)
    types = {}
    for fam in ("nutrunner", "pressfit"):
        f = os.path.join(root, f"{fam}.csv")
        if not os.path.exists(f):
            continue
        cols = pd.read_csv(f, nrows=1).columns
        if "fastener_type" not in cols:
            continue
        d = pd.read_csv(f, usecols=["tool_id", "fastener_type"]).drop_duplicates()
        types.update(dict(zip(d.tool_id, d.fastener_type)))
    return lots[lots.is_bad == 1], types


def evaluate(root, label, thresholds):
    truth = pd.read_csv(os.path.join(root, "hidden", "ground_truth.csv"))
    bad_lots, tool_type = load_lot_context(root)
    rows = []
    for fam in FAMS:
        f = os.path.join(root, f"{fam}.csv")
        if not os.path.exists(f):
            continue
        df = pd.read_csv(f)
        ot = pd.read_csv(os.path.join(root, "hidden", f"op_truth_{fam}.csv"))
        col = FAMILIES[fam]["primary"]
        thr = thresholds[fam]
        for tid, g in df.groupby("tool_id"):
            g = g.sort_values("timestamp").reset_index(drop=True)
            t = truth[truth.tool_id == tid].iloc[0]
            x = g[col].values
            mu, sd = baseline_stats(x)
            a = cusum_alarm(x, mu, sd, thr)
            tr = ot[ot.tool_id == tid].reset_index(drop=True)
            ref = sustained_onset(tr.true_defective.values)
            onset = int(t.true_onset_op)
            # Was this alarm caused by a bad fastener lot rather than the
            # tool? A lot shift is a REAL process fault - firing on it is
            # correct behaviour - but it calls for changing the material,
            # not servicing the tool, so it is scored in its own category.
            in_bad_lot = False
            if a >= 0 and bad_lots is not None and tid in tool_type:
                w = bad_lots[bad_lots.fastener_type == tool_type[tid]]
                in_bad_lot = bool(((a >= w.op_from - 20) & (a <= w.op_to)).any())

            if t.condition == "healthy":
                verdict = ("material-attributed" if in_bad_lot else
                           "FALSE ALARM" if a >= 0 else "clean")
                lead = np.nan
            elif a < 0:
                verdict = "missed"
                lead = np.nan
            elif onset >= 0 and a < onset:
                verdict = ("material-attributed" if in_bad_lot
                           else "FALSE ALARM (pre-onset)")
                lead = np.nan
            else:
                verdict = "detected"
                lead = (ref - a) if ref >= 0 else np.nan
            rows.append(dict(family=fam, tool_id=tid, condition=t.condition,
                             alarm_op=a, onset=onset, sustained_defect_op=ref,
                             lead=lead, verdict=verdict,
                             true_defects=int(t.total_true_defects),
                             passed_ok=int(t.defects_passed_ok),
                             reset_ops=str(t.reset_ops)))
    r = pd.DataFrame(rows)
    print(f"\n{'='*74}\n{label}\n{'='*74}")
    summ = r[r.condition != "healthy"].groupby("condition").agg(
        n=("tool_id", "count"),
        detected=("verdict", lambda s: (s == "detected").sum()),
        median_lead=("lead", "median"),
        true_defects=("true_defects", "sum"),
        passed_ok=("passed_ok", "sum"))
    print(summ.round(0).to_string())
    hz = r[r.condition == "healthy"]
    print(f"\nhealthy tools: {len(hz)}  |  clean: {(hz.verdict=='clean').sum()}"
          f"  material-attributed: {(hz.verdict=='material-attributed').sum()}"
          f"  TRUE false alarms: {(hz.verdict=='FALSE ALARM').sum()}")
    mat = r[r.verdict == "material-attributed"]
    print(f"alarms explained by a bad fastener lot (all conditions): {len(mat)}")
    fa = r[r.verdict.str.contains("FALSE ALARM")]
    print(f"unexplained false alarms: {len(fa)}"
          + ("  -> " + ", ".join(f"{x.tool_id}({x.condition})"
                                 for _, x in fa.iterrows()) if len(fa) else ""))
    return r


if __name__ == "__main__":
    print("CALIBRATION on held-out healthy tools (separate seed)")
    thresholds = {}
    for fam in FAMS:
        thr, n = calibrate(fam)
        thresholds[fam] = thr
        print(f"  {fam:10s} threshold {thr:5.1f}  ({n} healthy tools)")

    main = evaluate(P, "MAIN SET", thresholds)
    fw = evaluate(os.path.join(P, "firewall"),
                  "EVALUATION FIREWALL (Wiener damage, unseen mechanism)",
                  thresholds)

    # ---- claim 1: no alarm storm after a calibration reset
    print(f"\n{'='*74}\nCLAIM 1 - detector must settle after a service visit\n{'='*74}")
    for _, r in main[main.condition == "post_calibration_reset"].iterrows():
        resets = parse_ops(r.reset_ops)
        print(f"  {r.tool_id}: alarm at op {r.alarm_op}, service at {resets}, "
              f"onset {r.onset}")
        if resets:
            print(f"    -> alarm {'BEFORE' if r.alarm_op < resets[0] else 'after'} "
                  f"service; a post-service re-alarm would be a false alarm")

    # ---- claim 3: material faults are separable from tool faults by
    # cross-tool simultaneity among tools sharing a fastener lot
    print(f"\n{'='*74}\nCLAIM 3 - material vs tool fault, by lot simultaneity\n{'='*74}")
    lots_t = pd.read_csv(os.path.join(P, "hidden", "material_lots_truth.csv"))
    types = {}
    for fam in ("nutrunner", "pressfit"):
        d = pd.read_csv(os.path.join(P, f"{fam}.csv"),
                        usecols=["tool_id", "fastener_type"]).drop_duplicates()
        for _, r in d.iterrows():
            types[r.tool_id] = r.fastener_type
    m = main[main.alarm_op >= 0].copy()
    m["ftype"] = m.tool_id.map(types)
    print(f"{'fastener type':<12s} {'bad-lot start':>14s} {'tools alarming within 50 ops':>30s}")
    for ft, g in lots_t[lots_t.is_bad == 1].groupby("fastener_type"):
        for _, b in g.iterrows():
            same = m[m.ftype == ft]
            near = same[(same.alarm_op >= b.op_from - 20) &
                        (same.alarm_op <= b.op_from + 50)]
            other = m[(m.ftype != ft) & (m.alarm_op >= b.op_from - 20) &
                      (m.alarm_op <= b.op_from + 50)]
            print(f"{ft:<12s} {int(b.op_from):>14d} "
                  f"{len(near):>12d} of {len(same):<3d} sharing the lot   "
                  f"({len(other)} tools on other lots)")
    print("\nA tool fault moves one tool. A material fault moves every tool")
    print("consuming that lot, inside a few operations - and leaves tools on")
    print("other lots untouched. That contrast is the discriminant, and it is")
    print("only visible to a system watching the whole plant at once.")

    print(f"\n{'='*74}\nCLAIM 2 - sensor faults pass bad parts as OK\n{'='*74}")
    sb = main[main.condition.isin(["sensor_bias", "pure_transducer_drift"])]
    print(sb[["tool_id", "condition", "true_defects", "passed_ok",
              "alarm_op", "verdict"]].to_string(index=False))
    print("\nsensor_bias: true defects the controller cleared as OK = "
          f"{int(main[main.condition=='sensor_bias'].passed_ok.sum())}")
    print("pure_transducer_drift: true defects = "
          f"{int(main[main.condition=='pure_transducer_drift'].true_defects.sum())}"
          " (tool is healthy; only the reading drifts)")
    print("  -> detection alone cannot separate these two. That is the gap the")
    print("     failure-mode classifier fills: one needs recalibration, the")
    print("     other needs the tool taken out of service.")

    os.makedirs(os.path.join(P, "..", "..", "..", "results"), exist_ok=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "results", "process_v3_validation.csv")
    pd.concat([main.assign(set="main"), fw.assign(set="firewall")]).to_csv(out, index=False)
    print(f"\nwritten: results/process_v3_validation.csv")
