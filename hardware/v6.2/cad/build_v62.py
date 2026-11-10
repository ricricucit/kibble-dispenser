#!/usr/bin/env python3
"""
Kibble Dispenser Outdoor - design v6.2 (from v6.1.1).

Owner-approved changes:
 1. Screw access. v6.1.1 had two screw sets between bowl, tower and box (3x M3x12 tower->bowl from below at r 19
    0/125/240, 3x M3x10 box->tower driven from ABOVE through a 26 mm gap under the bowl). The 240/235 deg pair sat
    2.5 mm apart and no order worked. With the top lobes at 0/125/240 no box-screw triangle reachable from below can
    surround the tower axis (inside the box only the servo|board corridor and the -Y bay are free; outside the box
    the chute and the 125/240 access bores block the -X side). v6.2 replaces BOTH sets by 3 long M3x40 that clamp
    box + tower + bowl in one stack, driven from below after the shell is on:
      P1 (-18.25, 24.5) outside the box through an ear (no seal needed),
      P2 (-1.5, -25.5) in the -Y bay and P3 (18.375, 14) in the servo|board corridor, through the roof with an
      O-ring 3x1 under the head (the dry box stays sealed).
    The tower (colonna_v62) gets 3 pillars instead of top/bottom lobes; the bowl (chiocciola_v62) gets its 3 tower
    inserts moved to P1..P3 (old holes filled); the box (scatola_v62) loses its blind plateau inserts and gets the
    ear + 2 sealed through holes; the ePTFE vent moves 4 mm +X to clear P2. Real build order: tower placed on the bowl
    -> chute (2 screws) -> shell (3 screws, box not there yet, so the A/B cups no longer block 120/240) -> box -> 3x M3x40.
 2. Kibble shut-off gate (saracinesca) + interlock. The flange becomes two plates: flangia_piano_v62 (lower, the
    v6.1.1 bayonet plate, r 90) and flangia_alta_v62 (upper, 8 mm, holds the blade pocket, the funnel and the shelf
    gasket). A green PETG sector blade (saracinesca_v62) turns about the shaft axis between them, in the plane of the
    flange funnel's pie opening (100.3 deg sector: the blade turns 113 deg = 100.6 to cover + 12.4 overtravel). It is
    driven by a full orange ring round the pod top (anello_saracinesca_v62) hanging under the flange rim; the ring
    covers the flush release button except through ONE window that lines up with the button only in the last
    ~3.4 deg of the closing stroke, i.e. after the blade has fully covered the opening (strict interlock, no springs).
 3. Cable: no shelf hole, no grommet in the shelf. The 12 V cable leaves the pod top through a curved tunnel in the
    flange (R 15 bend, TPU grommet passacavo_v62 at the pod side) and runs under the shelf in a snap-in channel
    (canalina_base/coperchio/tappo_v62). The IP67 M8 inline connector hangs from the flange inside the pod top
    annulus, so it is free in the gap as soon as the unit is twisted and lowered 8 cm.
 4. One comb lip design (labbro_pettine_v62, x4) in all 4 grooves (plates piastra_gate_v62 / piastra_finestra_v62
    with the short grooves lengthened).
 5./8. Kit split and firmware note: recorded in v62.json (checks file).
 6. 1:1 drilling template: template_v62/ (checks file).
 7. Fox-bite web: thumb-turn dishes 26 -> 24 (fondello_v62): web 1.72 -> 2.72 mm.
Frame and pose as v6.1.1 (Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED pose, gate OPEN).
No existing file is modified: changed parts carry the suffix _v62; unchanged parts are reused from v6.1.1 / v6.1.

Status: designed and checked in CAD only; not printed, assembled or tested yet.

Run from anywhere:  python hardware/v6.2/cad/build_v62.py
  1. runs the earlier stages first when their outputs are missing or older than their scripts, each into build/:
     build_v6.py (which runs build_dosing.py and build_v5.py), build_v61.py and build_v611.py, all with their checks,
     because v6.2 imports their parameters and reuses their parts, JSON files and assembled-position copies;
  2. builds and exports the v6.2 parts, runs the checks (build_v62_checks.py) and writes v62.json, v62_viewer.json,
     check_v62.png, the drilling template (template_v62/) and the assembled-position copies (v62_asm/), all in build/;
  3. publishes the repository files with publish_v62.py: ../assembly (viewer meshes and manifest), ../template
     (drilling template), v62.json and check_v62.png. The print package in ../plates is rebuilt from build/ by
     ../plates/tools/run_all.sh (needs the OrcaSlicer command line for the slicer check).
Optional argument: "build" stops after building, "parts" after exporting to build/ (no checks, no publishing).
ref/measure_v61.json and ref/ta_v611.json are baseline measurements of v6.1 and v6.1.1 (line of sight, tool access),
made once; the v6.1.1 and v6.2 checks compare against them. los.py and toolaccess.py are the helpers of those checks.
Dependencies: trimesh, manifold3d, shapely, mapbox_earcut, rtree, numpy, scipy, networkx, lxml, matplotlib, fast_simplification
(the v6.1 checks decimate meshes with trimesh's quadric decimation).
"""
import json
import math
import os
import sys
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, Point, box as sbox, LineString
from shapely import affinity
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_V5 = ['build_drivetrain.py', 'layout_v4.json', 'build_dosing.py', 'build_v5.py', 'build_v5_checks.py']
_PREREQUISITES = (     # script, inputs it depends on, outputs v6.2 reads from build/
    ('build_v6.py', _V5 + ['build_v6.py', 'build_v6_checks.py'], ['v6.json']),
    ('build_v61.py', _V5 + ['build_v6.py', 'build_v6_checks.py', 'build_v61.py', 'build_v61_checks.py'], ['v61.json', 'v61_viewer.json']),
    ('build_v611.py', _V5 + ['build_v6.py', 'build_v6_checks.py', 'build_v61.py', 'build_v61_checks.py', 'build_v611.py',
                             'build_v611_checks.py', 'los.py', 'ref/measure_v61.json'], ['v611.json', 'v611_viewer.json']),
)


def _ensure_prerequisites():
    """Run the earlier stages (v6, v6.1, v6.1.1, each with its checks) when an output is missing or out of date."""
    for script, deps, outputs in _PREREQUISITES:
        newest = max(os.path.getmtime(os.path.join(_HERE, f)) for f in deps)
        paths = [os.path.join(_HERE, 'build', o) for o in outputs]
        if all(os.path.exists(q) and os.path.getmtime(q) >= newest for q in paths):
            continue
        print(f'--- running {script} first ---', flush=True)
        subprocess.run([sys.executable, os.path.join(_HERE, script)], check=True)


if __name__ == '__main__':
    _ensure_prerequisites()

