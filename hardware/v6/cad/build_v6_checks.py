# executed by build_v6.py (exec) in its namespace: context solids, checks, section render, v6.json, v6_viewer.json
import os
import time
t_start = time.time()
print('\n--- context solids ---')
R = v5.R
SHELF_T = 30.0
SHELF = D(box(-150, 150, -110, 110, FL_Z1, FL_Z1 + SHELF_T), at(cyl(v5.SHELF_HOLE_D, FL_Z1 - 1, FL_Z1 + SHELF_T + 1), *HOLE_C))
GSK_PIANO = trimesh.load(OUT + 'guarnizione_piano_v5.stl')
GSK_PIANO.apply_translation([0, 0, FL_Z1 - v5.FL_Z1])          # same part (v5 design), shelf 2 mm lower in v6
if not GSK_PIANO.is_watertight:
    GSK_PIANO = v5.build_flange_gasket(); GSK_PIANO.apply_translation([0, 0, FL_Z1 - v5.FL_Z1])
BOUGHT, SCREWS = bought_parts()
LIPS = U([R[k] for k in R if k.startswith('labbro')])
disc0, disc180 = P['disco_v6'], rotz(P['disco_v6'], 180)
shaft0, shaft180 = P['albero_v6'], rotz(P['albero_v6'], 180)
hub0, hub180 = P['mozzo_v6'], rotz(P['mozzo_v6'], 180)
BTN_ALL = U(BTNS)
# optional DN50 pipe (PP-HT OD 50 / ID 46.4) slid over the spigot up to the step, 150 mm shown
PIPE = D(incl_cyl(25.0, S_R + 0.01, S_R + 150.0, 96), incl_cyl(23.2, S_R - 1.0, S_R + 151.0, 96))

ALL = {'flangia_piano_v6': P['flangia_piano_v6'], 'colletto_v6': P['colletto_v6'], 'guarnizione_piano_v5': GSK_PIANO,
       'chiocciola_v6': P['chiocciola_v6'], 'scivolo_v6': P['scivolo_v6'], 'linguetta_sicura': R['linguetta_sicura'],
       'guarnizione_baionetta': R['guarnizione_baionetta'], 'piastra_gate_v4b': R['piastra_gate_v4b'],
       'piastra_finestra_v4b': R['piastra_finestra_v4b'], 'labbri': LIPS, 'disco_v6@0': disc0, 'disco_v6@180': disc180,
       'colonna_v6': P['colonna_v6'], 'albero_v6@0': shaft0, 'albero_v6@180': shaft180, 'mozzo_v6@0': hub0, 'mozzo_v6@180': hub180,
       'scatola_v6': P['scatola_v6'], 'fondello_v6': P['fondello_v6'], 'guarnizione_fondello_v6': P['guarnizione_fondello_v6'],
       'nottolini_v6': BTN_ALL, 'shelf': SHELF}
ALL.update({k: m for k, m in BOUGHT.items()})
ALL.update({k: m for k, m in SCREWS.items()})
NEW = ['flangia_piano_v6', 'colletto_v6', 'chiocciola_v6', 'scivolo_v6', 'disco_v6@0', 'disco_v6@180', 'colonna_v6', 'albero_v6@0',
       'albero_v6@180', 'mozzo_v6@0', 'mozzo_v6@180', 'scatola_v6', 'fondello_v6', 'guarnizione_fondello_v6', 'nottolini_v6']
SOFT = {frozenset(p) for p in [('flangia_piano_v6', 'guarnizione_baionetta'), ('guarnizione_piano_v5', 'shelf'),
                               ('guarnizione_fondello_v6', 'scatola_v6'), ('oring_shaft_9x2', 'colonna_v6'),
                               ('oring_face_24x2', 'colonna_v6'), ('oring_face_24x2', 'scatola_v6'), ('oring_shaft_9x2', 'albero_v6@0')]}
SKIP = {frozenset(p) for p in [('disco_v6@0', 'disco_v6@180'), ('albero_v6@0', 'albero_v6@180'), ('mozzo_v6@0', 'mozzo_v6@180'),
                               ('disco_v6@0', 'albero_v6@180'), ('disco_v6@180', 'albero_v6@0'), ('mozzo_v6@0', 'albero_v6@180'),
                               ('mozzo_v6@180', 'albero_v6@0'), ('disco_v6@0', 'mozzo_v6@180'), ('disco_v6@180', 'mozzo_v6@0'),
                               ('mozzo_v6@180', 'servo'), ('mozzo_v6@180', 'm3x8_hub'), ('albero_v6@180', 'oring_shaft_9x2'),
                               ('shelf', 'wood_5x25'), ('inserts_m3', 'm3x12_tower_top'), ('inserts_m3', 'm3x10_tower_box'),
                               ('inserts_m3', 'm3x10_chute'), ('inserts_m3', 'm3x8_servo'), ('servo', 'm3x8_hub'), ('servo', 'm3x8_servo'),
                               ('scatola_v6', 'gland_m16')]}


def bb_overlap(a, b, pad=0.05):
    return np.all(a.bounds[0] <= b.bounds[1] + pad) and np.all(b.bounds[0] <= a.bounds[1] + pad)


print('\n--- interference (mm3) ---')
inter, soft = {}, {}
names = list(ALL)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        key = frozenset((a, b))
        if key in SKIP or (a not in NEW and b not in NEW and not (a in BOUGHT or b in BOUGHT or a in SCREWS or b in SCREWS)):
            continue
        if (a in SCREWS or a in BOUGHT) and (b in SCREWS or b in BOUGHT) and key not in SOFT:
            if not bb_overlap(ALL[a], ALL[b]):
                continue
        if not bb_overlap(ALL[a], ALL[b]):
            v = 0.0
        else:
            v = round(vol(I(ALL[a], ALL[b])), 4)
        (soft if key in SOFT else inter)[f'{a}|{b}'] = v
        if key not in SOFT and v > 1e-3:
            print(f'  HARD {a:26s}|{b:22s} {v:.4f}')
HARD_MAX = max(inter.values())
print(f'{len(inter)} hard pairs checked, max {HARD_MAX:.4f} mm3; soft (designed compression):', soft)

# ---------------- passage along the kibble path ----------------
print('\n--- passage ---')


def hsec_inscribed(cav, z):
    s = cav.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return None
    p2, _ = s.to_2D()
    return round(2 * max(shapely.maximum_inscribed_circle(q, 0.2).length for q in p2.polygons_full), 1)


def psec_inscribed(cav, s_ax):
    o = axis_pt(s_ax)
    sec = cav.section(plane_origin=o, plane_normal=DIR)
    if sec is None:
        return None
    p2, T = sec.to_2D()
    o2 = trimesh.transform_points([o], np.linalg.inv(T))[0][:2]
    polys = [q for q in p2.polygons_full if q.buffer(1.0).contains(Point(o2))] or list(p2.polygons_full)
    return round(2 * shapely.maximum_inscribed_circle(polys[0], 0.2).length, 1)


