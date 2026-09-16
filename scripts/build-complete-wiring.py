"""Reproducible monochrome wiring poster, sourced from the guide's validated netlists."""
from pathlib import Path
import json, html, math, shutil
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/downloads/wiring-guide'
(ROOT/'tmp/pdfs').mkdir(parents=True,exist_ok=True)
WIRING=json.loads((ROOT/'data/wiring.json').read_text())
PERF=json.loads((OUT/'connections.json').read_text())
W,H=3000,2200

class SVG:
 def __init__(self,title):
  self.texts=[]
  self.boxes=[]
  self.e=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{html.escape(title)}</title>', '<rect width="3000" height="2200" fill="white"/>']
 def add(self,s):self.e.append(s)
 def text(self,x,y,s,size=23,bold=False,anchor='start',halo=False):
  attrs=''
  width=stringWidth(str(s),'Helvetica-Bold' if bold else 'Helvetica',size)
  left=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
  self.boxes.append((left,y-size*.8,left+width,y+size*.2,str(s)))
  self.texts.append(f'<rect x="{left-2}" y="{y-size*.8}" width="{width+4}" height="{size}" fill="white"/>')
  self.texts.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="black"{attrs}>{html.escape(str(s))}</text>')
 def rect(self,x,y,w,h,r=0,fill='white',stroke='black',sw=2,dash=None):
  ds=f' stroke-dasharray="{dash}"' if dash else ''
  self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}/>')
 def circle(self,x,y,r,fill='white',sw=2):self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="black" stroke-width="{sw}"/>')
 def path(self,d,sw=3,dash=None,halo=True):
  ds=f' stroke-dasharray="{dash}"' if dash else ''
  if halo:self.add(f'<path d="{d}" fill="none" stroke="white" stroke-width="{sw+7}" stroke-linecap="round" stroke-linejoin="round"/>')
  self.add(f'<path d="{d}" fill="none" stroke="black" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{ds}/>')
 def wire(self,pts,sw=3,dash=None,halo=True):self.path('M'+' L'.join(f'{x},{y}' for x,y in pts),sw,dash,halo)
 def dot(self,x,y,r=5):self.circle(x,y,r,'black',1)
 def terminal(self,x,y):self.circle(x,y,6,'white',2)
 def label(self,x,y,s,size=21):
  # White backing keeps route names legible at crossings, including in PDF renderers.
  width=len(s)*size*.55+14
  self.rect(x-7,y-size,width,size+7,3,stroke='none')
  self.text(x,y,s,size)
 def arrow(self,x,y,dx=1,dy=0):
  self.wire([(x-dx*12-dy*6,y-dy*12+dx*6),(x,y),(x-dx*12+dy*6,y-dy*12-dx*6)],2,halo=False)
 def resistor(self,x1,y1,x2,y2,label=None):
  self.wire([(x1,y1),(x2,y2)])
  mx,my=(x1+x2)/2,(y1+y2)/2
  if x1==x2:self.rect(mx-12,my-34,24,68,4)
  else:self.rect(mx-34,my-12,68,24,4)
  if label:self.text(mx+20,my+7,label,21)
 def save(self,name):
  (ROOT/'tmp/pdfs'/f'{name}.labels.json').write_text(json.dumps(self.boxes))
  p=OUT/name;p.write_text('\n'.join(self.e+self.texts)+ '\n</svg>');return p

def header(s,n,title,subtitle):
 s.text(70,77,'CODEX MICRO',25,True)
 s.text(70,132,title,52,True)
 s.text(70,176,subtitle,23)
 s.text(2925,78,f'{n} / 2',27,True,'end')
 s.wire([(70,205),(2930,205)],2,halo=False)
def footer(s,msg):
 s.wire([(70,2113),(2930,2113)],2,halo=False)
 s.text(70,2152,msg,21)
 s.text(2930,2152,'Complete intended wiring | 15 Sep 2026 | rev 1',20,False,'end')
 s.text(70,2185,'Matches the website firmware and bench perfboard map. Component positions are spread out for clarity; this is not a case-fit drawing or confirmation of your soldered build.',19)

