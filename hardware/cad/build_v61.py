#!/usr/bin/env python3
"""
Kibble Dispenser Outdoor - design iteration v6.1 ("pod").

v6 one-twist unit, now wrapped in ONE smooth claw-proof shell (guscio_v61) with a flat-bottomed cap (fondello_v61):
  shelf -> flangia_piano_v61 (round plate r 82, wood screws hidden under the shell rim, cable grommet, hooks in the
           LOCKED frame) + colletto_v6 (reused)
  unit  -> chiocciola_v61 (v6 bowl core, gaps 1.2, scissor window/outlet, low-force rim lip seal, funnel turned DOWN)
           + scivolo_v61 (green, vertical chute inside the pod, drip edge above the cap outlet)
           + piastra_gate_v61 / disco_v61 (sweeper ribs) / piastra_finestra_v61 + comb-slit TPU lips
           + colonna_v61 (v6 tower, bottom lobes moved clear of the chute) + albero_v6 + mozzo_v6 (reused, lubed for life)
           + scatola_v61 (sealed electronics box inside the pod: servo cradle, 70x50 board, M12 gland, M12 ePTFE vent)
           + guscio_v61 (shell, hangs from the bowl on 3 gusseted tabs, flush latch push-button)
           + fondello_v61 (bottom cap: outlet, D lip seal against the box, 3 flush quarter-turn thumb-turns)
Frame: Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside. All parts are drawn in the LOCKED pose
(v5/v6 drew the bowl at its insertion angle against hooks at the locked angle; fixed here).
No existing file is modified; every new file carries the suffix _v61.
"""
import json
import math
import os
import sys
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, Point, box as sbox, LineString, MultiPolygon
from shapely import affinity

import build_v6 as v6                      # v6 helpers + parameters; imports build_v5 (regenerated v4b parts in v5.R)
v5, dt, bd = v6.v5, v6.dt, v6.bd
OUT = dt.OUT
U, D, I = dt.U, dt.D, dt.I
cyl, box, at, hull_of, circle_pts, revolve, hexagon = dt.cyl, dt.box, dt.at, dt.hull_of, dt.circle_pts, dt.revolve, dt.hexagon
prism, rrect, ring2d, below, above, polar, yprism = v6.prism, v6.rrect, v6.ring2d, v6.below, v6.above, v6.polar, v6.yprism
rotz, text_poly, face_region, split, to_print, overhang, vol = bd.rotz, bd.text_poly, bd.face_region, bd.split, bd.to_print, bd.overhang, bd.vol
R5 = v5.R
bd.LUG_RAMP_DEG = 4.0          # v6.1 lugs: 4 deg lead-in ramp, then flat -> the flat bears on the hook over 16-25 deg at lock
                               # (v4b/v6: 18 deg ramp on a flat hook = 2-11 deg of real contact); possible because the rim seal is now a low-force lip
SEG = dt.SEG
VER = 'v6.1'
SFX = '_v61'
SCRATCH = OUT                                         # watertight probe exports (build/)
ASM = OUT + 'v61_asm/'
PETG, TPU = 1.27, 1.21
os.makedirs(SCRATCH, exist_ok=True)
os.makedirs(ASM, exist_ok=True)

# =====================================================================================
# PARAMETERS
# =====================================================================================
# ---- dosing core: gaps 0.8 -> 1.2 (crumbs pass), scissor edges, sweeper ribs ----
GAP = 1.2
DISC_Z0, DISC_Z1 = bd.DISC_Z0, bd.DISC_Z1            # 32 / 48 (disc unchanged in z)
PLATE_T = bd.PLATE_T
G1 = DISC_Z0 - GAP                                  # gate plate top 30.8
G0 = G1 - PLATE_T                                   # gate seat 27.8 (v6 28.2)
W0 = DISC_Z1 + GAP                                  # window plate underside 49.2 (v6 48.8)
W1 = W0 + PLATE_T                                   # 52.2
SKEW_DEG, SKEW_RM = 15.0, 31.5                      # window/outlet edges rotated 15 deg about their mid-radius point (pinwheel)
RIB_ANG, RIB_SKEW, RIB_W, RIB_H, RIB_R = (60.0, 90.0, 120.0), -30.0, 1.6, 0.6, (17.0, 50.0)   # sweeper ribs (disc underside)
# ---- TPU comb lips (plates) ----
LIPW, LIPD, LIPS = 3.0, 1.5, 1.0                    # groove width / depth / setback from the opening edge (as v4b)
ANCH_W, ANCH_H = 3.15, 1.0                          # anchor press-fit 0.15 in the 3.0 groove
FLAP_T, FLAP_LEAN, LIP_PRE = 0.8, 40.0, 0.15        # flap thickness, lean from vertical towards the opening, preload on the disc
SLIT_P, SLIT_W, SLIT_STOP = 5.0, 0.7, 1.0           # comb: slit every 5 mm, 0.7 wide, stops 1 mm above the anchor
# ---- bayonet rim lip seal (replaces the solid 2.1 x 2.5 ring compressed 1.0) ----
RG_R0, RG_R1, RG_Z0 = 56.9, 59.9, 63.8              # groove in the bowl rim (r, bottom z); rim top 66.0
RG_FOOT_T, RG_RISER = 0.6, (56.95, 57.45, 65.0)     # foot thickness; riser r0, r1, top z
RG_ROOT, RG_ANG, RG_T, RG_TIP_Z = (57.15, 64.85), 46.0, 0.45, 66.55   # flap root, angle above horizontal (>45: prints), thickness, free tip z
FLANGE_UNDERSIDE = v6.FL_Z0                         # 66.1 at lock -> lip bent 0.45
# ---- chute (vertical, inside the pod) ----
CH_X = -42.0                                        # chute axis (box -X rim flange at -16.25 -> 1.75 mm gap)
RI, T_CH = 22.0, 2.0
RO = RI + T_CH
# ---- pod (shell + cap) ----
Z_TOP = 64.0                                        # shell rim top (flange underside 66.1 at lock -> 2.1 shadow gap)
R_TOP = 82.0
Z_BOT = -104.0                                      # flat bottom of the cap
XM_F, XP_F = -67.0, 40.0                            # flat bottom from x -67 to +40 (circle centre -13.5, r 53.5)
RC, RC_P = 15.0, 17.0                               # bottom edge radius -X (capped by the outlet) / +X (owner: >= 15)
ALPHA_P = 65.0                                      # +X: bottom arc ends at 65 deg, then a convex Bezier to the rim (fitted: slimmest convex drop
                                                    #     that clears the box corners, the bowl and the flange skirt)
Z_S = -72.0                                         # seam shell | cap (horizontal); cap rim 0.6 lower
SEAM = 0.6
T_SHELL, T_CAP = 2.0, 2.0
# ---- electronics box (inside the pod) ----
BXO = (-15.25, 40.0, -41.0, 41.0)                   # outer x0, x1, y0, y1 (box -X wall = servo cradle -X wall)
BX_R, BX_T = 3.0, 2.0
Z_R = v6.Z_R                                        # -30 roof top (tower plateau)
Z_W = Z_S                                           # box wall bottom face = seam plane
BB_T = 1.6                                          # 70 x 50 perfboard standing beside the cradle, parts facing +X
# ---- shell tabs / latch push button / grommet ----
TAB_ANG, TAB_R_INS, TAB_W, TAB_T = (0.0, 120.0, 240.0), 56.0, 14.0, 6.0
LATCH_A = bd.LATCH_ANG                              # 76.5 (bowl frame = locked frame)
BTN_Z = 46.5
CABLE_ANG, CABLE_R = -40.0, 76.0                    # flange cable hole (Ø10, TPU grommet) and shelf hole Ø10 there
# ---- thumb-turns (cap) ----
TT = [(-26.0, 37.5), (-26.0, -37.5), (24.0, 0.0)]   # A, B (wet ring, no seal needed) and C (dry, O-ring 8x1.5)
TT_ARM_DIR = [0.0, 0.0, 180.0]                      # closed: arms point +X (A, B -> posts on the box -X wall) / -X (C -> cradle post)
TT_DISH_D, TT_DISH_H = 26.0, 3.5
TT_SHAFT_D, TT_FACE_D = 10.0, 18.0
TT_ARM_Z1 = -88.6                                   # arm top (closed, touching the post bottom face)
TT_ARM_T, TT_ARM_W, TT_ARM_L = 4.5, 9.0, 9.0


def report(name, m):
    print(f'{name:28s} watertight={m.is_watertight}  volume={m.volume/1000:8.3f} cm3  '
          f'x[{m.bounds[0,0]:.1f},{m.bounds[1,0]:.1f}] y[{m.bounds[0,1]:.1f},{m.bounds[1,1]:.1f}] '
          f'z[{m.bounds[0,2]:.2f},{m.bounds[1,2]:.2f}]  faces={len(m.faces)}')
    assert m.is_watertight and m.volume > 0, name


