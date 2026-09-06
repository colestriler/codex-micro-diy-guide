"""Offline geometry, fit-envelope and input-state checks; no hardware claims."""
from pathlib import Path
import json,sys,itertools,ast
import trimesh
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'firmware'))
from logic import KeyState,direction,rgbw
checks=[]
for p in sorted((ROOT/'stl').glob('*.stl')):
    m=trimesh.load_mesh(p)
    assert m.is_watertight,p.name+' not watertight'
    assert m.is_volume,p.name+' invalid mesh volume'
    assert len(m.split())==1,p.name+' disconnected pieces'
    assert m.bounds[0,2]>=-.03,p.name+' below print bed'
    checks.append({'file':p.name,'watertight':True,'single_solid':True,'size_mm':m.extents.round(2).tolist()})
parts={p.stem:cq.importers.importStep(str(p)) for p in (ROOT/'step').glob('*.step') if p.name!='assembly.step'}
for name,s in parts.items():assert s.val().isValid(),name+' bad STEP'
pairs=[('01_case','02_switch_plate'),('01_case','03_round_foot'),('02_switch_plate','04_joystick_cradle'),('02_switch_plate','05_touch_cap'),('02_switch_plate','06_encoder_knob')]
collisions=[]
for a,b in pairs:
    intersect=parts[a].intersect(parts[b]);volume=sum(s.Volume() for s in intersect.solids().vals())
    assert volume < .05,(a,b,volume)
    collisions.append({'a':a,'b':b,'intersection_mm3':round(volume,6)})
# A wide key must emit one down and one up, independent of switch event order.
for down_order in [(13,14),(14,13)]:
    for up_order in [(13,14),(14,13)]:
        k=KeyState();events=[k.update(n,True) for n in down_order]+[k.update(n,False) for n in up_order]
        assert [e for e in events if e is not None]==[(10,True),(10,False)]
k=KeyState();assert k.update(0,True) is None
assert k.update(1,True)==(0,True);assert k.update(1,True) is None;assert k.update(1,False)==(0,False)
assert direction(32768,32768,(32768,32768)) is None
assert direction(45000,32768,(32768,32768))=='right'
assert direction(32768,32768,(32768,32768),'right') is None
assert rgbw([0,120,255])==(0,120,255,0)
for bad in [[-1,0,0],[0,0,256],[0,0],['x',0,0]]:
    try:rgbw(bad)
    except ValueError:pass
    else:raise AssertionError(bad)
for p in (ROOT/'firmware').glob('*.py'):ast.parse(p.read_text())
report={'stl_checks':checks,'step_valid':True,'assembly_pair_checks':collisions,'input_state_tests':'passed','firmware_syntax':'passed','physical_print_test':'NOT PERFORMED','hardware_electrical_test':'NOT PERFORMED','native_codex_integration':'NOT IMPLEMENTED','oem_donor_fit':'NOT VERIFIED'}
(ROOT/'docs/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('stl_checks','assembly_pair_checks')},indent=2))
print('Validated',len(checks),'STLs and',len(parts),'STEP parts')