def perfboard(s,ox,oy,p,detail=False):
 # A-K / rows 12-03, chip component side facing viewer and notch toward row 14.
 def pos(h):return (ox+(ord(h[0])-65)*p,oy+(12-int(h[1:]))*p)
 s.rect(ox-p*.65,oy-p*.8,p*11.3,p*10.45,14,sw=2)
 for c in range(11):
  s.text(ox+c*p,oy-p*.42,chr(65+c),22 if detail else 18,True,'middle')
 for row in range(12,2,-1):
  s.text(ox-p*.38,oy+(12-row)*p+7,f'{row:02}',19 if detail else 15,False,'end')
  for c in range(11):s.circle(ox+c*p,oy+(12-row)*p,p*.075,sw=1)
 # Under-board bare-wire/solder bridges, visible in this transparent top view.
 for a,b,net in PERF['bridges']:s.wire([pos(a),pos(b)],5,dash='5 5')
 # IC body and legs.
 dx,dy=pos('D10');gx,by=pos('G4')
 s.rect(dx+p*.24,dy-p*.42,2.52*p,6.84*p,10)
 mid=(dx+gx)/2
 s.path(f'M{mid-14},{dy-p*.42} a14,14 0 0 0 28,0',2,halo=False)
 for h,n,net in PERF['pins']:
  x,y=pos(h);inside=dx+p*.24 if h[0]=='D' else gx-p*.24
  s.wire([(x,y),(inside,y)],4,halo=False)
  s.text(inside+(12 if h[0]=='D' else -12),y+6,n,19 if detail else 15,False,'start' if h[0]=='D' else 'end')
  if net=='unused':
   s.wire([(x-6,y-6),(x+6,y+6)],2,halo=False);s.wire([(x-6,y+6),(x+6,y-6)],2,halo=False)
 s.text(mid,dy+2.7*p,'74AHCT',22 if detail else 18,True,'middle')
 s.text(mid,dy+3.15*p,'125N',23 if detail else 18,True,'middle')
 # Route long insulated jumpers around the body rather than over its lettering.
 route={
 'g-loop':lambda a,b:[a,(a[0]-.37*p,a[1]+.35*p),(b[0]-.37*p,b[1]-.35*p),b],
 'unused-1':lambda a,b:[a,(a[0],b[1]),b],
 'unused-pair':lambda a,b:[a,(a[0]+.27*p,a[1]-.2*p),(b[0]+.27*p,b[1]+.2*p),b],
 'unused-ground':lambda a,b:[a,(a[0],oy+10*p),(b[0],oy+10*p),b],
 'enable-pair':lambda a,b:[a,(a[0]+.53*p,a[1]),(b[0]+.53*p,b[1]),b],
 'enable-power':lambda a,b:[a,(b[0],a[1]),b],
 'enable-last':lambda a,b:[a,(a[0]-.64*p,a[1]-.4*p),(a[0]-.64*p,oy-.32*p),(b[0],oy-.32*p),b]
 }
 for wire in PERF['wires']:
  if '.' in wire['b']:continue
  a,b=pos(wire['a']),pos(wire['b'])
  s.wire(route[wire['id']](a,b),3)
  s.dot(*a,4);s.dot(*b,4)
 s.resistor(*pos('B8'),*pos('B12'))
 s.text(ox+.4*p,oy+2.3*p,'330',20 if detail else 16,True)
 s.text(ox+.4*p,oy+2.65*p,'ohm',18 if detail else 14)
 a,b=pos('D11'),pos('G11');m=(a[0]+b[0])/2
 s.wire([a,(m-18,a[1])]);s.wire([(m+18,b[1]),b])
 s.wire([(m-18,a[1]-18),(m-18,a[1]+18)],4,halo=False)
 s.wire([(m+18,a[1]-18),(m+18,a[1]+18)],4,halo=False)
 s.text(m,a[1]-30,'104 / 100 nF',20 if detail else 16,True,'middle')
 return pos

