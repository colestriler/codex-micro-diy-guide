"""Publish the current revision exports and a STEP-only set without retired designs.

Run after updating a revision kit. Does not regenerate geometry or the legacy viewer.
The catalog in data/files.json defines the current printable parts and fit samples.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "public/downloads"
CURRENT = DOWNLOADS / "current-cad"
CURRENT.mkdir(exist_ok=True)
REVISIONS = {
    "07_two_layer_top_sample": "baffle-tray-v3/files/PRINT_FIRST_two_key_top_sample",
    "07_heatset_baffle_sample_v3": "baffle-tray-v3/files/PRINT_FIRST_two_key_baffle_sample",
    "04_flat_joystick_corner_v3_PRINT_FIRST": "joystick-flat-v3/files/PRINT_FIRST_flat_joystick_corner_v3",
    "02_two_layer_top_plate_WAIT": "baffle-tray-v3/files/WAIT_full_top_plate",
    "07_heatset_six_light_tray_v3_WAIT": "baffle-tray-v3/files/WAIT_six_light_baffle_tray",
}
files = json.loads((ROOT / "data/files.json").read_text())
assert set(REVISIONS) <= {part["id"] for part in files}
for part_id, source in REVISIONS.items():
    for extension in ("step", "stl"):
        shutil.copyfile(DOWNLOADS / f"{source}.{extension}",
                        DOWNLOADS / extension / f"{part_id}.{extension}")

readme = """CODEX MICRO — CURRENT STEP FILES

Current revisions: flat joystick mount v3 + heat-set baffle tray v3.
The upper plate includes BOTH the flat joystick mount and the four tray holes.
Its geometry and the upper fit sample are unchanged from baffle-tray-v2;
their STEP exports are now synchronized with the v3 kit.

START WITH THESE THREE FIT SAMPLES
07_two_layer_top_sample.step — upper two-key sample; reuse the v2 sample.
07_heatset_baffle_sample_v3.step — lower sample for M3 x 4 heat-set inserts.
04_flat_joystick_corner_v3_PRINT_FIRST.step — flat seat + raised joystick tabs.

FULL PARTS — WAIT FOR SAMPLE FIT CHECKS
02_two_layer_top_plate_WAIT.step — upper plate with both revised features.
07_heatset_six_light_tray_v3_WAIT.step — uses four M3 x 8 screws and M3 x 4 inserts.
The other current part files are included: case, foot, touch cap, knob,
flat 1u / wide 2u keycaps, switch-fit coupon and stem-fit coupon.
The case is the existing revision; no new KB2040 retention feature was added.

REFERENCE ONLY
reference/tray_v3_assembly_NOT_PRINTABLE.step shows the current upper plate,
lower tray, screws, inserts and approximate switch/LED envelopes.
It is a partial assembly for understanding the tray, not a complete keyboard
assembly or an additional print. The older full-keyboard assembly is excluded.

UNITS / PRINTING
All dimensions are millimeters. STEP is for CAD editing and inspection;
files can retain assembled coordinates. Use the matching print-oriented STL
from the website and follow each part's print orientation notes.
Physical fit, heat-set grip and full assembly strength remain unverified.
Print/check the samples before either WAIT full-size part.

Guides and matching STLs: https://codexmicro.diy/#files
Tray: https://codexmicro.diy/downloads/baffle-tray-v3/guide.html
Joystick: https://codexmicro.diy/downloads/joystick-flat-v3/guide.html
manifest.json records each source, quantity, print note and SHA-256.
"""
(CURRENT / "README.txt").write_text(readme)
entries = {}
manifest = []
for part in files:
    name = f"{part['id']}.step"
    source = f"step/{name}"
    data = (DOWNLOADS / source).read_bytes()
    assert data.startswith(b"ISO-10303-21;") and b"END-ISO-10303-21;" in data
    entries[f"parts/{name}"] = data
    manifest.append({"file": f"parts/{name}", "name": part["name"],
                     "quantity": part["quantity"], "print_note": part["note"],
                     "source": f"/downloads/{REVISIONS.get(part['id'], source.removesuffix('.step'))}.step",
                     "sha256": hashlib.sha256(data).hexdigest()})
reference = "baffle-tray-v3/files/reference_assembly_NOT_PRINTABLE.step"
reference_name = "reference/tray_v3_assembly_NOT_PRINTABLE.step"
entries[reference_name] = (DOWNLOADS / reference).read_bytes()
manifest.append({"file": reference_name, "name": "Tray v3 partial reference assembly — NOT PRINTABLE",
                 "source": f"/downloads/{reference}",
                 "sha256": hashlib.sha256(entries[reference_name]).hexdigest()})
(CURRENT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
entries["README.txt"] = (CURRENT / "README.txt").read_bytes()
entries["manifest.json"] = (CURRENT / "manifest.json").read_bytes()
with zipfile.ZipFile(CURRENT / "Codex-Micro-current-STEP.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for name, data in entries.items():
        archive.writestr(f"Codex-Micro-current-STEP/{name}", data)
with zipfile.ZipFile(CURRENT / "Codex-Micro-current-STEP.zip") as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(entries)
    for name, data in entries.items():
        assert archive.read(f"Codex-Micro-current-STEP/{name}") == data

# Keep the existing complete archive, including wiring/PDF and historical kits,
# synchronized without the legacy CAD script overwriting the current catalog.
paths = sorted(path for path in DOWNLOADS.rglob("*") if path.is_file()
               and path.name not in {"build-files.zip", ".DS_Store"}
               and "__pycache__" not in path.parts)
with zipfile.ZipFile(DOWNLOADS / "build-files.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for path in paths:
        archive.write(path, Path("codex-micro-diy") / path.relative_to(DOWNLOADS))
with zipfile.ZipFile(DOWNLOADS / "build-files.zip") as archive:
    assert archive.testzip() is None
    for path in paths:
        assert archive.read(str(Path("codex-micro-diy") / path.relative_to(DOWNLOADS))) == path.read_bytes()
print(f"Published {len(files)} current part STEP files, 1 partial reference assembly, and {len(paths)} complete-archive files.")
