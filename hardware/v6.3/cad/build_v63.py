#!/usr/bin/env python3
"""
Kibble Dispenser Outdoor - design v6.3 (from v6.2).

Owner requests (2026-11-10):
 1. Cable channel removed (canalina_base/coperchio/tappo + 4 wood screws 3.5x16). The 12 V cable leaves at the flange rim
    (270 deg) through the curved tunnel + TPU grommet and is routed by the user with ordinary clips. NEW strain relief at the
    exit: the tunnel is raised so the cable runs 0.4 mm proud of the shelf face over its last 7 mm (the shelf clamps it when
    the flange is screwed on), plus a cable-tie pocket (window through the upper plate, r 81.5..86.5): a UV-stable tie
    cinched round the cable there cannot pass the Ø5.6 bore, so a pull or bite outside is taken by the 3.5 mm rim wall and
    never reaches the M8 connector (which stays in the pod top as in v6.2). Rounded bell mouth at the exit.
 2. Fewer printed parts (36 -> 28 pieces):
    - 3 thumb-turns (+ 3 keys + 3 O-rings 8x1.5 + 3 cups) -> 3 thread-forming screws PT K30x12 (no inserts) with an O-ring
      3x1 under each head, in Ø7 counterbores in the flat bottom: they draw the cap home (no ~130 N push), the cap bosses
      bottom on the box bosses (hard stop = same lip compression as v6.2). A twist-lock cap was rejected: the dry-box seal is
      a D-shaped lip and the outlet socket is 31.8 mm off the seam centre, so the cap cannot rotate at all.
      Screw sites: A (15.75, 30) and C (19.5, 0) in the dry servo|board corridor (sealed heads), B (-20, -33) in the wet ring.
    - flange join screws 3x ST2.9 -> 3 press-fit pins on the upper plate (the 4 wood screws clamp the set in service)
    - chute + shell-tab screws -> PT K30 straight into the bowl: 5 heat-set inserts fewer (12 -> 7)
    - gate blade printed in ONE colour (green; its arm is hidden in the flange): -15 colour swaps
    - lower flange: the printed pivot pin is replaced by an ISO 2338 4x6 dowel (print_v62 correction folded in)
    - stack screw P3 moved 0.775 mm -X and given a Ø7.5 head pocket in the solid cradle top: >= 1.0 mm round the head
 3. Control panel in the pod cap, room side (centred on the release-button azimuth 76.5 deg): a straight-ruled band
    (z -98..-74.6, recessed <= 1.7 mm, smooth creases, 4 deg ramps at the ends) carrying 2 flush light pipes, the
    IP67 12 mm push-button in a paw-proof recess (Ø17 x 8 deep) and 3 knock-outs (19 deg from the button, then 16 deg pitch), FLUSH
    with the band (QC 2026-11-10): outside only a 0.3 mm engraved Ø12 ring + centre dot; 2.0 mm skin (1.7 under the engraving),
    thinned from the inside by a blind Ø12.4 counterbore, flat nut-seat pad behind it. Behind the band the cap forms a closed DRY pocket that opens into the D interior under the box (below
    the lip beam): the panel is the dry-box wall itself, no new joint, no gasket. Speaker on the dry floor under the
    panel, acoustic grille (7 x Ø1.5) facing down with an IP67 ePTFE acoustic membrane inside.
    The +X wet sump of v6.1.1/v6.2 (closed off by the D corners below z -91, no drain) gets its own labyrinth drain.
 4. Everything else as v6.2.
Release 6.3.0 fixes (QC 2026-11-10): LED light pipes square to the band face (no lens edge proud), pair moved to z -84 / -93
so the LED wells clear the pocket roof; lower-flange dowel seat gets a full 360 deg wall (the funnel opening apex is pulled
back to r 4.6; the pivot stays on the shaft axis because blade and ring turn about it together); cap seam spigot ring
joined to the cap wall by a 45 deg chamfered collar (it was a separate body 0.1-0.2 mm inside the wall with a flat 2.45 mm
underside); the groove is unchanged. All outputs are written to hidden temp names and renamed together at the end.
Frame and pose as v6.2 (Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED pose, gate OPEN).
No existing file is modified: changed/new parts carry the suffix _v63; unchanged parts are reused from v6.2 / v6.1.1 / v6.1.

Status: designed and checked in CAD only; not printed, assembled or tested yet. Hardware 6.3.0.

Run from anywhere:  python hardware/v6.3/cad/build_v63.py
  1. runs the earlier stages first when their outputs are missing or older than their scripts, each into build/:
     build_v6.py (which runs build_dosing.py and build_v5.py), build_v61.py, build_v611.py and build_v62.py, all with their
     checks, because v6.3 imports their parameters and reuses their parts, JSON files and assembled-position copies;
  2. builds and exports the v6.3 parts, runs the checks (build_v63_checks.py, which runs build_v63_report.py) and writes
     v63.json, v63_viewer.json, check_v63.png, the drilling template (template_v63/) and the assembled-position copies
     (v63_asm/), all in build/;
  3. publishes the repository files with publish_v63.py: ../assembly (viewer meshes and manifest), ../template
     (drilling template), v63.json and check_v63.png. The print package in ../plates is rebuilt from build/ by
     ../plates/tools/run_all.sh (needs the OrcaSlicer command line for the slicer check).
Optional argument: "build" stops after building, "parts" after exporting to build/ (no checks, no publishing).
The grams and pieces comparison with v6.2 reads the committed v6.2 print package (../../v6.2/plates/summary.json and stl/).
Dependencies: trimesh, manifold3d, shapely, mapbox_earcut, rtree, numpy, scipy, networkx, lxml, matplotlib, fast_simplification.
"""
import json
import math
import os
import sys
import contextlib
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, Point, box as sbox, LineString
from shapely import affinity
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_V5 = ['build_drivetrain.py', 'layout_v4.json', 'build_dosing.py', 'build_v5.py', 'build_v5_checks.py']
_V6 = _V5 + ['build_v6.py', 'build_v6_checks.py']
_V61 = _V6 + ['build_v61.py', 'build_v61_checks.py']
_V611 = _V61 + ['build_v611.py', 'build_v611_checks.py', 'los.py', 'ref/measure_v61.json']
_PREREQUISITES = (     # script, inputs it depends on, outputs v6.3 reads from build/
    ('build_v6.py', _V6, ['v6.json']),
    ('build_v61.py', _V61, ['v61.json', 'v61_viewer.json']),
    ('build_v611.py', _V611, ['v611.json', 'v611_viewer.json']),
    ('build_v62.py', _V611 + ['build_v62.py', 'build_v62_checks.py', 'toolaccess.py', 'ref/ta_v611.json'], ['v62.json', 'v62_viewer.json']),
)


def _ensure_prerequisites():
    """Run the earlier stages (v6, v6.1, v6.1.1, v6.2, each with its checks) when an output is missing or out of date."""
    for script, deps, outputs in _PREREQUISITES:
        newest = max(os.path.getmtime(os.path.join(_HERE, f)) for f in deps)
        paths = [os.path.join(_HERE, 'build', o) for o in outputs]
        if all(os.path.exists(q) and os.path.getmtime(q) >= newest for q in paths):
            continue
        print(f'--- running {script} first ---', flush=True)
        subprocess.run([sys.executable, os.path.join(_HERE, script)], check=True)


if __name__ == '__main__':
    _ensure_prerequisites()

import build_v62 as b62
from build_v62 import (b611, b61, v6, v5, dt, bd, OUT, U, D, I, cyl, box, at, hull_of, circle_pts, revolve, prism, ring2d,
                       below, above, polar, rotz, text_poly, face_region, overhang, vol, SEG, pod_solid, pod_circle, section_fn,
                       shell_r_at, radial_cyl, report, PETG, TPU, Z_TOP, R_TOP, Z_BOT, Z_S, T_SHELL, T_CAP, BXO, BX_T, Z_R, Z_W,
                       BOX_OUT, BOX_IN, ROOF_T, CRADLE_HALF_X, CAGE_Z0, BB, GLAND, CH_X, RI, RO, FL_Z0, FL_Z1, LATCH_A, BTN_Z,
                       TAB_ANG, TAB_R_INS, TAB_T, HOOKS61, PIN_ANG61, NF, tube_path, G0, G1, W0, W1)
from build_v62 import (FL_Z1_62, FL_R62, DZ_FL, OPEN_HALF, LEAD_OPEN, STROKE, BLADE_R, BLADE_Z, POCKET_Z1, PIVOT_D, ARM_ANG, PEG,
                       RING, RING_GRV, RING_BARB, RING_SLOT, WIN_ANG, DRAIN_ANG, WOOD_ANG62, WOOD_R62, JOIN, TUN, CABLE_ANG,
                       CABLE_D, CONN62, EAR_R, EAR_Z0, EAR_ROOT, SCREW_LEN, INS_DEPTH62, OR_3x1, VENT62, P_SEALED,
                       blade_sector, arm_poly, sector_ring, funnel62, pocket2d, gate_pose, rz_to_xyz, ang_of, screw_m3_up)

