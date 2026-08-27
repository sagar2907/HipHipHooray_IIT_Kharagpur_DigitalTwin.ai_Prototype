#!/usr/bin/env python3
"""DigitalTwin.ai — the live loop, served over SSE.

    python web/server.py --run <run_dir> [--speed 60] [--port 8000]

Then open http://127.0.0.1:8000

Why SSE and not WebSockets: the stream is one-way (twin -> viewer) and SSE
reconnects on its own, over plain HTTP, with no extra client library. The one
thing that travels the other way is a human confirming or overriding an alert,
and that is a POST - which is the correct shape anyway, because it is the
ISA-95 boundary: the twin advises, a person decides, and that decision is
recorded rather than assumed.

The server holds no analysis logic. It drives twin.loop.TwinLoop and forwards
frames. Everything defensible happens in src/twin/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from twin.record import Recorder          # noqa: E402
from twin.loop import TwinLoop            # noqa: E402
from twin.genealogy import assess_all     # noqa: E402

app = FastAPI(title="DigitalTwin.ai")
STATE: dict = {}


@app.get("/")
def index():
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as fh:
        return HTMLResponse(fh.read())


@app.get("/meta")
def meta():
    rec = STATE["loop"].rec
    dark = rec.dark_stations
    return JSONResponse({
        "run": os.path.basename(STATE["run_dir"].rstrip("/\\")),
        "speed": STATE["speed"],
        "step_s": STATE["step_s"],
        "horizon_s": rec.horizon_s,
        # the FULL spine, dark stations included - the gaps are the story
        "spine": rec.spine,
        "dark": dark,
        "stations": len(rec.spine),
        "instrumented": len(rec.spine) - len(dark),
    })


@app.get("/stream")
async def stream():
    """One frame per tick, paced to the requested replay speed."""
    loop: TwinLoop = STATE["loop"]
    speed: float = STATE["speed"]
    delay = loop.step_s / speed

    # One stream drives the loop. A page refresh opens a second connection to
    # the SAME loop, which was double-advancing the shift counter and racing
    # the ledger. The newest connection takes ownership and older ones retire.
    STATE["gen"] = STATE.get("gen", 0) + 1
    mine = STATE["gen"]

    async def gen():
        runs = STATE["runs"]
        i = 0
        while True:
            for frame in loop.frames():
                if STATE["gen"] != mine:
                    return          # a newer viewer took over

                # let /genealogy follow the replay clock, so the containment
                # panel is causal too rather than jumping to end-of-shift
                STATE["now_s"] = frame["t_s"]
                STATE["constraint"] = frame.get("constraint")
                yield f"data: {json.dumps(frame)}\n\n"
                await asyncio.sleep(delay)

            i += 1
            if STATE["gen"] != mine:
                return
            if not STATE["continuous"] or i >= len(runs) * STATE["cycles"]:
                yield f"data: {json.dumps({'done': True})}\n\n"
                return
            # roll onto the next shift. The ledger carries; the shift-local
            # state does not - see TwinLoop.next_shift.
            nxt = runs[i % len(runs)]
            loop.next_shift(Recorder.from_dir(nxt, i))
            STATE["run_dir"] = nxt
            marker = {"shift_change": True, "shift_no": loop.shift_no,
                      "run": os.path.basename(nxt.rstrip("/\\"))}
            yield f"data: {json.dumps(marker)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.post("/alert/{index}/{outcome}")
def resolve(index: int, outcome: str):
    """A human confirms or overrides. The twin never writes this itself."""
    if outcome not in ("confirmed", "overridden"):
        return JSONResponse({"error": "outcome must be confirmed|overridden"},
                            status_code=400)
    loop: TwinLoop = STATE["loop"]
    loop.resolve(index, outcome)
    return JSONResponse({"ok": True, "precision": loop.ledger.precision,
                         "scored": loop.ledger.scored})


@app.get("/genealogy")
def genealogy(at_s: int = 0):
    """Tool health, containment lists, and the stop-or-continue call.

    Causal: nothing past `at_s` is read. Defaults to the loop's current time
    so the panel tracks the replay.
    """
    loop: TwinLoop = STATE["loop"]
    rec = loop.rec
    if rec.tools is None or rec.tools.empty:
        return JSONResponse({"available": False,
                             "reason": "this run has no tool telemetry"})
    t = at_s or STATE.get("now_s") or rec.horizon_s
    rows = assess_all(rec.tools, rec.run.scans, t, rec.exit_station,
                      rec.run.buffers, STATE.get("constraint"))
    return JSONResponse({"available": True, "at_s": int(t),
                         "exit_station": rec.exit_station, "tools": rows})


@app.get("/rollup")
def rollup():
    """Manager + leadership views. Precomputed by scripts/build_rollup.py so
    every figure is traceable to a file and regenerable by one command."""
    p = os.path.join(HERE, "..", "results", "rollup.json")
    if not os.path.exists(p):
        return JSONResponse(
            {"error": "no rollup yet",
             "fix": "python scripts/build_rollup.py --runs 15"}, status_code=404)
    with open(p, encoding="utf-8") as fh:
        return JSONResponse(json.load(fh))


@app.get("/alerts")
def alerts():
    """Every alert with all five contract fields (design Part 4.2)."""
    loop: TwinLoop = STATE["loop"]
    return JSONResponse({
        "suppressed": loop.ledger.suppressed,
        "calibrated": bool(loop.calibration),
        "calibration": {k: loop.calibration.get(k) for k in
                        ("ece_before", "ece_after", "gate_within_10pts",
                         "n_fit", "n_holdout")} if loop.calibration else None,
        "alerts": [{
            "i": i, "clock": f"{(int(a.at_s) + 6 * 3600) // 3600 % 24:02d}:"
                             f"{(int(a.at_s) % 3600) // 60:02d}",
            "station": a.station, "kind": a.kind, "confidence": a.confidence,
            "detail": a.detail, "outcome": a.outcome,
            "margin_s": a.margin_s, "evidence": a.evidence,
            "persistence_min": a.persistence_min, "action": a.action,
            "cost_if_ignored": a.cost_if_ignored,
        } for i, a in enumerate(loop.ledger.alerts)]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=os.path.join(
        HERE, "..", "..", "digitaltwin.ai", "dataset", "v5", "flow",
        "runs", "L1_run_001"))
    ap.add_argument("--speed", type=float, default=60.0,
                    help="replay speed-up; 60 = an 8 h shift in 8 min")
    ap.add_argument("--step", type=int, default=300,
                    help="loop period in simulated seconds")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--shifts", type=int, default=1,
                    help="how many consecutive shifts to replay; the alert "
                         "ledger carries across them (Complexity 7: validated "
                         "over time). 0 = run forever, cycling the runs.")
    a = ap.parse_args()

    if not os.path.isdir(a.run):
        sys.exit(f"run directory not found: {a.run}\n"
                 f"Point --run at a dataset run, e.g. dataset/v5/flow/runs/L1_run_001")

    # consecutive shifts = consecutive runs in the same flow directory
    parent = os.path.dirname(os.path.abspath(a.run))
    first = os.path.basename(os.path.abspath(a.run))
    prefix = first.rsplit("_run_", 1)[0] + "_run_" if "_run_" in first else ""
    siblings = sorted(d for d in os.listdir(parent)
                      if d.startswith(prefix)) if prefix else [first]
    start = siblings.index(first) if first in siblings else 0
    ordered = siblings[start:] + siblings[:start]
    runs = [os.path.join(parent, d) for d in ordered]
    STATE["runs"] = runs
    STATE["continuous"] = (a.shifts != 1)
    STATE["cycles"] = 10 ** 6 if a.shifts == 0 else max(1, a.shifts)

    rec = Recorder.from_dir(a.run, 0)
    cal = None
    cp = os.path.join(HERE, "..", "results", "calibration.json")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as fh:
            cal = json.load(fh)
        print(f"  calib : ECE {cal['ece_before']:.3f} -> {cal['ece_after']:.3f} "
              f"(fitted on {len(cal['fit_runs'])} runs, this run excluded)")
    else:
        print("  calib : none — confidence will be labelled an ordering score")
    STATE.update(run_dir=a.run, speed=a.speed, step_s=a.step,
                 loop=TwinLoop(rec, step_s=a.step, calibration=cal))

    import uvicorn
    print(f"  run   : {a.run}")
    print(f"  shifts: {'continuous (cycling ' + str(len(runs)) + ' runs)' if a.shifts == 0 else a.shifts}"
          f"  — ledger carries across shifts")
    print(f"  speed : {a.speed}x  ({rec.horizon_s / a.speed / 60:.1f} min for an "
          f"{rec.horizon_s / 3600:.0f} h shift)")
    print(f"  open  : http://127.0.0.1:{a.port}")
    uvicorn.run(app, host="127.0.0.1", port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
