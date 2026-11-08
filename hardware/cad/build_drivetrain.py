#!/usr/bin/env python3
"""
Drivetrain v3 for the kibble dispenser: disc + hub/shaft + sealed bushing + spline test coupons.

Frame: Z-up, mm. Z=0 = top face of the box lid. X=Y=0 on the shaft axis.
Every part is built at its assembled height; the print STLs are re-oriented on z=0.
Booleans: trimesh + manifold3d (engine='manifold').

Run from anywhere:  python hardware/cad/build_drivetrain.py
Outputs (paths relative to this script's folder):
  ../stl/<part>.stl        print-ready, oriented for the bed
  ../3mf/<part>.3mf        at assembled height (frame above)
  build/<part>.stl         at assembled height, plus build/check_section.png (not committed)
  drivetrain.json          parameters, hardware list and checks
"""
import json
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
STL_DIR, MF_DIR, BUILD = HERE.parent / 'stl', HERE.parent / '3mf', HERE / 'build'
for _d in (STL_DIR, MF_DIR, BUILD):
    _d.mkdir(parents=True, exist_ok=True)
LAYOUT = json.load(open(HERE / 'layout_v3.json'))

# =====================================================================================
# PARAMETERS
# =====================================================================================
SEG = 128                      # facets on round features (disc rim uses 2x)

# ---- disco_v3 ----
DISC_D, DISC_Z0, DISC_Z1 = 103.0, 32.0, 36.0
TRAP_Y_IN, TRAP_W_IN = 9.0, 16.0        # short base at y=9
TRAP_Y_OUT, TRAP_W_OUT = 43.0, 35.0     # long base at y=43
TRAP_R = 3.0                            # corner radius
TRAP_CH_TOP, TRAP_CH_BOT = 1.5, 0.7     # 45 deg chamfers on the hole edges
BOSS_D, BOSS_Z0 = 16.0, 24.0            # boss from z=24 to the disc bottom (z=32)
POCKET_AF = 8.2                         # hex pocket across flats (0.1/flat on an 8.0 hex)
POCKET_DEPTH = 6.0                      # from z=24 up -> pocket top z=30
BORE_D = 3.4                            # M3 clearance through everything
CBORE_D, CBORE_DEPTH = 6.2, 3.2         # DIN912 M3 head 5.5 x 3.0 -> head 0.2 below the top face

# ---- albero_mozzo (hub + shaft) ----
HUB_D, HUB_Z0, HUB_Z1 = 24.0, -18.5, -8.5
SPL_TEETH, SPL_TIP_D, SPL_ROOT_D = 25, 5.90, 5.30
SPL_CLEAR = 0.10                        # radial clearance: tip & root radii of the socket each + SPL_CLEAR
SPL_DEPTH = 4.5                         # socket ceiling at z=-14 = spline tip
SPL_CHAMFER = 0.4                       # 45 deg entry chamfer at the hub bottom
SHAFT_D, SHAFT_Z1 = 12.0, 24.0          # round shaft z=-8.5..24, shoulder at z=24
HEX_AF = 8.0
HEX_LEN = POCKET_DEPTH - 0.5            # 0.5 mm air above the hex in the pocket
HEX_CHAMFER = 0.5
OR_GROOVE_D = 9.4                       # SPEC SAID 10.2 -> 106% gland fill / 45% squeeze in the 12.4 bore (see notes)
OR_GROOVE_W = 2.7                       # flat-bottom width; 45 deg cone above it up to the shaft OD
OR_GROOVE_Z = (-4.5, 0.5)               # groove centres (O-ring NBR 10x2)

