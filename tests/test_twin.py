"""Invariant tests for the twin package and the v3 datasets.

Run with:  pytest tests/ -q
These are the checks that keep the dataset honest - CRN determinism,
conservation, and above all NO information leakage from hidden/ into
observed files.
"""

import glob
import os
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from twin.calendar import Calendar, SHIFT_S                         # noqa: E402
from twin.events import active_periods, state_spans                 # noqa: E402
from twin.plant import build_plant_config, simulate_plant           # noqa: E402
from twin.tools import ToolSpec, damage_path, generate_tool         # noqa: E402

V3 = os.path.join(ROOT, "dataset", "v3")


# ------------------------------------------------------------- simulator
def test_crn_determinism():
    """Same config, same arguments -> identical completions, twice."""
    cfg = build_plant_config(123457, "L1", "degrade_ramp", 1)
    a = simulate_plant(cfg)["completions"]
    b = simulate_plant(cfg)["completions"]
    assert np.array_equal(a, b)


def test_crn_perturbation_isolated():
    """A windowed perturbation must not change anything before its window."""
    cfg = build_plant_config(123458, "L1", "none", 1)
    base = simulate_plant(cfg)["completions"]
    pert = simulate_plant(cfg, perturb=(5, 4 * 3600, 5 * 3600, 0.8))["completions"]
    assert np.array_equal(base[: 4 * 60], pert[: 4 * 60]), \
        "history before the perturbation window must be identical (CRN)"


def test_speedup_never_hurts_much():
    """Speeding one station up may gain cars, must not lose many.

    Holds on the CRN-safe failure path. It does NOT hold on the default
    wall-clock path - see test_wallclock_failures_break_crn below and the
    plant.py module docstring. This is the real invariant, kept as a passing
    test rather than deleted, because deleting it would delete the knowledge.
    """
    cfg = build_plant_config(123459, "L1", "none", 1)
    base = simulate_plant(cfg, crn_safe_failures=True)["total"]
    for i in (0, 7, 19):
        r = simulate_plant(cfg, speed_scale=np.where(np.arange(20) == i, 0.8, 1.0),
                           crn_safe_failures=True)
        assert r["total"] >= base - 2, f"station {i} lost {base - r['total']} cars"


def test_wallclock_failures_break_crn():
    """Pin the KNOWN defect so it cannot regress silently or be forgotten.

    z_fail is indexed by wall clock and gated on `busy`, so perturbing one
    station changes which failure draws its neighbours consult. This test
    asserts the bug is still exactly as characterised in PROGRESS.md defect
    #1; when we regenerate with crn_safe_failures=True it should start
    failing, and that failure is the signal to delete it.
    """
    cfg = build_plant_config(123459, "L1", "none", 1)
    base = simulate_plant(cfg)["total"]
    losses = [base - simulate_plant(
        cfg, speed_scale=np.where(np.arange(20) == i, 0.8, 1.0))["total"]
        for i in range(20)]
    assert max(losses) >= 3, "wall-clock desync appears fixed - retire this test"
    # and the CRN-safe path must be strictly better on the same seed
    safe_base = simulate_plant(cfg, crn_safe_failures=True)["total"]
    safe = [safe_base - simulate_plant(
        cfg, speed_scale=np.where(np.arange(20) == i, 0.8, 1.0),
        crn_safe_failures=True)["total"] for i in range(20)]
    assert sum(x > 0 for x in safe) < sum(x > 0 for x in losses)


def test_conservation():
    """Every vehicle that exits passed every spine station, in order."""
    cfg = build_plant_config(123460, "L1", "none", 1)
    res = simulate_plant(cfg, record=True)
    sc = pd.DataFrame(res["scans"], columns=["vin", "station", "event", "t"])
    veh = sc[sc.vin.str.startswith("V")]
    exited = set(veh[(veh.station == "S20") & (veh.event == "out")].vin)
    for v in list(exited)[:50]:
        g = veh[(veh.vin == v) & (veh.event == "in")].sort_values("t")
        seq = list(g.station)
        # first pass must be S01..S20 in order; any extra scans may only be
        # S20 retests after a rework-loop visit
        assert seq[:20] == [f"S{i:02d}" for i in range(1, 21)], v
        assert all(s == "S20" for s in seq[20:]), v