PASS = {}
PASS['shelf_hole_d'] = v5.SHELF_HOLE_D
PASS['collar_bore_top_d'] = round(v5.NECK_OD - 2 * v5.NECK_WALL, 1)
PASS['flange_funnel_horizontal'] = [(round(float(z), 1), hsec_inscribed(FL_CAV, z)) for z in np.linspace(NECK_Z1 - 0.5, FL_Z0 + 0.5, 8)]
PASS['window_opening_inscribed'] = round(2 * shapely.maximum_inscribed_circle(bd.WIN_TOP, 0.1).length, 1)
PASS['pocket_inscribed'] = round(2 * shapely.maximum_inscribed_circle(bd.P_TOP, 0.1).length, 1)
PASS['gate_outlet_inscribed'] = round(2 * shapely.maximum_inscribed_circle(bd.OUTLET_BOT, 0.1).length, 1)
PASS['bowl_funnel_horizontal'] = [(round(float(z), 1), hsec_inscribed(CAV_BOWL, z)) for z in np.linspace(Z_FL - 0.3, 0.3, 8)]
CH_CAV = chute_cavity()
PASS['chute_perpendicular'] = [(round(float(s), 1), psec_inscribed(CH_CAV, s)) for s in np.linspace(2.0, S_FLOOR_END - 1.0, 10)]
CHUTE_PASS_MIN = min(v for _, v in PASS['bowl_funnel_horizontal'] + PASS['chute_perpendicular'] if v)
PASS['chute_min_flare_to_outlet'] = CHUTE_PASS_MIN
print(json.dumps(PASS))

# ---------------- slopes ----------------
SLOPES = {'flange_funnel_min_deg': round(bd.floor_slope_min(FL_CAV, FL_Z0 + 0.2, NECK_Z1 - 0.2), 1),
          'bowl_funnel_min_deg': round(bd.floor_slope_min(CAV_BOWL, 0.3, Z_FL - 0.05), 1),
          'chute_tube_floor_deg': TH_DEG,
          'chute_part_min_floor_deg': round(bd.floor_slope_min(I(CH_CAV, D(above(Z_END + 0.5), above(-0.5))), Z_END + 0.6, -0.6), 1)}
print('slopes:', SLOPES)

# ---------------- chute / box clearance (surface sampling + nearest point) ----------------
print('\n--- clearances ---')
BOX_SET = U([P['scatola_v6'], P['fondello_v6'], BTN_ALL])


