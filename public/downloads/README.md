# Clip-on baffle update — print two small test pieces first

Open `baffle-snap-v1/guide.html`. The new cup needs matching underside plate clips. Its candidate full plate also includes the flat joystick v3 mount. Physical fit/release and fatigue remain unverified; wait for both fit tests before printing the full plate. The full plate requires supports in its supplied orientation. Old source/assembly geometry below is archived and still shows adhesive cups.

# Current joystick design: flat v3

Open `joystick-flat-v3/guide.html`. Print only the small v3 corner first, flat side down, raised supports up, supports OFF. It uses exposed M1.6 nuts with the same M1.6 × 8 mm screws. The full plate remains a candidate pending fit testing. Older kits below are archived.

# Integrated joystick v2 — print the corner first

Open `joystick-integrated-v2/guide.html`. The full top plate is a candidate pending the corner fit test. Two M1.6 × 8 mm screws and M1.6 nuts, same as v1; no loose shims. Original assembly STEP and original generator still show the old mount. The versioned v2 kit contains the new parametric source and reference assembly.

# Joystick fit-kit update

Joystick update: use the new screw-retained bench fit kit first. The original cradle and full keyboard animation are legacy geometry; the final top-plate attachment is not yet designed or physically verified. Keep your existing top plate until the sample fits.

Use `joystick-fit-v1/guide.html` and `joystick-fit-v1/joystick-fit-sample-v1.zip` in the downloads root. The original cad/build.py still generates the superseded cradle. New source: joystick-fit-v1/build.py. New screws: 2 × M1.6 × 8 mm DIN 912; nuts: 2 × M1.6 DIN 934; tool: 1.5 mm hex key.

# DIY Micro — Rev A

Open `build-guide.html` for the complete specification, bill of materials, links, assembly and firmware instructions.

This is an independent, dimensioned reconstruction of the OpenAI × Work Louder Codex Micro visual layout. It is not the manufacturer's CAD and has not been physically printed or electrically tested.

## Full native functionality

OpenAI documents support for the Codex Micro and Creator Micro 2. Keep the genuine electronics and firmware for the documented integration. The supplied CAD is for the custom hand-wired prototype; it is NOT verified to accept an OEM donor PCB. A donor enclosure requires the measurements in `docs/oem-measurements.csv` and a mechanical revision before printing.

The custom KB2040 firmware supports input scanning, generic USB macros, dial scrolling, joystick arrows, touch-selected banks, and manual RGBW commands. It does NOT implement native Codex task association, live status synchronization, push-to-talk integration, or native device detection. Do not buy custom electronics expecting automatic feature parity.

## Assembly animation

Open `assembly-animation.html` for the offline interactive 3D player, also embedded in the guide. It uses the nine assembled printed-part STEP geometries, plus simplified electronics and fasteners. Play eleven stages, scrub the timeline, rotate/zoom, inspect the underside, or make the case transparent. Cable paths illustrate service slack rather than electrical connections.

Rebuild the animation after exporting updated STEP files with `.venv/bin/python tools/make_animation.py`, then rebuild the guide with `.venv/bin/python tools/make_guide.py`. The Three.js 0.160.1 dependency is vendored with its MIT license.

## CAD

- `stl/` — print-oriented meshes (11 unique parts, some printed multiple times)
- `step/assembly.step` — assembled CAD; REF components are simplified purchased-part envelopes, not printable
- `step/` — individual editable STEP solids
- `cad/build.py` and `cad/parameters.json` — editable parametric source
- `cad/preview.glb` — 3D preview
- `docs/validation.json` — actual checks and limitations

Units: millimetres. Overall prototype case: 110 × 110 × 25 mm, before controls and 5 mm foot. It is deliberately deeper than a custom-PCB design. Standard MX switch centers: 19.05 mm.

Keycap update, 13 September 2026: both cap files now have flat finger surfaces, rounded corners and a 0.5 mm beveled rim. File 08 is shared by the five white command caps and six clear agent caps; file 09 is the white wide cap with two MX sockets 19.05 mm apart. Print top up at 100% scale, with underside supports as needed and sockets kept clear. For a 0.4 mm nozzle, start with 0.10–0.12 mm layers. Print the stem-fit coupon and one cap before the full set; physical fit and finish remain untested.

Rebuild:

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python cad/build.py
.venv/bin/python tools/verify.py
.venv/bin/python tools/render.py
```

Source research checked 2026-09-06. All electronics and CAD dimensions need a physical fit test before final assembly.
