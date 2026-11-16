#!/usr/bin/env python3
"""
Dosing module v4b for the kibble dispenser: hangs UNDER a level shelf by a quarter-turn bayonet.

CORE (mount-independent)
  disco_v4b            two-pocket volumetric disc (S/M/L via VARIANT), keyed hex to albero_mozzo (fits one way)
  piastra_gate_v4b     fixed plate under the disc, ONE outlet at 180 deg (-X), keyed one way
  piastra_finestra_v4b fixed plate above the disc, ONE filling window at 0 deg (+X), keyed one way
  chiocciola_scivolo_v4b ONE printed part: bowl (plate seats, keys, bayonet lugs, latch slot) + funnel + straight chute
  linguetta_sicura     orange safety latch (slides into the bowl wall from below, snaps behind a flange hook)
  guarnizione_baionetta TPU ring in the rim groove, compressed by the bayonet lift
MOUNT: the flange on the shelf (flangia_piano, other engineer) must match the BAYONET dict in dosing.json.
The old box-lid mount of v4a is kept in build_dosing_v4a.py.

Frame: Z-up mm, Z=0 = underside of the bowl base plate (was the lid top), X=Y=0 on the shaft axis.
Main files at assembled height; *_print.stl on z=0 in print orientation.
"""
import json
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox
from shapely import affinity
import shapely

import build_drivetrain as dt          # geometry only (exports/checks run only when that script is run directly)

OUT = dt.OUT
VER = 'v4b'
U, D, I = dt.U, dt.D, dt.I
cyl, box, at, prism, hull_of, circle_pts, revolve, hexagon = (dt.cyl, dt.box, dt.at, dt.prism, dt.hull_of,
                                                               dt.circle_pts, dt.revolve, dt.hexagon)
SEG = dt.SEG

# =====================================================================================
# PARAMETERS — CORE
# =====================================================================================
KIBBLE_MAX = 14.0                       # largest kibble expected (mm); large-breed variant: raise it
PASSAGE_MIN = max(30.0, 3.0 * KIBBLE_MAX)
VARIANT = 'M'                           # disc exported now
PLATES_FOR = 'L'                        # window/outlet sized for the largest pocket -> plates common to S/M/L
# pocket: r_in, r_out, target volume per pocket (cm3) from the research (section 5 C); angle solved from the volume
POCKETS = {'S': (18.0, 44.0, 10.1), 'M': (18.0, 46.0, 16.3), 'L': (16.0, 47.0, 21.8)}
POCKET_CORNER_R = 6.0
POCKET_DRAFT_DEG = 2.0                  # through-pocket widens downward (clean release)
POCKET_TOP_CH = 0.6                     # small top edge break (no big chamfer under the wiper lip)
BULK_DENSITY = 0.400                    # g/cm3

DISC_D, DISC_T = 103.0, 16.0
DISC_Z0 = dt.DISC_Z0                    # 32 (hub interface unchanged)
DISC_Z1 = DISC_Z0 + DISC_T              # 48
GAP = 0.8
PLATE_T = 3.0
GATE_Z1 = DISC_Z0 - GAP                 # 31.2
GATE_Z0 = GATE_Z1 - PLATE_T             # 28.2 = seat in the bowl
WIN_Z0 = DISC_Z1 + GAP                  # 48.8
WIN_Z1 = WIN_Z0 + PLATE_T               # 51.8
OUT_MARGIN_IN, OUT_MARGIN = 2.0, 2.5
WIN_MARGIN = 2.5
PLATE_DRAFT_DEG = 7.0
GATE_HOLE_D = dt.BOSS_D + 1.5
WIN_HOLE_D = 16.0
AGIT_HEX_AF, AGIT_HEX_DEPTH = 10.0, 3.0 # hex socket in the disc top for a future agitator stem
CRUMB_R = (28.0, 36.0, 44.0)
CRUMB_W, CRUMB_DEPTH = 1.5, 0.8
LIP_W, LIP_DEPTH, LIP_SETBACK = 3.0, 1.5, 1.0

BOWL_R_IN = 53.5                        # disc zone (disc r 51.5 -> 2.0 radial)
BOWL_R_STEP = 55.7                      # above the window-plate step
BOWL_R_OUT = 62.0
PLATE_CLR = 0.25
GATE_R = BOWL_R_IN - PLATE_CLR
WIN_R = BOWL_R_STEP - PLATE_CLR
KEY_ANG = (90.0, 250.0)                 # asymmetric: plates go in one way only, cannot be flipped
KEY_W, KEY_PROT_GATE, KEY_PROT_WIN, KEY_CLR = 6.0, 1.0, 1.5, 0.5

# ---- bayonet (bowl side; the flange must match -> dosing.json['bayonet']) ----
RIM_Z = 66.0                            # rim top (gasket groove face); >= 6 above the window plate
GSK_R0, GSK_R1, GSK_DEPTH = 57.0, 59.4, 1.4      # groove on the rim top
GSK_H = 2.5                             # TPU gasket height (proud 1.1, compressed 1.0 at lock)
LUG_ANG = (60.0, 180.0, 300.0)          # insertion positions (bowl frame = flange frame at insertion)
LUG_W = (22.0, 32.0, 22.0)              # angular widths; the 180 deg lug is the key (fits one way)
LUG_R1 = BOWL_R_OUT + 4.0               # lug outer radius 66
LUG_Z1 = 60.5                           # lug top
LUG_T_LEAD, LUG_T_FLAT = 3.5, 5.0       # lug thickness at the leading edge / on the flat: lift 1.5 mm
LUG_RAMP_DEG = 18.0                     # ramp length (deg), then flat
LOCK_ROT = 30.0                         # rotate +30 deg (CCW seen from above) to lock
LIFT = LUG_T_FLAT - LUG_T_LEAD
# ---- safety latch (separate orange part in a T-slot of the bowl wall, inserted from below) ----
LATCH_ANG = 76.5
LATCH_W, LATCH_T = 8.0, 1.4             # spring tab width / thickness
LATCH_FOOT_W, LATCH_FOOT_T = 12.0, 1.1  # T-foot
RAIL_Z1, TAB_Z0, TAB_Z1 = 40.0, 40.0, 56.5
NUB_Z0, NUB_Z1, NUB_H = 52.0, 56.0, 1.5
SLOT_CLR = 0.15
POCKET_R0 = 58.5                        # flex pocket floor radius behind the tab (inner wall 2.8 at the step)

# ---- chute (straight drop) ----
CHUTE_SLOPE_MIN = 46.0                  # kibble-bearing faces (hard rule 45; 50-55 preferred but costs ~1 mm depth per deg here)
CHUTE_WALL = 3.0
TUBE_D = math.ceil(PASSAGE_MIN + 2.0)   # 44
TUBE_X = -56.5                          # drop axis: collar edge x=-28.5 clears the passante flange (r 26.5) by 2.0
TUBE_END_Z = None                       # = funnel bottom - COLLAR_L (set after the depth search)
COLLAR_L = 10.0
MOUTH_FLARE = 1.0                       # funnel mouth = outlet bottom + flare (no upward step anywhere)
FLARE_OUT, FLARE_H = 4.0, 5.0           # 45 deg flare of the mouth (outward only): >= 42 mm inscribed within 5 mm of the gate
FLARE_R_MIN = None                      # hub-side chord of the flare = mouth inner radius (set below): no inward flare on the hub side
COLLAR_OD = 56.0                        # thick collar z TUBE_END_Z..COLLAR_TOP: valve seat + retaining-ring nubs
COLLAR_TOP = 2.0                        # thick collar up to z=2 (inside the base plate)
VALVE_FL_D, VALVE_FL_T, VALVE_SEAT_DEPTH = 49.0, 2.0, 1.8   # duckbill flange in an end-face pocket, 0.2 squeezed by the ring
VALVE_BILL_L, VALVE_WALL = 26.0, 1.2
NUB_ANG, NUB_W_DEG, NUB_DZ, NUB_R1 = (0.0, 120.0, 240.0), 12.0, (1.5, 3.0), COLLAR_OD / 2 + 1.5   # nub z = end + dz
RING_DZ0, RING_DZ1, RING_R1, RING_LIP_R0 = -2.0, 1.8, 31.5, TUBE_D / 2 + VALVE_WALL + 0.5   # ghiera_valvola (orange), z = end + dz
DRIP_DZ, DRIP_R1, DRIP_T = 7.0, 33.0, 1.5                 # TPU drip cone on the collar above the ring (z = end + dz)
TONGUE_R0, TONGUE_R1, TONGUE_H = 60.2, 61.2, 2.0          # rim labyrinth tongue (flange gets the groove)
N_WEDGE = 40

# ---- base (bottom plate, mount-neutral) ----
BASE_Z0, BASE_Z1 = 0.0, 3.0
BASE_HOLE_D = dt.COLLAR_D + 2.0         # 1.0 radial around the passante collar (centring)
FLOOR_RECESS = 1.0

# main screw
SCREW_STD_V4 = (60, 55, 65, 50)
TIP_TARGET = 4.0

PETG = 1.27
INLAY = 0.6
RIM_BAND = 2.0
FILAMENT = {'black': 'PETG black', 'orange': 'PETG orange', 'green': 'PETG green', 'yellow': 'TPU 95A yellow'}


# =====================================================================================
# HELPERS
# =====================================================================================
def rotz(m, deg):
    m = m.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1]))
    return m


