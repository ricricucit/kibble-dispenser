#!/usr/bin/env python3
"""
Kibble Dispenser Outdoor - design v6.4 (from 6.3.0).

Owner decision (2026-11-14): split the product into
  (1) MECHANICS + an electronics-case HOLDER (this file, version line 6.x), and
  (2) a detachable ELECTRONICS MODULE ("modulo elettronica", its own version line: "case 1.0").

What changes against 6.3.0 (everything else is the 6.3.0 file, byte for byte):
  scatola_v64   the electronics box shrinks to a SERVO BAY (x +-15.25, y +-41, same roof, tower face, cradle, gland wall):
                the servo stays in the chassis, coaxial and structural. It carries the holder: two posts with M3 inserts
                that hang in front of the bay east wall, and 4 PT bosses for the cap. P3 sits on a pad outside the bay.
  fondello_v64  cap: closes the servo bay from below with the same TPU lip concept (new D outline), keeps the outlet
                socket, drain 1, the 45 deg spigot collar; loses the panel, the pocket, drain 2 and the seam O-ring
                groove; has the module opening (x >= 17.05, |y| <= 52.35) with return ribs at the cut edges.
  guscio_v64    shell: opening for the module (z -72 .. -36.65, |y| <= 52.35) with return ribs. Nothing else.
  guarnizione_fondello_v64  TPU lip for the new bay outline.
Module "case 1.0" (4 printed pieces): modulo_vasca_v64 (tub: outer face = pod skin + control panel), modulo_coperchio_v64
(lid with the M8 5-pin interface connector), modulo_guarnizione_v64 (TPU lip gasket in the lid), modulo_anello_speaker_v64
(ring insert that adapts the speaker seat, Ø20-28).

The module is a vertical prism: it slides in from BELOW (unit hanging or taken down by the bayonet), its outer wall is the
missing piece of the pod skin, its top lip tucks behind the shell edge, two closed sockets take the holder posts and two
M3x16 screws from below lock it. Interface connector J1 on the lid is reached through the opening when the module is
lowered ~30 mm.
Frame and pose as 6.3 (Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside). No existing file is modified.

Status: designed and checked in CAD only; not printed, assembled or tested yet. Hardware 6.4.0 + electronics module case 1.0.

Run from anywhere:  python hardware/cad/build_v64.py
  1. runs the earlier stages first when their outputs are missing or older than their scripts, each into build/:
     build_v6.py (with build_dosing.py and build_v5.py), build_v61.py, build_v611.py, build_v62.py and build_v63.py, all
     with their checks, because v6.4 reuses the 6.3.0 parts (byte for byte), their JSON files and assembled-position copies;
  2. builds and exports the v6.4 chassis parts and the module case 1.0 parts, runs the checks (build_v64_checks.py, which
     runs build_v64_report.py) and writes v64.json, v64_viewer.json, check_v64.png, the module interface drawing
     (interface_v64/), the drilling template (template_v64/) and the assembled-position copies (v64_asm/), all in build/;
  3. publishes the repository files with publish_v64.py: ../assembly, ../template, v64.json, check_v64.png, and the module
     folder ../module/case-1.0 (parts and interface drawing). The print package in ../plates is rebuilt from build/ by
     ../plates/tools/run_all.sh (needs the OrcaSlicer command line for the slicer check).
Optional argument: "build" stops after building the parts (no export, checks or publishing).
The v6.3 stage compares grams with ref/baseline_print_v62.json and the print STLs in ../plates/stl.
Dependencies: trimesh, manifold3d, shapely, mapbox_earcut, rtree, numpy, scipy, networkx, lxml, matplotlib, fast_simplification.
"""
import json
import math
import os
import sys
import hashlib
import numpy as np
import trimesh
import shapely
import shapely.ops
from shapely.geometry import Polygon, Point, box as sbox, LineString
from shapely import affinity

import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_V5 = ['build_drivetrain.py', 'layout_v4.json', 'build_dosing.py', 'build_v5.py', 'build_v5_checks.py']
_V6 = _V5 + ['build_v6.py', 'build_v6_checks.py']
_V61 = _V6 + ['build_v61.py', 'build_v61_checks.py']
_V611 = _V61 + ['build_v611.py', 'build_v611_checks.py', 'los.py', 'ref/measure_v61.json']
_V62 = _V611 + ['build_v62.py', 'build_v62_checks.py', 'toolaccess.py', 'ref/ta_v611.json']
_V63 = _V62 + ['build_v63.py', 'build_v63_checks.py', 'build_v63_report.py']
_PREREQUISITES = (     # script, inputs it depends on, outputs v6.4 reads from build/
    ('build_v6.py', _V6, ['v6.json']),
    ('build_v61.py', _V61, ['v61.json', 'v61_viewer.json']),
    ('build_v611.py', _V611, ['v611.json', 'v611_viewer.json']),
    ('build_v62.py', _V62, ['v62.json', 'v62_viewer.json']),
    ('build_v63.py', _V63, ['v63.json', 'v63_viewer.json']),
)


def _ensure_prerequisites():
    """Run the earlier stages (v6 .. v6.3, each with its checks) when an output is missing or out of date."""
    for script, deps, outputs in _PREREQUISITES:
        newest = max(os.path.getmtime(os.path.join(_HERE, f)) for f in deps)
        paths = [os.path.join(_HERE, 'build', o) for o in outputs]
        if all(os.path.exists(q) and os.path.getmtime(q) >= newest for q in paths):
            continue
        print(f'--- running {script} first ---', flush=True)
        subprocess.run([sys.executable, os.path.join(_HERE, script)], check=True)


if __name__ == '__main__':
    _ensure_prerequisites()

import build_v63 as b63
from build_v63 import (b62, b611, b61, v6, v5, dt, bd, OUT, U, D, I, cyl, box, at, hull_of, circle_pts, revolve, prism, ring2d,
                       below, above, polar, rotz, text_poly, face_region, overhang, vol, SEG, pod_solid, pod_circle, section_fn,
                       report, PETG, TPU, Z_TOP, R_TOP, Z_BOT, Z_S, T_SHELL, T_CAP, Z_R, Z_W, ROOF_T, CRADLE_HALF_X, CAGE_Z0,
                       GLAND, CH_X, NF, tube_path, P_SCREWS, P3_POCKET_D, PT, BOX_BOSS_D, PILOT_DEPTH, CAP_SEAT_Z, CAP_CB_D,
                       CAP_BOSS_TOP, OR_3x1, EAR_R, EAR_Z0, EAR_ROOT, P_SEALED, REC, LED, KO, KO_COS, ZB0, ZB1, B_MARGIN, Z_E,
                       band_rho, loft_rings, band_inner_solid, axial_cyl, axial_cone, elem_frame, future_switch, staged, current,
                       commit_staged, patched, SPIG_COLLAR_RW)

VER = 'v6.4'
CASE_VER = 'case 1.0'
SFX = '_v64'
SCRATCH = OUT + 'scratch_v64/'                               # probe exports, previews (inside build/)
ASM = OUT + 'v64_asm/'
IFD = OUT + 'interface_v64/'
for _d in (SCRATCH, ASM, IFD):
    os.makedirs(_d, exist_ok=True)
v6.SCRATCH = SCRATCH
b63.SCRATCH = SCRATCH

