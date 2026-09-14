"""COM-09426 bench fit sample. Install requirements.txt, then run python build.py.

Dimensions are mm. Fits are provisional until checked against the user's part.
This tests joystick retention, not attachment to the keyboard top plate.
"""
from pathlib import Path
import json, math, zipfile
import cadquery as cq

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'files'
OUT.mkdir(exist_ok=True)
CENTERS = {'A': (-8.61, 8.97), 'B': (-7.44, -10.15)}
BODY_Z = 7.0

def box(w, d, h, x=0, y=0, z=0):
    return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))

def slot(length, width, h, x, y, z):
    return cq.Workplane('XY').slot2D(length,width).extrude(h).translate((x,y,z))

def roundbox(w,d,h,r,x=0,y=0,z=0):
    return box(w,d,h,x,y,z).edges('|Z').fillet(r)

# Solid bottom prints flat; small side nut tunnels bridge only 3.5 mm.
holder = roundbox(26.5,26.5,5,1.5)
# Open U-shaped passage: contact pads at the front, existing wire hole behind.
wire_void = roundbox(9,23,12,1,x=0,y=4.5,z=-1)
holder = holder.cut(wire_void)
for x in (-7,7):
    for y in (-3,3):
        holder = holder.union(box(3,3,2,x,y,5))
# Low locating stops, loose enough to avoid using interference as retention.
for x in (-9.8,9.8):
    holder = holder.union(box(.8,5,2.8,x,0,5))
holder = holder.union(box(5,.8,2.8,0,-9.8,5))
for name,(x,y) in CENTERS.items():
    holder = holder.union(roundbox(6.4,5.4,2,.5,x,y,5))
    # M1.6 hex nut: 3.2 mm across flats, ~1.3 mm high. Side insertion.
    left = -14
    holder = holder.cut(box(x+3-left,3.5,1.6,(left+x+3)/2,y,1.9))
    # Clearance slot permits X adjustment; Y clearance covers source offsets.
    # Blind at z=.6, retaining a closed bottom below screw tips.
    holder = holder.cut(slot(3.2,2.1,12,x,y,.6))

# Shims occupy only the ears' area, excluding the chamfered housing outline.
outline = [(-5.6,-9.55),(5.6,-9.55),(9.55,-5.6),(9.55,5.6),
           (5.6,9.55),(-5.6,9.55),(-9.55,5.6),(-9.55,-5.6)]
keepout = cq.Workplane('XY').polyline(outline).close().extrude(5).translate((0,0,-1))
shims = {}
for name,(x,y) in CENTERS.items():
    for height in (.5,1.0):
        s = roundbox(6.2,5.2,height,.4,x,y).cut(keepout)
        s = s.cut(slot(3.2,2.1,3,x,y,-1))
        shims[f'shim_{name}_{height:.1f}mm'] = s

def save(name, shape):
    solids=shape.solids().vals()
    assert len(solids)==1, (name,'must be one connected solid',len(solids))
    assert shape.val().isValid(), name
    assert shape.val().Volume()>0, name
    b=shape.val().BoundingBox()
    printed=shape.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
    cq.exporters.export(printed,str(OUT/f'{name}.stl'),tolerance=.015,angularTolerance=.08)
    cq.exporters.export(shape,str(OUT/f'{name}.step'))
    return {'volume_mm3':shape.val().Volume(),'size_mm':[b.xlen,b.ylen,b.zlen]}

results={'holder':save('holder',holder)}
for name,s in shims.items():results[name]=save(name,s)

# Community reference. Rotation maps native STEP X/Z plan into SparkFun's XY.
ref = cq.importers.importStep(str(ROOT/'references/marbastlib-PNT_psp1000.step'))
ref = ref.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90)
ref = ref.translate((-9.25,-9.25,BODY_Z))
assembly=cq.Assembly(name='COM09426_UNVERIFIED_FIT_SAMPLE')
assembly.add(holder,name='PRINT_holder',color=cq.Color(.18,.60,.75))
assembly.add(ref,name='REFERENCE_community_joystick_NOT_PRINTABLE',color=cq.Color(.2,.2,.2))
for n in ['shim_A_0.5mm','shim_B_1.0mm']:
    assembly.add(shims[n].translate((0,0,BODY_Z)),name='PRINT_'+n,color=cq.Color(.98,.65,.16))
