# DigitalTwin_Full_Submission_Video.mp4 — shot list & voiceover script

1280×720, 25fps, **4:56 (295.96s)**, H.264, **no audio track** — silent by
design, built for you and Priyansh to record voiceover over.

Four segments, cut back to back, no re-encoding drift at the seams (verified —
duration is exactly the sum of the four source clips):

| Segment | Time in final video | Source clip | Duration |
|---|---|---|---|
| 1 · Team intro | 0:00–0:05 | `_raw/intro.webm` | 5.2s |
| 2 · Overview animation | 0:05–1:09 | `_raw/overview.webm` | 63.8s |
| 3 · Prototype walkthrough | 1:09–4:16 | `DigitalTwin_Prototype_Demo.mp4` (the real live prototype, unchanged) | 187.1s |
| 4 · Deployment animation | 4:16–4:56 | `_raw/deployment.webm` | 39.8s |

All four were captured the same way: a self-contained HTML/SVG page, played
back in real Chrome via Playwright and recorded natively in real wall-clock
time — not a slideshow, not a mockup. Segment 3 is a recording of the actual
prototype server; segments 1, 2, 4 are original animations built for this
video (same visual language as `5_Animation_Sources/DigitalTwin_Animation_Captioned.mp4`,
which you asked to match, but rebuilt with Round 2's corrected numbers rather
than Round 1's).

---

## Segment 1 — Team intro (0:00–0:05)

Static title card. No voiceover needed — self-explanatory on screen.

---

## Segment 2 — Overview animation (0:05–1:09)

Every number here matches `PROGRESS.md`'s "MEASURED PROTOTYPE NUMBERS"
section and the proposal — none of it is Round 1's retired figures.

| Time | Scene | Voiceover script |
|---|---|---|
| 0:05–0:15 | The line, the problem | "A mixed-model assembly line. The constraint moves roughly twenty times a shift, and a defect caught late has already been built into every car since it started." |
| 0:15–0:27 | Uneven sensors | "Not every station is wired. Some are a person with a clipboard — and we tested whether that clipboard is honest. A ninety-six-point-five percent pass rate hid a real two-point-eight percent escape rate." |
| 0:27–0:39 | Prescriptive, not just predictive ⭐ | "Two tools can show the identical symptom and need opposite fixes. We separate real wear from a lying sensor by checking whether a mechanically coupled channel moved too — service one, recalibrate the other, never guess." |
| 0:39–0:51 | Trust, measured not asserted | "Confidence is calibrated against held-out shifts, not asserted. An alert that cannot state its evidence is suppressed, not shown — and every human decision is logged, so precision is proven over time, not claimed once." |
| 0:51–1:03 | One model, three views | "One record stream answers a supervisor in real time, a manager's week, and leadership's investment case — and we prove it is one twin: every total reconciles exactly." |
| 1:03–1:09 | Close | "DigitalTwin.ai. The plant already has the data." |

---

## Segment 3 — Prototype walkthrough (1:09–4:16)

This is `DigitalTwin_Prototype_Demo.mp4`, already shot list'd in detail below
(times relative to the segment itself, add 1:09 for position in the full video).

| Time (in segment) | What's on screen |
|---|---|
| 0:00–0:32 | Floor supervisor view: line strip, evidence table, recommended action, status panel; scrolls to the alert ledger |
| 0:32–1:47 | Genealogy panel; holds through **the star beat** — S05 "REAL WEAR → SERVICE" beside S06 "SENSOR LYING → RECALIBRATE only" |
| 1:51–2:02 | A live alert **confirmed on screen** |
| 2:02–2:20 | Plant manager tab — weekly constraint-occupancy bars |
| 2:20–2:45 | Leadership tab — reconciliation **PASS** table, CONWIP **"not measured"** row |
| 2:45–3:07 | Back to the live Supervisor view, plant still running |

---

## Segment 4 — Deployment animation (4:16–4:56)

| Time | Scene | Voiceover script |
|---|---|---|
| 4:16–4:26 | What it needs | "It reads seven tables a plant already produces — scans, PLC state tags, buffer counts, tool results, andon, rework, calendar. No new hardware to switch it on." |
| 4:26–4:36 | What it never does | "It never writes back to line control — enforced by a test that checks every module in the codebase, not a promise in a document." |
| 4:36–4:46 | How it rolls out | "Shadow mode runs today, on exported logs. Then one supervisor, then the floor, then a costed retrofit — and only then, another line." |
| 4:46–4:56 | Close | "One module connects it to a real line. Nothing downstream changes." |

---

## Re-recording or editing

Every animated segment is a self-contained HTML file in `5_Animation_Sources/`
— open it directly in a browser to preview, scrub scenes, or edit content.
Add `?bare=1` to hide the scrub bar, `?auto=1` to autoplay from load (both are
what the recording script uses).

```
5_Animation_Sources/Round2_Intro.html
5_Animation_Sources/Round2_Overview.html
5_Animation_Sources/Round2_Deployment.html
```

To re-record one clip:

```bash
python scripts/record_animation.py 5_Animation_Sources/Round2_Overview.html 62000 overview
```

(duration in ms; add ~2s buffer past the animation's own last scene so the
tail caption doesn't get cut). Output lands in `10_Demo_Video/_raw/<name>.webm`.

To re-record the live prototype segment: `scripts/record_demo.py` (see its
own instructions at the top of the file).

To re-encode a `.webm` to `.mp4`:

```bash
ffmpeg -i clip.webm -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -an clip_enc.mp4
```

To re-concatenate all four into the final video:

```bash
ffmpeg -i intro_enc.mp4 -i overview_enc.mp4 -i DigitalTwin_Prototype_Demo.mp4 -i deployment_enc.mp4 \
  -filter_complex "[0:v]fps=25,scale=1280:720,setsar=1,format=yuv420p[v0]; \
                   [1:v]fps=25,scale=1280:720,setsar=1,format=yuv420p[v1]; \
                   [2:v]fps=25,scale=1280:720,setsar=1,format=yuv420p[v2]; \
                   [3:v]fps=25,scale=1280:720,setsar=1,format=yuv420p[v3]; \
                   [v0][v1][v2][v3]concat=n=4:v=1:a=0[outv]" \
  -map "[outv]" -c:v libx264 -pix_fmt yuv420p -crf 19 -preset slow -movflags +faststart \
  DigitalTwin_Full_Submission_Video.mp4
```

The `.webm` raw captures are gitignored (`/10_Demo_Video/_raw/`); only the
encoded `.mp4` files are committed.
