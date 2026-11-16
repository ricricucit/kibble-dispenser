#!/usr/bin/env python3
"""
Kibble Dispenser Outdoor - design patch v6.1.1 ("closed pod").

v6.1 treated the pod (shell + cap) as a drained rain shield. v6.1.1 closes it as a SECOND barrier around the dry box:
  - thumb-turns: the v6.1 dish (3.5 deep) broke through the 2.0 cap floor (open ring r 10..13 round every turn, the one at C
    straight into the dry box) and the keyway ran the full boss height; the arms also sat UNDER the box posts, so nothing held
    the cap up. New: solid dish walls, round bore + O-ring 8x1.5 on every shaft, steel key 3x3x18 pressed through the shaft above
    the boss (captive), key rests on two bridged ledges in a cup hanging from the box (0.3 mm notch = click + positive lock)
  - shell | cap seam: O-ring 132x2 in a groove of a thicker vertical cap spigot (15 % squeeze), vertical seam band + lead-in chamfer in the shell
  - shadow gap under the flange: flange plate r 84.5 (2.5 mm drip overhang) + TPU skirt lip touching the shell's outer
    cylinder (radial, slides 30 deg, drops off with the unit)
  - drain slots into the outlet bore removed; one labyrinth drain (4 x 0.8 mm holes, no line of sight) at the low point of a
    1.5 deg sloped floor in the wet ring
  - chute extended 7.5 mm into a socket in the cap outlet; TPU lip ring on the chute: the pod interior is no longer reachable
    from the outlet bore (the kibble path itself stays open by design: rotary airlock)
  - latch push-button: O-ring 14x1.5 in the shell bore, longer head
  - cap lip seal: real retaining groove (2.1 wide in a 4.4 wide upstand; v6.1 groove was wider than the 2.0 upstand)
Frame and pose as v6.1 (Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED pose).
No existing file is modified: changed parts carry the suffix _v611; unchanged v6.1 parts are reused from disk.
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

import build_v61 as b61
from build_v61 import (v6, v5, dt, bd, OUT, U, D, I, cyl, box, at, hull_of, circle_pts, revolve, prism, rrect, ring2d,
                       below, above, polar, yprism, rotz, text_poly, face_region, overhang, vol, SEG, pod_solid, pod_circle,
                       section_fn, shell_r_at, radial_cyl, report, line_strip, PETG, TPU,
                       Z_TOP, R_TOP, Z_BOT, Z_S, SEAM, T_SHELL, T_CAP, BXO, BX_R, BX_T, Z_R, Z_W, BOX_OUT, BOX_IN, ROOF_T,
                       FL_OUT, CRADLE_HALF_X, CAGE_Z0, CAGE_Y, VOID_Y, SERVO_HOLES_W, BOT_INS61, BB, GLAND, VENT, CH_X, RI, RO,
                       T_CH, ZB, FL_Z0, FL_Z1, LATCH_A, BTN_Z, BTN, Z_C, WALL_C, GRV_D, OUTLET, TAB_ANG, TAB_R_INS, TAB_W, TAB_T,
                       WOOD_XY, HOOKS61, PIN_ANG61, CABLE_XY, GROM, VER as VER61)

VER = 'v6.1.1'
SFX = '_v611'
SCRATCH = OUT                                         # probe exports (build/)
ASM = OUT + 'v611_asm/'
os.makedirs(SCRATCH, exist_ok=True)
os.makedirs(ASM, exist_ok=True)
NF = 128                                              # facets on the small visible round parts (v6.1: 48..64)

# =====================================================================================
# PARAMETERS v6.1.1
# =====================================================================================
# ---- thumb-turns: A/B moved 3 mm -X (their cups must clear the wider cap upstand), C unchanged ----
TT = [(-29.0, 37.0), (-29.0, -37.0), (24.0, 0.0)]
TT_DISH_D, TT_DISH_H = 26.0, 3.5
TT_DISH_FLOOR = Z_BOT + TT_DISH_H                    # -100.5
TT_SHAFT_D, TT_BORE_D, TT_FACE_D = 10.0, 10.3, 18.0
TT_CONE_TOP = TT_DISH_FLOOR + (TT_FACE_D - TT_SHAFT_D) / 2      # -96.5 (45 deg cone behind the face disc)
BOSS_LO_D, BOSS_LO_TOP = 31.0, TT_DISH_FLOOR + 1.5   # solid wall round the dish (v6.1: boss 20 < dish 26 -> broke through)
BOSS_HI_D, BOSS_TOP = 18.0, -93.0
OR_TT = dict(z=(-96.0, -94.0), groove_d=8.0, id=8.0, cs=1.5)    # O-ring 8x1.5 on every shaft, bore 10.3 -> squeeze 23 %
CUP_Z0 = BOSS_TOP + 0.5                              # -92.5 cup bottom (0.5 over the boss at lock)
LEDGE_TOP = -89.0                                    # bridged ledges: top face
NOTCH = 0.3                                          # detent notch: the key drops 0.3 at 90 deg (click, positive lock)
Z_LOCK = LEDGE_TOP - NOTCH                           # key bottom at lock -89.3
KEY = dict(w=3.0, h=3.0, l=18.0)                     # DIN 6885 B 3x3x18 parallel key, stainless, pressed through the shaft
KEY_HOLE = 3.0
SHAFT_TOP = Z_LOCK + KEY['h'] + 2.0                  # -84.3
LEDGE_Y = 5.6                                        # ledges at |y_local| >= 5.6 (key passes between them at entry)
LEAD = 1.0                                           # 45 deg lead-in on the ledge inner top edge
CUP_RI, CUP_RO = 9.6, 11.2
RIB_W, RIB_ANG = 1.5, (105.0, 285.0, 340.0, 160.0)   # stop ribs: 2 at lock (+90 deg), 2 wrong-way (-20 deg from entry)
CUP_TOP_AB = Z_R                                     # A/B cups rise to the roof plane (print from the bed, no overhang)
CUP_TOP_C = -83.6                                    # C cup stays under the 70x50 board (bottom -83.0)
COL_C = dict(x0_lo=10.8, x0_hi=CRADLE_HALF_X - 0.01, x1=21.0, y0=-5.0, y1=7.0)   # C hanger column (servo | board corridor)
# ---- cap D upstand + retaining groove for guarnizione_fondello_v61 (base 2.2) ----
UP_OUT, UP_IN = 1.7, 2.7                             # upstand from offset +1.7 to -2.7 of the box outline (v6.1: +0.5 / -1.5)
GRV_W611 = 2.1                                       # 0.05 interference per side on the 2.2 lip base
# ---- shell | cap seam O-ring ----
SPIG_OFF = T_SHELL + 0.25                            # spigot outer face (0.25 radial clearance to the shell)
SEAM_BAND_TOP = Z_S + 6.0                            # shell inner face made a VERTICAL cylinder from the seam up to -66: v6.1's tapered
SEAM_CX, SEAM_R = pod_circle(T_SHELL, Z_S)           #   spigot was 0.5 wider than the shell mouth at +X (cap could not slide on/off)
SEAM_G = 1.45                                        # groove depth into the spigot -> squeeze (2.0 - 1.45 - 0.25)/2.0 = 15 %
SPIG_IN = SPIG_OFF + SEAM_G + 1.0                    # spigot inner face (1.0 under the groove)
SPIG_TOP = Z_S + 4.6                                 # -67.4
ZG_SEAM = (-71.3, -68.7)                             # groove (2.6 wide), O-ring centre -70.0 (enters the shell 2.0 before lock)
OR_SEAM_CS = 2.0
STD_ID_CS2 = [120.0, 125.0, 128.0, 130.0, 132.0, 135.0, 136.0, 138.0, 140.0, 145.0, 150.0]
SHELL_LEADIN = 0.8
# ---- shadow gap: flange overhang + TPU skirt lip ----
FL_R611 = 84.5
SH_GRV = (82.5, 83.5, 1.6)                           # groove r0, r1, depth in the flange underside
SH_LIP = dict(anchor=(82.45, 83.55), root=(82.95, FL_Z0), tip=(81.6, 62.4), t=0.5)   # tip 0.4 inside the shell r 82
SHELL_TOP_CH = 0.6                                   # lead-in chamfer on the shell top outer edge
# ---- chute into a cap socket + TPU lip ring ----
Z_CH_END611 = -81.3                                  # v6.1: -73 (1 mm air gap to the cap outlet tube)
CH_TIP_CH = 1.0
SOCK = dict(top=-72.7, r=24.35, pilot=(-82.3, -79.8), pocket=(-79.8, -76.8, 25.7), groove=(-76.8, -74.8, 26.45), r_out=27.45, bore_z=-82.3)
CH_LIP = dict(anchor=(24.95, 26.5, -76.8, -74.8), root=(25.2, -76.8), tip=(23.6, -79.55), t=0.6)
# ---- latch push-button: O-ring 14x1.5 in the shell bore ----
BTN611 = dict(BTN)
BTN611['u_boss'] = 74.0                              # boss inner face 1.5 further in (v6.1: 75.5); head 1.5 longer
BTN_OR = dict(u=(74.6, 76.6), groove_d=16.64, id=14.0, cs=1.5)  # gland 1.32 -> squeeze 12 % (rod seal on the Ø14 head)
# ---- condensation drain (labyrinth) + sloped wet-ring floor ----
DRAIN_XY = (-52.0, 27.0)
DRAIN = dict(boss_r=5.0, boss_top=-97.0, ch_r=2.6, ch_z=(-102.5, -98.5), slit_w=0.8, slit_z=(-102.2, -101.2),
             holes_d=0.8, holes_r=1.1, n_holes=4, n_slits=3)
FLOOR_SLOPE_DEG = 1.5


# =====================================================================================
# TURN + CUP
# =====================================================================================
def build_turn611(x, y):
    """flush quarter-turn: ridge flush with the flat bottom (along X when locked), face disc Ø18 under the dish floor,
    45 deg cone, Ø10 shaft through a round Ø10.3 bore with an O-ring 8x1.5, square hole for the 3x3 key (along Y when locked)"""
    ridge = box(-8.0, 8.0, -2.0, 2.0, Z_BOT + 0.05, TT_DISH_FLOOR - 1.15)
    face = U([cyl(TT_FACE_D, TT_DISH_FLOOR - 1.2, TT_DISH_FLOOR - 0.05, NF),
              hull_of((circle_pts(TT_FACE_D, NF), TT_DISH_FLOOR - 0.06), (circle_pts(TT_SHAFT_D, NF), TT_CONE_TOP - 0.05))])
    shaft = U([cyl(TT_SHAFT_D, TT_DISH_FLOOR - 0.1, SHAFT_TOP - 0.6, NF),
               hull_of((circle_pts(TT_SHAFT_D, NF), SHAFT_TOP - 0.61), (circle_pts(TT_SHAFT_D - 1.2, NF), SHAFT_TOP))])
    m = U([ridge, face, shaft])
    z0, z1 = OR_TT['z']
    m = D(m, [D(cyl(TT_SHAFT_D + 1, z0, z1, NF), cyl(OR_TT['groove_d'], z0 - 1, z1 + 1, NF)),
              box(-KEY_HOLE / 2, KEY_HOLE / 2, -TT_SHAFT_D, TT_SHAFT_D, Z_LOCK, Z_LOCK + KEY_HOLE)])
    return at(m, x, y)


def build_key(x, y):
    return box(x - KEY['w'] / 2, x + KEY['w'] / 2, y - KEY['l'] / 2, y + KEY['l'] / 2, Z_LOCK + 0.01, Z_LOCK + KEY['h'] - 0.01)


def cup_solid(x, y, top):
    """receptacle hanging from the box: tube + two BRIDGED ledges (|y_local| >= 5.6, print as bridges in the flipped box)
    with a 45 deg lead-in on their inner top edges and a 0.3 notch across them at 90 deg; 4 stop ribs on the tube wall.
    Entry: key along X passes between the ledges; turn +90 deg (CCW from above = clockwise seen from below) -> key along Y
    rests in the notches."""
    tube = D(cyl(2 * CUP_RO, CUP_Z0, top, NF), cyl(2 * CUP_RI, CUP_Z0 - 1, top + 1, NF))
    disk = Point(0, 0).buffer(CUP_RI + 0.3, resolution=64)
    ledges = []
    for sg in (1, -1):
        reg = disk.intersection(sbox(-20, LEDGE_Y, 20, 20) if sg > 0 else sbox(-20, -20, 20, -LEDGE_Y))
        led = prism(reg, CUP_Z0, LEDGE_TOP)
        yy = sg * LEDGE_Y
        # 45 deg lead-in: remove the wedge above the plane through (y 5.6, z top - LEAD) and (y 5.6 + LEAD, z top)
        tri = [(yy, LEDGE_TOP - LEAD), (yy, LEDGE_TOP + 0.5), (yy + sg * (LEAD + 0.5), LEDGE_TOP + 0.5), (yy - sg * 0.5, LEDGE_TOP + 0.5), (yy - sg * 0.5, LEDGE_TOP - LEAD)]
        w = trimesh.convex.convex_hull(np.array([[xx, a, b] for xx in (-20.0, 20.0) for a, b in tri]))
        led = D(led, [w, box(-1.75, 1.75, -20, 20, LEDGE_TOP - NOTCH, LEDGE_TOP + 1)])
        ledges.append(led)
    ribs = [rotz(box(CUP_RI - 1.0, CUP_RI + 0.3, -RIB_W / 2, RIB_W / 2, CUP_Z0, LEDGE_TOP + 3.5), a) for a in RIB_ANG]
    return at(U([tube] + ledges + ribs), x, y)


# =====================================================================================
# CAP (fondello_v611)
# =====================================================================================
def drain_parts():
    """labyrinth drain: boss with 3 entry slits (0.8) at floor level, chamber (sump 0.5 under the floor), 4 exit holes Ø0.8
    in a 1.5 mm web; entry slits and exit holes never see each other in a straight line"""
    xd, yd = DRAIN_XY
    boss = at(cyl(2 * DRAIN['boss_r'], Z_BOT - 1, DRAIN['boss_top'], 64), xd, yd)
    cuts = [at(cyl(2 * DRAIN['ch_r'], DRAIN['ch_z'][0], DRAIN['ch_z'][1], 64), xd, yd)]
    for k in range(DRAIN['n_slits']):
        a = 90.0 + 120.0 * k
        s = rotz(box(DRAIN['ch_r'] - 0.5, DRAIN['boss_r'] + 1.0, -DRAIN['slit_w'] / 2, DRAIN['slit_w'] / 2, *DRAIN['slit_z']), a)
        cuts.append(at(s, xd, yd))
    for k in range(DRAIN['n_holes']):
        a = 45.0 + 90.0 * k
        hx, hy = polar(DRAIN['holes_r'], a)
        cuts.append(at(cyl(DRAIN['holes_d'], Z_BOT - 1, DRAIN['ch_z'][0] + 0.01, 24), xd + hx, yd + hy))
    return boss, cuts


def floor_screed(clip_in, keep_out):
    """1.5 deg cone rising away from the drain over the wet-ring floor (outside the D): the drain is the low point"""
    xd, yd = DRAIN_XY
    s = math.tan(math.radians(FLOOR_SLOPE_DEG))
    R = 140.0
    cone = revolve([(0.0, Z_BOT + T_CAP - 0.6), (R, Z_BOT + T_CAP - 0.6), (R, Z_BOT + T_CAP + s * R), (0.0, Z_BOT + T_CAP)], 96)
    if cone.volume < 0:
        cone.invert()
    cone = at(cone, xd, yd)
    return D(I(cone, clip_in), [keep_out])


def build_cap611():
    outer = pod_solid(0.0, z_hi=Z_S - SEAM)
    inner = pod_solid(T_CAP)
    shell = D(outer, [inner])
    clip_in = pod_solid(T_CAP - 0.3)
    up = I(prism(ring2d(BOX_OUT.buffer(UP_OUT, join_style=1, resolution=16), BOX_OUT.buffer(-UP_IN, join_style=1, resolution=16)), Z_BOT - 5, Z_C), clip_in)
    so, si = SEAM_R - (SPIG_OFF - T_SHELL), SEAM_R - (SPIG_IN - T_SHELL)          # vertical spigot (constant section)
    spig = at(D(cyl(2 * so, Z_S - SEAM - 0.01, SPIG_TOP, 512), cyl(2 * si, Z_S - SEAM - 1, SPIG_TOP + 1, 512)), SEAM_CX, 0)
    tube = I(at(cyl(2 * SOCK['r_out'], Z_BOT - 5, SOCK['top'], NF), CH_X, 0), clip_in)
    bosses = []
    for x, y in TT:
        bosses += [I(at(cyl(BOSS_LO_D, Z_BOT - 5, BOSS_LO_TOP, NF), x, y), clip_in), I(at(cyl(BOSS_HI_D, BOSS_LO_TOP - 0.01, BOSS_TOP, NF), x, y), clip_in)]
    sup = [I(box(BB['x'][0] - 1.0, BB['x'][1] + 1.0, y0, y1, Z_BOT, BB['z'][0] - 0.1), clip_in) for y0, y1 in ((20.0, 28.0), (-28.0, -20.0))]
    dboss, dcuts = drain_parts()
    D_KEEP = prism(BOX_OUT.buffer(UP_OUT - 0.01, join_style=1, resolution=16), Z_BOT - 10, Z_C + 1)
    screed = floor_screed(clip_in, D_KEEP)
    body = U([shell, up, spig, tube, screed, I(dboss, clip_in)] + bosses + sup)
    groove = prism(ring2d(WALL_C.buffer(GRV_W611 / 2, join_style=1, resolution=16), WALL_C.buffer(-GRV_W611 / 2, join_style=1, resolution=16)), Z_C - GRV_D, Z_C + 1)
    seam_grv = at(D(cyl(2 * (so + 1.0), ZG_SEAM[0], ZG_SEAM[1], 512), cyl(2 * (so - SEAM_G), ZG_SEAM[0] - 1, ZG_SEAM[1] + 1, 512)), SEAM_CX, 0)
    cx_, r_ = CH_X, OUTLET['r']
    cuts = [groove, seam_grv,
            at(cyl(2 * r_, Z_BOT - 10, SOCK['bore_z'] + 0.01, NF), cx_, 0),                                 # outlet bore Ø46
            at(hull_of((circle_pts(2 * r_, NF), Z_BOT + OUTLET['chamfer']), (circle_pts(2 * (r_ + OUTLET['chamfer'] + 1.0), NF), Z_BOT - 1.0)), cx_, 0),
            at(cyl(2 * SOCK['r'], SOCK['pilot'][0], SOCK['top'] + 1, NF), cx_, 0),                            # pilot + upper socket Ø48.7
            at(cyl(2 * SOCK['pocket'][2], SOCK['pocket'][0], SOCK['pocket'][1], NF), cx_, 0),                 # flap pocket
            at(cyl(2 * SOCK['groove'][2], SOCK['groove'][0], SOCK['groove'][1], NF), cx_, 0),                 # lip anchor groove
            at(hull_of((circle_pts(2 * SOCK['r'], NF), SOCK['top'] - 0.6), (circle_pts(2 * (SOCK['r'] + 0.7), NF), SOCK['top'] + 0.01)), cx_, 0)]
    cuts += dcuts
    for x, y in TT:
        cuts += [at(cyl(TT_BORE_D, Z_BOT - 1, BOSS_TOP + 1, NF), x, y),
                 at(cyl(TT_DISH_D, Z_BOT - 5, TT_DISH_FLOOR, NF), x, y),
                 at(hull_of((circle_pts(TT_FACE_D + 0.4, NF), TT_DISH_FLOOR - 0.01), (circle_pts(TT_BORE_D, NF), TT_CONE_TOP + 0.15)), x, y)]
    return D(body, cuts)


# =====================================================================================
# BOX (scatola_v611): v6.1 box with the posts replaced by 3 cups
# =====================================================================================
def build_box611():
    walls = prism(ring2d(BOX_OUT, BOX_IN), Z_W, Z_R - ROOF_T + 0.01)
    roof = prism(BOX_OUT, Z_R - ROOF_T, Z_R)
    rim = prism(ring2d(BOX_OUT.buffer(FL_OUT, join_style=1, resolution=16), BOX_IN), Z_W, Z_W + 3.0)
    boss = prism(Point(0, 0).buffer(v6.BOSS_R, resolution=96).intersection(BOX_OUT), v6.BOSS_Z0, Z_R - 1.0)
    cage = prism(sbox(-CRADLE_HALF_X, CAGE_Y[0], CRADLE_HALF_X, CAGE_Y[1]), CAGE_Z0, Z_R - 1.0)
    parts = [walls, roof, rim, boss, cage]
    slot_cuts = []
    for sy in (1, -1):
        y_in, y_end = sy * (BOX_IN.bounds[3] + 0.5), sy * (BB['y'][1] - 2.0)
        parts.append(box(BB['x'][0] - 2.0, BB['x'][1] + 2.0, min(y_in, y_end), max(y_in, y_end), Z_W + 3.0, Z_R - 1.0))
        slot_cuts.append(box(BB['x'][0] - 0.15, BB['x'][1] + 0.15, min(y_in, sy * (BB['y'][1] - 3.0)), max(y_in, sy * (BB['y'][1] - 3.0)), Z_W - 1.0, BB['z'][1] + 0.3))
    parts += [b61._wall_pad(GLAND, GLAND['pad_d'])]
    # A/B: cups rise to the roof plane outside the -X wall, joined to the wall by a web (tube in tension, prints from the bed)
    for (x, y) in TT[:2]:
        parts.append(cup_solid(x, y, CUP_TOP_AB))
        parts.append(box(x + CUP_RO - 1.0, BXO[0] + 0.5, y - 4.0, y + 4.0, Z_W, Z_R))
    # C: cup under the board, hung from a column in the servo | board corridor (cradle face -> roof)
    parts.append(cup_solid(TT[2][0], TT[2][1], CUP_TOP_C))
    c = COL_C
    parts.append(box(c['x0_hi'], c['x1'], c['y0'], c['y1'], CAGE_Z0 - 2.0, Z_R - 0.5))
    parts.append(box(c['x0_lo'], c['x1'], c['y0'], c['y1'], CUP_TOP_C - 0.01, CAGE_Z0 - 2.0))
    parts.append(trimesh.convex.convex_hull(np.array([[xx, yy, zz] for yy in (c['y0'], c['y1']) for xx, zz in
                                                      ((c['x0_lo'], CAGE_Z0 - 2.0), (c['x0_hi'], CAGE_Z0 - 2.0), (c['x0_hi'], CAGE_Z0 - 2.0 + (c['x0_hi'] - c['x0_lo'])))])))
    body = U(parts)
    cuts = [box(-CRADLE_HALF_X + 2.5, CRADLE_HALF_X - 2.5, VOID_Y[0], VOID_Y[1], CAGE_Z0 - 1.0, v6.S_TOP + 0.5),
            cyl(2 * dt.HUB_CAV_R, v6.S_TOP + 0.5 - 0.01, v6.CAV_TOP + 0.01, 96),
            hull_of((circle_pts(2 * dt.HUB_CAV_R, 96), v6.CAV_TOP), (circle_pts(2 * v6.PLAT_HOLE_R, 96), v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R)),
            cyl(2 * v6.PLAT_HOLE_R, v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R - 0.01, Z_R + 1.0, 96),
            b61._wall_pad(GLAND, GLAND['hole_d'], True), at(cyl(VENT['hole_d'], Z_R - ROOF_T - 1, Z_R + 1, 48), VENT['x'], VENT['y'])] + slot_cuts
    for x, y in SERVO_HOLES_W:
        cuts.append(at(U([cyl(v6.INS_D, CAGE_Z0 - 1, CAGE_Z0 + dt.SERVO_INS_DEPTH, 48),
                          hull_of((circle_pts(v6.INS_D + 1.8, 48), CAGE_Z0 - 0.5), (circle_pts(v6.INS_D, 48), CAGE_Z0 + 0.4))]), x, y))
    for x, y in BOT_INS61:
        cuts.append(at(U([cyl(v6.INS_D, Z_R - v6.INS_DEPTH, Z_R + 1.0, 48),
                          hull_of((circle_pts(v6.INS_D, 48), Z_R - 0.4), (circle_pts(v6.INS_D + 1.8, 48), Z_R + 0.5))]), x, y))
    cuts.append(face_region(text_poly(f'{VER} DRY', 6.0, 20.0, 0.0), Z_R, True))
    return D(body, cuts)


# =====================================================================================
# SHELL + PUSH-BUTTON (guscio_v611, pulsante_v611)
# =====================================================================================
def build_shell611():
    outer = pod_solid(0.0, z_lo=Z_S, z_hi=Z_TOP)
    inner = pod_solid(T_SHELL)
    body = D(outer, [inner])
    parts = [body]
    tab_cuts = []
    for a in TAB_ANG:
        r_w = shell_r_at(a, -3.0, T_SHELL)
        tab = rotz(box(TAB_R_INS - 6.0, r_w + 1.0, -TAB_W / 2, TAB_W / 2, -TAB_T, 0.0), a)
        webs = []
        for off in (-TAB_W / 2 + 1.5, TAB_W / 2 - 1.5):
            L = r_w - (TAB_R_INS - 6.0)
            web = trimesh.convex.convex_hull(np.array([[TAB_R_INS - 6.0, off + sgn * 1.5, -TAB_T] for sgn in (-1, 1)] +
                                                      [[r_w + 1.0, off + sgn * 1.5, -TAB_T] for sgn in (-1, 1)] +
                                                      [[r_w + 1.0, off + sgn * 1.5, -TAB_T - L * 1.0] for sgn in (-1, 1)]))
            webs.append(rotz(web, a))
        parts += [I(U([tab] + webs), pod_solid(T_SHELL - 0.5))]
        x, y = polar(TAB_R_INS, a)
        tab_cuts.append(at(cyl(3.4, -TAB_T - 1, 1.0, 32), x, y))
    r_out = shell_r_at(LATCH_A, BTN_Z, 0.0)
    boss = I(radial_cyl(BTN611['boss_d'], BTN611['u_boss'], r_out - 0.5, LATCH_A, BTN_Z, NF), pod_solid(0.5))
    parts.append(boss)
    parts.append(D(pod_solid(0.0, z_lo=Z_S, z_hi=SEAM_BAND_TOP), [at(cyl(2 * SEAM_R, Z_S - 1, SEAM_BAND_TOP + 1, 512), SEAM_CX, 0)]))
    sh = U(parts)
    rs = (BTN611['dish_d'] / 2) ** 2 / (2 * BTN611['dish_h']) + BTN611['dish_h'] / 2
    sph = trimesh.creation.icosphere(subdivisions=5, radius=rs)
    sph.apply_translation([r_out - BTN611['dish_h'] + rs, 0, BTN_Z])
    # lead-in chamfer at the bottom inner edge (seam O-ring) and at the top outer edge (shadow lip)
    lead_b = hull_of((circle_pts(2 * (SEAM_R + SHELL_LEADIN), 512) + [SEAM_CX, 0], Z_S - 0.01), (circle_pts(2 * SEAM_R, 512) + [SEAM_CX, 0], Z_S + SHELL_LEADIN))
    seam_cyl = at(cyl(2 * SEAM_R, Z_S - 1, SEAM_BAND_TOP, 512), SEAM_CX, 0)
    top_ch = D(cyl(2 * (R_TOP + 5), Z_TOP - SHELL_TOP_CH, Z_TOP + 1, 256),
               hull_of((circle_pts(2 * (R_TOP + 0.02), 256), Z_TOP - SHELL_TOP_CH - 0.01), (circle_pts(2 * (R_TOP - SHELL_TOP_CH), 256), Z_TOP + 0.01)))
    cuts = tab_cuts + [rotz(sph, LATCH_A), radial_cyl(BTN611['bore'], BTN611['u_boss'] - 1, r_out + 2, LATCH_A, BTN_Z, NF),
                       radial_cyl(BTN_OR['groove_d'], BTN_OR['u'][0], BTN_OR['u'][1], LATCH_A, BTN_Z, NF), lead_b, top_ch]
    return D(sh, cuts), r_out


def build_button611(r_out):
    """v6.1 push-button with the head 1.5 longer (collar 1.5 further in): the head covers the bore O-ring at rest and pressed"""
    u_face = r_out - BTN611['dish_h']
    ub = BTN611['u_boss'] - 0.1
    rh, rc, rs = BTN611['head_d'] / 2, BTN611['collar_d'] / 2, BTN611['shaft_d'] / 2
    prof = [(0, BTN611['tip_u']), (rs - 0.4, BTN611['tip_u']), (rs, BTN611['tip_u'] + 0.4), (rs, ub - 2.4), (rc, ub - 2.4), (rc, ub - (rc - rh)),
            (rh, ub), (rh, u_face - 0.5), (rh - 0.5, u_face), (0, u_face)]
    m = revolve(prof, NF)
    if m.volume < 0:
        m.invert()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation([0, 0, BTN_Z])
    return rotz(m, LATCH_A)


# =====================================================================================
# FLANGE + SHADOW LIP (flangia_piano_v611, labbro_ombra_v611)
# =====================================================================================
def build_flange611(cav):
    plate = revolve([(0, FL_Z0), (FL_R611 - 0.5, FL_Z0), (FL_R611, FL_Z0 + 0.5), (FL_R611, FL_Z1 - 0.5), (FL_R611 - 0.5, FL_Z1), (0, FL_Z1)], 2 * SEG)
    if plate.volume < 0:
        plate.invert()
    skirt = D(cyl(2 * v6.SKIRT_R1, v5.HOOK_Z0, FL_Z0 + 0.01), cyl(2 * v6.SKIRT_R0, v5.HOOK_Z0 - 1, FL_Z0 + 1))
    tongues = [bd.sector_solid(a0, a1, v5.HOOK_R0, v6.SKIRT_R1 - 0.5, v5.HOOK_Z0, v5.HOOK_Z1, 24) for a0, a1 in HOOKS61]
    pins = []
    for a in PIN_ANG61:
        x, y = polar(v6.PIN_R, a)
        z0 = b61.W1 + v6.PIN_GAP
        pins.append(at(U([cyl(v6.PIN_D, z0, FL_Z0 + 0.01, 48), hull_of((circle_pts(v6.PIN_D, 48), FL_Z0 - 1.0), (circle_pts(v6.PIN_D + 2.0, 48), FL_Z0 + 0.01))]), x, y))
    body = U([plate, skirt] + tongues + pins)
    cuts = [cav,
            D(cyl(2 * v5.LGROOVE_R1, FL_Z0 - 1, FL_Z0 + v5.LGROOVE_D), cyl(2 * v5.LGROOVE_R0, FL_Z0 - 2, FL_Z0 + v5.LGROOVE_D + 1)),
            at(D(cyl(2 * v5.FL_GSK_R + v5.GRV_W, FL_Z1 - v5.GRV_D, FL_Z1 + 1), cyl(2 * v5.FL_GSK_R - v5.GRV_W, FL_Z1 - v5.GRV_D - 1, FL_Z1 + 2)), *v6.HOLE_C),
            at(cyl(GROM['hole'], FL_Z0 - 1, FL_Z1 + 1, 48), *CABLE_XY),
            D(cyl(2 * SH_GRV[1], FL_Z0 - 1, FL_Z0 + SH_GRV[2], 2 * SEG), cyl(2 * SH_GRV[0], FL_Z0 - 2, FL_Z0 + SH_GRV[2] + 1, 2 * SEG))]
    for x, y in v6.COLLAR_PINS:
        cuts.append(at(cyl(3.4, FL_Z1 - 3.0, FL_Z1 + 1.0, 32), x, y))
    for x, y in WOOD_XY:
        cuts.append(at(U([cyl(v5.WOOD_D, FL_Z0 - 1, FL_Z1 + 1, 32), cyl(v5.WOOD_CB_D, FL_Z0 - 1, FL_Z0 + v5.WOOD_CB_H, 48)]), x, y))
    ex, ey = polar(72.0, 180.0)
    cuts.append(face_region(affinity.scale(text_poly(VER, 5.0, ex, ey, 90.0), -1, 1, origin=(ex, ey)), FL_Z0, False))
    return D(body, cuts)


def lip_revolve(poly, n=2 * SEG):
    c = np.array(poly.exterior.coords)[:-1]
    m = trimesh.creation.revolve(np.vstack([c, c[:1]]), sections=n)
    if m.volume < 0:
        m.invert()
    return m


def flap_poly(root, tip, t):
    A, B = np.array(root, float), np.array(tip, float)
    d = (B - A) / np.linalg.norm(B - A)
    nrm = np.array([-d[1], d[0]]) * t / 2
    return Polygon([A - nrm, B - nrm, B + nrm, A + nrm])


def build_shadow_lip():
    a0, a1 = SH_LIP['anchor']
    anchor = sbox(a0, FL_Z0 + 0.02, a1, FL_Z0 + SH_GRV[2] - 0.05)
    p = shapely.unary_union([anchor, flap_poly((SH_LIP['root'][0], FL_Z0 + 0.3), SH_LIP['tip'], SH_LIP['t'])]).buffer(0.05).buffer(-0.05)
    return lip_revolve(p)


# =====================================================================================
# CHUTE + CHUTE LIP (scivolo_v611, labbro_scivolo_v611)
# =====================================================================================
def build_chute611(F):
    b61.Z_CH_END = Z_CH_END611                       # v6.1 builder reads Z_CH_END for the tube and tip
    try:
        m = b61.build_chute61(F)
    finally:
        b61.Z_CH_END = -73.0
    # v6.1 tip = drip-edge chamfer at -80.5 now; replace it by a 1 mm 45 deg lead-in on the outer edge (it enters the socket)
    tip_add = at(D(cyl(2 * RO, Z_CH_END611, Z_CH_END611 + 1.6, NF), cyl(2 * RI, Z_CH_END611 - 1, Z_CH_END611 + 2, NF)), CH_X, 0)
    tip_cut = at(D(cyl(2 * RO + 4, Z_CH_END611 - 1, Z_CH_END611 + CH_TIP_CH, NF),
                   hull_of((circle_pts(2 * (RO - CH_TIP_CH), NF), Z_CH_END611 - 0.01), (circle_pts(2 * RO, NF), Z_CH_END611 + CH_TIP_CH))), CH_X, 0)
    return D(U([m, tip_add]), [tip_cut])


def build_chute_lip():
    r0, r1, z0, z1 = CH_LIP['anchor']
    anchor = sbox(r0, z0 + 0.02, r1, z1 - 0.02)
    p = shapely.unary_union([anchor, flap_poly((CH_LIP['root'][0], z0 + 0.3), CH_LIP['tip'], CH_LIP['t'])]).buffer(0.05).buffer(-0.05)
    return at(lip_revolve(p, NF), CH_X, 0)


# =====================================================================================
# BOUGHT PARTS
# =====================================================================================
def oring_radial_cyl(id_, cs, u_c, n=NF):
    """O-ring (torus) round the push-button axis"""
    m = v6.torus(id_ / 2 + cs / 2, cs / 2, 0.0, n=n)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation([u_c, 0, BTN_Z])
    return rotz(m, LATCH_A)


def seam_oring_ring():
    """O-ring in the spigot groove: horizontal circle at z -70, centre/radius from the pod section"""
    zc = sum(ZG_SEAM) / 2
    cxs, rs = SEAM_CX, SEAM_R                         # vertical seam band of the shell (contact)
    gland = 0.25 + SEAM_G                             # 1.70 between groove bottom and the shell
    m = v6.torus(rs - gland / 2, OR_SEAM_CS / 2, zc, x=cxs, y=0.0, n=256)   # free section drawn: overlaps = squeeze
    return m, rs


def bought611():
    B, sc = b61.bought61()
    B.pop('oring_tt_8x1.5', None)
    B['oring_tt_8x1.5'] = U([v6.torus(OR_TT['groove_d'] / 2 + 0.7, 0.7, sum(OR_TT['z']) / 2, x=x, y=y) for x, y in TT])
    B['keys_3x3x18'] = U([build_key(x, y) for x, y in TT])
    B['oring_seam_2'], _ = seam_oring_ring()
    rc_b = (BTN611['head_d'] / 2 + BTN_OR['groove_d'] / 2) / 2                # gland centre, free section drawn (overlaps = squeeze)
    B['oring_btn_14x1.5'] = oring_radial_cyl(2 * (rc_b - BTN_OR['cs'] / 2), BTN_OR['cs'], sum(BTN_OR['u']) / 2)
    return B, sc


# =====================================================================================
# BUILD / EXPORT
# =====================================================================================
def build_all():
    P, COLOUR, EXTRA = {}, {}, {}
    F = b61.funnel61()
    EXTRA['F'] = F
    ye = b61.zsec_poly(F[3], -0.05).bounds[3] + 5.0          # chute ears as in build_bowl61 (bowl reused from disk)
    b61.CH_EARS = [(CH_X, round(ye, 1)), (CH_X, -round(ye, 1))]
    cav = v6.fl_funnel_cavity()
    v6.COLLAR_PINS = v6.collar_pin_sites(cav)
    EXTRA['FL_CAV'] = cav
    P['fondello_v611'] = build_cap611()
    P['scatola_v611'] = build_box611()
    P['guscio_v611'], EXTRA['btn_r_out'] = build_shell611()
    P['pulsante_v611'] = build_button611(EXTRA['btn_r_out'])
    P['flangia_piano_v611'] = build_flange611(cav)
    P['labbro_ombra_v611'] = build_shadow_lip()
    P['scivolo_v611'] = build_chute611(F)
    P['labbro_scivolo_v611'] = build_chute_lip()
    tts = [build_turn611(x, y) for x, y in TT]
    P['nottolino_v611'] = tts[2]
    EXTRA['tts'] = tts
    col = {'scivolo_v611': 'green', 'pulsante_v611': 'orange', 'nottolino_v611': 'orange'}
    for k, m in P.items():
        COLOUR[k] = [(col.get(k, 'yellow' if k.startswith('labbro') else 'black'), m)]
    return P, COLOUR, EXTRA


FLIP = {'fondello_v611': False, 'scatola_v611': True, 'guscio_v611': False, 'pulsante_v611': None, 'flangia_piano_v611': True,
        'labbro_ombra_v611': True, 'scivolo_v611': True, 'labbro_scivolo_v611': True, 'nottolino_v611': True}
RHO = {k: (TPU if k.startswith('labbro') else PETG) for k in FLIP}


def print_matrix(m, name, flip=None):
    """exact 4x4 print transform (rotation, then centre XY and drop to z 0) - the same matrix is applied to every
    colour body (v6.1 fitted it from 4 vertices: degenerate for some meshes)"""
    T = np.eye(4)
    if name.startswith('pulsante'):
        T = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]) @ trimesh.transformations.rotation_matrix(-math.radians(LATCH_A), [0, 0, 1])
    elif name.startswith('guscio'):
        pass
    elif (FLIP.get(name) if flip is None else flip):
        T = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    p = m.copy()
    p.apply_transform(T)
    return trimesh.transformations.translation_matrix([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]]) @ T


def export_part(name, m, bodies, flip=None, suffix=''):
    m = v6.clean(m)
    if not suffix:
        m.export(OUT + f'{name}.stl'); m.export(OUT + f'{name}.3mf')
    wt = bool(trimesh.load(OUT + f'{name}.stl').is_watertight) if not suffix else None
    T = print_matrix(m, name, flip)
    pm = m.copy(); pm.apply_transform(T)
    sc = trimesh.Scene()
    cb = {}
    for c, b in bodies:
        pb = v6.clean(b).copy()
        pb.apply_transform(T)
        if len(bodies) > 1:
            pb.export(OUT + f'{name}_print_{c}{suffix}.stl')
        cb[c] = pb
        sc.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
    sc.export(OUT + f'{name}_print{suffix}.3mf')
    if not suffix:
        pm.export(OUT + f'{name}_print.stl')
    return wt, pm, cb


def reexport_v61_colour_bodies():
    """coordinator finding: v6.1 colour-body print STLs of disco / gate / window were zero-volume or shifted (4-vertex fit).
    Re-export them from the assembled-position colour bodies with the exact print matrix of the main body."""
    res = {}
    fl61 = b61.FLIP
    for name, cols in (('disco_v61', ('orange', 'black')), ('piastra_gate_v61', ('black', 'green')), ('piastra_finestra_v61', ('black', 'green'))):
        main = trimesh.load(OUT + f'{name}.stl')
        bodies = [(c, v6.clean(trimesh.load(ASM.replace('v611_asm', 'v61_asm') + f'{name}_{c}.stl'))) for c in cols]   # clean: float32 reload of one body was open
        T = print_matrix(main, name, flip=fl61[name])
        pm = main.copy(); pm.apply_transform(T)
        ref = trimesh.load(OUT + f'{name}_print.stl')
        sc = trimesh.Scene()
        info = {'main_print_matches_v61_print_stl': bool(np.allclose(pm.bounds, ref.bounds, atol=0.02))}
        vols = 0.0
        for c, b in bodies:
            pb = b.copy(); pb.apply_transform(T)
            pb.export(OUT + f'{name}_print_{c}_v611.stl')
            sc.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
            inside = bool(np.all(pb.bounds[0] >= ref.bounds[0] - 0.02) and np.all(pb.bounds[1] <= ref.bounds[1] + 0.02))
            info[c] = {'volume_mm3': round(float(pb.volume), 1), 'watertight': bool(pb.is_watertight), 'inside_print_stl_bbox': inside,
                       'bounds': np.round(pb.bounds, 2).tolist()}
            vols += pb.volume
        tb = []
        for c, b in bodies:
            q = b.copy(); q.apply_transform(T); tb.append(q)
        info['sum_colour_volumes_mm3'] = round(float(vols), 1)
        info['main_volume_mm3'] = round(float(ref.volume), 1)
        try:
            u = U(tb)
            info['union_colour_volume_mm3'] = round(float(u.volume), 1)
            info['union_minus_main_mm3'] = round(float(vol(D(u, [ref]))), 3)
            info['main_minus_union_mm3'] = round(float(vol(D(ref, [u]))), 3)
        except ValueError as e:
            info['union_check'] = f'skipped: {e}'
        sc.export(OUT + f'{name}_print_v611.3mf')
        res[name] = info
    return res


if __name__ == '__main__':
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    v6.SCRATCH = SCRATCH
    P, COLOUR, EXTRA = build_all()
    print('\n--- v6.1.1 parts ---')
    for k, m in P.items():
        report(k, m)
    for k, m in zip('ABC', EXTRA['tts']):
        assert m.is_watertight, k
    if STAGE == 'build':
        sys.exit(0)
    EXPORT_WT, PR, OVH, GR = {}, {}, {}, {}
    for k, m in P.items():
        EXPORT_WT[k], PR[k], _ = export_part(k, m, COLOUR[k])
        OVH[k] = round(overhang(PR[k]), 1)
        GR[k] = v6.grams_est(m, RHO[k])
    COLFIX = reexport_v61_colour_bodies()
    print('exported; watertight on reload:', EXPORT_WT)
    print('colour bodies re-exported:', json.dumps(COLFIX, indent=1))
    if STAGE == 'parts':
        sys.exit(0)
    exec(open(dt.HERE + 'build_v611_checks.py').read())