def line_strip(q, d, s0, s1, w0, w1, z0, z1):
    """prism of a strip along the 2D line q + s*d, offset w0..w1 to its left-hand normal"""
    d = np.asarray(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    q = np.asarray(q, float)
    pts = [q + s0 * d + w0 * n, q + s1 * d + w0 * n, q + s1 * d + w1 * n, q + s0 * d + w1 * n]
    return prism(Polygon(pts), z0, z1)


# =====================================================================================
# POD PROFILE (horizontal sections are circles: centre (cx(z), 0), radius R(z))
# =====================================================================================
def _bez(P0, P1, P2, P3, n=200):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3


def _profiles():
    a = np.radians(np.linspace(0, ALPHA_P, 40))
    arc_p = np.c_[XP_F + RC_P * np.sin(a), Z_BOT + RC_P - RC_P * np.cos(a)]
    e = arc_p[-1]
    tg = np.array([math.cos(math.radians(ALPHA_P)), math.sin(math.radians(ALPHA_P))])
    bz_p = _bez(e, e + 20.0 * tg, np.array([R_TOP, Z_TOP - 20.0]), np.array([R_TOP, Z_TOP]))
    xp = np.vstack([arc_p, bz_p[1:]])
    a = np.radians(np.linspace(0, 90, 40))
    arc_m = np.c_[XM_F - RC * np.sin(a), Z_BOT + RC - RC * np.cos(a)]
    e = arc_m[-1]
    bz_m = _bez(e, e + np.array([0, 60.0]), np.array([-R_TOP, Z_TOP - 60.0]), np.array([-R_TOP, Z_TOP]))
    xm = np.vstack([arc_m, bz_m[1:]])
    # extend vertically above the rim (for the inner offset) and make z strictly increasing
    xp = np.vstack([xp, [[R_TOP, Z_TOP + 8.0]]])
    xm = np.vstack([xm, [[-R_TOP, Z_TOP + 8.0]]])
    return xp, xm


XPP, XMP = _profiles()
SIL = Polygon(np.vstack([[[XM_F, Z_BOT]], XPP, XMP[::-1]]))   # XZ silhouette of the pod (closed, CCW not needed)


def _sil_x(poly, z):
    """leftmost / rightmost x of a silhouette polygon at height z"""
    ln = LineString([(-300, z), (300, z)]).intersection(poly)
    if ln.is_empty:
        return None
    xs = np.array(ln.coords if ln.geom_type == 'LineString' else [c for g in ln.geoms for c in g.coords])[:, 0]
    return xs.min(), xs.max()


def section_fn(t):
    """(x_min(z), x_max(z)) of the pod offset inward by t (2D offset of the XZ silhouette)"""
    p = SIL if t == 0 else SIL.buffer(-t, join_style=1, resolution=32)
    zs = np.r_[np.linspace(p.bounds[1] + 0.005, Z_BOT + RC + 2.0, 160), np.linspace(Z_BOT + RC + 2.0, p.bounds[3] - 0.005, 220)[1:]]
    xs = np.array([_sil_x(p, z) for z in zs])
    return zs, xs[:, 0], xs[:, 1]


def pod_solid(t, z_lo=None, z_hi=None, n=192):
    """loft of circles of the pod offset by t; flat bottom; z_lo / z_hi give exact end rings (no boolean slivers)"""
    zs, x0, x1 = section_fn(t)
    if z_lo is not None or z_hi is not None:
        lo = zs[0] if z_lo is None else z_lo
        hi = zs[-1] if z_hi is None else z_hi
        zn = np.unique(np.r_[lo, zs[(zs > lo + 0.05) & (zs < hi - 0.05)], hi])
        x0, x1, zs = np.interp(zn, zs, x0), np.interp(zn, zs, x1), zn
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rings = []
    for z, a, b in zip(zs, x0, x1):
        c, r = (a + b) / 2, (b - a) / 2
        rings.append(np.c_[c + r * np.cos(th), r * np.sin(th), np.full(n, z)])
    V = np.vstack(rings + [[[(x0[0] + x1[0]) / 2, 0, zs[0]]], [[(x0[-1] + x1[-1]) / 2, 0, zs[-1]]]])
    F = []
    m = len(rings)
    for k in range(m - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            F += [[a, b, b + n], [a, b + n, a + n]]
    cb, ct = m * n, m * n + 1
    for j in range(n):
        F.append([cb, (j + 1) % n, j])
        F.append([ct, (m - 1) * n + j, (m - 1) * n + (j + 1) % n])
    s = trimesh.Trimesh(V, np.array(F), process=True)
    s.fix_normals()
    assert s.is_watertight, 'pod loft not watertight'
    return s


def pod_circle(t, z):
    """(cx, R) of the pod section offset by t at height z"""
    zs, x0, x1 = section_fn(t)
    a, b = np.interp(z, zs, x0), np.interp(z, zs, x1)
    return (a + b) / 2, (b - a) / 2


# =====================================================================================
# DOSING CORE v6.1: skewed (scissor) window/outlet, plates at the 1.2 gaps, comb lips, sweeper disc, rim lip seal
# =====================================================================================
def _halfplane(q, d, left=True, L=400.0):
    d = np.asarray(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * (1 if left else -1)
    q = np.asarray(q, float)
    return Polygon([q - L * d, q + L * d, q + L * d + L * n, q - L * d + L * n])


def edge_lines(half, rm=SKEW_RM, delta=SKEW_DEG):
    """the two pinwheel edge lines (point, direction) of a sector of half-angle `half` centred on +X"""
    out = []
    for sgn in (+1, -1):
        h = math.radians(sgn * half)
        q = rm * np.array([math.cos(h), math.sin(h)])
        d = np.array([math.cos(h + math.radians(delta)), math.sin(h + math.radians(delta))])
        out.append((q, d))
    return out                                   # [(+edge), (-edge)]


def skew_sector(r_in, r_out, half, corner):
    (qp, dp), (qm, dm) = edge_lines(half)
    reg = _halfplane(qp, dp, left=False).intersection(_halfplane(qm, dm, left=True))
    ann = Point(0, 0).buffer(r_out, resolution=128).difference(Point(0, 0).buffer(r_in, resolution=128))
    return reg.intersection(ann).buffer(-corner, resolution=32).buffer(corner, resolution=32)


r_in_p, r_out_p = bd.POCKETS[bd.PLATES_FOR][:2]
HALF_L = bd.POCKET_ANG[bd.PLATES_FOR] / 2
P_PLATES_S = skew_sector(r_in_p, r_out_p, HALF_L, bd.POCKET_CORNER_R)
_ann = Point(0, 0).buffer(bd.OUT_R_MAX - bd.PL_DRAFT, resolution=64).difference(Point(0, 0).buffer(r_in_p - bd.OUT_MARGIN_IN, resolution=64))
OUT_T = P_PLATES_S.buffer(bd.DRAFT_OFF + bd.OUT_MARGIN, resolution=32).intersection(_ann).buffer(-1.0).buffer(1.0)
OUT_B = OUT_T.buffer(bd.PL_DRAFT, resolution=32)
WIN_T = P_PLATES_S.buffer(bd.DRAFT_OFF + bd.WIN_MARGIN, resolution=32).intersection(
    Point(0, 0).buffer(bd.WIN_R_MAX - bd.PL_DRAFT, resolution=64)).buffer(-1.0).buffer(1.0)
WIN_B = WIN_T.buffer(bd.PL_DRAFT, resolution=32)
EDGE_OFF = {'out': bd.DRAFT_OFF + bd.OUT_MARGIN, 'win': bd.DRAFT_OFF + bd.WIN_MARGIN + bd.PL_DRAFT}   # lip face outline offsets


def lip_lines(kind):
    """opening edge lines of the face that carries the lips: gate TOP face (outlet, built at +X then turned 180) /
    window BOTTOM face; returned as (point, dir, outward-normal sign) in the +X frame"""
    off = EDGE_OFF[kind]
    res = []
    for k, (q, d) in enumerate(edge_lines(HALF_L)):
        n = np.array([-d[1], d[0]])                  # left normal
        sgn = +1 if k == 0 else -1                   # + edge: solid plate is on the LEFT (larger angles); - edge: right
        res.append((q + sgn * off * n, d, sgn))
    return res


def airlock_check():
    """min angular clearance (deg) over radius between the pocket (any angle) and the window+outlet: the pocket may
    never touch both at once (half-angle sum < 180 at every radius) -> returns the worst margin"""
    worst = 1e9
    for r in np.arange(14.0, 51.0, 0.5):
        circ = Point(0, 0).buffer(r + 0.01, resolution=256).exterior

        def half_extent(poly, centre_deg):
            g = circ.intersection(poly)
            if g.is_empty:
                return None
            c = np.array(g.coords if g.geom_type == 'LineString' else [p for s in g.geoms for p in s.coords])
            a = (np.degrees(np.arctan2(c[:, 1], c[:, 0])) - centre_deg + 180) % 360 - 180
            return a.min(), a.max()
        w = half_extent(WIN_B, 0.0)
        o = half_extent(rotz_poly(OUT_B, 180), 180.0)
        p = half_extent(bd.P_BOT, 0.0)
        if not (w and o and p):
            continue
        span = (w[1] - w[0]) / 2 + (o[1] - o[0]) / 2 + (p[1] - p[0])
        worst = min(worst, 180.0 - span)
    return round(worst, 1)


def rotz_poly(p, a):
    return affinity.rotate(p, a, origin=(0, 0))


def _grv_w(sgn):
    """groove offsets (left-normal coordinate) LIPS..LIPS+LIPW into the solid plate"""
    return (LIPS, LIPS + LIPW) if sgn > 0 else (-(LIPS + LIPW), -LIPS)


def build_gate61():
    g = cyl(2 * bd.GATE_R, G0, G1, n=2 * SEG)
    outlet = rotz(bd.loft_wedges(OUT_T, G1 + 0.5, OUT_B.buffer(bd.PL_DRAFT / PLATE_T * 0.5), G0 - 0.5), 180)
    cuts = [outlet, cyl(bd.GATE_HOLE_D, G0 - 1, G1 + 1, 96)]           # no crumb grooves any more (they trapped crumbs)
    for q, d, sgn in lip_lines('out'):
        s0, s1 = edge_s_range(OUT_T, q, d)
        s0, s1 = s0 - 1.0, s1 + 0.5
        cuts.append(rotz(line_strip(q, d, s0, s1, *_grv_w(sgn), G1 - LIPD, G1 + 1), 180))
    cuts += bd.notch_cuts(bd.BOWL_R_IN - bd.KEY_PROT_GATE - bd.KEY_CLR, G0 - 1, G1 + 1)
    return D(g, cuts)


def build_window61():
    w = cyl(2 * bd.WIN_R, W0, W1, n=2 * SEG)
    win = bd.loft_wedges(WIN_T, W1 + 0.5, WIN_B.buffer(bd.PL_DRAFT / PLATE_T * 0.5), W0 - 0.5)
    cuts = [win, cyl(bd.WIN_HOLE_D, W0 - 1, W1 + 1, 96)]
    for q, d, sgn in lip_lines('win'):
        s0, s1 = edge_s_range(WIN_B, q, d)
        s0, s1 = s0 - 1.0, s1 + 0.5
        cuts.append(line_strip(q, d, s0, s1, *_grv_w(sgn), W0 - 1, W0 + LIPD))
    cuts += bd.notch_cuts(bd.BOWL_R_STEP - bd.KEY_PROT_WIN - bd.KEY_CLR, W0 - 1, W0 + 1 + PLATE_T)
    return D(w, cuts)


def edge_s_range(poly, q, d, tol=0.35):
    """s range along the line q + s d over which the opening outline runs straight on that line"""
    c = np.array(poly.exterior.coords)
    d = np.asarray(d, float) / np.linalg.norm(d)
    dist = np.abs(d[0] * (c[:, 1] - q[1]) - d[1] * (c[:, 0] - q[0]))
    s = (c[dist < tol] - q) @ d
    return float(s.min()), float(s.max())


def _strip_range(q, d, r0, r1):
    """s range of the line q + s d between radii r0 and r1 (outer intersections)"""
    b = 2 * np.dot(q, d)
    out = []
    for r in (r0, r1):
        c = np.dot(q, q) - r * r
        out.append((-b + math.sqrt(max(b * b - 4 * c, 0.0))) / 2)     # clamps to the closest approach
    return out


def build_lip(q, d, sgn, face_z, up):
    """comb-slit TPU lip along an opening edge line: anchor 3.15 x 1.0 pressed into the groove bottom, flap 0.8
    leaning 40 deg towards the opening, tip 0.15 into the disc face; slits every 5 mm (0.7 wide) stop 1 mm above
    the anchor. up=True: gate (groove opens upwards, disc above)"""
    s0, s1 = edge_s_range(OUT_T if up else WIN_B, q, d)
    s0, s1 = s0 - 0.7, s1 + 0.2
    n = np.array([-d[1], d[0]]) * sgn               # unit normal pointing INTO the plate (away from the opening)
    zs = 1 if up else -1
    zg = face_z - zs * LIPD                         # groove bottom
    za = zg + zs * ANCH_H                           # anchor top
    z_tip = (DISC_Z0 if up else DISC_Z1) + zs * LIP_PRE
    wc = LIPS + LIPW / 2                            # groove centre offset from the edge
    h = abs(z_tip - za)
    lean = h * math.tan(math.radians(FLAP_LEAN))
    tw = FLAP_T / math.cos(math.radians(FLAP_LEAN))  # horizontal width of the inclined flap
    P = lambda s, w, z: [*(q + s * d + w * n), z]
    anchor = trimesh.convex.convex_hull(np.array([P(s, w, z) for s in (s0, s1) for w in (wc - ANCH_W / 2, wc + ANCH_W / 2) for z in (zg + zs * 0.02, za)]))
    flap = trimesh.convex.convex_hull(np.array(
        [P(s, wc + tw / 2, za - zs * 0.05) for s in (s0, s1)] + [P(s, wc - tw / 2, za - zs * 0.05) for s in (s0, s1)] +
        [P(s, wc - lean + tw / 2, z_tip) for s in (s0, s1)] + [P(s, wc - lean - tw / 2, z_tip) for s in (s0, s1)]))
    lip = U([anchor, flap])
    cuts = []
    z_stop = za + zs * SLIT_STOP
    for s in np.arange(s0 + SLIT_P, s1 - 1.5, SLIT_P):
        lo, hi = sorted((z_stop, z_tip + zs * 1.0))
        cuts.append(line_strip(q, d, s - SLIT_W / 2, s + SLIT_W / 2, -20, 20, lo, hi))
    return D(lip, cuts), round(s1 - s0, 1), round(h / math.cos(math.radians(FLAP_LEAN)), 2)


def build_lips61():
    L = {}
    for k, (q, d, sgn) in enumerate(lip_lines('out')):
        m, ln, fl = build_lip(q, d, sgn, G1, True)
        L[f'labbro_uscita{SFX}_{k+1}'] = rotz(m, 180)
    for k, (q, d, sgn) in enumerate(lip_lines('win')):
        m, ln, fl = build_lip(q, d, sgn, W0, False)
        L[f'labbro_finestra{SFX}_{k+1}'] = m
    return L, ln, fl


def build_disc61():
    disc, orange_v6, black_v6 = None, None, None
    plate = cyl(bd.DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG)
    pc = bd.pocket_cutter(DISC_Z0, DISC_Z1)
    plate = D(plate, [pc, rotz(pc, 180)])
    cap = revolve([(4.0, dt.CAP_CEIL), (dt.CAP_RI, dt.CAP_CEIL), (dt.CAP_RI, dt.CAP_Z0), (dt.CAP_RO, dt.CAP_Z0),
                   (dt.CAP_RO, dt.CAP_ZS), (dt.BOSS_D / 2, dt.CAP_ZF), (4.0, dt.CAP_ZF)])
    # sweeper ribs on the lands of the underside, skewed -30 deg (cross the +15 deg lips at ~45 deg, push crumbs round
    # to the outlet in both turning directions); kept 1.5 mm off the pocket edges
    land = Point(0, 0).buffer(RIB_R[1], resolution=128).difference(Point(0, 0).buffer(RIB_R[0], resolution=64)).difference(
        shapely.unary_union([bd.P_BOT, rotz_poly(bd.P_BOT, 180)]).buffer(1.5, resolution=16))
    ribs2d = []
    for a0 in RIB_ANG:
        for a in (a0, a0 + 180.0):
            rm = (RIB_R[0] + RIB_R[1]) / 2
            q = rm * np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
            d = np.array([math.cos(math.radians(a + RIB_SKEW)), math.sin(math.radians(a + RIB_SKEW))])
            nn = np.array([-d[1], d[0]])
            ribs2d.append(Polygon([q - 30 * d - RIB_W / 2 * nn, q + 30 * d - RIB_W / 2 * nn, q + 30 * d + RIB_W / 2 * nn, q - 30 * d + RIB_W / 2 * nn]))
    ribs2d = shapely.unary_union(ribs2d).intersection(land)
    ribs = prism(ribs2d, DISC_Z0 - RIB_H, DISC_Z0 + 0.3)
    disc = U([plate, cyl(dt.BOSS_D, dt.CAP_ZF - 0.2, DISC_Z0 + 0.5), cap, ribs])
    key_slot = box(-(dt.HEX_KEY_W + 0.3) / 2, (dt.HEX_KEY_W + 0.3) / 2, 0, dt.POCKET_AF / 2 + dt.HEX_KEY_H + 0.15, dt.BOSS_Z0 - 0.5, bd.POCKET_TOP_Z)
    disc = D(disc, [cyl(dt.SLEEVE_BORE_D, dt.CAP_CEIL - 1, dt.BOSS_Z0),
                    hull_of((circle_pts(dt.SLEEVE_BORE_D + 2 * (dt.SLEEVE_CH + 0.5)), dt.CAP_CEIL - 0.5), (circle_pts(dt.SLEEVE_BORE_D), dt.CAP_CEIL + dt.SLEEVE_CH)),
                    prism(hexagon(bd.AGIT_HEX_AF), DISC_Z1 - bd.AGIT_HEX_DEPTH, DISC_Z1 + 1),
                    prism(hexagon(dt.POCKET_AF), dt.BOSS_Z0 - 0.5, bd.POCKET_TOP_Z), key_slot])
    portion = vol(I(pc, cyl(bd.DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG))) / 1000 * bd.BULK_DENSITY
    label = text_poly(f'{bd.VARIANT} · ~{portion:.1f} g · {VER}', 5.5, 0, 36).union(text_poly('SELF-CLEAN', 3.2, 0, -14.5))
    orange, black = split(disc, face_region(label, DISC_Z1, True))
    return disc, orange, black, round(portion, 2), ribs2d


def rim_lip_profile():
    """(r, z) polygon of the low-force rim lip seal: foot + riser in the groove, 0.5 flap rising outward at 42 deg"""
    foot = sbox(RG_RISER[0], RG_Z0 + 0.02, RG_R1 - 0.05, RG_Z0 + RG_FOOT_T)
    riser = sbox(RG_RISER[0], RG_Z0 + 0.02, RG_RISER[1], RG_RISER[2])
    a = math.radians(RG_ANG)
    A = np.array(RG_ROOT)
    L = (RG_TIP_Z - A[1]) / math.sin(a)
    B = A + L * np.array([math.cos(a), math.sin(a)])
    nrm = np.array([-math.sin(a), math.cos(a)]) * RG_T / 2
    flap = Polygon([A - nrm, B - nrm, B + nrm, A + nrm]).intersection(sbox(50, 0, 70, RG_TIP_Z))
    p = shapely.unary_union([foot, riser, flap]).buffer(0.05).buffer(-0.05)
    return p, L, B


def build_rim_gasket61():
    p, L, B = rim_lip_profile()
    c = np.array(p.exterior.coords)[:-1]
    m = trimesh.creation.revolve(np.vstack([c, c[:1]]), sections=2 * SEG)
    if m.volume < 0:
        m.invert()
    return m, L, B


def rim_lip_force():
    """flap = cantilever (E 30 MPa TPU 95A), tip pushed down by the flange: F/w = E t^3 d / (4 L^3 sin^2 theta);
    torque = tip friction + lug friction + lift (ramp) for the gasket load only"""
    p, L, B = rim_lip_profile()
    E, mu_tpu, mu_petg = 30.0, 0.6, 0.3
    th = math.radians(90 - RG_ANG)                    # angle of the flap from vertical
    dlt = RG_TIP_Z - FLANGE_UNDERSIDE
    fw = E * RG_T ** 3 * dlt / (4 * L ** 3 * math.sin(th) ** 2)
    rg = B[0]
    F = fw * 2 * math.pi * rg
    tan_ramp = bd.LIFT / (math.radians(bd.LUG_RAMP_DEG) * (bd.LUG_R1 - 2.0))
    r_lug = (bd.BOWL_R_OUT + bd.LUG_R1) / 2 / 1000
    T = F * (mu_tpu * rg / 1000 + mu_petg * r_lug + tan_ramp * r_lug)
    # v6 solid ring: 2.1 x 2.5 TPU, compressed 1.0 at lock (40 %), unconfined linear estimate
    A6 = math.pi * ((bd.GSK_R1 - 0.15) ** 2 - (bd.GSK_R0 + 0.15) ** 2)
    F6 = E * (1.0 / bd.GSK_H) * A6
    tan_ramp6 = bd.LIFT / (math.radians(18.0) * (bd.LUG_R1 - 2.0))       # v6 lugs: 18 deg ramp
    T6 = F6 * (mu_tpu * (bd.GSK_R0 + bd.GSK_R1) / 2000 + mu_petg * r_lug + tan_ramp6 * r_lug)
    return {'model': 'flap as cantilever, F/w = E t^3 d / (4 L^3 sin^2 th), E = 30 MPa (TPU 95A), mu TPU/PETG 0.6, PETG/PETG 0.3; '
                     'torque = F (mu_tpu r_seal + mu_petg r_lug + tan(ramp) r_lug)',
            'v61_lip': {'thickness': RG_T, 'free_length': round(L, 2), 'angle_above_horizontal_deg': RG_ANG, 'deflection_at_lock': round(dlt, 2),
                        'force_per_mm': round(fw, 4), 'total_force_N': round(F, 1), 'extra_twist_torque_Nm': round(T, 2),
                        'contact_starts_after_lift_mm': round(bd.LIFT - dlt, 2), 'lug_ramp_deg': bd.LUG_RAMP_DEG,
                        'note': 'peak at the end of the 4 deg ramp; the last 16 deg slide on the flats with friction only'},
            'v6_solid_ring': {'section': '2.1 x 2.5', 'compression': 1.0, 'strain': 0.4, 'force_N': round(F6), 'extra_twist_torque_Nm': round(T6),
                              'verdict': 'cannot be locked by hand: the lugs/hooks would yield first'}}


def lips_torque(lip_len, flap_len):
    E, mu = 30.0, 0.6
    th = math.radians(FLAP_LEAN)
    fw = lambda dl: E * FLAP_T ** 3 * dl / (4 * flap_len ** 3 * math.sin(th) ** 2) * (SLIT_P - SLIT_W) / SLIT_P
    rm = 0.032
    res = {}
    for nm, dl in (('nominal_0.15', 0.15), ('max_0.3', 0.30)):
        F = fw(dl) * lip_len
        res[nm] = {'force_per_lip_N': round(F, 2), 'torque_4_lips_Nm': round(4 * mu * F * rm, 3)}
    # v6 solid strip 3.0 wide, 2.2 tall (groove + flap) if it touched the disc by 0.3: compression, not bending
    F6 = E * 0.3 / 2.2 * 3.0 * lip_len
    res['v6_solid_strip_if_0.3_contact'] = {'force_per_lip_N': round(F6), 'torque_4_lips_Nm': round(4 * mu * F6 * rm, 1),
                                            'note': 'v4b/v6 modelled the strips 0.05 short of the disc (no seal) because contact would stall the servo'}
    res['servo_stall_Nm'] = 2.5
    return res


# =====================================================================================
# FUNNEL (bowl nose above z 0, chute below): skewed gate outlet -> 45 deg flare -> morph to the vertical tube at CH_X
# =====================================================================================
MOUTH = OUT_B.buffer(bd.MOUTH_FLARE, resolution=32)
FLARE_R_MIN = round(OUT_B.exterior.distance(Point(0, 0)) - bd.MOUTH_FLARE - 0.3, 2)
Z_FL = G0 - bd.FLARE_H                               # 22.8


def flare61(extra=0.0):
    clip = Point(0, 0).buffer(200).difference(Point(0, 0).buffer(FLARE_R_MIN - extra, resolution=64))
    return MOUTH.buffer(bd.FLARE_OUT + extra, resolution=32).intersection(clip).buffer(-1.0).buffer(1.0)


FLARE_W, FLARE_OW = rotz_poly(flare61(), 180), rotz_poly(flare61(T_CH), 180)


def morph_circle(top, z_top, r, z_bot, levels=20, n=128):
    return v6.morph_ell(top, z_top, CH_X, r, r, z_bot, levels=levels, n=n)


def pick_zb(target=51.0):
    for zb in np.arange(-4.0, -30.0, -1.0):
        cav = morph_circle(FLARE_W, Z_FL + 0.01, RI, zb, levels=12, n=96)
        s = bd.floor_slope_min(cav, zb + 0.05, Z_FL - 0.05)
        if s >= target:
            return float(zb), round(s, 1)
    raise RuntimeError('no funnel depth')


ZB, _ZB_SLOPE = pick_zb()


def funnel61():
    cav_fl = rotz(bd.loft_wedges(MOUTH, G0 + 1.0, flare61(), Z_FL), 180)
    out_fl = rotz(bd.loft_wedges(MOUTH.buffer(T_CH, resolution=32), G0, flare61(T_CH), Z_FL), 180)
    cav_m = morph_circle(FLARE_W, Z_FL + 0.01, RI, ZB)
    out_m = morph_circle(FLARE_OW, Z_FL + 0.01, RO, ZB)
    return cav_fl, out_fl, cav_m, out_m


def zsec_poly(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    T = np.eye(4); T[2, 3] = -z
    p2, _ = s.to_2D(to_2D=T)
    return shapely.unary_union(list(p2.polygons_full))


# =====================================================================================
# CHIOCCIOLA_v61 (bowl): v6 core, plates at the 1.2 gaps, rim lip-seal groove, funnel turned down, shell-tab inserts
# =====================================================================================
TWR_INS = v6.TWR_INS                                  # tower top lobes r 19 at 0/125/240 (unchanged)
TAB_INS = [polar(TAB_R_INS, a) for a in TAB_ANG]
DRAIN = (np.array([-11.5, 0.0, 3.4]), np.array([-22.0, 0.0, 2.0]), 3.0)
CH_EARS = None


def build_bowl61(F):
    global CH_EARS
    cav_fl, out_fl, cav_m, out_m = F
    sec0 = zsec_poly(out_m, -0.05)
    ye = sec0.bounds[3] + 5.0
    CH_EARS = [(CH_X, round(ye, 1)), (CH_X, -round(ye, 1))]
    lugs = [bd.lug(a, w) for a, w in zip(bd.LUG_ANG, bd.LUG_W)]
    tongue = D(cyl(2 * bd.TONGUE_R1, bd.RIM_Z - 0.5, bd.RIM_Z + bd.TONGUE_H, 2 * SEG), cyl(2 * bd.TONGUE_R0, bd.RIM_Z - 1, bd.RIM_Z + 3, 2 * SEG))
    body = U([cyl(2 * bd.BOWL_R_OUT, 0.0, bd.RIM_Z, n=2 * SEG), out_fl, I(out_m, above(0.0)), tongue] + lugs)
    p0, p1, dd = DRAIN
    v = p1 - p0
    drain = trimesh.creation.cylinder(radius=dd / 2, height=np.linalg.norm(v), sections=32)
    drain.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / np.linalg.norm(v)))
    drain.apply_translation((p0 + p1) / 2)
    cav = [cyl(2 * bd.BOWL_R_IN, G0, W0 + 0.01, n=2 * SEG), cyl(2 * bd.BOWL_R_STEP, W0, bd.RIM_Z + 5, n=2 * SEG),
           bd.central_cavity(), cav_fl, cav_m, cyl(bd.BASE_HOLE_D, -1, bd.BASE_Z1 + 1, 96),
           D(cyl(2 * RG_R1, RG_Z0, bd.RIM_Z + 1, 2 * SEG), cyl(2 * RG_R0, RG_Z0 - 1, bd.RIM_Z + 2, 2 * SEG)),
           below(0.0), drain] + bd.latch_slot_cuts()
    for x, y in TWR_INS + CH_EARS + TAB_INS:
        cav.append(at(U([cyl(v6.INS_D, -1.0, v6.INS_DEPTH, 48), cyl(v6.INS_D + 1.6, -1.0, 0.4, 48)]), x, y))
    bowl = D(body, cav)
    ribs = []
    for a in bd.KEY_ANG:
        ribs.append(rotz(box(bd.BOWL_R_IN - bd.KEY_PROT_GATE, bd.BOWL_R_IN + 0.5, -bd.KEY_W / 2, bd.KEY_W / 2, G0, W0), a))
        ribs.append(rotz(box(bd.BOWL_R_STEP - bd.KEY_PROT_WIN, bd.BOWL_R_STEP + 0.5, -bd.KEY_W / 2, bd.KEY_W / 2, W0, RG_Z0 - 0.5), a))
    return U([bowl] + ribs)


# =====================================================================================
# SCIVOLO_v61 (green chute: morph below z 0 + vertical Ø44 tube, ends 1 mm above the cap outlet with a drip edge)
# =====================================================================================
Z_CH_END = Z_S - 1.0                                  # -73 (cap outlet tube top at -74)
CH_FL_T = 3.0


def build_chute61(F):
    cav_fl, out_fl, cav_m, out_m = F
    tube = at(cyl(2 * RO, Z_CH_END, ZB + 0.02, 128), CH_X, 0)
    outer = U([I(out_m, below(0.0)), tube])
    fl = zsec_poly(out_m, -0.05).buffer(2.0, resolution=24)
    ears = shapely.unary_union([Point(x, y).buffer(4.5, resolution=24) for x, y in CH_EARS] +
                               [sbox(x - 4.5, min(0, y), x + 4.5, max(0, y)) for x, y in CH_EARS])
    flange = prism(fl.union(ears), -CH_FL_T, 0.0)
    gus = [hull_of((np.array(Point(x, y).buffer(4.5, resolution=16).exterior.coords)[:-1], -CH_FL_T),
                   (np.array(Point(x, 0.6 * y).buffer(2.0, resolution=16).exterior.coords)[:-1], -CH_FL_T - 8.0)) for x, y in CH_EARS]
    body = U([outer, flange] + gus)
    tip = at(D(cyl(2 * RO + 2, Z_CH_END - 1, Z_CH_END + 1.4, 96),
               hull_of((circle_pts(2 * (RI + 0.6), 96), Z_CH_END - 0.01), (circle_pts(2 * RO, 96), Z_CH_END + 1.4))), CH_X, 0)
    cuts = [cav_m, at(cyl(2 * RI, Z_CH_END - 2, ZB + 0.05, 128), CH_X, 0), tip]
    for x, y in CH_EARS:
        cuts.append(at(U([cyl(3.4, -CH_FL_T - 9, 1.0, 32), cyl(6.2, -CH_FL_T - 9, -CH_FL_T + 0.0, 48)]), x, y))
    return D(body, cuts)


# =====================================================================================
# COLONNA_v61 (v6 tower, bottom lobes moved from 215 to 235 deg: 5 mm clear of the chute)
# =====================================================================================
BOT_LOBE_ANG61 = (90.0, 235.0, 330.0)


def build_column61():
    keep = v6.BOT_LOBE_ANG
    v6.BOT_LOBE_ANG = BOT_LOBE_ANG61
    try:
        return v6.build_column()
    finally:
        v6.BOT_LOBE_ANG = keep


# =====================================================================================
# FLANGIA_PIANO_v61: round plate r 82 (screws hidden under the shell rim), hooks in the LOCKED frame, cable grommet hole
# =====================================================================================
FL_Z0, FL_Z1 = v6.FL_Z0, v6.FL_Z1
FL_R = 82.0
WOOD_R, WOOD_ANG = 75.5, (45.0, 135.0, 225.0, 315.0)
WOOD_XY = [polar(WOOD_R, a) for a in WOOD_ANG]
HOOKS61 = [(a0 - bd.LOCK_ROT, a1 - bd.LOCK_ROT) for a0, a1 in v5.HOOKS]
PIN_ANG61 = (120.0, 190.0, 320.0)                     # clear of the bowl key ribs (60-90 and 220-250 over the twist)
CABLE_ANG, CABLE_R = -20.0, 76.0
CABLE_XY = polar(CABLE_R, CABLE_ANG)
GROM = dict(hole=10.0, od=10.4, id=5.0, lip_d=12.0, lip_t=1.2)


def build_flange61(cav):
    plate = revolve([(0, FL_Z0), (FL_R - 1.0, FL_Z0), (FL_R, FL_Z0 + 1.0), (FL_R, FL_Z1 - 0.5), (FL_R - 0.5, FL_Z1), (0, FL_Z1)], 2 * SEG)
    if plate.volume < 0:
        plate.invert()
    skirt = D(cyl(2 * v6.SKIRT_R1, v5.HOOK_Z0, FL_Z0 + 0.01), cyl(2 * v6.SKIRT_R0, v5.HOOK_Z0 - 1, FL_Z0 + 1))
    tongues = [bd.sector_solid(a0, a1, v5.HOOK_R0, v6.SKIRT_R1 - 0.5, v5.HOOK_Z0, v5.HOOK_Z1, 24) for a0, a1 in HOOKS61]
    pins = []
    for a in PIN_ANG61:
        x, y = polar(v6.PIN_R, a)
        z0 = W1 + v6.PIN_GAP
        pins.append(at(U([cyl(v6.PIN_D, z0, FL_Z0 + 0.01, 48), hull_of((circle_pts(v6.PIN_D, 48), FL_Z0 - 1.0), (circle_pts(v6.PIN_D + 2.0, 48), FL_Z0 + 0.01))]), x, y))
    body = U([plate, skirt] + tongues + pins)
    cuts = [cav,
            D(cyl(2 * v5.LGROOVE_R1, FL_Z0 - 1, FL_Z0 + v5.LGROOVE_D), cyl(2 * v5.LGROOVE_R0, FL_Z0 - 2, FL_Z0 + v5.LGROOVE_D + 1)),
            at(D(cyl(2 * v5.FL_GSK_R + v5.GRV_W, FL_Z1 - v5.GRV_D, FL_Z1 + 1), cyl(2 * v5.FL_GSK_R - v5.GRV_W, FL_Z1 - v5.GRV_D - 1, FL_Z1 + 2)), *v6.HOLE_C),
            at(cyl(GROM['hole'], FL_Z0 - 1, FL_Z1 + 1, 48), *CABLE_XY)]
    for x, y in v6.COLLAR_PINS:
        cuts.append(at(cyl(3.4, FL_Z1 - 3.0, FL_Z1 + 1.0, 32), x, y))
    for x, y in WOOD_XY:
        cuts.append(at(U([cyl(v5.WOOD_D, FL_Z0 - 1, FL_Z1 + 1, 32), cyl(v5.WOOD_CB_D, FL_Z0 - 1, FL_Z0 + v5.WOOD_CB_H, 48)]), x, y))
    ex, ey = polar(72.0, 180.0)
    cuts.append(face_region(affinity.scale(text_poly(VER, 5.0, ex, ey, 90.0), -1, 1, origin=(ex, ey)), FL_Z0, False))
    return D(body, cuts)


def build_grommet():
    x, y = CABLE_XY
    m = U([cyl(GROM['od'], FL_Z0, FL_Z1 - 0.05, 48), cyl(GROM['lip_d'], FL_Z0 - GROM['lip_t'], FL_Z0 + 0.01, 48)])
    m = D(m, [cyl(GROM['id'], FL_Z0 - 5, FL_Z1 + 5, 32)])
    return at(m, x, y)


# =====================================================================================
# SCATOLA_v61 (sealed electronics box inside the pod; hangs from the tower like v6)
# =====================================================================================
BOX_OUT = rrect(BXO[0], BXO[1], BXO[2], BXO[3], BX_R)
BOX_IN = BOX_OUT.buffer(-BX_T, join_style=1, resolution=16)
ROOF_T = 2.4
FL_OUT = 1.0                                          # bottom rim flange -> 3.0 mm wide face for the cap lip
CRADLE_HALF_X = dt.CAGE_OUT_HALF_Y
CAGE_Z0 = v6.CAGE_Z0
CAGE_Y = v6.CAGE_Y
VOID_Y = v6.VOID_Y
SERVO_HOLES_W = v6.SERVO_HOLES_W
BOT_INS61 = [polar(v6.BOT_LOBE_R, a) for a in BOT_LOBE_ANG61]
IX1 = BXO[1] - BX_T
BB = dict(x=(21.5, 21.5 + BB_T), y=(-35.0, 35.0), z=(Z_R - ROOF_T - 0.6 - 50.0, Z_R - ROOF_T - 0.6))
GLAND = dict(x=-3.0, z=-48.0, hole_d=12.2, pad_d=20.0, pad_t=2.0, side=-1)      # M12 IP68 (cable 4-7) on the -Y wall, inside the pod
VENT = dict(x=8.0, y=-30.0, hole_d=12.2)           # M12x1.5 ePTFE IP68 vent in the roof, pointing up under the bowl (highest, sheltered)
POST_AB = dict(x=(-23.5, -18.0), w=6.0)               # posts for thumb-turns A/B on the -X wall
POST_C = dict(x=(CRADLE_HALF_X - 0.01, 19.0), w=6.0)  # post for C on the cradle +X face
POST_Z0 = TT_ARM_Z1                                    # post bottom face = arm top when closed


def _wall_pad(spec, poly_d, hole=False):
    y_face = BXO[3] if spec['side'] > 0 else BXO[2]
    s = spec['side']
    if not hole:
        return yprism(Point(spec['x'], spec['z']).buffer(poly_d / 2, resolution=64), min(y_face - s * 1.0, y_face + s * spec['pad_t']),
                      max(y_face - s * 1.0, y_face + s * spec['pad_t']))
    return yprism(v6.teardrop_xz(spec['x'], spec['z'], poly_d), y_face - 4.0, y_face + 4.0)


def post(x0, x1, yc, w, z_top, z_bot, chamfer=1.2):
    """vertical post with lead-in chamfers (30 deg) on both Y edges of its bottom face (the thumb-turn arm climbs them)"""
    pts = []
    for x in (x0, x1):
        for y in (yc - w / 2, yc + w / 2):
            pts.append([x, y, z_top])
        pts += [[x, yc - w / 2, z_bot + chamfer], [x, yc + w / 2, z_bot + chamfer],
                [x, yc - w / 2 + chamfer / math.tan(math.radians(30)), z_bot], [x, yc + w / 2 - chamfer / math.tan(math.radians(30)), z_bot]]
    return trimesh.convex.convex_hull(np.array(pts))


def build_box61():
    walls = prism(ring2d(BOX_OUT, BOX_IN), Z_W, Z_R - ROOF_T + 0.01)
    roof = prism(BOX_OUT, Z_R - ROOF_T, Z_R)
    rim = prism(ring2d(BOX_OUT.buffer(FL_OUT, join_style=1, resolution=16), BOX_IN), Z_W, Z_W + 3.0)
    boss = prism(Point(0, 0).buffer(v6.BOSS_R, resolution=96).intersection(BOX_OUT), v6.BOSS_Z0, Z_R - 1.0)
    cage = prism(sbox(-CRADLE_HALF_X, CAGE_Y[0], CRADLE_HALF_X, CAGE_Y[1]), CAGE_Z0, Z_R - 1.0)
    parts = [walls, roof, rim, boss, cage]
    slot_cuts = []
    for sy in (1, -1):                                   # perfboard: slotted blocks on both Y walls, board slides up to the roof
        y_in, y_end = sy * (BOX_IN.bounds[3] + 0.5), sy * (BB['y'][1] - 2.0)
        parts.append(box(BB['x'][0] - 2.0, BB['x'][1] + 2.0, min(y_in, y_end), max(y_in, y_end), Z_W + 3.0, Z_R - 1.0))
        slot_cuts.append(box(BB['x'][0] - 0.15, BB['x'][1] + 0.15, min(y_in, sy * (BB['y'][1] - 3.0)) - (0 if sy > 0 else 0.0),
                             max(y_in, sy * (BB['y'][1] - 3.0)), Z_W - 1.0, BB['z'][1] + 0.3))
    parts += [_wall_pad(GLAND, GLAND['pad_d'])]
    # thumb-turn posts: A/B hang from an L bracket on the -X wall (gusset above), C from the cradle +X face
    for (x, y) in TT[:2]:
        parts.append(box(POST_AB['x'][0], BXO[0] + 0.5, y - POST_AB['w'] / 2, y + POST_AB['w'] / 2, Z_W, Z_W + 6.0))
        parts.append(trimesh.convex.convex_hull(np.array([[xx, yy, zz] for yy in (y - 1.5, y + 1.5) for xx, zz in
                                                          ((POST_AB['x'][0], Z_W + 6.0), (BXO[0] + 0.5, Z_W + 6.0), (BXO[0] + 0.5, Z_W + 6.0 + 8.0))])))
        parts.append(post(POST_AB['x'][0], POST_AB['x'][1], y, POST_AB['w'], Z_W + 6.0, POST_Z0))
    parts.append(post(POST_C['x'][0], POST_C['x'][1], 0.0, POST_C['w'], CAGE_Z0 + 12.0, POST_Z0))
    for (x, y), ad in zip(TT, TT_ARM_DIR):
        bump = trimesh.creation.icosphere(subdivisions=2, radius=0.8)
        bump.apply_translation([x + (TT_ARM_L - 2.5) * math.cos(math.radians(ad)), y + (TT_ARM_L - 2.5) * math.sin(math.radians(ad)), POST_Z0 + 0.3])
        parts.append(bump)
    body = U(parts)
    cuts = [box(-CRADLE_HALF_X + 2.5, CRADLE_HALF_X - 2.5, VOID_Y[0], VOID_Y[1], CAGE_Z0 - 1.0, v6.S_TOP + 0.5),
            cyl(2 * dt.HUB_CAV_R, v6.S_TOP + 0.5 - 0.01, v6.CAV_TOP + 0.01, 96),
            hull_of((circle_pts(2 * dt.HUB_CAV_R, 96), v6.CAV_TOP), (circle_pts(2 * v6.PLAT_HOLE_R, 96), v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R)),
            cyl(2 * v6.PLAT_HOLE_R, v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R - 0.01, Z_R + 1.0, 96),
            _wall_pad(GLAND, GLAND['hole_d'], True), at(cyl(VENT['hole_d'], Z_R - ROOF_T - 1, Z_R + 1, 48), VENT['x'], VENT['y'])] + slot_cuts
    for x, y in SERVO_HOLES_W:
        cuts.append(at(U([cyl(v6.INS_D, CAGE_Z0 - 1, CAGE_Z0 + dt.SERVO_INS_DEPTH, 48),
                          hull_of((circle_pts(v6.INS_D + 1.8, 48), CAGE_Z0 - 0.5), (circle_pts(v6.INS_D, 48), CAGE_Z0 + 0.4))]), x, y))
    for x, y in BOT_INS61:
        cuts.append(at(U([cyl(v6.INS_D, Z_R - v6.INS_DEPTH, Z_R + 1.0, 48),
                          hull_of((circle_pts(v6.INS_D, 48), Z_R - 0.4), (circle_pts(v6.INS_D + 1.8, 48), Z_R + 0.5))]), x, y))
    ex, ey = 20.0, 0.0
    cuts.append(face_region(text_poly(f'{VER} DRY', 6.0, ex, ey), Z_R, True))
    return D(body, cuts)


# =====================================================================================
# GUSCIO_v61 (pod shell): smooth skin from the rim (z 64, under the flange) to the seam (z -72); 3 gusseted tabs
# under the bowl base (M3x12 into inserts), flush latch push-button boss
# =====================================================================================
BTN = dict(dish_d=28.0, dish_h=3.0, bore=14.4, head_d=14.0, shaft_d=7.0, collar_d=18.0, boss_d=21.0, u_boss=75.5, tip_u=62.0)


def radial_cyl(d, u0, u1, ang, z, n=64):
    m = trimesh.creation.cylinder(radius=d / 2, height=u1 - u0, sections=n)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation([(u0 + u1) / 2, 0, z])
    return rotz(m, ang)


def shell_r_at(ang, z, t=0.0):
    """radius of the pod surface (offset t) in direction ang at height z"""
    cx, R = pod_circle(t, z)
    a = math.radians(ang)
    # ray from the axis: |(u cos a - cx, u sin a)| = R
    b = -2 * cx * math.cos(a)
    c = cx * cx - R * R
    return (-b + math.sqrt(b * b - 4 * c)) / 2


def build_shell61():
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
    boss = I(radial_cyl(BTN['boss_d'], BTN['u_boss'], r_out - 0.5, LATCH_A, BTN_Z), pod_solid(0.5))
    parts.append(boss)
    sh = U(parts)
    rs = (BTN['dish_d'] / 2) ** 2 / (2 * BTN['dish_h']) + BTN['dish_h'] / 2
    sph = trimesh.creation.icosphere(subdivisions=4, radius=rs)
    sph.apply_translation([r_out - BTN['dish_h'] + rs, 0, BTN_Z])
    cuts = tab_cuts + [rotz(sph, LATCH_A), radial_cyl(BTN['bore'], BTN['u_boss'] - 1, r_out + 2, LATCH_A, BTN_Z)]
    return D(sh, cuts), r_out


def build_button61(r_out):
    u_face = r_out - BTN['dish_h']
    ub = BTN['u_boss'] - 0.1
    rh, rc, rs = BTN['head_d'] / 2, BTN['collar_d'] / 2, BTN['shaft_d'] / 2
    prof = [(0, BTN['tip_u']), (rs - 0.4, BTN['tip_u']), (rs, BTN['tip_u'] + 0.4), (rs, ub - 2.4), (rc, ub - 2.4), (rc, ub - (rc - rh)),
            (rh, ub), (rh, u_face - 0.5), (rh - 0.5, u_face), (0, u_face)]
    m = revolve(prof, 96)
    if m.volume < 0:
        m.invert()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))   # axis z -> +x
    m.apply_translation([0, 0, BTN_Z])
    return rotz(m, LATCH_A)