hardware=[]
for name,x,y,top in [('A',-8.328428,8.95,9.5),('B',-7.5,-10.232119,9.0)]:
    screw=cq.Workplane('XY').center(x,y).circle(.8).extrude(8).translate((0,0,top-8))
    head=cq.Workplane('XY').center(x,y).circle(1.5).extrude(1.6).translate((0,0,top))
    socket=cq.Workplane('XY').center(x,y).polygon(6,1.5/math.cos(math.pi/6)).extrude(1).translate((0,0,top+.9))
    screw=screw.union(head.cut(socket))
    nut=cq.Workplane('XY').center(x,y).polygon(6,3.2/math.cos(math.pi/6)).extrude(1.3).translate((0,0,2.2))
    nut=nut.cut(cq.Workplane('XY').center(x,y).circle(.8).extrude(5))
    assert holder.intersect(nut).val().Volume()<.001,(name,'nut collision')
    assert holder.intersect(screw).val().Volume()<.001,(name,'screw collision')
    hardware.extend([screw,nut])
    assembly.add(screw,name='BUY_M1_6x8_screw_'+name,color=cq.Color(.5,.52,.55))
    assembly.add(nut,name='BUY_M1_6_nut_'+name,color=cq.Color(.6,.6,.62))
assembly.save(str(OUT/'reference-assembly.step'))

# Actual reference geometry must not intersect the printed support surfaces.
results['reference_overlap_mm3'] = holder.intersect(ref).val().Volume()
assert results['reference_overlap_mm3'] < .001, results['reference_overlap_mm3']
for n in ['shim_A_0.5mm','shim_B_1.0mm']:
    v=shims[n].translate((0,0,BODY_Z)).intersect(ref).val().Volume()
    results[n]['reference_overlap_mm3']=v
    assert v<.001,(n,v)

# Check full M1.6 shaft clearance at both documented hole layouts.
layouts={'SparkFun':{'A':(-8.89,8.985),'B':(-7.375,-10.06)},
         'marbastlib':{'A':(-8.328428,8.95),'B':(-7.5,-10.232119)}}
for source,points in layouts.items():
    for name,(x,y) in points.items():
        shaft=cq.Workplane('XY').center(x,y).circle(.8).extrude(9).translate((0,0,1))
        v=holder.intersect(shaft).val().Volume()
        assert v<.001,(source,name,'shaft obstruction',v)

# M1.6x8 modeled stack: ear tops z9.5 (A), z9 (B), screw ends z1.5 and z1.
# Both clear the .6 floor and traverse the full nominal nut z1.9..3.2.
for ear_top in (9.5,9.0):
    tip=ear_top-8
    assert .6<tip<1.9
# Screw heads: nominal DIN912 M1.6, 3 mm diameter, 1.6 mm tall.
for name,(x,y) in layouts['marbastlib'].items():
    top=9.5 if name=='A' else 9.0
    head=cq.Workplane('XY').center(x,y).circle(1.5).extrude(1.6).translate((0,0,top))
    assert head.intersect(ref).val().Volume()<.001,(name,'head collision')
results['validation']='CAD checks only; physical fit and printed nut pockets unverified'
(ROOT/'validation.json').write_text(json.dumps(results,indent=2))

# Render from tessellated solids, preserving the actual CAD geometry.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(12,6),facecolor='#f7f8fa')
render_faces={}
def draw(ax,shape,color):
    faces,colors=render_faces.setdefault(ax,([],[]))
    for solid in shape.solids().vals():
        vertices,triangles=solid.tessellate(.05)
        vs=[v.toTuple() for v in vertices]
        faces.extend([[vs[i] for i in t] for t in triangles])
        colors.extend([color]*len(triangles))
for i,title in enumerate(['1  Printed holder + removable spacers','2  Joystick seated (reference model)']):
    ax=fig.add_subplot(1,2,i+1,projection='3d',facecolor='#f7f8fa')
    draw(ax,holder,'#5aa8c2')
    for n in ['shim_A_0.5mm','shim_B_1.0mm']:
        draw(ax,shims[n].translate((0,0,BODY_Z)),'#efb449')
    if i:
        draw(ax,ref,'#4b5058')
        for part in hardware:draw(ax,part,'#b4bac1')
    else:
        for name,(x,y) in CENTERS.items():
            ax.text(x,y,12,name,fontsize=16,fontweight='bold',color='#202936',ha='center')
    faces,colors=render_faces[ax]
    ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors=(0,0,0,.04),
                        linewidth=.08,shade=True,
                        lightsource=matplotlib.colors.LightSource(azdeg=135,altdeg=45)))
    ax.set(xlim=(-15,15),ylim=(-15,15),zlim=(0,18))
    ax.set_box_aspect((30,30,18));ax.view_init(elev=38,azim=125);ax.set_axis_off()
    ax.set_title(title,fontsize=12,pad=0)
fig.suptitle('Joystick mounting fit sample • v1',fontsize=19,y=.96)
fig.text(.5,.08,'Side-loading M1.6 nuts • adjustable screw slots • open wire passage',ha='center',fontsize=12)
fig.text(.5,.035,'26.5 × 26.5 mm base. Community joystick geometry; physical fit still needs checking.',ha='center',fontsize=10,color='#586274')
fig.savefig(ROOT/'preview.png',dpi=160,bbox_inches='tight');plt.close(fig)
print(json.dumps(results,indent=2))