VER = 'v6.3'
SFX = '_v63'
SCRATCH = OUT                                               # probe exports, previews (build/)
ASM = OUT + 'v63_asm/'
TPL = OUT + 'template_v63/'
for _d in (SCRATCH, ASM, TPL):
    os.makedirs(_d, exist_ok=True)
v6.SCRATCH = SCRATCH
STAGED = []                                                 # (temp, final): every output is renamed in one pass at the end


def staged(path):
    """hidden temp name in the same folder (same extension, so exporters keep the format); renamed by commit_staged()"""
    d_, b_ = os.path.split(path)
    tmp = os.path.join(d_, '.tmp63_' + b_)
    STAGED.append((tmp, path))
    return tmp


def current(path):
    """the file as this run sees it: the staged temp if it was written in this run, else the existing file"""
    for tmp, final in STAGED:
        if final == path and os.path.exists(tmp):
            return tmp
    return path


def commit_staged():
    for tmp, final in STAGED:
        if os.path.exists(tmp):
            os.replace(tmp, final)
    print(f'committed {len(STAGED)} files (temp -> final)')


@contextlib.contextmanager
def patched(mod, **kw):
    """temporarily set module attributes (the earlier builders read their parameters from module globals)"""
    old = {k: getattr(mod, k) for k in kw}
    for k, v in kw.items():
        setattr(mod, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(mod, k, v)


# =====================================================================================
# PARAMETERS v6.3
# =====================================================================================
# ---- stack screws: P3 0.775 mm -X (head 1.15 mm from the board) + Ø7.5 head pocket in the solid cradle top ----
P_SCREWS = [(-18.25, 24.5), (-1.5, -25.5), (17.6, 14.0)]
P3_POCKET_D = 7.5                                           # Ø5.5 head + 1.0 all round
# ---- cap retention: 3 thread-forming screws (no inserts), O-ring 3x1 under each head ----
CAP_SCREWS = {'A': (15.75, 30.0), 'B': (-21.2, -33.0), 'C': (19.5, 0.0)}     # A, C dry (corridor), B wet ring
CAP_SEAT_Z = Z_BOT + 3.5                                    # head seat (counterbore floor) -100.5
CAP_CB_D = 7.0                                              # counterbore for the pan head (Ø6.0)
CAP_BOSS_TOP = -96.5                                        # cap boss top = box boss bottom (hard stop)
PT = dict(d=3.0, pilot=2.5, head_d=6.0, head_h=2.4, len_cap=12.0, len_tab=12.0, len_chute=10.0)
BOX_BOSS_D = 8.0
PILOT_DEPTH = 10.5                                          # box boss pilot (K30x12: 8 mm engagement + 2.5 tip room)
COL_A = dict(x0_lo=12.0, x0_hi=CRADLE_HALF_X - 0.01, x1=19.5, y0=26.5, y1=33.5)   # A hanger column (servo | board corridor)
BOWL_PILOT = dict(d=2.5, depth=v6.INS_DEPTH, csk=0.4)      # chute ears + shell tabs: PT K30 pilots where the inserts were
# ---- flange ----
DOWEL = dict(d=4.0, depth=2.7, len=6.0)                     # ISO 2338 4 m6 x 6 A2, pressed into the lower plate
PIVOT_WALL_R = 4.6                                          # 6.3.0: funnel opening apex pulled back to r 4.6 -> 2.6 mm wall all round the seat
OPENING63 = v5.OPENING.difference(Point(0, 0).buffer(PIVOT_WALL_R, resolution=64))
FPIN = dict(d=3.0, h=2.8, hole_d=3.0, hole_depth=3.0, ch=0.4)   # press-fit pins (upper plate -> lower plate) at the JOIN sites
TUN63 = dict(TUN, zh=76.0)                                  # cable centre at the rim exit: top 78.5 = 0.4 proud of the shelf face
TIE_POCKET = dict(r0=80.8, r1=86.8, half_w=8.5)             # cable-tie window through the upper plate (floor = lower plate)
BELL = dict(r0=88.0, d1=8.0)                                # rounded exit: bore Ø5.6 -> Ø8.0 at the rim
SPIG_COLLAR, LED_NORMAL = True, True                         # 6.3.0 fixes (switches kept for A/B checks)
SPIG_COLLAR_RW = 70.2                                       # collar reaches r 70.2 from the seam centre: >= 0.44 into the wall, >= 0.7 from the skin
RING_WIN_TOP = 15.2                                         # ring window: teardrop top (45 deg) cut flat 15.2 above the centre
# ---- control panel (in the cap, room side) ----
ZB0, ZB1 = -98.0, -74.6                                     # band creases (flush with the skin)
PHI_A, PHI_B, PHI_RAMP = 38.0, 132.0, 6.0                   # band ends (section frame) + side ramps (cut starts mid-ramp)
B_MARGIN = 2.0                                              # B stands 2 mm outside the skin off the band (no slivers)
Z_E = -87.0                                                 # element row height
TILT = 3.0                                                  # element axes 3 deg down-outward (recesses drain)
PITCH = 16.0                                                # knock-out grid pitch (20.35 -> 19.1 mm on the band)
BTN_KO_GAP = 19.0                                           # button -> KO1: a future switch in KO1 clears the button boss and nut
KO_DZ = -1.5                                                # knock-out row 1.5 below the button: a future switch body (axis on the
                                                            # facet normal, rising inward) clears the pocket roof
ELEMS = [('led1', 51.0, 3.0), ('led2', 51.0, -6.0), ('btn', 67.0, 0.0), ('ko1', 67.0 + BTN_KO_GAP, KO_DZ), ('ko2', 67.0 + BTN_KO_GAP + PITCH, KO_DZ),
         ('ko3', 67.0 + BTN_KO_GAP + 2 * PITCH, KO_DZ)]    # (name, phi in the section frame, dz): LEDs as a vertical pair, status on top
REC = dict(d=17.0, face=8.0, floor=9.5, wall=3.0, boss_d=23.0, hole=12.2, ch=0.5)   # the real button: paw-guard recess
# knock-outs FLUSH with the band (QC 2026-11-10): no outer recess, only a 0.3 mm engraved ring (Ø12 = the future hole) and
# a centre dot (pilot mark). The outer wall is the skin: 2.0 mm (1.7 under the engraving), thinned only from the inside by a
# blind Ø12.4 counterbore whose floor follows the facet. Behind it a flat nut-seat pad (face perpendicular to the axis) for
# a future 12 mm switch. Future switch envelope (checks only): nut 14 AF (Ø16.2 corners) swinging with 0.3 clearance,
# Ø13 body 11.5 long behind the nut.
KO = dict(ring_d=12.0, ring_w=0.6, engr=0.3, dot_d=1.2, skin=2.0, bore=12.4, pad_d=19.0, pad=4.8,
          nut_d=16.2, nut_h=2.5, nut_swing=0.3, body_d=13.0, body_len=11.5)
KO_COS = math.cos(math.radians(14.0))
LED = dict(hole=5.1, boss_d=10.0, len=9.0, cb_d=7.2, cb_depth=0.75, well_d=9.0, well_len=7.0)
BAND_WALL = 3.0
POCKET = dict(phi0=44.0, phi1=128.0, rho_ci=39.5, wall=2.5, roof_top=-74.0, roof_t=2.0, slope_deg=1.0, x_east=46.0)
SPK = dict(x=-4.0, y=44.5, d=20.0, h=4.5, grille_r=2.6, hole=1.5, cup_id=21.0, cup_t=1.5, cup_h=4.5)
DRAIN2 = dict(xy=(44.6, 0.0), boss_r=4.6, boss_top=-97.5, ch_r=2.2, ch_z=(-102.3, -98.8), slit_w=0.8, slit_z=(-101.6, -100.6),
              slit_ang=(0.0, 90.0, 270.0), holes_d=0.8, holes_r=1.0, n_holes=4)


# =====================================================================================
# 1. TOWER / BOWL with P3 moved; bowl: PT pilots for chute ears and shell tabs (inserts only at P1..P3)
# =====================================================================================
def build_column63():
    with patched(b62, P_SCREWS=P_SCREWS):
        return b62.build_column62()


def build_bowl63(F):
    cav_fl, out_fl, cav_m, out_m = F
    lugs = [bd.lug(a, w) for a, w in zip(bd.LUG_ANG, bd.LUG_W)]
    tongue = D(cyl(2 * bd.TONGUE_R1, bd.RIM_Z - 0.5, bd.RIM_Z + bd.TONGUE_H, 2 * SEG), cyl(2 * bd.TONGUE_R0, bd.RIM_Z - 1, bd.RIM_Z + 3, 2 * SEG))
    body = U([cyl(2 * bd.BOWL_R_OUT, 0.0, bd.RIM_Z, n=2 * SEG), out_fl, I(out_m, above(0.0)), tongue] + lugs)
    p0, p1, dd = b61.DRAIN
    v = p1 - p0
    drain = trimesh.creation.cylinder(radius=dd / 2, height=np.linalg.norm(v), sections=32)
    drain.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / np.linalg.norm(v)))
    drain.apply_translation((p0 + p1) / 2)
    cav = [cyl(2 * bd.BOWL_R_IN, G0, W0 + 0.01, n=2 * SEG), cyl(2 * bd.BOWL_R_STEP, W0, bd.RIM_Z + 5, n=2 * SEG),
           bd.central_cavity(), cav_fl, cav_m, cyl(bd.BASE_HOLE_D, -1, bd.BASE_Z1 + 1, 96),
           D(cyl(2 * b61.RG_R1, b61.RG_Z0, bd.RIM_Z + 1, 2 * SEG), cyl(2 * b61.RG_R0, b61.RG_Z0 - 1, bd.RIM_Z + 2, 2 * SEG)),
           below(0.0), drain] + bd.latch_slot_cuts()
    for x, y in P_SCREWS:                                    # stack inserts (as v6.2, P3 moved)
        cav.append(at(U([cyl(v6.INS_D, -1.0, INS_DEPTH62, 48), cyl(v6.INS_D + 1.6, -1.0, 0.4, 48)]), x, y))
    for x, y in list(b61.CH_EARS) + list(b61.TAB_INS):     # PT K30 pilots (no inserts), 0.4 x 45 deg entry chamfer
        p = BOWL_PILOT
        cav.append(at(U([cyl(p['d'], -1.0, p['depth'], 32), hull_of((circle_pts(p['d'] + 2 * p['csk'] + 0.02, 32), -0.01),
                                                                   (circle_pts(p['d'], 32), p['csk']))]), x, y))
    bowl = D(body, cav)
    ribs = []
    for a in bd.KEY_ANG:
        ribs.append(rotz(box(bd.BOWL_R_IN - bd.KEY_PROT_GATE, bd.BOWL_R_IN + 0.5, -bd.KEY_W / 2, bd.KEY_W / 2, G0, W0), a))
        ribs.append(rotz(box(bd.BOWL_R_STEP - bd.KEY_PROT_WIN, bd.BOWL_R_STEP + 0.5, -bd.KEY_W / 2, bd.KEY_W / 2, W0, b61.RG_Z0 - 0.5), a))
    return U([bowl] + ribs)