import build_v611 as b611
from build_v611 import (b61, v6, v5, dt, bd, OUT, U, D, I, cyl, box, at, hull_of, circle_pts, revolve, prism, ring2d, below,
                        above, polar, yprism, rotz, text_poly, face_region, overhang, vol, SEG, pod_solid, pod_circle,
                        section_fn, shell_r_at, radial_cyl, report, PETG, TPU, Z_TOP, R_TOP, Z_BOT, Z_S, T_SHELL, T_CAP,
                        BXO, BX_T, Z_R, Z_W, BOX_OUT, BOX_IN, ROOF_T, CRADLE_HALF_X, CAGE_Z0, BB, GLAND, CH_X, RI, RO,
                        FL_Z0, FL_Z1, LATCH_A, BTN_Z, TAB_ANG, TAB_R_INS, TAB_T, HOOKS61, PIN_ANG61, NF, TT,
                        SH_GRV, flap_poly, lip_revolve)
from build_v61 import (lip_lines, edge_s_range, line_strip, OUT_T, OUT_B, WIN_T, WIN_B, G0, G1, W0, W1, LIPS, LIPW, LIPD,
                       ANCH_W, ANCH_H, FLAP_T, FLAP_LEAN, LIP_PRE, SLIT_W, SLIT_STOP, DISC_Z0, DISC_Z1, PLATE_T, rotz_poly,
                       tube_path)

VER = 'v6.2'
SFX = '_v62'
SCRATCH = OUT                                               # probe exports, previews (build/)
ASM = OUT + 'v62_asm/'
TPL = OUT + 'template_v62/'
for _d in (SCRATCH, ASM, TPL):
    os.makedirs(_d, exist_ok=True)
v6.SCRATCH = SCRATCH

# =====================================================================================
# PARAMETERS v6.2
# =====================================================================================
# ---- 1. one screw set: 3x M3x40 clamp box + tower + bowl, driven from below ----
P_SCREWS = [(-18.25, 24.5), (-1.5, -25.5), (18.375, 14.0)]   # P1 outside (ear), P2 -Y bay, P3 servo|board corridor
P_SEALED = (False, True, True)                              # through the box roof: O-ring 3x1 under the head
PIL_R = 4.5                                                 # tower pillar radius (Ø9)
WEB_T = 4.0                                                 # tower web thickness
TOP_ARM_H = 4.0                                             # top arms (bear on the bowl underside)
TOP_ARM_R = 3.5                                             # top arm half-width (7 wide: clears the chute flange at P1)
EAR_R, EAR_Z0 = 4.6, Z_R - 5.0                              # box ear round P1 (5 mm thick, prints on the bed with the roof)
EAR_ROOT = 7.0                                              # ear root along the -X wall: 14 mm wide
SCREW_LEN = 40.0
INS_DEPTH62 = 8.5                                           # bowl insert holes for the M3x40 tips (tip at z +5.0..+7.6)
OR_3x1 = dict(id=3.0, cs=1.0, csk_d=5.2)                    # O-ring 3x1 NBR70 in a 90 deg countersink under the head
VENT62 = dict(x=12.0, y=-30.0, hole_d=12.2)                 # ePTFE vent moved +4 in X (clears P2)
# ---- 2. two-plate flange + rotary gate + interlock ring ----
DZ_FL = 8.0                                                 # upper plate thickness: the shelf sits 8 mm higher
FL_Z1_62 = FL_Z1 + DZ_FL                                    # 78.1 shelf underside
FL_R62 = 90.0                                               # both plates (v6.1.1: 84.5); the ring hangs 2 mm inside
OPEN_HALF = 50.15                                           # flange funnel pie opening: radial edges at +-50.15 deg
LEAD_OPEN = 50.5                                            # blade leading edge when OPEN (0.35 deg outside the pie)
STROKE = 113.0                                              # 2 x 50.3 to cover + 12.4 overtravel (window alignment band)
G_COVER = LEAD_OPEN + OPEN_HALF                             # 100.65 deg: from here on the pie is fully covered
BLADE_W = STROKE + 6.0                                      # 119 deg sector: 6 deg trailing support stays in the pocket
BLADE_R = 69.5
BLADE_Z = (FL_Z1 + 0.2, FL_Z1 + 3.2)                        # 70.3..73.3 (3.0 thick), 0.2 clearance top and bottom
POCKET_Z1 = FL_Z1 + 3.4                                     # 73.5
POCKET_R = 70.0
KNIFE = dict(edge_t=0.6, run=5.5)                           # single top bevel on the leading edge (pushes kibble up)
PIVOT_D, PIVOT_HOLE = 4.0, 4.3
ARM_ANG = 64.0                                              # arm angle when OPEN (gate frame); sweeps [-49, 64]
ARM_W, ARM_R = (8.0, (BLADE_R - 0.5, 88.6))
PEG = dict(r=85.75, d=3.0, hole=3.3)
RING = dict(ri=85.0, ro=88.0, z0=28.5, z1=FL_Z0 - 0.2, tongue=(85.0, 86.5), tongue_top=69.1, win_d=28.0, win_z=BTN_Z)
RING_GRV = dict(r0=84.85, r1=86.65, z1=69.3, uc=(87.2, 67.85))  # tongue groove in the lower plate underside + snap undercut
RING_BARB = dict(r1=87.0, z=(68.3, 68.85))                  # snap barb on the tongue: holds the ring up all round (360 deg)
RING_SLOT = dict(r0=84.05, r1=87.45, z0=68.8)               # peg slot over the arm sweep (lower plate top layer)
WIN_ANG = LATCH_A + STROKE                                  # window angle in the gate frame (lines up at the end of stroke)
DRAIN_ANG = -OPEN_HALF - 12.0                               # landing drain slot at the far end of the overtravel landing
WOOD_ANG62 = (80.0, 150.0, 225.0, 295.0)                    # clear of the arm sweep [-52, 67] and the cable tunnel (270)
WOOD_R62 = 75.5
JOIN = dict(r=57.0, ang=(215.0, 255.0, 290.0), pilot=2.4, clr=3.1, csk=6.0)   # ST2.9x9.5 DIN 7982, plates joined from the top
# ---- 3. cable: tunnel in the flange, channel under the shelf, connector in the pod top ----
CABLE_ANG = 270.0
CABLE_D = 5.0                                               # PUR 4x0.34, Ø5 (M8 A-coded IP67 pair)
TUN = dict(r_s=89.0, R=15.0, r_v=74.0, bore=5.6)
CH = dict(w=20.0, h=8.0, wall=1.4, base_t=1.2, rail=(6.6, 8.0), barb=(8.0, 8.6), seg=150.0, insert=5.0)
L2_CH = 112.0                                               # 2nd channel section cut to length (scene: shelf edge at y -360)
CONN62 = ((0.0, -69.2, 6.0), (0.0, -69.2, 49.0))            # M8 IP67 inline pair Ø12 x 44, hangs from the supply cable
# ---- 4. comb lips ----
LIP_L = 27.4                                                # one length for all 4 lips (longest edge 26.4 + 1.0)
LIP_SLITS = (-10.0, -5.0, 0.0, 5.0, 10.0)                   # symmetric about the middle: the lip is reversible end for end
# ---- 7. fox-bite web ----
TT_DISH_D62 = 24.0


