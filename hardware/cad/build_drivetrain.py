#!/usr/bin/env python3
"""
Drivetrain v3 for the kibble dispenser (script revision 4: lid-mounted servo cradle, labyrinth cap).

Parts
  disco_v3        disc + underside boss extended into a sleeve with a downward labyrinth cap over the collar
  albero_mozzo    hub (25T spline socket, 45 deg top cone) + shaft (2 O-ring grooves 9x2) + hex 8 AF
  passante_culla  ONE part: sealed bushing (face O-ring, collar, bore) + servo cradle hung from the lid
  test_scanalato  spline fit coupons

Frame: Z-up, mm. Z=0 = top face of the box lid. X=Y=0 on the shaft axis (axis frame of layout_v3).
Main files are at assembled height; *_print.stl are re-oriented on z=0 in the print orientation.
Booleans: trimesh + manifold3d (engine='manifold').

Run from anywhere:  python hardware/cad/build_drivetrain.py
Outputs (paths relative to this script's folder):
  ../stl/<part>.stl        print-ready, oriented for the bed
  ../3mf/<part>.3mf        at assembled height (frame above)
  build/<part>.stl         at assembled height, plus build/check_section.png (not committed)
  drivetrain.json          parameters, z-stack, hardware list, lid drilling, checks
Input: layout_v3.json (read-only).
"""
import json
import math
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
STL_DIR, MF_DIR, BUILD = HERE.parent / 'stl', HERE.parent / '3mf', HERE / 'build'
for _d in (STL_DIR, MF_DIR, BUILD):
    _d.mkdir(parents=True, exist_ok=True)
LAYOUT = json.load(open(HERE / 'layout_v3.json'))        # read-only

# =====================================================================================
# PARAMETERS
# =====================================================================================
SEG = 128                      # facets on round features (disc rim uses 2x)

# ---- environment, from layout_v3 (axis frame) ----
BX = LAYOUT['box']
AX_X, AX_Y = LAYOUT['shaft_axis_xy']
WALL_X = (BX['outer_x'][0] + BX['wall']) - AX_X      # -29: -X (short side) inner wall plane
WALL_Y = (BX['outer_y'][0] + BX['wall']) - AX_Y      # -29: -Y (long side) inner wall plane
WALL_MIN_GAP = 2.0                                   # everything under the lid stays >= 2 mm inside
LID_T = BX['lid_plate_t']                            # lid plate z = -3.5..0
FLOOR_Z0, FLOOR_Z1 = LAYOUT['camera']['floor_z']     # bowl floor z = 0..3 (sits on the lid)
FLOOR_HOLE_D = LAYOUT['camera']['floor_hole_d']
SV = LAYOUT['servo']
SERVO_L, SERVO_W, SERVO_H = SV['body_xyz']           # 40 x 20 x 40.5
SERVO_CX = -SV['shaft_offset_x_from_center']         # body centre x = +10
SERVO_TOP, SERVO_BOT = SV['body_top_z'], SV['body_bottom_z']
TAB_Z0, TAB_T = SV['tab_underside_z'], 2.5
TAB_Z1 = TAB_Z0 + TAB_T                              # tab top -32 = cradle pad face
TAB_L, TAB_W = SV['tab_len_x'], SERVO_W
TAB_HOLE_DX, TAB_HOLE_DY, TAB_HOLE_D = 24.75, 5.0, 4.5
SERVO_SPLINE_D = 6.0
SPLINE_TIP_Z = SV['spline_tip_z']

# ---- disco_v3 ----
DISC_D, DISC_Z0, DISC_Z1 = 103.0, 32.0, 36.0
TRAP_Y_IN, TRAP_W_IN = 9.0, 16.0        # short base at y=9
TRAP_Y_OUT, TRAP_W_OUT = 43.0, 35.0     # long base at y=43
TRAP_R = 3.0                            # corner radius
TRAP_CH_TOP, TRAP_CH_BOT = 1.5, 0.7     # 45 deg chamfers on the hole edges
BOSS_D, BOSS_Z0 = 16.0, 24.0            # boss/sleeve OD; z=24 = seat on the shaft shoulder (hex pocket above)
POCKET_AF = 8.2                         # hex pocket across flats (0.1/flat on an 8.0 hex)
POCKET_DEPTH = 6.0                      # from z=24 up -> pocket top z=30
BORE_D = 3.4                            # M3 clearance through everything
CBORE_D, CBORE_DEPTH = 6.2, 3.2         # DIN912 M3 head 5.5 x 3.0 -> head 0.2 below the top face
# labyrinth sleeve + cap (belongs to the disc)
SLEEVE_BORE_D = 12.4                    # around the 12.0 shaft
SLEEVE_CH = 0.6                         # lead-in at the sleeve mouth
CAP_GAP_R = 1.25                        # skirt inside -> collar outside (spec >= 1.0)
CAP_GAP_Z = 1.0                         # cap ceiling -> collar top
CAP_SKIRT_T = 1.6
CAP_FLOOR_GAP = 0.5                     # skirt bottom above the bowl floor top
CAP_OVERLAP_MIN = 1.5                   # skirt below the collar top
CAP_WALL_MIN = 1.6                      # normal wall thickness through the 45 deg flare

# ---- albero_mozzo (hub + shaft) ----
HUB_D, HUB_Z0, HUB_Z1 = 22.0, -18.5, -13.0   # was 24 / top -8.5: shrunk + 45 deg top cone (support-free cavity)
SPL_TEETH, SPL_TIP_D, SPL_ROOT_D = 25, 5.90, 5.30
SPL_CLEAR = 0.10                        # radial clearance: tip & root radii of the socket each + SPL_CLEAR
SPL_DEPTH = 4.5                         # socket ceiling at z=-14 = spline tip
SPL_CHAMFER = 0.4                       # 45 deg entry chamfer at the hub bottom
SHAFT_D, SHAFT_Z1 = 12.0, 24.0          # round shaft up to the shoulder at z=24
HEX_AF = 8.0
HEX_LEN = POCKET_DEPTH - 0.5            # 0.5 mm air above the hex in the pocket
HEX_CHAMFER = 0.5
OR_SIZE = (9.0, 2.0)                    # shaft O-ring NBR 9x2 (rotary, low friction)
OR_GROOVE_D = 9.0                       # groove bottom
OR_GROOVE_W = 1.9                       # flat-bottom width; 45 deg flank above it up to the shaft OD
OR_GROOVE_Z = (-4.5, 0.5)               # groove centres (lower one is enough, upper optional)