def min_dist(a, b, spacing=0.6, refine=400):
    """minimum surface distance: KD-tree on even surface samples (b cropped near a), exact refinement on the closest samples"""
    from scipy.spatial import cKDTree
    lo, hi = a.bounds[0] - 25.0, a.bounds[1] + 25.0
    bc = I(b, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    if bc is None or len(bc.faces) == 0:
        return [None, 'farther than 25 mm']
    pa, _ = trimesh.sample.sample_surface_even(a, int(max(200, min(60000, a.area / spacing ** 2))), seed=0)
    pb, _ = trimesh.sample.sample_surface_even(bc, int(max(200, min(120000, bc.area / spacing ** 2))), seed=0)
    if len(pa) == 0 or len(pb) == 0:
        return [None, 'no samples']
    d, _ = cKDTree(pb).query(pa)
    cand = pa[np.argsort(d)[:refine]]
    best, at_pt = 1e9, None
    for k in range(0, len(cand), 100):
        _, dd, _ = trimesh.proximity.closest_point(bc, cand[k:k + 100])
        j = int(np.argmin(dd))
        if dd[j] < best:
            best, at_pt = float(dd[j]), cand[k + j]
    return [round(best, 2), np.round(at_pt, 1).tolist()] if at_pt is not None else [None, 'refinement failed']


nose = I(P['chiocciola_v6'], D(box(-120, -15, -60, 60, -1, 30), cyl(2 * 62.0, -2, 40, 2 * SEG)))
CLR = {}
CLR['chute_part_to_box'] = min_dist(P['scivolo_v6'], BOX_SET)
CLR['bowl_nose_to_box'] = min_dist(nose, BOX_SET, 20000) if len(nose.faces) else None
CLR['dn50_pipe_to_box'] = min_dist(PIPE, BOX_SET)
CLR['chute_part_to_tower'] = min_dist(P['scivolo_v6'], P['colonna_v6'], 30000)
CLR['chute_screws_to_box'] = min_dist(SCREWS['m3x10_chute'], BOX_SET, 5000)
CLR['outlet_floor_lip_x_vs_box_eave_x'] = [round(float(axis_pt(S_FLOOR_END)[0] + R_SP_I * math.sin(TH)), 1), WX[0] - EAVE]
print('clearances (mm, at point):', CLR)

# ---------------- bayonet removal sweep ----------------
print('\n--- bayonet removal sweep ---')
FIXED = U([P['flangia_piano_v6'], P['colletto_v6'], GSK_PIANO, SHELF])
latch_pressed = R['linguetta_sicura'].copy()
ua = np.radians(bd.LATCH_ANG)
latch_pressed.apply_translation([-1.6 * math.cos(ua), -1.6 * math.sin(ua), 0])
MOVING = U([P['chiocciola_v6'], latch_pressed, R['piastra_finestra_v4b'], R['labbro_finestra_1'], R['labbro_finestra_2'], disc0, R['piastra_gate_v4b']])
MOVING = I(MOVING, above(40.0))                        # only the part that can reach the flange (everything else is >= 50 mm below it)
poses = [(-a, -bd.LIFT * a / bd.LOCK_ROT) for a in np.linspace(0, bd.LOCK_ROT, 7)] + [(-bd.LOCK_ROT, -bd.LIFT - dz) for dz in (2, 5, 10, 20, 40, 80)]
SWEEP = []
for ang, dz in poses:
    m = rotz(MOVING, ang); m.apply_translation([0, 0, dz])
    SWEEP.append((round(float(ang), 1), round(float(dz), 2), round(vol(I(m, FIXED)), 3)))
BAY_MAX = max(v for _, _, v in SWEEP)
LATCH_LOCK = round(vol(I(R['linguetta_sicura'], P['flangia_piano_v6'])), 4)
ins = rotz(U([P['chiocciola_v6'], R['linguetta_sicura']]), -bd.LOCK_ROT); ins.apply_translation([0, 0, -bd.LIFT])
BAY_INS = round(vol(I(I(ins, above(40.0)), FIXED)), 4)
print('sweep (angle, dz, mm3):', SWEEP, ' latch locked vs flange', LATCH_LOCK, ' bowl+latch at insertion vs flange', BAY_INS)

# ---------------- coaxiality ----------------


def hole_centre(m, z, rmax=20.0):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    T = np.eye(4); T[2, 3] = -z
    p2, _ = s.to_2D(to_2D=T)
    best = None
    for q in p2.polygons_full:
        for h in q.interiors:
            hp = Polygon(h)
            c = hp.centroid
            if math.hypot(c.x, c.y) < 5 and hp.area < math.pi * rmax ** 2:
                best = (round(c.x, 3), round(c.y, 3), round(2 * math.sqrt(hp.area / math.pi), 2))
    return best


COAX = {'bowl_base_hole@z1.5': hole_centre(P['chiocciola_v6'], 1.5),
        'tower_bushing_bore@z-5': hole_centre(P['colonna_v6'], -5.0),
        'tower_dry_bore@z-20': hole_centre(P['colonna_v6'], -20.0),
        'box_plateau_hole@z-30.5': hole_centre(P['scatola_v6'], Z_R - 0.1),
        'box_hub_cavity@z-40': hole_centre(P['scatola_v6'], -40.0, 15),
        'disc_hex_pocket@z27': hole_centre(disc0, 27.0, 8),
        'hub_spline_socket@z-44': hole_centre(hub0, HUB_Z0 + 2.0, 6),
        'radial_clearances_mm': {'shaft_in_bushing': (dt.BUSH_BORE_D - dt.SHAFT_D) / 2, 'hub_in_cavity': dt.HUB_CAV_R - dt.HUB_D / 2,
                                 'hub_neck_in_tower_bore': (COL_BORE_D - 16.0) / 2, 'hub_neck_in_plateau_hole': PLAT_HOLE_R - 8.0,
                                 'tower_to_box_location': 'self-centring on 3x M3 in Ø3.3 holes: +-0.15'}}
print('coaxiality (x, y, d):', COAX)

# ---------------- disc axial retention ----------------
win_top = R['piastra_finestra_v4b'].bounds[1, 2]
pin_tip = I(P['flangia_piano_v6'], D(cyl(2 * (PIN_R + 4), 0, 60), cyl(2 * (PIN_R - 4), -1, 61))).bounds[0, 2]
RET = {'disc_top_to_window_plate': round(R['piastra_finestra_v4b'].bounds[0, 2] - disc0.bounds[1, 2], 2),
       'window_plate_to_flange_pins': round(pin_tip - win_top, 2),
       'disc_bottom_to_gate_plate': round(bd.DISC_Z0 - R['piastra_gate_v4b'].bounds[1, 2], 2),
       'hex_engagement_nominal': dt.HEX_LEN}
RET['max_disc_lift'] = round(RET['disc_top_to_window_plate'] + RET['window_plate_to_flange_pins'], 2)
RET['hex_engagement_min'] = round(dt.HEX_LEN - RET['max_disc_lift'], 2)
RET['shaft_in_hub_engagement_min'] = round(HUB_TOP - SHAFT_BOT - RET['max_disc_lift'], 2)
RET['torque'] = {'stall_Nm': 2.5, 'shaft_shear_at_groove_MPa': round(16 * 2500 / (math.pi * dt.OR_GROOVE_D ** 3), 1),
                 'note': 'hex AF8 x 5.5 in PETG, unchanged from v4b (the M3x60 only clamped axially; torque always went through the hex)'}
print('disc retention:', RET)

# ---------------- grams ----------------
print('\n--- grams ---')
V6_PRINTED = {k: (P[k], RHO[k], 4 if k == 'nottolino_v6' else 1) for k in P}
for k in ('piastra_gate_v4b', 'piastra_finestra_v4b', 'linguetta_sicura'):
    V6_PRINTED[k] = (R[k], PETG, 1)
V6_PRINTED['guarnizione_baionetta'] = (R['guarnizione_baionetta'], TPU, 1)
V6_PRINTED['labbri (4)'] = (LIPS, TPU, 1)
V6_PRINTED['guarnizione_piano_v5'] = (GSK_PIANO, TPU, 1)
V5_PRINTED = {}
for k in ('flangia_piano_v5', 'scatola_v5', 'fondello_v5'):
    V5_PRINTED[k] = (trimesh.load(OUT + k + '.stl'), PETG, 1)
for k in ('guarnizione_piano_v5', 'guarnizione_scivolo_v5', 'guarnizione_collare_v5', 'guarnizione_fondello_v5'):
    V5_PRINTED[k] = (trimesh.load(OUT + k + '.stl'), TPU, 1)
for k in ('chiocciola_scivolo_v4b', 'piastra_gate_v4b', 'piastra_finestra_v4b', 'disco_v4b', 'linguetta_sicura', 'ghiera_valvola',
          'albero_mozzo', 'passante_culla'):
    V5_PRINTED[k] = (R[k], PETG, 1)
for k in ('valvola_becco', 'guarnizione_baionetta'):
    V5_PRINTED[k] = (R[k], TPU, 1)
V5_PRINTED['labbri (4)'] = (LIPS, TPU, 1)


def gram_table(d):
    t, tot = {}, [0.0, 0.0, 0.0]
    for k, (m, rho, q) in d.items():
        s, e = grams_est(m, rho)
        t[k] = {'qty': q, 'volume_cm3': round(abs(m.volume) / 1000 * q, 2), 'grams_solid': round(float(s) * q, 1),
                'grams_print_est': round(float(e) * q, 1), 'material': 'TPU 95A' if rho == TPU else 'PETG', 'watertight': bool(m.is_watertight)}
        tot[0] += abs(m.volume) / 1000 * q; tot[1] += float(s) * q; tot[2] += float(e) * q
    return t, {'volume_cm3': round(tot[0], 1), 'grams_solid': round(tot[1], 1), 'grams_print_est': round(tot[2], 1),
               'grams_print_est_PETG': round(sum(v['grams_print_est'] for v in t.values() if v['material'] == 'PETG'), 1),
               'grams_print_est_TPU': round(sum(v['grams_print_est'] for v in t.values() if v['material'] != 'PETG'), 1)}


G6, G6T = gram_table(V6_PRINTED)
G5, G5T = gram_table(V5_PRINTED)
print('v6 total', G6T, '\nv5 total', G5T)
COUNT = {'v5': {'printed_PETG_parts': 11, 'printed_TPU_parts': 10, 'printed_pieces': 21,
                'screws': 22, 'heat_set_inserts': 17, 'o_rings': 2, 'note': '4 wood + 1 M3x60 + 3 M3x8 csk + 4 M3x8 servo + 4 M3x14 legs + 6 M3x10 cover'},
         'v6': {'printed_PETG_parts': 14, 'printed_PETG_pieces': 17, 'printed_TPU_parts': 7, 'printed_pieces': 17 + 7,
                'new_v6_designs': 12, 'reused_designs': 'gate, window, latch (PETG); bayonet gasket, 4 lips, shelf gasket (TPU)',
                'screws': 4 + 3 + 3 + 2 + 4 + 1, 'heat_set_inserts': 3 + 2 + 3 + 4, 'o_rings': 3, 'printed_quarter_turn_buttons': 4,
                'note': '4 wood + 3 M3x12 tower-bowl + 3 M3x10 tower-box + 2 M3x10 chute + 4 M3x8 servo + 1 M3x8 hub; cover: 4 printed buttons, 0 screws'}}
print('counts:', COUNT)

# ---------------- assembled-position files for the viewer ----------------
os.makedirs(ASM, exist_ok=True)


def save(name, m):
    p = ASM + name + '.stl'
    m.export(p)
    return p


win_band = bd.WIN_TOP.buffer(bd.RIM_BAND, resolution=32).difference(bd.WIN_TOP)
win_text = text_poly('FOOD IN →', 6, -30, 0).union(text_poly('v4b', 4, -30, -9))
win_black, win_green = split(R['piastra_finestra_v4b'], face_region(win_band.union(win_text), bd.WIN_Z1, True))
out_band = affinity.rotate(bd.OUTLET_TOP.buffer(bd.RIM_BAND, resolution=32).difference(bd.OUTLET_TOP), 180, origin=(0, 0)).intersection(Point(0, 0).buffer(bd.GATE_R - 0.8))
gate_text = text_poly('← OUT', 6, 30, 0).union(text_poly('v4b', 4, 30, -9))
gate_black, gate_green = split(R['piastra_gate_v4b'], face_region(out_band.union(gate_text), bd.GATE_Z1, True))
FILES = {}
for k, bodies in COLOUR.items():
    if len(bodies) == 1 and k != 'nottolino_v6':
        FILES[k] = {bodies[0][0]: OUT + k + '.stl'}
    elif k == 'nottolino_v6':
        FILES[k] = {'orange': save('nottolino_v6_x4', BTN_ALL)}
    else:
        FILES[k] = {c: save(f'{k}_{c}', b) for c, b in bodies}
FILES['piastra_gate_v4b'] = {'black': save('piastra_gate_v4b_black', gate_black), 'green': save('piastra_gate_v4b_green', gate_green)}
FILES['piastra_finestra_v4b'] = {'black': save('piastra_finestra_v4b_black', win_black), 'green': save('piastra_finestra_v4b_green', win_green)}
FILES['linguetta_sicura'] = {'orange': save('linguetta_sicura', R['linguetta_sicura'])}
FILES['guarnizione_baionetta'] = {'yellow': save('guarnizione_baionetta', R['guarnizione_baionetta'])}
FILES['labbri'] = {'yellow': save('labbri_x4', LIPS)}
FILES['guarnizione_piano_v5'] = {'yellow': save('guarnizione_piano_v5_at_v6', GSK_PIANO)}
for k, m in list(BOUGHT.items()) + list(SCREWS.items()):
    FILES[k] = {'bought': save('bought_' + k, m)}
print('assembled-position files in', ASM)

# ---------------- section render ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
DRAW = [('shelf (wood, 30 drawn)', SHELF, '#E8D9B5', '#8A6D3B', '///'),
        ('electronics (bought)', U([BOUGHT['breadboard'], BOUGHT['esp32'], BOUGHT['reg_12v_d36v50f6'], BOUGHT['reg_5v_logic'], BOUGHT['cap_1000uF'], BOUGHT['silica_10g']]), '#DDDDDD', '#777777', '...'),
        ('gland (bought)', BOUGHT['gland_m16'], '#BBBBBB', '#555555', 'xx'),
        ('DN50 pipe (optional, ghost)', PIPE, '#EEEEEE', '#AAAAAA', '\\\\'),
        ('servo (bought)', BOUGHT['servo'], '#8FA0D0', '#23305f', None),
        ('flangia_piano_v6 / colonna_v6 / scatola_v6 (black)', U([P['flangia_piano_v6'], P['colonna_v6'], P['scatola_v6'], P['fondello_v6']]), '#3A3A3A', 'k', None),
        ('chiocciola_v6 (black)', P['chiocciola_v6'], '#555555', 'k', None),
        ('colletto_v6 / scivolo_v6 (green)', U([P['colletto_v6'], P['scivolo_v6']]), '#2E9D4F', 'k', None),
        ('plates v4b', U([R['piastra_gate_v4b'], R['piastra_finestra_v4b']]), '#7A7A7A', 'k', None),
        ('disco_v6 / nottolini / latch (orange)', U([disc0, BTN_ALL, R['linguetta_sicura']]), '#F07A1A', '#7A3A00', None),
        ('albero_v6 / mozzo_v6', U([shaft0, hub0]), '#9A9A9A', 'k', None),
        ('TPU + O-rings (yellow)', U([GSK_PIANO, R['guarnizione_baionetta'], LIPS, P['guarnizione_fondello_v6'], BOUGHT['oring_shaft_9x2'], BOUGHT['oring_face_24x2']]), '#F2C81E', '#7A6A00', None),
        ('screws / inserts', U(list(SCREWS.values())), '#A8ADB3', '#555555', None)]


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


Txz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
Tyz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
fig, axs = plt.subplots(1, 3, figsize=(32, 12), facecolor='white', gridspec_kw={'width_ratios': [1.25, 1.35, 1.0]})
draw(axs[0], [0, 0, 0], [0, 1, 0], Txz, f'{VER} section Y=0 (XZ): shelf, flange+collar, dosing core, outward funnel + 55 deg chute, tower, box, cover',
     (-170, 90), (-125, 115), 'X [mm]', 'Z [mm]')
axs[0].text(-165, 108, f'chute {TH_DEG:.0f} deg, passage min {CHUTE_PASS_MIN} mm, funnel min {SLOPES["bowl_funnel_min_deg"]} deg; chute-box {CLR["chute_part_to_box"][0]} mm; '
            f'hard interference max {HARD_MAX:.3f} mm3; bayonet sweep max {BAY_MAX} mm3', fontsize=8)
draw(axs[1], [0, 0, 0], [1, 0, 0], Tyz, 'Section X=0 (YZ): bayonet, tower (passante + 2 O-rings 9x2), face O-ring 24x2, cradle + servo, breadboard rails, gland',
     (-100, 100), (-125, 115), 'Y [mm]', 'Z [mm]')
Ty = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, BTN_Y[0]], [0, 0, 0, 1]], float)
draw(axs[2], [0, BTN_Y[0], 0], [0, 1, 0], Txz, f'Section Y={BTN_Y[0]:.0f} (XZ): quarter-turn buttons under the cover ears, lip gasket, breadboard',
     (-60, 75), (-110, -20), 'X [mm]', 'Z [mm]')
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
axs[1].legend(handles, [d[0] for d in DRAW], loc='upper right', fontsize=7)
plt.tight_layout()
plt.savefig(OUT + 'check_v6.png', dpi=75)
plt.close(fig)
print('check_v6.png written')