def ang_of(p):
    return math.degrees(math.atan2(p[1], p[0]))


# =====================================================================================
# 1. TOWER (colonna_v62): tube + bushing as v6, 3 pillars + webs instead of top/bottom lobes
# =====================================================================================
def build_column62():
    collar = cyl(dt.COLLAR_D, -0.5, dt.COLLAR_Z1)
    tube = cyl(2 * v6.COL_R, v6.COL_FL_Z1 - 0.01, 0.0)
    disc = Point(0, 0).buffer(v6.FACE_OR['groove_od'] / 2 + 1.5, resolution=64)
    arms, webs, tops, pils = [], [], [], []
    for (x, y) in P_SCREWS:
        a = math.atan2(y, x)
        foot = (9.0 * math.cos(a), 9.0 * math.sin(a))
        arms.append(LineString([foot, (x, y)]).buffer(PIL_R, resolution=24))
        webs.append(prism(LineString([foot, (x, y)]).buffer(WEB_T / 2, cap_style=2), v6.COL_FL_Z1 - 0.01, -TOP_ARM_H + 0.01))
        tops.append(prism(LineString([foot, (x, y)]).buffer(TOP_ARM_R, resolution=24), -TOP_ARM_H, 0.0))
        # 45 deg chamfer under the top arm (prints upright without support)
        L = math.hypot(x - foot[0], y - foot[1])
        n = (-math.sin(a), math.cos(a))
        pts = []
        for s in (0.0, 1.0):
            px, py = foot[0] + s * (x - foot[0]), foot[1] + s * (y - foot[1])
            for side in (-1, 1):
                pts.append([px + side * TOP_ARM_R * n[0], py + side * TOP_ARM_R * n[1], -TOP_ARM_H])
                pts.append([px + side * WEB_T / 2 * n[0], py + side * WEB_T / 2 * n[1], -TOP_ARM_H - (TOP_ARM_R - WEB_T / 2)])
        tops.append(trimesh.convex.convex_hull(np.array(pts)))
        pils.append(at(cyl(2 * PIL_R, Z_R, 0.0, 48), x, y))
    bfl = prism(disc.union(shapely.unary_union(arms)), Z_R, v6.COL_FL_Z1)
    body = U([collar, tube, bfl] + webs + tops + pils)
    ctp = dt.BUSH_BORE_CH_TOP
    cuts = [cyl(dt.BUSH_BORE_D, v6.BUSH_BOT - 0.01, v6.BUSH_TOP + 1.0),
            hull_of((circle_pts(dt.BUSH_BORE_D), v6.BUSH_TOP - ctp), (circle_pts(dt.BUSH_BORE_D + 2 * (ctp + 0.5)), v6.BUSH_TOP + 0.5)),
            hull_of((circle_pts(dt.BUSH_BORE_D), v6.BUSH_BOT), (circle_pts(v6.COL_BORE_D), v6.BUSH_BOT - (v6.COL_BORE_D - dt.BUSH_BORE_D) / 2)),
            cyl(v6.COL_BORE_D, Z_R - 1.0, v6.BUSH_BOT - (v6.COL_BORE_D - dt.BUSH_BORE_D) / 2 + 0.01),
            D(cyl(v6.FACE_OR['groove_od'], Z_R - 1.0, Z_R + v6.FACE_OR['depth']),
              cyl(v6.FACE_OR['groove_od'] - 2 * v6.FACE_OR['groove_w'], Z_R - 2.0, Z_R + 3.0))]
    for x, y in P_SCREWS:
        cuts.append(at(cyl(3.4, Z_R - 1.0, 1.0, 32), x, y))
    return D(body, cuts)


# =====================================================================================
# 1. BOWL (chiocciola_v62): v6.1 bowl, tower inserts moved from r 19 (0/125/240) to P1..P3
# =====================================================================================
def build_bowl62(F):
    keep = b61.TWR_INS
    b61.TWR_INS = []
    try:
        m = b61.build_bowl61(F)                  # v6.1 bowl without the 3 tower inserts (chute + shell inserts unchanged)
    finally:
        b61.TWR_INS = keep
    cuts = [at(U([cyl(v6.INS_D, -1.0, INS_DEPTH62, 48), cyl(v6.INS_D + 1.6, -1.0, 0.4, 48)]), x, y) for x, y in P_SCREWS]
    return D(m, cuts)


# =====================================================================================
# 1. BOX (scatola_v62): v6.1.1 box without the blind plateau inserts; ear at P1; sealed through holes at P2/P3;
#    vent moved to (12, -30)
# =====================================================================================
def build_box62():
    keep = (b611.BOT_INS61, b611.VENT, b611.VER)
    b611.BOT_INS61, b611.VENT, b611.VER = [], VENT62, VER
    try:
        m = b611.build_box611()
    finally:
        b611.BOT_INS61, b611.VENT, b611.VER = keep
    x1, y1 = P_SCREWS[0]
    ear2d = shapely.unary_union([Point(x1, y1).buffer(EAR_R, resolution=32),
                                 sbox(BXO[0] - 0.5, y1 - EAR_ROOT, BXO[0] + 1.0, y1 + EAR_ROOT)]).convex_hull
    ear = prism(ear2d, EAR_Z0, Z_R)
    m = U([m, ear])
    cuts = [at(cyl(3.4, EAR_Z0 - 1.0, Z_R + 1.0, 32), x1, y1)]
    zr0 = Z_R - ROOF_T
    for (x, y), sealed in zip(P_SCREWS[1:], P_SEALED[1:]):
        cuts.append(at(cyl(3.4, zr0 - 1.0, Z_R + 1.0, 32), x, y))
        cuts.append(at(cyl(6.6, v6.BOSS_Z0 - 1.0, zr0 + 0.01, 48), x, y))      # head pocket where the old plateau boss (r 21) reaches
        c = OR_3x1['csk_d']
        cuts.append(at(hull_of((circle_pts(c, 48), zr0 - 0.01), (circle_pts(3.4, 48), zr0 + (c - 3.4) / 2)), x, y))
    return D(m, cuts)


# =====================================================================================
# 7. CAP (fondello_v62): v6.1.1 cap with Ø24 thumb-turn dishes (web to the outlet chamfer 1.72 -> 2.72)
# =====================================================================================
def build_cap62():
    keep = b611.TT_DISH_D
    b611.TT_DISH_D = TT_DISH_D62
    try:
        return b611.build_cap611()
    finally:
        b611.TT_DISH_D = keep


