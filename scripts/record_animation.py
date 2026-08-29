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
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=OUT_DIR,
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
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
