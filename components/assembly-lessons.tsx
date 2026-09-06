"use client";

import { useEffect, useRef, useState } from "react";
import lessons from "@/data/assembly-lessons.json";
import catalog from "@/data/parts.json";

const parts = new Map(catalog.map(part => [part.id, part]));

export default function AssemblyLessons({ onSelect }: { onSelect: (id: string) => void }) {
  const [index, setIndex] = useState(0);
  const [status, setStatus] = useState("loading");
  const step = lessons[index];
  const frame = useRef<HTMLIFrameElement>(null);
  const panel = useRef<HTMLElement>(null);

  useEffect(() => {
    function receive(event: MessageEvent) {
      if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return;
      if (event.data?.type === "micro:ready") {
        frame.current?.contentWindow?.postMessage({ type: "micro:lesson", id: step.id }, window.location.origin);
      }
      if (event.data?.type === "micro:lesson-applied" && event.data.id === step.id) setStatus("ready");
      if (event.data?.type === "micro:error") setStatus("unavailable");
      if (event.data?.type === "micro:select" && typeof event.data.partId === "string") onSelect(event.data.partId);
    }
    window.addEventListener("message", receive);
    frame.current?.contentWindow?.postMessage({ type: "micro:lesson", id: step.id }, window.location.origin);
    return () => window.removeEventListener("message", receive);
  }, [step.id, onSelect]);

  function choose(next: number) {
    if (next === index) return;
    setIndex(next);
    setStatus("loading");
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    panel.current?.scrollIntoView({ block: "start", behavior: reduce ? "instant" : "smooth" });
  }

  return (
    <div className="assembly-lessons" id="assembly-lessons">
      <div className="lesson-intro"><h3>Build it, one step at a time.</h3><p>Choose a step to see its parts, learn the idea behind it, and check your work. These lessons follow the custom build using the supplied Rev A files.</p></div>
      <div className="lesson-workbench">
        <nav className="lesson-nav" aria-label="Assembly lessons"><ol>{lessons.map((lesson, i) => <li key={lesson.id}><button type="button" aria-current={i === index ? "step" : undefined} aria-controls="assembly-lesson-panel" onClick={() => choose(i)}><span>{String(i + 1).padStart(2, "0")}</span><span>{lesson.title}</span></button></li>)}</ol></nav>
        <label className="lesson-mobile-select">Choose an assembly step<select value={index} onChange={event => choose(Number(event.target.value))}>{lessons.map((lesson, i) => <option key={lesson.id} value={i}>{String(i + 1).padStart(2, "0")} · {lesson.title}</option>)}</select></label>
        <article ref={panel} className="lesson-panel" id="assembly-lesson-panel" aria-labelledby="lesson-title" data-lesson={step.id}>
          <header className="lesson-heading"><p className="lesson-eyebrow">Step {String(index + 1).padStart(2, "0")} / {lessons.length}</p><h3 id="lesson-title">{step.title}</h3><p>{step.summary}</p></header>
          <figure className="lesson-figure">
            {step.visual === "cad" ? <>
              <iframe ref={frame} src="/viewer/index.html?mode=lesson" title={`Assembly lesson: ${step.title}`} className="lesson-viewer" onLoad={() => frame.current?.contentWindow?.postMessage({ type: "micro:lesson", id: step.id }, window.location.origin)} />
              {status !== "ready" && <p className="lesson-model-status" role="status">{status === "unavailable" ? "3D is unavailable in this browser. The instructions and part links below are still available." : "Loading this step’s model…"}</p>}
            </> : <LessonDiagram kind={step.visual} />}
            <figcaption>{step.caption}</figcaption>
          </figure>
          <div className="lesson-body">
            <div className="lesson-part-list"><span>On your bench</span><div>{step.parts.map(id => {
              const part = parts.get(id)!;
              return part.category === "Printed" ? <button key={id} onClick={() => onSelect(id)}>{part.name} <span aria-hidden="true">↓</span></button> : <a key={id} href={part.links[0].url} target="_blank" rel="noopener noreferrer">{part.name} <span aria-hidden="true">↗</span></a>;
            })}</div></div>
            <h4>How to do it</h4><ol className="lesson-actions">{step.how.map(action => <li key={action}>{action}</li>)}</ol>
            <div className="lesson-why"><h4>Why it matters</h4><p>{step.why}</p></div>
            <div className="lesson-check"><h4>Before you move on</h4><p>{step.check}</p></div>
            {step.links.length > 0 && <div className="lesson-resources">{step.links.map(link => <a key={link.url} href={link.url} {...(link.url.startsWith("#") ? {} : { target: "_blank", rel: "noopener noreferrer" })}>{link.label}<span aria-hidden="true"> {link.url.startsWith("#") ? "↓" : "↗"}</span></a>)}</div>}
            <div className="lesson-pagination"><button disabled={index === 0} onClick={() => choose(index - 1)}>← Previous step</button><span aria-live="polite">Step {index + 1} of {lessons.length}</span><button disabled={index === lessons.length - 1} onClick={() => choose(index + 1)}>Next step →</button></div>
          </div>
        </article>
      </div>
    </div>
  );
}

