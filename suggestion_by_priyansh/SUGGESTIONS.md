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

## Complexity 2 — Multi-causal, intermittent root causes

> *"Bottlenecks and defects often have multi-causal, intermittent root causes (equipment
> wear, operator variation, upstream part quality, environmental conditions) that are hard
> to isolate from data alone."*

**Status:** `open` — needs Sagar's review. Adds `zone_id` to layout config and a confounded
scenario mode to the generator (my files); the co-occurrence engine is new and unowned.

### 2.1 Why it's hard

The four causes are **correlated with each other** (ambient rises in the afternoon; the
afternoon is also shift 2; shift 2 also runs a different variant mix). Intermittent means
**tiny sample size** and **no reproduction on demand**. And multi-causal usually means
**interaction** — A alone fine, B alone fine, A+B fails.

Note the brief's own wording: *"hard to isolate from data alone."* It is telling us
correlation won't get there. Our answer takes that seriously rather than throwing a model at it.

### 2.2 The core move — isolate by **scope**, not by statistics

Each cause leaves a different fingerprint in **how far the correlation spreads**. We don't
disentangle them statistically; we tell them apart structurally.

| Root cause | Shape in time | Who else is affected |
|---|---|---|
| Equipment wear | slow monotonic drift | **this station only**, persistent |
| Upstream part quality | step change | **every station on that lot**, none on other lots |
| Environmental | slow cyclic | **every station in that zone**, regardless of lot |
| Operator / practice | step at shift boundary | **this station**, shift-periodic |

Needs four identifiers we already have or can add cheaply: `station_id`, `material_lot_id`,
`zone_id`, `shift_id`. No new sensors.

**The negative control is the whole argument.** 21 of 23 tools on the bad lot alarmed and
**zero** on other lots. A shift or ambient effect would have moved those too. That is
correlation *with a control*, which is categorically stronger than correlation.
**Always look at who is fine, not just who is broken.**

### 2.3 Intermittent doesn't mean random — it means conditional

An intermittent fault is almost never random. It is **conditional on something not yet
measured** — a variant, an ambient threshold, the first 20 minutes after a break, a supplier.
So we stop asking "why is it unpredictable" and ask "**what else is true when it happens**",
which turns intermittency into an estimable conditional effect.

Two supports for the low-sample problem: CUSUM accumulates weak evidence over time rather
than needing a big window, and pooling across an equipment family (then testing both pooled
and individual) separates a family-level issue from a single-tool one.

### 2.4 Natural experiments the plant already runs

Free, and nobody reads them:

| Experiment | What it settles |
|---|---|
| **Parallel twin comparison** — two servers, same operation, same lot, shift and air | **Definitively equipment.** Everything else held constant by construction. We already have a parallel pair in L3 |
| **Did it follow the tool?** — `tool_serial` appears at a different station after a swap | Tool vs fixture / position / practice |
| **Lot boundary before/after** | Material, with a clean control period either side |
| **Variant stratification** | Line balancing vs equipment |

### 2.5 What goes in the prototype

| Component | State |
|---|---|
| Five grouping tags on every event | ✅ have four; **`zone_id` missing** — one line in layout config, and without it "environmental" and "material" both just look like *many stations at once* |
| **Change register** — timeline of everything that changed (lot, shift, variant, maintenance, calibration, tool move, changeover, ambient excursion, break) | ❌ new. This is what produces the *"couldn't rule out"* line |
| **Co-occurrence engine** — on alarm, build a contingency table per grouping dimension (alarmed/not × in-group/out-group) and score concentration | ❌ new, ~60 lines. No model, no training. **This is the core piece** |
| **Signature classifier** — drift / step / cyclic / shift-step | ⚠️ mostly have (shift ratio, spread ratio); add time-shape |
| **Natural-experiment queries** — the four above | ❌ new, but they are database queries, not models |
| **Ranker + experiment proposer** | ❌ new |
| **Cause panel** in the UI | ❌ new |

