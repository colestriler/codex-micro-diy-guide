"use client";

import { useState } from "react";
import wiring from "@/data/wiring.json";

type Chapter = (typeof wiring.chapters)[number];
type Step = Chapter["steps"][number];
type Point = [number, number];
type Trace = { id: string; paths: string[]; ends?: Point[]; color?: string };
const C = { power: "#c44f38", ground: "#42494c", signal: "#267e79", row: "#ab6832", column: "#5963b8", analog: "#865ba4", low: "#ad731a" };
const KB = { x: 35, y: 185, scale: 420 / 710 };
function pin(id: string): Point {
  const pad = wiring.kbPins.find(p => p.id === id)!;
  return [KB.x + (pad.x - 120) * KB.scale, KB.y + (pad.y - 185) * KB.scale];
}
const xy = (p: Point) => p.join(" ");
const icPin = (n: number): Point => [n <= 7 ? 650 : 800, 175 + (n <= 7 ? n - 1 : 14 - n) * 34];
const joyPin = (n: number): Point => [851.3, 355.6 + (n - 1) * 18.8];

export default function WiringWorkbench() {
  const [chapterIndex, setChapterIndex] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [showAll, setShowAll] = useState(false);
  const [zoom, setZoom] = useState(false);
  const chapter = wiring.chapters[chapterIndex];
  const step = chapter.steps[stepIndex];
  function selectStep(id: string) {
    const index = chapter.steps.findIndex(s => s.id === id);
    if (index >= 0) { setStepIndex(index); setShowAll(false); }
  }
  return <div className="wiring-workbench">
    <p className="section-intro">Follow the wires on the actual component photos. Pick a circuit, then a connection to see exactly where it lands and why it belongs there.</p>
    <div className="wiring-chapters" role="group" aria-label="Wiring circuits">
      {wiring.chapters.map((item, i) => <button key={item.id} aria-pressed={i === chapterIndex} onClick={() => { setChapterIndex(i); setStepIndex(0); setShowAll(false); }}><span>0{i + 1}</span>{item.title}</button>)}
    </div>
    <div className="wiring-workspace">
      <div className="wiring-topline"><div><h3>{chapter.title}</h3><p>{chapter.intro}</p></div><span className="wiring-photo-badge">Photos + pin overlays</span></div>
      <div className="wiring-controls">
        <label><span>{chapter.id === "matrix" ? "Choose a key" : "Follow a connection"}</span><select aria-label="Wiring connection" value={stepIndex} onChange={e => { setStepIndex(Number(e.target.value)); setShowAll(false); }}>{chapter.steps.map((s, i) => <option key={s.id} value={i}>{String(i + 1).padStart(2, "0")} · {s.title}</option>)}</select></label>
        <div className="wiring-actions"><button aria-label="Previous wiring connection" disabled={stepIndex === 0} onClick={() => { setStepIndex(i => i - 1); setShowAll(false); }}>←</button><button aria-label="Next wiring connection" disabled={stepIndex === chapter.steps.length - 1} onClick={() => { setStepIndex(i => i + 1); setShowAll(false); }}>→</button>{chapter.id !== "matrix" && <button aria-pressed={showAll} onClick={() => setShowAll(v => !v)}>All wires</button>}<button aria-pressed={zoom} onClick={() => setZoom(v => !v)}>{zoom ? "Fit view" : "Zoom in"}</button></div>
      </div>
      <p className="wiring-pan-hint">Swipe the diagram sideways to see the full circuit.</p>
      <div className="wiring-canvas-scroll" tabIndex={0} role="region" aria-label="Wiring visual. Scroll to pan when zoomed.">
        <svg className={`wiring-canvas${zoom ? " is-zoomed" : ""}`} viewBox="0 0 1000 580" role="group" aria-labelledby="wiring-visual-title wiring-visual-description">
          <title id="wiring-visual-title">{`${chapter.title}: ${step.title}`}</title><desc id="wiring-visual-description">{`${chapter.orientation} Selected connection: ${step.from_} to ${step.to}. ${step.how}`}</desc>
          <defs><pattern id="wiring-dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#dce0da" /></pattern><linearGradient id="wiring-metal"><stop stopColor="#8e9392"/><stop offset=".45" stopColor="#f0f0e9"/><stop offset="1" stopColor="#969c98"/></linearGradient><linearGradient id="wiring-chip"><stop stopColor="#393d3b"/><stop offset="1" stopColor="#1c211e"/></linearGradient></defs>
          <rect width="1000" height="580" fill="#f5f6f2"/><rect width="1000" height="580" fill="url(#wiring-dots)"/>
          {chapter.id === "matrix" ? <MatrixScene step={step} select={selectStep}/> : chapter.id === "pixels" ? <PixelScene/> : <>
            <Controller active={step.kbPins} />
            {chapter.id === "power" ? <PowerParts active={step.icPins}/> : chapter.id === "controls" ? <ControlParts/> : <ExtraParts/>}
          </>}
          {chapter.id !== "matrix" && <Traces chapter={chapter} selected={step.id} all={showAll} select={selectStep} traces={getTraces(chapter.id)}/>}
          <text x="26" y="559" className="wiring-svg-note">{chapter.id === "matrix" ? "Each key gets its own diode. The 13 switches share 4 row wires and 4 column wires." : "Wire paths are illustrative; measure lengths in your case. Crossings connect only at marked endpoints / junctions."}</text>
        </svg>
      </div>
      <div className="wiring-orientation"><span>↳ {chapter.orientation}</span><span>Scroll to pan · Zoom for solder pads</span></div>
      <div className="wiring-lesson" aria-live="polite" aria-atomic="true">
        <div className="wiring-lesson-heading"><span className="wiring-step-number">{String(stepIndex + 1).padStart(2, "0")} / {String(chapter.steps.length).padStart(2, "0")}</span><h4>{step.title}</h4></div>
        <div className="wiring-endpoints"><b>{step.from_}</b><span aria-hidden="true">→</span><b>{step.to}</b></div>
        <div className="wiring-explanations"><div><h5>How to connect it</h5><p>{step.how}</p></div><div><h5>Why we’re doing it</h5><p>{step.why}</p></div><div><h5>Check your work</h5><p>{step.check}</p></div></div>
      </div>
    </div>
    <p className="wiring-bench-note"><b>At your workbench:</b> unplug USB before soldering or using continuity mode. Tin pads and wire ends, keep joints brief, and insulate bare leads. The pin map is checked against the linked documentation and supplied firmware; this DIY circuit still needs a physical bench test.</p>
    <details className="wiring-reference"><summary>All connections & source references</summary>
      <p>Use the pad names on your KB2040: <b>MO = MOSI</b>, <b>MI = MISO</b>, and <b>CLK = SCK</b>. Pins marked D+ / D−, RST, and the STEMMA QT connector are unused in this build.</p>
      <div className="table-scroll"><table><thead><tr><th>Circuit / connection</th><th>From</th><th>To</th></tr></thead><tbody>{wiring.chapters.flatMap(c => c.steps.map(s => <tr key={`${c.id}-${s.id}`}><th scope="row">{c.short} · {s.title}</th><td>{s.from_}</td><td>{s.to}</td></tr>))}</tbody></table></div>
      <p className="wiring-source-links">Component photos and manufacturer render: <a href="https://www.adafruit.com/product/5302" target="_blank" rel="noreferrer">Adafruit KB2040</a>, <a href="https://www.adafruit.com/product/4776" target="_blank" rel="noreferrer">RGBW mini PCBs</a>, <a href="https://www.adafruit.com/product/377" target="_blank" rel="noreferrer">encoder</a>, <a href="https://www.sparkfun.com/thumb-slide-joystick.html" target="_blank" rel="noreferrer">SparkFun COM-09426</a>, <a href="https://www.gateron.com/products/gateron-new-north-pole-yellow-20-switch-set" target="_blank" rel="noreferrer">Gateron switch</a>. Photos remain the property of their respective makers. IC, resistor, diode, LED and encoder underside drawings are explanatory illustrations.</p>
      <p className="wiring-source-links">Pin references: <a href="https://learn.adafruit.com/adafruit-kb2040/pinouts" target="_blank" rel="noreferrer">KB2040 pinouts</a> · <a href="https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf" target="_blank" rel="noreferrer">TI SN74AHCT125, pages 3–4</a> · <a href="https://cdn-shop.adafruit.com/datasheets/pec11.pdf" target="_blank" rel="noreferrer">PEC11 mechanical drawing</a> · <a href="https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices" target="_blank" rel="noreferrer">NeoPixel wiring practices</a> · <a href="https://docs.circuitpython.org/en/latest/shared-bindings/touchio/" target="_blank" rel="noreferrer">RP2040 touch pulldown</a> · <a href="/downloads/firmware/code.py" download>Matching firmware</a></p>
    </details>
  </div>;
}

