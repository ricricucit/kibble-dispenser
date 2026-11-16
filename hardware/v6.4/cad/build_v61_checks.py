# executed by build_v61.py (exec) in its namespace: context, checks, load case, grams, section/exterior render,
# v61.json, v61_viewer.json, assembled-position STLs in v61_asm/
import time
from scipy.spatial import cKDTree
t_start = time.time()
print('\n--- context ---')
SHELF_T = 30.0
SHELF = D(box(-150, 150, -110, 110, FL_Z1, FL_Z1 + SHELF_T), [at(cyl(v5.SHELF_HOLE_D, FL_Z1 - 1, FL_Z1 + SHELF_T + 1), *v6.HOLE_C),
                                                              at(cyl(10.0, FL_Z1 - 1, FL_Z1 + SHELF_T + 1, 32), *CABLE_XY)])
GSK_PIANO = v5.build_flange_gasket() if hasattr(v5, 'build_flange_gasket') else trimesh.load(OUT + 'guarnizione_piano_v5.stl')
GSK_PIANO.apply_translation([0, 0, FL_Z1 - v5.FL_Z1])
COLLAR = v6.build_collar(EXTRA['FL_CAV'])
SHAFT, HUB = v6.build_shaft(), v6.build_hub()
LATCH = R5['linguetta_sicura']
BOUGHT, SCREWS = bought61()
TTS = EXTRA['tts']
LIPS = {k: P[k] for k in ('labbro_uscita_v61', 'labbro_uscita_v61_b', 'labbro_finestra_v61', 'labbro_finestra_v61_b')}
disc0, disc180 = P['disco_v61'], rotz(P['disco_v61'], 180)
ALL = {'flangia_piano_v61': P['flangia_piano_v61'], 'colletto_v6': COLLAR, 'guarnizione_piano_v5': GSK_PIANO, 'passacavo_v61': P['passacavo_v61'],
       'chiocciola_v61': P['chiocciola_v61'], 'scivolo_v61': P['scivolo_v61'], 'linguetta_sicura': LATCH,
       'guarnizione_baionetta_v61': P['guarnizione_baionetta_v61'], 'piastra_gate_v61': P['piastra_gate_v61'],
       'piastra_finestra_v61': P['piastra_finestra_v61'], 'disco_v61@0': disc0, 'disco_v61@180': disc180,
       'colonna_v61': P['colonna_v61'], 'albero_v6@0': SHAFT, 'albero_v6@180': rotz(SHAFT, 180), 'mozzo_v6@0': HUB, 'mozzo_v6@180': rotz(HUB, 180),
       'scatola_v61': P['scatola_v61'], 'guscio_v61': P['guscio_v61'], 'pulsante_v61': P['pulsante_v61'], 'fondello_v61': P['fondello_v61'],
       'guarnizione_fondello_v61': P['guarnizione_fondello_v61'], 'nottolino_A': TTS[0], 'nottolino_B': TTS[1], 'nottolino_C': TTS[2], 'shelf': SHELF}
ALL.update(LIPS)
ALL.update(BOUGHT)
ALL.update(SCREWS)
NEW = [k for k in ALL if k not in BOUGHT and k not in SCREWS and k not in ('shelf', 'guarnizione_piano_v5', 'linguetta_sicura', 'colletto_v6')]
_soft = [('flangia_piano_v61', 'guarnizione_baionetta_v61'), ('guarnizione_piano_v5', 'shelf'), ('guarnizione_fondello_v61', 'scatola_v61'),
         ('oring_shaft_9x2', 'colonna_v61'), ('oring_face_24x2', 'colonna_v61'), ('oring_face_24x2', 'scatola_v61'), ('oring_shaft_9x2', 'albero_v6@0'),
         ('passacavo_v61', 'flangia_piano_v61'), ('cable_12v', 'passacavo_v61'), ('oring_tt_8x1.5', 'nottolino_C'), ('oring_tt_8x1.5', 'fondello_v61')]
for lk in LIPS:
    _soft += [(lk, 'disco_v61@0'), (lk, 'disco_v61@180'), (lk, 'piastra_gate_v61' if 'uscita' in lk else 'piastra_finestra_v61')]
SOFT = {frozenset(p) for p in _soft}
_skip = [('disco_v61@0', 'disco_v61@180'), ('albero_v6@0', 'albero_v6@180'), ('mozzo_v6@0', 'mozzo_v6@180'), ('disco_v61@0', 'albero_v6@180'),
         ('disco_v61@180', 'albero_v6@0'), ('mozzo_v6@0', 'albero_v6@180'), ('mozzo_v6@180', 'albero_v6@0'), ('disco_v61@0', 'mozzo_v6@180'),
         ('disco_v61@180', 'mozzo_v6@0'), ('mozzo_v6@180', 'servo'), ('mozzo_v6@180', 'm3x8_hub'), ('albero_v6@180', 'oring_shaft_9x2'),
         ('shelf', 'wood_5x25'), ('inserts_bowl', 'm3x12_tower_top'), ('inserts_box', 'm3x10_tower_box'), ('inserts_bowl', 'm3x10_chute'),
         ('inserts_bowl', 'm3x12_shell_tabs'), ('inserts_box', 'm3x8_servo'), ('servo', 'm3x8_hub'), ('servo', 'm3x8_servo'),
         ('scatola_v61', 'gland_m12'), ('scatola_v61', 'vent_m12_eptfe'), ('cable_12v', 'gland_m12'), ('cable_12v', 'connector_ip67'),
         ('cable_12v', 'shelf')]
SKIP = {frozenset(p) for p in _skip}


def bb_overlap(a, b, pad=0.05):
    return bool(np.all(a.bounds[0] <= b.bounds[1] + pad) and np.all(b.bounds[0] <= a.bounds[1] + pad))


print('\n--- interference (mm3) ---')
inter, soft = {}, {}
names = list(ALL)
for i, a in enumerate(names):
    for b_ in names[i + 1:]:
        key = frozenset((a, b_))
        if key in SKIP or (a not in NEW and b_ not in NEW and not (a in BOUGHT or b_ in BOUGHT or a in SCREWS or b_ in SCREWS)):
            continue
        if not bb_overlap(ALL[a], ALL[b_]):
            v = 0.0
        else:
            v = round(vol(I(ALL[a], ALL[b_])), 4)
        (soft if key in SOFT else inter)[f'{a}|{b_}'] = v
        if key not in SOFT and v > 1e-3:
            print(f'  HARD {a:26s}|{b_:26s} {v:.4f}')
HARD_MAX = max(inter.values())
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3; soft:', {k: v for k, v in soft.items() if v > 0})

# ---------------- passage ----------------
print('\n--- passage ---')


def hsec_inscribed(cav, z):
    s = cav.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return None
    p2, _ = s.to_2D()
    return round(2 * max(shapely.maximum_inscribed_circle(q, 0.2).length for q in p2.polygons_full), 1)


cav_fl, out_fl, cav_m, out_m = EXTRA['F']
CAV_FUN = U([cav_fl, cav_m])
CH_BORE = at(cyl(2 * RI, Z_CH_END, ZB + 0.05, 128), CH_X, 0)
PASS = {'shelf_hole_d': v5.SHELF_HOLE_D, 'collar_bore_top_d': round(v5.NECK_OD - 2 * v5.NECK_WALL, 1),
        'window_opening_inscribed': round(2 * shapely.maximum_inscribed_circle(WIN_T, 0.1).length, 1),
        'pocket_inscribed': round(2 * shapely.maximum_inscribed_circle(bd.P_TOP, 0.1).length, 1),
        'gate_outlet_inscribed': round(2 * shapely.maximum_inscribed_circle(OUT_B, 0.1).length, 1),
        'funnel_horizontal': [(round(float(z), 1), hsec_inscribed(CAV_FUN, z)) for z in np.linspace(Z_FL - 0.3, ZB + 0.3, 8)],
        'chute_tube_d': 2 * RI, 'chute_end_to_cap_outlet_gap_mm': round(Z_CH_END - OUTLET['top'], 2), 'cap_outlet_bore_d': 2 * OUTLET['r'],
        'outlet_opening_d_with_chamfer': 2 * (OUTLET['r'] + OUTLET['chamfer'])}
PASS['min_flare_to_opening'] = min([v for _, v in PASS['funnel_horizontal'] if v] + [PASS['chute_tube_d'], PASS['cap_outlet_bore_d']])
PASS['note'] = 'gate outlet 36.8 / window 35.7 / pocket 28 belong to the v4b dosing core upstream: kibble < 28 mm (owner max 25)'
print(json.dumps(PASS))
SLOPES = {'funnel_morph_min_deg': round(bd.floor_slope_min(cav_m, ZB + 0.2, Z_FL - 0.05), 1),
          'flare': '45 deg outward only (ceiling side), as v4b/v6', 'tube_deg': 90.0}
