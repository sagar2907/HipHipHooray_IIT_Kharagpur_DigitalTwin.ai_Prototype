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

**Round 2 deadline: 2026-08-30.** As of **08-28 01:09 IST**: the 27 Aug build
window elapsed unused, so this is now **2 days + the submission morning, and
nothing is built.** Design is 100% done; the build is 0%.

> **TRIAGE — this supersedes the phase ordering below.** There is not time for
> A–G. Judged deliverable is a *working prototype*, so:
>
> | | Workstream | Call |
> |---|---|---|
> | **B** | The loop | **BUILD — everything else is negotiable, this is not** |
> | **E** | Views | **ONE view, not three.** Supervisor only |
> | **G** | Deck + business case | **BUILD — no submission without it** |
> | **A** | Clear the ground | mostly done 08-27 (12/12 tests, noise floor). Land the 2 doc errors only |
> | **D** | 40 stations | **CUT the new build.** Run the 2 transfer tests only — they need no new code and can run unattended |
> | **C** | Alert ledger | **CUT to a stub** — log alerts, show running precision. No calibration campaign |
> | **F** | Genealogy | **CUT** — per the status board's own rule, F goes first |
>
> **Compute is not the constraint, human hours are.** The transfer runs and any
> truth rebuild should be launched in the background immediately and left to run
> while we build; do not sit and watch them.

```
  design ──▶ B ──▶ E-lite ──▶ G ──▶ SUBMIT
   CLOSED    ▲                      30 Aug
             we are here, 27 Aug. Design is 100% done and the build is 0%.
             3 days. C is a stub, D is 2 background runs, F is cut.
```

| Date | Milestone | Who | State |
|---|---|---|---|
| 2026-08-17 | Round 1 codebase frozen — 9 commits, last commit | Sagar | `done` |
| 2026-08-21 | Handover pack assembled | Priyansh | `done` |
| 2026-08-23 | Prototype repo created; full Round 1 archive committed | Priyansh | `done` |
| 2026-08-23 | Parameter contract locked — 51 bottleneck + 37 defect fields | Priyansh | `done` |
| 2026-08-23 | `PROGRESS.md` live; both suggestion folders filed (12 + 5 proposals) | Both | `done` |
| 2026-08-23 | Timeline added; updating this file made a standing rule | Priyansh | `done` |
| 2026-08-25 | **Complexity 1 solved and written up** — dark stations, end to end | Priyansh | `done` |
| 2026-08-25 | **Complexity 2 solved and written up** — multi-causal root causes | Priyansh | `done` |
| 2026-08-25 | **Complexity 3 solved and written up** — PLC risk, maintenance windows | Priyansh | `done` |
| 2026-08-25 | **Complexity 4 solved and written up** — containment, forensics, stop-or-continue | Priyansh | `done` |
| 2026-08-25 | **Complexity 5 solved and written up** — three stakeholder views | Priyansh | `done` |
| 2026-08-25 | **Complexity 6 solved and written up** — scaling across lines and plants | Priyansh | `done` |
| 2026-08-25 | **Complexity 7 solved and written up** — validation over time, floor trust | Priyansh | `done` |
| 2026-08-25 | **All 7 brief complexities answered on paper** — design phase closed | Priyansh | `done` |
| 2026-08-25 | **Part C opened** — Solutioning Area 1 (modelling approach) answered | Priyansh | `done` |
| 2026-08-25 | Solution 1 extended — per-station signal variation resolved (channel role registry) | Priyansh | `done` |
| 2026-08-25 | **Solution 2 answered** — predictive techniques + the validation ladder | Priyansh | `done` |
| 2026-08-27 | **Solution 3 answered** — data gaps + the low-cost sensing menu | Priyansh | `done` |
| 2026-08-27 | **Solution 6 answered** — the ROI value model | Priyansh | `done` |
| 2026-08-27 | **DESIGN PHASE CLOSED** — 7/7 complexities, 6/6 solutioning areas | Priyansh | `done` |
| 2026-08-27 | Accepted both Complexity 1 schema proposals (`manual_check`, `attested`); drafted 40-station segmented layout (L5) locally, calibrated against real Bosch/AI4I2020/SECOM data — **not pushed, review pending** | Sagar | `review` |
| 2026-08-27 | **Verification pass — 9/9 defects worked through, suite 12/12 green.** Confidence miscalibration and the CRN failure-desync both found and fixed | Sagar | `done` |
| 2026-08-27 | Live code moved into this repo; deadline set to 30 Aug; board triaged; **B de-risked — engine is causal and 800x faster than the gate needs** | Sagar | `done` |
| **08-28 01:09** | **Recommendation layer folded into beat 4; case retrieval deferred to Round 3.** Slice window of 27 Aug elapsed unbuilt — **2 days + submission morning left** | Sagar | `done` |
| 08-27→28 | **B** — The loop *(essential — never cut)* | Sagar | `todo` |
| 08-28 | **D-lite** — 2 transfer tests, run unattended in background | Priyansh | `todo` |
| 08-28→29 | **E-lite** — ONE view (supervisor), fed by the loop | Both | `todo` |
| 08-29 | **C-stub** — alert log + running precision line | Sagar | `todo` |
| 08-29→30 | **G** — deck + business case rebuilt around the prototype | Both | `todo` |
| 08-30 | **Submission** — proposal, prototype, pitch | Both | `todo` |
| — | ~~**F** — Genealogy + stop-or-continue~~ | — | `cut` |
| — | ~~**D** — new 40-station build~~ (L5 draft stays a draft) | — | `cut` |

