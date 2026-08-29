"""Records the narrated walkthrough of the live prototype.

Drives real Chrome (via Playwright) against the running demo server and lets
Playwright's native recorder capture the session continuously, in real
wall-clock time - a true recording of the working system, not a slideshow.

The BEATS table below is the single source of truth for the segment: it drives
the page AND generates the burned-in caption track, so the two cannot drift
apart. Captions are deliberately written in plain language - a judge watching
this has not read the codebase.

Usage:
    python web/server.py --speed 100 --shifts 0 --port 8099 --no-record &
    python scripts/record_demo.py

Writes 10_Demo_Video/_raw/prototype.webm and 10_Demo_Video/_raw/prototype.ass.
"""

import os
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

PORT = 8099
BASE = f"http://127.0.0.1:{PORT}"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "10_Demo_Video", "_raw"))
os.makedirs(OUT_DIR, exist_ok=True)

# Warm up before recording: the honest "not enough units to rank yet" opening
# state is correct behaviour and a poor first frame.
WARMUP_S = 30

# Playwright's recorder captures the viewport at CSS-pixel size and PADS to
# record_video_size rather than scaling up (device_scale_factor does not change
# what lands in the video either). So the viewport IS the recording size, and
# the page is zoomed to fill it: 1920/1.5 = 1280 and 900/1.5 = 600, which is the
# short-and-wide CSS layout the beats are written against. A tall viewport shows
# every panel at once and reads as a wall of numbers; this shows one thing at a
# time.
REC_W, REC_H = 1920, 900
ZOOM = 1.5
VIEW_W, VIEW_H = REC_W, REC_H

# The dashboard's own single-column layout - the responsive mode it already
# uses on a narrow screen. Forced on here because the media query keys off the
# layout viewport, which body zoom does not change. In two-column mode the
# right-hand column is far taller than the left, so scrolling to any panel
# below the evidence table leaves half the frame empty; single column keeps
# every card full-width and the segment reads as one continuous story.
SINGLE_COLUMN_CSS = ".grid{grid-template-columns:1fr!important}"

# (start_ms, action, caption)
#   action: None | ("top",) | ("card", heading_substring) | ("tab", data_v) | ("confirm",)
# "card" scrolls the panel whose <h2> contains the substring, so the heading
# stays in frame with its content. Targeting the inner content div instead
# would scroll the title off the top.
BEATS = [
    (0,      ("top",),                   "This is the twin, running live. One full eight-hour shift plays out in about three minutes."),
    (7000,   None,                       "The strip along the top is the assembly line - twenty stations, in the order a car passes through them."),
    (14000,  None,                       "Red is the station slowing the whole line down right now."),
    (20500,  None,                       "The hatched grey ones have no sensors at all. The twin still has to work out what they are doing."),
    (27500,  ("card", "Evidence"),       "It never just asserts. This table is the evidence behind the call."),
    (34500,  None,                       "Each row is a station and the measured numbers that ranked it. 'Measured' means a sensor actually said so."),
    (42000,  ("card", "Recommended"),    "It then says what to do about it - and what it costs if you ignore it."),
    (49500,  None,                       "And it says so plainly: advisory only. It never touches the machines. A person decides."),
    (56500,  ("card", "Status"),         "Confidence is a real probability. Before we calibrated it, it claimed 99% and was right about one time in ten."),
    (64500,  ("card", "Forming next"),   "'Forming next' is the early warning - which station is about to become the problem."),
    (71500,  None,                       "When that warning names a station with no sensors, it says so: DARK, inferred."),
    (78500,  ("card", "Alert ledger"),   "The ledger is how the floor keeps score. Every call gets confirmed or overridden by a person."),
    (85500,  None,                       "Some alerts are suppressed. If the twin cannot show its evidence, it stays quiet rather than guess."),
    (92500,  ("confirm",),               "Confirming one now. That decision is recorded and counts towards the running accuracy."),
    (99500,  ("card", "Tool health"),    "Now the defect side. This is where a drifting tool gets caught."),
    (106500, None,                       "Onset is worked out backwards, so it can list exactly which cars were built after the drift began."),
    (114000, None,                       "The ones still on the line can be reworked. The ones already finished are a customer problem."),
    # Deliberately describes the RULE, not which tool is on screen. The panel
    # ranks by drift, so the tools shown at this moment vary run to run - a
    # caption naming a specific verdict could contradict the picture.
    (121500, None,                       "Here is the beat that matters. Two tools can move the very same way and still need opposite fixes."),
    (129000, None,                       "If a mechanically linked channel moved along with the torque, the tool really is worn. Service it."),
    (136000, None,                       "If only the torque moved, the sensor is lying. Recalibrate it - servicing would scrap good parts and fix nothing."),
    (144000, ("card", "Manual checklist"), "Manual checklist stations report here, with how long the person took to write the result down."),
    (151000, ("tab", "mgr"),             "The plant manager sees the same data, a week at a time."),
    (158000, None,                       "Not an average. The constraint moves about twenty times a shift, so an average describes no real moment of it."),
    (165500, None,                       "This shows how often each station was the constraint - that is a scheduling and spending decision."),
    (173000, ("tab", "led"),             "Leadership sees the investment case."),
    (180000, ("card", "What is measured"), "Every claim names the file that produced it."),
    (187000, None,                       "And one row reads NOT MEASURED - we deleted a number from our own business case because no file produced it."),
    (195000, ("card", "reconciliation"), "The reconciliation test proves these are one model, not three dashboards. Every total matches exactly."),
    (203000, ("tab", "sup"),             "Back to the live view. The plant has been running the whole time."),
]
SEGMENT_MS = 211000