s=SVG('Codex Micro complete keyboard wiring, black and white, expanded top-down view')
header(s,1,'The entire keyboard, wire by wire','Expanded top-down view. Key positions match the front of the keyboard; hidden contacts are exposed as labeled insets.')
# Legend and functional grouping.
s.wire([(90,249),(160,249)],3);s.text(175,257,'Wire',21)
s.wire([(320,249),(390,249)],5,dash='5 5');s.text(405,257,'Bridge underneath perfboard',21)
s.dot(835,249);s.text(850,257,'Dot = joined',21)
s.wire([(1130,240),(1190,265)],3);s.wire([(1130,265),(1190,240)],3);s.text(1210,257,'Crossing without dot = separate',21)
s.text(2930,257,'All wires are black here; follow labels, not insulation color.',21,False,'end')
# Components first, routed wiring on top.
bx,by=810,500
s.rect(bx,by,1080,260,16,sw=3)
s.rect(770,564,150,127,12)
s.rect(780,580,42,95,8)
s.text(810,646,'USB',23,True,'middle')
s.wire([(770,625),(650,625),(650,515),(525,515)],10)
s.text(530,488,'USB to computer',24,True)
s.rect(1260,561,150,142,4)
s.text(1335,639,'RP2040',28,True,'middle')
s.rect(1020,568,86,74,4)
s.circle(1770,586,18);s.circle(1770,690,18)
s.text(1570,640,'KB2040',35,True,'middle')
s.text(1570,680,'Component side / USB left',21,False,'middle')
top=['D-','RAW','G','RST','3V','A3','A2','A1','A0','CLK','MI','MO','10']
bot=['D+','TX','RX','GND','GND2','2','3','4','5','6','7','8','9']
kb={}
for names,y,label_y in [(top,500,534),(bot,760,738)]:
 for i,n in enumerate(names):
  x=860+80*i;kb[n]=(x,y);s.terminal(x,y)
  s.text(x,label_y,'GND' if n=='GND2' else n,21,True,'middle')
s.text(1280,712,'CLK=SCK / MI=MISO / MO=MOSI',16)
# Encoder: underscore its pin-side view so users don't mirror it accidentally.
s.text(160,329,'KNOB / ENCODER',29,True)
s.text(160,360,'Underside contact inset',21)
s.rect(160,410,240,235,18)
s.circle(280,525,69);s.circle(280,525,23)
enc={'button':(200,410),'bg':(360,410),'a':(190,645),'g':(280,645),'b':(370,645)}
for x,y in enc.values():s.terminal(x,y)
s.text(280,398,'Push button: 2 pins',21,False,'middle')
s.text(190,631,'A',19,True,'middle');s.text(280,631,'GND',19,True,'middle');s.text(370,631,'B',19,True,'middle')
s.text(160,683,'Rotation: outer / middle / outer',21)
# Joystick bottom-view inset matching the user's photo.
s.text(2370,755,'JOYSTICK',29,True)
s.text(2370,786,'COM-09426 / underside',21)
s.rect(2390,415,225,250,22)
s.rect(2440,420,111,232,7)
s.circle(2390,670,17);s.circle(2615,670,17)
joy={}
for i,(name,label) in enumerate([('X','1  X'),('V','2  3.3V'),('Y','3  Y'),('G','4  GND')]):
 x,y=2605,445+i*58;joy[name]=(x,y);s.rect(x-25,y-10,36,20,3);s.text(2650,y+7,label,23,True)
s.text(2498,713,'Tabs at bottom. Four gold pads at right.',20,False,'middle')
# Individual indicators with physical lead labels.
s.text(1950,510,'3 BANK LEDs',27,True)
s.text(1950,540,'Separate from the RGBW lights',20)
ind=[]
for i,y in enumerate([602,684,766]):
 s.resistor(1930,y,2090,y);s.text(2008,y-24,'1k ohm',20,False,'middle')
 s.circle(2150,y,27);s.text(2150,y+7,str(i+1),22,True,'middle')
 s.wire([(2090,y),(2123,y)]);s.wire([(2177,y),(2250,y)])
 s.text(2120,y+45,'+',21,True);s.text(2185,y+45,'-',21,True)
 ind.append((1930,y))
s.text(1950,845,'Long lead +  |  short / flat side -',20)
# Touch electrode.
s.text(440,865,'TOUCH PAD',27,True)
s.circle(522,922,52);s.text(522,928,'Foil',23,True,'middle')
s.terminal(574,922);s.resistor(650,922,800,922);s.text(725,900,'1M ohm',20,True,'middle')
s.wire([(574,922),(650,922)]);s.dot(620,922)
# Matrix outlines and physical key positions.
s.text(95,1040,'KEY SWITCHES',30,True)
s.text(95,1074,'Front layout, USB / back of keyboard at the top. Wire contacts underneath.',21)
centers=[240,535,830,1125]; rows=[1180,1395,1610,1825]
# Eight continuous matrix lines.
for c,x in enumerate(centers):
 rail=x-107;s.wire([(rail,1120),(rail,1910)],3)
 s.label(rail-15,1107,f'C{c+1}',20)
