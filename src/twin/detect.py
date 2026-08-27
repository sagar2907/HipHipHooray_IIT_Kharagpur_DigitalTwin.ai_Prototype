"""Bottleneck detection, second generation.

Built from the method worked out in review rather than from a single paper.
The chain of reasoning, and why each piece is here:

  1. Rank stations by PROCESSING time, not by how busy they look.
     Utilisation cannot separate a station that is slow from one that is
     merely never allowed to rest - both read ~95% busy. Processing time
     separates them immediately.

  2. Processing time means WORK, not dwell. The time a car spends at a
     station includes any wait caused by a full buffer downstream. Charging
     that wait to the station blames a victim for its neighbour's fault.
     Where station states exist we subtract it directly; where they do not
     we infer it from the neighbour signature (see infer_states_from_scans).

  3. Divide by availability. A station at 55 s that is broken 10% of the
     time needs 61 s per car in practice, which is worse than a reliable
     58 s station. Raw processing time ranks those backwards.

  4. Compare every station to ITS OWN baseline, never to takt. Takt is a
     target for the line and says nothing about whether one station is
     behaving normally. A station drifting 54 -> 57 s is abnormal even
     though it is still comfortably under a 60 s takt.

  5. Never judge from one car. Manual station times scatter widely - a
     single 68 s car on a 54 s station is normal noise, not a fault.
     Averaging shrinks that noise by sqrt(n), and CUSUM accumulates
     evidence so small drifts are caught without a fixed window.

  6. Report where a constraint is FORMING - but from BUFFER SLOPE, not by
     extrapolating a station's drift rate. Drift extrapolation was measured
     at 5.9% correct against 70-100% stated confidence and abandoned; the
     buffer countdown that replaced it ran 59.6% of 178 warnings, median
     error +0.57 min. Both numbers are in results/forming_*.csv.

  7. Attach confidence and provenance. A directly measured value and an
     inferred one must never look identical to the operator. `confidence`
     is only a probability once fit_calibration() has been called -
     Verdict.confidence_calibrated says which you are looking at.

Ranking is on effective_ct ALONE, deliberately. The design note that it
should additionally be down-weighted by starved share was tested on 319
blocks of v5 truth and made every variant equal or worse (top-1 32.3% ->
30.1-32.0%, regret 1.303 -> 1.304-1.342). The reason is mechanical: work
time already excludes blocked and starved seconds, so down-weighting by
starved share charges the station for the same idleness twice. The code
was right and the design note was wrong.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .events import Run, state_spans
from .forming import buffer_countdowns

WORK_STATES = ("working",)
DOWN_STATES = ("down",)
WAIT_STATES = ("blocked", "starved")
PAUSE_STATES = ("break",)

WINDOW_S = 1800          # trailing observation window
MIN_UNITS = 8            # below this the average is too noisy to rank on
# Beyond about an hour a buffer countdown is extrapolation, not a warning:
# it is past the point where the current slope is still the operative fact,
# and a supervisor cannot act on it anyway.
FORMING_HORIZON_MIN = 60


# --------------------------------------------------------------------------
# Station state from scans alone (the dark-station case)
# --------------------------------------------------------------------------
def infer_states_from_scans(scans: pd.DataFrame, horizon_s: int,
                            baseline_ct: dict | None = None) -> pd.DataFrame:
    """Reconstruct blocked / starved / working from boundary scans only.

    The neighbour signature: if a station is the constraint, the station
    BEHIND it shows its dwell stretching past its own baseline (it has
    finished but cannot hand over - blocked), and the station AHEAD shows
    gaps between arrivals (nothing is reaching it - starved). Neither
    requires a sensor inside any station.

    Returns one row per (station, unit) with dwell, an estimate of the work
    portion, and the inferred state.
    """
    p = scans.pivot_table(index=["vin", "station_id"], columns="event",
                          values="t_s", aggfunc="first").dropna(
                              subset=["in", "out"]).reset_index()
    p["dwell"] = p["out"] - p["in"]
    p = p.sort_values(["station_id", "in"])

    # each station's own baseline = the fast end of its dwell distribution.
    # A car that passed through with no waiting is the cleanest observation
    # of pure work time available, so the low quantile approximates it.
    if baseline_ct is None:
        baseline_ct = p.groupby("station_id").dwell.quantile(0.15).to_dict()
    p["baseline"] = p.station_id.map(baseline_ct)
    p["excess"] = (p.dwell - p.baseline).clip(lower=0)

    # gap since the previous car arrived at this station -> starvation
    p["prev_out"] = p.groupby("station_id")["out"].shift(1)
    p["arrival_gap"] = (p["in"] - p["prev_out"]).clip(lower=0).fillna(0)

    p["work_est"] = p.dwell - p.excess
    p["state_hint"] = np.where(
        p.excess > 0.25 * p.baseline, "blocked",
        np.where(p.arrival_gap > 0.25 * p.baseline, "starved", "working"))
    return p[["vin", "station_id", "in", "out", "dwell", "baseline",
              "work_est", "arrival_gap", "state_hint"]]


# --------------------------------------------------------------------------
@dataclass
class StationReading:
    station: str
    units: int
    proc_time: float          # mean WORK seconds per unit
    availability: float
    effective_ct: float       # proc_time / availability - the ranking key
    blocked_share: float
    starved_share: float
    drift_cusum: float        # accumulated evidence of a shift vs baseline
    drift_rate: float         # seconds of processing time gained per hour
    provenance: str           # "measured" | "inferred"
    confidence: float


@dataclass
class Verdict:
    at_s: int
    ranking: list             # StationReading, worst (slowest) first
    constraint: str
    margin: float             # seconds between first and second
    confidence: float
    forming: list = field(default_factory=list)   # (station, minutes_to_form)
    cross_check_agrees: bool = True
    confidence_raw: float = 0.0        # the ordering score before calibration
    confidence_calibrated: bool = False  # False => `confidence` is NOT a probability


class Detector:
    """Cascade detector: cheap ranking always, expensive work only on demand."""

    def __init__(self, run: Run, window_s: int = WINDOW_S,
                 use_states: bool = True):
        self.run = run
        self.window_s = window_s
        self.spans = state_spans(run.states, run.horizon_s) if use_states else {}
        self.use_states = use_states and bool(self.spans)
        self.stations = sorted(
            {s for s in (self.spans or {}) if s.startswith("S")}
            or {s for s in run.scans.station_id.unique() if s.startswith("S")})
        self.scan_view = infer_states_from_scans(run.scans, run.horizon_s)
        self.exits = (run.scans[run.scans.event == "out"]
                      .groupby("station_id").t_s.apply(np.sort).to_dict())
        self._baseline: dict[str, tuple] = {}
        # CUSUM accumulator, memoised per (station, window index). See _cusum:
        # it must stay a pure function of at_s because verdict() calls read()
        # out of order, and an order-dependent accumulator would corrupt.
        self._cusum_cache: dict[tuple, float] = {}
        self._calibrator = None        # set by fit_calibration()

    # ------------------------------------------------------------- helpers
    def _measure(self, st: str, w0: int, w1: int):
        """Window measurement from whichever source this run supports."""
        if self.use_states:
            return self._from_states(st, w0, w1)
        return self._from_scans(st, w0, w1)

    def _baseline_for(self, st: str) -> tuple:
        """The station's own early behaviour, learned once and cached."""
        if st not in self._baseline:
            b0, b1 = 0, min(self.run.horizon_s, 2 * self.window_s)
            bw, bd, _, _, bs = self._measure(st, b0, b1)
            bu = max(1, self._units(st, b0, b1))
            self._baseline[st] = (bw / bu, max(0.05, (bs - bd) / bs))
        return self._baseline[st]

    def _cusum(self, st: str, at_s: int) -> float:
        """Tabular CUSUM over successive windows: S_j = max(0, S_j-1 + z - k).

        Previously this was recomputed from the current window alone, which
        made it a one-window z-score wearing a CUSUM's name - it had no
        memory, so a slow drift never accumulated and the statistic could not
        be read backwards to date a fault onset. It now carries state across
        windows, which is the whole point of the method.

        Memoised on the window index so it is a deterministic function of
        at_s regardless of the order read() is called in.
        """
        idx = int(at_s // self.window_s)
        if idx < 1:
            return 0.0
        if (st, idx) in self._cusum_cache:
            return self._cusum_cache[(st, idx)]
        base_proc, _ = self._baseline_for(st)
        sd = max(0.02 * base_proc, 0.5)
        s = 0.0
        for j in range(1, idx + 1):
            if (st, j) in self._cusum_cache:
                s = self._cusum_cache[(st, j)]
                continue
            w0, w1 = (j - 1) * self.window_s, j * self.window_s
            u = self._units(st, w0, w1)
            if u >= 1:
                work, _, _, _, _ = self._measure(st, w0, w1)
                z = ((work / u) - base_proc) / sd
                s = max(0.0, s + z - 0.5)          # k = 0.5 sd, standard slack
            self._cusum_cache[(st, j)] = s
        return s

    # ---------------------------------------------------------------- window
    def _from_states(self, st: str, w0: int, w1: int):
        work = down = blocked = starved = pause = 0
        for a, b, v in self.spans.get(st, []):
            if b <= w0 or a >= w1:
                continue
            d = min(b, w1) - max(a, w0)
            if v in WORK_STATES:
                work += d
            elif v in DOWN_STATES:
                down += d
            elif v in WAIT_STATES:
                blocked += d if v == "blocked" else 0
                starved += d if v == "starved" else 0
            elif v in PAUSE_STATES:
                pause += d
        span = max(1, (w1 - w0) - pause)          # breaks are not the station's fault
        return work, down, blocked, starved, span

    def _from_scans(self, st: str, w0: int, w1: int):
        g = self.scan_view[(self.scan_view.station_id == st) &
                           (self.scan_view["out"] > w0) &
                           (self.scan_view["in"] < w1)]
        if g.empty:
            return 0.0, 0.0, 0.0, 0.0, max(1, w1 - w0)
        work = float(g.work_est.sum())
        blocked = float((g.dwell - g.work_est).sum())
        starved = float(g.arrival_gap.sum())
        return work, 0.0, blocked, starved, max(1, w1 - w0)

    def _units(self, st: str, w0: int, w1: int) -> int:
        a = self.exits.get(st)
        if a is None:
            return 0
        return int(np.searchsorted(a, w1) - np.searchsorted(a, w0))

    def read(self, at_s: int) -> list[StationReading]:
        w0, w1 = max(0, at_s - self.window_s), at_s
        out = []
        for st in self.stations:
            if self.use_states:
                work, down, blk, srv, span = self._from_states(st, w0, w1)
                prov = "measured"
            else:
                work, down, blk, srv, span = self._from_scans(st, w0, w1)
                prov = "inferred"
            units = self._units(st, w0, w1)
            if units < 1:
                continue
            proc = work / units
            avail = max(0.05, (span - down) / span)
            eff = proc / avail

            # baseline: the station's own early behaviour, learned once
            base_proc, base_av = self._baseline_for(st)
            cusum = self._cusum(st, at_s)

            out.append(StationReading(
                station=st, units=units, proc_time=proc, availability=avail,
                effective_ct=eff, blocked_share=blk / span,
                starved_share=srv / span, drift_cusum=cusum, drift_rate=0.0,
                provenance=prov,
                confidence=min(1.0, units / MIN_UNITS)))
        return out

    # ------------------------------------------------------------- verdict
    def verdict(self, at_s: int) -> Verdict | None:
        rd = self.read(at_s)
        rd = [r for r in rd if r.units >= 2]
        if len(rd) < 2:
            return None
        rd.sort(key=lambda r: r.effective_ct, reverse=True)
        top, second = rd[0], rd[1]
        margin = top.effective_ct - second.effective_ct

        # cross-check: the constraint should be the station least often
        # forced idle by a neighbour. Agreement raises confidence; a clash
        # is reported rather than hidden.
        idle = {r.station: r.blocked_share + r.starved_share for r in rd}
        agrees = min(idle, key=idle.get) == top.station

        # drift rate is still reported per station as a DIAGNOSTIC, but it is
        # no longer extrapolated into a time-to-overtake - see below.
        prev = self.read(max(0, at_s - self.window_s))
        prevmap = {r.station: r.proc_time for r in prev}
        for r in rd[1:]:
            p0 = prevmap.get(r.station)
            if p0 is not None and r.proc_time > p0:
                r.drift_rate = (r.proc_time - p0) / (self.window_s / 3600.0)

        forming = self._forming(at_s)

        n = max(1e-6, np.mean([r.effective_ct for r in rd]))
        raw = float(np.clip(margin / (0.08 * n), 0, 1)) * (1.0 if agrees else 0.7)
        raw *= min(1.0, top.units / MIN_UNITS)
        # Part 4.1 says confidence must be calibrated, not asserted. `raw` is
        # an ordering score, not a probability: fit_calibration() maps it onto
        # the observed hit rate. Until that is fitted the raw score is passed
        # through unchanged, so nothing silently claims to be a probability.
        conf = self._calibrator(raw) if self._calibrator else raw

        return Verdict(at_s=at_s, ranking=rd, constraint=top.station,
                       margin=margin, confidence=round(float(conf), 3),
                       confidence_raw=round(raw, 3),
                       confidence_calibrated=self._calibrator is not None,
                       forming=forming[:3], cross_check_agrees=agrees)

    # ------------------------------------------------------------- forming
    def _forming(self, at_s: int) -> list:
        """Where a constraint is FORMING, from buffer countdowns.

        Replaces the previous mechanism, which extrapolated the gap to the
        current constraint by a station's drift rate. That was measured at
        5.9% correct against 70-100% stated confidence and publicly declared
        failed, but it was still being computed here - so any consumer of
        Verdict, the live loop included, would have shipped it.

        Buffer slope is the mechanism that actually held up: 59.6% of 178
        warnings were followed by a real block, median error +0.57 min. It is
        a projection under current flow, not a forecast, and is labelled that
        way at source in forming.buffer_countdowns.
        """
        if self.run.buffers is None or self.run.buffers.empty:
            return []
        out = []
        for c in buffer_countdowns(self.run.buffers, at_s):
            # B(i+1) sits between S(i) and S(i+1). Filling means the station
            # AHEAD is not draining it fast enough, so that station is the
            # emerging constraint; emptying means the station BEHIND is not
            # feeding it. The victim and the cause are different stations.
            if np.isfinite(c.minutes_to_full):
                out.append((c.starves_station, int(round(c.minutes_to_full))))
            elif np.isfinite(c.minutes_to_empty):
                out.append((c.blocks_station, int(round(c.minutes_to_empty))))
        # A countdown longer than the horizon is arithmetic, not a warning. A
        # buffer creeping up at 0.01 units/min yields "full in 576 minutes",
        # which is past the end of the shift and past the point where the
        # slope it was extrapolated from means anything. Emitting it would
        # bury the real warnings - the alarm-flood failure mode the brief
        # names, caused by us rather than by the plant.
        out = [(s, m) for s, m in out if 0 < m <= FORMING_HORIZON_MIN]
        out.sort(key=lambda x: x[1])
        return out

    def fit_calibration(self, pairs: list) -> None:
        """Fit score -> observed hit rate from (raw_score, was_correct) pairs.

        Isotonic-style binning: monotone, needs no distributional assumption,
        and degrades gracefully on the sample sizes we actually have.
        """
        if not pairs:
            return
        df = pd.DataFrame(pairs, columns=["score", "hit"]).sort_values("score")
        n_bins = max(2, min(10, len(df) // 40))
        df["b"] = pd.qcut(df.score.rank(method="first"), n_bins, labels=False)
        g = df.groupby("b").agg(lo=("score", "min"), hi=("score", "max"),
                                p=("hit", "mean")).reset_index()
        # enforce monotonicity (pool-adjacent-violators, single pass)
        p = g.p.values.copy()
        for i in range(1, len(p)):
            if p[i] < p[i - 1]:
                p[i] = p[i - 1] = (p[i] + p[i - 1]) / 2
        edges, probs = g.hi.values, p

        def _cal(s: float) -> float:
            return float(probs[int(np.searchsorted(edges, s, side="left")
                                   .clip(0, len(probs) - 1))])
        self._calibrator = _cal

    def timeline(self, step_s: int = 300):
        rows = []
        for at in range(self.window_s, self.run.horizon_s, step_s):
            v = self.verdict(at)
            if v is None:
                continue
            rows.append(dict(minute=at // 60, constraint=v.constraint,
                             second=v.ranking[1].station,
                             margin=round(v.margin, 2), confidence=v.confidence,
                             agrees=v.cross_check_agrees,
                             forming=";".join(f"{s}@{m}min" for s, m in v.forming)))
        return pd.DataFrame(rows)