# =====================================================================================
# 2. BOX (scatola_v63): v6.2 box with the 3 thumb-turn cups replaced by PT screw bosses (A, C on corridor columns, B on a
#    -X wall web), P3 moved + Ø7.5 head pocket
# =====================================================================================
def _column(c, z_bot):
    """corridor hanger column (as v6.1.1 COL_C): cradle +X face -> roof above the cradle bottom, wider below it, 45 deg step"""
    return U([box(c['x0_hi'], c['x1'], c['y0'], c['y1'], CAGE_Z0 - 2.0, Z_R - 0.5),
              box(c['x0_lo'], c['x1'], c['y0'], c['y1'], z_bot - 0.01, CAGE_Z0 - 2.0),
              trimesh.convex.convex_hull(np.array([[xx, yy, zz] for yy in (c['y0'], c['y1']) for xx, zz in
                                                   ((c['x0_lo'], CAGE_Z0 - 2.0), (c['x0_hi'], CAGE_Z0 - 2.0),
                                                    (c['x0_hi'], CAGE_Z0 - 2.0 + (c['x0_hi'] - c['x0_lo'])))]))])


def build_box63():
    walls = prism(ring2d(BOX_OUT, BOX_IN), Z_W, Z_R - ROOF_T + 0.01)
    roof = prism(BOX_OUT, Z_R - ROOF_T, Z_R)
    rim = prism(ring2d(BOX_OUT.buffer(b61.FL_OUT, join_style=1, resolution=16), BOX_IN), Z_W, Z_W + 3.0)
    boss = prism(Point(0, 0).buffer(v6.BOSS_R, resolution=96).intersection(BOX_OUT), v6.BOSS_Z0, Z_R - 1.0)
    cage = prism(sbox(-CRADLE_HALF_X, b61.CAGE_Y[0], CRADLE_HALF_X, b61.CAGE_Y[1]), CAGE_Z0, Z_R - 1.0)
    parts = [walls, roof, rim, boss, cage]
    slot_cuts = []
    for sy in (1, -1):                                       # perfboard slot blocks (as v6.1)
        y_in, y_end = sy * (BOX_IN.bounds[3] + 0.5), sy * (BB['y'][1] - 2.0)
        parts.append(box(BB['x'][0] - 2.0, BB['x'][1] + 2.0, min(y_in, y_end), max(y_in, y_end), Z_W + 3.0, Z_R - 1.0))
        slot_cuts.append(box(BB['x'][0] - 0.15, BB['x'][1] + 0.15, min(y_in, sy * (BB['y'][1] - 3.0)), max(y_in, sy * (BB['y'][1] - 3.0)),
                             Z_W - 1.0, BB['z'][1] + 0.3))
    parts.append(b61._wall_pad(GLAND, GLAND['pad_d']))
    # PT screw bosses: B on a web from the -X wall (wet ring), A and C hung from corridor columns (dry)
    bx, by = CAP_SCREWS['B']
    parts += [at(cyl(BOX_BOSS_D, CAP_BOSS_TOP, Z_R, 48), bx, by), box(bx + BOX_BOSS_D / 2 - 1.0, BXO[0] + 0.5, by - 3.5, by + 3.5, Z_W, Z_R)]
    ax, ay = CAP_SCREWS['A']
    parts += [at(cyl(BOX_BOSS_D, CAP_BOSS_TOP, CAGE_Z0 - 2.0, 48), ax, ay), _column(COL_A, CAP_BOSS_TOP + 4.0)]
    cx_, cy_ = CAP_SCREWS['C']
    parts += [at(cyl(BOX_BOSS_D, CAP_BOSS_TOP, b611.CUP_TOP_C, 48), cx_, cy_), _column(b611.COL_C, b611.CUP_TOP_C)]
    # P1 ear (as v6.2)
    x1, y1 = P_SCREWS[0]
    ear2d = shapely.unary_union([Point(x1, y1).buffer(EAR_R, resolution=32), sbox(BXO[0] - 0.5, y1 - EAR_ROOT, BXO[0] + 1.0, y1 + EAR_ROOT)]).convex_hull
    parts.append(prism(ear2d, EAR_Z0, Z_R))
    body = U(parts)
    cuts = [box(-CRADLE_HALF_X + 2.5, CRADLE_HALF_X - 2.5, b61.VOID_Y[0], b61.VOID_Y[1], CAGE_Z0 - 1.0, v6.S_TOP + 0.5),
            cyl(2 * dt.HUB_CAV_R, v6.S_TOP + 0.5 - 0.01, v6.CAV_TOP + 0.01, 96),
            hull_of((circle_pts(2 * dt.HUB_CAV_R, 96), v6.CAV_TOP), (circle_pts(2 * v6.PLAT_HOLE_R, 96), v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R)),
            cyl(2 * v6.PLAT_HOLE_R, v6.CAV_TOP + dt.HUB_CAV_R - v6.PLAT_HOLE_R - 0.01, Z_R + 1.0, 96),
            b61._wall_pad(GLAND, GLAND['hole_d'], True), at(cyl(VENT62['hole_d'], Z_R - ROOF_T - 1, Z_R + 1, 48), VENT62['x'], VENT62['y'])] + slot_cuts
    for x, y in b61.SERVO_HOLES_W:
        cuts.append(at(U([cyl(v6.INS_D, CAGE_Z0 - 1, CAGE_Z0 + dt.SERVO_INS_DEPTH, 48),
                          hull_of((circle_pts(v6.INS_D + 1.8, 48), CAGE_Z0 - 0.5), (circle_pts(v6.INS_D, 48), CAGE_Z0 + 0.4))]), x, y))
    for x, y in CAP_SCREWS.values():                         # PT pilots in the box bosses
        cuts.append(at(U([cyl(PT['pilot'], CAP_BOSS_TOP - 1.0, CAP_BOSS_TOP + PILOT_DEPTH, 32),
                          hull_of((circle_pts(PT['pilot'] + 0.82, 32), CAP_BOSS_TOP - 0.01), (circle_pts(PT['pilot'], 32), CAP_BOSS_TOP + 0.4))]), x, y))
    cuts.append(at(cyl(3.4, EAR_Z0 - 1.0, Z_R + 1.0, 32), x1, y1))
    zr0 = Z_R - ROOF_T
    for k, ((x, y), sealed) in enumerate(zip(P_SCREWS[1:], P_SEALED[1:])):
        cuts.append(at(cyl(3.4, zr0 - 1.0, Z_R + 1.0, 32), x, y))
        cuts.append(at(cyl(P3_POCKET_D if k == 1 else 6.6, v6.BOSS_Z0 - 1.0, zr0 + 0.01, 48), x, y))
        c = OR_3x1['csk_d']
        cuts.append(at(hull_of((circle_pts(c, 48), zr0 - 0.01), (circle_pts(3.4, 48), zr0 + (c - 3.4) / 2)), x, y))
    cuts.append(face_region(text_poly(f'{VER} DRY', 6.0, 20.0, 0.0), Z_R, True))
    return D(body, cuts)