# ---- passante_stagno (sealed bushing) ----
FL_D, FL_Z0, FL_Z1 = 50.0, -7.5, -3.5     # was 44 (layout); enlarged so the screws sit inside the face seal
COLLAR_D, COLLAR_Z1 = 21.5, 4.0
BUSH_BORE_D = 12.4
BUSH_BORE_CH_BOT = 1.0                  # lead-in for the shaft O-rings (shaft enters from below)
BUSH_BORE_CH_TOP = 0.4
# face seal OUTSIDE the screws: NBR O-ring 40x2 (ID 40, CS 2), seated on the inner wall with ~1% stretch
FACE_OR_SIZE = (40.0, 2.0)
FACE_OR_ID, FACE_OR_OD, FACE_OR_DEPTH = 40.4, 45.6, 1.5   # width 2.6, depth 1.5 -> 25% squeeze, ~80% fill
INS_D, INS_R = 4.0, 15.5
MIN_WALL_INS, MIN_WALL_EDGE = 2.5, 2.0
INS_DEPTH = FL_Z1 - FL_Z0               # SPEC SAID 6 deep; flange is only 4 thick -> through hole
INS_ANGLES = (90.0, 210.0, 330.0)       # one insert on +Y (disc-hole side), 120 deg apart

# ---- screw ----
SCREW_STD = (50, 45, 55, 60)            # preferred first
SCREW_HEAD_D, SCREW_HEAD_H = 5.5, 3.0
SPLINE_TIP_Z = LAYOUT['servo']['spline_tip_z']
TIP_BELOW = (3.0, 6.0)                  # screw tip must land 3..6 mm below the spline tip
MIN_SOLID = 2.5                         # material between pocket top and counterbore bottom

# ---- test_scanalato ----
CP_D, CP_H = 14.0, 6.0
CP_CLEARS = (0.05, 0.10, 0.20)          # 1 / 2 / 3 notches
CP_PITCH = 18.0
NOTCH_W, NOTCH_DEPTH, NOTCH_STEP = 1.2, 1.0, 22.0

COLORS = {'disco_v3': '#E9E5DC', 'albero_mozzo': '#E8792B',
          'passante_stagno': '#3A6EA5', 'test_scanalato': '#9AA0A6'}

# sanity vs layout
assert LAYOUT['disc_v3'].items() >= {"bottom_z": DISC_Z0, "top_z": DISC_Z1, "d": DISC_D, "boss_d": BOSS_D,
                                     "boss_z": [BOSS_Z0, DISC_Z0]}.items()   # layout may carry extra keys
assert LAYOUT['hub'] == {"z": [HUB_Z0, HUB_Z1], "d": HUB_D}
assert LAYOUT['shaft']['d'] == SHAFT_D and LAYOUT['shaft']['round_z'] == [HUB_Z1, SHAFT_Z1]
assert LAYOUT['bushing']['flange_z'] == [FL_Z0, FL_Z1] and LAYOUT['bushing']['bore_d'] == BUSH_BORE_D

# =====================================================================================
# SCREW RULE
# =====================================================================================
CBORE_BOT = DISC_Z1 - CBORE_DEPTH
POCKET_TOP = BOSS_Z0 + POCKET_DEPTH
assert CBORE_BOT - POCKET_TOP >= MIN_SOLID, 'not enough material above the hex pocket'
SCREW_LEN = None
for _len in SCREW_STD:
    below = SPLINE_TIP_Z - (CBORE_BOT - _len)
    if TIP_BELOW[0] <= below <= TIP_BELOW[1]:
        SCREW_LEN = _len
        break
assert SCREW_LEN is not None, 'no standard M3 length fits'
SCREW_TIP_Z = CBORE_BOT - SCREW_LEN
print(f'screw M3x{SCREW_LEN}: head {CBORE_BOT}..{CBORE_BOT+SCREW_HEAD_H} (top face {DISC_Z1}), '
      f'tip z={SCREW_TIP_Z} ({SPLINE_TIP_Z-SCREW_TIP_Z:.1f} below spline tip), '
      f'solid above pocket {CBORE_BOT-POCKET_TOP:.1f}')

# =====================================================================================
# HELPERS
# =====================================================================================
U = lambda ms: trimesh.boolean.union(ms, engine='manifold')
D = lambda a, b: trimesh.boolean.difference([a, b] if not isinstance(b, list) else [a] + b, engine='manifold')
I = lambda a, b: trimesh.boolean.intersection([a, b], engine='manifold')


def cyl(d, z0, z1, n=SEG):
    m = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=n)
    m.apply_translation([0, 0, (z0 + z1) / 2])
    return m


