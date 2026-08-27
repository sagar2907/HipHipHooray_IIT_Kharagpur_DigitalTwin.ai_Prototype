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

**Status:** `accepted` (2026-08-27, Sagar) — both schema proposals (`manual_check`, `attested`)
built against in a local draft of the 40-station segmented layout, see `PROGRESS.md` Work log
2026-08-27. Not pushed — flagged for your review since `layouts.py`/`plant.py` are Workstream D.

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

## Complexity 4 — Late-surfacing defects and containment

> *"A defect introduced early in the line may not surface until a much later inspection
> point, by which time many downstream units may carry the same undetected issue — making
> root-cause tracing after the fact especially difficult."*

**Status:** `open` — needs Sagar's review. Onset estimation depends on the CUSUM fix
(defect #5, his file); containment and stop-or-continue are Workstream F, joint.

Three problems in one sentence. **The first is already solved** by Complexity 1
(process monitoring + detection horizon), so this covers the other two.

| Part | Problem | Status |
|---|---|---|
| (a) introduced early, surfaces late | lead time | ✅ done in C1 |
| (b) many downstream units carry it | **containment** | ❌ new |
| (c) tracing after the fact is hard | **forensics** | ❌ new |

### 4.1 Containment — onset, not detection

**"When it started" and "when we noticed" are different moments, and the gap is the exposure.**

A CUSUM gives us onset for free: the accumulator sits at zero while healthy and lifts off at
onset, crossing threshold later at detection. So we read backwards down our own counter to
find the start. **This only works if the counter actually accumulates** — our current code
recomputes each window, so there is no history to read back. Another reason defect #5 matters
more than it looked.

Onset is uncertain, so output **three bands, not a hard line**: definitely affected /
possibly affected / probably clear. The middle band is where an inspector goes rather than a
teardown. The cut-off sits where the **cost asymmetry** puts it, not at 50% — under-containing
ships escapes, over-containing scraps good cars, and those costs differ by orders of magnitude.

### 4.2 Where the units are — the part that makes cost concrete

38 affected vehicles are not in the same place, and the fix cost differs by orders of magnitude:

| Location | Action | Relative cost |
|---|---|---|
| Still on the line | Divert | **1×** |
| Finished-vehicle yard | Recall to rework | **~10×** |
| Shipped | Warranty campaign | **~100×** |

So containment output is **partitioned by location**. This is also the sharper argument for
early detection: not merely "fewer units affected", but **units get more expensive every
minute they sit undetected** as they migrate line → yard → customer.

### 4.3 Forensics — replay and backward attribution

**Flight recorder.** Every alert, record and **model refit** logged with timestamps, so the
shift can be replayed exactly as it stood. After an incident the only question is *what did
the twin know and when* — and a silently refitted model cannot be reconstructed, which is why
refits are logged.

**Backward attribution.** When a cluster of EOL failures appears, join back through genealogy
and ask what they share — station, tool, lot, shift. That is **C2's co-occurrence engine run
on outcome data instead of alarm data.** Same code, different input.

### 4.4 Stop-or-continue — corrected

*(An earlier draft said "high P(constraint) → wait for the break". That is wrong as stated.
Bottleneck status is not the deciding factor — where the defects go is.)*

**The decisive question is what happens to the bad parts:**

| Escape route | What we're producing | Decision |
|---|---|---|
| Safety-critical joint | unacceptable risk | **Stop. No calculation.** |
| Escapes — nothing downstream catches it | warranty, possible recall | **Stop.** Escape cost dominates |
| Caught at EOL or a gate | rework, not escapes | **Economics apply** |

The economics only apply in the third row, and there: **a car reworked is not a car lost.**
Throughput lost at a bottleneck is permanent; a reworked car still gets built and still sells.

**Two things dissolve most of the dilemma:**

1. **At detection, scrap usually hasn't started.** Our measured warning is 421–1,322 vehicles
   before sustained scrap. So the choice is rarely "stop, or make 22 defective cars" — it is
   "stop, or make 22 more *good* cars and fix it at the break, with 400 units of runway left."
   The question is not *is it defective now* but *how much damage accumulates before the next
   planned stop* — the integrated hazard, which is near zero early in degradation.

2. **Stopping a station is not stopping the line.** That is what buffers are for. Our layouts
   carry 1–4 units, so at 60s takt there is **1–4 minutes of free single-station stoppage**.
   A tool swap (2–3 min) or recalibration (3–5 min) often fits inside it at zero throughput cost.

So the real question is: **what is the cheapest intervention that fixes this, and does it fit
in the buffer time available?** We already model buffer levels per station, so the twin can
compute the free-stop window at any moment and only escalate to "wait for the break" when
nothing fits.

**Corrected logic:**

```
1. Safety-critical?                     -> STOP, no calculation
2. Will it escape undetected?           -> STOP, escape cost dominates
3. Caught downstream (rework, not escape):
   a. Has scrap actually started?       NO -> runway exists, schedule it
   b. Cheapest fix fits in the buffer?  YES -> do it now, costs nothing
                                        NO  -> compare damage-until-next-stop
                                               vs cars permanently lost
```

**Bottleneck status only enters at the final step**, by which point most cases are already resolved.

When it genuinely is the bottleneck, *is* producing escapes, and the fix needs 40 minutes,
there is no clever answer. The twin puts both numbers on screen — *"stopping now costs 38
cars; continuing to the break ships ~14 escapes at ₹X"* — and a human decides, with a record
of what they were shown. The value is not that the system decides; it is that the person
deciding can see both sides of a trade-off that in every real plant is split across two
systems that never talk.

### 4.5 What goes in the prototype

| Item | State |
|---|---|
| **Onset estimation** from the CUSUM accumulator | ❌ new, small — needs a real CUSUM first |
| **Graded containment list** — 3 bands | ❌ new |
| **Location partition** — on-line / yard / shipped | ❌ new; this is what makes cost concrete |
| Cost-asymmetric containment boundary | ❌ new, small |
| **Free-stop window** from downstream buffer level | ⚠️ small — we already model buffer levels |
| Intervention menu with durations (swap / recalibrate / divert / repair) | ❌ new, a lookup table |
| **Audit log + replay** | ✅ nearly free from Workstream B |
| **Backward attribution** from EOL clusters | ✅ reuses C2's co-occurrence engine |
| Stop-or-continue | ❌ new — Workstream F |

### 4.6 The demo

> **S22 — drifting since 10:14 (±6 min). Detected 10:52. Scrap not yet started (~380 units runway).**
> **38 vehicles built since:** 12 on line · 21 in yard · 5 shipped.
> Defect would be caught at EOL, so this is rework, not escapes.
> Cheapest fix is a tool swap, 3 min. Downstream buffer holds 3 units = **3 min free.**
> **Recommend: swap now. Zero throughput cost.**

### 4.7 How we score it

We inject the fault, so the truth is known:

- **Onset estimation error** — estimate vs true injection time
- **Containment recall** — did we catch every affected unit?
- **Containment precision** — how many good units did we sweep in?
- Lead time (T2 − T1) — already have

Containment precision/recall is measurable only because we built the plant. Nobody else will report it.

### 4.8 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 4 — late surfacing, downstream units, hard tracing | ✅ all three parts |
| Gap list: **genealogy containment** — the most explicitly-named capability we lack | ✅ specified |
| Complexity 7 — validated against outcomes over time | ⚠️ partial — the audit log is the substrate |

---

## Complexity 5 — Three stakeholder views

> *"Different stakeholders need very different views of the same twin — a floor supervisor
> needs real-time, in-the-moment signals, a plant manager needs weekly planning trends, and
> leadership needs a rollout business case."*

**Status:** `open` — needs Sagar's review. This is Workstream E (joint); the record stream
it renders comes from his Workstream B.

The three personas are the easy part. **The interesting word is "same."** Anyone can build
three dashboards; the claim worth making is that these are three views of *one twin* — and
that is provable rather than assertable.

### 5.1 The proof — a reconciliation test

```
leadership annual figure == sum of manager weekly figures
manager weekly figure    == sum of supervisor per-minute records
```

Write it as a test. If it fails we don't have one twin, we have three products that will
drift apart the first time one is patched. Same move as the read-only enforcement test in
C3: **assert the architectural property in code rather than claiming it in a diagram.**

### 5.2 The three decisions differ on two axes, not one

| | Time to decide | Time to reverse | Cost of being wrong |
|---|---|---|---|
| **Supervisor** | seconds | minutes | a wasted walk |
| **Manager** | hours | a week | a misallocated shift |
| **Leadership** | a quarter | years | a capital programme |

**So the same number surfaces at a different confidence threshold in each view.** A
supervisor can act on 60% because being wrong costs a two-minute walk; leadership cannot fund
a rollout on 60%. The confidence gate is **per view, not global** — only possible because our
confidence is calibrated rather than asserted, so this is a direct payoff from that decision.

### 5.3 The manager's view is NOT the supervisor's view averaged

Our own measurement exposes the trap: **the constraint moves ~6× per shift**, so "the
bottleneck last week" describes a station that was constraining maybe 15% of the time. The
manager needs a **different statistic over the same records**, not a coarser one.

| ❌ Wrong | ✅ Right |
|---|---|
| "Average bottleneck: S12" | **Constraint occupancy heatmap** — station × time, where constraints *recur* |
| "Average confidence" | **Sole vs shifting periods** (Roser 2002) — how much of the week had a dominant station at all |
| "Average buffer level" | Which buffers *threatened*, and how often |

The heatmap earns its place because it reveals what is invisible at both other timescales —
e.g. *"S07 constrains for two hours after every changeover."* Actionable only at this timescale.

### 5.4 What each view must NOT show

ISA-101 names the failure directly: embedding lower-level detail on upper-level screens.

| View | Must not show |
|---|---|
| Supervisor | Weekly trends, ROI, model internals — none of it changes where they walk next |
| Manager | Per-second state — noise at their timescale |
| Leadership | Station detail they cannot act on |

**One inversion, stated loudly: leadership must see the negative results.** The failed
overtake risk, the unvalidated dark localisation, the two-regime split rather than a blended
accuracy number. They are the audience deciding whether to *fund a rollout*, and a business
case resting on capabilities that don't work is a false prospectus. **The leadership view is
where honesty matters most, not least.**

### 5.5 Leadership's view is live, not a slide

The twin computes these numbers, so the view recomputes continuously — cars recovered to
date, sensor spend recommended, payback tracked. And the feature nobody will have:

> **Actual vs forecast.** *"We said this sensor would save ₹10L/year. Twelve months in,
> measured saving: ₹8.4L."*

That is the trust ledger applied to money — the same *validated against outcomes over time*
discipline the brief demands, pointed at the business case. It is the difference between a
projection and a track record.

### 5.6 Adoption risk is asymmetric — and it all sits on one screen

Managers and leadership *consume* reports. **The supervisor is the only user who can kill the
system by ignoring it**, and the brief says exactly how: false alarms erode floor trust.

So three things live permanently on the supervisor view, none of which help find the
constraint but all of which decide whether the tool is still in use in month three:

- The **trust ledger** — *"right on 24 of the last 34 calls"*
- **Override in one click**, logged
- **Alarm count against budget** — *"37 this shift, budget 150"*

### 5.7 What goes in the prototype

| Item | State |
|---|---|
| One record stream as the single source | ✅ Workstream B produces it |
| Three aggregators — per-minute (identity), per-week, per-quarter | ❌ new, small |
| Three renderers over those aggregators | ❌ new — Workstream E |
| **Reconciliation test** | ❌ new, tiny, high credibility |
| Per-view confidence thresholds | ❌ new, small |
| **Constraint occupancy heatmap** | ❌ new — the manager view's core visual |
| Actual-vs-forecast on the leadership view | ❌ new |
| Trust ledger + override + alarm budget on supervisor view | ⚠️ ledger is Workstream C |

**Not React. Not three apps.** One page, three tabs, ISA-101 grayscale on the supervisor view.

### 5.8 How we prove it in the demo — about 40 seconds

1. **Switch views live on the same running data** — not three screenshots
2. **Trace one alert through all three** — an instruction on the floor, a recurrence pattern
   to the manager, a line item in recovered throughput to leadership
3. **Show the reconciliation test passing**

### 5.9 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 5 — three stakeholder views | ✅ fully |
| Solutioning: user experience, *"from the same underlying model"* | ✅ provably, via reconciliation |
| Complexity 7 — false alarms erode trust | ⚠️ partial — ledger and alarm budget made visible |
| Deliverable: business case | ⚠️ partial — the leadership view is its live form |
| Gap list: **three stakeholder views** | ✅ specified |

---

## Complexity 6 — Scaling across lines, plants and sites

> *"Extending a solution beyond a single line or plant means accounting for real variation
> in layout, equipment vintage, and sensor maturity across different sites."*

**Status:** `open` — needs Sagar's review. Workstream D (mine). **Two of the three
experiments need no new code and have never been run.**

Everyone claims their solution generalises. The difference is whether the experiment was run.

### 6.1 Ask "how long until it works", not "does it work"

"It transfers" is three questions: **zero-shot** (calibrate on A, deploy on B cold),
**few-shot** (how much B data before recovery), and **ceiling** (fully fitted on B).

The useful output is not one number but a **transfer curve** — performance against amount of
target-line data. And the curve *is the commissioning estimate*:

> *"70% of full performance on day one, 90% after a week, 100% after a month."*

That is the sentence a customer actually wants, and it is the same experiment either way.
The method transfers even though the local knowledge does not — like a driving instructor
moving city: the teaching skill comes along, the knowledge of which junctions are dangerous
has to be relearned.

### 6.2 What actually breaks, per axis

| Axis | Variation | Risk |
|---|---|---|
| **Layout** | Station count | low — windows already in units, not seconds |
| | Merges / feeders | low — topology is config |
| | Buffer capacities | **medium** — our own finding was that tighter buffers are what made the constraint visible, so the distribution changes the dynamics |
| | **Parallel stations** | **high** — breaks the pure-series assumption under the arrow / turning-point methods. L3 exists for exactly this and has never been run |
| **Vintage** | MTBF, MTTR, variance | low — fitted per line |
| | Protocols, tag granularity | low — adapter |
| | **Sampling rate** | **high, and subtle** — see below |
| | Genuinely different failure modes | **classifier does not transfer**, must be refit per equipment family |
| **Sensors** | Fewer channels | handled — health score aggregates what's present, confidence drops (C1) |
| | No PLC state tags | the `use_states=False` path |
| | Higher dark density | tier ladder handles it, but **measure the degradation** |

**On sampling rate:** if line A reports per unit and line B once a shift, that is not the
same detector with different parameters — **some detectors stop working**, because CUSUM on
three samples a day cannot accumulate. That is a capability boundary, not a tuning problem,
and the observability map should say so rather than implying a setting fixes it.

### 6.3 What makes two lines "close enough"

If we claim transfer we need a **distance between lines**. Six cheap dimensions:

`station count · takt · buffer capacity distribution · instrumented fraction · variant count · segment mix`

Then plot transfer performance against that distance, giving a real claim —
*"transfer holds within X; beyond it, refit"* — rather than "it should generalise".

### 6.4 Rollout economics — costs don't divide evenly per line

| Cost | Charged |
|---|---|
| Platform (detectors, model, interfaces) | **once, ever** |
| Cybersecurity + network review | **per site** |
| Adapter writing | per line (days) |
| Fitting period | per line (weeks, but passive) |
| Threshold calibration | per line |

Three genuinely different tiers: **first line ever** (platform + site + line), **second line
same plant** (line only — network already approved), **first line new plant** (site + line,
no platform). **Payback shortens sharply after line one, and again after plant one** — a far
more credible rollout case than a flat per-line figure.

### 6.5 What we can run today — the actionable part

| Experiment | Effort | Status |
|---|---|---|
| **Layout transfer** — calibrate on L1, test on L2 / L3 / L4 | already built | ❌ **never run** |
| **Sensor maturity** — `Detector(run, use_states=False)`, rich → poor | **one flag** | ❌ **never run** |
| Equipment vintage cohorts | new generator work | ❌ not modelled |

The first two produce publishable transfer numbers with essentially no new code. Since "how
would this extend to other sites" is a named solutioning area that we currently answer with
an *argument* rather than a *measurement*, **this is the highest value-per-hour item anywhere
on our list.**

### 6.6 Decompose the transfer loss — don't report one number

| What degraded | Meaning | Severity |
|---|---|---|
| **Ranking** — picks the wrong station | The method doesn't transfer | **serious** |
| **Calibration** — right station, wrong confidence | Needs a week of local data | **minor** |

Same drop in score, completely different problem and completely different fix. Report
Δ regret zero-shot, **which component degraded**, and shifts-to-recovery.

### 6.7 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 6 — layout, vintage, sensor maturity | ⚠️ two axes measurable today; vintage needs generator work |
| Solutioning: scalability & ROI | ✅ transfer curve + three-tier rollout economics |
| Gap list: layout transfer, sensor-maturity transfer | ✅ specified, **and runnable now** |
| Deliverable: business case | ⚠️ partial — rollout tiers are its scaling half |

---

## Complexity 7 — Validation over time, and floor trust

> *"Predictive claims must be validated against real outcomes over time — false alarms about
> defects that don't materialise can erode floor-level trust in the system quickly."*

**Status:** `open` — needs Sagar's review. The ledger is Workstream C (his); the override and
abstention display are Workstream E (joint).

We are strongest here — held-out calibration, firewall set, economic ground truth, negatives
reported at equal prominence. But note the two words doing the work: **"over time."**
Everything we have validates at a *point* in time on a *fixed* dataset. Continuous validation
in production is a different problem, and it is the half we haven't built.

### 7.1 The label delay problem

Truth does not arrive when the alert does. It arrives in three waves, so the ledger always
holds **pending** entries and precision must be reported **per tier**:

| Tier | Label source | Delay |
|---|---|---|
| Immediate | Supervisor confirms / overrides | minutes |
| Short | EOL test result | ~40 min |
| Long | Warranty / field failure | months |

"We're 70% accurate" without naming the tier is meaningless, and it is the commonest way this
number gets quietly inflated.

### 7.2 The override button is our fastest label source

This reframes what it is for. **It is not a courtesy to the operator — it is our primary data
collection mechanism**, and the only label that arrives in minutes rather than months.

Therefore: **one click** or it won't be used; capture *why* (wrong station / not worth it /
already knew / it's fine); and never discard overrides — a system that throws them away is
discarding its best feedback.

### 7.3 Rolling calibration, and monitoring the monitor

Recompute the reliability diagram on a **trailing window**, not once — a detector calibrated
in August is not necessarily calibrated in November after a changeover or a tooling swap.

And watch our own precision over time. If it falls from 70% to 45% across three months,
nobody would notice. We already built twin drift for the model; this is the same idea for the
detector. **A system whose performance silently degrades is worse than no system, because
people still trust it.**

### 7.4 Trust is asymmetric — precision dominates recall for adoption

One false alarm costs far more than one true alarm gains. A supervisor remembers the wasted
walk; the useful call becomes background. A missed detection is *invisible* — they never knew
it existed. A false alarm is visible and irritating.

This conflicts with the safety view where recall matters, and the resolution is a principle
we already half-have as two separate mechanisms:

> **Separate "what we detected" from "what we tell you." Detect everything. Alert on little.
> Log the rest.**

That is the suppress-without-evidence rule plus the persistence filter, stated as one idea.

### 7.5 The ledger is how trust *recovers*, not just how it's measured

The point most easily missed. **Without a ledger, lost trust cannot be regained** — one bad
week becomes a permanent impression because there is no counter-evidence, only a feeling that
the thing cries wolf.

With **"right on 24 of the last 34 calls"** on screen, the supervisor recalibrates against
data instead of memory. That is why the ledger belongs on the supervisor view permanently
rather than in a monthly report.

### 7.6 Silence must be visible

On 35.7% of blocks no station dominates, and a system that stays quiet there is **behaving
correctly**. But a blank screen reads as *broken*. So abstention is displayed explicitly —
*"Monitoring. Nothing dominates — the line is balanced."* — or correct behaviour looks like a
fault and someone reboots it.

### 7.7 Our self-audit already answers this clause

Worth saying plainly, because it maps directly and it is our strongest asset:

| What we did | Why it is this clause |
|---|---|
| Overtake risk: stated 70–100%, right 5.9% → **cut** | A predictive claim validated against outcomes and abandoned |
| "Zero false alarms" → really ~1 per 5 tool-weeks | A claim corrected once measured properly |
| A detector scoring 95.2% → an identity, not a result | Validation that caught itself |
| Two regimes reported separately, never blended | Refusing a flattering average |

**Four of the six self-catches are literally "a predictive claim validated against real
outcomes and found wanting."** In a mentored Round 3 that is not a weakness to explain — it
is the evidence for this clause.

### 7.8 What goes in the prototype

| Item | State |
|---|---|
| **Alert ledger** — three maturity tiers, pending state | ❌ new — Workstream C |
| Running precision **per tier**, displayed | ❌ new |
| **One-click override with reason code** | ❌ new — the label source, not a courtesy |
| Rolling reliability diagram | ⚠️ have the method; needs to run on a window |
| **Performance drift monitor** — precision over time | ❌ new, small |
| **Abstention shown explicitly** | ❌ new, tiny, high value |
| Alarm count vs ISA-18.2 budget (<150/shift) | ❌ new, trivial |

### 7.9 How we score it

Precision **at the alerting threshold**; precision **by maturity tier** (never blended);
rolling calibration error; alarm rate vs budget; and **time-to-trust** — how many alerts
before the precision estimate stabilises. If it takes 200 alerts to know our precision and we
raise 30 a shift, that is a week before the number means anything, and that is a deployment
fact worth stating rather than hiding.

### 7.10 What this closes

| Brief clause | Covered |
|---|---|
| Complexity 7 — validation over time, false alarms erode trust | ✅ design complete; ledger unbuilt |
| Solutioning: predictive techniques, *"how you'd validate before trusting output"* | ✅ |
| Gap list: alert ledger | ✅ specified |

---

# Part A summary — all seven complexities

| # | Complexity | Status |
|---|---|---|
| 1 | Inconsistent sensor coverage | ✅ fully |
| 2 | Multi-causal, intermittent causes | ✅ all four causes |
| 3 | PLC risk + maintenance windows | ✅ both halves |
| 4 | Late-surfacing defects | ✅ all three parts |
| 5 | Three stakeholder views | ✅ fully, and provably |
| 6 | Scaling across sites | ⚠️ two axes runnable now; vintage needs generator work |
| 7 | Validation over time + trust | ✅ design complete; ledger unbuilt |

**Six and a half of seven on paper. The gap between *specified* and *built* is now the entire
remaining risk** — which is what the status board has said since day one.

---

# Part C — Solutions to the Solutioning Areas

One entry per Solutioning Area from the brief. Statement first, then the solution.

**Coverage note:** three of the six are already answered in full inside Part A, so those
entries cross-reference rather than repeat. The genuinely open ones are 1, 2 and the ROI
half of 6.

| # | Solutioning area | Where it's answered |
|---|---|---|
| 1 | Modelling approach | **below** |
| 2 | Predictive techniques + validation | ✅ **below** |
| 3 | Handling data gaps + low-cost sensing | ✅ **Complexity 1** + **Solution 3** (sensing menu) |
| 4 | User experience | ✅ **Complexity 5** |
| 5 | Integration approach | ✅ **Complexity 3** |
| 6 | Scalability & ROI | ✅ scaling in **Complexity 6** + **Solution 6** (ROI) |

---

## Solution 1 — Modelling approach

> *"Modelling approach — what to represent explicitly (cycle time, torque, vibration,
> temperature, throughput) versus infer indirectly, especially at sensor-poor stations."*