# =====================================================================================
# FONDELLO_v61 (cap: flat bottom on the bed, outlet with chamfer, D-lip seal on the box rim, spigot ring into the
# shell, 3 thumb-turn bosses) + GUARNIZIONE_FONDELLO_v61 (TPU lip on the D) + NOTTOLINO_v61 (flush thumb-turn)
# =====================================================================================
Z_C = Z_W - 0.5                                       # lip seat face (box rim face 0.5 above: lip bent ~1.2)
WALL_C = BOX_OUT.buffer(-0.5, join_style=1, resolution=16)   # centreline of the 3.0 wide box rim face
GRV_W, GRV_D = 2.4, 1.2
LIP_GH, LIP_LEAN = 1.7, 1.0
OUTLET = dict(r=23.0, wall=2.0, top=Z_CH_END - 1.0, chamfer=1.5)
TT_BOSS_TOP = TT_ARM_Z1 - TT_ARM_T - 0.3
TT_DISH_FLOOR = Z_BOT + TT_DISH_H
TT_CONE_TOP = TT_DISH_FLOOR + (TT_FACE_D - TT_SHAFT_D) / 2      # 45 deg countersink behind the face disc
TT_OR_Z = (TT_CONE_TOP + TT_BOSS_TOP) / 2


def build_cap61():
    outer = pod_solid(0.0, z_hi=Z_S - SEAM)
    inner = pod_solid(T_CAP)
    shell = D(outer, [inner])
    clip_in = pod_solid(T_CAP - 0.3)
    up = I(prism(ring2d(BOX_OUT.buffer(0.5, join_style=1, resolution=16), BOX_OUT.buffer(-1.5, join_style=1, resolution=16)), Z_BOT - 5, Z_C), clip_in)
    spig = I(D(pod_solid(T_SHELL + 0.25), pod_solid(T_SHELL + 1.85)), box(-200, 200, -200, 200, Z_S - SEAM - 0.01, Z_S + 3.4))
    tube = I(at(cyl(2 * (OUTLET['r'] + OUTLET['wall']), Z_BOT - 5, OUTLET['top'], 128), CH_X, 0), clip_in)
    bosses = [I(at(cyl(20.0, Z_BOT - 5, TT_BOSS_TOP, 64), x, y), clip_in) for x, y in TT]
    sup = [box(BB['x'][0] - 1.0, BB['x'][1] + 1.0, y0, y1, Z_BOT, BB['z'][0] - 0.1) for y0, y1 in ((20.0, 28.0), (-28.0, -20.0))]
    sup = [I(s, clip_in) for s in sup]
    body = U([shell, up, spig, tube] + bosses + sup)
    groove = prism(ring2d(WALL_C.buffer(GRV_W / 2, join_style=1, resolution=16), WALL_C.buffer(-GRV_W / 2, join_style=1, resolution=16)), Z_C - GRV_D, Z_C + 1)
    cuts = [groove, at(cyl(2 * OUTLET['r'], Z_BOT - 10, OUTLET['top'] + 1, 128), CH_X, 0),
            at(hull_of((circle_pts(2 * OUTLET['r'], 128), Z_BOT + OUTLET['chamfer']), (circle_pts(2 * (OUTLET['r'] + OUTLET['chamfer'] + 1.0), 128), Z_BOT - 1.0)), CH_X, 0)]
    for sy in (1, -1):                                 # wet-ring drain slots into the outlet bore
        cuts.append(box(CH_X - 1.5, CH_X + 1.5, sy * (OUTLET['r'] - 1.0), sy * (OUTLET['r'] + OUTLET['wall'] + 1.0), Z_BOT + T_CAP - 0.3, Z_BOT + T_CAP + 1.7)
                    if sy > 0 else box(CH_X - 1.5, CH_X + 1.5, -(OUTLET['r'] + OUTLET['wall'] + 1.0), -(OUTLET['r'] - 1.0), Z_BOT + T_CAP - 0.3, Z_BOT + T_CAP + 1.7))
    for (x, y), ad in zip(TT, TT_ARM_DIR):
        kd = math.radians(ad + 180.0)
        key = rotz(box(0, TT_ARM_L + 1.0, -(TT_ARM_W + 0.6) / 2, (TT_ARM_W + 0.6) / 2, TT_DISH_FLOOR - 0.01, TT_BOSS_TOP + 1), ad + 180.0)
        key.apply_translation([x, y, 0])
        cuts += [at(cyl(TT_SHAFT_D + 0.3, Z_BOT - 1, TT_BOSS_TOP + 1, 48), x, y),
                 at(cyl(TT_DISH_D, Z_BOT - 5, TT_DISH_FLOOR, 64), x, y),
                 at(hull_of((circle_pts(TT_FACE_D + 0.4, 64), TT_DISH_FLOOR - 0.01), (circle_pts(TT_SHAFT_D + 0.3, 64), TT_CONE_TOP + 0.15)), x, y), key]
    cap = D(body, cuts)
    return cap