function LessonDiagram({ kind }: { kind: string }) {
  const title = kind === "fit" ? "Test the switch aperture, MX socket and insert fit before printing the body" : kind === "matrix" ? "Thirteen switch positions in a four-row, four-column matrix, with one diode per switch" : "USB powers the KB2040; fused RAW powers the lights, 3V powers the joystick, and all grounds connect";
  return <svg className={`lesson-diagram diagram-${kind}`} viewBox="0 0 600 450" role="img" aria-label={title}>
    <title>{title}</title>
    {kind === "fit" ? <>
      <text x="32" y="38" className="diagram-kicker">01 / SWITCH APERTURE</text>
      <rect x="32" y="59" width="536" height="144" rx="12" className="diagram-surface" />
      {["14.0", "14.1", "14.2"].map((size, i) => <g key={size} transform={`translate(${66 + i * 178},80)`}><rect width="110" height="75" rx="3" className="diagram-cutout" /><text x="55" y="106" textAnchor="middle">{size} mm</text></g>)}
      <text x="300" y="237" textAnchor="middle" className="diagram-note">Choose the aperture that lets the real switch latch.</text>
      <text x="32" y="284" className="diagram-kicker">02 / STEM + INSERT</text>
      <rect x="32" y="306" width="250" height="114" rx="10" className="diagram-surface" />
      <path d="M80 329h18v22h22v18H98v22H80v-22H58v-18h22z" className="diagram-cutout" />
      <text x="141" y="355">MX socket</text><text x="141" y="379" className="diagram-note">Grip, no split.</text>
      <rect x="302" y="306" width="266" height="114" rx="10" className="diagram-surface" />
      <circle cx="353" cy="361" r="28" fill="#c9b27a" stroke="#92743e" strokeWidth="2"/><circle cx="353" cy="361" r="13" className="diagram-cutout" />
      <text x="399" y="355">M3 insert</text><text x="399" y="379" className="diagram-note">Straight, no spin.</text>
    </> : kind === "matrix" ? <>
      <text x="300" y="29" textAnchor="middle" className="diagram-kicker">USB / REAR · VIEW FROM ABOVE</text>
      {["C1 / D6", "C2 / D7", "C3 / D8", "C4 / D9"].map((label, i) => <text key={label} x={156 + i * 114} y="68" textAnchor="middle" className="diagram-note">{label}</text>)}
      {[[null, "01", "02", null], ["03", "04", "05", "06"], ["FAST", "APPROVE", "DECLINE", "NEW CHAT"], [null, "VOICE L", "VOICE R", "SEND"]].map((row, r) => <g key={r}><text x="17" y={110 + r * 55} className="diagram-note">R{r + 1} / D{r + 2}</text>{row.map((key, c) => <g key={c}><rect x={103 + c * 114} y={83 + r * 55} width="105" height="43" rx="6" fill={key ? r < 2 ? "#dde7d7" : "#ffffff" : "#eff1eb"} stroke="#cdd7c3" strokeDasharray={key ? undefined : "3 4"}/><text x={156 + c * 114} y={110 + r * 55} textAnchor="middle" className="diagram-key">{key || ["DIAL", "STICK", "TOUCH"][[[0,0],[0,3],[3,0]].findIndex(([rr,cc]) => r===rr && c===cc)]}</text></g>)}</g>)}
      <text x="32" y="339" className="diagram-kicker">ONE SWITCH CONNECTION · REPEAT × 13</text>
      <text x="32" y="388">Column</text><path d="M103 382h64m0 0 34-17m7 17h73m108 0h116" fill="none" stroke="#6f8963" strokeWidth="3"/><circle cx="167" cy="382" r="4" fill="#6f8963"/><circle cx="208" cy="382" r="4" fill="#6f8963"/>
      <rect x="281" y="370" width="108" height="24" rx="7" fill="#caaa77" stroke="#937247"/><path d="M370 371v22" stroke="#384334" strokeWidth="6"/>
      <text x="514" y="388">Row</text><text x="182" y="425" textAnchor="middle" className="diagram-note">Switch</text><text x="346" y="425" textAnchor="middle" className="diagram-note">Diode band → row</text>
    </> : <>
      <text x="32" y="36" className="diagram-kicker">TEST WITH THE PLATE OPEN</text>
      <rect x="205" y="60" width="190" height="52" rx="8" className="diagram-cutout"/><text x="300" y="92" textAnchor="middle">USB data cable</text>
      <path d="M300 112v39" className="diagram-wire"/><rect x="190" y="151" width="220" height="67" rx="10" fill="#dee7d8" stroke="#93a486"/><text x="300" y="180" textAnchor="middle">KB2040</text><text x="300" y="203" textAnchor="middle" className="diagram-note">Fuse bypass stays OPEN</text>
      <path d="M245 218v30H155v40M355 218v30h90v40" className="diagram-wire"/><text x="151" y="272" textAnchor="middle" className="diagram-note">Fused RAW ≈ 5 V</text><text x="445" y="272" textAnchor="middle" className="diagram-note">3V = 3.3 V</text>
      <rect x="32" y="288" width="246" height="66" rx="9" className="diagram-cutout"/><text x="155" y="315" textAnchor="middle">14 pixels + level shifter</text><text x="155" y="339" textAnchor="middle" className="diagram-note">Keep brightness at 15%</text>
      <rect x="322" y="288" width="246" height="66" rx="9" className="diagram-cutout"/><text x="445" y="315" textAnchor="middle">Slide joystick</text><text x="445" y="339" textAnchor="middle" className="diagram-note">Analog outputs to A0 / A1</text>
      <path d="M155 354v32h290v-32M300 386v13" fill="none" stroke="#7d8576" strokeWidth="2"/><text x="300" y="424" textAnchor="middle">Common ground, including the KB2040</text>
    </>}
  </svg>;
}