print('slopes:', SLOPES)

# ---------------- bayonet: lug/hook overlap at lock + removal sweep from the LOCKED pose ----------------
print('\n--- bayonet ---')
LUG_SPANS = [(a - w / 2, a + w / 2) for a, w in zip(bd.LUG_ANG, bd.LUG_W)]


def ang_overlap(s1, s2):
    best = 0.0
    for k in (-360, 0, 360):
        best = max(best, min(s1[1], s2[1] + k) - max(s1[0], s2[0] + k))
    return round(max(0.0, best), 1)


BAY_OVL = {'locked_lug_hook_overlap_deg': [ang_overlap(l, h) for l, h in zip(LUG_SPANS, HOOKS61)],
           'locked_lug_FLAT_on_hook_deg (bearing)': [ang_overlap((l[0], l[1] - bd.LUG_RAMP_DEG), h) for l, h in zip(LUG_SPANS, HOOKS61)],
           'v6_lug_flat_on_hook_deg (18 deg ramp)': [ang_overlap((l[0], l[1] - 18.0), (h[0] - 30, h[1] - 30)) for l, h in zip(LUG_SPANS, v5.HOOKS)],
           'lug_ramp_deg': bd.LUG_RAMP_DEG,
           'insertion_lug_hook_overlap_deg': [max(ang_overlap((l[0] - bd.LOCK_ROT, l[1] - bd.LOCK_ROT), h) for h in HOOKS61) for l in LUG_SPANS],
           'v6_drawn_pose_lug_hook_overlap_deg': [max(ang_overlap(l, h) for h in v5.HOOKS) for l in LUG_SPANS]}
FIXED = U([P['flangia_piano_v61'], COLLAR, GSK_PIANO, SHELF, P['passacavo_v61']])
ua = np.radians(bd.LATCH_ANG)
latch_pressed = LATCH.copy(); latch_pressed.apply_translation([-1.6 * math.cos(ua), -1.6 * math.sin(ua), 0])
btn_pressed = P['pulsante_v61'].copy(); btn_pressed.apply_translation([-1.5 * math.cos(ua), -1.5 * math.sin(ua), 0])
MOVING = I(U([P['chiocciola_v61'], latch_pressed, P['piastra_finestra_v61'], LIPS['labbro_finestra_v61'], LIPS['labbro_finestra_v61_b'],
              disc0, P['piastra_gate_v61'], P['guscio_v61'], btn_pressed]), above(40.0))


def unlock_dz(a):                                     # first 12 deg of unlocking run on the lug flats, then the 18 deg ramp drops 1.5
    return 0.0 if a <= bd.LOCK_ROT - bd.LUG_RAMP_DEG else -bd.LIFT * (a - (bd.LOCK_ROT - bd.LUG_RAMP_DEG)) / bd.LUG_RAMP_DEG


poses = [(-a, unlock_dz(a)) for a in np.linspace(0, bd.LOCK_ROT, 11)] + [(-bd.LOCK_ROT, -bd.LIFT - dz) for dz in (2, 5, 10, 20, 40, 80)]
SWEEP = []
for ang, dz in poses:
    m = rotz(MOVING, ang); m.apply_translation([0, 0, dz])
    SWEEP.append((round(float(ang), 1), round(float(dz), 2), round(vol(I(m, FIXED)), 3)))
BAY_MAX = max(v for _, _, v in SWEEP)
LATCH_LOCK = round(vol(I(LATCH, P['flangia_piano_v61'])), 4)
ins = rotz(U([P['chiocciola_v61'], LATCH, P['guscio_v61']]), -bd.LOCK_ROT); ins.apply_translation([0, 0, -bd.LIFT])
BAY_INS = round(vol(I(I(ins, above(40.0)), FIXED)), 4)
print('overlap', BAY_OVL, '\nsweep', SWEEP, 'latch locked vs flange', LATCH_LOCK, 'insertion', BAY_INS)

# ---------------- disc retention, gaps, sweeper ribs, airlock ----------------
win_top = P['piastra_finestra_v61'].bounds[1, 2]
pin_tip = I(P['flangia_piano_v61'], D(cyl(2 * (v6.PIN_R + 4), 0, 60), cyl(2 * (v6.PIN_R - 4), -1, 61))).bounds[0, 2]
RET = {'disc_top_to_window_plate': round(P['piastra_finestra_v61'].bounds[0, 2] - DISC_Z1, 2),
       'disc_bottom_to_gate_plate': round(DISC_Z0 - P['piastra_gate_v61'].bounds[1, 2], 2),
       'window_plate_to_flange_pins': round(pin_tip - win_top, 2), 'hex_engagement_nominal': dt.HEX_LEN}
RET['max_disc_lift'] = round(RET['disc_top_to_window_plate'] + RET['window_plate_to_flange_pins'], 2)
RET['hex_engagement_min'] = round(dt.HEX_LEN - RET['max_disc_lift'], 2)
RIBS = {'count': len(EXTRA['ribs2d'].geoms) if hasattr(EXTRA['ribs2d'], 'geoms') else 1, 'height': RIB_H, 'width': RIB_W,
        'skew_from_radial_deg': RIB_SKEW, 'clearance_to_gate_plate_mm': round(GAP - RIB_H, 2),
        'crossing_angle_with_lips_deg': abs(RIB_SKEW - SKEW_DEG),
        'lip_deflection_when_a_rib_passes_mm': round(RIB_H + LIP_PRE, 2),
        'rib_vs_pocket_edge_min_mm': round(EXTRA['ribs2d'].distance(shapely.unary_union([bd.P_BOT, rotz_poly(bd.P_BOT, 180)])), 2),
        'kibble_min_mm': 4.0, 'gap_mm': GAP}
AIRLOCK = {'margin_deg_min_over_radius': airlock_check(), 'v6_margin_deg': round(180 - bd.ANG_SUM, 1),
           'scissor': f'window/outlet edges rotated {SKEW_DEG} deg about r {SKEW_RM} (pinwheel): they cross the radial pocket edges at '
                      f'{math.degrees(math.atan(math.tan(math.radians(SKEW_DEG)) * 14 / SKEW_RM)):.0f}-{math.degrees(math.atan(math.tan(math.radians(SKEW_DEG)) * 50 / SKEW_RM)):.0f} deg '
                      'instead of 0 (progressive scissor cut, kibble pushed along the edge into the pocket); window/outlet areas -0.3 %',
           'dose_g_per_180deg': EXTRA['portion_g']}
print('retention', RET, '\nribs', RIBS, '\nairlock', AIRLOCK)

# ---------------- clearances ----------------
print('\n--- clearances ---')


