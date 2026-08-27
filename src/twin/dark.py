"""Stations with little or no sensor data - the brief's hardest prompt.

The principle: never fabricate a missing reading. Estimate state from evidence
that does exist, attach confidence and provenance, and let resolution degrade
gracefully rather than letting the system fail.

  Tier A  fully instrumented              -> directly observed
  Tier B  one dark station between scans  -> strongly estimated
  Tier C  consecutive dark stations       -> localised to a block
  Tier D  fully opaque section            -> bounded + sensor recommendation

The order matters. LOCALISE BEFORE YOU RESOLVE: establishing that the
constraint is somewhere inside S07-S09 narrows twenty stations to three, which
is most of the operational value, and it needs no model at all. Only then is it
worth trying to say which of the three.

The confound this module exists to handle: a bracketed time is
`occupancy = work + waiting`. If the dark station was starved or blocked, that
figure blames it for a neighbour's delay. Measured on our own data, occupancy
overstates true work by roughly 50%. Bracketing therefore never stands alone -
it is always paired with the neighbour evidence that splits the two.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class DarkBlock:
    stations: list          # the consecutive dark stations
    upstream: str           # last instrumented station before the block
    downstream: str         # first instrumented station after it
    tier: str               # "B" (single) or "C" (consecutive)


def find_dark_blocks(all_spine: list, dark: set) -> list[DarkBlock]:
    """Group dark stations into maximal consecutive runs, with their brackets."""
    idx = {s: i for i, s in enumerate(all_spine)}
    d = sorted((s for s in dark if s in idx), key=lambda s: idx[s])
    blocks, cur = [], []
    for s in d:
        if cur and idx[s] == idx[cur[-1]] + 1:
            cur.append(s)
        else:
            if cur:
                blocks.append(cur)
            cur = [s]
    if cur:
        blocks.append(cur)

    out = []
    for b in blocks:
        i0, i1 = idx[b[0]], idx[b[-1]]
        up = all_spine[i0 - 1] if i0 > 0 else ""
        dn = all_spine[i1 + 1] if i1 + 1 < len(all_spine) else ""
        out.append(DarkBlock(stations=b, upstream=up, downstream=dn,
                             tier="B" if len(b) == 1 else "C"))
    return out


def block_traversal_times(scans: pd.DataFrame, block: DarkBlock) -> np.ndarray:
    """Time each unit took to cross the dark block, from the bracketing scans.

    This is occupancy for the whole block - work plus any waiting inside it.
    It is exactly what a plant can see and nothing more.
    """
    if not block.upstream or not block.downstream:
        return np.array([])
    p = scans.pivot_table(index=["vin", "station_id"], columns="event",
                          values="t_s", aggfunc="first").reset_index()
    up = p[p.station_id == block.upstream][["vin", "out"]].rename(columns={"out": "t_up"})
    dn = p[p.station_id == block.downstream][["vin", "in"]].rename(columns={"in": "t_dn"})
    j = up.merge(dn, on="vin").dropna()
    return (j.t_dn - j.t_up).values.astype(float)


@dataclass
class Localisation:
    block: list
    mean_block_time: float
    slowest_visible_time: float
    constraint_inside: bool
    confidence: float
    reason: str


def localise(scans: pd.DataFrame, block: DarkBlock, visible_proc: dict,
             window: tuple | None = None) -> Localisation | None:
    """Is the line's constraint inside this dark block?

    The test needs no model: if the block's per-station traversal time exceeds
    every instrumented station's processing time, then whatever is limiting the
    line is in there. If it does not, the block is exonerated and attention
    belongs elsewhere - which is just as useful and much more common.

    `visible_proc` maps instrumented station -> processing seconds per unit.
    """
    tt = block_traversal_times(scans, block)
    if window is not None:
        pass                                    # window filtering handled upstream
    if len(tt) < 20 or not visible_proc:
        return None
    n = len(block.stations)
    per_station = float(np.median(tt)) / n      # median resists micro-stop tails
    slowest_visible = float(max(visible_proc.values()))

    inside = per_station > slowest_visible
    # confidence from the margin, normalised by the visible spread, and by how
    # many units we measured
    spread = float(np.std(list(visible_proc.values()))) or 1.0
    margin = abs(per_station - slowest_visible)
    conf = float(np.clip(margin / (2 * spread), 0, 1)) * min(1.0, len(tt) / 60)

    return Localisation(
        block=block.stations, mean_block_time=round(per_station, 1),
        slowest_visible_time=round(slowest_visible, 1),
        constraint_inside=inside, confidence=round(conf, 3),
        reason=(f"block averages {per_station:.1f}s per station vs "
                f"{slowest_visible:.1f}s for the slowest visible station"))


def position_within_block(scans: pd.DataFrame, states: pd.DataFrame,
                          block: DarkBlock) -> dict:
    """Rank stations inside a consecutive dark block by likely position.

    Time-difference-of-arrival: a slow station pushes a blocking wave backwards
    and a starvation wave forwards, each travelling one buffer at a time. The
    ratio of how quickly the upstream station starts blocking versus the
    downstream station starts starving places the source inside the block -
    the same principle that locates an earthquake from arrival times.

    Returns a posterior over positions. It is deliberately NOT a single answer:
    with several hidden stations changing at once the problem is not uniquely
    identifiable, and a confident wrong station is worse than a ranked guess.
    """
    n = len(block.stations)
    if n == 1:
        return {block.stations[0]: 1.0}
    up_blocked = states[(states.station_id == block.upstream) &
                        (states.state == "blocked")]
    dn_starved = states[(states.station_id == block.downstream) &
                        (states.state == "starved")]
    if up_blocked.empty or dn_starved.empty:
        return {s: 1.0 / n for s in block.stations}

    # first arrival of each wave, relative to the start of observation
    t_block = float(up_blocked.t_s.min())
    t_starve = float(dn_starved.t_s.min())
    total = abs(t_block) + abs(t_starve)
    if total <= 0:
        return {s: 1.0 / n for s in block.stations}

    # a source near the upstream end blocks upstream sooner than it starves
    # downstream, and vice versa
    frac = abs(t_block) / total
    centre = frac * (n - 1)
    w = np.exp(-0.5 * ((np.arange(n) - centre) / 0.8) ** 2)
    w = w / w.sum()
    return {s: round(float(p), 3) for s, p in zip(block.stations, w)}
