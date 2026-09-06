import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const labels = JSON.parse(await readFile(resolve(root, "data/key-labels.json"), "utf8"));
const centers = [14, 40, 66, 92, 127, 158];
const decals = labels.map((label, index) => {
  const x = centers[index % 6], y = index < 6 ? 30 : 60;
  const width = label.entry === "wide" ? 37.05 : 18;
  return `<g transform="translate(${x} ${y})">
    <rect x="${-width / 2}" y="-9" width="${width}" height="18" rx="3" fill="none" stroke="#ccc" stroke-width=".2" stroke-dasharray="1 1"/>
    ${label.icon ? `<path d="${label.icon}" transform="translate(0 -2) scale(.75)" fill="none" stroke="#111" stroke-width=".45" stroke-linecap="round" stroke-linejoin="round"/>` : ""}
    <text y="${label.icon ? 4.5 : 1.4}" font-size="${label.icon ? 1.9 : 3.6}" text-anchor="middle" font-family="Arial,sans-serif" fill="#111">${label.label}</text>
  </g>`;
}).join("\n").replace(/[ \t]+$/gm, "");
await writeFile(resolve(root, "public/downloads/docs/key-legends.svg"), `<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="95mm" viewBox="0 0 180 95">
  <title>DIY Micro numbered key labels and command legends</title>
  <desc>Functional DIY labels matching the interactive model. Printed CAD caps are blank; apply these as decals. Not manufacturer artwork.</desc>
  <g font-family="Arial,sans-serif" fill="#333"><text x="5" y="7" font-size="3">DIY MICRO / KEY LABELS</text><text x="5" y="13" font-size="2.4">Print at 100% on clear decal paper. Cut close to the black legends; discard gray outlines.</text></g>
  ${decals}
  <path d="M6 82h20M6 80v4M26 80v4" fill="none" stroke="#111" stroke-width=".25"/>
  <text x="31" y="83" font-family="Arial,sans-serif" font-size="2.4" fill="#333">20 mm — verify with a ruler before applying</text>
  <text x="5" y="91" font-family="Arial,sans-serif" font-size="2.2" fill="#666">Concept labels describe intended controls. Custom firmware still needs native Codex integration.</text>
</svg>\n`);
console.log("Built printable label sheet for twelve keycaps.");
