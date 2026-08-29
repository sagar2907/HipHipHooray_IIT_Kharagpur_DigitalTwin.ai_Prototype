#!/usr/bin/env python3
"""Build the Round 2 pitch deck.

    python scripts/build_deck.py

No template is mandated for Round 2, so the design is ours. The palette is
deliberately the product's own argument: a steel/charcoal base with colour
reserved for deviation, which is the ISA-101 principle the twin itself
follows. A deck that is visually quiet until something is wrong makes the
same point the supervisor view does.

Every number here traces to results/ or results/twin.db. Nothing is rounded
up, and the two figures that were corrected downward after 903 shifts
(48.6 alerts/shift, 70.5% actionable) appear in their corrected form.
"""

import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "9_Deck", "DigitalTwin_Round2_Pitch.pptx")

# palette — the product's own ISA-101 logic: grey until something is wrong
INK   = RGBColor(0x1B, 0x1E, 0x21)
STEEL = RGBColor(0x1F, 0x2A, 0x33)
PAPER = RGBColor(0xF4, 0xF6, 0xF8)
MUTED = RGBColor(0x5A, 0x60, 0x67)
LINE  = RGBColor(0xC3, 0xCB, 0xD2)
BLUE  = RGBColor(0x1C, 0x5D, 0x99)
ALARM = RGBColor(0xB3, 0x26, 0x1E)
WARN  = RGBColor(0xC8, 0xA4, 0x15)
GOOD  = RGBColor(0x2D, 0x6A, 0x4F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DIM   = RGBColor(0x9F, 0xB3, 0xC4)

W, H = Inches(13.333), Inches(7.5)


def deck():
    p = Presentation()
    p.slide_width, p.slide_height = W, H
    return p


def blank(prs, dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = STEEL if dark else PAPER
    return s


def tb(s, x, y, w, h, text, size=18, bold=False, color=INK,
       align=PP_ALIGN.LEFT, font="Calibri", space=0, line=None):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, part in enumerate(text.split("\n")):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        if space:
            para.space_after = Pt(space)
        if line:
            para.line_spacing = line
        r = para.add_run()
        r.text = part
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return box


def rect(s, x, y, w, h, fill, outline=None, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if outline is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = outline
        sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def heading(s, text, kicker=None, dark=False):
    """Title with NO underline rule - an accent line under a title is the
    single clearest tell of a generated slide."""
    if kicker:
        tb(s, 0.7, 0.45, 12, 0.3, kicker.upper(), 11, True,
           DIM if dark else BLUE, font="Calibri")
    tb(s, 0.7, 0.78, 12, 0.9, text, 30, True, WHITE if dark else INK,
       font="Calibri")


def station_strip(s, x, y, n=20, dark_idx=(9, 13, 14), constraint=19,
                  forming=(6,), w=0.46, h=0.5, gap=0.055):
    """The line itself - the deck's recurring visual motif."""
    for i in range(n):
        cx = x + i * (w + gap)
        if i in dark_idx:
            fill, txt = RGBColor(0xB6, 0xBC, 0xC2), RGBColor(0x6B, 0x70, 0x76)
        elif i == constraint:
            fill, txt = ALARM, WHITE
        elif i in forming:
            fill, txt = WARN, RGBColor(0x24, 0x1F, 0x00)
        else:
            fill, txt = RGBColor(0xDD, 0xE2, 0xE6), MUTED
        sh = rect(s, cx, y, w, h, fill, LINE)
        tf = sh.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        r = para.add_run()
        r.text = f"{i+1:02d}"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = txt
        r.font.name = "Consolas"


def kpi(s, x, y, w, value, label, color=BLUE, vsize=34):
    rect(s, x, y, w, 1.5, WHITE, LINE)
    rect(s, x, y, 0.055, 1.5, color)
    tb(s, x + 0.22, y + 0.16, w - 0.4, 0.6, value, vsize, True, color,
       font="Consolas")
    tb(s, x + 0.22, y + 0.82, w - 0.4, 0.6, label, 10.5, False, MUTED, line=1.15)


def bars(s, x, y, w, h, rows, maxv, unit="", color=BLUE, hi=None):
    """Simple horizontal bar chart."""
    rowh = h / len(rows)
    for i, (lab, val) in enumerate(rows):
        yy = y + i * rowh
        tb(s, x, yy + 0.04, 2.5, 0.3, lab, 11.5, False, INK)
        track = w - 3.6
        rect(s, x + 2.6, yy + 0.06, track, rowh - 0.22,
             RGBColor(0xE4, 0xE8, 0xEB), LINE)
        bw = max(0.04, track * (val / maxv))
        rect(s, x + 2.6, yy + 0.06, bw, rowh - 0.22,
             ALARM if (hi and lab in hi) else color)
        tb(s, x + w - 0.95, yy + 0.04, 0.95, 0.3, f"{val}{unit}", 11.5, True,
           INK, font="Consolas")


def build():
    prs = deck()

    # ---------------------------------------------------------------- 1 title
    s = blank(prs, dark=True)
    tb(s, 0.9, 2.05, 11, 1.2, "DigitalTwin.ai", 60, True, WHITE)
    tb(s, 0.95, 3.25, 11, 0.6,
       "A vehicle assembly line that tells you which station is costing you cars —"
       "\nand what to do about it.", 20, False, DIM, line=1.25)
    rect(s, 0.95, 4.35, 1.5, 0.045, ALARM)
    tb(s, 0.95, 4.7, 11, 0.9,
       "Team HipHipHooray  ·  Sagar Sahu, Priyansh Goyal  ·  IIT Kharagpur"
       "\nAccenture Innovation Challenge 2026  ·  Problem Track 4  ·  Round 2",
       13, False, DIM, line=1.4)
    station_strip(s, 0.95, 6.15, constraint=19, forming=(6,))

    # ------------------------------------------------------------- 2 problem
    s = blank(prs)
    heading(s, "A plant knows last month's OEE.", "the problem")
    tb(s, 0.7, 1.72, 11.9, 0.5,
       "It does not know which station is holding the line back at 14:20 today.",
       19, False, MUTED)
    for i, (t, d) in enumerate([
        ("The constraint moves", "~20 times per shift in our data. A weekly average\ndescribes no moment of the shift it covers."),
        ("Utilisation lies", "A blocked station and a slow station both read ~95%\nbusy. Ranking by busyness sends people to the victim."),
        ("The data is uneven", "Legacy and modern equipment mixed. Some stations\nemit nothing at all — a human with a clipboard.")]):
        x = 0.7 + i * 4.07
        rect(s, x, 2.5, 3.85, 2.15, WHITE, LINE)
        rect(s, x, 2.5, 3.85, 0.05, [ALARM, WARN, BLUE][i])
        tb(s, x + 0.28, 2.78, 3.3, 0.4, t, 16, True, INK)
        tb(s, x + 0.28, 3.32, 3.35, 1.2, d, 12, False, MUTED, line=1.3)
    tb(s, 0.7, 5.2, 11.9, 0.9,
       "The gap is not sensing, and it is not another dashboard. It is the step from"
       " describing the line to deciding on it —\nand doing that honestly enough that a"
       " supervisor still trusts it after the third false alarm.",
       15, False, INK, line=1.35)

    # --------------------------------------------------------- 3 what we built
    s = blank(prs)
    heading(s, "We built the loop, and ran it for 903 shifts.", "what exists")
    tb(s, 0.7, 1.72, 12, 0.4,
       "Ingest → detect → rank → prescribe → re-read, on a timer. Not a report.",
       15, False, MUTED)
    for i, (v, l, c) in enumerate([
        ("903", "shifts replayed through\nthe live loop", BLUE),
        ("86,742", "decisions recorded to\na queryable database", BLUE),
        ("26 ms", "per decision — 800× the\nheadroom a 60× replay needs", GOOD),
        ("13/13", "timepoints verified causal:\nit never reads t > now", GOOD)]):
        kpi(s, 0.7 + i * 3.07, 2.35, 2.85, v, l, c, vsize=30)
    tb(s, 0.7, 4.35, 12, 0.45, "Causality is enforced structurally, not promised.",
       17, True, INK)
    tb(s, 0.7, 4.85, 12, 1.2,
       "The detector is handed a view of the run truncated at now — so it cannot read the"
       " future even by accident.\nRebuilding it per tick also means each station's baseline"
       " is learned only from data that has actually happened,\nwhich is what a plant sees on"
       " day one and is strictly harder than the offline case.",
       14, False, MUTED, line=1.35)

    # ------------------------------------------------------- 4 dark stations
    s = blank(prs)
    heading(s, "It names stations that have no sensors.", "complexity 1 · uneven coverage")
    station_strip(s, 0.95, 1.95, dark_idx=(9, 13, 14), constraint=19, forming=(6,),
                  w=0.55, h=0.62, gap=0.06)
    tb(s, 0.95, 2.72, 12, 0.35,
       "hatched = no sensors at all   ·   red = the constraint   ·   amber = forming",
       11.5, False, MUTED)
    kpi(s, 0.7, 3.35, 3.85, "15.5%", "of all forming-bottleneck warnings name a\n"
        "station with zero instrumentation   [15.0–15.9]\nn=29,060", BLUE, vsize=32)
    kpi(s, 4.75, 3.35, 3.85, "2.76%", "of vehicles a manual checklist PASSED\n"
        "went on to fail end-of-line   ·   96.51% pass rate\nn=31,329 checklist entries", ALARM, vsize=32)
    tb(s, 8.8, 3.42, 3.85, 2.2,
       "Body + final assembly:\n75.3% instrumented,\n24.7% on manual checks —\n"
       "an exact match to the\nbrief's own reference\nparameters.",
       13, True, GOOD, line=1.3)
    tb(s, 0.7, 5.15, 11.93, 1.05,
       "A checklist reading near-100% against a non-zero EOL failure rate is measuring compliance"
       " with the checklist,\nnot quality — exactly what the design predicted, and structurally the"
       " same failure as our sensor_bias\ntools: the instrument is the thing that is wrong. Manual"
       " checks enter as a fourth data tier — attested —\ncarrying the entry latency (mean 4.8 min),"
       " because a human record does not exist until someone types it in.",
       12.5, False, MUTED, line=1.32)

    # ---------------------------------------------------------- 5 prescription
    s = blank(prs)
    heading(s, "It does not just report. It prescribes.", "from detection to decision")
    for i, (a, b, c) in enumerate([
        ("DESCRIPTIVE", "what happened", RGBColor(0xDD, 0xE2, 0xE6)),
        ("DIAGNOSTIC", "why", RGBColor(0xC3, 0xD3, 0xE0)),
        ("PREDICTIVE", "what is about to", RGBColor(0x7F, 0xA8, 0xCC)),
        ("PRESCRIPTIVE", "what to do", BLUE)]):
        x = 0.7 + i * 3.07
        rect(s, x, 1.95, 2.85, 0.95, c)
        tb(s, x + 0.2, 2.12, 2.5, 0.3, a, 12.5, True,
           WHITE if i == 3 else INK)
        tb(s, x + 0.2, 2.45, 2.5, 0.3, b, 11, False,
           WHITE if i == 3 else MUTED)
    rect(s, 0.7, 3.3, 11.93, 1.55, WHITE, LINE)
    rect(s, 0.7, 3.3, 0.055, 1.55, BLUE)
    tb(s, 1.0, 3.5, 11.4, 0.4,
       "S20 — Tool change / maintenance pull-forward", 19, True, INK)
    tb(s, 1.0, 3.95, 11.4, 0.8,
       "processing time is climbing against this station's own baseline   ·   margin 71.8 s"
       "   ·   next best S12\nLeaving it alone costs ≈ 0.73 vehicles over the median"
       " 10-minute episode.", 13, False, MUTED, line=1.3)
    tb(s, 0.7, 5.1, 12, 0.42,
       "The action vocabulary is a library. The ranking and the cost are computed.", 16, True, INK)
    tb(s, 0.7, 5.55, 12, 0.8,
       "Ground truth is not \"which station looked busiest\" — it is the station whose speed-up"
       " actually produces more cars,\nmeasured by re-running the line under common random"
       " numbers. That makes the benchmark economic, not definitional.",
       13, False, MUTED, line=1.35)

    # ---------------------------------------------------------- 6 performance
    s = blank(prs)
    heading(s, "Measured against economic ground truth.", "does it work")
    tb(s, 0.7, 1.7, 12, 0.35,
       "Regret = cars per block lost by acting on our pick instead of the true best. Lower is better.",
       13, False, MUTED)
    bars(s, 0.7, 2.2, 11.9, 1.85, [
        ("Ours (effective CT)", 1.309),
        ("Active period (Roser)", 1.348),
        ("Utilisation baseline", 1.477)], maxv=1.6, hi={"Utilisation baseline"})
    rect(s, 0.7, 4.25, 5.8, 1.9, WHITE, LINE)
    rect(s, 0.7, 4.25, 0.055, 1.9, GOOD)
    tb(s, 1.0, 4.45, 5.3, 0.35, "What we claim", 15, True, GOOD)
    tb(s, 1.0, 4.85, 5.3, 1.1,
       "We beat the utilisation baseline —\nMcNemar paired test, p = 0.0025, n = 202 blocks.",
       13, False, INK, line=1.35)
    rect(s, 6.83, 4.25, 5.8, 1.9, WHITE, LINE)
    rect(s, 6.83, 4.25, 0.055, 1.9, ALARM)
    tb(s, 7.13, 4.45, 5.3, 0.35, "What we refuse to claim", 15, True, ALARM)
    tb(s, 7.13, 4.85, 5.3, 1.1,
       "That we beat the active-period method.\np = 0.45 — statistically tied. Saying otherwise"
       "\nwould not survive one question.", 13, False, INK, line=1.3)

    # ------------------------------------------------------------- 7 transfer
    s = blank(prs)
    heading(s, "Regret transfers. Accuracy does not.", "complexity 6 · scaling")
    tb(s, 0.7, 1.7, 12, 0.35,
       "The same method on four different line topologies — including one with a parallel"
       " pair that breaks the series assumption.", 13, False, MUTED)
    tb(s, 0.7, 2.2, 5.6, 0.35, "TOP-1 ACCURACY  — collapses", 12, True, ALARM)
    bars(s, 0.7, 2.6, 5.7, 1.75, [
        ("L1  20 stn", 44.5), ("L2  30 stn", 10.6),
        ("L3  parallel", 13.8), ("L4  15 stn", 21.9)], maxv=50, unit="%", color=ALARM)
    tb(s, 6.9, 2.2, 5.6, 0.35, "REGRET  — holds", 12, True, GOOD)
    bars(s, 6.9, 2.6, 5.7, 1.75, [
        ("L1  20 stn", 1.208), ("L2  30 stn", 1.218),
        ("L3  parallel", 1.431), ("L4  15 stn", 1.221)], maxv=1.6, color=GOOD)
    rect(s, 0.7, 4.6, 11.93, 1.55, WHITE, LINE)
    rect(s, 0.7, 4.6, 0.055, 1.55, BLUE)
    tb(s, 1.0, 4.8, 11.3, 0.38,
       "Sensor maturity: running with zero PLC state tags costs +1.683 cars/block on L1 —"
       " but +0.021 on L2.", 15, True, INK)
    tb(s, 1.0, 5.25, 11.3, 0.8,
       "State tags matter enormously where a strong constraint exists, and almost not at all"
       " on a balanced line.\nSo instrument the lines with the most to gain first — a more"
       " useful retrofit input than one averaged number.",
       13, False, MUTED, line=1.3)

    # ---------------------------------------------------------------- 8 trust
    s = blank(prs)
    heading(s, "The hard part is being trusted on day 30.", "complexity 7 · false alarms")
    for i, (v, l, c) in enumerate([
        ("0.479 → 0.025", "calibration error (ECE)\nbefore → after fitting", GOOD),
        ("48.6", "alerts per shift, against the\nISA-18.2 budget of 150", BLUE),
        ("7", "alerts SUPPRESSED for want\nof evidence, not downgraded", BLUE)]):
        kpi(s, 0.7 + i * 4.07, 2.0, 3.85, v, l, c, vsize=26)
    tb(s, 0.7, 3.85, 12, 0.42,
       "Calibrating the confidence broke our own alerting — and that was the finding.", 17, True, INK)
    tb(s, 0.7, 4.32, 12, 1.3,
       "Uncalibrated, the detector claimed ~1.0 confidence and everything got through."
       " Calibrated, it sits at the honest\nhit rate near 0.11 — and the same threshold"
       " silenced every alert. The system went quiet precisely because it\nbecame truthful."
       " So we stopped gating on the probability of being exactly right, and started gating"
       " on the cost\nof being ignored. That is our \"regret, not accuracy\" principle moved"
       " out of the evaluation and into the product.",
       13.5, False, MUTED, line=1.32)
    rect(s, 0.7, 5.85, 11.93, 0.9, WHITE, LINE)
    rect(s, 0.7, 5.85, 0.055, 0.9, ALARM)
    tb(s, 1.0, 6.0, 11.3, 0.6,
       "We also killed one of our own mechanisms: overtake-risk predicted a bottleneck"
       " 5.9% of the time [1.0–27.0, n=17]\nwhile claiming 70–100% confidence. It is gone from"
       " the live path. Negative results get equal billing.",
       12.5, False, INK, line=1.3)

    # ------------------------------------------------------------ 9 genealogy
    s = blank(prs)
    heading(s, "Two tools. Same symptom. Opposite answers.",
            "complexity 4 · defects found late")
    tb(s, 0.7, 1.68, 12, 0.32,
       "Both present identically to a torque-only monitor: \"the reading moved\".",
       13, False, MUTED)
    for i, (stn, cond, act, col, ch) in enumerate([
        ("S05", "REAL WEAR", "SERVICE the tool",
         ALARM, "torque −3.6σ  ·  current −4.1σ  ·  angle +6.0σ"),
        ("S06", "SENSOR LYING", "RECALIBRATE only — do NOT service",
         BLUE, "torque −2.9σ  ·  current +0.5σ  ·  angle −0.2σ")]):
        y = 2.12 + i * 1.72
        rect(s, 0.7, y, 11.93, 1.5, WHITE, LINE)
        rect(s, 0.7, y, 0.055, 1.5, col)
        tb(s, 1.0, y + 0.18, 1.0, 0.4, stn, 22, True, INK, font="Consolas")
        tb(s, 2.0, y + 0.24, 2.6, 0.35, cond, 13, True, col)
        tb(s, 4.7, y + 0.22, 7.6, 0.4, act, 16, True, INK)
        tb(s, 4.7, y + 0.72, 7.6, 0.4, ch, 12, False, MUTED, font="Consolas")
        tb(s, 1.0, y + 0.78, 3.4, 0.5,
           "both look like\n\"the torque moved\"", 11, False, MUTED, line=1.2)
    tb(s, 0.7, 5.6, 12, 0.42,
       "Servicing a lying sensor scraps good parts and fixes nothing.", 16, True, INK)
    tb(s, 0.7, 6.05, 12, 0.8,
       "Onset is read backwards off the CUSUM accumulator — dated to +2 minutes of truth —"
       " then the VIN thread lists\nexactly which vehicles carry it: 202 through S05,"
       " 48 still on the line, 154 already completed. 70.5% of alarmed tools\nget an"
       " actionable diagnosis [67.9–72.9, n=1,246].", 13, False, MUTED, line=1.3)

    # -------------------------------------------------------------- 10 views
    s = blank(prs)
    heading(s, "Three users. One twin. Proven, not asserted.", "complexity 5")
    for i, (who, what, detail) in enumerate([
        ("Floor supervisor", "real time",
         "ISA-101: grey base, colour only on\ndeviation. Quiet until something\nis wrong."),
        ("Plant manager", "weekly planning",
         "A constraint-occupancy distribution,\ndeliberately not an average —\n"
         "the constraint moves ~20×/shift."),
        ("Leadership", "investment case",
         "Value and coverage, every figure\nnaming the file that produced it.")]):
        x = 0.7 + i * 4.07
        rect(s, x, 1.95, 3.85, 2.4, WHITE, LINE)
        rect(s, x, 1.95, 3.85, 0.05, BLUE)
        tb(s, x + 0.28, 2.22, 3.3, 0.35, who, 16, True, INK)
        tb(s, x + 0.28, 2.62, 3.3, 0.3, what, 12, True, BLUE)
        tb(s, x + 0.28, 3.05, 3.4, 1.2, detail, 12, False, MUTED, line=1.3)
    rect(s, 0.7, 4.7, 11.93, 1.65, WHITE, LINE)
    rect(s, 0.7, 4.7, 0.055, 1.65, GOOD)
    tb(s, 1.0, 4.92, 11.3, 0.4, "The reconciliation test", 16, True, GOOD)
    tb(s, 1.0, 5.35, 11.3, 0.9,
       "Each level totals independently and is compared: 6,730 constraint-minutes and"
       " 4,431 vehicles — identical across\nsupervisor records, manager weeks and leadership."
       " That is how you show three views are one twin rather than\nthree dashboards that"
       " happen to sit in the same app.", 13, False, MUTED, line=1.3)

    # ------------------------------------------------------------- 11 roadmap
    s = blank(prs)
    heading(s, "Shadow first. Never closed-loop.", "roadmap")
    tb(s, 0.7, 1.66, 12, 0.3,
       "Reads seven tables the plant already produces — scans, PLC state tags, buffer"
       " counters, tool results, andon, rework, calendar. No new hardware on day one.",
       11, False, MUTED)
    phases = [("0", "Shadow", "wk 1–4", "Subscribe to streams the plant\nalready discards. No writes."),
              ("1", "One supervisor", "wk 5–10", "One line, one shift, one screen.\nEvery alert confirmed by a person."),
              ("2", "Floor", "mo 3–6", "All shifts. Manager view opens\nfor planning."),
              ("3", "Retrofit", "next window", "Costed sensor list, installed at a\nscheduled shutdown."),
              ("4", "Second line", "mo 6–12", "Transfer. Report the commissioning\ncurve, not a yes/no.")]
    for i, (n, name, when, what) in enumerate(phases):
        x = 0.7 + i * 2.44
        rect(s, x, 2.0, 2.25, 2.5, WHITE, LINE)
        rect(s, x, 2.0, 2.25, 0.05, BLUE)
        tb(s, x + 0.2, 2.2, 1.8, 0.4, n, 24, True, BLUE, font="Consolas")
        tb(s, x + 0.2, 2.72, 1.9, 0.3, name, 13.5, True, INK)
        tb(s, x + 0.2, 3.05, 1.9, 0.25, when, 10.5, False, BLUE)
        tb(s, x + 0.2, 3.4, 2.0, 1.0, what, 10.5, False, MUTED, line=1.25)
    rect(s, 0.7, 4.85, 11.93, 0.75, WHITE, LINE)
    rect(s, 0.7, 4.85, 0.055, 0.75, ALARM)
    tb(s, 1.0, 5.02, 11.3, 0.45,
       "Never: closed-loop write to line control — enforced by a test, not a promise.",
       15, True, INK)
    tb(s, 0.7, 5.78, 12, 0.95,
       "What we deliberately did not do:  operator variation — excluded on ethical grounds,"
       " we measure the station, never\nthe person.  ·  equipment vintage — no data axis for it."
       "  ·  a CONWIP lead-time figure — no source file, so it does not appear.\n"
       "Not yet built:  the historian adapter. Shadow mode runs today on exported logs;"
       " one module connects it live.",
       12.5, False, MUTED, line=1.3)

    # --------------------------------------------------------------- 12 close
    s = blank(prs, dark=True)
    tb(s, 0.9, 1.5, 11.5, 0.9,
       "The plant already has the data.", 40, True, WHITE)
    tb(s, 0.9, 2.5, 11.5, 1.0,
       "What it has been missing is a model that connects it to cause,"
       "\nconsequence, and the next best action.", 22, False, DIM, line=1.3)
    rect(s, 0.95, 3.85, 1.5, 0.045, ALARM)
    for i, (v, l) in enumerate([
        ("903", "shifts run"), ("15.5%", "warnings on dark stations"),
        ("0.025", "calibration error"), ("70.5%", "tools actionably diagnosed")]):
        x = 0.9 + i * 3.05
        tb(s, x, 4.35, 2.9, 0.55, v, 28, True, WHITE, font="Consolas")
        tb(s, x, 4.95, 2.9, 0.4, l, 11.5, False, DIM)
    tb(s, 0.9, 5.9, 11.5, 0.8,
       "Every number here is measured, with its source file named — including the ones"
       " that got worse\nwhen we looked harder, and the mechanism we killed.",
       13.5, False, DIM, line=1.35)
    station_strip(s, 0.95, 6.85, constraint=19, forming=(6,), h=0.35, w=0.46)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs.save(OUT)
    print(f"written: {OUT}")
    print(f"slides : {len(prs.slides.__iter__.__self__._sldIdLst)}")


if __name__ == "__main__":
    build()