# =====================================================================================
# 3. CAP (fondello_v63): v6.1.1 cap without thumb-turns; PT screw bosses + counterbores; 2nd drain; control panel
# =====================================================================================
def loft_rings(rings):
    """closed solid from a list of (n, 3) rings (same n, increasing z), capped at both ends"""
    n = len(rings[0])
    V = np.vstack(rings + [rings[0].mean(axis=0, keepdims=True), rings[-1].mean(axis=0, keepdims=True)])
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
    assert s.is_watertight, 'loft not watertight'
    return s


_C0, _R0 = pod_circle(0.0, ZB0)
_C1, _R1 = pod_circle(0.0, ZB1)


def band_rho(z):
    """facet radius (moving frame centred on the skin section centre): straight chord of the skin between the creases"""
    return _R0 + (_R1 - _R0) * (z - ZB0) / (ZB1 - ZB0)


def ramp_w(phi):
    """1 on the band, smooth 0 -> 1 over PHI_RAMP at both ends"""
    def ss(t):
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3 - 2 * t)
    return ss((phi - PHI_A) / PHI_RAMP) * ss((PHI_B - phi) / PHI_RAMP)


def band_solid():
    """B: equals the skin + 0.6 everywhere except on the band, where it is the ruled facet; cap := I(cap, B)"""
    # the facet is linear in z (straight generatrices), so few levels are exact on the band; 0.5 deg in plan
    zs = np.unique(np.r_[Z_BOT - 1.0, np.linspace(Z_BOT + 0.01, ZB0 - 1.0, 24), np.linspace(ZB0 - 1.0, ZB1 + 1.0, 14), np.linspace(ZB1 + 1.0, -66.0, 8)])
    ph = np.linspace(0.0, 360.0, 720, endpoint=False)
    w = ramp_w(ph)
    rings = []
    for z in zs:
        cx, R = pod_circle(0.0, min(max(z, Z_BOT + 0.01), -60.0))
        rf = band_rho(z)
        rho = (R + B_MARGIN) - w * max(0.0, R + B_MARGIN - rf)
        a = np.radians(ph)
        rings.append(np.c_[cx + rho * np.cos(a), rho * np.sin(a), np.full(len(ph), z)])
    return loft_rings(rings)


def band_inner_solid(off):
    """circle loft at the facet radius minus `off` (moving frame): the dry pocket stays inside it"""
    zs = np.linspace(Z_BOT - 1.0, -66.0, 40)
    ph = np.radians(np.linspace(0.0, 360.0, 720, endpoint=False))
    rings = []
    for z in zs:
        cx, _ = pod_circle(0.0, min(max(z, Z_BOT + 0.01), -60.0))
        r = band_rho(z) - off
        rings.append(np.c_[cx + r * np.cos(ph), r * np.sin(ph), np.full(len(ph), z)])
    return loft_rings(rings)


def facet_point(phi_rad, z):
    cx, _ = pod_circle(0.0, z)
    r = band_rho(z)
    return np.array([cx + r * math.cos(phi_rad), r * math.sin(phi_rad), z])


def elem_frame(phi, z=Z_E, normal=False):
    """(P, n): facet point and outward axis. Default: horizontal radial in the moving frame, tilted TILT down-outward
    (light pipes, button recess). normal=True: the true facet normal (flush knock-outs: a future switch gasket must seat
    square on the outer face; the tapered pod makes the facet face 10-14 deg downward)"""
    a, t = math.radians(phi), math.radians(TILT)
    P = facet_point(a, z)
    if normal:
        tz = (facet_point(a, z + 0.01) - facet_point(a, z - 0.01)) / 0.02
        tp = (facet_point(a + 1e-4, z) - facet_point(a - 1e-4, z)) / 2e-4
        n = np.cross(tp, tz)
        n /= np.linalg.norm(n)
        return P, (n if n @ (P - np.array([pod_circle(0.0, z)[0], 0.0, z])) > 0 else -n)
    n = np.array([math.cos(a) * math.cos(t), math.sin(a) * math.cos(t), -math.sin(t)])
    return P, n


def axial_cyl(P, n, d, t0, t1, sec=64):
    """cylinder of diameter d along -n from depth t0 to t1 (depth measured inward from P)"""
    c = trimesh.creation.cylinder(radius=d / 2, height=t1 - t0, sections=sec)
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], -n))
    c.apply_translation(P - n * (t0 + t1) / 2)
    return c


def axial_cone(P, n, d0, t0, d1, t1, sec=64):
    c0 = circle_pts(d0, sec); c1 = circle_pts(d1, sec)
    R = trimesh.geometry.align_vectors([0, 0, 1], -n)[:3, :3]
    pts = [np.c_[c, np.zeros(len(c))] @ R.T + P - n * t for c, t in ((c0, t0), (c1, t1))]
    return trimesh.convex.convex_hull(np.vstack(pts))


def pocket_plans():
    """(cavity plan, solid plan) in world XY; sector in the moving frame at the element row"""
    cx, _ = pod_circle(0.0, Z_E)
    pc = POCKET
    a = np.radians(np.linspace(pc['phi0'], pc['phi1'], 200))
    sector = Polygon(np.r_[[[cx, 0.0]], np.c_[cx + 120 * np.cos(a), 120 * np.sin(a)]])
    # the pocket may only open the +Y side of the D upstand (y >= 36); everything stays on the room side (y >= 30), so the
    # sector apex can never reach the -X upstand wall next to the outlet socket
    reach = shapely.unary_union([Point(cx, 0).buffer(200, resolution=8).difference(Point(cx, 0).buffer(pc['rho_ci'], resolution=128)),
                                 BOX_OUT.buffer(b611.UP_OUT + 0.3, join_style=1, resolution=16).intersection(sbox(-200, 36.0, 200, 200))])
    d_inner = BOX_OUT.buffer(-b611.UP_IN - 1.0, join_style=1, resolution=16)      # cavity runs 1 mm past the upstand inner face
    cav = sector.intersection(reach).difference(d_inner).intersection(sbox(-200, 30.0, 200, 200))
    sol = cav.buffer(pc['wall'], join_style=2).difference(d_inner)
    return cav, sol


def roof_halfspace(z_east):
    """solid below the plane z = z_east at x = x_east, falling westward (-x) at POCKET slope (water runs to the west end)"""
    pc = POCKET
    big = box(-300, 300, -300, 300, -400.0, 0.0)
    big.apply_translation([0, 0, z_east])
    T = trimesh.transformations.rotation_matrix(-math.radians(pc['slope_deg']), [0, 1, 0], point=[pc['x_east'], 0, z_east])
    big.apply_transform(T)
    return big


def drain2_parts():
    p = DRAIN2
    xd, yd = p['xy']
    bos = at(cyl(2 * p['boss_r'], Z_BOT - 1, p['boss_top'], 64), xd, yd)
    cuts = [at(cyl(2 * p['ch_r'], p['ch_z'][0], p['ch_z'][1], 64), xd, yd)]
    for a in p['slit_ang']:
        cuts.append(at(rotz(box(p['ch_r'] - 0.5, p['boss_r'] + 1.0, -p['slit_w'] / 2, p['slit_w'] / 2, *p['slit_z']), a), xd, yd))
    for k in range(p['n_holes']):
        hx, hy = polar(p['holes_r'], 45.0 + 90.0 * k)
        cuts.append(at(cyl(p['holes_d'], Z_BOT - 2, p['ch_z'][0] + 0.01, 24), xd + hx, yd + hy))
    return bos, cuts


