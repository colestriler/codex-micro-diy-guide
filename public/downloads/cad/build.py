"""Parametric DIY reconstruction of the Codex Micro visual layout, millimetres.
Run from any directory: .venv/bin/python cad/build.py
OEM case dimensions and joystick seating geometry are not verified.
STLs are in print orientation. STEP parts and assembly use assembled coordinates.
"""
from pathlib import Path
import json, math
import cadquery as cq
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT/'cad/parameters.json').read_text())
PARTS = {}
VISUALS = []
H=P['case_height']; PT=P['plate_thickness']; PZ=H-PT; pitch=P['key_pitch']
C=[-1.5*pitch,-.5*pitch,.5*pitch,1.5*pitch]
R=list(reversed(C))
POSITIONS=[(r,c,C[c],R[r]) for r in range(4) for c in range(4) if (r,c) not in [(0,0),(0,3),(3,0)]]
AGENTS=[(C[1],R[0]),(C[2],R[0])]+[(x,R[1]) for x in C]
screw=P['case_screw_xy']; SCREWS=[(x,y) for x in (-screw,screw) for y in (-screw,screw)]

def box(w,d,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))
def rr(w,d,h,r,x=0,y=0,z=0):
    return box(w,d,h,x,y,z).edges('|Z').fillet(r)
def cyl(d,h,x=0,y=0,z=0):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z))
def save(name,shape,print_shape=None,qty=1,color=(.8,.8,.8),notes=''):
    assert shape.val().isValid(),name+' invalid BRep'
    assert len(shape.solids().vals()) == 1, name+' must be one solid'
    if print_shape is None:
        print_shape=shape.translate((0,0,-shape.val().BoundingBox().zmin))
    exporters.export(shape,str(ROOT/'step'/f'{name}.step'))
    exporters.export(print_shape,str(ROOT/'stl'/f'{name}.stl'),tolerance=.04,angularTolerance=.08)
    # Remove degenerate seam triangles introduced by STEP-to-STL tessellation.
    import trimesh
    path=ROOT/'stl'/f'{name}.stl'
    mesh=trimesh.load_mesh(path)
    mesh.merge_vertices(digits_vertex=6)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_volume, name+' invalid exported mesh'
    mesh.export(path)
    b=print_shape.val().BoundingBox()
    PARTS[name]={'qty':qty,'bounds_mm':[round(v,3) for v in (b.xlen,b.ylen,b.zlen)],'volume_mm3':round(shape.val().Volume(),2),'notes':notes}
    return shape

# Base tray: broad recessed bezel, corner insert pillars, underside foot mounts.
case=rr(P['case_width'],P['case_depth'],H,P['case_corner_radius'])
case=case.cut(rr(98,98,H,9,z=P['floor_thickness']))
# Restore the narrow upper ledge that supports the face plate.
ledge=rr(102,102,PT,10,z=PZ).cut(rr(P['plate_width']+2*P['plate_gap_per_side'],P['plate_width']+2*P['plate_gap_per_side'],PT+2,5.25,z=PZ-1))
case=case.union(ledge)
for x,y in SCREWS:
    case=case.union(cyl(8,PZ,x,y)).cut(cyl(P['insert_hole_diameter'],P['insert_depth']+.1,x,y,PZ-P['insert_depth']))
    case=case.cut(cyl(3.3,2.2,x,y,PZ-P['insert_depth']-2))
# Oversized cable tunnel allows access to the real controller's USB-C receptacle.
case=case.cut(rr(15,16,8,2,x=0,y=52,z=4))
# Controller locators leave solder pads exposed; board is secured with removable tape.
for x in (-10.3,10.3):
    case=case.union(box(1.6,29,3.6,x=x,y=30,z=2.4))
case=case.union(box(22.2,1.6,3.6,y=11.5,z=2.4))
for x in (-25,25):
    case=case.union(cyl(9,7.2,x,0)).cut(cyl(P['insert_hole_diameter'],P['insert_depth']+.1,x,0,z=-.1))
    case=case.cut(cyl(3.3,2,x,0,z=P['insert_depth']))
