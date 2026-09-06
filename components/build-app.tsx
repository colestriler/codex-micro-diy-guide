"use client";

import { useEffect, useRef, useState } from "react";
import catalog from "@/data/parts.json";
import instructions from "@/data/instructions.json";
import files from "@/data/files.json";

type Part = (typeof catalog)[number];
type Tab = "Parts" | "Assembly" | "Printing" | "Files";
const tabs: Tab[] = ["Parts", "Assembly", "Printing", "Files"];
const categories = ["All parts", "Printed", "Electronics", "Hardware", "Materials", "Native"];
const byId = new Map(catalog.map(part => [part.id, part]));

export default function BuildApp() {
  const [tab, setTab] = useState<Tab>("Parts");
  const [category, setCategory] = useState("All parts");
  const [part, setPart] = useState<Part | null>(null);
  const [viewerStatus, setViewerStatus] = useState("loading");
  const frame = useRef<HTMLIFrameElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return;
      if (event.data?.type === "micro:ready") setViewerStatus("ready");
      if (event.data?.type === "micro:error") setViewerStatus("unavailable");
      if (event.data?.type !== "micro:select" || typeof event.data.partId !== "string") return;
      const selected = byId.get(event.data.partId);
      if (selected) setPart(selected);
    };
    window.addEventListener("message", receive);
    frame.current?.contentWindow?.postMessage({ type: "micro:ping" }, window.location.origin);
    return () => window.removeEventListener("message", receive);
  }, []);

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (part && !element.open) element.showModal();
    if (!part && element.open) element.close();
  }, [part]);

  function selectPart(selected: Part) {
    setPart(selected);
    frame.current?.contentWindow?.postMessage({ type: "micro:highlight", partId: selected.id }, window.location.origin);
  }

  function changeTab(next: Tab) { setTab(next); }
  const shown = category === "All parts" ? catalog : catalog.filter(p => p.category === category);

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top">micro<span> / build guide</span></a>
        <div className="header-links"><a href="https://github.com/colestriler/codex-micro-guide" target="_blank" rel="noreferrer">GitHub ↗</a><a href="/downloads/build-files.zip" download>Download files ↓</a></div>
      </header>

      <section className="intro" id="top">
        <div><h1>A small keypad. Every part explained.</h1><p>Explore the model, watch the assembly, and build your own.</p></div>
        <span className="revision">DIY prototype · Rev A</span>
      </section>

      <section className="model-section" aria-label="Interactive assembly model">
        <div className="model-caption"><span>Click a part for details and buying links.</span><span className="model-status">{viewerStatus === "ready" ? "3D model ready" : viewerStatus === "unavailable" ? "Use the parts list below" : "Loading 3D model…"}</span></div>
        <iframe ref={frame} src="/viewer/index.html" title="Interactive Micro assembly — click parts to inspect them" className="assembly-viewer" onLoad={() => frame.current?.contentWindow?.postMessage({ type: "micro:ping" }, window.location.origin)} />
      </section>

      <p className="prototype-note">This is a custom hardware prototype. Full native Codex behavior requires genuine compatible electronics. <button onClick={() => { changeTab("Assembly"); document.getElementById("guide")?.scrollIntoView({ behavior: "smooth" }); }}>Read the compatibility notes ↗</button></p>

      <section id="guide" className="guide-section">
        <div className="tabs" role="tablist" aria-label="Build guide sections">
          {tabs.map((item, index) => <button key={item} role="tab" id={`tab-${item}`} aria-controls={`panel-${item}`} aria-selected={tab === item} tabIndex={tab === item ? 0 : -1} onClick={() => changeTab(item)} onKeyDown={event => {
            let target = index;
            if (event.key === "ArrowRight") target = (index + 1) % tabs.length;
            else if (event.key === "ArrowLeft") target = (index + tabs.length - 1) % tabs.length;
            else if (event.key === "Home") target = 0;
            else if (event.key === "End") target = tabs.length - 1;
            else return;
            event.preventDefault(); changeTab(tabs[target]); document.getElementById(`tab-${tabs[target]}`)?.focus();
          }}>{item}</button>)}
        </div>

        <div role="tabpanel" id="panel-Parts" aria-labelledby="tab-Parts" hidden={tab !== "Parts"}>
          <div className="section-toolbar"><p>Select any item to see what it does, what to order, and where to get it.</p><label className="filter-label"><span className="sr-only">Filter parts</span><select aria-label="Filter parts" value={category} onChange={e => setCategory(e.target.value)}>{categories.map(c => <option key={c}>{c}</option>)}</select></label></div>
          <div className="parts-grid">{shown.map(item => <button className="part-row" key={item.id} onClick={() => selectPart(item)}><span className={`part-mark mark-${item.category.toLowerCase()}`} aria-hidden="true"/><span className="part-name">{item.name}<small>{item.category} · {item.quantity}</small></span><span className="row-arrow" aria-hidden="true">↗</span></button>)}</div>
          <p className="section-footnote">Choose either custom electronics or a genuine donor route. Supplier availability and prices can change. Generic hardware links require selecting the stated dimensions.</p>
        </div>

        <div role="tabpanel" id="panel-Assembly" aria-labelledby="tab-Assembly" hidden={tab !== "Assembly"}>
          <div className="section-toolbar"><p>Start with the fit coupons. Test the electronics before closing the case.</p><a href="/downloads/docs/wiring.svg" target="_blank" rel="noreferrer">Open wiring diagram ↗</a></div>
          <Instruction title="Read first: native Codex compatibility" content={instructions.route} />
          <Instruction title="Assemble and wire the hardware" content={instructions.assembly} />
          <Instruction title="Install firmware and understand the colors" content={instructions.software} />
          <Instruction title="Checks before the first full build" content={instructions.checks} />
        </div>

        <div role="tabpanel" id="panel-Printing" aria-labelledby="tab-Printing" hidden={tab !== "Printing"}>
          <div className="section-toolbar"><p>Clear PETG for the light, white for the controls, black to block light spill.</p></div>
          <div className="material-row">{["petg-clear", "petg-white", "petg-black"].map(id => { const material = byId.get(id)!; return <button key={id} className="material" onClick={() => selectPart(material)}><span className={`filament-swatch swatch-${id}`} aria-hidden="true"/><b>{material.name}</b><span>{material.quantity}</span><small>Details & purchase ↗</small></button>; })}</div>
          <div className="print-summary"><h2>Does it need to be see-through?</h2><p>Yes, the shell and six agent caps need to transmit light. Colorless, frosted PETG works well; optical clarity is not required. Opaque filament will block the status lights.</p><p>Start with a 0.4 mm nozzle and 0.20 mm layers. Use finer layers for keycaps, four walls, and the filament maker’s temperature profile. Confirm your printer’s filament diameter before ordering.</p></div>
          <Instruction title="Full material choices and print settings" content={instructions.plastic} />
        </div>

        <div role="tabpanel" id="panel-Files" aria-labelledby="tab-Files" hidden={tab !== "Files"}>
          <div className="section-toolbar"><p>STLs are oriented for printing. STEP files retain assembly coordinates. Units are millimeters.</p><a href="/downloads/build-files.zip" download>Download everything ↓</a></div>
          <div className="file-shortcuts"><a href="/downloads/step/assembly.step" download>Assembly STEP</a><a href="/downloads/cad/parameters.json" download>CAD parameters</a><a href="/downloads/cad/build.py" download>CAD source</a><a href="/downloads/docs/key-legends.svg" download>Key legends</a><a href="/downloads/docs/bom.csv" download>Shopping list CSV</a><a href="/downloads/build-guide.html" download>Offline guide</a></div>
          <div className="table-scroll"><table className="files-table"><thead><tr><th>Printed part</th><th>Quantity</th><th>Files</th></tr></thead><tbody>{files.map(file => <tr key={file.id}><td><b>{file.name.replace(/^\d+ /, "").replaceAll("_", " ")}</b><small>{file.note}</small></td><td>{file.quantity}</td><td><a href={`/downloads/stl/${file.id}.stl`} download>STL</a><a href={`/downloads/step/${file.id}.step`} download>STEP</a></td></tr>)}</tbody></table></div>
          <details className="instruction"><summary>Firmware, wiring and validation files</summary><div className="file-shortcuts"><a href="/downloads/firmware/boot.py" download>boot.py</a><a href="/downloads/firmware/code.py" download>code.py</a><a href="/downloads/firmware/logic.py" download>logic.py</a><a href="/downloads/tools/set_light.py" download>Manual LED helper</a><a href="/downloads/docs/wiring.svg" download>Wiring SVG</a><a href="/downloads/docs/validation.json" download>CAD validation</a><a href="/downloads/docs/oem-measurements.csv" download>Donor measurement sheet</a></div></details>
        </div>
      </section>

      <footer><span>Independent DIY reconstruction. Physical fit and electronics remain untested.</span><a href="https://openai.com/supply/co-lab/work-louder/" target="_blank" rel="noreferrer">Original reference ↗</a></footer>

      <dialog ref={dialog} className="part-dialog" aria-labelledby="part-title" onCancel={() => setPart(null)} onClose={() => setPart(null)} onClick={event => { if (event.target === event.currentTarget) setPart(null); }}>
        {part && <article onClick={event => event.stopPropagation()}><div className="dialog-top"><span>{part.category} · {part.quantity}</span><button className="close-dialog" aria-label="Close part details" onClick={() => setPart(null)}>×</button></div><h2 id="part-title">{part.name}</h2><p className="part-description">{part.description}</p><div className="part-spec"><h3>What you need</h3><p>{part.spec}</p></div>{part.note && <p className="part-note">{part.note}</p>}<div className="buy-links">{part.links.map(link => <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer">{link.label}<span aria-hidden="true">↗</span></a>)}</div>{part.files.length > 0 && <div className="part-downloads"><span>Print files</span>{part.files.map(file => <a key={file.url} href={file.url} download>{file.label} ↓</a>)}</div>}</article>}
      </dialog>
    </main>
  );
}

function Instruction({ title, content }: { title: string; content: string }) {
  // Trusted, checked-in content extracted from this project's original build guide.
  return <details className="instruction"><summary>{title}</summary><div className="instruction-body" dangerouslySetInnerHTML={{ __html: content }} /></details>;
}
