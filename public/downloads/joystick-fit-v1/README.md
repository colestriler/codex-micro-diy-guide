# Joystick fit holder — v1

A 26.5 × 26.5 mm bench sample for SparkFun COM-09426. It supports the stationary housing, locates it with low stops, provides adjustable screw slots and leaves an open passage beneath the solder pads. The removable spacers support the mounting ears without pulling them down when screws tighten.

Open `guide.html` for pictures, print-file links and hardware links.

## Print first

- `files/holder.stl`: one, flat bottom down, 0.2 mm layers, 4 walls, 100% infill.
- `files/shim_A_0.5mm.stl`: one, flat down, 0.1 mm layers, 100% infill.
- `files/shim_B_1.0mm.stl`: one, flat down, 0.1 mm layers, 100% infill.
- The other two shim files are optional thickness alternatives; keep each A/B shim at its own mounting position. All STLs are already centered and placed on Z=0 for printing. Units are millimeters; use 100% scale.
- Use your existing PETG, including clear PETG. PLA is also suitable for this bench sample. Transparency is not required. A 0.4 mm nozzle is suitable. Supports off; the small nut tunnels require bridging. Clean strings from slots. Do not force nuts into an undersized printed tunnel.

## Hardware for the retention test

- Two M1.6 × 8 mm, 0.35 mm pitch, DIN 912 socket-head screws; head diameter 3 mm, head height 1.6 mm.
- Two M1.6 DIN 934 hex nuts, 3.2 mm across flats, 1.3 mm thick.
- 1.5 mm hex key for the specified screws; tweezers help position the nuts.

Screw specifications/product: https://www.accu.co.uk/metric-cap-head-screws/3784-SSCF-M1-6-8-A2

Nut specifications/product: https://www.accu.co.uk/hexagon-nuts/7882-HPN-M1-6-A2

Equivalent fasteners with those dimensions can be sourced elsewhere. Live availability and delivery are not verified. The previously discussed M2 screws are superseded for this sample: their 3.8 mm heads slightly intersect one corner of the community reference model. M1.6 leaves clearance in the nominal 2 mm joystick holes. Do not substitute the keyboard's M3 case screws.

## Fit check — before soldering or tightening

1. Unplug the KB2040. Work with the joystick loose on the bench. Keep its mounting ears and metal retention cage intact.
2. Face the holder's open U-shaped end away from you; the two screw platforms are on your left. A is the far-left platform near the open end; B is the near-left platform near the closed end.
3. Put the 0.5 mm A shim on A and the 1 mm B shim on B. Their cut-away inner corners face the main joystick body. They sit on the two screw platforms, with slots aligned. You can rotate each loose shim in the slicer preview to compare its shape with the assembly STEP; do not flip its A/B designation.
4. Lower the joystick onto the four small inner support blocks. Its four underside solder pads face the open end. The two ears should align with the two platforms. The pads remain accessible over the open passage; later the insulated wires can turn down toward the existing top-plate opening.
5. Check that the stationary body rests flat, both ears are supported, and the thumb control moves freely. If a spacer makes the body rock, stop and try the thinner spacer for that position. If there is still a gap or it will not seat, send top and side photos before tightening. Do not use screws to pull a bent or unsupported ear into place.
6. Once the dry fit works, slide one nut into each side tunnel. Put the screws down through the joystick ears and shim slots, then turn them gently into the nuts. The slots allow slight adjustment; hold a nut with tweezers if it turns. The two nuts must be engaged. Tighten only enough to stop movement; tiny plastic ears need very little force.
7. Move the thumb control fully in all directions, then gently check for lift or rocking of the fixed housing. The screw tips should stay inside the holder. If a screw bottoms out, an ear bends, or movement binds, stop. Do not add more torque.

You can perform steps 1–5 without the new screws. The next useful feedback is one top photo and one side photo with the joystick resting in the sample.

## What this sample establishes

It tests housing clearance, mounting alignment, spacer height, fastener access, and room for wires. Attachment of this holder to the keyboard top plate, surrounding keycap clearance, and the full thumb-cap motion envelope still need checking. Keep your current top plate; do not drill, glue or reprint it for this test. The holder's full base sits above a plate; it does not press into the old 22 mm recess.

The sample raises the joystick body bottom 7 mm above its underside. This height provides accessible nut tunnels and screw-tip clearance for the bench test; the final integrated mounting height may change after fit feedback.

## CAD validation and provenance

`build.py` creates the holder, four shim choices, and a STEP reference assembly. `validation.json` records the checks: one valid solid per printable part; no solid overlap with the community joystick; shafts fit at both SparkFun and marbastlib hole layouts; selected screw heads and nuts clear the modeled housing and holder. These checks do not establish physical fit, FDM hole accuracy, or motion limits. Threads are simplified in the reference assembly. The original removable thumb cap is not represented accurately by the community model.

The source model hole centers differ from SparkFun's footprint. This sample intentionally accommodates both; it is not called a verified BOM or final production design.

- Exact-SKU footprint: https://github.com/sparkfun/SparkFun-Eagle-Libraries/blob/main/SparkFun-Switches.lbr (`JOYSTICK-PSP1000`, COM-09426).
- Community model: https://github.com/ebastler/marbastlib/blob/6b0a9a73f579e377816d60b58eac2b3252de7868/3dmodels/PNT_psp1000.step
- marbastlib credits Hendrik Roth for the PSP-1000 model. Its CERN-OHL-P-2.0 license is included in `reference-model-LICENSE.txt`. The reference assembly incorporates that model, rotated and translated; the manufactured joystick itself is not a printable part.

Only print files named `holder.stl` and `shim_*.stl`. The STEP assembly includes purchased reference hardware and is for inspection.

## Rebuild the sample

Using Python 3.12, install `requirements.txt` in a virtual environment and run `python build.py`. The community STEP reference is included under `references/`; its license is included in `reference-model-LICENSE.txt`. This source regenerates the five sample prints, reference assembly, preview and validation report. It does not redesign the full keyboard plate.