def prism(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, height=z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def ring(p):
    return np.array(p.exterior.coords)[:-1]


def hull_of(*layers):
    """convex hull of planar rings [(poly_or_pts, z), ...]"""
    P = []
    for p, z in layers:
        a = ring(p) if isinstance(p, Polygon) else np.asarray(p)
        P.append(np.c_[a, np.full(len(a), z)])
    return trimesh.convex.convex_hull(np.vstack(P))


def circle_pts(d, n=SEG):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[d / 2 * np.cos(a), d / 2 * np.sin(a)]


def hexagon(af):
    rc = af / np.sqrt(3)                 # circumradius; vertices on +-X, flats normal to +-Y
    a = np.radians(np.arange(6) * 60.0)
    return Polygon(np.c_[rc * np.cos(a), rc * np.sin(a)])


def spline_socket_poly(c):
    """25T triangular-tooth socket: male star with tip and root radii each grown by c."""
    k = np.arange(2 * SPL_TEETH)
    a = k * np.pi / SPL_TEETH
    r = np.where(k % 2 == 0, SPL_TIP_D / 2 + c, SPL_ROOT_D / 2 + c)
    return Polygon(np.c_[r * np.cos(a), r * np.sin(a)])


def spline_socket_cutter(c, z_mouth, depth):
    """socket opening downward at z_mouth, ceiling at z_mouth+depth, 45 deg entry chamfer."""
    teeth = prism(spline_socket_poly(c), z_mouth - 1.0, z_mouth + depth)
    r_out = SPL_TIP_D / 2 + c
    over = 0.5
    cham = hull_of((circle_pts(2 * (r_out + SPL_CHAMFER + over), 96), z_mouth - over),
                   (circle_pts(2 * r_out, 96), z_mouth + SPL_CHAMFER))
    return U([teeth, cham])


def report(name, m):
    print(f'{name:18s} watertight={m.is_watertight}  volume={m.volume/1000:7.3f} cm3  '
          f'z=[{m.bounds[0,2]:.2f}, {m.bounds[1,2]:.2f}]  faces={len(m.faces)}')
    assert m.is_watertight and m.volume > 0


# =====================================================================================
# 1. DISCO v3
# =====================================================================================
T = DISC_Z1 - DISC_Z0
bufr = dict(join_style=1, resolution=24)
nom = Polygon([(-TRAP_W_IN / 2, TRAP_Y_IN), (TRAP_W_IN / 2, TRAP_Y_IN),
               (TRAP_W_OUT / 2, TRAP_Y_OUT), (-TRAP_W_OUT / 2, TRAP_Y_OUT)]
              ).buffer(-TRAP_R, **bufr).buffer(TRAP_R, **bufr)
plate = cyl(DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG)
trap_cut = U([prism(nom, DISC_Z0 - 1, DISC_Z1 + 1),
              hull_of((nom, DISC_Z1 - TRAP_CH_TOP), (nom.buffer(TRAP_CH_TOP, **bufr), DISC_Z1)),
              hull_of((nom.buffer(TRAP_CH_BOT, **bufr), DISC_Z0), (nom, DISC_Z0 + TRAP_CH_BOT))])
plate = D(plate, trap_cut)
disc = U([plate, cyl(BOSS_D, BOSS_Z0, DISC_Z0 + 0.5)])
disc = D(disc, [cyl(BORE_D, BOSS_Z0 - 1, DISC_Z1 + 1, 48),
                cyl(CBORE_D, CBORE_BOT, DISC_Z1 + 1, 64),
                prism(hexagon(POCKET_AF), BOSS_Z0 - 1, POCKET_TOP)])
disc.process(validate=True)

# =====================================================================================
# 2. ALBERO + MOZZO
# =====================================================================================
HEX_Z1 = SHAFT_Z1 + HEX_LEN
hx = hexagon(HEX_AF)
hex_body = hull_of((hx, SHAFT_Z1 - 0.2), (hx, HEX_Z1 - HEX_CHAMFER),
                   (hexagon(HEX_AF - 2 * HEX_CHAMFER), HEX_Z1))
shaft = U([cyl(HUB_D, HUB_Z0, HUB_Z1), cyl(SHAFT_D, HUB_Z1 - 0.2, SHAFT_Z1), hex_body])
rg, ro = OR_GROOVE_D / 2, SHAFT_D / 2 + 0.5
groove_cuts = []
for zc in OR_GROOVE_Z:
    z_lo, z_hi = zc - OR_GROOVE_W / 2, zc + OR_GROOVE_W / 2
    prof = np.array([[rg, z_lo], [ro, z_lo], [ro, z_hi + (ro - rg)], [rg, z_hi], [rg, z_lo]])
    groove_cuts.append(trimesh.creation.revolve(prof, sections=SEG))
albero = D(shaft, groove_cuts + [cyl(BORE_D, HUB_Z0 - 1, HEX_Z1 + 1, 48),
                                 spline_socket_cutter(SPL_CLEAR, HUB_Z0, SPL_DEPTH)])
albero.process(validate=True)

# =====================================================================================
# 3. PASSANTE STAGNO
# =====================================================================================
bush = U([cyl(FL_D, FL_Z0, FL_Z1), cyl(COLLAR_D, FL_Z1 - 0.2, COLLAR_Z1)])
cb, ctp = BUSH_BORE_CH_BOT, BUSH_BORE_CH_TOP
bore_cut = U([cyl(BUSH_BORE_D, FL_Z0 - 1, COLLAR_Z1 + 1),
              hull_of((circle_pts(BUSH_BORE_D + 2 * (cb + 0.5)), FL_Z0 - 0.5),
                      (circle_pts(BUSH_BORE_D), FL_Z0 + cb)),
              hull_of((circle_pts(BUSH_BORE_D), COLLAR_Z1 - ctp),
                      (circle_pts(BUSH_BORE_D + 2 * (ctp + 0.5)), COLLAR_Z1 + 0.5))])
face_groove = D(cyl(FACE_OR_OD, FL_Z1 - FACE_OR_DEPTH, FL_Z1 + 0.01),
                cyl(FACE_OR_ID, FL_Z1 - FACE_OR_DEPTH - 1, FL_Z1 + 1))
inserts = []
for ang in INS_ANGLES:
    h = cyl(INS_D, FL_Z1 - INS_DEPTH - (1 if INS_DEPTH >= FL_Z1 - FL_Z0 else 0), FL_Z1 + 1, 48)
    h.apply_translation([INS_R * np.cos(np.radians(ang)), INS_R * np.sin(np.radians(ang)), 0])
    inserts.append(h)
passante = D(bush, [bore_cut, face_groove] + inserts)
passante.process(validate=True)

# =====================================================================================
# 4. TEST SCANALATO (print-ready, socket on the bed)
# =====================================================================================
coupons = []
for i, c in enumerate(CP_CLEARS):
    body = cyl(CP_D, 0, CP_H, 96)
    cuts = [spline_socket_cutter(c, 0.0, SPL_DEPTH), cyl(BORE_D, -1, CP_H + 1, 48)]
    n = i + 1
    for j in range(n):
        ang = np.radians(90 + (j - (n - 1) / 2) * NOTCH_STEP)
        b = trimesh.creation.box(extents=[NOTCH_DEPTH * 2, NOTCH_W, CP_H + 2])
        b.apply_translation([CP_D / 2, 0, CP_H / 2])
        b.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 0, 1]))
        cuts.append(b)
    cp = D(body, cuts)
    cp.apply_translation([(i - 1) * CP_PITCH, 0, 0])
    cp.process(validate=True)
    coupons.append(cp)