def min_dist(a, b, spacing=0.8, refine=300):
    lo, hi = a.bounds[0] - 25.0, a.bounds[1] + 25.0
    bc = I(b, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    if bc is None or len(bc.faces) == 0:
        return [None, 'farther than 25 mm']
    pa, _ = trimesh.sample.sample_surface_even(a, int(max(300, min(40000, a.area / spacing ** 2))), seed=0)
    pb, _ = trimesh.sample.sample_surface_even(bc, int(max(300, min(80000, bc.area / spacing ** 2))), seed=0)
    d, _ = cKDTree(pb).query(pa)
    cand = pa[np.argsort(d)[:refine]]
    best, at_pt = 1e9, None
    for k in range(0, len(cand), 100):
        _, dd, _ = trimesh.proximity.closest_point(bc, cand[k:k + 100])
        j = int(np.argmin(dd))
        if dd[j] < best:
            best, at_pt = float(dd[j]), cand[k + j]
    return [round(best, 2), np.round(at_pt, 1).tolist()]


CLR = {}
CLR['chute_to_box'] = min_dist(P['scivolo_v61'], P['scatola_v61'])
CLR['chute_to_tower'] = min_dist(P['scivolo_v61'], P['colonna_v61'])
CLR['chute_to_shell'] = min_dist(P['scivolo_v61'], P['guscio_v61'])
CLR['box_to_shell'] = min_dist(P['scatola_v61'], P['guscio_v61'])
CLR['gland_to_shell'] = min_dist(BOUGHT['gland_m12'], P['guscio_v61'])
CLR['vent_to_shell'] = min_dist(BOUGHT['vent_m12_eptfe'], P['guscio_v61'])
CLR['cable_to_shell'] = min_dist(BOUGHT['cable_12v'], P['guscio_v61'])
CLR['connector_to_parts'] = min_dist(BOUGHT['connector_ip67'], U([P['guscio_v61'], P['scatola_v61'], P['colonna_v61'], P['chiocciola_v61']]))
CLR['button_plunger_below_flange_skirt_z'] = round(v5.HOOK_Z0 - (BTN_Z + BTN['shaft_d'] / 2), 2)
CLR['shell_inner_to_flange_skirt_radial'] = round(shell_r_at(0.0, 55.0, T_SHELL) - v6.SKIRT_R1, 2)
CLR['shadow_gap_locked_mm'] = round(FL_Z0 - Z_TOP, 2)
CLR['shadow_gap_at_insertion_mm'] = round(FL_Z0 - Z_TOP + bd.LIFT, 2)
fc, fr = pod_circle(0.0, Z_BOT)
CLR['flat_bottom_circle'] = {'centre_x': round(fc, 2), 'r': round(fr, 2)}
oc = Point(CH_X, 0).buffer(OUTLET['r'] + OUTLET['chamfer'], resolution=64)
flat = Point(fc, 0).buffer(fr - 0.01, resolution=128)
CLR['outlet_chamfer_inside_flat_bottom'] = bool(flat.contains(oc))
CLR['dish_to_outlet_chamfer_mm'] = [round(Point(x, y).buffer(TT_DISH_D / 2).distance(oc), 2) for x, y in TT]
CLR['dishes_inside_flat_bottom'] = [bool(flat.contains(Point(x, y).buffer(TT_DISH_D / 2))) for x, y in TT]
print(CLR)
print(f'part A done in {time.time() - t_start:.0f} s')

# ---------------- pod geometry: edge radii, print angles ----------------
def min_curv_radius(pl, step=2.0):
    pl = np.asarray(pl, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pl, axis=0), axis=1))]
    s = np.arange(0, seg[-1], step)
    q = np.c_[np.interp(s, seg, pl[:, 0]), np.interp(s, seg, pl[:, 1])]
    r = []
    for a, b_, c in zip(q[:-2], q[1:-1], q[2:]):
        A = np.linalg.norm(b_ - a); B = np.linalg.norm(c - b_); C = np.linalg.norm(c - a)
        area = abs((b_[0] - a[0]) * (c[1] - a[1]) - (b_[1] - a[1]) * (c[0] - a[0])) / 2
        r.append(A * B * C / (4 * area) if area > 1e-9 else 1e9)
    return round(float(min(r)), 1)


zs0, xa0, xb0 = section_fn(0.0)
yprof = np.c_[(xb0 - xa0) / 2, zs0]
ang_from_vertical = lambda pl: np.degrees(np.arctan2(np.abs(np.diff(pl[:, 0])), np.abs(np.diff(pl[:, 1])) + 1e-9))
pp = np.asarray(XPP); pm_ = np.asarray(XMP)
sel_sh = pp[:-1, 1] >= Z_S
sel_cap = (pp[:-1, 1] < Z_S - SEAM)
POD = {'outer_size_mm': {'diameter_top': 2 * R_TOP, 'height_below_shelf': round(FL_Z1 - Z_BOT, 1), 'flat_bottom_d': round(2 * fr, 1),
                         'v6_height_below_shelf': 168.1},
       'min_edge_radius_mm': {'plus_x_profile': min_curv_radius(XPP[:-1]), 'minus_x_profile': min_curv_radius(XMP[:-1]),
                              'y_profile': min_curv_radius(yprof[yprof[:, 1] < Z_TOP - 1]), 'bottom_edge_design': RC,
                              'rim': 'top rim sits 2.1 under the flange plate (shadow gap), not reachable'},
       'shell_print_seam_down_max_overhang_from_vertical_deg': round(float(ang_from_vertical(pp)[sel_sh].max()), 1),
       'cap_print_bottom_down_band_flatter_than_45_mm': round(max(RC, RC_P) * (1 - math.cos(math.radians(45))), 1),
       'seams': ['shadow gap 2.1 under the flange plate (rotating joint)', f'one horizontal flush seam at z {Z_S} (shell | cap, {SEAM} mm)'],
       'visible_features': 'round outlet Ø49 with 1.5 chamfer in the flat bottom; 3 flush orange thumb-turns in Ø26 dishes; one flush orange latch button in a Ø28 dish; no screws, no cable, no ledges'}
print('pod:', POD)

# ---------------- load case (hand calcs, static, PETG) ----------------
print('\n--- load case ---')
S_XY, S_Z, TAU = 45.0, 20.0, 25.0                    # printed PETG: in-layer tensile, inter-layer tensile, shear (conservative)
units_g = {k: v6.grams_est(P[k], RHO[k])[0] for k in P if k not in ('flangia_piano_v61', 'passacavo_v61')}
W_UNIT = round((sum(units_g.values()) + 55 + 45 + 60) * 9.81 / 1000, 1)     # printed solid g + servo 55 + electronics 45 + screws/inserts/cable 60
F_KIB = 20.0
FV = 250.0 + W_UNIT + F_KIB
FL_LAT = 100.0
Z_LOW = Z_BOT
z_bay = (bd.LUG_Z1 - bd.LUG_T_FLAT / 2)
M_bay = FL_LAT * (z_bay - Z_LOW) / 1000
r_lug = (bd.BOWL_R_OUT + bd.LUG_R1) / 2
ovl = min(BAY_OVL['locked_lug_FLAT_on_hook_deg (bearing)'])
b_arc = math.radians(ovl) * r_lug
F_lug = FV / 3 * 1.5 + M_bay * 1000 / (1.5 * r_lug)  # 1.5 = uneven sharing of 3 lugs + moment share
sig_lug = 6 * F_lug * (r_lug - bd.BOWL_R_OUT) / (b_arc * bd.LUG_T_FLAT ** 2)
a_hook = v6.SKIRT_R0 - r_lug
sig_hook = 6 * F_lug * a_hook / (b_arc * v5.HOOK_T ** 2)
sig_skirt = F_lug / (math.radians(ovl) * (v6.SKIRT_R0 + v6.SKIRT_R1) / 2 * (v6.SKIRT_R1 - v6.SKIRT_R0))
M_sh = FL_LAT * (FL_Z1 - Z_LOW) / 1000
d_far = FL_R + WOOD_R * math.cos(math.radians(45)); d_near = FL_R - WOOD_R * math.cos(math.radians(45))
F_wood = FV / 4 + M_sh * 1000 * d_far / (2 * d_far ** 2 + 2 * d_near ** 2)
tau_head = F_wood / (math.pi * 9.5 * (v6.FL_T - v5.WOOD_CB_H))
# shell -> bowl tabs (load hanging on the shell or on the cap through the spigot ring)
r_w = shell_r_at(0.0, -3.0, T_SHELL)
M_tab_lat = FL_LAT * (-TAB_T / 2 - Z_LOW) / 1000
F_tab = FV / 3 * 1.5 + M_tab_lat * 1000 / (1.5 * TAB_R_INS)
h_web = 0.8 * (r_w - (TAB_R_INS - 6.0))
# T-section at the wall: flange TAB_W x TAB_T on top, 2 webs 3 x h_web below
A1, A2 = TAB_W * TAB_T, 2 * 3.0 * h_web
yc = (A1 * TAB_T / 2 + A2 * (TAB_T + h_web / 2)) / (A1 + A2)
Itab = TAB_W * TAB_T ** 3 / 12 + A1 * (yc - TAB_T / 2) ** 2 + 2 * 3.0 * h_web ** 3 / 12 + A2 * (TAB_T + h_web / 2 - yc) ** 2
M_tab = F_tab * (r_w - TAB_R_INS)
sig_tab = M_tab * max(yc, TAB_T + h_web - yc) / Itab
sig_shell = FV / (2 * math.pi * pod_circle(T_SHELL / 2, Z_S)[1] * T_SHELL)
# cap -> thumb-turns -> posts -> box -> tower -> bowl
xc = fc
xA, xC = TT[0][0], TT[2][0]
F_C = FV * (xc - xA) / (xC - xA)
F_AB = (FV - F_C) / 2
F_lip = 0.3 * WALL_C.length                            # TPU lip line load ~0.3 N/mm (v6 lip, bent 1.2)
F_tt = max(F_C, F_AB) + F_lip / 3
arm_a = 4.0
sig_arm = 6 * F_tt * arm_a / (TT_ARM_W * TT_ARM_T ** 2)
sig_post = F_tt / ((POST_AB['x'][1] - POST_AB['x'][0]) * POST_AB['w'])
sig_brk = 6 * F_tt * 6.0 / (POST_AB['w'] * 6.0 ** 2)
F_twr_screw = (FV + F_lip) / 3
sig_tower = (FV + F_lip) / (math.pi * (v6.COL_R ** 2 - (v6.COL_BORE_D / 2) ** 2))
INSERT_PULL = 600.0
WOOD_PULL = 900.0
LOAD = {'case': f'static 250 N down at the lowest point (flat bottom, z {Z_LOW}) + 100 N sideways there; plus unit weight {W_UNIT} N and {F_KIB} N kibble column on the window plate',
        'materials': {'PETG_in_layer_MPa': S_XY, 'PETG_inter_layer_MPa': S_Z, 'PETG_shear_MPa': TAU, 'M3_insert_pullout_N': INSERT_PULL,
                      'wood_screw_5x25_pullout_softwood_N': WOOD_PULL},
        'bayonet_lugs': {'worst_lug_N': round(F_lug), 'overlap_arc_mm': round(b_arc, 1), 'bending_MPa': round(sig_lug, 1), 'layer_direction': 'across layers',
                         'SF': round(S_Z / sig_lug, 1)},
        'flange_hooks': {'bending_MPa': round(sig_hook, 1), 'layer_direction': 'in layer (flange printed flat)', 'SF': round(S_XY / sig_hook, 1),
                         'skirt_tension_MPa': round(sig_skirt, 1), 'skirt_SF_inter_layer': round(S_Z / sig_skirt, 1)},
        'flange_wood_screws': {'moment_at_shelf_Nm': round(M_sh, 1), 'worst_screw_N': round(F_wood), 'SF_pullout': round(WOOD_PULL / F_wood, 1),
                               'head_pull_through_shear_MPa': round(tau_head, 1), 'SF_head': round(TAU / tau_head, 1)},
        'shell_tabs': {'worst_tab_N': round(F_tab), 'T_section_web_depth_mm': round(h_web, 1), 'bending_MPa': round(sig_tab, 1),
                       'SF': round(S_XY / sig_tab, 1), 'M3x12_into_insert_SF': round(INSERT_PULL / F_tab, 1)},
        'shell_wall_membrane_MPa': round(sig_shell, 2),
        'cap_thumbturns': {'share_N': {'A': round(F_AB), 'B': round(F_AB), 'C': round(F_C)}, 'lip_preload_N': round(F_lip), 'worst_arm_N': round(F_tt),
                           'arm_bending_MPa': round(sig_arm, 1), 'arm_SF': round(S_XY / sig_arm, 1),
                           'post_tension_MPa': round(sig_post, 1), 'post_SF_inter_layer': round(S_Z / sig_post, 1),
                           'bracket_bending_MPa': round(sig_brk, 1), 'bracket_SF': round(S_XY / sig_brk, 1)},
        'box_to_tower_screws_N': round(F_twr_screw), 'box_to_tower_SF': round(INSERT_PULL / F_twr_screw, 1),
        'tower_tension_MPa': round(sig_tower, 1),
        'sideways': 'the cap spigot ring hands the 100 N to the shell (bearing on a 4 mm ring), the shell to the bowl via the tabs (included above)',
        'fox_bite_outlet_rim': {'assumed_N': 250, 'canine_tip_mm': 3.0, 'punching_shear_MPa': round(250 / (math.pi * 3.0 * T_CAP), 1),
                                'SF': round(TAU / (250 / (math.pi * 3.0 * T_CAP)), 1),
                                'note': 'the outlet rim is the only biteable edge (the pod is too big and convex for a jaw); print the cap with 100 % infill within 8 mm of the outlet'}}