# =====================================================================================
# PARAMETERS v6.4
# =====================================================================================
# ---- servo bay (chassis) ----
BAY = (-CRADLE_HALF_X, CRADLE_HALF_X, -41.0, 41.0)          # x0, x1, y0, y1: the cradle rails are the bay side walls
BAY_OUT = b61.rrect(BAY[0], BAY[1], BAY[2], BAY[3], b61.BX_R)
BAY_IN = BAY_OUT.buffer(-b61.BX_T, join_style=1, resolution=16)
WALL_C64 = BAY_OUT.buffer(-0.5, join_style=1, resolution=16)  # centreline of the 3.0 wide bay rim face (cap lip)
CAP64 = {'A': (-21.2, 33.0), 'B': (-21.2, -33.0), 'C': (11.0, 47.0), 'D': (11.0, -47.0)}   # cap screws PT K30x12, all outside the bay
P3_PAD = dict(r=6.0, z0=-36.0)                              # P3 (17.6, 14) outside the bay: cup-shaped pad, head seat as 6.3
VENT64 = dict(y=-25.0, z=-64.0, d=2.0, patch_d=12.0)        # adhesive ePTFE vent over a Ø2 hole in the bay -X wall
# ---- module opening / holder interface (FIXED for every module version) ----
XM0 = 17.4                                                  # module back face
YM = 52.0                                                   # module half width
GAP = 0.35                                                  # clearance module | pod opening and holder
ZMT = -37.0                                                 # module top (lid top, skin top)
TOP_SEAM = 0.5                                              # review m1: the post ends are the vertical stop, the top seam stays open
ZSH = ZMT + TOP_SEAM                                        # lower edge of the shell above the module: -36.5
NX1, NY0 = 29.6, 38.0                                       # back corner notches of the module (x XM0..NX1, |y| NY0..YM)
ZN0 = -89.0                                                 # notches open above this height; below: solid screw columns
ZSOCK = -71.5                                               # ZN0..ZSOCK: closed sockets round the posts
POST = dict(xy=(24.0, 45.5), d=9.0, z0=-89.0, z1=Z_R, web_z0=-70.5, ins_d=4.0, ins_depth=6.5)   # review M1: post + web run up to the roof plane (the bed)
SOCK_GAP = 0.5                                              # review m12: sockets Ø10.0 on Ø9.0 posts
LOCK = dict(d=3.0, clr=3.4, head_d=5.5, head_h=3.0, cb_d=6.5, seat_z=Z_BOT + 4.9, len=16.0)   # 2 x M3x16 ISO 4762 from below
LIP = dict(h=4.0, t=2.0, gap=0.4)                           # top lip of the module behind the shell wall
RIB = dict(t=2.0, depth=6.0)                                # return ribs at the cut edges of cap and shell
# ---- module "case 1.0" ----
WALL_M, WALL_B, WALL_S, FLOOR_M = 2.5, 2.0, 2.5, 2.5        # skin wall, back wall, side walls, floor
PAR = 4.5                                                   # skin wall thickness at the top (parapet round the lid + lip root)
LID_T = 3.2
Z_LU = ZMT - LID_T                                          # lid underside -40.2
Z_LAND = Z_LU - 0.5                                         # tub seal land -40.7 (lip gasket bent as the cap lip)
Z_RIM0 = -46.5                                              # the rim thickening is full from here up; 45 deg stair below
GUIDE_Y = 34.0                                              # guide walls: slots for 70 mm wide boards (slot bottoms +-35.3)
SLOTS = dict(A=22.4, B=30.0, w=1.9, depth=1.3, z0=-91.5)   # board back face x; A = main board, B = second slot (both in the guide walls)
FRONT_X0 = 33.5                                             # the guide walls end here; lobes and full width in front
O_BACK, O_Y, O_SIDE = 21.6, 35.5, 4.0                       # lid opening: back edge, half width of the board zone, side land
O_SKIN = 9.3                                                # lid opening stays this far inside the skin (parapet + land)
LID_SCREWS = [(38.0, 43.5), (38.0, -43.5), (46.0, 36.5), (46.0, -36.5), (54.5, 0.0)]  # PT K30x8 + O-ring 3x1 (inside the gasket loop)
LID_BOSS = dict(d=7.5, h=9.0)
J1 = dict(xy=(45.0, -24.0), hole=8.2, body_d=11.0, body_len=11.0, tur_d=21.0, tur_id=16.5, tur_h=12.0, tur_top=3.0, seat_d=13.0, skin=0.2)   # M8 5-pin A-coded panel socket in a turret
USB = dict(xy=(39.0, 0.0), ring_d=13.0)                     # blind position for a sealed USB-C service port
SPK64 = dict(x=33.0, y=-10.0, seat_z=-99.5, collar_id=26.4, collar_t=1.5, collar_top=-96.5, ledge_id=22.0,
             ring_od=26.0, ring_h=3.5, spk_d=23.0, spk_h=4.5, hole=1.5, grille_r=2.6)        # floor seat: speakers Ø20..24 by ring insert
# ---- control panel on the module (east face, band as 6.3) ----
PHI_A64, PHI_B64, PHI_RAMP64 = -47.0, 44.0, 5.0
ELEMS64 = [('led1', 31.0, 3.0), ('led2', 31.0, -6.0), ('btn', 16.0, 0.0), ('ko1', -3.0, b63.KO_DZ), ('ko2', -19.0, b63.KO_DZ),
           ('ko3', -35.0, b63.KO_DZ)]
BAND_WALL = b63.BAND_WALL
PLAN = sbox(XM0, -YM, 200.0, YM)
NOTCH_N = sbox(XM0 - 1.0, NY0, NX1, YM + 1.0)
NOTCH_S = sbox(XM0 - 1.0, -YM - 1.0, NX1, -NY0)
PLAN_UP = PLAN.difference(NOTCH_N).difference(NOTCH_S)
DRAIN_HOLES = dict(d=1.5, r=1.35, ang=(45.0, 225.0))
# ---- chassis harness (6.4.0 assembly review): anchor lug on the bay, service loop parked on the module lid ----
TIE_LUG = dict(x=(11.5, 14.0), y=(-58.5, -50.0), z0=-40.0, slot_y=(-56.6, -55.0), slot_z=(-37.5, -34.0))   # cable tie 2.5 x 100 round bar + cable
HARN = dict(r_tail=2.25, r_branch=2.0, r_12v=2.0, splice=(7.0, -64.0, -50.0), splice_d=8.0, splice_len=20.0, anchor=(16.35, -57.5, -35.75))
EYELET = dict(xy=(32.5, -48.5), od=11.0, id=6.5, slit=3.8, z0=-32.0, arm_w=3.0)   # C-hook on the south post top: the tail drops into the opening here
LID_FENCE = dict(x=(24.6, 26.4), y=(3.0, 25.0), h=3.0)       # keeps the parked loop out from under the P3 pad (1.0 mm over the lid)
JR = dict(x=(-5.0, 2.6), y=(-31.0, -27.4), z=(-76.0, -48.0))  # mated JR/Futaba 3-pin pair inside the bay (south room)
CORBEL_INFO = []
RIM_T = 2.0                                                 # notch walls thickened outward at the rim (seal land)
PLAN_RIM = PLAN.difference(sbox(XM0 - 1.0, NY0 + RIM_T, NX1, YM + 1.0)).difference(sbox(XM0 - 1.0, -YM - 1.0, NX1, -NY0 - RIM_T))
OPEN2D = sbox(XM0 - GAP, -YM - GAP, 200.0, YM + GAP)        # opening in cap and shell


def clean64(m):
    """STL is float32. First the 6.x variants; if none reloads watertight, snap the vertices to float32 and pass the mesh once
    through the boolean kernel (it collapses the triangles that became degenerate): same solid, no open edges on reload"""
    probe = SCRATCH + '_probe64.stl'
    m.export(probe)
    if trimesh.load(probe).is_watertight:
        return m
    mm = trimesh.Trimesh(m.vertices.astype(np.float32).astype(np.float64), m.faces, process=False)
    try:
        r = U([mm, box(900, 901, 900, 901, 900, 901)])
        big = max(r.split(only_watertight=False), key=lambda q: len(q.faces))
        big.export(probe)
        if trimesh.load(probe).is_watertight and abs(big.volume - m.volume) < 1e-3 * abs(m.volume) + 1.0:
            return big
    except Exception:
        pass
    return v6.clean(m)


def bottom_fill(overlap=1.0):
    """review M3: the R15 bottom edge starts at 81 deg from vertical on the bed. A 45 deg chamfer is laid under it (from the
    point where the radius itself reaches 45 deg down to the bed): ring solid to be united with cap and tub"""
    zs, x0, x1 = section_fn(0.0)
    g1, g0 = np.gradient(x1, zs), np.gradient(-x0, zs)
    k1 = int(np.argmax((g1 <= 1.0) & (zs > Z_BOT + 0.3))); k0 = int(np.argmax((g0 <= 1.0) & (zs > Z_BOT + 0.3)))
    kt = max(k0, k1) + 1
    lev = zs[:kt + 1]
    a = np.minimum(x0[:kt + 1], x0[k0] + (zs[k0] - lev)); b_ = np.maximum(x1[:kt + 1], x1[k1] - (zs[k1] - lev))
    th = np.linspace(0, 2 * np.pi, 192, endpoint=False)
    rings = [np.c_[(p + q) / 2 + (q - p) / 2 * np.cos(th), (q - p) / 2 * np.sin(th), np.full(192, z)] for z, p, q in zip(lev, a, b_)]
    fill = loft_rings(rings)
    return D(fill, [pod_solid(overlap)]), float(lev[-1]), float((b_[0] - a[0]) / 2)