def coords_of(g):
    if g.is_empty:
        return np.zeros((0, 2))
    if isinstance(g, Polygon):
        return np.array(g.exterior.coords)
    return np.vstack([coords_of(x) for x in g.geoms if not x.is_empty] or [np.zeros((0, 2))])


def rounded_sector(r_in, r_out, half_deg, corner_r, n=256):
    a = np.radians(np.linspace(-half_deg, half_deg, n))
    pts = np.r_[np.c_[r_out * np.cos(a), r_out * np.sin(a)], np.c_[r_in * np.cos(a[::-1]), r_in * np.sin(a[::-1])]]
    return Polygon(pts).buffer(-corner_r, resolution=32).buffer(corner_r, resolution=32)


def ang_extent(poly):
    c = coords_of(poly)
    a = np.degrees(np.arctan2(c[:, 1], c[:, 0]))
    return a.min(), a.max()


def wedge(a0, a1, R=300.0):
    a = np.radians(np.linspace(a0, a1, 8))
    return Polygon(np.r_[[[0, 0]], np.c_[R * np.cos(a), R * np.sin(a)]])


def loft_wedges(p_top, z_top, p_bot, z_bot, n=N_WEDGE, eps=0.15):
    """drafted prism between two similar outlines centred on +X: union of convex hulls of matching wedges"""
    lo = min(ang_extent(p_top)[0], ang_extent(p_bot)[0])
    hi = max(ang_extent(p_top)[1], ang_extent(p_bot)[1])
    edges = np.linspace(lo, hi, n + 1)
    parts = []
    for k in range(n):
        a0 = edges[k] - eps if k else lo - 30
        a1 = edges[k + 1] + eps if k < n - 1 else hi + 30
        w = wedge(a0, a1)
        ct, cb = coords_of(p_top.intersection(w)), coords_of(p_bot.intersection(w))
        if len(ct) < 3 or len(cb) < 3:
            continue
        parts.append(trimesh.convex.convex_hull(np.r_[np.c_[ct, np.full(len(ct), z_top)],
                                                      np.c_[cb, np.full(len(cb), z_bot)]]))
    return U(parts)


def sector_solid(a0, a1, r0, r1, z0, z1, n=24):
    a = np.radians(np.linspace(a0, a1, n))
    p = Polygon(np.r_[np.c_[r1 * np.cos(a), r1 * np.sin(a)], np.c_[r0 * np.cos(a[::-1]), r0 * np.sin(a[::-1])]])
    return prism(p, z0, z1)


def vol(m):
    return float(abs(m.volume)) if m is not None and len(m.faces) else 0.0


def report(name, m):
    print(f'{name:28s} watertight={m.is_watertight}  volume={m.volume/1000:8.3f} cm3  '
          f'x[{m.bounds[0,0]:.1f},{m.bounds[1,0]:.1f}] z[{m.bounds[0,2]:.2f},{m.bounds[1,2]:.2f}]  faces={len(m.faces)}')
    assert m.is_watertight and m.volume > 0, name


# =====================================================================================
# POCKETS, OUTLET, WINDOW OUTLINES (at 0 deg = +X)
# =====================================================================================
DRAFT_OFF = DISC_T * math.tan(math.radians(POCKET_DRAFT_DEG))


def solve_pocket_angle(variant):
    r_in, r_out, v_target = POCKETS[variant]
    lo, hi = 20.0, 120.0
    for _ in range(40):
        mid = (lo + hi) / 2
        p = rounded_sector(r_in, r_out, mid / 2, POCKET_CORNER_R)
        v = (p.area + p.buffer(DRAFT_OFF, resolution=32).area) / 2 * DISC_T / 1000
        lo, hi = (mid, hi) if v < v_target else (lo, mid)
    return round((lo + hi) / 2, 2)


POCKET_ANG = {v: solve_pocket_angle(v) for v in POCKETS}
P_TOP = rounded_sector(*POCKETS[VARIANT][:2], POCKET_ANG[VARIANT] / 2, POCKET_CORNER_R)
P_BOT = P_TOP.buffer(DRAFT_OFF, resolution=32)
P_PLATES = rounded_sector(*POCKETS[PLATES_FOR][:2], POCKET_ANG[PLATES_FOR] / 2, POCKET_CORNER_R)
PL_DRAFT = PLATE_T * math.tan(math.radians(PLATE_DRAFT_DEG))
r_in_p, r_out_p = POCKETS[PLATES_FOR][:2]
WIN_R_MAX = DISC_D / 2 - 2.5
OUT_R_MAX = GATE_R - 2.5
_ann = Point(0, 0).buffer(OUT_R_MAX - PL_DRAFT, resolution=64).difference(
    Point(0, 0).buffer(r_in_p - OUT_MARGIN_IN, resolution=64))
OUTLET_TOP = P_PLATES.buffer(DRAFT_OFF + OUT_MARGIN, resolution=32).intersection(_ann).buffer(-1.0).buffer(1.0)
OUTLET_BOT = OUTLET_TOP.buffer(PL_DRAFT, resolution=32)
WIN_TOP = P_PLATES.buffer(DRAFT_OFF + WIN_MARGIN, resolution=32).intersection(
    Point(0, 0).buffer(WIN_R_MAX - PL_DRAFT, resolution=64)).buffer(-1.0).buffer(1.0)
WIN_BOT = WIN_TOP.buffer(PL_DRAFT, resolution=32)
half = lambda p: max(abs(a) for a in ang_extent(p))
FLARE_R_MIN = round(OUTLET_BOT.exterior.distance(Point(0, 0)) - MOUTH_FLARE - 0.3, 2)   # arc clip 0.3 INSIDE the mouth arc: no ledge
ANG_SUM = half(P_BOT) + half(WIN_BOT) + half(OUTLET_BOT)
assert ANG_SUM < 180.0, ANG_SUM
assert WIN_BOT.bounds[2] <= WIN_R_MAX + 0.01 and OUTLET_BOT.bounds[2] <= OUT_R_MAX + 0.01
LIG_GATE = round(OUTLET_BOT.exterior.distance(Point(0, 0)) - GATE_HOLE_D / 2, 2)
LIG_WIN = round(WIN_BOT.exterior.distance(Point(0, 0)) - WIN_HOLE_D / 2, 2)
assert LIG_GATE >= 3.0 and LIG_WIN >= 3.0, (LIG_GATE, LIG_WIN)
print(f'pocket {VARIANT}: angle {POCKET_ANG[VARIANT]} deg r {POCKETS[VARIANT][0]}..{POCKETS[VARIANT][1]}; '
      f'plates sized for {PLATES_FOR} ({POCKET_ANG[PLATES_FOR]} deg); half-angle sum {ANG_SUM:.1f} < 180; '
      f'ligaments gate {LIG_GATE} / window {LIG_WIN}')

# =====================================================================================
# 1. DISCO v4b
# =====================================================================================
CBORE_D = dt.CBORE_D
POCKET_TOP_Z = dt.POCKET_TOP
SCREW_LEN = CBORE_BOT = None
for L in SCREW_STD_V4:
    cb = dt.SPLINE_TIP_Z - TIP_TARGET + L
    if cb + dt.SCREW_HEAD_H <= DISC_Z1 - AGIT_HEX_DEPTH and cb - POCKET_TOP_Z >= dt.MIN_SOLID:
        SCREW_LEN, CBORE_BOT = L, cb
        break
assert SCREW_LEN
SCREW_TIP_Z = CBORE_BOT - SCREW_LEN
print(f'main screw M3x{SCREW_LEN} DIN912: head z {CBORE_BOT}..{CBORE_BOT + dt.SCREW_HEAD_H}, tip z {SCREW_TIP_Z} '
      f'({dt.SPLINE_TIP_Z - SCREW_TIP_Z:.1f} below spline tip), solid under head {CBORE_BOT - POCKET_TOP_Z:.1f}')


def pocket_cutter(z0, z1, ext=1.0):
    body = loft_wedges(P_TOP, z1 + ext, P_BOT.buffer(DRAFT_OFF / DISC_T * ext, resolution=32), z0 - ext)
    ch = loft_wedges(P_TOP.buffer(POCKET_TOP_CH + 0.5, resolution=16), z1 + 0.5, P_TOP, z1 - POCKET_TOP_CH)
    return U([body, ch])


def build_disc():
    plate = cyl(DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG)
    pc = pocket_cutter(DISC_Z0, DISC_Z1)
    plate = D(plate, [pc, rotz(pc, 180)])
    cap = revolve([(4.0, dt.CAP_CEIL), (dt.CAP_RI, dt.CAP_CEIL), (dt.CAP_RI, dt.CAP_Z0), (dt.CAP_RO, dt.CAP_Z0),
                   (dt.CAP_RO, dt.CAP_ZS), (dt.BOSS_D / 2, dt.CAP_ZF), (4.0, dt.CAP_ZF)])
    disc = U([plate, cyl(dt.BOSS_D, dt.CAP_ZF - 0.2, DISC_Z0 + 0.5), cap])
    key_slot = box(-(dt.HEX_KEY_W + 0.3) / 2, (dt.HEX_KEY_W + 0.3) / 2, 0, dt.POCKET_AF / 2 + dt.HEX_KEY_H + 0.15,
                   dt.BOSS_Z0 - 0.5, POCKET_TOP_Z)
    disc = D(disc, [cyl(dt.SLEEVE_BORE_D, dt.CAP_CEIL - 1, dt.BOSS_Z0),
                    hull_of((circle_pts(dt.SLEEVE_BORE_D + 2 * (dt.SLEEVE_CH + 0.5)), dt.CAP_CEIL - 0.5),
                            (circle_pts(dt.SLEEVE_BORE_D), dt.CAP_CEIL + dt.SLEEVE_CH)),
                    cyl(dt.BORE_D, dt.CAP_CEIL - 1, DISC_Z1 + 1, 48),
                    cyl(CBORE_D, CBORE_BOT, DISC_Z1 + 1, 64),
                    prism(hexagon(AGIT_HEX_AF), DISC_Z1 - AGIT_HEX_DEPTH, DISC_Z1 + 1),
                    prism(hexagon(dt.POCKET_AF), dt.BOSS_Z0 - 0.5, POCKET_TOP_Z), key_slot])
    return disc, pc


