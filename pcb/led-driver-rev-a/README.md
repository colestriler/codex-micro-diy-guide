# Codex Micro LED Driver — Rev A prototype

This 36 × 30 mm board replaces the hand-built perfboard section only. JLCPCB
can assemble the level shifter, 330 Ω resistor, 100 nF bypass capacitor,
100 µF bulk capacitor, and two right-angle JST XH connectors.

The connections are deliberately identical at both ends:

| Pin | KB2040 connector J1 | LED connector J2 |
| --- | --- | --- |
| 1 | `+5V` from `RAW` | `+5V` |
| 2 | data from `MO` / `MOSI` | `DIN` through the buffer and 330 Ω resistor |
| 3 | `GND` | `GND` |

The board does not contain the KB2040, key switches, diodes, encoder,
joystick, touch circuit, or RGBW LED boards. Matching three-wire JST XH cable
assemblies are still required. One cable's free end connects to KB2040
`RAW`, `MO`, and `GND`; the other connects to the first LED's `5V`, `DIN`,
and `GND` pads.

## Before ordering

This is an unbuilt first revision. Confirm that the existing single-LED
perfboard circuit lights successfully, then compare JLCPCB's component preview
against `board-top.png`: U1 pin 1 and C2 positive must match the board markers.
Order the smallest prototype quantity first. Inspect the board and test it with
one dim LED before connecting the complete chain.

The 100 µF capacitor matches the current prototype BOM. The finished 14-pixel
chain still needs a measured current and USB-power check. Firmware should keep
brightness limited during initial tests.

## Manufacturing files

- `Codex-Micro-LED-Driver-Rev-A-JLCPCB.zip`: Gerbers, BOM and CPL.
- `manufacturing/gerbers-jlcpcb.zip`: bare-board fabrication archive.
- `bom-jlcpcb.csv`: exact LCSC choices, including SMT/THT classification.
- `cpl-jlcpcb.csv`: placement coordinates in millimetres.
- `codex-micro-led-driver.kicad_pcb`: editable KiCad source.
- `drc-report.txt`: KiCad design-rule results.
- `design-summary.json`: scope and remaining physical checks.

The assembly BOM includes two through-hole JST XH connectors, so choose mixed
SMT + THT assembly if JLCPCB recognizes those parts. Do not silently omit J1 or
J2 if the assembly quote cannot place them.