# ---------------- key-access columns (hex key 2.5: needs ~21 mm straight line under/over the screw heads) ----------------
ACCESS = {}
for nm, pts, z0, z1 in (('tower_top_screws_from_below', TWR_INS, Z_R + 0.1, -TOP_LOBE_T - 3.0),
                        ('tower_box_screws_from_above', BOT_INS, COL_FL_Z1 + 3.0, -0.1)):
    col = U([at(cyl(5.0, z0, z1, 24), x, y) for x, y in pts])
    hit = {k: round(vol(I(col, ALL[k])), 2) for k in ('chiocciola_v6', 'colonna_v6', 'scatola_v6', 'scivolo_v6') if bb_overlap(col, ALL[k])}
    ACCESS[nm] = {'free_length_mm': round(z1 - z0, 1), 'obstruction_mm3': hit}
print('key access:', ACCESS)
print(f'checks done in {time.time() - t_start:.0f} s')

# ---------------- v6.json ----------------
HEX = {'chiocciola_v6': 'PETG black: bowl, v4b core (seats, keys, bayonet lugs, latch slot, rim gasket groove) + outward funnel ending on the base plane; inserts 3 tower + 2 chute; well drain Ø3; drip groove (new)',
       'scivolo_v6': 'PETG green: 55 deg chute Ø44, 12 mm taper to the DN50 spigot Ø42.4/45.6, drip ring + skirt, horizontal outlet cut = 32 mm hood (new)',
       'colletto_v6': 'PETG green: funnel neck lining the shelf hole, sits on the plate, 2 pins, 6 weep slots (new, split from the flange)',
       'flangia_piano_v6': 'PETG black: plate 4 mm, 4 wood-screw ears, skirt + 3 bayonet hooks, 3 window-plate hold-down pins, no legs (new)',
       'disco_v6': 'PETG orange + black label: disco_v4b without the M3x60 bore/counterbore, closed top (new)',
       'piastra_gate_v4b': 'PETG black + green (reused)', 'piastra_finestra_v4b': 'PETG black + green (reused)', 'linguetta_sicura': 'PETG orange (reused)',
       'colonna_v6': 'PETG black: dry tower OD 24, passante at the top (collar Ø21.5, bushing Ø12.4 z 5..-12), 3 top lobes to the bowl, 3 bottom lobes + face O-ring groove to the box (new)',
       'albero_v6': 'PETG black: shaft Ø12 solid, keyed hex AF8 at both ends, 2 O-ring grooves (new)',
       'mozzo_v6': 'PETG black: hub on the 25T servo spline, keyed hex socket for the shaft, one M3x8 (new)',
       'scatola_v6': 'PETG black: box 2.4 walls, hip roof 2.5 deg with flat plateau Ø51, drip lip, integrated coaxial servo cradle, breadboard rails, gland pad, 4 button lugs/posts (new)',
       'fondello_v6': 'PETG black + orange inlays: cover with skirt, inner lip, lip-gasket groove, 4 ears with detent dimples, breadboard supports (new)',
       'nottolino_v6': 'PETG orange x4: quarter-turn buttons on the box posts, captive (keyway passes the flatted head only 135 deg from closed), detent bump (new)'}
