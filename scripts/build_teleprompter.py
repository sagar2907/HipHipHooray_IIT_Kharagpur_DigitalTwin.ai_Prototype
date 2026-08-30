"""Builds 10_Demo_Video/DigitalTwin_Teleprompter_Round2.html, synced to the
ACTUAL encoded duration of each segment - measured with ffprobe at build time,
never hardcoded.

Why this exists: the first version of this file hardcoded each segment's
duration as a constant. When the overview animation was re-recorded to fix a
flicker bug, its duration shifted by one frame (66.48s -> 66.44s) and every
segment after it in the teleprompter's timeline was quietly wrong by that
amount, because nothing re-derived the numbers. Measuring fresh here removes
that whole class of bug: run this after ANY segment is re-recorded and the
sync is correct by construction, not by remembering to update five constants.

    python scripts/build_video.py          # first, so _enc.mp4 files exist
    python scripts/build_teleprompter.py

The scene text (name + voiceover) for the three animated segments is
transcribed from each HTML's own SCENES array - the same words that animation
renders as its on-screen caption - and the prototype segment's lines are
transcribed from scripts/record_demo.py's own BEATS table, the same table
that generated its burned-in subtitles. So the four sources of truth for
"what does this video say" (each animation's captions, the prototype's
burned-in .ass, record_demo.py's BEATS, and this teleprompter) are always
kept to the same words - only the TIMING is independently derived here.
"""

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RAW = os.path.join(ROOT, "10_Demo_Video", "_raw")
OUT = os.path.join(ROOT, "10_Demo_Video", "DigitalTwin_Teleprompter_Round2.html")

SEGMENTS = ["intro", "overview", "virtualplant", "prototype", "deployment"]

# Authored duration baked into each animation's own `const TOTAL=...` - used
# only to compute the scale factor against the segment's true recorded
# length. Keep these in sync with the TOTAL constant in each HTML file; if
# a scene is added/removed there, update the number here to match.
AUTHORED_TOTAL_MS = {
    "overview": 62000,
    "virtualplant": 48000,
    "deployment": 52000,
}

# (authored_t_ms, name, vo) - transcribed verbatim from each animation's own
# SCENES array. Verify against the HTML source if either changes.
OVERVIEW_SCENES = [
    (0, "2 · The line & the problem", "A mixed-model assembly line. The constraint moves roughly twenty times a shift, and a defect caught late has already been built into every car since it started."),
    (10000, "2 · Uneven sensors", "Not every station is wired. Some are a person with a clipboard — and we tested whether that clipboard is honest. A ninety-six-point-five percent pass rate hid a real two-point-eight percent escape rate."),
    (22000, "2 · Prescriptive, not just predictive", "Two tools can show the identical symptom and need opposite fixes. We separate real wear from a lying sensor by checking whether a mechanically coupled channel moved too — service one, recalibrate the other, never guess."),
    (34000, "2 · Trust, measured not asserted", "Confidence is calibrated against held-out shifts, not asserted. An alert that cannot state its evidence is suppressed, not shown — and every human decision is logged, so precision is proven over time, not claimed once."),
    (46000, "2 · One model, three views", "One record stream answers a supervisor in real time, a manager's week, and leadership's investment case — and we prove it is one twin: every total reconciles exactly."),
    (58000, "2 · Close", "DigitalTwin.ai. The plant already has the data."),
]
VIRTUALPLANT_SCENES = [
    (0, "3 · We built the plant", "We could not put sensors on a real assembly line, so we built one in software — twenty stations, the buffers between them, the tools, the breaks, the rework, even the operator stops."),
    (13000, "3 · Observed vs hidden", "It writes out only what a real plant would actually record. The true answer — which fault we injected and exactly when — is written to a separate place the detector is never allowed to open."),
    (27000, "3 · Why that matters", "That is the whole point. We know the right answer and the detector does not, so we can mark its work. Every number you are about to see was scored this way."),
    (39000, "3 · The scale we ran it at", "A hundred and sixty-two simulated shifts, four different line layouts, nearly a thousand tools. Then we pointed the twin at it and watched."),
]
DEPLOYMENT_SCENES = [
    (0, "5 · What it needs", "It runs on five things a plant already records — barcode scans, machine status, buffer counts, tool readings, and the manual checklist. Nothing here is new hardware."),
    (10000, "5 · What it never does", "It never writes back to the machines that run the line. That is not a promise in a document — it is a test that checks every file in the codebase."),
    (20000, "5 · How it rolls out", "It starts in shadow mode on yesterday's data, then one supervisor, then the whole floor, then a costed sensor upgrade — and only then, a second line."),
    (30000, "5 · Does it work elsewhere?", "And we checked it moves. On four different line shapes — more stations, more merge points, even two machines working in parallel — the cost of a wrong call stayed almost flat."),
    (44000, "5 · Close (see the credit for README.md in the last few seconds)", "One module connects it to a real line. Nothing downstream changes."),
]

