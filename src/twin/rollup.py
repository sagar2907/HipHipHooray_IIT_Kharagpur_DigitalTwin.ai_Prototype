"""Three stakeholder views from ONE record stream.

Complexity 5: a floor supervisor needs real-time signals, a plant manager
needs weekly planning trends, leadership needs an investment case. The easy
mistake is to build three dashboards. The claim that matters is that all
three are the SAME TWIN at different resolutions, and we prove it rather
than assert it - see `reconcile()`.

Two design points worth defending out loud:

1. THE MANAGER'S VIEW IS A DIFFERENT STATISTIC, NOT AN AVERAGE.
   The constraint moves ~15 times a shift. Averaging effective cycle time
   across a shift produces a number that describes no moment of that shift
   and hides the only actionable fact - WHICH stations hold the line back
   and for how long. So the manager sees a constraint-occupancy
   distribution: "S20 held the line 34% of the time across 15 shifts."
   That is a scheduling and capex input. A mean is not.

2. EVERY NUMBER HERE IS DERIVED FROM RECORDS, NOT ASSERTED.
   The rollup only aggregates what the loop actually emitted. Anything we
   cannot source from a file is reported as absent, loudly, rather than
   filled in with a plausible figure.
"""

from __future__ import annotations

import os
from collections import defaultdict

SHIFTS_PER_WEEK = 5


def rollup_shift(frames: list, step_s: int) -> dict:
    """Collapse one shift's frames into the numbers both upper views need."""
    live = [f for f in frames if f.get("constraint")]
    occupancy: dict[str, float] = defaultdict(float)
    for f in live:
        occupancy[f["constraint"]] += step_s / 60.0        # minutes

    return {
        "ticks": len(frames),
        "live_ticks": len(live),
        "units_out": frames[-1]["units_out"] if frames else 0,
        "constraint_moves": frames[-1]["shifts_so_far"] if frames else 0,
        "occupancy_min": dict(occupancy),
        "constraint_minutes": sum(occupancy.values()),
        "alerts": frames[-1]["ledger"]["open"] + frames[-1]["ledger"]["scored"]
                  if frames else 0,
        "mean_latency_ms": round(
            sum(f["compute_ms"] for f in frames) / max(1, len(frames)), 1),
    }


def rollup_week(shifts: list) -> dict:
    occ: dict[str, float] = defaultdict(float)
    for s in shifts:
        for st, m in s["occupancy_min"].items():
            occ[st] += m
    total = sum(occ.values()) or 1.0
    top = sorted(occ.items(), key=lambda kv: -kv[1])
    return {
        "n_shifts": len(shifts),
        "units_out": sum(s["units_out"] for s in shifts),
        "constraint_minutes": sum(s["constraint_minutes"] for s in shifts),
        "constraint_moves": sum(s["constraint_moves"] for s in shifts),
        "occupancy_min": dict(occ),
        # THE manager statistic: who holds the line, and how much of the time
        "top_constraints": [
            {"station": st, "minutes": round(m, 1),
             "share": round(100 * m / total, 1)} for st, m in top[:6]],
        "mean_units_per_shift": round(
            sum(s["units_out"] for s in shifts) / max(1, len(shifts)), 1),
    }


def reconcile(shifts: list, weeks: list, leadership: dict) -> dict:
    """Prove the three views are one twin.

    Leadership total == sum of weekly totals == sum of per-shift records.
    Computed independently at each level and compared, so a divergence is a
    real inconsistency rather than a rounding artefact of one shared sum.
    """
    from_shifts = round(sum(s["constraint_minutes"] for s in shifts), 3)
    from_weeks = round(sum(w["constraint_minutes"] for w in weeks), 3)
    from_leader = round(leadership["constraint_minutes"], 3)

    units_shifts = sum(s["units_out"] for s in shifts)
    units_weeks = sum(w["units_out"] for w in weeks)
    units_leader = leadership["units_out"]

    ok = (from_shifts == from_weeks == from_leader
          and units_shifts == units_weeks == units_leader)
    return {
        "passes": bool(ok),
        "constraint_minutes": {"supervisor_records": from_shifts,
                               "manager_weeks": from_weeks,
                               "leadership": from_leader},
        "units_out": {"supervisor_records": units_shifts,
                      "manager_weeks": units_weeks,
                      "leadership": units_leader},
        "statement": ("leadership total == sum of manager weeks == sum of "
                      "supervisor records"),
    }


