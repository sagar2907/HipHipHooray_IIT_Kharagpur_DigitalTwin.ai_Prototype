# Suggestions — Priyansh

Proposals for Sagar to review. Nothing here is decided.

**How this works:** I raise it here → Sagar responds in the Response column → if we agree,
it moves to **Locked decisions** or the **Status board** in `PROGRESS.md` and gets marked
`moved` below. Sagar's equivalent is `suggestion_by_sagar/`.

_Last updated: 2026-08-23_

---

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
