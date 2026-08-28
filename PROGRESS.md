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

**Round 2 deadline: 2026-08-31** (moved). As of **08-28 01:18 IST**: the 27 Aug build
window elapsed unused. Remaining: 28, 29, 30 and the 31st up to the evening
recording. **Design is 100% done; the build is 0%.**

> **REVISED 08-28 for the 31 Aug deadline.** The extra day plus round-the-clock
> working restores what the 3-day triage had cut:
>
> | | Workstream | Call |
> |---|---|---|
> | **B** | The loop | **BUILD FIRST, tonight.** Nothing else starts until it runs |
> | **E** | Views | **RESTORED to all three** — the PS names them in Complexity 5 *and* Solutioning Area 4 |
> | **C** | Alert ledger | **RESTORED to a real ledger** — Complexity 7 is a named clause |
> | **D** | Scaling | **RESTORED** — 2 transfer runs (one flag, never run) + L5 dark-ratio fix + truth build, all in the background |
> | **F** | Genealogy | **RESTORED, scheduled last (30th)** — Complexity 4 is named; drops cleanly if the 29th slips |
> | **G** | Proposal + deck | **BUILD — 2 of the 3 graded deliverables are documents** |
> | **A** | Clear the ground | done 08-27 (12/12 tests, noise floor). Only the 2 doc errors remain |
>
> **Compute is not the constraint, human hours are.** Transfer runs and the L5
> truth build go to the background at 09:00 on the 28th and are not watched.