# =====================================================================================
# 3. CABLE PATH (centreline) at 270 deg: channel (horizontal) -> R 15 bend in the flange -> vertical in the pod top
# =====================================================================================
def tunnel_rz(n_arc=24):
    """(r, z) points of the cable centreline through the flange, from the channel inward/down"""
    zh = FL_Z1_62 - (CH['base_t'] + CABLE_D / 2 + 0.25)          # 74.15
    zc = zh - TUN['R']
    pts = [(96.0, zh), (TUN['r_s'], zh)]
    for k in range(1, n_arc + 1):
        ph = math.radians(90.0 * k / n_arc)
        pts.append((TUN['r_s'] - TUN['R'] * math.sin(ph), zc + TUN['R'] * math.cos(ph)))
    pts.append((TUN['r_v'], 52.0))
    return pts, zh, zc


def rz_to_xyz(pts, ang=CABLE_ANG):
    a = math.radians(ang)
    return [(r * math.cos(a), r * math.sin(a), z) for r, z in pts]


def tunnel_solid(radius, z_lo=None, z_hi=None, r_out_max=None):
    pts, _, _ = tunnel_rz()
    sel = [(r, z) for r, z in pts if (r_out_max is None or r <= r_out_max + 1e-9)]
    if r_out_max is not None and sel[0][0] < r_out_max:
        sel = [(r_out_max, pts[0][1])] + sel
    m = tube_path(rz_to_xyz(sel), radius, 24)
    if z_lo is not None or z_hi is not None:
        m = I(m, box(-200, 200, -200, 200, -100 if z_lo is None else z_lo, 200 if z_hi is None else z_hi))
    return m


# =====================================================================================
# 2. FLANGE: lower plate (flangia_piano_v62) + upper plate (flangia_alta_v62)
# =====================================================================================
def blade_sector(a0, a1, r=BLADE_R, n=180):
    a = np.radians(np.linspace(a0, a1, n))
    return Polygon(np.r_[[[0.0, 0.0]], np.c_[r * np.cos(a), r * np.sin(a)]])


def arm_poly(ang, w=ARM_W, r0=ARM_R[0], r1=ARM_R[1], grow=0.0):
    p = sbox(r0 - grow, -w / 2 - grow, r1 + grow, w / 2 + grow)
    return affinity.rotate(p, ang, origin=(0, 0))


def arm_sweep(grow=0.4, step=1.0):
    return shapely.unary_union([arm_poly(ARM_ANG - g, grow=grow) for g in np.arange(0.0, STROKE + 1e-6, step)]).buffer(0.01)


def sector_ring(a0, a1, r0, r1, n=180):
    a = np.radians(np.linspace(a0, a1, n))
    return Polygon(np.r_[np.c_[r1 * np.cos(a), r1 * np.sin(a)], np.c_[r0 * np.cos(a[::-1]), r0 * np.sin(a[::-1])]])


def build_flange_low62():
    plate = revolve([(0, FL_Z0), (FL_R62 - 0.6, FL_Z0), (FL_R62, FL_Z0 + 0.6), (FL_R62, FL_Z1), (0, FL_Z1)], 2 * SEG)
    if plate.volume < 0:
        plate.invert()
    skirt = D(cyl(2 * v6.SKIRT_R1, v5.HOOK_Z0, FL_Z0 + 0.01), cyl(2 * v6.SKIRT_R0, v5.HOOK_Z0 - 1, FL_Z0 + 1))
    tongues = [bd.sector_solid(a0, a1, v5.HOOK_R0, v6.SKIRT_R1 - 0.5, v5.HOOK_Z0, v5.HOOK_Z1, 24) for a0, a1 in HOOKS61]
    pins = []
    for a in PIN_ANG61:
        x, y = polar(v6.PIN_R, a)
        z0 = b61.W1 + v6.PIN_GAP
        pins.append(at(U([cyl(v6.PIN_D, z0, FL_Z0 + 0.01, 48), hull_of((circle_pts(v6.PIN_D, 48), FL_Z0 - 1.0), (circle_pts(v6.PIN_D + 2.0, 48), FL_Z0 + 0.01))]), x, y))
    pivot = cyl(PIVOT_D, FL_Z1 - 0.01, BLADE_Z[1] + 0.1, 48)
    body = U([plate, skirt, pivot] + tongues + pins)
    a_lo, a_hi = ARM_ANG - STROKE - 3.0, ARM_ANG + 3.0
    cuts = [prism(v5.OPENING, FL_Z0 - 1.0, FL_Z1 + 0.02),
            D(cyl(2 * v5.LGROOVE_R1, FL_Z0 - 1, FL_Z0 + v5.LGROOVE_D), cyl(2 * v5.LGROOVE_R0, FL_Z0 - 2, FL_Z0 + v5.LGROOVE_D + 1)),
            D(cyl(2 * SH_GRV[1], FL_Z0 - 1, FL_Z0 + SH_GRV[2], 2 * SEG), cyl(2 * SH_GRV[0], FL_Z0 - 2, FL_Z0 + SH_GRV[2] + 1, 2 * SEG)),
            D(cyl(2 * RING_GRV['r1'], FL_Z0 - 1, RING_GRV['z1'], 2 * SEG), cyl(2 * RING_GRV['r0'], FL_Z0 - 2, RING_GRV['z1'] + 1, 2 * SEG)),
            D(cyl(2 * RING_GRV['uc'][0], RING_GRV['uc'][1], RING_GRV['z1'], 2 * SEG), cyl(2 * RING_GRV['r1'] - 0.02, RING_GRV['uc'][1] - 1, RING_GRV['z1'] + 1, 2 * SEG)),
            prism(sector_ring(a_lo, a_hi, RING_SLOT['r0'], RING_SLOT['r1']), RING_SLOT['z0'], FL_Z1 + 0.02),
            # landing drain: crumbs pushed past the far pie edge by the blade fall through (no crumb cake in the overtravel landing)
            prism(affinity.rotate(sbox(6.0, -0.8, 50.0, 0.8), DRAIN_ANG, origin=(0, 0)), FL_Z0 - 1.0, FL_Z1 + 0.02),
            tunnel_solid(TUN['bore'] / 2, z_hi=FL_Z1 + 0.01, r_out_max=FL_R62 + 2)]
    for a in WOOD_ANG62:
        x, y = polar(WOOD_R62, a)
        cuts.append(at(U([cyl(v5.WOOD_D, FL_Z0 - 1, FL_Z1 + 1, 32), cyl(v5.WOOD_CB_D, FL_Z0 - 1, FL_Z0 + v5.WOOD_CB_H, 48)]), x, y))
    for a in JOIN['ang']:
        x, y = polar(JOIN['r'], a)
        cuts.append(at(cyl(JOIN['pilot'], FL_Z0 + 0.5, FL_Z1 + 1, 24), x, y))
    ex, ey = polar(72.0, 180.0)
    cuts.append(face_region(affinity.scale(text_poly(VER, 5.0, ex, ey, 90.0), -1, 1, origin=(ex, ey)), FL_Z0, False))
    return D(body, cuts)


