"""Removable light cup: plate clips with accessible underside release tips.
Experimental PETG fit test; CAD geometry checks do not establish latch strength.
"""
from pathlib import Path
import json, math
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'files';OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'parameters.json').read_text())
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))
def rr(w,d,h,r,x=0,y=0,z=0):return box(w,d,h,x,y,z).edges('|Z').fillet(r)
def vol(a,b):return a.intersect(b).val().Volume()
# Top plate z22..25, clip lands z23.4..25, cup z10.5..22.
# Two symmetric cantilever beams pass through independent floor windows.
# Squeeze both tips from below, away from the wall/pins, to release the cup.
profile=[(7.5,9.1),(8.3,9.1),(8.95,10.4),(8.6,10.4),(8.3,10.7),(8.3,21.7),(8.9,23.4),(8.9,24.0),(7.5,24.0)]
right=cq.Workplane('XZ').polyline(profile).close().extrude(P['clip_width_mm']/2,both=True)
left=right.mirror('YZ');clips=[left,right]
# Plate coupon uses the actual MX opening and underside relief of the full plate.
frame=box(23,23,3,z=22).cut(box(14.1,14.1,5,z=21)).cut(box(16.8,16.8,1.4,z=22))
for clip in clips:frame=frame.union(clip)
cup=rr(18.7,18.7,11.5,1.2,z=10.5).cut(rr(16.3,16.3,12,.7,z=11.7))
for sign in [-1,1]:
 # Through-windows leave a .75 mm retaining lip on the outer floor edge.
 cup=cup.cut(box(1.35,P['clip_width_mm']+.5,13,sign*7.925,0,10.4))
 # Open top notches clear the enlarged clip root, without loading the switch.
 cup=cup.cut(box(3,4,1.3,sign*8.8,0,20.8))
 # Wire exits on the other two walls, separate from the latch movement.
 cup=cup.cut(box(6,3,4.6,0,sign*9,17.5))
# Lower, edge-open wire exit lets insulated LED leads leave the cup.
cup=cup.cut(box(5,4,2,0,-8.6,10.4))
# Exact candidate plate: latest flat-joystick plate plus 12 identical clips.
plate=cq.importers.importStep(str(ROOT/'references/flat-joystick-plate-v3.step'))
centers=[(-9.525,28.575),(9.525,28.575)]+[(x,9.525) for x in [-28.575,-9.525,9.525,28.575]]
for x,y in centers:
 for clip in clips:plate=plate.union(clip.translate((x,y,0)))
