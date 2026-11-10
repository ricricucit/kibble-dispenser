#!/usr/bin/env python3
"""
Simplified assembly v5 of the kibble dispenser: shelf -> flangia_piano_v5 (bayonet flange + funnel neck + 4 legs)
-> dosing module v4b (unchanged) -> scatola_v5 (enclosure in axis under the module, wet chimney for the chute)
-> fondello_v5 (bottom cover, 6 screws, breadboard rails).  Servo in axis (albero_mozzo + passante_culla v4), no gears.

Frame: Z-up mm, X=Y=0 shaft axis, Z=0 = enclosure roof top = bowl base underside (dosing frame).
Reused parts are loaded from their validated STL exports and never rebuilt here.
"""
import json
import math
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, Point, box as sbox, LineString
from shapely import affinity
from scipy.spatial import Delaunay

import build_drivetrain as dt           # geometry only: culla, albero, servo_solid, helpers
import build_dosing as bd               # geometry only: window outline, helpers, text

OUT = dt.OUT
U, D, I = dt.U, dt.D, dt.I
cyl, box, at, prism, hull_of, circle_pts, revolve = dt.cyl, dt.box, dt.at, dt.prism, dt.hull_of, dt.circle_pts, dt.revolve
rotz, text_poly, face_region, split, to_print, overhang, grams, vol = (bd.rotz, bd.text_poly, bd.face_region, bd.split,
                                                                      bd.to_print, bd.overhang, bd.grams, bd.vol)
SEG = dt.SEG
VER = 'v5'
DOSING = json.load(open(OUT + 'dosing.json'))
BAY = DOSING['bayonet']


def load(name):
    m = trimesh.load(OUT + name + '.stl')
    assert m.is_watertight, name
    return m


def report(name, m):
    print(f'{name:26s} watertight={m.is_watertight}  volume={m.volume/1000:8.3f} cm3  '
          f'x[{m.bounds[0,0]:.1f},{m.bounds[1,0]:.1f}] y[{m.bounds[0,1]:.1f},{m.bounds[1,1]:.1f}] '
          f'z[{m.bounds[0,2]:.2f},{m.bounds[1,2]:.2f}]  faces={len(m.faces)}')
    assert m.is_watertight and m.volume > 0, name


def rrect(x0, x1, y0, y1, r):
    return sbox(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=16)


def ring2d(outer, inner):
    return outer.difference(inner)


def sector2d(r0, r1, a0, a1, n=48):
    a = np.radians(np.linspace(a0, a1, n))
    pts = np.r_[np.c_[r1 * np.cos(a), r1 * np.sin(a)], np.c_[r0 * np.cos(a[::-1]), r0 * np.sin(a[::-1])]] if r0 > 0 \
        else np.r_[[[0, 0]], np.c_[r1 * np.cos(a), r1 * np.sin(a)]]
    return Polygon(pts)


def prism(poly, z0, z1):
    """extrude a (Multi)Polygon; multipolygons are unioned part by part"""
    if isinstance(poly, Polygon):
        return dt.prism(poly, z0, z1)
    return U([dt.prism(g, z0, z1) for g in poly.geoms if isinstance(g, Polygon) and g.area > 0.05])


def xprism(poly_yz, x0, x1):
    """prism of a polygon drawn in (y, z) extruded along X"""
    m = trimesh.creation.extrude_polygon(poly_yz, height=x1 - x0)      # built in (u=y, v=z, w=x)
    T = np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    m.apply_transform(T)
    return m