for r,y in enumerate(rows):
 s.wire([(95,y+86),(1390-r*27,y+86)],3)
 s.label(95,y+115,f'R{r+1} / D{r+2}',20)
# Empty matrix positions denote other controls (not phantom switches).
for c,r,name in [(0,0,'Knob above'),(3,0,'Joystick above'),(0,3,'Touch pad above')]:
 s.rect(centers[c]-66,rows[r]-42,185,87,12,stroke='black',dash='6 7')
 s.text(centers[c]+26,rows[r]+8,name,20,False,'middle')
for key in WIRING['matrix']['keys']:
 c,r=key['column'],key['row'];x,y=centers[c],rows[r]
 s.rect(x-63,y-45,183,94,9)
 s.text(x+28,y-15,key['label'].replace(' · ',' '),22,True,'middle')
 # Hidden switch legs pulled out as logical pads (not a footprint).
 a,b=(x-36,y+18),(x+92,y+18)
 s.terminal(*a);s.terminal(*b)
 s.wire([(x-107,y+18),a]);s.dot(x-107,y+18)
 s.wire([a,(x+5,y+18),(x+58,y-1)],2,halo=False)
 s.wire([(x+74,y+18),b],2,halo=False)
 # Axial diode, band towards row, below second switch terminal.
 s.wire([b,(b[0],y+86)])
 s.rect(b[0]-11,y+39,22,32,6)
 s.rect(b[0]-10,y+61,20,5,fill='black',stroke='none')
 s.dot(b[0],y+86)
# Indicate dual-switch cap.
s.wire([(477,1900),(477,1935),(939,1935),(939,1900)],2,halo=False)
s.text(708,1964,'One wide Voice cap, two switches / two diodes',21,False,'middle')
s.text(95,2012,'Every switch: column wire > switch > diode > row wire.',24,True)
s.text(95,2047,'All 13 diodes are 1N4148. The black band faces the row wire.',23)
s.text(95,2082,'Key legs are symbolic here; either switch terminal can be the column.',20)
# Perfboard actual coordinates, cropped to occupied area.
s.text(1885,938,'PERFBOARD / LED DRIVER',29,True)
s.text(1885,974,'Used holes A-K / 03-12; enlarged on sheet 2',21)
pos=perfboard(s,1900,1070,50)
# Bulk capacitor separate from bench circuit, shown as intended full chain.
s.circle(2730,1510,53);s.text(2730,1518,'100 uF',22,True,'middle')
s.text(2730,1450,'Bulk capacitor',21,True,'middle')
s.text(2675,1555,'+',27,True);s.text(2760,1555,'-',27,True)
s.text(2730,1595,'Stripe = negative',20,False,'middle')
# LED pixel chain: six input/output pads each, identical marking orientation.
s.text(1515,1659,'14 RGBW LIGHTS',29,True)
s.text(1900,1659,'Underside pads: 0-5 at Agent 01-06; 6-13 at case',21)
pix=[]
for i in range(14):
 row=i//7;col=i%7;x=1570+col*200;y=1783+row*213
 s.circle(x,y,61)
 s.text(x,y-4,str(i),30,True,'middle');s.text(x,y+25,'RGBW',16,False,'middle')
 for dx in [-45,45]:
  for dy in [-35,0,35]:s.terminal(x+dx,y+dy)
 s.text(x,y-44,'5V',16,True,'middle');s.text(x,y+52,'GND',16,True,'middle')
 s.text(x-45,y-10,'IN',13,True,'middle');s.text(x+45,y-10,'OUT',13,True,'middle')
 s.text(x,y+94,('Agent '+f'{i+1:02}') if i<6 else 'Case '+str(i-5),19,False,'middle')
 pix.append((x,y))
 # Power/ground duplicated pads internally connected; show one tap each.
 s.wire([(x-45,y-35),(x-45,y-81)],4);s.dot(x-45,y-81)
 s.wire([(x-45,y+35),(x-45,y+72)],3);s.dot(x-45,y+72)
for row in range(2):
 y=1783+row*213
 s.wire([(1500,y-81),(2870,y-81)],4)
 s.wire([(1500,y+72),(2910,y+72)],3)
 s.label(1510,y-92,'5V',18);s.label(2840,y+98,'GND',18)
