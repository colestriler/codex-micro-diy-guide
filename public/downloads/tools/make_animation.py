"""Build an offline 3D assembly player from the exported, assembled-coordinate STEP parts."""
from pathlib import Path
import base64, json
import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
geometries = {}
for p in sorted((ROOT/'step').glob('0*.step')):
    shape = cq.importers.importStep(str(p)).val()
    assert shape.isValid()
    verts, faces = shape.tessellate(.12, .12)
    vertices = np.asarray([v.toTuple() for v in verts], dtype='<f4')
    indices = np.asarray(faces, dtype='<u4').ravel()
    geometries[p.stem[:2]] = {
        'vertices': base64.b64encode(vertices.tobytes()).decode(),
        'indices': base64.b64encode(indices.tobytes()).decode(),
        'file': p.name,
    }
assert len(geometries) == 9
page = (ROOT/'animation/assembly-template.html').read_text()
for key, value in {
    '__THREE__': (ROOT/'animation/three.min.js').read_text(),
    '__GEOMETRY__': json.dumps(geometries, separators=(',', ':')),
    '__PLAYER__': (ROOT/'animation/assembly.js').read_text(),
}.items():
    page = page.replace(key, value)
assert not any(k in page for k in ['<script>__THREE__</script>', '__GEOMETRY__', '__PLAYER__'])
(ROOT/'assembly-animation.html').write_text(page)
print(f'Built assembly-animation.html: {len(page)/1e6:.2f} MB; 9 actual STEP geometries embedded')
