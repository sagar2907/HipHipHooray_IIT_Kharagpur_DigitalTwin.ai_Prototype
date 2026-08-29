"""Encodes the recorded clips and assembles the full submission video.

Run after scripts/record_animation.py and scripts/record_demo.py have produced
the raw .webm clips in 10_Demo_Video/_raw/.

  python scripts/build_video.py

Every input is normalised to 1920x1080 / 25 fps before the concat, so a single
mismatched clip cannot silently distort or drop frames at a cut. The prototype
clip is recorded at 1920x900 and padded to 1080 with its caption band, into
which its .ass caption track is burned.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VID = os.path.abspath(os.path.join(HERE, "..", "10_Demo_Video"))
RAW = os.path.join(VID, "_raw")
OUT = os.path.join(VID, "DigitalTwin_Full_Submission_Video.mp4")

BAND_BG = "0x0b0d12"     # matches the animations' caption band
BAND_RULE = "0x242833"   # the 1px divider above it

# In final running order.
SEGMENTS = ["intro", "overview", "virtualplant", "prototype", "deployment"]


def run(cmd, **kw):
    print("+", " ".join(cmd[:6]), "...")
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(f"command failed: {cmd[0]}")
    return r


def probe(path, entries="stream=width,height:format=duration"):
    r = run(["ffprobe", "-v", "error", "-show_entries", entries,
             "-of", "default=noprint_wrappers=1", path])
    return dict(
        line.split("=", 1) for line in r.stdout.strip().splitlines() if "=" in line
    )


def encode(name):
    src = os.path.join(RAW, f"{name}.webm")
    dst = os.path.join(RAW, f"{name}_enc.mp4")
    if not os.path.exists(src):
        sys.exit(f"missing raw clip: {src}")

    if name == "prototype":
        ass = os.path.join(RAW, "prototype.ass")
        if not os.path.exists(ass):
            sys.exit("missing prototype.ass caption track")
        # Pad the 1920x900 capture to 1080 and burn the captions into the band.
        # Run from RAW so the subtitles filter gets a bare filename - a Windows
        # absolute path with a drive-letter colon is parsed as filter syntax.
        vf = (f"pad=1920:1080:0:0:color={BAND_BG},"
              f"drawbox=x=0:y=900:w=1920:h=2:color={BAND_RULE}@1.0:t=fill,"
              f"subtitles=prototype.ass")
        cwd = RAW
    else:
        vf = "scale=1920:1080:force_original_aspect_ratio=decrease," \
             "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=" + BAND_BG
        cwd = None

    run(["ffmpeg", "-y", "-i", src, "-vf", vf, "-r", "25",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
         "-crf", "18", "-preset", "slow", "-movflags", "+faststart", "-an",
         dst], cwd=cwd)
    info = probe(dst)
    print(f"    {name}: {info.get('width')}x{info.get('height')} "
          f"{float(info.get('duration', 0)):.2f}s")
    return dst, float(info.get("duration", 0))


def main():
    encoded, durations = [], []
    for name in SEGMENTS:
        path, dur = encode(name)
        encoded.append(path)
        durations.append(dur)

    # Normalise every input again inside the concat: identical fps, size, SAR
    # and pixel format. Without this a single odd clip distorts the whole cut.
    parts = "".join(
        f"[{i}:v]fps=25,scale=1920:1080,setsar=1,format=yuv420p[v{i}];"
        for i in range(len(encoded))
    )
    chain = "".join(f"[v{i}]" for i in range(len(encoded)))
    filt = f"{parts}{chain}concat=n={len(encoded)}:v=1:a=0[outv]"

    cmd = ["ffmpeg", "-y"]
    for p in encoded:
        cmd += ["-i", p]
    cmd += ["-filter_complex", filt, "-map", "[outv]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-crf", "19", "-preset", "slow", "-movflags", "+faststart", OUT]
    run(cmd)

    info = probe(OUT)
    total, expected = float(info["duration"]), sum(durations)
    print(f"\n  {OUT}")
    print(f"  {info['width']}x{info['height']}  {total:.2f}s "
          f"({int(total // 60)}:{int(total % 60):02d})  "
          f"{os.path.getsize(OUT) / 1e6:.1f} MB")
    print(f"  expected {expected:.2f}s  drift {abs(total - expected):.3f}s")
    if abs(total - expected) > 0.5:
        sys.exit("FAIL: concat duration does not match the sum of its inputs")
    print("  duration matches the sum of its parts - no frames lost at a cut")

    t = 0.0
    print("\n  segment boundaries:")
    for name, d in zip(SEGMENTS, durations):
        print(f"    {int(t // 60)}:{int(t % 60):02d}  {name}")
        t += d


if __name__ == "__main__":
    main()
