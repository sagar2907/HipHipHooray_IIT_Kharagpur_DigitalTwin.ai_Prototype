#!/usr/bin/env python3
"""Complexity 1, second half: is the manual checklist telling the truth?

    python scripts/eval_manual_checks.py

The design (Part A 1.3) makes a specific, testable claim: a manual checklist is
not a sensor. It is low-frequency, categorical, recorded late, and above all
CONFIRMATION-BIASED - a checklist that always reads OK is measuring compliance
with the checklist, not quality.

And it names the test: compare the checklist's pass rate against the EOL
failures attributable to that station. If the checklist says 100% and end-of-
line says 2% fail, the checklist is not seeing what it claims to see.

That test had never been run. This runs it.

Run on the L5 segmented layout, the only one carrying manual_check.csv. The
DEMO stays on L1 - this is evidence, not a change of dataset, and the
distinction is kept deliberately because switching the demo the day before a
recording is how demos break.
"""

import argparse
import glob
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.join(HERE, "..", "..", "digitaltwin.ai", "dataset",
                    "v6_segmented", "flow", "runs")
RESULTS = os.path.join(HERE, "..", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", default=FLOW)
    a = ap.parse_args()

    runs = sorted(glob.glob(os.path.join(a.flow, "L5_run_*")))
    if not runs:
        sys.exit(f"no L5 runs under {a.flow} - build with scripts/build_v6_segmented.py")

    rows = []
    for rd in runs:
        mp = os.path.join(rd, "manual_check.csv")
        rw = os.path.join(rd, "rework_log.csv")
        if not (os.path.exists(mp) and os.path.exists(rw)):
            continue
        mc = pd.read_csv(mp)
        rework = pd.read_csv(rw)
        # EOL failures, via the VIN thread - genealogy is what lets us attribute
        eol_fail = set(rework[rework.event == "fail"].vin)

        for st, g in mc.groupby("station_id"):
            n = len(g)
            nok = int((g.result == "NOK").sum())
            # vehicles this station passed that EOL later failed
            passed = set(g[g.result == "OK"].unit_id)
            escaped = len(passed & eol_fail)
            rows.append(dict(
                run=os.path.basename(rd), station=st, checks=n, nok=nok,
                pass_rate=round(100 * (n - nok) / n, 2),
                passed_but_eol_failed=escaped,
                escape_rate=round(100 * escaped / max(len(passed), 1), 2),
                mean_latency_min=round(g.entry_latency_s.mean() / 60, 1)))

    df = pd.DataFrame(rows)
    if df.empty:
        sys.exit("no manual_check data found")

    tot_checks = int(df.checks.sum())
    tot_nok = int(df.nok.sum())
    pass_rate = 100 * (tot_checks - tot_nok) / tot_checks
    tot_escape = int(df.passed_but_eol_failed.sum())
    mean_lat = df.mean_latency_min.mean()

    print("=" * 78)
    print("MANUAL CHECKLIST — is it seeing what it claims to see?")
    print("=" * 78)
    print(f"  runs analysed          {df.run.nunique()}  (L5 segmented layout)")
    print(f"  stations on checklists {df.station.nunique()}")
    print(f"  checklist entries      {tot_checks:,}")
    print()
    print(f"  checklist PASS RATE    {pass_rate:.2f}%   ({tot_nok:,} NOK of {tot_checks:,})")
    print(f"  vehicles passed by the checklist that EOL later failed: {tot_escape:,}")
    print(f"  -> escape rate         {100*tot_escape/max(tot_checks-tot_nok,1):.2f}%")
    print()
    print(f"  mean ENTRY LATENCY     {mean_lat:.1f} min")
    print("     the gap between the work happening and a human recording it.")
    print("     For that window the twin has no signal from this station at all —")
    print("     which is why manual data is a fourth tier (attested), not a sensor.")
    print()
    print("  READING IT: the checklist passes ~%.0f%% of vehicles, and ~%.1f%% of those"
          % (pass_rate, 100 * tot_escape / max(tot_checks - tot_nok, 1)))
    print("  it passed went on to fail end-of-line. A checklist reading near-100%%")
    print("  against a non-zero EOL failure rate is measuring compliance with the")
    print("  checklist, not quality — exactly the failure the design predicted, and")
    print("  the same shape as our sensor_bias tools: the instrument is the thing")
    print("  that is wrong.")

    out = os.path.join(RESULTS, "manual_check_eval.csv")
    df.to_csv(out, index=False)
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
