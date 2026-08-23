# PROGRESS

**Repo:** `HipHipHooray_IIT_Kharagpur_DigitalTwin.ai_Prototype`
**Team:** Sagar Sahu (`@sagar2907`) · Priyansh Goyal (`@Priyansh0704`)
**Accenture Innovation Challenge 2026 — Problem Statement 4, Round 2**

> **Both of us write to this file, and everything we do on this project lands here.**
> It is the one place either of us can look to know what the other has done, what is
> locked, and what is blocked.
>
> **The rule — no work is finished until this file reflects it:**
> 1. Add a **Work log** line — one line, what changed and why it matters
> 2. Update the **Timeline** with the date
> 3. Move the **Status board** row if a workstream advanced
> 4. Update **Right now** before you stop for the day
>
> Do all four **in the same commit as the work itself**. Keep it summarised — detail
> belongs in the commit message, not here.

---

## Timeline

**Round 2 deadline:** _(set this — everything below hangs off it)_

```
  A ──▶ B ──▶ C ──▶ D ──▶ E ──▶ F ──▶ G
  ▲
  we are here — setup done, nothing built yet
```

| Date | Milestone | Who | State |
|---|---|---|---|
| 2026-08-17 | Round 1 codebase frozen — 9 commits, last commit | Sagar | `done` |
| 2026-08-21 | Handover pack assembled | Priyansh | `done` |
| 2026-08-23 | Prototype repo created; full Round 1 archive committed | Priyansh | `done` |
| 2026-08-23 | Parameter contract locked — 51 bottleneck + 37 defect fields | Priyansh | `done` |
| 2026-08-23 | `PROGRESS.md` live; both suggestion folders filed (12 + 5 proposals) | Both | `done` |
| 2026-08-23 | Timeline added; updating this file made a standing rule | Priyansh | `done` |
| _tbd_ | **A** — Clear the ground | Priyansh | `todo` |
| _tbd_ | **B** — The loop *(essential — never cut)* | Sagar | `todo` |
| _tbd_ | **C** — Alert contract + trust ledger | Sagar | `todo` |
| _tbd_ | **D** — 40 stations + transfer tests | Priyansh | `todo` |
| _tbd_ | **E** — Three stakeholder views | Both | `todo` |
| _tbd_ | **F** — Genealogy + stop-or-continue | Both | `todo` |
| _tbd_ | **G** — Business case + deck | Both | `todo` |
| _tbd_ | **Submission** — proposal, prototype, pitch | Both | `todo` |

Move the `▲` marker as workstreams complete. Fill the `_tbd_` dates once the deadline is set.

---

## Right now

_Last updated: 2026-08-23 by **Sagar**_

| | Working on | Branch | ETA | Blocked by |
|---|---|---|---|---|
| **Sagar** | reviewed repo + Priyansh's audit; filed `suggestion_by_sagar/`; **B (the loop)** not yet started | — | — | — |
| **Priyansh** | repo seeded; next is **A (clear the ground)** | `main` | — | — |

**Next joint checkpoint:** _(set a date)_

**Sagar, start here:** `START_HERE.txt` → `4_Design_Documents/DigitalTwin_Three_Pipelines.pdf`
(source of truth, not the old README) → `DigitalTwin_Model_Parameters.pdf` (what feeds the model).

---

## Work log

Append-only, newest first. Both of us add to this.

| Date | Who | What changed | Commit |
|---|---|---|---|
| 2026-08-23 | Priyansh | Added the **Timeline** section and made it a standing rule that every piece of work updates this file in the same commit. | — |
| 2026-08-23 | Sagar | Added `suggestion_by_sagar/` — 5 proposals: cite Turning Point Method (blocked/starved signature is prior art), add IoU as a second scoring axis, ARIMA-forecast spike as a candidate for B after its gate is green, ISO 22400 vocabulary for the leadership view, closed the old prototype-placeholder note | `fdf5f7c` |
| 2026-08-23 | Priyansh | Added `suggestion_by_priyansh/` — 12 proposals for Sagar to review, with a response table. Sagar's equivalent folder to follow. | `8e747e2` |
| 2026-08-23 | Priyansh | Committed the full Round 1 archive. **Repo is now the single source of truth**; the Desktop handover folder is a copy. | `d843ba8` |
| 2026-08-23 | Priyansh | Added `DigitalTwin_Model_Parameters.pdf` — 51 bottleneck + 37 defect parameters with explanations. Agree changes to it before coding against it. | `d843ba8` |
| 2026-08-23 | Priyansh | Created this file. | `f7a4860` |