TPUD = {'guarnizione_baionetta': 'rim gasket (reused)', 'labbro_uscita_1/2, labbro_finestra_1/2': 'plate lips (reused, 4 pcs)',
        'guarnizione_piano_v5': 'flange <-> shelf ring 2x2 (reused design, same file; sits 2 mm lower in v6)',
        'guarnizione_fondello_v6': 'cover <-> box: TPU 95A lip seal (base 2.2x1.2 in the groove, lip 0.8 thick, 1.7 tall, 30 deg inward, bent 1.2 when closed) (new)'}
HARDWARE = [
    {'qty': 4, 'item': 'wood screw 5x25 pan head (5x20 for an 18 mm shelf)', 'use': 'flange -> shelf, heads counterbored from below'},
    {'qty': 3, 'item': 'M3x12 DIN912 A2', 'use': 'tower top lobes -> inserts in the bowl base, from below (bench joint)'},
    {'qty': 3, 'item': 'M3x10 DIN912 A2', 'use': 'tower bottom lobes -> blind inserts in the box plateau, from above, outside the face O-ring'},
    {'qty': 2, 'item': 'M3x10 DIN912 A2', 'use': 'chute ears -> inserts in the bowl nose, from below'},
    {'qty': 4, 'item': 'M3x8 DIN912 A2 + washer DIN 125', 'use': 'servo tabs -> cradle pad inserts, from below (as drivetrain v4)'},
    {'qty': 1, 'item': 'M3x8 DIN912 A2', 'use': 'mozzo_v6 -> servo spline thread, from above through the hub hex socket (bench)'},
    {'qty': 12, 'item': 'M3 heat-set insert L 5.7 for Ø4.0 (Ruthex RX-M3x5.7)', 'use': '3 bowl base + 2 bowl nose + 3 box plateau (blind) + 4 servo pads'},
    {'qty': 2, 'item': 'O-ring NBR70 9x2', 'use': 'shaft, both grooves, in the Ø12.4 bushing at the top of the tower'},
    {'qty': 1, 'item': 'O-ring NBR70 24x2', 'use': 'face seal tower flange <-> box plateau (groove OD 28, 2.7 x 1.5)'},
    {'qty': 1, 'item': 'M16x1.5 cable gland IP68 + locknut', 'use': 'the only cable entry (12 V), +Y end wall, low, on a flat Ø28 pad'},
    {'qty': 1, 'item': 'food-grade silicone grease NSF H1', 'use': 'shaft O-rings, face O-ring, lip gasket'},
    {'qty': 1, 'item': 'optional: PP-HT DN50 pipe (OD 50 / ID 46.4)', 'use': 'slides over the chute spigot up to the step to extend the outlet down to the bowl'}]
ASSEMBLY = [
    f'shelf: hole saw Ø{v5.SHELF_HOLE_D:.0f}, centre {HOLE_C[0]:.0f} mm towards +X (window side) from the shaft axis; shelf 18..40 mm',
    'flange: guarnizione_piano_v5 in the top groove, colletto_v6 on the plate (2 pins), neck into the hole, 4 wood screws 5x25 from below',
    'bowl (bench): heat-set 3 inserts (tower) + 2 (chute) from below; latch into its slot; rim gasket; scivolo_v6 onto the nose, 2x M3x10 from below',
    'box (bench): heat-set 3 plateau + 4 pad inserts; breadboard with ESP32, regulators, capacitor slid up between the +X wall rails; M16 gland; silica bag',
    'servo (bench): mozzo_v6 on the spline (set the 25T position for the firmware zero), M3x8 from above through the hex socket; push the servo up into the cradle, 4x M3x8 + washers',
    'tower (bench): greased O-ring 24x2 in the flange groove; colonna_v6 on the plateau (one-way lobes), 3x M3x10 from above',
    'shaft (bench): 2 greased O-rings 9x2 on albero_v6; push it down through the bushing into the keyed hex socket of the hub',
    'tower -> bowl (bench): collar through the bowl base hole, one-way lobes on the inserts, 3x M3x12 from below (2.5 mm L-key in the 30 mm gap)',
    'dosing core from above: gate plate (keys), disco_v6 on the hex (rib on the +Y flat), window plate, 4 lips',
    'cover: lip gasket in the groove, push the cover up (ears against the lugs), turn the 4 orange buttons 90 deg until they click (no tool)',
    'install: lift the whole unit to the flange, lugs at 60/180(key)/300 into the slots, push up, rotate +30 deg until the orange latch clicks; plug the 12 V cable; drum on the shelf',
    'REMOVAL: press the orange latch, rotate -30 deg, lower: bowl + plates + disc + chute + tower + shaft + box + servo + electronics come down as ONE unit; only the 12 V plug/cable comes along (fit an inline IP67 connector or leave slack)',
    'SERVICE on the bench: window plate, disc, gate plate lift out from the top; shaft pulls out upward (O-ring check) without opening the box; cover: 4 buttons']