def heightfield_solid(outline, ztop, zbot, step=6.0):
    """solid under a height function over a CONVEX outline: top z = ztop(x, y), bottom z = zbot(x, y) (or constant)."""
    ring = np.array(outline.exterior.coords)[:-1]
    # densify the boundary
    bpts = []
    for i in range(len(ring)):
        p, q = ring[i], ring[(i + 1) % len(ring)]
        n = max(1, int(np.linalg.norm(q - p) / 3.0))
        for t in np.linspace(0, 1, n, endpoint=False):
            bpts.append(p + t * (q - p))
    bpts = np.array(bpts)
    minx, miny, maxx, maxy = outline.bounds
    gx, gy = np.meshgrid(np.arange(minx + step / 2, maxx, step), np.arange(miny + step / 2, maxy, step))
    g = np.c_[gx.ravel(), gy.ravel()]
    inside = outline.buffer(-1.5).contains(shapely.points(g))
    pts = np.vstack([bpts, g[inside]])
    tri = Delaunay(pts).simplices
    cen = pts[tri].mean(axis=1)
    keep = outline.buffer(0.05).contains(shapely.points(cen))
    tri = tri[keep]
    zt = np.array([ztop(x, y) for x, y in pts])
    zb = np.array([zbot(x, y) for x, y in pts]) if callable(zbot) else np.full(len(pts), float(zbot))
    nb = len(bpts)
    V = np.vstack([np.c_[pts, zt], np.c_[pts, zb]])
    # ensure top triangles are CCW (normal up)
    def ccw(t):
        a, b, c = pts[t[0]], pts[t[1]], pts[t[2]]
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0
    F = []
    for t in tri:
        t = list(t) if ccw(t) else [t[0], t[2], t[1]]
        F.append(t)
        F.append([t[0] + len(pts), t[2] + len(pts), t[1] + len(pts)])
    for i in range(nb):
        j = (i + 1) % nb
        F += [[i, i + len(pts), j + len(pts)], [i, j + len(pts), j]]
    m = trimesh.Trimesh(V, np.array(F), process=True)
    m.fix_normals()
    if m.volume < 0:
        m.invert()
    assert m.is_watertight, 'heightfield not watertight'
    return m


# =====================================================================================
# REUSED PARTS (validated, loaded as-is)
# =====================================================================================
# the exported STL/3MF lose watertightness in the float round trip, so the v4b parts are regenerated by the
# validated build_dosing functions (same code, same parameters) instead of being reloaded from disk
Z_BOT, _SLOPE = bd.pick_z_bot()
bd.TUBE_END_Z = Z_BOT - bd.COLLAR_L
_bowl, _chute_cav, _chute_out = bd.build_bowl(Z_BOT)
_disc, _pc = bd.build_disc()
R = {'chiocciola_scivolo_v4b': _bowl, 'piastra_gate_v4b': bd.build_gate(), 'piastra_finestra_v4b': bd.build_window_plate(),
     'disco_v4b': _disc, 'linguetta_sicura': bd.build_latch(), 'ghiera_valvola': bd.build_ring(),
     'valvola_becco': bd.build_valve(), 'guarnizione_baionetta': bd.build_gasket()}
R.update(bd.build_lips())
REUSE = list(R)
R['albero_mozzo'] = dt.albero
R['passante_culla'] = dt.culla
SERVO = dt.servo_solid
bowl = R['chiocciola_scivolo_v4b']


def chute_section(z, grow=0.0):
    """outer outline of the chute at height z (world XY), optionally buffered"""
    T = np.eye(4); T[2, 3] = -z
    s = bowl.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p2, _ = s.to_2D(to_2D=T)
    u = shapely.unary_union([q.buffer(0) for q in p2.polygons_full])
    u = u.buffer(grow, resolution=16) if grow else u
    return u if isinstance(u, Polygon) else max(u.geoms, key=lambda g: g.area)


# =====================================================================================
# PARAMETERS
# =====================================================================================
# ---- bayonet interface (from dosing.json) ----
RIM_Z = BAY['rim_top_z']                                  # 66
FL_Z0 = BAY['gasket']['flange_underside_z_locked']        # 66.1
FL_T = 6.0
FL_Z1 = FL_Z0 + FL_T                                      # 72.1 = shelf underside
HOOK_R0, HOOK_R1 = BAY['flange_hooks']['inner_r'], BAY['flange_hooks']['outer_r_min']   # 62.5 / 66.5
HOOK_Z1 = BAY['flange_hooks']['top_face_z_bowl_frame_locked']                           # 55.5
HOOK_T = 3.5
HOOK_Z0 = HOOK_Z1 - HOOK_T                                # 52.0
SKIRT_R0, SKIRT_R1 = HOOK_R1, 70.0                        # full ring r 66.5..70 (lugs pass inside it)
LUG_INS = BAY['lugs']['insert_angles_deg']
LUG_W = BAY['lugs']['widths_deg']
LOCK_ROT = BAY['lock_rotation_deg']
# hook spans: end = lug trailing edge +1 (as specified); start = max(spec start + 3, insertion footprint end + 1):
# the 32 deg key lug is wider than the 30 deg lock rotation, and the latch nub (76.5 +-3.7 deg) must clear the
# 90 deg hook at insertion -> hooks support 19-30 of the 22-32 deg lug widths
HOOKS = []
for a, w in zip(LUG_INS, LUG_W):
    lock = a + LOCK_ROT
    start = max(lock - w / 2 + 2.0, a + w / 2 + 1.0)
    HOOKS.append((round(start, 1), round(lock + w / 2 + 1.0, 1)))