print(json.dumps(LOAD, indent=1))

# ---------------- grams and counts ----------------
print('\n--- grams ---')
QTY = {'nottolino_v61': 3}
G61 = {}
for k, m in P.items():
    s, e = v6.grams_est(m, RHO[k])
    q = QTY.get(k, 1)
    G61[k] = {'qty': q, 'volume_cm3': round(abs(m.volume) / 1000 * q, 2), 'grams_solid': round(s * q, 1), 'grams_print_est': round(e * q, 1),
              'material': 'TPU 95A' if RHO[k] == TPU else 'PETG', 'watertight': bool(m.is_watertight)}
for k, m, rho in (('colletto_v6 (reused)', COLLAR, PETG), ('linguetta_sicura (reused)', LATCH, PETG), ('albero_v6 (reused)', SHAFT, PETG),
                  ('mozzo_v6 (reused)', HUB, PETG), ('guarnizione_piano_v5 (reused)', GSK_PIANO, TPU)):
    s, e = v6.grams_est(m, rho)
    G61[k] = {'qty': 1, 'volume_cm3': round(abs(m.volume) / 1000, 2), 'grams_solid': s, 'grams_print_est': e, 'material': 'TPU 95A' if rho == TPU else 'PETG', 'watertight': bool(m.is_watertight)}
G61T = {'grams_print_est': round(sum(v['grams_print_est'] for v in G61.values()), 1),
        'grams_print_est_PETG': round(sum(v['grams_print_est'] for v in G61.values() if v['material'] == 'PETG'), 1),
        'grams_print_est_TPU': round(sum(v['grams_print_est'] for v in G61.values() if v['material'] != 'PETG'), 1),
        'grams_solid': round(sum(v['grams_solid'] for v in G61.values()), 1)}
V6DOC = json.load(open(OUT + 'v6.json'))
G6T = V6DOC['grams']['v6_total']
pod_g = sum(G61[k]['grams_print_est'] for k in ('guscio_v61', 'fondello_v61'))
GRAMS = {'method': V6DOC['grams']['method'], 'v61': G61, 'v61_total': G61T, 'v6_total': G6T,
         'delta_print_est_g': round(G61T['grams_print_est'] - G6T['grams_print_est'], 1),
         'delta_pct': round(100 * (G61T['grams_print_est'] / G6T['grams_print_est'] - 1), 1),
         'where_it_goes': f'shell + cap {pod_g:.0f} g replace box + cover + chute + buttons of v6 ({sum(V6DOC["grams"]["v6"][k]["grams_print_est"] for k in ("scatola_v6", "fondello_v6", "scivolo_v6", "nottolino_v6")):.0f} g); '
                         f'the box inside the pod is a lighter 2.0-wall D box ({G61["scatola_v61"]["grams_print_est"]:.0f} g)'}
print('v6.1', G61T, ' v6', G6T)
COUNT = {'v6': V6DOC['count']['v6'],
         'v61': {'printed_PETG_parts': sum(1 for k in G61 if G61[k]['material'] == 'PETG'),
                 'printed_PETG_pieces': sum(G61[k]['qty'] for k in G61 if G61[k]['material'] == 'PETG'),
                 'printed_TPU_parts': sum(1 for k in G61 if G61[k]['material'] != 'PETG'),
                 'new_v61_designs': len(P), 'reused_designs': 'colletto_v6, linguetta_sicura, albero_v6, mozzo_v6 (PETG); guarnizione_piano_v5 (TPU)',
                 'screws': 4 + 3 + 3 + 2 + 3 + 4 + 1, 'heat_set_inserts': 8 + 7, 'o_rings': 2 + 1 + 1, 'quarter_turn_thumbturns': 3, 'push_buttons': 1,
                 'note': '4 wood + 3 M3x12 tower-bowl + 3 M3x10 tower-box + 2 M3x10 chute + 3 M3x12 shell tabs + 4 M3x8 servo + 1 M3x8 hub; '
                         'cap: 3 flush thumb-turns, 0 screws; O-rings: 2 shaft 9x2 + face 24x2 + thumb-turn C 8x1.5'}}
COUNT['v61']['printed_pieces'] = COUNT['v61']['printed_PETG_pieces'] + COUNT['v61']['printed_TPU_parts']
print('counts', COUNT['v61'])

# ---------------- assembled-position files ----------------
def save(name, m):
    p = ASM + name + '.stl'
    m.export(p)
    return p


FILES = {}
for k, bodies in COLOUR.items():
    if len(bodies) == 1:
        FILES[k] = {bodies[0][0]: OUT + k + '.stl'}
    else:
        FILES[k] = {c: save(f'{k}_{c}', b) for c, b in bodies}
