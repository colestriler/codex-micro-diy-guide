# Codex Micro mounting v5 — fit-test release

Hidden upward tray fasteners and a separate keyed joystick adapter. Replaces
baffle-tray-v4 + joystick-flat-v3 as the current candidate. Both full plates
change; the old upper/lower pair must not be mixed with these parts.

Start with `guide.html`. `print-first-STLs.zip` contains exactly four small
prints: upper joint sample, lower joint sample, joystick corner and adapter.
Use `WAIT_` full-size files only after both tests pass. The tested adapter can
be reused. STEP files retain assembly coordinates; STLs are bed-oriented.

## Fasteners

- 4 M3 x 8 socket cap screws enter from under the lower tray.
- 4 Adafruit 4255 M3 x 4 inserts (4.2 mm OD) go in the UPPER plate bosses.
- Joint: 3 mm lower grip + 4 mm engagement + 1 mm thread past insert;
  blind tip well leaves 1 mm tip clearance. Insert interference is intentional.
- Joystick uses two M1.6 x 10 DIN912 screws with existing standard M1.6 nuts.
  The prior 8 mm screws are too short for full nut engagement with this adapter.
  Nuts are exposed below the upper plate. No captive nut boxes.
- Existing four corner case fasteners remain. The two joystick tab screws are
  still visible at the joystick; no tray screws appear on the front.

## Design

Upper bosses: 8 mm diameter, 9 mm tall, 3.9 x 4.3 mm starting insert pilots.
Lower tray: original v4 cups and 10 x 4 mm rounded LED openings preserved;
old tall posts shortened to mounting shelves. The upper boss enters a cutout
with 0.2 mm nominal radial clearance.

Adapter: 1.6 mm base; 0.5 / 1.0 mm ear seats; two 3.6 mm pegs, 2 mm long,
in 4 mm plate holes; 2.4 mm joystick clearance holes; 9 x 4 mm wire slot.
Joysticks vary: confirm both ears are supported without bending and the actual
thumb control has full travel. Do not tighten screws to compensate for a gap.

## Reproduce

Python environment with `requirements.txt`: run `python build.py`, then
`python render.py`. Models in references are the immutable input geometry.
Validation is written only after checks pass. `scene.js` and `preview.png`
are generated from the actual CAD geometry.

The community joystick reference is attributed under `reference-model-LICENSE.txt`.
The vendor product is SparkFun COM-09426 / PSP1000:
https://www.sparkfun.com/thumb-slide-joystick.html
M1.6 x 10 screw dimensions:
https://www.accu.co.uk/metric-cap-head-screws/3785-SSCF-M1-6-10-A2
M3 x 8 screw: https://www.mcmaster.com/91290A113/
M3 insert: https://www.adafruit.com/product/4255

## Limits

Nominal CAD collision checks and watertight meshes are not physical validation.
No structural load, fatigue, insert pullout or completed-keyboard tests have
been performed. Real wires, solder, thumb cap travel and driver access require
checking on the samples. Do not claim this is a verified production fit.
