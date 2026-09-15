"use client";

import { useEffect, useRef, useState } from "react";
import lessonData from "@/data/wiring-lessons.json";
import wiring from "@/data/wiring.json";

const BASE = "/downloads/wiring-guide";
const PDF = `${BASE}/Codex-Micro-LED-Wiring-Guide.pdf`;
const KEY = "codexmicro:wiring-checkpoints:v1";
type Step = { id: string; title: string; how: string[]; why: string; check: string; trace: string | null; links: {label: string; url: string}[] };
type Phase = { id: string; title: string; intro: string; need: string; groups: {title: string; steps: Step[]}[] };
const lessons: Phase[] = lessonData;
const allSteps = lessons.flatMap(phase => phase.groups.flatMap(group => group.steps));
const knownIds = new Set(allSteps.map(step => step.id));

export default function WiringLessons() {
  const [done, setDone] = useState<string[]>([]);
  const [storageAvailable, setStorageAvailable] = useState(true);
  useEffect(() => {
    try {
      const saved: unknown = JSON.parse(localStorage.getItem(KEY) || "[]");
      if (Array.isArray(saved)) setDone([...new Set(saved.filter((id): id is string => typeof id === "string" && knownIds.has(id)))]);
    } catch { setStorageAvailable(false); }
  }, []);
  function toggle(id: string) {
    const next = done.includes(id) ? done.filter(item => item !== id) : [...done, id];
    setDone(next);
    try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { setStorageAvailable(false); }
  }

  return <div className="bench-guide">
    <p className="bench-lead">One small circuit at a time. Start with the knob, build the LED circuit on the perfboard, then light one key. These are the short steps from our workbench walkthrough, with a reason and a checkpoint for each.</p>
    <div className="bench-downloads"><a href={PDF} target="_blank" rel="noopener noreferrer">Read the wiring PDF ↗</a><a href={PDF} download>Download PDF ↓</a><a href={`${BASE}/wiring-starter.zip`} download>Test code + libraries ↓</a></div>
    <nav className="bench-index" aria-label="Wiring stages"><ol>{lessons.map((phase,i) => <li key={phase.id}><a href={`#${phase.id}`}><span>{i+1}</span>{phase.title}</a></li>)}<li><a href="#wiring-rest"><span>6</span>Finish the remaining circuits</a></li></ol></nav>
    <p className="bench-progress" aria-live="polite">{done.length} of {allSteps.length} checkpoints complete. {storageAvailable ? "Saved in this browser on this device." : "Browser storage is unavailable; checks will not persist after reload."}</p>
    <details className="bench-basics"><summary>New to soldering? Read this first.</summary><div>
      <p><b>USB stays unplugged while you solder or move wires.</b> Power on only at the test checkpoints. A soldering iron holder, ventilation and eye protection make the work easier and safer.</p>
      <p><b>A ribbon cable is several insulated wires joined side by side.</b> Peel apart the conductors you need without nicking the insulation. Strip only the ends. Four inches is about 10 cm; 3 mm is roughly ⅛ inch.</p>
      <p><b>Hold the part, not the hot joint.</b> Use a small vise, helping hands, or heat-resistant tape on a soldering surface. Tin the pad and wire, bring them together, then briefly heat both. Keep still as the joint cools.</p>
      <p><b>Perfboard holes are separate.</b> An insulated wire goes across the top. Underneath, its bare end bends to the target pad or chip leg. Solder both contacts. Use the bare wire to span the gap rather than a large solder blob. Trim only the leftover tail; hold the offcut as you clip.</p>
      <p><b>Ground is a shared connection.</b> G and GND on the KB2040 are the same ground. A4 on the perfboard means column A, row 04; it is not a KB2040 pin name. The underside is mirrored, so locate holes from the top before flipping the board.</p>
      <p>These soldered connections can stay in the finished build, but wire lengths, insulation and enclosure fit must be checked before fastening the plate. Printed mounts remain prototypes.</p>
    </div></details>

    {lessons.map((phase, phaseIndex) => <section id={phase.id} className="bench-phase" aria-labelledby={`${phase.id}-title`} key={phase.id}>
      <header><span className="bench-phase-number">{String(phaseIndex+1).padStart(2,"0")}</span><div><h3 id={`${phase.id}-title`}>{phase.title}</h3><p>{phase.intro}</p></div></header>
      <p className="bench-materials"><b>Have ready</b> {phase.need}</p>
      {phase.id === "wiring-knob-button" && <KnobVisual rotation={false} />}
      {phase.id === "wiring-knob-turn" && <KnobVisual rotation />}
      {phase.id === "wiring-perfboard" && <CircuitExplorer />}
      {phase.groups.map(group => <div className="bench-group" key={group.title}>
        <h4>{group.title}</h4>
        {group.steps.map((step,index) => <BenchStep key={step.id} step={step} index={index} checked={done.includes(step.id)} toggle={toggle} />)}
      </div>)}
      <a className="bench-next" href={`#${lessons[phaseIndex+1]?.id || "wiring-rest"}`}>Next: {lessons[phaseIndex+1]?.title || "the remaining circuits"} ↓</a>
    </section>)}
    <RemainingCircuits />
    <details className="bench-basics"><summary>Component references &amp; what has been tested</summary><div>
      <p>The knob’s button and rotation were exercised during the bench walkthrough. The one-LED configuration ran on the KB2040, but a successful program log is not confirmation that the external LED lit. Confirm each checkpoint on your own build. The finished keyboard, LED chain and printed mounts still need full assembly testing.</p>
      <p>The PDF and explorer document the shared-ground reroute we used at A3/A4. If you use an otherwise free KB2040 GND pad, you can leave the knob ground in place instead.</p>
      <ul><li><a href="https://learn.adafruit.com/adafruit-kb2040/pinouts" target="_blank" rel="noreferrer">Adafruit KB2040 pin labels</a></li><li><a href="https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf" target="_blank" rel="noreferrer">TI SN74AHCT125 pin functions</a></li><li><a href="https://www.adafruit.com/product/377" target="_blank" rel="noreferrer">Adafruit 377 rotary encoder</a></li><li><a href="https://www.adafruit.com/product/4776" target="_blank" rel="noreferrer">Adafruit 4776 RGBW mini LEDs</a></li><li><a href="https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices" target="_blank" rel="noreferrer">NeoPixel wiring and power practices</a></li><li><a href={`${BASE}/library-sources.json`}>Starter library versions and licenses</a></li></ul>
      <p>KB2040 photo: Adafruit. Encoder underside and wires are explanatory drawings; follow your component’s terminals and printed labels.</p>
    </div></details>
  </div>;
}

