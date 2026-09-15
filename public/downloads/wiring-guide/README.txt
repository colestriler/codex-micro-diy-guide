CODEX MICRO - START WITH ONE CIRCUIT AT A TIME

1. Install CircuitPython for Adafruit KB2040. This guide targets CircuitPython 10.x.
2. Copy the contents of lib into CIRCUITPY/lib. These are Python-source libraries.
3. Back up the code.py already on your board to your computer.
4. Choose ONE file from firmware, copy it to CIRCUITPY and name it code.py.

button-test.py: button on A2/G types a. No rotation wires needed yet.
knob-test.py: TX/RX rotation types r/l; button still types a.
led-test.py: same knob test + ONE RGBW LED on MO at 8% brightness.
reasoning-knob.py: optional app shortcut example; does not drive the LED.

Changing code.py replaces the previous program. Copy your calibrated
REVERSE_ROTATION value into each new knob test. The reasoning example sends
Ctrl+Option+Command+Up/Down, but the app or OS must bind these shortcuts.
It does not read the app's reasoning level or create missing app commands.

The one-LED program uses the same MO/RGBW/8% LED configuration as our bench
program. A program running successfully is not proof of physical LED operation.
There is no automatic native Codex integration.

Follow https://codexmicro.diy/#wiring for wiring, checkpoints and the PDF.
Unplug USB before soldering or moving wires. Do not change the RAW bypass jumper.
The final 14-LED build requires a separate current-budget and power review.

Adafruit library licenses are in licenses; exact sources are in library-sources.json.
