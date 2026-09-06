import { readFile, writeFile, mkdir, copyFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "viewer-src");
const output = resolve(root, "public/viewer");
await mkdir(output, { recursive: true });
const [geometry, mapping] = await Promise.all([
  readFile(resolve(source, "geometry.json"), "utf8"),
  readFile(resolve(source, "part-map.json"), "utf8"),
]);
await writeFile(resolve(output, "model-data.js"), `const CAD=${geometry};\nconst MODEL_PARTS=${mapping};\n`);
for (const name of ["assembly.js", "three.min.js", "THREE-LICENSE.txt"]) await copyFile(resolve(source, name), resolve(output, name));
await copyFile(resolve(source, "template.html"), resolve(output, "index.html"));
console.log("Built viewer assets from the actual STEP geometry and the part catalog mapping.");