test = trimesh.util.concatenate(coupons)

# =====================================================================================
# EXPORT
# =====================================================================================
def to_print(m, flip=False):
    p = m.copy()
    if flip:
        p.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    p.apply_translation([0, 0, -p.bounds[0, 2]])
    return p


parts = {'disco_v3': (disc, True), 'albero_mozzo': (albero, False), 'passante_stagno': (passante, False)}
print('\n--- meshes ---')
for name, (m, flip) in parts.items():
    report(name, m)
    m.export(BUILD / f'{name}.stl')
    m.export(MF_DIR / f'{name}.3mf')
    p = to_print(m, flip)
    report(name + '_print', p)
    p.export(STL_DIR / f'{name}.stl')
for c, m in zip(CP_CLEARS, coupons):
    report(f'coupon c={c}', m)
report('test_scanalato', test)
test.export(BUILD / 'test_scanalato.stl')
test.export(STL_DIR / 'test_scanalato.stl')
sc = trimesh.Scene()
for c, m in zip(CP_CLEARS, coupons):
    sc.add_geometry(m, geom_name=f'spline_c{int(round(c*100)):03d}')
sc.export(MF_DIR / 'test_scanalato.3mf')

# =====================================================================================
# CHECKS
# =====================================================================================
print('\n--- interference (intersection volume, mm3) ---')
pairs = [('disco_v3', 'albero_mozzo'), ('albero_mozzo', 'passante_stagno'), ('disco_v3', 'passante_stagno')]
inter = {}
for a, b in pairs:
    x = I(parts[a][0], parts[b][0])
    v = float(abs(x.volume)) if len(x.faces) else 0.0
    inter[f'{a}|{b}'] = round(v, 6)
    print(f'{a:16s} x {b:16s}: {v:.6f}')
    assert v < 1e-3