# Eight internal pockets leave a 0.8 mm translucent outer skin for perimeter light.
for sign in (-1,1):
    for t in (-22,22):
        case=case.cut(box(12,6.2,11,x=t,y=sign*51.1,z=3.5))
        case=case.cut(box(6.2,12,11,x=sign*51.1,y=t,z=3.5))
save('01_case',case,color=(.81,.85,.88),notes='Open side up; supports in USB tunnel only if your slicer needs them.')

# Faceplate, with locally thin MX retaining lands under the switch clips.
plate=rr(P['plate_width'],P['plate_width'],PT,5,z=PZ)
for r,c,x,y in POSITIONS:
    plate=plate.cut(box(P['switch_cutout'],P['switch_cutout'],PT+2,x,y,PZ-1))
    plate=plate.cut(box(16.8,16.8,PT-P['switch_clip_thickness']+.01,x,y,PZ-.01))
for x,y in SCREWS:plate=plate.cut(cyl(3.4,PT+2,x,y,PZ-1))
plate=plate.cut(cyl(P['encoder_hole_diameter'],PT+2,C[0],R[0],PZ-1))
# Anti-rotation locator pocket on underside, reserved for encoder tang.
plate=plate.cut(box(2.4,2.8,1.6,C[0],R[0]+7.5,PZ-.01))
# Joystick cradle sits in a shallow, keyed square recess. Slot admits its cable.
jx,jy=P['joystick_center']; cradle_outer=P['joystick_pocket']+1.8
plate=plate.cut(rr(cradle_outer+.4,cradle_outer+.4,1.01,2.1,jx,jy,H-1))
plate=plate.cut(box(6,5,PT+2,jx,jy-3,PZ-1))
# Touch disk and three status LED lenses.
plate=plate.cut(cyl(16.2,PT+2,C[0],R[3],PZ-1))
for y in (-24.5,-29,-33.5):plate=plate.cut(cyl(3.2,PT+2,-41,y,PZ-1))
# Invert for smooth visible face on bed; all underside clip recesses face upward.
plate_print=plate.rotate((0,0,0),(1,0,0),180).translate((0,0,H))
save('02_switch_plate',plate,plate_print,notes='Visible face DOWN. 1.6 mm switch clip lands, 3 mm structural plate.')

# Circular detachable foot with four optional M8 fender washer ballast pockets.
foot=cyl(P['foot_diameter'],P['foot_height'],z=-P['foot_height'])
for x in (-20,20):
    for y in (-20,20):foot=foot.cut(cyl(24.6,2.41,x,y,-2.4))
for x in (-25,25):
    foot=foot.cut(cyl(3.4,7,x,0,-6)).cut(cyl(6.3,1.81,x,0,-5.01))
save('03_round_foot',foot,notes='Flat bottom DOWN. Washer pockets face up; secure washers with tape before assembly.')

# PSP slide joystick tray, bonded into the faceplate pocket after test fitting.
cradle=rr(cradle_outer,cradle_outer,3.6,2,jx,jy,H-1)
cradle=cradle.cut(rr(P['joystick_pocket'],P['joystick_pocket'],3,1.1,jx,jy,H+.6))
cradle=cradle.cut(box(6,5,6,jx,jy-3,H-2))
cradle=cradle.cut(box(5,5,3,jx,jy-cradle_outer/2,H+.8))
save('04_joystick_cradle',cradle,notes='Pocket 19.8 mm. Vendor does not publish a controlled drawing; fit-check actual joystick.')

# Touch cap is fixed; copper foil is bonded to its underside (no switch).
touch=cyl(18.8,1.0,C[0],R[3],PZ-1).union(cyl(15.8,PT+.05,C[0],R[3],PZ))
touch=touch.cut(cyl(13.8,PT+1-.8+.01,C[0],R[3],PZ-1-.01))
save('05_touch_cap',touch,touch.rotate((0,0,0),(1,0,0),180).translate((-C[0],R[3],H+.05)),notes='Visible face DOWN. Bond 13 mm copper disk immediately beneath the 0.8 mm top skin.')