def funnel62():
    """flange funnel: pie prism from the bowl rim up through the gate plane, then the v6 morph raised by DZ_FL"""
    cav6 = v6.fl_funnel_cavity()
    cav6.apply_translation([0, 0, DZ_FL])
    return U([cav6, prism(v5.OPENING, FL_Z0 - 1.0, FL_Z0 + DZ_FL + 0.05)])


def pocket2d():
    return shapely.unary_union([blade_sector(LEAD_OPEN - STROKE - 0.3, LEAD_OPEN + BLADE_W + 0.3, POCKET_R), arm_sweep(),
                                Point(0, 0).buffer(PIVOT_D / 2 + 0.3, resolution=32)])


def build_flange_up62(cav):
    plate = revolve([(0, FL_Z1), (FL_R62, FL_Z1), (FL_R62, FL_Z1_62 - 0.6), (FL_R62 - 0.6, FL_Z1_62), (0, FL_Z1_62)], 2 * SEG)
    if plate.volume < 0:
        plate.invert()
    hc = v6.HOLE_C
    cuts = [cav, prism(pocket2d(), FL_Z1 - 1.0, POCKET_Z1),
            at(D(cyl(2 * v5.FL_GSK_R + v5.GRV_W, FL_Z1_62 - v5.GRV_D, FL_Z1_62 + 1), cyl(2 * v5.FL_GSK_R - v5.GRV_W, FL_Z1_62 - v5.GRV_D - 1, FL_Z1_62 + 2)), *hc),
            tunnel_solid(TUN['bore'] / 2, z_lo=FL_Z1 - 0.01, r_out_max=FL_R62 + 2)]
    # channel port: the base + cover of the first channel section slide 5 mm into the rim
    a = math.radians(CABLE_ANG)
    port = box(-CH['w'] / 2 - 0.2, CH['w'] / 2 + 0.2, -(FL_R62 + 1.0), -(FL_R62 - CH['insert']), FL_Z1 + 0.0, FL_Z1_62 + 1.0)
    cuts.append(rotz(port, CABLE_ANG + 90.0))
    for x, y in v6.COLLAR_PINS:
        cuts.append(at(cyl(3.4, FL_Z1_62 - 3.0, FL_Z1_62 + 1.0, 32), x, y))
    for aw in WOOD_ANG62:
        x, y = polar(WOOD_R62, aw)
        cuts.append(at(cyl(v5.WOOD_D, FL_Z1 - 1, FL_Z1_62 + 1, 32), x, y))
    for aj in JOIN['ang']:
        x, y = polar(JOIN['r'], aj)
        cuts.append(at(U([cyl(JOIN['clr'], FL_Z1 - 1, FL_Z1_62 + 1, 24),
                          hull_of((circle_pts(JOIN['clr'], 32), FL_Z1_62 - (JOIN['csk'] - JOIN['clr']) / 2), (circle_pts(JOIN['csk'], 32), FL_Z1_62 + 0.01))]), x, y))
    return D(plate, cuts)


# =====================================================================================
# 2. BLADE (saracinesca_v62, green blade + orange arm) and RING (anello_saracinesca_v62, orange)
# =====================================================================================
def build_blade62():
    z0, z1 = BLADE_Z
    sec = blade_sector(LEAD_OPEN, LEAD_OPEN + BLADE_W).difference(Point(0, 0).buffer(PIVOT_HOLE / 2, resolution=32))
    blade = prism(sec, z0, z1)
    # knife: single top bevel along the leading edge (radial line at LEAD_OPEN): edge 0.6 thick, 5.5 mm run
    a = math.radians(LEAD_OPEN)
    d = np.array([math.cos(a), math.sin(a)]); n = np.array([-math.sin(a), math.cos(a)])      # n points into the blade
    pts = []
    for s in (-2.0, BLADE_R + 2.0):
        for (w, z) in ((-1.0, z0 + KNIFE['edge_t']), (-1.0, z1 + 1.0), (KNIFE['run'], z1 + 1.0), (KNIFE['run'], z1 + 0.001)):
            p = s * d + w * n
            pts.append([p[0], p[1], z])
    wedge = trimesh.convex.convex_hull(np.array(pts))
    blade = D(blade, [wedge])
    arm = prism(arm_poly(ARM_ANG).difference(Point(*polar(PEG['r'], ARM_ANG)).buffer(PEG['hole'] / 2, resolution=32)), z0, z1)
    green = blade
    orange = D(arm, [prism(Point(0, 0).buffer(BLADE_R - 0.01, resolution=256), z0 - 1, z1 + 1)])
    return U([green, orange]), green, orange


def build_ring62():
    r = RING
    zb0, zb1 = RING_BARB['z']
    prof = [(r['ri'], r['z0'] + 1.2), (r['ri'] + 1.2, r['z0']), (r['ro'] - 1.2, r['z0']), (r['ro'], r['z0'] + 1.2),
            (r['ro'], r['z1'] - 0.4), (r['ro'] - 0.4, r['z1']), (r['tongue'][1], r['z1']),
            (r['tongue'][1], zb0 - 0.3), (RING_BARB['r1'], zb0), (RING_BARB['r1'], zb1 - 0.05), (r['tongue'][1], r['tongue_top'] - 0.1),
            (r['tongue'][1] - 0.2, r['tongue_top']), (r['tongue'][0] + 0.3, r['tongue_top']),
            (r['tongue'][0], r['tongue_top'] - 0.3)]
    m = revolve(prof, 2 * SEG)
    if m.volume < 0:
        m.invert()
    px, py = polar(PEG['r'], ARM_ANG)
    peg = at(U([cyl(PEG['d'], r['tongue_top'] - 0.3, BLADE_Z[1] - 0.3, 32),
                hull_of((circle_pts(PEG['d'] - 0.8, 32), BLADE_Z[1] - 0.3), (circle_pts(PEG['d'], 32), BLADE_Z[1] - 0.7))]), px, py)
    m = U([m, peg])
    # window: lines up with the button only at the end of the closing stroke
    w = trimesh.creation.cylinder(radius=r['win_d'] / 2, height=12.0, sections=64)
    w.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    w.apply_translation([(r['ri'] + r['ro']) / 2, 0, r['win_z']])
    ch_ = hull_of((circle_pts(r['win_d'], 64), 0.0), (circle_pts(r['win_d'] + 2.4, 64), 1.21))
    ch_.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    ch_.apply_translation([r['ro'] - 1.2, 0, r['win_z']])
    m = D(m, [rotz(w, WIN_ANG), rotz(ch_, WIN_ANG)])
    return m


def gate_pose(m, g):
    """gate parts are built OPEN (g = 0); closing turns them by -g about the shaft axis (CW from above)"""
    return rotz(m, -g)


