# PROGRESS

**Repo:** `HipHipHooray_IIT_Kharagpur_DigitalTwin.ai_Prototype`
**Team:** Sagar Sahu (`@sagar2907`) · Priyansh Goyal (`@Priyansh0704`)
**Accenture Innovation Challenge 2026 — Problem Statement 4, Round 2**

> **The one rule:** update the **Right now** block before you stop working for the day.
> Everything else in this file can drift a little. That block cannot.

---

## Right now

_Last updated: 2026-08-23 by **Priyansh**_

| | Working on | Branch | Expect to finish | Blocked by |
|---|---|---|---|---|
| **Sagar** | _not started_ — Workstream B (the loop) is yours and nothing blocks it | — | — | — |
| **Priyansh** | Repo set up and seeded. Next: Workstream A, clear the ground | `main` | — | — |

**Next joint checkpoint:** _(set a date)_

**Sagar — read this first.** The repo is no longer empty. The entire Round 1 archive is now
in it, so you don't need anything off a shared drive or the old repo. Start at
`START_HERE.txt`, then `4_Design_Documents/DigitalTwin_Three_Pipelines.pdf` — that is the
source of truth, not the old README. Then `DigitalTwin_Model_Parameters.pdf` for what
actually feeds the model.

---

## Work log

Append-only, newest at the top. One line per meaningful change, so whoever was away can
catch up without reading diffs.

| Date | Who | What | Commit |
|---|---|---|---|
| 2026-08-23 | **Priyansh** | Committed the full Round 1 archive into the repo — guide, Round 2 plan, Round 1 submission (deck, PDF, 2:53 pitch video), design documents, animation sources, code snapshot zip. 24 files, ~34 MB. **The repo is now the single source of truth**; the Desktop handover folder is a copy, not the original. | `d843ba8` |
| 2026-08-23 | **Priyansh** | Added `DigitalTwin_Model_Parameters.pdf` — the two parameter tables (51 bottleneck, 37 defect) with an explanation for every field. This is the contract for what feeds the model; agree any change to it before coding against it. | `d843ba8` |
| 2026-08-23 | **Priyansh** | Created this file — status board, file-ownership split, decision log, the nine defects carried from Round 1, and the gap list against the brief. | `f7a4860` |

---

## Repo layout

| Path | What it is |
|---|---|
| `PROGRESS.md` | **This file — the canonical copy. Edit this one.** |
| `DigitalTwin_Model_Parameters.pdf` | Every parameter fed to the model, with explanations |
| `1_Guide/` | Project guide — what is built, what is designed, what failed |
| `2_Plan/` | The original Round 2 plan. Superseded on sequencing by the status board below |
| `3_Round1_Submission/` | Deck, PDF and pitch video exactly as submitted |
| `4_Design_Documents/` | **Source of truth.** Three Pipelines (21pp), Evidence File (6pp), official brief |
| `5_Animation_Sources/` | Self-contained HTML animations, captioned MP4, result figures |
| `6_Code/` | Round 1 codebase snapshot. Live version: `github.com/sagar2907/HipHipHooray_DigitalTwin.ai` |
| `7_Prototype/` | Round 2 prototype work goes here |

> **Two housekeeping items, both for whoever gets there first:**
> 1. There are two copies of this file — root and `7_Prototype/`. Root is canonical.
>    Delete `7_Prototype/PROGRESS.md` before they diverge.
> 2. The video, pptx and zip are ~30 MB and are now permanent in git history. Fine at this
>    size, but don't add more large binaries. Datasets stay gitignored and get regenerated
>    from the seeded builders.

---

## Status board

State: `todo` · `wip` · `review` · `done` · `blocked` · `cut`