# ---- passante_culla: bushing ----
FL_D, FL_Z0, FL_Z1 = 53.0, -7.5, -3.5   # sealing flange, top face against the lid underside
COLLAR_D = 21.5
COLLAR_Z1_SPEC = 4.0
BUSH_BORE_D = 12.4
BUSH_BORE_CH_TOP = 0.4
FACE_OR_SIZE = (45.0, 2.0)              # face O-ring NBR 45x2, encloses collar + lid screws
FACE_OR_OD, FACE_OR_W, FACE_OR_DEPTH = 48.8, 2.7, 1.5    # OD seat (internal pressure), 25% squeeze
FACE_OR_ID = FACE_OR_OD - 2 * FACE_OR_W
LID_SCREW_R, LID_SCREW_ANG = 17.5, (90.0, 210.0, 330.0)
LID_SCREW_HOLE_D = 3.4                  # in lid + bowl floor
LID_CSK_D = 6.5                         # 90 deg countersink in the bowl floor (ISO 10642 M3 head 6.0)
LID_HOLE_D = COLLAR_D + 1.0             # lid centre hole
INS_D, INS_L, INS_SINK = 4.0, 5.7, 0.2  # M3 heat-set insert (hole 4.0, length 5.7, set 0.2 below the face)
LID_INS_DEPTH = 7.5                     # BLIND hole from the flange face
LID_ENG_MIN = 4.0
LID_SCREW_STD = (8, 10, 12, 14, 16)     # ISO 10642 M3 lengths (overall, head included)
MIN_WALL_INS, MIN_WALL_EDGE = 2.0, 2.0

# ---- passante_culla: cradle ----
HUB_CLR_R, HUB_CLR_AX, HUB_CLR_CONE = 1.5, 1.0, 1.5
HUB_CAV_R = HUB_D / 2 + HUB_CLR_R       # 12.5
SERVO_CLR_END, SERVO_CLR_TOP = 0.5, 0.5
CAGE_IN_HALF_Y = 12.75                  # inner half-width: Ø22 hub passes from below during assembly
CAGE_SIDE_T = 2.5
PAD_WALL = 2.25                         # servo insert hole -> pad faces
CAGE_TOP = FL_Z1 - 0.5                  # cradle top outside the flange disc: 0.5 relief under the lid
HIP_Z_MAX = -8.0                        # hip-roof void clipped here (2.5 mm bridged strip) -> >=4.5 under the face
SERVO_INS_DEPTH = 8.0
SERVO_SCREW_STD = (6, 8, 10)            # DIN912 M3
WASHER_T = 0.5                          # DIN 125-A M3 (3.2 x 7 x 0.5)
FIN_X, FIN_T, FIN_TOP_Z, FIN_FOOT = (-5.0, 9.0), 2.4, -12.0, 3.0   # 4 gusset fins on the side walls

# ---- main screw ----
SCREW_STD = (50, 45, 55, 60)            # preferred first
SCREW_HEAD_D, SCREW_HEAD_H = 5.5, 3.0
TIP_BELOW = (3.0, 6.0)                  # screw tip must land 3..6 mm below the spline tip
MIN_SOLID = 2.5                         # material between pocket top and counterbore bottom

# ---- test_scanalato ----
CP_D, CP_H = 14.0, 6.0
CP_CLEARS = (0.05, 0.10, 0.20)          # 1 / 2 / 3 notches
CP_PITCH = 18.0
NOTCH_W, NOTCH_DEPTH, NOTCH_STEP = 1.2, 1.0, 22.0

COLORS = {'disco_v3': '#E8792B', 'albero_mozzo': '#4A4A4A', 'passante_culla': '#262626',
          'test_scanalato': '#262626'}
FILAMENT = {'disco_v3': 'PETG orange', 'albero_mozzo': 'PETG black', 'passante_culla': 'PETG black',
            'test_scanalato': 'PETG black'}

# =====================================================================================
# DERIVED
# =====================================================================================
# labyrinth: collar must rise >= CAP_OVERLAP_MIN above the skirt bottom
CAP_Z0 = FLOOR_Z1 + CAP_FLOOR_GAP                                  # 3.5
COLLAR_Z1 = max(COLLAR_Z1_SPEC, CAP_Z0 + CAP_OVERLAP_MIN)          # 5.0 (spec said 4 -> overlap only 0.5)
CAP_RI = COLLAR_D / 2 + CAP_GAP_R
CAP_RO = CAP_RI + CAP_SKIRT_T
CAP_CEIL = COLLAR_Z1 + CAP_GAP_Z
CAP_ZS = math.ceil((CAP_WALL_MIN * math.sqrt(2) + CAP_RI + CAP_CEIL - CAP_RO) * 10) / 10   # flare start
CAP_ZF = CAP_ZS + (CAP_RO - BOSS_D / 2)                            # flare reaches the sleeve OD
HUB_CONE_Z1 = HUB_Z1 + (HUB_D - SHAFT_D) / 2                       # hub cone meets the shaft
CAV_C0 = HUB_Z1 + HUB_CLR_CONE - (HUB_CAV_R - HUB_D / 2)           # cavity cone starts at r=HUB_CAV_R
BORE_START_Z = CAV_C0 + (HUB_CAV_R - BUSH_BORE_D / 2)              # cavity cone meets the bore
SERVO_ZONE_TOP = SERVO_TOP + SERVO_CLR_TOP                         # -19.5
CAGE_Z0 = TAB_Z1                                                   # -32
CAGE_X_IN0 = SERVO_CX - SERVO_L / 2 - SERVO_CLR_END                # -10.5
CAGE_X_IN1 = SERVO_CX + SERVO_L / 2 + SERVO_CLR_END                # 30.5
CAGE_X_OUT0 = SERVO_CX - TAB_HOLE_DX - INS_D / 2 - PAD_WALL        # -19
CAGE_X_OUT1 = SERVO_CX + TAB_HOLE_DX + INS_D / 2 + PAD_WALL        # 39
CAGE_OUT_HALF_Y = CAGE_IN_HALF_Y + CAGE_SIDE_T
HIP_RIDGE_Z = SERVO_ZONE_TOP + CAGE_IN_HALF_Y
BELL_R_BOT = FL_D / 2 - (FL_Z0 - CAGE_Z0)                          # 45 deg bell under the flange
SERVO_HOLES = [(SERVO_CX + sx * TAB_HOLE_DX, sy * TAB_HOLE_DY) for sx in (-1, 1) for sy in (-1, 1)]
LID_HOLES = [(LID_SCREW_R * math.cos(math.radians(a)), LID_SCREW_R * math.sin(math.radians(a)))
             for a in LID_SCREW_ANG]
LID_INS_BOT = FL_Z1 - LID_INS_DEPTH
SERVO_INS_TOP = CAGE_Z0 + SERVO_INS_DEPTH

assert abs(TAB_Z1 - (-32.0)) < 1e-9 and abs(SERVO_TOP - SERVO_H - SERVO_BOT) < 1e-6
assert HUB_D >= 20.0
assert HIP_Z_MAX < BORE_START_Z - 1.0

# =====================================================================================
# SCREW RULES
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
print(f'main screw M3x{SCREW_LEN} DIN912: head {CBORE_BOT}..{CBORE_BOT+SCREW_HEAD_H} (top face {DISC_Z1}), '
      f'tip z={SCREW_TIP_Z} ({SPLINE_TIP_Z-SCREW_TIP_Z:.1f} below spline tip), '
      f'solid under head {CBORE_BOT-POCKET_TOP:.1f}')