# =====================================================================================
# 3. GROMMET (passacavo_v62, TPU) + CHANNEL (canalina_*_v62)
# =====================================================================================
def build_grommet62():
    pts, zh, zc = tunnel_rz(48)
    seg = [(r, z) for r, z in pts if 63.0 <= z <= 69.0 and r < 82]
    outer = tube_path(rz_to_xyz(seg), TUN['bore'] / 2 + 0.15, 24)
    xe, ye = polar(np.interp(FL_Z0, [z for _, z in seg[::-1]], [r for r, _ in seg[::-1]]), CABLE_ANG)
    lip = prism(Point(xe, ye).buffer(5.4, resolution=32), FL_Z0 - 1.0, FL_Z0 + 0.15)
    g = U([I(outer, box(-200, 200, -200, 200, FL_Z0 - 1.0, FL_Z0 + 2.6)), lip])
    return D(g, [tube_path(rz_to_xyz(pts), CABLE_D / 2 - 0.2, 24)])


def channel_profiles():
    """cross-sections in (u across, v down from the shelf face)"""
    c = CH
    base = shapely.unary_union([sbox(-c['rail'][1], 0.0, c['rail'][1], c['base_t']),
                                sbox(-c['rail'][1], c['base_t'] - 0.01, -c['rail'][0], 3.2),
                                sbox(c['rail'][0], c['base_t'] - 0.01, c['rail'][1], 3.2),
                                Polygon([(-c['rail'][1], 2.4), (-c['barb'][1], 2.4), (-c['barb'][1], 2.7), (-c['rail'][1], 3.2)]),
                                Polygon([(c['rail'][1], 2.4), (c['barb'][1], 2.4), (c['barb'][1], 2.7), (c['rail'][1], 3.2)])])
    ow, wl = c['w'] / 2, c['wall']
    outer = Polygon([(-ow, 0.2), (ow, 0.2), (ow, c['h'] - 2.5), (ow - 2.5, c['h']), (-ow + 2.5, c['h']), (-ow, c['h'] - 2.5)])
    inner = Polygon([(-ow + wl, -1.0), (ow - wl, -1.0), (ow - wl, c['h'] - wl - 1.2), (ow - wl - 1.2, c['h'] - wl),
                     (-ow + wl + 1.2, c['h'] - wl), (-ow + wl, c['h'] - wl - 1.2)])
    lips = shapely.unary_union([Polygon([(-ow + wl - 0.01, 1.4), (-c['barb'][0] + 0.15, 1.4), (-c['barb'][0] + 0.15, 1.9), (-ow + wl - 0.01, 2.35)]),
                                Polygon([(ow - wl + 0.01, 1.4), (c['barb'][0] - 0.15, 1.4), (c['barb'][0] - 0.15, 1.9), (ow - wl + 0.01, 2.35)])])
    cover = outer.difference(inner).union(lips)
    return base, cover


