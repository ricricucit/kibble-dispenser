#!/usr/bin/env python3
"""
Check that every mesh under a hardware folder is a closed solid with a positive volume.

Usage:  python hardware/cad/check_meshes.py [HARDWARE_DIR] [--skip GLOB ...]
HARDWARE_DIR defaults to the folder above this script (prototype 1); pass hardware/v6 or hardware/v6.2 for those
designs. --skip leaves out meshes whose path relative to HARDWARE_DIR matches a glob (listed in the output).
It scans stl/*.stl, 3mf/*.3mf, assembly/*.stl and cad/build/*.stl (the build folder exists after
running the generator scripts).

A mesh passes when it is watertight (every edge shared by exactly two faces), or when it is closed
but two bodies in it touch along an edge (every edge shared by an even number of faces, for example
raised lettering that meets the part on a line). Slicers print both; the second kind is reported
with the number of shared edges. A mesh with an open edge, or a zero or negative volume, fails.
Exit code 1 if any mesh fails or none is found.
"""
import fnmatch
import sys
from pathlib import Path

import numpy as np
import trimesh

args, skip = [], []
it = iter(sys.argv[1:])
for a in it:
    if a == '--skip':
        skip.append(next(it))
    else:
        args.append(a)
root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
files = sorted([*root.glob('stl/*.stl'), *root.glob('3mf/*.3mf'), *root.glob('assembly/*.stl'),
                *root.glob('cad/build/*.stl')])
skipped = [f for f in files if any(fnmatch.fnmatch(str(f.relative_to(root)), g) for g in skip)]
for f in skipped:
    print(f'skip {f.relative_to(root)}')
files = [f for f in files if f not in skipped]
if not files:
    sys.exit(f'no meshes found under {root}')
failed, touching = [], 0
for f in files:
    m = trimesh.load(f, force='mesh')
    _, counts = np.unique(m.edges_sorted, axis=0, return_counts=True)
    closed = len(counts) > 0 and bool(np.all(counts % 2 == 0))
    shared = int(np.count_nonzero(counts > 2))
    ok = closed and m.volume > 0
    note = f'watertight={m.is_watertight}' if not shared else f'closed, {shared} edges shared by touching bodies'
    print(f"{'ok  ' if ok else 'FAIL'} {f.relative_to(root)}  {note} volume={m.volume / 1000:.3f} cm3")
    touching += ok and shared > 0
    if not ok:
        failed.append(f)
print(f'{len(files) - len(failed)}/{len(files)} meshes closed ({touching} of them with touching bodies)')
sys.exit(1 if failed else 0)