function BenchStep({ step, index, checked, toggle }: { step: Step; index: number; checked: boolean; toggle: (id: string) => void }) {
  return <details className={`bench-step${checked ? " is-complete" : ""}`} id={`step-${step.id}`}>
    <summary><span className="bench-step-number">{checked ? "✓" : String(index+1).padStart(2,"0")}</span><span>{step.title}</span><span className="bench-expand" aria-hidden="true">+</span></summary>
    <div className="bench-step-body">
      <ol>{step.how.map((line,i) => <li key={i}>{line}</li>)}</ol>
      <div className="bench-why"><b>Why</b><p>{step.why}</p></div>
      <div className="bench-check"><b>Check</b><p>{step.check}</p></div>
      {(step.links.length > 0 || step.trace) && <div className="bench-step-links">{step.links.map(link => <a key={link.url} href={link.url} download={link.url.startsWith("/") || undefined} target={link.url.startsWith("/") ? undefined : "_blank"} rel={link.url.startsWith("/") ? undefined : "noopener noreferrer"}>{link.label} {link.url.startsWith("/") ? "↓" : "↗"}</a>)}{step.trace && <a href={`${BASE}/circuit.html?trace=${step.trace}`} target="_blank" rel="noopener noreferrer">See this wire on the diagram ↗</a>}</div>}
      <label className="bench-complete"><input type="checkbox" checked={checked} onChange={() => toggle(step.id)} /> I checked this step</label>
    </div>
  </details>;
}

function CircuitExplorer() {
  const frame = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(850);
  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== location.origin || event.source !== frame.current?.contentWindow || event.data?.type !== "micro:wiring-height") return;
      const next = event.data.height;
      if (typeof next === "number" && Number.isFinite(next) && next > 100 && next < 2200) setHeight(Math.ceil(next)+4);
    };
    window.addEventListener("message", receive);
    return () => window.removeEventListener("message", receive);
  }, []);
  return <div className="bench-explorer">
    <div className="bench-explorer-heading"><h4>Understand what you’re connecting</h4><a href={`${BASE}/circuit.html`} target="_blank" rel="noopener noreferrer">Open diagram ↗</a></div>
    <iframe ref={frame} src={`${BASE}/circuit.html`} title="Perfboard wiring explorer: follow power, ground or LED data" loading="lazy" style={{height}} />
    <p>All coordinates use the same top view. Solid lines are insulated wires; dashed links show the soldered connections underneath. The chip’s legs are numbered separately from the perfboard holes.</p>
    <a href={PDF} target="_blank" rel="noopener noreferrer">Prefer paper? Open the six-page PDF ↗</a>
  </div>;
}