def edge_blunt(z0, z1, d=0.9, step=1.0):
    """review m10: the cut faces of the opening meet the skin at ~45 deg. Take the feather tip off: a face square to the skin
    0.9 mm back from the edge (solid to subtract from cap / shell)"""
    out = []
    for s_ in (1, -1):
        y0 = s_ * (YM + GAP)
        prev = None
        for z in np.r_[np.arange(z0, z1, step), z1]:
            c, r = pod_circle(0.0, float(z))
            if r <= abs(y0) + 1.0:
                prev = None
                continue
            e = np.array([c + math.sqrt(r * r - y0 * y0), y0]); n = (e - np.array([c, 0.0])) / r
            t = np.array([-n[1], n[0]]) * s_
            a_ = e + d * t
            q = a_ - n * ((a_[1] - y0) / n[1])
            pts = np.array([e + 0.6 * n, a_ + 0.6 * n, q, e])
            cur = np.c_[pts, np.full(4, z)]
            if prev is not None:
                out.append(trimesh.convex.convex_hull(np.vstack([prev, cur])))
            prev = cur
    return out


def mirror_y(m):
    c = m.copy()
    c.apply_transform(np.diag([1.0, -1.0, 1.0, 1.0]))
    if c.volume < 0:
        c.invert()
    return c


def post_xy(s):
    return POST['xy'][0], s * POST['xy'][1]


# =====================================================================================
# 1. SERVO BAY + HOLDER (scatola_v64)
# =====================================================================================
def build_box64():
    walls = prism(ring2d(BAY_OUT, BAY_IN), Z_W, Z_R - ROOF_T + 0.01)
    roof = prism(BAY_OUT, Z_R - ROOF_T, Z_R)
    rim = prism(ring2d(BAY_OUT.buffer(b61.FL_OUT, join_style=1, resolution=16), BAY_IN), Z_W, Z_W + 3.0)
    # review m4: 45 deg run-out above the rim flange (it printed as a 1.0 mm flat step)
    rim = U([rim] + [prism(ring2d(BAY_OUT.buffer(b61.FL_OUT * (1 - (j + 1) / 10), join_style=1, resolution=16), BAY_IN), Z_W + 3.0 + j * 0.1 - 0.01, Z_W + 3.0 + (j + 1) * 0.1) for j in range(9)])
    boss = prism(Point(0, 0).buffer(v6.BOSS_R, resolution=96).intersection(BAY_OUT), v6.BOSS_Z0, Z_R - 1.0)
    cage = prism(sbox(-CRADLE_HALF_X, b61.CAGE_Y[0], CRADLE_HALF_X, b61.CAGE_Y[1]), CAGE_Z0, Z_R - 1.0)
    parts = [walls, roof, rim, boss, cage, b61._wall_pad(GLAND, GLAND['pad_d'])]
    # cap bosses: A, B on webs from the -X wall, C, D on webs from the north / south wall
    for k in ('A', 'B'):
        bx, by = CAP64[k]
        parts += [at(cyl(BOX_BOSS_D, CAP_BOSS_TOP, Z_R, 48), bx, by), box(bx + BOX_BOSS_D / 2 - 1.0, BAY[0] + 0.5, by - 3.5, by + 3.5, Z_W, Z_R)]
    for k, s in (('C', 1), ('D', -1)):
        bx, by = CAP64[k]
        y_in, y_out = s * (BAY[3] - 0.5), s * (abs(by) - BOX_BOSS_D / 2 + 1.0)
        parts += [at(cyl(BOX_BOSS_D, CAP_BOSS_TOP, Z_R, 48), bx, by), box(bx - 3.5, bx + 3.5, min(y_in, y_out), max(y_in, y_out), Z_W, Z_R)]
    # P1 ear (as 6.3) and P3 pad (cup: thick ring round the head, seat at the roof underside as 6.3)
    x1, y1 = P_SCREWS[0]
    ear2d = shapely.unary_union([Point(x1, y1).buffer(EAR_R, resolution=32), sbox(BAY[0] - 0.5, y1 - EAR_ROOT, BAY[0] + 1.0, y1 + EAR_ROOT)]).convex_hull
    parts.append(prism(ear2d, EAR_Z0, Z_R))
    x3, y3 = P_SCREWS[2]
    parts.append(at(cyl(2 * P3_PAD['r'], P3_PAD['z0'], Z_R, 64), x3, y3))
    # holder posts: hang in front of the bay east wall, tied to the north / south wall by a web (above the cap upstand)
    for s in (1, -1):
        px, py = post_xy(s)
        root = sbox(8.0, s * 40.5 if s > 0 else -41.5, 14.5, s * 41.5 if s > 0 else -40.5)
        web2d = shapely.unary_union([Point(px, py).buffer(POST['d'] / 2, resolution=48), root]).convex_hull
        parts += [at(cyl(POST['d'], POST['z0'], POST['z1'], 64), px, py), prism(web2d, POST['web_z0'], POST['z1'])]
    tl = TIE_LUG                                             # harness anchor: lug on the south side of cap boss D
    parts.append(box(tl['x'][0], tl['x'][1], tl['y'][0], tl['y'][1], tl['z0'], Z_R))
    ex_, ey_ = EYELET['xy']                                  # C-hook guide on the south post top (grows from the bed, 3 mm plate)
    parts += [box(POST['xy'][0], ex_, ey_ - EYELET['arm_w'] / 2, ey_ + EYELET['arm_w'] / 2, EYELET['z0'], Z_R), at(cyl(EYELET['od'], EYELET['z0'], Z_R, 64), ex_, ey_)]
    body = U(parts)
    cuts = [box(tl['x'][0] - 1.0, tl['x'][1] + 1.0, tl['slot_y'][0], tl['slot_y'][1], tl['slot_z'][0], tl['slot_z'][1]),
            at(cyl(EYELET['id'], EYELET['z0'] - 1.0, Z_R + 1.0, 48), ex_, ey_),
            box(ex_, ex_ + EYELET['od'], ey_ - EYELET['slit'] / 2, ey_ + EYELET['slit'] / 2, EYELET['z0'] - 1.0, Z_R + 1.0),
            box(-CRADLE_HALF_X + 2.5, CRADLE_HALF_X - 2.5, b61.VOID_Y[0], b61.VOID_Y[1], CAGE_Z0 - 1.0, v6.S_TOP + 0.5),
            cyl(2 * dt.HUB_CAV_R, v6.S_TOP + 0.5 - 0.01, v6.CAV_TOP + 0.01, 96),
            hull_of((circle_pts(2 * dt.HUB_CAV_R, 96), v6.CAV_TOP), (circle_pts(2 * v6.PLAT_HOLE_R, 96), v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R)),
            cyl(2 * v6.PLAT_HOLE_R, v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R - 0.01, Z_R + 1.0, 96),
            b61._wall_pad(GLAND, GLAND['hole_d'], True)]
    vh = trimesh.creation.cylinder(radius=VENT64['d'] / 2, height=8.0, sections=24)
    vh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    vh.apply_translation([BAY[0] + 1.0, VENT64['y'], VENT64['z']])
    cuts.append(vh)
    for x, y in b61.SERVO_HOLES_W:
        cuts.append(at(U([cyl(v6.INS_D, CAGE_Z0 - 1, CAGE_Z0 + dt.SERVO_INS_DEPTH, 48),
                          hull_of((circle_pts(v6.INS_D + 1.8, 48), CAGE_Z0 - 0.5), (circle_pts(v6.INS_D, 48), CAGE_Z0 + 0.4))]), x, y))
    for x, y in CAP64.values():
        cuts.append(at(U([cyl(PT['pilot'], CAP_BOSS_TOP - 1.0, CAP_BOSS_TOP + PILOT_DEPTH, 32),
                          hull_of((circle_pts(PT['pilot'] + 0.82, 32), CAP_BOSS_TOP - 0.01), (circle_pts(PT['pilot'], 32), CAP_BOSS_TOP + 0.4))]), x, y))
    cuts.append(at(cyl(3.4, EAR_Z0 - 1.0, Z_R + 1.0, 32), x1, y1))
    zr0 = Z_R - ROOF_T
    c = OR_3x1['csk_d']
    for k, (x, y) in enumerate(P_SCREWS[1:]):
        cuts.append(at(cyl(3.4, zr0 - 1.0, Z_R + 1.0, 32), x, y))
        cuts.append(at(cyl(P3_POCKET_D if k == 1 else 6.6, v6.BOSS_Z0 - 1.0, zr0 + 0.01, 48), x, y))
        if k == 0:                                           # O-ring countersink only at P2 (inside the bay); P3 is outside: flat seat
            cuts.append(at(hull_of((circle_pts(c, 48), zr0 - 0.01), (circle_pts(3.4, 48), zr0 + (c - 3.4) / 2)), x, y))
    for s in (1, -1):                                        # M3 heat-set inserts in the post ends (module lock screws)
        px, py = post_xy(s)
        cuts.append(at(U([cyl(POST['ins_d'], POST['z0'] - 1.0, POST['z0'] + POST['ins_depth'], 48),
                          hull_of((circle_pts(POST['ins_d'] + 1.6, 48), POST['z0'] - 0.01), (circle_pts(POST['ins_d'], 48), POST['z0'] + 0.5))]), px, py))
    cuts.append(at(cyl(3.7, Z_W - 1.0, Z_W + 4.0, 32), *P_SCREWS[2]))       # P3 key path: relief in the rim flange (0.45 of its outer edge)
    cuts.append(face_region(text_poly(f'{VER} SERVO', 4.5, 0.0, -31.0), Z_R, True))
    return D(body, cuts)


