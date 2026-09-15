"""Two-layer screwed LED tray. Units mm. Physical fit pending.
Run with requirements.txt. STEP is assembled, STL is bed-oriented.
Reference switch/pin/controller envelopes are conservative approximations,
not a completed electrical harness or a strength simulation.
"""
from pathlib import Path
import json, math
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'files'; OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'parameters.json').read_text())
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))
def rr(w,d,h,r,x=0,y=0,z=0):return box(w,d,h,x,y,z).edges('|Z').fillet(r)
def cyl(r,h,x=0,y=0,z=0):return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def vol(a,b):return a.intersect(b).val().Volume()
def link(a,b,w,h,z):
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
 body=box(length,w,h,z=z).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(dy,dx))).translate(((a[0]+b[0])/2,(a[1]+b[1])/2,0))
 return body.union(cyl(w/2,h,*a,z)).union(cyl(w/2,h,*b,z))
C=[-28.575,-9.525,9.525,28.575]
centers=[(-9.525,28.575),(9.525,28.575)]+[(x,9.525) for x in C]
mounts=[(-16,41.5),(16,41.5),(-41.5,9.525),(41.5,9.525)]
base=P['floor_bottom_z_mm']; rim=22.; floor_top=base+1.8
# Stepped footprint avoids encoder and joystick undersides. Solid shared floor
# joins the six compartments; outside arms carry screw loads into this floor.
tray=rr(75.85,18.7,1.8,1.2,0,9.525,base).union(rr(37.75,37.75,1.8,1.2,0,19.05,base))
for a,b in zip([(-9.525,34),(9.525,34),(-34,9.525),(34,9.525)],mounts):
 tray=tray.union(link(a,b,8,1.8,base))
 tray=tray.union(cyl(4,rim-base,*b,base))
for x,y in centers:
 cup=rr(18.7,18.7,rim-floor_top,1.2,x,y,floor_top).cut(rr(16.3,16.3,rim-floor_top+1,.7,x,y,floor_top))
 # Matrix leads can leave in either axis below the switch housing.
 for s in [-1,1]:
  cup=cup.cut(box(6,3,5.1,x,y+s*9,17))
  cup=cup.cut(box(3,6,5.1,x+s*9,y,17))
 tray=tray.union(cup)
 # LED pocket: 0.8 mm remaining floor; 0.2 mm insulating tape allowance.
 tray=tray.cut(rr(9.7,9.7,3,.4,x,y,base+.8))
 # LED cable passes through floor outside the LED pocket, toward -Y.
 tray=tray.cut(rr(6,2.2,3,.4,x,y-6.5,base-.1))
plate=cq.importers.importStep(str(ROOT/'references/top-plate-v3.step'))
for x,y in mounts:
 hole=cyl(P['hole_diameter_mm']/2,25,x,y,4)
 tray=tray.cut(hole);plate=plate.cut(hole)
# Small sample is literally cropped from the assembled upper/lower pair.
crop=box(48,26.95,30,0,32.525,0) # y19.05..46, includes the two upper mounts
sample_top=plate.intersect(crop); sample_tray=tray.intersect(crop)
results={'revision':'Two-layer baffle tray v2; physical fit pending','mount_centers_mm':mounts,'cup_centers_mm':centers}
def save(name,s,flip=False):
 assert s.val().isValid() and len(s.solids().vals())==1,name
 cq.exporters.export(s,str(OUT/(name+'.step')))
 p=s.rotate((0,0,0),(1,0,0),180) if flip else s
 b=p.val().BoundingBox();p=p.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
 f=OUT/(name+'.stl');cq.exporters.export(p,str(f),tolerance=.02,angularTolerance=.08)
 m=trimesh.load_mesh(f);m.merge_vertices(digits_vertex=6);m.update_faces(m.nondegenerate_faces());m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
 assert m.is_watertight and m.is_volume and len(m.split())==1,name
 m.export(f);results[name]={'size_mm':m.extents.tolist(),'volume_mm3':float(m.volume),'watertight':True,'one_solid':True}