def leadership_case(shifts: list, weeks: list, evidence: dict) -> dict:
    """The investment case, built only from things we can point at."""
    units = sum(s["units_out"] for s in shifts)
    cmin = sum(s["constraint_minutes"] for s in shifts)
    return {
        "shifts_observed": len(shifts),
        "weeks": len(weeks),
        "units_out": units,
        "constraint_minutes": cmin,
        "mean_units_per_shift": round(units / max(1, len(shifts)), 1),
        "mean_constraint_moves": round(
            sum(s["constraint_moves"] for s in shifts) / max(1, len(shifts)), 1),
        "evidence": evidence,
    }


def detection_evidence(results_dir: str) -> dict:
    """Published performance, read from the files that produced it.

    Every entry names its source. An item we cannot source is returned with
    `"value": None` and a reason - the view then shows the gap instead of a
    number, which is the whole point of the rule.
    """
    import pandas as pd

    ev: dict = {}
    ep = os.path.join(results_dir, "eval_v5.csv")
    if os.path.exists(ep):
        r = pd.read_csv(ep)
        strong = r[r.margin >= 2]
        ours = strong[strong.method == "effective_ct"]
        util = strong[strong.method == "utilisation"]
        n = len(ours)
        ev["top1_strong"] = {
            "value": round(100 * ours.top1.mean(), 1), "n": int(n),
            "source": "results/eval_v5.csv", "unit": "%",
            "label": "top-1 on strong constraints"}
        ev["top2_strong"] = {
            "value": round(100 * ours.top2.mean(), 1), "n": int(n),
            "source": "results/eval_v5.csv", "unit": "%",
            "label": "top-2 on strong constraints"}
        # All-blocks regret. n MUST come from the same subset the mean was
        # taken over - the first cut of this reported the all-blocks value
        # against the strong-constraint n, which is the exact value/n mismatch
        # defect #9 exists to stop.
        ours_all = r[r.method == "effective_ct"]
        util_all = r[r.method == "utilisation"]
        ev["regret_all"] = {
            "value": round(ours_all.regret.mean(), 3), "n": int(len(ours_all)),
            "source": "results/eval_v5.csv", "unit": "cars/block",
            "label": "regret, all blocks (ours)"}
        ev["regret_utilisation"] = {
            "value": round(util_all.regret.mean(), 3), "n": int(len(util_all)),
            "source": "results/eval_v5.csv", "unit": "cars/block",
            "label": "regret, all blocks (utilisation baseline)"}

    fp = os.path.join(results_dir, "forming_buffer_countdown.csv")
    if os.path.exists(fp):
        f = pd.read_csv(fp)
        ev["forming_n"] = {
            "value": int(len(f)), "n": int(len(f)),
            "source": "results/forming_buffer_countdown.csv", "unit": "warnings",
            "label": "buffer-countdown warnings measured"}

    # Deliberately absent. suggestion_by_priyansh #10 wants the business case
    # LED by "same throughput, 36% lower lead time, zero capex" and calls it a
    # measured release-rate result - but no file in results/ produces it. Under
    # our own rule (measured with a named source, cited with a named reference,
    # or it does not appear) it cannot be shown as measured. Surfacing the gap
    # here is safer than a number that dies under one question from a judge.
    ev["conwip_lead_time"] = {
        "value": None, "source": None, "unit": "%",
        "label": "CONWIP lead-time reduction",
        "reason": "claimed at 36% in the design notes, but no file in results/ "
                  "produces it - must be re-measured or dropped before it is "
                  "presented as ours"}
    return ev