# Encoder knob: nut clearance, 6 mm D-shaft socket, and central finger ridge.
knob=cyl(17.8,11.5,C[0],R[0],H+1.0)
knob=knob.union(box(2.4,15,2,C[0],R[0],H+12.5))
knob=knob.cut(cyl(10.8,3.2,C[0],R[0],H+.99))
shaft=cyl(P['knob_shaft_diameter'],6.8,C[0],R[0],H+4.1)
shaft=shaft.intersect(box(P['knob_shaft_diameter']/2+P['knob_shaft_flat_x'],8,8,C[0]+(P['knob_shaft_flat_x']-P['knob_shaft_diameter']/2)/2,R[0],H+4))
knob=knob.cut(shaft).translate((0,0,1.3))
save('06_encoder_knob',knob,notes='Socket DOWN; short bridging above nut pocket. Trial fit the D socket before pressing fully. Adhesive optional after testing.')

# Six light baffles: black plastic, side wiring notches and recessed LED floor.
# Baffles are individual adhesive-mounted cups; top rim meets faceplate underside.
pod=rr(18.7,18.7,11.5,1.2,z=10.5).cut(rr(16.3,16.3,10.4,.7,z=11.7))
pod=pod.cut(box(10,4,2.6,y=-5,z=10.4))
for x in (-9,9):pod=pod.cut(box(3,5,4.5,x,0,17.6))
save('07_led_baffle',pod,qty=6,notes='Black filament, cavity UP. LED PCB on floor, insulated pads underneath. Six identical cups.')

# 1U keycaps and dual-MX-stem 2U cap: printable, trial fit required for cross sockets.
def keycap(w,stems):
    cap=rr(w,18,6,3,z=0)
    cap=cap.cut(rr(w-2.8,15.2,4.2,2,z=-.01))
    # Shallow bowl; the wide cap uses a capsule-shaped dish.
    scoop=cq.Workplane('XY').sphere(42).translate((0,0,47.3))
    if len(stems)>1:
        span=max(stems)-min(stems)
        scoop=cq.Workplane('YZ').circle(42).extrude(span).translate((-span/2,0,47.3))
        for x in stems:
            scoop=scoop.union(cq.Workplane('XY').sphere(42).translate((x,0,47.3)))
    cap=cap.cut(scoop)
    for x in stems:
        cap=cap.union(cyl(6.0,4.9,x,0,-.6))
        a=P['mx_stem_cross_length'];b=P['mx_stem_cross_width']
        cross=box(a,b,4.1,x,0,-.61).union(box(b,a,4.1,x,0,-.61))
        cap=cap.cut(cross)
    return cap
cap=keycap(P['keycap_width'],[0])
cap2=keycap(P['keycap_width']+pitch,[-pitch/2,pitch/2])
save('08_keycap_1u',cap,qty=11,notes='Prototype cap: 6 translucent and 5 white. Support only cavity roofs, keep sockets clear. Bought MX caps feel better.')
save('09_keycap_2u_dual_stem',cap2,notes='Two MX stems spaced 19.05 mm; uses two switches, NOT a conventional centered 2U stabilizer.')

# Fit coupon: three switch cutouts and three stem sockets plus encoder hole and insert well.
coupon=box(66,24,3)
for i,size in enumerate((14.0,14.1,14.2)):
    x=(i-1)*21
    coupon=coupon.cut(box(size,size,5,x,0,-1)).cut(box(16.8,16.8,1.4,x,0,-.01))
save('10_switch_fit_coupon',coupon,coupon.rotate((0,0,0),(1,0,0),180).translate((0,0,3)),notes='Left/middle/right from top: 14.0 / 14.1 / 14.2 mm. Choose snug clip fit before full print.')
coupon2=box(62,18,7)
for i,delta in enumerate((-.05,0,.05)):
    x=-22+i*13; a=P['mx_stem_cross_length']+delta;b=P['mx_stem_cross_width']+delta
    coupon2=coupon2.cut(box(a,b,4.1,x,0,-.01).union(box(b,a,4.1,x,0,-.01)))