# =====================================================================================
# 2. CAP (fondello_v64) + its TPU lip
# =====================================================================================
TAB_GUS_R0 = 62.6                                           # bowl radius at the tabs is 62.0


def edge_ribs(t_wall, z0, z1, depth=None):
    """return ribs behind the two cut edges of the opening (|y| = YM + GAP): 2 thick, 6 deep behind the wall"""
    band = D(pod_solid(t_wall - 0.1), [pod_solid(t_wall + (RIB['depth'] if depth is None else depth))])
    slabs = U([box(XM0 - GAP, 200.0, s * (YM + GAP) if s > 0 else -(YM + GAP + RIB['t']), s * (YM + GAP + RIB['t']) if s > 0 else -(YM + GAP), z0, z1)
               for s in (1, -1)])
    return I(band, slabs)


def build_cap64():
    outer = pod_solid(0.0, z_hi=Z_S - b611.SEAM)
    inner = pod_solid(T_CAP)
    shell = D(outer, [inner])
    clip_in = pod_solid(T_CAP - 0.3)
    up = I(prism(ring2d(BAY_OUT.buffer(b611.UP_OUT, join_style=1, resolution=16), BAY_OUT.buffer(-b611.UP_IN, join_style=1, resolution=16)),
                 Z_BOT - 5, b61.Z_C), clip_in)
    so, si = b611.SEAM_R - (b611.SPIG_OFF - T_SHELL), b611.SEAM_R - (b611.SPIG_IN - T_SHELL)
    zt, rw = Z_S - b611.SEAM, SPIG_COLLAR_RW
    spig = at(D(cyl(2 * so, zt - 0.6, b611.SPIG_TOP, 512), cyl(2 * si, zt - 1.6, b611.SPIG_TOP + 1, 512)), b611.SEAM_CX, 0)
    collar = revolve([(si, zt - 0.4), (rw, zt - 0.4), (rw, zt - 0.4 - (rw - si))], 512)
    if collar.volume < 0:
        collar.invert()
    spig = U([spig, at(collar, b611.SEAM_CX, 0)])
    tube = I(at(cyl(2 * b611.SOCK['r_out'], Z_BOT - 5, b611.SOCK['top'], NF), CH_X, 0), clip_in)
    dboss, dcuts = drain64()
    d_keep = prism(BAY_OUT.buffer(b611.UP_OUT - 0.01, join_style=1, resolution=16), Z_BOT - 10, b61.Z_C + 1)
    screed = b611.floor_screed(clip_in, d_keep)
    sboss = [I(at(cyl(10.0, Z_BOT - 5, CAP_BOSS_TOP, 64), x, y), clip_in) for x, y in CAP64.values()]
    # floor edge dam along the opening (stiffens the free floor edge north and south of the bay upstand)
    dam = [I(box(XM0 - GAP - 2.0, XM0 - GAP, min(s * 42.0, s * (YM + GAP + RIB['t'])), max(s * 42.0, s * (YM + GAP + RIB['t'])), Z_BOT, Z_BOT + T_CAP + 4.0), clip_in)
           for s in (1, -1)]
    ribs = edge_ribs(T_CAP, Z_BOT + 0.5, Z_S - b611.SEAM - 0.4)
    wedge, _, _ = bottom_fill()
    body = U([shell, up, spig, tube, screed, I(dboss, clip_in), ribs, wedge] + sboss + dam)
    groove = prism(ring2d(WALL_C64.buffer(b611.GRV_W611 / 2, join_style=1, resolution=16), WALL_C64.buffer(-b611.GRV_W611 / 2, join_style=1, resolution=16)),
                   b61.Z_C - b61.GRV_D, b61.Z_C + 1)
    r_ = b61.OUTLET['r']
    S = b611.SOCK
    cuts = [groove,
            at(cyl(2 * r_, Z_BOT - 10, S['bore_z'] + 0.01, NF), CH_X, 0),
            at(hull_of((circle_pts(2 * r_, NF), Z_BOT + b61.OUTLET['chamfer']), (circle_pts(2 * (r_ + b61.OUTLET['chamfer'] + 1.0), NF), Z_BOT - 1.0)), CH_X, 0),
            at(cyl(2 * S['r'], S['pilot'][0], S['top'] + 1, NF), CH_X, 0),
            at(cyl(2 * S['pocket'][2], S['pocket'][0], S['pocket'][1], NF), CH_X, 0),
            at(cyl(2 * S['groove'][2], S['groove'][0], S['groove'][1], NF), CH_X, 0),
            at(hull_of((circle_pts(2 * S['r'], NF), S['top'] - 0.6), (circle_pts(2 * (S['r'] + 0.7), NF), S['top'] + 0.01)), CH_X, 0),
            # 6.4.0 slicer check: the groove ceiling was a 2.1 mm ring over air. The unchanged TPU chute lip anchors on it from r 24.95
            # outward (b611.CH_LIP), so only the 0.6 mm bore-side strip it does not use becomes a 45 deg chamfer; 1.5 mm flat ring stays
            at(hull_of((circle_pts(2 * b611.CH_LIP['anchor'][0], NF), S['groove'][1] - 0.01), (circle_pts(2 * S['r'], NF), S['groove'][1] + b611.CH_LIP['anchor'][0] - S['r'])), CH_X, 0)]
    cuts += dcuts
    c = OR_3x1['csk_d']
    for x, y in CAP64.values():
        cuts += [at(cyl(3.4, Z_BOT - 1, CAP_BOSS_TOP + 1, 32), x, y),
                 at(cyl(CAP_CB_D, Z_BOT - 1, CAP_SEAT_Z, 64), x, y),
                 at(hull_of((circle_pts(c, 48), CAP_SEAT_Z - 0.01), (circle_pts(3.4, 48), CAP_SEAT_Z + (c - 3.4) / 2)), x, y)]
    cuts.append(prism(OPEN2D, Z_BOT - 5.0, Z_S + 20.0))     # the module opening
    cuts += edge_blunt(Z_BOT + 5.0, Z_S - b611.SEAM)        # review m10 (above the bottom chamfer)
    xe = XM0 - GAP                                          # review m9: 0.4 x 45 deg on the bottom seam edge
    cuts.append(trimesh.convex.convex_hull(np.array([[xe - 0.4, y, Z_BOT - 0.01] for y in (-80, 80)] + [[xe + 0.01, y, Z_BOT - 0.01] for y in (-80, 80)] + [[xe + 0.01, y, Z_BOT + 0.4] for y in (-80, 80)])))
    return D(body, cuts)


def drain64():
    """review m11: the 4 x Ø0.8 exit holes would print closed. Two Ø1.5 holes instead; the three 0.8 mm entry slits of the
    labyrinth stay and are the insect barrier (as 6.1.1: slits and holes never in line)"""
    dr = b611.DRAIN
    xd, yd = b611.DRAIN_XY
    bos = at(cyl(2 * dr['boss_r'], Z_BOT - 1, dr['boss_top'], 64), xd, yd)
    cuts = [at(cyl(2 * dr['ch_r'], dr['ch_z'][0], dr['ch_z'][1], 64), xd, yd)]
    for k in range(dr['n_slits']):
        cuts.append(at(rotz(box(dr['ch_r'] - 0.5, dr['boss_r'] + 1.0, -dr['slit_w'] / 2, dr['slit_w'] / 2, *dr['slit_z']), 90.0 + 120.0 * k), xd, yd))
    for a in DRAIN_HOLES['ang']:
        hx, hy = polar(DRAIN_HOLES['r'], a)
        cuts.append(at(cyl(DRAIN_HOLES['d'], Z_BOT - 1, dr['ch_z'][0] + 0.01, 24), xd + hx, yd + hy))
    return bos, cuts


def build_cap_lip64():
    with patched(b61, WALL_C=WALL_C64):
        return b61.build_cap_gasket61()


