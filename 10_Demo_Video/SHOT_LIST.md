# DigitalTwin_Full_Submission_Video.mp4 — shot list & voiceover script

**1920×1080, 25 fps, H.264, no audio track** — silent by design, built for you
and Priyansh to record voiceover over.

Five segments, cut back to back. Every one was captured the same way: a page
played back in real Chrome via Playwright and recorded natively in real
wall-clock time — not a slideshow, not a mockup. Segment 4 is a recording of
the **actual prototype server** running on the sample shift.

| # | Segment | Duration | Source |
|---|---|---|---|
| 1 | Team intro | ~5s | `5_Animation_Sources/Round2_Intro.html` |
| 2 | The problem & our approach | ~64s | `5_Animation_Sources/Round2_Overview.html` |
| 3 | **The virtual plant we built** | ~49s | `5_Animation_Sources/Round2_VirtualPlant.html` |
| 4 | **Prototype demonstration** | ~211s | live server, `scripts/record_demo.py` |
| 5 | Deploying to a real line | ~52s | `5_Animation_Sources/Round2_Deployment.html` |

Segments 2, 3 and 5 already carry burned-in captions matching the script below,
so the voiceover only needs to be read in time with them. Segment 4's captions
are burned in from `scripts/record_demo.py`'s own beat table.

---

## Segment 1 — Team intro

Static title card: names, roles, department, IIT Kharagpur, Team HipHipHooray.
No voiceover needed.

---

## Segment 2 — The problem & our approach

| Scene | Voiceover |
|---|---|
| The line | "A mixed-model assembly line. The constraint moves roughly twenty times a shift, and a defect caught late has already been built into every car since it started." |
| Uneven sensors | "Not every station is wired. Some are a person with a clipboard — and we tested whether that clipboard is honest. A ninety-six-point-five percent pass rate hid a real two-point-eight percent escape rate." |
| Prescriptive ⭐ | "Two tools can show the identical symptom and need opposite fixes. We separate real wear from a lying sensor by checking whether a mechanically coupled channel moved too — service one, recalibrate the other, never guess." |
| Trust | "Confidence is calibrated against held-out shifts, not asserted. An alert that cannot state its evidence is suppressed, not shown — and every human decision is logged, so precision is proven over time, not claimed once." |
| Three views | "One record stream answers a supervisor in real time, a manager's week, and leadership's investment case — and we prove it is one twin: every total reconciles exactly." |
| Close | "DigitalTwin.ai. The plant already has the data." |

---

## Segment 3 — The virtual plant we built

This segment exists to answer the question a judge will ask immediately:
*where did your data come from?*

| Scene | Voiceover |
|---|---|
| We built the plant | "We could not put sensors on a real assembly line, so we built one in software — twenty stations, the buffers between them, the tools, the breaks, the rework, even the operator stops." |
| Observed vs hidden | "It writes out only what a real plant would actually record. The true answer — which fault we injected and exactly when — is written to a separate place the detector is never allowed to open." |
| Why that matters | "That is the whole point. We know the right answer and the detector does not, so we can mark its work. Every number you are about to see was scored this way." |
| The scale | "A hundred and sixty-two simulated shifts, four different line layouts, nearly a thousand tools. Then we pointed the twin at it and watched." |

---

## Segment 4 — Prototype demonstration

Captions are burned in and written in plain language on purpose — a judge
watching has not read the codebase. Times are **within the segment**; add
roughly 1:58 for position in the full video.

