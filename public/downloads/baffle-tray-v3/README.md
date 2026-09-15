# Two-layer baffle tray v3 — existing screws and inserts

Replaces v2 loose nuts and long bolts with the M3 × 8 mm screws and Adafruit M3 × 4 mm inserts already specified for this build. Physical heat-set fit and strength remain unverified.

## What to print

One `PRINT_FIRST_two_key_baffle_sample.stl`, black PETG. Reuse the v2 upper sample if already printed; otherwise print one `PRINT_FIRST_two_key_top_sample.stl` in white or clear PETG. Both included STL orientations use supports off. 100% scale, 0.4 mm nozzle, 0.15 mm layers, four walls, 100% infill.

After the sample and joystick tests pass: one `WAIT_six_light_baffle_tray.stl`. The full `WAIT_full_top_plate.stl` is geometrically unchanged from baffle-tray-v2; do not reprint it if you have that exact version. Older snap/adhesive plates are different. Lower tray bottom down, cups up. Full upper plate underside down, joystick seats up; review local support for underside switch recesses (different orientation from the small upper sample).

## Existing hardware

- Full tray: four spare M3 × 8 mm socket cap screws, McMaster 91290A113: https://www.mcmaster.com/91290A113/
- Four M3 × 4 mm heat-set inserts, 4.2 mm OD, Adafruit 4255: https://www.adafruit.com/product/4255
- Sample: two screws and two inserts. Screws can be reused; embedded sample inserts stay there.
- Keyboard total: ten inserts installed (four case, two foot, four tray), plus two for this sample. Existing 50-pack covers these quantities if sufficient spares remain. Original case and foot screws are still required.
- No M3 × 20 screws or loose tray nuts required. Screw heads remain above the upper plate.

The insert dimensions are verified on Adafruit's product page. The existing BOM identifies the screws as M3 × 8; the McMaster part number is also identified as M3 × 8 in the PUNYO project BOM: https://punyo.tech/downloads/Bubble_Gripper_BOM_v2.0.pdf . McMaster's product page could not be retrieved by the research tool. Confirm your packet label and measure under-head length before assembly.

## Insert installation

Unplug USB, remove all electronics, and place the lower tray flat with cups up. Slowly press each heated insert vertically into its top-facing pilot using a suitable insertion tip. Follow the filament/tool heat-setting guidance; no single temperature is prescribed here. Seat flush with the post top. Do not force cold brass into plastic, screw into hot brass, or use the screw as an insertion press. Allow complete cooling before assembly. Stop if plastic distorts or the insert tilts/spins.

Adafruit recommends a heat-set installation tip for alignment: https://www.adafruit.com/product/4255 . The 3.9 mm pilot is a starting fit, not a validated hole for every printer/PETG combination. Trial on the small sample. Do not change the scale of the complete part to alter one hole.

Join the empty layers with the M3 × 8 screws from above, threading them gently into the cooled inserts. Snug only until seated; no loose nuts. Check for rocking, insert rotation, cracks, and screw binding. Then dry-fit real switches, caps, insulated LEDs and leads. Support the tray as you undo its screws. For service, lift the top/tray assembly clear of the case before separating if wiring access requires it.

## Geometry / verification

The upper plate is z22–25; posts meet its underside at z22. Inserts sit flush at z22 and extend to z18 (4 mm length). An 8 mm screw through the 3 mm plate reaches z17: full nominal 4 mm insert engagement plus 1 mm into the relief well. The well floor is z16, leaving 1 mm nominal tip clearance. Screw tips stay entirely inside the posts, 7 mm above the tray bottom.

Each post is 8 mm OD. Nominal radial plastic outside the 4.2 mm insert is 1.9 mm. Printed pilot: 3.9 mm diameter × 4.3 mm depth; 3.4 mm screw-tip relief below, ending at z16. Heat-setting intentionally displaces the pilot wall. CAD collision tests use the installed/melted insert envelope instead of treating that interference as a fault. Heat creep, knurl grip and pullout strength require a physical test.

Mount centers (-16,41.5), (16,41.5), (-41.5,9.525), (41.5,9.525) mm are unchanged. Tray floor z10, LED pockets z10.8. A 0.2 mm insulating adhesive layer plus a 3.1 mm LED yields top z14.1, nominally 0.8 mm below the switch pin envelope. Controller top reference z8.9 gives 1.1 mm tray clearance. Actual wires/solder/component heights still need checking.

LED pockets locate but do not clamp boards; thin removable insulating adhesive remains necessary for LED retention. LED leads use floor slots; matrix leads use wall notches. Leave about 20 mm lowering travel in the wires and keep all metal pads isolated. No hot-swap or electrical disconnect is added.

`build.py` exports four single-solid watertight printable meshes, checks screw/insert fit, nominal engagement, tip clearance, insertion-tip access, case and electronics envelopes, and tray removal past switches. It does not validate real soldering or physical strength. STEP uses assembled coordinates; STL is print-oriented. Reference assembly is not printable. Viewer and preview use the same CAD.

Run `python build.py` with Python 3.12 and `requirements.txt`. Test both the baffle sample and joystick sample before the full plate. The older main keyboard animation remains a legacy illustration. See this folder's interactive guide for v3.