| # | Workstream | Owner | State | Gate — what "done" means |
|---|---|---|---|---|
| **A** | Clear the ground | Priyansh | `todo` | 11/11 tests green; noise floor published; two doc errors corrected |
| **B** | The loop (`record.py` + `loop.py`) | Sagar | `todo` | A full shift replays at 60x in a browser, driven by a loop that never sees `t > now` |
| **C** | Alert contract + trust ledger | Sagar | `todo` | Every alert carries all 5 fields; calibration curve within ±10 pts; ledger shows running precision |
| **D** | Scale to 40 stations + transfer tests | Priyansh | `todo` | Layout-transfer number, sensor-maturity transfer number, classifier scored on firewall set |
| **E** | Three stakeholder views | Both | `todo` | Three views, one record stream, switchable live |
| **F** | Genealogy + stop-or-continue | Both | `todo` | Same drifting tool, opposite correct answers depending on flow state |
| **G** | Business case + deck | Both | `todo` | 5-minute walkthrough runnable end to end without touching a script |

**Cut order if time runs short:** F first, then D, then E. **Never B.**

---

## File ownership — avoid merge conflicts

Don't edit outside your column without saying so in the Right now block first.

| Sagar | Priyansh | Shared (announce before editing) |
|---|---|---|
| `src/twin/loop.py` | `src/twin/plant.py` | `src/twin/detect.py` |
| `src/twin/record.py` | `src/twin/layouts.py` | `src/twin/events.py` |
| `src/twin/alerts.py` | `src/twin/dark.py` | `tests/` |
| `web/` | `scripts/` | `PROGRESS.md` (append, don't rewrite) |

---

## Locked decisions

Neither of us re-opens these without a conversation. Add the date and a one-line reason when you add a row.

| Date | Decision | Why |
|---|---|---|
| 2026-08-23 | **Method: Sensitivity of the System, via Monte Carlo rollout of a fitted twin, with Bottleneck Walk as the cheap prefilter** | The 2023 systematic review rates it best; its only stated shortcoming is that it needs counterfactuals, which is the one thing we already have |
| 2026-08-23 | **Twin is fitted from the event stream, never from `PlantConfig`** | Initialising from the generator's true parameters makes the twin identical to the plant, and the result meaningless |
| 2026-08-23 | **Headline metric is regret + calibration, not top-1 accuracy** | Top-1 punishes correct behaviour on the 35.7% of blocks where no station dominates |
| 2026-08-23 | **Parameter schema is fixed across all lines; only the adapter, fitted values and thresholds vary** | If features change per line we have N products, not one, and the scaling claim dies |
| 2026-08-23 | **Window sizes defined in units, not seconds** | A 30-min window holds 30 units at 60s takt and 50 at 35s takt — a hidden per-line constant |
| 2026-08-23 | **Twin advises, never writes to line control** | Writing to safety-certified control is a regulated change no plant grants a prototype |
| 2026-08-23 | **Operator variation excluded on ethical grounds** | Measure the station, never the person. State it out loud rather than leaving it silent |
| 2026-08-23 | **UI follows ISA-101: grayscale base, colour only for deviation** | A visually quiet screen is what a real plant HMI looks like; supervisor view only, leadership view may use colour |

---

## Known defects carried from Round 1 — fix before building on top

| # | Defect | Where | Owner | State |
|---|---|---|---|---|
| 1 | `test_speedup_never_hurts_much` fails — RNG desync in the global `speed_scale` path. Delete `speed_scale` and correct the docstring that claims speed perturbation "changes no other draw" | `src/twin/plant.py` | Priyansh | `todo` |
| 2 | **"46% / 58%" is the active-period (Roser 2001) number, quoted as ours.** Ours is 43.1% / 59.4%. Re-anchor on regret, where we genuinely win: 1.309 vs 1.348 vs 1.477 | deck, `1_Guide` | Priyansh | `todo` |
| 3 | Evidence file attaches the **all-blocks** ceiling (2.271) to the **strong-constraint** table. Real ceiling there is 5.255, capture 57.4% — better than the 45% claimed | Evidence File §4 | Priyansh | `todo` |
| 4 | `Verdict.forming` still computes `gap / drift_rate` — the mechanism we measured at 5.9% and publicly declared failed. Must not reach the live emit path | `detect.py:238` | Sagar | `todo` |
| 5 | `drift_cusum` is recomputed fresh each window — a scaled z-score, not a CUSUM. Needs to carry state across windows | `detect.py:203` | Sagar | `todo` |
| 6 | Stage 6 says down-weight candidates by starved share; `verdict()` sorts on `effective_ct` alone | `detect.py` | Sagar | `todo` |
| 7 | `confidence` is asserted from margin and unit count, which violates our own Part 4.1 ("calibrated, not asserted") | `detect.py:249` | Sagar | `todo` |
| 8 | `results/eval_v5_chained.log` records a `ZeroDivisionError` crash from before the zero-width-window guard. Confirm the published 958-block CSV came from a clean post-fix run, then remove the stale log | `results/` | Priyansh | `todo` |
| 9 | Every published rate needs `n` and a Wilson interval. The overtake failure rests on n=17 | all docs | Priyansh | `todo` |

---

## Gaps against the Round 2 brief

Ticked when the artifact exists, not when it's designed.

- [ ] The loop — ingest, detect, rank, emit on a timer *(no artifact exists)*
- [ ] Web prototype, three views
- [ ] **Genealogy containment** — the most explicitly-named capability in the brief that we don't have
- [ ] Alert ledger — the answer to "false alarms erode floor-level trust"
- [ ] Observability map as software (drop the ILLUSTRATIVE label)
- [ ] 40 stations across body / paint / final, with sensor coverage varying **by segment**
- [ ] Failure-mode classifier fitted on ratios, scored on the Wiener firewall set
- [ ] Manual-checklist event type — the brief names it explicitly
- [ ] Equipment-vintage cohorts as a second axis alongside layout
- [ ] Runtime telemetry — loop latency, rollout replications, cost per decision
- [ ] Layout transfer on L1–L4 *(code exists, never run)*
- [ ] Sensor-maturity transfer — `Detector(run, use_states=False)` *(one flag, never run)*
- [ ] Noise floor across ~50 seeds
- [ ] Business case / ROI computed from our own outputs
- [ ] Phased roadmap
- [ ] Sensor retrofit plan phased by maintenance window
- [ ] Pitch deck rebuilt around the prototype

---

## Open questions — need a joint decision

| Q | Raised by | Status |
|---|---|---|
| Web stack: FastAPI + SSE, or Streamlit? | — | open |
| How many rollout replications `N` before it's too slow to demo at 60x? | — | open |
| Do we regenerate v5 with biased dark placement, or ship localisation as designed-not-validated? | — | open |
| Dataset storage — 765 MB is gitignored; where does it live so we both have the same bytes? | — | open |

---

## Blockers

_None yet. Add here the moment something stops you — don't wait for the checkpoint._

| Date | Who | Blocked on | Needs |
|---|---|---|---|
| | | | |

---

## Working agreement

- **Branches:** `sagar/<thing>`, `priyansh/<thing>`. Never commit directly to `main`.
- **Update this file** in the same PR as the work it describes.
- **The Right now block** gets updated before you stop for the day, even if nothing moved. "No progress, stuck on X" is a useful entry.
- **Locked decisions** are append-only. If you disagree with one, raise it in Open questions rather than editing the row.
- **Datasets are gitignored.** Regenerate with the seeded builders in `scripts/` — fixed seeds, so we get identical bytes. Budget ~2h for the full v5 truth build.
- **Every number in a doc** is either ours with a named source file, or literature with a named reference. If it is neither, it does not appear.
- **Negative results get reported at the same prominence as positive ones.** This is our strongest asset in a mentored Round 3.

---

## Reference

| Doc | Where |
|---|---|
| Full pipeline design (source of truth) | `4_Design_Documents/DigitalTwin_Three_Pipelines.pdf` |
| Per-claim provenance | `4_Design_Documents/DigitalTwin_Evidence_File.pdf` |
| Model parameter tables | `DigitalTwin_Model_Parameters.pdf` |
| Official Round 2 brief | `4_Design_Documents/Round2_Problem_Statements.pdf` |
| Round 1 codebase | `github.com/sagar2907/HipHipHooray_DigitalTwin.ai` |