def build_cap_gasket61():
    base = prism(ring2d(WALL_C.buffer(1.1, join_style=1, resolution=16), WALL_C.buffer(-1.1, join_style=1, resolution=16)), Z_C - GRV_D + 0.05, Z_C)
    pts = lambda off: np.array(WALL_C.buffer(off, join_style=1, resolution=16).exterior.coords)[:-1]
    o = lambda z, k: k - (z - Z_C) / LIP_GH * LIP_LEAN
    zt, e = Z_C + LIP_GH, 0.5
    outer = hull_of((pts(o(Z_C, 0.4)), Z_C - 0.01), (pts(o(zt, 0.4)), zt))
    inner = hull_of((pts(o(Z_C - e, -0.4)), Z_C - e), (pts(o(zt + e, -0.4)), zt + e))
    return U([base, D(outer, inner)])


def build_thumbturn(x, y, arm_dir):
    """flush quarter-turn: grip ridge flush with the flat bottom inside a Ø26 dish, face disc bears on the dish floor,
    shaft through the boss, arm under the box post when closed (shown closed); O-ring groove (8x1.5) in the boss"""
    ridge = box(-8.0, 8.0, -2.0, 2.0, Z_BOT + 0.05, TT_DISH_FLOOR - 1.15)
    face = U([cyl(TT_FACE_D, TT_DISH_FLOOR - 1.2, TT_DISH_FLOOR - 0.05, 64),
              hull_of((circle_pts(TT_FACE_D, 64), TT_DISH_FLOOR - 0.06), (circle_pts(TT_SHAFT_D, 64), TT_CONE_TOP - 0.05))])
    shaft = cyl(TT_SHAFT_D, TT_DISH_FLOOR - 0.1, TT_ARM_Z1 - TT_ARM_T + 0.01, 48)
    arm = U([cyl(TT_SHAFT_D, TT_ARM_Z1 - TT_ARM_T, TT_ARM_Z1, 48), box(0, TT_ARM_L, -TT_ARM_W / 2, TT_ARM_W / 2, TT_ARM_Z1 - TT_ARM_T, TT_ARM_Z1)])
    dimple = trimesh.creation.icosphere(subdivisions=2, radius=0.9)
    dimple.apply_translation([TT_ARM_L - 2.5, 0, TT_ARM_Z1])
    m = D(U([ridge, face, shaft, rotz(arm, arm_dir)]), [rotz(dimple, arm_dir)])
    zg = TT_OR_Z
    m = D(m, [D(cyl(TT_SHAFT_D + 1, zg - 0.85, zg + 0.85, 48), cyl(TT_SHAFT_D - 2.4, zg - 1, zg + 1, 48))])
    m.apply_translation([x, y, 0])
    return m