IP65 = {
    'principle': 'wet volumes: the bowl interior, the funnel and the open chute. Dry volume: tower bore below the shaft O-rings + the box. Every wet/dry joint has an O-ring or a TPU seal; openings face down; no windows',
    'openings': [
        'shelf hole -> colletto_v6: open by design (kibble + rain path); the collar lines the hole, 6 weep slots drain the annulus into the funnel; flange <-> shelf: guarnizione_piano ring',
        'flange <-> bowl rim: labyrinth tongue/groove + guarnizione_baionetta compressed by the bayonet lift (unchanged)',
        'bowl base <-> tower top: NOT a wet/dry boundary - both sides are wet and the tower top is solid around the bore; the only path to the dry side is along the shaft',
        'shaft: disc labyrinth cap over the collar (unchanged) + NEW Ø3 drain from the central well into the funnel (water never stands near the collar top) + 2x O-ring 9x2 in the bushing at the top of the tower',
        'tower <-> box: face O-ring 24x2 in the tower flange underside on the plateau top (the box print-bed face = flattest surface); 3 screws OUTSIDE the O-ring in BLIND inserts -> no through hole into the box',
        'box: 2.4 walls, hip roof 2.5 deg + drip lip, flat plateau Ø51 sheltered under the bowl; only opening = M16 IP68 gland low on the +Y end wall',
        'cover <-> box: outer skirt (notched only under the 4 lugs, which cover the notch), TPU lip seal under the wall edge, inner lip; ears bear on the lugs = defined lip deflection',
        'chute: open outlet facing straight down (horizontal cut) with a 32 mm hood; drip ring + skirt shed water before the outlet / pipe joint; drip groove on the bowl base underside keeps creeping water away from the tower; bowl <-> chute joint is wet/outside (no seal needed)',
        'pests/humidity: no grid; the two-pocket disc is the rotary airlock (at rest no straight path outlet -> container); no moving parts in the food path other than the disc']}
DEVIATIONS = [
    'stack +30 mm (box plateau at z -30 under the bowl base): the chute alone would clear with less; 30 mm is set by straight 2.5 mm hex-key access to the 3 tower-top screws (needs ~21 mm under their heads)',
    'breadboard sits on the +X wall, i.e. under the shelf-hole vertical: putting it on the -X wall needed the roof 12 mm lower and left only ~3.6 mm to the chute (vs 14.2 mm now); the bowl shadows the box either way',
    f'>= 42 mm passage holds for the whole chute (flare -> outlet, min {CHUTE_PASS_MIN} mm) but NOT for the dosing core inherited from v4b: pocket 28, window 35.7, gate outlet 36.8 mm inscribed - the pocket limits kibble to < 28 mm (owner max 25 mm)',
    'chute is a separate green part (scivolo_v6, 2x M3 from below, not tool-free): an integral inclined chute dips below the bowl base and would need a ~45 mm support tower under the whole base; the joint is the bowl base plane',
    'funnel neck split off the flange as colletto_v6 so the plate prints shelf-face-down without ~13 mm supports under its whole face (v5 needed them, ~30 g of support); above the plate the funnel corners are clamped to the collar wall (in v5 the morph broke ~1 mm through the neck wall at the corners)',
    'two-piece shaft: albero_v6 (keyed hex both ends, solid, O-rings) + mozzo_v6 (spline, one M3x8). M3x60 eliminated; the disc rides on the hex and is trapped by gate/window plates + 3 flange pins (max lift 1.0 of 5.5 mm hex)',
    'servo cradle integrated in the box roof (no passante_culla): the tower is the column with the passante at its top; the box hangs from the tower by 3 screws, the servo hangs from the box',
    'tower <-> bowl and tower <-> box use screws (bench joints); tool-free only for the unit (bayonet) and the cover (buttons)',
    'cover seal is a TPU lip (low force) instead of a compressed TPU 95A 2x2 frame: compressing 95A by 25 % over ~480 mm needs kN-level clamping that printed quarter-turn fasteners cannot give',
    'box roof printed on its plateau needs a thin bed-only support wedge under the 2.5 deg slopes (max ~3.2 mm), as v5; funnel far-side ceiling inside the bowl nose is ~52 deg from vertical (internal, prints with slight sag)',
    'speaker/meow of the behavioural contract still has no opening (sealed box, as v5): a piezo inside will be muffled - open point']
RISKS = ['TPU 95A printed lip seal: print a test strip, then hose-test the closed box',
         'hub M3x8 into the servo spline thread: check the real thread depth of the servo (engagement 3.5 mm modelled)',
         '25T spline: the hub can seat in 25 positions -> set the disc zero in firmware after assembly',
         'butt joint bowl/chute drips a little to the outside under heavy rain (harmless, not into the box)',
         'DN50 pipe must be supported separately if longer than ~0.5 m (2 small screws hold the chute)',
         'top 6 mm of the breadboard (top rail) has no room for tall parts within r 21 of the axis (plateau boss)',
         'bayonet hook tongues print as 4 mm ledges without support (optional support if the bearing face sags)']