# Copied verbatim from scripts/record_demo.py's BEATS table, minus the
# per-beat actions (only the timing and caption matter for reading aloud).
# +900ms accounts for the settle time before that recording's own clock (t0)
# begins - the same as record_demo.py's own goto()+wait_for_timeout(900).
PROTOTYPE_SETTLE_MS = 900
PROTOTYPE_BEATS = [
    (0, "This is the twin, running live. One full eight-hour shift plays out in about three minutes."),
    (7000, "The strip along the top is the assembly line - twenty stations, in the order a car passes through them."),
    (14000, "Red is the station slowing the whole line down right now."),
    (20500, "The hatched grey ones have no sensors at all. The twin still has to work out what they are doing."),
    (27500, "It never just asserts. This table is the evidence behind the call."),
    (34500, "Each row is a station and the measured numbers that ranked it. 'Measured' means a sensor actually said so."),
    (42000, "It then says what to do about it - and what it costs if you ignore it."),
    (49500, "And it says so plainly: advisory only. It never touches the machines. A person decides."),
    (56500, "Confidence is a real probability. Before we calibrated it, it claimed 99% and was right about one time in ten."),
    (64500, "'Forming next' is the early warning - which station is about to become the problem."),
    (71500, "When that warning names a station with no sensors, it says so: DARK, inferred."),
    (78500, "The ledger is how the floor keeps score. Every call gets confirmed or overridden by a person."),
    (85500, "Some alerts are suppressed. If the twin cannot show its evidence, it stays quiet rather than guess."),
    (92500, "Confirming one now. That decision is recorded and counts towards the running accuracy."),
    (99500, "Now the defect side. This is where a drifting tool gets caught."),
    (106500, "Onset is worked out backwards, so it can list exactly which cars were built after the drift began."),
    (114000, "The ones still on the line can be reworked. The ones already finished are a customer problem."),
    (121500, "Here is the beat that matters. Two tools can move the very same way and still need opposite fixes."),
    (129000, "If a mechanically linked channel moved along with the torque, the tool really is worn. Service it."),
    (136000, "If only the torque moved, the sensor is lying. Recalibrate it - servicing would scrap good parts and fix nothing."),
    (144000, "Manual checklist stations report here, with how long the person took to write the result down."),
    (151000, "The plant manager sees the same data, a week at a time."),
    (158000, "Not an average. The constraint moves about twenty times a shift, so an average describes no real moment of it."),
    (165500, "This shows how often each station was the constraint - that is a scheduling and spending decision."),
    (173000, "Leadership sees the investment case."),
    (180000, "Every claim names the file that produced it."),
    (187000, "And one row reads NOT MEASURED - we deleted a number from our own business case because no file produced it."),
    (195000, "The reconciliation test proves these are one model, not three dashboards. Every total matches exactly."),
    (203000, "Back to the live view. The plant has been running the whole time."),
]

INTRO_SCENE = ("1 · Team intro", "Hi, we're Team HipHipHooray. I'm Sagar Sahu, and this is Priyansh Goyal, both from IIT Kharagpur.")