save('PRINT_FIRST_two_key_top_sample',sample_top,True)
save('PRINT_FIRST_two_key_baffle_sample',sample_tray)
save('WAIT_full_top_plate',plate) # underside down: flat except shallow MX reliefs
save('WAIT_six_light_baffle_tray',tray)
case=cq.importers.importStep(str(ROOT/'references/case.step'))
board=box(17.8,35,4.9,0,31,4)
encoder=box(16,16,13,-28.575,28.575,9) # enlarged housing approximation
# Joystick pins, nuts and tails below its plate opening: conservative envelope.
joy_under=box(11,6,8,30,22.5,14) # v3 pad opening plus 1 mm wire allowance
for x,y in [(38.61,21.03),(37.44,40.15)]:
 joy_under=joy_under.union(cyl(2.05,1.3,x,y,20.7)).union(cyl(.8,3,x,y,19))
hardware=[];nuts=[]
for x,y in mounts:
 screw=cyl(1.5,20,x,y,5).union(cyl(2.75,3,x,y,25))
 nut=cq.Workplane('XY').polygon(6,5.5/math.cos(math.pi/6)).extrude(2.4).translate((x,y,base-2.4)).cut(cyl(1.5,30,x,y,0))
 # Model a 9mm OD socket from below; exposed nuts remain tool-accessible.
 tool=cyl(4.5,base-1.8,x,y,0)
 assert vol(tool,tray)<.001,'underside socket access obstructed'
 for obj in [plate,tray,case,board,encoder,joy_under]:
  assert vol(obj,screw)<.001,('screw collision',x,y,vol(obj,screw))
  assert vol(obj,nut)<.001,('nut collision',x,y)
 bearing=vol(tray,nut.translate((0,0,.01)))/.01
 assert bearing>10,('nut bearing area',bearing)
 results.setdefault('nut_bearing_area_mm2',[]).append(round(bearing,3))
 hardware.append(screw);nuts.append(nut)
results['screw_tip_below_nut_mm']=base-2.4-5
results['screw_tip_above_case_floor_mm']=5-2.4
for name,obj in [('case',case),('top_plate',plate),('KB2040_reference',board),('encoder_reference',encoder),('joystick_underside_reference',joy_under)]:
 v=vol(tray,obj);results[name+'_tray_overlap_mm3']=v;assert v<.001,(name,v)
results['top_plate_case_overlap_mm3']=vol(plate,case);assert results['top_plate_case_overlap_mm3']<.001
positions=[(x,y) for y in [28.575,9.525,-9.525,-28.575] for x in C if (x,y) not in [(-28.575,28.575),(28.575,28.575),(-28.575,-28.575)]]
switches=[];leds=[]
for x,y in positions:
 sw=box(14.2,14.2,5,x,y,18.4);pins=box(12,12,3.5,x,y,14.9)
 cap=box(18,18,12,x,y,25)
 assert vol(tray,sw)<.001 and vol(tray,pins)<.001
 for h in hardware:assert vol(h,cap)<.001,'head/keycap overlap'
 for dz in [0,-1,-4,-8,-12,-18]:
  lowered=tray.translate((0,0,dz))
  assert vol(lowered,sw)<.001 and vol(lowered,pins)<.001,'tray removal obstruction'
 switches.append(sw)
 if (x,y) in centers:
  led=box(9.1,9.1,3.1,x,y,base+1.0)
  assert vol(led,tray)<.001 and vol(led,pins)<.001
  leds.append(led)
results['nominal_LED_to_pin_envelope_gap_mm']=round(14.9-(base+1+3.1),3)
results['nominal_tray_to_controller_gap_mm']=round(base-8.9,3)
results['limits']=['Not physically printed or load/fatigue tested. No claim of verified strength.','Switch, pin, controller, encoder and joystick underside envelopes are approximations; solder joints and wires require a real fit check.','Test two small parts with real switches, keycaps, LEDs and two M3x20 screws/nuts before full print.','Lift the top plate and tray together out of the case before accessing the exposed nuts.','LED pockets locate LEDs but do not clamp them: use a thin removable insulating adhesive pad, total thickness 0.2mm allowance.','Keep service slack and insulate LED rear pads; no electrical disconnect is included.','Full top plate prints underside down; shallow switch reliefs may need slicer-specific support. Physical joystick fit remains pending.','Reference assembly and older main animation are not manufacturing verification.']
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
asm=cq.Assembly(name='TWO_LAYER_BAFFLE_V2_PHYSICAL_FIT_PENDING')
asm.add(plate,name='PRINT_upper_plate',color=cq.Color(.77,.88,.92));asm.add(tray,name='PRINT_lower_baffle_tray',color=cq.Color(.13,.15,.17))
for i,(s,n) in enumerate(zip(hardware,nuts)):
 asm.add(s,name=f'BUY_M3x20_screw_{i}',color=cq.Color(.5,.5,.5));asm.add(n,name=f'BUY_M3_nut_{i}',color=cq.Color(.5,.5,.5))