FILES['nottolini'] = {'orange': save('nottolino_v61_x3', U(TTS))}
FILES['colletto_v6'] = {'green': save('colletto_v6', COLLAR)}
FILES['linguetta_sicura'] = {'orange': save('linguetta_sicura', LATCH)}
FILES['albero_v6'] = {'black': save('albero_v6', SHAFT)}
FILES['mozzo_v6'] = {'black': save('mozzo_v6', HUB)}
FILES['guarnizione_piano_v5'] = {'yellow': save('guarnizione_piano_v5_at_v61', GSK_PIANO)}
FILES['labbri'] = {'yellow': save('labbri_v61_x4', U(list(LIPS.values())))}
for k, m in list(BOUGHT.items()) + list(SCREWS.items()):
    FILES[k] = {'bought': save('bought_' + k.replace('.', '_'), m)}

# ---------------- render: sections + exterior ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ELEC = U([BOUGHT[k] for k in ('board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF')])
DRAW = [('shelf (wood, 30 drawn)', SHELF, '#E8D9B5', '#8A6D3B', '///'),
        ('electronics (bought)', ELEC, '#DDDDDD', '#777777', '...'),
        ('gland M12 / ePTFE vent M12 / cable + IP67 connector', U([BOUGHT['gland_m12'], BOUGHT['vent_m12_eptfe'], BOUGHT['cable_12v'], BOUGHT['connector_ip67']]), '#BBBBBB', '#555555', 'xx'),
        ('servo (bought)', BOUGHT['servo'], '#8FA0D0', '#23305f', None),
        ('guscio / fondello (black, pod)', U([P['guscio_v61'], P['fondello_v61']]), '#2a2b2e', 'k', None),
        ('flangia / colonna / scatola (black)', U([P['flangia_piano_v61'], P['colonna_v61'], P['scatola_v61']]), '#4a4a4a', 'k', None),
        ('chiocciola_v61 (black)', P['chiocciola_v61'], '#606060', 'k', None),
        ('colletto / scivolo (green)', U([COLLAR, P['scivolo_v61']]), '#2E9D4F', 'k', None),
        ('plates v61', U([P['piastra_gate_v61'], P['piastra_finestra_v61']]), '#8A8A8A', 'k', None),
        ('disco / nottolini / latch + push button (orange)', U([disc0, U(TTS), LATCH, P['pulsante_v61']]), '#F07A1A', '#7A3A00', None),
        ('albero / mozzo', U([SHAFT, HUB]), '#9A9A9A', 'k', None),
        ('TPU + O-rings (yellow)', U([GSK_PIANO, P['guarnizione_baionetta_v61'], U(list(LIPS.values())), P['guarnizione_fondello_v61'], P['passacavo_v61'],
                                     BOUGHT['oring_shaft_9x2'], BOUGHT['oring_face_24x2'], BOUGHT['oring_tt_8x1.5']]), '#F2C81E', '#7A6A00', None),
        ('screws / inserts', U(list(SCREWS.values())), '#A8ADB3', '#555555', None)]


def draw(ax, origin, normal, T, title, xlim, ylim, xl, yl):
    for nm, m, fc_, ec, hatch in DRAW:
        sct = m.section(plane_origin=origin, plane_normal=normal)
        if sct is None:
            continue
        p2, _ = sct.to_2D(to_2D=T)
        for poly in p2.polygons_full:
            ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=fc_, ec=ec, lw=0.4, hatch=hatch,
                               alpha=0.95 if hatch is None else 0.6, zorder=3 if hatch is None else 1))
            for h in poly.interiors:
                ax.add_patch(MPoly(np.array(h.coords), closed=True, fc='white', ec=ec, lw=0.4, zorder=4 if hatch is None else 2))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title, fontsize=10)


def shade(ax, parts, elev, azim, title):
    L = np.array([0.4, -0.6, 0.7]); L /= np.linalg.norm(L)
    tris, fcs = [], []
    for m, col in parts:                              # one collection -> global depth sort
        mm = m.simplify_quadric_decimation(face_count=min(len(m.faces), 16000)) if len(m.faces) > 16000 else m
        n = mm.face_normals
        base = np.array(matplotlib.colors.to_rgb(col))
        k = 0.30 + 0.70 * np.clip(n @ L, 0, 1)
        tris.append(mm.triangles)
        fcs.append(np.clip(base[None, :] * k[:, None] + 0.10, 0, 1))
    pc = Poly3DCollection(np.vstack(tris), facecolors=np.vstack(fcs), edgecolors='none', linewidths=0)
    ax.add_collection3d(pc)
    ax.set_xlim(-110, 110); ax.set_ylim(-110, 110); ax.set_zlim(-120, 100)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, fontsize=10)


Txz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
Tyz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
fig = plt.figure(figsize=(34, 13), facecolor='white')
ax1 = fig.add_subplot(1, 4, 1); ax2 = fig.add_subplot(1, 4, 2)
ax3 = fig.add_subplot(1, 4, 3, projection='3d'); ax4 = fig.add_subplot(1, 4, 4, projection='3d')
draw(ax1, [0, 0, 0], [0, 1, 0], Txz, f'{VER} section Y=0 (XZ): pod shell + cap, vertical chute to the round outlet, dosing core, tower, box, thumb-turn C',
     (-110, 110), (-115, 105), 'X [mm]', 'Z [mm]')
ax1.text(-108, 98, f'passage >= {PASS["min_flare_to_opening"]} mm gate->opening; funnel min {SLOPES["funnel_morph_min_deg"]} deg; hard interference max {HARD_MAX:.3f} mm3; '
         f'bayonet sweep max {BAY_MAX} mm3', fontsize=8)
draw(ax2, [0, 0, 0], [1, 0, 0], Tyz, 'Section X=0 (YZ): bayonet + rim lip seal, tower, servo, box (M12 gland -Y, cable rising inside the shell), cap D-lip',
     (-110, 110), (-115, 105), 'Y [mm]', 'Z [mm]')
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
ax2.legend(handles, [d[0] for d in DRAW], loc='upper right', fontsize=7)
EXT = [(P['flangia_piano_v61'], '#2a2b2e'), (P['guscio_v61'], '#2a2b2e'), (P['fondello_v61'], '#2a2b2e'), (U(TTS), '#f07a1a'), (P['pulsante_v61'], '#f07a1a')]
shade(ax3, EXT, 8, -60, 'exterior: side (latch push-button on the +Y flank)')
shade(ax4, EXT, -55, -120, 'exterior: from below (outlet, 3 flush thumb-turns, one seam)')
plt.tight_layout()
plt.savefig(OUT + 'check_v61.png', dpi=72)
plt.close(fig)
print('check_v61.png written')

# ---------------- v61.json ----------------
LIPT = lips_torque(EXTRA['lip_len'], EXTRA['flap_len'])
RIMT = rim_lip_force()
HEX = {
    'flangia_piano_v61': 'PETG black: round plate r 82 (4 mm), 4 wood screws at r 75.5 hidden under the shell rim, skirt + 3 hooks in the LOCKED frame (v6 -30 deg), 3 hold-down pins (120/190/320, 0.4 shorter), Ø10 cable hole with TPU grommet at -20 deg (new)',
    'chiocciola_v61': 'PETG black: v6 bowl core; gate seat -0.4 / window step +0.4 (1.2 gaps); rim groove 3.0 x 2.2 for the lip seal; funnel from the skewed outlet turned DOWN onto the vertical chute (morph to z -4, min 56 deg); inserts 3 tower + 2 chute + 3 shell tabs (new)',
    'scivolo_v61': 'PETG green: morph z 0..-4 + vertical Ø44 tube (2.0 wall) at x -41 down to z -73, drip-edge chamfer 1 mm above the cap outlet; 2 ears with gussets, M3x10 from below (new)',
    'piastra_gate_v61': 'PETG black + green: v4b gate at z 27.8..30.8, outlet edges skewed 15 deg (scissor), lip grooves along them, crumb grooves removed (new)',
    'piastra_finestra_v61': 'PETG black + green: v4b window plate at z 49.2..52.2, window edges skewed 15 deg, lip grooves along them (new)',
    'disco_v61': 'PETG orange + black label: disco_v6 + 6 sweeper ribs 1.6 x 0.6 on the underside lands (skewed -30 deg), label v6.1 / SELF-CLEAN (new)',
    'colonna_v61': 'PETG black: colonna_v6 with the bottom lobes at 90/235/330 (215 -> 235: 5 mm clear of the chute) (new)',
    'scatola_v61': 'PETG black: sealed box inside the pod (x -15.25..40, y +-41, z -30..-72, 2.0 walls, flat roof), v6 plateau/boss/face-O-ring seat, integrated servo cradle, slotted guides for the 70x50 board, M12 gland pad (-Y), M12 vent hole in the roof, 3 thumb-turn posts with detent bumps, 3.0 mm rim face for the cap lip (new)',
    'guscio_v61': 'PETG black: pod shell z -72..64, 2.0 wall, circle top r 82 (2.1 shadow gap under the flange), -X flank vertical, +X flank curving into the cap; 3 gusseted tabs under the bowl base (M3x12); flush latch push-button boss in a Ø28 dish (new)',
    'pulsante_v61': 'PETG orange: flush latch push-button (Ø14 face 3 mm deep in a dish, Ø7 plunger to the linguetta_sicura, collar keeps it in) (new)',
    'fondello_v61': 'PETG black: pod cap z -72.6..-104, flat bottom Ø107.5 on the bed, R15 edges, round outlet Ø46 + 1.5 chamfer, D-upstand with lip groove under the box rim, spigot ring into the shell, 3 thumb-turn bosses + dishes, wet-ring drain slots into the outlet, breadboard supports (new)',
    'nottolino_v61': 'PETG orange x3: flush quarter-turn thumb-turn (grip ridge flush with the flat bottom in a Ø26 dish), arm under the box post, captive keyway, detent bump, O-ring groove (new)'}
