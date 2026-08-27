# PLAN — Round 2 final submission

**Team HipHipHooray** · Sagar Sahu (`@sagar2907`) · Priyansh Goyal (`@Priyansh0704`)
**Accenture Innovation Challenge 2026 · Problem Track 4 — DigitalTwin.ai**

> **Deadline: 31 August 2026.** Prototype recorded on the evening of the 31st.
> Written 28 Aug 01:20 IST. `PROGRESS.md` stays the live log — this file is the
> plan it executes against. If the two disagree, `PROGRESS.md` is newer.

---

## 1. Where we actually stand

**Design: 100% done. Build: 0%.**

Priyansh has answered all 7 real-world complexities and all 6 solutioning
areas on paper — 13 documents. Sagar has verified the engine: 12/12 tests
green, 9/9 carried defects resolved, and the detector proven **causal** and
**~800x faster** than the demo needs.

Nothing user-facing exists. There is no loop, no UI, no proposal document.
That is the whole remaining risk, and it is why this plan is front-loaded.

---

## 2. What the PS actually grades — read this twice

The problem statement asks for **three deliverables**, and **two of them are
documents**. Earlier plans over-weighted the prototype; this is the
correction.

| # | Deliverable | PS wording | Owner |
|---|---|---|---|
| 1 | **Detailed Business Proposal** | problem framing, solution design, target users, business case **and impact**, **phased roadmap**, key risks **with mitigations** | **Priyansh** |
| 2 | **Working Prototype** | "a functional demonstration of your solution's **core mechanism**" — illustrative/simulated data is *explicitly* fine | **Sagar** |
| 3 | **Pitch Presentation** | presents **both** the proposal and the prototype | Both |

**The split: Priyansh owns the proposal and the deck for all four days.
Sagar owns the prototype.** Neither of us should drift into the other's lane
before the 30th.

---

## 3. Coverage — every PS complexity must land somewhere

| # | Complexity (PS wording, abridged) | Where we answer it | Status |
|---|---|---|---|
| 1 | Inconsistent sensor coverage; some stations on manual checklists | L5 segments, `manual_check` events, observability map — live in the UI | **fix dark ratio first** (§6) |
| 2 | Multi-causal, intermittent root causes | Proposal (Part A C2); demo distinguishes fault kinds | proposal + narration |
| 3 | PLC/live-production risk; retrofits only in maintenance windows | Read-only boundary **enforced by a test**; window-dated sensor schedule | proposal + UI label |
| 4 | Early defect surfaces late; downstream units carry it | **Genealogy containment list** from the VIN thread | build 30 Aug |
| 5 | Supervisor / plant manager / leadership need different views | **Three views** off one record stream | build 29 Aug |
| 6 | Scaling across layout, equipment vintage, sensor maturity | **L1–L4 transfer + `use_states=False`** — one flag, never run | background 28 Aug |
| 7 | Predictive claims validated over time; false alarms erode trust | **Alert ledger** + the calibration fix (ECE 0.454 → 0.074) | build 29 Aug |

Solutioning areas 1–6 map onto the same work: modelling approach (Tier A–D),
predictive techniques + the **validation ladder**, data gaps + the low-cost
sensing menu, the three views, integration/read-only, and ROI.

---

## 4. The demo is the spec — seven beats

Build only what these seven minutes need. Anything else is cut.

| # | Beat | What it proves | Status |
|---|---|---|---|
| 1 | A real shift replays at 60x | **Twin, not shadow** — the core Round 2 claim | needs `loop.py` |
| 2 | The constraint **moves** ~6x/shift; utilisation names one station all day | Our central finding, live | ranking exists |
| 3 | "S12 forming, ~11 min" — then it happens | Prediction, not description | **already built** |
| 4 | Evidence **+ recommended action**: "relieve S12 — worth 2.3 cars; next best S07, 0.4" | Reasoning shown, and it *acts* | ranking exists + action table |
| 5 | Ledger: "right on 24 of the last 34" | Answers the false-alarm clause | build |
| 6 | Advises, **never writes**; a person confirms | The ISA-95 boundary we locked | button + label |
| 7 | CONWIP: same throughput, **−36% lead time, zero capex** | ROI, and it is measured | number exists |

**Four of seven are already built.** That is why this is achievable.

---

## 5. Day plan — 28 → 31 August

| When | Sagar (prototype) | Priyansh (proposal + deck) |
|---|---|---|
| **28 Aug 01:00–09:00** | **THE SLICE.** `record.py` + `loop.py` + FastAPI/SSE + one ugly page. Gate: a shift replays at 60x from a loop that never sees `t > now` | *Sleep — you take the 31st night shift* |
| **28 Aug 09:00–13:00** | Ranking panel + evidence panel | **First 30 min:** fix `seg_dark_p` (§6), rebuild L5, launch `build_truth.py` **and** the 2 transfer runs in the background. Then start the **Proposal** |
| **28 Aug 13:00–21:00** | Forming warnings + prescriptive line | Proposal: framing, solution design, target users |
| **28 Aug 21:00–01:00** | Buffer/catch-up. **Gate: beats 1–4 running** | Proposal: business case; fold in transfer numbers |
| **29 Aug** | **Three views** (supervisor ISA-101 / manager weekly / leadership ROI), then the **alert ledger** | Proposal: **phased roadmap**, **risks + mitigations**. Deck skeleton |
| **30 Aug** | **Genealogy containment**, then the **reconciliation test** (leadership total == Σ manager weeks == Σ supervisor records) | Deck to full draft. **Proposal COMPLETE by end of day** |
| **30 Aug, late** | **Insurance recording** — rough, but a complete run-through | — |
| **31 Aug, by 12:00** | **FREEZE.** No new features after noon. Bug-fix and rehearse only | Deck final |
| **31 Aug evening** | **RECORD THE PROTOTYPE** — several takes | Record the pitch |
| **31 Aug night** | **SUBMIT** all three deliverables | Both |