TONGUE_R0, TONGUE_R1, TONGUE_H = 60.2, 61.2, 2.0          # bowl rim labyrinth tongue
LGROOVE_R0, LGROOVE_R1, LGROOVE_D = 59.7, 61.7, 2.5       # flange groove for it
# ---- shelf, funnel neck ----
SHELF_HOLE_D = 76.0                                       # bi-metal hole saw
HOLE_C = (27.0, 0.0)
NECK_OD, NECK_H, NECK_WALL = SHELF_HOLE_D - 3.0, 12.0, 2.0
NECK_Z1 = FL_Z1 + NECK_H                                  # 84.1
WEEP_N, WEEP_W, WEEP_H = 6, 3.0, 2.0
OPEN_MARGIN_R, OPEN_MARGIN_ANG = 2.0, 2.0
SHELF_T = 20.0                                            # drawn shelf (15..40 ok)
# ---- flange plate, legs, wood screws, gasket ----
PL_X, PL_Y, PL_R = (-121.0, 96.0), (-66.0, 66.0), 10.0
LEG_XY = [(-109.0, -53.0), (-109.0, 53.0), (84.0, -53.0), (84.0, 53.0)]
LEG_D, LEG_FILLET = 12.0, 5.0
WOOD_XY = [(-80.0, -45.0), (-80.0, 45.0), (60.0, -50.0), (60.0, 50.0)]
WOOD_D, WOOD_CB_D, WOOD_CB_H = 5.2, 10.5, 2.0
GSK_W, GSK_H, GRV_W, GRV_D = 2.0, 2.0, 2.8, 1.5           # 2x2 TPU in a 2.8 x 1.5 groove (fill 95 %, proud 0.5)
FL_GSK_R = 41.0                                           # gasket ring centre radius around the shelf hole
INS_D, INS_DEPTH, INS_L = 4.0, 7.5, 5.7                   # M3 heat-set insert (Ruthex RX-M3x5.7)
# ---- enclosure ----
WALL, ROOF_T = 3.0, 3.0
WX, WY = (-100.0, 75.0), (-43.0, 103.0)                   # wall outer
IX, IY = (WX[0] + WALL, WX[1] - WALL), (WY[0] + WALL, WY[1] - WALL)
WALL_R = 6.0
ROOF_X, ROOF_Y, ROOF_R = (-119.0, 93.0), (-63.0, 107.0), 8.0
SLOPE_DEG = 2.5
DRIP_W, DRIP_H = 1.5, 1.5
BOX_Z0 = -71.0                                            # wall bottom edge = cover top
RIM_OUT, RIM_H = 8.0, 10.0
LEG_BOSS_D, LEG_BOSS_H = 16.0, 8.0
CHUTE_AX = tuple(BAY['chute_drop_zone']['axis_xy'])       # (-56.5, 0)
CH_R_IN, CH_FLAT_X, CH_WALL = 34.0, -24.0, 3.0             # chimney bore: r 34 clipped at x=-24 (passante cage at -19)
LIP_R0, LIP_Z0, LIP_Z1 = 30.0, -15.5, -13.5                # collar nubs (r 29.5, z -17.5..-16) pass; TPU ring seat
COLLAR_R = 28.0
CRING_ID, CRING_OD, CRING_T = 55.4, 63.0, 2.0              # guarnizione_collare_v5 stretched on the collar
CUT_GROW, REBATE_GROW, REBATE_D = 2.0, 4.0, 2.0            # roof cutout = chute section (z -1.5) + 2; rebate + 4, 2 deep
CGSK_T, CGSK_INT = 2.8, 0.3                                # chute gasket 2.8 tall (0.8 proud), 0.3 interference on the chute
GLAND = dict(wall='+X', y=20.0, z=-38.0, hole_d=16.2, pad_d=30.0, pad_t=2.0)
# ---- cover ----
CV_T, SKIRT_T, SKIRT_H, SKIRT_CLR = 4.0, 2.0, 6.0, 0.4
LIP_T, LIP_H, LIP_CLR = 1.5, 4.0, 0.3
CV_Z0, CV_Z1 = BOX_Z0 - CV_T, BOX_Z0                      # -75..-71
N_SCREWS = 6
BB = dict(x=(-94.0, 71.0), y=(40.0, 95.0), t=10.0)         # breadboard 165 x 55 x ~10 on the cover rails
RAIL_W, RAIL_H = 2.5, 4.0
INLAY = 0.6
PETG = 1.27