TPUD = {'guarnizione_baionetta_v61': f'rim LIP seal: foot + riser in the 3.0 x 2.2 groove, 0.5 flap rising outward at 42 deg, bent 0.45 by the flange at lock (pressure from outside energises it); extra twist torque {RIMT["v61_lip"]["extra_twist_torque_Nm"]} N m vs ~{RIMT["v6_solid_ring"]["extra_twist_torque_Nm"]} N m for the v6 solid ring (new)',
        'labbro_uscita_v61 / _b, labbro_finestra_v61 / _b': f'comb-slit plate lips: anchor 3.15 x 1.0 pressed in the groove, 0.8 flap leaning 40 deg, 0.15 preload on the disc, slits 0.7 every 5 mm stopping 1 mm above the anchor; 4 lips {LIPT["nominal_0.15"]["torque_4_lips_Nm"]} N m nominal (new)',
        'guarnizione_fondello_v61': 'cap <-> box: v6 TPU lip seal on the D outline of the box rim (new)',
        'passacavo_v61': 'cable grommet in the flange plate (Ø10.4 / Ø5 for a Ø6 cable, lip under the plate) (new)',
        'guarnizione_piano_v5': 'flange <-> shelf ring (reused)'}
HARDWARE = [
    {'qty': 4, 'item': 'wood screw 5x25 pan head (5x20 for an 18 mm shelf)', 'use': 'flange -> shelf, from below, hidden by the shell rim once the unit is on'},
    {'qty': 3, 'item': 'M3x12 DIN912 A2', 'use': 'tower top lobes -> bowl inserts (factory)'},
    {'qty': 3, 'item': 'M3x10 DIN912 A2', 'use': 'tower bottom lobes -> box plateau blind inserts (factory)'},
    {'qty': 2, 'item': 'M3x10 DIN912 A2', 'use': 'chute ears -> bowl nose inserts, from below (factory)'},
    {'qty': 3, 'item': 'M3x12 DIN912 A2', 'use': 'shell tabs -> bowl base inserts, from below (factory)'},
    {'qty': 4, 'item': 'M3x8 DIN912 A2 + washer', 'use': 'servo -> cradle inserts (factory)'},
    {'qty': 1, 'item': 'M3x8 DIN912 A2', 'use': 'hub -> servo spline (factory)'},
    {'qty': 15, 'item': 'M3 heat-set insert RX-M3x5.7', 'use': '3 tower + 2 chute + 3 shell tabs in the bowl, 3 plateau + 4 servo in the box'},
    {'qty': 2, 'item': 'O-ring NBR70 9x2', 'use': 'shaft (tower module, greased for life at the factory)'},
    {'qty': 1, 'item': 'O-ring NBR70 24x2', 'use': 'tower <-> box face seal (factory)'},
    {'qty': 1, 'item': 'O-ring NBR70 8x1.5', 'use': 'thumb-turn C (the only one inside the dry D); A/B sit in the drained ring outside the seal'},
    {'qty': 1, 'item': 'M12x1.5 cable gland IP68 (cable 4-7 mm) + locknut', 'use': 'box -Y wall, inside the pod'},
    {'qty': 1, 'item': 'M12x1.5 screw-in ePTFE membrane vent IP68 + locknut (e.g. GORE PolyVent / Amphenol LTW VENT-PS1 class)', 'use': 'box roof, pointing up under the bowl (the highest, most sheltered point of the dry volume): pressure + humidity balance, replaces the silica bag'},
    {'qty': 1, 'item': 'inline IP67 2-pin connector (e.g. M12 A-coded or a screw-lock DC pair) + 12 V cable Ø6', 'use': 'under the bowl inside the pod; cable rises inside the shell and leaves through the flange grommet into a Ø10 hole in the shelf'},
    {'qty': 1, 'item': 'food-grade silicone grease NSF H1', 'use': 'FACTORY ONLY: shaft O-rings, face O-ring, thumb-turn O-ring; the user never greases anything'},
    {'qty': 1, 'item': '70 x 50 perfboard (ESP32 board on female headers, 2 regulators, 1000 uF, JST/screw terminals)', 'use': 'replaces the 165 mm breadboard of the bench prototype (cannot fit a pod); slides up into slots, parts face the shell'}]
ASSEMBLY = [
    f'shelf: hole saw Ø{v5.SHELF_HOLE_D:.0f} at x +27 (as v6) + Ø10 cable hole at r {CABLE_R} / {CABLE_ANG} deg (template = the flange)',
    'flange: guarnizione_piano_v5 + colletto_v6 + passacavo_v61, 4 wood screws from below (they disappear under the shell rim)',
    'FACTORY module 1 (tower): colonna_v61 + albero_v6 with 2 O-rings 9x2 + face O-ring 24x2, greased for life',
    'FACTORY module 2 (box): inserts; servo + mozzo_v6 (set the 25T zero), 70x50 board slid up into its slots, M12 gland, ePTFE vent, connector pigtail; tower module screwed on (3x M3x10)',
    'FACTORY unit: bowl inserts; latch; rim lip seal; tower+box -> bowl (3x M3x12 from below); chute (2x M3x10 from below); shell (3x M3x12 from below, push-button inserted from inside first); dosing core from above (gate, disc, window, 4 comb lips); cap: lip seal, 3 thumb-turns, push up, turn 90 deg each',
    'INSTALL: plug the 12 V connector (inside the pod top, cable from the shelf grommet), lift the pod, lugs into the slots, push up, turn +30 deg until the latch clicks',
    'REMOVE: press the orange push-button (flush, in its dish), turn the pod -30 deg, lower it ~8 cm, unplug the connector through the gap under the flange, take it down as ONE piece',
    'OPEN the electronics (bench, unit upside down or on its side): turn the 3 orange thumb-turns 90 deg with the fingertips, lift the cap off: servo screws, board (slides out downward), gland are reachable'];
IP65 = {'principle': 'outer skin = shell + cap (not sealed, drained); wet zones: bowl, funnel, chute, the pod interior outside the box; dry zone: the box (tower bore below the shaft O-rings + box + cap D region)',
        'openings': ['shadow gap under the flange: the only opening at the top, horizontal, 2.1 mm, under the shelf',
                     'flange <-> bowl rim: labyrinth + NEW low-force TPU lip seal (outside pressure presses it shut)',
                     'shaft: disc labyrinth cap + well drain + 2 O-rings 9x2 (factory greased)',
                     'tower <-> box: face O-ring 24x2, screws in blind inserts (as v6)',
                     'box: 2.0 walls, flat roof under the bowl inside the pod; M12 IP68 gland on the -Y wall and M12 IP68 ePTFE vent in the roof, both inside the shell',
                     'box <-> cap: TPU lip seal on the 3.0 mm box rim face; only thumb-turn C goes through the dry D (O-ring)',
                     'pod drainage: water entering at the shadow gap runs down the shell to the cap ring outside the D and out through 2 slots into the outlet bore',
                     'chute: vertical, closed tube; ends 1 mm above the cap outlet with a drip edge; outlet faces straight down in the flat bottom; a snout reaches only the empty pocket of the disc (rotary airlock)']}