CLAMP = (FLOOR_Z1 - FLOOR_Z0) + LID_T                              # bowl floor + lid
LID_SCREW_LEN = None
for _len in LID_SCREW_STD:
    into = _len - CLAMP
    eng = min(into - INS_SINK, INS_L)
    if eng >= LID_ENG_MIN and FL_Z1 - into >= LID_INS_BOT + 1.0:
        LID_SCREW_LEN, LID_SCREW_ENG, LID_SCREW_TIP_Z = _len, eng, FL_Z1 - into
        break
assert LID_SCREW_LEN is not None
SERVO_SCREW_LEN = None
for _len in SERVO_SCREW_STD:
    into = _len - WASHER_T - TAB_T
    eng = min(into - INS_SINK, INS_L)
    if eng >= LID_ENG_MIN and CAGE_Z0 + into <= SERVO_INS_TOP - 1.0:
        SERVO_SCREW_LEN, SERVO_SCREW_ENG, SERVO_SCREW_TIP_Z = _len, eng, CAGE_Z0 + into
        break
assert SERVO_SCREW_LEN is not None
print(f'lid screws 3x M3x{LID_SCREW_LEN} ISO 10642: engagement {LID_SCREW_ENG:.1f}, tip z={LID_SCREW_TIP_Z}, '
      f'blind hole bottom z={LID_INS_BOT}')
print(f'servo screws 4x M3x{SERVO_SCREW_LEN} DIN912 + washer: engagement {SERVO_SCREW_ENG:.1f}, '
      f'tip z={SERVO_SCREW_TIP_Z}, blind hole top z={SERVO_INS_TOP}')

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


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def at(m, x, y, z=0.0):
    m = m.copy()
    m.apply_translation([x, y, z])
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


def rect(x0, y0, x1, y1):
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def revolve(profile, n=SEG):
    p = np.asarray(profile, float)
    if not np.allclose(p[0], p[-1]):
        p = np.vstack([p, p[:1]])
    return trimesh.creation.revolve(p, sections=n)


def hexagon(af):
    rc = af / np.sqrt(3)                 # circumradius; vertices on +-X, flats normal to +-Y
    a = np.radians(np.arange(6) * 60.0)
    return Polygon(np.c_[rc * np.cos(a), rc * np.sin(a)])


def spline_poly(c):
    """25T triangular-tooth star, tip and root radii each grown by c (c<0 never used)."""
    k = np.arange(2 * SPL_TEETH)
    a = k * np.pi / SPL_TEETH
    r = np.where(k % 2 == 0, SPL_TIP_D / 2 + c, SPL_ROOT_D / 2 + c)
    return Polygon(np.c_[r * np.cos(a), r * np.sin(a)])


def spline_socket_cutter(c, z_mouth, depth):
    """socket opening downward at z_mouth, ceiling at z_mouth+depth, 45 deg entry chamfer."""
    teeth = prism(spline_poly(c), z_mouth - 1.0, z_mouth + depth)
    r_out = SPL_TIP_D / 2 + c
    over = 0.5
    cham = hull_of((circle_pts(2 * (r_out + SPL_CHAMFER + over), 96), z_mouth - over),
                   (circle_pts(2 * r_out, 96), z_mouth + SPL_CHAMFER))
    return U([teeth, cham])


def vol(m):
    return float(abs(m.volume)) if m is not None and len(m.faces) else 0.0


def report(name, m):
    print(f'{name:22s} watertight={m.is_watertight}  volume={m.volume/1000:7.3f} cm3  '
          f'z=[{m.bounds[0,2]:.2f}, {m.bounds[1,2]:.2f}]  faces={len(m.faces)}')
    assert m.is_watertight and m.volume > 0


# =====================================================================================
# 1. DISCO v3 (+ sleeve + labyrinth cap)
# =====================================================================================
bufr = dict(join_style=1, resolution=24)
nom = Polygon([(-TRAP_W_IN / 2, TRAP_Y_IN), (TRAP_W_IN / 2, TRAP_Y_IN),
               (TRAP_W_OUT / 2, TRAP_Y_OUT), (-TRAP_W_OUT / 2, TRAP_Y_OUT)]
              ).buffer(-TRAP_R, **bufr).buffer(TRAP_R, **bufr)
plate = cyl(DISC_D, DISC_Z0, DISC_Z1, n=2 * SEG)
trap_cut = U([prism(nom, DISC_Z0 - 1, DISC_Z1 + 1),
              hull_of((nom, DISC_Z1 - TRAP_CH_TOP), (nom.buffer(TRAP_CH_TOP, **bufr), DISC_Z1)),
              hull_of((nom.buffer(TRAP_CH_BOT, **bufr), DISC_Z0), (nom, DISC_Z0 + TRAP_CH_BOT))])
plate = D(plate, trap_cut)
cap = revolve([(4.0, CAP_CEIL), (CAP_RI, CAP_CEIL), (CAP_RI, CAP_Z0), (CAP_RO, CAP_Z0), (CAP_RO, CAP_ZS),
               (BOSS_D / 2, CAP_ZF), (4.0, CAP_ZF)])
disc = U([plate, cyl(BOSS_D, CAP_ZF - 0.2, DISC_Z0 + 0.5), cap])
disc = D(disc, [cyl(SLEEVE_BORE_D, CAP_CEIL - 1, BOSS_Z0),
                hull_of((circle_pts(SLEEVE_BORE_D + 2 * (SLEEVE_CH + 0.5)), CAP_CEIL - 0.5),
                        (circle_pts(SLEEVE_BORE_D), CAP_CEIL + SLEEVE_CH)),
                cyl(BORE_D, CAP_CEIL - 1, DISC_Z1 + 1, 48),
                cyl(CBORE_D, CBORE_BOT, DISC_Z1 + 1, 64),
                prism(hexagon(POCKET_AF), BOSS_Z0 - 0.5, POCKET_TOP)])
disc.process(validate=True)

# =====================================================================================
# 2. ALBERO + MOZZO
# =====================================================================================
HEX_Z1 = SHAFT_Z1 + HEX_LEN
hx = hexagon(HEX_AF)
hex_body = hull_of((hx, SHAFT_Z1 - 0.2), (hx, HEX_Z1 - HEX_CHAMFER),
                   (hexagon(HEX_AF - 2 * HEX_CHAMFER), HEX_Z1))
hub = U([cyl(HUB_D, HUB_Z0, HUB_Z1),
         hull_of((circle_pts(HUB_D), HUB_Z1 - 0.5), (circle_pts(HUB_D), HUB_Z1),
                 (circle_pts(SHAFT_D), HUB_CONE_Z1))])
shaft = U([hub, cyl(SHAFT_D, HUB_CONE_Z1 - 0.5, SHAFT_Z1), hex_body])
rg, ro = OR_GROOVE_D / 2, SHAFT_D / 2 + 0.5
groove_cuts = []
for zc in OR_GROOVE_Z:
    z_lo, z_hi = zc - OR_GROOVE_W / 2, zc + OR_GROOVE_W / 2
    groove_cuts.append(revolve([[rg, z_lo], [ro, z_lo], [ro, z_hi + (ro - rg)], [rg, z_hi]]))
albero = D(shaft, groove_cuts + [cyl(BORE_D, HUB_Z0 - 1, HEX_Z1 + 1, 48),
                                 spline_socket_cutter(SPL_CLEAR, HUB_Z0, SPL_DEPTH)])