screw = U([cyl(3.0, SCREW_TIP_Z, CBORE_BOT, 32), cyl(SCREW_HEAD_D, CBORE_BOT, CBORE_BOT + SCREW_HEAD_H, 48)])
for n, (m, _) in parts.items():
    v = I(m, screw).volume if len(I(m, screw).faces) else 0.0
    print(f'screw x {n:16s}: {v:.6f}')
    assert v < 1e-3
# hex fit: clearance per flat, axial gap
print(f'hex {HEX_AF} AF in pocket {POCKET_AF} AF: {(POCKET_AF-HEX_AF)/2:.2f}/flat, '
      f'axial gap {POCKET_TOP-HEX_Z1:.2f} mm; hub top->flange gap {FL_Z0-HUB_Z1:.2f} mm')
# O-ring glands
gland = (BUSH_BORE_D - OR_GROOVE_D) / 2
or_area = np.pi * 1.0 ** 2
print(f'shaft O-ring 10x2: gland {gland:.2f} mm, squeeze {(2-gland)/2*100:.0f}%, '
      f'fill {or_area/(OR_GROOVE_W*gland)*100:.0f}%  (spec 10.2 would be '
      f'{(2-(BUSH_BORE_D-10.2)/2)/2*100:.0f}% / {or_area/(OR_GROOVE_W*(BUSH_BORE_D-10.2)/2)*100:.0f}%)')
fw = (FACE_OR_OD - FACE_OR_ID) / 2
f_id, f_cs = FACE_OR_SIZE
stretch = FACE_OR_ID / f_id - 1
cs_eff = f_cs * (1 - 0.5 * stretch)                     # CS shrink ~ half the stretch
FACE_SQUEEZE = (cs_eff - FACE_OR_DEPTH) / cs_eff
FACE_FILL = np.pi * (cs_eff / 2) ** 2 / (fw * FACE_OR_DEPTH)
WALL_INS_COLLAR = INS_R - INS_D / 2 - COLLAR_D / 2
WALL_INS_GROOVE = FACE_OR_ID / 2 - (INS_R + INS_D / 2)
WALL_GROOVE_EDGE = FL_D / 2 - FACE_OR_OD / 2
print(f'face O-ring {f_id:.0f}x{f_cs:.0f}: groove ID {FACE_OR_ID} OD {FACE_OR_OD} (w {fw:.2f}) depth {FACE_OR_DEPTH}, '
      f'stretch {stretch*100:.1f}%, squeeze {FACE_SQUEEZE*100:.0f}%, fill {FACE_FILL*100:.0f}%')
print(f'walls: insert->collar {WALL_INS_COLLAR:.2f}, insert->groove {WALL_INS_GROOVE:.2f}, groove->flange edge '
      f'{WALL_GROOVE_EDGE:.2f} mm')
