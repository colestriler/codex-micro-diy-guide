"""Flat COM-09426 mount with exposed nuts, revision 3. Dimensions in mm.
Run with Python 3.12 and requirements.txt installed. Physical fit pending.
The test corner and full plate are cut from the SAME finished geometry.
"""
from pathlib import Path
import json, math
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'files';OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'parameters.json').read_text())
TOP=25.; BOTTOM=22.; BODY=TOP; JX,JY=P['joystick_center_mm']
# Rotation by 180 degrees moves the ears toward the outer/right plate edge.
CENTERS={'A':(8.61,-8.97),'B':(7.44,10.15)}
def box(w,d,h,x=0,y=0,z=0):
 return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))
def rr(w,d,h,r,x=0,y=0,z=0):return box(w,d,h,x,y,z).edges('|Z').fillet(r)
def slot(length,width,h,x,y,z):return cq.Workplane('XY').slot2D(length,width).extrude(h).translate((x,y,z))
def globalize(s):return s.translate((JX,JY,0))
plate=cq.importers.importStep(str(ROOT/'references/original-plate.step'))
# Restore only the old joystick recess and central wire hole before recutting.
plate=plate.union(rr(22,22,3,2.1,30,30,BOTTOM))
# Only two raised seats above the flat plate. Their inside corners clear the
# stationary housing; heights reproduce the original 0.5 / 1.0 mm test shims.
outline=[(-5.6,-9.55),(5.6,-9.55),(9.55,-5.6),(9.55,5.6),
         (5.6,9.55),(-5.6,9.55),(-9.55,5.6),(-9.55,-5.6)]
keepout=cq.Workplane('XY').polyline(outline).close().extrude(6).translate((0,0,TOP-.1))
for name,(x,y) in CENTERS.items():
 seat=rr(6.4,5.4,P['ear_support_mm'][name],.5,x,y,TOP).cut(keepout)
 plate=plate.union(globalize(seat))
# Straight through-holes, with access for ordinary loose nuts below the plate.
# 2.4 mm accommodates both documented hole layouts around these midpoints.
for name,(x,y) in CENTERS.items():
 hole=cq.Workplane('XY').center(x,y).circle(P['screw_clearance_diameter_mm']/2).extrude(12).translate((0,0,18))
 plate=plate.cut(globalize(hole))
# Through-opening under the four solder pads; no recessed body pocket.
plate=plate.cut(globalize(rr(9,4,12,.5,0,-7.5,18)))
# Cropped directly from the full plate. This crop avoids all adjacent MX clip
# reliefs, leaving a flat underside that can print on the bed without supports.
corner=plate.intersect(box(28.7,28.7,15,32.65,32.65,18))
results={}
def save(name,shape):
 assert shape.val().isValid() and len(shape.solids().vals())==1,name
 cq.exporters.export(shape,str(OUT/f'{name}.step'))
 # Flat underside on the bed; raised tab seats point UP.
 printing=shape
 b=printing.val().BoundingBox()
 printing=printing.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
 path=OUT/f'{name}.stl'
 cq.exporters.export(printing,str(path),tolerance=.02,angularTolerance=.08)
 mesh=trimesh.load_mesh(path);mesh.merge_vertices(digits_vertex=6)
 mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces())
 mesh.remove_unreferenced_vertices()
 assert mesh.is_watertight and mesh.is_volume,name
 assert len(mesh.split())==1,name
 mesh.export(path)
 results[name]={'size_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'watertight':True,'connected_solids':1,'print_z_min':float(mesh.bounds[0,2])}
save('PRINT_FIRST_flat_joystick_corner_v3',corner)
save('WAIT_flat_top_plate_v3',plate)
# Re-use the reference used for v1 and rotate it to the outer side of the plate.
ref=cq.importers.importStep(str(ROOT/'references/marbastlib-PNT_psp1000.step'))
ref=ref.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90).translate((-9.25,-9.25,0))
ref=ref.rotate((0,0,0),(0,0,1),180).translate((JX,JY,BODY))
case=cq.importers.importStep(str(ROOT/'references/original-case.step'))
def overlap(a,b):return a.intersect(b).val().Volume()
results['reference_joystick_overlap_mm3']=overlap(plate,ref)
results['existing_case_overlap_mm3']=overlap(plate,case)
results['underside_protrusions_mm3']=overlap(plate,box(110,110,10,z=BOTTOM-10))
assert results['underside_protrusions_mm3']<.001
# The entire printable test corner underside is flat.
assert abs(corner.val().BoundingBox().zmin-BOTTOM)<1e-6
assert results['reference_joystick_overlap_mm3']<.001,results
assert results['existing_case_overlap_mm3']<.001,results
layouts={'SparkFun':{'A':(8.89,-8.985),'B':(7.375,10.06)},'community':{'A':(8.328428,-8.95),'B':(7.5,10.232119)}}
for label,points in layouts.items():
 for name,(x,y) in points.items():
  shaft=globalize(cq.Workplane('XY').center(x,y).circle(.8).extrude(8).translate((0,0,BODY-6)))
  assert overlap(plate,shaft)<.001,(label,name,'shaft obstruction')