albero.process(validate=True)

# =====================================================================================
# 3. PASSANTE + CULLA (one part, prints upright: pad faces on the bed, collar up)
# =====================================================================================
fins = []
for xf in FIN_X:
    r_bell = FL_D / 2 + (FIN_TOP_Z - FL_Z0)
    y_top = math.sqrt(r_bell ** 2 - xf ** 2) - 0.3
    for s in (-1, 1):
        yz = [(CAGE_OUT_HALF_Y - 0.5, CAGE_Z0), (CAGE_OUT_HALF_Y + FIN_FOOT, CAGE_Z0),
              (y_top, FIN_TOP_Z), (CAGE_OUT_HALF_Y - 0.5, FIN_TOP_Z)]
        P = []
        for y, z in yz:
            for dx in (-FIN_T / 2, FIN_T / 2):
                P.append([xf + dx, s * y, z])
        fins.append(trimesh.convex.convex_hull(np.array(P)))
solid = U([cyl(FL_D, FL_Z0, FL_Z1),
           cyl(COLLAR_D, FL_Z1 - 0.2, COLLAR_Z1),
           hull_of((circle_pts(FL_D), FL_Z0 + 0.01), (circle_pts(2 * BELL_R_BOT), CAGE_Z0)),
           box(CAGE_X_OUT0, CAGE_X_OUT1, -CAGE_OUT_HALF_Y, CAGE_OUT_HALF_Y, CAGE_Z0, CAGE_TOP)] + fins)
R_in = rect(CAGE_X_IN0, -CAGE_IN_HALF_Y, CAGE_X_IN1, CAGE_IN_HALF_Y)
ridge = np.array([[CAGE_X_IN0 + CAGE_IN_HALF_Y, 0.0], [CAGE_X_IN1 - CAGE_IN_HALF_Y, 0.0]])
servo_void = hull_of((R_in, CAGE_Z0 - 1), (R_in, SERVO_ZONE_TOP), (ridge, HIP_RIDGE_Z))   # 45 deg hip roof
servo_void = I(servo_void, box(-100, 100, -100, 100, CAGE_Z0 - 2, HIP_Z_MAX))
hub_cav = U([cyl(2 * HUB_CAV_R, SERVO_ZONE_TOP, CAV_C0 + 0.01),
             hull_of((circle_pts(2 * HUB_CAV_R), CAV_C0),
                     (circle_pts(BUSH_BORE_D - 1.0), CAV_C0 + HUB_CAV_R - BUSH_BORE_D / 2 + 0.5))])
ctp = BUSH_BORE_CH_TOP
bore_cut = U([cyl(BUSH_BORE_D, BORE_START_Z - 2, COLLAR_Z1 + 1),
              hull_of((circle_pts(BUSH_BORE_D), COLLAR_Z1 - ctp),
                      (circle_pts(BUSH_BORE_D + 2 * (ctp + 0.5)), COLLAR_Z1 + 0.5))])
face_groove = D(cyl(FACE_OR_OD, FL_Z1 - FACE_OR_DEPTH, FL_Z1 + 0.5),
                cyl(FACE_OR_ID, FL_Z1 - FACE_OR_DEPTH - 1, FL_Z1 + 1))
lid_ins = [at(cyl(INS_D, LID_INS_BOT, FL_Z1 + 1, 48), x, y) for x, y in LID_HOLES]
servo_ins = [at(U([cyl(INS_D, CAGE_Z0 - 1, SERVO_INS_TOP, 48),
                   hull_of((circle_pts(INS_D + 1.8, 48), CAGE_Z0 - 0.5), (circle_pts(INS_D, 48), CAGE_Z0 + 0.4))]),
                x, y) for x, y in SERVO_HOLES]
culla = D(solid, [servo_void, hub_cav, bore_cut, face_groove] + lid_ins + servo_ins)
culla.process(validate=True)

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
# CONTEXT SOLIDS (checks + section only, not exported as parts)
# =====================================================================================
servo_solid = U([box(SERVO_CX - SERVO_L / 2, SERVO_CX + SERVO_L / 2, -SERVO_W / 2, SERVO_W / 2, SERVO_BOT, SERVO_TOP),
                 box(SERVO_CX - TAB_L / 2, SERVO_CX + TAB_L / 2, -TAB_W / 2, TAB_W / 2, TAB_Z0, TAB_Z1),
                 cyl(SERVO_SPLINE_D, SERVO_TOP - 0.1, HUB_Z0, 64),                 # Ø6 below the hub
                 prism(spline_poly(0.0), HUB_Z0 - 0.05, SPLINE_TIP_Z)])            # 25T male inside the socket
servo_solid = D(servo_solid, [cyl(3.0, SPLINE_TIP_Z - 8, SPLINE_TIP_Z + 1, 32)] +  # M3 thread core
                [at(cyl(TAB_HOLE_D, TAB_Z0 - 1, TAB_Z1 + 1, 32), x, y) for x, y in SERVO_HOLES])
lid = D(box(WALL_X - BX['wall'], 90, WALL_Y - BX['wall'], 70, -LID_T, 0),
        [cyl(LID_HOLE_D, -LID_T - 1, 1)] + [at(cyl(LID_SCREW_HOLE_D, -LID_T - 1, 1, 32), x, y) for x, y in LID_HOLES])
bowl = D(box(WALL_X, 60, WALL_Y, 60, FLOOR_Z0, FLOOR_Z1),
         [cyl(FLOOR_HOLE_D, -1, FLOOR_Z1 + 1)] +
         [at(U([cyl(LID_SCREW_HOLE_D, -1, FLOOR_Z1 + 1, 32),
                hull_of((circle_pts(LID_SCREW_HOLE_D, 32), FLOOR_Z1 - (LID_CSK_D - LID_SCREW_HOLE_D) / 2),
                        (circle_pts(LID_CSK_D, 32), FLOOR_Z1), (circle_pts(LID_CSK_D, 32), FLOOR_Z1 + 1))]), x, y)
          for x, y in LID_HOLES])
wall_x = box(WALL_X - BX['wall'], WALL_X, -60, 100, -70, 0)
wall_y = box(-60, 120, WALL_Y - BX['wall'], WALL_Y, -70, 0)
screw = U([cyl(3.0, SCREW_TIP_Z, CBORE_BOT, 32), cyl(SCREW_HEAD_D, CBORE_BOT, CBORE_BOT + SCREW_HEAD_H, 48)])
lid_screws = U([at(U([cyl(3.0, LID_SCREW_TIP_Z, FLOOR_Z1 - 1.7, 32),
                      hull_of((circle_pts(3.0, 32), FLOOR_Z1 - 1.7), (circle_pts(6.0, 32), FLOOR_Z1))]), x, y)
                for x, y in LID_HOLES])
servo_screws = U([at(U([cyl(3.0, TAB_Z0 - WASHER_T - 0.01, SERVO_SCREW_TIP_Z, 32),
                        cyl(7.0, TAB_Z0 - WASHER_T, TAB_Z0, 32),
                        cyl(5.5, TAB_Z0 - WASHER_T - 3.0, TAB_Z0 - WASHER_T, 32)]), x, y) for x, y in SERVO_HOLES])

