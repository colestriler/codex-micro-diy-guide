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

Rebuild:

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python cad/build.py
.venv/bin/python tools/verify.py
.venv/bin/python tools/render.py
```

Source research checked 2026-09-06. All electronics and CAD dimensions need a physical fit test before final assembly.