| Time | On screen | Caption / voiceover |
|---|---|---|
| 0:00 | Top of supervisor view | "This is the twin, running live. One full eight-hour shift plays out in about three minutes." |
| 0:07 | Station strip | "The strip along the top is the assembly line - twenty stations, in the order a car passes through them." |
| 0:14 | Constraint highlighted | "Red is the station slowing the whole line down right now." |
| 0:20 | Dark stations hatched | "The hatched grey ones have no sensors at all. The twin still has to work out what they are doing." |
| 0:27 | Evidence table | "It never just asserts. This table is the evidence behind the call." |
| 0:34 | — | "Each row is a station and the measured numbers that ranked it. 'Measured' means a sensor actually said so." |
| 0:42 | Recommended action | "It then says what to do about it - and what it costs if you ignore it." |
| 0:49 | Advisory-only notice | "And it says so plainly: advisory only. It never touches the machines. A person decides." |
| 0:56 | Status panel | "Confidence is a real probability. Before we calibrated it, it claimed 99% and was right about one time in ten." |
| 1:04 | Forming next | "'Forming next' is the early warning - which station is about to become the problem." |
| 1:11 | DARK · inferred badge | "When that warning names a station with no sensors, it says so: DARK, inferred." |
| 1:18 | Alert ledger | "The ledger is how the floor keeps score. Every call gets confirmed or overridden by a person." |
| 1:25 | Suppression count | "Some alerts are suppressed. If the twin cannot show its evidence, it stays quiet rather than guess." |
| 1:32 | **confirm clicked live** | "Confirming one now. That decision is recorded and counts towards the running accuracy." |
| 1:39 | Genealogy panel | "Now the defect side. This is where a drifting tool gets caught." |
| 1:46 | Onset & containment | "Onset is worked out backwards, so it can list exactly which cars were built after the drift began." |
| 1:54 | On-line vs shipped | "The ones still on the line can be reworked. The ones already finished are a customer problem." |
| 2:01 | ⭐ opposite actions | "Here is the beat that matters. Two tools can move the very same way and still need opposite fixes." |
| 2:09 | — | "If a mechanically linked channel moved along with the torque, the tool really is worn. Service it." |
| 2:16 | — | "If only the torque moved, the sensor is lying. Recalibrate it - servicing would scrap good parts and fix nothing." |
| 2:24 | Manual checklist card | "Manual checklist stations report here, with how long the person took to write the result down." |
| 2:31 | **Manager tab** | "The plant manager sees the same data, a week at a time." |
| 2:38 | — | "Not an average. The constraint moves about twenty times a shift, so an average describes no real moment of it." |
| 2:45 | Constraint occupancy | "This shows how often each station was the constraint - that is a scheduling and spending decision." |
| 2:53 | **Leadership tab** | "Leadership sees the investment case." |
| 3:00 | Evidence table | "Every claim names the file that produced it." |
| 3:07 | **NOT MEASURED row** | "And one row reads NOT MEASURED - we deleted a number from our own business case because no file produced it." |
| 3:15 | Reconciliation PASS | "The reconciliation test proves these are one model, not three dashboards. Every total matches exactly." |
| 3:23 | Back to live view | "Back to the live view. The plant has been running the whole time." |

**Recorded in the dashboard's single-column layout** — its own responsive mode.
In two-column mode the right-hand column is much taller than the left, so
scrolling to any panel below the evidence table leaves half the frame empty.

---

## Segment 5 — Deploying to a real line

| Scene | Voiceover |
|---|---|
| What it needs | "It runs on five things a plant already records — barcode scans, machine status, buffer counts, tool readings, and the manual checklist. Nothing here is new hardware." |
| What it never does | "It never writes back to the machines that run the line. That is not a promise in a document — it is a test that checks every file in the codebase." |
| How it rolls out | "It starts in shadow mode on yesterday's data, then one supervisor, then the whole floor, then a costed sensor upgrade — and only then, a second line." |
| Does it work elsewhere ⭐ | "And we checked it moves. On four different line shapes — more stations, more merge points, even two machines working in parallel — the cost of a wrong call stayed almost flat." |
| Close | "One module connects it to a real line. Nothing downstream changes." |

---

## Re-recording and editing

Every animated segment is a self-contained HTML file in `5_Animation_Sources/`.
Open one directly in a browser to preview or edit; add `?bare=1` to hide the
scrub bar and `?auto=1` to autoplay (what the recorder uses).

```bash
# one animation  (args: html, duration_ms, output name)
python scripts/record_animation.py 5_Animation_Sources/Round2_Overview.html 64000 overview

# the live prototype segment
python web/server.py --speed 100 --shifts 0 --port 8099 --no-record &
python scripts/record_demo.py
```

Raw clips land in `10_Demo_Video/_raw/` as `.webm` (gitignored). Encode and
assemble with `scripts/build_video.py`.

**A note on resolution.** Playwright's recorder captures the viewport at
CSS-pixel size and *pads* to `record_video_size` — it does not scale up, and
`device_scale_factor` does not change what lands in the video. So the viewport
must itself be 1080p and the page is zoomed 1.5× to fill it. Setting a larger
`record_video_size` alone silently produces 720p content in a grey 1080p frame.
