# Suggestions — Priyansh

Proposals for Sagar to review. Nothing here is decided.

**How this works:** I raise it here → Sagar responds in the Response column → if we agree,
it moves to **Locked decisions** or the **Status board** in `PROGRESS.md` and gets marked
`moved` below. Sagar's equivalent is `suggestion_by_sagar/`.

_Last updated: 2026-08-25_

---

# Part A — Worked solutions to brief clauses

One entry per Real-World Complexity. Statement first, then the solution we'd defend.
These are more settled than the numbered proposals below — but still not locked until
Sagar agrees.

---

## Complexity 1 — Inconsistent sensor coverage

> *"Assembly lines mix legacy and modern equipment, so sensor coverage is often
> inconsistent — some stations are richly instrumented, others rely entirely on manual
> checklists."*

**Status:** `open` — needs Sagar's review. Touches `record.py` (provenance) and the shared event schema.

### 1.1 The reality this has to work against

Sensors follow the **operation**, not the station. A station gets instrumented only if
(a) the joint is legally traceable, (b) the machine can't run without the sensor, or
(c) it caused a problem once. Everything else gets nothing.

| Segment | ~stations | Instrumented | Why |
|---|---|---|---|
| Body | 15 | ~90% | Robots need feedback to run |
| Paint | 10 | booth-level only | Per-unit quality is sampled, not measured |
| **Final assembly** | 20 | **~30–40%** | Only the safety-critical fastening stations |

Across the whole line the brief's "majority instrumented" holds. **Inside final assembly it
inverts** — and that is where the manual work and most defect risk actually live.

### 1.2 Bottleneck detection at a dark station — solved, and free

Flow needs only **unit in/out timestamps and buffer levels**. It does not need process
values. So a dark station gets a bottleneck answer today through neighbour inference
(Tier B), with no hardware at all.

Optional upgrades that raise it from *inferred* to *measured*: a digitised checklist tap, a
barcode scan, or a photoeye. All three mount externally and publish on a separate network,
so **no PLC program changes and therefore no re-validation** — they fit inside an ordinary
maintenance window.

### 1.3 Manual checklists are not a sensor — and we say so

Low-frequency, categorical, recorded late, and **confirmation-biased**. A checklist that
always reads OK is measuring compliance with the checklist, not quality.