**Status:** `open` — needs Sagar's review. Touches the shared schema and `plant.py` (mine).

### C1.1 The rule, and four tiers not two

**Model what propagates on the timescale of your decision and can actually be observed.
Collapse everything else into a distribution.**

The brief implies two buckets; there are four. The last two matter because "we don't model
weld physics" sounds like an omission until you say "we model its outcome distribution
instead", at which point it is a scoping decision.

| Tier | Meaning | Example |
|---|---|---|
| **Represent explicitly** | It propagates through the system | Processing times, buffer levels |
| **Infer indirectly** | Can't see it, can reason to it | Dark-station state, micro-stops, true clamp force |
| **Collapse to a distribution** | Matters only through its outcome | Weld physics, robot kinematics |
| **Skip** | Changes nothing we decide | 3D geometry, CAD visuals |

### C1.2 The five quantities the brief names

**Cycle time** — explicit, as a **distribution including the tail**, not a mean. 55s ± 2s
behaves nothing like 55s with occasional 90s excursions, and the difference surfaces
downstream as starvation. Critical move: decompose observed **dwell** into **processing**
(work) and **waiting**. Dwell is what we measure; processing is what we need.

**Torque** — explicit at fastening stations, nearly free because safety-critical joints are
legally traceable. Subtlety: *measured* and *applied* value are conceptually distinct, and
their divergence is the sensor-fault signature. In a plant we only ever hold the measured
one, so what we actually represent is **the relationship between channels** — torque flat
while current and angle move means the tool is degrading and the sensor is lying.

