"""Mounting v5. CadQuery millimeters; print STLs at 100%.
Hidden upward M3 tray screws + keyed removable PSP1000 adapter.
Nominal CAD verification is not a physical fit or strength test.
"""
from pathlib import Path
import json, math
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'files'; OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'parameters.json').read_text())
TOP=P['plate_top_z_mm']; BOTTOM=P['plate_bottom_z_mm']
FLOOR=P['tray_floor_bottom_z_mm']; CONTACT=P['boss_contact_z_mm']
JX,JY=P['joystick_center_mm']; BODY=TOP+P['adapter_thickness_mm']
CENTERS=P['ear_centers_mm']; MOUNTS=P['tray_mount_centers_mm']
results={'status':'CAD checked; physical fit pending','parts':{},'checks':{},'hardware':{}}
def box(w,d,h,x=0,y=0,z=0):
 return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))
def rr(w,d,h,r,x=0,y=0,z=0): return box(w,d,h,x,y,z).edges('|Z').fillet(r)
def cyl(r,h,x=0,y=0,z=0): return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def local(s):return s.translate((JX,JY,0))
def volume(s):return sum(v.Volume() for v in s.vals())
def overlap(a,b):return volume(a.intersect(b))
def clear(label,a,b):
 v=overlap(a,b);results['checks'][label]=round(v,6)
 assert v<.002,(label,v)
def read(name):return cq.importers.importStep(str(ROOT/'references'/name))
original=read('original-plate.step')
# Restore the retired pocket. No old light-tray screw holes exist in this source.
plate=original.union(rr(22,22,3,2.1,30,30,BOTTOM))
tray=read('tray-v4.step')
for x,y in MOUNTS:
 # Move structural posts onto the upper plate; remove tall old lower posts.
 tray=tray.cut(cyl(P['tray_boss_clearance_radius_mm'],20,x,y,CONTACT))
 tray=tray.cut(cyl(P['m3_clearance_diameter_mm']/2,8,x,y,FLOOR-1))
 boss=cyl(P['boss_radius_mm'],BOTTOM-CONTACT+.01,x,y,CONTACT)
 pilot=cyl(P['insert_pilot_diameter_mm']/2,P['insert_pilot_depth_mm']+.01,x,y,CONTACT-.01)
 well=cyl(P['m3_clearance_diameter_mm']/2,P['tip_well_top_z_mm']-CONTACT,x,y,CONTACT)
 plate=plate.union(boss).cut(pilot.union(well))
# Adapter: flat body, two raised ear seats and two SOLID location pegs.
adapter=rr(20,20,P['adapter_thickness_mm'],1,0,0,TOP)
outline=[(-5.6,-9.55),(5.6,-9.55),(9.55,-5.6),(9.55,5.6),(5.6,9.55),(-5.6,9.55),(-9.55,5.6),(-9.55,-5.6)]
keepout=cq.Workplane('XY').polyline(outline).close().extrude(6).translate((0,0,BODY-.001))
for name,(x,y) in CENTERS.items():
 adapter=adapter.union(rr(6.4,5.4,P['adapter_thickness_mm'],.5,x,y,TOP))
 adapter=adapter.union(rr(6.4,5.4,P['ear_support_mm'][name],.5,x,y,BODY).cut(keepout))
 hole=cyl(P['joystick_hole_diameter_mm']/2,20,x,y,15)
 adapter=adapter.cut(hole);plate=plate.cut(local(hole))
for x,y in P['locating_peg_centers_mm']:
 peg=cyl(P['locating_peg_diameter_mm']/2,P['locating_peg_length_mm']+.01,x,y,TOP-P['locating_peg_length_mm'])
 peg=peg.edges('<Z').chamfer(.25)
 adapter=adapter.union(peg)
 plate=plate.cut(local(cyl(P['locating_hole_diameter_mm']/2,5,x,y,BOTTOM-1)))