def floor_screed2(clip_in, keep_out):
    """1.5 deg cones rising away from BOTH drains (the floor takes the lower of the two): every wet region drains"""
    s = math.tan(math.radians(b611.FLOOR_SLOPE_DEG))
    R = 140.0
    cones = []
    for xd, yd in (b611.DRAIN_XY, DRAIN2['xy']):
        c = revolve([(0.0, Z_BOT + T_CAP - 0.6), (R, Z_BOT + T_CAP - 0.6), (R, Z_BOT + T_CAP + s * R), (0.0, Z_BOT + T_CAP)], 96)
        if c.volume < 0:
            c.invert()
        cones.append(at(c, xd, yd))
    return D(I(I(cones[0], cones[1]), clip_in), [keep_out])


def future_switch(P, n):
    """envelope of a future 12 mm switch fitted in a drilled-out knock-out (checks only): thread through the skin and the
    pad, nut swing volume on the pad face, body behind it"""
    k = KO
    return {'thread': axial_cyl(P, n, 12.0, -0.5, k['pad'], 48),
            'nut_swing': axial_cyl(P, n, k['nut_d'] + 2 * k['nut_swing'], k['pad'] + 0.01, k['pad'] + k['nut_h'], 64),
            'body': axial_cyl(P, n, k['body_d'], k['pad'] + k['nut_h'], k['pad'] + k['nut_h'] + k['body_len'], 48)}


def panel_parts():
    """dict of the panel solids/cuts in world coordinates"""
    out = {'bosses': [], 'cuts': [], 'cav_extra': [], 'frames': {}}
    for name, phi, dz in ELEMS:
        P, n = elem_frame(phi, Z_E + dz, normal=name.startswith('ko') or (LED_NORMAL and name.startswith('led')))   # square to the band face
        out['frames'][name] = (P, n, phi)
    # band_inner_solid offsets in plan; the facet leans 10-14 deg, so the plan offsets are divided by cos(14 deg) to give the
    # skin and the engraving depth normal to the facet
    skin_in = band_inner_solid(KO['skin'] / KO_COS)          # deeper than the skin: the knock-out counterbore may cut there
    engr_in = band_inner_solid(KO['engr'] / KO_COS)          # deeper than the engraving: never cut by it
    for name, phi, dz in ELEMS:
        P, n, _ = out['frames'][name]
        if name.startswith('led'):
            out['bosses'].append(axial_cyl(P, n, LED['boss_d'], -1.0, LED['len'], 48))
            out['cuts'] += [axial_cyl(P, n, LED['hole'], -4.0, LED['len'] + 0.05, 48),
                            axial_cyl(P, n, LED['cb_d'], LED['len'] - LED['cb_depth'], LED['len'] + 0.05, 48)]
            out['cav_extra'].append(axial_cyl(P, n, LED['well_d'], LED['len'], LED['len'] + LED['well_len'], 48))
        elif name == 'btn':                                  # the real button: Ø17 x 8 paw-guard recess, unchanged
            r = REC
            out['bosses'].append(axial_cyl(P, n, r['boss_d'], -1.0, r['floor'] + r['wall'], 96))
            out['cuts'] += [axial_cyl(P, n, r['d'], -8.0, r['floor'], 96),
                            axial_cone(P, n, r['d'] + 2 * r['ch'] + 2.0, -1.0, r['d'], r['ch'] + 0.0),
                            axial_cyl(P, n, r['hole'], r['floor'] - 0.1, r['floor'] + r['wall'] + 0.1, 96)]
        else:                                                # knock-out: flush, engraved mark outside, counterbore inside
            k = KO
            out['bosses'].append(axial_cyl(P, n, k['pad_d'], -1.0, k['pad'], 96))
            ring = D(axial_cyl(P, n, k['ring_d'] + k['ring_w'], -2.0, 1.5, 96), [axial_cyl(P, n, k['ring_d'] - k['ring_w'], -3.0, 2.0, 96)])
            out['cuts'] += [I(axial_cyl(P, n, k['bore'], -1.0, k['pad'] + 0.1, 96), skin_in),
                            D(U([ring, axial_cyl(P, n, k['dot_d'], -2.0, 1.5, 24)]), [engr_in])]
    return out


def build_cap63(with_panel=True):
    outer = pod_solid(0.0, z_hi=Z_S - b611.SEAM)
    inner = pod_solid(T_CAP)
    shell = D(outer, [inner])
    clip_in = pod_solid(T_CAP - 0.3)
    up = I(prism(ring2d(BOX_OUT.buffer(b611.UP_OUT, join_style=1, resolution=16), BOX_OUT.buffer(-b611.UP_IN, join_style=1, resolution=16)),
                 Z_BOT - 5, b61.Z_C), clip_in)
    so, si = b611.SEAM_R - (b611.SPIG_OFF - T_SHELL), b611.SEAM_R - (b611.SPIG_IN - T_SHELL)
    zt, rw = Z_S - b611.SEAM, SPIG_COLLAR_RW
    spig = at(D(cyl(2 * so, zt - 0.6, b611.SPIG_TOP, 512), cyl(2 * si, zt - 1.6, b611.SPIG_TOP + 1, 512)), b611.SEAM_CX, 0)
    # 6.3.0: the spigot ring sat 0.1-0.2 mm inside the cap wall (separate body, flat 2.45 mm underside): a collar joins it to
    # the wall 0.4 below the cap top (a top face coplanar with the cap top gave float32 slivers on export), its underside a
    # 45 deg chamfer from the ring bore down into the wall (prints without support); the O-ring groove is unchanged
    collar = revolve([(si, zt - 0.4), (rw, zt - 0.4), (rw, zt - 0.4 - (rw - si))], 512)
    if collar.volume < 0:
        collar.invert()
    if SPIG_COLLAR:
        spig = U([spig, at(collar, b611.SEAM_CX, 0)])
    tube = I(at(cyl(2 * b611.SOCK['r_out'], Z_BOT - 5, b611.SOCK['top'], NF), CH_X, 0), clip_in)
    sup = [I(box(BB['x'][0] - 1.0, BB['x'][1] + 1.0, y0, y1, Z_BOT, BB['z'][0] - 0.1), clip_in) for y0, y1 in ((20.0, 28.0), (-28.0, -20.0))]
    dboss, dcuts = b611.drain_parts()
    dboss2, dcuts2 = drain2_parts()
    D_KEEP = prism(BOX_OUT.buffer(b611.UP_OUT - 0.01, join_style=1, resolution=16), Z_BOT - 10, b61.Z_C + 1)
    screed = floor_screed2(clip_in, D_KEEP)
    sboss = [I(at(cyl(10.0, Z_BOT - 5, CAP_BOSS_TOP, 64), x, y), clip_in) for x, y in CAP_SCREWS.values()]
    body = U([shell, up, spig, tube, screed, I(dboss, clip_in), I(dboss2, clip_in)] + sup + sboss)
    groove = prism(ring2d(b61.WALL_C.buffer(b611.GRV_W611 / 2, join_style=1, resolution=16), b61.WALL_C.buffer(-b611.GRV_W611 / 2, join_style=1, resolution=16)),
                   b61.Z_C - b61.GRV_D, b61.Z_C + 1)
    seam_grv = at(D(cyl(2 * (so + 1.0), b611.ZG_SEAM[0], b611.ZG_SEAM[1], 512), cyl(2 * (so - b611.SEAM_G), b611.ZG_SEAM[0] - 1, b611.ZG_SEAM[1] + 1, 512)), b611.SEAM_CX, 0)
    r_ = b61.OUTLET['r']
    S = b611.SOCK
    cuts = [groove, seam_grv,
            at(cyl(2 * r_, Z_BOT - 10, S['bore_z'] + 0.01, NF), CH_X, 0),
            at(hull_of((circle_pts(2 * r_, NF), Z_BOT + b61.OUTLET['chamfer']), (circle_pts(2 * (r_ + b61.OUTLET['chamfer'] + 1.0), NF), Z_BOT - 1.0)), CH_X, 0),
            at(cyl(2 * S['r'], S['pilot'][0], S['top'] + 1, NF), CH_X, 0),
            at(cyl(2 * S['pocket'][2], S['pocket'][0], S['pocket'][1], NF), CH_X, 0),
            at(cyl(2 * S['groove'][2], S['groove'][0], S['groove'][1], NF), CH_X, 0),
            at(hull_of((circle_pts(2 * S['r'], NF), S['top'] - 0.6), (circle_pts(2 * (S['r'] + 0.7), NF), S['top'] + 0.01)), CH_X, 0)]
    cuts += dcuts + dcuts2
    c = OR_3x1['csk_d']
    for x, y in CAP_SCREWS.values():
        cuts += [at(cyl(3.4, Z_BOT - 1, CAP_BOSS_TOP + 1, 32), x, y),
                 at(cyl(CAP_CB_D, Z_BOT - 1, CAP_SEAT_Z, 64), x, y),
                 at(hull_of((circle_pts(c, 48), CAP_SEAT_Z - 0.01), (circle_pts(3.4, 48), CAP_SEAT_Z + (c - 3.4) / 2)), x, y)]
    if not with_panel:
        return D(body, cuts), None
    # ---------------- control panel: dry pocket behind the band ----------------
    pp = panel_parts()
    cav_plan, sol_plan = pocket_plans()
    pc = POCKET
    pocket_sol = I(I(prism(sol_plan, Z_BOT - 1.0, -60.0), roof_halfspace(pc['roof_top'])), pod_solid(0.0, z_hi=Z_S - b611.SEAM))
    cav = I(I(prism(cav_plan, Z_BOT + T_CAP, -60.0), roof_halfspace(pc['roof_top'] - pc['roof_t'])), band_inner_solid(BAND_WALL))
    cav = U([cav] + [I(e, roof_halfspace(pc['roof_top'] - pc['roof_t'])) for e in pp['cav_extra']])
    fcx, fr = pod_circle(T_CAP + 0.5, Z_BOT + T_CAP + 0.6)
    keep = U([pod_solid(T_CAP + 0.5), prism(Point(fcx, 0).buffer(fr - 0.3, resolution=128), Z_BOT + T_CAP - 0.01, Z_BOT + T_CAP + 0.8)])
    cav = I(cav, keep)                                       # >= 2.5 mm skin on the walls and the bottom fillet; flat floor stays at -102
    # speaker cup ring on the dry floor + grille through the flat bottom
    sx, sy = SPK['x'], SPK['y']
    cup = at(D(cyl(SPK['cup_id'] + 2 * SPK['cup_t'], Z_BOT + T_CAP - 0.5, Z_BOT + T_CAP + SPK['cup_h'], 96),
               U([cyl(SPK['cup_id'], Z_BOT, Z_BOT + T_CAP + SPK['cup_h'] + 1, 96),
                  box(-1.5, 1.5, -20, 0, Z_BOT + T_CAP + 2.0, Z_BOT + T_CAP + SPK['cup_h'] + 1)])), sx, sy)   # wire notch
    grille = []
    for hx, hy in [(0.0, 0.0)] + [polar(SPK['grille_r'], 30.0 + 60.0 * k) for k in range(6)]:
        grille += [at(cyl(SPK['hole'], Z_BOT - 1, Z_BOT + T_CAP + 0.5, 24), sx + hx, sy + hy),
                   at(hull_of((circle_pts(SPK['hole'] + 1.0, 24), Z_BOT - 0.01), (circle_pts(SPK['hole'], 24), Z_BOT + 0.5)), sx + hx, sy + hy)]
    body = U([body, pocket_sol] + [I(I(b, pod_solid(0.0, z_hi=Z_S - b611.SEAM)), roof_halfspace(pc['roof_top'])) for b in pp['bosses']])
    body = D(body, [D(cav, pp['bosses'])])
    body = U([body, I(cup, clip_in)])
    body = D(body, cuts + pp['cuts'] + grille + [I(I(e, roof_halfspace(pc['roof_top'] - pc['roof_t'])), keep) for e in pp['cav_extra']])
    body = I(body, band_solid())
    return body, pp