**Vibration** — **an honest gap.** Accelerometers are a retrofit, not existing plant data, so
vibration belongs in the costed sensor recommendation rather than the base model. **Motor
current is its free proxy** — current signature analysis is established for motor-driven
equipment, and the controller already reports it.

**Temperature** — two different roles, and conflating them causes false alarms. Tool
temperature is a *secondary degradation channel*; ambient is a *shared confounder* coupling
every tool in a zone. Without ambient explicit, a warm afternoon looks like forty tools
failing at once.

**Throughput** — **not a primitive.** It is emergent from stations, buffers, variants and the
calendar. Model it directly and we have built a regression on the outcome, confidently wrong
the first time the line changes. Its correct role is the **comparison surface** — predicted
vs observed over a trailing window *is* the twin-drift metric. Making it an output is what
makes drift measurable at all.

### C1.3 At sensor-poor stations: represent the doors, infer the room

We can see the doorway, not the room. So the split is clean:

**Represent — all measured, all at the edges, all free:**
car in-time · car out-time · buffer level before · buffer level after · neighbour states ·
variant · shift and time-since-break

**Infer — by subtracting the waiting:**
90 seconds inside is not 90 seconds of work. Ask the neighbours — buffer before empty means
*starved*; buffer after full means *blocked*. Subtract both and what remains is real work.
Measured size of this correction: **raw 88.8 s vs true 58.0 s**, a 53% overstatement. Trusting
the raw number sends a technician to a station that isn't broken.