# =====================================================================================
# BOUGHT PARTS (placeholders)
# =====================================================================================
def tube_path(pts, r=3.0, n=16):
    segs = []
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = np.asarray(p, float), np.asarray(q, float)
        v = q - p
        c = trimesh.creation.cylinder(radius=r, height=np.linalg.norm(v), sections=n)
        c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / np.linalg.norm(v)))
        c.apply_translation((p + q) / 2)
        segs.append(c)
        s = trimesh.creation.icosphere(subdivisions=1, radius=r)
        s.apply_translation(q)
        segs.append(s)
    return U(segs)


CABLE_PTS = [(-3.0, -60.0, -48.0), (-2.0, -61.0, -28.0), (8.0, -61.0, -15.0), (44.0, -42.0, -15.0), (54.0, -40.0, -4.0), (58.0, -36.0, 8.0),
             (66.0, -27.0, 40.0), (CABLE_XY[0], CABLE_XY[1], 60.0), (CABLE_XY[0], CABLE_XY[1], 110.0)]
CONN = ((12.0, -59.0, -15.0), (38.0, -45.4, -15.0))       # inline IP67 2-pin connector, under the bowl, above the box


def bought61():
    B = {}
    sv = rotz(dt.servo_solid, 90.0)
    sv.apply_translation([0, 0, v6.DZ_SERVO])
    B['servo'] = sv
    B['board_70x50'] = box(BB['x'][0], BB['x'][1], BB['y'][0], BB['y'][1], BB['z'][0], BB['z'][1])
    zc = (BB['z'][0] + BB['z'][1]) / 2
    x1b = BB['x'][1]
    zt, zl = BB['z'][1] - 2.0, BB['z'][0] + 11.0          # ESP32 in the upper band, regulators + capacitor in the lower band
    B['esp32'] = box(x1b, x1b + 14.0, -31.0, 24.0, zt - 28.0, zt)
    B['reg_12v_d36v50f6'] = box(x1b, x1b + 8.0, -30.0, -4.6, zl - 9.0, zl + 9.0)
    B['reg_5v_logic'] = box(x1b, x1b + 6.0, 0.0, 10.0, zl - 5.0, zl + 5.0)
    cap = trimesh.creation.cylinder(radius=5.0, height=13.0, sections=32)
    cap.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    cap.apply_translation([x1b + 6.6, 19.0, zl])
    B['cap_1000uF'] = cap
    g = Point(GLAND['x'], GLAND['z'])
    yf = BXO[2]
    B['gland_m12'] = U([yprism(g.buffer(7.6, resolution=6), yf - GLAND['pad_t'] - 7.0, yf - GLAND['pad_t'] + 0.01),
                        yprism(g.buffer(6.0, resolution=32), yf - GLAND['pad_t'] - 16.0, yf - GLAND['pad_t'] - 6.99),
                        yprism(g.buffer(5.9, resolution=32), yf - GLAND['pad_t'], yf + 5.0),
                        yprism(g.buffer(8.6, resolution=6), yf + BX_T + 0.01, yf + BX_T + 4.0)])
    vx, vy = VENT['x'], VENT['y']
    B['vent_m12_eptfe'] = U([at(cyl(15.0, Z_R - 0.01, Z_R + 6.0, 6), vx, vy), at(cyl(14.0, Z_R + 5.99, Z_R + 11.0, 32), vx, vy),
                             at(cyl(11.8, Z_R - ROOF_T - 4.0, Z_R + 0.01, 32), vx, vy), at(cyl(17.0, Z_R - ROOF_T - 4.0, Z_R - ROOF_T - 0.01, 6), vx, vy)])
    B['oring_shaft_9x2'] = U([v6.torus(dt.OR_GROOVE_D / 2 + 1.0, 1.0, z) for z in v6.OR_SHAFT_Z])
    B['oring_face_24x2'] = v6.torus(v6.FACE_OR['id'] / 2 + 1.0, 1.0, Z_R + 1.0)
    zg = (TT_DISH_FLOOR + TT_BOSS_TOP) / 2
    B['oring_tt_8x1.5'] = v6.torus(4.0 + 0.6, 0.75, zg, x=TT[2][0], y=TT[2][1])
    B['cable_12v'] = tube_path(CABLE_PTS, 3.0)
    B['connector_ip67'] = tube_path(list(CONN), 7.0, 24)
    sc = {}
    sc['wood_5x25'] = U([at(U([cyl(5.0, FL_Z0 - 0.01 + v5.WOOD_CB_H, FL_Z1 + 18.0, 24), cyl(9.5, FL_Z0 - 0.5, FL_Z0 + v5.WOOD_CB_H, 32)]), x, y) for x, y in WOOD_XY])
    sc['m3x12_tower_top'] = U([v6.screw_m3(x, y, -v6.TOP_LOBE_T, 12) for x, y in TWR_INS])
    sc['m3x10_tower_box'] = U([v6.screw_m3(x, y, v6.COL_FL_Z1, 10, head_up=True) for x, y in BOT_INS61])
    sc['m3x10_chute'] = U([v6.screw_m3(x, y, -CH_FL_T, 10) for x, y in CH_EARS])
    sc['m3x12_shell_tabs'] = U([v6.screw_m3(x, y, -TAB_T, 12) for x, y in TAB_INS])
    tz = dt.TAB_Z0 + v6.DZ_SERVO
    sc['m3x8_servo'] = U([at(U([cyl(3.0, tz - 0.01, tz + 8.0 - dt.WASHER_T, 24), cyl(7.0, tz - dt.WASHER_T, tz, 32), cyl(5.5, tz - dt.WASHER_T - 3.0, tz - dt.WASHER_T, 32)]), x, y)
                          for x, y in SERVO_HOLES_W])
    sc['m3x8_hub'] = v6.screw_m3(0, 0, v6.HUB_SCREW_HEAD_Z, v6.HUB_SCREW_LEN, head_up=True)
    sc['inserts_bowl'] = U([at(cyl(4.0, 0.2, 5.9, 24), x, y) for x, y in TWR_INS + CH_EARS + TAB_INS])
    sc['inserts_box'] = U([at(cyl(4.0, Z_R - 5.9, Z_R - 0.2, 24), x, y) for x, y in BOT_INS61] +
                          [at(cyl(4.0, CAGE_Z0 + 0.2, CAGE_Z0 + 5.9, 24), x, y) for x, y in SERVO_HOLES_W])
    return B, sc


