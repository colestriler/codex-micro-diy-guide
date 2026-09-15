"""Codex Micro staged bench test - CircuitPython on Adafruit KB2040.
Install lib/adafruit_hid. Back up your current code.py before replacing it.
Unplug USB before changing wiring. No matrix or joystick needed for this test.
"""
import time
import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

import rotaryio

# If right types l (or decreases reasoning), toggle this and save.
# Keep the value calibrated for YOUR TX/RX wiring when changing tests.
REVERSE_ROTATION = True
encoder = rotaryio.IncrementalEncoder(board.TX, board.RX, divisor=4)
keyboard = Keyboard(usb_hid.devices, timeout=10)
button = keypad.Keys((board.A2,), value_when_pressed=False, pull=True,
                     interval=0.01, debounce_threshold=3)
time.sleep(0.2)
held = False
event = button.events.get()
while event is not None:
    held = event.pressed
    event = button.events.get()
last_position = encoder.position
# One external Adafruit 4776 RGBW LED via SN74AHCT125 and 330-ohm resistor.
# Also install lib/neopixel.py and lib/adafruit_pixelbuf.py.
import neopixel
pixels = neopixel.NeoPixel(board.MOSI, 1, bpp=4, pixel_order=neopixel.GRBW,
                          brightness=0.08, auto_write=False)
time.sleep(0.1)
pixels[0] = (255, 20, 80, 0)
pixels.show()
print("LED TEST: dim pink sent on MO; confirm the external light visually")
print("KNOB READY: button types a")
try:
    while True:
        event = button.events.get()
        while event is not None:
            if event.pressed and not held:
                keyboard.send(Keycode.A)
                print("PRESS: a")
            held = event.pressed
            event = button.events.get()
        position = encoder.position
        delta = position - last_position
        last_position = position
        if REVERSE_ROTATION:
            delta = -delta
        if delta:
            key = Keycode.R if delta > 0 else Keycode.L
            for _ in range(min(abs(delta), 10)):
                keyboard.send(key)
                time.sleep(0.03)
            print("TURN:", delta)
        time.sleep(0.005)
finally:
    keyboard.release_all()
    button.deinit()
    encoder.deinit()
    pixels.deinit()