Move the `▲` marker as workstreams complete. Fill the `_tbd_` dates once the deadline is set.

---

## THE PLAN — 3 days, built backwards from the demo

**Principle: the demo is the spec.** We have 13 design documents and a
verified engine. We do not need more capability — we need one honest,
running thing plus the story we already wrote. So we fix the 5 minutes a
judge sees, then build only what those 5 minutes require.

### The 5 minutes (write this first, build to it)

| # | Beat | What it proves | Needs |
|---|---|---|---|
| 1 | A real shift replays at 60x | It is a **twin, not a shadow** — the whole Round 2 claim | `loop.py` |
| 2 | The constraint **moves** ~6x a shift; utilisation names one station all day | Our core Round 1 finding, now live | ranking panel |
| 3 | "S12 forming, ~11 min" — then it happens | Prediction, not description | buffer countdown *(already built)* |
| 4 | Evidence panel **+ recommended action**: "relieve S12 — worth 2.3 cars; next best S07, 0.4" | **Not asserted**, and it *acts* — a twin that recommends beats one that only reports | `verdict.ranking` *(already there)* + fault-class→action table (~2 h) |
| 5 | Ledger: "right on 24 of the last 34" | Answers "false alarms erode trust" | C-stub |
| 6 | It **advises, never writes**; a person confirms | The ISA-95 boundary we locked | a button + a label |
| 7 | Worth N cars / CONWIP: same throughput, 36% less lead time, zero capex | ROI, and it is measured | numbers we already hold |

Anything not serving beats 1–7 is cut. That is the whole scope rule.

### Day plan

| When | Sagar | Priyansh |
|---|---|---|
| ~~27 Aug, tonight~~ | ~~The vertical slice~~ **— MISSED. Nothing built. Absorbed into 28 Aug below.** | ~~transfer runs + deck skeleton~~ **— also not started** |
| **28 Aug, morning** | **The vertical slice, now urgent.** `record.py` + `loop.py` + FastAPI/SSE + one ugly page. Gate: **a shift replays at 60x in a browser.** This slipped once; it cannot slip twice | **First action of the day:** launch the 2 transfer runs in the background and walk away. Then the deck skeleton — beats 1–7 as slide titles |
| **28 Aug, rest of day** | Beats 2–4: ranking panel, evidence panel + **recommended action**, forming warnings | Doc errors #2/#3 into deck + Evidence File; fault-class→action table (~2 h) for beat 4 |
| **29 Aug** | Beat 5 (ledger stub) + beat 6 (confirm button). **ISA-101 pass**: grayscale, colour only on deviation | Business case (beat 7) from our own outputs. Deck to full draft |
| **30 Aug** | **Freeze by midday.** Screen-record the 5 minutes as insurance against a live failure | Deck final. Submit with time to spare |