ZERO = {'a_lubrication': 'tower + shaft + 2 O-rings 9x2 + face O-ring = factory module greased for life (NSF H1); two O-rings kept: the upper is the wet seal, the lower a backup; one O-ring would not shorten anything (stack unchanged) and halves the margin',
        'b_self_cleaning_disc': RIBS, 'b_top_ribs': 'not added: the disc top is under the kibble column; crumbs on it ride into the pocket anyway; ribs there would scrape the window plate',
        'b_gaps_mm': {'disc_to_gate': RET['disc_bottom_to_gate_plate'], 'disc_to_window': RET['disc_top_to_window_plate'], 'v6': 0.8},
        'b_crumb_grooves': 'removed from the gate plate (they collected crumbs)',
        'c_anti_jam': AIRLOCK, 'd_breather': 'M12x1.5 ePTFE membrane vent in the box roof, pointing up under the bowl, inside the pod (bought); silica bag removed',
        'e_lips': LIPT, 'e_rim_gasket': RIMT}
DEV = ['assembled pose is now the LOCKED pose: v5/v6 drew the bowl at its insertion angle against hooks at the locked angle, so once locked the window sat 30 deg off the funnel opening and the v6 sweep started from the wrong pose; v6.1 flange hooks are v6 -30 deg',
       'electronics: 70 x 50 perfboard standing beside the servo cradle (parts facing the shell) instead of the 165 mm breadboard of the bench prototype: a wide board forces a can-shaped pod (tried: the half breadboard needed the +X flank >= 69 mm all the way down); same circuit (ESP32 + 2 regulators + capacitor)',
       'the pod is asymmetric (vertical -X flank above the outlet, +X flank curving in): the outlet (>= 46 mm, next to the coaxial servo) needs a flat bottom reaching x -65.5; a symmetric drop would be a can',
       f'cap held by 3 flush thumb-turns (no hinge): 2 in the drained ring (no seal), 1 inside the dry D with an O-ring',
       'chute is a separate green part inside the pod (food-path colour kept, prints without supports); the shell is not the chute wall because the chute must clear the box by 1.75 mm',
       '>= 42 mm passage from the gate outlet to the opening holds (min %.1f); the dosing core upstream (pocket 28 mm) still limits kibble to < 28 mm (owner max 25 mm)' % PASS['min_flare_to_opening'],
       'cap bottom edge R15 printed on the bed: lowest 4.4 mm overhang > 45 deg (bed-only support ring or slight droop)',
       'speaker/meow still without an acoustic opening (sealed box, as v6): an acoustic ePTFE vent or a piezo on the cap is the next step; physical ON/OFF + dispense buttons and LED of the bench prototype are not on the pod yet']
RISKS = ['TPU lip seals (rim lip 0.5, cap lip, comb lips): print test strips; the 0.5 rim flap needs 1 clean perimeter (0.4 nozzle, Arachne)',
         'thumb-turn arms bear on 30 deg lead-in chamfers to pull the cap up 1.2 mm: check the click/feel on a test print',
         'the cable must have a ~15 cm slack loop above the connector for the 30 deg twist and the 8 cm lowering before unplugging',
         'shell print (Ø164 x 136, 2.0 wall, seam edge on the bed) takes ~6 h: check warping of the long thin rim; brim recommended',
         'fox bite on the outlet rim: SF ~%.1f at 250 N with 2.0 walls - 100 %% infill near the outlet' % LOAD['fox_bite_outlet_rim']['SF'],
         'hub M3x8 thread depth in the servo spline and the 25T zero (as v6)',
         'max disc lift %.1f leaves %.1f mm hex engagement (v6: 4.5)' % (RET['max_disc_lift'], RET['hex_engagement_min'])]
OVH_D = {k: OVH[k] for k in OVH}
v61doc = {'version': VER, 'frame': 'Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside; parts drawn in the LOCKED bayonet pose',
          'concept': 'pod: everything under the shelf is one smooth claw-proof skin (shell + flat-bottomed cap, one flush seam, 2.1 shadow gap under the flange); one twist still brings down the whole unit; the box with servo + electronics sits inside and opens from below with 3 flush thumb-turns',
          'parts_printed_PETG': HEX, 'parts_TPU_95A': TPUD, 'count': COUNT, 'hardware': HARDWARE,
          'stack_z': {'shelf_underside': FL_Z1, 'flange_plate': [FL_Z0, FL_Z1], 'shell': [Z_S, Z_TOP], 'cap': [Z_BOT, Z_S - SEAM], 'bowl': [0.0, bd.RIM_Z],
                      'gate_plate': [G0, G1], 'disc': [DISC_Z0, DISC_Z1], 'window_plate': [W0, W1], 'funnel_bottom': ZB, 'chute_end': Z_CH_END,
                      'tower': [Z_R, v6.BUSH_TOP], 'box': [Z_W, Z_R], 'servo_case': [v6.S_TOP - 40.5, v6.S_TOP], 'thumbturn_arm_top': TT_ARM_Z1,
                      'unit_height_below_shelf_mm': round(FL_Z1 - Z_BOT, 1), 'v6_unit_height_below_shelf_mm': 168.1},
          'shelf': {'hole_saw_d': v5.SHELF_HOLE_D, 'hole_centre_xy': list(v6.HOLE_C), 'cable_hole': {'d': 10.0, 'xy': [round(v, 1) for v in CABLE_XY]},
                    'wood_screws_xy': [[round(v, 1) for v in p] for p in WOOD_XY]},
          'pod': POD, 'chute': {'axis_x': CH_X, 'inner_d': 2 * RI, 'wall': T_CH, 'funnel_morph_bottom_z': ZB, 'end_z': Z_CH_END,
                                'cap_outlet': {'bore_d': 2 * OUTLET['r'], 'chamfer': OUTLET['chamfer'], 'top_z': OUTLET['top']}},
          'box': {'outer_xy': [list(BXO[:2]), list(BXO[2:])], 'wall': BX_T, 'roof': ROOF_T, 'breadboard': BB, 'gland': GLAND, 'vent': VENT},
          'thumbturns_xy': TT, 'latch_button': {'angle_deg': LATCH_A, 'z': BTN_Z, **BTN},
          'assembly': ASSEMBLY, 'ip65': IP65, 'zero_maintenance': ZERO, 'load_case': LOAD, 'deviations_from_brief': DEV, 'open_risks': RISKS,
          'checks': {'watertight_built': {k: bool(m.is_watertight) for k, m in P.items()}, 'watertight_exported_stl_reload': EXPORT_WT,
                     'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'soft_designed_overlap_mm3': soft,
                     'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
                     'passage_mm': PASS, 'slopes_deg': SLOPES,
                     'bayonet': {**BAY_OVL, 'removal_sweep_angle_dz_mm3': SWEEP, 'max_mm3': BAY_MAX, 'latch_locked_vs_flange': LATCH_LOCK, 'unit_at_insertion_vs_flange': BAY_INS},
                     'disc_axial_retention': RET, 'sweeper_ribs': RIBS, 'airlock': AIRLOCK, 'clearances_mm': CLR,
                     'print_downfacing_flatter_45_mm2': OVH_D},
          'grams': GRAMS, 'print': PRINT_TXT,
          'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] + [f'{k}_print_{c}.stl' for c, _ in COLOUR[k] if len(COLOUR[k]) > 1] for k in P} |
                   {'assembled_position_copies': 'v61_asm/*.stl', 'check': 'check_v61.png', 'viewer': 'v61_viewer.json'}}
_dflt = lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
json.dump(v61doc, open(OUT + 'v61.json', 'w'), indent=1, default=_dflt)
print('v61.json written')

# ---------------- v61_viewer.json ----------------
C = dict(black='#2a2b2e', orange='#f07a1a', green='#2e9d4f', yellow='#f2c81e', steel='#a8adb3', servo='#23305f', breadboard='#f2f0ea', esp32='#1b1b1b')
DZ = lambda z: [0.0, 0.0, z]
VP = []


def vp(pid, name, key, ck, colour, group, material, qty, bought, explode, rotates=False, opacity=1.0):
    VP.append({'id': pid, 'name': name, 'file': FILES[key][ck], 'color': colour, 'opacity': opacity, 'group': group, 'material': material,
               'qty': qty, 'bought': bought, 'explode': [round(float(v), 1) for v in explode], 'rotates': rotates})