# =====================================================================================
# 4. FLANGE: tunnel raised (strain relief), dowel pivot, press-fit pins, tie pocket, bell mouth; ring window teardrop
# =====================================================================================
def tunnel_rz63(n_arc=24):
    """(r, z) of the cable centreline through the flange, from outside the rim inward/down (R 15 bend as v6.2, exit raised)"""
    zh = TUN63['zh']
    zc = zh - TUN63['R']
    pts = [(96.0, zh), (TUN63['r_s'], zh)]
    for k in range(1, n_arc + 1):
        ph = math.radians(90.0 * k / n_arc)
        pts.append((TUN63['r_s'] - TUN63['R'] * math.sin(ph), zc + TUN63['R'] * math.cos(ph)))
    pts.append((TUN63['r_v'], 52.0))
    return pts, zh, zc


def tunnel_solid63(radius, z_lo=None, z_hi=None, r_out_max=None):
    with patched(b62, tunnel_rz=tunnel_rz63):
        return b62.tunnel_solid(radius, z_lo, z_hi, r_out_max)


def build_flange_low63():
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
    body = U([plate, skirt] + tongues + pins)
    a_lo, a_hi = ARM_ANG - STROKE - 3.0, ARM_ANG + 3.0
    cuts = [prism(OPENING63, FL_Z0 - 1.0, FL_Z1 + 0.02),          # 6.3.0: apex pulled back, full wall round the dowel seat
            D(cyl(2 * v5.LGROOVE_R1, FL_Z0 - 1, FL_Z0 + v5.LGROOVE_D), cyl(2 * v5.LGROOVE_R0, FL_Z0 - 2, FL_Z0 + v5.LGROOVE_D + 1)),
            D(cyl(2 * b611.SH_GRV[1], FL_Z0 - 1, FL_Z0 + b611.SH_GRV[2], 2 * SEG), cyl(2 * b611.SH_GRV[0], FL_Z0 - 2, FL_Z0 + b611.SH_GRV[2] + 1, 2 * SEG)),
            D(cyl(2 * RING_GRV['r1'], FL_Z0 - 1, RING_GRV['z1'], 2 * SEG), cyl(2 * RING_GRV['r0'], FL_Z0 - 2, RING_GRV['z1'] + 1, 2 * SEG)),
            D(cyl(2 * RING_GRV['uc'][0], RING_GRV['uc'][1], RING_GRV['z1'], 2 * SEG), cyl(2 * RING_GRV['r1'] - 0.02, RING_GRV['uc'][1] - 1, RING_GRV['z1'] + 1, 2 * SEG)),
            prism(sector_ring(a_lo, a_hi, RING_SLOT['r0'], RING_SLOT['r1']), RING_SLOT['z0'], FL_Z1 + 0.02),
            prism(affinity.rotate(sbox(6.0, -0.8, 50.0, 0.8), DRAIN_ANG, origin=(0, 0)), FL_Z0 - 1.0, FL_Z1 + 0.02),
            tunnel_solid63(TUN['bore'] / 2, z_hi=FL_Z1 + 0.01, r_out_max=FL_R62 + 2),
            cyl(DOWEL['d'], FL_Z1 - DOWEL['depth'], FL_Z1 + 1.0, 48)]                      # dowel hole (pivot)
    for a in WOOD_ANG62:
        x, y = polar(WOOD_R62, a)
        cuts.append(at(U([cyl(v5.WOOD_D, FL_Z0 - 1, FL_Z1 + 1, 32), cyl(v5.WOOD_CB_D, FL_Z0 - 1, FL_Z0 + v5.WOOD_CB_H, 48)]), x, y))
    for a in JOIN['ang']:                                    # press-fit pin holes (blind, 1.1 mm skin to the rim-seal face)
        x, y = polar(JOIN['r'], a)
        cuts.append(at(U([cyl(FPIN['hole_d'], FL_Z1 - FPIN['hole_depth'], FL_Z1 + 1, 32),
                          hull_of((circle_pts(FPIN['hole_d'], 32), FL_Z1 - 0.4), (circle_pts(FPIN['hole_d'] + 0.8, 32), FL_Z1 + 0.01))]), x, y))
    ex, ey = polar(72.0, 180.0)
    cuts.append(face_region(affinity.scale(text_poly(VER, 5.0, ex, ey, 90.0), -1, 1, origin=(ex, ey)), FL_Z0, False))
    return D(body, cuts)


