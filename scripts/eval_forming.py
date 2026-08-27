#!/usr/bin/env python3
"""
Score the FORMING layer - the brief's opening clause.

Two questions, answered separately because they are different claims:

  1. Buffer countdown accuracy. When the twin says "B07 fills in 6 minutes",
     does the station behind it actually block ~6 minutes later? Scored as
     error in minutes against what the hidden state log shows happened.

  2. Overtake risk calibration. When the twin says "S14 has a 0.7 chance of
     becoming the constraint within the hour", is it right about 70% of the
     time? Scored against truth/sensitivity.csv.

Both are reported including where they fail. A countdown that is only accurate
once the buffer is nearly full is not useful, so accuracy is broken out by how
far ahead the warning was - the far-ahead bands are the ones that matter.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from twin.detect import Detector                                # noqa: E402
from twin.events import load_run, state_spans                   # noqa: E402
from twin.forming import buffer_countdowns, overtake_risk       # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset", "v5")
FLOW = os.path.join(BASE, "flow")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def first_block_after(spans, station, t0, horizon=3600):
    for a, b, v in spans.get(station, []):
        if v == "blocked" and a >= t0:
            return a - t0 if a - t0 <= horizon else None
    return None


def main(limit=40):
    man = pd.read_csv(os.path.join(FLOW, "run_manifest.csv"))
    runs = man[man.n_shifts == 1].run.tolist()[:limit]
    cd_rows, ov_rows = [], []

    for k, tag in enumerate(runs):
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        run = load_run(rd, k)
        bufs = pd.read_csv(os.path.join(rd, "buffer_level.csv"))
        # blocking truth comes from the FULL state log; the detector never sees
        # it, we only use it to score
        full = pd.read_csv(os.path.join(rd, "hidden", "station_state_full.csv"))
        spans = state_spans(full, run.horizon_s)

        for at in range(2400, run.horizon_s - 1800, 900):
            for c in buffer_countdowns(bufs, at)[:3]:
                # only score genuine forward-looking warnings: the buffer must
                # have slack left and be filling toward capacity
                if (not np.isfinite(c.minutes_to_full)
                        or c.minutes_to_full <= 0 or c.minutes_to_full > 45
                        or c.level >= c.capacity):
                    continue
                actual = first_block_after(spans, c.blocks_station, at)
                cd_rows.append(dict(
                    run=tag, at_s=at, buffer=c.buffer_id,
                    station=c.blocks_station, predicted_min=c.minutes_to_full,
                    actual_min=(actual / 60.0) if actual is not None else np.nan,
                    confidence=c.confidence))
        if (k + 1) % 10 == 0:
            print(f"  ...countdown {k+1}/{len(runs)}", flush=True)

    cd = pd.DataFrame(cd_rows)
    os.makedirs(RESULTS, exist_ok=True)
    cd.to_csv(os.path.join(RESULTS, "forming_buffer_countdown.csv"), index=False)

    print("\n" + "=" * 72)
    print("1. BUFFER COUNTDOWN - does the block arrive when predicted?")
    print("=" * 72)
    hit = cd.dropna(subset=["actual_min"])
    print(f"predictions made: {len(cd)}   station did block within the hour: "
          f"{len(hit)} ({100*len(hit)/max(len(cd),1):.0f}%)")
    if len(hit):
        err = hit.actual_min - hit.predicted_min
        print(f"\nerror (actual - predicted) in minutes:")
        print(f"  median {err.median():+.1f}   mean {err.mean():+.1f}   "
              f"IQR {err.quantile(.25):+.1f} to {err.quantile(.75):+.1f}")
        h = hit.assign(band=pd.cut(hit.predicted_min, [0, 5, 15, 30, 45],
                                   labels=["<5 min", "5-15", "15-30", "30-45"]))
        rows = []
        for b, g in h.groupby("band", observed=True):
            e = g.actual_min - g.predicted_min
            rows.append(dict(band=str(b), n=len(g),
                             median_err_min=round(float(e.median()), 1),
                             within_5min=round(float((e.abs() <= 5).mean()), 2)))
        print("\nby how far ahead the warning was:")
        print(pd.DataFrame(rows).to_string(index=False))

    print("\n" + "=" * 72)
    print("2. OVERTAKE RISK - is the stated probability calibrated?")
    print("=" * 72)
    truth = pd.read_csv(os.path.join(BASE, "truth", "sensitivity.csv"))
    for k, tag in enumerate(runs[:20]):
        rd = os.path.join(FLOW, "runs", tag)
        if not os.path.exists(rd):
            continue
        run = load_run(rd, k)
        det = Detector(run)
        t = truth[truth.run == tag]
        for _, tr in t.iterrows():
            at = int(tr.block) * 3600
            if at < 3 * det.window_s or at + 3600 > run.horizon_s:
                continue
            nxt = t[t.block == tr.block + 1]
            if nxt.empty:
                continue
            future = nxt.primary.iloc[0]
            for o in overtake_risk(det, at):
                ov_rows.append(dict(run=tag, block=int(tr.block), station=o.station,
                                    p60=o.p_within.get(60, 0.0),
                                    became=int(o.station == future)))
        if (k + 1) % 10 == 0:
            print(f"  ...risk {k+1}/20", flush=True)

    ov = pd.DataFrame(ov_rows)
    if len(ov):
        ov.to_csv(os.path.join(RESULTS, "forming_overtake_risk.csv"), index=False)
        ov["bin"] = pd.cut(ov.p60, [-.01, .1, .3, .5, .7, 1.0],
                           labels=["0-10%", "10-30%", "30-50%", "50-70%", "70-100%"])
        rel = ov.groupby("bin", observed=True).agg(
            n=("became", "size"), predicted=("p60", "mean"),
            actually_became=("became", "mean"))
        print(rel.round(3).to_string())
        print("\n-> a calibrated forecaster has 'predicted' and 'actually_became'")
        print("   close on every row. Divergence IS the finding, not a failure.")
    else:
        print("  no scoreable overtake predictions")
    print("\nwritten: results/forming_*.csv")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else 40)