# =====================================================================================
# 2./3. PLATES
# =====================================================================================
def lip_groove(edge_angle_deg, side, z_face, up, r0, r1):
    rect = sbox(r0, side * LIP_SETBACK, r1, side * (LIP_SETBACK + LIP_W)) if side > 0 else \
        sbox(r0, side * (LIP_SETBACK + LIP_W), r1, side * LIP_SETBACK)
    rect = affinity.rotate(rect, edge_angle_deg, origin=(0, 0))
    z0, z1 = (z_face - LIP_DEPTH, z_face + 1) if up else (z_face - 1, z_face + LIP_DEPTH)
    return prism(rect, z0, z1)


def notch_cuts(r_from, z0, z1):
    return [rotz(box(r_from, r_from + 10, -(KEY_W + 2 * KEY_CLR) / 2, (KEY_W + 2 * KEY_CLR) / 2, z0, z1), a)
            for a in KEY_ANG]


def build_gate():
    g = cyl(2 * GATE_R, GATE_Z0, GATE_Z1, n=2 * SEG)
    outlet = rotz(loft_wedges(OUTLET_TOP, GATE_Z1 + 0.5, OUTLET_BOT.buffer(PL_DRAFT / PLATE_T * 0.5), GATE_Z0 - 0.5), 180)
    cuts = [outlet, cyl(GATE_HOLE_D, GATE_Z0 - 1, GATE_Z1 + 1, 96)]
    for r in CRUMB_R:
        cuts.append(D(cyl(2 * r + CRUMB_W, GATE_Z1 - CRUMB_DEPTH, GATE_Z1 + 1, 2 * SEG),
                      cyl(2 * r - CRUMB_W, GATE_Z1 - CRUMB_DEPTH - 1, GATE_Z1 + 2, 2 * SEG)))
    a0, a1 = ang_extent(OUTLET_TOP)
    rr0, rr1 = OUTLET_TOP.bounds[0] - 1.0, OUTLET_TOP.bounds[2] + 0.5
    for a, s in ((a0, -1), (a1, +1)):
        cuts.append(rotz(lip_groove(a, s, GATE_Z1, True, rr0, rr1), 180))
    cuts += notch_cuts(BOWL_R_IN - KEY_PROT_GATE - KEY_CLR, GATE_Z0 - 1, GATE_Z1 + 1)
    return D(g, cuts)


def build_window_plate():
    w = cyl(2 * WIN_R, WIN_Z0, WIN_Z1, n=2 * SEG)
    win = loft_wedges(WIN_TOP, WIN_Z1 + 0.5, WIN_BOT.buffer(PL_DRAFT / PLATE_T * 0.5), WIN_Z0 - 0.5)
    cuts = [win, cyl(WIN_HOLE_D, WIN_Z0 - 1, WIN_Z1 + 1, 96)]
    a0, a1 = ang_extent(WIN_BOT)
    rr0, rr1 = WIN_BOT.bounds[0] - 1.5, WIN_BOT.bounds[2] + 1.0
    for a, s in ((a0, -1), (a1, +1)):
        cuts.append(lip_groove(a, s, WIN_Z0, False, rr0, rr1))
    cuts += notch_cuts(BOWL_R_STEP - KEY_PROT_WIN - KEY_CLR, WIN_Z0 - 1, WIN_Z1 + 1)
    return D(w, cuts)


# =====================================================================================
# 4. CHIOCCIOLA + SCIVOLO (straight drop)
# =====================================================================================
def funnel(top_poly, z_top, x_c, r_bot, z_bot, n=N_WEDGE, eps=0.15):
    """local frame (outlet at +X): wedges of the outlet footprint lofted to Y-strips of the bottom circle"""
    lo, hi = ang_extent(top_poly)
    edges = np.linspace(lo, hi, n + 1)
    ys = np.linspace(-r_bot, r_bot, n + 1)
    circ = Point(x_c, 0).buffer(r_bot, resolution=64)
    parts = []
    for k in range(n):
        a0 = edges[k] - eps if k else lo - 30
        a1 = edges[k + 1] + eps if k < n - 1 else hi + 30
        y0 = ys[k] - 0.1 if k else -r_bot - 5
        y1 = ys[k + 1] + 0.1 if k < n - 1 else r_bot + 5
        ct = coords_of(top_poly.intersection(wedge(a0, a1)))
        cb = coords_of(circ.intersection(sbox(x_c - r_bot - 5, y0, x_c + r_bot + 5, y1)))
        if len(ct) < 3 or len(cb) < 3:
            continue
        parts.append(trimesh.convex.convex_hull(np.r_[np.c_[ct, np.full(len(ct), z_top)],
                                                      np.c_[cb, np.full(len(cb), z_bot)]]))
    return U(parts)


def radial_outline(poly, c, n=96):
    """radius of a convex outline around centre c at n angles"""
    from shapely.geometry import LineString
    out = []
    for th in np.linspace(0, 2 * np.pi, n, endpoint=False):
        ray = LineString([c, (c[0] + 400 * math.cos(th), c[1] + 400 * math.sin(th))])
        hit = ray.intersection(poly.exterior)
        pts = [hit] if hit.geom_type == 'Point' else list(getattr(hit, 'geoms', []))
        out.append(max(math.hypot(q.x - c[0], q.y - c[1]) for q in pts) if pts else 0.0)
    return np.array(out)