# =====================================================================================
# 3. SHELL (guscio_v64): the 6.1.1 shell with the module opening + return ribs
# =====================================================================================
def build_shell64(shell611):
    ribs = edge_ribs(T_SHELL, b611.SPIG_TOP + 0.4, ZSH)      # above the cap spigot
    # review M2 (small): 45 deg lead-in of the ribs above the opening (they started as an abrupt fin in print)
    n = 12
    lead = [edge_ribs(T_SHELL, ZSH + j * RIB['depth'] / n - 0.01, ZSH + (j + 1) * RIB['depth'] / n, depth=RIB['depth'] * (1 - (j + 1) / n)) for j in range(n - 1)]
    # review M2: 45 deg corbel from the wall under each bowl tab (print side), as far in as the bowl allows (r 62.6)
    gus = []
    inside = pod_solid(T_SHELL - 0.5)
    for a in b611.TAB_ANG:
        rw = b63.b62.shell_r_at(a, 14.0, T_SHELL) + 1.5
        pts = [[r_, sg * b611.TAB_W / 2, z_] for sg in (-1, 1) for r_, z_ in ((TAB_GUS_R0, -0.5), (rw, -0.5), (rw, rw - TAB_GUS_R0), (TAB_GUS_R0, 0.0))]
        gus.append(I(rotz(trimesh.convex.convex_hull(np.array(pts)), a), inside))
    return D(U([shell611, ribs] + lead + gus), [prism(OPEN2D, Z_S - 5.0, ZSH)] + edge_blunt(Z_S, ZSH))


# =====================================================================================
# 4. MODULE "case 1.0"
# =====================================================================================
def ramp_w64(phi):
    def ss(t):
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3 - 2 * t)
    p = (np.asarray(phi, float) + 180.0) % 360.0 - 180.0
    return ss((p - PHI_A64) / PHI_RAMP64) * ss((PHI_B64 - p) / PHI_RAMP64)


def band_solid64():
    """as b63.band_solid, with the band on the east face (angles wrapped to -180..180)"""
    zs = np.unique(np.r_[Z_BOT - 1.0, np.linspace(Z_BOT + 0.01, ZB0 - 1.0, 24), np.linspace(ZB0 - 1.0, ZB1 + 1.0, 14), np.linspace(ZB1 + 1.0, -30.0, 12)])
    ph = np.linspace(0.0, 360.0, 720, endpoint=False)
    w = ramp_w64(ph)
    rings = []
    for z in zs:
        cx, R = pod_circle(0.0, min(max(z, Z_BOT + 0.01), -20.0))
        rf = band_rho(z)
        rho = (R + B_MARGIN) - w * max(0.0, R + B_MARGIN - rf)
        a = np.radians(ph)
        rings.append(np.c_[cx + rho * np.cos(a), rho * np.sin(a), np.full(len(ph), z)])
    return loft_rings(rings)


def band_inner64(off):
    """b63.band_inner_solid is only valid where the band is; elsewhere the pod offset rules: intersect the two outside"""
    return band_inner_solid(off)


def lid_plan():
    c, r = pod_circle(0.0, Z_LAND)
    return PLAN_RIM.intersection(Point(c, 0).buffer(r - PAR - 0.3, resolution=128))


def lid_opening():
    c, r = pod_circle(0.0, Z_RIM0)
    o = shapely.unary_union([sbox(O_BACK, -O_Y, 200.0, O_Y), sbox(FRONT_X0, -(YM - O_SIDE), 200.0, YM - O_SIDE)])
    o = o.intersection(Point(c, 0).buffer(r - O_SKIN, resolution=128))
    for x, y in LID_SCREWS:
        o = o.difference(Point(x, y).buffer(LID_BOSS['d'] / 2, resolution=32))
    return o.buffer(-0.6, join_style=1).buffer(0.6, join_style=1)        # no knife edges


def panel_parts64():
    with patched(b63, ELEMS=ELEMS64):
        return b63.panel_parts()


