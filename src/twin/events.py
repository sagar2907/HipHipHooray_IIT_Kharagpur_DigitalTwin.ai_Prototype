"""Event ingestion and state reconstruction.

Everything downstream of this module works from the five event types a real
plant already emits. Nothing here assumes access to anything a plant would
have to buy new hardware to provide.

The important object is the *active period*: a maximal uninterrupted span in
which a station is working or under repair - that is, not waiting on a
neighbour. Roser's bottleneck criterion is defined on these spans, so the
whole flow model is built on top of this one construction.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

# A station is "active" when it is doing its own work - producing, or being
# repaired. It is *inactive* only when a neighbour is holding it up.
ACTIVE_STATES = ("working", "down")


@dataclass
class Run:
    """One simulated shift, loaded from the observed event logs."""

    run_id: int
    scans: pd.DataFrame          # vin, station_id, event, t_s
    states: pd.DataFrame         # station_id, state, t_s  (transitions)
    buffers: pd.DataFrame        # buffer_id, level, capacity, t_s
    horizon_s: int

    @property
    def observed_stations(self) -> list[str]:
        """Spine stations that emit state data. Dark stations are absent."""
        s = sorted({x for x in self.states.station_id.unique() if x.startswith("S")})
        return s


def load_run(run_dir: str, run_id: int, horizon_s: int = 8 * 3600) -> Run:
    """Load the OBSERVED logs for one run.

    Deliberately does not touch hidden/ - a detector that reads ground truth
    is not a detector. The evaluation harness loads hidden/ separately.
    """
    return Run(
        run_id=run_id,
        scans=pd.read_csv(os.path.join(run_dir, "unit_scan.csv")),
        states=pd.read_csv(os.path.join(run_dir, "station_state.csv")),
        buffers=pd.read_csv(os.path.join(run_dir, "buffer_level.csv")),
        horizon_s=horizon_s,
    )


def state_spans(states: pd.DataFrame, horizon_s: int) -> dict[str, list[tuple]]:
    """Expand a transition log into (start, end, state) spans per station.

    The log records only changes, so a state persists until the next
    transition for that station, or until the end of the shift.
    """
    out: dict[str, list[tuple]] = {}
    for station, g in states.sort_values("t_s").groupby("station_id"):
        t = g.t_s.to_numpy()
        s = g.state.to_numpy()
        ends = np.append(t[1:], horizon_s)
        out[station] = [(int(a), int(b), str(v))
                        for a, b, v in zip(t, ends, s) if b > a]
    return out


def active_periods(spans: list[tuple]) -> list[tuple[int, int]]:
    """Merge consecutive active spans into maximal active periods.

    Two adjacent working spans separated by a 'down' span are ONE active
    period, not two - the station never stopped working on its own account.
    That merge is the whole subtlety of the method: it is what separates a
    station that is genuinely busy from one that is merely often busy.
    """
    periods: list[list[int]] = []
    for a, b, v in spans:
        if v not in ACTIVE_STATES:
            continue
        if periods and periods[-1][1] == a:
            periods[-1][1] = b
        else:
            periods.append([a, b])
    return [(a, b) for a, b in periods]


def window_active_stats(periods: list[tuple[int, int]], w0: int, w1: int):
    """Average active-period length, and active share, over a window.

    Two different clippings, deliberately:

    * The average period length uses each period's TRUE elapsed duration,
      measured from its real start (which may precede the window) up to the
      present moment. Clipping a period at the window edge instead would
      saturate every long period at the window width, and every station that
      never paused would tie at the maximum - which destroys exactly the
      discrimination Roser's method exists to provide.
    * The active share is clipped to the window, because that is what
      utilisation means: the fraction of this window spent producing.

    Both stay causal: nothing is measured past w1.
    """
    if w1 <= w0:
        # zero-width window: happens when a caller asks for a verdict at t=0,
        # before any history exists. There is nothing to average, and dividing
        # by the window width would raise. No opinion is the honest answer.
        return 0.0, 0.0
    lens, total = [], 0
    for a, b in periods:
        if b <= w0 or a >= w1:
            continue
        total += min(b, w1) - max(a, w0)
        lens.append(min(b, w1) - a)          # true elapsed length so far
    if not lens:
        return 0.0, 0.0
    return float(np.mean(lens)), total / float(w1 - w0)


def forced_idle_share(spans: list[tuple], w0: int, w1: int) -> float:
    """Fraction of the window spent blocked or starved - i.e. waiting on a
    neighbour. The bottleneck is the station with the least of this."""
    if w1 <= w0:
        return 0.0                    # same zero-width guard as above
    idle = 0
    for a, b, v in spans:
        if v in ACTIVE_STATES or b <= w0 or a >= w1:
            continue
        idle += max(0, min(b, w1) - max(a, w0))
    return idle / float(w1 - w0)


def cycle_times_from_scans(scans: pd.DataFrame) -> pd.DataFrame:
    """Per-unit dwell time at each station, from boundary scans alone.

    This is the measurement that needs no sensor inside the station: an
    in-scan and an out-scan bracket the time the unit spent there. It
    includes waiting as well as work, which is exactly the confound the
    dark-station estimator has to resolve later.
    """
    p = scans.pivot_table(index=["vin", "station_id"], columns="event",
                          values="t_s", aggfunc="first")
    p = p.dropna(subset=["in", "out"])
    p["dwell_s"] = p["out"] - p["in"]
    return p.reset_index()[["vin", "station_id", "in", "out", "dwell_s"]] \
            .rename(columns={"in": "t_in", "out": "t_out"})