assert WALL_INS_COLLAR >= MIN_WALL_INS and WALL_INS_GROOVE >= MIN_WALL_INS and WALL_GROOVE_EDGE >= MIN_WALL_EDGE
assert 0.20 <= FACE_SQUEEZE <= 0.30 and FACE_FILL < 0.85
# lid skirt (box wall continues up into the lid, z -25..0): distance from axis to its inner faces
bx = LAYOUT['box']
ax_x, ax_y = LAYOUT['shaft_axis_xy']
SKIRT_DIST = {'-Y': ax_y - (bx['outer_y'][0] + bx['wall']), '+Y': (bx['outer_y'][1] - bx['wall']) - ax_y,
              '-X': ax_x - (bx['outer_x'][0] + bx['wall']), '+X': (bx['outer_x'][1] - bx['wall']) - ax_x}
SKIRT_CLASH = {k: round(FL_D / 2 - v, 2) for k, v in SKIRT_DIST.items() if FL_D / 2 > v}
print('axis -> lid skirt inner wall:', {k: round(v, 2) for k, v in SKIRT_DIST.items()},
      '| flange r', FL_D / 2, '-> CLASH (mm into wall):' if SKIRT_CLASH else '-> clear', SKIRT_CLASH or '')

# =====================================================================================
# SECTION RENDER
# =====================================================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Polygon as MPoly, Rectangle

render = [('disco_v3', disc), ('albero_mozzo', albero), ('passante_stagno', passante)]
keep = trimesh.creation.box(extents=[200, 400, 400]); keep.apply_translation([100, 0, 0])   # keep x>=0
fig = plt.figure(figsize=(16, 9), facecolor='white')
ax = fig.add_subplot(1, 2, 1, projection='3d')
light = np.array([-0.6, -0.3, 0.75]); light /= np.linalg.norm(light)
tris, cols = [], []
for name, m in render:
    h = I(m, keep)
    base = np.array(matplotlib.colors.to_rgb(COLORS[name]))
    if name == 'disco_v3':
        base = base * 0.85
    sh = 0.35 + 0.65 * np.clip(h.face_normals @ light, 0, 1)
    tris.append(h.triangles)
    cols.append(np.clip(base[None, :] * sh[:, None], 0, 1))
pc = Poly3DCollection(np.vstack(tris), facecolors=np.vstack(cols), edgecolors='none', linewidths=0)
ax.add_collection3d(pc)
ax.set_xlim(-50, 50); ax.set_ylim(-50, 50); ax.set_zlim(-30, 40)
ax.set_box_aspect((100, 100, 70))
ax.view_init(elev=18, azim=-160)
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title('Assembled drivetrain, cut at X=0 (half X>=0 kept)')

ax2 = fig.add_subplot(1, 2, 2)
T2 = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)   # (x,y,z)->(y,z)
for name, m in render:
    s = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    p2, _ = s.to_2D(to_2D=T2)
    for poly in p2.polygons_full:
        ext = np.array(poly.exterior.coords)
        ax2.add_patch(MPoly(ext, closed=True, fc=COLORS[name], ec='k', lw=0.6, alpha=0.95, zorder=3))
        for hole in poly.interiors:
            ax2.add_patch(MPoly(np.array(hole.coords), closed=True, fc='white', ec='k', lw=0.6, zorder=4))
# context: lid plate (hole assumed 22), bowl floor (hole 22), screw, spline
for z0, z1, lab in [(-LAYOUT['box']['lid_plate_t'], 0, 'lid (hole assumed Ø22)'),
                    (LAYOUT['camera']['floor_z'][0], LAYOUT['camera']['floor_z'][1], 'bowl floor Ø22')]:
    for sgn in (-1, 1):
        x0 = sgn * 11
        ax2.add_patch(Rectangle((min(x0, x0 + sgn * 45), z0), 45, z1 - z0, fc='#DDDDDD', ec='#888888',
                                hatch='///', lw=0.5, zorder=1))
    ax2.text(57, (z0 + z1) / 2, lab, va='center', fontsize=8)