# =====================================================================================
# EXPORT
# =====================================================================================
def to_print(m, flip=False):
    p = m.copy()
    if flip:
        p.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    p.apply_translation([0, 0, -p.bounds[0, 2]])
    return p


def overhang(p, lim_deg=45.0):
    """area (mm2) of down-facing faces flatter than lim_deg from horizontal, not on the bed"""
    nz = p.face_normals[:, 2]
    zmin = p.triangles[:, :, 2].min(axis=1)
    sel = (nz < -math.sin(math.radians(lim_deg + 1.0))) & (zmin > 0.05)
    return float(p.area_faces[sel].sum())


PRINT = {'disco_v3': (disc, True, 'flipped: disc TOP face on the bed, sleeve + cap pointing up (45 deg flare)'),
         'albero_mozzo': (albero, False, 'as assembled: hub (spline socket) on the bed, hex up; 100% infill or >=6 walls'),
         'passante_culla': (culla, False, 'as assembled: servo-pad face (z=-32) on the bed, collar up; '
                                          'seal face + O-ring groove print as top surfaces')}
print('\n--- meshes ---')
prints, ovh = {}, {}
for name, (m, flip, _) in PRINT.items():
    report(name, m)
    m.export(BUILD / f'{name}.stl')
    m.export(MF_DIR / f'{name}.3mf')
    p = to_print(m, flip)
    report(name + '_print', p)
    p.export(STL_DIR / f'{name}.stl')
    prints[name] = p
    ovh[name] = round(overhang(p), 1)
for c, m in zip(CP_CLEARS, coupons):
    report(f'coupon c={c}', m)
report('test_scanalato', test)
test.export(BUILD / 'test_scanalato.stl')
test.export(STL_DIR / 'test_scanalato.stl')
ovh['test_scanalato'] = round(overhang(test), 1)
sc = trimesh.Scene()
for c, m in zip(CP_CLEARS, coupons):
    sc.add_geometry(m, geom_name=f'spline_c{int(round(c*100)):03d}')
sc.export(MF_DIR / 'test_scanalato.3mf')
print('down-facing area flatter than 45 deg (bridges), mm2:', ovh)

# =====================================================================================
# CHECKS
# =====================================================================================
print('\n--- interference (intersection volume, mm3) ---')
PARTS = {'disco_v3': disc, 'albero_mozzo': albero, 'passante_culla': culla}
CTX = {'servo': servo_solid, 'lid_plate': lid, 'bowl_floor': bowl, 'wall_-X': wall_x, 'wall_-Y': wall_y,
       'screw_M3x%d' % SCREW_LEN: screw, 'lid_screws': lid_screws, 'servo_screws': servo_screws}
ENV = {'lid_plate', 'bowl_floor', 'wall_-X', 'wall_-Y'}
ALL = {**PARTS, **CTX}
names = list(ALL)
inter = {}
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if a in ENV and b in ENV:
            continue
        v = vol(I(ALL[a], ALL[b]))
        inter[f'{a}|{b}'] = round(v, 4)
worst = max(inter.values())
for k, v in inter.items():
    if v > 1e-4:
        print(f'  {k:40s} {v:.4f}')
print(f'{len(inter)} pairs, max intersection {worst:.5f} mm3')
assert worst < 1e-2

# walls: >= 2 mm inside
WALL_MARGIN = {}
below_lid = box(-200, 200, -200, 200, -200, -LID_T)        # the rule is for everything under the lid
for n, m in {'albero_mozzo': albero, 'passante_culla': culla, 'servo': servo_solid,
             'servo_screws': servo_screws}.items():
    mb = I(m, below_lid)
    WALL_MARGIN[n] = {'-X': round(mb.bounds[0, 0] - WALL_X, 2), '-Y': round(mb.bounds[0, 1] - WALL_Y, 2)}
    assert min(WALL_MARGIN[n].values()) >= WALL_MIN_GAP, n
print('distance to inner walls (mm):', WALL_MARGIN)

# hub clearance envelope (1.5 radial / 1.0 axial, 1.5 on the cones), small numeric tolerance
tol = 0.02
env = hull_of((circle_pts(HUB_D + 2 * (HUB_CLR_R - tol)), HUB_Z0 - HUB_CLR_AX + tol),
              (circle_pts(HUB_D + 2 * (HUB_CLR_R - tol)), HUB_Z1),
              (circle_pts(SHAFT_D + 2 * (HUB_CLR_CONE - tol)), HUB_CONE_Z1))
servo_body_only = U([box(SERVO_CX - SERVO_L / 2, SERVO_CX + SERVO_L / 2, -SERVO_W / 2, SERVO_W / 2, SERVO_BOT, SERVO_TOP),
                     box(SERVO_CX - TAB_L / 2, SERVO_CX + TAB_L / 2, -TAB_W / 2, TAB_W / 2, TAB_Z0, TAB_Z1)])
HUB_ENV = {'culla': round(vol(I(env, culla)), 5), 'servo_body': round(vol(I(env, servo_body_only)), 5)}
HUB_CLEAR = {'radial_to_cavity': HUB_CAV_R - HUB_D / 2,
             'cone_to_cavity_cone_axial_and_radial': round(CAV_C0 - HUB_Z1 + HUB_CAV_R - HUB_D / 2, 3),
             'top_axial_to_cradle': None,
             'bottom_to_servo_top': round(HUB_Z0 - SERVO_TOP, 3),
             'bottom_to_-X_ledge': round(HUB_Z0 - SERVO_ZONE_TOP, 3),
             'envelope_intersection_mm3': HUB_ENV}
HUB_CLEAR.pop('top_axial_to_cradle')
print('hub clearance:', HUB_CLEAR)
assert max(HUB_ENV.values()) < 1e-2


# material under the lid inserts (ray down from points on/inside the blind hole bottom)
def floor_under(m, x, y, z):
    loc, _, _ = m.ray.intersects_location([[x, y, z - 0.01]], [[0, 0, -1]])
    return min(z - p[2] for p in loc) if len(loc) else float('inf')