From the corrected number we then infer: true processing time, whether it is drifting,
whether it is the constraint, and its state at any moment.

**Cannot know — and we say so:** whether the joint was tightened correctly, any process value,
which specific defect occurred. No cleverness recovers these from door timings.

For defects at these stations the fallback order is: **time it** (a trigger, not a diagnosis)
→ **watch the next coupled instrumented station** (a free inspector) → **ask for a sensor**,
with its cost and payback.

### C1.4 What the seven complexities changed

Three connections only visible after Part A:

**Diagnostic need drives modelling decisions, not just throughput prediction.** From C2, the
four root causes separate by *scope* — one station, one lot, one zone, one shift. So we must
represent enough to **distinguish causes**, not merely to predict output. Ambient barely
affects throughput; it is represented explicitly anyway, because without it we cannot tell
environmental from equipment. A throughput-only analysis would never reach that argument.

**What we represent bounds which couplings we can see.** From C1, a downstream station can act
as a free inspector only if we represent the channel carrying the coupling — station 13's
*angle*, not just its torque. Represent only primary spec channels and every coupling
disappears.

**What we represent must be fittable from the event stream, or it doesn't transfer.** From C6,
any parameter needing data a new line doesn't emit breaks commissioning. That is a hard filter
on the "represent explicitly" tier.