def _extrude_uv(poly, t0, t1):
    """prism of a (u, v) profile along +t; local frame: x = u, y = t, z = -v"""
    m = trimesh.creation.extrude_polygon(poly, height=t1 - t0)              # (u, v, t)
    T = np.array([[1, 0, 0, 0], [0, 0, 1, t0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
    m.apply_transform(T)
    if m.volume < 0:
        m.invert()
    return m


def build_channel62(L=CH['seg']):
    base_p, cover_p = channel_profiles()
    base = _extrude_uv(base_p, 0.0, L)
    holes = []
    for t in (25.0, L - 25.0):
        holes.append(U([cyl(3.8, -CH['base_t'] - 1, 1.0, 32), hull_of((circle_pts(3.8, 32), -0.55), (circle_pts(7.2, 32), -CH['base_t'] - 0.01))]))
        holes[-1].apply_translation([0, t, 0])
    base = D(base, holes)
    cover = _extrude_uv(cover_p, 0.0, L)
    return base, cover


def build_channel_cap62():
    """end cap at the shelf edge: tongue into the cover, closed end, cable exit downward through a rounded hole"""
    base_p, cover_p = channel_profiles()
    ow = CH['w'] / 2
    outer = Polygon([(-ow, 0.2), (ow, 0.2), (ow, CH['h'] - 2.5), (ow - 2.5, CH['h']), (-ow + 2.5, CH['h']), (-ow, CH['h'] - 2.5)])
    body = _extrude_uv(outer, 0.0, 10.0)
    tongue = _extrude_uv(sbox(-ow + CH['wall'] + 0.2, CH['base_t'] + 0.3, ow - CH['wall'] - 0.2, CH['h'] - CH['wall'] - 0.2), -6.0, 0.01)
    tongue = D(tongue, [_extrude_uv(sbox(-CH['rail'][1] - 0.2, 0.0, CH['rail'][1] + 0.2, 3.4), -7.0, 1.0)])
    m = U([body, tongue])
    hole = cyl(6.2, -CH['h'] - 1, -CH['base_t'] - 2.3, 48)
    hole.apply_translation([0, 4.0, 0])
    rnd = hull_of((circle_pts(6.2, 48), -CH['h'] + 1.0), (circle_pts(8.6, 48), -CH['h'] - 0.01))
    rnd.apply_translation([0, 4.0, 0])
    groove = _extrude_uv(sbox(-3.2, CH['base_t'] + 0.2, 3.2, 6.6), -7.0, 4.0)
    return D(m, [hole, rnd, groove])


def place_channel(m, t_start, ang=CABLE_ANG):
    """local channel frame (x = u across, y = t along, z = -v down) -> world: t runs radially outward at `ang` from
    radius t_start, the channel's top face on the shelf underside"""
    q = m.copy()
    q.apply_translation([0, t_start, FL_Z1_62])
    return rotz(q, ang - 90.0)


# =====================================================================================
# 4. COMB LIP (labbro_pettine_v62, one design x4) + plates with lengthened grooves
# =====================================================================================
def build_lip62():
    """canonical lip in the GATE frame: s along the strip (centred), w from the opening edge into the plate, z from the
    groove bottom; anchor 3.15 x 1.0, flap 0.8 leaning 40 deg towards the opening, tip 0.15 into the disc face;
    5 slits 0.7 symmetric about the middle (reversible end for end)"""
    h = (DISC_Z0 + LIP_PRE) - (G1 - LIPD + ANCH_H)                       # 1.85 (identical on the window side)
    wc = LIPS + LIPW / 2
    lean = h * math.tan(math.radians(FLAP_LEAN))
    tw = FLAP_T / math.cos(math.radians(FLAP_LEAN))
    s0, s1 = -LIP_L / 2, LIP_L / 2
    P = lambda s, w, z: [s, w, z]
    anchor = trimesh.convex.convex_hull(np.array([P(s, w, z) for s in (s0, s1) for w in (wc - ANCH_W / 2, wc + ANCH_W / 2) for z in (0.02, ANCH_H)]))
    flap = trimesh.convex.convex_hull(np.array([P(s, wc + tw / 2, ANCH_H - 0.05) for s in (s0, s1)] + [P(s, wc - tw / 2, ANCH_H - 0.05) for s in (s0, s1)] +
                                               [P(s, wc - lean + tw / 2, ANCH_H + h) for s in (s0, s1)] + [P(s, wc - lean - tw / 2, ANCH_H + h) for s in (s0, s1)]))
    lip = U([anchor, flap])
    cuts = [box(s - SLIT_W / 2, s + SLIT_W / 2, -20, 20, ANCH_H + SLIT_STOP, ANCH_H + h + 1.0) for s in LIP_SLITS]
    return D(lip, cuts), round(h, 3)


def lip_frames():
    """placement of the canonical lip in the 4 grooves: proper rotations only (the same part everywhere)"""
    out = []
    for kind, face, poly in (('out', G1, OUT_T), ('win', W0, WIN_B)):
        for k, (q, d, sgn) in enumerate(lip_lines(kind)):
            s0, s1 = edge_s_range(poly, q, d)
            lo, hi = s0 - 0.7, s1 + 0.2                                     # v6.1 lip span
            if hi - lo < LIP_L - 0.01:                                      # short (skewed) edge: keep the outer end, grow inward
                sc = hi - LIP_L / 2
            else:
                sc = (lo + hi) / 2
            dd = np.array([d[0], d[1], 0.0]) / np.linalg.norm(d)
            nn = sgn * np.array([-dd[1], dd[0], 0.0])                     # into the plate
            if kind == 'out':
                S, Z, z0 = sgn * dd, np.array([0, 0, 1.0]), G1 - LIPD
            else:
                S, Z, z0 = -sgn * dd, np.array([0, 0, -1.0]), W0 + LIPD
            T = np.eye(4)
            T[:3, 0], T[:3, 1], T[:3, 2] = S, nn, Z
            T[:3, 3] = np.array([q[0], q[1], 0.0]) + sc * dd + np.array([0, 0, z0])
            if kind == 'out':                                              # outlet plate is built at +X and turned 180
                T = trimesh.transformations.rotation_matrix(math.pi, [0, 0, 1]) @ T
            out.append((f'{kind}_{k + 1}', T, sc, (lo, hi), round(s1 - s0, 2), q, d, sgn))
    return out


def _groove_cuts(kind, z0, z1):
    cuts = []
    for name, T, sc, (lo, hi), elen, q, d, sgn in lip_frames():
        if not name.startswith(kind):
            continue
        w0, w1 = (LIPS, LIPS + LIPW) if sgn > 0 else (-(LIPS + LIPW), -LIPS)
        c = line_strip(q, d, sc - LIP_L / 2 - 0.3, sc + LIP_L / 2 + 0.3, w0, w1, z0, z1)
        cuts.append(rotz(c, 180) if kind == 'out' else c)
    return cuts


def build_gate62():
    g = cyl(2 * bd.GATE_R, G0, G1, n=2 * SEG)
    outlet = rotz(bd.loft_wedges(OUT_T, G1 + 0.5, OUT_B.buffer(bd.PL_DRAFT / PLATE_T * 0.5), G0 - 0.5), 180)
    cuts = [outlet, cyl(bd.GATE_HOLE_D, G0 - 1, G1 + 1, 96)] + _groove_cuts('out', G1 - LIPD, G1 + 1)
    cuts += bd.notch_cuts(bd.BOWL_R_IN - bd.KEY_PROT_GATE - bd.KEY_CLR, G0 - 1, G1 + 1)
    return D(g, cuts)


def build_window62():
    w = cyl(2 * bd.WIN_R, W0, W1, n=2 * SEG)
    win = bd.loft_wedges(WIN_T, W1 + 0.5, WIN_B.buffer(bd.PL_DRAFT / PLATE_T * 0.5), W0 - 0.5)
    cuts = [win, cyl(bd.WIN_HOLE_D, W0 - 1, W1 + 1, 96)] + _groove_cuts('win', W0 - 1, W0 + LIPD)
    cuts += bd.notch_cuts(bd.BOWL_R_STEP - bd.KEY_PROT_WIN - bd.KEY_CLR, W0 - 1, W0 + 1 + PLATE_T)
    return D(w, cuts)


def plate_colours(gate, window):
    split = bd.split
    win_band = WIN_T.buffer(bd.RIM_BAND, resolution=32).difference(WIN_T)
    wb, wg = split(window, face_region(win_band.union(text_poly('FOOD IN →', 6, -30, 0)).union(text_poly(VER, 4, -30, -9)), W1, True))
    out_band = rotz_poly(OUT_T.buffer(bd.RIM_BAND, resolution=32).difference(OUT_T), 180).intersection(Point(0, 0).buffer(bd.GATE_R - 0.8))
    gb, gg = split(gate, face_region(out_band.union(text_poly('← OUT', 6, 30, 0)).union(text_poly(VER, 4, 30, -9)), G1, True))
    return [('black', gb), ('green', gg)], [('black', wb), ('green', wg)]


# =====================================================================================
# BOUGHT PARTS v6.2
# =====================================================================================
def screw_m3_up(x, y, z_seat, length):
    """DIN912 placeholder with the head UNDER z_seat (screw driven upward)"""
    return v6.screw_m3(x, y, z_seat, length)


def head_seat_z():
    return [EAR_Z0, Z_R - ROOF_T, Z_R - ROOF_T]


def cable_paths():
    pts, zh, zc = tunnel_rz(36)
    # supply side: shelf edge end cap -> channel -> flange tunnel -> pod top -> connector top
    y_exit = -(FL_R62 - CH['insert'] + CH['seg'] + L2_CH + 4.0)       # end-cap cable hole (local t = 4)
    sup = [(0.0, y_exit, FL_Z1_62 - 45.0), (0.0, y_exit, zh - 3.0), (0.0, y_exit + 3.0, zh), (0.0, -96.5, zh)] + rz_to_xyz(pts)[1:] + \
          [(0.0, -72.0, 50.6), (0.0, -69.2, 49.0)]
    a, b_ = CONN62
    unit = [(0.0, -69.2, a[2]), (0.0, -69.2, -2.0), (-1.0, -67.0, -18.0), (-3.0, -65.0, -34.0), (-3.0, -63.0, -45.0), (-3.0, -58.0, -48.0)]
    return sup, unit


def bought62():
    B, sc = b611.bought611()
    for k in ('cable_12v', 'connector_ip67'):
        B.pop(k, None)
    sup, unit = cable_paths()
    B['cable_12v_supply'] = tube_path(sup, CABLE_D / 2, 16)
    B['cable_12v_unit'] = tube_path(unit, CABLE_D / 2, 16)
    a, b_ = CONN62
    B['connector_m8_ip67'] = U([at(cyl(12.0, a[2], b_[2], 32), a[0], a[1]), at(cyl(13.0, (a[2] + b_[2]) / 2 - 4, (a[2] + b_[2]) / 2 + 4, 6), a[0], a[1])])
    # vent moved
    vx, vy = VENT62['x'], VENT62['y']
    B['vent_m12_eptfe'] = U([at(cyl(15.0, Z_R - 0.01, Z_R + 6.0, 6), vx, vy), at(cyl(14.0, Z_R + 5.99, Z_R + 11.0, 32), vx, vy),
                             at(cyl(11.8, Z_R - ROOF_T - 4.0, Z_R + 0.01, 32), vx, vy), at(cyl(17.0, Z_R - ROOF_T - 4.0, Z_R - ROOF_T - 0.01, 6), vx, vy)])
    B['oring_3x1'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, Z_R - ROOF_T + 0.45, x=x, y=y, n=48) for x, y in P_SCREWS[1:]])   # free section drawn in the countersink: overlap = squeeze
    for k in ('m3x12_tower_top', 'm3x10_tower_box', 'wood_5x25', 'inserts_bowl', 'inserts_box'):
        sc.pop(k, None)
    zs = head_seat_z()
    sc['m3x40_stack'] = U([screw_m3_up(x, y, z, SCREW_LEN) for (x, y), z in zip(P_SCREWS, zs)])
    sc['wood_5x35'] = U([at(U([cyl(5.0, FL_Z0 - 0.01 + v5.WOOD_CB_H, FL_Z1_62 + 20.0, 24), cyl(9.5, FL_Z0 - 0.5, FL_Z0 + v5.WOOD_CB_H, 32)]), *polar(WOOD_R62, a))
                         for a in WOOD_ANG62])
    sc['st29_join'] = U([at(U([cyl(2.9, FL_Z1 - 3.4, FL_Z1_62 - 1.0, 16), hull_of((circle_pts(2.9, 24), FL_Z1_62 - 1.55), (circle_pts(5.6, 24), FL_Z1_62 - 0.05))]),
                            *polar(JOIN['r'], a)) for a in JOIN['ang']])
    ins_bowl = list(P_SCREWS) + list(b61.CH_EARS) + list(b61.TAB_INS)
    sc['inserts_bowl'] = U([at(cyl(4.0, 0.2, 5.9, 24), x, y) for x, y in ins_bowl])
    sc['inserts_box'] = U([at(cyl(4.0, CAGE_Z0 + 0.2, CAGE_Z0 + 5.9, 24), x, y) for x, y in b61.SERVO_HOLES_W])
    return B, sc


# =====================================================================================
# BUILD / EXPORT
# =====================================================================================
def build_all():
    P, COLOUR, EXTRA = {}, {}, {}
    P611, COL611, EX611 = b611.build_all()                       # v6.1.1 parts in memory (sets the chute ears, collar pins)
    EXTRA['P611'], EXTRA['EX611'] = P611, EX611
    F = EX611['F']
    P['chiocciola_v62'] = build_bowl62(F)
    P['colonna_v62'] = build_column62()
    P['scatola_v62'] = build_box62()
    P['fondello_v62'] = build_cap62()
    cav = funnel62()
    EXTRA['FUNNEL'] = cav
    P['flangia_piano_v62'] = build_flange_low62()
    P['flangia_alta_v62'] = build_flange_up62(cav)
    P['saracinesca_v62'], bl_g, bl_o = build_blade62()
    P['anello_saracinesca_v62'] = build_ring62()
    P['passacavo_v62'] = build_grommet62()
    P['labbro_pettine_v62'], EXTRA['lip_h'] = build_lip62()
    P['piastra_gate_v62'] = build_gate62()
    P['piastra_finestra_v62'] = build_window62()
    base, cover = build_channel62()
    P['canalina_base_v62'], P['canalina_coperchio_v62'] = base, cover
    P['canalina_tappo_v62'] = build_channel_cap62()
    col = {'saracinesca_v62': None, 'anello_saracinesca_v62': 'orange', 'passacavo_v62': 'yellow', 'labbro_pettine_v62': 'yellow'}
    for k, m in P.items():
        COLOUR[k] = [(col.get(k) or 'black', m)]
    COLOUR['saracinesca_v62'] = [('green', bl_g), ('orange', bl_o)]
    COLOUR['piastra_gate_v62'], COLOUR['piastra_finestra_v62'] = plate_colours(P['piastra_gate_v62'], P['piastra_finestra_v62'])
    return P, COLOUR, EXTRA


FLIP = {'chiocciola_v62': False, 'colonna_v62': False, 'scatola_v62': True, 'fondello_v62': False, 'flangia_piano_v62': True,
        'flangia_alta_v62': True, 'saracinesca_v62': False, 'anello_saracinesca_v62': False, 'passacavo_v62': True,
        'labbro_pettine_v62': False, 'piastra_gate_v62': False, 'piastra_finestra_v62': True,
        'canalina_base_v62': False, 'canalina_coperchio_v62': True, 'canalina_tappo_v62': False}
RHO = {k: (TPU if k.startswith('labbro') or k.startswith('passacavo') else PETG) for k in FLIP}


def print_matrix(m, name):
    T = np.eye(4)
    if name == 'flangia_alta_v62' or FLIP.get(name):
        T = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    if name == 'canalina_tappo_v62':
        T = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    p = m.copy(); p.apply_transform(T)
    return trimesh.transformations.translation_matrix([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]]) @ T


