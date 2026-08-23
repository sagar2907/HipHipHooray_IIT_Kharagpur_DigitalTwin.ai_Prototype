# Suggestions — Sagar

Proposals for Priyansh to review. Nothing here is decided.

**How this works:** I raise it here → Priyansh responds in the Response column → if we agree,
it moves to **Locked decisions** or the **Status board** in `PROGRESS.md` and gets marked
`moved` below. Priyansh's equivalent is `suggestion_by_priyansh/`.

_Last updated: 2026-08-23_

---

## 1 — Cite the Turning Point Method before a judge finds it first

Our "blocked upstream, starved downstream" signature (`detect.py`) is functionally the
**Turning Point Method** (Li, Chang & Ni, 2009, *IJPR*) — the crossing point of blockage
and starvation probability. We built it independently, but it isn't independently
discovered anymore once it's published.

This is the same category of risk Priyansh flagged in his #2 (Roser attribution): our
credibility strategy is provenance discipline, so an unattributed rediscovery of prior art
reads worse than a cited one. Costs one line in the Evidence File.

**Proposal:** add the citation wherever the signature is described. No code or number
changes.

**Status:** `open`.

---

## 2 — Add Intersection-over-Union as an evaluation metric

Everything we score today (top-1/top-2, regret) grades a single instant. The constraint
shifts ~6 times a shift, so an alert that's right about *which station* but off by a few
minutes on *when it started/ended* currently scores as flatly wrong.

Subramaniyan et al. (Chalmers, 2018) score their ARIMA bottleneck-forecast against ground
truth using **IoU** — predicted-active-period overlap vs actual, borrowed from
image-segmentation scoring. It rewards getting the *duration* right, which top-1 doesn't.

**Proposal:** add IoU alongside regret as a second scoring axis — cheap to compute from
data we already have (predicted interval vs `verdict()` ground truth), and nobody else in
the competition will have thought to report it.

**Status:** `open` — sits naturally in Workstream A or D, whoever gets there first.

---

## 3 — ARIMA-forecast as a candidate mechanism for Workstream B

Everything locked so far detects the *current* constraint. Subramaniyan et al. forecast
the *next* one — ARIMA over active-period history, evaluated on real ANDON-light MES data,
which is closer to our sensor reality than a lab simulation.

I'm not proposing we adopt it yet — Monte Carlo rollout is already locked as our method and
I'm not second-guessing that call. But it's worth a half-day spike inside Workstream B
**after** the loop is running end-to-end: if it beats buffer-countdown on lead time, it's a
second predictive mechanism we can show working; if it doesn't, that's a negative result we
already know how to report well.

**Status:** `open` — low priority, only after B's gate is green.

---

## 4 — ISO 22400 vocabulary for the leadership view

Priyansh's #11 locks ISA-101 (grayscale, colour-on-deviation) for the supervisor view —
agreed, no change proposed there. For the **leadership** view specifically: frame the
top-line numbers in **ISO 22400** terms (OEE, MTBF, MTTR) rather than our own metric names.
It's the vocabulary a plant manager or judge with a manufacturing background already has,
and it costs us nothing since OEE decomposes cleanly from data we already hold.

**Proposal:** leadership view's headline tile reads "OEE impact," not "regret." Regret
still drives the ranking underneath — this is presentation only, not a metric change.

**Status:** `open` — Workstream E.

---

## 5 — Close the loop on the old prototype placeholder

For the record: the Desktop `DigitalTwin_Handover/7_Prototype/PROTOTYPE_GOES_HERE.txt` note
(also carried into `7_Prototype/` here) was written when no Round 2 work could be found
anywhere on my machine after three separate searches. Priyansh's `d843ba8` confirms this
repo is the actual starting point — that placeholder was correct, not a bug. No action
needed, just flagging so neither of us re-searches for phantom files later.

**Status:** `moved` → closed, informational only.

---

## Priyansh's responses

| # | Response | Outcome |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
