"""Replay driver: turns a finished shift into a live event stream.

This is the piece that makes the difference between a digital SHADOW and a
digital TWIN. Everything before it was batch - a script reads a completed
dataset, computes a score, prints it. A twin ingests, decides, and re-reads
on a clock, having seen only the past.

The whole design rests on one rule:

    THE DETECTOR MUST NEVER SEE t > now.

We enforce that PHYSICALLY, not by convention. `view_at(t)` hands back a Run
whose frames have been truncated, so a detector holding that view cannot read
the future even if it tries - there is nothing there to read. Auditing a
promise not to peek is much harder than removing the ability to.

That also fixes a real leak for free. `Detector.__init__` calls
`infer_states_from_scans`, which learns each station's baseline as a quantile
over *the whole run*. Constructing the detector against a truncated view means
the baseline is learned only from data that has actually happened - which is
what a plant would see on day one, and is strictly harder than the batch case.

Cost of rebuilding per tick was measured before this was written: ~20 ms to
construct plus ~6 ms per verdict, against a 60x replay budget of 5 s per tick.
Roughly two orders of magnitude of headroom, so the honest implementation is
also the affordable one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd

from .events import Run, load_run


@dataclass
class Recorder:
    """Serves a finished run as if it were unfolding now."""

    run: Run
    run_dir: str = ""
    manual: pd.DataFrame | None = None     # manual_check.csv, when present
    tools: pd.DataFrame | None = None      # tool_readings.csv, when present

    # ------------------------------------------------------------------ load
    @classmethod
    def from_dir(cls, run_dir: str, run_id: int = 0,
                 horizon_s: int = 8 * 3600) -> "Recorder":
        run = load_run(run_dir, run_id, horizon_s)
        manual = None
        mp = os.path.join(run_dir, "manual_check.csv")
        if os.path.exists(mp):
            manual = pd.read_csv(mp)
        tools = None
        tp = os.path.join(run_dir, "tool_readings.csv")
        if os.path.exists(tp):
            tools = pd.read_csv(tp)
        return cls(run=run, run_dir=run_dir, manual=manual, tools=tools)

    # ------------------------------------------------------------------ view
    def view_at(self, t_s: float) -> Run:
        """The run as known at time t_s. Nothing later exists in the result."""
        return Run(
            run_id=self.run.run_id,
            scans=self.run.scans[self.run.scans.t_s <= t_s].copy(),
            states=self.run.states[self.run.states.t_s <= t_s].copy(),
            buffers=self.run.buffers[self.run.buffers.t_s <= t_s].copy(),
            horizon_s=self.run.horizon_s,
        )

    def manual_checks_at(self, t_s: float, window_s: int = 1800) -> pd.DataFrame:
        """Manual checklist entries RECORDED by t_s.

        Filtered on `recorded_at_s`, never on when the work happened: a
        checklist entry does not exist for the twin until a human types it in,
        and `entry_latency_s` is exactly that delay. Filtering on the work time
        would quietly hand the twin information the plant did not have yet.
        """
        if self.manual is None or self.manual.empty:
            return pd.DataFrame()
        m = self.manual
        return m[(m.recorded_at_s <= t_s) & (m.recorded_at_s > t_s - window_s)].copy()

    # --------------------------------------------------------------- helpers
    @property
    def horizon_s(self) -> int:
        return self.run.horizon_s

    @property
    def spine(self) -> list[str]:
        """EVERY station on the line, dark ones included.

        A dark station emits no scans and no states, so it is invisible in the
        logs - which is exactly why `Run.observed_stations` under-counts. We
        recover the full spine from the numbering: stations run S01..S{max}
        contiguously, so any index in that range with no traffic is dark rather
        than absent. Showing those gaps IS the sensor-coverage story; dropping
        them would silently hide the problem we claim to solve.
        """
        seen = {s for s in self.run.scans.station_id.unique()
                if isinstance(s, str) and s.startswith("S")}
        if not seen:
            return []
        top = max(int(s[1:]) for s in seen)
        return [f"S{i:02d}" for i in range(1, top + 1)]

    @property
    def dark_stations(self) -> list[str]:
        """Stations on the spine that emit nothing at all."""
        seen = {s for s in self.run.scans.station_id.unique()
                if isinstance(s, str) and s.startswith("S")}
        return [s for s in self.spine if s not in seen]

    @property
    def exit_station(self) -> str | None:
        """The last instrumented station - where finished vehicles are counted."""
        instrumented = [s for s in self.spine if s not in set(self.dark_stations)]
        return instrumented[-1] if instrumented else None

    def units_completed_by(self, t_s: float) -> int:
        """Vehicles off the end of the line by t_s.

        Counted at the EXIT station specifically. Counting at 'whichever
        station we have seen most recently' makes the figure wander early in
        the shift, before the first unit has reached the end.
        """
        ex = self.exit_station
        if ex is None:
            return 0
        sc = self.run.scans
        return int(((sc.station_id == ex) & (sc.event == "out")
                    & (sc.t_s <= t_s)).sum())