v6doc = {
    'version': VER, 'frame': 'Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside (dosing frame unchanged)',
    'concept': 'one-twist unit: one quarter-turn of the bowl brings down bowl + dosing core + chute + tower + shaft + box + servo + electronics; the flange stays on the shelf',
    'parts_printed_PETG': HEX, 'parts_TPU_95A': TPUD, 'count': COUNT, 'hardware': HARDWARE,
    'stack_z': {'shelf_underside': FL_Z1, 'collar_top': NECK_Z1, 'flange_plate': [FL_Z0, FL_Z1], 'bowl': [0.0, bd.RIM_Z], 'disc': [bd.DISC_Z0, bd.DISC_Z1],
                'tower': [Z_R, BUSH_TOP], 'bushing_bore': [BUSH_BOT, BUSH_TOP], 'shaft_orings_z': list(OR_SHAFT_Z), 'box_plateau_top': Z_R,
                'servo_case': [S_TOP - 40.5, S_TOP], 'spline_tip': SPL_TIP, 'hub': [HUB_Z0, HUB_TOP], 'shaft': [SHAFT_BOT, dt.HEX_Z1],
                'box_wall_bottom': Z_W, 'cover': [Z_C - CV_T, Z_C], 'buttons': [HEAD_Z0, BTN_Z1], 'chute_outlet_cut': round(Z_END, 2),
                'unit_height_below_shelf_mm': round(FL_Z1 - (Z_C - CV_T), 1), 'v5_unit_height_below_shelf_mm': round(v5.FL_Z1 - v5.CV_Z0, 1)},
    'shelf': {'hole_saw_d': v5.SHELF_HOLE_D, 'hole_centre_xy': list(HOLE_C), 'thickness_mm': [18, 40], 'wood_screws_xy': [list(map(lambda v: round(v, 1), p)) for p in WOOD_XY]},
    'chute': {'angle_deg': TH_DEG, 'inner_d': 2 * RI, 'wall': T_CH, 'funnel_ellipse_centre_x_at_z0': X_B, 'step_s': S_R, 'spigot': {'od': 2 * R_SP_O, 'id': 2 * R_SP_I, 'floor_side_len': SP_FLOOR_L},
              'outlet': 'horizontal cut at z %.2f: opening faces straight down, hood %.1f mm' % (Z_END, HOOD_EXT), 'drip_ring': {'od': 2 * RING_R, 'skirt': [SKIRT_L, SKIRT_T]}},
    'tower': {'od': 2 * COL_R, 'top_lobes_deg': list(TOP_LOBE_ANG), 'bottom_lobes_deg': list(BOT_LOBE_ANG), 'bore_dry_d': COL_BORE_D, 'face_oring': FACE_OR},
    'box': {'outer_xy': [list(WX), list(WY)], 'inner_xy': [list(IX), list(IY)], 'wall': WALL, 'roof': ROOF_T, 'plateau_r': PLAT_R, 'slope_deg': SLOPE_DEG,
            'height_outer_mm': round(Z_R - Z_W, 1), 'inner_height_mm': round(Z_R - PLAT_T - Z_C, 1),
            'outer_size_mm': [round(WX[1] - WX[0], 1), round(WY[1] - WY[0], 1), round(Z_R - (Z_C - CV_T), 1)],
            'v5_outer_size_mm': [round(v5.WX[1] - v5.WX[0] + 2 * v5.RIM_OUT, 1), round(v5.WY[1] - v5.WY[0] + 2 * v5.RIM_OUT, 1), round(0 - v5.CV_Z0, 1)],
            'breadboard': BB, 'gland': GLAND, 'buttons_y': list(BTN_Y)},
    'assembly': ASSEMBLY, 'ip65': IP65, 'deviations_from_brief': DEVIATIONS, 'open_risks': RISKS,
    'checks': {'watertight_built': {k: bool(m.is_watertight) for k, m in P.items()}, 'watertight_exported_stl_reload': EXPORT_WT,
               'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'soft_designed_overlap_mm3': soft,
               'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
               'passage_mm': PASS, 'slopes_deg': SLOPES, 'clearances_mm': CLR,
               'bayonet': {'removal_sweep_angle_dz_mm3': SWEEP, 'max_mm3': BAY_MAX, 'latch_locked_vs_flange': LATCH_LOCK, 'bowl_latch_at_insertion_vs_flange': BAY_INS},
               'coaxiality': COAX, 'disc_axial_retention': RET, 'key_access': ACCESS, 'print_downfacing_flatter_45_mm2': OVH},
    'grams': {'method': 'solid = volume x density (PETG 1.27, TPU 1.21); print estimate = 1.2 mm shell over the whole surface (~3 walls / top-bottom) + 15 % infill of the rest; same formula for v5 and v6',
              'v6': G6, 'v6_total': G6T, 'v5': G5, 'v5_total': G5T,
              'saving_print_est_g': round(G5T['grams_print_est'] - G6T['grams_print_est'], 1),
              'saving_pct': round(100 * (1 - G6T['grams_print_est'] / G5T['grams_print_est']), 1),
              'note': 'v5 additionally needed ~13 mm supports under the whole flange face (~30 g) and a support wedge under the box roof; v6 keeps only the roof wedge'},
    'print': PRINT_TXT,
    'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] + [f'{k}_print_{c}.stl' for c, _ in COLOUR[k] if len(COLOUR[k]) > 1] for k in P} |
             {'assembled_position_copies': 'v6_asm/*.stl (colour bodies, reused parts at their v6 position, bought placeholders)', 'check': 'check_v6.png', 'viewer': 'v6_viewer.json'}}
json.dump(v6doc, open(OUT + 'v6.json', 'w'), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else (int(o) if isinstance(o, np.integer) else str(o)))
print('v6.json written')

# ---------------- v6_viewer.json ----------------
C = dict(black='#2a2b2e', orange='#f07a1a', green='#2e9d4f', yellow='#f2c81e', steel='#a8adb3', servo='#23305f', breadboard='#f2f0ea', esp32='#1b1b1b')
DZ = lambda z: [0.0, 0.0, z]
ch_ex = (np.array([0, 0, 30.0]) + 45.0 * DIR).round(1).tolist()
ins_bowl = U([at(cyl(4.0, 0.2, 5.9, 24), x, y) for x, y in TWR_INS + CH_EARS])
ins_box = U([at(cyl(4.0, Z_R - 5.9, Z_R - 0.2, 24), x, y) for x, y in BOT_INS] + [at(cyl(4.0, CAGE_Z0 + 0.2, CAGE_Z0 + 5.9, 24), x, y) for x, y in SERVO_HOLES_W])
FILES['inserts_bowl'] = {'bought': save('bought_inserts_bowl', ins_bowl)}
FILES['inserts_box'] = {'bought': save('bought_inserts_box', ins_box)}
FILES['dn50_pipe'] = {'bought': save('bought_dn50_pipe_optional', PIPE)}
VP = []


def vp(pid, name, key, colour_key, colour, group, material, qty, bought, explode, rotates=False, opacity=1.0):
    VP.append({'id': pid, 'name': name, 'file': FILES[key][colour_key], 'color': colour, 'opacity': opacity, 'group': group, 'material': material,
               'qty': qty, 'bought': bought, 'explode': [round(float(v), 1) for v in explode], 'rotates': rotates})