def ruled_solid(rings):
    """closed mesh from index-matched rings (list of (n,3) arrays, same n, top to bottom), caps triangulated"""
    n = len(rings[0])
    V = np.vstack(rings)
    F = []
    for k in range(len(rings) - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            F += [[a + i, b + i, b + j], [a + i, b + j, a + j]]
    for k, flip in ((0, False), (len(rings) - 1, True)):
        poly = Polygon(rings[k][:, :2])
        _, tri = trimesh.creation.triangulate_polygon(poly, engine='earcut')
        # earcut keeps the exterior vertex order -> indices map 1:1 onto the ring
        for t in tri:
            t = [k * n + int(i) for i in t]
            F.append(t[::-1] if flip else t)
    m = trimesh.Trimesh(V, np.array(F), process=False)
    m.fix_normals()
    if m.volume < 0:
        m.invert()
    assert m.is_volume, 'ruled solid not a volume'
    return m


def funnel_morph(top_poly, z_top, x_c, r_bot, z_bot, levels=16, n=96):
    """smooth morph from the top outline (star-shaped around its centroid) to the bottom circle (around (x_c,0)):
    centre and radius function interpolated linearly; ruled surface between index-matched rings (keeps the
    concave hub-side arc, unlike a convex-hull loft)"""
    c0 = np.array(top_poly.centroid.coords[0])
    c1 = np.array([x_c, 0.0])
    r0 = radial_outline(top_poly, c0, n)
    r1 = np.full(n, r_bot)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rings = []
    for t in np.linspace(0, 1, levels + 1):
        c = (1 - t) * c0 + t * c1
        r = (1 - t) * r0 + t * r1
        z = (1 - t) * z_top + t * z_bot
        rings.append(np.c_[c[0] + r * np.cos(th), c[1] + r * np.sin(th), np.full(n, z)])
    return ruled_solid(rings)


def funnel_strips(top_poly, z_top, x_c, r_bot, z_bot, n=N_WEDGE):
    return funnel_morph(top_poly, z_top, x_c, r_bot, z_bot)


def flare_poly(extra=0.0):
    mouth = OUTLET_BOT.buffer(MOUTH_FLARE, resolution=32)
    clip = Point(0, 0).buffer(200).difference(Point(0, 0).buffer(FLARE_R_MIN - extra, resolution=64))   # hub-side arc
    return mouth.buffer(FLARE_OUT + extra, resolution=32).intersection(clip).buffer(-1.0).buffer(1.0)


def floor_slope_min(cav, z_lo, z_hi):
    """min slope (deg from horizontal) of upward-facing cavity surfaces between z_lo and z_hi"""
    n = cav.face_normals
    zc = cav.triangles_center[:, 2]
    sel = (n[:, 2] < -1e-3) & (zc > z_lo) & (zc < z_hi) & (cav.area_faces > 0.5)   # ignore boolean slivers
    return float(np.degrees(np.arccos(np.clip(-n[sel, 2], 0, 1))).min()) if sel.any() else 90.0


def chute(z_bot):
    xc = -TUBE_X
    mouth = OUTLET_BOT.buffer(MOUTH_FLARE, resolution=32)
    flare, flare_o = flare_poly(), flare_poly(CHUTE_WALL)
    z_fl = GATE_Z0 - FLARE_H
    cav_f = U([loft_wedges(mouth, GATE_Z0 + 1.0, flare, z_fl), funnel_strips(flare, z_fl + 0.01, xc, TUBE_D / 2, z_bot)])
    out_f = U([loft_wedges(mouth.buffer(CHUTE_WALL, resolution=32), GATE_Z0, flare_o, z_fl),
               funnel_strips(flare_o, z_fl + 0.01, xc, TUBE_D / 2 + CHUTE_WALL, z_bot)])
    circ = Point(xc, 0).buffer(TUBE_D / 2, resolution=64)
    cav_t = prism(circ, TUBE_END_Z - 1, z_bot + 0.5)
    out_t = U([prism(Point(xc, 0).buffer(TUBE_D / 2 + CHUTE_WALL, resolution=64), TUBE_END_Z, z_bot + 0.5),
               prism(Point(xc, 0).buffer(COLLAR_OD / 2, resolution=96), TUBE_END_Z, COLLAR_TOP)] +
              [nub_at(xc, a) for a in NUB_ANG])
    seat = prism(Point(xc, 0).buffer(VALVE_FL_D / 2 + 0.2, resolution=96), TUBE_END_Z - 1, TUBE_END_Z + VALVE_SEAT_DEPTH)
    return tuple(rotz(m, 180) for m in (cav_f, out_f, U([cav_t, seat]), out_t))


def nub_at(xc, a):
    """retaining-ring nub on the collar outside, built around the tube axis then moved"""
    m = sector_solid(a - NUB_W_DEG / 2, a + NUB_W_DEG / 2, COLLAR_OD / 2 - 0.5, NUB_R1, TUBE_END_Z + NUB_DZ[0], TUBE_END_Z + NUB_DZ[1], 8)
    return at(m, xc, 0)


def build_valve():
    """duckbill (TPU): flange in the collar seat, bill tapering to a closed slit; built around the drop axis"""
    def rrect(w, t, r):
        return sbox(-w / 2, -t / 2, w / 2, t / 2).buffer(r, resolution=16) if t > 2 * r else sbox(-w / 2, -t / 2, w / 2, t / 2)
    zf0 = TUBE_END_Z - (VALVE_FL_T - VALVE_SEAT_DEPTH)      # flange 0.2 proud of the collar end, pressed by the ring lip
    fl = prism(Point(0, 0).buffer(VALVE_FL_D / 2, resolution=96), zf0, zf0 + VALVE_FL_T)
    d_out = TUBE_D + 2 * VALVE_WALL
    outer = hull_of((circle_pts(d_out, 96), zf0 + 0.5), (rrect(d_out, 2 * VALVE_WALL + 1.0, 1.5), zf0 - VALVE_BILL_L))
    inner = hull_of((circle_pts(TUBE_D, 96), zf0 + VALVE_FL_T + 0.5), (rrect(TUBE_D - 2.0, 1.0, 0.4), zf0 - VALVE_BILL_L + 1.0))
    slit = box(-(TUBE_D - 2.0) / 2, (TUBE_D - 2.0) / 2, -0.15, 0.15, zf0 - VALVE_BILL_L - 1, zf0 - VALVE_BILL_L + 1.5)
    v = D(U([fl, outer]), [inner, slit])
    return at(v, TUBE_X, 0)


def build_ring():
    """ghiera_valvola (orange): quarter-turn retaining ring with 3 L-slots over the collar nubs"""
    r_in = COLLAR_OD / 2 + 0.3
    RING_Z0, RING_Z1 = TUBE_END_Z + RING_DZ0, TUBE_END_Z + RING_DZ1
    NUB_Z = (TUBE_END_Z + NUB_DZ[0], TUBE_END_Z + NUB_DZ[1])
    body = U([D(cyl(2 * RING_R1, RING_Z0, RING_Z1, 96), cyl(2 * r_in, RING_Z0 - 1, RING_Z1 + 1, 96)),
              D(cyl(2 * RING_R1, RING_Z0, TUBE_END_Z - (VALVE_FL_T - VALVE_SEAT_DEPTH), 96),
                cyl(2 * RING_LIP_R0, RING_Z0 - 1, RING_Z1, 96))])
    cuts = []
    for a in NUB_ANG:
        a = a + 180.0                                        # the chute is built at +X and rotated 180
        w = NUB_W_DEG + 3.0
        cuts.append(sector_solid(a - w / 2, a + w / 2, r_in - 1, NUB_R1 + 0.3, NUB_Z[0] - 0.3, RING_Z1 + 1, 8))      # entry
        cuts.append(sector_solid(a - w / 2, a + 40.0, r_in - 1, NUB_R1 + 0.3, NUB_Z[0] - 0.3, NUB_Z[1] + 0.3, 12))  # turn
    grips = [rotz(box(RING_R1 - 0.5, RING_R1 + 2.0, -1.5, 1.5, RING_Z0, RING_Z1), a) for a in range(90, 271, 30)]   # none on the hub side
    return at(U([D(body, cuts)] + grips), TUBE_X, 0)


def build_drip():
    """gocciolatoio (TPU): cone ring stretched over the collar above the retaining ring"""
    r0 = COLLAR_OD / 2 + 0.05               # modelled at the collar OD; print the TPU ring ID 0.4 under for stretch
    DRIP_Z = TUBE_END_Z + DRIP_DZ
    m = revolve([(r0, DRIP_Z - DRIP_T), (r0, DRIP_Z), (r0 + 1.5, DRIP_Z), (DRIP_R1, DRIP_Z - (DRIP_R1 - r0 - 1.5)),
                 (DRIP_R1, DRIP_Z - (DRIP_R1 - r0 - 1.5) - DRIP_T), (r0 + 1.5, DRIP_Z - DRIP_T)][::-1])
    if not m.is_volume:
        m.invert()
    return at(m, TUBE_X, 0)


def build_lips():
    """TPU lip strips: anchor 2.9 x 1.5 in the groove + 0.8 flap to the disc face (contact by design)"""
    lips = {}
    for nm, poly, z_face, up, (rr0, rr1), rot in (('labbro_uscita', OUTLET_TOP, GATE_Z1, True, (OUTLET_TOP.bounds[0] - 1.0, OUTLET_TOP.bounds[2] + 0.5), 180),
                                                  ('labbro_finestra', WIN_BOT, WIN_Z0, False, (WIN_BOT.bounds[0] - 1.5, WIN_BOT.bounds[2] + 1.0), 0)):
        a0, a1 = ang_extent(poly)
        for i, (a, sd) in enumerate(((a0, -1), (a1, +1))):
            g = lip_groove(a, sd, z_face, up, rr0, rr1)
            b = g.bounds
            z0, z1 = (z_face - LIP_DEPTH + 0.05, z_face + GAP - 0.05) if up else (z_face - GAP + 0.05, z_face + LIP_DEPTH - 0.05)
            rect = (sbox(rr0, sd * LIP_SETBACK + 0.05, rr1, sd * (LIP_SETBACK + LIP_W) - 0.05) if sd > 0 else
                    sbox(rr0, sd * (LIP_SETBACK + LIP_W) + 0.05, rr1, sd * LIP_SETBACK - 0.05))
            rect = affinity.rotate(rect, a, origin=(0, 0))
            lips[f'{nm}_{i+1}'] = rotz(prism(rect, z0, z1), rot)
    return lips


def central_cavity():
    """labyrinth cap / collar / sleeve zone free by >= 1 mm"""
    rc = dt.CAP_RO + 1.0
    rs = dt.BOSS_D / 2 + 1.0
    k = dt.CAP_RO + 1.0 * math.sqrt(2)
    zA = dt.CAP_ZS + (k - rc)
    zB = dt.CAP_ZS + (k - rs)
    z0 = dt.CAP_Z0 - FLOOR_RECESS - 0.5
    return revolve([(0, z0), (rc, z0), (rc, zA), (rs, zB), (rs, GATE_Z0 + 1), (0, GATE_Z0 + 1)])


def lug(ang_c, width):
    """bayonet lug: underside ramp (thin at the leading edge in LOCK direction... the lug enters the hook with
    its THIN end first: the thin end is on the +angle side) then flat; top at LUG_Z1"""
    a0, a1 = ang_c - width / 2, ang_c + width / 2          # +angle side = leading in the +LOCK_ROT rotation
    a_ramp = a1 - LUG_RAMP_DEG
    parts = []
    n = 12
    for aa, ab in zip(np.linspace(a_ramp, a1, n + 1)[:-1], np.linspace(a_ramp, a1, n + 1)[1:]):
        ta = LUG_T_LEAD + (LUG_T_FLAT - LUG_T_LEAD) * (a1 - aa) / LUG_RAMP_DEG
        tb = LUG_T_LEAD + (LUG_T_FLAT - LUG_T_LEAD) * (a1 - ab) / LUG_RAMP_DEG
        P = []
        for a, t in ((aa - 0.05, ta), (ab + 0.05, tb)):
            for r in (BOWL_R_OUT - 0.5, LUG_R1):
                P += [[r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), LUG_Z1],
                      [r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), LUG_Z1 - t]]
        parts.append(trimesh.convex.convex_hull(np.array(P)))
    parts.append(sector_solid(a0, a_ramp + 0.05, BOWL_R_OUT - 0.5, LUG_R1, LUG_Z1 - LUG_T_FLAT, LUG_Z1))
    return U(parts)