# =====================================================================================
# FLANGIA_PIANO_v5
# =====================================================================================
w_c = bd.coords_of(bd.WIN_TOP)
WIN_HALF = float(np.degrees(np.arctan2(w_c[:, 1], w_c[:, 0])).max())
WIN_RMAX = float(np.hypot(w_c[:, 0], w_c[:, 1]).max())
OPEN_R = WIN_RMAX + OPEN_MARGIN_R
OPEN_HALF = WIN_HALF + OPEN_MARGIN_ANG
OPENING = sector2d(0.0, OPEN_R, -OPEN_HALF, OPEN_HALF, 96).buffer(-3.0, resolution=16).buffer(3.0, resolution=16)


def funnel_cavity():
    """ruled morph: neck top circle (z NECK_Z1) -> pie opening (z FL_Z0); extended 1 mm beyond both faces"""
    r_top = NECK_OD / 2 - NECK_WALL
    core = bd.funnel_morph(OPENING, FL_Z0, HOLE_C[0], r_top, NECK_Z1, levels=18, n=128)
    ext = U([core, prism(OPENING, FL_Z0 - 1.0, FL_Z0 + 0.02), cyl(2 * r_top, NECK_Z1 - 0.02, NECK_Z1 + 1.0, SEG, )
             .apply_translation([HOLE_C[0], HOLE_C[1], 0])])
    return ext


def build_flange():
    plate = prism(rrect(*PL_X, *PL_Y, PL_R), FL_Z0, FL_Z1)
    neck = at(cyl(NECK_OD, FL_Z1 - 0.01, NECK_Z1), *HOLE_C)
    skirt = D(cyl(2 * SKIRT_R1, HOOK_Z0, FL_Z0 + 0.01), cyl(2 * SKIRT_R0, HOOK_Z0 - 1, FL_Z0 + 1))
    tongues = [bd.sector_solid(a0, a1, HOOK_R0, SKIRT_R1 - 0.5, HOOK_Z0, HOOK_Z1, 24) for a0, a1 in HOOKS]
    legs = []
    for x, y in LEG_XY:
        legs.append(at(cyl(LEG_D, 0.0, FL_Z0 + 0.01, 64), x, y))
        legs.append(at(hull_of((circle_pts(LEG_D, 64), FL_Z0 - LEG_FILLET), (circle_pts(LEG_D + 2 * LEG_FILLET, 64), FL_Z0 + 0.01)), x, y))
    body = U([plate, neck, skirt] + tongues + legs)
    cuts = [funnel_cavity(),
            # labyrinth groove for the rim tongue
            D(cyl(2 * LGROOVE_R1, FL_Z0 - 1, FL_Z0 + LGROOVE_D), cyl(2 * LGROOVE_R0, FL_Z0 - 2, FL_Z0 + LGROOVE_D + 1)),
            # top gasket groove around the shelf hole
            at(D(cyl(2 * FL_GSK_R + GRV_W, FL_Z1 - GRV_D, FL_Z1 + 1), cyl(2 * FL_GSK_R - GRV_W, FL_Z1 - GRV_D - 1, FL_Z1 + 2)), *HOLE_C)]
    # weep slots through the neck base: the annulus hole-wall/neck drains into the funnel
    for k in range(WEEP_N):
        a = 360.0 * k / WEEP_N + 30.0
        s = box(NECK_OD / 2 - NECK_WALL - 6.0, NECK_OD / 2 + 1.0, -WEEP_W / 2, WEEP_W / 2, FL_Z1, FL_Z1 + WEEP_H)
        cuts.append(at(rotz(s, a), *HOLE_C))
    for x, y in WOOD_XY:
        cuts.append(at(U([cyl(WOOD_D, FL_Z0 - 1, FL_Z1 + 1, 32), cyl(WOOD_CB_D, FL_Z0 - 1, FL_Z0 + WOOD_CB_H, 48)]), x, y))
    for x, y in LEG_XY:
        cuts.append(at(cyl(INS_D, -1.0, INS_DEPTH, 48), x, y))
    ver = face_region(affinity.scale(text_poly(VER, 6.0, -95.0, 0.0), -1, 1, origin=(-95.0, 0.0)), FL_Z0, False)  # deboss, read from below
    cuts.append(ver)
    return D(body, cuts)