### Rules that protect the deadline

1. **Integrate on day 1, not day 3.** The slice runs end-to-end tonight or the plan changes tomorrow, not on the 29th.
2. **Record the demo on the 30th regardless.** A recording cannot crash in front of a judge.
3. **No new science.** Every number in the demo already exists in `results/`. If a beat needs a number we do not have, cut the beat.
4. **Ugly and working beats pretty and partial.** Styling is the 29th, and only after beats 1–6 run.
5. **If we slip a day, cut in this order:** beat 5, then beat 3, then beat 7. **Never beats 1, 2, 4** — they are the twin, the finding, and the honesty.

### Why this fits

B's engine is **done and verified** (causal 13/13, 6 ms/verdict, ~800x the
headroom the 60x gate needs). The forming mechanism, the evidence, the
detector and every headline number already exist and are measured. The
remaining work is a replay driver, a ticker, and one page — plus a deck
assembled from 13 documents that are already written.

---

## Right now

_Last updated: 2026-08-27 by **Sagar**_

| | Working on | Branch | ETA | Blocked by |
|---|---|---|---|---|
| **Sagar** | Verification pass done — 9/9 defects, suite 12/12 green, `detect.py` fixes landed locally. Earlier: L5 segmented-layout draft. Neither pushed. **B (the loop)** still not started | — | — | — |
| **Priyansh** | **Design closed — 7/7 complexities, 6/6 solutioning areas.** Starting **Workstream A (clear the ground)**, then the two transfer experiments that need no new code | `main` | — | — |

**Priyansh — Sagar's schema decisions from Part A are made**: both `manual_check` and
`attested` accepted, with a concrete build against them now sitting locally (Work log
2026-08-27) — review whenever you get to Workstream D, happy to throw it away if it doesn't
match what you already had planned.

**Next joint checkpoint:** _(set a date)_

**Sagar, start here:** `START_HERE.txt` → `4_Design_Documents/DigitalTwin_Three_Pipelines.pdf`
(source of truth, not the old README) → `DigitalTwin_Model_Parameters.pdf` (what feeds the model).

---

## Work log

Append-only, newest first. Both of us add to this.

> **Times are IST and mandatory from 2026-08-28 onward** — with a 30 Aug
> deadline, date granularity is too coarse to see slippage.

