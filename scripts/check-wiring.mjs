import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
const read = path => readFile(new URL('../' + path, import.meta.url), 'utf8');
const [data, firmware, logic] = await Promise.all([read('data/wiring.json'), read('public/downloads/firmware/code.py'), read('public/downloads/firmware/logic.py')]);
const wiring = JSON.parse(data);
const boardPins = text => [...text.matchAll(/board\.(\w+)/g)].map(match => match[1]);
const assignment = name => boardPins(firmware.match(new RegExp(name + '=\\(([^)]+)\\)'))[1]);
assert.deepEqual(wiring.matrix.rows, assignment('row_pins'), 'Visual rows must match the firmware');
assert.deepEqual(wiring.matrix.columns, assignment('column_pins'), 'Visual columns must match the firmware');
assert.match(firmware, /columns_to_anodes=True/, 'The visual diode orientation requires columns_to_anodes');
const physical = [...logic.match(/PHYSICAL_TO_LOGICAL\s*=\s*\{([^}]+)\}/)[1].matchAll(/(\d+)\s*:\s*(\d+)/g)].map(m => [Number(m[1]), Number(m[2])]);
assert.deepEqual(wiring.matrix.keys.map(k => k.row * 4 + k.column), physical.map(([p]) => p), 'Every physical key, including both Voice switches, must match firmware positions');
assert.equal(new Set(physical.map(([p]) => p)).size, 13);
assert.equal(new Set(physical.map(([,l]) => l)).size, 12);
const steps = wiring.chapters.flatMap(c => c.steps);
const step = id => steps.find(s => s.id === id);
const aliases = { MO: 'MOSI', MI: 'MISO', CLK: 'SCK' };
for (const [id, expression] of [
  ['shift', /pixels=neopixel.NeoPixel\((board\.\w+)/],
  ['joy-x', /joy_x=analogio.AnalogIn\((board\.\w+)/],
  ['joy-y', /joy_y=analogio.AnalogIn\((board\.\w+)/],
  ['encoder-push', /encoder_button=keypad.Keys\(\((board\.\w+)/],
  ['touch', /touch=touchio.TouchIn\((board\.\w+)/],
]) assert.equal(aliases[step(id).kbPins[0]] || step(id).kbPins[0], boardPins(firmware.match(expression)[1])[0], `${id}: wrong controller pad`);
assert.deepEqual([step('encoder-a').kbPins[0],step('encoder-b').kbPins[0]], boardPins(firmware.match(/encoder=rotaryio.IncrementalEncoder\(([^)]+)\)/)[1]));
assert.deepEqual([0,1,2].map(i=>aliases[step(`indicator-${i}`).kbPins[0]]||step(`indicator-${i}`).kbPins[0]),boardPins(firmware.match(/for pin in \(([^)]+)\)/)[1]));
assert.equal(wiring.pixelCount, Number(firmware.match(/NeoPixel\(board\.MOSI,(\d+)/)[1]));
assert.match(firmware, /pixel_order=neopixel.GRBW/);
const documentedLegs = new Set(wiring.chapters[0].steps.flatMap(s => s.icPins));
assert.deepEqual([...documentedLegs].sort((a,b)=>a-b),Array.from({length:14},(_,i)=>i+1),'All DIP legs, including unused channels, must be documented');
const pads = new Set(wiring.kbPins.map(p => p.id));
for(const s of steps) {
  for(const field of ['title','from_','to','how','why','check']) assert(s[field], `Missing ${field} for ${s.id}`);
  for(const pad of s.kbPins) assert(pads.has(pad), `Unknown photo pad ${pad}`);
}
for(const asset of ['kb2040.jpg','pixels.jpg','joystick-bottom.jpg','encoder.jpg','switch.webp']) await access(new URL('../public/images/wiring/'+asset,import.meta.url));
console.log(`Wiring checked: ${steps.length} guided connections, 13 physical switches / 12 actions, ${wiring.pixelCount} RGBW pixels, all controller assignments and 14 IC legs.`);