def build_flange_gasket():
    g = at(D(cyl(2 * FL_GSK_R + GSK_W, FL_Z1 - GRV_D, FL_Z1 - GRV_D + GSK_H), cyl(2 * FL_GSK_R - GSK_W, FL_Z1 - 5, FL_Z1 + 5)), *HOLE_C)
    return g


# =====================================================================================
# SCATOLA_v5
# =====================================================================================
WALL_OUT = rrect(*WX, *WY, WALL_R)
WALL_IN = rrect(*IX, *IY, WALL_R - WALL)
ROOF_OUT = rrect(*ROOF_X, *ROOF_Y, ROOF_R)
RIM_OUT_P = rrect(WX[0] - RIM_OUT, WX[1] + RIM_OUT, WY[0] - RIM_OUT, WY[1] + RIM_OUT, WALL_R + RIM_OUT)
CUTOUT = chute_section(-1.5, CUT_GROW)
REBATE = chute_section(-1.5, REBATE_GROW)
PLATEAU = shapely.unary_union([Point(0, 0).buffer(63.0, resolution=64), chute_section(-1.5, REBATE_GROW + 3.0)]).convex_hull
TAN_S = math.tan(math.radians(SLOPE_DEG))
BORE = Point(*CHUTE_AX).buffer(CH_R_IN, resolution=96).intersection(sbox(-200, -100, CH_FLAT_X, 100))
BORE_OUT = BORE.buffer(CH_WALL, join_style=2, resolution=16)


def ztop(x, y, off=0.0):
    p = Point(x, y)
    d = 0.0 if PLATEAU.contains(p) else PLATEAU.exterior.distance(p)
    return -TAN_S * d + off


