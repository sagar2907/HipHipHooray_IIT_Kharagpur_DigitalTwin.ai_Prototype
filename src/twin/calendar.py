"""Shift calendar: breaks, lunch, changeover and PM windows.

The calendar is OBSERVED data - a plant knows its own schedule - so it is
written alongside the event logs, and models are welcome to use it. What
models may not use is anything in hidden/.

Why this module exists at all: breaks are the only mechanism that drains
accumulated WIP (proven in session - a backlog never clears while input
continues), and the post-break warm-up is a real, clock-correlated effect
that a naive detector will mistake for degradation. Both belong in any
dataset claiming production realism.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SHIFT_S = 8 * 3600


@dataclass
class Calendar:
    """One shift's schedule, repeated for multi-shift runs."""
    breaks: list[tuple[int, int]] = field(default_factory=lambda: [
        (2 * 3600, 10 * 60),           # tea, 10 min
        (4 * 3600, 30 * 60),           # lunch, 30 min
        (6 * 3600 + 30 * 60, 10 * 60), # tea, 10 min
    ])
    warmup_s: int = 10 * 60            # elevated cycle times after each break
    warmup_factor: float = 1.10

    def on_break(self, t: int) -> bool:
        ts = t % SHIFT_S
        return any(s <= ts < s + d for s, d in self.breaks)

    def warmup_mult(self, t: int) -> float:
        ts = t % SHIFT_S
        for s, d in self.breaks:
            dt = ts - (s + d)
            if 0 <= dt < self.warmup_s:
                return self.warmup_factor * (1 - dt / self.warmup_s) + 1.0 * (dt / self.warmup_s)
        return 1.0

    def rows(self, horizon_s: int):
        """The observed calendar file: one row per scheduled pause."""
        out = []
        for shift0 in range(0, horizon_s, SHIFT_S):
            for s, d in self.breaks:
                if shift0 + s < horizon_s:
                    out.append(dict(kind="break", start_s=shift0 + s, dur_s=d))
        return out