### C1.5 Enforcement

An explicitly represented value and an inferred value **must never look identical**. Every
field carries value + provenance + calibrated confidence; a field missing any of the three is
not published. Without that, a twin quietly launders estimates into facts.

Scoping decisions are **proved by ablation, not asserted** — remove the element, re-run,
report what changed. We have been wrong twice: the shift calendar looked cosmetic until it
turned out to be the only thing that drains a backlog, and the material lot table looked like
flavour until it produced 21 simultaneous alarms.

### C1.6 The five in brackets are examples, not a list

**The signals that matter differ per station.** Torque is meaningless at a paint booth; weld
resistance is meaningless at a manual clip station. So how do we configure this without
hand-tuning 40 stations? Three levels, and only one is real work.

**Level 1 — the primary signal is DECLARED, not discovered.** It is a fact from engineering,
already in the part master and quality plan because the plant needs it to inspect anything at
all: *"this joint must be torqued to 45 Nm ± 4"* makes torque the primary channel there by
definition. We read it; we don't infer it.

| Station type | Primary | From |
|---|---|---|
| Nutrunner | torque | part master / quality plan |
| Spot weld | weld resistance | weld schedule |
| Press-fit | force | process spec |
| Paint booth | film thickness | paint spec |
| Manual clip | *none — no spec channel* | — |

**Level 2 — supporting signals are learned per equipment FAMILY, not per station.** Which
other channels move when the primary degrades is a genuine measurement, but it is made once
per family. All 40 nutrunners behave alike.

```
family: nutrunner      primary torque
                       secondaries angle, motor current, cycle time
                       environmental ambient temp
family: spot weld      primary weld resistance
                       secondaries current, voltage, electrode force, cycle time
                       environmental coolant temp, ambient
```

**A 40-station line typically has 5–6 equipment families**, so this is five or six entries,
not forty. That is the whole reason it scales. An uncharacterised family starts on **cycle
time only** (which works everywhere), is flagged *"family not yet characterised"*, and gets
characterised once a few faults have been seen — degrading gracefully rather than failing.

