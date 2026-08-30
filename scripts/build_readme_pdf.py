"""Renders README.md to README.pdf for platforms that require a PDF upload
(the Unstop submission form asks for the README as a PDF, max 20MB - the repo
itself carries the .md as the source of truth).

    pip install markdown
    python scripts/build_readme_pdf.py
    # then print via headless Chrome, see the command it prints

Deliberately no nl2br: this README's paragraphs are hard-wrapped at ~80 chars
with single newlines meant to reflow as one paragraph. nl2br would break every
one of them into short fragments - only the title's own line break needed
fixing, and that was fixed in the source (a blank line between the two lines),
not by changing how the whole file converts.
"""

import io
import os
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

STYLE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>DigitalTwin.ai - README</title>
<style>
@page { size: A4; margin: 16mm 15mm 14mm 15mm; }
body{font:10.5pt/1.5 "Segoe UI",Arial,sans-serif;color:#1b1e21;margin:0;max-width:none}
h1{font-size:22pt;margin:0 0 6px;letter-spacing:-.4px;color:#12171b;border-bottom:3px solid #1c5d99;padding-bottom:8px}
h2{font-size:14pt;margin:22px 0 8px;padding-bottom:4px;border-bottom:1.5px solid #1c5d99;color:#1c5d99;page-break-after:avoid}
h3{font-size:11.5pt;margin:15px 0 5px;color:#24303a;page-break-after:avoid}
p{margin:0 0 8px}
hr{border:0;border-top:1px solid #d8dee3;margin:14px 0}
a{color:#1c5d99}
code{font-family:Consolas,monospace;font-size:9pt;background:#eef2f5;padding:0 4px;border-radius:2px}
pre{background:#12171b;color:#e9ebf0;padding:10px 14px;border-radius:6px;overflow-x:auto;
    font-size:8.7pt;line-height:1.5;page-break-inside:avoid}
pre code{background:none;color:inherit;padding:0}
table{width:100%;border-collapse:collapse;font-size:9pt;margin:8px 0 12px}
table{page-break-inside:auto} tr{page-break-inside:avoid} thead{display:table-header-group}
th{background:#eef2f5;text-align:left;padding:5px 7px;border:1px solid #c9d2d9;font-size:8.5pt}
td{padding:5px 7px;border:1px solid #d8dee3;vertical-align:top}
ul,ol{margin:0 0 8px;padding-left:20px} li{margin-bottom:3px}
strong{color:#12171b}
</style></head><body>
"""


def main():
    src = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    body = markdown.markdown(src, extensions=["tables", "fenced_code"])
    html_path = os.path.join(ROOT, "README_render.html")
    io.open(html_path, "w", encoding="utf-8", newline="\n").write(
        STYLE + body + "\n</body></html>"
    )
    pdf_path = os.path.join(ROOT, "README.pdf")
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path]
    print("running:", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(1)
    os.remove(html_path)
    print("wrote", pdf_path, os.path.getsize(pdf_path), "bytes")


if __name__ == "__main__":
    main()
