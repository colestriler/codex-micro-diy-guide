"""DIY Micro Rev A / KB2040 / CircuitPython. Hardware prototype, not OEM firmware.
Default keys are F13..F24; joystick sends arrows; dial scrolls.
Install lib/adafruit_hid, neopixel.mpy and adafruit_pixelbuf.mpy.
The USB data port accepts a newline-delimited JSON color command:
  {"led":0,"rgb":[0,120,255]}
It does NOT read Codex task state automatically.
"""
import time, json
import board, keypad, digitalio, analogio, rotaryio, touchio
import usb_hid, usb_cdc, neopixel
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from logic import KeyState, direction, rgbw

matrix=keypad.KeyMatrix(row_pins=(board.D2,board.D3,board.D4,board.D5),
    column_pins=(board.D6,board.D7,board.D8,board.D9),
    columns_to_anodes=True,interval=.005,debounce_threshold=3)
encoder=rotaryio.IncrementalEncoder(board.TX,board.RX)
encoder_button=keypad.Keys((board.A2,),value_when_pressed=False,pull=True,
    interval=.005,debounce_threshold=3)
joy_x=analogio.AnalogIn(board.A0); joy_y=analogio.AnalogIn(board.A1)
touch=touchio.TouchIn(board.D10)  # 1 MOhm external pulldown REQUIRED
pixels=neopixel.NeoPixel(board.MOSI,14,brightness=.15,auto_write=False,
    pixel_order=neopixel.GRBW)
indicators=[]
for pin in (board.SCK,board.MISO,board.A3):
    d=digitalio.DigitalInOut(pin);d.switch_to_output(value=False);indicators.append(d)
kbd=Keyboard(usb_hid.devices);mouse=Mouse(usb_hid.devices)
keys=KeyState()
# Three banks retain identical F13-F24 usages but add modifiers to banks 2/3.
# Configure them in your OS shortcut app, or edit these mappings.
FUNCTION_KEYS=[getattr(Keycode,'F'+str(i)) for i in range(13,25)]
MODIFIERS=[(),(Keycode.LEFT_SHIFT,),(Keycode.LEFT_CONTROL,)]
ARROWS={'left':Keycode.LEFT_ARROW,'right':Keycode.RIGHT_ARROW,
        'up':Keycode.UP_ARROW,'down':Keycode.DOWN_ARROW}
active_chords={};held_usages=set();layer=0
# Sample at rest. Do not touch the stick while connecting USB.
sx=sy=0
for _ in range(32):
    sx+=joy_x.value;sy+=joy_y.value;time.sleep(.005)
center=(sx//32,sy//32)
last_direction=None;last_touch=False;touch_time=0;last_position=encoder.position
serial=usb_cdc.data;buffer=bytearray()

def sync_keyboard():
    desired=set()
    for chord in active_chords.values():desired.update(chord)
    for key in held_usages-desired:kbd.release(key)
    for key in desired-held_usages:kbd.press(key)
    held_usages.clear();held_usages.update(desired)

def set_layer(value):
    global layer
    layer=value%3
    for i,led in enumerate(indicators):led.value=(i==layer)
    # This is bank feedback; these colors do not represent agent status.
    colors=((0,30,55,0),(35,0,40,0),(30,25,0,0))
    pixels.fill(colors[layer]);pixels.show()

def serial_command(line):
    try:
        data=json.loads(line)
        index=data['led']
        if not isinstance(index,int) or not 0<=index<14:raise ValueError('LED index 0..13')
        pixels[index]=rgbw(data['rgb']);pixels.show()
    except (ValueError,KeyError,TypeError) as exc:
        print('Color command ignored:',exc)

set_layer(0)
try:
    while True:
        changed=False
        event=matrix.events.get()
        while event:
            transition=keys.update(event.key_number,event.pressed)
            if transition:
                logical,down=transition
                if down:active_chords[logical]=MODIFIERS[layer]+(FUNCTION_KEYS[logical],)
                else:active_chords.pop(logical,None)
                changed=True
            event=matrix.events.get()
        if matrix.events.overflowed:
            keys=KeyState();active_chords.clear();matrix.events.clear();matrix.reset();changed=True
        event=encoder_button.events.get()
        while event:
            if event.pressed:active_chords['dial']=(Keycode.ENTER,)
            else:active_chords.pop('dial',None)
            changed=True;event=encoder_button.events.get()
        position=encoder.position;delta=position-last_position
        if delta:mouse.move(wheel=max(-10,min(10,delta)));last_position=position
        # First prototype defaults to normal arrow keys. Reverse Y here if required.
        new_direction=direction(joy_x.value,joy_y.value,center,last_direction)
        if new_direction!=last_direction:
            if new_direction:active_chords['joy']=(ARROWS[new_direction],)
            else:active_chords.pop('joy',None)
            changed=True;last_direction=new_direction
        touched=touch.value;now=time.monotonic()
        if touched and not last_touch and now-touch_time>.4:
            set_layer(layer+1);touch_time=now
        last_touch=touched
        if changed:sync_keyboard()
        if serial and serial.connected and serial.in_waiting:
            chunk=serial.read(min(serial.in_waiting,128))
            if chunk:buffer.extend(chunk)
            while b'\n' in buffer:
                line,_,rest=buffer.partition(b'\n');buffer=bytearray(rest)
                serial_command(line)
            if len(buffer)>512:buffer.clear()
        time.sleep(.002)
finally:
    kbd.release_all();pixels.fill((0,0,0,0));pixels.show()