la = math.radians(LATCH_A)
SH = [0.0, -215.0, 20.0]                                # the shell slides away sideways so the inside shows
vp('guarnizione_piano', 'Guarnizione piano (TPU)', 'guarnizione_piano_v5', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(195))
vp('colletto_v6', 'Colletto imbuto', 'colletto_v6', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(180))
vp('flangia_piano_v61', 'Flangia piano (viti nascoste)', 'flangia_piano_v61', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(150))
vp('passacavo_v61', 'Passacavo flangia (TPU)', 'passacavo_v61', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, [10, -4, 168])
vp('viti_legno', 'Viti legno 5x25', 'wood_5x25', 'bought', C['steel'], 'ferramenta', 'acciaio', 4, True, DZ(170))
vp('guarnizione_baionetta_v61', 'Guarnizione a labbro baionetta', 'guarnizione_baionetta_v61', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(128))
vp('piastra_finestra_nero', 'Piastra finestra (nero)', 'piastra_finestra_v61', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(108))
vp('piastra_finestra_verde', 'Piastra finestra (verde)', 'piastra_finestra_v61', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(108))
vp('labbri', 'Labbri a pettine (4)', 'labbri', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 4, False, DZ(94))
vp('disco_v61_arancio', 'Disco autopulente', 'disco_v61', 'orange', C['orange'], 'dosatore', 'PETG arancione', 1, False, DZ(80), True)
vp('disco_v61_nero', 'Disco (etichetta)', 'disco_v61', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(80), True)
vp('piastra_gate_nero', 'Piastra gate (nero)', 'piastra_gate_v61', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(60))
vp('piastra_gate_verde', 'Piastra gate (verde)', 'piastra_gate_v61', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(60))
vp('chiocciola_v61', 'Chiocciola (vasca dosatore)', 'chiocciola_v61', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(30))
vp('linguetta_sicura', 'Linguetta di sicurezza', 'linguetta_sicura', 'orange', C['orange'], 'dosatore', 'PETG arancione', 1, False, [25 * math.cos(la), 25 * math.sin(la), 30])
vp('inserti_vasca', 'Inserti M3 (vasca)', 'inserts_bowl', 'bought', '#b08d57', 'ferramenta', 'ottone', 8, True, DZ(30))
vp('guscio_v61', 'Guscio (pod)', 'guscio_v61', 'black', C['black'], 'struttura', 'PETG nero', 1, False, SH)
vp('pulsante_v61', 'Pulsante sgancio a filo', 'pulsante_v61', 'orange', C['orange'], 'struttura', 'PETG arancione', 1, False,
   [SH[0] + 30 * math.cos(la), SH[1] + 30 * math.sin(la), SH[2]])
vp('viti_guscio', 'Viti M3x12 guscio-vasca', 'm3x12_shell_tabs', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 3, True, [SH[0], SH[1], SH[2] - 18])
vp('scivolo_v61', 'Scivolo verticale (interno)', 'scivolo_v61', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, [-85, 0, -10])
vp('viti_scivolo', 'Viti M3x10 scivolo', 'm3x10_chute', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 2, True, [-85, 0, -25])
vp('viti_torre_vasca', 'Viti M3x12 torre-vasca', 'm3x12_tower_top', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 3, True, DZ(-18))
vp('albero_v6', 'Albero (modulo lubrificato a vita)', 'albero_v6', 'black', C['black'], 'trasmissione', 'PETG nero', 1, False, DZ(-8), True)
vp('oring_albero', 'O-ring albero 9x2 (2)', 'oring_shaft_9x2', 'bought', '#1e1e1e', 'guarnizioni', 'NBR70', 2, True, DZ(-8), True)
vp('colonna_v61', 'Torre (passante)', 'colonna_v61', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-40))
vp('oring_faccia', 'O-ring torre-scatola 24x2', 'oring_face_24x2', 'bought', '#1e1e1e', 'guarnizioni', 'NBR70', 1, True, DZ(-52))
vp('viti_torre_scatola', 'Viti M3x10 torre-scatola', 'm3x10_tower_box', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 3, True, DZ(-28))
vp('mozzo_v6', 'Mozzo (scanalato 25T)', 'mozzo_v6', 'black', C['black'], 'trasmissione', 'PETG nero', 1, False, DZ(-60), True)
vp('vite_mozzo', 'Vite M3x8 mozzo', 'm3x8_hub', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 1, True, DZ(-46), True)
vp('scatola_v61', 'Scatola elettronica (interna)', 'scatola_v61', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-85))
vp('inserti_scatola', 'Inserti M3 (scatola)', 'inserts_box', 'bought', '#b08d57', 'ferramenta', 'ottone', 7, True, DZ(-85))
vp('pressacavo', 'Pressacavo M12 IP68', 'gland_m12', 'bought', '#303030', 'elettronica', 'PA nero', 1, True, [0, -40, -85])
vp('sfiato_eptfe', 'Sfiato ePTFE M12 IP68', 'vent_m12_eptfe', 'bought', '#d0d0d0', 'elettronica', 'acquistato', 1, True, [0, -30, -60])
vp('cavo_12v', 'Cavo 12 V (esce in alto)', 'cable_12v', 'bought', '#151515', 'elettronica', 'acquistato', 1, True, [70, -60, 0])
vp('connettore_ip67', 'Connettore IP67 in linea', 'connector_ip67', 'bought', '#3b3b3b', 'elettronica', 'acquistato', 1, True, [70, -60, 0])
vp('servo', 'Servo standard', 'servo', 'bought', C['servo'], 'trasmissione', 'acquistato', 1, True, DZ(-160))
vp('viti_servo', 'Viti M3x8 servo + rondelle', 'm3x8_servo', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 4, True, DZ(-175))
vp('scheda', 'Scheda millefori 70x50', 'board_70x50', 'bought', '#3d7a3d', 'elettronica', 'acquistato', 1, True, [45, 0, -160])
vp('esp32', 'ESP32-WROVER dev board', 'esp32', 'bought', C['esp32'], 'elettronica', 'acquistato', 1, True, [30, 0, -160])
vp('reg_12v', 'Regolatore Pololu D36V50F6', 'reg_12v_d36v50f6', 'bought', '#2b4a7a', 'elettronica', 'acquistato', 1, True, [30, 0, -160])
vp('reg_5v', 'Regolatore 5 V logica', 'reg_5v_logic', 'bought', '#2b4a7a', 'elettronica', 'acquistato', 1, True, [30, 0, -160])
vp('condensatore', 'Condensatore 1000 µF', 'cap_1000uF', 'bought', '#1a1a2e', 'elettronica', 'acquistato', 1, True, [30, 0, -160])
vp('guarnizione_fondello_v61', 'Guarnizione a labbro fondello', 'guarnizione_fondello_v61', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(-215))
vp('fondello_v61', 'Fondello (fondo del pod, uscita)', 'fondello_v61', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-240))
vp('nottolini_v61', 'Nottolini a filo (3)', 'nottolini', 'orange', C['orange'], 'struttura', 'PETG arancione', 3, False, DZ(-270))
vp('oring_nottolino', 'O-ring nottolino C 8x1.5', 'oring_tt_8x1.5', 'bought', '#1e1e1e', 'guarnizioni', 'NBR70', 1, True, DZ(-270))
path = [[v6.HOLE_C[0], 0, FL_Z1 + SHELF_T], [v6.HOLE_C[0], 0, v6.NECK_Z1], [30, 0, FL_Z0], [30, 0, W1], [30, 0, 40]]
path += [[round(30 * math.cos(math.radians(a)), 1), round(30 * math.sin(math.radians(a)), 1), 40] for a in (45, 90, 135)]
path += [[-30, 0, 40], [-30, 0, G0], [-32, 0, Z_FL], [-37, 0, 10], [CH_X, 0, ZB], [CH_X, 0, -40], [CH_X, 0, Z_CH_END], [CH_X, 0, Z_BOT],
         [CH_X, 0, Z_BOT - 40], [CH_X - 3, 0, Z_BOT - 80]]
viewer = {'title': 'Kibble Dispenser Outdoor v6.1', 'units': 'mm', 'frame': 'Z-up, shaft axis x=y=0', 'rotation_axis_xy': [0, 0],
          'groups': {'struttura': 'Struttura', 'dosatore': 'Dosatore', 'trasmissione': 'Trasmissione', 'elettronica': 'Elettronica',
                     'guarnizioni': 'Guarnizioni TPU', 'ferramenta': 'Ferramenta'},
          'parts': VP,
          'scene': {'shelf_underside_z': FL_Z1, 'shelf_thickness': SHELF_T, 'shelf_hole_xy': list(v6.HOLE_C), 'shelf_hole_d': v5.SHELF_HOLE_D,
                    'outlet_xyz': [CH_X, 0.0, Z_BOT], 'outlet_dir': [0, 0, -1]},
          'kibble_path': [[round(float(v), 2) for v in p] for p in path]}
json.dump(viewer, open(OUT + 'v61_viewer.json', 'w'), indent=1)
missing = [p['file'] for p in VP if not os.path.exists(p['file'])]
print('v61_viewer.json written:', len(VP), 'entries; missing files:', missing)
print(f'checks done in {time.time() - t_start:.0f} s')
