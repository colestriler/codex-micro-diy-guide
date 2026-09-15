# Flat joystick mount — v3

Print **only `files/PRINT_FIRST_flat_joystick_corner_v3.stl`** first. It is one piece with a flat 3 mm base and two raised mounting-tab seats. There are no nut boxes, underside bosses, deep recesses or separate shims.

The 28.7 × 28.7 mm test corner is cropped from the same solid as the candidate full top plate. The full plate is 94 × 94 mm with a 3 mm main thickness. The two local seats rise 0.5 mm (A) and 1.0 mm (B) above the top face. Their heights reproduce the v1 starting shims, not new measurements of your joystick.

## Print this corner

- One STL at 100% scale, units millimeters.
- Keep the supplied orientation: **flat underside on the bed, raised supports facing UP**.
- Existing PETG, any color. 0.4 mm nozzle, 0.10 mm layers, four walls, 100% infill for this small test.
- **Supports OFF for the test corner.** It has a flat underside and straight through-holes. A brim is optional if you need help with bed adhesion.
- Clean strings from the holes without changing the support heights. No support material should need removing from a body recess or nut tunnel because neither exists in v3.

## Attachment

Screw head → joystick mounting tab → raised support → plate → exposed nut underneath.

The stationary body rests directly on the flat top. The screws hold the two supported ears down. Each nut bears against the flat underside. Hold the nut with small pliers while turning the screw from above. Keep the pliers on the metal nut, not the joystick or its wiring. Use gentle tightening; don't bend a tab or crush the plastic.

The joystick ears face the outer edge of the plate. The four solder pads face the neighboring key row and sit over the rectangular wire opening. Seat B is the one nearest the larger case-screw hole. Do not use v1/v2 orientation or wiring photos to infer pad order: verify the actual component labels and supplier orientation before soldering.

## Hardware — same sizes

- Two M1.6 × 8 mm DIN 912 socket-head screws, 0.35 mm pitch, 3 mm head diameter, 1.6 mm head height: [supplier specifications](https://www.accu.co.uk/metric-cap-head-screws/3784-SSCF-M1-6-8-A2).
- Two M1.6 DIN 934 nuts, 3.2 mm across flats, 1.3 mm thick: [supplier specifications](https://www.accu.co.uk/hexagon-nuts/7882-HPN-M1-6-A2).
- 1.5 mm hex key and small pliers to hold the exposed nuts.

Your existing 8 mm screws fit the modeled stack and fully engage the nuts. Their ends extend approximately 1.2 mm (A) and 1.7 mm (B) past the nuts. CAD checks show clearance from the original case; keep the exposed tips clear of real wires. No new screw size, washers or electronics are specified. Supplier stock is not verified.

## Fit check

1. Unplug the KB2040. Dry-fit the joystick on the loose test corner before using screws. The body should sit flat and both ears should touch their raised seats. No loose shims. If there is rocking or a gap, stop and report it instead of using screw force to close it.
2. Insert the two screws through the joystick ears and supports. Start each nut by hand underneath. Hold the nut with pliers and gently tighten from above. Check that both nuts sit flat and the fixed joystick housing does not shift, lift or rock.
3. Move the thumb cap fully in every direction and diagonally. Check clearance from the screw heads, supports and plate. The CAD joystick reference does not reproduce the exact textured thumb cap, so this real movement check is required.
4. Remove the old full top plate and rest the test corner on the bare case ledge, aligned with the rounded outer corner and larger M3 case hole. It replaces that area of the plate; it is not an insert for the old recess. Check that both nuts and screw tips clear the case post and wiring. Fit the nuts while the plate is off the case, where they are accessible.
5. Share a top and side photo and report any gap, wobble, binding or case interference before printing the full plate.

## Candidate full plate

`WAIT_flat_top_plate_v3.stl` is included for inspection and later printing. Wait until the corner passes. The joystick area uses the same flat design. Other switch, encoder, touch, indicator and M3 case-hole geometry is preserved from the original plate.

The full STL is also face UP. Unlike the small corner, the full plate includes the original underside MX clip reliefs: inspect those small overhangs in the slicer and add localized support if required. Support-free guidance above applies specifically to the test corner. After printing the full plate, dry-fit the actual neighboring switches and caps and check their full travel before assembly.

The full-keyboard animation and original `downloads/step/assembly.step` remain legacy geometry. Use this kit's preview and `reference-assembly_NOT_FOR_PRINTING.step` for the v3 mount. Reference STEP files and the assembly are not additional prints.

## CAD verification and source

Both exported print meshes are watertight, single connected volumes, placed on Z=0. Automated CAD checks cover reference-joystick interference, original-case interference, screw shaft clearance at both documented hole layouts, hardware clearance, nominal adjacent keycaps and flat nut-bearing surfaces. The mount adds no plastic below the original plate underside. `validation.json` records these checks and the limits. These are geometry checks, not physical fit, stiffness, durability or printer validation.

Install `requirements.txt` in a Python 3.12 virtual environment, then run `python build.py`. `parameters.json` exposes the joystick center, support heights and 2.4 mm screw-clearance holes. The holes accommodate the small discrepancy between the two source mounting layouts; printed fit still needs checking.

Exact-SKU footprint: [SparkFun-Switches.lbr](https://github.com/sparkfun/SparkFun-Eagle-Libraries/blob/main/SparkFun-Switches.lbr), JOYSTICK-PSP1000, COM-09426. Community reference: [marbastlib PNT_psp1000](https://github.com/ebastler/marbastlib/blob/6b0a9a73f579e377816d60b58eac2b3252de7868/3dmodels/PNT_psp1000.step), credited to Hendrik Roth, rotated and translated in the assembly. Its CERN-OHL-P-2.0 license is included. Neither source is a measurement of your exact part.