def build_flange_up63(cav):
    plate = revolve([(0, FL_Z1), (FL_R62, FL_Z1), (FL_R62, FL_Z1_62 - 0.6), (FL_R62 - 0.6, FL_Z1_62), (0, FL_Z1_62)], 2 * SEG)
    if plate.volume < 0:
        plate.invert()
    hc = v6.HOLE_C
    pins = []
    for aj in JOIN['ang']:                                   # press-fit pins replace the 3 ST2.9 join screws
        x, y = polar(JOIN['r'], aj)
        pins.append(at(U([cyl(FPIN['d'], FL_Z1 - FPIN['h'] + FPIN['ch'], FL_Z1 + 0.01, 32),
                          hull_of((circle_pts(FPIN['d'] - 2 * FPIN['ch'], 32), FL_Z1 - FPIN['h']), (circle_pts(FPIN['d'], 32), FL_Z1 - FPIN['h'] + FPIN['ch']))]), x, y))
    body = U([plate] + pins)
    cuts = [cav, prism(pocket2d(), FL_Z1 - 1.0, POCKET_Z1),
            at(D(cyl(2 * v5.FL_GSK_R + v5.GRV_W, FL_Z1_62 - v5.GRV_D, FL_Z1_62 + 1), cyl(2 * v5.FL_GSK_R - v5.GRV_W, FL_Z1_62 - v5.GRV_D - 1, FL_Z1_62 + 2)), *hc),
            tunnel_solid63(TUN['bore'] / 2, z_lo=FL_Z1 - 0.01, r_out_max=FL_R62 + 2)]
    # cable-tie window (floor = lower plate top face) + rounded exit
    tp = TIE_POCKET
    a0 = math.degrees(tp['half_w'] / ((tp['r0'] + tp['r1']) / 2))
    cuts.append(prism(sector_ring(CABLE_ANG - a0, CABLE_ANG + a0, tp['r0'], tp['r1']).buffer(0.8, join_style=1).buffer(-0.8, join_style=1), FL_Z1 - 0.01, FL_Z1_62 + 1.0))
    bell = hull_of((circle_pts(TUN['bore'], 48), 0.0), (circle_pts(BELL['d1'], 48), FL_R62 + 0.5 - BELL['r0']))
    bell.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))    # axis +z -> -y
    bell.apply_translation([0.0, -BELL['r0'], TUN63['zh']])
    cuts.append(rotz(bell, CABLE_ANG - 270.0))                                                  # built at -y = 270 deg
    for x, y in v6.COLLAR_PINS:
        cuts.append(at(cyl(3.4, FL_Z1_62 - 3.0, FL_Z1_62 + 1.0, 32), x, y))
    for aw in WOOD_ANG62:
        x, y = polar(WOOD_R62, aw)
        cuts.append(at(cyl(v5.WOOD_D, FL_Z1 - 1, FL_Z1_62 + 1, 32), x, y))
    return D(body, cuts)


def build_ring63():
    """v6.2 ring with the window as a 45 deg teardrop cut flat at RING_WIN_TOP (prints on its edge without support)"""
    r = RING
    zb0, zb1 = RING_BARB['z']
    prof = [(r['ri'], r['z0'] + 1.2), (r['ri'] + 1.2, r['z0']), (r['ro'] - 1.2, r['z0']), (r['ro'], r['z0'] + 1.2),
            (r['ro'], r['z1'] - 0.4), (r['ro'] - 0.4, r['z1']), (r['tongue'][1], r['z1']),
            (r['tongue'][1], zb0 - 0.3), (RING_BARB['r1'], zb0), (RING_BARB['r1'], zb1 - 0.05), (r['tongue'][1], r['tongue_top'] - 0.1),
            (r['tongue'][1] - 0.2, r['tongue_top']), (r['tongue'][0] + 0.3, r['tongue_top']), (r['tongue'][0], r['tongue_top'] - 0.3)]
    m = revolve(prof, 2 * SEG)
    if m.volume < 0:
        m.invert()
    px, py = polar(PEG['r'], ARM_ANG)
    peg = at(U([cyl(PEG['d'], r['tongue_top'] - 0.3, BLADE_Z[1] - 0.3, 32),
                hull_of((circle_pts(PEG['d'] - 0.8, 32), BLADE_Z[1] - 0.3), (circle_pts(PEG['d'], 32), BLADE_Z[1] - 0.7))]), px, py)
    m = U([m, peg])
    # teardrop window in the (tangential, z) plane, extruded radially through the ring wall
    rw = r['win_d'] / 2
    circ = Point(0, 0).buffer(rw, resolution=64)
    tip = Polygon([(-rw * math.cos(math.radians(45)), rw * math.sin(math.radians(45))), (rw * math.cos(math.radians(45)), rw * math.sin(math.radians(45))),
                   (0.0, rw / math.sin(math.radians(45)))])
    tear = circ.union(tip).intersection(sbox(-rw - 1, -rw - 1, rw + 1, RING_WIN_TOP))
    tp_ = np.array(tear.exterior.coords)[:-1]
    w = hull_of((tp_, 0.0), (tp_, 12.0))                                          # (t, z, radial); the teardrop is convex
    w.apply_transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))   # (t, z, r) -> (r, t, z)
    w.apply_translation([(r['ri'] + r['ro']) / 2 - 6.0, 0, r['win_z']])
    if w.volume < 0:
        w.invert()
    ch_ = hull_of((np.array(tear.exterior.coords)[:-1], 0.0), (np.array(tear.buffer(1.2, join_style=2).exterior.coords)[:-1], 1.21))
    ch_.apply_transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))
    ch_.apply_translation([r['ro'] - 1.2, 0, r['win_z']])
    return D(m, [rotz(w, WIN_ANG), rotz(ch_, WIN_ANG)])


def build_blade63():
    """v6.2 blade geometry, printed in ONE colour (green): the arm runs hidden inside the flange"""
    m, g, o = b62.build_blade62()
    return m


def build_grommet63():
    with patched(b62, tunnel_rz=tunnel_rz63):
        return b62.build_grommet62()


def latch_print_matrix(m):
    """linguetta_sicura on its back (T-foot face down, nub up), as the print_v62 package found"""
    a = math.radians(LATCH_A)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    R = trimesh.geometry.align_vectors(u, [0, 0, 1])
    p = m.copy(); p.apply_transform(R)
    ext = p.bounds[1] - p.bounds[0]
    if ext[1] > ext[0]:
        R = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]) @ R
    p = m.copy(); p.apply_transform(R)
    return trimesh.transformations.translation_matrix([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]]) @ R


# =====================================================================================
# BOUGHT PARTS v6.3
# =====================================================================================
def pt_screw(x, y, z_seat, length, up=True):
    """thread-forming pan-head screw placeholder (head under z_seat, shank upward)"""
    return at(U([cyl(PT['d'], z_seat - 0.01, z_seat + length, 24), cyl(PT['head_d'], z_seat - PT['head_h'], z_seat, 32)]), x, y)


def cable_paths63():
    pts, zh, zc = tunnel_rz63(36)
    x_clip = -(FL_R62 + 160.0)                                  # user's clips along the shelf underside (drawn 160 mm)
    sup = [(0.0, x_clip, zh), (0.0, -96.5, zh)] + rz_to_xyz(pts)[1:] + [(0.0, -72.0, 50.6), (0.0, -69.2, 49.0)]
    a, b_ = CONN62
    unit = [(0.0, -69.2, a[2]), (0.0, -69.2, -2.0), (-1.0, -67.0, -18.0), (-3.0, -65.0, -34.0), (-3.0, -63.0, -45.0), (-3.0, -58.0, -48.0)]
    return sup, unit


def panel_bought(pp):
    """switch (bezel, thread, nut, body), light pipes + O-rings + LEDs, speaker + membrane, harness"""
    B = {}
    P, n, _ = pp['frames']['btn']
    r = REC
    B['switch_12mm_ip67'] = U([axial_cyl(P, n, 14.0, r['face'], r['floor'] + 0.3, 64),            # bezel + front gasket (0.3 squeeze into the floor)
                               axial_cyl(P, n, 10.0, r['face'] - 0.3, r['face'] + 0.01, 48),
                               axial_cyl(P, n, 12.2, r['floor'], r['floor'] + r['wall'] + 2.5, 48),
                               axial_cyl(P, n, 18.4, r['floor'] + r['wall'], r['floor'] + r['wall'] + 2.5, 6),
                               axial_cyl(P, n, 13.0, r['floor'] + r['wall'] + 2.5, r['floor'] + r['wall'] + 14.0, 48)])
    lp, orr, leds = [], [], []
    for k in ('led1', 'led2'):
        P, n, _ = pp['frames'][k]
        lp.append(U([axial_cyl(P, n, 5.0, 0.0, LED['len'], 32), axial_cyl(P, n, 8.0, LED['len'], LED['len'] + 1.0, 32)]))
        t = v6.torus(2.5 + 0.5, 0.5, 0.0, n=32)
        Rm = trimesh.geometry.align_vectors([0, 0, 1], -n)
        t.apply_transform(Rm)
        t.apply_translation(P - n * (LED['len'] - LED['cb_depth'] + 0.5 - 0.15))
        orr.append(t)
        leds.append(axial_cyl(P, n, 3.2, LED['len'] + 1.0, LED['len'] + 6.0, 24))
    B['lightpipes_5mm'] = U(lp)
    B['oring_5x1_lightpipe'] = U(orr)
    B['leds_3mm'] = U(leds)
    sx, sy = SPK['x'], SPK['y']
    zf = Z_BOT + T_CAP
    B['membrane_acoustic_ip67'] = at(cyl(15.0, zf, zf + 0.25, 48), sx, sy)
    B['speaker_20mm'] = at(U([cyl(SPK['d'] - 0.4, zf + 1.25, zf + 1.25 + SPK['h'], 48), cyl(12.0, zf + 0.25, zf + 1.26, 48)]), sx, sy)
    Pb = pp['frames']['btn'][0] - pp['frames']['btn'][1] * (r['floor'] + r['wall'] + 14.0)
    B['harness_jst'] = tube_path([tuple(Pb), (Pb[0] - 1.0, Pb[1] - 4.0, -94.0), (11.0, 24.0, -94.0), (19.0, 15.0, -90.0), (20.0, 12.0, -82.0)], 1.6, 12)
    return B


