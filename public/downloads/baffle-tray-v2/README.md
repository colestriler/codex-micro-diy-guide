# Codex Micro: two-layer baffle tray v2

Experimental mechanical design. CAD checks pass; physical print fit, assembly access, strength and optical performance are not verified.

## Print these two first

- `files/PRINT_FIRST_two_key_top_sample.stl` — one, white or clear PETG. Visible face DOWN as supplied. 48 × 26.95 × 3 mm.
- `files/PRINT_FIRST_two_key_baffle_sample.stl` — one, black PETG. Flat bottom DOWN, cavities UP. 40 × 26.45 × 12 mm.

100% scale; 0.4 mm nozzle; 0.15 mm layers; four walls; 100% infill; supports OFF for these two samples. Check the sliced holes, floor slots and wall paths. Do not scale to adjust fit.

These are literal crops of the full plate and tray, not a differently dimensioned mock-up. The sample contains two illuminated-key positions and the two rear mounting points. It does not verify the full assembly against your case, encoder, joystick, controller or complete harness.

## What it is

The upper plate holds the switches. A separate lower tray combines the six light cups, LED locating pockets and four 8 mm diameter solid posts. Four metal through-bolts clamp the top plate to the posts; loose exposed nuts bear on the flat underside. No plastic snap arms, glue or captive nut boxes attach the tray.

The lower piece covers just the six illuminated keys, not the whole keyboard. This stepped footprint leaves space for other controls. Existing case geometry is retained. The candidate upper plate is the flat joystick v3 plate with four new holes, without snap-baffle clips. Existing top plates do not have these holes; print the matching candidate after the fit tests rather than improvising a drilling operation.

## Hardware

Full assembly: four M3 × 20 mm fully threaded DIN 912 socket cap screws and four ordinary M3 DIN 934 hex nuts. Test sample: two pairs, reusable in final build. These are additional to the original case and joystick hardware.

- Screw: https://www.vital-parts.co.uk/socket-cap-screws-din-912/13260-hsc912-m3-20-a2
- Nut: https://www.accu.co.uk/hexagon-nuts/7888-HPN-M3-A2

Reference screw head is 5.5 mm diameter × 3 mm high; nut is 5.5 mm across flats × 2.4 mm thick. Use a 2.5 mm hex key plus 5.5 mm wrench/small socket. Stock and shipping not verified. Black equivalents must match these dimensions. Do not substitute the short case screws or M1.6 joystick screws. Longer screws reduce case/wiring clearance.

Heads remain visible above the upper plate. Nuts are exposed underneath. No washers are included in the modeled stack. Tighten only until the parts seat without rocking; PETG can creep or crush under excessive clamp force. Inspect for loosening after use.

## Assembly / learning test

1. USB disconnected. Clear printing burrs and strings. Screws should pass freely through the 3.4 mm holes, not cut threads into them.
2. Put the cup openings toward the underside of the upper sample. Insert screws from above and finger-start the exposed nuts below. Hold each nut with a wrench; gently snug the screw.
3. The cup rims and posts should meet the upper plate with no rocking. Snap in two real switches from above and test the keycaps through full travel.
4. Unscrew the lower sample to expose switch pins for soldering. These screws only release the lighting tray, not the soldered switches from the upper plate.
5. Dry-fit the real 9.1 × 9.1 × 3.1 mm LEDs in the 9.7 mm square pockets. Pockets locate, but do not positively retain, the LEDs. Use thin removable electrically insulating adhesive beneath each board; total allowance is 0.2 mm. Cover rear pads and keep light-emitting faces clear. Thicker foam is not covered by the clearance check.
6. LED wires pass down through the 6 × 2.2 mm floor slots. Switch/diode leads pass through the 6 mm wide top notches on all four sides. Keep metal ends clear and leave about 20 mm of usable lowering travel in the harness. There is no electrical disconnect in this revision.
7. Reassemble without trapping wires. Check actual solder joints and switch pins remain clear of LEDs. Test one correctly wired LED for light leakage before committing to the full lighting chain.

For service in the finished keyboard: unplug USB, undo case screws and lift the upper plate and tray together far enough to access the nuts without stressing the attached controller/wires. Support both pieces. Undo the four tray nuts and lower the tray. Do not attempt to pull it down through the case floor or force it past fixed wires.

## Full files — WAIT for fit tests

- `files/WAIT_full_top_plate.stl`: one upper plate, 94 × 94 × 4 mm overall. Underside down as supplied, joystick seats up. Review shallow MX underside recesses in the slicer; local support may be needed. It deliberately has a different orientation from the small upper coupon.
- `files/WAIT_six_light_baffle_tray.stl`: one black PETG tray, 91 × 45.325 × 12 mm. Flat bottom down; all cups and posts up. Supports off; four walls and 100% infill.

Also pass the separate joystick v3 physical fit test before printing the full upper plate. STEP files use assembled coordinates. STL files are translated to the bed and oriented for printing; do not overlay the STLs to infer assembly alignment. `reference_assembly_NOT_PRINTABLE.step` includes reference electronics envelopes and is for viewing only.

## Dimensions and checks

Coordinates relative to the center of the original upper plate:
- Mounts: (-16, 41.5), (16, 41.5), (-41.5, 9.525), (41.5, 9.525) mm.
- Upper plate: z22–25 mm (joystick seats up to z26).
- Lower tray: z10–22 mm, floor generally 1.8 mm, cup walls 1.2 mm.
- LED pocket floor z10.8 mm (0.8 mm remaining plastic), insulated LED bottom z11 mm, top z14.1 mm.
- Nominal switch pin envelope begins z14.9 mm: 0.8 mm vertical gap.
- Approximate controller top z8.9 mm: tray floor clearance 1.1 mm. Real solder, wiring, mounting tape and component heights must be checked.
- Screws extend from z25 to z5; nuts z7.6–10. Tips protrude 2.6 mm below nuts, remain 2.6 mm above the modeled case floor, and must be kept clear of wires.

`build.py` checks each printable export is a single valid watertight solid; checks tray/plate/case separation, approximate control envelopes, 13 switch/pin envelopes, six LED clearances, screw/nut intersections and nut bearing area; samples the downward tray-removal path after lifting the assembly out of the case. `validation.json` records results and limits. This is not a load simulation or a complete vendor-component assembly.

The old main keyboard animation still shows individual adhesive cups. This folder's guide and CAD are the current two-layer proposal. Archived clip files remain for history and should not be mixed with this design.

## Rebuild

Install `requirements.txt` in a Python 3.12 environment and run `python build.py` from this directory. The bundled STEP references are the project's existing case and flat joystick v3 top plate. `preview.png`, `scene.js` and `scene.json` are generated from the same CadQuery shapes as the print exports. `guide.html` uses local Three.js (license included); it works as a downloaded local page as well as on the website.
