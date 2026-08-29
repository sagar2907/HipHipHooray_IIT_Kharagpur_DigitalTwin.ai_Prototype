# DigitalTwin_Prototype_Demo.mp4 — shot list for the voiceover

1280×720, 25fps, 3:07, **no audio track** — silent by design, for a voiceover pass.
Captured as a real recording of the live prototype (Playwright driving actual
Chrome against `web/server.py --speed 120`), not a mockup or a screenshot
slideshow — every number and state on screen is the twin actually running.

| Timestamp | What's on screen | Say something like |
|---|---|---|
| 0:00–0:22 | Floor supervisor view: line strip, evidence table, recommended action, status panel | What the twin is, live on one shift |
| 0:22–0:32 | Scrolls to Forming Next + Alert Ledger | Suppressed-alert count, the contract |
| 0:32–1:47 | Scrolls to Tool health & genealogy | Onset, containment, vehicles since onset |
| **~1:10** | **S05 "REAL WEAR → SERVICE" beside S06 "SENSOR LYING → RECALIBRATE only"** | **⭐ the star beat — same symptom, opposite correct answers** |
| 1:47–1:51 | Scrolls back to top | — |
| 1:51–2:02 | A live alert confirmed on screen (button click visible) | The ledger records a real human decision |
| 2:02–2:20 | Plant manager tab — weekly constraint-occupancy bars | Not an average — the constraint moves too often for one |
| 2:20–2:45 | Leadership tab — investment case, evidence table with **CONWIP "not measured"** in orange, reconciliation **PASS** table | The thirty seconds the runbook calls the strongest — what we refuse to claim, and the proof it's one twin |
| 2:45–3:07 | Back to the live Supervisor view, plant still running | Close on the system still working |

## Re-recording

`scripts/record_demo.py` reproduces this exact walkthrough. It needs
`playwright` (`pip install playwright`) and a Chrome install; point
`CHROME` in the script at yours if it isn't at the default path.

```bash
python web/server.py --speed 120 --shifts 0 --port 8099 --no-record &
python scripts/record_demo.py
```

Output lands in a `record_video_dir` temp folder as `.webm`; convert with:

```bash
ffmpeg -i page@*.webm -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -an out.mp4
```
