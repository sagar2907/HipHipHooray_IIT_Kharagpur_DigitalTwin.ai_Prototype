"""Line topologies for the layout-transfer experiment.

Four layouts differing in length, merge count and the presence of a
parallel station pair. The literature review found no published work
demonstrating bottleneck-predictor transfer across line layouts; these
four are the substrate for that experiment: train on some, test on the
rest, report the degradation honestly.

A `parallel` station is one logical operation executed by two servers
sharing a queue - the standard plant response to an operation that cannot
be sped up. It deliberately breaks the pure-series assumption that most
bottleneck detection implicitly relies on.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Layout:
    name: str
    n_spine: int
    merges: dict = field(default_factory=dict)     # spine idx (0-based) -> feeder length
    parallel: set = field(default_factory=set)     # spine idx with 2 servers
    # A 12-second spread (was 5) so one station is CLEARLY the slowest.
    # With 52-58 s the line had no dominant constraint: nine stations showed
    # positive marginal value and the "true bottleneck" label was decided by
    # differences of half a car, which is noise. A real line is balanced but
    # not perfectly - there is normally one station everyone knows is tight.
    ct_range: tuple = (50.0, 62.0)
    feeder_ct_range: tuple = (48.0, 58.0)
    # --- segment metadata (opt-in; None on L1-L4, so build_plant_config's
    # original per-station draw falls through unchanged for them) -----------
    # segment[i]  : 'body' | 'paint' | 'final' for spine station i
    # vintage[i]  : 'legacy' | 'modern' - a FIXED line property, not drawn
    #               per-seed, matching how the brief poses it as a transfer
    #               axis alongside layout, not a per-shift random variable
    # seg_ct      : segment -> (ct_range, sigma_range) override
    # seg_dark_p  : segment -> P(station has no controller/sensors at all)
    segment: list = None
    vintage: list = None
    seg_ct: dict = None
    seg_dark_p: dict = None


LAYOUTS = {
    "L1": Layout("L1", 20, merges={11: 3}),
    "L2": Layout("L2", 30, merges={9: 3, 21: 4}),
    "L3": Layout("L3", 20, merges={11: 3}, parallel={6}),
    "L4": Layout("L4", 15, merges={7: 2}),
}


def _l5_segment():
    # Real body-in-white -> paint -> final-assembly order. 15 + 10 + 15 = 40,
    # matching Workstream D's stated station-count target with the three
    # behaviourally-distinct segments Priyansh's Part A and proposal #8 argue
    # for, instead of one more uniform stretch of L2.
    return ["body"] * 15 + ["paint"] * 10 + ["final"] * 15


def _l5_vintage():
    # Vintage is fixed per station, not per-seed: paint ovens are the
    # hardest and most disruptive equipment to replace on a real line, so
    # they skew legacy. Body (robots) and final (manual/fixture-heavy,
    # cheap to retrofit) skew modern, with a few legacy holdouts each.
    body = ["modern"] * 12 + ["legacy"] * 3
    paint = ["legacy"] * 8 + ["modern"] * 2
    final = ["modern"] * 11 + ["legacy"] * 4
    return body + paint + final


LAYOUTS["L5"] = Layout(
    "L5", 40, merges={24: 3},
    segment=_l5_segment(),
    vintage=_l5_vintage(),
    seg_ct={
        # body: robotic, tight variance - threshold detection is enough
        "body": ((48.0, 58.0), (0.05, 0.09)),
        # paint: batch/oven-adjacent, wider spread than a pure flow station
        "paint": ((55.0, 68.0), (0.10, 0.16)),
        # final: manual, CV 0.25-0.6 per Part A 1.1 - needs drift detection,
        # not a threshold
        "final": ((50.0, 65.0), (0.25, 0.55)),
    },
    # Tuned to the PS reference parameter: "a MAJORITY of stations
    # well-instrumented, a MEANINGFUL MINORITY reliant on manual checks".
    # The first cut (0.10/0.90/0.65) gave 48.5% dark line-wide, which is not a
    # minority and would have read as contradicting the brief. These give
    # ~30% dark while KEEPING the inversion inside final assembly, which is
    # the actual argument in Part A 1.1 - coverage holds across the line and
    # fails exactly where the manual work is.
    seg_dark_p={"body": 0.05, "paint": 0.60, "final": 0.45},
)
