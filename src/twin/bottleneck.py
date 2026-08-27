"""Bottleneck detection.

Three detectors, all causal (they see only data up to the moment of the
call) and all working from observed event logs only - dark stations are
simply absent, exactly as they would be on a real line.

  utilisation      rank by share of time working.  The conventional
                   dashboard answer, and the baseline to beat.
  least_idle       rank by least time blocked-or-starved. Good intuition,
                   noisy in practice, ties are common.
  active_period    rank by longest average uninterrupted active period.
                   Roser, Nakano & Tanaka (2001, 2002).

The distinction that matters: utilisation cannot separate a station that is
intrinsically slow from one that is fed so heavily it never gets a pause.
Both look busy. Only one sets the line rate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .events import (Run, active_periods, forced_idle_share, state_spans,
                     window_active_stats)

WINDOW_S = 1800         # trailing observation window
STEP_S = 60             # emit a verdict once a minute


class BottleneckDetector:
    """Precomputes per-station spans once, then answers queries per minute."""

    def __init__(self, run: Run, window_s: int = WINDOW_S):
        self.run = run
        self.window_s = window_s
        self.spans = state_spans(run.states, run.horizon_s)
        self.periods = {k: active_periods(v) for k, v in self.spans.items()}
        self.stations = [s for s in self.spans if s.startswith("S")]

    # ------------------------------------------------------------ scoring
    def _scores(self, method: str, w0: int, w1: int) -> dict[str, float]:
        out: dict[str, float] = {}
        for st in self.stations:
            if method == "active_period":
                avg, _ = window_active_stats(self.periods[st], w0, w1)
                out[st] = avg
            elif method == "utilisation":
                _, share = window_active_stats(self.periods[st], w0, w1)
                out[st] = share
            elif method == "least_idle":
                out[st] = -forced_idle_share(self.spans[st], w0, w1)
            else:
                raise ValueError(method)
        return out

    def rank(self, method: str, at_s: int) -> list[str]:
        w0, w1 = at_s - self.window_s, at_s
        sc = self._scores(method, max(0, w0), w1)
        return sorted(sc, key=sc.get, reverse=True)

    def timeline(self, method: str, step_s: int = STEP_S) -> pd.DataFrame:
        """Primary/secondary verdict once per step, over the whole shift."""
        rows = []
        for at in range(self.window_s, self.run.horizon_s, step_s):
            r = self.rank(method, at)
            if len(r) >= 2:
                rows.append(dict(minute=at // 60, primary=r[0], secondary=r[1]))
        return pd.DataFrame(rows)


def detect_all(run: Run, methods=("active_period", "utilisation", "least_idle")):
    """Run every detector over one shift. Returns {method: timeline}."""
    d = BottleneckDetector(run)
    return {m: d.timeline(m) for m in methods}


def shifting_summary(timeline: pd.DataFrame) -> dict:
    """How much the constraint moved, as this detector saw it."""
    if timeline.empty:
        return dict(switches=0, distinct=0, median_reign_min=np.nan)
    changed = timeline.primary != timeline.primary.shift()
    reigns = timeline.groupby(changed.cumsum()).size()
    return dict(switches=int(changed.sum() - 1),
                distinct=int(timeline.primary.nunique()),
                median_reign_min=float(reigns.median()))