wire=rr(9,4,20,.5,0,-7.5,15)
adapter=local(adapter.cut(wire));plate=plate.cut(local(wire))
# Samples are literal crops of the full final CAD, not independent approximations.
crop=box(48,26.95,40,0,32.525,0)
top_sample=plate.intersect(crop);bottom_sample=tray.intersect(crop)
# Cut the joystick-only sample at the plate underside to exclude a sliver of
# the neighboring tray boss. Its complete joystick interface stays identical.
corner=plate.intersect(box(28.7,28.7,18,32.65,32.65,BOTTOM))
parts={
 'PRINT_FIRST_upper_joint_sample':(top_sample,True),
 'PRINT_FIRST_lower_joint_sample':(bottom_sample,False),
 'PRINT_FIRST_joystick_corner':(corner,True),
 'PRINT_joystick_adapter':(adapter,False),
 'WAIT_full_top_plate':(plate,True),
 'WAIT_lower_light_tray':(tray,False),
}
for name,(shape,flip) in parts.items():
 assert shape.val().isValid() and len(shape.solids().vals())==1,(name,'invalid/disconnected')
 cq.exporters.export(shape,str(OUT/f'{name}.step'))
 printing=shape.rotate((0,0,0),(1,0,0),180) if flip else shape
 b=printing.val().BoundingBox();printing=printing.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
 path=OUT/f'{name}.stl';cq.exporters.export(printing,str(path),tolerance=.025,angularTolerance=.08)
 mesh=trimesh.load_mesh(path);mesh.merge_vertices(digits_vertex=6)
 mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
 assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1,(name,'bad STL')
 mesh.export(path)
 results['parts'][name]={'size_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'watertight':True,'solid_count':1,'bed_z':float(mesh.bounds[0,2]),'orientation':'visible face down, bosses up' if flip else ('pegs down; support underside of adapter' if 'adapter' in name else 'cups up')}
 print('Exported',name,flush=True)
case=read('case.step')
ref=read('joystick-reference.step').rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90).translate((-9.25,-9.25,0))
ref=ref.rotate((0,0,0),(0,0,1),180).translate((JX,JY,BODY))
for label,a,b in [('upper_vs_case',plate,case),('lower_vs_case',tray,case),('upper_vs_lower',plate,tray),('adapter_vs_upper',adapter,plate),('adapter_vs_reference_joystick',adapter,ref),('joystick_vs_case',ref,case),('adapter_vs_case',adapter,case),('joystick_vs_tray',ref,tray)]:clear(label,a,b)
assembly=cq.Assembly(name='MOUNTING_V5_PHYSICAL_FIT_PENDING');scene=[]
def add(shape,name,color,layer,reference=False):
 assembly.add(shape,name=name,color=cq.Color(color))
 # One tessellation per solid prevents accidentally discarding compound components.
 for idx,solid in enumerate(shape.solids().vals()):
  verts,tris=solid.tessellate(.06)
  scene.append({'name':name,'color':color,'layer':layer,'vertices':[round(c,4) for v in verts for c in v.toTuple()],'indices':[i for t in tris for i in t]})
add(plate,'Upper_plate','#d6e1e8','top');add(tray,'Lower_light_tray','#485765','bottom')
add(adapter,'Removable_joystick_adapter','#eaa156','adapter');add(ref,'REFERENCE_joystick','#44484c','joystick')
# Heat-set insert is an interference fit in its pilot by design; no false
# zero-overlap assertion. Use OD envelope, unthreaded visual bore.
for i,(x,y) in enumerate(MOUNTS):
 insert=cyl(P['insert_outer_diameter_mm']/2,4,x,y,CONTACT).cut(cyl(1.5,4,x,y,CONTACT))
 screw=cyl(1.5,8,x,y,FLOOR).union(cyl(2.85,3,x,y,FLOOR-3))
 screw=screw.cut(cq.Workplane('XY').polygon(6,2.5/math.cos(math.pi/6)).extrude(1.8).translate((x,y,FLOOR-3)))
 for name,s in [('screw',screw),('insert',insert)]:
  clear(f'tray_{i}_{name}_vs_case',s,case)
  clear(f'tray_{i}_{name}_vs_lower',s,tray)
  clear(f'tray_{i}_{name}_vs_adapter',s,adapter)
 clear(f'tray_{i}_screw_vs_upper',screw,plate)
 # Allow entry into the pilot itself, but ensure insertion tool clears nearby walls.
 tool=cyl(2.5,10,x,y,CONTACT-10)
 clear(f'insert_{i}_tool_access',tool,plate)
 add(screw,f'M3x8_upward_screw_{i+1}','#9ba6af','screw')
 add(insert,f'M3x4_heat_set_insert_{i+1}','#caab60','insert')
 # No tray hole through the front skin.
 skin=cyl(1.7,.5,x,y,TOP-.5)
 assert abs(overlap(skin,plate)-volume(skin))<.002,'tray hole in visible face'
results['hardware']['tray']={'quantity':4,'screw':'M3 x 8 socket cap, DIN912','insert':'Adafruit M3 x 4, 4.2 mm OD','lower_grip_mm':CONTACT-FLOOR,'insert_engagement_mm':4,'tip_clearance_mm':P['tip_well_top_z_mm']-(FLOOR+8),'pilot_diameter_mm':P['insert_pilot_diameter_mm'],'roof_above_tip_well_mm':TOP-P['tip_well_top_z_mm']}
layouts={'SparkFun':{'A':(8.89,-8.985),'B':(7.375,10.06)},'community':{'A':(8.328428,-8.95),'B':(7.5,10.232119)}}
hardware=[]
for label,points in layouts.items():
 for name,(x,y) in points.items():
  shaft=local(cyl(.8,16,x,y,15))
  clear(f'{label}_{name}_shaft_upper',shaft,plate);clear(f'{label}_{name}_shaft_adapter',shaft,adapter)
