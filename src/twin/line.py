"""The line simulator, as a library, with common random numbers.

Why CRN matters here. To find the true constraint we ask a counterfactual:
"if this station ran 10% faster, how many more cars would leave the line?"
That question is only answerable if the perturbed run and the baseline run
share every random draw - otherwise the answer is buried in simulation
noise. So all randomness is pre-drawn into fixed streams, and a speed
perturbation rescales a cycle time without touching the stream it came from.

With CRN, perturbing a station that is not constraining typically changes
the output by exactly zero cars. That is not a bug: it is the constraint
principle, visible as an identity.

Line model
  20-station serial spine, plus a 3-station subassembly feeder merging at
  S12. Buffers of capacity 2-5. Three product variants. Lognormal cycle
  times. Random breakdowns with lognormal repair. Station 1 draws from a
  supplying process that can itself run dry, so the head of the line is not
  trivially saturated.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

N_SPINE = 20
N_SUB = 3
MERGE_AT = 12
SHIFT_S = 8 * 3600
DRAWS_PER_STATION = 1200          # more than enough units per shift


SUPPLY_MTBF_S = 45 * 60           # body-store dry spell, roughly hourly
SUPPLY_MTTR_S = 4 * 60


def _supply_schedule(rng, horizon_s: int = SHIFT_S) -> np.ndarray:
    """Boolean per tick: is a body available to start at the head of the line?

    Modelled as occasional dry spells lasting minutes, not an independent
    coin flip per tick. A per-tick flip is retried immediately and therefore
    never actually starves station 1, which would leave the head of the line
    permanently active and trivially the constraint - an artefact, not a
    property of real plants, where the body store does run dry.
    """
    avail = np.ones(horizon_s, dtype=bool)
    t = 0
    while t < horizon_s:
        t += int(rng.exponential(SUPPLY_MTBF_S))
        if t >= horizon_s:
            break
        dur = int(rng.lognormal(np.log(SUPPLY_MTTR_S), 0.4))
        avail[t:t + dur] = False
        t += dur
    return avail


@dataclass
class LineConfig:
    seed: int
    mean_ct: np.ndarray               # spine + sub station mean cycle times
    sigma: np.ndarray
    caps: list[int]
    sub_caps: list[int]
    variant_mult: np.ndarray
    mtbf: np.ndarray
    mttr_mu: np.ndarray
    # pre-drawn random streams (common random numbers)
    z_ct: np.ndarray                  # [station, k] lognormal(0, sigma) multipliers
    z_fail: np.ndarray                # [station, tick] uniform
    z_mttr: np.ndarray                # [station, k] lognormal repair draws
    variant_of: np.ndarray            # [unit] variant id
    z_supply: np.ndarray              # [tick] uniform, head-of-line supply
    supply_p: float
    dark: list[int] = field(default_factory=list)
    fault: dict = field(default_factory=dict)


def build_config(seed: int, fault_kind: str = "none") -> LineConfig:
    rng = np.random.default_rng(seed)
    n_all = N_SPINE + N_SUB
    mean_ct = np.concatenate([rng.uniform(52, 58, N_SPINE),
                              rng.uniform(50, 56, N_SUB)])
    sigma = np.concatenate([rng.uniform(0.06, 0.14, N_SPINE),
                            rng.uniform(0.06, 0.12, N_SUB)])
    caps = [int(x) for x in rng.integers(2, 6, N_SPINE - 1)]
    sub_caps = [int(x) for x in rng.integers(2, 5, N_SUB - 1)] + [4]
    variant_mult = rng.normal(1.0, 0.05, size=(3, n_all)).clip(0.85, 1.18)
    mtbf = rng.uniform(2, 4, n_all) * 3600
    mttr_mu = rng.uniform(3, 8, n_all) * 60

    z_ct = np.exp(rng.normal(0, 1, size=(n_all, DRAWS_PER_STATION)) * sigma[:, None])
    z_fail = rng.random(size=(n_all, SHIFT_S))
    z_mttr = np.exp(rng.normal(0, 0.35, size=(n_all, 200)))
    variant_of = rng.integers(0, 3, size=DRAWS_PER_STATION * 2)
    z_supply = _supply_schedule(rng)

    dark = sorted(int(x) for x in rng.choice(np.arange(1, N_SPINE - 1), 3,
                                             replace=False))

    fault = dict(kind=fault_kind, idx=-1, onset_s=-1, magnitude=0.0,
                 ramp_s=0, duration_s=0)
    if fault_kind != "none":
        fault["idx"] = int(rng.integers(2, N_SPINE))
        fault["onset_s"] = int(rng.uniform(1.5, 4.5) * 3600)
        if fault_kind == "degrade_ramp":
            fault["magnitude"] = float(rng.uniform(0.10, 0.30))
            fault["ramp_s"] = int(rng.uniform(20, 40) * 60)
        elif fault_kind == "degrade_step":
            fault["magnitude"] = float(rng.uniform(0.10, 0.30))
        elif fault_kind == "station_down":
            fault["duration_s"] = int(rng.uniform(10, 25) * 60)

    return LineConfig(seed=seed, mean_ct=mean_ct, sigma=sigma, caps=caps,
                      sub_caps=sub_caps, variant_mult=variant_mult, mtbf=mtbf,
                      mttr_mu=mttr_mu, z_ct=z_ct, z_fail=z_fail, z_mttr=z_mttr,
                      variant_of=variant_of, z_supply=z_supply,
                      supply_p=0.985, dark=dark, fault=fault)


def reseed_streams(cfg: LineConfig, seed: int) -> LineConfig:
    """Fresh random streams, identical line. One replication of the same plant.

    The layout, cycle-time means, buffer sizes and fault schedule are held
    fixed; only the noise changes. Averaging a sensitivity measurement over
    several of these separates a real constraint from a lucky shift.
    """
    import copy
    rng = np.random.default_rng(seed)
    n_all = N_SPINE + N_SUB
    c = copy.copy(cfg)
    c.z_ct = np.exp(rng.normal(0, 1, size=(n_all, DRAWS_PER_STATION))
                    * cfg.sigma[:, None])
    c.z_fail = rng.random(size=(n_all, SHIFT_S))
    c.z_mttr = np.exp(rng.normal(0, 0.35, size=(n_all, 200)))
    c.variant_of = rng.integers(0, 3, size=DRAWS_PER_STATION * 2)
    c.z_supply = _supply_schedule(rng)
    return c


def simulate(cfg: LineConfig, speed_scale: np.ndarray | None = None,
             record: bool = False, horizon_s: int = SHIFT_S):
    """Run one shift. speed_scale[i] < 1 makes station i faster.

    Returns completions per minute always; full event logs only if record.
    """
    n_all = N_SPINE + N_SUB
    if speed_scale is None:
        speed_scale = np.ones(n_all)

    unit = [None] * n_all              # (id, variant) per station
    rem = np.zeros(n_all)
    draw_k = np.zeros(n_all, dtype=int)
    mttr_k = np.zeros(n_all, dtype=int)
    down_left = np.zeros(n_all)
    bufs = [[] for _ in range(N_SPINE - 1)]
    sub_bufs = [[] for _ in range(N_SUB)]

    scans, states, buffers = [], [], []
    last_state = [None] * n_all
    completions = np.zeros(horizon_s // 60 + 1, dtype=int)
    n_unit = 0
    n_sub = 0
    f = cfg.fault
    base_mean = cfg.mean_ct.copy()

    def log_state(i, s, t):
        if record and last_state[i] != s:
            states.append((_name(i), s, t))
            last_state[i] = s

    def _name(i):
        return f"S{i+1:02d}" if i < N_SPINE else f"A{i-N_SPINE+1:02d}"

    def start(i, u, t):
        nonlocal unit
        unit[i] = u
        k = draw_k[i] % DRAWS_PER_STATION
        draw_k[i] += 1
        ct = base_mean[i] * speed_scale[i] * cfg.variant_mult[u[1], i] * cfg.z_ct[i, k]
        if i == f["idx"] and f["kind"] in ("degrade_ramp", "degrade_step") \
                and f["onset_s"] >= 0 and t >= f["onset_s"]:
            if f["kind"] == "degrade_step":
                ct *= 1.0 + f["magnitude"]
            else:
                ct *= 1.0 + f["magnitude"] * min(1.0, (t - f["onset_s"]) / f["ramp_s"])
        rem[i] = max(1.0, ct)
        if record:
            scans.append((u[0], _name(i), "in", t))

    for t in range(horizon_s):
        if f["kind"] == "station_down" and t == f["onset_s"]:
            down_left[f["idx"]] = float(f["duration_s"])

        # ---------------- subassembly feeder, downstream first
        for j in range(N_SUB - 1, -1, -1):
            i = N_SPINE + j
            if down_left[i] > 0:
                down_left[i] -= 1
                log_state(i, "down", t)
                continue
            if unit[i] is not None and rem[i] > 0 and cfg.z_fail[i, t] < 1.0 / cfg.mtbf[i]:
                k = mttr_k[i] % 200
                mttr_k[i] += 1
                down_left[i] = cfg.mttr_mu[i] * cfg.z_mttr[i, k]
                log_state(i, "down", t)
                continue
            cap = cfg.sub_caps[j] if j < N_SUB - 1 else 4
            if unit[i] is not None:
                if rem[i] > 0:
                    rem[i] -= 1
                    log_state(i, "working", t)
                elif len(sub_bufs[j]) < cap:
                    sub_bufs[j].append(unit[i])
                    if record:
                        scans.append((unit[i][0], _name(i), "out", t))
                        buffers.append((f"BA{j+1:02d}", len(sub_bufs[j]), cap, t))
                    unit[i] = None
                else:
                    log_state(i, "blocked", t)
            if unit[i] is None:
                got = None
                if j == 0:
                    n_sub += 1
                    got = (f"U{n_sub:05d}", int(cfg.variant_of[n_sub % len(cfg.variant_of)]))
                elif sub_bufs[j - 1]:
                    got = sub_bufs[j - 1].pop(0)
                    if record:
                        buffers.append((f"BA{j:02d}", len(sub_bufs[j - 1]),
                                        cfg.sub_caps[j - 1], t))
                if got is not None:
                    start(i, got, t)
                    log_state(i, "working", t)
                else:
                    log_state(i, "starved", t)

        # ---------------- spine, downstream first
        for i in range(N_SPINE - 1, -1, -1):
            if down_left[i] > 0:
                down_left[i] -= 1
                log_state(i, "down", t)
                continue
            if unit[i] is not None and rem[i] > 0 and cfg.z_fail[i, t] < 1.0 / cfg.mtbf[i]:
                k = mttr_k[i] % 200
                mttr_k[i] += 1
                down_left[i] = cfg.mttr_mu[i] * cfg.z_mttr[i, k]
                log_state(i, "down", t)
                continue
            if unit[i] is not None:
                if rem[i] > 0:
                    rem[i] -= 1
                    log_state(i, "working", t)
                elif i == N_SPINE - 1:
                    if record:
                        scans.append((unit[i][0], _name(i), "out", t))
                    unit[i] = None
                    completions[t // 60] += 1
                elif len(bufs[i]) < cfg.caps[i]:
                    bufs[i].append(unit[i])
                    if record:
                        scans.append((unit[i][0], _name(i), "out", t))
                        buffers.append((f"B{i+1:02d}", len(bufs[i]), cfg.caps[i], t))
                    unit[i] = None
                else:
                    log_state(i, "blocked", t)
            if unit[i] is None:
                got = None
                if i == 0:
                    # head of line: supply is a process, not an infinite tap
                    if cfg.z_supply[t]:
                        n_unit += 1
                        got = (f"V{n_unit:05d}",
                               int(cfg.variant_of[n_unit % len(cfg.variant_of)]))
                elif bufs[i - 1]:
                    if i == MERGE_AT - 1:
                        if sub_bufs[-1]:
                            got = bufs[i - 1].pop(0)
                            sub_bufs[-1].pop(0)
                            if record:
                                buffers.append((f"B{i:02d}", len(bufs[i - 1]),
                                                cfg.caps[i - 1], t))
                    else:
                        got = bufs[i - 1].pop(0)
                        if record:
                            buffers.append((f"B{i:02d}", len(bufs[i - 1]),
                                            cfg.caps[i - 1], t))
                if got is not None:
                    start(i, got, t)
                    log_state(i, "working", t)
                else:
                    log_state(i, "starved", t)

    out = dict(completions=completions, total=int(completions.sum()))
    if record:
        out.update(scans=scans, states=states, buffers=buffers,
                   dark=[f"S{i+1:02d}" for i in cfg.dark])
    return out