```
  design ──▶ B ──▶ E(x3) ──▶ C ──▶ F ──▶ G ──▶ FREEZE ──▶ RECORD ──▶ SUBMIT
   CLOSED    ▲     29 Aug    29     30     30     31 noon    31 eve    31 night
             28 Aug 01:18 — we are here. Design 100%, build 0%.
             The loop runs before sunrise or the plan changes at 09:00.
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
| **08-28 02:40** | **`PLAN.md` written; dataset docs rescued from gitignore; handover verified by fresh clone.** Repo confirmed complete and runnable from Priyansh's side | Sagar | `done` |
| **08-28 01:09** | **Recommendation layer folded into beat 4; case retrieval deferred to Round 3.** Slice window of 27 Aug elapsed unbuilt — **2 days + submission morning left** | Sagar | `done` |
| **08-28 03:30** | **B — the loop RUNS.** `record.py`, `loop.py`, SSE, ISA-101 view. Gate met | Sagar | `done` |
| **08-28** | **D** — transfer runs launched in background; L5 dark-ratio fix; truth build | Priyansh | `todo` |
| **08-28** | **Business Proposal** drafting starts — it is 1 of the 3 graded deliverables | Priyansh | `todo` |
| **08-28 04:20** | **E — three views DONE**, reconciliation test PASSES | Sagar | `done` |
| **08-28 05:10** | **C — alert contract DONE.** ECE 0.479→0.025, gate PASS; 25 alerts/shift | Sagar | `done` |
| **08-28 06:00** | **F — genealogy DONE.** onset +2 min; stop/continue flips. *(6/6 was one run — at scale it is 70.5% actionable, see 13:40)* | Sagar | `done` |
| **08-28 13:40** | **Data collection COMPLETE — plant stopped.** 903 shifts, 647k station-rows, 92 MB. Two claims corrected downward | Sagar | `done` |
| **08-28 15:10** | **Bug sweep — 4 bugs fixed**, incl. a ledger-corrupting key and the UI showing stale dark stations for 119/120 runs | Sagar | `done` |
| **08-30** | **G** — deck; proposal complete | Priyansh | `todo` |
| **08-31 day** | Freeze, rehearse, **record the prototype in the evening** | Both | `todo` |
| **08-31 night** | **SUBMIT** — proposal + prototype + pitch | Both | `todo` |

Move the `▲` marker as workstreams complete.

---

## MEASURED PROTOTYPE NUMBERS — quote these, not the demo run

**Source: `results/twin.db` (92 MB, 903 shifts). Regenerate with
`python scripts/query_twin.py`.** All rates are Wilson 95%, computed on the
**120 independent runs** — repeats excluded, because the loop is
deterministic and a replay reproduces a run byte-identically.

### ⚠ Two figures were corrected DOWNWARD once we left the demo run

| Claim | Demo run said | **Truth at scale** | Use |
|---|---|---|---|
| Alert rate | 25 / shift | **48.6 / shift (range 20–102)** | still inside the ISA-18.2 budget of 150 — quote **48.6**, with the range |
| Tool diagnosis | "6/6 correct" | **70.5% actionable [67.9, 72.9]**, n=1,246 tools | say *"actionable diagnosis on ~70% of alarmed tools"* — **never "6/6"** |

`L1_run_001` is a flattering run. A perfect score invites the general case,
and the general case is 70.5% — which is still a good number, and survives
questioning in a way a perfect score does not.

Final tool verdicts: wear 30.0% · unclear 29.5% · mechanical_change 29.4% ·
sensor 11.1%.

### Figures that held up at scale

| Claim | Value | 95% CI | n |
|---|---|---|---|
| Forming warnings naming a **station with NO sensors** | **15.5%** | [15.0, 15.9] | 29,060 warnings |
| Stop-or-continue — WAIT | 55.6% | [54.6, 56.5] | 10,560 |
| Stop-or-continue — STOP NOW (free) | 41.2% | [40.2, 42.1] | 10,560 |
| Stop-or-continue — STOP SOON | 3.2% | [2.9, 3.6] | 10,560 |
| Constraint occupancy — S20 | 8.0% | [7.7, 8.4] | 21,548 ticks |
| Confidence calibration | ECE **0.479 → 0.025** | gate ±10 pts | 600 held-out |
| Reconciliation (one twin, three views) | **PASS** | exact | 6,730 min / 4,431 veh |
| Loop latency | mean 71 ms | — | 86,742 ticks |

### Why collection stopped at 903 shifts

The loop is deterministic — verified: `L1_run_005` yields the identical
180-step constraint sequence on every cycle. We completed **7.5 full cycles
of all 120 runs**, so ~87% of the database is exact repeats carrying zero
information. **Sufficiency was reached at cycle 1 (~120 shifts).** More
running widens the file, not the sample.

### Known gap

`manual_checks` = **0 rows**. L1 runs carry no `manual_check.csv`; only the
**L5 segmented dataset** does. The table and the write path are built and
tested, but this dataset cannot exercise them — see the L1-vs-L5 fork in
`PLAN.md` §7, still open and now more consequential.

---

## THE FINAL PLAN — 28→31 Aug, mapped to the problem statement

**Deadline moved to 31 Aug. Prototype recorded on the evening of the 31st.**
That is ~3.5 days at high intensity, which restores F, D and the full
three-view E that the 3-day triage had cut.

### The PS asks for THREE graded deliverables — not one

This is the single most important correction to the earlier plan, which
over-indexed on the prototype:

| Deliverable | PS wording | Owner | State |
|---|---|---|---|
| **1. Detailed Business Proposal** | problem framing, solution design, target users, business case **and impact**, **phased roadmap**, key risks **with mitigations** | Priyansh | 13 design docs exist — must be assembled into ONE document |
| **2. Working Prototype** | "functional demonstration of your solution's **core mechanism**", illustrative data explicitly fine | Sagar | 0% built; engine verified ready |
| **3. Pitch Presentation** | presents **both** proposal and prototype | Both | not started |

Two of the three are documents. Priyansh's 3.5 days are the proposal and
deck; Sagar's are the prototype. That split is the plan.

### PS coverage matrix — LIVE STATUS (rewritten 08-28 16:00)

**SOLO PROJECT from 08-28.** Priyansh is on academic work; Sagar owns all
three deliverables. The earlier two-person split is void.

Legend: ✅ **demonstrated in the running prototype** · ⚠️ **partly** ·
📄 **written up but nothing runs** · ❌ **nothing**

| # | Complexity (PS wording, abridged) | State | What exists / what is missing |
|---|---|---|---|
| 1 | Inconsistent sensor coverage; some stations on **manual checklists** | ⚠️ | ✅ dark stations live, **15.5% of forming warnings name a station with no sensors** (n=29,060). ❌ **manual checklists show nothing** — `manual_checks` is 0 rows because only L5 carries them |
| 2 | **Multi-causal, intermittent** root causes (wear, operator, upstream parts, environment) | 📄 | Written up in Part A C2; the demo separates fault *kinds* but there is **no co-occurrence / zone logic in code**. Note the PS names **operator variation** and we exclude it on ethical grounds — that must be **stated out loud**, not silently skipped |
| 3 | PLC risk; retrofits only in **maintenance windows** | ⚠️ | ✅ advisory-only boundary on screen and argued in ISA-95 terms. ❌ the **window-dated sensor schedule** is not an output |
| 4 | Early defect surfaces late; downstream units carry it | ✅ | Containment lists partitioned by location, onset read back off the CUSUM to **+2 min**, and **opposite** repair-vs-recalibrate actions. 70.5% actionable [67.9, 72.9] on 1,246 tools |
| 5 | Three stakeholder views | ✅ | Supervisor / manager / leadership off one record stream, **reconciliation test PASSES** (6,730 min, 4,431 vehicles identical at all three levels) |
| 6 | Scaling: **layout, equipment vintage, sensor maturity** | ❌ | **Nothing runs.** L1–L4 transfer and `use_states=False` still never executed — no new code needed. **The cheapest remaining win by a wide margin** |
| 7 | Validation over time; false alarms erode trust | ✅ | Alert ledger with human confirm/override persisted, **ECE 0.479 → 0.025** on 600 held-out samples, **48.6 alerts/shift** vs the ISA-18.2 budget of 150, across 903 shifts |

**Score: 3 of 7 fully demonstrated, 2 partial, 1 paper-only, 1 untouched.**

### Reference parameters — where we stand

| PS says | Reality |
|---|---|
| 30–50 stations across body, paint, final | ❌ demo runs **20 stations, no segments**. L5 has 40 with segments but is unused |
| Majority instrumented, **meaningful minority** manual | ⚠️ L1 is 17/20 instrumented ✅ but has **zero** manual checks; L5 is 48.5% dark ✗ (needs the `seg_dark_p` fix) |
| Retrofits only in scheduled windows | 📄 argued, not an output |

Solutioning areas 1–6 map onto the same work: modelling (Tier A–D),
predictive techniques + **the validation ladder**, data gaps + low-cost
sensing menu, the three views, integration/read-only, and ROI.

### Reference parameters — one real mismatch to fix

- *"30–50 stations across body, paint, final"* → **L5 is 40. ✅**
- *"a majority well-instrumented, a meaningful minority manual"* →
  **L5 is currently 48.5% dark (19.4/40). ✗** That is not a minority. Fix
  `seg_dark_p` to roughly `{body 0.05, paint 0.60, final 0.45}` → ~30% dark.
  Keeps the segment story and the inversion *inside* final assembly, while
  matching the PS at line level. **One line in `layouts.py`, then rebuild.**
- *"pause only in scheduled maintenance windows"* → the window-dated sensor
  schedule already answers this.

### Principle: the demo is the spec

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

### CLOSING THE REMAINING 4 COMPLEXITIES — dated schedule (08-28 16:20)

The PS says *"you are not expected to address every point listed"*, so the
target is **honest coverage with the gaps named**, not a forced 7/7. What
follows is what each remaining complexity actually costs.

| # | Complexity | When | Cost | Target state | How |
|---|---|---|---|---|---|
| **6** | Scaling: layout / vintage / sensor maturity | **28 Aug, tonight** | ~30 min setup, then unattended | ✅ **demonstrated** | Run L1–L4 layout transfer + `use_states=False`. **No new code** — the flag exists and has never been run. Launch it, write the proposal while it runs |
| **2** | Multi-causal, intermittent root causes | **29 Aug** (inside the proposal) | ~1 h | 📄 **credibly addressed, not demonstrated** | Full version (zone_id, co-occurrence engine) is a multi-day build and **will not happen**. What ships: the fault-kind separation we already demonstrate, plus an explicit statement that **operator variation is excluded on ethical grounds** — the PS names it, so saying so is a *strength*, and silently skipping it is not |
| **3** | PLC risk / maintenance windows | **30 Aug** | ~3 h | ✅ **demonstrated** | Turn the argument into an **output**: dark stations → detection horizon → cost of the blind window → *"these sensors at the next shutdown, ranked by exposure closed per rupee, and here is the cost of deferring the rest"*. `coupling_map.csv` already exists in L5 |
| **1** | Manual checklists (the missing half) | **29–30 Aug** | ~3 h + 2–3 h unattended | ✅ **demonstrated** *(if L5 is chosen)* | Needs the L1-vs-L5 decision. If L5: fix `seg_dark_p` → rebuild → run the loop on it. Verified ready: **1,458 entries, 96.8% pass rate computable**. Also fixes the 30–50-station reference parameter in the same move |

**Projected final coverage: 6 of 7 demonstrated, 1 (Complexity 2) addressed
in the proposal with its exclusion stated.** That is a defensible submission,
and the one gap is a deliberate ethical choice rather than an oversight.

### The hard constraint

Two of three graded deliverables **do not exist**. Complexity work is
scheduled *around* them, never instead of them:

| Day | Documents (priority) | Complexity work (fills gaps) |
|---|---|---|
| **28 Aug eve** | Proposal skeleton + framing | **C6** launched, runs unattended |
| **29 Aug** | **Proposal body — the main effort** | **C2** written in; **C1** L5 rebuild launched overnight |
| **30 Aug** | Deck drafted; proposal complete | **C3** built; **C1** captured |
| **31 Aug** | **Freeze at noon.** Rehearse, record, submit | none — no new work after noon |

**If a day slips, complexity work is cut before document work.** A missing
complexity costs part of one criterion; a missing proposal costs a third of
the submission.

---

### ⚠ SOLO REPLAN — 08-28 16:00

**Priyansh is out (academic work). Sagar owns all three deliverables.** The
day plan below was written for two people and is superseded by this ordering:

| Priority | Work | Why it is here | Cost |
|---|---|---|---|
| **1** | **Business Proposal** | 1 of 3 graded deliverables, **not started**, and the largest single item. 13 design docs + `results/twin.db` mean it is assembly, not authorship | ~1 day |
| **2** | **Complexity 6 — run the transfer tests** | An entire named complexity with **zero** demonstration, and it needs **no new code** (`use_states=False`, L1–L4). Highest coverage-per-hour left | ~2 h, mostly unattended |
| **3** | **Pitch deck** | 1 of 3 graded deliverables, not started | ~half day |
| **4** | **Complexity 1 — manual checklists** | The only half-missing piece of an otherwise strong story. Needs the L5 decision + `seg_dark_p` fix | ~3 h |
| **5** | **Complexity 3 — window-dated sensor schedule** | Turns an argument into an output; the brief names the constraint explicitly | ~2 h |
| **6** | **Complexity 2 — state the operator exclusion** | Cheapest of all: the PS names operator variation, we exclude it deliberately, and saying so is a **strength** | ~15 min, in the proposal |
| — | ~~more prototype features~~ | **STOP.** The prototype is done and over-built relative to the ask. Every further hour there is an hour not spent on 2 unstarted deliverables | — |

**The rule for a solo run:** the prototype cannot earn more marks than the two
documents that do not yet exist. Build only what closes PS coverage.

### Original day plan (two-person — SUPERSEDED, kept for the record)

| When | Sagar (prototype) | Priyansh (proposal + deck) |
|---|---|---|
| **28 Aug 01:00–09:00** | **THE SLICE.** `record.py` + `loop.py` + FastAPI/SSE + one ugly page. Gate: **a shift replays at 60x in a browser from a loop that never sees `t > now`.** Nothing else until this runs | Sleep — you take the 31st night shift |
| **28 Aug 09:00–13:00** | Ranking panel + evidence panel (why this station) | **First:** fix `seg_dark_p`, rebuild L5, launch `build_truth.py` in background (~2–3 h) and the 2 transfer runs. Then start the **Business Proposal** |
| **28 Aug 13:00–21:00** | Forming warnings (buffer countdown) + **prescriptive line** (action + cars) | Proposal §problem framing, §solution design, §target users |
| **28 Aug 21:00–01:00** | Buffer + catch-up. **Gate check: beats 1–4 running** | Proposal §business case, feed in transfer numbers |
| **29 Aug** | **E: all three views** — supervisor (ISA-101 grayscale, real-time), manager (weekly trend, *a different statistic, not an average*), leadership (ROI). Then **C: alert ledger** + calibrated confidence on screen | Proposal §phased roadmap, §risks with mitigations. Deck skeleton |
| **30 Aug** | **F: genealogy containment** — VIN thread → "these 47 vehicles carry the suspect joint". Then **the reconciliation test** (leadership total == sum of manager weeks == sum of supervisor records) | Deck to full draft, built on the beats. Proposal COMPLETE by end of day |
| **31 Aug morning** | **FREEZE 12:00.** No new features after noon. Bug-fix and rehearse only | Deck final; rehearse the pitch |
| **31 Aug evening** | **RECORD THE PROTOTYPE.** Multiple takes | Record the pitch |
| **31 Aug night** | **SUBMIT** all three deliverables with hours to spare | Both |

### Rules that protect this deadline

1. **The slice runs before sunrise or the plan changes at 09:00.** It has already slipped one night; it cannot slip two.
2. **Freeze at noon on the 31st.** Every team that misses a deadline does so by shipping a feature at hour 23 that breaks the demo.
3. **Record early and often.** A recording cannot crash in front of a judge. Take a rough recording on the 30th as insurance, then a good one on the 31st.
4. **No new science.** Every number shown already exists in `results/`. If a beat needs a number we do not have, cut the beat, not the honesty.
5. **Cut order if we slip:** the LLM phrasing, then F (genealogy), then the manager view. **Never** the loop, the shifting-constraint finding, the evidence panel, or the proposal.
6. **The proposal is graded equally with the prototype.** If on the 30th the proposal is behind, Sagar stops building and writes.

### Two genuine forks — decide these on the 28th, not the 30th

**FORK 1 — which line does the demo run on?**

| | Option A: demo on **L5** (40 stations) | Option B: demo on **L1** (20 stations) |
|---|---|---|
| PS fit | **Matches "30–50 stations, body/paint/final" exactly** | 20 stations — visibly under the stated range |
| Validation | Truth labels need a 2–3 h build; numbers would be new and unaudited | **Every published number already applies** — 958 blocks, Wilson intervals, McNemar |
| Risk | New data, one day old, could surprise us live | Story is "we validated on 20 and it looks small" |
| Segments/manual checks | **Body/paint/final visible; manual_check real** | Not present at all |

**Recommendation: A, with B's numbers.** Run the demo on L5 so it looks like
the PS, and cite L1/v5 for every accuracy claim, stating plainly that
validation was done on the 126-run L1 corpus and L5 is the scaled layout.
Launch `build_truth.py` on L5 on the morning of the 28th so the option stays
open — it costs one background job, not a decision.

**FORK 2 — genealogy (Complexity 4): build or narrate?**

| | Option A: build a minimal containment view | Option B: proposal only |
|---|---|---|
| Cost | ~4 h on the 30th; VIN thread already exists in `unit_scan`/`rework_log` | zero |
| Value | Complexity 4 is **explicitly named** in the PS, and "47 vehicles carry this joint" is a *visceral* demo beat | a paragraph a judge may not read |
| Risk | Competes with the three views if the 29th runs late | leaves a named complexity undemonstrated |

**Recommendation: A, but scheduled last (30th).** If the 29th slips, it drops
without touching anything else. That is exactly what a cut item should look
like.

*(Third, smaller: the LLM phrasing layer is IN if the 30th is calm, OUT
otherwise — already logged, already bounded, already cheap to drop.)*

### Why this fits

B's engine is **done and verified** (causal 13/13, 6 ms/verdict, ~800x the
headroom the 60x gate needs). The forming mechanism, the evidence, the
detector and every headline number already exist and are measured. The
remaining work is a replay driver, a ticker, and one page — plus a proposal
and deck assembled from 13 documents that are already written.

**One honest note on working 24 h a day for four days:** the highest-risk
hours of this whole plan are the evening of the 31st, when we record — and
that is the point at which four days of no sleep will have accumulated. The
freeze at noon and the insurance recording on the 30th exist specifically so
that a tired evening cannot cost us the submission. Protect those two rules
above any feature.

---

## Right now

_Last updated: 2026-08-28 16:20 by **Sagar**_

| | Working on | Branch | ETA | Blocked by |
|---|---|---|---|---|
| **Sagar** | **B, C, E, F DONE + bug sweep complete (4 fixed). Data collection COMPLETE, plant STOPPED** — 903 shifts in `results/twin.db`. **Read "MEASURED PROTOTYPE NUMBERS" above before writing any slide**: alert rate is 48.6/shift not 25, and tool diagnosis is 70.5% actionable not 6/6. Restart the demo with `python web/server.py --run <run> --speed 60 --shifts 0`. Originally: — loop, alert contract, three views, genealogy. **Every workstream I own is complete, ~2 days early** (F was scheduled for the 30th). Remaining for me: polish + the ROI beat. | `main` | — | — |
| **Priyansh** | **OUT — academic work (from 08-28).** Design contribution complete: 7/7 complexities and 6/6 solutioning areas written up, which the proposal is being assembled from | — | — | — |

### PRIYANSH — START HERE (written 08-28 02:20)

1. **Read `PLAN.md`.** Deadline moved to **31 Aug**; the plan is hour-blocked to it.
2. **Your lane is the Business Proposal + deck for all four days.** Two of the
   three graded deliverables are documents, and you hold all 13 design docs.
   That is the single biggest change from the earlier plan.
3. **First 30 minutes of the 28th, in this order:**
   - fix `seg_dark_p` in `layouts.py` (we are 48.5% dark; the PS says the
     manual-check stations should be a *minority* — see `PLAN.md` §6)
   - rebuild L5, then launch `build_truth.py` **and** the 2 transfer runs in
     the background and walk away from them
   - then start the proposal
4. **`docs/dataset/` is new** — the v5 dataset documentation was invisible to
   you until now because `dataset/` is gitignored. Read `v5_dataset.md`.
5. **Two forks need your view** (`PLAN.md` §7): which line the demo runs on,
   and whether genealogy is built or narrated. My recommendations are in there.
6. Schema decisions from your Part A are **both accepted** (`manual_check`,
   `attested`) and built against.

**Claim discipline for the deck — UPDATED 08-28 13:40:** use the **MEASURED PROTOTYPE NUMBERS**
section above. Two figures were corrected downward after 903 shifts: **alert rate 48.6/shift
(not 25)** and **tool diagnosis 70.5% actionable (not 6/6)**. Also: McNemar says we **significantly beat
utilisation (p=0.0025)** and are **statistically tied with active-period
(p=0.45)**. Claim the first. Never the second. The "46 vs 43" framing is
retired entirely.

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
| **08-28 16:20** | Sagar | **Dated schedule for the 4 remaining complexities.** C6 (scaling) **tonight** — no new code, launch L1–L4 transfer + `use_states=False` and write while it runs; C2 (multi-causal) **29 Aug in the proposal** — the full zone/co-occurrence build is multi-day and **will not happen**, so what ships is the fault-kind separation we already demonstrate plus an explicit statement that **operator variation is excluded on ethical grounds** (the PS names it, so saying so is a strength); C3 (maintenance windows) **30 Aug** — turn the argument into a **dated sensor schedule ranked by exposure closed per rupee**, `coupling_map.csv` already exists; C1 (manual checklists) **29–30 Aug** — needs the L1-vs-L5 call, and choosing L5 also fixes the 30–50-station reference parameter in the same move. **Projected final coverage: 6/7 demonstrated, C2 addressed on paper with its exclusion stated.** Recorded the hard constraint: complexity work is scheduled *around* the two unstarted documents, never instead of them, and **if a day slips, complexity work is cut before document work** — a missing complexity costs part of one criterion, a missing proposal costs a third of the submission. | — |
| **08-28 16:00** | Sagar | **PROJECT IS NOW SOLO — Priyansh is on academic work; Sagar owns all three deliverables.** The two-person split (he writes, I build) is void and the day plan is superseded. **Rewrote the PS coverage matrix to live status** — it had been written *before* B/C/E/F existed, so it described intentions rather than reality, and carried a stale ECE figure. **Honest score: 3 of 7 complexities fully demonstrated (4, 5, 7), 2 partial (1, 3), 1 paper-only (2), 1 untouched (6).** New solo priority order: **(1) Business Proposal** — 1 of 3 graded deliverables, not started, and assembly rather than authorship given 13 design docs + `results/twin.db`; **(2) Complexity 6 transfer tests** — an entire named complexity with zero demonstration needing **no new code**, the best coverage-per-hour left; (3) deck; (4) Complexity 1 manual checklists (needs the L5 call); (5) Complexity 3 window-dated schedule; (6) state the operator-variation exclusion out loud — the PS names it, we exclude it deliberately, and saying so is a strength. **Explicit stop rule recorded: no more prototype features.** It is done and over-built relative to the ask, and every further hour there is an hour not spent on two deliverables that do not exist. | — |
| **08-28 15:10** | Sagar | **COMPONENT-BY-COMPONENT BUG SWEEP — 4 bugs found and fixed, 2 of which would have shown a judge wrong information.** Probed each component with edge cases rather than reading it; `record.py`, `rollup.py` and the loop's shift-reset logic came back clean. **(1) `update_outcome` matched on `(session, station, at_s)` — but `at_s` is a *within-shift* clock and repeats. On the recorded data that key matched up to 45 rows across 45 different shifts, so one supervisor pressing *confirm* would have silently marked 44 decisions nobody made** — corrupting exactly the ledger we use to argue trustworthiness. `Alert` now carries `shift_no` and the key includes it. **(2) Only NOK manual checks reached storage, capped at 3** (the display list was being persisted). A checklist's **pass rate** is the whole diagnostic — Part A §1.3 turns on comparing it to EOL failures — so storing only failures made that test impossible. Frames now carry a separate full set windowed on the *tick* (not the 30-min display window, which would have written each entry 6×). **Verified on L5: 1,458 entries, 1,411 OK / 47 NOK, pass rate 96.8% now computable.** **(3) `POST /alert/<bad index>` returned `{"ok":true}` having done nothing** — a client would believe a decision was recorded when it was dropped; silently losing a decision is the worst failure available to a trust ledger. Now 404, plus 409 on an already-resolved alert. **(4) The UI fetched the dark-station set ONCE at page load, but every run has its own** — run_001 is S10/S14/S15, run_003 shares *none* of them. After the first shift change the line drew the **previous** run's sensor coverage — **wrong for 119 of 120 runs**, and wrong about precisely the claim that panel exists to make. Meta is re-fetched on every shift change. Also clamps `/genealogy?at_s` to `[0, horizon]`. Tests 10 passed / 2 skipped. | `d3c6418` |
| **08-28 13:40** | Sagar | **DATA COLLECTION COMPLETE — plant stopped. 903 shifts recorded, and two headline numbers CORRECTED downward.** Final store: **86,742 frames · 647,855 station-rows · 108,208 forming rows · 73,581 tool assessments · 10,766 alerts · 903 shifts · 2 sessions · 92 MB.** **Why we stopped:** the loop is deterministic, so replaying a run reproduces it **byte-identically** — verified, `L1_run_005` gives the same 180-step constraint sequence every cycle. We completed **7.5 full cycles of all 120 runs**, so ~87% of the database is exact repeats carrying **zero** information. Sufficiency was reached at cycle 1 (~120 shifts); everything after that was burning CPU, not gathering evidence. **Two corrections that must reach the deck — the demo run was flattering:** (1) **Alert rate is 48.6/shift (range 20–102), NOT the 25 measured on `L1_run_001`.** Still inside the ISA-18.2 budget of 150, so the claim survives, but quote 48.6 with its range. (2) **Tool classification is 70.5% actionable [67.9, 72.9] across 1,246 alarmed tools — not 6/6.** Final verdicts: wear 30.0%, unclear 29.5%, mechanical_change 29.4%, sensor 11.1%. The 6/6 was one favourable run; claiming it invites the general case, and the general case is 70.5%. **Numbers that held up at scale (Wilson 95%, deduplicated to 120 independent runs):** forming warnings naming a **dark station 15.5% [15.0, 15.9]** (n=29,060); stop-or-continue **55.6% WAIT / 41.2% STOP NOW / 3.2% STOP SOON** (n=10,560); constraint occupancy S20 8.0%, S19 7.0% (n=21,548). **Known gap:** `manual_checks` is 0 rows — L1 runs carry no `manual_check.csv`; only the **L5 segmented dataset** does. The plumbing is built and tested but this dataset cannot exercise it, which is the open L1-vs-L5 fork in `PLAN.md` §7. | `15ed7dc` |
| **08-28 07:40** | Sagar | **All live data now gathered into SQLite, and the plant runs independently of viewers.** **Structural fix first:** the loop lived inside `/stream`, so **the line only ran while a browser was attached** — close the tab and the plant stopped and nothing was gathered. A driver task now owns the loop from server start to shutdown; viewers subscribe to a broadcast, and joining/leaving changes nothing about what is recorded. **`src/twin/store.py`** writes **7 tables** — `sessions, frames, rankings, forming, alerts, shifts, tool_assessments` — to `results/twin.db` in **WAL mode**, so analysis reads never block the plant. One row per *(frame, station)* in `rankings` is what makes after-the-fact evidence queries possible; **every row carries a session id** so numbers can never be silently mixed across runs, speeds or calibrations. JSONL kept alongside as a crash-proof raw stream. **`scripts/query_twin.py`** opens it **read-only** and prints the standard report — safe against a live plant. **Early numbers:** 782 station-rows behind 110 ticks; alerts avg cost 0.94 (constraint) / 1.56 (forming) vehicles; **30 of 118 forming warnings — 25.4% — name a station with NO sensors**; stop-or-continue already splitting 32 WAIT / 13 STOP NOW / 2 STOP SOON on the same faults. **The plant is left running and must not be stopped without Sagar's instruction.** | `89bd435` |
| **08-28 07:00** | Sagar | **Continuous multi-shift replay + persistence — the twin was amnesiac.** `--shifts 0` replays consecutive runs as consecutive shifts (120 available, cycling); **the ledger, confirmed/overridden counts and calibration carry across shifts** while shift-local state resets. That is what Complexity 7 actually needs — one shift cannot demonstrate a precision that has "survived over time". Then found nothing was being *kept*: frames streamed to the browser and were dropped, the ledger lived in memory, a restart erased it all. `src/twin/sink.py` now appends three JSONL streams to `results/live/` (compact frame per tick, every alert with its 5 contract fields, a row per shift); `scripts/summarize_live.py` reads them back into a committable `results/live_summary.json` while the raw stream is gitignored. `/recording` reports capture status without interrupting the run. **Two bugs found by running continuously:** (a) every `/stream` connection drove the *same* loop, so a page refresh double-advanced the shift counter and raced the ledger — streams now carry a generation number and the newest viewer takes ownership; (b) buffer countdowns name stations with **no sensors at all** and the UI didn't say so — now flagged `DARK · inferred`. **First 17 simulated hours give quotable numbers: 19.5 alerts/shift (ISA-18.2 budget is 150), and 42 of 211 forming warnings — ~20% — name a station with zero instrumentation.** | `5aa4470`, `676657e` |
| **08-28 06:00** | Sagar | **WORKSTREAM F DONE — genealogy containment + stop-or-continue. Gate met.** `src/twin/genealogy.py`. **Onset is read backwards off the CUSUM accumulator** — only possible because defect #5's stateful-CUSUM fix landed in the verification pass. **Scored against hidden tool truth on `L1_run_001`: all 6 tools classified correctly, onset within +2 min on S05, zero false alarms on the 3 healthy tools.** **The headline beat:** S05 and S06 get **opposite instructions from the same symptom** — S05 is real wear (*SERVICE it*), S06 is a lying transducer whose 26 NOKs are **false rejections of good parts** (*RECALIBRATE only — do NOT service*; servicing scraps good parts and fixes nothing). Separated by asking whether a mechanically-coupled channel moved with the torque (S05: current −4.09σ, angle +6.01σ; S06: current +0.45σ, angle −0.17σ). Containment partitioned by location — 202 vehicles through S05 since onset, 48 still on the line vs 154 completed — because a car on the line is a rework instruction and one that has left is a customer event. **Stop-or-continue follows Priyansh's C4 correction — the escape route decides, not bottleneck status:** the *same* S05 tool is told **STOP NOW** at buffer 0/3 and **WAIT FOR THE BREAK** at 3/3, which is the gate *"same drifting tool, opposite correct answers"* demonstrated live. **Bug caught by scoring rather than reading:** the CUSUM was one-sided and detected **nothing at all**, because tool wear drives torque *down*. Now two-sided and running on torque *and* motor current, so an early mechanical change (S08) is visible before the joint result moves. | `18c117c` |
| **08-28 05:10** | Sagar | **WORKSTREAM C DONE — alert contract, calibrated confidence, trust ledger. Gate met.** Implemented design **Part 4.2** verbatim: an alert carries candidate+margin, evidence, persistence, action, and cost-if-ignored, and an incomplete alert is **suppressed, not downgraded** (7 suppressed on the demo run, shown on screen). Persistence is *measured* — median of completed constraint episodes, withheld until two exist. `scripts/fit_calibration.py` fits on 30 runs, reports on **20 disjoint held-out runs**, demo run excluded from both: **ECE 0.479 → 0.025**, so the gate *"calibration within ±10 pts"* **PASSES**. **The finding worth telling:** calibration *broke* alerting. Uncalibrated confidence sat near 1.0 so a 0.5 cut-off admitted everything (~170 alerts/shift); calibrated, it sits at the true hit rate ~0.11 and the same cut-off **silenced every constraint alert — the system went quiet precisely because it became honest.** "2× base rate" was worse: the calibrator's output is bounded by its top bin (~0.117), so that threshold is unreachable *by construction*. **Top-1 probability is the wrong gate** — the argmax label is near a coin flip (our own 0.79-car noise floor), so a well-calibrated top-1 confidence *cannot* be high. Alerts now gate on **cost of not acting** (≥0.5 vehicles over the median episode), moving our locked "regret not top-1" decision out of evaluation and into the product. Confidence still shown, with lift over base rate, as context not gate. **25 alerts/shift, within the ISA-18.2 budget of 150.** | `4ec6000` |
| **08-28 04:20** | Sagar | **WORKSTREAM E DONE — three stakeholder views, and the reconciliation test PASSES.** `src/twin/rollup.py` + `scripts/build_rollup.py` replay 15 shifts and cache `results/rollup.json`, so every figure in the upper views is traceable to a file and regenerable by one command. **Manager view is deliberately NOT an average** — the constraint moves ~20×/shift, so a mean describes no moment of it; it shows a **constraint-occupancy distribution** instead (S20 held the line **21.3%** of week 1, S19 12.2%), which is a scheduling and capex input. **Leadership view carries the reconciliation test** — the proof that these are one twin, not three dashboards: each level totals independently and matches at **6730 constraint-minutes / 4431 vehicles** across supervisor records, manager weeks and leadership. Colour returns here only; ISA-101 governs the plant HMI, not a business dashboard. **Two honesty items:** (a) every evidence row names its source file, and **the CONWIP "36% lower lead time" claim is displayed as NOT MEASURED** — suggestion #10 wants the business case *led* by it and calls it measured, but **no file in `results/` produces it**; it must be re-measured or dropped before being presented as ours. (b) Caught and fixed a value/n mismatch on screen — all-blocks regret was reported against the strong-constraint n, which is exactly the defect #9 failure mode. | `1c76c4f` |
| **08-28 03:30** | Sagar | **WORKSTREAM B IS DONE — the loop runs in a browser. Shadow is now a twin.** `src/twin/record.py` (replay driver), `src/twin/loop.py` (ticker), `web/server.py` (FastAPI+SSE), `web/index.html` (ISA-101 supervisor view). **Gate met**: an 8 h shift replays at 60x from a loop that never sees `t > now` — causality enforced *physically* (`view_at(t)` truncates the Run, so the future cannot be read even by accident), which also closes the `infer_states_from_scans` whole-run-baseline leak for free. Measured on `L1_run_001`: **26 ms/tick against a 5 s budget**, constraint moves **15×** in the shift, 279 vehicles out, latency shown on screen. **Beats 1–6 all visible**; only ROI (beat 7, leadership view) outstanding. **Three defects found by actually running it:** (a) the line diagram *omitted* dark stations, hiding the sensor-coverage story we exist to tell — spine is now recovered from the numbering and gaps drawn hatched (20 stations, 17 instrumented, 3 dark); (b) `units_out` counted at whichever station was last seen, so it wandered early in the shift; (c) **alerts fired every tick — ~170/shift, breaching the ISA-18.2 <150 budget our own design cites.** Alerts now fire on *change*, not on state: **26/shift**. Also capped forming warnings at 60 min after the UI showed "forming in ~576 min", which is arithmetic, not a warning. | `4ee80b5` |
| **08-28 02:40** | Sagar | **Verified the handover from Priyansh's side, not mine — two silent repo bugs found and fixed.** (1) The four dataset READMEs were invisible because they sat inside gitignored `dataset/`; **`v5/README.md` — the whole primary dataset's documentation — had never been in the repo at all.** Rescued to `docs/dataset/`. (2) **The rescue nearly failed identically**: a bare `dataset/` in `.gitignore` matches that directory name at *any depth*, so it silently swallowed `docs/dataset/` too. Anchored to `/dataset/`. **Both fixes verified in both directions** — planted a fake `dataset/v5/flow/unit_scan.csv` and confirmed git still ignores it (the 765 MB cannot be committed by accident) while `docs/dataset/` stays tracked. (3) **Fresh-clone test**: cloned the repo to a temp dir as Priyansh would — all key files present, `pytest` gives 10 passed / 2 skipped, AI-reference scan clean apart from the deliberate `claude-opus-5` API choice. (4) **Diffed both repos**: no code drift, the prototype repo carries the latest `detect.py`/`plant.py`/`layouts.py`. **Lesson generalised into the working agreement below** — neither bug was findable from this machine, because both were about what *someone else* receives. | — |
| **08-28 02:20** | Sagar | **`PLAN.md` created + rescued four dataset docs that were invisible to Priyansh.** (1) **`PLAN.md`** — standalone final-submission plan: PS coverage matrix, the 7 demo beats, hour-blocked day plan to the 31st, the two open forks, cut order, and what is already in the bank. (2) **Found four dataset READMEs trapped under `.gitignore`** (`dataset/` is ignored, so `v5/README.md` — the primary dataset's entire documentation — had never been visible to Priyansh). Rescued to **`docs/dataset/`** as v2/v3/v5/v6_segmented. Two of them carried AI-provenance notes; **removed per the standing rule**, replaced with factual status sections. (3) Added **`scripts/verify_rank_variants.py`** and **`scripts/verify_calibration.py`** — the evidence behind rejecting defect #6 and fixing #7, now re-runnable by either of us and made path-portable. | — |
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
| **B** | The loop (`record.py`, `loop.py`) | Sagar | **`done` 08-28 03:30** | ~~A shift replays at 60x in a browser, from a loop that never sees `t > now`~~ **MET** — 26 ms/tick, causality enforced structurally |
| **C** | Alert contract + trust ledger | Sagar | **`done` 08-28 05:10** | ~~all 5 fields; calibration within ±10 pts; running precision~~ **ALL MET** — contract enforced w/ suppression, ECE 0.025, ledger live |
| **D** | 40 stations + transfer tests | Priyansh | `todo` | Layout-transfer and sensor-maturity numbers **decomposed** (ranking loss vs calibration loss — they mean different things), plus classifier scored on the firewall set |
| **E** | Three stakeholder views | Sagar | **`done` 08-28 04:20** | ~~Three views, one record stream, switchable live, and the reconciliation test passing~~ **MET** — PASS at 6730 min / 4431 vehicles |
| **F** | Genealogy + stop-or-continue | Sagar | **`done` 08-28 06:00** | ~~Same drifting tool, opposite correct answers by flow state~~ **MET** — S05 flips STOP NOW ↔ WAIT on buffer state; 6/6 tools classified correctly vs hidden truth |
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
- **Check the repo from the OTHER person's side before any handover.** Twice on
  08-28 something was invisible to the teammate while looking fine locally — the
  v5 dataset documentation was never in the repo, and the fix for it was itself
  swallowed by the same ignore rule. Neither was findable from the machine that
  wrote them. The only reliable test is a fresh clone:

  ```bash
  git clone <url> /tmp/check && cd /tmp/check && python -m pytest tests/ -q
  ```

  Expect **10 passed, 2 skipped** (the skips need `dataset/`, which is
  regenerable). Run this before saying "pushed" on anything that matters.
- **Documentation never lives inside a gitignored data directory.** Docs go in
  `docs/`. `.gitignore` patterns are root-anchored (`/dataset/`, not `dataset/`)
  because the bare form matches at every depth.

---

## Repo map

| Path | What |
|---|---|
| `PROGRESS.md` | This file — canonical live log |
| **`PLAN.md`** | **The final-submission plan — read this first if you have been away** |
| `docs/dataset/` | Dataset documentation (v2/v3/v5/v6_L5) — was trapped under `.gitignore` until 28 Aug |
| `scripts/verify_*.py` | The evidence behind the defect #6 rejection and the #7 calibration fix |
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