INS_FLOOR = {}
for ang, (x, y) in zip(LID_SCREW_ANG, LID_HOLES):
    pts = [(x, y)] + [(x + (INS_D / 2 + 0.05) * math.cos(t), y + (INS_D / 2 + 0.05) * math.sin(t))
                      for t in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
    INS_FLOOR[int(ang)] = round(min(floor_under(culla, px, py, LID_INS_BOT) for px, py in pts), 2)
print('solid under lid insert holes (mm):', INS_FLOOR)
assert min(INS_FLOOR.values()) >= 1.5

# O-ring glands
from shapely.geometry import Polygon as SP
z_lo, z_hi = -OR_GROOVE_W / 2, OR_GROOVE_W / 2
gland = SP([(rg, z_lo), (BUSH_BORE_D / 2, z_lo), (BUSH_BORE_D / 2, z_hi + (SHAFT_D / 2 - rg)),
            (SHAFT_D / 2, z_hi + (SHAFT_D / 2 - rg)), (rg, z_hi)])
SH_GLAND = (BUSH_BORE_D - OR_GROOVE_D) / 2
SH_SQUEEZE = (OR_SIZE[1] - SH_GLAND) / OR_SIZE[1]
SH_FILL = math.pi * (OR_SIZE[1] / 2) ** 2 / gland.area
SH_STRETCH = OR_GROOVE_D / OR_SIZE[0] - 1
SH_FILL_RECT = math.pi * (OR_SIZE[1] / 2) ** 2 / ((OR_GROOVE_W + SH_GLAND) * SH_GLAND)
print(f'shaft O-ring {OR_SIZE[0]:.0f}x{OR_SIZE[1]:.0f}: groove Ø{OR_GROOVE_D} in bore Ø{BUSH_BORE_D}: gland {SH_GLAND:.2f}, '
      f'squeeze {SH_SQUEEZE*100:.0f}%, fill {SH_FILL*100:.0f}% (true gland incl. 45 deg flank), stretch {SH_STRETCH*100:.1f}%')
f_id, f_cs = FACE_OR_SIZE
FACE_OD_COMP = 1 - FACE_OR_OD / (f_id + 2 * f_cs)
FACE_SQUEEZE = (f_cs - FACE_OR_DEPTH) / f_cs
FACE_FILL = math.pi * (f_cs / 2) ** 2 / (FACE_OR_W * FACE_OR_DEPTH)
WALL_INS_GROOVE = FACE_OR_ID / 2 - (LID_SCREW_R + INS_D / 2)
WALL_GROOVE_EDGE = FL_D / 2 - FACE_OR_OD / 2
WALL_INS_CAV = LID_SCREW_R - INS_D / 2 - HUB_CAV_R
WALL_LIDHOLE = LID_SCREW_R - LID_SCREW_HOLE_D / 2 - LID_HOLE_D / 2
print(f'face O-ring {f_id:.0f}x{f_cs:.0f}: groove ID {FACE_OR_ID:.1f} OD {FACE_OR_OD} (w {FACE_OR_W}) depth {FACE_OR_DEPTH}, '
      f'OD seat {FACE_OD_COMP*100:.1f}% compressed, squeeze {FACE_SQUEEZE*100:.0f}%, fill {FACE_FILL*100:.0f}%')
print(f'walls: insert->groove {WALL_INS_GROOVE:.2f}, groove->flange edge {WALL_GROOVE_EDGE:.2f}, '
      f'insert->hub cavity {WALL_INS_CAV:.2f}, lid: centre hole->screw hole {WALL_LIDHOLE:.2f}')
assert WALL_INS_GROOVE >= MIN_WALL_INS and WALL_GROOVE_EDGE >= MIN_WALL_EDGE and WALL_INS_CAV >= MIN_WALL_INS
assert 0.20 <= FACE_SQUEEZE <= 0.30 and FACE_FILL < 0.85 and 0.12 <= SH_SQUEEZE <= 0.18 and SH_FILL < 0.85
assert FL_D / 2 <= -WALL_X - WALL_MIN_GAP and FL_D / 2 <= -WALL_Y - WALL_MIN_GAP
CAP = {'skirt_inner_r': CAP_RI, 'skirt_outer_r': CAP_RO, 'radial_gap_to_collar': CAP_GAP_R,
       'skirt_bottom_z': CAP_Z0, 'gap_to_bowl_floor': CAP_FLOOR_GAP, 'overlap_below_collar_top': COLLAR_Z1 - CAP_Z0,
       'cap_ceiling_z': CAP_CEIL, 'flare_z': [CAP_ZS, CAP_ZF], 'sleeve_bore_d': SLEEVE_BORE_D, 'sleeve_od': BOSS_D}
print('cap:', CAP)
TORQUE = {'stall_Nm': 2.5, 'tab_screw_force_N': round(2500 / (2 * TAB_HOLE_DX) / 2, 1),
          'lid_screw_shear_N': round(2500 / (3 * LID_SCREW_R), 1),
          'shaft_core_shear_MPa_at_groove': round(2500 * (OR_GROOVE_D / 2) / (math.pi * (OR_GROOVE_D ** 4 - BORE_D ** 4) / 32), 1)}
print('torque path:', TORQUE)

# =====================================================================================
# SECTION RENDER
# =====================================================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle

DRAW = [('wall_-X', wall_x, '#F2B8B8', '#B03030', '///'), ('wall_-Y', wall_y, '#F2B8B8', '#B03030', '///'),
        ('lid_plate', lid, '#D8D8D8', '#808080', '///'), ('bowl_floor', bowl, '#E6E1D3', '#9A8F70', '\\\\\\'),
        ('servo', servo_solid, '#8FB3E0', '#2F5D8A', None),
        ('passante_culla', culla, '#3A3A3A', 'k', None), ('albero_mozzo', albero, '#9A9A9A', 'k', None),
        ('disco_v3', disc, COLORS['disco_v3'], 'k', None),
        ('screws', U([screw, lid_screws, servo_screws]), '#C9A227', '#6B5410', None)]


def draw_section(ax, origin, normal, T, title, xlim, ylim, xl, yl):
    for name, m, fc, ec, hatch in DRAW:
        s = m.section(plane_origin=origin, plane_normal=normal)
        if s is None:
            continue
        p2, _ = s.to_2D(to_2D=T)
        for poly in p2.polygons_full:
            ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=fc, ec=ec, lw=0.5,
                               hatch=hatch, alpha=0.95 if hatch is None else 0.6, zorder=3 if hatch is None else 1))
            for hole in poly.interiors:
                ax.add_patch(MPoly(np.array(hole.coords), closed=True, fc='white', ec=ec, lw=0.5,
                                   zorder=4 if hatch is None else 2))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal')
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.25); ax.set_title(title, fontsize=10)


fig, axs = plt.subplots(2, 2, figsize=(17, 14), facecolor='white')
Txz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
Tyz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
draw_section(axs[0, 0], [0, 0, 0], [0, 1, 0], Txz, 'Section Y=0 (XZ): servo, cradle pads, hub, bushing, disc + cap',
             (-36, 52), (-64, 40), 'X [mm]', 'Z [mm]')
draw_section(axs[0, 1], [0, 0, 0], [1, 0, 0], Tyz, 'Section X=0 (YZ): -Y wall, side walls, lid screw at 90 deg',
             (-36, 52), (-64, 40), 'Y [mm]', 'Z [mm]')
for ax in axs[0]:
    ax.axhline(SPLINE_TIP_Z, color='r', lw=0.6, ls='--')
    ax.text(ax.get_xlim()[1] - 1, SPLINE_TIP_Z + 0.5, f'spline tip {SPLINE_TIP_Z}', color='r', fontsize=7, ha='right')
    ax.axhline(SCREW_TIP_Z, color='m', lw=0.6, ls=':')
    ax.text(ax.get_xlim()[1] - 1, SCREW_TIP_Z - 2.0, f'M3x{SCREW_LEN} tip {SCREW_TIP_Z:.1f}', color='m', fontsize=7,
            ha='right')
    for z, lab in ((COLLAR_Z1, f'collar top {COLLAR_Z1}'), (CAP_Z0, f'skirt bottom {CAP_Z0}'),
                   (CAGE_Z0, f'pads / tab top {CAGE_Z0}')):
        ax.text(ax.get_xlim()[0] + 1, z + 0.4, lab, fontsize=7, color='#555')
