#!/usr/bin/env python3
"""
Assembly-frame meshes and data for the 3D viewer (site/).

Run from anywhere:  python hardware/cad/build_assembly.py
Inputs (relative to this script's folder):
  ../3mf/<part>.3mf      drivetrain parts at assembled height, X=Y=0 on the shaft axis
  ../3mf/scivolo_v1.3mf  chute in its local frame (flange plane at x = -4..0)
  layout_v3.json         assembly frame, positions and key heights
Outputs:
  ../assembly/<part>.stl  meshes in the assembly frame ("axis" or "world", see below)
  ../assembly/assembly.json  part list, colours, materials, explode vectors and the
                             layout numbers used to draw the non-printed parts

Frames: Z-up, mm, Z=0 = top face of the box lid.
  "axis":  X=Y=0 on the shaft axis; the viewer moves the part to layout shaft_axis_xy.
  "world": already placed in the assembly frame.
These are not print files: use ../stl/ for printing.

The servo cradle is part of passante_culla (bushing and cradle in one print).
Third-party-derived parts (servo mounts, spacers) are never included.
"""
from pathlib import Path
import json
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
MF_DIR, OUT = HERE.parent / '3mf', HERE.parent / 'assembly'
OUT.mkdir(parents=True, exist_ok=True)
L = json.loads((HERE / 'layout_v3.json').read_text())
SX, SY = L['shaft_axis_xy']

BLACK, ORANGE, GREEN = '#26282c', '#ee6a1f', '#2f9550'

# Printed parts shown in the viewer.
PARTS = [
    dict(id='disco_v3', name='Rotating disc', frame='axis', spins=True, colour=ORANGE,
         material='PETG', spool='orange', status='designed', explode=[0, 0, 70],
         description='103 mm disc in the bowl with a trapezoid opening. Turning it 180° '
                     'lets one portion drop. A sleeve under it ends in a labyrinth cap over the '
                     'bushing collar. It sits on the shaft hex and is clamped by an M3x50 screw.'),
    dict(id='albero_mozzo', name='Shaft and hub', frame='axis', spins=True, colour=BLACK,
         material='PETG', spool='black', status='designed', explode=[0, 0, -66],
         description='22 mm hub with the 25-tooth socket for the servo spline and a 45° top cone, '
                     'a 12 mm shaft with grooves for 9x2 O-rings, and an 8 mm hex at the top that '
                     'drives the disc. Print at 100 % infill.'),
    dict(id='passante_culla', name='Sealed bushing and servo cradle', frame='axis', spins=False,
         colour=BLACK, material='PETG', spool='black', status='designed', explode=[0, 0, -22],
         description='One part. It carries the shaft through the lid, sealed by a 45x2 face O-ring '
                     'under the lid and a 9x2 O-ring on the shaft, and hangs the servo from the lid '
                     'on four pads with heat-set inserts. Designed, not printed or mounted yet: the '
                     'prototype still uses a wall bracket.'),
    dict(id='scivolo_v1', name='Chute', frame='world', spins=False, colour=GREEN,
         material='PETG', spool='green', status='designed', explode=[-36, -46, 34],
         description='Curved hollow duct bolted to the bowl spout. It carries the portion out '
                     'and down. Print orientation not validated yet.'),
]

# Non-printed parts, drawn by the viewer as simple shapes from "layout" below.
CONTEXT = [
    dict(id='container', name='Kibble container', kind='container', status='to design',
         colour='#5b7f9a', opacity=0.16, explode=[0, 0, 190],
         description='Any container that holds the kibble above the hopper. Shape shown is a placeholder.'),
    dict(id='hopper', name='Hopper and shelf', kind='hopper', status='to design',
         colour='#6c7a86', opacity=0.24, explode=[0, 0, 125],
         description='Funnels the kibble into the bowl and seats on the bowl rim. Not designed yet.'),
    dict(id='bowl', name='Bowl with spout', kind='bowl', status='reused',
         colour='#2d3034', opacity=0.62, explode=[0, 0, 34],
         description='A reused round chamber with a tangential spout. It sits on the lid; the disc '
                     'turns inside it and the chute bolts to the spout.'),
    dict(id='servo', name='Servo, 25 kg·cm', kind='servo', status='bought',
         colour='#b3302a', opacity=1, explode=[0, 0, -100],
         description='Digital servo with a 25-tooth spline (DS3218 / DS3225 class). In the design it '
                     'hangs from the lid in the cradle of passante_culla and turns the shaft; the '
                     'prototype still holds it in a wall bracket.'),
    dict(id='esp32', name='ESP32 board and 12 V input', kind='board', status='bought',
         colour='#1f4d3a', opacity=1, explode=[0, 0, -150],
         description='ESP32 board (Freenove ESP32-WROVER as documented; to be verified on the '
                     'device) running the MicroPython firmware drives the servo. The planned design '
                     'takes power from an external 12 V adapter through a cable gland; prototype 1 '
                     'runs on a 5 V bench supply. Position in the box is indicative.'),
    dict(id='box', name='Waterproof box', kind='box', status='bought',
         colour='#1f2124', opacity=0.14, explode=[0, 0, -150],
         description='265 x 185 mm sealed box. The lid is the reference plane (Z = 0); in the '
                     'exploded view only the base moves.'),
]