# =====================================================================================
# BUILD / EXPORT
# =====================================================================================
def build_all():
    P, COLOUR, EXTRA = {}, {}, {}
    F = funnel61()
    P['chiocciola_v61'] = build_bowl61(F)
    P['scivolo_v61'] = build_chute61(F)
    P['piastra_gate_v61'] = build_gate61()
    P['piastra_finestra_v61'] = build_window61()
    P['disco_v61'], d_or, d_bk, EXTRA['portion_g'], EXTRA['ribs2d'] = build_disc61()
    L, EXTRA['lip_len'], EXTRA['flap_len'] = build_lips61()
    P['labbro_uscita_v61'] = L['labbro_uscita_v61_1']           # the 2 outlet lips are mirror twins: export one design each side
    P['labbro_uscita_v61_b'] = L['labbro_uscita_v61_2']
    P['labbro_finestra_v61'] = L['labbro_finestra_v61_1']
    P['labbro_finestra_v61_b'] = L['labbro_finestra_v61_2']
    P['guarnizione_baionetta_v61'], EXTRA['rim_lip_L'], EXTRA['rim_lip_tip'] = build_rim_gasket61()
    P['colonna_v61'] = build_column61()
    cav = v6.fl_funnel_cavity()
    v6.COLLAR_PINS = v6.collar_pin_sites(cav)
    EXTRA['FL_CAV'] = cav
    P['flangia_piano_v61'] = build_flange61(cav)
    P['passacavo_v61'] = build_grommet()
    P['scatola_v61'] = build_box61()
    P['guscio_v61'], EXTRA['btn_r_out'] = build_shell61()
    P['pulsante_v61'] = build_button61(EXTRA['btn_r_out'])
    P['fondello_v61'] = build_cap61()
    P['guarnizione_fondello_v61'] = build_cap_gasket61()
    tts = [build_thumbturn(x, y, a) for (x, y), a in zip(TT, TT_ARM_DIR)]
    P['nottolino_v61'] = tts[2]
    EXTRA['tts'] = tts
    EXTRA['F'] = F
    for k, m in P.items():
        COLOUR[k] = [({'scivolo_v61': 'green', 'pulsante_v61': 'orange', 'nottolino_v61': 'orange'}.get(k, 'yellow' if (k.startswith('guarn') or k.startswith('labbro') or k.startswith('passa')) else 'black'), m)]
    COLOUR['disco_v61'] = [('orange', d_or), ('black', d_bk)]
    # plates: green food bands on the top faces (as v4b)
    win_band = WIN_T.buffer(bd.RIM_BAND, resolution=32).difference(WIN_T)
    wb, wg = split(P['piastra_finestra_v61'], face_region(win_band.union(text_poly('FOOD IN →', 6, -30, 0)).union(text_poly(VER, 4, -30, -9)), W1, True))
    out_band = rotz_poly(OUT_T.buffer(bd.RIM_BAND, resolution=32).difference(OUT_T), 180).intersection(Point(0, 0).buffer(bd.GATE_R - 0.8))
    gb, gg = split(P['piastra_gate_v61'], face_region(out_band.union(text_poly('← OUT', 6, 30, 0)).union(text_poly(VER, 4, 30, -9)), G1, True))
    COLOUR['piastra_finestra_v61'] = [('black', wb), ('green', wg)]
    COLOUR['piastra_gate_v61'] = [('black', gb), ('green', gg)]
    return P, COLOUR, EXTRA