for ax, zc in ((axs[1, 0], -10.0), (axs[1, 1], -27.0)):
    Tp = np.eye(4); Tp[2, 3] = -zc
    draw_section(ax, [0, 0, zc], [0, 0, 1], Tp, f'Plan section Z={zc} (XY), walls at x,y = {WALL_X:.0f}',
                 (-36, 52), (-36, 36), 'X [mm]', 'Y [mm]')
    ax.axvline(WALL_X + WALL_MIN_GAP, color='#B03030', lw=0.5, ls=':')
    ax.axhline(WALL_Y + WALL_MIN_GAP, color='#B03030', lw=0.5, ls=':')
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3]) for d in DRAW]
axs[0, 0].legend(handles, [d[0] for d in DRAW], loc='lower right', fontsize=7)
plt.tight_layout()
plt.savefig(BUILD / 'check_section.png', dpi=100)
plt.close(fig)

# =====================================================================================
# JSON
# =====================================================================================
params = {k: v for k, v in globals().items()
          if k.isupper() and len(k) > 1 and isinstance(v, (int, float, tuple)) and not isinstance(v, bool)
          and k not in ('SEG',)}
rnd = lambda v: round(v, 4) if isinstance(v, float) else v
params = {k: ([rnd(x) for x in v] if isinstance(v, tuple) else rnd(v)) for k, v in params.items()}
lid_xy = [[round(x, 3), round(y, 3)] for x, y in LID_HOLES]
doc = {
    'frame': 'Z-up mm, Z=0 = lid top face, X=Y=0 = shaft axis; main files at assembled height',
    'shaft_axis_world_xy': LAYOUT['shaft_axis_xy'],
    'axis_from_box_outer_edges_mm': {'-X (short side)': round(-WALL_X + BX['wall'], 2),
                                     '-Y (long side)': round(-WALL_Y + BX['wall'], 2)},
    'parameters': params,
    'z_stack': {'servo_body': [SERVO_BOT, SERVO_TOP], 'servo_tabs': [TAB_Z0, TAB_Z1], 'spline_tip': SPLINE_TIP_Z,
                'hub_cyl': [HUB_Z0, HUB_Z1], 'hub_cone_to_shaft': [HUB_Z1, HUB_CONE_Z1],
                'cradle_pads_bottom': CAGE_Z0, 'hub_cavity': [SERVO_ZONE_TOP, CAV_C0], 'bore': [BORE_START_Z, COLLAR_Z1],
                'flange_disc': [FL_Z0, FL_Z1], 'lid': [-LID_T, 0], 'bowl_floor': [FLOOR_Z0, FLOOR_Z1],
                'collar_top': COLLAR_Z1, 'cap_skirt_bottom': CAP_Z0, 'cap_ceiling': CAP_CEIL,
                'shaft_shoulder_disc_seat': SHAFT_Z1, 'disc': [DISC_Z0, DISC_Z1],
                'note': 'servo, spline, disc and main screw z unchanged; only the hub top and collar top moved'},
    'screw': {'spec': f'M3x{SCREW_LEN} DIN912 (ISO 4762)', 'head_z': [CBORE_BOT, CBORE_BOT + SCREW_HEAD_H],
              'tip_z': round(SCREW_TIP_Z, 3), 'tip_below_spline_tip_mm': round(SPLINE_TIP_Z - SCREW_TIP_Z, 3),
              'solid_under_head_mm': round(CBORE_BOT - POCKET_TOP, 3), 'pocket_depth': POCKET_DEPTH, 'hex_len': HEX_LEN},
    'hardware': [
        {'qty': 1, 'item': f'M3x{SCREW_LEN} DIN912 / ISO 4762 socket head, A2', 'use': 'disc + shaft into the servo spline thread'},
        {'qty': 3, 'item': f'M3x{LID_SCREW_LEN} ISO 10642 (DIN 7991) countersunk socket, A2',
         'use': f'from above through bowl floor (countersunk) + lid into blind inserts; engagement {LID_SCREW_ENG:.1f} mm'},
        {'qty': 4, 'item': f'M3x{SERVO_SCREW_LEN} DIN912 / ISO 4762 socket head, A2', 'use': 'servo tabs, from below'},
        {'qty': 4, 'item': 'M3 washer DIN 125-A / ISO 7089 (3.2 x 7 x 0.5), A2', 'use': 'under the servo screw heads'},
        {'qty': 7, 'item': f'M3 brass heat-set insert, L {INS_L} mm, for Ø{INS_D} hole (e.g. Ruthex RX-M3x5.7)',
         'use': f'3 lid (blind, {LID_INS_DEPTH} deep from the seal face) + 4 servo pads (blind, {SERVO_INS_DEPTH} deep from below)'},
        {'qty': 1, 'item': 'O-ring NBR70 9x2 (ID 9, CS 2)', 'use': 'shaft, lower groove (+1 optional for the upper groove)'},
        {'qty': 1, 'item': 'O-ring NBR70 45x2 (ID 45, CS 2)', 'use': 'face seal flange <-> lid underside'},
        {'qty': 1, 'item': 'food-grade silicone grease NSF H1 (e.g. Molykote 111), ~0.2 g',
         'use': 'thin film on shaft O-ring and bore; light film on the face O-ring'}],
    'lid_drilling': {
        'frame': 'axis frame: X along the long side, Y along the short side, origin on the shaft axis',
        'axis_position': f'{-WALL_X + BX["wall"]:.1f} mm from the -X outer edge and {-WALL_Y + BX["wall"]:.1f} mm from '
                         f'the -Y outer edge (29 + 3.5 wall); world {LAYOUT["shaft_axis_xy"]}',
        'centre_hole_d': LID_HOLE_D,
        'screw_holes': {'qty': 3, 'd': LID_SCREW_HOLE_D, 'r': LID_SCREW_R, 'angles_deg': list(LID_SCREW_ANG),
                        'xy_axis_frame': lid_xy,
                        'xy_world': [[round(AX_X + x, 3), round(AX_Y + y, 3)] for x, y in lid_xy]},
        'bowl_floor_same_pattern': f'3x Ø{LID_SCREW_HOLE_D} at the same r/angles with 90 deg countersink Ø{LID_CSK_D} '
                                   f'from the top (heads flush); centre hole: layout Ø{FLOOR_HOLE_D} works, Ø{LID_HOLE_D} proposed',
        'seal_zone': f'flange face O-ring groove ID {FACE_OR_ID:.1f} / OD {FACE_OR_OD} encloses the centre hole and the 3 screw holes; '
                     f'keep the lid underside flat and rib-free inside Ø{FL_D}'},
    'face_seal': {'oring': '%dx%d NBR70' % FACE_OR_SIZE, 'groove_id': round(FACE_OR_ID, 2), 'groove_od': FACE_OR_OD,
                  'groove_width': FACE_OR_W, 'groove_depth': FACE_OR_DEPTH,
                  'seat': f'O-ring OD on the groove OD ({FACE_OD_COMP*100:.1f}% compression), no stretch',
                  'squeeze_pct': round(FACE_SQUEEZE * 100, 1), 'fill_pct': round(FACE_FILL * 100, 1),
                  'walls_mm': {'insert_hole_to_groove': round(WALL_INS_GROOVE, 2),
                               'groove_to_flange_edge': round(WALL_GROOVE_EDGE, 2),
                               'insert_hole_to_hub_cavity': round(WALL_INS_CAV, 2)}},
    'shaft_seal': {'oring': '%dx%d NBR70' % OR_SIZE, 'groove_bottom_d': OR_GROOVE_D, 'groove_flat_w': OR_GROOVE_W,
                   'upper_flank': '45 deg to the shaft OD (support-free)', 'groove_centres_z': list(OR_GROOVE_Z),
                   'bore_d': BUSH_BORE_D, 'squeeze_pct': round(SH_SQUEEZE * 100, 1), 'fill_pct': round(SH_FILL * 100, 1),
                   'fill_pct_rectangular_equiv': round(SH_FILL_RECT * 100, 1), 'stretch_pct': round(SH_STRETCH * 100, 1)},
    'labyrinth_cap': CAP,
    'files_note': 'paths relative to hardware/: stl/ = print-ready, 3mf/ = assembled height',
    'parts': {
        'disco_v3': {'files': ['stl/disco_v3.stl', '3mf/disco_v3.3mf'], 'filament': FILAMENT['disco_v3'],
                     'print': PRINT['disco_v3'][2], 'supports': 'none', 'volume_cm3': round(disc.volume / 1000, 3)},
        'albero_mozzo': {'files': ['stl/albero_mozzo.stl', '3mf/albero_mozzo.3mf'],
                         'filament': FILAMENT['albero_mozzo'], 'print': PRINT['albero_mozzo'][2],
                         'supports': 'none (Ø6 socket ceiling bridges)', 'volume_cm3': round(albero.volume / 1000, 3)},
        'passante_culla': {'files': ['stl/passante_culla.stl', '3mf/passante_culla.3mf'],
                           'filament': FILAMENT['passante_culla'], 'print': PRINT['passante_culla'][2],
                           'supports': 'none: hip-roof and hub-cavity ceilings are 45 deg; only bridges are a 2.5 mm '
                                       'strip at z=-8 and the 4 servo-insert hole ceilings',
                           'volume_cm3': round(culla.volume / 1000, 3)},
        'test_scanalato': {'files': ['stl/test_scanalato.stl', '3mf/test_scanalato.3mf'],
                           'filament': FILAMENT['test_scanalato'], 'print': 'as is, socket on the bed', 'supports': 'none',
                           'coupons': {f'{n+1} notch(es)': c for n, c in enumerate(CP_CLEARS)}},
    },
    'assembly': [
        'press 3 inserts into the flange face and 4 into the pad faces of passante_culla',
        'grease, fit 9x2 O-ring(s) on albero_mozzo, push it up from below through the cradle into the bore',
        'push the servo up from below (spline into the hub socket), 4x M3x%d + washers into the pads' % SERVO_SCREW_LEN,
        'face O-ring 45x2 in the groove; offer the sub-assembly to the lid from below, bowl on top, 3x M3x%d countersunk from above' % LID_SCREW_LEN,
        'slide disco_v3 sleeve over the shaft from above (hex into pocket), M3x%d from the disc top into the spline' % SCREW_LEN],
    'checks': {'watertight': {n: bool(m.is_watertight) for n, m in PARTS.items()} | {'test_scanalato': bool(test.is_watertight)},
               'intersection_mm3_max': round(worst, 5), 'intersection_mm3': inter,
               'wall_distance_mm': WALL_MARGIN, 'hub_clearance': HUB_CLEAR, 'solid_under_lid_inserts_mm': INS_FLOOR,
               'print_downfacing_area_flatter_than_45deg_mm2': ovh, 'torque_path': TORQUE},
    'proposed_layout_v3_changes': {
        'bushing.flange_d': f'44 -> {FL_D} (face O-ring 45x2 outside the screws; r {FL_D/2} = {-WALL_X-FL_D/2:.1f} mm from the walls)',
        'bushing.collar_top_z': f'4 -> {COLLAR_Z1} (E needs skirt bottom 3.5 AND >=1.5 overlap below the collar top; 4 gives 0.5)',
        'bushing.cradle': f'integrated servo cradle, pads z={CAGE_Z0}, footprint x {CAGE_X_OUT0}..{CAGE_X_OUT1}, y +-{CAGE_OUT_HALF_Y} (+fins to y +-{FIN_FOOT+CAGE_OUT_HALF_Y})',
        'hub': f'd 24 -> {HUB_D}; z [-18.5,-8.5] -> cylinder [{HUB_Z0},{HUB_Z1}] + 45 deg cone to Ø{SHAFT_D} at {HUB_CONE_Z1}',
        'shaft.round_z': f'[-8.5, 24] -> [{HUB_CONE_Z1}, {SHAFT_Z1}]',
        'disc_v3': f'add sleeve Ø{BOSS_D}/bore Ø{SLEEVE_BORE_D} from z=24 down to the cap; cap skirt r {CAP_RI}..{CAP_RO}, z {CAP_Z0}..{CAP_ZS}, flare to z {CAP_ZF}',
        'lid': f'centre hole Ø{LID_HOLE_D} + 3x Ø{LID_SCREW_HOLE_D} at r {LID_SCREW_R}, {list(LID_SCREW_ANG)} deg; flat inside Ø{FL_D}',
        'camera.floor': f'3x Ø{LID_SCREW_HOLE_D} countersunk Ø{LID_CSK_D} at the same pattern; floor_hole_d 22 -> {LID_HOLE_D} (optional)',
        'servo.mounting': f'4x M3x{SERVO_SCREW_LEN} DIN912 + washers from below into heat-set inserts in the cradle pads'},
    'superseded_files': ['passante_stagno.* (now passante_culla)',
                         'wall-mounted servo brackets (never in this repository): replaced by the cradle in the design; '
                         'the as-built prototype still uses a third-party CC BY-NC-SA wall bracket'],
    'notes': ['SPL_CLEAR is radial (tip and root radii both +c); print test_scanalato first and set SPL_CLEAR.',
              f'Shaft core at the grooves is Ø{OR_GROOVE_D} with the Ø{BORE_D} bore: ~{TORQUE["shaft_core_shear_MPa_at_groove"]} MPa '
              'shear at 2.5 N.m stall -> print albero_mozzo 100% infill.',
              'Shaft O-ring 9x2 on a Ø9.0 groove has 0% stretch (as specified); a ring at the low end of the ID tolerance will be slightly loose but cannot fall out in the bore.',
              'Servo solid is simplified (no output boss on the case top): hub bottom is 1.5 above the case top; check the real servo for a raised boss.'],
}
json.dump(doc, open(HERE / 'drivetrain.json', 'w'), indent=2)
print('\nwrote', HERE / 'drivetrain.json')