results={}
def save(name,shape,flip=False):
 assert shape.val().isValid() and len(shape.solids().vals())==1,name
 cq.exporters.export(shape,str(OUT/f'{name}.step'))
 oriented=shape.rotate((0,0,0),(1,0,0),180) if flip else shape
 b=oriented.val().BoundingBox();oriented=oriented.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
 path=OUT/f'{name}.stl';cq.exporters.export(oriented,str(path),tolerance=.02,angularTolerance=.06)
 mesh=trimesh.load_mesh(path);mesh.merge_vertices(digits_vertex=6);mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
 assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1,name
 mesh.export(path);results[name]={'size_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'watertight':True,'one_solid':True}
save('PRINT_ONE_test_plate_with_clips',frame,True)
save('PRINT_ONE_snap_baffle',cup)
save('WAIT_full_plate_flat_joystick_and_baffle_clips',plate,True)
assert vol(frame,cup)<.001,'cup interferes with seated plate/clips'
# Conservative reference envelopes. Physical switch clips/pins and solder must
# also be trial-fitted: these are NOT a vendor CAD model or a wiring harness.
switch=box(14.2,14.2,5.0,z=18.4)
pin_keepout=box(12,12,3.5,z=14.9)
led=box(9.1,9.1,3.1,z=11.9) # allows 0.2 mm insulation above floor
for name,shape in [('switch_lower_housing',switch),('pin_keepout',pin_keepout),('led_with_insulation',led)]:
 assert vol(cup,shape)<.001,(name,'cup interference')
 for clip in clips:assert vol(clip,shape)<.001,(name,'clip interference')
# Check a prescribed cantilever displacement profile for the .5 mm release
# movement: geometric clearance estimate, not a finite-element stress analysis.
delta=P['release_deflection_mm'];L=23.4-10.4
for z in [14.9+i*.25 for i in range(35)]:
 u=max(0,min(1,(23.4-z)/L));displacement=delta*u*u*(3-u)/2
 assert 7.5-displacement > (7.1 if z>=18.4 else 6.),('release collision',z)
assert 8.95-delta < 8.6,'hook does not clear floor window'
results['estimated_beam_surface_strain_percent']=100*1.5*.8*delta/(L*L)
results['nominal_latch_overlap_mm']=.35
results['nominal_axial_play_mm']=.1
results['release_deflection_mm']=delta
results['seated_cup_overlap_mm3']=vol(frame,cup)
# Hooks obstruct a downward pull while relaxed: positive retention overlap.
results['locked_pull_overlap_mm3']=sum(vol(clip,cup.translate((0,0,-.4))) for clip in clips)
assert results['locked_pull_overlap_mm3']>.01
# Once relaxed arms are absent, the cup has a clear downward path around the
# switch and LED envelopes. The real LED stays connected: service slack needed.
for dz in [0,-1,-4,-8,-12]:
 assert vol(cup.translate((0,0,dz)),switch)<.001
 assert vol(cup.translate((0,0,dz)),pin_keepout)<.001
case=cq.importers.importStep(str(ROOT/'references/case.step'))
results['plate_case_overlap_mm3']=vol(plate,case);assert results['plate_case_overlap_mm3']<.001
allcups=[cup.translate((x,y,0)) for x,y in centers]
for i,c in enumerate(allcups):
 assert vol(c,plate)<.001,(i,'plate/cup interference')
 assert vol(c,case)<.001,(i,'case/cup interference')
 for other in allcups[i+1:]:assert vol(c,other)<.001,'adjacent cups interfere'
results['neighbor_cup_gap_mm']=19.05-18.7
results['limits']=['Physical latch fit, release accessibility, fatigue, print strength and light leakage unverified.','Strain number is a small-deflection beam estimate, not FEA or a material guarantee.','Switch and pin envelopes are approximations; actual switch retention tabs and solder joints require a dry fit.','No six-cup wiring or real LED optical test performed.','Candidate full plate requires supports in the supplied face-down orientation because the joystick seats protrude on its face.','Only print the TWO small test parts first; keep all older plates until fit passes.']
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
asm=cq.Assembly(name='SNAP_BAFFLE_FIT_SAMPLE_UNVERIFIED')
asm.add(frame,name='PRINT_test_plate',color=cq.Color(.8,.87,.9));asm.add(cup,name='PRINT_removable_cup',color=cq.Color(.14,.15,.16));asm.add(switch,name='REFERENCE_lower_switch_envelope',color=cq.Color(.5,.6,.62));asm.add(led,name='REFERENCE_LED_envelope',color=cq.Color(.8,.65,.12));asm.save(str(OUT/'reference_fit_assembly_NOT_PRINTABLE.step'))
# Actual CAD views, with clip color highlighted for assembly learning.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(13,5),facecolor='#f7f8fa');geometry={}
def draw(ax,s,color):
 faces,colors=geometry.setdefault(ax,([],[]))
 for solid in s.solids().vals():
  vs,ts=solid.tessellate(.06);vs=[v.toTuple() for v in vs]
  for t in ts:
   f=[vs[i] for i in t];faces.append(f);a,b,c=np.array(f);n=np.cross(b-a,c-a);n=n/max(np.linalg.norm(n),1e-12)
   colors.append(tuple(np.array(matplotlib.colors.to_rgb(color))*(.60+.3*abs(n[2])+.1*abs(n[0]))))
for i,title in enumerate(['1  Two clips belong to the plate','2  Cup slides up over the clips','3  Pinch the two tips underneath']):
 ax=fig.add_subplot(1,3,i+1,projection='3d',facecolor='#f7f8fa')
 plain=frame
 for clip in clips:plain=plain.cut(clip)
 draw(ax,plain,'#a5cbd6')
 for clip in clips:draw(ax,clip,'#dc9b38')
 if i:draw(ax,cup.translate((0,0,-7 if i==1 else 0)),'#555d67')
 faces,colors=geometry[ax];ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors=(0,0,0,0),linewidth=0))
 ax.set(xlim=(-13,13),ylim=(-13,13),zlim=(1,26));ax.set_box_aspect((26,26,25));ax.view_init(elev=-25,azim=-65);ax.set_axis_off();ax.set_title(title,fontsize=11)
fig.suptitle('Removable light baffle · experimental fit sample',fontsize=18)
fig.text(.5,.03,'Gold highlights the flexible clips. They print as part of the plate. Test the empty cup before adding a switch or LED.',ha='center',fontsize=10)
fig.savefig(ROOT/'preview.png',dpi=160,bbox_inches='tight');plt.close(fig)
print(json.dumps(results,indent=2))