def wait_for_server(timeout=40):
    for _ in range(timeout):
        try:
            urllib.request.urlopen(BASE + "/meta", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def ass_time(ms):
    cs = int(round(ms / 10.0))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(path):
    """Caption track for the 180px band ffmpeg pads below the video."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {REC_W}
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial,38,&H00F8F4F2,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, (t, _act, cap) in enumerate(BEATS):
        end = BEATS[i + 1][0] if i + 1 < len(BEATS) else SEGMENT_MS
        text = cap.replace("\n", " ").strip()
        lines.append(
            f"Dialogue: 0,{ass_time(t)},{ass_time(end)},Cap,,0,0,0,,"
            f"{{\\an5\\pos({REC_W // 2},990)}}{text}"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(head + "\n".join(lines) + "\n")


def main():
    print("waiting for server ...")
    if not wait_for_server():
        sys.exit("server never came up on " + BASE)
    print(f"server up. warming up {WARMUP_S}s ...")
    time.sleep(WARMUP_S)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        context = browser.new_context(
            viewport={"width": VIEW_W, "height": VIEW_H},
            record_video_dir=OUT_DIR,
            record_video_size={"width": REC_W, "height": REC_H},
        )
        page = context.new_page()
        page.add_init_script(
            "document.addEventListener('DOMContentLoaded',"
            f"()=>{{document.body.style.zoom='{ZOOM}';}});"
        )
        page.goto(BASE, wait_until="domcontentloaded")
        page.add_style_tag(content=SINGLE_COLUMN_CSS)
        page.wait_for_timeout(900)

        t0 = time.time()
        for i, (start_ms, action, cap) in enumerate(BEATS):
            # Sleep until this beat is due, measured from the true start.
            due = t0 + start_ms / 1000.0
            delay = due - time.time()
            if delay > 0:
                page.wait_for_timeout(int(delay * 1000))

            try:
                if action is None:
                    pass
                elif action[0] == "top":
                    page.evaluate("window.scrollTo({top:0,behavior:'smooth'})")
                elif action[0] == "card":
                    found = page.evaluate(
                        """needle => {
                            const h = [...document.querySelectorAll('h2')].find(
                                x => x.offsetParent !== null &&
                                     x.textContent.toLowerCase().includes(needle.toLowerCase()));
                            if (!h) return false;
                            (h.closest('.card') || h).scrollIntoView(
                                {behavior:'smooth', block:'start'});
                            return true;
                        }""",
                        action[1],
                    )
                    if not found:
                        print(f"  WARNING: no visible card heading matching {action[1]!r}")
                elif action[0] == "tab":
                    page.click(f"button[data-v='{action[1]}']")
                    page.evaluate("window.scrollTo({top:0,behavior:'smooth'})")
                elif action[0] == "confirm":
                    btn = page.locator("#alerts button:has-text('confirm')").first
                    if btn.count() and btn.is_visible():
                        btn.click()
                        print("  clicked confirm")
                    else:
                        print("  no confirmable alert visible - skipped")
            except Exception as e:
                print(f"  beat {i} action failed: {e}")
            print(f"  {start_ms:>7}ms  {cap[:58]}")

        remaining = SEGMENT_MS / 1000.0 - (time.time() - t0)
        if remaining > 0:
            page.wait_for_timeout(int(remaining * 1000))

        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()

    final = os.path.join(OUT_DIR, "prototype.webm")
    if os.path.exists(final):
        os.remove(final)
    os.rename(video_path, final)
    ass_path = os.path.join(OUT_DIR, "prototype.ass")
    write_ass(ass_path)
    print("SAVED:", final)
    print("SAVED:", ass_path)


if __name__ == "__main__":
    main()
