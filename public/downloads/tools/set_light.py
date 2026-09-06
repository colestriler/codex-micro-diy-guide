"""Set a DIY Micro LED via its USB data port. Requires: pip install pyserial.
Example: python tools/set_light.py /dev/cu.usbmodemXXXX 0 0 120 255
List ports: python -m serial.tools.list_ports
Choose the second/data port, not the CircuitPython REPL port.
"""
import argparse,json,time
import serial
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('port');p.add_argument('led',type=int,choices=range(14))
for name in ('red','green','blue'):p.add_argument(name,type=int,choices=range(256))
a=p.parse_args()
with serial.Serial(a.port,115200,timeout=1) as s:
    time.sleep(.2)
    s.write((json.dumps({'led':a.led,'rgb':[a.red,a.green,a.blue]})+'\n').encode())
    s.flush()
print('Color command sent. Verify the physical LED; this script is not a Codex bridge.')