def build_box():
    block = heightfield_solid(ROOF_OUT, ztop, BOX_Z0)
    cavity = heightfield_solid(WALL_IN, lambda x, y: ztop(x, y, -ROOF_T), BOX_Z0 - 10)
    eave_void = D(heightfield_solid(ROOF_OUT.buffer(1.0), lambda x, y: ztop(x, y, -ROOF_T), BOX_Z0 - 10), prism(WALL_OUT, BOX_Z0 - 20, 5))
    shell = D(block, [cavity, eave_void])
    drip = I(prism(ring2d(ROOF_OUT, ROOF_OUT.buffer(-DRIP_W)), -10, 1), heightfield_solid(ROOF_OUT, ztop, lambda x, y: ztop(x, y, -ROOF_T - DRIP_H)))
    rim = prism(ring2d(RIM_OUT_P, WALL_IN), BOX_Z0, BOX_Z0 + RIM_H)
    chim = U([prism(ring2d(BORE_OUT, BORE), BOX_Z0, LIP_Z1), prism(ring2d(BORE_OUT, Point(*CHUTE_AX).buffer(LIP_R0, resolution=96)), LIP_Z0, LIP_Z1)])
    bosses = []
    for x, y in LEG_XY:
        bosses.append(at(cyl(LEG_BOSS_D, -LEG_BOSS_H, 0.0, 64), x, y))
        # rib to the nearest wall
        if x < WX[0]:
            bosses.append(box(x, WX[0] + 1.0, y - 4.0, y + 4.0, -LEG_BOSS_H, -0.5))
        else:
            bosses.append(box(WX[1] - 1.0, x, y - 4.0, y + 4.0, -LEG_BOSS_H, -0.5))
        if y < WY[0]:
            bosses.append(box(x - 4.0, x + 4.0, y, WY[0] + 1.0, -LEG_BOSS_H, -0.5))
    # gland pad on the +X wall
    gy, gz = GLAND['y'], GLAND['z']
    pad = xprism(Point(gy, gz).buffer(GLAND['pad_d'] / 2, resolution=64), WX[1] - 1.0, WX[1] + GLAND['pad_t'])
    body = U([shell, drip, rim, chim, pad] + bosses)
    cuts = [prism(CUTOUT, -ROOF_T - 1, 1), prism(REBATE, -REBATE_D, 1),
            cyl(dt.LID_HOLE_D, -ROOF_T - 1, 1)]          # the chimney ring is built hollow: no separate bore cut (avoids coplanar slivers)
    for x, y in dt.LID_HOLES:         # passante screws: countersunk from the roof top, into the passante inserts
        cuts.append(at(U([cyl(dt.LID_SCREW_HOLE_D, -ROOF_T - 1, 1, 32),
                          hull_of((circle_pts(dt.LID_SCREW_HOLE_D, 32), -(dt.LID_CSK_D - dt.LID_SCREW_HOLE_D) / 2),
                                  (circle_pts(dt.LID_CSK_D, 32), 0.0), (circle_pts(dt.LID_CSK_D, 32), 1.0))]), x, y))
    for x, y in LEG_XY:
        cuts.append(at(cyl(3.4, -LEG_BOSS_H - 1, 1, 32), x, y))
    # gland hole (teardrop: 45 deg roof, prints without support)
    tear = Point(gy, gz).buffer(GLAND['hole_d'] / 2, resolution=48).union(Point(gy, gz + GLAND['hole_d'] / 2 * math.sqrt(2) - 0.01).buffer(0.01)).convex_hull
    cuts.append(xprism(tear, WX[1] - WALL - 1, WX[1] + GLAND['pad_t'] + 1))
    # cover screw inserts: blind from below in the rim
    for x, y in screw_xy():
        cuts.append(at(cyl(INS_D, BOX_Z0 - 1, BOX_Z0 + INS_DEPTH, 48), x, y))
    return D(body, cuts)


def screw_xy():
    c = RIM_OUT / 2 + WALL / 2            # rim centreline offset from the wall outer face
    xs, ys = (WX[0] - c + WALL / 2, WX[1] + c - WALL / 2), (WY[0] - c + WALL / 2, WY[1] + c - WALL / 2)
    xs = (WX[0] - RIM_OUT / 2, WX[1] + RIM_OUT / 2)
    ys = (WY[0] - RIM_OUT / 2, WY[1] + RIM_OUT / 2)
    pts = [(xs[0], ys[0]), (xs[0], ys[1]), (xs[1], ys[0]), (xs[1], ys[1]), ((xs[0] + xs[1]) / 2, ys[0]), ((xs[0] + xs[1]) / 2, ys[1])]
    return pts


def build_chute_gasket():
    inner = chute_section(-1.0, -CGSK_INT)
    outer = chute_section(-1.5, REBATE_GROW - 0.4)
    g = prism(outer.difference(inner), -REBATE_D, -REBATE_D + CGSK_T)
    # compressed representation under the bowl base (r < 62.5): top at z 0
    g = D(g, D(cyl(125.0, -0.001, 5.0), cyl(0.1, -1, 6)))
    return g


def build_collar_ring():
    return at(D(cyl(CRING_OD, LIP_Z1, LIP_Z1 + CRING_T, SEG), cyl(CRING_ID, LIP_Z1 - 1, LIP_Z1 + 5, SEG)), *CHUTE_AX)