def export_part(name, m, bodies):
    m = v6.clean(m)
    m.export(OUT + f'{name}.stl'); m.export(OUT + f'{name}.3mf')
    wt = bool(trimesh.load(OUT + f'{name}.stl').is_watertight)
    T = print_matrix(m, name)
    pm = m.copy(); pm.apply_transform(T)
    scn = trimesh.Scene()
    for c, b in bodies:
        pb = v6.clean(b).copy(); pb.apply_transform(T)
        if len(bodies) > 1:
            pb.export(OUT + f'{name}_print_{c}.stl')
        scn.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
    scn.export(OUT + f'{name}_print.3mf')
    pm.export(OUT + f'{name}_print.stl')
    return wt, pm


if __name__ == '__main__':
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    P, COLOUR, EXTRA = build_all()
    print('\n--- v6.2 parts ---')
    for k, m in P.items():
        report(k, m)
        for c, b in COLOUR[k]:
            assert b.is_watertight, (k, c)
    if STAGE == 'build':
        sys.exit(0)
    EXPORT_WT, PR, OVH, GR = {}, {}, {}, {}
    for k, m in P.items():
        EXPORT_WT[k], PR[k] = export_part(k, m, COLOUR[k])
        OVH[k] = round(overhang(PR[k]), 1)
        GR[k] = v6.grams_est(m, RHO[k])
    print('exported; watertight on reload:', EXPORT_WT)
    if STAGE == 'parts':
        sys.exit(0)
    exec(open(dt.HERE + 'build_v62_checks.py').read())
    import publish_v62                    # copy the deliverables from build/ into the repository folders
    publish_v62.main()