# lid skirt wall on the -Y side (box wall, from layout) -- shows any flange clash
yw = -SKIRT_DIST['-Y']
ax2.add_patch(Rectangle((yw - bx['wall'], -bx['lid_skirt']), bx['wall'], bx['lid_skirt'], fc='#F4B6B6', ec='#B03030',
                        lw=0.8, alpha=0.6, zorder=6))
ax2.text(yw - bx['wall'] - 0.5, -bx['lid_skirt'] + 0.5, f'lid skirt wall\n(axis {SKIRT_DIST["-Y"]:.0f} mm)',
         ha='right', va='bottom', fontsize=7, color='#B03030')
ax2.add_patch(Rectangle((-1.5, SCREW_TIP_Z), 3.0, CBORE_BOT - SCREW_TIP_Z, fc='#555555', alpha=0.55, zorder=5))
ax2.add_patch(Rectangle((-SCREW_HEAD_D / 2, CBORE_BOT), SCREW_HEAD_D, SCREW_HEAD_H, fc='#555555', alpha=0.55, zorder=5))
ax2.add_patch(Rectangle((-SPL_TIP_D / 2, -20), SPL_TIP_D, 6, fc='#B0B0B0', ec='#555555', alpha=0.6, zorder=2))
ax2.axhline(SPLINE_TIP_Z, color='r', lw=0.6, ls='--'); ax2.text(-56, SPLINE_TIP_Z + 0.4, 'spline tip z=-14', color='r', fontsize=8)
ax2.axhline(SCREW_TIP_Z, color='m', lw=0.6, ls=':'); ax2.text(-56, SCREW_TIP_Z - 1.6, f'M3x{SCREW_LEN} tip z={SCREW_TIP_Z:.1f}', color='m', fontsize=8)
ax2.set_xlim(-58, 70); ax2.set_ylim(-24, 40); ax2.set_aspect('equal')
ax2.set_xlabel('Y [mm]'); ax2.set_ylabel('Z [mm]'); ax2.grid(alpha=0.3)
ax2.set_title('Section X=0 (YZ plane); trapezoid hole on +Y')
handles = [Rectangle((0, 0), 1, 1, fc=COLORS[n], ec='k') for n, _ in render]
ax2.legend(handles, [n for n, _ in render], loc='center right', fontsize=8)
plt.tight_layout()
plt.savefig(BUILD / 'check_section.png', dpi=110)
plt.close(fig)

# =====================================================================================
# JSON
# =====================================================================================
params = {k: v for k, v in globals().items()
          if k.isupper() and len(k) > 1 and isinstance(v, (int, float, tuple)) and k not in ('SEG',)}
