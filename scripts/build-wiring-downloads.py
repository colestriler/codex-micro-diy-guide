"""Package staged CircuitPython programs and pinned, MIT-licensed Adafruit libraries."""
from pathlib import Path
import ast, hashlib, json, urllib.request, zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/downloads/wiring-guide'
(OUT/'firmware').mkdir(parents=True,exist_ok=True)
(OUT/'lib/adafruit_hid').mkdir(parents=True,exist_ok=True)
(OUT/'licenses').mkdir(exist_ok=True)
HEADER='''"""Codex Micro staged bench test - CircuitPython on Adafruit KB2040.
Install lib/adafruit_hid. Back up your current code.py before replacing it.
Unplug USB before changing wiring. No matrix or joystick needed for this test.
"""
import time
import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

'''
INIT='''keyboard = Keyboard(usb_hid.devices, timeout=10)
button = keypad.Keys((board.A2,), value_when_pressed=False, pull=True,
                     interval=0.01, debounce_threshold=3)
time.sleep(0.2)
held = False
event = button.events.get()
while event is not None:
    held = event.pressed
    event = button.events.get()
'''
EVENT='''        event = button.events.get()
        while event is not None:
            if event.pressed and not held:
                keyboard.send(Keycode.A)
                print("PRESS: a")
            held = event.pressed
            event = button.events.get()
'''
button=HEADER+INIT+'''print("BUTTON READY: press the knob to type a")
try:
    while True:
'''+EVENT+'''        time.sleep(0.005)
finally:
    keyboard.release_all()
    button.deinit()
'''
(OUT/'firmware/button-test.py').write_text(button)
for name,led,reasoning in [('knob-test.py',False,False),('led-test.py',True,False),('reasoning-knob.py',False,True)]:
    text=HEADER+'''import rotaryio

# If right types l (or decreases reasoning), toggle this and save.
# Keep the value calibrated for YOUR TX/RX wiring when changing tests.
REVERSE_ROTATION = True
encoder = rotaryio.IncrementalEncoder(board.TX, board.RX, divisor=4)
'''+INIT+'''last_position = encoder.position
'''
    if led:
        text+='''# One external Adafruit 4776 RGBW LED via SN74AHCT125 and 330-ohm resistor.
# Also install lib/neopixel.py and lib/adafruit_pixelbuf.py.
import neopixel
pixels = neopixel.NeoPixel(board.MOSI, 1, bpp=4, pixel_order=neopixel.GRBW,
                          brightness=0.08, auto_write=False)
time.sleep(0.1)
pixels[0] = (255, 20, 80, 0)
pixels.show()
print("LED TEST: dim pink sent on MO; confirm the external light visually")
'''
    text+='''print("KNOB READY: button types a")
try:
    while True:
'''+EVENT+'''        position = encoder.position
        delta = position - last_position
        last_position = position
        if REVERSE_ROTATION:
            delta = -delta
        if delta:
'''
    if reasoning:
        text+='''            # The target app/OS must bind these shortcuts to real commands.
            # This firmware cannot read or create a reasoning-level command.
            key = Keycode.UP_ARROW if delta > 0 else Keycode.DOWN_ARROW
            for _ in range(min(abs(delta), 10)):
                keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.GUI, key)
                time.sleep(0.08)
'''
    else:
        text+='''            key = Keycode.R if delta > 0 else Keycode.L
            for _ in range(min(abs(delta), 10)):
                keyboard.send(key)
                time.sleep(0.03)
'''
    text+='''            print("TURN:", delta)
        time.sleep(0.005)
finally:
    keyboard.release_all()
    button.deinit()
    encoder.deinit()
'''
    if led: text+='    pixels.deinit()\n'
    ast.parse(text)
    (OUT/'firmware'/name).write_text(text)

sources=[]
for repo,files in [
 ('Adafruit_CircuitPython_HID',['adafruit_hid/__init__.py','adafruit_hid/keyboard.py','adafruit_hid/keycode.py']),
 ('Adafruit_CircuitPython_NeoPixel',['neopixel.py']),
 ('Adafruit_CircuitPython_Pixelbuf',['adafruit_pixelbuf.py'])
]:
    request=urllib.request.Request(f'https://api.github.com/repos/adafruit/{repo}/commits/main',headers={'User-Agent':'codex-micro-guide'})
    sha=json.load(urllib.request.urlopen(request))['sha']
    for name in files+['LICENSE']:
        url=f'https://raw.githubusercontent.com/adafruit/{repo}/{sha}/{name}'
        content=urllib.request.urlopen(url).read()
        dest=OUT/('licenses/'+repo+'.txt' if name=='LICENSE' else 'lib/'+name)
        dest.write_bytes(content)
        if name.endswith('.py'): ast.parse(content)
        sources.append(dict(path=str(dest.relative_to(OUT)),url=url,sha256=hashlib.sha256(content).hexdigest()))
(OUT/'library-sources.json').write_text(json.dumps(sources,indent=2)+'\n')
(OUT/'README.txt').write_text('''CODEX MICRO - START WITH ONE CIRCUIT AT A TIME

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
''')
with zipfile.ZipFile(OUT/'wiring-starter.zip','w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.rglob('*')):
        if file.is_file() and (file.parts[-2]=='firmware' or 'lib' in file.parts or file.parts[-2]=='licenses' or file.name in ['README.txt','library-sources.json']):
            z.write(file,str(file.relative_to(OUT)))
print('Staged tests and licensed starter ZIP ready')