for i in range(13):
 x,y=pix[i];nx,ny=pix[i+1]
 if i==6:
  s.wire([(x+45,y),(2840,y),(2840,y+118),(1475,y+118),(1475,ny),(nx-45,ny)],3)
  s.arrow(nx-55,ny)
 else:
  s.wire([(x+45,y),(nx-45,ny)],3);s.arrow((x+nx)/2,y)
s.wire([(2815,1996),(2860,1996)],3);s.circle(2860,1996,5)
s.text(2840,1974,'End',18);s.text(2840,2027,'OUT open',18)
# External wires: route with white underlay so crossings remain visibly separate.
# Matrix rows / columns from their actual KB2040 holes.
for r,y in enumerate(rows):
 xk,yk=kb[str(r+2)];lane=1390-r*27
 s.wire([(xk,yk),(xk,845+r*24),(lane,845+r*24),(lane,y+86)],3)
 s.label(lane-50,1050+r*35,f'D{r+2}',18)
for c,x in enumerate(centers):
 xk,yk=kb[str(c+6)];lane_y=940+c*23
 s.wire([(xk,yk),(xk,lane_y),(x-107,lane_y),(x-107,1120)],3)
 s.label(280+c*295,lane_y-8,f'D{c+6} / C{c+1}',20)
# Controller to knob.
s.wire([kb['TX'],(940,787),(190,787),enc['a']]);s.label(465,784,'TX - outer contact',21)
s.wire([kb['RX'],(1020,811),(370,811),enc['b']]);s.label(465,813,'RX - other outer',21)
s.wire([kb['GND'],(1100,835),(405,835),(405,708),(280,708),enc['g']])
s.wire([kb['A2'],(1340,342),(200,342),enc['button']]);s.label(515,333,'A2 - knob push',21)
# Rerouted push-button ground exactly as bench instructions (A3 perfboard, not KB A3).
s.wire([enc['bg'],(360,385),(1855,385),(1855,1560),(1900,1560),pos('A3')]);s.label(825,377,'Knob push ground > perfboard A3 > A4 > B4 > KB G',21)
# Joystick wire routes on upper lanes, no RAW connection.
for name,pin,lane in [('X','A0',305),('V','3V',283),('Y','A1',317)]:
 xk,yk=kb[pin];ex,ey=joy[name]
 # stagger final verticals so they do not overlap adjacent pads.
 lane_x={'X':2800,'V':2835,'Y':2900}[name]
 s.wire([(xk,yk),(xk,lane),(lane_x,lane),(lane_x,ey),(ex,ey)],3)
 s.label({'X':1730,'V':2115,'Y':1950}[name],lane-5,f'{pin} > joystick {name if name!="V" else "power 3.3V"}',19)
# Bank indicators routes.
for i,pin in enumerate(['CLK','MI','A3']):
 xk,yk=kb[pin];x,y=ind[i];lane=431-i*23
 s.wire([(xk,yk),(xk,lane),(1920+i*16,lane),(1920+i*16,y),(x,y)],3)
 s.label(1940,lane-7,pin+' > indicator '+str(i+1),20)
# Shared auxiliary ground connected to free GND hole; do not crowd existing holes.
s.wire([kb['GND2'],(1180,823),(2930,823),(2930,628),joy['G']],3)
s.label(2580,814,'Shared GND junction',20)
for y in [602,684,766]:
 s.wire([(2250,y),(2300,y),(2300,823)],3);s.dot(2300,823)