# Item numbers (BOM balloons on the site), top to bottom as assembled.
BOM_ORDER = ['container', 'hopper', 'disco_v3', 'bowl', 'scivolo_v1', 'passante_culla',
             'albero_mozzo', 'servo', 'esp32', 'box']

NOT_SHOWN = [
    dict(id='test_scanalato', name='Spline fit test', material='PETG', spool='black',
         status='designed',
         description='Three short coupons with the 25-tooth socket at 0.05, 0.10 and 0.20 mm '
                     'clearance. Print these first and try them on the servo.'),
]


def chute_world_matrix():
    """Chute local frame -> assembly frame: local +x along the chute heading, inlet at inlet_center."""
    heading = {'+X': 0, '+Y': 90, '-X': 180, '-Y': -90}[L['chute']['heading']]
    M = trimesh.transformations.rotation_matrix(np.radians(heading), [0, 0, 1])
    M[:3, 3] = L['chute']['inlet_center']
    return M


def chute_path(M, n=24):
    """Kibble path along the chute floor, from the same Bezier as build_disc_v2_chute.py."""
    P = [np.array(p, float) for p in [(0, 0), (55, 0), (85, -18), (92, -62)]]
    t = np.linspace(0, 1, n)[:, None]
    C = (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]
    pts = np.c_[C[:, 0], np.zeros(n), C[:, 1] - 6]   # 6 mm below the duct axis = on its floor
    return np.round(trimesh.transform_points(pts, M), 1).tolist()


def load(name):
    m = trimesh.load(MF_DIR / f'{name}.3mf', force='mesh')
    assert m.is_watertight, f'{name} is not watertight'
    return m


parts = []
for p in PARTS:
    m = load(p['id'])
    if p['frame'] == 'world':
        m.apply_transform(chute_world_matrix())
    p = dict(p, file=f"{p['id']}.stl")
    m.export(OUT / p['file'])
    p['bounds'] = np.round(m.bounds, 1).tolist()
    parts.append(p)

order = {k: i for i, k in enumerate(BOM_ORDER)}
def bom_key(q):
    return order.get(q['id'], len(order))


everything = sorted(parts + CONTEXT, key=bom_key)
for i, q in enumerate(everything, 1):
    q['bom'] = i

layout = {k: L[k] for k in ('box', 'shaft_axis_xy', 'servo', 'camera', 'disc_v3', 'bushing',
                            'hub', 'shaft', 'chute', 'ripiano')}
layout['chute'] = dict(layout['chute'], path=chute_path(chute_world_matrix()))
# Placeholder sizes for parts that are not designed yet (viewer only, not design decisions).
layout['hopper'] = dict(plate_r=64, plate_t=4, throat_r=20, funnel_top_r=62, funnel_h=40,
                        note='placeholder, not designed yet')
layout['container'] = dict(bottom_gap=0, h=150, r_bottom=58, r_top=70,
                           note='placeholder, any container')
layout['esp32'] = dict(board_xyz=[64, 27, 1.6], center=[45, 10], standoff=6,
                       gland_xyz=[132.5, 20, -70], gland_d=16, note='position indicative')
layout['spout'] = dict(start_deg=95, end_deg=180, width_outer=46, wall=3, top_z=27,
                       note='tangential spout of the reused bowl, approximate')

data = {
    '_about': 'Generated by hardware/cad/build_assembly.py. Assembly-frame data for the 3D viewer; '
              'not print files (see hardware/stl/).',
    'frame': 'Z-up, mm, Z=0 = top face of the box lid. "axis" parts have X=Y=0 on the shaft axis '
             'and are moved to shaft_axis_xy; "world" parts are already in the assembly frame.',
    'shaft_axis_xy': [SX, SY],
    'servo_rotation': 'Disc angle = open_dir_deg - 270 + servo_deg: at servo 180° the disc local +Y '
                      '(its opening) points at layout.disc_v3.open_dir_deg, towards the chute.',
    'parts': parts,
    'context': CONTEXT,
    'not_shown': NOT_SHOWN,
    'layout': layout,
}
(OUT / 'assembly.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
for p in parts:
    print(f"{p['id']:<16} {p['frame']:<5} bounds {p['bounds']}")
print(f'wrote {len(parts)} meshes and assembly.json to {OUT}')