def latch_slot_cuts():
    """T-slot for linguetta_sicura in the outer wall, open at the bottom (z=0), closed at the top"""
    r_neck0 = BOWL_R_OUT - 2.2
    c = [box(r_neck0, BOWL_R_OUT + 1, -(LATCH_W + 2 * SLOT_CLR) / 2, (LATCH_W + 2 * SLOT_CLR) / 2, -1, TAB_Z1 + 0.5),
         box(r_neck0 - LATCH_FOOT_T - 0.2, r_neck0 + 0.01, -(LATCH_FOOT_W + 2 * SLOT_CLR) / 2,
             (LATCH_FOOT_W + 2 * SLOT_CLR) / 2, -1, RAIL_Z1 + 1.0),
         box(POCKET_R0, BOWL_R_OUT + 1, -(LATCH_W + 2 * SLOT_CLR) / 2, (LATCH_W + 2 * SLOT_CLR) / 2, TAB_Z0, TAB_Z1 + 0.5)]
    return [rotz(m, LATCH_ANG) for m in c]


def build_latch():
    """orange: T-rail z 0..RAIL_Z1, spring tab above with the nub; built at angle 0 then rotated"""
    r_neck0 = BOWL_R_OUT - 2.2
    rail = U([box(r_neck0 - SLOT_CLR - 0.01, BOWL_R_OUT - 0.3, -LATCH_W / 2, LATCH_W / 2, 0.0, RAIL_Z1),
              box(r_neck0 - LATCH_FOOT_T, r_neck0 - SLOT_CLR, -LATCH_FOOT_W / 2, LATCH_FOOT_W / 2, 0.0, RAIL_Z1)])
    tab = box(BOWL_R_OUT - 0.3 - LATCH_T, BOWL_R_OUT - 0.3, -LATCH_W / 2, LATCH_W / 2, RAIL_Z1 - 0.01, TAB_Z1)
    # nub: 1.5 proud, 45 deg chamfer on the +angle face (leading face when the bowl is rotated to lock)
    nub = trimesh.convex.convex_hull(np.array(
        [[BOWL_R_OUT - 0.4, -LATCH_W / 2, NUB_Z0], [BOWL_R_OUT - 0.4, LATCH_W / 2, NUB_Z0],
         [BOWL_R_OUT - 0.4, -LATCH_W / 2, NUB_Z1], [BOWL_R_OUT - 0.4, LATCH_W / 2, NUB_Z1],
         [BOWL_R_OUT + NUB_H, -LATCH_W / 2, NUB_Z0], [BOWL_R_OUT + NUB_H, -LATCH_W / 2, NUB_Z1],
         [BOWL_R_OUT + NUB_H, LATCH_W / 2 - NUB_H, NUB_Z0], [BOWL_R_OUT + NUB_H, LATCH_W / 2 - NUB_H, NUB_Z1]]))
    return rotz(U([rail, tab, nub]), LATCH_ANG)


def build_gasket():
    return D(cyl(2 * GSK_R1 - 0.3, RIM_Z - GSK_DEPTH, RIM_Z - GSK_DEPTH + GSK_H, 2 * SEG),
             cyl(2 * GSK_R0 + 0.3, RIM_Z - GSK_DEPTH - 1, RIM_Z + 5, 2 * SEG))


def build_bowl(z_bot):
    cav_f, out_f, cav_t, out_t = chute(z_bot)
    body = cyl(2 * BOWL_R_OUT, BASE_Z0, RIM_Z, n=2 * SEG)
    lugs = [lug(a, w) for a, w in zip(LUG_ANG, LUG_W)]
    tongue = D(cyl(2 * TONGUE_R1, RIM_Z - 0.5, RIM_Z + TONGUE_H, 2 * SEG), cyl(2 * TONGUE_R0, RIM_Z - 1, RIM_Z + 3, 2 * SEG))
    bowl = U([body, out_f, out_t, tongue] + lugs)
    cav = [cyl(2 * BOWL_R_IN, GATE_Z0, WIN_Z0 + 0.01, n=2 * SEG), cyl(2 * BOWL_R_STEP, WIN_Z0, RIM_Z + 5, n=2 * SEG),
           central_cavity(), cav_f, cav_t, cyl(BASE_HOLE_D, BASE_Z0 - 1, BASE_Z1 + 1, 96),
           D(cyl(2 * GSK_R1, RIM_Z - GSK_DEPTH, RIM_Z + 1, 2 * SEG), cyl(2 * GSK_R0, RIM_Z - GSK_DEPTH - 1, RIM_Z + 2, 2 * SEG))]
    cav += latch_slot_cuts()
    bowl = D(bowl, cav)
    ribs = []
    for a in KEY_ANG:
        ribs.append(rotz(box(BOWL_R_IN - KEY_PROT_GATE, BOWL_R_IN + 0.5, -KEY_W / 2, KEY_W / 2, GATE_Z0, WIN_Z0), a))
        ribs.append(rotz(box(BOWL_R_STEP - KEY_PROT_WIN, BOWL_R_STEP + 0.5, -KEY_W / 2, KEY_W / 2, WIN_Z0, RIM_Z - GSK_DEPTH - 0.5), a))
    bowl = U([bowl] + ribs)
    return bowl, U([cav_f, cav_t]), [out_f, out_t]


def funnel_cavity(z_bot):
    """cavity only (cheap) for the depth search"""
    return funnel_strips(flare_poly(), GATE_Z0 - FLARE_H, -TUBE_X, TUBE_D / 2, z_bot, n=24)


def pick_z_bot():
    """highest funnel bottom (shortest funnel) giving >= CHUTE_SLOPE_MIN on every kibble-bearing face;
    start from the analytic estimate for the hub-side wall (flare inner arc -> tube near edge)"""
    z_fl = GATE_Z0 - FLARE_H
    run = (-TUBE_X - TUBE_D / 2) - FLARE_R_MIN
    z_est = z_fl - run / math.tan(math.radians(CHUTE_SLOPE_MIN))
    for zb in np.arange(math.floor(z_est) + 2.0, -20.0, -0.5):
        s = floor_slope_min(funnel_cavity(zb), zb + 0.05, z_fl - 0.05)
        if s >= CHUTE_SLOPE_MIN:
            return float(zb), s
    raise RuntimeError('no funnel depth found')


# =====================================================================================
# COLOUR / LABEL / EXPORT HELPERS
# =====================================================================================
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
FONT = FontProperties(family='DejaVu Sans', weight='bold')


def text_poly(s, h, cx, cy, rot=0.0):
    tp = TextPath((0, 0), s, size=h, prop=FONT)
    g = Polygon()
    for ring in tp.to_polygons():
        if len(ring) >= 3:
            g = g.symmetric_difference(Polygon(ring).buffer(0))
    b = g.bounds
    g = affinity.translate(g, cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)
    return affinity.rotate(g, rot, origin=(cx, cy)) if rot else g


def face_region(poly, z_face, top):
    z0, z1 = (z_face - INLAY, z_face + 1.0) if top else (z_face - 1.0, z_face + INLAY)
    poly = poly.buffer(0.02, resolution=4).buffer(-0.02, resolution=4).simplify(0.01)
    geoms = [poly] if isinstance(poly, Polygon) else [g for g in poly.geoms if isinstance(g, Polygon)]
    ms = []
    for g in geoms:
        if g.area < 0.05:
            continue
        m = prism(g, z0, z1)
        if not m.is_volume:
            m.fix_normals()
        ms.append(m)
    return U(ms)


def split(part, region):
    return D(part, region), I(part, region)


def overhang(p, lim_deg=45.0):
    nz = p.face_normals[:, 2]
    zmin = p.triangles[:, :, 2].min(axis=1)
    sel = (nz < -math.sin(math.radians(lim_deg + 1.0))) & (zmin > 0.05)
    return float(p.area_faces[sel].sum())


def to_print(m, flip, dz=None):
    p = m.copy()
    if flip:
        p.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    p.apply_translation([0, 0, -p.bounds[0, 2] if dz is None else dz])
    return p


def grams(m, rho=PETG):
    V, A = abs(m.volume) / 1000, m.area / 1000
    shell = min(V, A * 1.0)
    return round(V * rho, 1), round((shell + 0.15 * (V - shell)) * rho, 1)


def passage(cav, p0, p1, n=20):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    out = []
    for t in np.linspace(0.05, 0.95, n):
        o = p0 + t * (p1 - p0)
        sec = cav.section(plane_origin=o, plane_normal=d)
        if sec is None:
            continue
        p2, T = sec.to_2D()
        o2 = trimesh.transform_points([o], np.linalg.inv(T))[0][:2]
        polys = [q for q in p2.polygons_full if q.buffer(1.0).contains(Point(o2))] or list(p2.polygons_full)
        if polys:
            out.append((round(float(t), 2), round(2 * shapely.maximum_inscribed_circle(polys[0], 0.2).length, 1)))
    return out