s.wire([(800,922),(805,922),(805,823),(1180,823)],3);s.dot(1180,823)
s.wire([kb['10'],(1820,463),(1910,463),(1910,883),(620,883),(620,922)],3);s.label(900,875,'D10 - touch electrode',21)
# Full perfboard external leads.
s.wire([kb['RAW'],(940,400),(2870,400),(2870,1170),pos('H10')],4)
s.label(2220,392,'RAW / USB 5V > H10',21)
s.wire([kb['MO'],(1740,475),(1760,475),(1760,1220),pos('C9')],3)
s.label(1550,1136,'MO > C9',20)
s.wire([kb['G'],(1020,480),(1710,480),(1710,1520),pos('B4')],3)
s.label(1510,1507,'KB G > B4',21)
# Perfboard supply outputs and one series data chain.
s.wire([pos('A12'),(1845,1070),(1845,1020),(1445,1020),(1445,1783),(1525,1783)],3)
s.label(1468,1630,'A12 > pixel 0 DIN',21)
s.wire([pos('I10'),(2870,1170),(2870,1915)],4);s.dot(2870,1170);s.dot(2870,1702)
s.wire([pos('A4'),(1900,1607),(2910,1607),(2910,2068)],3);s.dot(2910,1855)
s.wire([(2697,1551),(2697,1572),(2870,1572)],4);s.dot(2870,1572)
s.wire([(2763,1551),(2763,1607)],3);s.dot(2763,1607)
# Exact landing-hole flags, after wiring to prevent obscured labels.
for h,dx,dy,txt in [('C9',-54,-13,'C9'),('B4',-62,27,'B4'),('H10',-9,-20,'H10'),('I10',5,31,'I10'),('A12',-56,-18,'A12'),('A3',6,28,'A3'),('A4',-65,-10,'A4')]:
 x,y=pos(h);s.dot(x,y,4);s.label(x+dx,y+dy,txt,18)
for x,y in pix:
 s.dot(x-45,y-81);s.dot(x-45,y+72)
for y in [602,684,766]:s.dot(2300,y)
footer(s,'Unplug USB before soldering. Keep RAW jumper open. Use the firmware brightness limit (15%).')
master=s.save('complete-keyboard-wiring.svg')

# Sheet 2: large physical pad map plus a plain-language connection register.
s=SVG('Codex Micro enlarged perfboard and component pin orientation')
header(s,2,'Inside the perfboard','Top/component side. Column A is at the left; row 01 is at the bottom. Dashed bridges are on the underside, seen through the board.')
pos=perfboard(s,215,465,86,True)
s.text(215,330,'SAME HOLES YOU SOLDERED',32,True)
s.text(215,358,'Crop of the 4 x 6 cm board: A-K, rows 03-12.',24)
s.text(215,389,'Each hole is isolated until you deliberately join it.',24)
# External wire labels, laid out around board.
externals=[('A12',90,290,'Pixel 0 DIN'),('C9',90,720,'KB MO'),('B4',90,1200,'KB G'),('A3',430,1410,'Knob button ground'),('A4',100,1365,'All pixel GND'),('H10',1200,320,'KB RAW / 5V'),('I10',1200,560,'All pixel 5V')]
for h,ex,ey,txt in externals:
 x,y=pos(h)
 if ex==90:s.wire([(x,y),(130,y),(130,ey),(ex,ey)],3)
 elif ex==1200:s.wire([(x,y),(ex-40,y),(ex-40,ey),(ex,ey)],3)
 else:s.wire([(x,y),(x,ey-45),(ex,ey-45),(ex,ey-12)],3)
 s.label(ex,ey-12,txt,23)
s.text(190,1478,'NOTCH points toward the column letters / higher row numbers.',24,True)
s.text(190,1515,'Looking underneath mirrors left and right. Locate the holes from above first.',23)
s.text(190,1570,'Solid line = insulated wire on top. Short dashed line = bent lead + solder below.',23)
s.text(190,1607,'Small X = intentionally unused chip output; leave unconnected.',23)
# Pin table.
tx=1430
s.text(tx,317,'WHAT EACH CHIP LEG DOES',32,True)
s.text(tx,356,'SN74AHCT125N - the small chip translates only the LED data.',23)
cols=[tx,tx+110,tx+260,tx+490]
for x,t in zip(cols,['Pin','Hole','Function','Connect to']):s.text(x,406,t,22,True)
s.wire([(tx,421),(2870,421)],2,halo=False)
functions={1:('/OE1','GND - enables channel 1'),2:('1A input','KB2040 MO through C9'),3:('1Y output','330 ohm resistor > A12 > pixel 0 DIN'),4:('/OE2','5V - disables spare channel'),5:('2A input','GND'),6:('2Y output','Leave open'),7:('GND','Common ground'),8:('3Y output','Leave open'),9:('3A input','GND'),10:('/OE3','5V - disables spare channel'),11:('4Y output','Leave open'),12:('4A input','GND'),13:('/OE4','5V - disables spare channel'),14:('VCC','RAW / 5V through H10')}
for i,(h,n,net) in enumerate(PERF['pins']):
 y=466+i*46
 for x,t in zip(cols,[str(n),h,*functions[n]]):s.text(x,y,t,22,n in [1,2,3,7,14])
 s.wire([(tx,y+15),(2870,y+15)],.6,halo=False)