function Photo({ file, crop, x, y, width, height }: { file: string; crop: string; x: number; y: number; width: number; height: number }) {
  const [iw, ih] = file === "joystick-bottom.jpg" ? [600, 600] : file === "switch.webp" ? [716, 485] : [970, 728];
  // Nested SVG viewports crop the original, unmodified supplier assets; pad coordinates use the same transform.
  return <svg x={x} y={y} width={width} height={height} viewBox={crop} preserveAspectRatio="none" aria-hidden="true"><image href={`/images/wiring/${file}`} width={iw} height={ih}/></svg>;
}
function Label({ x, y, children, anchor = "start", muted = false }: { x: number; y: number; children: React.ReactNode; anchor?: "start" | "middle" | "end"; muted?: boolean }) {
  return <text x={x} y={y} textAnchor={anchor} className={muted ? "wiring-svg-note" : "wiring-svg-label"}>{children}</text>;
}
function Controller({ active }: { active: string[] }) {
  return <g><Photo file="kb2040.jpg" crop="120 185 710 385" x={KB.x} y={KB.y} width={420} height={385 * KB.scale}/>
    {active.map(id => { const [x, y] = pin(id); const above = y < 300; const lx = x + 25; return <g key={id}><circle cx={x} cy={y} r={9} fill="none" stroke="#fff" strokeWidth={5}/><circle cx={x} cy={y} r={8} fill="none" stroke={C.signal} strokeWidth={2}/><rect x={lx - 19} y={y + (above ? -31 : 16)} width={38} height={20} rx={4} fill="#fff"/><text x={lx} y={y + (above ? -17 : 30)} textAnchor="middle" className="wiring-pad-label">{id}</text></g>; })}
    <Label x={35} y={active.every(id => pin(id)[1] > 300) ? 158 : 444} muted>KB2040 · component side, USB left · rings mark solder pads.</Label>
  </g>;
}
function Resistor({ x, y, value, vertical = false }: { x: number; y: number; value: string; vertical?: boolean }) {
  const bands = value === "330Ω" ? ["#d97932", "#d97932", "#77502f"] : value === "1MΩ" ? ["#77502f", "#282b27", "#477b4c"] : ["#77502f", "#282b27", "#b74839"];
  return <g transform={`translate(${x} ${y})`}><g transform={vertical ? "rotate(90)" : undefined}><path d="M-40 0H40" stroke="#9aa79c" strokeWidth={4}/><rect x={-24} y={-9} width={48} height={18} rx={6} fill="#d6c9a5" stroke="#9b8c68"/>{[-13,-6,1,16].map((b,i)=><path key={b} d={`M${b} -8v16`} stroke={i===3 ? "#ad8935" : bands[i]} strokeWidth={3}/>)}</g><Label x={vertical ? 19 : 0} y={vertical ? 4 : -18} anchor={vertical ? "start" : "middle"}>{value}</Label></g>;
}
function PowerParts({ active }: { active: number[] }) {
  return <g><Label x={674} y={111}>SN74AHCT125N</Label><Label x={674} y={129} muted>DIP-14 · notch at top</Label><rect x={674} y={151} width={102} height={258} rx={7} fill="url(#wiring-chip)"/><path d="M710 151a15 15 0 0 0 30 0" fill="#101613" stroke="#565e58"/><circle cx={686} cy={167} r={4} fill="#a9b0a8"/><text x={723} y={290} textAnchor="middle" style={{ fill: "#a8b0a7" }} fontSize={13} transform="rotate(-90 723 290)">74AHCT125</text>
    {Array.from({length:14},(_,i)=>i+1).map(n=>{ const [x,y]=icPin(n);return <g key={n}><rect x={n<=7?650:776} y={y-5} width={24} height={10} rx={2} fill="url(#wiring-metal)"/><text x={n<=7?685:765} y={y+4} textAnchor={n<=7?"start":"end"} fontSize={12} style={{ fill: "#f2f3ed" }}>{n}</text>{active.includes(n)&&<circle cx={x} cy={y} r={8} fill="none" stroke={C.signal} strokeWidth={3}/>}</g>;})}
    <Label x={944} y={74} anchor="end">+5V rail → LEDs</Label><Label x={944} y={535} anchor="end">GND rail → LEDs</Label>
    <Resistor x={805} y={455} value="330Ω"/><Label x={932} y={443} anchor="end">Pixel 0 DIN</Label>
    <g><path d="M853 247V267M853 301V325" stroke="#9aa79c" strokeWidth={4}/><rect x={840} y={266} width={26} height={37} rx={7} fill="#c99151" stroke="#99682f"/><text x={853} y={289} textAnchor="middle" style={{ fill: "#513622" }} fontSize={10}>104</text><Label x={875} y={281}>100nF</Label><Label x={875} y={301} muted>No polarity</Label></g>
    <g><path d="M942 314V287M912 300V324" stroke="#9aa79c" strokeWidth={4}/><rect x={899} y={324} width={56} height={66} rx={10} fill="#26302d"/><ellipse cx={927} cy={324} rx={28} ry={9} fill="url(#wiring-metal)"/><rect x={903} y={333} width={13} height={48} fill="#c5ccc6"/><text x={909} y={355} textAnchor="middle" style={{ fill: "#333" }} fontSize={18}>−</text><path d="M942 314v12M912 314v10" stroke="#9aa79c" strokeWidth={4}/><Label x={985} y={415} anchor="end">100µF · stripe = −</Label><Label x={949} y={281}>+</Label></g>
    <Label x={652} y={431} muted>6, 8, 11: leave open</Label>
  </g>;
}
function getTraces(id: string): Trace[] {
  const p=(name:string)=>xy(pin(name));
  const ic=(n:number)=>xy(icPin(n));
  if(id === "power") return [
    {id:"ground",paths:[`M${p('G')}V112H515V505H972`,`M${ic(1)}H555V505`,`M${ic(7)}H555`],ends:[pin('G'),icPin(1),icPin(7),[555,379],[555,505],[972,505]]},
    {id:"raw",paths:[`M${p('RAW')}V85H972`,`M890 85V175H800`],ends:[pin('RAW'),icPin(14),[890,85],[972,85]]},
    {id:"shift",paths:[`M${p('MO')}V62H605V209H650`],ends:[pin('MO'),icPin(2)]},
    {id:"output",paths:[`M${ic(3)}H590V455H765`,`M845 455H955`],ends:[icPin(3),[765,455],[845,455],[955,455]]},
    {id:"bypass",paths:[`M${ic(14)}H853V247`,`M853 325V475H555V379H650`],ends:[icPin(14),[853,247],[853,325],[555,475],icPin(7)]},
    {id:"bulk",paths:[`M942 85V287`,`M912 300H878V505`],ends:[[942,85],[942,287],[912,300],[878,505]]},
    {id:"unused",color:C.ground,paths:[`M${ic(5)}H535V505`,`M${ic(9)}H820V505`,`M${ic(12)}H832V475H555`],ends:[icPin(5),icPin(9),icPin(12),[535,505],[820,505],[555,475]]},
    {id:"unused",color:C.power,paths:[`M${ic(4)}H620V42H925V85`,`M${ic(10)}H890V85`,`M${ic(13)}H905V85`],ends:[icPin(4),icPin(10),icPin(13),[925,85],[890,85],[905,85]]},
  ];
  if(id === "controls") return [
    {id:'joy-ground',paths:[`M${p('G')}V92H488V485H930V${joyPin(4)[1]}H${joyPin(4)[0]}`],ends:[pin('G'),joyPin(4)]},
    {id:'joy-power',paths:[`M${p('3V')}V110H950V${joyPin(2)[1]}H${joyPin(2)[0]}`],ends:[pin('3V'),joyPin(2)]},
    {id:'joy-x',paths:[`M${p('A0')}V128H915V${joyPin(1)[1]}H${joyPin(1)[0]}`],ends:[pin('A0'),joyPin(1)]},
    {id:'joy-y',paths:[`M${p('A1')}V76H975V${joyPin(3)[1]}H${joyPin(3)[0]}`],ends:[pin('A1'),joyPin(3)]},
    {id:'encoder-common',paths:[`M${p('G')}V92H488V285H775V256`],ends:[pin('G'),[775,256]]},
    {id:'encoder-a',paths:[`M${p('TX')}V464H720V256`],ends:[pin('TX'),[720,256]]},
    {id:'encoder-b',paths:[`M${p('RX')}V449H830V256`],ends:[pin('RX'),[830,256]]},
    {id:'encoder-push',paths:[`M${p('A2')}V60H744V146`],ends:[pin('A2'),[744,146]]},
    {id:'encoder-push',color:C.ground,paths:[`M${p('G')}V92H805V146`],ends:[pin('G'),[805,146]]}
  ];
  if(id === "extras") return [
    {id:'touch',paths:[`M${p('D10')}V75H815V155`],ends:[pin('D10'),[815,155]]},
    {id:'pulldown',paths:[`M${p('D10')}V75H535V170`,`M535 250V500H490V110H${pin('G')[0]}V${pin('G')[1]}`],ends:[pin('D10'),[535,170],[535,250],pin('G')]},
    ...['CLK','MI','A3'].flatMap<Trace>((name,i)=>[
      {id:`indicator-${i}`,paths:[`M${p(name)}V${52-i*16}H${615+i*145}V275`,`M${615+i*145} 355V385`],ends:[pin(name),[615+i*145,275],[615+i*145,355],[615+i*145,385]]},
      {id:`indicator-${i}`,color:C.ground,paths:[`M${645+i*145} 405V500H490V110H${pin('G')[0]}V${pin('G')[1]}`],ends:[[645+i*145,405],pin('G')]}
    ])
  ];
  return pixelTraces();
}
function Traces({chapter,selected,all,select,traces}:{chapter:Chapter;selected:string;all:boolean;select:(id:string)=>void;traces:Trace[]}) {
  // Paint the focused connection last so its pads and wire remain legible at crossings.
  return <g>{[...traces].sort((a,b)=>Number(a.id===selected)-Number(b.id===selected)).map((trace,i)=>{
    const step=chapter.steps.find(s=>s.id===trace.id)!;
    const active=trace.id===selected;
    const color=trace.color||step.color;
    return <g key={`${trace.id}-${i}`} className={`wiring-trace${active?" is-active":""}`} role="button" tabIndex={0} aria-label={`Trace ${step.title}${trace.color ? ` · ${trace.color === C.ground ? "ground" : "power"}` : ""}`} aria-pressed={active} onClick={()=>select(trace.id)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(trace.id);}}} style={{opacity:all||active?1:.1}}>
      {trace.paths.map((d,j)=><g key={j}><path d={d} fill="none" stroke="#f5f6f2" strokeWidth={8} strokeLinejoin="round"/><path className="wire-colored" d={d} fill="none" stroke={color} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round"/><path d={d} fill="none" stroke="transparent" strokeWidth={16}/></g>)}
      {trace.ends?.map(([x,y],j)=><g key={j}><circle cx={x} cy={y} r={5} fill={color} stroke="#fff" strokeWidth={1.5}/>{active&&<circle className="wiring-focus-ring" cx={x} cy={y} r={9} fill="none" stroke={color} strokeWidth={1.5}/>}</g>)}
    </g>;
  })}</g>;
}
function ControlParts() {
  return <g><Label x={530} y={116}>Adafruit 377</Label><Photo file="encoder.jpg" crop="675 175 212 420" x={535} y={135} width={114} height={226}/><Label x={535} y={384} muted>Reference photo</Label>
    <rect x={698} y={160} width={152} height={78} rx={12} fill="#344838" stroke="#778273" strokeWidth={3}/><circle cx={775} cy={199} r={25} fill="#747d6c"/><rect x={686} y={188} width={12} height={26} fill="url(#wiring-metal)"/><rect x={850} y={188} width={12} height={26} fill="url(#wiring-metal)"/>
    {[720,775,830].map(x=><path key={x} d={`M${x} 236v20`} stroke="#9aa79c" strokeWidth={10}/>)}{[744,805].map(x=><path key={x} d={`M${x} 146v14`} stroke="#9aa79c" strokeWidth={10}/>)}
    <Label x={775} y={116} anchor="middle">Encoder underside</Label><Label x={775} y={136} anchor="middle" muted>Two push-switch contacts</Label><Label x={720} y={278} anchor="middle">TX</Label><Label x={775} y={278} anchor="middle">G</Label><Label x={830} y={278} anchor="middle">RX</Label>
    <Photo file="joystick-bottom.jpg" crop="160 78 375 328" x={660} y={291} width={225} height={196.8}/>
    {[1,2,3,4].map(n=><Label key={n} x={860} y={joyPin(n)[1]+4}>{n} · {['X','VCC','Y','GND'][n-1]}</Label>)}
    <Label x={660} y={515}>COM-09426 · actual underside</Label><Label x={660} y={535} muted>Pad 4 is nearest this pair of mounting tabs.</Label>
  </g>;
}
function ExtraParts() {
  return <g><circle cx={815} cy={160} r={63} fill="#ba8052" stroke="#986645" strokeWidth={2}/><circle cx={815} cy={160} r={54} fill="none" stroke="#ca966c"/><Label x={815} y={163} anchor="middle">Copper foil</Label><Label x={815} y={242} anchor="middle" muted>Inside the touch cap</Label><Resistor x={535} y={210} value="1MΩ" vertical/>
    {[0,1,2].map(i=><g key={i}><Resistor x={615+i*145} y={315} value="1kΩ" vertical/><path d={`M${615+i*145} 385v52M${645+i*145} 405v32`} stroke="#9aa79c" strokeWidth={5}/><path d={`M${606+i*145} 456v-30a24 24 0 0 1 48 0v30z`} fill="#dfe7dc" stroke="#889d89" strokeWidth={2}/><rect x={603+i*145} y={453} width={54} height={9} rx={2} fill="#c6d1c2" stroke="#889d89"/><Label x={601+i*145} y={390} anchor="end">+</Label><Label x={660+i*145} y={411}>−</Label><Label x={630+i*145} y={487} anchor="middle">Bank {i+1}</Label></g>)}
    <Label x={615} y={531} muted>Long lead: anode (+). Short lead / flat rim: cathode (−).</Label>
  </g>;
}
function MatrixScene({step,select}:{step:Step;select:(id:string)=>void}) {
  const key=wiring.matrix.keys.find(k=>k.id===step.id)!;
  const col=wiring.matrix.columns[key.column],row=wiring.matrix.rows[key.row];
  const cp=pin(col),rp=pin(row);
  return <g><Controller active={[col,row]}/><Label x={510} y={45}>Choose the key you’re wiring</Label><Label x={970} y={45} anchor="end" muted>TOP VIEW · USB ↑</Label>
    {Array.from({length:4},(_,r)=>Array.from({length:4},(_,c)=>{const k=wiring.matrix.keys.find(k=>k.row===r&&k.column===c); const x=510+c*115,y=61+r*44; const content=<><rect x={x} y={y} width={107} height={36} rx={5} fill={k?.id===step.id?C.column:'#fff'} stroke={k?.id===step.id?C.column:'#dce1d8'}/><text x={x+53.5} y={y+23} textAnchor="middle" fontSize={12} style={{fill:k?.id===step.id?'#fff':'#596257'}}>{k?.label||(['Dial','','','Joystick'][c]&&r===0?['Dial','','','Joystick'][c]:'Touch')}</text></>;
      return k?<g key={k.id} role="button" tabIndex={0} className="wiring-key" aria-label={`Wire ${k.label}`} aria-pressed={k.id===step.id} onClick={()=>select(k.id)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(k.id);}}}>{content}</g>:<g key={`${r}-${c}`} opacity={.45}>{content}</g>;
    }))}
    <Photo file="switch.webp" crop="300 40 365 390" x={530} y={265} width={237} height={253.2}/><Label x={530} y={251}>Two metal switch legs</Label>
    <path d={`M${xy(cp)}V${475+key.column*12}H606V506`} className="wire-colored" fill="none" stroke={C.column} strokeWidth={4} strokeLinejoin="round"/>
    <path d="M691 503V518H799" fill="none" stroke={C.signal} strokeWidth={4}/><path d={`M867 518H973V242H480V${435+key.row*9}H${rp[0]}V${rp[1]}`} fill="none" stroke={C.row} strokeWidth={4} strokeLinejoin="round"/>
    <path d="M799 518H867" stroke="#9aa79c" strokeWidth={4}/><rect x={815} y={510} width={38} height={16} rx={5} fill="#bc704b" stroke="#864b32"/><path d="M846 510v16" stroke="#302b2b" strokeWidth={5}/><Label x={833} y={477} anchor="middle">1N4148 diode</Label><Label x={876} y={501}>Band → row</Label>
    {[cp,rp,[606,506],[691,503]].map(([x,y],i)=><circle key={i} cx={x} cy={y} r={6} fill={i%2?C.row:C.column} stroke="#fff" strokeWidth={2}/>)}
    <rect x={784} y={304} width={185} height={129} rx={8} fill="#fff" stroke="#e0e5dc"/><Label x={800} y={329}>{step.title}</Label><text x={800} y={356} style={{fill:C.column}} fontSize={14}>Column {key.column+1} · {col}</text><text x={800} y={381} style={{fill:C.row}} fontSize={14}>Row {key.row+1} · {row}</text><Label x={800} y={410} muted>No ground connection.</Label>
  </g>;
}
const pixelPosition=(n:number):Point=>[100+n%7*128,n<7?185:365];
const pp=(n:number,contact:'in'|'out'|'plus'|'minus'|'plusOut'|'minusOut'):Point=>{
  const [x,y]=pixelPosition(n); const dx={in:44,out:44,plus:61,minus:27,plusOut:61,minusOut:27}[contact];return [x+dx,y+(['out','plusOut','minusOut'].includes(contact)?59:25)];
};
function PixelScene() {
  return <g><Label x={35} y={43}>14 boards · 6 agent keys + 8 perimeter lights</Label><Label x={35} y={67} muted>Each board below repeats the same actual back-side photo, with the same orientation.</Label>
    {Array.from({length:wiring.pixelCount},(_,n)=>{const [x,y]=pixelPosition(n);return <g key={n}><Photo file="pixels.jpg" crop="107 257 108 108" x={x} y={y} width={86.4} height={86.4}/><Label x={x+43} y={n<7?y-17:y-27} anchor="middle">{n<6?`Agent 0${n+1}`:`Edge ${n-5}`}</Label><Label x={x+43} y={y+108} anchor="middle" muted>Pixel {n}</Label></g>;})}
    <Label x={30} y={108}>+5V</Label><Label x={30} y={139}>GND</Label><Label x={26} y={237}>From</Label><Label x={26} y={257}>330Ω</Label>
    <Label x={143} y={319} anchor="middle" muted>Left: GND · Middle: data · Right: 5V</Label><Label x={675} y={526} muted>Final DOUT is left open.</Label>
  </g>;
}
function pixelTraces():Trace[] {
  const dataPaths=Array.from({length:13},(_,n)=>{
    const a=pp(n,'out'),b=pp(n+1,'in');
    if(n===6)return `M${xy(a)}V329H80V343H${b[0]}V${b[1]}`;
    return `M${xy(a)}V${a[1]+20}H${a[0]+69}V${b[1]-17}H${b[0]}V${b[1]}`;
  });
  return [
    {id:'pixel-power',color:C.power,paths:['M80 105H981',...Array.from({length:14},(_,n)=>`M${xy(pp(n,'plus'))}V${n<7?105:345}${n<7?'':`H${pp(n,'plus')[0]+43}V105`}`)],ends:Array.from({length:14},(_,n)=>pp(n,'plus'))},
    {id:'pixel-power',color:C.ground,paths:['M80 137H981',...Array.from({length:14},(_,n)=>`M${xy(pp(n,'minus'))}V${n<7?137:337}${n<7?'':`H${pp(n,'minus')[0]-16}V137`}`)],ends:Array.from({length:14},(_,n)=>pp(n,'minus'))},
    {id:'pixel-first',paths:[`M35 250H86V162H${pp(0,'in')[0]}V${pp(0,'in')[1]}`],ends:[[35,250],pp(0,'in')]},
    {id:'pixel-chain',paths:dataPaths,ends:Array.from({length:13},(_,n)=>[pp(n,'out'),pp(n+1,'in')]).flat()},
    {id:'pixel-end',paths:[`M${xy(pp(12,'out'))}V444H941V373H${pp(13,'in')[0]}V${pp(13,'in')[1]}`],ends:[pp(12,'out'),pp(13,'in'),pp(13,'out')]},
  ];
}