**Output contract — never a single cause.** Ranked hypotheses with confidence, the evidence
(*who else, and who not*), the **confounders not ruled out**, and either a recommended action
or a proposed test. When the top two are within ~15 points, propose the cheapest separating
test instead of guessing — e.g. *"swap tools between S22 and S24 at the next planned stop;
if the effect follows the tool it's the tool. 20 minutes."* That is the direct answer to
*"hard to isolate from data alone."*

### 2.6 The demo scenario we must be able to generate

**Easy to miss:** our generator currently injects faults one at a time. We cannot demonstrate
untangling multiple causes if only one cause is ever present. Add a **confounded scenario
mode** — two overlapping causes, both truths recorded:

> Bad lot enters 09:40. Ambient rises 4°C at the same time. Two tools are genuinely wearing.
> Truth: 18 affected by the lot, 2 by wear, 0 by ambient.

The naive view shows 20 tools alarming at once and the plant looks like it is falling apart.
The twin says: *"18 share lot L-4471 and no tool outside it is affected — hold the lot. Two
are unrelated and genuinely wearing. Ambient moved, but other zone tools are flat, so it
isn't that."* **Thirty seconds, and the clause is answered.**

### 2.7 How we score it

Because we own the simulator the true cause is known, so this is measurable rather than claimed:

- Cause attribution **top-1**
- Cause attribution **on confounded scenarios** — the hard case: does it find *both*?
- **Calibration** — when it says 68%, is it right ~68% of the time
- **False attribution rate** — how often it confidently blames the wrong cause

Nobody will report cause-attribution accuracy on deliberately confounded scenarios. That is a headline.

### 2.8 What we will not build

A causal-graph / do-calculus engine (needs assumptions we cannot verify, unexplainable in
five minutes — scope plus shape does the job with arithmetic); a deep model; and anything
that outputs a single cause.

Gradient boosting is allowed in exactly one role: surfacing which **combinations** of
conditions co-occur with failure, since trees find interactions naturally. It is a
**hypothesis generator, never a conclusion** — anything it surfaces must be confirmed by a
natural experiment or ruled physically plausible.

### 2.9 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 2 — multi-causal, intermittent root causes | ✅ all four causes; operator identified by scope but **never attributed to an individual** |
| Solutioning: predictive techniques, *"how you'd validate before trusting output"* | ✅ negative controls and natural experiments **are** the validation |
| Complexity 7 — false alarms erode trust | ⚠️ partial — "couldn't rule out" and proposed tests reduce confident wrong calls |

---

## Complexity 3 — PLC risk and maintenance windows

> *"Modifying live production systems (PLCs, line control logic) carries real operational
> risk, and most plants only allow retrofits during scheduled, infrequent maintenance
> windows."*

**Status:** `open` — needs Sagar's review. The read-only enforcement test touches `tests/`
(shared); shadow mode falls out of Workstream B (his).

Two separate claims in one sentence: a **risk** constraint and a **timing** constraint.

### 3.1 The read-only boundary, made credible

We already say *the twin advises, never writes*. Three things turn that from an intention
into something a plant engineer believes.

**Use the standard vocabulary.** Under ISA-95 / the Purdue model, the twin reads at Level 3
(MES, historian) and subscribes read-only at Level 2 (SCADA). It never touches Level 0–1
(sensors, actuators, **PLCs, control logic**).

**Explain why it matters operationally, not architecturally.** This table is the argument:

| Touching Level 1/2 needs | Reading at Level 3 needs |
|---|---|
| Safety case re-validation | Network access |
| Possible functional-safety re-certification | Cybersecurity review |
| Regression testing of control logic | Historian permissions |
| A shutdown window, safety-engineering sign-off | — |
| **Quarters to years** | **Weeks** |

