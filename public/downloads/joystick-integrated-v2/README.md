# Integrated joystick mount — v2 fit test

Print **only `files/PRINT_FIRST_joystick_corner_v2.stl`** for now. The holder and both tab supports are part of this one print. No loose shims.

This is a 30.5 × 30.5 mm corner cut directly from the redesigned full top plate. It retains the actual rounded case corner, M3 mounting hole and nearby switch-opening edges. The rest of the plate is unchanged outside the joystick area. The candidate full plate is included as `WAIT_full_top_plate_v2`; do not print it until the corner passes the fit checks.

## How it mounts

The stationary joystick body sits in a shallow 1 mm recess. Its two ears sit on built-in supports at 0.5 mm and 1.0 mm above the body seat, reproducing the starting v1 shims. Two screws clamp those ears to metal nuts in pockets under the plate. The main plate is still 3 mm thick; only the nut bosses project 4.8 mm below it. Nothing is stacked on top as a separate stand.

The joystick is rotated 180 degrees relative to the v1 bench holder. The mounting ears face the outside/right edge of the keyboard; the four solder pads face the neighboring key row. A 9 × 4 mm opening beneath the pads routes the wires down into the case. Do not reuse the old center hole or infer pad order from the old orientation.

Its center is now (29, 30.5) mm in the original plate coordinates. A relief around the existing case screw pillar provides clearance. CAD checks found no interference with the original case or nominal neighboring 18 mm keycaps. The real textured thumb cap's shape and travel are not accurately represented by the community reference: physical movement must be checked.

## Print settings — support needed for the shallow recess

- One corner STL, 100% scale, millimeters. Do not mirror or scale to fit.
- Use existing PETG. Any color works for this test; white matches the final plate.
- 0.4 mm nozzle, 0.10 mm layers, four walls, 100% infill for the small test.
- Leave the STL in its supplied orientation: visible face down, the two nut bosses pointing up. The final full plate uses the same orientation.
- Enable build-plate supports beneath the shallow joystick recess and the lower mounting-ear seat. Inspect your slicer's layer preview: those recessed surfaces begin above the bed and must not print into air. Keep the wire opening clear and use support blockers for the narrow nut tunnels and screw slots; the 3.5 mm nut-tunnel roofs are short bridges.
- Remove supports carefully from the body seat and ear seat, and clean strings from the wire opening and nut slots. A leftover support layer can lift the joystick and create a false gap. Do not sand the support heights down to force a fit.

## Hardware

Same as v1: **two M1.6 × 8 mm DIN 912 screws**, **two M1.6 DIN 934 nuts**, and a **1.5 mm hex key**. No additional electronics or new fastener size.

- [Screws](https://www.accu.co.uk/metric-cap-head-screws/3784-SSCF-M1-6-8-A2): 0.35 mm pitch, 3 mm head diameter, 1.6 mm head height.
- [Nuts](https://www.accu.co.uk/hexagon-nuts/7882-HPN-M1-6-A2): 3.2 mm across flats, 1.3 mm thick.

Check stock and pack sizes with the seller. The screws are not the M3 screws used to attach the top plate to the case.

## Fit checks — do these before the full plate

1. Unplug the KB2040. Remove print supports, then try the joystick in the loose corner with no screws or nuts. Do not put any of the old loose shims in this mount.
2. Identify the rounded outer corner and its larger M3 case hole. The joystick ears go on that outer side. The ear near the case hole uses support B; the other uses support A. The four underside solder pads go over the rectangular through-opening toward the key row. Keep its original metal cage and mounting ears intact.
3. Confirm the body sits flat without rocking and both tabs touch their seats. If a tab has a gap or a support lifts the body, stop and report it. Do not tighten screws to close a gap.
4. If the dry fit passes, turn the sample over and slide an M1.6 nut into each side pocket. Insert the M1.6 screws through the joystick ears from above and tighten gently. Hold a nut with tweezers if needed; do not force it into an undersized pocket. Check that the screws engage the nuts without bottoming out.
5. Move the thumb cap all the way in each direction and diagonally. The stationary housing should not lift, twist or rock, and the cap must not catch the plate, screw heads or edges. This physical check is required because the reference model does not reproduce the real cap's motion.
6. Remove the original full top plate and gently place this corner on the bare case ledge, aligning its rounded corner and original M3 case hole. It is a replacement test section, not an insert that goes into or on top of the old plate. The nut bosses and screw tips must clear the case post and internal wiring. Do not force it down or pull it down with the case screw.
7. Share a top and side photo, and whether there is any rocking, gap, binding or case interference. Only after these pass should the full plate be printed. The full plate will need an additional real neighboring-switch/keycap travel check during dry assembly.

## CAD and limitations

Both exported print meshes are watertight, single connected solids, at Z=0. The corner is cropped from the same CAD solid as the full plate. The generator checks reference joystick, case, hardware and static neighboring keycap clearances. This is geometric validation, not physical strength testing, slicer validation or confirmation of the actual thumb cap's movement. `validation.json` records the limits.

The original full-keyboard animation and `downloads/step/assembly.step` are still legacy geometry. Use this kit's preview and `reference-assembly_NOT_FOR_PRINTING.step` to inspect the new mount. Files under `references/` are generator inputs, not additional prints.

Install `requirements.txt` in a Python 3.12 virtual environment and run `python build.py` to regenerate. Support offsets are in `parameters.json`; their current values reproduce the v1 starting shims rather than claiming new measured dimensions.

Reference: SparkFun COM-09426 footprint in [SparkFun-Switches.lbr](https://github.com/sparkfun/SparkFun-Eagle-Libraries/blob/main/SparkFun-Switches.lbr), package JOYSTICK-PSP1000. Community model: [marbastlib PNT_psp1000](https://github.com/ebastler/marbastlib/blob/6b0a9a73f579e377816d60b58eac2b3252de7868/3dmodels/PNT_psp1000.step), credited to Hendrik Roth. The community geometry is rotated and translated in the reference assembly; its CERN-OHL-P-2.0 license is included. Its hole centers differ slightly from the SparkFun footprint; clearance slots accommodate both. Neither is a measurement of your exact joystick.
