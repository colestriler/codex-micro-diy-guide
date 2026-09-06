import { readFile, access } from "node:fs/promises";
import { resolve } from "node:path";
import assert from "node:assert/strict";
const root = resolve(import.meta.dirname, "..");
const read = async path => JSON.parse(await readFile(resolve(root, path), "utf8"));
const parts = await read("data/parts.json");
const mappings = await read("viewer-src/part-map.json");
const files = await read("data/files.json");
const labels = await read("data/key-labels.json");
const lessons = await read("data/assembly-lessons.json");
assert.equal(labels.length, 12, "Expected twelve labeled keycaps");
assert.equal(new Set(labels.map(label => label.entry)).size, 12, "Duplicate key label");
for (const label of labels) assert(mappings[label.entry] && label.label, `Unknown key label: ${label.entry}`);
const ids = new Set(parts.map(part => part.id));
assert.equal(lessons.length, 10, "Expected all ten assembly lessons");
assert.equal(new Set(lessons.map(lesson => lesson.id)).size, lessons.length, "Duplicate assembly lesson id");
for (const lesson of lessons) {
  assert(lesson.title && lesson.why && lesson.check && lesson.caption && lesson.how.length, `Incomplete lesson: ${lesson.id}`);
  for (const id of lesson.parts) assert(ids.has(id), `Unknown lesson part: ${id}`);
  if (lesson.visual === "cad") {
    const model = lesson.model;
    assert(model.from >= 0 && model.to <= 11 && model.from <= model.to, `Invalid animation range: ${lesson.id}`);
    for (const pattern of [...model.parts, ...model.context]) {
      assert(Object.keys(mappings).some(id => pattern.endsWith("*") ? id.startsWith(pattern.slice(0, -1)) : id === pattern), `Unknown focus group: ${pattern}`);
    }
    for (const label of model.labels) assert(mappings[label.entry], `Unknown annotation: ${label.entry}`);
  }
  for (const link of lesson.links) {
    if (link.url.startsWith("/")) await access(resolve(root, "public" + link.url));
    else if (!link.url.startsWith("#")) assert.equal(new URL(link.url).protocol, "https:");
  }
}
assert.equal(ids.size, parts.length, "Duplicate part id");
for (const [mesh, part] of Object.entries(mappings)) assert(ids.has(part), `Unknown part mapping: ${mesh} → ${part}`);
for (const part of parts) {
  assert(part.name && part.description && part.spec && part.links.length, `Incomplete part: ${part.id}`);
  if (part.category === "Printed") assert(["Clear PETG", "White PETG", "Black PETG"].includes(part.material), `Missing print material: ${part.id}`);
  for (const link of part.links) assert.equal(new URL(link.url).protocol, "https:", `Unsafe purchase link: ${part.id}`);
  for (const file of part.files) await access(resolve(root, "public" + file.url));
}
for (const file of files) for (const ext of ["stl", "step"]) await access(resolve(root, `public/downloads/${ext}/${file.id}.${ext}`));
const geometry = await read("viewer-src/geometry.json");
assert.equal(Object.keys(geometry).length, 9);
for (const mesh of Object.values(geometry)) {
  const vertices = Buffer.from(mesh.vertices, "base64");
  const indices = Buffer.from(mesh.indices, "base64");
  assert.equal(vertices.length % 12, 0);assert.equal(indices.length % 12, 0);
  for (let i=0; i<indices.length; i+=4) assert(indices.readUInt32LE(i) < vertices.length/12);
}
console.log(`Checked ${parts.length} described parts, ${Object.keys(mappings).length} model mappings, 9 CAD meshes, and all printable downloads.`);