# =====================================================================================
# FONDELLO_v5
# =====================================================================================
def build_cover():
    cv_out = RIM_OUT_P.buffer(SKIRT_CLR + SKIRT_T, join_style=1, resolution=16)
    plate = prism(cv_out, CV_Z0, CV_Z1)
    skirt = prism(ring2d(cv_out, RIM_OUT_P.buffer(SKIRT_CLR, join_style=1, resolution=16)), CV_Z1 - 0.01, CV_Z1 + SKIRT_H)
    lip_in = WALL_IN.buffer(-LIP_CLR, join_style=1, resolution=16)
    lip = prism(ring2d(lip_in, lip_in.buffer(-LIP_T, join_style=1, resolution=16)), CV_Z1 - 0.01, CV_Z1 + LIP_H)
    bore_in = BORE.buffer(-LIP_CLR, join_style=2)
    clip = prism(ring2d(bore_in, bore_in.buffer(-LIP_T, join_style=2)), CV_Z1 - 0.01, CV_Z1 + LIP_H)
    rails = [box(BB['x'][0] + 4.0, BB['x'][1] - 4.0, BB['y'][0] - RAIL_W, BB['y'][0], CV_Z1 - 0.01, CV_Z1 + RAIL_H),
             box(BB['x'][0] + 4.0, BB['x'][1] - 4.0, BB['y'][1], BB['y'][1] + RAIL_W, CV_Z1 - 0.01, CV_Z1 + RAIL_H)]
    body = U([plate, skirt, lip, clip] + rails)
    # gasket grooves: under the wall centreline and under the chimney wall centreline
    wc = WALL_OUT.buffer(-WALL / 2, join_style=1, resolution=16)
    g1 = ring2d(wc.buffer(GRV_W / 2, join_style=1, resolution=16), wc.buffer(-GRV_W / 2, join_style=1, resolution=16))
    cc = BORE.buffer(CH_WALL / 2, join_style=2)
    g2 = ring2d(cc.buffer(GRV_W / 2, join_style=2), cc.buffer(-GRV_W / 2, join_style=2))
    cuts = [prism(g1, CV_Z1 - GRV_D, CV_Z1 + 1), prism(g2, CV_Z1 - GRV_D, CV_Z1 + 1),
            prism(bore_in.buffer(-LIP_T, join_style=2), CV_Z0 - 1, CV_Z1 + LIP_H + 1)]
    for x, y in screw_xy():
        cuts.append(at(U([cyl(3.4, CV_Z0 - 1, CV_Z1 + 1, 32), cyl(6.2, CV_Z0 - 1, CV_Z0 + 2.0, 48)]), x, y))
    # orange inlays on the outer face (read from below -> mirrored in world X)
    rings = shapely.unary_union([Point(x, y).buffer(5.5, resolution=32).difference(Point(x, y).buffer(3.6, resolution=32)) for x, y in screw_xy()])
    txt = text_poly('OPEN HERE', 9.0, -12.5, 78.0).union(text_poly('v5', 7.0, -12.5, 62.0))
    arrows = shapely.unary_union([text_poly('↓', 9.0, x, y + 9.0) for x, y in screw_xy() if y < 0] +
                                 [text_poly('↑', 9.0, x, y - 9.0) for x, y in screw_xy() if y > 0])
    orange2d = affinity.scale(rings.union(txt).union(arrows), -1, 1, origin=(0, 0))
    orange_rg = face_region(orange2d, CV_Z0, False)
    cover = D(body, cuts)
    black, orange = split(cover, orange_rg)
    return cover, black, orange


def build_cover_gasket():
    wc = WALL_OUT.buffer(-WALL / 2, join_style=1, resolution=16)
    g1 = ring2d(wc.buffer(GSK_W / 2, join_style=1, resolution=16), wc.buffer(-GSK_W / 2, join_style=1, resolution=16))
    cc = BORE.buffer(CH_WALL / 2, join_style=2)
    g2 = ring2d(cc.buffer(GSK_W / 2, join_style=2), cc.buffer(-GSK_W / 2, join_style=2))
    return prism(g1, CV_Z1 - GRV_D, CV_Z1 - GRV_D + GSK_H), prism(g2, CV_Z1 - GRV_D, CV_Z1 - GRV_D + GSK_H)


