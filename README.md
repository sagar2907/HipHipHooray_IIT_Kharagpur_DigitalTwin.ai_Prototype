# DigitalTwin.ai
Accenture Innovation Challenge 2026 - Problem Statement 4

A live digital twin of a vehicle assembly line that predicts forming
bottlenecks and predicts defects before they are produced.

## Folders

- `dataset/`  the generated tool telemetry and its hidden ground truth
- `results/`  detector output, RUL estimates, the chart and the full console log
- `scripts/`  the two scripts that regenerate everything
- `reports/`  the three PDF documents

## dataset/

**tool_telemetry.csv** - 54,000 fastening operations across 6 nutrunners,
about 6 days at a 60 second takt. Three tools wear out gradually, one fails
as a sudden step change, two stay healthy.

| column | meaning |
|---|---|
| timestamp, vin | when, and which vehicle (the genealogy backbone) |
| station_id, tool_id | where, and with which tool |
| target_nm, spec_low_nm, spec_high_nm | engineering specification for the joint |
| measured_torque_nm | the primary drift signal |
| measured_angle_deg | rises as the joint under-torques |
| motor_current_a | falls as the motor wears |
| tool_temp_c, cycle_time_s | secondary degradation indicators |
| joint_defective | ground truth: outside tolerance |
| eol_detected | whether end-of-line testing would have caught it |

Modelling notes: degradation is **Weibull** (shape 2.2), not exponential -
memoryless failure is unpredictable in principle. Healthy process capability
is **Cpk approx 1.33**, so the tolerance band is plus or minus four sigma and
random out-of-spec readings are essentially absent before wear begins.

**tool_ground_truth.csv** - the hidden truth per tool: condition, true
degradation onset, first defect and total defects. This is what makes
warning lead time measurable rather than merely asserted.

## Headline results

All four detectors were calibrated to the most sensitive threshold that raised
**no alarm on the 35,300 operations of healthy data used for calibration**, so
that lead times are compared at a matched sensitivity.

> **Do not read that as a false-alarm rate.** Thresholds tuned until a dataset
> produces no alarm will always produce no alarm on *that* dataset — it is a
> definition, not a measurement. Measured on **held-out** healthy data the real
> rate is roughly **one false alarm per five tool-weeks** for CUSUM. The v3
> process dataset carries a separate held-out calibration set precisely so this
> mistake cannot recur; see `dataset/v5/README.md`.

| detector | median warning before scrap begins |
|---|---|
| Spec limit (current practice) | 181 vehicles |
| Shewhart chart | 150 vehicles |
| EWMA | 212 vehicles |
| **CUSUM** | **423 vehicles** |

One vehicle = one minute of line time. Against end-of-line testing, which
sits 40 stations downstream, total warning is 463 vehicles.

Two findings reported just as prominently:
- The **sudden-failure** tool gave no warning to any method. You can predict
  a tyre wearing bald; you cannot predict a nail.
- **Remaining-life estimates are biased roughly 3x too long**, because wear
  accelerates faster than any curve fitted to its early flat stretch. The
  product should alert on detection and show a coarse band, never a countdown.

## Reproducing

```bash
pip install numpy pandas matplotlib
cd scripts
python tool_fault_dataset.py     # writes the two dataset CSVs
python detect_tool_fault.py      # writes results, RUL and the chart
```

Both scripts read and write in the working directory, so run them from a
folder containing the CSVs (or copy the CSVs next to the scripts).