FLIP = {'chiocciola_v61': False, 'scivolo_v61': True, 'piastra_gate_v61': False, 'piastra_finestra_v61': True, 'disco_v61': True,
        'labbro_uscita_v61': False, 'labbro_uscita_v61_b': False, 'labbro_finestra_v61': True, 'labbro_finestra_v61_b': True,
        'guarnizione_baionetta_v61': False, 'colonna_v61': False, 'flangia_piano_v61': True, 'passacavo_v61': True, 'scatola_v61': True,
        'guscio_v61': False, 'pulsante_v61': None, 'fondello_v61': False, 'guarnizione_fondello_v61': False, 'nottolino_v61': True}
PRINT_TXT = {
    'chiocciola_v61': 'as assembled, flat base on the bed; supports only under the 3 bayonet lugs (as v4b/v6); deeper rim groove (2.2) prints as a plain channel',
    'scivolo_v61': 'flipped: joint flange on the bed, tube rises vertically, morph faces >= 51 deg; drip-edge chamfer is the last layers; no supports; PETG green',
    'piastra_gate_v61': 'as assembled, bottom face on the bed; green OUT band in the top 3 layers',
    'piastra_finestra_v61': 'flipped, top face on the bed (green FOOD IN band in the first 3 layers)',
    'disco_v61': 'flipped: disc top on the bed (black label first 3 layers); sweeper ribs (0.6) and sleeve grow up; no supports',
    'labbro_uscita_v61': 'as modelled: anchor on the bed, flap rises at 40 deg; TPU 95A, 0.4 nozzle, slits 0.7 = one gap; print 1 of each side',
    'labbro_uscita_v61_b': 'as labbro_uscita_v61 (other edge)',
    'labbro_finestra_v61': 'flipped: anchor on the bed, flap rises at 40 deg; TPU 95A',
    'labbro_finestra_v61_b': 'as labbro_finestra_v61 (other edge)',
    'guarnizione_baionetta_v61': 'as assembled: foot on the bed, riser + 0.5 flap rising at 42 deg; TPU 95A, 1 perimeter for the flap, slow',
    'colonna_v61': 'as colonna_v6 (lobed flange on the bed); only the bottom lobes moved 215 -> 235 deg',
    'flangia_piano_v61': 'flipped: shelf face on the bed; skirt, hooks, pins grow up (hooks are 4 mm ledges, optional support)',
    'passacavo_v61': 'flipped: top face on the bed; TPU 95A',
    'scatola_v61': 'flipped: flat roof on the bed (no support wedge any more); walls, cradle, rails, posts grow up; L-brackets have 45 deg gussets',
    'guscio_v61': 'as assembled? NO: seam edge (z -72) on the bed, rim up; outer wall leans out <= 40 deg near the bed, tabs carried by 45 deg webs, '
                  'push-button bore is a 14 mm horizontal hole (bridges); no supports; 5 perimeters (2.0 wall), PETG black, 0.2 layers',
    'pulsante_v61': 'standing on its head face (Ø14), 45 deg collar chamfer, plunger up; PETG orange, 100 % infill',
    'fondello_v61': 'as assembled: flat bottom on the bed (outer face = bed face); the lowest 4.4 mm of the R15 bottom edge overhang > 45 deg '
                    '-> bed-only support ring or accept a slight droop; upstand, outlet tube, bosses, spigot ring grow up',
    'guarnizione_fondello_v61': 'as assembled: base on the bed, lip up; TPU 95A',
    'nottolino_v61': 'flipped: arm top on the bed (detent dimple = first layers), shaft, 45 deg cone, face disc and grip ridge grow up; print 3, PETG orange, 100 % infill'}