if __name__ == '__main__':
    print('\n--- chute depth ---')
    Z_BOT, SLOPE = pick_z_bot()
    TUBE_END_Z = Z_BOT - COLLAR_L
    print(f'funnel bottom z={Z_BOT}, min kibble-face slope {SLOPE:.1f} deg, drop axis x={TUBE_X}, tube Ø{TUBE_D}')
    bowl, chute_cav, chute_out = build_bowl(Z_BOT)
    gate = build_gate()
    disc, pc = build_disc()
    win = build_window_plate()
    latch = build_latch()
    gasket = build_gasket()
    valve, ring_v, drip = build_valve(), build_ring(), build_drip()
    lips = build_lips()

    # ---------------- colour bodies ----------------
    big = 400
    bowl_green = I(bowl, box(-big, big, -big, big, -big, GATE_Z0))        # funnel + tube below the gate seat
    bowl_black = I(bowl, box(-big, big, -big, big, GATE_Z0, big))
    pocket_v = vol(I(pc, cyl(DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG))) / 1000
    portion = pocket_v * BULK_DENSITY
    # disc top (bed face when printed flipped): black text + two black rings leaving an ORANGE RING round the screw
    disc_label = text_poly(f'{VARIANT} · ~{portion:.0f} g · {VER}', 5.5, 0, 36).union(
        text_poly(f'M3x{SCREW_LEN}', 3.2, 0, -14.5))
    ring = lambda r0, r1: Point(0, 0).buffer(r1, resolution=64).difference(Point(0, 0).buffer(r0, resolution=64))
    disc_black_rg = disc_label.union(ring(AGIT_HEX_AF / math.sqrt(3) + 0.6, AGIT_HEX_AF / math.sqrt(3) + 1.4)).union(ring(10.6, 11.4))
    disc_orange, disc_black = split(disc, face_region(disc_black_rg, DISC_Z1, True))
    win_band = WIN_TOP.buffer(RIM_BAND, resolution=32).difference(WIN_TOP)
    win_text = text_poly('FOOD IN →', 6, -30, 0).union(text_poly(VER, 4, -30, -9))
    win_black, win_green = split(win, face_region(win_band.union(win_text), WIN_Z1, True))
    out_band = affinity.rotate(OUTLET_TOP.buffer(RIM_BAND, resolution=32).difference(OUTLET_TOP), 180, origin=(0, 0)
                               ).intersection(Point(0, 0).buffer(GATE_R - 0.8))
    gate_text = text_poly('← OUT', 6, 30, 0).union(text_poly(VER, 4, 30, -9))
    gate_black, gate_green = split(gate, face_region(out_band.union(gate_text), GATE_Z1, True))
    # bowl top layers when printed upright = rim top: black "LOCK ->" arrow? the rim top is the gasket face: keep clean.

    NAMES = {'chiocciola_scivolo': f'chiocciola_scivolo_{VER}', 'piastra_gate': f'piastra_gate_{VER}',
             'piastra_finestra': f'piastra_finestra_{VER}', 'disco': f'disco_{VER}',
             'linguetta': 'linguetta_sicura', 'guarnizione': 'guarnizione_baionetta'}
    BODIES = {NAMES['chiocciola_scivolo']: (bowl, [('black', bowl_black), ('green', bowl_green)], False),
              NAMES['piastra_gate']: (gate, [('black', gate_black), ('green', gate_green)], False),
              NAMES['piastra_finestra']: (win, [('black', win_black), ('green', win_green)], True),
              NAMES['disco']: (disc, [('orange', disc_orange), ('black', disc_black)], True),
              NAMES['linguetta']: (latch, [('orange', latch)], False),
              NAMES['guarnizione']: (gasket, [('yellow', gasket)], False),
              'valvola_becco': (valve, [('yellow', valve)], True),
              'ghiera_valvola': (ring_v, [('orange', ring_v)], False),
              'gocciolatoio': (drip, [('yellow', drip)], False)}
    for k, m in lips.items():
        BODIES[k] = (m, [('yellow', m)], False)
    PRINT_TXT = {
        NAMES['chiocciola_scivolo']: 'upright as assembled on the chute collar end (z=-10): green funnel+tube first, one '
                                     'colour change at z=28.2 (gate seat), black above; supports: bed-only under the base '
                                     'plate (10 mm high) and under the 3 lugs',
        NAMES['piastra_gate']: 'as assembled, bottom face on the bed; OUT band + labels in the top 3 layers',
        NAMES['piastra_finestra']: 'flipped, top face on the bed (window band + FOOD IN in the first 3 layers)',
        NAMES['disco']: 'flipped, disc top on the bed (black label + rings in the first 3 layers), sleeve + cap up',
        NAMES['linguetta']: 'lying on its back (T-foot face down); 100% infill, 4 walls; tab 1.4 mm = 3-4 perimeters',
        NAMES['guarnizione']: 'flat ring, TPU 95A, 100% infill',
        'valvola_becco': 'flipped: flange on the bed, bill pointing up (walls lean inward, no supports); TPU 95A, 2 walls, 0.2 layers, slow',
        'ghiera_valvola': 'as assembled, lip face on the bed; PETG orange',
        'gocciolatoio': 'as assembled, inner collar face on the bed, 45 deg cone; TPU 95A',
        'labbro_uscita_1': 'flat on its wide face; TPU 95A', 'labbro_uscita_2': 'flat on its wide face; TPU 95A',
        'labbro_finestra_1': 'flat on its wide face; TPU 95A', 'labbro_finestra_2': 'flat on its wide face; TPU 95A'}
    print('\n--- meshes ---')
    PR, OVH, GR = {}, {}, {}
    for name, (m, bodies, flip) in BODIES.items():
        report(name, m)
        for c, b in bodies:
            report(f'  {name}[{c}]', b)
        m.export(OUT + f'{name}.stl')
        m.export(OUT + f'{name}.3mf')
        pm = to_print(m, flip)
        ref = m.copy()
        if flip:
            ref.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
        tz = -ref.bounds[0, 2]
        sc = trimesh.Scene()
        for c, b in bodies:
            pb = to_print(b, flip, dz=tz)
            if len(bodies) > 1:
                pb.export(OUT + f'{name}_print_{c}.stl')
            sc.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
        sc.export(OUT + f'{name}_print.3mf')
        pm.export(OUT + f'{name}_print.stl')
        PR[name], OVH[name] = pm, round(overhang(pm), 1)
        GR[name] = grams(m, 1.21 if bodies[0][0] == 'yellow' else PETG)
    print('down-facing area flatter than 45 deg in print orientation (mm2):', OVH)
    print('grams (solid, est.):', GR)

    # ---------------- interference ----------------
    print('\n--- interference (mm3) ---')
    screw = U([cyl(3.0, SCREW_TIP_Z, CBORE_BOT, 32), cyl(dt.SCREW_HEAD_D, CBORE_BOT, CBORE_BOT + dt.SCREW_HEAD_H, 48)])
    Tz = np.eye(4); Tz[2, 3] = dt.LID_T / 2
    sec = U(chute_out).section(plane_origin=[0, 0, -dt.LID_T / 2], plane_normal=[0, 0, 1]).to_2D(to_2D=Tz)[0]
    ROOF_CUT = shapely.unary_union(list(sec.polygons_full)).buffer(2.0, resolution=16)
    ROOF_CUT = ROOF_CUT if isinstance(ROOF_CUT, Polygon) else max(ROOF_CUT.geoms, key=lambda g: g.area)
    roof = D(box(-110, 70, -70, 70, -dt.LID_T, 0), [cyl(dt.LID_HOLE_D, -5, 1), prism(ROOF_CUT, -5, 1)])   # roof stand-in
    ALL = {f'disco@0': disc, f'disco@180': rotz(disc, 180), 'piastra_gate': gate, 'piastra_finestra': win,
           'chiocciola': bowl, 'linguetta': latch, 'guarnizione': gasket, 'valvola_becco': valve, 'ghiera_valvola': ring_v,
           'gocciolatoio': drip, 'albero_mozzo': dt.albero, 'albero_mozzo@180': rotz(dt.albero, 180),
           'passante_culla': dt.culla, 'servo': dt.servo_solid, f'screw_M3x{SCREW_LEN}': screw, 'roof_plate': roof}
    CTX = {'servo', 'albero_mozzo', 'albero_mozzo@180', 'passante_culla', 'roof_plate'}
    SKIP = {('disco@0', 'albero_mozzo@180'), ('disco@180', 'albero_mozzo')}     # the shaft turns with the keyed disc
    names = list(ALL)
    inter = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a in CTX and b in CTX) or {a, b} == {'disco@0', 'disco@180'} or (a, b) in SKIP:
                continue
            inter[f'{a}|{b}'] = round(vol(I(ALL[a], ALL[b])), 4)
    WORST = max(inter.values())
    for k, v in inter.items():
        if v > 1e-3:
            print(f'  {k:45s} {v:.4f}')
    print(f'{len(inter)} pairs, max {WORST:.4f} mm3')
    LIPS = {k: {'vs_plate': round(vol(I(m, gate if 'uscita' in k else win)), 3),
                'vs_disc_contact_by_design': round(vol(I(m, disc)), 3), 'vs_bowl': round(vol(I(m, bowl)), 3)} for k, m in lips.items()}
    print('lips:', LIPS)

    # ---------------- other checks ----------------
    mouth_c = OUTLET_BOT.centroid
    PASS = passage(chute_cav, [-mouth_c.x, 0, GATE_Z0 - 0.3], [TUBE_X, 0, Z_BOT + 0.5])
    pmin = min(v for _, v in PASS)
    THROAT = round(2 * shapely.maximum_inscribed_circle(OUTLET_BOT, 0.1).length, 1)
    # horizontal sections of the funnel (what a falling kibble sees)
    HSEC = []
    for z in np.linspace(GATE_Z0 - 0.5, Z_BOT + 1.0, 12):
        s = chute_cav.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        p2, _ = s.to_2D()
        HSEC.append((round(float(z), 1), round(2 * max(shapely.maximum_inscribed_circle(q, 0.2).length for q in p2.polygons_full), 1)))
    print(f'passage: gate outlet (inscribed) {THROAT} mm; funnel perpendicular min {pmin} mm; tube {TUBE_D} mm (target {PASSAGE_MIN})')
    print('  horizontal sections (z, inscribed d):', HSEC)
    c9 = 0.95
    cap_env = revolve([(0, dt.CAP_Z0 - c9), (dt.CAP_RO + c9, dt.CAP_Z0 - c9), (dt.CAP_RO + c9, dt.CAP_ZS),
                       (dt.BOSS_D / 2 + c9, dt.CAP_ZF + 0.4), (dt.BOSS_D / 2 + c9, GATE_Z0 - 0.01), (0, GATE_Z0 - 0.01)])
    if not cap_env.is_volume:
        cap_env.invert()
    CAP_CLEAR = round(vol(I(bowl, cap_env)), 4)
    COLLAR_CLEAR = round(vol(I(bowl, cyl(dt.COLLAR_D + 2 * c9, -1, dt.COLLAR_Z1 + c9))), 4)
    TUBE_TO_CAP = round(-TUBE_D / 2 - TUBE_X - CHUTE_WALL - (dt.CAP_RO + 1.0), 2)
    FUNNEL_SLOPE = round(floor_slope_min(chute_cav, Z_BOT + 0.05, GATE_Z0 - 0.05), 1)
    WT = {n: bool(m.is_watertight) for n, (m, _, _) in BODIES.items()}
    # latch flex: deflection needed vs strain
    L_tab = TAB_Z1 - RAIL_Z1
    defl = NUB_H + 0.3
    strain = 3 * defl * (LATCH_T / 2) / L_tab ** 2
    print(f'cap zone +1: {CAP_CLEAR} mm3; collar +1: {COLLAR_CLEAR} mm3; tube wall -> cap zone {TUBE_TO_CAP} mm; '
          f'latch strain {strain*100:.2f}% at {defl} mm deflection')
    print('watertight:', WT)

    # bayonet spec for the flange (flangia_piano)
    lock_pos = [a + LOCK_ROT for a in LUG_ANG]
    hooks = [[round(a - w / 2 - 1.0, 1), round(a + w / 2 + 1.0, 1)] for a, w in zip(lock_pos, LUG_W)]
    BAYONET = {
        'frame': 'same axis frame as the bowl (Z up, X=Y=0 shaft axis), angles CCW from +X seen from above; '
                 'flange angles == bowl angles at insertion; bowl rotates +LOCK_ROT to lock',
        'bowl_outer_d': 2 * BOWL_R_OUT, 'rim_top_z': RIM_Z,
        'gasket': {'groove_r': [GSK_R0, GSK_R1], 'groove_depth': GSK_DEPTH, 'tpu_ring_h': GSK_H,
                   'proud_uncompressed': round(GSK_H - GSK_DEPTH, 2), 'compression_at_lock': round(LIFT - 0.5, 2),
                   'flange_underside_z_locked': round(RIM_Z + (GSK_H - GSK_DEPTH) - (LIFT - 0.5), 2),
                   'flange_underside_z_at_insertion': round(RIM_Z + (GSK_H - GSK_DEPTH) - (LIFT - 0.5) + LIFT, 2),
                   'note': 'flange underside flat and smooth inside r 60.5..62 (gasket contact), rim hard-stops 0.1 under it'},
        'lugs': {'n': 3, 'insert_angles_deg': list(LUG_ANG), 'widths_deg': list(LUG_W), 'key': '180 deg lug is 32 wide (one way)',
                 'r': [BOWL_R_OUT, LUG_R1], 'top_z': LUG_Z1, 'thickness_leading_edge': LUG_T_LEAD, 'thickness_flat': LUG_T_FLAT,
                 'ramp_deg': LUG_RAMP_DEG, 'ramp_on': 'lug UNDERSIDE (thin end = +angle side): the flange hook is FLAT',
                 'lift_mm': LIFT},
        'lock_rotation_deg': LOCK_ROT, 'locked_lug_centres_deg': lock_pos,
        'flange_hooks': {'n': 3, 'angle_spans_deg': hooks, 'inner_r': BOWL_R_OUT + 0.5, 'outer_r_min': LUG_R1 + 0.5,
                         'top_face_z_bowl_frame_locked': round(LUG_Z1 - LUG_T_FLAT, 2),
                         'top_face_below_flange_underside': round(RIM_Z + (GSK_H - GSK_DEPTH) - (LIFT - 0.5) - (LUG_Z1 - LUG_T_FLAT), 2),
                         'thickness_min': 3.0, 'skirt': 'between hooks leave the full gap (slots) for lug insertion; '
                         'skirt may be a full ring at r > %.1f' % (LUG_R1 + 0.5)},
        'safety_latch': {'part': NAMES['linguetta'], 'bowl_angle_deg': LATCH_ANG, 'nub_r': [BOWL_R_OUT, BOWL_R_OUT + NUB_H],
                         'nub_z': [NUB_Z0, NUB_Z1], 'engages': 'the trailing end face of the hook at %.1f deg (flange) after the +%.0f deg lock '
                         'rotation; press the orange tab inward (%.1f mm) to release' % (hooks[0][1], LOCK_ROT, NUB_H),
                         'hook_end_face_must_be_flat_between_z': [NUB_Z0 - 0.5, NUB_Z1 + 0.5]},
        'chute_drop_zone': {'axis_xy': [TUBE_X, 0.0], 'outer_d': TUBE_D + 2 * CHUTE_WALL, 'collar_bottom_z': TUBE_END_Z,
                            'keep_clear': 'cylinder Ø%.0f around (%.0f, 0) from z=%.0f downward + the falling kibble below; ghiera OD %.0f' %
                                          (COLLAR_OD + 4, TUBE_X, 0, 2 * RING_R1 + 4)},
        'roof_cutout_for_chute': {'z': [-dt.LID_T, 0], 'polygon_xy_axis_frame': [[round(x, 1), round(y, 1)] for x, y in ROOF_CUT.exterior.coords[::4]],
                                  'bounds': [round(v, 1) for v in ROOF_CUT.bounds], 'note': 'chute outer section at the roof plane + 2 mm'},
        'base_underside': 'flat at z=0 inside r 62 except the chute tube (x %.0f..%.0f) ; centre hole Ø%.1f centres on the '
                          'passante collar; NO screws in the bowl base (v4b)' % (TUBE_X - TUBE_D / 2 - CHUTE_WALL,
                                                                                  TUBE_X + TUBE_D / 2 + CHUTE_WALL, BASE_HOLE_D)}

    # ---------------- section render ----------------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly, Rectangle
    DRAW = [('roof plate (stand-in)', roof, '#D8D8D8', '#808080', '///'), ('servo', dt.servo_solid, '#8FB3E0', '#2F5D8A', None),
            ('passante_culla', dt.culla, '#555555', 'k', None), ('albero_mozzo', dt.albero, '#9A9A9A', 'k', None),
            ('chiocciola black', bowl_black, '#2B2B2B', 'k', None), ('chiocciola green', bowl_green, '#2E9E4F', 'k', None),
            ('piastra_gate', gate, '#6B6B6B', 'k', None), ('piastra_finestra', win, '#6B6B6B', 'k', None),
            ('disco', disc, '#E8792B', 'k', None), ('linguetta', latch, '#E8792B', '#7A3A00', None),
            ('guarnizione', gasket, '#E8D44D', '#7A6A00', None), ('TPU valve/drip/lips', U([valve, drip] + list(lips.values())), '#E8D44D', '#7A6A00', None),
            ('ghiera_valvola', ring_v, '#E8792B', '#7A3A00', None), ('screw', screw, '#C9A227', '#6B5410', None)]

    def draw(ax, origin, normal, T, title, xlim, ylim, xl, yl):
        for nm, m, fc, ec, hatch in DRAW:
            sct = m.section(plane_origin=origin, plane_normal=normal)
            if sct is None:
                continue
            p2, _ = sct.to_2D(to_2D=T)
            for poly in p2.polygons_full:
                ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=fc, ec=ec, lw=0.5, hatch=hatch,
                                   alpha=0.95 if hatch is None else 0.6, zorder=3 if hatch is None else 1))
                for h in poly.interiors:
                    ax.add_patch(MPoly(np.array(h.coords), closed=True, fc='white', ec=ec, lw=0.5, zorder=4 if hatch is None else 2))
        ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=0.25)
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title, fontsize=10)

    fig, axs = plt.subplots(1, 3, figsize=(26, 9), facecolor='white', gridspec_kw={'width_ratios': [1.3, 1, 1]})
    Txz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
    Tyz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    draw(axs[0], [0, 0, 0], [0, 1, 0], Txz, f'Section Y=0 (XZ) {VER}: disc, plates, bowl, straight chute, lugs (180 key lug at left)',
         (-95, 75), (-65, 72), 'X [mm]', 'Z [mm]')
    axs[0].text(-73, 69, f'min kibble-face slope {FUNNEL_SLOPE} deg; funnel min passage {pmin}; tube Ø{TUBE_D}; M3x{SCREW_LEN}', fontsize=8)
    draw(axs[1], [TUBE_X, 0, 0], [1, 0, 0], Tyz, f'Section X={TUBE_X} (YZ) through the drop axis: funnel y-walls, valve, ring', (-70, 70), (-40, 70), 'Y [mm]', 'Z [mm]')
    a = math.radians(LATCH_ANG)
    Tl = trimesh.transformations.rotation_matrix(-a, [0, 0, 1])
    Tl = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float) @ Tl
    draw(axs[2], [0, 0, 0], [-math.sin(a), math.cos(a), 0], Tl, f'Radial section at {LATCH_ANG} deg: latch T-slot, tab, nub, rim gasket', (45, 70), (-2, 70), 'r [mm]', 'Z [mm]')
    handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3]) for d in DRAW]
    axs[0].legend(handles, [d[0] for d in DRAW], loc='lower right', fontsize=7)
    plt.tight_layout()
    plt.savefig(OUT + 'check_dosing.png', dpi=90)
    plt.close(fig)

    # ---------------- JSON ----------------
    doc = {
        'version': VER, 'frame': 'Z-up mm, Z=0 = bowl base underside (enclosure roof top), X=Y=0 = shaft axis',
        'architecture': 'hangs under a level shelf by a quarter-turn bayonet (flangia_piano by the other engineer); '
                        'straight-drop chute; no screws in the bowl; passante_culla is screwed to the enclosure roof',
        'parameters': {'KIBBLE_MAX': KIBBLE_MAX, 'PASSAGE_MIN': PASSAGE_MIN, 'VARIANT': VARIANT, 'PLATES_FOR': PLATES_FOR,
                       'DISC_T': DISC_T, 'DISC_Z': [DISC_Z0, DISC_Z1], 'GAP': GAP, 'GATE_Z': [GATE_Z0, GATE_Z1],
                       'WIN_Z': [WIN_Z0, WIN_Z1], 'BOWL_R_IN': BOWL_R_IN, 'BOWL_R_STEP': BOWL_R_STEP, 'BOWL_R_OUT': BOWL_R_OUT,
                       'RIM_Z': RIM_Z, 'TUBE_D': TUBE_D, 'TUBE_X': TUBE_X, 'TUBE_END_Z': TUBE_END_Z, 'COLLAR_OD': COLLAR_OD, 'Z_FUNNEL_BOTTOM': Z_BOT,
                       'KEY_ANG_plates': list(KEY_ANG), 'hex_key': f'{dt.HEX_KEY_W}x{dt.HEX_KEY_H} rib on the +Y flat of albero_mozzo',
                       'pockets': {v: {'r_in': POCKETS[v][0], 'r_out': POCKETS[v][1], 'angle_deg': POCKET_ANG[v],
                                       'target_cm3': POCKETS[v][2]} for v in POCKETS}},
        'pocket': {'variant': VARIANT, 'volume_cm3_each': round(pocket_v, 2),
                   'portion_g_per_180deg_move_at_400gL': round(portion, 2),
                   'range_g_330_450gL': [round(pocket_v * 0.33, 1), round(pocket_v * 0.45, 1)],
                   'draft_deg': POCKET_DRAFT_DEG, 'corner_r': POCKET_CORNER_R, 'top_edge_break': POCKET_TOP_CH},
        'screw': {'spec': f'M3x{SCREW_LEN} DIN912 (ISO 4762) A2', 'head_z': [CBORE_BOT, CBORE_BOT + dt.SCREW_HEAD_H],
                  'tip_z': SCREW_TIP_Z, 'tip_below_spline_tip': round(dt.SPLINE_TIP_Z - SCREW_TIP_Z, 2),
                  'solid_under_head': round(CBORE_BOT - POCKET_TOP_Z, 2), 'label': 'orange ring between two black rings on the disc top + "M3x%d"' % SCREW_LEN},
        'bayonet': BAYONET,
        'tpu_parts': [{'part': k, 'shore': '95A', 'print': PRINT_TXT[k], 'grams': GR[k][0]} for k in BODIES if BODIES[k][1][0][0] == 'yellow'],
        'weather_sealing': {'bayonet_labyrinth': 'rim tongue r %.1f..%.1f, %.1f high above the rim top -> flange groove r %.1f..%.1f, %.1f deep: '
                            'water must go up over the tongue and down again (2 direction changes) before the TPU gasket' %
                            (TONGUE_R0, TONGUE_R1, TONGUE_H, TONGUE_R0 - 0.5, TONGUE_R1 + 0.5, TONGUE_H + 0.5),
                            'chute_outlet': 'TPU duckbill valvola_becco (closed at rest) in the collar end seat Ø%.1f x %.1f, held by ghiera_valvola '
                                            '(quarter-turn over 3 nubs at %s deg around the drop axis, z %s); TPU drip cone gocciolatoio on the collar above the ring' %
                                            (VALVE_FL_D + 0.2, VALVE_SEAT_DEPTH, [a + 180 for a in NUB_ANG], [TUBE_END_Z + d for d in NUB_DZ]),
                            'plates': 'TPU lip strips in the 4 radial grooves (contact 0..0.3 with the disc; slit the flap every 5 mm if too stiff)',
                            'lips_check': LIPS},
        'colour_language': {'black': 'structure', 'orange': 'you act here (disc, screw ring, latch)', 'green': 'food path (chute, window/outlet bands)',
                            'yellow TPU': 'soft/seal (rim gasket, lips later)'},
        'parts': {n: {'files': [f'{n}.stl', f'{n}.3mf', f'{n}_print.stl', f'{n}_print.3mf'] +
                               ([f'{n}_print_{c}.stl' for c, _ in BODIES[n][1]] if len(BODIES[n][1]) > 1 else []),
                      'colour_bodies': {c: FILAMENT[c] for c, _ in BODIES[n][1]},
                      'print': PRINT_TXT[n], 'downfacing_flatter_45_mm2': OVH[n],
                      'grams_solid': GR[n][0], 'grams_est_3walls_15pct': GR[n][1],
                      'volume_cm3': round(BODIES[n][0].volume / 1000, 2)} for n in BODIES},
        'hardware': [{'qty': 1, 'item': f'M3x{SCREW_LEN} DIN912 / ISO 4762 A2', 'use': 'disc top -> servo spline; the only screw inside'},
                     {'qty': 1, 'item': 'valvola_becco (TPU 95A)', 'use': 'duckbill in the chute collar seat'},
                     {'qty': 1, 'item': 'ghiera_valvola (PETG orange)', 'use': 'quarter-turn retaining ring over the collar nubs'},
                     {'qty': 1, 'item': 'gocciolatoio (TPU 95A)', 'use': 'drip cone on the collar above the ring'},
                     {'qty': 1, 'item': NAMES['guarnizione'] + ' (TPU 95A)', 'use': 'rim groove, compressed by the bayonet lift'},
                     {'qty': 1, 'item': NAMES['linguetta'] + ' (PETG orange)', 'use': 'slides up into the bowl wall T-slot from below'},
                     {'qty': 4, 'item': f'TPU 95A lip strips {LIP_W} mm (later)', 'use': 'window plate + gate plate grooves'},
                     {'qty': 0, 'item': 'rim ears / lid screws', 'use': 'REMOVED in v4b (bayonet + no-screw bowl)'}],
        'assembly': ['slide linguetta_sicura up into the bowl wall slot (z=0 opening); gasket into the rim groove',
                     'piastra_gate in (notches on the 90/250 ribs, one way)',
                     'disco over the shaft: keyed hex (rib on the +Y flat), M3x%d from the top into the spline' % SCREW_LEN,
                     'piastra_finestra on the step (one way), window over +X',
                     'valve: drip cone over the collar, duckbill flange into the seat, ghiera over the 3 nubs, quarter turn',
                     'offer the bowl to the flange: lugs at 60/180(key)/300 into the slots, push up, rotate +%.0f deg until the latch clicks' % LOCK_ROT,
                     'unmount: press the orange latch, rotate back, lower; everything inside is then reachable without tools'],
        'checks': {'watertight': WT, 'intersection_mm3_max': WORST, 'intersection_mm3': inter,
                   'min_kibble_face_slope_deg': FUNNEL_SLOPE,
                   'passage_mm': {'gate_outlet_inscribed': THROAT, 'funnel_perpendicular_min': pmin, 'tube': TUBE_D,
                                  'target': PASSAGE_MIN, 'funnel_sections': PASS, 'horizontal_sections': HSEC},
                   'cap_zone_1mm_vs_bowl_mm3': CAP_CLEAR, 'collar_1mm_vs_bowl_mm3': COLLAR_CLEAR,
                   'tube_wall_to_cap_zone_mm': TUBE_TO_CAP, 'latch_strain_pct': round(strain * 100, 2),
                   'pocket_window_outlet_half_angle_sum_deg': round(ANG_SUM, 1)},
        'superseded_files': ['disco_v3.* and disco_v4a.* (now disco_v4b)', 'scivolo_v1.*, w_scivolo*.stl, chiocciola_scivolo_v4a.* (now chiocciola_scivolo_v4b)',
                             'piastra_*_v4a.* (now *_v4b)', 'dosing_v4a.json / check_dosing_v4a.png (reference only)'],
        'notes': ['passante_culla still has its 3 blind inserts on the flange face: they now take screws from the enclosure roof (other engineer)',
                  'the bowl base only CENTRES on the passante collar (Ø%.1f hole); the face O-ring of the passante seals against the roof, not the bowl' % BASE_HOLE_D,
                  'print the bowl upright: supports only under the base plate ring (10 mm) and the 3 lug undersides',
                  'the latch is a separate orange part so the bowl 3MF has only ONE colour change (green->black at the gate seat)'],
    }
    json.dump(doc, open(OUT + 'dosing.json', 'w'), indent=2, default=float)
    print('wrote dosing.json')