def build_tub64():
    """module tub: outer face = pod skin (flush), back / side walls vertical, open top with a seal land and a parapet"""
    wedge, z_wedge, _ = bottom_fill()
    pod_o = U([pod_solid(0.0), wedge])                      # review M3: 45 deg chamfer under the bottom radius
    outer = I(pod_o, U([prism(PLAN, Z_BOT - 1.0, ZN0), prism(PLAN_UP, ZN0 - 0.01, ZMT)]))
    # closed sockets round the holder posts (ZN0..ZSOCK) and the rim thickening of the notch walls (45 deg stair below)
    add = []
    for s in (1, -1):
        px, py = post_xy(s)
        blk = sbox(XM0, NY0 - 0.01, NX1 + 0.01, YM) if s > 0 else sbox(XM0, -YM, NX1 + 0.01, -NY0 + 0.01)
        add.append(prism(blk.difference(Point(px, py).buffer(POST['d'] / 2 + SOCK_GAP, resolution=64)), ZN0 - 0.01, ZSOCK))
    strip = PLAN_RIM.difference(PLAN_UP)
    n = 20                                                   # review m4: 0.1 mm steps = a true 45 deg face for the slicer
    for j in range(n):
        g = PLAN_UP.buffer(RIM_T * (j + 1) / n, join_style=2).intersection(strip)
        add.append(prism(g, Z_RIM0 - RIM_T + RIM_T * j / n, Z_RIM0 - RIM_T + RIM_T * (j + 1) / n + 0.01))
    add.append(prism(strip, Z_RIM0, Z_LAND))
    outer = U([outer] + [I(a, pod_o) for a in add])
    # top lip behind the shell wall (retains the module top against an outward pull; closes the horizontal seam)
    lip = I(D(pod_solid(T_SHELL + LIP['gap']), [pod_solid(T_SHELL + LIP['gap'] + LIP['t'])]), prism(sbox(XM0, -YM + 3.0, 200.0, YM - 3.0), ZMT - 0.01, ZMT + LIP['h']))   # review m10: the lip stops 3 mm before its ends
    # cavity
    c2d = shapely.unary_union([sbox(XM0 + WALL_B, -GUIDE_Y, 200.0, GUIDE_Y), sbox(FRONT_X0, -(YM - WALL_S), 200.0, YM - WALL_S)])
    big = sbox(-300, -300, 300, 300)
    band_in = U([band_inner_solid(BAND_WALL), prism(big, ZB1 + 2.0, 0.0)])       # the band loft ends at -66: free above the band
    cav = I(I(pod_solid(WALL_M), band_in), prism(c2d, Z_BOT, Z_LAND))
    cav0 = cav.copy()                                        # plain cavity (real walls) for the boss corbels
    o2d = lid_opening()
    big = sbox(-300, -300, 300, 300)
    n = 68                                                   # review m4: 0.1 mm steps
    hstair = O_SKIN - WALL_M
    fill = [prism(big.difference(o2d), Z_RIM0, Z_LAND + 1.0)]
    for j in range(n):
        fill.append(prism(big.difference(o2d.buffer(hstair * (1 - (j + 1) / n), join_style=1)), Z_RIM0 - hstair + hstair * j / n, Z_RIM0 - hstair + hstair * (j + 1) / n + 0.01))
    cav = D(cav, fill)
    # board slots in the guide walls
    fins, slots = [], []
    for s in (1, -1):
        for k in ('A', 'B'):
            xs = SLOTS[k]
            ys0, ys1 = (GUIDE_Y - 1.0, GUIDE_Y + SLOTS['depth']) if s > 0 else (-GUIDE_Y - SLOTS['depth'], -GUIDE_Y + 1.0)
            slots.append(box(xs - 0.15, xs - 0.15 + SLOTS['w'], ys0, ys1, SLOTS['z0'], Z_LAND + 1.0))
    # lid screw bosses (PT pilots), 0.5 proud of the land = hard stop for the lid
    bosses, pilots = [], []
    for x, y in LID_SCREWS:
        bz0 = Z_LU - LID_BOSS['h']
        bosses.append(at(U([cyl(LID_BOSS['d'], bz0, Z_LU, 48), hull_of((circle_pts(1.0, 24), bz0 - 3.2), (circle_pts(LID_BOSS['d'], 48), bz0 + 0.01))]), x, y))
        pilots.append(at(U([cyl(PT['pilot'], Z_LU - 8.5, Z_LU + 1.0, 32), hull_of((circle_pts(PT['pilot'], 32), Z_LU - 0.4), (circle_pts(PT['pilot'] + 0.82, 32), Z_LU + 0.01))]), x, y))
    # speaker seat collar on the floor + grille through the floor
    sx, sy = SPK64['x'], SPK64['y']
    collar = at(U([D(cyl(SPK64['collar_id'] + 2 * SPK64['collar_t'], Z_BOT + 0.5, SPK64['collar_top'], 96), cyl(SPK64['collar_id'], Z_BOT, SPK64['collar_top'] + 1, 96)),
                   D(cyl(SPK64['collar_id'] + 0.1, Z_BOT + 0.5, SPK64['seat_z'], 96), cyl(SPK64['ledge_id'], Z_BOT, SPK64['seat_z'] + 1, 96))]), sx, sy)
    collar = D(collar, [at(box(-2.0, 2.0, 0.0, 30.0, SPK64['seat_z'] - 1.5, SPK64['collar_top'] + 1), sx, sy)])       # wire notch (north)
    grille = []
    for hx, hy in [(0.0, 0.0)] + [polar(SPK64['grille_r'], 30.0 + 60.0 * k) for k in range(6)]:
        grille += [at(cyl(SPK64['hole'], Z_BOT - 1, Z_BOT + FLOOR_M + 0.5, 24), sx + hx, sy + hy),
                   at(hull_of((circle_pts(SPK64['hole'] + 1.0, 24), Z_BOT - 0.01), (circle_pts(SPK64['hole'], 24), Z_BOT + 0.5)), sx + hx, sy + hy)]
    pp = panel_parts64()
    inside = pod_solid(WALL_M - 0.2)
    body = U([outer, lip] + [I(b_, pod_o) for b_ in pp['bosses']])
    body = D(body, [D(cav, pp['bosses'])])
    room = I(inside, prism(c2d.buffer(0.3), Z_BOT, Z_LAND))                 # additions stay inside the cavity plan
    # 6.4.0 slicer check: the boss cone tips started in mid-air 1.5-3.3 mm from the wall. Each boss is now the hull of the boss, its
    # cone and a disc sunk into the nearest wall 45 deg lower: the underside rises at 45 deg from the wall (prints without support)
    bz0 = Z_LU - LID_BOSS['h']
    sec_ = cav0.section(plane_origin=[0, 0, bz0 - 1.0], plane_normal=[0, 0, 1]); T_ = np.eye(4); T_[2, 3] = -(bz0 - 1.0)
    p2_, _ = sec_.to_2D(to_2D=T_)
    walls_ = shapely.unary_union(list(p2_.polygons_full)).boundary
    corbels = []
    CORBEL_INFO.clear()
    for x, y in LID_SCREWS:
        q_ = shapely.ops.nearest_points(walls_, Point(x, y))[0]
        v_ = np.array([q_.x - x, q_.y - y]); d_ = float(np.linalg.norm(v_)); u_ = v_ / d_
        t_ = d_ + 1.5
        wx, wy = x + u_[0] * t_, y + u_[1] * t_
        cb = circle_pts(LID_BOSS['d'], 48)
        corbels.append(I(hull_of((cb + [x, y], Z_LU), (cb + [x, y], bz0), (circle_pts(1.0, 24) + [x, y], bz0 - 3.2),
                                 (cb + [wx, wy], Z_LU), (cb + [wx, wy], bz0 - 3.2 - t_)), outer))     # stays inside the module envelope (notches free)
        CORBEL_INFO.append({'screw_xy': [x, y], 'wall_gap_mm': round(d_ - LID_BOSS['d'] / 2, 2), 'toward': [round(float(u_[0]), 2), round(float(u_[1]), 2)],
                            'corbel_bottom_z': round(bz0 - 3.2 - t_, 2)})
    body = U([body] + [I(f, room) for f in fins + [collar]] + [I(b_, room) for b_ in bosses] + corbels)
    # lid recess above the land (the skin wall stays as a parapet), lock screws, slots, pilots, grille, panel cuts
    cl, rl = pod_circle(0.0, Z_LAND)
    recess = prism(PLAN_RIM.buffer(0.5).intersection(Point(cl, 0).buffer(rl - PAR, resolution=128)), Z_LAND, ZMT + 1.0)
    cuts = [recess] + slots + pilots + grille + pp['cuts']
    for s in (1, -1):
        px, py = post_xy(s)
        cuts += [at(cyl(LOCK['clr'], Z_BOT - 1.0, ZN0 + 1.0, 32), px, py), at(cyl(LOCK['cb_d'], Z_BOT - 3.0, LOCK['seat_z'], 48), px, py)]
        # review m9: 0.4 x 45 deg on the vertical back corners
        cuts.append(trimesh.convex.convex_hull(np.array([[XM0 - 0.01, s * YM + s * 0.01, z_] for z_ in (Z_BOT - 1, ZMT + 5)] + [[XM0 + 0.4, s * YM + s * 0.01, z_] for z_ in (Z_BOT - 1, ZMT + 5)] +
                                                        [[XM0 - 0.01, s * (YM - 0.4), z_] for z_ in (Z_BOT - 1, ZMT + 5)])))
    cuts.append(trimesh.convex.convex_hull(np.array([[XM0 - 0.01, y, Z_BOT - 0.01] for y in (-80, 80)] + [[XM0 + 0.4, y, Z_BOT - 0.01] for y in (-80, 80)] + [[XM0 - 0.01, y, Z_BOT + 0.4] for y in (-80, 80)])))
    body = D(body, cuts)
    body = U([body] + [I(b_, I(inside, prism(c2d.buffer(0.3), Z_BOT, ZMT))) for b_ in bosses_top(bosses)])
    body = D(body, pilots)
    body = I(body, U([band_solid64(), prism(big, Z_BOT - 5.0, ZB0 - 1.5)]))    # the band never clips the bottom chamfer
    return body, pp


def bosses_top(bosses):
    """the lid recess cut the boss tops back to the land: put the 0.5 hard-stop tops back"""
    return [I(b_, prism(sbox(-300, -300, 300, 300), Z_LAND - 0.01, Z_LU)) for b_ in bosses]


def lid_gasket_centre():
    return lid_plan().buffer(-2.25, join_style=1, resolution=16)     # review m6: groove outer wall 1.2


def build_lid64():
    lp = lid_plan()
    lid = prism(lp, Z_LU, ZMT)
    wc = lid_gasket_centre()
    groove = prism(ring2d(wc.buffer(b611.GRV_W611 / 2, join_style=1, resolution=16), wc.buffer(-b611.GRV_W611 / 2, join_style=1, resolution=16)),
                   Z_LU - 1.0, Z_LU + b61.GRV_D)
    # stiffening rib along the back edge on top (interrupted under the P3 pad)
    # stiffening ribs on top along the edges that cannot take a screw (back edge and both notch edges); gap under the P3 pad
    ribs = [box(XM0 + 3.6, XM0 + 6.1, -(NY0 + RIM_T) + 3.6, NY0 + RIM_T - 3.6, ZMT - 0.01, ZMT + 3.2)]
    ribs += [box(XM0 + 3.6, NX1 + 3.0, min(s * (NY0 + RIM_T - 3.6), s * (NY0 + RIM_T - 6.1)), max(s * (NY0 + RIM_T - 3.6), s * (NY0 + RIM_T - 6.1)), ZMT - 0.01, ZMT + 3.2) for s in (1, -1)]
    rib = D(U(ribs), [box(XM0, XM0 + 12, P_SCREWS[2][1] - 8.0, P_SCREWS[2][1] + 8.0, ZMT - 1, ZMT + 5)])
    lf = LID_FENCE                                           # fence in front of the P3 pad: the parked harness loop cannot slide under it
    rib = U([rib, box(lf['x'][0], lf['x'][1], lf['y'][0], lf['y'][1], ZMT - 0.01, ZMT + lf['h'])])
    jx, jy = J1['xy']
    zt = ZMT + J1['tur_h']                                   # J1 sits in a turret: its body stays above the lid, clear of the boards
    tur = at(cyl(J1['tur_d'], ZMT - 0.01, zt, 96), jx, jy)
    body = U([lid, rib, tur])
    zi = zt - J1['tur_top']                                  # nut seat. review m7: 45 deg run-in to a Ø13 flat, 0.2 mm skin over the hole (drill Ø8.2)
    hc = (J1['tur_id'] - J1['seat_d']) / 2
    cuts = [groove, at(cyl(J1['tur_id'], Z_LU - 1, zi - hc + 0.01, 96), jx, jy),
            at(hull_of((circle_pts(J1['tur_id'], 96), zi - hc), (circle_pts(J1['seat_d'], 96), zi)), jx, jy),
            at(cyl(J1['hole'], zi + J1['skin'], zt + 1, 48), jx, jy)]
    c = OR_3x1['csk_d']
    for x, y in LID_SCREWS:
        cuts += [at(cyl(3.4, Z_LU - 1, ZMT + 1, 32), x, y),
                 at(hull_of((circle_pts(3.4, 48), ZMT - (c - 3.4) / 2), (circle_pts(c, 48), ZMT + 0.01)), x, y)]
    ux, uy = USB['xy']                                       # blind USB-C position: engraved ring + dot on the top face
    cuts += [at(D(cyl(USB['ring_d'] + 0.6, ZMT - 0.3, ZMT + 1, 64), cyl(USB['ring_d'] - 0.6, ZMT - 1, ZMT + 2, 64)), ux, uy), at(cyl(1.2, ZMT - 0.3, ZMT + 1, 24), ux, uy)]
    cuts.append(face_region(text_poly(CASE_VER.upper(), 4.0, 33.0, 16.0), ZMT, True))
    return D(body, cuts)