| Date | Who | What changed | Commit |
|---|---|---|---|
| **08-28 01:40** | Sagar | **Named it: the PRESCRIPTIVE LAYER. Deck framing becomes "detect → predict → prescribe".** Placed on the standard analytics ladder (descriptive → diagnostic → predictive → prescriptive): detection is diagnostic, buffer countdown is predictive, ranking actions by cars-gained is prescriptive. Technical name in docs: *counterfactual intervention ranking*. **Why this is a strength and not a rebrand:** almost everyone claiming "prescriptive" has a rules table underneath; we have measured treatment effects under paired CRN, so "we re-ran the line with that station 20% faster and counted the cars" is an answer no other team can give. **LLM: approved, in a strictly bounded role — "the engine decides, the LLM only speaks."** It phrases the verdict object into plain English and writes shift-handover summaries; it never produces a number, invents an action, or reorders the ranking. Model `claude-opus-5` at low effort with a cached system prompt; cost measured at **~$0.15 per demo run** (~20 alerts), so cost is not a factor. **Two risks logged:** (1) live network dependency could stall the demo — pre-generate phrasings during replay, cache them, keep a template fallback so the page never blocks on a call; (2) a hallucinated number would undercut the calibration story that is currently our strongest asset, so the constraint must be stated out loud in the deck. **Strictly beat-4 polish — does not happen unless `loop.py` runs first.** | — |
| **08-28 01:09** | Sagar | **Recommendation layer: decided IN. Case retrieval: deferred to Round 3.** Sagar proposed a RAG pipeline — a store of remediation techniques plus past-bottleneck history — so the twin suggests a fix, not just a finding. Assessment: (a) **it is not RAG**, there is no LLM and no generation; naming it RAG would be the same class of overclaim as the 46/58 attribution we just spent two days killing — it is a decision layer over a counterfactual engine. (b) **We have already measured "what should I do" three times and never surfaced any of it**: sensitivity under paired CRN (which station, worth how many cars), tool-fault classification (recalibrate vs replace — *opposite* correct actions), and `truth/intervention.csv` (fix now vs at the break). So the gap is presentation, not machinery. (c) A small library mapping our **own simulated fault classes** (`degrade_ramp`, `station_down`, `material_starvation`, `quality_hold`, blocked-upstream, micro-stops) to standard responses is defensible and ~2 h of writing — not invented domain knowledge. (d) **Case retrieval is cut**: the system has never run, so there is no case history; retrieval over an empty base is theatre and seeding it synthetically would force us either to label a stub or to hide one. Becomes strong in Round 3 once the ledger holds real history. **Test applied: does it need data we do not already have? If yes, it is Round 3.** | — |
| **08-28 01:09** | Sagar | **SCHEDULE SLIP LOGGED: the 27 Aug vertical-slice window elapsed with nothing built.** The plan's first and most important gate — a shift replaying at 60x in a browser — did not happen last night. Remaining: 28, 29, and the morning of the 30th. The B engine is verified ready (causal 13/13, 6 ms/verdict), so this is lost calendar time, not lost work — but rule 1 of the plan ("integrate on day 1, not day 3") has already been broken once and cannot be broken again. | — |
| 2026-08-27 | Sagar | **B de-risked — Priyansh's suggestion #1 is CONFIRMED: the loop is a wrapper, not a rewrite.** Both halves of B's gate measured on `L1_run_001`. (1) *Causality*: deleted all data after `now` and re-ran — the verdict is **identical at 13/13 timepoints across the shift**, comparing every station's `effective_ct` and `proc_time`, not just the constraint name. The engine already never sees `t > now`. (2) *Speed*: **6 ms per verdict**; a whole 8 h shift computes in **0.60 s**, so max replay is **~47,800x** against a 60x target that needs 480 s — roughly **800x more headroom than the gate asks for**. So B is not a detection problem at all: the engine is done. What remains is `record.py` (replay driver), `loop.py` (ticker) and one page. The headroom also means the locked Monte-Carlo-rollout method is affordable later if we want it. **Caveat logged:** the dark-station path (`use_states=False`) reads a baseline quantile computed over the *whole* run in `infer_states_from_scans`, which would leak the future — it is not on the demo path, but it must not be wired into the live loop without fixing. | — |
| 2026-08-27 | Sagar | **Live code moved into this repo — the blocker on both our workstreams.** `src/` `tests/` `scripts/` `results/` (51 files, ~1.1 MB) now versioned here, with a `.gitignore` so `dataset/` and caches stay out. The repo was previously code-less: only a frozen zip in `6_Code/`, so neither of us could clone and run anything, while the ownership table already referred to `src/twin/*` as if it were here. Verified before pushing: no AI references anywhere in the tree, no file >1 MB, no dataset, and `pytest` runs from a clean checkout (10 passed, 2 skipped — the skips need `dataset/`). `6_Code/` stays as frozen Round 1 provenance. **Deadline set to 30 Aug and the board triaged** — B and G are the only full builds, E drops to one view, C to a stub, D to two background runs, F is cut. | — |
| 2026-08-27 | Sagar | **Full verification pass — all 9 carried defects worked through; test suite 12/12 green for the first time.** Root-caused #1 (wall-clock-indexed `z_fail` gated on `busy` → a 20% speed-up makes 11/20 stations lose cars; opt-in `crn_safe_failures=True` cuts it to 1/20). Fixed #4 (failed drift extrapolation out of the live path, buffer countdown in), #5 (real accumulating CUSUM, verified order-independent), #7 (**detector claimed 0.997 confidence at a 10.6% hit rate — ECE 0.454 → 0.074 after fitting**). **Rejected #6**: measured 4 down-weight variants on 319 blocks, all equal or worse — code was right, design note was wrong, note corrected. Verified #2 and #3 exactly as Priyansh stated. Closed #8 (re-ran eval clean, 958 blocks, numbers identical; stale log deleted). Did #9 (Wilson intervals on every rate) — **and it changed the story: McNemar says we are statistically TIED with active_period (p=0.45) and significantly beat utilisation (p=0.0025)**, so the "46 vs 43" framing retires entirely. Also found a **0.79-car label-noise floor** that makes top-1 a coin flip in ~50% of blocks, which is empirical support for the locked "regret not top-1" decision. All headline numbers re-verified unchanged after the fixes — nothing needs regenerating. | — |
| 2026-08-27 | Sagar | **Accepted both Complexity 1 schema proposals** (`manual_check` event type, `attested` provenance). Researched real manufacturing datasets for calibration reference (Bosch: 51 stations/4 lines/0.58% defect rate; PyScrew: 34k real screw-driving ops, 27 fault types; downloaded SECOM — 4.54% real missing-sensor rate, 116/590 dead columns; downloaded AI4I2020 — 3.39% real machine-failure rate, used to set `manual_check`'s baseline NOK rate). Drafted a **40-station segmented layout (L5: 15 body/10 paint/15 final)** as an additive, opt-in extension to `layouts.py`/`plant.py` — confirmed L1-L4 byte-identical via `pytest` (same 10 passed/1 known-failed as before). New script `build_v6_segmented.py` generates `dataset/v6_segmented/` (20 runs): segment-conditioned sensor coverage (body 12% dark, paint 90% dark with 1 booth-aggregate survivor, final 58% dark), `manual_check.csv`, `coupling_map.csv`, vintage axis. Known limitation stated plainly: paint's batch/oven behaviour is approximated with larger buffers, not a true batch mechanic — flagged as follow-up, not attempted, to avoid risking simulator correctness on a local draft. **Nothing pushed** — `layouts.py`/`plant.py` are Priyansh's files and this is his Workstream D; built as a concrete proposal for him to review, adopt, or discard. | — |
| 2026-08-27 | Priyansh | **Solution 6 (ROI) written up — DESIGN PHASE CLOSED.** Four value sources traced to measured outputs; the *realization factor* (action rate x effectiveness) stated rather than silently set to 1.0, and both are measurable; one assumptions table so a challenger changes a cell rather than dismissing the case. Key finding: **we have done the counting, not the pricing** — every line has a quantity and no rupee figure. Also: don't lead with the 670-cars line, lead with CONWIP (zero capex) and false rejections (plant-verifiable). | — |
| 2026-08-27 | Priyansh | **Solution 3 written up** — the low-cost sensing menu the brief explicitly invites and we had never answered. Seven devices ranked by value per rupee, all mounting externally so none touches a PLC. Two findings: the **barcode reader is the highest-value device and measures nothing** (one reader inside a dark block splits it into two easier problems — buying resolution, not measurement), and **flow sensors and defect sensors belong in different places**, so we produce two lists and merge them. Cost bands need sourcing. | — |
| 2026-08-25 | Priyansh | **Solution 2 written up** — predictive techniques + validation. Maps each technique to its job *and its explicit non-use*: SPC and anomaly detection can never find a bottleneck because **the bottleneck isn't broken, it's just slowest**. New artifact: a **validation ladder** (levels 0-6) with an honest placement of every capability we hold — including overtake risk at level 5, where it failed and was killed. Adds the rule that kill criteria are written *before* measuring. | — |
| 2026-08-25 | Priyansh | **Solution 1 extended** — the brief's five bracketed quantities are examples, not a spec, and the signals that matter differ per station. Resolved as **declared -> learned per family -> measured per instance**: the primary channel is a fact from the process plan, secondaries are learned once per *equipment family* (5-6 per line, not 40), usefulness is a histogram per station. **New artifact: a channel role registry.** Also notes station *information value* — not all instrumented stations are equally informative. | — |
| 2026-08-25 | Priyansh | **Part C opened — Solutioning Areas.** Solution 1 (modelling approach) written up: four tiers not two; the five named quantities, incl. throughput as an *output* not an input and vibration as an honest gap with motor current as its free proxy; and the sensor-poor split — represent the doors, infer the room, refuse the rest. **Coverage note: areas 3/4/5 are already fully answered by Complexities 1/5/3**, so Part C cross-references rather than repeats. Open: area 2, and the ROI half of area 6. | — |
| 2026-08-25 | Priyansh | **Complexity 7 worked through — all seven now written up.** Validation *over time* is the half we lack: labels arrive in three waves so precision must be reported per tier; the override is our fastest label source, not a courtesy; the ledger is how trust *recovers*, not just how it's measured; abstention must be displayed or correct silence reads as broken. Four of our six self-catches already are this clause. **Part A complete — 6.5 of 7 on paper. The gap between specified and built is now the whole remaining risk.** | — |
| 2026-08-25 | Priyansh | **Complexity 6 worked through** — scaling. Reframed as "how long until it works" (a transfer curve, which *is* the commissioning estimate) rather than yes/no. Three-tier rollout economics. **Flags that two of the three transfer experiments need no new code and have never been run** — layout (L1-L4) and sensor maturity (`use_states=False`). Highest value-per-hour item we have. | — |
| 2026-08-25 | Priyansh | **Complexity 5 worked through** — three stakeholder views. Key move: prove "one twin" with a *reconciliation test* rather than asserting it. Confidence thresholds differ per view because the cost of being wrong differs. The manager's view is a different statistic, not an average — averaging a constraint that moves 6x/shift destroys the information. Leadership must see the negative results. | — |
| 2026-08-25 | Priyansh | **Complexity 4 worked through** — late-surfacing defects. Onset read backwards off the CUSUM accumulator (so defect #5 now blocks containment, not just detection); 3-band containment partitioned by unit location, since a car on the line costs ~1/100th of one at a customer; replay as flight recorder; backward attribution reuses C2's engine. **Stop-or-continue corrected** — escape route decides, not bottleneck status, and a station stop inside the downstream buffer is free. | — |
| 2026-08-25 | Priyansh | **Complexity 3 worked through** — PLC risk and maintenance windows. Read-only boundary justified in ISA-95 terms and *enforced by a test* rather than asserted; three risk classes with additive sensing separated from control modification; the window as a job-selection problem; four-phase rollout (shadow -> one supervisor -> floor -> never closed-loop). Shadow mode falls out of the replay driver for free, and the phasing is the spine of the phased-roadmap deliverable. | — |
| 2026-08-25 | Priyansh | **Complexity 2 worked through** — multi-causal, intermittent root causes. Isolate by *scope* (who else is affected, and who isn't) rather than by statistics; natural experiments the plant already runs; ranked hypotheses with a "couldn't rule out" list. New build items: `zone_id`, change register, co-occurrence engine, confounded scenario mode. | — |
| 2026-08-25 | Priyansh | **Complexity 1 worked through and written up** in `suggestion_by_priyansh/` Part A — dark-station handling end to end: coupling map, detection horizon, cycle time as trigger-not-diagnosis, and the sensor case as a window-dated schedule. Proposes two schema changes (`manual_check` event, `attested` provenance) — needs Sagar's sign-off. | — |
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
| **A** | Clear the ground | Priyansh | `wip` | ~~tests green~~ **12/12 done 08-27**; ~~noise floor~~ **published 08-27 (0.79 cars)**; 2 doc errors (#2, #3) still to land in the deck and Evidence File |
| **B** | The loop (`record.py`, `loop.py`) | Sagar | `todo` | A shift replays at 60x in a browser, from a loop that never sees `t > now` |
| **C** | Alert contract + trust ledger | Sagar | `todo` | Every alert carries all 5 fields; calibration within ±10 pts; ledger shows running precision |
| **D** | 40 stations + transfer tests | Priyansh | `todo` | Layout-transfer and sensor-maturity numbers **decomposed** (ranking loss vs calibration loss — they mean different things), plus classifier scored on the firewall set |
| **E** | Three stakeholder views | Both | `todo` | Three views, one record stream, switchable live, **and the reconciliation test passing** (leadership total == sum of manager weeks == sum of supervisor records) |
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

**Verification pass 2026-08-27 (Sagar): all 9 worked through. Test suite is
12/12 green — first time in the project's history.** Every claim below was
measured, not assumed; the commands are in the Work log entry.

| # | Defect | Where | Owner | State |
|---|---|---|---|---|
| 1 | RNG desync — **root-caused**: `z_fail[i,t]` is indexed by wall clock and gated on `busy`, so perturbing any station shifts which ticks its neighbours are busy and they sample different pre-drawn failure values. Measured: a 20% speed-up makes **11/20 stations LOSE cars** (worst −5) via 3 extra breakdowns. Fixed with opt-in `simulate_plant(crn_safe_failures=True)` (index by the station's own busy ticks — also better physics, MTBF is in operating hours): violations drop to **1/20**. Docstring corrected. Test rewritten to pass on the correct path + a second test pins the old bug so it can't regress silently | `plant.py` | Sagar | `review` |
| 2 | **VERIFIED — Priyansh is right.** Measured on 202 strong-constraint blocks: active_period 46.04/57.92, effective_ct (ours) 43.07/59.41. But see the **new** finding below: McNemar says the two are *statistically tied*, so neither "they beat us" nor "we beat them" is defensible | deck, `1_Guide` | Priyansh | `todo` |
| 3 | **VERIFIED exactly.** all-blocks ceiling 2.271 (n=958); strong-constraint ceiling 5.255 (n=202), capture 57.4%. Correction stands and does make us look better | Evidence File §4 | Priyansh | `todo` |
| 4 | **FIXED.** Drift extrapolation removed from the live path; `Verdict.forming` now comes from `forming.buffer_countdowns` (59.6% of 178, median error +0.57 min) instead of the mechanism measured at 5.9%. `drift_rate` is still reported as a diagnostic but is never extrapolated | `detect.py` | Sagar | `done` |
| 5 | **FIXED.** Now a real tabular CUSUM, `S_j = max(0, S_{j-1} + z − k)`, accumulating across windows and memoised per window index so it stays a pure function of `at_s` — necessary because `verdict()` calls `read()` out of order. Verified order-independent (forward / reverse / shuffled identical) and monotone. Unblocks Complexity 4's backwards onset dating | `detect.py` | Sagar | `done` |
| 6 | **REJECTED — the code was right and the design note was wrong.** Tested 4 down-weight variants on 319 blocks: every one is equal or worse (top-1 32.3% → 30.1–32.0%, regret 1.303 → 1.304–1.342). Mechanism: work time already excludes blocked/starved seconds, so down-weighting charges the station twice for the same idleness. Design note corrected in the `detect.py` docstring rather than changing the code | `detect.py` | Sagar | `done` |
| 7 | **FIXED, and it was serious.** Measured on 900 held-out samples: the detector claimed **0.997 confidence while being right 10.6% of the time** (ECE 0.454) — the same failure class as the overtake-risk bug we already killed, but live. Added `fit_calibration()` (monotone binning) → **ECE 0.074, an 84% improvement**. `Verdict.confidence_calibrated` now states plainly whether the number is a probability or just an ordering score | `detect.py` | Sagar | `done` |
| 8 | **RESOLVED.** Crash confirmed as `ZeroDivisionError` at `events.py:117`; the guard now exists at `events.py:109`. Re-ran `eval_v5.py` clean to completion — 958 blocks, numbers identical to published. Stale log deleted (tracked in git, recoverable) | `results/` | Sagar | `done` |
| 9 | **DONE — and it changes the story.** Wilson 95% on every published rate (below). Overtake failure confirmed at exactly n=17, 1/17 = 5.9% **[1.0%, 27.0%]** — the honest claim is "no evidence it works", not "it fails at 5.9%". Also: comparing independent CIs is the *wrong test* for same-block data, so McNemar was run instead | all docs | Sagar | `done` |

### Measured intervals — use these numbers, not bare point estimates

Strong-constraint blocks, n=202, Wilson 95%:

| method | top-1 | top-2 |
|---|---|---|
| effective_ct (ours) | 43.1% [36.4, 50.0] | 59.4% [52.5, 65.9] |
| active_period (Roser) | 46.0% [39.3, 52.9] | 57.9% [51.0, 64.5] |
| utilisation | 35.1% [28.9, 42.0] | 48.0% [41.2, 54.9] |

**McNemar paired tests on top-1** (the correct test — all methods score the
same blocks):

| comparison | p | verdict |
|---|---|---|
| ours vs active_period | 0.4514 | **not significant — statistically tied** |
| ours vs utilisation | 0.0025 | **significant** |
| active_period vs utilisation | <0.0001 | significant |

**What we may claim:** we significantly beat the naive utilisation baseline
(p=0.0025). **What we may not claim:** that we beat, or are beaten by, the
active-period method — on n=202 those two are indistinguishable. This is a
stronger and safer position than either the original deck or the correction
in defect #2, and it retires the "46 vs 43" framing entirely.

### The label-noise ceiling — new, and it reframes top-1

The defect #1 desync puts a **0.79-car noise floor** under every sensitivity
label (visible as 5.0% physically-impossible negative gains in
`v5/truth/sensitivity_raw.csv`, down to −4.00). Median margin between the
best and second-best station is only **0.50 cars**, so **59.7% of blocks have
a margin smaller than the noise**. Jittering gains at the noise scale moves
the argmax in **~50% of blocks**.

So top-1 is partly measuring label noise, and **~43% may be close to the
achievable ceiling**, not a shortfall. Regret is far more robust: the median
cost of a noise-flipped pick is **0.000 cars**. This is direct empirical
support for the locked decision to lead on regret rather than top-1 — that
call now has a measurement behind it, not just an argument.

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
| Web stack: FastAPI + SSE, or Streamlit? | — | **decided 08-27: FastAPI + SSE + one hand-written HTML page.** Streamlit fights both the live-stream model and ISA-101 (it looks like a data-science tool, not a plant HMI), and we already proved we can hand-build good self-contained HTML in the Round 1 animations — play to that |
| How many rollout replications before it's too slow to demo at 60x? | — | **answered 08-27: not a constraint.** A full 8 h shift of verdicts computes in 0.60 s vs the 480 s a 60x replay allows — ~800x headroom. Rollouts are affordable if we want them; they are not needed for the gate |
| Regenerate v5 with biased dark placement, or ship localisation as designed-not-validated? | — | open |
| Where do the 765 MB of datasets live so we both have identical bytes? | — | open |
| **Do we regenerate v5 with `crn_safe_failures=True`?** It removes the 0.79-car label-noise floor and is better physics, but changes every published number and costs the ~2–3 h truth rebuild. Left opt-in until we both agree | Sagar (08-27) | **open — needs Priyansh** |
| **Do we retire the "46 vs 43" framing entirely?** McNemar says ours and active_period are statistically tied (p=0.45); the defensible claim is only that we beat utilisation (p=0.0025). Affects deck, Evidence File and defect #2's wording | Sagar (08-27) | **open — needs Priyansh** |

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
| `src/` · `tests/` · `scripts/` · `results/` | **The live code — moved in 27 Aug. Work here.** `pytest tests/ -q` → 10 passed, 2 skipped on a fresh clone (skips need `dataset/`) |
| `6_Code/` | FROZEN Round 1 snapshot, provenance only — do not work in it |
| `7_Prototype/` | Round 2 prototype work |