assembly=cq.Assembly(name='FLAT_V3_PHYSICAL_FIT_PENDING')
assembly.add(plate,name='PRINT_full_plate',color=cq.Color(.82,.87,.89))
assembly.add(ref,name='REFERENCE_joystick_NOT_PRINTABLE',color=cq.Color(.2,.2,.2))
hardware=[]
for name,(x,y) in layouts['community'].items():
 top=BODY+(2.5 if name=='A' else 2.)
 screw=cq.Workplane('XY').center(x,y).circle(.8).extrude(8).translate((0,0,top-8))
 head=cq.Workplane('XY').center(x,y).circle(1.5).extrude(1.6).translate((0,0,top))
 socket=cq.Workplane('XY').center(x,y).polygon(6,1.5/math.cos(math.pi/6)).extrude(1).translate((0,0,top+.9))
 screw=globalize(screw.union(head.cut(socket)))
 nut=cq.Workplane('XY').center(x,y).polygon(6,3.2/math.cos(math.pi/6)).extrude(1.3).translate((0,0,BOTTOM-1.3))
 nut=globalize(nut.cut(cq.Workplane('XY').center(x,y).circle(.8).extrude(30)))
 for s in (screw,nut):
  assert overlap(plate,s)<.001,(name,'hardware/plate collision')
  assert overlap(ref,s)<.001,(name,'hardware/joystick collision')
  assert overlap(case,s)<.001,(name,'hardware/case collision')
 # Nut sits directly against the flat underside. Existing screws traverse
 # the entire nut, leaving 1.2 mm (A) / 1.7 mm (B) exposed below it.
 assert top-8 < BOTTOM-1.3
 protrusion=(BOTTOM-1.3)-(top-8)
 results.setdefault('screw_tip_below_nut_mm',{})[name]=round(protrusion,3)
 # Check real bearing area underneath the nut, excluding the clearance hole.
 bearing=overlap(plate,nut.translate((0,0,.01)))/.01
 assert bearing>2.,(name,'insufficient nut bearing area',bearing)
 results.setdefault('nut_bearing_area_mm2',{})[name]=round(bearing,3)
 hardware.extend([screw,nut])
 assembly.add(screw,name='BUY_M1_6x8_'+name,color=cq.Color(.5,.52,.55))
 assembly.add(nut,name='BUY_M1_6_nut_'+name,color=cq.Color(.5,.52,.55))
assembly.save(str(OUT/'reference-assembly_NOT_FOR_PRINTING.step'))
# Verify neighboring keycaps against a conservative 18 mm square footprint.
# Static joystick envelope only; actual thumb-cap sweep still needs a fit check.
for x,y in [(9.525,28.575),(28.575,9.525)]:
 cap=box(18,18,12,x,y,TOP)
 v=overlap(cap,ref)
 assert v<.001,'neighbor keycap reference interference'
 for s in hardware:assert overlap(cap,s)<.001,'neighbor keycap hardware interference'
results['source_plate']= 'Unchanged switch, encoder, touch, status LED and M3 case hole geometry outside joystick area.'
results['mounting']='M1.6 x 8 DIN912 screws and exposed M1.6 DIN934 nuts against the flat underside. Two raised seats; no nut pockets or loose shims.'
results['limits']=['Physical fit and stiffness unverified.','Stock thumb-cap shape and full travel not accurately modeled; test in all directions.','Printed hole fit and support heights require physical confirmation.','Exposed screw tips must remain clear of wiring; case check covers the CAD case only.','Full plate withheld from recommended printing until corner fit passes.']
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
# Views are rendered from the actual exported geometry, not an invented image.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(14,5),facecolor='#f7f8fa')
render_faces={}
def draw(ax,shape,color):
 faces,colors=render_faces.setdefault(ax,([],[]))
 for solid in shape.solids().vals():
  vs,ts=solid.tessellate(.06);vs=[v.toTuple() for v in vs]
  for t in ts:
   face=[vs[i] for i in t];faces.append(face)
   a,b,c=np.array(face);n=np.cross(b-a,c-a);n=n/max(np.linalg.norm(n),1e-12)
   light=.58+.32*abs(n[2])+.10*abs(n[0])
   colors.append(tuple(np.array(matplotlib.colors.to_rgb(color))*light))
for i,title in enumerate(['1  Flat plate + two raised tab supports','2  Screws go through the mounting tabs','3  Exposed nuts on a flat underside']):
 ax=fig.add_subplot(1,3,i+1,projection='3d',facecolor='#f7f8fa');draw(ax,corner,'#82b8c9')
 if i in (1,2):
  if i==1:draw(ax,ref,'#41454a')
  for s in hardware:draw(ax,s,'#a9acaf')
 faces,colors=render_faces[ax]
 ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors=(0,0,0,0),linewidth=0,shade=False))
 ax.set(xlim=(15,48),ylim=(15,48),zlim=(16,34));ax.set_box_aspect((33,33,18))
 ax.view_init(elev=-35 if i==2 else 42,azim=135 if i==2 else -55);ax.set_axis_off();ax.set_title(title,fontsize=10)
fig.suptitle('Flat joystick mount · v3 · one small test print',fontsize=17)
fig.text(.5,.04,'No nut boxes. No deep recess. Same screws and nuts. Physical fit still needs checking.',ha='center',fontsize=10)
fig.savefig(ROOT/'preview.png',dpi=160,bbox_inches='tight');plt.close(fig)
print(json.dumps(results,indent=2))