def build_lid_gasket64(n=6):
    """lip gasket as the cap lip (base 2.2 in the lid groove, 0.8 lip leaning 1.0 inward over 1.7), built in layers because the
    lid outline is not convex (the cap lip builder uses hulls); lip points DOWN onto the tub land"""
    wc = lid_gasket_centre()
    rr = lambda a, b_: ring2d(wc.buffer(a, join_style=1, resolution=16), wc.buffer(b_, join_style=1, resolution=16))
    parts = [prism(rr(1.075, -1.075), Z_LU - 0.01, Z_LU + b61.GRV_D - 0.05)]
    h = b61.LIP_GH / n
    for j in range(n):
        off = (j + 0.5) / n * b61.LIP_LEAN                   # lip tip points OUTWARD: outside pressure presses it on (review)
        parts.append(prism(rr(off + 0.4, off - 0.4), Z_LU - (j + 1) * h, Z_LU - j * h + 0.01))
    return U(parts)


def build_spk_ring64(spk_d=None):
    d = SPK64['spk_d'] if spk_d is None else spk_d
    z0 = SPK64['seat_z']
    ring = D(cyl(SPK64['ring_od'], z0, z0 + SPK64['ring_h'], 96), U([cyl(d - 3.0, z0 - 1, z0 + 1.0, 96), cyl(d + 0.4, z0 + 1.0 - 0.01, z0 + SPK64['ring_h'] + 1, 96)]))
    ring = D(ring, [box(-2.0, 2.0, 0.0, 30.0, z0 + 1.0, z0 + SPK64['ring_h'] + 1)])
    return at(ring, SPK64['x'], SPK64['y'])


# =====================================================================================
# 5. BOUGHT PARTS / HARNESS (models for checks and the viewer)
# =====================================================================================
def plug_exit(D=0.0):
    """cable exit of the angled M8 plug on J1 (points +y), module lowered by D"""
    return (J1['xy'][0], J1['xy'][1] + 22.0, ZMT + J1['tur_h'] + 10.5 - D)


def tail_points(D=None):
    """centre line of the harness tail (round PUR Ø4.5) from the Y splice over the lug to the plug.
    D=None: parked (module in): over the module south rim onto the lid, north along the back fence, U-turn R 11.5, back south
    and up into the plug. D >= 80: module lowered by D: from the lug over the rim zone straight down through the vacated opening"""
    sx, sy, sz = HARN['splice']
    top = (sx, sy, sz + HARN['splice_len'] / 2)
    A = HARN['anchor']
    ex_, ey_ = EYELET['xy']
    head = [top, (13.0, -62.5, -39.0), (16.6, -60.5, -37.0), A, (22.0, -56.0, -31.5), (28.0, -52.5, -27.0), (ex_, ey_, -26.5), (ex_, ey_, ZMT + HARN['r_tail'] + 0.15)]   # straight down through the hook to lid height
    zl = ZMT + HARN['r_tail'] + 0.15
    if D is None:
        u = [(43.1 + 11.5 * math.cos(math.radians(a)), 18.5 + 11.5 * math.sin(math.radians(a)), zl) for a in np.linspace(180.0, 0.0, 13)]
        ex = plug_exit()
        return head + [(32.0, -44.0, zl), (31.6, -41.6, zl), (31.6, -39.0, -31.2), (31.6, -30.8, -31.2), (31.6, -27.0, zl)] + u + \
            [(54.6, 14.0, zl), (52.5, 9.0, -31.5), (48.5, 6.5, -24.0), (45.6, 4.5, -17.0), (ex[0], ex[1] + 3.0, ex[2] - 0.1), ex]
    ex = plug_exit(D)
    return head + [(33.0, -30.0, -60.0), (33.0, -8.0, ex[2] + 6.0), (37.0, 9.0, ex[2] - 0.5), (43.0, 7.0, ex[2] - 0.5),
                   (ex[0], ex[1] + 3.0, ex[2]), ex]


def path_len(pts):
    p = np.asarray(pts, float)
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


def chassis_bought():
    B = {}
    sv = rotz(dt.servo_solid, 90.0)
    sv.apply_translation([0, 0, v6.DZ_SERVO])
    B['servo'] = sv
    g = Point(GLAND['x'], GLAND['z'])
    yf = BAY[2]
    B['gland_m12'] = U([b61.yprism(g.buffer(7.6, resolution=6), yf - GLAND['pad_t'] - 7.0, yf - GLAND['pad_t'] + 0.01),
                        b61.yprism(g.buffer(6.0, resolution=32), yf - GLAND['pad_t'] - 16.0, yf - GLAND['pad_t'] - 6.99),
                        b61.yprism(g.buffer(5.9, resolution=32), yf - GLAND['pad_t'], yf + 5.0),
                        b61.yprism(g.buffer(8.6, resolution=6), yf + b61.BX_T + 0.01, yf + b61.BX_T + 4.0)])
    vp = trimesh.creation.cylinder(radius=VENT64['patch_d'] / 2, height=0.3, sections=32)
    vp.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    vp.apply_translation([BAY[0] + b61.BX_T + 0.15, VENT64['y'], VENT64['z']])
    B['vent_patch_eptfe'] = vp
    B['oring_shaft_9x2'] = U([v6.torus(dt.OR_GROOVE_D / 2 + 1.0, 1.0, z) for z in v6.OR_SHAFT_Z])
    B['oring_face_24x2'] = v6.torus(v6.FACE_OR['id'] / 2 + 1.0, 1.0, Z_R + 1.0)
    B['oring_3x1'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, Z_R - ROOF_T + 0.45, x=x, y=y, n=48) for x, y in P_SCREWS[1:2]])     # P2 only
    B['oring_3x1_cap'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, CAP_SEAT_Z + 0.45, x=x, y=y, n=48) for x, y in CAP64.values()])
    jx, jy = J1['xy']
    # chassis harness: one M8 5-pin angled plug on J1; Y split into the 12 V pigtail (pod-top M8) and the servo lead (gland)
    zt = ZMT + J1['tur_h']
    B['plug_m8_5p_angled'] = U([at(cyl(10.0, zt + 2.2, zt + 15.0, 32), jx, jy), box(jx - 4.5, jx + 4.5, jy, jy + 22.0, zt + 6.0, zt + 15.0)])   # cable exit +y
    sx, sy, sz = HARN['splice']
    B['harness_tail'] = tube_path(tail_points(), HARN['r_tail'], 16)                  # parked service loop on the lid
    B['harness_splice_y'] = at(cyl(HARN['splice_d'], sz - HARN['splice_len'] / 2, sz + HARN['splice_len'] / 2, 24), sx, sy)
    B['harness_12v'] = tube_path([(sx, sy, sz + HARN['splice_len'] / 2 - 1.0), (4.0, -66.0, -24.0), (1.0, -68.5, -8.0), (0.0, -69.2, 6.5)], HARN['r_12v'], 16)
    # servo branch: ROUND 3-core cable through the M12 gland (seals properly), JR female crimped on inside the bay
    B['harness_servo'] = tube_path([(sx, sy, sz - HARN['splice_len'] / 2 + 1.0), (2.0, -64.0, -56.0), (-3.0, -63.0, -49.0), (-3.0, -59.5, -48.0), (-3.0, -35.0, -48.0),
                                    (-2.0, -31.5, -46.5), (-1.2, -29.2, -47.0)], HARN['r_branch'], 16)
    B['jr_3p_junction'] = box(JR['x'][0], JR['x'][1], JR['y'][0], JR['y'][1], JR['z'][0], JR['z'][1])
    B['servo_lead_in_bay'] = tube_path([(0.0, -16.5, -84.0), (0.0, -24.0, -84.0), (-1.2, -29.2, -77.0)], 1.0, 12)      # the servo's own flat lead, untouched
    a, b_ = b62.CONN62
    B['connector_m8_ip67'] = U([at(cyl(12.0, a[2], b_[2], 32), a[0], a[1]), at(cyl(13.0, (a[2] + b_[2]) / 2 - 4, (a[2] + b_[2]) / 2 + 4, 6), a[0], a[1])])
    sc = {}
    tz = dt.TAB_Z0 + v6.DZ_SERVO
    sc['m3x8_servo'] = U([at(U([cyl(3.0, tz - 0.01, tz + 8.0 - dt.WASHER_T, 24), cyl(7.0, tz - dt.WASHER_T, tz, 32), cyl(5.5, tz - dt.WASHER_T - 3.0, tz - dt.WASHER_T, 32)]), x, y)
                          for x, y in b61.SERVO_HOLES_W])
    sc['m3x8_hub'] = v6.screw_m3(0, 0, v6.HUB_SCREW_HEAD_Z, v6.HUB_SCREW_LEN, head_up=True)
    sc['inserts_servo'] = U([at(cyl(4.0, CAGE_Z0 + 0.2, CAGE_Z0 + 5.9, 24), x, y) for x, y in b61.SERVO_HOLES_W])
    sc['inserts_holder'] = U([at(cyl(4.0, POST['z0'] + 0.2, POST['z0'] + 5.9, 24), *post_xy(s)) for s in (1, -1)])
    sc['pt_k30x12_cap'] = U([b63.pt_screw(x, y, CAP_SEAT_Z, PT['len_cap']) for x, y in CAP64.values()])
    sc['m3x16_module_lock'] = U([v6.screw_m3(*post_xy(s), LOCK['seat_z'], LOCK['len']) for s in (1, -1)])
    tl = TIE_LUG                                             # cable tie round the lug bar and the tail
    ring = D(box(tl['x'][0] - 0.6, HARN['anchor'][0] + HARN['r_tail'] + 0.7, tl['y'][0] - 0.7, tl['slot_y'][1] - 0.05, tl['slot_z'][0] + 0.4, tl['slot_z'][1] - 0.4),
             [box(tl['x'][0] - 0.01, HARN['anchor'][0] + HARN['r_tail'], tl['y'][0] + 0.01, tl['slot_y'][0] + 0.01, tl['slot_z'][0], tl['slot_z'][1])])
    sc['cable_tie_harness'] = D(ring, [box(tl['x'][0], tl['x'][1], tl['y'][0], tl['y'][1], -100, 0), tube_path([HARN['anchor'], (HARN['anchor'][0], HARN['anchor'][1] + 3, HARN['anchor'][2])], HARN['r_tail'], 16)])
    return B, sc