function KnobVisual({ rotation }: { rotation: boolean }) {
  const active = rotation ? ["TX","RX","GND"] : ["G","A2"];
  return <figure className="bench-knob-figure"><div className="bench-knob-pair">
    <svg viewBox="0 0 710 430" role="img" aria-label={`KB2040 component side, USB on the left. Use ${active.join(", ")}.`}>
      <svg x="0" y="25" width="710" height="385" viewBox="120 185 710 385"><image href="/images/wiring/kb2040.jpg" width="970" height="728" /></svg>
      {active.map(id => { const p=wiring.kbPins.find(p=>p.id===id)!; const x=p.x-120,y=p.y-185+25, top=p.y<300; return <g key={id}><circle cx={x} cy={y} r="13" fill="none" stroke="white" strokeWidth="8"/><circle cx={x} cy={y} r="13" fill="none" stroke="#6a853e" strokeWidth="4"/><text x={x} y={top?20:426} textAnchor="middle" fontSize="22" fill="#283323">{id}</text></g>; })}
    </svg>
    <svg viewBox="0 0 380 330" role="img" aria-label={rotation ? "Encoder underside. Three terminals: outer to TX, middle to GND, outer to RX." : "Encoder underside. Use the two button terminals, one to G and the other to A2."}>
      <rect x="87" y="95" width="206" height="150" rx="16" fill="#315947" stroke="#223c30" strokeWidth="3"/><circle cx="190" cy="168" r="34" fill="#70917b"/><rect x="75" y="149" width="12" height="45" fill="#adb3ae"/><rect x="293" y="149" width="12" height="45" fill="#adb3ae"/>
      {[140,240].map((x,i)=><g key={x}><path d={`M${x} 95V57`} stroke={rotation?"#aeb4b0":"#6a853e"} strokeWidth="10"/><text x={x} y="41" textAnchor="middle" fill={rotation?"#73796f":"#283323"} fontSize="18">{rotation?"Button":i===0?"G":"A2"}</text></g>)}
      {[125,190,255].map((x,i)=><g key={x}><path d={`M${x} 245V280`} stroke={rotation?"#6a853e":"#aeb4b0"} strokeWidth="10"/><text x={x} y="308" textAnchor="middle" fill={rotation?"#283323":"#73796f"} fontSize="18">{rotation?["TX","GND","RX"][i]:["Outer","Middle","Outer"][i]}</text></g>)}
      <text x="190" y="174" textAnchor="middle" fontSize="15" fill="white">UNDERSIDE</text>
    </svg>
  </div><figcaption>{rotation ? "Three-terminal side: ground in the middle, TX and RX on the outside. Reversed rotation is corrected in software." : "Two-terminal side: the pushbutton. The pictured terminal order may be swapped; the button has no polarity."} Match the terminal groups, not the orientation of the knob cap.</figcaption></figure>;
}

function RemainingCircuits() {
  const refs = wiring.chapters.filter(c=>["matrix","pixels","controls","extras"].includes(c.id));
  return <section id="wiring-rest" className="bench-phase" aria-labelledby="wiring-rest-title">
    <header><span className="bench-phase-number">06</span><div><h3 id="wiring-rest-title">Finish the remaining circuits</h3><p>Get the knob and one LED working before moving on. These are the remaining wiring references, not completed bench checkpoints.</p></div></header>
    <p>Fit-test the top plate before soldering the keys. A hand-wired switch matrix makes plate replacement a desoldering job; it is not hot-swappable.</p>
    <p><b>Before adding more LEDs:</b> plan their physical order and wire lengths. The full design has six key LEDs and eight perimeter LEDs. Add the planned bulk capacitor across the LED supply, confirm its polarity, and review the total current against the USB supply and KB2040 RAW protection. Do not simply run 14 pixels at full white or bypass the fuse.</p>
    {refs.map(chapter=><details className="bench-basics" key={chapter.id}><summary>{({matrix:"Add the key matrix",pixels:"Extend the LED chain",controls:"Connect the joystick",extras:"Add touch and bank indicators"} as Record<string,string>)[chapter.id]}</summary><div><p>{chapter.intro}</p><p>{chapter.orientation}</p>{chapter.steps.filter(s=>chapter.id!=="controls"||s.id.startsWith("joy-")).map(s=><div className="bench-reference-step" key={s.id}><h4>{s.title}</h4><p><b>{s.from_} → {s.to}</b></p><p>{s.how}</p><p><b>Check:</b> {s.check}</p></div>)}</div></details>)}
    <p>The <a href="#software">full-keyboard firmware</a> uses a different mapping from these small tests: function keys for the matrix and scrolling for the dial. Install it only after its required circuits are ready, and re-check the mappings you want.</p>
  </section>;
}
