#!/usr/bin/env python3
"""
Check that every mesh under a hardware folder is watertight with a positive volume.

Usage:  python hardware/cad/check_meshes.py [HARDWARE_DIR]
HARDWARE_DIR defaults to the folder above this script. It scans stl/*.stl, 3mf/*.3mf and
cad/build/*.stl (the build folder exists after running the generator scripts).
Exit code 1 if any mesh fails or none is found.
"""
import sys
from pathlib import Path
import trimesh

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
files = sorted([*root.glob('stl/*.stl'), *root.glob('3mf/*.3mf'), *root.glob('cad/build/*.stl')])
if not files:
    sys.exit(f'no meshes found under {root}')
failed = []
for f in files:
    m = trimesh.load(f, force='mesh')
    ok = bool(m.is_watertight) and m.volume > 0
    print(f"{'ok  ' if ok else 'FAIL'} {f.relative_to(root)}  watertight={m.is_watertight} volume={m.volume / 1000:.3f} cm3")
    if not ok:
        failed.append(f)
print(f'{len(files) - len(failed)}/{len(files)} meshes watertight')
sys.exit(1 if failed else 0)