---

## 6. Do this before anything else touches L5

The PS reference parameters say:

> *"a majority of stations well-instrumented, a **meaningful minority**
> reliant on manual checks"*

**Our L5 is currently 48.5% dark (19.4 of 40).** That is not a minority — it
nearly inverts the assumption a judge will check us against.

**Fix:** in `src/twin/layouts.py`, change `seg_dark_p` from
`{body 0.10, paint 0.90, final 0.65}` to roughly
`{body 0.05, paint 0.60, final 0.45}` → about **30% dark**. This keeps the
segment story *and* keeps the inversion inside final assembly, which is
exactly the argument in Part A §1.1 — it just stops the *line-level* number
contradicting the PS. Then rebuild L5 and run the truth build.

Station count (40, across body/paint/final) already fits "30–50". ✅

---

## 7. Two open forks — decide on the 28th, not the 30th

### Fork 1 — which line does the demo run on?

| | **A: L5** (40 stations) | **B: L1** (20 stations) |
|---|---|---|
| PS fit | matches "30–50, body/paint/final" | visibly under range |
| Validation | needs a 2–3 h truth build; numbers new | **every published number already applies** |
| Segments / manual checks | visible and real | absent |

**Recommended: A for the demo, B for every accuracy claim** — run it on L5 so
it looks like the PS, and state plainly that validation was done on the
126-run L1 corpus. Launching the L5 truth build on the morning of the 28th
keeps this option open for the cost of a background job.

### Fork 2 — genealogy (Complexity 4): build or narrate?

**Recommended: build, scheduled last (30 Aug).** ~4 h, the VIN thread already
exists, and *"these 47 vehicles carry the suspect joint"* is a visceral demo
beat for an explicitly-named complexity. Because it is last, it drops cleanly
if the 29th runs long.

*(Smaller: the LLM phrasing layer is IN if the 30th is calm, OUT otherwise.)*

---

## 8. Rules that protect the deadline

1. **The slice runs before sunrise, or the plan changes at 09:00.** It has already slipped one night.
2. **Freeze at noon on the 31st.** Teams miss deadlines by shipping a feature at hour 23 that breaks the demo.
3. **Record early and often.** A recording cannot crash in front of a judge — rough cut on the 30th, good one on the 31st.
4. **No new science.** Every number shown already exists in `results/`. If a beat needs a number we do not have, cut the beat, not the honesty.
5. **Cut order if we slip:** LLM phrasing → genealogy → manager view. **Never** the loop, the shifting-constraint finding, the evidence panel, or the proposal.
6. **The proposal is graded equally with the prototype.** If it is behind on the 30th, Sagar stops building and writes.

**On working around the clock for four days:** the riskiest hours in this
plan are the evening of the 31st, when we record — precisely when four days
of no sleep will have accumulated. Rules 2 and 3 exist so a tired evening
cannot cost us the submission. Protect them above any feature.

---

## 9. What is already in the bank

Do not rebuild these — they are done, measured, and defensible:

- **The engine**: causal at 13/13 timepoints, 6 ms/verdict, 12/12 tests green
- **Detection**: 43.1% / 59.4% top-1/top-2 on strong constraints, regret 1.309
- **Statistical honesty**: Wilson intervals on every rate; **McNemar shows we
  significantly beat utilisation (p=0.0025) and are statistically tied with
  active-period (p=0.45)** — claim the first, never the second
- **Forming**: buffer countdown, 59.6% of 178 warnings, median error +0.57 min
- **Calibration**: ECE 0.454 → 0.074 (the detector previously claimed 0.997
  confidence at a 10.6% hit rate — found and fixed)
- **Negative results**: overtake risk 5.9% [1.0–27.0] at n=17, killed and
  reported. **Lead with these; they are our strongest credibility asset.**
- **Data**: v5 (162 runs), v3/process (deep tool corpus), L5 (40 stations)
- **Design**: 7/7 complexities and 6/6 solutioning areas written up

---

## 10. Where things live

| Path | What |
|---|---|
| `PROGRESS.md` | **Canonical live log.** Both of us write here, every session |
| `PLAN.md` | This file |
| `src/` `tests/` `scripts/` `results/` | The live code — work here |
| `docs/dataset/` | Dataset documentation (was trapped under gitignore until 28 Aug) |
| `suggestion_by_priyansh/` · `suggestion_by_sagar/` | Proposals awaiting the other's response |
| `4_Design_Documents/` | Source of truth for the design |
| `6_Code/` | **Frozen** Round 1 snapshot — provenance only, do not work in it |

```bash
pip install numpy pandas matplotlib pytest
python -m pytest tests/ -q     # 10 passed, 2 skipped on a fresh clone
```

The 2 skips are leakage tests needing `dataset/`, which is gitignored and
regenerable: `python scripts/build_v5.py` then
`python scripts/build_truth.py --workers 10` (~2–3 h). All seeded — identical
bytes on both machines.