for i,s in enumerate(switches):asm.add(s,name=f'REF_switch_envelope_{i}',color=cq.Color(.5,.6,.6))
for i,s in enumerate(leds):asm.add(s,name=f'REF_LED_envelope_{i}',color=cq.Color(.85,.7,.15))
asm.save(str(OUT/'reference_assembly_NOT_PRINTABLE.step'))
# Export geometry-only viewer payload from the SAME CAD as the printable parts.
scene=[]
def mesh_payload(s):
 vertices=[];indices=[]
 for solid in s.solids().vals():
  vs,ts=solid.tessellate(.08);offset=len(vertices)//3
  vertices.extend(v for p in vs for v in p.toTuple());indices.extend(i+offset for t in ts for i in t)
 return {'vertices':[round(v,5) for v in vertices],'indices':indices}
for name,s,color,layer in [('Upper plate',plate,'#b6d9e3','top'),('Lower baffle tray',tray,'#434c55','bottom')]+[(f'Screw {i+1}',s,'#919ba2','screw') for i,s in enumerate(hardware)]+[(f'Nut {i+1}',s,'#c1c8ce','nut') for i,s in enumerate(nuts)]:
 scene.append({'name':name,'color':color,'layer':layer,**mesh_payload(s)})
(ROOT/'scene.json').write_text(json.dumps(scene,separators=(',',':')))
(ROOT/'scene.js').write_text('window.BAFFLE_SCENE='+json.dumps(scene,separators=(',',':'))+';')
# Static views also derive from actual geometry; no generated product image.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(14,6),facecolor='#f6f7f8')
def draw(ax,shapes):
 faces=[];colors=[]
 for s,color in shapes:
  for solid in s.solids().vals():
   vs,ts=solid.tessellate(.08);vs=[v.toTuple() for v in vs]
   for t in ts:
    f=[vs[j] for j in t];a,b,c=np.array(f);n=np.cross(b-a,c-a);n=n/max(np.linalg.norm(n),1e-12)
    faces.append(f);colors.append(tuple(np.array(matplotlib.colors.to_rgb(color))*(.58+.32*abs(n[2])+.1*abs(n[0]))))
 ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors=(0,0,0,0),linewidth=0))
for i,title in enumerate(['1  Upper plate + removable lower tray','2  Six compartments, four rigid posts','3  Print this two-key sample first']):
 ax=fig.add_subplot(1,3,i+1,projection='3d',facecolor='#f6f7f8')
 if i==0:
  draw(ax,[(plate.translate((0,0,22)),'#b6d9e3'),(tray,'#434c55')]+[(s.translate((0,0,30)),'#939b9f') for s in hardware]+[(n.translate((0,0,-6)),'#939b9f') for n in nuts]);bounds=(-50,50,-48,48,-1, 60)
 elif i==1:draw(ax,[(tray,'#64727b')]);bounds=(-49,49,-2,47,8,29)
 else:
  draw(ax,[(sample_tray,'#64727b'),(sample_top.translate((0,0,10)),'#b6d9e3')]);bounds=(-26,26,17,48,8,41)
 ax.set(xlim=bounds[:2],ylim=bounds[2:4],zlim=bounds[4:]);ax.set_box_aspect((bounds[1]-bounds[0],bounds[3]-bounds[2],bounds[5]-bounds[4]));ax.view_init(elev=38,azim=-65);ax.set_axis_off();ax.set_title(title,fontsize=10)
fig.suptitle('Two layers. Four screws. No flexible clips.',fontsize=19)
fig.text(.5,.04,'Actual CAD geometry · black PETG lower tray · ordinary exposed M3 nuts underneath · physical fit pending',ha='center',fontsize=10)
fig.savefig(ROOT/'preview.png',dpi=150,bbox_inches='tight');plt.close(fig)
print(json.dumps(results,indent=2))
