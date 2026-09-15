import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root = new URL('../',import.meta.url);
const read = p => readFile(new URL(p,root),'utf8');
const phases=JSON.parse(await read('data/wiring-lessons.json'));
const steps=phases.flatMap(p=>p.groups.flatMap(g=>g.steps));
assert.equal(new Set(steps.map(s=>s.id)).size,steps.length,'Duplicate checkpoint IDs');
assert.deepEqual(phases.map(p=>p.id),['wiring-start','wiring-knob-button','wiring-knob-turn','wiring-perfboard','wiring-led-test']);
for(const step of steps){
  assert(step.title && step.why && step.check && step.how.length>=2,`Incomplete step ${step.id}`);
  for(const link of step.links){
    if(link.url.startsWith('/'))await access(new URL('public'+link.url,root));
    else assert.equal(new URL(link.url).protocol,'https:');
  }
}
const map=JSON.parse(await read('public/downloads/wiring-guide/connections.json'));
const wireIds=new Set(map.wires.map(w=>w.id));
for(const step of steps)if(step.trace)assert(wireIds.has(step.trace),`Unknown diagram trace ${step.trace}`);
const graph=new Map();
function edge(a,b){if(!graph.has(a))graph.set(a,new Set());if(!graph.has(b))graph.set(b,new Set());graph.get(a).add(b);graph.get(b).add(a);}
map.bridges.forEach(([a,b])=>edge(a,b));map.wires.forEach(w=>edge(w.a,w.b));
function connected(a,b){const pending=[a],seen=new Set(pending);while(pending.length){const x=pending.pop();if(x===b)return true;for(const y of graph.get(x)||[])if(!seen.has(y)){seen.add(y);pending.push(y);}}return false;}
// Electrical checks intentionally exclude conduction THROUGH the resistor and capacitor.
// A wire bypassing either component would be a meaningful failure.
for(const [hole,pin,net] of map.pins){
  if(net==='ground')assert(connected(hole,'KB.G'),`Ground missing at pin ${pin}`);
  if(net==='power')assert(connected(hole,'KB.RAW'),`Power missing at pin ${pin}`);
  if(net==='unused')assert(!graph.has(hole),`Unused output pin ${pin} must be open`);
}
assert(!connected('KB.RAW','KB.G'),'5V-to-ground short');
assert(connected('KB.MO','D9'),'Input must reach chip pin 2');
assert(connected('D8','B8') && connected('B12','LED.DIN'),'Data must pass through resistor endpoints');
assert(!connected('B8','B12'),'Resistor bypassed');
assert(connected('D11','KB.G') && connected('G11','KB.RAW'),'Capacitor across wrong nets');
assert(connected('LED.5V','KB.RAW') && connected('LED.GND','KB.G'));
assert(connected('KNOB.G','KB.G'),'Moved knob ground disconnected');
const pdf=await readFile(new URL('public/downloads/wiring-guide/Codex-Micro-LED-Wiring-Guide.pdf',root));
assert.equal(pdf.subarray(0,5).toString(),'%PDF-');
const led=await read('public/downloads/wiring-guide/firmware/led-test.py');
assert.match(led,/NeoPixel\(board.MOSI, 1, bpp=4/);assert.match(led,/brightness=0.08/);assert.match(led,/pixel_order=neopixel.GRBW/);
for(const name of ['button-test.py','knob-test.py','led-test.py','reasoning-knob.py']){
 const code=await read('public/downloads/wiring-guide/firmware/'+name);
 assert.match(code,/board.A2/);assert.doesNotMatch(code,/KeyMatrix|AnalogIn|TouchIn/);
 if(name!=='button-test.py')assert.match(code,/IncrementalEncoder\(board.TX, board.RX/);
}
const sources=JSON.parse(await read('public/downloads/wiring-guide/library-sources.json'));
for(const file of sources){const bytes=await readFile(new URL('public/downloads/wiring-guide/'+file.path,root));assert.equal(createHash('sha256').update(bytes).digest('hex'),file.sha256);}
console.log(`Bench lessons checked: ${phases.length} phases, ${steps.length} checkpoints; perfboard connectivity, staged firmware pins, PDF and library hashes.`);