---

## Status board

`todo` · `wip` · `review` · `done` · `blocked` · `cut`

| # | Workstream | Owner | State | Gate |
|---|---|---|---|---|
| **A** | Clear the ground | Priyansh | `todo` | 11/11 tests green; noise floor published; 2 doc errors fixed |
| **B** | The loop (`record.py`, `loop.py`) | Sagar | `todo` | A shift replays at 60x in a browser, from a loop that never sees `t > now` |
| **C** | Alert contract + trust ledger | Sagar | `todo` | Every alert carries all 5 fields; calibration within ±10 pts; ledger shows running precision |
| **D** | 40 stations + transfer tests | Priyansh | `todo` | Layout-transfer number, sensor-maturity number, classifier scored on firewall set |
| **E** | Three stakeholder views | Both | `todo` | Three views, one record stream, switchable live |
| **F** | Genealogy + stop-or-continue | Both | `todo` | Same drifting tool, opposite correct answers by flow state |
| **G** | Business case + deck | Both | `todo` | 5-minute walkthrough runnable without touching a script |

**If time runs short, cut F first, then D, then E. Never B.**

---

## Who owns which files

Don't edit outside your column without saying so in **Right now** first.

| Sagar | Priyansh | Shared — announce first |
|---|---|---|
| `src/twin/loop.py` | `src/twin/plant.py` | `src/twin/detect.py` |
| `src/twin/record.py` | `src/twin/layouts.py` | `src/twin/events.py` |
| `src/twin/alerts.py` | `src/twin/dark.py` | `tests/` |
| `web/` | `scripts/` | `PROGRESS.md` (append, don't rewrite) |

---

## Locked decisions

Append-only. Disagree? Raise it in **Open questions** — don't edit the row.

| Date | Decision | Why |
|---|---|---|
| 08-23 | Method: **Sensitivity of the System via Monte Carlo rollout of a fitted twin**, Bottleneck Walk as prefilter | 2023 systematic review rates it best; its only stated shortcoming is needing counterfactuals, which we already have |
| 08-23 | Twin fitted **from the event stream, never from `PlantConfig`** | Using the generator's true parameters makes the twin identical to the plant — result is meaningless |
| 08-23 | Headline metric is **regret + calibration**, not top-1 accuracy | Top-1 punishes correct behaviour on the 35.7% of blocks where nothing dominates |
| 08-23 | **Parameter schema fixed across all lines**; only adapter, fitted values and thresholds vary | Features changing per line means N products, not one — the scaling claim dies |
| 08-23 | Window sizes in **units, not seconds** | 30 min holds 30 units at 60s takt, 50 at 35s takt — a hidden per-line constant |
| 08-23 | Twin **advises, never writes** to line control | Writing to safety-certified control is a regulated change no plant grants a prototype |
| 08-23 | **Operator variation excluded** on ethical grounds | Measure the station, never the person — and say so out loud |
| 08-23 | UI follows **ISA-101**: grayscale base, colour only for deviation | Supervisor view only; leadership view may use colour |

---

## Defects carried from Round 1 — fix before building on top

| # | Defect | Where | Owner | State |
|---|---|---|---|---|
| 1 | `test_speedup_never_hurts_much` fails — RNG desync in `speed_scale`. Delete it, fix the docstring that claims speed perturbation "changes no other draw" | `plant.py` | Priyansh | `todo` |
| 2 | **"46% / 58%" is Roser's active-period number, quoted as ours.** Ours is 43.1% / 59.4%. Re-anchor on regret: 1.309 vs 1.348 vs 1.477 | deck, `1_Guide` | Priyansh | `todo` |
| 3 | Evidence File puts the all-blocks ceiling (2.271) on the strong-constraint table. Real ceiling 5.255, capture 57.4% — better than claimed | Evidence File §4 | Priyansh | `todo` |
| 4 | `Verdict.forming` still computes the drift extrapolation we measured at 5.9% and declared failed | `detect.py:238` | Sagar | `todo` |
| 5 | `drift_cusum` recomputed each window — a z-score, not a CUSUM. Must carry state | `detect.py:203` | Sagar | `todo` |
| 6 | Design says down-weight by starved share; `verdict()` sorts on `effective_ct` alone | `detect.py` | Sagar | `todo` |
| 7 | `confidence` is asserted, violating our own Part 4.1 ("calibrated, not asserted") | `detect.py:249` | Sagar | `todo` |
| 8 | `eval_v5_chained.log` shows a crash pre-dating the zero-width guard. Confirm the 958-block CSV came from a clean run, then delete the log | `results/` | Priyansh | `todo` |
| 9 | Every published rate needs `n` and a Wilson interval — the overtake failure rests on n=17 | all docs | Priyansh | `todo` |

---

## Gaps against the brief

Tick when the artifact exists, not when it's designed.

- [ ] The loop — ingest, detect, rank, emit on a timer
- [ ] Web prototype, three views
- [ ] **Genealogy containment** — the most explicitly-named capability we don't have
- [ ] Alert ledger — answers "false alarms erode floor-level trust"
- [ ] Observability map as software (drop the ILLUSTRATIVE label)
- [ ] 40 stations across body/paint/final, coverage varying **by segment**
- [ ] Failure-mode classifier on ratios, scored on the Wiener firewall set
- [ ] Manual-checklist event type — the brief names it explicitly
- [ ] Equipment-vintage cohorts as a second axis alongside layout
- [ ] Runtime telemetry — loop latency, replications, cost per decision
- [ ] Layout transfer L1–L4 *(code exists, never run)*
- [ ] Sensor-maturity transfer — `use_states=False` *(one flag, never run)*
- [ ] Noise floor across ~50 seeds
- [ ] Business case computed from our own outputs
- [ ] Phased roadmap
- [ ] Sensor retrofit plan phased by maintenance window
- [ ] Deck rebuilt around the prototype

---

## Open questions — need both of us

| Q | Raised by | Status |
|---|---|---|
| Web stack: FastAPI + SSE, or Streamlit? | — | open |
| How many rollout replications before it's too slow to demo at 60x? | — | open |
| Regenerate v5 with biased dark placement, or ship localisation as designed-not-validated? | — | open |
| Where do the 765 MB of datasets live so we both have identical bytes? | — | open |

---

## Blockers

Add the moment something stops you — don't wait for the checkpoint.

| Date | Who | Blocked on | Needs |
|---|---|---|---|
| | | | |

---

## Working agreement

- **Branches:** `sagar/<thing>`, `priyansh/<thing>`. No direct commits to `main`.
- **Update this file in the same PR** as the work it describes.
- **Suggestions** go in `suggestion_by_priyansh/` and `suggestion_by_sagar/`, not here.
  Once a suggestion is agreed, it moves into **Locked decisions** or the **Status board**.
- **Datasets are gitignored.** Regenerate from the seeded builders in `scripts/` — fixed
  seeds, identical bytes. ~2h for the full v5 truth build. Don't commit large binaries;
  the ~30 MB already in history is enough.
- **Every number** is either ours with a named source file, or literature with a named
  reference. Otherwise it doesn't appear.
- **Negative results get equal prominence.** It's our strongest asset in a mentored Round 3.

---

## Repo map

| Path | What |
|---|---|
| `PROGRESS.md` | This file — canonical |
| `DigitalTwin_Model_Parameters.pdf` | Every parameter fed to the model |
| `suggestion_by_priyansh/` · `suggestion_by_sagar/` | Proposals for the other to review |
| `1_Guide/` | What is built, designed, and failed |
| `2_Plan/` | Original Round 2 plan — superseded on sequencing by the status board |
| `3_Round1_Submission/` | Deck, PDF, pitch video as submitted |
| `4_Design_Documents/` | **Source of truth** — Three Pipelines, Evidence File, official brief |
| `5_Animation_Sources/` | HTML animations, captioned MP4, result figures |
| `6_Code/` | Round 1 snapshot. Live: `github.com/sagar2907/HipHipHooray_DigitalTwin.ai` |
| `7_Prototype/` | Round 2 prototype work |
