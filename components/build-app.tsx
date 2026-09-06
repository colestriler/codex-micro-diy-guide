"use client";

import { useEffect, useRef, useState } from "react";
import catalog from "@/data/parts.json";
import instructions from "@/data/instructions.json";
import files from "@/data/files.json";
import PartsTable from "@/components/parts-table";
import TableOfContents from "@/components/table-of-contents";

type Part = (typeof catalog)[number];
const categories = ["All parts", "Printed", "Electronics", "Hardware", "Materials", "Native"];
const byId = new Map(catalog.map(part => [part.id, part]));

export default function BuildApp() {
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

  const shown = category === "All parts" ? catalog : catalog.filter(p => p.category === category);

  return (
    <main id="top">
      <header className="site-header">
        <a className="wordmark" href="#top">micro<span> / build guide</span></a>
        <div className="header-links"><a href="https://github.com/colestriler/codex-micro-guide" target="_blank" rel="noreferrer">GitHub ↗</a><a href="/downloads/build-files.zip" download>Download files ↓</a></div>
      </header>

      <div className="guide-layout">
      <TableOfContents />
      <div className="guide-content">
      <section className="intro">
        <div><h1>A small keypad. Every part explained.</h1><p>Explore the model, watch the assembly, and build your own.</p></div>
        <span className="revision">DIY prototype · Rev A</span>
      </section>

      <section id="before-you-start" className="build-section" aria-labelledby="heading-start">
        <SectionHeading number="01" id="heading-start" title="Before you start" />
        <p className="section-intro">Choose your electronics route before ordering or printing. This is a DIY prototype; full native Codex behavior requires genuine compatible electronics.</p>
        <Instruction content={instructions.route} />
      </section>

      <section id="parts" className="build-section" aria-labelledby="heading-parts">
          <SectionHeading number="02" id="heading-parts" title="Parts checklist" />
          <div className="section-toolbar"><p>Check off what you have. Click a part name for details.</p><label className="filter-label"><span className="sr-only">Filter parts</span><select aria-label="Filter parts" value={category} onChange={e => setCategory(e.target.value)}>{categories.map(c => <option key={c}>{c}</option>)}</select></label></div>
          <PartsTable parts={shown} onSelect={selectPart} />
          <p className="section-footnote">Choose either custom electronics or a genuine donor route. Supplier availability and prices can change. Generic hardware links require selecting the stated dimensions.</p>
      </section>

      <section id="printing" className="build-section" aria-labelledby="heading-printing">
          <SectionHeading number="03" id="heading-printing" title="3D printing" />
          <div className="section-toolbar"><p>Clear PETG for the light, white for the controls, black to block light spill.</p></div>
          <div className="material-row">{["petg-clear", "petg-white", "petg-black"].map(id => { const material = byId.get(id)!; return <button key={id} className="material" onClick={() => selectPart(material)}><span className={`filament-swatch swatch-${id}`} aria-hidden="true"/><b>{material.name}</b><span>{material.quantity}</span><small>Details & purchase ↗</small></button>; })}</div>
          <div className="print-summary"><h3>Does it need to be see-through?</h3><p>Yes, the shell and six agent caps need to transmit light. Colorless, frosted PETG works well; optical clarity is not required. Opaque filament will block the status lights.</p><p>Start with a 0.4 mm nozzle and 0.20 mm layers. Use finer layers for keycaps, four walls, and the filament maker’s temperature profile. Confirm your printer’s filament diameter before ordering.</p></div>
          <Instruction content={instructions.plastic} />
      </section>

      <section id="assembly" className="build-section" aria-labelledby="heading-assembly">
          <SectionHeading number="04" id="heading-assembly" title="Assembly" />
          <div className="section-toolbar"><p>Watch the pieces come together, then follow the steps below.</p><a href="/downloads/docs/wiring.svg" target="_blank" rel="noreferrer">Open wiring diagram ↗</a></div>
          <div className="model-section" aria-label="Interactive assembly model">
            <div className="model-caption"><span>Click a part for print files or buying links.</span><span className="model-status">{viewerStatus === "ready" ? "3D model ready" : viewerStatus === "unavailable" ? "Use the parts checklist" : "Loading 3D model…"}</span></div>
            <iframe ref={frame} src="/viewer/index.html" title="Interactive Micro assembly — click parts to inspect them" className="assembly-viewer" onLoad={() => frame.current?.contentWindow?.postMessage({ type: "micro:ping" }, window.location.origin)} />
          </div>
          <Instruction content={instructions.assembly} />
      </section>

      <section id="software" className="build-section" aria-labelledby="heading-software">
          <SectionHeading number="05" id="heading-software" title="Firmware & colors" />
          <Instruction content={instructions.software} />
      </section>

      <section id="checks" className="build-section" aria-labelledby="heading-checks">
          <SectionHeading number="06" id="heading-checks" title="Final checks" />
          <Instruction content={instructions.checks} />
      </section>

      <section id="files" className="build-section" aria-labelledby="heading-files">
          <SectionHeading number="07" id="heading-files" title="Downloads" />
          <div className="section-toolbar"><p>STLs are oriented for printing. STEP files retain assembly coordinates. Units are millimeters.</p><a href="/downloads/build-files.zip" download>Download everything ↓</a></div>
          <div className="file-shortcuts"><a href="/downloads/step/assembly.step" download>Assembly STEP</a><a href="/downloads/cad/parameters.json" download>CAD parameters</a><a href="/downloads/cad/build.py" download>CAD source</a><a href="/downloads/docs/key-legends.svg" download>Key legends</a><a href="/downloads/docs/bom.csv" download>Shopping list CSV</a><a href="/downloads/build-guide.html" download>Offline guide</a></div>
          <div className="table-scroll"><table className="files-table"><thead><tr><th>Printed part</th><th>Quantity</th><th>Files</th></tr></thead><tbody>{files.map(file => <tr key={file.id}><td><b>{file.name.replace(/^\d+ /, "").replaceAll("_", " ")}</b><small>{file.note}</small></td><td>{file.quantity}</td><td><a href={`/downloads/stl/${file.id}.stl`} download>STL</a><a href={`/downloads/step/${file.id}.step`} download>STEP</a></td></tr>)}</tbody></table></div>
          <h3 className="download-subheading">Firmware, wiring and validation files</h3><div className="file-shortcuts"><a href="/downloads/firmware/boot.py" download>boot.py</a><a href="/downloads/firmware/code.py" download>code.py</a><a href="/downloads/firmware/logic.py" download>logic.py</a><a href="/downloads/tools/set_light.py" download>Manual LED helper</a><a href="/downloads/docs/wiring.svg" download>Wiring SVG</a><a href="/downloads/docs/validation.json" download>CAD validation</a><a href="/downloads/docs/oem-measurements.csv" download>Donor measurement sheet</a></div>
      </section>

      <footer><span>Independent DIY reconstruction. Physical fit and electronics remain untested.</span><a href="https://openai.com/supply/co-lab/work-louder/" target="_blank" rel="noreferrer">Original reference ↗</a></footer>
      </div>
      </div>

      <dialog ref={dialog} className="part-dialog" aria-labelledby="part-title" onCancel={() => setPart(null)} onClose={() => setPart(null)} onClick={event => { if (event.target === event.currentTarget) setPart(null); }}>
        {part && <article onClick={event => event.stopPropagation()}>
          <div className="dialog-top"><span>{part.category === "Printed" ? "3D-printed part" : part.category} · {part.quantity}</span><button className="close-dialog" aria-label="Close part details" onClick={() => setPart(null)}>×</button></div>
          <h2 id="part-title">{part.name}</h2>
          <p className="part-description">{part.description}</p>
          {part.category === "Printed" && <div className="print-file-links">{part.files.map(file => <a key={file.url} href={file.url} download>{file.label === "STL" ? "Download STL to print" : "Download editable STEP"}<span aria-hidden="true">↓</span></a>)}</div>}
          <div className="part-spec"><h3>{part.category === "Printed" ? "Print specification" : "What you need"}</h3><p>{part.spec}</p></div>
          {part.note && <p className="part-note">{part.note}</p>}
          {part.category !== "Printed" && <div className="buy-links">{part.links.map(link => <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer">{link.label}<span aria-hidden="true">↗</span></a>)}</div>}
        </article>}
      </dialog>
    </main>
  );
}

function SectionHeading({ number, id, title }: { number: string; id: string; title: string }) {
  return <div className="section-heading"><span aria-hidden="true">{number}</span><h2 id={id}>{title}</h2></div>;
}

function Instruction({ content }: { content: string }) {
  // Trusted, checked-in content extracted from this project's original build guide.
  return <div className="instruction-body" dangerouslySetInnerHTML={{ __html: content }} />;
}