if __name__ == '__main__':
    import sys
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    print('hooks (deg):', HOOKS, ' opening: r', round(OPEN_R, 1), 'half', round(OPEN_HALF, 1))
    print('\n--- building new parts ---')
    flange = build_flange(); report('flangia_piano_v5', flange)
    fl_gsk = build_flange_gasket(); report('guarnizione_piano_v5', fl_gsk)
    scat = build_box(); report('scatola_v5', scat)
    ch_gsk = build_chute_gasket(); report('guarnizione_scivolo_v5', ch_gsk)
    cring = build_collar_ring(); report('guarnizione_collare_v5', cring)
    cover, cover_black, cover_orange = build_cover(); report('fondello_v5', cover)
    cv_g1, cv_g2 = build_cover_gasket(); report('guarnizione_fondello_v5[rim]', cv_g1); report('guarnizione_fondello_v5[chimney]', cv_g2)

    # ---------------- export (first version, before checks) ----------------
    BODIES = {'flangia_piano_v5': (flange, [('black', flange)], True),
              'scatola_v5': (scat, [('black', scat)], True),
              'fondello_v5': (cover, [('black', cover_black), ('orange', cover_orange)], False),
              'guarnizione_piano_v5': (fl_gsk, [('yellow', fl_gsk)], False),
              'guarnizione_scivolo_v5': (ch_gsk, [('yellow', ch_gsk)], False),
              'guarnizione_collare_v5': (cring, [('yellow', cring)], False),
              'guarnizione_fondello_v5': (U([cv_g1, cv_g2]), [('yellow', cv_g1), ('yellow_chimney', cv_g2)], False)}
    PRINT_TXT = {
        'flangia_piano_v5': 'flipped: neck top on the bed, legs + hooks up; supports under the shelf face (12 mm) and under the 3 hook tongues',
        'scatola_v5': 'flipped: roof top on the bed (plateau flat, 2.5 deg slope needs a thin support wedge: slicer "on build plate only"), walls, rim and chimney up; supports inside the chimney under the lip (z 13.5..15.5 in print)',
        'fondello_v5': 'as printed: outer face on the bed (orange inlays first 3 layers), skirt, lips and rails up; no supports',
        'guarnizione_piano_v5': 'flat ring, TPU 95A, 100 % infill',
        'guarnizione_scivolo_v5': 'flat, TPU 95A, 100 % infill (D-shaped ring)',
        'guarnizione_collare_v5': 'flat ring, TPU 95A; stretched over the collar nubs from below, rests on the chimney lip',
        'guarnizione_fondello_v5': 'two flat loops (rim frame + chimney ring), TPU 95A, in one print'}
    def candidates(m):
        yield m
        for digits in (5, 4):
            c = m.copy()
            c.merge_vertices(digits_vertex=digits)
            c.update_faces(c.nondegenerate_faces(height=1e-6))
            c.remove_unreferenced_vertices()
            if not c.is_watertight:
                trimesh.repair.fill_holes(c)
            if c.is_watertight:
                c.fix_normals()
                yield c

    def clean(m):
        """export is float32: pick the variant whose STL reloads as a watertight volume"""
        for c in candidates(m):
            c.export(OUT + '_v5_probe.stl')
            if trimesh.load(OUT + '_v5_probe.stl').is_watertight:
                return c
        print('  WARNING: no watertight export variant found, exporting as built')
        return m

    PR, OVH, GR = {}, {}, {}
    for name, (m, bodies, flip) in BODIES.items():
        m = clean(m)
        bodies = [(c, clean(b)) for c, b in bodies]
        m.export(OUT + f'{name}.stl'); m.export(OUT + f'{name}.3mf')
        chk = trimesh.load(OUT + f'{name}.stl')
        EXPORT_WT = globals().setdefault('EXPORT_WT', {}); EXPORT_WT[name] = bool(chk.is_watertight)
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
        sc.export(OUT + f'{name}_print.3mf'); pm.export(OUT + f'{name}_print.stl')
        PR[name], OVH[name] = pm, round(overhang(pm), 1)
        GR[name] = grams(m, 1.21 if bodies[0][0].startswith('yellow') else PETG)
    print('exported; down-facing area flatter than 45 deg (mm2):', OVH)
    print('grams (solid, est.):', GR)
    if STAGE == 'parts':
        sys.exit(0)
    exec(open(dt.HERE + 'build_v5_checks.py').read())
