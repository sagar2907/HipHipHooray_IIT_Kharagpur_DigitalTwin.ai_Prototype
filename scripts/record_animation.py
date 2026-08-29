"""Records one of the self-contained SVG animations in 5_Animation_Sources/
to video, via Playwright's native recorder against real Chrome - same method
as record_demo.py, so every clip in the final video is captured the same way.

Usage: python record_animation.py <html_file> <duration_ms> <out_name>
"""

import os
import sys

from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "10_Demo_Video", "_raw")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    html_path = os.path.abspath(sys.argv[1])
    duration_ms = int(sys.argv[2])
    out_name = sys.argv[3]

    url = "file:///" + html_path.replace("\\", "/") + "?auto=1&bare=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        # Playwright's recorder captures the viewport at CSS-pixel size and
        # PADS to record_video_size - it does not scale up, and
        # device_scale_factor does not change what lands in the video. So to
        # actually record 1080p, the viewport must BE 1080p and the page is
        # zoomed to fill it: the stage is authored at 1280x720, and 1280 x 1.5
        # = 1920, 720 x 1.5 = 1080 exactly. Zoom (not transform) is what
        # reflows the layout to the authored 1280 width.
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=OUT_DIR,
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        page.add_init_script(
            "document.addEventListener('DOMContentLoaded',"
            "()=>{document.body.style.zoom='1.5';});"
        )
        page.goto(url)
        page.wait_for_timeout(duration_ms + 400)
        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()

    final = os.path.join(OUT_DIR, out_name + ".webm")
    if os.path.exists(final):
        os.remove(final)
    os.rename(video_path, final)
    print("SAVED:", final)


if __name__ == "__main__":
    main()
