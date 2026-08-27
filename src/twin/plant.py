"""Layout-driven plant simulator with production calendar. Supersedes line.py.

Everything line.py had - CRN streams, buffers, breakdowns, variants, dark
stations, bursty head-of-line supply - plus the elements a practitioner
would notice missing:

  rework loop            EOL failures visit a repair bay and re-enter for
                         retest; WIP dynamics change materially
  shift calendar         breaks and lunch (the only backlog-drain mechanism),
                         with post-break warm-up on cycle times
  changeover             a scheduled mid-shift model change sweeping down
                         the line as a station-by-station setup wave
  andon stops            operator pulls with reason codes, logged observably
  PM window              one station serviced in the lunch shadow
  parallel stations      one operation, two servers, shared queue (layouts.py)
  new fault classes      material starvation and quality hold - constraints
                         that are NOT "a station got slower"

CRN contract, stated precisely - the earlier version of this note claimed
"perturbing a station's speed changes no other draw", and that is FALSE:

  Every random draw is pre-drawn in build_plant_config, so a rerun with the
  same arguments is bit-identical. But the breakdown draw z_fail[i, t] is
  indexed by WALL CLOCK and only consulted while station i is busy. Perturb
  any station and its neighbours become busy at different ticks, so they
  consult different pre-drawn values and break down at different times.

  Measured consequence (seed 123459, L1): speeding a station up by 20% makes
  11 of 20 stations LOSE cars, worst -5, via 3 extra breakdowns. That puts a
  ~0.79-car noise floor under every sensitivity label in dataset/v5/truth,
  where it shows up as 5.0% physically-impossible negative gains.

  simulate_plant(crn_safe_failures=True) indexes z_fail by the station's own
  accumulated busy ticks instead. Violations drop from 11/20 to 1/20. It is
  also the more defensible physics - MTBF is quoted in operating hours, not
  calendar hours - but it changes every published number, so it is OPT-IN
  until we agree to regenerate. See PROGRESS.md, defect #1.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .calendar import SHIFT_S, Calendar
from .layouts import LAYOUTS, Layout

ANDON_REASONS = ("part_misfeed", "quality_check", "fixture_jam",
                 "operator_assist", "safety_check")


@dataclass
class PlantConfig:
    seed: int
    layout: Layout
    horizon_s: int
    cal: Calendar
    mean_ct: np.ndarray               # spine means
    sigma: np.ndarray
    caps: list
    feeder_ct: dict                   # merge idx -> array of feeder means
    variant_mult: np.ndarray          # [3, n_spine]
    mtbf: np.ndarray
    mttr_mu: np.ndarray
    dark: list
    vintage: object                     # None on L1-L4; per-station list on L5+
    fault: dict
    p_eol_fail: float
    # streams
    z_ct: np.ndarray                  # [spine, draws]
    z_ct_feed: dict                   # merge idx -> [feeder_len, draws]
    z_fail: np.ndarray                # [spine, horizon]
    z_mttr: np.ndarray
    z_supply: np.ndarray              # bool per tick
    variant_of: np.ndarray
    z_eol: np.ndarray                 # per completed unit, uniform
    z_rework: np.ndarray              # per rework visit, lognormal duration
    andon: list = field(default_factory=list)
    changeover_at: int = -1
    pm_station: int = -1
    warm_noise: np.ndarray = None
    # --- physical conveyor transit between stations -----------------------
    # Previously units teleported from one station to the next, which left the
    # dark-station bracketing formula with no transit term to subtract and made
    # "treat transit as a distribution" untestable. Real lines move a body a
    # few seconds between workstations, and the time varies.
    transit_mean: np.ndarray = None       # [n_spine-1] seconds
    z_transit: np.ndarray = None          # [n_spine-1, draws] multipliers
    # --- micro-stops -------------------------------------------------------
    # Brief pauses (20-150 s) that clear themselves before anyone raises a
    # ticket. Industry data puts minor stops at ~34% of production loss and
    # they are INVISIBLE in the downtime log - which is exactly why we model
    # them as inflated processing time with NO state change. They are
    # recoverable only from cycle-time anomalies, which is our claim.
    microstop_rate: np.ndarray = None     # [n_spine] per-unit probability
    z_micro: np.ndarray = None            # [n_spine, draws] uniform
    z_micro_dur: np.ndarray = None        # [n_spine, draws] seconds


# Head-of-line supply dry spells. The first version used MTBF 45 min with a
# 4 min outage - an 8.2% duty cycle that starved the WHOLE line from the front
# and became the dominant loss: 14.1% of station time, three times blocking.
# Every station sat waiting for material, so speeding any one of them bought
# almost nothing and the constraint signal disappeared into the noise.
# Dry spells still occur - the head must be able to starve, which is the
# artefact this originally fixed - but at ~1.1% duty they no longer swamp it.
SUPPLY_MTBF_S = 3 * 3600
SUPPLY_MTTR_S = 2 * 60


def _supply(rng, horizon):
    avail = np.ones(horizon, dtype=bool)
    t = 0
    while t < horizon:
        t += int(rng.exponential(SUPPLY_MTBF_S))
        if t >= horizon:
            break
        d = int(rng.lognormal(np.log(SUPPLY_MTTR_S), 0.4))
        avail[t:t + d] = False
        t += d
    return avail


def build_plant_config(seed: int, layout_name: str = "L1",
                       fault_kind: str = "none", n_shifts: int = 1) -> PlantConfig:
    rng = np.random.default_rng(seed)
    lay = LAYOUTS[layout_name]
    n = lay.n_spine
    horizon = n_shifts * SHIFT_S
    draws = max(1400 * n_shifts, 1400)

    if lay.segment is not None:
        # segment-conditioned draw: each station's ct/sigma range comes from
        # its segment (see layouts.L5) instead of one line-wide range. Order
        # of draws still runs station-by-station 0..n-1 so this is a pure
        # parameterization change, not a new draw pattern.
        mean_ct = np.array([rng.uniform(*lay.seg_ct[s][0]) for s in lay.segment])
        sigma = np.array([rng.uniform(*lay.seg_ct[s][1]) for s in lay.segment])
    else:
        mean_ct = rng.uniform(*lay.ct_range, n)
        sigma = rng.uniform(0.06, 0.14, n)
    # Tighter buffers (was 2-5). Generous buffers absorb a disturbance instead
    # of propagating it, which is precisely what hid the constraint: a station
    # could slow down and the line barely noticed.
    caps = [int(x) for x in rng.integers(1, 4, n - 1)]
    if lay.segment is not None:
        # Paint approximation, NOT a true batch/oven resource: this is a
        # per-unit serial simulator, so "capacity behaves differently from
        # flow" is approximated by larger buffers ahead of paint stations
        # (units accumulate in clusters rather than draining one-for-one),
        # not by a real shared-capacity batch mechanic. Flagged as a known
        # limitation in the v6 README - a real batch resource is future work.
        for i in range(n - 1):
            if lay.segment[i] == "paint":
                caps[i] = max(caps[i], int(rng.integers(4, 8)))
    feeder_ct = {m: rng.uniform(*lay.feeder_ct_range, ln)
                 for m, ln in lay.merges.items()}
    variant_mult = rng.normal(1.0, 0.05, size=(3, n)).clip(0.85, 1.18)
    # Longer MTBF (was 2-4 h). Breakdowns contributed 4.4% of station time and
    # added noise that competed with the cycle-time signal we actually want to
    # detect. Failures still happen; they no longer dominate.
    mtbf = rng.uniform(5, 8, n) * 3600
    mttr_mu = rng.uniform(3, 8, n) * 60

    # dark stations: even seeds force a consecutive pair so the dark-block
    # problem is guaranteed to be present in a controlled share of runs
    inner = np.arange(1, n - 1)
    if lay.segment is not None:
        # segment-conditioned coverage (Part A 1.1): body mostly instrumented,
        # paint booth-level only (all but one station dark - the survivor
        # represents the booth's aggregate sensor), final majority dark.
        # A guaranteed consecutive dark pair is still forced somewhere in
        # final assembly, same spirit as L1-L4's block guarantee.
        dark = [i for i in inner if rng.random() < lay.seg_dark_p[lay.segment[i]]]
        paint_idx = [i for i in inner if lay.segment[i] == "paint"]
        if paint_idx:
            booth = int(rng.choice(paint_idx))
            dark = [i for i in dark if i != booth] + \
                   [i for i in paint_idx if i != booth]
        final_idx = [i for i in inner if lay.segment[i] == "final"]
        if len(final_idx) >= 2 and seed % 2 == 0:
            a = int(rng.choice(final_idx[:-1]))
            if a + 1 in final_idx and a not in dark and a + 1 not in dark:
                dark += [a, a + 1]
        dark = sorted(set(dark))
    elif seed % 2 == 0:
        a = int(rng.choice(inner[:-1]))
        rest = [x for x in inner if abs(x - a) > 1]
        dark = sorted([a, a + 1, int(rng.choice(rest))])
    else:
        dark = sorted(int(x) for x in rng.choice(inner, 3, replace=False))

    fault = dict(kind=fault_kind, idx=-1, onset_s=-1, magnitude=0.0,
                 ramp_s=0, duration_s=0)
    if fault_kind != "none":
        fault["idx"] = int(rng.integers(2, n))
        fault["onset_s"] = int(rng.uniform(1.5, 4.5) * 3600)
        # Stronger degradations (was 10-30%). A 15% slowdown on a station that
        # was not already the slowest changed nothing measurable - correct
        # physics, but it meant most "faulted" runs contained no detectable
        # event. A fault should reliably make its station the constraint.
        if fault_kind == "degrade_ramp":
            fault["magnitude"] = float(rng.uniform(0.35, 0.60))
            fault["ramp_s"] = int(rng.uniform(20, 40) * 60)
        elif fault_kind == "degrade_step":
            fault["magnitude"] = float(rng.uniform(0.35, 0.60))
        elif fault_kind in ("station_down", "material_starvation", "quality_hold"):
            fault["duration_s"] = int(rng.uniform(10, 25) * 60)
        if fault_kind == "quality_hold":
            fault["idx"] = n - 1               # the hold is at the exit gate

    andon = []
    for s0 in range(0, horizon, SHIFT_S):
        for _ in range(int(rng.integers(4, 9))):
            andon.append(dict(
                station=int(rng.integers(1, n)),
                start_s=s0 + int(rng.uniform(0.2, 7.8) * 3600),
                dur_s=int(rng.uniform(1, 6) * 60),
                reason=str(rng.choice(ANDON_REASONS))))
    andon.sort(key=lambda a: a["start_s"])

    return PlantConfig(
        seed=seed, layout=lay, horizon_s=horizon, cal=Calendar(),
        mean_ct=mean_ct, sigma=sigma, caps=caps, feeder_ct=feeder_ct,
        variant_mult=variant_mult, mtbf=mtbf, mttr_mu=mttr_mu, dark=dark,
        vintage=lay.vintage, fault=fault, p_eol_fail=0.03,
        z_ct=np.exp(rng.normal(0, 1, (n, draws)) * sigma[:, None]),
        z_ct_feed={m: np.exp(rng.normal(0, 0.08, (len(v), draws)))
                   for m, v in feeder_ct.items()},
        z_fail=rng.random((n, horizon)),
        z_mttr=np.exp(rng.normal(0, 0.35, (n, 400))),
        z_supply=_supply(rng, horizon),
        variant_of=rng.integers(0, 3, draws * 2),
        z_eol=rng.random(draws * 2),
        z_rework=np.exp(rng.normal(np.log(15 * 60), 0.35, draws)),
        andon=andon,
        changeover_at=int(rng.uniform(3, 5) * 3600),
        pm_station=int(rng.integers(1, n)),
        warm_noise=rng.normal(1.0, 0.02, horizon // 60 + 2),
        # 2-6 s: an indexing line moves a body between adjacent stations in a
        # few seconds. 3-9 s cost ~2 cars of constraint margin for no realism
        # gain, since transit is a flat tax on every station and therefore
        # dilutes the difference between them.
        transit_mean=rng.uniform(2.0, 6.0, max(n - 1, 1)),
        z_transit=np.exp(rng.normal(0, 0.18, (max(n - 1, 1), draws))),
        # 0.4-2.5% of units hit a micro-stop at any given station
        microstop_rate=rng.uniform(0.004, 0.025, n),
        z_micro=rng.random((n, draws)),
        z_micro_dur=np.exp(rng.normal(np.log(45), 0.7, (n, draws))).clip(15, 180))


def simulate_plant(cfg: PlantConfig, speed_scale: np.ndarray | None = None,
                   record: bool = False,
                   perturb: tuple | None = None,
                   stop_at_s: int | None = None,
                   crn_safe_failures: bool = False):
    """perturb=(station_idx, t0_s, t1_s, factor): scale that station's cycle
    time by `factor` ONLY for units started in [t0, t1). With CRN this makes
    the pre-t0 trajectory identical to the baseline run, so a within-window
    completion delta is caused by the within-window perturbation alone -
    the clean per-block counterfactual the sensitivity labels require."""
    lay, n, horizon = cfg.layout, cfg.layout.n_spine, cfg.horizon_s
    if speed_scale is None:
        speed_scale = np.ones(n)
    f = cfg.fault

    # spine: per-station server lists (2 servers for parallel stations)
    servers = [[{"unit": None, "rem": 0.0} for _ in range(2 if i in lay.parallel else 1)]
               for i in range(n)]
    down = np.zeros(n)
    busy_ticks = np.zeros(n, dtype=int)     # see crn_safe_failures
    draw_k = np.zeros(n, dtype=int)
    mttr_k = np.zeros(n, dtype=int)
    setup_until = np.zeros(n)          # changeover wave
    bufs = [[] for _ in range(n - 1)]

    # feeders per merge: chain of single-server stations + output buffer
    feeders = {}
    for m, means in cfg.feeder_ct.items():
        feeders[m] = dict(units=[None] * len(means), rem=[0.0] * len(means),
                          k=[0] * len(means), bufs=[[] for _ in range(len(means))],
                          means=means)

    andon_q = list(cfg.andon)
    andon_active = {}                  # station -> end_s
    rework_pool = []                   # (ready_s, unit)
    rework_k = 0
    eol_k = 0

    scans, states, buffer_ev, andon_log, rework_log = [], [], [], [], []
    last_state = {}
    completions = np.zeros(horizon // 60 + 1, dtype=int)
    n_unit = [0]

    tick_end = horizon if stop_at_s is None else min(horizon, stop_at_s)

    def sname(i):
        return f"S{i+1:02d}"

    def log_state(name, s, t):
        if record and last_state.get(name) != s:
            states.append((name, s, t))
            last_state[name] = s

    microstops = []          # hidden truth: (station, t, duration)

    def start_unit(i, srv, u, t):
        srv["unit"] = u
        k = draw_k[i] % cfg.z_ct.shape[1]
        draw_k[i] += 1
        ct = (cfg.mean_ct[i] * speed_scale[i] * cfg.variant_mult[u[1], i]
              * cfg.z_ct[i, k] * cfg.cal.warmup_mult(t))
        if perturb is not None and i == perturb[0] and perturb[1] <= t < perturb[2]:
            ct *= perturb[3]
        # micro-stop: the unit simply takes much longer. The station never
        # reports a fault and nothing appears in the downtime log - which is
        # the whole point. Only the cycle time betrays it.
        if cfg.z_micro is not None and cfg.z_micro[i, k] < cfg.microstop_rate[i]:
            dur = float(cfg.z_micro_dur[i, k])
            ct += dur
            microstops.append((sname(i), t, round(dur, 1)))
        if i == f["idx"] and f["kind"] in ("degrade_ramp", "degrade_step") \
                and 0 <= f["onset_s"] <= t < f.get("end_s", 10 ** 12):
            if f["kind"] == "degrade_step":
                ct *= 1 + f["magnitude"]
            else:
                ct *= 1 + f["magnitude"] * min(1.0, (t - f["onset_s"]) / f["ramp_s"])
        srv["rem"] = max(1.0, ct)
        if record:
            scans.append((u[0], sname(i), "in", t))

    for t in range(tick_end):
        # ---- calendar: whole line freezes on breaks
        if cfg.cal.on_break(t):
            if record:
                for i in range(n):
                    log_state(sname(i), "break", t)
            # PM: chosen station's service extends 10 min past lunch
            continue

        # ---- scheduled events
        if t == f["onset_s"] and f["kind"] == "station_down":
            down[f["idx"]] = float(f["duration_s"])
        for s0 in range(0, horizon, SHIFT_S):
            if t == s0 + cfg.changeover_at:
                for i in range(n):
                    setup_until[i] = t + i * 45 + 8 * 60
        while andon_q and andon_q[0]["start_s"] == t:
            a = andon_q.pop(0)
            andon_active[a["station"]] = t + a["dur_s"]
            down[a["station"]] = max(down[a["station"]], a["dur_s"])
            if record:
                andon_log.append((sname(a["station"]), a["reason"], t, a["dur_s"]))
        # PM window: 10 extra minutes after lunch for one station
        lunch_end = (t // SHIFT_S) * SHIFT_S + cfg.cal.breaks[1][0] + cfg.cal.breaks[1][1]
        if t == lunch_end:
            down[cfg.pm_station] = max(down[cfg.pm_station], 10 * 60)

        # ---- rework returns: rejoin the buffer before the exit gate
        for r in [r for r in rework_pool if r[0] <= t]:
            if len(bufs[n - 2]) < cfg.caps[n - 2]:
                bufs[n - 2].append((r[1], t))      # repaired unit is available now
                rework_pool.remove(r)
                if record:
                    rework_log.append((r[1][0], "return", t))

        # ---- feeders (downstream first)
        for m, fd in feeders.items():
            L = len(fd["means"])
            for j in range(L - 1, -1, -1):
                cap = 4 if j == L - 1 else 3
                if fd["units"][j] is not None:
                    if fd["rem"][j] > 0:
                        fd["rem"][j] -= 1
                    elif len(fd["bufs"][j]) < cap:
                        fd["bufs"][j].append(fd["units"][j])
                        fd["units"][j] = None
                if fd["units"][j] is None:
                    if j == 0:
                        fd["units"][j] = (f"U{m}_{fd['k'][0]}", 0)
                        fd["k"][0] += 1
                        kk = fd["k"][0] % cfg.z_ct_feed[m].shape[1]
                        fd["rem"][j] = max(1.0, fd["means"][j] * cfg.z_ct_feed[m][j, kk])
                    elif fd["bufs"][j - 1]:
                        fd["units"][j] = fd["bufs"][j - 1].pop(0)
                        kk = fd["k"][j] % cfg.z_ct_feed[m].shape[1]
                        fd["k"][j] += 1
                        fd["rem"][j] = max(1.0, fd["means"][j] * cfg.z_ct_feed[m][j, kk])

        # ---- spine (downstream first)
        for i in range(n - 1, -1, -1):
            nm = sname(i)
            if down[i] > 0:
                down[i] -= 1
                log_state(nm, "down", t)
                continue
            if t < setup_until[i]:
                log_state(nm, "down", t)
                continue
            busy = any(s["unit"] is not None and s["rem"] > 0 for s in servers[i])
            # Failure draw index. Default (wall clock) is NOT CRN-safe: the
            # draw is gated on `busy`, so perturbing any station shifts which
            # ticks its neighbours are busy for, and they then sample entirely
            # different pre-drawn failure values. That is what lets a 20%
            # SPEED-UP lose cars (measured: 33 -> 36 breakdowns, -5 cars) and
            # it puts a ~0.79-car noise floor under every sensitivity label.
            # crn_safe_failures indexes by the station's own accumulated busy
            # ticks instead, so its failure sequence depends only on how much
            # work it has done - which is also the more defensible physics,
            # since MTBF is quoted in operating hours, not calendar hours.
            if crn_safe_failures:
                fi = busy_ticks[i]
                if busy:
                    busy_ticks[i] += 1
            else:
                fi = t
            if busy and cfg.z_fail[i, fi % cfg.z_fail.shape[1]] < 1.0 / cfg.mtbf[i]:
                down[i] = cfg.mttr_mu[i] * cfg.z_mttr[i, mttr_k[i] % 400]
                mttr_k[i] += 1
                log_state(nm, "down", t)
                continue

            worked = blocked = False
            for srv in servers[i]:
                if srv["unit"] is None:
                    continue
                if srv["rem"] > 0:
                    srv["rem"] -= 1
                    worked = True
                    continue
                u = srv["unit"]
                if i == n - 1:
                    # exit gate: EOL test with rework loop; quality_hold
                    # freezes release with no station fault at all
                    if f["kind"] == "quality_hold" and \
                            f["onset_s"] <= t < f["onset_s"] + f["duration_s"]:
                        blocked = True
                        continue
                    if record:
                        scans.append((u[0], nm, "out", t))
                    if cfg.z_eol[eol_k % len(cfg.z_eol)] < cfg.p_eol_fail:
                        dur = cfg.z_rework[rework_k % len(cfg.z_rework)]
                        rework_k += 1
                        rework_pool.append((t + dur, u))
                        if record:
                            rework_log.append((u[0], "fail", t))
                    else:
                        completions[t // 60] += 1
                    eol_k += 1
                    srv["unit"] = None
                elif len(bufs[i]) < cfg.caps[i]:
                    # unit rides the conveyor: it enters the buffer now but is
                    # not reachable by the next station until transit elapses
                    kt = draw_k[i] % cfg.z_transit.shape[1]
                    tr = cfg.transit_mean[i] * cfg.z_transit[i, kt]
                    bufs[i].append((u, t + tr))
                    if record:
                        scans.append((u[0], nm, "out", t))
                        buffer_ev.append((f"B{i+1:02d}", len(bufs[i]), cfg.caps[i], t))
                    srv["unit"] = None
                else:
                    blocked = True

            for srv in servers[i]:
                if srv["unit"] is not None:
                    continue
                # material starvation: station cannot start new units
                if i == f["idx"] and f["kind"] == "material_starvation" and \
                        f["onset_s"] <= t < f["onset_s"] + f["duration_s"]:
                    continue
                got = None
                if i == 0:
                    if cfg.z_supply[t]:
                        n_unit[0] += 1
                        got = (f"V{n_unit[0]:06d}",
                               int(cfg.variant_of[n_unit[0] % len(cfg.variant_of)]))
                elif bufs[i - 1] and bufs[i - 1][0][1] <= t:
                    # head of the upstream buffer has finished its transit
                    if i in lay.merges:
                        fd = feeders[i]
                        if fd["bufs"][-1]:
                            got = bufs[i - 1].pop(0)[0]
                            fd["bufs"][-1].pop(0)
                            if record:
                                buffer_ev.append((f"B{i:02d}", len(bufs[i - 1]),
                                                  cfg.caps[i - 1], t))
                    else:
                        got = bufs[i - 1].pop(0)[0]
                        if record:
                            buffer_ev.append((f"B{i:02d}", len(bufs[i - 1]),
                                              cfg.caps[i - 1], t))
                if got is not None:
                    start_unit(i, srv, got, t)
                    worked = True

            state = ("working" if worked else
                     "blocked" if blocked else "starved")
            log_state(nm, state, t)

    out = dict(completions=completions, total=int(completions.sum()),
               rework_visits=rework_k)
    if record:
        out.update(microstops=microstops,
                   scans=scans, states=states, buffers=buffer_ev,
                   andon=andon_log, rework=rework_log,
                   dark=[sname(i) for i in cfg.dark],
                   calendar=cfg.cal.rows(horizon))
    return out