Test it: compare its pass rate against EOL failures attributed to that station through
genealogy. If the checklist says 100% and EOL says 2% fail, the checklist isn't seeing what
it claims. *(Same shape as our torque finding — the instrument can be the thing that's
wrong, whether it's silicon or a person.)*

**Two design additions this argues for:**

1. A sixth event type `manual_check` — `unit_id, station_id, check_id, result, reason_code,
   recorded_at, entry_latency`. The `entry_latency` field carries the gap between the work
   happening and a human recording it.
2. A fourth provenance value **`attested`** — a person says so. Not measured, not inferred,
   not predicted. Schema becomes `measured / attested / inferred / predicted`.

### 1.4 Defect detection at a dark station — three buckets

| Bucket | Meaning | Answer |
|---|---|---|
| **Time-visible** | The fault changes how long the work takes | Free, real-time |
| **Neighbour-visible** | Shows up at a downstream *coupled* station | Free, a few stations late |
| **Silent** | Nothing moves until final test | Needs a sensor — costed case |

**Time-visible.** Cycle time is a proxy process channel at a dark station — we already have
it from scans. Catches fixture wear, bad upstream parts, variant trouble. Watch the
**spread**, not just the mean. Critically it is a **trigger, not a diagnosis**: a cycle-time
anomaly should raise the priority of watching that station's coupled downstream stations for
the next N units, not raise a defect alert on its own.

**Neighbour-visible — the coupling map.** The earliest downstream station whose process
*physically depends* on the dark station's output acts as a free inspector. Two things we
got sharper on:

- Coupling is **per-operation, not per-station**. One dark station doing three jobs has
  three different downstream couplings.
- You want the earliest station with **adequate measured detection power**, not merely the
  earliest coupled one. Measure it; don't assume it.

This turns a 40-station detection delay into a few stations. It is our direct answer to the
brief's late-inspection clause.

**Silent.** Some faults are coupled to nothing — cosmetic defects, rattles, seal leaks. The
system says so plainly rather than implying coverage it doesn't have.

### 1.5 Detection horizon, and the sensor business case

The coupling map yields, per dark operation, **how many vehicles are built before anything
could notice**. That one number does three jobs: it quantifies the risk of each blind spot,
it sizes the containment list *in advance*, and it prioritises sensors.

**The cost comparison is not detection-vs-detection.** Reading a coupled station is free —
the sensor is already there. The real comparison is:

> **cost of the blind window** vs **cost of the sensor**

`horizon × fault frequency × cost per affected vehicle` = avoidable loss per year. Buy the
sensor when that exceeds its annualised cost. Two cheaper options to check first: extend an
existing inspection gate, or re-sequence.

**And the output is a dated schedule, not a shopping list.** The brief says instrumentation
changes happen only in a few scheduled windows a year, so the recommendation is: which
sensors go in at the *next* window, ranked by exposure closed per rupee — with **the cost of
deferring the rest to the following window stated explicitly**. Most teams will acknowledge
this constraint in one sentence; making it the shape of the output is the difference between
analysis and a decision.

*(Caveat worth stating: sensors interact — installing at S12 changes the value of a sensor
between S12 and its coupled station. Independent ranking is fine for a prototype, but say so.)*

### 1.6 How we validate all of it

**Switch off a sensor we actually have.** Pretend that station is dark, detect its known
faults using only cycle time and its neighbours' channels, compare against the truth we held
back. That produces a **measured detectability table per fault mode** — which tells us which
bucket each fault is in, justifies every sensor recommendation with evidence rather than
assertion, and is the same demo we already planned for the dark-station flow story.

### 1.7 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 1 — inconsistent coverage, manual checklists | ✅ fully |
| Complexity 4 — defect surfaces at a later inspection point | ✅ detection horizon quantifies it in vehicles |
| Complexity 2 — multi-causal root causes | ⚠️ 3 of 4 (operator variation excluded on ethical grounds) |
| Complexity 3 — retrofits only in maintenance windows | ✅ the schedule is the output |
| Solutioning: handling data gaps + low-cost sensing | ✅ |
| Solutioning: scalability & ROI | ⚠️ partial — the sensor case is computed, wider ROI still open |

---

# Part B — Numbered proposals

## 1 — Sequencing: build the demo first, not last

The Round 2 plan orders phases by dependency, which puts the demo at day ~21. Round 2 is
judged on a **working prototype**, and right now no user-facing artifact exists at all.

**Proposal:** get a thin end-to-end slice running in a browser by day 3, then thicken it.
The loop is closer than the plan assumes — `Detector.verdict(at_s)` is already causal and
windowed, and `timeline()` already steps forward. Workstream B is a wrapper, not a rewrite.

**Status:** `open` — needs Sagar's view, it's his workstream.

---

## 2 — Re-anchor the headline number before it reaches a slide

**"46% / 58%" is the active-period (Roser 2001) number, and we quote it as ours.** Ours
(effective cycle time) is 43.1% / 59.4%.

Our entire credibility strategy is provenance discipline. Being caught attributing Roser's
result to ourselves in a mentored Round 3 would be badly damaging — and it's unnecessary,
because on **regret** we genuinely win: **1.309 vs 1.348 (active period) vs 1.477
(utilisation)** cars/block.

**Proposal:** lead on regret. It's the metric we already argue is the operationally honest
one, and it's actually ours.

**Status:** `open` — I'll do the doc fixes, but we should agree the framing together.

---

## 3 — Fix the Evidence File ceiling before anyone divides

Evidence File §4 attaches "perfect-picker ceiling 2.27, capture ~45%" to the
**strong-constraint** table. 2.271 is the **all-blocks** ceiling. On strong constraints
(n=202) the ceiling is **5.255** and capture is **57.4%**.

As printed, regret 2.24 against a 2.27 ceiling reads as capturing 1% — self-refuting, and
a judge who divides will find it. **The correction makes our result better, not worse.**

**Status:** `open` — mine to fix, flagging so you know the number changes.

---

## 4 — Strip the failed mechanism out of the live path

`detect.py:238` still computes `gap / drift_rate` — that is drift-based overtake risk, the
thing we measured at **5.9% against 70–100% stated confidence** and publicly declared
failed. If the loop emits `Verdict`, the demo ships it.

**Proposal:** replace that slot with the buffer countdown, which is the forming mechanism
that actually works (59.6% of 178 warnings followed by a real block, median error +0.57 min).

**Status:** `open` — your file, Sagar.

---

## 5 — Rank fusion: the cheapest measurable win we have

From `eval_v5.csv`: effective CT gets 19.5% top-1, active period 21.0% — but **either one
is right on 29.5%**, and both are right on only 11.0%.

**The two detectors are making different mistakes.** That's ~8 points of top-1 sitting
unclaimed, and a Borda-count or confidence-weighted fusion should capture a good part of it.

**Proposal:** do this early. Hours of work, a genuine measured result, and nobody else will
have it.

**Status:** `open`.

---

## 6 — Run the sensor-maturity transfer test

The brief asks about variation in "layout, equipment vintage, and **sensor maturity**."
Our L1–L4 test only covers layout.

`Detector(run, use_states=False)` already runs the whole pipeline from boundary scans with
zero PLC tags. Calibrate on a well-instrumented line, deploy on a sensor-poor one, report
the degradation.

**Proposal:** run it. It's one flag, and it's a headline nobody else will have.

**Status:** `open` — mine (Workstream D).

---

## 7 — Add an alert ledger

The brief names "false alarms erode floor-level trust." We have held-out calibration, but
nothing that validates **over time**, which is what the clause actually asks for.

**Proposal:** log every alert → confirmed or overridden → what actually happened → running
precision, shown on the supervisor view: *"right on 24 of the last 34 calls."* Cheap, and
it's the only real answer to that clause.

**Status:** `open` — sits in your Workstream C, Sagar.

---

## 8 — Segments as archetypes, not just a bigger station count

Going from 20 to 40 stations isn't enough on its own. The three segments should behave
differently:

- **Body** — robotic, tight variance, a threshold works
- **Final assembly** — manual, CV 0.25–0.6, needs drift detection
- **Paint** — batch oven, capacity behaves differently from flow

And crucially **sensor coverage should vary by segment** — body rich, final assembly largely
dark. That satisfies the reference parameters *and* makes the observability map a striking
image instead of a uniform grid.

**Status:** `open` — mine (Workstream D).

---

## 9 — Phase the sensor plan by maintenance window

The brief says retrofits happen only during "a small number of scheduled maintenance
windows per year." Our Tier D output is a costed sensor recommendation — it should be
**phased by window**: these four at the spring shutdown, these three in autumn.

Small change, and I doubt any other team will answer that clause at all.

**Status:** `open`.

---

## 10 — Lead the business case with CONWIP

Our measured release-rate result — **same throughput, 36% lower lead time, zero capital
expenditure** — is the most defensible ROI line in the project, and it's currently buried.

Every other value line needs assumptions about margin and volume. This one is a scheduling
policy, so its payback is immediate by construction.

**Status:** `open` — Workstream G, both of us.

---

## 11 — ISA-101 for the supervisor view

Grayscale base, colour reserved strictly for deviation (yellow = warning, red = alarm,
blue = action needed). A well-designed plant HMI is **visually quiet during normal
operation**.

This is the opposite of the instinct to build a colourful dashboard, and that's the point —
a grey screen that erupts in colour only when a constraint forms reads as built by someone
who has stood on a plant floor. Leadership view can use colour; it's a business dashboard.

Also worth displaying: alert count against the ISA-18.2 budget of **<150 actionable alarms
per shift**.

**Status:** `open` — Workstream E, both of us.

---

## 12 — Define windows in units, not seconds

A 30-minute window holds ~30 units at 60s takt and ~50 at 35s takt. The statistics behave
completely differently and nothing in the code signals that anything changed.

This is a hidden per-line constant masquerading as a global, and it would quietly break the
transfer claim.

**Status:** `moved` → **Locked decisions** in `PROGRESS.md`.

---

## Sagar's responses

| # | Response | Outcome |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |
| 11 | | |