def test_breaks_freeze_line():
    """No completions during scheduled breaks."""
    cfg = build_plant_config(123461, "L1", "none", 1)
    res = simulate_plant(cfg)
    cal = Calendar()
    for s, d in cal.breaks:
        m0, m1 = s // 60, (s + d) // 60
        assert res["completions"][m0 + 1: m1 - 1].sum() == 0


# ---------------------------------------------------------------- events
def test_active_period_merge():
    """working->down->working is ONE active period, not three."""
    spans = [(0, 100, "working"), (100, 130, "down"), (130, 300, "working"),
             (300, 350, "starved"), (350, 400, "working")]
    ap = active_periods(spans)
    assert ap == [(0, 300), (350, 400)]


# ----------------------------------------------------------------- tools
def test_damage_paths_differ():
    rng = np.random.default_rng(1)
    a = damage_path(rng, 5000, 1000, 2000)
    b = damage_path(rng, 5000, 1000, 2000)
    assert not np.allclose(a, b), "damage paths must be stochastic"
    assert a[:1000].sum() == 0 and b[:1000].sum() == 0


def test_pure_transducer_drift_is_mechanically_silent():
    """The defining property: sensor drifts, machine channels do not."""
    rng = np.random.default_rng(2)
    t = ToolSpec("T1", "nutrunner", 5, "pure_transducer_drift", 45.0, 0.10,
                 4000, 3000)
    ch, true_p, tdef, nok, truth, _ = generate_tool(
        rng, t, 12000, np.zeros(12000), np.zeros(12000))
    late, early = slice(-2000, None), slice(0, 2000)
    # measured torque drifts by construction
    assert ch["torque_nm"][late].mean() < ch["torque_nm"][early].mean() - 0.5
    # but motor current stays put - the tool is healthy
    assert abs(ch["current_a"][late].mean() - ch["current_a"][early].mean()) < 0.15
    # and the TRUE process barely makes defects
    assert truth["total_true_defects"] < 30
    # while the controller, judging the lying sensor, rejects good parts
    assert truth["total_controller_nok"] > 200


def test_sensor_bias_passes_bad_parts():
    rng = np.random.default_rng(3)
    t = ToolSpec("T2", "nutrunner", 5, "sensor_bias", 45.0, 0.10, 4000, 3000)
    *_, truth, _ = generate_tool(rng, t, 12000, np.zeros(12000), np.zeros(12000))
    assert truth["defects_passed_ok"] > 0.8 * truth["total_true_defects"]


# ----------------------------------------------- dataset leakage (if built)
FORBIDDEN = ("true_", "onset", "condition", "defective", "damage", "health")


@pytest.mark.skipif(not os.path.isdir(V3), reason="v3 not generated")
def test_no_leakage_process():
    for f in glob.glob(os.path.join(V3, "process", "*.csv")) + \
             glob.glob(os.path.join(V3, "process", "holdout", "*.csv")):
        cols = [c.lower() for c in pd.read_csv(f, nrows=1).columns]
        for c in cols:
            assert not any(k in c for k in FORBIDDEN), (f, c)


@pytest.mark.skipif(not os.path.isdir(V3), reason="v3 not generated")
def test_no_leakage_flow():
    for rd in glob.glob(os.path.join(V3, "flow", "runs", "*")):
        for f in glob.glob(os.path.join(rd, "*.csv")):
            cols = [c.lower() for c in pd.read_csv(f, nrows=1).columns]
            for c in cols:
                assert not any(k in c for k in FORBIDDEN), (f, c)
        # dark stations truly absent from observed logs
        import json
        dark = None
        st = pd.read_csv(os.path.join(rd, "station_state.csv"))
        full = pd.read_csv(os.path.join(rd, "hidden", "station_state_full.csv"))
        hidden_only = set(full.station_id) - set(st.station_id)
        assert len(hidden_only) == 3, rd