**Level 3 — usefulness is measured per station instance.** A channel can exist and still carry
nothing here. Test: plot its distribution healthy vs faulty at this station; if they overlap,
drop it from this station's health score. A histogram, nothing more.

> **Declared → learned per family → measured per instance.** Nobody hand-configures 40 stations.

**Not all stations are equally informative, either.** A richly instrumented station in a
well-buffered stretch may tell us little; a sparse one at a choke point may tell us a lot.
Station **information value** depends on how often it constrains, how many dark stations it can
inspect (the coupling map), and how long its blind window is (the detection horizon). It ranks
both *where to look first* and *where to add sensors*.

**New artifact needed:** a **channel role registry** — 5–6 entries, one per equipment family.
Nothing else changes, because the detector never looks at what a channel physically measures.
It compares each channel to **its own healthy baseline** and reduces it to a dimensionless
number — so a weld resistance drifting 2σ and a booth humidity drifting 2σ are literally the
same feature. **The answer to "every station has different signals" is: yes, and after
normalisation the detector never finds out.**

### C1.7 What this closes

| Brief clause | Covered |
|---|---|
| Solutioning 1 — modelling approach, represent vs infer | ✅ fully |
| Solutioning 1 — *"especially at sensor-poor stations"* | ✅ the doors/room split |
| Solutioning 1 — the bracketed list as examples, not a spec | ✅ declared / family / instance |
| Complexity 1 — inconsistent coverage | ✅ reinforces Part A |

---

## Solution 2 — Predictive techniques, and validating them

> *"Predictive techniques — anomaly detection, statistical process control, physics-informed
> models, or ML-based bottleneck/defect prediction, and how you'd validate them before
> trusting their output."*

**Status:** `open` — needs Sagar's review. Mostly assembly of decisions already made; the
**validation ladder** (C2.4) is new and unowned.

### C2.1 Which technique does which job — and what each is NOT for

The value is not in listing four families. It is in stating precisely where each does *not*
belong, because using the wrong one is the common failure.

| Technique | Its job | **Explicitly not for** |
|---|---|---|
| **SPC (CUSUM / EWMA)** | Defect precursors at instrumented stations | **Bottleneck detection** |
| **Anomaly detection** | Micro-stops; cross-channel disagreement | Ranking constraints |
| **Physics-informed** | **The bottleneck method** — DES twin + queueing theory | Replacing measurement where it exists |
| **ML** | Failure-mode classifier; interaction discovery | Replacing arithmetic |

**Why SPC and anomaly detection can never find a bottleneck:** *the bottleneck is not broken —
it is just the slowest.* Nothing is abnormal about it; it runs exactly as it always has. A
"something is wrong" detector looks straight past it every time. Anomalous and constraining
are orthogonal properties.

**Why CUSUM specifically:** averaging shrinks noise by √n, so a fixed window forces an
unwinnable trade — short catches big shifts and misses small ones, long catches small ones too
late. CUSUM accumulates and fires when there is enough evidence; you set a sensitivity, not a
window. Two state variables per channel. Measured: **421–1,322 vehicles of warning**. One
caveat before calibrating anything: **autocorrelation inflates the false-alarm rate silently**
— consecutive fastenings share a joint, an operator, a lot.

**Micro-stops** are anomaly detection's real home — measured **2,648 vs 876 logged down
entries, zero overlap**, which is why they are invisible in the plant's own downtime report.

### C2.2 Why physics-informed is the primary, not a preference

To know which station is the bottleneck you must answer *"what would happen if this one were
faster?"* — and the only honest way to answer is **to try it**. You cannot stare at a traffic
jam and deduce which of five roadworks causes it; you would have to remove one. You cannot do
that on a real line. **You can in a copy.**

The 2023 systematic review makes this decision for us: the method matching the *definition* of
a bottleneck is sensitivity-of-the-system, its only stated shortcoming is that it **requires
counterfactuals**, and data science *"is not able to evaluate counterfactuals... some
modelling needs to be reintroduced."* A calibrated DES twin under CRN is exactly that
instrument — **our architecture, described in print as the field's open gap.**

Alongside it: **Kingman** (queue time explodes as utilisation → 1 *and scales with
variability*, so a station can become the constraint with no change in its mean at all),
**Little's Law**, and **TOC** (our measured 106 vs 106).

### C2.3 Where ML earns its keep — two places only

