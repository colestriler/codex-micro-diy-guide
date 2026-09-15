# Snap-on light baffle — first fit test

Print **two small pieces, one of each**:

1. `files/PRINT_ONE_test_plate_with_clips.stl`
2. `files/PRINT_ONE_snap_baffle.stl`

The plate sample includes both flexible clips; there are no separate clips to print. No glue, screws, nuts or new electronics are required for this test. The old glue-mounted cup and old top plate do not have these matching features.

## Why the clips are on the plate

The existing cups are 18.7 mm across on 19.05 mm key centers: only 0.35 mm separates neighboring cups. Side release tabs would be difficult to reach. This design puts two flexible arms on the underside of the plate. They pass through windows in the cup floor, and their hooked ends are accessible underneath. Pinch the two ends toward one another and lower the cup. The clips are integral to the plate, so a broken clip would require a plate repair/reprint; test them on this inexpensive coupon first.

The baffle rim still meets the underside of the plate. Two 0.8 mm thick beams extend down beside the switch and LED; their hooks latch under the cup floor. Nominal retaining overlap is 0.35 mm, axial clearance is 0.1 mm, and the target release movement is about 0.5 mm per tip. Do not treat those as measured print tolerances. Keep the two clip channels clear of solder, diode leads and wires.

## Printing the two small samples

- Use PETG for the plate/clip sample. White matches the full plate; clear is also suitable for the mechanical test. Use black PETG for the cup so it blocks light. These are not TPU designs; PLA is not the recommended clip-test material.
- Print at 100% scale in millimeters, with a 0.4 mm nozzle, 0.10 mm layers, four walls and 100% infill for the small samples. Use your printer's existing PETG temperature/cooling profile.
- Keep the supplied STL orientations: plate's visible face on the bed, clips standing upward; cup flat bottom on the bed, cavity upward.
- Start with supports OFF for these two small samples. The plate's MX clip lands bridge/cantilever only a short distance; the hook has a short ramp and a 0.35 mm retaining ledge. Inspect the sliced preview: each 0.8 mm beam must have continuous extrusion paths and each hook must exist. If your slicer omits a beam or a hook prints poorly, stop and report it instead of forcing the joint.
- Leave the parts to cool before removing them from the bed. Clean strings from the floor windows; do not sand away the retaining lips or bend the long clips sideways while cleaning.

## Test empty first

1. Keep USB disconnected. Do not install or solder the switch or LED yet.
2. Hold the plate sample with its two clips pointing down. Orient the cup open side up. The two narrow floor windows line up with the clips; the larger wire notches are on the other pair of walls.
3. Slide the cup upward gently so the clips enter those windows. You can gently pinch the tips as they emerge below the cup to help them through. Stop if the arms buckle, a hook catches sideways or the cup needs force.
4. Release both clips. Their hooks should catch the underside of the floor when the cup rim reaches the plate. Check that both hooks have emerged and the cup stays attached under its own weight.
5. Pinch both exposed ends toward the center and lower the cup. Press the plastic tips, not the wires or switch. The cup should release without prying its rim away from the plate.
6. Repeat about ten gentle attach/release cycles. Stop for whitening, cracking, permanent bending, excessive looseness or difficult access. This is a fit and usability test, not a validated fatigue rating. Send photos if either clip fails to engage or release.

## Then dry-fit the real components

After the empty mechanism works, clip one real switch into the sample from above. Its own retention tabs must latch normally without touching the added clips. Confirm full key travel. Try the removable cup again.

Place one **unpowered** Adafruit 4776 board in the cup, LED facing the switch, with an insulating layer beneath its pads. Check for clearance from the switch's plastic pegs, metal pins and future solder joints. The CAD uses simplified keepout envelopes, not an exact Gateron switch model; your dry fit is required.

The cup is mechanically removable, but a wired LED remains connected. Leave a service loop long enough to lower the cup clear of the switch (start by checking a 20 mm drop on the bench), route wires through the open notches, and keep them away from both latch channels. Never pull on solder joints. Full electrical disconnection would need a connector and is not included in this revision.

Do not wire all six cups until the print fit, switch fit and one powered LED light-leak test have passed. Some leakage through the service openings is possible and needs a real LED test.

## Full plate: wait

`files/WAIT_full_plate_flat_joystick_and_baffle_clips.stl` combines the latest flat joystick mount v3 with twelve clips for the six agent-key cups. It preserves the other original switch holes and case attachment geometry. It is provided for CAD review and later printing only.

**Printing the full plate differs from printing the small coupon.** The supplied full-plate STL is face down with clips pointing up. The joystick's raised supports project on the bed side, so support is needed beneath the raised-off-bed plate face as well as any unsupported local features. Do not reuse the v3 corner's supports-OFF instruction for this full plate. Review the entire layer preview and support interface before printing; this orientation/support strategy is not physically validated. Both joystick and baffle samples must pass first.

The site's original full-keyboard animation still shows the earlier adhesive cups. Use this kit's preview and `reference_fit_assembly_NOT_PRINTABLE.step` for the new clip mechanism. The STEP assembly includes simplified reference blocks that are not printable parts.

## Validation and source

The three print meshes are watertight and single connected solids. The seated cup has no nominal overlap with the plate/clips. A downward pull without releasing the clips produces positive latch interference. All six cups and the candidate plate clear the original case geometry and one another. Simplified lower-switch, pin and LED envelopes clear the cup and clips.

A cantilever calculation estimates approximately 0.36% surface strain at the modeled release movement. It does not account for FDM layer adhesion, local stress concentration, material creep, actual print dimensions or repeated cycles. It is not FEA or a strength guarantee. Release travel is checked geometrically against conservative keepouts; insertion/release motion has not been experimentally measured. See `validation.json` for limits.

Rebuild with Python 3.12: install `requirements.txt` in a virtual environment, then run `python build.py`. Inputs under `references/` are existing project STEP files, not extra prints.

Design references:
- [Formlabs snap-fit design guide](https://formlabs.com/blog/designing-3d-printed-snap-fit-enclosures/) — cantilever and strain principles; not PETG FDM fit validation.
- [Gateron North Pole Yellow 2.0 specification](https://gateron.com/u_file/2311/22/file/GATERONNewNorthPole20yellow-KS-7Y10B050NW-Y39.pdf) — exact switch identification; actual retention tabs and pins still require a trial fit.
- [Adafruit 4776](https://www.adafruit.com/product/4776) — LED board used by this project.