RHO = {k: (TPU if (k.startswith('guarn') or k.startswith('labbro') or k.startswith('passa')) else PETG) for k in FLIP}


def to_print61(m, name):
    p = m.copy()
    if name == 'pulsante_v61':                         # stand it on its head face: radial axis -> -Z
        p.apply_transform(trimesh.transformations.rotation_matrix(-math.radians(LATCH_A), [0, 0, 1]))
        p.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif name == 'guscio_v61':
        pass                                          # seam edge is the lowest face already (z -72)
    elif FLIP[name]:
        p.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    p.apply_translation([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]])
    return p


def export_part(name, m, bodies):
    m = v6.clean(m)
    m.export(OUT + f'{name}.stl'); m.export(OUT + f'{name}.3mf')
    wt = bool(trimesh.load(OUT + f'{name}.stl').is_watertight)
    pm = to_print61(m, name)
    T = np.linalg.lstsq(np.c_[m.vertices[:4], np.ones(4)], np.c_[pm.vertices[:4], np.ones(4)], rcond=None)[0].T
    sc = trimesh.Scene()
    for c, b in bodies:
        pb = v6.clean(b).copy()
        pb.apply_transform(T)
        if len(bodies) > 1:
            pb.export(OUT + f'{name}_print_{c}.stl')
        sc.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
    sc.export(OUT + f'{name}_print.3mf'); pm.export(OUT + f'{name}_print.stl')
    return wt, pm


if __name__ == '__main__':
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    v6.SCRATCH = SCRATCH
    print(f'funnel bottom z {ZB} (min slope {_ZB_SLOPE}), chute axis x {CH_X}, airlock margin {airlock_check()} deg')
    P, COLOUR, EXTRA = build_all()
    print('\n--- new parts ---')
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
    print('down-facing area flatter than 45 deg in print orientation (mm2):', OVH)
    if STAGE == 'parts':
        sys.exit(0)
    exec(open(dt.HERE + 'build_v61_checks.py').read())