rnd = lambda v: round(v, 4) if isinstance(v, float) else v
params = {k: ([rnd(x) for x in v] if isinstance(v, tuple) else rnd(v)) for k, v in params.items()}
doc = {
    'frame': 'Z-up mm, Z=0 = lid top face, X=Y=0 = shaft axis; main files at assembled height',
    'shaft_axis_world_xy': LAYOUT['shaft_axis_xy'],
    'parameters': params,
    'screw': {'spec': f'M3x{SCREW_LEN} DIN912', 'head_z': [CBORE_BOT, CBORE_BOT + SCREW_HEAD_H],
              'tip_z': round(SCREW_TIP_Z, 3), 'tip_below_spline_tip_mm': round(SPLINE_TIP_Z - SCREW_TIP_Z, 3),
              'pocket_depth': POCKET_DEPTH, 'hex_len': HEX_LEN,
              'solid_above_pocket_mm': round(CBORE_BOT - POCKET_TOP, 3)},
    'hardware': ['1x M3x%d DIN912' % SCREW_LEN, '2x O-ring NBR 10x2 (shaft)',
                 '1x O-ring NBR %dx%d (face seal, outside the screws)' % FACE_OR_SIZE,
                 '3x M3 heat-set insert, short (<=4 mm long, hole 4.0)',
                 '3x M3 screw from above through bowl floor + lid (M3x10 with a 3 mm insert); inside the sealed zone, no washers needed'],
    'face_seal': {'oring': '%dx%d NBR' % FACE_OR_SIZE, 'groove_id': FACE_OR_ID, 'groove_od': FACE_OR_OD,
                  'groove_width': round(fw, 3), 'groove_depth': FACE_OR_DEPTH, 'stretch_pct': round(stretch * 100, 1),
                  'squeeze_pct': round(FACE_SQUEEZE * 100, 1), 'fill_pct': round(FACE_FILL * 100, 1),
                  'insert_r': INS_R, 'walls_mm': {'insert_to_collar': round(WALL_INS_COLLAR, 2),
                                                  'insert_to_groove': round(WALL_INS_GROOVE, 2),
                                                  'groove_to_flange_edge': round(WALL_GROOVE_EDGE, 2)}},
    'files_note': 'paths relative to hardware/: stl/ = print-ready, 3mf/ = assembled height',
    'parts': {
        'disco_v3': {'files': ['stl/disco_v3.stl', '3mf/disco_v3.3mf'], 'color': COLORS['disco_v3'],
                     'print': 'top face on bed (boss up), PETG food-contact', 'volume_cm3': round(disc.volume / 1000, 3)},
        'albero_mozzo': {'files': ['stl/albero_mozzo.stl', '3mf/albero_mozzo.3mf'],
                         'color': COLORS['albero_mozzo'], 'print': 'hub on bed, 100% infill / >=6 walls (core Ø9.4 at grooves)',
                         'volume_cm3': round(albero.volume / 1000, 3)},
        'passante_stagno': {'files': ['stl/passante_stagno.stl', '3mf/passante_stagno.3mf'],
                            'color': COLORS['passante_stagno'], 'print': 'flange on bed',
                            'volume_cm3': round(passante.volume / 1000, 3)},
        'test_scanalato': {'files': ['stl/test_scanalato.stl', '3mf/test_scanalato.3mf'],
                           'color': COLORS['test_scanalato'], 'print': 'as is, socket on bed',
                           'coupons': {f'{n+1} notch(es)': c for n, c in enumerate(CP_CLEARS)}},
    },
    'checks': {'watertight': {n: bool(m.is_watertight) for n, (m, _) in parts.items()} | {'test_scanalato': bool(test.is_watertight)},
               'intersection_mm3': inter},
    'spec_changes': {
        'OR_GROOVE_D': 'spec 10.2 -> 9.4: with bore 12.4 the 10.2 groove gives 45% squeeze and 106% gland fill; 9.4 gives 25% / 78%',
        'FACE_SEAL': 'rev2 (coordinator): flange 44 -> 50, inserts r 17 -> 15.5, face seal moved outside the screws: '
                     'O-ring 40x2, groove ID 40.4 / OD 45.6 / depth 1.5',
        'INS_DEPTH': 'spec 6 deep -> 4 through: flange is 4 thick and must print flange-down; use short M3 inserts',
        'CBORE_DEPTH': '3.2 (head 0.2 below face) so the M3x50 tip is 3.2 mm (not exactly 3.0) into the spline thread',
        'added': 'bore lead-in chamfers on bushing (1.0 bottom for O-rings, 0.4 top)',
    },
    'notes': ['SPL_CLEAR is radial (tip and root radii both +c); print test_scanalato first and set SPL_CLEAR.']
             + ([f'CLASH: axis is {SKIRT_DIST["-Y"]:.1f} mm from the lid skirt inner wall on -Y (layout box/shaft_axis_xy); '
                 f'flange r={FL_D/2} goes {SKIRT_CLASH["-Y"]:.1f} mm into it (the old Ø44 already clashed by '
                 f'{22-SKIRT_DIST["-Y"]:.1f}).'] if '-Y' in SKIRT_CLASH else []),
    'lid_skirt_distance_mm': {k: round(v, 2) for k, v in SKIRT_DIST.items()},
}
json.dump(doc, open(HERE / 'drivetrain.json', 'w'), indent=2)
print('\nwrote', HERE / 'drivetrain.json')