The failure-mode classifier (4 classes, 3 features, fitted on **ratios** so it learns physics
rather than our generator's units), and interaction discovery — gradient boosting surfacing
which *combinations* of conditions co-occur with failure. In that second role it is a
**hypothesis generator, never a conclusion**; anything it surfaces must be confirmed by a
natural experiment or ruled physically plausible.

The position: **don't train a computer to guess something you can just work out.** State
reconstruction, constraint ranking and the buffer countdown are arithmetic; drift detection is
1954 statistics. And we hold 1,248 labelled blocks — enough for gradient boosting, nowhere
near enough for anything deep.

### C2.4 Validation — ten rules, each one earned

| | Rule | Because |
|---|---|---|
| 1 | Detector must not mark its own homework | We scored 95.2% — it was an identity, not a test |
| 2 | Ground truth **economic**, not procedural | The constraint is whichever speed-up produces cars |
| 3 | Calibrate on **held-out** data | "Zero false alarms" was really ~1 per 5 tool-weeks |
| 4 | **Firewall** the headline | Different failure mechanism than development |
| 5 | Beat **real** baselines, incl. persistence | "Same as ten minutes ago" is hard to beat and usually skipped |
| 6 | Report **regret**, not accuracy | Picking a 4-of-5-car station loses one car, not everything |
| 7 | Two regimes, **never averaged** | A balanced line genuinely has no answer |
| 8 | **Reliability diagram** for any probability | This is what killed overtake risk |
| 9 | Report **n and an interval** | The 5.9% rests on n=17 |
| 10 | Negatives at **equal prominence** | Our strongest asset in a mentored round |

Lead-time protocol: **T0** injected → **T1** twin alerts → **T2** conventional KPI would show
it → **T3** EOL catches it. Lead time = T2 − T1, with T2 pinned to a stated convention
(15-min KPI refresh) so the baseline is not self-graded.

### C2.5 The validation ladder — and where we honestly sit

"Validated" is not binary. **This table is new and worth building** — it states the discipline
and the gaps in one object.

| Level | Meaning |
|---|---|
| 0 | It runs |
| 1 | Scored against independent truth |
| 2 | Scored on held-out data |
| 3 | Scored on a firewall set |
| 4 | Beats real baselines |
| 5 | Calibrated — reliability diagram |
| 6 | Validated **over time** in production |

| Capability | Level | Note |
|---|---|---|
| Effective-CT detection | **4** | Beats utilisation; not yet calibrated |
| Multi-channel drift | **3–4** | Held-out calibration; firewall set exists, unused for the headline |
| Buffer countdown | **4** | 60% of 178, limits stated |
| **Overtake risk** | **5 — and failed there** | Reached calibration and was killed by it |
| Dark localisation | **1** | Built; base rate defeats scoring |
| Failure-mode classifier | **0–1** | Signatures separable; classifier not fitted |
| Everything in Parts A and C | **0** | Designed, unbuilt |

The overtake row is the most convincing line in the file: a capability that climbed to the
highest rung of validation and was abandoned there.

### C2.6 Decide the kill criterion *before* measuring

Otherwise we will always find a way to say it worked. Like setting a target weight before
stepping on the scales.

We did this once by accident — we required the prediction to be honestly confident, measured
it, and cut it. **That only counts as a result because the standard existed first.** So for
each capability still to come we write the kill criterion now, e.g. *"if the rollout
predictor's reliability diagram is off by more than 15 points after calibration, we report it
failed and fall back to the cheap ranker."*

### C2.7 What this closes

| Brief clause | Covered |
|---|---|
| Solutioning 2 — the four technique families | ✅ mapped, with explicit non-uses |
| Solutioning 2 — *"how you'd validate before trusting output"* | ✅ ten rules + the ladder |
| Complexity 7 — validation over time | ✅ level 6 is where the ledger lives |

---

## Solution 3 — Handling data gaps and low-cost sensing

> *"Handling data gaps — how the twin stays useful at stations with partial or no
> instrumentation, including any low-cost sensing you might propose."*

**Status:** `open` — needs Sagar's review. The first half is already answered by **Complexity
1**; the **low-cost sensing menu (C3.3) is new** and was previously unanswered. Cost bands
still need real sourcing.

### C3.1 We never answer "unknown" — the answer just gets vaguer

Like asking where someone is in a building:

| Situation | What we can say |
|---|---|
| Station has sensors | *"Room 12"* |
| One blind station, neighbours visible | *"Second floor"* |
| Several blind in a row | *"Somewhere in the east wing"* — you can still go and look |
| Fully opaque | *"I don't know. A camera in this corridor would tell us, and it costs this much."* |

All four are useful. **The last one is useful *because* it is honest** — it turns a blind spot
into a decision rather than a shrug. Mechanism detail is in Complexity 1.

### C3.2 The rule every proposal must satisfy

**Mount externally. Publish to our gateway. Never into the PLC.**

That keeps every device in **risk class 2** (C3) — a technician job in a routine window, not a
controls-engineering change needing re-validation. *Putting a thermometer in your fridge is
fine; rewiring the thermostat needs an electrician and might break the fridge.* Everything
below is a thermometer.

### C3.3 The low-cost sensing menu — previously unanswered

Ranked by **value per rupee**, not price. **Cost bands are order-of-magnitude and must be
sourced before they enter any document** — same discipline as the ROI assumptions table.

| # | Device | Rough cost | What it gives | Tier movement |
|---|---|---|---|---|
| **1** | **Barcode / RFID reader** at a boundary | Rs 15-40k | Unit in/out timestamps | **C -> B** — splits a dark block |
| **2** | **Split-core current clamp** + logger | Rs 5-15k | Running vs idle, load signature, mechanical condition | **A process channel where there was none** |
| **3** | Photoeye / proximity sensor | Rs 3-10k | Occupancy timing without a scan | Cheapest timing signal |
| **4** | Ambient temp + humidity, one per zone | Rs 2-5k | Removes a shared confounder | Stops 40 tools looking like they fail at once |
| **5** | Digital andon / tablet checklist | Rs 15-30k | `manual_check` events + completion timestamps | **D -> B** at a manual station |
| **6** | Wireless accelerometer | Rs 20-60k | Vibration where current signature isn't enough | Rotating equipment only |
| **7** | Vision unit counter | Rs 30-80k | Counting without mounting anything | When a scanner can't be fitted |

**Two deserve emphasis.**

**#1 is the highest-value device and it is not obvious** — it measures nothing about the
process at all. But one reader placed *inside* a dark block converts one Tier C problem into
two Tier B problems. *Trying to find where a delay happened on a long journey: knowing only
departure and arrival, you can't. Add one checkpoint in the middle and you know which half.*
**You are buying resolution, not measurement.**

**#2 is the cheapest genuinely useful thing available** — clips around the supply cable with
zero contact with the machine, no downtime to fit, no interaction with the controller, and it
doubles as the stand-in for vibration.

### C3.4 Flow sensors and defect sensors go in different places

Given *k* sensors, **maximise what?** Two objectives, and they disagree:

| Goal | Maximise | Favours |
|---|---|---|
| **Flow** | Localisation power x P(station constrains) | Stations near choke points |
| **Defects** | Exposure closed = detection horizon x fault rate x cost | Stations with **long blind windows**, however trivial |

A station fitting a plastic clip is fast and will **never** be the bottleneck — worthless for
flow. But if a badly fitted clip isn't caught until final test, hundreds of cars carry it, so
it is a **top defect priority**. Worthless for one job, first on the list for the other.

**So produce two lists and merge them by value.** One blended ranking hides the reasoning.

### C3.5 What the twin actually shows

The observability map is a **first-class output, not an internal diagnostic**:

> **S12 — 2 of 10 signals measured, 6 inferred, confidence 0.81**
> *Blind spot: errors here go unnoticed for 19 cars.*
> *A barcode reader (Rs 25k) cuts that to 2. Next install window: March.*

That reframes the conversation from *"instrument everything"* to **"spend this much, here, for
this much."**

### C3.6 What this closes

| Brief clause | Covered |
|---|---|
| Solutioning 3 — twin stays useful at sensor-poor stations | OK — via C1's tier ladder |
| Solutioning 3 — *"low-cost sensing you might propose"* | OK — **the menu, previously unanswered** |
| Complexity 1 — inconsistent coverage | OK — reinforces |
| Complexity 3 — retrofits only in windows | OK — every device is risk class 2 |

**Open item:** the seven cost bands are estimates and need sourcing.

---

## Solution 6 — Scalability & ROI (the ROI half)

> *"Scalability & ROI — how a prototype built for one line could reasonably extend to other
> lines, plants, or sites with different starting conditions."*

**Status:** `open` — needs Sagar's review. The **scaling** half is answered in **Complexity 6**
(transfer curve, three-tier rollout, what breaks per axis). This is the **money** half, and it
is the thinnest thing in the project. Feeds the unticked deliverable *"business case and impact"*.

**Discipline:** every value line traces to a named measured output or a cited source. Nothing
unattributed — the same rule our documents already follow.

### C6.1 Four value sources, and they are not equal

**1. Better constraint identification -> cars recovered**

| | |
|---|---|
| Measured | Regret **1.309** (ours) vs **1.477** (utilisation) cars/block |
| Improvement | **0.168 cars/block**, block = 60 min |
| x production hours | ~4,000 h/year (2 shifts, ~250 days) |
| **Ceiling** | **~670 cars/year** |

**A ceiling, not a forecast** — it assumes every recommendation is acted on and every action works.

**2. Defect warning -> scrap and warranty avoided.** Two sub-lines, one far more defensible:

| Sub-line | Measured | Verifiable by the plant itself? |
|---|---|---|
| Escapes prevented | 11,631 of 11,826 defects passed as OK under sensor bias | **No** — only measurable because we hold independent truth; in a plant this surfaces as warranty months later |
| **False rejections prevented** | **2,355** good joints wrongly scrapped under transducer drift | **Yes** — the controller's own NOK count |

**Lead with the second.** The first is the better story; the second is the better evidence,
because a plant can check it without trusting us.

**3. Release-rate control -> lead time, at zero capital cost**

Measured: **same throughput, 36% lower lead time, no equipment change.** By Little's Law that
is 36% less WIP; separately confirmed that 8 extra cars of WIP produced exactly 8 minutes of
extra lead time.

**Our most defensible line, and it is currently buried.** It is a scheduling policy, so capital
cost is zero and payback is immediate by construction. Every other line needs assumptions about
margin and volume; this one barely does.

**4. Micro-stop visibility -> surfaced capacity.** Measured **2,648 micro-stops vs 876 logged
down entries, zero overlap**; cited industry figures put minor stops at ~34% of production loss.
**Honest caveat: detecting them does not recover capacity — someone must act.** Label it a
surfaced opportunity, not a realised saving.

### C6.2 The realization factor — what most ROI models hide

```
realised value = detection value x action rate x action effectiveness
```

Most business cases quietly set all three to 1.0. We state them, and **both are measurable
rather than guessed**: action rate from the alert ledger once running, action effectiveness
from our paired-CRN intervention outcomes **today**.

### C6.3 The cost side — four tiers

| Cost | Charged | Note |
|---|---|---|
| Platform — detectors, model, interfaces | **once, ever** | |
| Network, cybersecurity review, historian access | **per site** | |
| Adapter | per line | days |
| Fitting period | per line | weeks, but **passive** |
| Threshold calibration | per line | needs healthy data |
| **Sensors** | per station | **the Solution 3 menu**, phased by maintenance window |

Solution 3 now gives this line real devices and bands rather than an abstract "sensor cost".
Combined with C6's three tiers: **payback shortens after the first line, and again after the
first plant.**

### C6.4 One assumptions table — the move that makes it credible

Every number we had to assume goes in **one clearly labelled table**, so a judge who disagrees
changes a cell rather than dismissing the case. *(Showing your working: one wrong step still
earns most of the marks.)*

| Assumption | Source | Value |
|---|---|---|
| Contribution margin per vehicle | must cite | _tbd_ |
| Cost per rework at EOL | must cite | _tbd_ |
| Cost per warranty claim | must cite | _tbd_ |
| Sensor + install + integration | **Solution 3 menu** — bands, need sourcing | _tbd_ |
| Cost of capital (for WIP) | must cite | _tbd_ |
| **Action rate** | **measurable — ledger** | _tbd_ |
| **Action effectiveness** | **measurable — paired CRN** | _tbd_ |
| Production hours/year | stated assumption | ~4,000 |

**Then state which assumption dominates** — almost certainly contribution margin and action
rate. Naming it first defuses the obvious challenge.

### C6.5 The claim worth making

> **Our business case is computed by the same code that produces the alerts — not written in a
> spreadsheet afterwards.**

Which makes the leadership view's **actual-vs-forecast** tracking (C5) automatic: *"we said
this sensor would save Rs 10L; twelve months in, measured Rs 8.4L."* **Nobody else will have a
business case that audits itself.**

### C6.6 What is missing, and what not to lead with

**We have done the counting. We have not done the pricing.** Every line carries a measured
*quantity* and an unsourced *price* — 670 cars, 2,355 parts, 36% less lead time, and no rupee
figures anywhere. Sourcing those five costs is literature research, not engineering.

**Do not lead with the constraint-identification line.** 0.168 cars/block is a modest edge over
utilisation ranking and the easiest number to challenge. **Lead with release-rate control**
(zero capex, immediate payback, 36% measured), **then false rejections** (verifiable by the
plant itself).

### C6.7 What this closes

| Brief clause | Covered |
|---|---|
| Solutioning 6 — scalability | OK — Complexity 6 |
| Solutioning 6 — ROI | OK — value model, realization factor, assumptions table |
| Deliverable: **business case and impact** | Partial — structure complete, prices unsourced |

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
