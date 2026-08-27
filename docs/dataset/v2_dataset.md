# Datasets v2 — telemetry taxonomy + line flow

Generated 2026-08-14 by `scripts/tool_telemetry_v2.py` and `scripts/line_sim.py`.
Validation output: `results/validation_v2.txt` (regenerate with `scripts/validate_v2.py`).

These extend the original `tool_telemetry.csv` experiment after an audit found
its three weak points: in-sample calibration, a single seed, and one fault
signature. v2 fixes all three and adds the flow half of the problem.

## v2/ — tool telemetry, second generation

| file | rows | what it is |
|---|---|---|
| `telemetry_v2.csv` | 288,000 | 24 tools × 12,000 ops, 7 condition types |
| `ground_truth_v2.csv` | 24 | hidden truth: condition, onset, defects, EOL lag |
| `healthy_calibration.csv` | 144,000 | 12 healthy tools, **different seed** — calibrate thresholds here, never on the evaluation data |
| `quality_results.csv` | 5,284 | end-of-line inspection events (VIN, arrival time at EOL, FAIL/PASS, codes) — join via VIN for genealogy |

What changed vs v1:

- **Physical time.** Vehicle *v* is at station *s* at `t0 + (v+s)·takt`. A VIN
  is never at two stations simultaneously; EOL events occur at true arrival.
- **Stochastic wear.** Gamma-process damage with acceleration feedback —
  every degradation path is different, none is a memorizable curve.
- **Seven conditions**: healthy (8), gradual_wear (5), spread_only (3),
  sudden_shift (2), sensor_bias (2), overtorque (2), intermittent (2).
  `sensor_bias` is the important one: the torque *reading* stays near target
  while the true clamp force drifts — over 1,000 defects with almost no
  torque signal. Only motor current / angle reveal it.
- **Confounded channels.** Current and temperature share a daily ambient
  cycle; a per-joint friction factor moves torque, angle and current
  together. The current channel is no longer a free lunch.
- **Random escapes are real and quantified**: at Cpk 1.33 expect ~0.76
  out-of-tolerance readings per healthy 12,000-op tool (≈6.3×10⁻⁵/op).
  Healthy tools in the ground truth show 0–1 defects. This is by design —
  do not claim "zero random escapes."

Measured baseline (held-out calibration, pre-onset alarms scored as false):

| condition | torque-only CUSUM median lead | torque+current median lead |
|---|---|---|
| gradual_wear | 309 vehicles | 328 |
| overtorque | 755 | 755 |
| spread_only | **−28 (fails)** | 470 |
| sensor_bias | **−52 (fails)** | 480 |
| intermittent | **−896 (fails)** | 299 |
| sudden_shift | 22 (physics: no precursor) | 23 |

False alarms out-of-sample: torque-CUSUM 0/8 healthy tools, current-CUSUM
2/8 over 12,000 ops each. Report these numbers, not "zero."

## line/ — assembly line flow event logs

28 simulated 8-hour shifts of a 20-station serial line with a 3-station
subassembly feeder merging at S12. Buffers 2–5, three product variants,
lognormal cycle times (means 52–58 s, randomized per run), background
breakdowns (MTBF 2–4 h, MTTR 3–8 min).

| file | what it is |
|---|---|
| `run_manifest.csv` | per run: config, injected fault, dark stations, JPH, event counts |
| `runs/run_NN/unit_scan.csv` | vin, station, in/out, t — **dark stations removed** |
| `runs/run_NN/station_state.csv` | working/blocked/starved/down transitions — dark removed |
| `runs/run_NN/buffer_level.csv` | buffer level changes (PLC counters exist even at dark stations) |
| `runs/run_NN/hidden/unit_scan_full.csv` | includes dark stations — virtual-sensing ground truth |
| `runs/run_NN/hidden/station_state_full.csv` | full state truth |
| `runs/run_NN/hidden/bottleneck_truth.csv` | per-minute primary/secondary bottleneck via active-period criterion (full knowledge) |

Fault mix: 8× `degrade_ramp` (10–30% cycle-time ramp over 20–40 min),
6× `degrade_step`, 6× `station_down` (10–25 min), 8× `none` (for false-alarm
measurement). Onsets known exactly → lead time is measurable.

Two properties are deliberate, not bugs:

1. **Not every injected fault becomes the bottleneck.** A 12% slowdown on a
   fast station can stay sub-constraint (`truth_bneck_is_fault_station_post_onset`
   near 0). Distinguishing faults that matter from faults that don't is the
   twin's job — a dataset where every fault dominates would be too easy.
2. **Repair time counts as active** (Roser's criterion): during a breakdown
   the broken station *is* the momentary bottleneck, so background failures
   move the truth label around. That is the shifting-bottleneck phenomenon,
   present in the labels because it is present in real lines.

Conservation verified: every exited vehicle passed all 20 stations, in order.
No-fault JPH 56.3 mean vs 54.2 under faults.

## Status

**Superseded.** v5 replaces `dataset/line` and `line_v2` entirely; see
`v5_dataset.md`. Kept here because the v2 validation results are still the
source for the torque-only-CUSUM failure claim. Everything regenerates from
`scripts/tool_telemetry_v2.py`, `line_sim.py` and `validate_v2.py` on fixed
seeds.
