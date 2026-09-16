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
    "07_upper_joint_sample_v5": "mounting-v5/files/PRINT_FIRST_upper_joint_sample",
    "07_lower_joint_sample_v5": "mounting-v5/files/PRINT_FIRST_lower_joint_sample",
    "04_joystick_corner_v5": "mounting-v5/files/PRINT_FIRST_joystick_corner",
    "02_top_plate_v5_WAIT": "mounting-v5/files/WAIT_full_top_plate",
    "07_light_tray_v5_WAIT": "mounting-v5/files/WAIT_lower_light_tray",
    "04_joystick_adapter_v5": "mounting-v5/files/PRINT_joystick_adapter"
}
files = json.loads((ROOT / "data/files.json").read_text())
assert set(REVISIONS) <= {part["id"] for part in files}
for part_id, source in REVISIONS.items():
    for extension in ("step", "stl"):
        shutil.copyfile(DOWNLOADS / f"{source}.{extension}",
                        DOWNLOADS / extension / f"{part_id}.{extension}")

# Four test parts only: no full plates, STEP models or old revisions.
fit_kit = DOWNLOADS / "mounting-v5"
with zipfile.ZipFile(fit_kit / "print-first-STLs.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for model in ["PRINT_FIRST_upper_joint_sample", "PRINT_FIRST_lower_joint_sample",
                  "PRINT_FIRST_joystick_corner", "PRINT_joystick_adapter"]:
        archive.write(fit_kit / "files" / f"{model}.stl", f"{model}.stl")
    archive.writestr("READ-ME.txt", "Print one of each STL at 100% scale. Upper/corner visible face DOWN. Lower cups UP. Adapter pegs DOWN with support under the base. Follow https://codexmicro.diy/downloads/mounting-v5/guide.html. Test both joints before full plates. M3 x 8 screws + M3 x 4 inserts; joystick M1.6 x 10 screws + existing nuts. Physical fit pending.\n")

# The downloadable revision kit must include its regenerated models and viewer.
kit = DOWNLOADS / "mounting-v5"
kit_files = sorted(path for path in kit.rglob("*") if path.is_file()
                   and path.name not in {"mounting-v5-kit.zip", ".DS_Store"}
                   and "__pycache__" not in path.parts)
with zipfile.ZipFile(kit / "mounting-v5-kit.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for path in kit_files:
        archive.write(path, Path("mounting-v5") / path.relative_to(kit))
with zipfile.ZipFile(kit / "mounting-v5-kit.zip") as archive:
    assert archive.testzip() is None
    for path in kit_files:
        assert archive.read(str(Path("mounting-v5") / path.relative_to(kit))) == path.read_bytes()

readme = """CODEX MICRO — CURRENT STEP FILES

Current candidate: MOUNTING V5. Physical fit testing pending.
Hidden upward M3 tray screws and separate pegged joystick adapter.
Both upper and lower plates must be the new matching v5 pair.
Keep the existing case, electronics and M3 hardware.

PRINT FIRST — FOUR SMALL PIECES
07_upper_joint_sample_v5: insert bosses belong to the UPPER sample.
07_lower_joint_sample_v5: M3 x 8 screw heads underneath this lower sample.
04_joystick_corner_v5: flat plate corner, locating/screw holes and wire slot.
04_joystick_adapter_v5: separate base, two pegs and raised ear supports.
The adapter can be reused in the final keyboard. Test inserts stay in sample.

AFTER BOTH FIT TESTS PASS
02_top_plate_v5_WAIT: new full upper plate, visible face down for printing.
07_light_tray_v5_WAIT: matching full lower tray, cups up.
Four M3 x 8 screws + four Adafruit M3 x 4 inserts (4.2 mm OD), reused types.
Joystick now needs TWO M1.6 x 10 screws; existing M1.6 nuts are reused.
Prior 8 mm joystick screws are too short for full nut engagement in v5.

The other current parts remain: case, foot, touch cap, knob, flat 1u and
wide 2u caps, switch-fit and stem-fit coupons. No new KB2040 holder added.

REFERENCE ONLY
reference/mounting_v5_assembly_NOT_PRINTABLE.step: upper, lower, adapter,
reference joystick and hardware. Not a complete keyboard or printable part.

UNITS / PRINTING
Millimeters. STEP preserves assembly coordinates; use matching bed-oriented
STLs and the guide's support notes. Adapter prints pegs down with support
under the base. No print-fit, structural or physical assembly claim is made.

https://codexmicro.diy/downloads/mounting-v5/guide.html
manifest.json records source files, quantities, print notes and SHA-256.
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
reference = "mounting-v5/files/reference_assembly_NOT_PRINTABLE.step"
reference_name = "reference/mounting_v5_assembly_NOT_PRINTABLE.step"
entries[reference_name] = (DOWNLOADS / reference).read_bytes()
manifest.append({"file": reference_name, "name": "Mounting v5 partial reference assembly — NOT PRINTABLE",
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
