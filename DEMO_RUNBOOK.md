# DEMO RUNBOOK — recording the prototype

**For the 31 Aug evening recording.** Timings below are **measured**, not
estimated: the beat timeline was computed by replaying the shift and recording
when each event actually becomes visible.

---

## 1. Setup (do this once, before recording)

```bash
cd HipHipHooray_IIT_Kharagpur_DigitalTwin.ai_Prototype
python web/server.py --run "../digitaltwin.ai/dataset/v5/flow/runs/L1_run_001" --speed 120 --shifts 0 --port 8080
```

Then open **http://127.0.0.1:8080**

**Use `--speed 120`, not 60.** At 60× the shift takes 8 minutes and the single
best beat — two tools with opposite correct answers — does not appear until
**3:30**. At 120× the whole shift is 4 minutes and that beat lands at ~1:45,
which is a far better shape for a recording.

**Before you hit record:**

- Let it run for **20 seconds first**. The opening two minutes of sim time are
  honestly labelled *"warming up — not enough units to rank yet"*. That is
  correct behaviour and a poor opening shot.
- Browser at 100% zoom, window maximised.
- Close the terminal window or move it off-screen.
- Have the **Leadership tab** pre-checked once (it loads `rollup.json` on first
  click; you do not want that on camera).

---

## 2. The measured beat timeline

At **120×**. Halve these for 60×, double for 240×.

| Wall | Sim | What appears | Say this |
|---|---|---|---|
| **0:15** | 0h30 | First verdict, prescription, and **1 alert already suppressed** | "It has a verdict. Note it has already *suppressed* an alert — the contract refuses anything that cannot state its evidence." |
| **0:17** | 0h35 | **Forming warning on a DARK station** | "That station has **no sensors at all**. We inferred it from the buffer slope either side. 15.5% of all our warnings are like this." |
| **0:35** | 1h10 | **The constraint MOVES** | "There it is. It moved. It does that ~20 times a shift — which is why a weekly average is useless." |
| **0:40** | 1h20 | First alert carrying **all five contract fields** | "Candidate, evidence, persistence, action, and what ignoring it costs. All five, or it does not appear." |
| **0:45** | 1h30 | First tool alarm | "Now the defect side." |
| **1:45** | 3h30 | **Two tools, opposite correct answers** ⭐ | "Same symptom — the torque moved. One is real wear: service it. The other is a lying transducer: recalibrate only. Servicing that one scraps good parts and fixes nothing." |
| 4:00 | 8h00 | Shift ends, next begins, **ledger carries over** | "New shift. The ledger carries — that is how you validate over time." |

**⭐ is the beat to build the recording around.** Everything before it is setup.

---

## 3. What to show, in order (5 minutes)

1. **Supervisor view, live** — let it run. Point at the line: red = constraint,
   amber = forming, hatched = no sensors.
2. **The evidence table** — "it does not just assert; here is why this station."
3. **The prescription** — the action *and* the cost of ignoring it.
4. **Confidence** — `0.1 calibrated`. Say the honest thing: *"That is a real
   probability. Before we calibrated it, it said 0.997 and was right 10% of the
   time. Most demos show you the 0.997."*
5. **The ledger** — running precision, suppression count, confirm/override.
   Click **confirm** on one alert on camera.
6. **Genealogy panel** — the opposite-actions pair. Containment: *"202 vehicles
   through since onset — 48 still on the line, 154 already completed."*
7. **Manager tab** — the occupancy distribution. *"Not an average — an average
   describes no moment of the shift."*
8. **Leadership tab** — the reconciliation test (**PASS**), and the evidence
   table with the **CONWIP row reading "not measured"**. Say that out loud: it
   is the strongest thirty seconds in the demo.

---

## 4. Failure modes and what to do

| If | Then |
|---|---|
| Page is blank / stream dead | Refresh. The plant keeps running server-side; the viewer is passive. |
| Port already in use | `Get-CimInstance Win32_Process -Filter "Name='python.exe'" \| Where-Object { $_.CommandLine -like '*web/server.py*' } \| Stop-Process -Force` |
| Leadership tab shows "no rollup yet" | `python scripts/build_rollup.py --runs 15` |
| Confidence shows "ordering score" not "calibrated" | `results/calibration.json` missing → `python scripts/fit_calibration.py` |
| Genealogy panel empty | Normal before ~0:45 wall. Wait for it. |
| Anything else | **Use the insurance recording from the 30th.** |

---

## 5. Take the insurance recording on the 30th

A rough, complete run-through recorded a day early. It will not be as polished,
and that does not matter — a recording cannot crash in front of a judge, and
four days of no sleep is precisely when a live demo goes wrong.

If the 31st goes well, use the good take. If anything at all misfires, you
still have a submission.

---

## 6. Lines worth having ready

Judges probe the weakest claim. Say these before they have to ask:

- **"Do you beat the state of the art?"** — "We significantly beat the
  utilisation baseline, p=0.0025. We are *statistically tied* with the
  active-period method, p=0.45, and we do not claim otherwise."
- **"How accurate is it?"** — "43% top-1, and that number is nearly meaningless
  — the label itself is a coin flip in half the blocks because of a 0.79-car
  noise floor. Regret is the honest metric, and it transfers across four
  topologies while accuracy collapses."
- **"Does it work on a different line?"** — "Regret held between 1.21 and 1.43
  across four topologies including one with a parallel pair. Top-1 fell from
  44.5% to 10.6%. The useful metric transfers; the vanity metric does not."
- **"What does it not do?"** — "It does not model operators — by choice, on
  ethical grounds. It does not model equipment vintage — no data axis. And we
  deleted a lead-time figure from our own business case because no file
  produced it."
- **"What failed?"** — "Our overtake-risk predictor. 5.9% correct against
  70–100% stated confidence. We measured it, killed it, and it is in the deck."