s.text(tx,1160,'THE TWO COMPONENTS ALREADY ON THE BOARD',27,True)
for y,t in [(1201,'330 ohm resistor: B8 to B12. B8-C8-D8 and A12-B12 are bridges.'),(1238,'104 ceramic capacitor: D11 to G11. D11-D10 and G11-G10 are bridges.'),(1275,'The capacitor crosses power and ground; it does not short them together.')]:s.text(tx,y,t,23)
s.text(tx,1345,'ADDITIONS FOR THE COMPLETE KEYBOARD',27,True)
for y,t in [(1387,'100 uF capacitor near the start of the light chain: + to 5V; stripe to GND.'),(1424,'More lights: each needs 5V + GND, plus data from the preceding DOUT.'),(1461,'Joystick, touch and indicators share GND. Use a separate soldered junction'),(1498,'from the spare GND hole; the illustration does not assign new perfboard holes.')]:s.text(tx,y,t,23)
# Bottom reference strip: orientation compact and sources.
s.wire([(190,1650),(2870,1650)],2,halo=False)
s.text(190,1700,'HOW TO READ THE REST OF THE KEYBOARD',29,True)
s.text(190,1750,'Keys',25,True)
s.text(190,1790,'A key closes a column-to-row path.',23)
s.text(190,1827,'Diode black band faces its row.',23)
s.text(190,1864,'Both Voice switches get a diode.',23)
s.text(880,1750,'Knob + joystick',25,True)
s.text(880,1790,'Knob center of 3 terminals = GND.',23)
s.text(880,1827,'Other side: two pushbutton contacts.',23)
s.text(880,1864,'Joystick pads, from underside: X, 3V, Y, GND.',23)
s.text(1700,1750,'Lights',25,True)
s.text(1700,1790,'All 5V pads share power; all GND pads share ground.',23)
s.text(1700,1827,'Only DATA chains: OUT of one > IN of the next.',23)
s.text(1700,1864,'Pixel pads: underside, arrows left to right, 5V at top.',23)
s.text(190,1940,'References checked against this project and manufacturer documentation:',23,True)
for y,t in [(1978,'KB2040: learn.adafruit.com/adafruit-kb2040/pinouts  |  Level shifter: ti.com/lit/ds/symlink/sn74ahct125.pdf'),(2015,'NeoPixels: adafruit.com/product/4776  |  Encoder: adafruit.com/product/377  |  Joystick: sparkfun.com/thumb-slide-joystick.html'),(2052,'Project source: data/wiring.json + wiring-guide/connections.json + downloads/firmware/code.py on codexmicro.diy.')]:s.text(190,y,t,21)
footer(s,'A3 / A4 here are PERFBOARD coordinates, not the analog pins on the KB2040.')
detail=s.save('complete-keyboard-perfboard.svg')

# Convert SVG to a two-page vector PDF. Custom poster ratio avoids distortions.
pdf=ROOT/'output/pdf/Codex-Micro-Complete-Wiring.pdf'
pdf.parent.mkdir(parents=True,exist_ok=True)
pagesize=(594*mm,594*mm*H/W)
c=canvas.Canvas(str(pdf),pagesize=pagesize)
c.setTitle('Codex Micro - Complete Keyboard Wiring');c.setAuthor('Codex Micro DIY')
for svg in [master,detail]:
 drawing=svg2rlg(str(svg));factor=pagesize[0]/drawing.width
 c.saveState();c.scale(factor,factor);renderPDF.draw(drawing,c,0,0);c.restoreState();c.showPage()
c.save()
shutil.copy2(pdf,OUT/pdf.name)
# Render both pages for visual QA and a smaller website preview.
doc=fitz.open(pdf)
for i,page in enumerate(doc):
 page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(str(ROOT/f'tmp/pdfs/complete-page-{i+1}.png'))
page=doc[0];page.get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False).save(str(OUT/'complete-keyboard-preview.png'))
print(json.dumps({'pdf':str(pdf),'svg':str(master),'pages':len(doc),'page_points':pagesize},indent=2))