vp('guarnizione_piano', 'Guarnizione piano (TPU)', 'guarnizione_piano_v5', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(190))
vp('colletto_v6', 'Colletto imbuto', 'colletto_v6', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(175))
vp('flangia_piano_v6', 'Flangia piano', 'flangia_piano_v6', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(150))
vp('viti_legno', 'Viti legno 5x25', 'wood_5x25', 'bought', C['steel'], 'ferramenta', 'acciaio', 4, True, DZ(170))
vp('guarnizione_baionetta', 'Guarnizione baionetta', 'guarnizione_baionetta', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(128))
vp('piastra_finestra_nero', 'Piastra finestra (nero)', 'piastra_finestra_v4b', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(105))
vp('piastra_finestra_verde', 'Piastra finestra (verde)', 'piastra_finestra_v4b', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(105))
vp('labbri', 'Labbri piastre (4)', 'labbri', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 4, False, DZ(92))
vp('disco_v6_arancio', 'Disco dosatore', 'disco_v6', 'orange', C['orange'], 'dosatore', 'PETG arancione', 1, False, DZ(80), True)
vp('disco_v6_nero', 'Disco dosatore (etichetta)', 'disco_v6', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(80), True)
vp('piastra_gate_nero', 'Piastra gate (nero)', 'piastra_gate_v4b', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(58))
vp('piastra_gate_verde', 'Piastra gate (verde)', 'piastra_gate_v4b', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, DZ(58))
vp('chiocciola_v6', 'Chiocciola (vasca dosatore)', 'chiocciola_v6', 'black', C['black'], 'dosatore', 'PETG nero', 1, False, DZ(30))
la = math.radians(bd.LATCH_ANG)
vp('linguetta_sicura', 'Linguetta di sicurezza', 'linguetta_sicura', 'orange', C['orange'], 'dosatore', 'PETG arancione', 1, False, [25 * math.cos(la), 25 * math.sin(la), 30])
vp('inserti_vasca', 'Inserti M3 (vasca)', 'inserts_bowl', 'bought', '#b08d57', 'ferramenta', 'ottone', 5, True, DZ(30))
vp('scivolo_v6', 'Scivolo 55° con cappuccio', 'scivolo_v6', 'green', C['green'], 'dosatore', 'PETG verde', 1, False, ch_ex)
vp('viti_scivolo', 'Viti M3x10 scivolo', 'm3x10_chute', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 2, True, [ch_ex[0], 0, ch_ex[2] - 14])
vp('tubo_dn50', 'Tubo DN50 (opzionale)', 'dn50_pipe', 'bought', '#c9ccd1', 'ferramenta', 'PP-HT', 1, True, [ch_ex[0] - 20, 0, ch_ex[2] - 28], False, 0.3)
vp('viti_torre_vasca', 'Viti M3x12 torre-vasca', 'm3x12_tower_top', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 3, True, DZ(-18))
vp('albero_v6', 'Albero', 'albero_v6', 'black', C['black'], 'trasmissione', 'PETG nero', 1, False, DZ(-8), True)
vp('oring_albero', 'O-ring albero 9x2 (2)', 'oring_shaft_9x2', 'bought', '#1e1e1e', 'guarnizioni', 'NBR70', 2, True, DZ(-8), True)
vp('colonna_v6', 'Torre (passante)', 'colonna_v6', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-40))
vp('oring_faccia', 'O-ring torre-scatola 24x2', 'oring_face_24x2', 'bought', '#1e1e1e', 'guarnizioni', 'NBR70', 1, True, DZ(-52))
vp('viti_torre_scatola', 'Viti M3x10 torre-scatola', 'm3x10_tower_box', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 3, True, DZ(-28))
vp('mozzo_v6', 'Mozzo (scanalato 25T)', 'mozzo_v6', 'black', C['black'], 'trasmissione', 'PETG nero', 1, False, DZ(-55), True)
vp('vite_mozzo', 'Vite M3x8 mozzo', 'm3x8_hub', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 1, True, DZ(-42), True)
vp('scatola_v6', 'Scatola elettronica', 'scatola_v6', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-80))
vp('inserti_scatola', 'Inserti M3 (scatola)', 'inserts_box', 'bought', '#b08d57', 'ferramenta', 'ottone', 7, True, DZ(-80))
vp('pressacavo', 'Pressacavo M16', 'gland_m16', 'bought', '#303030', 'elettronica', 'PA nero', 1, True, [0, 35, -80])
vp('servo', 'Servo standard', 'servo', 'bought', C['servo'], 'trasmissione', 'acquistato', 1, True, DZ(-150))
vp('viti_servo', 'Viti M3x8 servo + rondelle', 'm3x8_servo', 'bought', C['steel'], 'ferramenta', 'acciaio A2', 4, True, DZ(-165))
vp('breadboard', 'Breadboard 165x55', 'breadboard', 'bought', C['breadboard'], 'elettronica', 'acquistato', 1, True, DZ(-150))
vp('esp32', 'ESP32-WROVER dev board', 'esp32', 'bought', C['esp32'], 'elettronica', 'acquistato', 1, True, [-15, 0, -150])
vp('reg_12v', 'Regolatore Pololu D36V50F6', 'reg_12v_d36v50f6', 'bought', '#2b4a7a', 'elettronica', 'acquistato', 1, True, [-15, 0, -150])
vp('reg_5v', 'Regolatore 5 V logica', 'reg_5v_logic', 'bought', '#2b4a7a', 'elettronica', 'acquistato', 1, True, [-15, 0, -150])
vp('condensatore', 'Condensatore 1000 µF', 'cap_1000uF', 'bought', '#1a1a2e', 'elettronica', 'acquistato', 1, True, [-15, 0, -150])
vp('silica', 'Silica gel 10 g', 'silica_10g', 'bought', '#e8e4d8', 'elettronica', 'acquistato', 1, True, DZ(-150))
vp('guarnizione_fondello_v6', 'Guarnizione a labbro fondello', 'guarnizione_fondello_v6', 'yellow', C['yellow'], 'guarnizioni', 'TPU 95A giallo', 1, False, DZ(-200))
vp('fondello_v6_nero', 'Fondello', 'fondello_v6', 'black', C['black'], 'struttura', 'PETG nero', 1, False, DZ(-215))
vp('fondello_v6_arancio', 'Fondello (scritte)', 'fondello_v6', 'orange', C['orange'], 'struttura', 'PETG arancione', 1, False, DZ(-215))
vp('nottolini_v6', 'Nottolini quarto di giro', 'nottolino_v6', 'orange', C['orange'], 'struttura', 'PETG arancione', 4, False, DZ(-235))
s_out = -Z_END / math.sin(TH)
outlet = axis_pt(s_out)
path = [[HOLE_C[0], 0, FL_Z1 + SHELF_T], [HOLE_C[0], 0, NECK_Z1], [30, 0, FL_Z0], [30, 0, bd.WIN_Z1], [30, 0, 40]]
path += [[round(30 * math.cos(math.radians(a)), 1), round(30 * math.sin(math.radians(a)), 1), 40] for a in (45, 90, 135)]
path += [[-30, 0, 40], [-30, 0, bd.GATE_Z0], [-32, 0, Z_FL], [-40, 0, 12], axis_pt(0).round(1).tolist(), axis_pt(S_R).round(1).tolist(),
         outlet.round(1).tolist(), [round(outlet[0] - 8, 1), 0, round(outlet[2] - 30, 1)], [round(outlet[0] - 12, 1), 0, round(outlet[2] - 70, 1)]]
viewer = {'title': 'Kibble Dispenser Outdoor v6', 'units': 'mm', 'frame': 'Z-up, shaft axis x=y=0', 'rotation_axis_xy': [0, 0],
          'groups': {'struttura': 'Struttura', 'dosatore': 'Dosatore', 'trasmissione': 'Trasmissione', 'elettronica': 'Elettronica',
                     'guarnizioni': 'Guarnizioni TPU', 'ferramenta': 'Ferramenta'},
          'parts': VP,
          'scene': {'shelf_underside_z': FL_Z1, 'shelf_thickness': SHELF_T, 'shelf_hole_xy': list(HOLE_C), 'shelf_hole_d': v5.SHELF_HOLE_D,
                    'outlet_xyz': outlet.round(2).tolist(), 'outlet_dir': [0, 0, -1]},
          'kibble_path': [[round(float(v), 2) for v in p] for p in path]}
json.dump(viewer, open(OUT + 'v6_viewer.json', 'w'), indent=1)
missing = [p['file'] for p in VP if not os.path.exists(p['file'])]
print('v6_viewer.json written:', len(VP), 'entries; missing files:', missing)