def bought63(pp):
    B, sc = b611.bought611()
    for k in ('cable_12v', 'connector_ip67', 'oring_tt_8x1.5', 'keys_3x3x18'):
        B.pop(k, None)
    sup, unit = cable_paths63()
    B['cable_12v_supply'] = tube_path(sup, CABLE_D / 2, 16)
    B['cable_12v_unit'] = tube_path(unit, CABLE_D / 2, 16)
    a, b_ = CONN62
    B['connector_m8_ip67'] = U([at(cyl(12.0, a[2], b_[2], 32), a[0], a[1]), at(cyl(13.0, (a[2] + b_[2]) / 2 - 4, (a[2] + b_[2]) / 2 + 4, 6), a[0], a[1])])
    vx, vy = VENT62['x'], VENT62['y']
    B['vent_m12_eptfe'] = U([at(cyl(15.0, Z_R - 0.01, Z_R + 6.0, 6), vx, vy), at(cyl(14.0, Z_R + 5.99, Z_R + 11.0, 32), vx, vy),
                             at(cyl(11.8, Z_R - ROOF_T - 4.0, Z_R + 0.01, 32), vx, vy), at(cyl(17.0, Z_R - ROOF_T - 4.0, Z_R - ROOF_T - 0.01, 6), vx, vy)])
    B['oring_3x1'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, Z_R - ROOF_T + 0.45, x=x, y=y, n=48) for x, y in P_SCREWS[1:]])
    B['oring_3x1_cap'] = U([v6.torus(OR_3x1['id'] / 2 + 0.55, OR_3x1['cs'] / 2, CAP_SEAT_Z + 0.45, x=x, y=y, n=48) for x, y in CAP_SCREWS.values()])
    # cable tie cinched round the cable in the window (loop round the cable + head beside it)
    rt = (TIE_POCKET['r0'] + TIE_POCKET['r1']) / 2 - 0.3
    zc = TUN63['zh'] - TUN63['R']
    zt = zc + math.sqrt(TUN63['R'] ** 2 - (TUN63['r_s'] - rt) ** 2)
    tang = np.array([0.0, -(zt - zc), TUN63['r_s'] - rt]); tang /= np.linalg.norm(tang)        # cable direction at 270 deg (r -> -y)
    loop = v6.torus(CABLE_D / 2 + 0.6, 0.6, 0.0, n=32)
    head = box(CABLE_D / 2 + 0.6, CABLE_D / 2 + 4.1, -1.3, 1.3, -2.0, 2.0)
    tie = U([loop, head])
    ex = np.array([1.0, 0, 0]); ey = np.cross(tang, ex)
    Tt = np.eye(4); Tt[:3, 0], Tt[:3, 1], Tt[:3, 2], Tt[:3, 3] = ex, ey, tang, [0.0, -rt, zt]   # local z = cable direction, head towards +x
    tie.apply_transform(Tt)
    B['cable_tie'] = tie
    B['dowel_4x6'] = cyl(DOWEL['d'], FL_Z1 - DOWEL['depth'] + 0.01, FL_Z1 - DOWEL['depth'] + DOWEL['len'], 32)
    B.update(panel_bought(pp))
    for k in ('m3x12_tower_top', 'm3x10_tower_box', 'wood_5x25', 'inserts_bowl', 'inserts_box', 'm3x10_chute', 'm3x12_shell_tabs'):
        sc.pop(k, None)
    zs = [EAR_Z0, Z_R - ROOF_T, Z_R - ROOF_T]
    sc['m3x40_stack'] = U([screw_m3_up(x, y, z, SCREW_LEN) for (x, y), z in zip(P_SCREWS, zs)])
    sc['pt_k30x12_cap'] = U([pt_screw(x, y, CAP_SEAT_Z, PT['len_cap']) for x, y in CAP_SCREWS.values()])
    sc['pt_k30x10_chute'] = U([pt_screw(x, y, -b61.CH_FL_T, PT['len_chute']) for x, y in b61.CH_EARS])
    sc['pt_k30x12_shell_tabs'] = U([pt_screw(x, y, -TAB_T, PT['len_tab']) for x, y in b61.TAB_INS])
    sc['wood_5x35'] = U([at(U([cyl(5.0, FL_Z0 - 0.01 + v5.WOOD_CB_H, FL_Z1_62 + 20.0, 24), cyl(9.5, FL_Z0 - 0.5, FL_Z0 + v5.WOOD_CB_H, 32)]), *polar(WOOD_R62, a))
                         for a in WOOD_ANG62])
    sc['inserts_bowl'] = U([at(cyl(4.0, 0.2, 5.9, 24), x, y) for x, y in P_SCREWS])
    sc['inserts_box'] = U([at(cyl(4.0, CAGE_Z0 + 0.2, CAGE_Z0 + 5.9, 24), x, y) for x, y in b61.SERVO_HOLES_W])
    return B, sc


# =====================================================================================
# BUILD / EXPORT
# =====================================================================================
def build_all():
    P, COLOUR, EXTRA = {}, {}, {}
    P611, COL611, EX611 = b611.build_all()                   # v6.1.1 parts in memory (sets the chute ears, collar pins)
    EXTRA['P611'], EXTRA['EX611'] = P611, EX611
    F = EX611['F']
    P['chiocciola_v63'] = build_bowl63(F)
    P['colonna_v63'] = build_column63()
    P['scatola_v63'] = build_box63()
    P['fondello_v63'], EXTRA['PANEL'] = build_cap63()
    cav = funnel62()
    EXTRA['FUNNEL'] = cav
    P['flangia_piano_v63'] = build_flange_low63()
    P['flangia_alta_v63'] = build_flange_up63(cav)
    P['saracinesca_v63'] = build_blade63()
    P['anello_saracinesca_v63'] = build_ring63()
    P['passacavo_v63'] = build_grommet63()
    P['linguetta_sicura_v63'] = b61.R5['linguetta_sicura'].copy()          # geometry unchanged, print file corrected
    col = {'saracinesca_v63': 'green', 'anello_saracinesca_v63': 'orange', 'passacavo_v63': 'yellow', 'linguetta_sicura_v63': 'orange'}
    for k, m in P.items():
        COLOUR[k] = [(col.get(k) or 'black', m)]
    return P, COLOUR, EXTRA


FLIP = {'chiocciola_v63': False, 'colonna_v63': False, 'scatola_v63': True, 'fondello_v63': False, 'flangia_piano_v63': True,
        'flangia_alta_v63': True, 'saracinesca_v63': False, 'anello_saracinesca_v63': False, 'passacavo_v63': False,
        'linguetta_sicura_v63': None}
RHO = {k: (TPU if k.startswith('passacavo') else PETG) for k in FLIP}


def print_matrix(m, name):
    if name == 'linguetta_sicura_v63':
        return latch_print_matrix(m)
    T = np.eye(4)
    if FLIP.get(name):
        T = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    p = m.copy(); p.apply_transform(T)
    return trimesh.transformations.translation_matrix([-p.centroid[0], -p.centroid[1], -p.bounds[0, 2]]) @ T


def export_part(name, m, bodies):
    m = v6.clean(m)
    m.export(staged(OUT + f'{name}.stl')); m.export(staged(OUT + f'{name}.3mf'))
    wt = bool(trimesh.load(current(OUT + f'{name}.stl')).is_watertight)
    T = print_matrix(m, name)
    pm = m.copy(); pm.apply_transform(T)
    scn = trimesh.Scene()
    for c, b in bodies:
        pb = v6.clean(b).copy(); pb.apply_transform(T)
        if len(bodies) > 1:
            pb.export(staged(OUT + f'{name}_print_{c}.stl'))
        scn.add_geometry(pb, geom_name=f'{name}_{c}', node_name=f'{name}_{c}')
    scn.export(staged(OUT + f'{name}_print.3mf'))
    pm.export(staged(OUT + f'{name}_print.stl'))
    return wt, pm


if __name__ == '__main__':
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
    P, COLOUR, EXTRA = build_all()
    print('\n--- v6.3 parts ---')
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
        commit_staged()
        sys.exit(0)
    exec(open(dt.HERE + 'build_v63_checks.py').read())
    import publish_v63                    # copy the deliverables from build/ into the repository folders
    publish_v63.main()
