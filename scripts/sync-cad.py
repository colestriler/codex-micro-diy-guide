"""Publish regenerated CAD to the website viewer, catalog, offline guide and ZIP.

Run with the CAD Python environment after cad/build.py, tools/verify.py,
tools/render.py and tools/make_animation.py in public/downloads/.
"""
from pathlib import Path
import base64
import json
import subprocess
import sys
import zipfile

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / 'public/downloads'

geometry = {}
for path in sorted((DOWNLOADS / 'step').glob('0*.step')):
    shape = cq.importers.importStep(str(path)).val()
    assert shape.isValid(), path.name
    vertices, faces = shape.tessellate(.12, .12)
    geometry[path.stem[:2]] = {
        'vertices': base64.b64encode(np.asarray([v.toTuple() for v in vertices], dtype='<f4').tobytes()).decode(),
        'indices': base64.b64encode(np.asarray(faces, dtype='<u4').ravel().tobytes()).decode(),
        'file': path.name,
    }
assert len(geometry) == 9
(ROOT / 'viewer-src/geometry.json').write_text(json.dumps(geometry, separators=(',', ':')) + '\n')

parts = json.loads((DOWNLOADS / 'docs/parts.json').read_text())
files_path = ROOT / 'data/files.json'
files = json.loads(files_path.read_text())
for entry in files:
    part = parts[entry['id']]
    entry.update(quantity=part['qty'], note=part['notes'], size=part['bounds_mm'])
files_path.write_text(json.dumps(files, indent=2) + '\n')

subprocess.run([sys.executable, str(DOWNLOADS / 'tools/make_guide.py')], check=True)
paths = sorted(path for path in DOWNLOADS.rglob('*')
               if path.is_file() and path.name != 'build-files.zip'
               and '__pycache__' not in path.parts and path.name != '.DS_Store')
with zipfile.ZipFile(DOWNLOADS / 'build-files.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in paths:
        archive.write(path, Path('codex-micro-diy') / path.relative_to(DOWNLOADS))
with zipfile.ZipFile(DOWNLOADS / 'build-files.zip') as archive:
    assert archive.testzip() is None
    for path in paths:
        assert archive.read(str(Path('codex-micro-diy') / path.relative_to(DOWNLOADS))) == path.read_bytes()
print(f'Synced 9 viewer geometries, {len(files)} file entries and {len(paths)} verified ZIP entries.')