**Enforce it in code — don't assert it.** Our own discipline (*prove the boundary, don't
claim it*) applied to integration: configure the OPC-UA session read-only, firewall to
outbound-only with no inbound to OT, and **write a test that fails if anyone ever adds a
write path**. Then in the pitch we show the test rather than ask to be believed.

### 3.2 Three risk classes — the distinction most solutions blur

| Class | What it is | Risk | Needs |
|---|---|---|---|
| **1. Passive tap** | Subscribe to data already published | none | network access |
| **2. Additive sensing** | Sensor bolted on, publishing to **our** gateway | low | a window, a technician |
| **3. Control modification** | Change setpoints or logic | high | **never** |

The brief asks about **retrofits** — class 2, and class 2 is achievable. Most write-ups
treat any hardware change as class 3 and conclude nothing can be done.

**Design rule:** every sensor we propose publishes to our own gateway, **never into the
PLC**. Same device either way — but on our network it is a technician job in a routine
window; wired into a PLC input card it is a controls-engineering job with a safety sign-off.

*(The analogy that lands: a dashcam fits in 20 minutes, self-driving takes years of
certification. Same car — one watches, one acts.)*

### 3.3 The question a plant-experienced judge will ask

*"How did you get network access, and who signed off?"*

OT is segmented from IT; the governing standard is **IEC 62443** and the accepted pattern is
a DMZ with controlled traffic. Read-only makes this far easier — the twin runs IT-side,
reads a historian replica in the DMZ, holds read-scoped credentials, and opens **no inbound
connection to OT at all**. A system that cannot write has a much simpler threat model, which
is a second independent reason the boundary is right.

### 3.4 The maintenance window as a planning object

Extends the sensor scheduling from Complexity 1 in two ways.

**Everything requiring a stop goes in one plan** — not just sensors but buffer resizing,
station rebalancing, adding a parallel server. Batched by window, ranked, with cost of deferral.

**And the twin plans the window itself.** A shutdown has finite hours and technicians, so
you cannot do everything. It is a selection problem, and the twin is the only system holding
the value of each candidate job:

> *"March window: 3 days, 4 technicians. Optimal set is these five jobs — closes ₹38L of
> annual exposure. The three deferred to September cost ₹4L over the wait."*

### 3.5 Deploying the twin itself without disruption

The solutioning area asks about deploying **the twin**, not the sensors. Four phases:

| Phase | What happens | Risk |
|---|---|---|
| **1. Shadow** | Runs, predicts, shows nobody. Compared afterwards against what happened | zero |
| **2. One supervisor** | One person sees it, free to ignore it; ledger records action and outcome | zero |
| **3. Floor-wide advisory** | Rolled out once the ledger shows precision holds | zero |
| **4. Closed loop** | **Never** | — |

**Phase 1 is nearly free** — our replay driver *is* shadow mode. Replaying a recorded shift
and comparing recommendations against the actual outcome is exactly what a shadow deployment
does, so Workstream B produces it as a by-product.

This phasing is also the spine of the **phased roadmap**, a named Round 2 deliverable we
don't currently have — so this clause and that gap close together.

### 3.6 What goes in the prototype

| Item | State |
|---|---|
| Architecture figure — ISA-95 levels, **directional arrows** | ❌ new — a diagram, not code |
| **Read-only enforcement test** — fails if a write path is added | ❌ new, tiny, high credibility |
| **Window planner** — given capacity, select the best set of jobs | ❌ new, small |
| **Shadow mode** as an operating mode of the loop | ✅ nearly free — it's replay |
| Sensor recommendations tagged *"our gateway, no PLC change"* | ⚠️ extend the Complexity 1 output |

### 3.7 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 3 — PLC risk + maintenance windows | ✅ both halves |
| Solutioning: integration approach, *"without disrupting ongoing operations"* | ✅ the four-phase rollout |
| Reference parameter — instrumentation only in scheduled windows | ✅ the window planner |
| Deliverable: **phased roadmap** | ✅ partial — this is its spine |

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