coupon2=coupon2.cut(cyl(P['insert_hole_diameter'],4.31,24,0,-.01))
save('11_stem_insert_coupon',coupon2,coupon2.rotate((0,0,0),(1,0,0),180).translate((0,0,7)),notes='Cross fits -0.05 / nominal / +0.05, then 3.9 mm insert pocket. Sockets UP for inspection.')

# STEP assembly contains real printable parts plus distinctly named reference envelopes.
asm=cq.Assembly(name='DIY_Micro_Rev_A')
for name,s,col in [('case',case,(.84,.87,.89)),('switch_plate',plate,(.88,.90,.91)),('round_foot',foot,(.67,.69,.72)),('joystick_cradle',cradle,(.16,.17,.19)),('touch_cap',touch,(.06,.06,.07)),('encoder_knob',knob,(.95,.95,.92))]:
    asm.add(s,name=name,color=cq.Color(*col)); VISUALS.append((name,s,col))
for i,(x,y) in enumerate(AGENTS):
    s=pod.translate((x,y,0));asm.add(s,name=f'light_baffle_{i+1}',color=cq.Color(.12,.13,.14))
    # Entire module envelope, with room below the switch pins.
    led=box(9.1,9.1,3.1,x,y,11.7);asm.add(led,name=f'REF_RGBW_LED_{i+1}',color=cq.Color(.22,.65,.8))
for r,c,x,y in POSITIONS:
    switch=box(14,14,8.3,x,y,H-8.3)
    asm.add(switch,name=f'REF_MX_switch_R{r+1}C{c+1}',color=cq.Color(.3,.3,.34))
    if r==3 and c in (1,2):continue
    col=(.6,.73,.8) if (x,y) in AGENTS else (.94,.94,.9)
    s=cap.translate((x,y,H+5.5));asm.add(s,name=f'keycap_R{r+1}C{c+1}',color=cq.Color(*col));VISUALS.append(('key',s,col))
s=cap2.translate((0,R[3],H+5.5));asm.add(s,name='wide_keycap',color=cq.Color(.94,.94,.9));VISUALS.append(('wide',s,(.94,.94,.9)))
joy=rr(19,19,5,1,jx,jy,H+.6).union(cyl(14,4,jx,jy,H+5.6))
asm.add(joy,name='REF_PSP_joystick_envelope',color=cq.Color(.06,.06,.07));VISUALS.append(('joystick',joy,(.06,.06,.07)))
board=box(17.8,35,4.9,0,31,4)
asm.add(board,name='REF_KB2040_envelope',color=cq.Color(.09,.1,.12))
for x,y in SCREWS:
    s=cyl(5.5,2.5,x,y,H);VISUALS.append(('screw',s,(.12,.13,.14)))
    asm.add(s,name=f'REF_screw_{x}_{y}',color=cq.Color(.12,.13,.14))
for y in (-24.5,-29,-33.5):VISUALS.append(('indicator',cyl(2.8,.8,-41,y,H),(.7,.85,.21)))
asm.export(str(ROOT/'step/assembly.step'))
(ROOT/'docs/parts.json').write_text(json.dumps(PARTS,indent=2)+'\n')
# Simplified envelopes checked against case for impossible placement.
checks={'case_valid':case.val().isValid(),'plate_valid':plate.val().isValid(),'printed_parts':len(PARTS),'switches':len(POSITIONS),'agent_leds':len(AGENTS),'perimeter_leds':8,'case_plate_intersection_mm3':case.intersect(plate).val().Volume() if case.intersect(plate).solids().size() else 0,'controller_case_intersection_mm3':case.intersect(board).val().Volume() if case.intersect(board).solids().size() else 0}
(ROOT/'docs/cad_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
# Mesh scene for local review/export; no externally hosted viewer dependency.
import trimesh
scene=trimesh.Scene()
for i,(name,s,color) in enumerate(VISUALS):
    vs,fs=s.val().tessellate(.15)
    mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in vs],faces=fs,process=False)
    mesh.visual.face_colors=[int(c*255) for c in color]+[255]
    scene.add_geometry(mesh,node_name=f'{name}_{i}')
scene.export(str(ROOT/'cad/preview.glb'))
print('Exported 11 STL/STEP parts, assembly and preview.')
