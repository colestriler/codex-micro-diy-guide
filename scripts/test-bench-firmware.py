"""Exercise downloadable stages with simulated button/encoder/LED hardware, not a physical device."""
from pathlib import Path
import ast, sys, types, zipfile

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'public/downloads/wiring-guide'
class Finished(BaseException):pass
for name in ['button-test.py','knob-test.py','led-test.py','reasoning-knob.py']:
    sends=[]; pixels=[]; sleeps=[0]; events=iter([None,types.SimpleNamespace(pressed=True),None,types.SimpleNamespace(pressed=True),None,types.SimpleNamespace(pressed=False),None])
    def sleep(t):
        if t==.005:
            sleeps[0]+=1
            if sleeps[0]>=4:raise Finished()
    class Keyboard:
        def __init__(self,*a,**kw):pass
        def send(self,*args):sends.append(args)
        def release_all(self):pass
    class Button:
        def __init__(self,*a,**kw):self.events=types.SimpleNamespace(get=lambda:next(events,None))
        def deinit(self):pass
    class Encoder:
        def __init__(self,*a,**kw):self.positions=iter([0,1,0,0,0])
        @property
        def position(self):return next(self.positions,0)
        def deinit(self):pass
    class Pixel:
        def __init__(self,*a,**kw):pixels.append(('init',a,kw))
        def __setitem__(self,i,v):pixels.append(('color',i,v))
        def show(self):pixels.append(('show',))
        def deinit(self):pass
    keycode=types.SimpleNamespace(**{k:k for k in ['A','R','L','UP_ARROW','DOWN_ARROW','CONTROL','ALT','GUI']})
    modules={
     'time':types.SimpleNamespace(sleep=sleep),
     'board':types.SimpleNamespace(A2='A2',TX='TX',RX='RX',MOSI='MOSI'),
     'keypad':types.SimpleNamespace(Keys=Button),
     'rotaryio':types.SimpleNamespace(IncrementalEncoder=Encoder),
     'usb_hid':types.SimpleNamespace(devices=[]),
     'adafruit_hid':types.ModuleType('adafruit_hid'),
     'adafruit_hid.keyboard':types.SimpleNamespace(Keyboard=Keyboard),
     'adafruit_hid.keycode':types.SimpleNamespace(Keycode=keycode),
     'neopixel':types.SimpleNamespace(NeoPixel=Pixel,GRBW='GRBW')
    }
    old={k:sys.modules.get(k) for k in modules};sys.modules.update(modules)
    try:
        code=(DIR/'firmware'/name).read_text();ast.parse(code)
        try:exec(compile(code,name,'exec'),{})
        except Finished:pass
    finally:
        for k,v in old.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    assert sends.count(('A',))==1,(name,'held button repeated',sends)
    if name in ['knob-test.py','led-test.py']:assert ('L',) in sends and ('R',) in sends
    if name=='reasoning-knob.py':
        assert ('CONTROL','ALT','GUI','UP_ARROW') in sends and ('CONTROL','ALT','GUI','DOWN_ARROW') in sends
    if name=='led-test.py':
        assert pixels[0]==('init',('MOSI',1),dict(bpp=4,pixel_order='GRBW',brightness=.08,auto_write=False))
        assert ('color',0,(255,20,80,0)) in pixels and ('show',) in pixels
    else:assert not pixels
    print('PASS',name)
with zipfile.ZipFile(DIR/'wiring-starter.zip') as z:
    assert z.testzip() is None
    for file in ['firmware/button-test.py','firmware/knob-test.py','firmware/led-test.py','lib/adafruit_hid/keyboard.py','lib/neopixel.py','lib/adafruit_pixelbuf.py','README.txt']:
        assert z.read(file)==(DIR/file).read_bytes(),file
print('Starter ZIP contents match published files')
