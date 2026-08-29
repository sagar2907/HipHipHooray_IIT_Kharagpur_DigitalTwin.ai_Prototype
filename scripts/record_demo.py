"""Records a silent walkthrough of the DigitalTwin.ai prototype for voiceover.

Drives real Chrome (via Playwright) against the live demo server exactly as
DEMO_RUNBOOK.md describes doing by hand, and lets Playwright's native video
recorder capture the session continuously and in real wall-clock time - a true
recording, not a screenshot slideshow. Server runs at --speed 120, matching the
runbook's measured beat timeline, so the beats named in DEMO_RUNBOOK.md land at
the same wall-clock moments described there.
"""

import os
import time
import urllib.request

from playwright.sync_api import sync_playwright

PORT = 8099
BASE = f"http://127.0.0.1:{PORT}"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "10_Demo_Video", "_raw")
os.makedirs(OUT_DIR, exist_ok=True)


def wait_for_server(timeout=30):
    for _ in range(timeout):
        try:
            urllib.request.urlopen(BASE + "/meta", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def main():
    print("waiting for server...")
    assert wait_for_server(), "server never came up"
    print("server up. warming up 22s (runbook: skip the 'not enough units' opener)...")
    time.sleep(22)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=OUT_DIR,
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        print("recording started -> navigating")
        page.goto(BASE, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        # ---- 0:00-0:22 top of Supervisor view: line, evidence, action, status
        page.wait_for_timeout(22_000)

        # ---- 0:22-0:32 reveal Forming Next + Alert Ledger
        page.evaluate("document.getElementById('alerts')?.scrollIntoView({behavior:'smooth', block:'center'})")
        page.wait_for_timeout(10_000)

        # ---- 0:32-1:47 reveal Genealogy + Manual checklist, hold through the
        #      star beat (opposite-actions pair lands here per the runbook)
        page.evaluate("document.querySelector('#geno')?.scrollIntoView({behavior:'smooth', block:'start'})")
        page.wait_for_timeout(75_000)

        # ---- 1:47-2:02 back to the top - line + status, one alert confirmed live
        page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
        page.wait_for_timeout(4_000)
        try:
            btn = page.locator("#alerts button:has-text('confirm')").first
            if btn.is_visible(timeout=3000):
                btn.click()
                print("clicked confirm on a live alert")
        except Exception as e:
            print("no confirmable alert on screen yet:", e)
        page.wait_for_timeout(11_000)

        # ---- 2:02-2:20 Plant manager view
        page.click("button[data-v='mgr']")
        page.wait_for_timeout(4_000)
        page.evaluate("window.scrollBy({top:260, behavior:'smooth'})")
        page.wait_for_timeout(14_000)

        # ---- 2:20-2:45 Leadership view - reconciliation test + CONWIP row
        page.click("button[data-v='led']")
        page.wait_for_timeout(4_000)
        page.evaluate("window.scrollBy({top:280, behavior:'smooth'})")
        page.wait_for_timeout(13_000)
        page.evaluate("window.scrollBy({top:280, behavior:'smooth'})")
        page.wait_for_timeout(8_000)

        # ---- 2:45-3:05 back to the live Supervisor view to close on the running plant
        page.click("button[data-v='sup']")
        page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
        page.wait_for_timeout(20_000)

        print("stopping recording")
        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()
        print("SAVED:", video_path)


if __name__ == "__main__":
    main()