for name,(x,y) in layouts['community'].items():
 bearing_z=BODY+(2.5 if name=='A' else 2.)
 screw=cyl(.8,P['joystick_screw_length_mm'],x,y,bearing_z-P['joystick_screw_length_mm']).union(cyl(1.5,1.6,x,y,bearing_z))
 screw=screw.cut(cq.Workplane('XY').polygon(6,1.5/math.cos(math.pi/6)).extrude(1).translate((x,y,bearing_z+.9)))
 nut=cq.Workplane('XY').polygon(6,3.2/math.cos(math.pi/6)).extrude(1.3).translate((x,y,BOTTOM-1.3)).cut(cyl(.8,4,x,y,BOTTOM-2))
 screw=local(screw);nut=local(nut)
 for kind,s in [('screw',screw),('nut',nut)]:
  for label,target in [('plate',plate),('adapter',adapter),('case',case),('tray',tray),('joystick',ref)]:clear(f'joy_{name}_{kind}_vs_{label}',s,target)
 bearing=overlap(plate,nut.translate((0,0,.01)))/.01;assert bearing>2
 results['hardware'][f'joystick_{name}']={'screw':'M1.6 x 10 socket cap','nut':'M1.6 standard hex, AF 3.2 x 1.3 mm','tip_below_nut_mm':round(BOTTOM-1.3-(bearing_z-10),3),'nut_bearing_area_mm2':round(bearing,3)}
 hardware += [screw,nut]
 add(screw,'M1_6x10_joystick_screw_'+name,'#abb2b9','joyscrew');add(nut,'M1_6_exposed_nut_'+name,'#abb2b9','joynut')
# Approximate bounding envelopes; real wiring/solder and moving caps still need a physical check.
lights=[(-9.525,28.575),(9.525,28.575)]+[(x,9.525) for x in [-28.575,-9.525,9.525,28.575]]
for i,(x,y) in enumerate(lights):
 switch=box(14.2,14.2,5,x,y,18.4);pins=box(12,12,3.5,x,y,14.9);cap=box(18,18,12,x,y,25);led=box(9.4,9.4,3.1,x,y,11)
 for label,s in [('switch',switch),('pins',pins),('cap',cap),('LED',led)]:
  for n,target in [('upper',plate),('lower',tray),('adapter',adapter),('joystick',ref)]:
   # Plate clips/led pocket fit already validated in source; switch bodies here
   # are bounding boxes and may intersect intended clips. Check NEW geometry separately.
   if label=='switch' and n=='upper':continue
   clear(f'{i}_{label}_vs_{n}',s,target)
  for j,h in enumerate(hardware):clear(f'{i}_{label}_vs_joy_hardware_{j}',s,h)
 # Preserve full 10 x 4 mm LED access opening through the lower floor.
 clear(f'{i}_10x4_LED_access',rr(10,4,2,.4,x,y-5,FLOOR-.1),tray)
for name,envelope in [('KB2040',box(17.8,35,4.9,0,31,4)),('encoder',box(16,16,13,-28.575,28.575,9))]:
 for n,s in [('upper',plate),('lower',tray),('adapter',adapter)]:clear(name+'_vs_'+n,envelope,s)
# Switch/encoder/touch/case-hole geometry outside joystick and mounts must be unchanged.
mask=box(26,28,20,JX,JY,18)
for x,y in MOUNTS:mask=mask.union(cyl(4.3,20,x,y,10))
old=original.cut(mask);new=plate.cut(mask)
assert volume(new.cut(old))+volume(old.cut(new))<.002,'unexpected source geometry change'
results['checks']['source_geometry_symmetric_difference_outside_mounts_mm3']=round(volume(new.cut(old))+volume(old.cut(new)),6)
assembly.save(str(OUT/'reference_assembly_NOT_PRINTABLE.step'))
(ROOT/'scene.js').write_text('window.MOUNTING_SCENE='+json.dumps(scene,separators=(',',':'))+';\n')
results['limits']=['No physical fit, fatigue, heat-set pullout or strength testing performed.','Ear heights A 0.5 / B 1.0 mm retained from previous fit study; confirm both tabs sit without bending.','Joystick reference is a community model, not a controlled manufacturer drawing; test full thumb travel.','Actual wire routing, solder blobs, underside insulation and driver access need a dry assembly check.','Adapter pegs-down orientation requires support under its base; keep pegs, holes and seats clean.','Both full upper and lower parts are new matched v5 geometry; do not mix with v2-v4 hardware locations.']
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS',len(results['checks']),'nominal geometry checks',flush=True)
