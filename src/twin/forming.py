"""Where a bottleneck is FORMING - the brief's opening clause.

Detection answers "which station constrains the line now". The brief asks
something harder: where is a constraint *forming*. This module answers it two
ways, deliberately ordered cheapest first.

  1. Buffer countdown   physics. A buffer filling at a steady rate has a
                        computable time-to-full, and the moment it fills the
                        station behind it blocks. Symmetrically, a draining
                        buffer gives a countdown to starvation ahead. No
                        training, no history, no model - it works on the first
                        shift at a plant that has never run this system.

  2. Overtake risk      statistics. A station drifting slower closes the gap on
                        the current constraint. Gap divided by drift rate is
                        the intuition, but shipped as a point countdown it
                        would repeat the error that made our remaining-life
                        estimates ~3x too long: extrapolating a noisy early
                        trend as though it were linear. So this returns a
                        PROBABILITY over a horizon, widened by the uncertainty
                        in the drift estimate itself.

Both are computed from data a plant already emits. Neither requires the
station being predicted about to be instrumented beyond boundary scans.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BufferCountdown:
    buffer_id: str
    level: float
    capacity: int
    slope_per_min: float          # + filling, - draining
    minutes_to_full: float        # inf if not filling
    minutes_to_empty: float       # inf if not draining
    blocks_station: str           # the station that blocks when this fills
    starves_station: str          # the station that starves when this empties
    confidence: float             # from fit quality and sample count


def buffer_countdowns(buffers: pd.DataFrame, at_s: int,
                      window_s: int = 900) -> list[BufferCountdown]:
    """Time until each buffer fills or empties, at current flow.

    Deliberately labelled a *projection under current flow conditions*, not a
    forecast: a variant change, a downstream recovery, a break or any
    intervention invalidates the slope it was computed from. It is a nowcast
    with a countdown attached, and that is still the earliest physically
    grounded warning available.
    """
    out = []
    w0 = max(0, at_s - window_s)
    for bid, g in buffers[(buffers.t_s > w0) & (buffers.t_s <= at_s)].groupby("buffer_id"):
        if len(g) < 4:
            continue
        g = g.sort_values("t_s")
        t = g.t_s.values.astype(float)
        lv = g.level.values.astype(float)
        cap = int(g.capacity.iloc[0])
        # least-squares slope in units per minute
        slope, intercept = np.polyfit(t / 60.0, lv, 1)
        pred = np.polyval([slope, intercept], t / 60.0)
        ss_res = float(np.sum((lv - pred) ** 2))
        ss_tot = float(np.sum((lv - lv.mean()) ** 2))
        fit = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        level = float(lv[-1])

        # A buffer already at capacity is not a prediction - it is a statement
        # of current state, and the station behind it is blocked NOW. Emitting
        # "0 minutes to full" as a countdown would flood the output with
        # already-happened events and crowd out every genuine warning.
        to_full = ((cap - level) / slope
                   if (slope > 1e-4 and level < cap - 1e-9) else np.inf)
        to_empty = (level / -slope
                    if (slope < -1e-4 and level > 1e-9) else np.inf)
        # a buffer between S(i) and S(i+1) is named B(i+1): filling blocks the
        # station behind it, emptying starves the station ahead of it
        try:
            idx = int(bid.lstrip("BA"))
        except ValueError:
            idx = 0
        out.append(BufferCountdown(
            buffer_id=bid, level=level, capacity=cap,
            slope_per_min=round(float(slope), 4),
            minutes_to_full=round(float(to_full), 1),
            minutes_to_empty=round(float(to_empty), 1),
            blocks_station=f"S{idx:02d}",
            starves_station=f"S{idx+1:02d}",
            confidence=round(float(np.clip(fit, 0, 1)) * min(1.0, len(g) / 12), 3)))
    return sorted(out, key=lambda c: min(c.minutes_to_full, c.minutes_to_empty))


@dataclass
class OvertakeRisk:
    station: str
    gap_s: float                  # effective-CT gap to the current constraint
    drift_s_per_h: float
    drift_se: float               # standard error of the drift estimate
    p_within: dict                # horizon minutes -> probability


def overtake_risk(detector, at_s: int, horizons=(15, 30, 60),
                  lookback: int = 3) -> list[OvertakeRisk]:
    """P(station closes the gap on the constraint within horizon H).

    Why a probability and not `gap / rate`: drift is noisy, intermittent and
    nonlinear - disturbed by variants, breaks, maintenance and micro-stops. We
    already learned what a linear extrapolation of an early trend costs on the
    quality side, where it made remaining-life estimates about three times too
    long. The same arithmetic applied to flow would be wrong the same way.

    So the drift rate is estimated over several windows, its standard error is
    carried, and the result is the probability that a normally-distributed
    drift closes the gap in time - which widens honestly when the trend is
    unstable instead of producing a confident wrong number.
    """
    ts = [at_s - k * detector.window_s for k in range(lookback, -1, -1)]
    ts = [t for t in ts if t >= detector.window_s]
    if len(ts) < 3:
        return []
    hist: dict[str, list] = {}
    for t in ts:
        for r in detector.read(t):
            hist.setdefault(r.station, []).append((t, r.proc_time, r.effective_ct))

    v = detector.verdict(at_s)
    if v is None:
        return []
    lead = v.ranking[0].effective_ct

    out = []
    for st, seq in hist.items():
        if len(seq) < 3 or st == v.constraint:
            continue
        t = np.array([x[0] for x in seq], dtype=float) / 3600.0
        p = np.array([x[1] for x in seq], dtype=float)
        n = len(t)
        slope, intercept = np.polyfit(t, p, 1)
        resid = p - np.polyval([slope, intercept], t)
        dof = max(n - 2, 1)
        sx = float(np.sum((t - t.mean()) ** 2))
        se = float(np.sqrt(np.sum(resid ** 2) / dof / sx)) if sx > 0 else np.inf
        gap = lead - seq[-1][2]
        if gap <= 0:
            continue
        probs = {}
        for h in horizons:
            need = gap / (h / 60.0)              # s/hour of drift required
            if not np.isfinite(se) or se <= 0:
                probs[h] = float(slope >= need)
            else:
                # P(drift >= required), normal around the fitted slope
                z = (slope - need) / se
                probs[h] = round(float(0.5 * (1 + __import__("math").erf(z / np.sqrt(2)))), 3)
        out.append(OvertakeRisk(station=st, gap_s=round(float(gap), 2),
                                drift_s_per_h=round(float(slope), 3),
                                drift_se=round(float(se), 3) if np.isfinite(se) else -1.0,
                                p_within=probs))
    return sorted(out, key=lambda o: -max(o.p_within.values()))