def probe_duration_ms(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise SystemExit(f"ffprobe failed on {path}: {r.stderr}")
    return round(float(r.stdout.strip()) * 1000)


def main():
    durations = {}
    for name in SEGMENTS:
        p = os.path.join(RAW, f"{name}_enc.mp4")
        if not os.path.exists(p):
            raise SystemExit(f"missing {p} - run scripts/build_video.py first")
        durations[name] = probe_duration_ms(p)

    seg_start = {}
    t = 0
    for name in SEGMENTS:
        seg_start[name] = t
        t += durations[name]
    total = t

    print("measured durations (ms):", durations)
    print("segment starts (ms):", seg_start)
    print("total:", total, f"({total/1000:.2f}s)")

    def scaled(seg, authored_t):
        scale = durations[seg] / AUTHORED_TOTAL_MS[seg]
        return round(seg_start[seg] + authored_t * scale)

    scenes = [{"t": 0, "name": INTRO_SCENE[0], "vo": INTRO_SCENE[1]}]
    for at, name, vo in OVERVIEW_SCENES:
        scenes.append({"t": scaled("overview", at), "name": name, "vo": vo})
    for at, name, vo in VIRTUALPLANT_SCENES:
        scenes.append({"t": scaled("virtualplant", at), "name": name, "vo": vo})
    proto_offset = seg_start["prototype"] + PROTOTYPE_SETTLE_MS
    for i, (ms, cap) in enumerate(PROTOTYPE_BEATS):
        scenes.append({"t": proto_offset + ms, "name": f"4 · Prototype beat {i+1}", "vo": cap})
    for at, name, vo in DEPLOYMENT_SCENES:
        scenes.append({"t": scaled("deployment", at), "name": name, "vo": vo})

    last = scenes[-1]["t"]
    if not (total - 20000 < last < total):
        raise SystemExit(f"sanity check failed: last scene at {last}ms, total {total}ms")
    print(f"last scene at {last}ms, {total - last}ms before the end - OK")

    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')

    scenes_js = "\n".join(
        ' {t:%d, name:"%s", vo:"%s"},' % (s["t"], esc(s["name"]), esc(s["vo"]))
        for s in scenes
    )

    total_fmt = f"{int(total // 60000)}:{int((total % 60000) // 1000):02d}"
    html = TEMPLATE.replace("__SCENES__", scenes_js).replace("__TOTAL_MS__", str(total)).replace("__TOTAL_FMT__", total_fmt)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("wrote", OUT, len(scenes), "scenes")


TEMPLATE = r"""<title>DigitalTwin.ai Teleprompter — Round 2</title>
<style>
  :root{--tsize:44px;--purple:#b98cff}
  *{box-sizing:border-box}
  html,body{height:100%}
  body{margin:0;background:#05060a;color:#e9ebf0;
       font-family:Arial,Helvetica,sans-serif;display:flex;flex-direction:column;
       overflow:hidden}

  #top{display:flex;align-items:center;gap:18px;padding:12px 24px;
       background:#0b0d12;border-bottom:1px solid #1a1e27;flex:0 0 auto}
  #scene{font:bold 15px Arial;color:var(--purple);letter-spacing:.08em}
  #clock{font:bold 16px Consolas,monospace;color:#fff}
  #left{font:14px Arial;color:#7b8296;margin-left:auto}

  #bar{height:6px;background:#161a22;flex:0 0 auto}
  #fill{height:100%;width:0;background:#7c3aed;transition:width .12s linear}

  #script{flex:1;overflow-y:auto;padding:44vh 8vw;scroll-behavior:smooth}
  #script::-webkit-scrollbar{width:0}
  .sc{font:bold 13px Arial;color:#4a5162;letter-spacing:.14em;margin:34px 0 10px}
  .chunk{font:600 var(--tsize)/1.42 Arial;display:block;margin:0 0 18px;
         color:#454b5c;transition:color .18s ease}
  .chunk.spoken{color:#2f3440}
  .chunk.now{color:#ffffff}
  .chunk.now .w{color:#ffffff}
  .chunk.now .w.pending{color:#8a92a6}
  .chunk.now .w.cur{background:#7c3aed;color:#fff;border-radius:5px;padding:2px 7px}

  #ctrl{display:flex;gap:9px;align-items:center;padding:12px 24px;
        background:#0b0d12;border-top:1px solid #1a1e27;flex:0 0 auto;flex-wrap:wrap}
  button{background:#6d28d9;color:#fff;border:0;padding:10px 17px;border-radius:5px;
         font:bold 13px Arial;cursor:pointer}
  button:hover{background:#7c3aed}
  button.g{background:#242833}
  .hint{font:12px Arial;color:#6b7285;margin-left:auto}

  #pre{position:fixed;inset:0;display:none;align-items:center;justify-content:center;
       background:rgba(5,6,10,.94);font:bold 28vh Arial;color:var(--purple);z-index:9}
  body.mirror #script{transform:scaleX(-1)}

  #note{font:12px Arial;color:#565d70;padding:8px 24px;background:#08090d;
        border-bottom:1px solid #1a1e27}
</style>

<div id="note">Synced to <b>DigitalTwin_Full_Submission_Video.mp4</b> (__TOTAL_FMT__), timings measured from the actual encoded segments — press Play here at the same instant you press play on the video.</div>
<div id="top">
  <span id="scene">READY</span>
  <span id="clock">0:00 / __TOTAL_FMT__</span>
  <span id="left">press Play — 3s countdown, then read the white line</span>
</div>
<div id="bar"><div id="fill"></div></div>
<div id="script"></div>
<div id="ctrl">
  <button id="play">▶ Play</button>
  <button id="restart" class="g">⟲ Restart</button>
  <button id="prev" class="g">◀ Scene</button>
  <button id="next" class="g">Scene ▶</button>
  <button id="b2" class="g">−2s</button>
  <button id="f2" class="g">+2s</button>
  <button id="sm" class="g">A−</button>
  <button id="bg" class="g">A+</button>
  <button id="mir" class="g">Mirror</button>
  <span class="hint">Space play/pause · R restart · ← → scenes · [ ] nudge 2s · F fullscreen</span>
</div>
<div id="pre"></div>

<script>
/* Generated by scripts/build_teleprompter.py - do not hand-edit the SCENES
   timings; re-run that script after any segment is re-recorded. */
const SCENES=[
__SCENES__
];
const TOTAL=__TOTAL_MS__;

SCENES.forEach(s=>{s.vo=s.vo.replace(/DigitalTwin\.ai/g,"DigitalTwin․ai");});

function splitVO(vo){
  const sents=vo.match(/[^.!?]+[.!?]+/g)||[vo],out=[];
  sents.forEach(s=>{
    s=s.trim();
    if(s.split(/\s+/).length<=21){out.push(s);return;}
    const marks=[];const re=/[,—;:]\s/g;let m;
    while((m=re.exec(s)))marks.push(m.index+1);
    if(!marks.length){out.push(s);return;}
    const mid=s.length/2;
    const cut=marks.reduce((a,b)=>Math.abs(b-mid)<Math.abs(a-mid)?b:a);
    out.push(s.slice(0,cut).trim(),s.slice(cut).trim());
  });
  const merged=[];
  out.filter(Boolean).forEach(p=>{
    const last=merged[merged.length-1],w=p.split(/\s+/).length;
    if(last&&(last.split(/\s+/).length<7||w<6)&&
       last.split(/\s+/).length+w<=21)merged[merged.length-1]=last+" "+p;
    else merged.push(p);
  });
  return merged;
}
const CHUNKS=[];
SCENES.forEach((s,i)=>{
  const end=(i+1<SCENES.length)?SCENES[i+1].t:TOTAL,span=end-s.t;
  const parts=splitVO(s.vo),wc=parts.map(p=>p.split(/\s+/).length);
  const tot=wc.reduce((a,b)=>a+b,0);let acc=0;
  parts.forEach((p,k)=>{
    const a=s.t+(acc/tot)*span;acc+=wc[k];
    CHUNKS.push({scene:i,t:a,end:s.t+(acc/tot)*span,text:p});
  });
});

const script=document.getElementById("script");
const els=[];
SCENES.forEach((s,i)=>{
  const h=document.createElement("div");
  h.className="sc";h.textContent=s.name;script.appendChild(h);
  CHUNKS.filter(c=>c.scene===i).forEach(c=>{
    const sp=document.createElement("span");
    sp.className="chunk";
    c.text.split(/\s+/).forEach((w,k)=>{
      const ws=document.createElement("span");
      ws.className="w";ws.textContent=(k?" ":"")+w;sp.appendChild(ws);
    });
    script.appendChild(sp);
    els.push({el:sp,c});
  });
});

const clockEl=document.getElementById("clock"),sceneEl=document.getElementById("scene"),
      leftEl=document.getElementById("left"),fill=document.getElementById("fill");
const fmt=ms=>{const s=Math.max(0,Math.floor(ms/1000));
  return Math.floor(s/60)+":"+String(s%60).padStart(2,"0");};

let playing=false,elapsed=0,t0=0,raf=null,prerolling=false,lastLive=null;

function centre(el){
  const b=script.getBoundingClientRect(),r=el.getBoundingClientRect();
  script.scrollTop+=(r.top+r.height/2)-(b.top+b.height/2);
}
function paint(){
  clockEl.textContent=fmt(elapsed)+" / "+fmt(TOTAL);
  const si=SCENES.reduce((a,s,i)=>elapsed>=s.t?i:a,0);
  const sEnd=(si+1<SCENES.length)?SCENES[si+1].t:TOTAL;
  sceneEl.textContent=SCENES[si].name;
  leftEl.textContent=Math.max(0,Math.ceil((sEnd-elapsed)/1000))+"s left in scene";
  let live=null;
  els.forEach(({el,c})=>{
    el.classList.remove("spoken","now");
    if(elapsed>=c.end)el.classList.add("spoken");
    else if(elapsed>=c.t){el.classList.add("now");live={el,c};}
  });
  if(live){
    const k=(elapsed-live.c.t)/(live.c.end-live.c.t);
    const ws=live.el.querySelectorAll(".w");
    const cur=Math.min(ws.length-1,Math.floor(k*ws.length));
    ws.forEach((w,i)=>{
      w.classList.toggle("cur",i===cur);
      w.classList.toggle("pending",i>cur);
    });
    fill.style.width=(k*100).toFixed(1)+"%";
    if(live.el!==lastLive){lastLive=live.el;centre(live.el);}
  }else fill.style.width="0%";
}
function frame(now){
  if(!playing)return;
  elapsed=Math.min(now-t0,TOTAL);paint();
  if(elapsed<TOTAL)raf=requestAnimationFrame(frame);
  else{playing=false;document.getElementById("play").textContent="▶ Play";}
}
function play(){if(playing)return;playing=true;t0=performance.now()-elapsed;
  document.getElementById("play").textContent="❚❚ Pause";raf=requestAnimationFrame(frame);}
function pause(){playing=false;cancelAnimationFrame(raf);
  document.getElementById("play").textContent="▶ Play";}
function seek(t){
  const wasPlaying=playing;pause();
  elapsed=Math.max(0,Math.min(t,TOTAL));lastLive=null;paint();
  if(wasPlaying)play();
}
function playPre(){
  if(prerolling)return;
  if(playing){pause();return;}
  if(elapsed>150){play();return;}
  prerolling=true;
  const el=document.getElementById("pre");let n=3;
  el.style.display="flex";el.textContent=n;
  const iv=setInterval(()=>{
    n--;
    if(n>0)el.textContent=n;
    else if(n===0)el.textContent="GO";
    else{clearInterval(iv);el.style.display="none";prerolling=false;play();}
  },1000);
}
const size=d=>{
  const c=parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue("--tsize"))||44;
  document.documentElement.style.setProperty("--tsize",
    Math.max(24,Math.min(88,c+d))+"px");
  lastLive=null;paint();
};
document.getElementById("play").onclick=playPre;
document.getElementById("restart").onclick=()=>{pause();elapsed=0;lastLive=null;
  paint();script.scrollTop=0;};
document.getElementById("next").onclick=()=>{
  const n=SCENES.find(s=>s.t>elapsed+250);if(n)seek(n.t);};
document.getElementById("prev").onclick=()=>{
  const p=[...SCENES].reverse().find(s=>s.t<elapsed-250);seek(p?p.t:0);};
document.getElementById("b2").onclick=()=>seek(elapsed-2000);
document.getElementById("f2").onclick=()=>seek(elapsed+2000);
document.getElementById("sm").onclick=()=>size(-4);
document.getElementById("bg").onclick=()=>size(4);
document.getElementById("mir").onclick=()=>document.body.classList.toggle("mirror");
addEventListener("keydown",e=>{
  if(e.code==="Space"){e.preventDefault();playPre();}
  else if(e.key==="r"||e.key==="R")document.getElementById("restart").click();
  else if(e.key==="ArrowRight")document.getElementById("next").click();
  else if(e.key==="ArrowLeft")document.getElementById("prev").click();
  else if(e.key==="[")seek(elapsed-2000);
  else if(e.key==="]")seek(elapsed+2000);
  else if(e.key==="f"||e.key==="F")document.documentElement.requestFullscreen?.();
  else if(e.key==="m"||e.key==="M")document.body.classList.toggle("mirror");
});
paint();
</script>
"""

if __name__ == "__main__":
    main()
