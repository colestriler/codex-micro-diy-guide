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

keyboard = Keyboard(usb_hid.devices, timeout=10)
button = keypad.Keys((board.A2,), value_when_pressed=False, pull=True,
                     interval=0.01, debounce_threshold=3)
time.sleep(0.2)
held = False
event = button.events.get()
while event is not None:
    held = event.pressed
    event = button.events.get()
print("BUTTON READY: press the knob to type a")
try:
    while True:
        event = button.events.get()
        while event is not None:
            if event.pressed and not held:
                keyboard.send(Keycode.A)
                print("PRESS: a")
            held = event.pressed
            event = button.events.get()
        time.sleep(0.005)
finally:
    keyboard.release_all()
    button.deinit()