def module_bought(pp):
    with patched(b63, SPK=dict(b63.SPK, x=SPK64['x'], y=SPK64['y'])):
        B = b63.panel_bought(pp)
    B.pop('harness_jst', None)
    sx, sy = SPK64['x'], SPK64['y']
    zf = Z_BOT + FLOOR_M
    B['membrane_acoustic_ip67'] = at(cyl(15.0, zf, zf + 0.25, 48), sx, sy)
    z0 = SPK64['seat_z'] + 1.0
    B['speaker_23mm'] = at(U([cyl(SPK64['spk_d'], z0, z0 + SPK64['spk_h'], 48)]), sx, sy)
    B.pop('speaker_20mm', None)
    xa = SLOTS['A']
    zb0, zb1 = SLOTS['z0'], SLOTS['z0'] + 50.0
    B['board_70x50_A'] = box(xa, xa + 1.6, -35.0, 35.0, zb0, zb1)
    B['esp32_wrover_stack'] = box(xa + 1.6, xa + 1.6 + 25.0, -30.5, 30.5, -74.5, -46.5)
    B['reg_6v'] = box(xa + 1.6, xa + 1.6 + 20.3, -29.0, -3.6, -88.0, -78.5)       # lying under the ESP zone (flying leads or a shelf)
    B['reg_5v'] = box(xa + 1.6, xa + 1.6 + 6.0, 21.0, 33.0, -90.0, -80.0)
    cap = trimesh.creation.cylinder(radius=5.0, height=20.0, sections=32)
    cap.apply_translation([40.0, 36.0, -65.5])
    B['cap_1000uF'] = cap
    jx, jy = J1['xy']
    zt = ZMT + J1['tur_h']
    zi = zt - J1['tur_top']
    B['socket_m8_5p'] = U([at(cyl(J1['hole'] - 0.2, zi - J1['body_len'], zt + 6.0, 32), jx, jy), at(cyl(J1['body_d'], zi - J1['body_len'], zi - 3.0, 32), jx, jy),
                           at(cyl(12.0, zi - 3.0, zi, 6), jx, jy), at(cyl(12.0, zt, zt + 2.2, 6), jx, jy)])
    sc = {}
    sc['pt_k30x10_lid'] = U([at(U([cyl(3.0, ZMT - 10.0, ZMT + 0.01, 24), cyl(PT['head_d'], ZMT, ZMT + PT['head_h'], 32)]), x, y)
                            for x, y in LID_SCREWS])
    B['oring_3x1_lid'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, ZMT - 0.45, x=x, y=y, n=48) for x, y in LID_SCREWS])
    return B, sc


# =====================================================================================
# BUILD / EXPORT
# =====================================================================================
RHO = {'scatola_v64': PETG, 'fondello_v64': PETG, 'guscio_v64': PETG, 'guarnizione_fondello_v64': TPU,
       'modulo_vasca_v64': PETG, 'modulo_coperchio_v64': PETG, 'modulo_guarnizione_v64': TPU, 'modulo_anello_speaker_v64': PETG}
CHASSIS_NEW = ['scatola_v64', 'fondello_v64', 'guscio_v64', 'guarnizione_fondello_v64']
MODULE_NEW = ['modulo_vasca_v64', 'modulo_coperchio_v64', 'modulo_guarnizione_v64', 'modulo_anello_speaker_v64']
FLIP = {'scatola_v64': True, 'modulo_guarnizione_v64': True, 'guscio_v64': True}   # box prints roof down; lid gasket base down (lip up)


def print_matrix(m, name):
    T = np.eye(4)
    if FLIP.get(name):
        T = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
    if name == 'modulo_coperchio_v64':                      # lid: top face (rib, pad) up is fine: underside (groove) on the bed -> flip so the flat top is down
        T = np.eye(4)
    p = m.copy(); p.apply_transform(T)
    return trimesh.transformations.translation_matrix([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]]) @ T


def drop_fins(m):
    """remove closed zero-volume slivers (back-to-back triangle pairs) that some booleans leave behind"""
    parts = m.split(only_watertight=False)
    keep = [p for p in parts if abs(p.volume) > 1e-2 and len(p.faces) > 8]
    if len(keep) == len(parts):
        return m
    return keep[0] if len(keep) == 1 else trimesh.util.concatenate(keep)


def export_part(name, m):
    m = clean64(drop_fins(m))
    m.export(staged(OUT + f'{name}.stl')); m.export(staged(OUT + f'{name}.3mf'))
    wt = bool(trimesh.load(current(OUT + f'{name}.stl')).is_watertight)
    T = print_matrix(m, name)
    pm = m.copy(); pm.apply_transform(T)
    pm = clean64(drop_fins(pm))
    scn = trimesh.Scene(); scn.add_geometry(pm, geom_name=name, node_name=name)
    scn.export(staged(OUT + f'{name}_print.3mf'))
    pm.export(staged(OUT + f'{name}_print.stl'))
    pm.export(SCRATCH + '_pchk.stl')
    wt = wt and bool(trimesh.load(SCRATCH + '_pchk.stl').is_watertight)
    return wt, pm


def build_all():
    P, EXTRA = {}, {}
    shell611 = v6.clean(trimesh.load(OUT + 'guscio_v611.stl'))
    assert shell611.is_volume
    EXTRA['BOTTOM_FILL'] = bottom_fill()
    P['scatola_v64'] = build_box64()
    P['fondello_v64'] = build_cap64()
    P['guscio_v64'] = build_shell64(shell611)
    P['guarnizione_fondello_v64'] = build_cap_lip64()
    P['modulo_vasca_v64'], EXTRA['PANEL'] = build_tub64()
    P['modulo_coperchio_v64'] = build_lid64()
    P['modulo_guarnizione_v64'] = build_lid_gasket64()
    P['modulo_anello_speaker_v64'] = build_spk_ring64()
    return P, EXTRA


if __name__ == '__main__':
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    P, EXTRA = build_all()
    print('\n--- v6.4 parts ---')
    for k, m in P.items():
        report(k, m)
    if STAGE == 'build':
        import pickle
        pickle.dump((P, EXTRA), open(SCRATCH + 'parts.pkl', 'wb'))
        sys.exit(0)
    EXPORT_WT, PR, OVH, GR = {}, {}, {}, {}
    for k, m in P.items():
        EXPORT_WT[k], PR[k] = export_part(k, m)
        OVH[k] = round(overhang(PR[k]), 1)
        GR[k] = v6.grams_est(m, RHO[k])
    print('exported; watertight on reload:', EXPORT_WT)
    exec(open(dt.HERE + 'build_v64_checks.py').read())
    import publish_v64                    # copy the deliverables from build/ into the repository folders
    publish_v64.main()
