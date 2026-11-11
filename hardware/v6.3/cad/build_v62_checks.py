# executed by build_v62.py (exec) in its namespace: context, interference + designed contacts, seal continuity, line of
# sight, tool access per screw, gate passage / hold / interlock, bayonet sweep, load case, grams, render, drilling
# template, v62.json, v62_viewer.json
import time
import collections
from scipy.spatial import cKDTree
sys.path.insert(0, dt.HERE)                           # toolaccess.py and los.py live next to the scripts
from toolaccess import check_screw, axial_hits
from los import crop, first_hits
t_start = time.time()
P611, EX611 = EXTRA['P611'], EXTRA['EX611']
TTS = EX611['tts']
LD = lambda f: trimesh.load(f)
print('\n--- context ---')
SHELF_T = 30.0
SHELF = D(box(-150, 150, -110, 110, FL_Z1_62, FL_Z1_62 + SHELF_T), [at(cyl(v5.SHELF_HOLE_D, FL_Z1_62 - 1, FL_Z1_62 + SHELF_T + 1), *v6.HOLE_C)])
R61 = {k: v6.clean(LD(OUT + k + '.stl')) for k in ('guarnizione_baionetta_v61', 'guarnizione_fondello_v61', 'disco_v61')}
COLLAR = v6.build_collar(v6.fl_funnel_cavity()); COLLAR.apply_translation([0, 0, DZ_FL])
GSK_PIANO = v5.build_flange_gasket() if hasattr(v5, 'build_flange_gasket') else LD(OUT + 'guarnizione_piano_v5.stl')
GSK_PIANO.apply_translation([0, 0, FL_Z1_62 - (v5.FL_Z1 if hasattr(v5, 'build_flange_gasket') else FL_Z1)])
SHAFT, HUB = v6.build_shaft(), v6.build_hub()
LATCH = b61.R5['linguetta_sicura']
BOUGHT, SCREWS = bought62()
LIPS = {}
for nm, T, *_ in lip_frames():
    m = P['labbro_pettine_v62'].copy(); m.apply_transform(T); LIPS[f'labbro_pettine_{nm}'] = m
disc0, disc180 = R61['disco_v61'], rotz(R61['disco_v61'], 180)
G_OPEN, G_CLOSED = 0.0, STROKE
BLADE = {g: gate_pose(P['saracinesca_v62'], g) for g in (G_OPEN, G_CLOSED)}
RINGP = {g: gate_pose(P['anello_saracinesca_v62'], g) for g in (G_OPEN, G_CLOSED)}
CH_PLACED = {'canalina_base_1': place_channel(P['canalina_base_v62'], FL_R62 - CH['insert']),
             'canalina_coperchio_1': place_channel(P['canalina_coperchio_v62'], FL_R62 - CH['insert'])}
L2 = L2_CH
b2, c2 = build_channel62(L2)
CH_PLACED['canalina_base_2'] = place_channel(b2, FL_R62 - CH['insert'] + CH['seg'])
CH_PLACED['canalina_coperchio_2'] = place_channel(c2, FL_R62 - CH['insert'] + CH['seg'])
CH_PLACED['canalina_tappo'] = place_channel(P['canalina_tappo_v62'], FL_R62 - CH['insert'] + CH['seg'] + L2)
ALL = {'flangia_piano_v62': P['flangia_piano_v62'], 'flangia_alta_v62': P['flangia_alta_v62'], 'saracinesca_v62@open': BLADE[G_OPEN],
       'anello_saracinesca_v62@open': RINGP[G_OPEN], 'passacavo_v62': P['passacavo_v62'], 'labbro_ombra_v611': P611['labbro_ombra_v611'],
       'colletto_v6': COLLAR, 'guarnizione_piano_v5': GSK_PIANO, 'chiocciola_v62': P['chiocciola_v62'], 'scivolo_v611': P611['scivolo_v611'],
       'labbro_scivolo_v611': P611['labbro_scivolo_v611'], 'linguetta_sicura': LATCH, 'guarnizione_baionetta_v61': R61['guarnizione_baionetta_v61'],
       'piastra_gate_v62': P['piastra_gate_v62'], 'piastra_finestra_v62': P['piastra_finestra_v62'], 'disco_v61@0': disc0, 'disco_v61@180': disc180,
       'colonna_v62': P['colonna_v62'], 'albero_v6@0': SHAFT, 'mozzo_v6@0': HUB, 'scatola_v62': P['scatola_v62'], 'guscio_v611': P611['guscio_v611'],
       'pulsante_v611': P611['pulsante_v611'], 'fondello_v62': P['fondello_v62'], 'guarnizione_fondello_v61': R61['guarnizione_fondello_v61'],
       'nottolino_A': TTS[0], 'nottolino_B': TTS[1], 'nottolino_C': TTS[2], 'shelf': SHELF}
ALL.update(LIPS); ALL.update(BOUGHT); ALL.update(SCREWS); ALL.update(CH_PLACED)
CHANGED = set(P) | {'saracinesca_v62@open', 'anello_saracinesca_v62@open', 'colletto_v6', 'guarnizione_piano_v5', 'shelf', 'cable_12v_supply', 'cable_12v_unit',
                    'connector_m8_ip67', 'vent_m12_eptfe', 'oring_3x1', 'm3x40_stack', 'wood_5x35', 'st29_join', 'inserts_bowl', 'inserts_box'} | set(LIPS) | set(CH_PLACED)
SOFT_ROLE = {
    ('flangia_piano_v62', 'guarnizione_baionetta_v61'): 'bayonet rim lip seal under the lower plate (as v6.1)',
    ('flangia_piano_v62', 'labbro_ombra_v611'): 'skirt lip anchor pressed in the lower plate groove',
    ('labbro_ombra_v611', 'guscio_v611'): 'shadow-gap skirt lip on the shell (as v6.1.1)',
    ('flangia_piano_v62', 'passacavo_v62'): 'cable grommet pressed in the tunnel mouth',
    ('passacavo_v62', 'cable_12v_supply'): 'grommet on the cable (pod second barrier)',
    ('guarnizione_piano_v5', 'shelf'): 'shelf gasket (as v6.1)', ('guarnizione_piano_v5', 'flangia_alta_v62'): 'shelf gasket in its groove',
    ('scatola_v62', 'guarnizione_fondello_v61'): 'PRIMARY dry box: cap lip on the box rim face', ('fondello_v62', 'guarnizione_fondello_v61'): 'cap lip in its groove',
    ('oring_shaft_9x2', 'colonna_v62'): 'shaft O-rings in the bushing', ('oring_shaft_9x2', 'albero_v6@0'): 'shaft O-rings in their grooves',
    ('oring_face_24x2', 'colonna_v62'): 'face O-ring in the tower groove', ('oring_face_24x2', 'scatola_v62'): 'face O-ring on the box plateau',
    ('oring_3x1', 'scatola_v62'): 'NEW: O-ring 3x1 in the roof countersink (P2/P3 keep the dry box sealed)',
    ('oring_3x1', 'm3x40_stack'): 'NEW: O-ring 3x1 squeezed by the screw head / on the shank',
    ('oring_tt_8x1.5', 'fondello_v62'): 'thumb-turn O-rings in the bores', ('oring_tt_8x1.5', 'nottolino_A'): 'thumb-turn O-ring', ('oring_tt_8x1.5', 'nottolino_B'): 'thumb-turn O-ring',
    ('oring_tt_8x1.5', 'nottolino_C'): 'thumb-turn O-ring', ('keys_3x3x18', 'nottolino_A'): 'key pressed in the shaft', ('keys_3x3x18', 'nottolino_B'): 'key pressed in the shaft',
    ('keys_3x3x18', 'nottolino_C'): 'key pressed in the shaft', ('keys_3x3x18', 'scatola_v62'): 'keys on the cup ledges',
    ('oring_seam_2', 'fondello_v62'): 'seam O-ring in the spigot groove', ('oring_seam_2', 'guscio_v611'): 'seam O-ring on the shell',
    ('labbro_scivolo_v611', 'fondello_v62'): 'chute lip anchor', ('labbro_scivolo_v611', 'scivolo_v611'): 'chute lip on the chute',
    ('oring_btn_14x1.5', 'guscio_v611'): 'button O-ring', ('oring_btn_14x1.5', 'pulsante_v611'): 'button O-ring',
    ('flangia_alta_v62', 'canalina_base_1'): 'channel base end pressed into the flange port', ('flangia_alta_v62', 'canalina_coperchio_1'): 'channel cover end in the port',
    ('canalina_base_1', 'canalina_coperchio_1'): 'cover snap lips on the base barbs', ('canalina_base_2', 'canalina_coperchio_2'): 'cover snap lips on the base barbs',
    ('canalina_base_2', 'canalina_tappo'): 'end-cap tongue in the channel', ('canalina_coperchio_2', 'canalina_tappo'): 'end-cap tongue in the cover',
    ('canalina_base_1', 'shelf'): 'channel base screwed to the shelf face', ('canalina_base_2', 'shelf'): 'channel base screwed to the shelf face'}
for lk in LIPS:
    SOFT_ROLE[(lk, 'disco_v61@0')] = 'comb lip on the disc (0.15 preload)'; SOFT_ROLE[(lk, 'disco_v61@180')] = 'comb lip on the disc (0.15 preload)'
    SOFT_ROLE[(lk, 'piastra_gate_v62' if 'out' in lk else 'piastra_finestra_v62')] = 'comb lip anchor pressed in the groove'
SOFT = {frozenset(k): v for k, v in SOFT_ROLE.items()}
_skip = [('disco_v61@0', 'disco_v61@180'), ('disco_v61@0', 'mozzo_v6@0'), ('mozzo_v6@0', 'albero_v6@0'), ('mozzo_v6@0', 'servo'), ('mozzo_v6@0', 'm3x8_hub'),
         ('shelf', 'wood_5x35'), ('inserts_bowl', 'm3x40_stack'), ('inserts_bowl', 'm3x10_chute'), ('inserts_bowl', 'm3x12_shell_tabs'), ('inserts_box', 'm3x8_servo'),
         ('servo', 'm3x8_hub'), ('servo', 'm3x8_servo'), ('scatola_v62', 'gland_m12'), ('scatola_v62', 'vent_m12_eptfe'), ('cable_12v_unit', 'gland_m12'),
         ('cable_12v_unit', 'connector_m8_ip67'), ('cable_12v_supply', 'connector_m8_ip67'), ('inserts_bowl', 'chiocciola_v62'), ('inserts_box', 'scatola_v62'),
         ('st29_join', 'flangia_alta_v62'), ('st29_join', 'flangia_piano_v62'), ('wood_5x35', 'flangia_alta_v62'), ('wood_5x35', 'flangia_piano_v62'),
         ('cable_12v_supply', 'canalina_base_1'), ('cable_12v_supply', 'canalina_base_2'), ('cable_12v_supply', 'canalina_tappo'), ('cable_12v_supply', 'shelf'),
         ('cable_12v_supply', 'canalina_coperchio_1'), ('cable_12v_supply', 'canalina_coperchio_2'),
         ('m3x40_stack', 'chiocciola_v62'), ('m3x40_stack', 'colonna_v62'), ('m3x40_stack', 'scatola_v62')]
SKIP = {frozenset(p) for p in _skip}
# the stack screws run in clearance holes / inserts: their contact with the drilled parts is checked separately (hole clearances)


def bb_overlap(a, b, pad=0.05):
    return bool(np.all(a.bounds[0] <= b.bounds[1] + pad) and np.all(b.bounds[0] <= a.bounds[1] + pad))


print('\n--- interference (mm3) ---')
inter, soft = {}, {}
names = list(ALL)
for i, a in enumerate(names):
    for b_ in names[i + 1:]:
        key = frozenset((a, b_))
        if key in SKIP or (a not in CHANGED and b_ not in CHANGED):
            continue
        v = round(vol(I(ALL[a], ALL[b_])), 4) if bb_overlap(ALL[a], ALL[b_]) else 0.0
        (soft if key in SOFT else inter)[f'{a}|{b_}'] = v
        if key not in SOFT and v > 1e-3:
            print(f'  HARD {a:30s}|{b_:30s} {v:.4f}')
HARD_MAX = max(inter.values())
# stack screws vs the parts they pass through: must sit in the clearance holes (Ø3.4) / inserts only
SCREW_HOLE = {k: round(vol(I(SCREWS['m3x40_stack'], ALL[k])), 4) for k in ('chiocciola_v62', 'colonna_v62', 'scatola_v62')}
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3; stack screw vs drilled parts {SCREW_HOLE}')
print(f'interference done {time.time() - t_start:.0f} s')

# ---------------- gate closed + all-angle sweep of the gate against everything that stays ----------------
print('\n--- gate sweep ---')
GATE_FIXED = U([P['flangia_piano_v62'], P['flangia_alta_v62']])
UNIT_TOP = I(U([P611['guscio_v611'], P611['pulsante_v611'], P611['labbro_ombra_v611'], P['chiocciola_v62'], LATCH]), above(28.0))
GATE_SWEEP = []
for g in np.r_[np.arange(0.0, STROKE, 8.0), STROKE]:
    bl, rg = gate_pose(P['saracinesca_v62'], g), gate_pose(P['anello_saracinesca_v62'], g)
    GATE_SWEEP.append([round(float(g), 1), round(vol(I(bl, GATE_FIXED)), 4), round(vol(I(rg, GATE_FIXED)), 4), round(vol(I(U([bl, rg]), UNIT_TOP)), 4),
                       round(vol(I(bl, rg)), 4)])
print('g, blade|flange, ring|flange, gate|unit, blade|ring(peg)', GATE_SWEEP)

# ---------------- open passage, coverage vs angle, interlock ----------------
from shapely.ops import polylabel
PIE = v5.OPENING
PIN2D = Point(0, 0).buffer(PIVOT_D / 2, resolution=64)


def blade2d(g):
    return blade_sector(LEAD_OPEN - g, LEAD_OPEN + BLADE_W - g).difference(Point(0, 0).buffer(PIVOT_HOLE / 2, resolution=32))


open_free = PIE.difference(blade2d(0.0)).difference(PIN2D)
pl = polylabel(open_free, 0.02)
PASSAGE = {'v611_minimum_section': 'flange funnel pie at the flange underside (v6.1.1)', 'v611_area_mm2': round(PIE.area, 1),
           'v611_inscribed_d_mm': round(2 * PIE.exterior.distance(polylabel(PIE, 0.02)), 2),
           'v62_gate_open_area_mm2': round(open_free.area, 1), 'v62_area_ratio': round(open_free.area / PIE.area, 4),
           'v62_inscribed_d_mm': round(2 * open_free.exterior.distance(pl), 2),
           'pivot_pin_takes_mm2': round(PIE.intersection(PIN2D).area, 2),
           'note': 'the Ø4 pivot pin covers 1.1 mm2 at the pie apex (r < 2), where the opening is narrower than the smallest kibble; '
                   'the blade parks 0.35 deg outside the pie edge: full passage elsewhere',
           'gate_plane_z': list(BLADE_Z), 'downstream_unchanged': 'pie prism down to the bowl rim (66.1), then the unchanged v6.1 window/disc'}
COVER = []
for g in np.arange(0.0, STROKE + 0.01, 1.0):
    cov = PIE.intersection(blade2d(g).union(PIN2D)).area / PIE.area
    COVER.append((round(float(g), 1), round(cov, 4)))
RESID_OK = 3.0                                              # mm2 left open allowed (crumb-size slivers only)


def residual(g):
    r_ = PIE.difference(blade2d(g).union(PIN2D))
    if r_.is_empty:
        return 0.0, 0.0
    gs_ = [r_] if r_.geom_type == 'Polygon' else list(r_.geoms)
    return r_.area, max(2 * gg.exterior.distance(polylabel(gg, 0.01)) for gg in gs_ if gg.area > 1e-6) if any(gg.area > 1e-6 for gg in gs_) else 0.0


def covered(g):
    a_, d_ = residual(g)
    return a_ <= RESID_OK and d_ <= 1.0


g_full = min(g for g, c in COVER if covered(g))
# interlock: probes along the button axis (radial, LATCH_A, BTN_Z) from the button face outward; the ring at angle g
r_out_btn = shell_r_at(LATCH_A, BTN_Z, 0.0)
u_face = r_out_btn - b611.BTN611['dish_h']
ua = math.radians(LATCH_A)
uvec = np.array([math.cos(ua), math.sin(ua), 0.0]); wvec = np.array([-math.sin(ua), math.cos(ua), 0.0]); zvec = np.array([0, 0, 1.0])
PROBES = [('thumb Ø16 centred', 16.0, 0.0, 0.0)] + [('fingertip Ø10 offset 4 mm', 10.0, 4.0 * math.cos(t), 4.0 * math.sin(t)) for t in np.radians(np.arange(0, 360, 45))] + \
         [('fingertip Ø10 centred', 10.0, 0.0, 0.0)]


def reachable(ring_m):
    rc = I(ring_m, box(-60, 80, 20, 120, 20, 75))
    out = []
    for nm_, dpr, ow, oz in PROBES:
        p0 = np.array([0, 0, BTN_Z]) + (u_face + 0.3) * uvec + ow * wvec + oz * zvec
        hits = axial_hits({'ring': rc}, p0, uvec, dpr / 2, 0.0, 40.0)
        out.append(not hits)
    return out


INTERLOCK = []
for g in np.r_[np.arange(0.0, 96.0, 8.0), np.arange(96.0, STROKE + 0.01, 1.0)]:
    rr = reachable(gate_pose(P['anello_saracinesca_v62'], g))
    cov = PIE.intersection(blade2d(g).union(PIN2D)).area / PIE.area
    ra_, rd_ = residual(g)
    INTERLOCK.append({'g_deg': round(float(g), 1), 'opening_covered': round(cov, 4), 'residual_open_mm2': round(ra_, 2), 'residual_gap_d_mm': round(rd_, 2),
                      'kibble_tight': bool(covered(g)), 'thumb_reaches_button': bool(rr[0]), 'any_fingertip_reaches': bool(any(rr[1:]))})
reach_g = [d['g_deg'] for d in INTERLOCK if d['any_fingertip_reaches'] or d['thumb_reaches_button']]
g_reach_first = min(reach_g) if reach_g else None
INTERLOCK_OK = bool(reach_g and all(d['kibble_tight'] for d in INTERLOCK if d['any_fingertip_reaches'] or d['thumb_reaches_button'])
                    and INTERLOCK[-1]['thumb_reaches_button'])
RESID_CLOSED = residual(STROKE)
print('full cover from g', g_full, '; button first reachable at g', g_reach_first, '; interlock strict:', INTERLOCK_OK, '; residual at full stroke', RESID_CLOSED)

# ---------------- gate holds a full column: Janssen + plate ----------------
RHO_B, Dd, Hh, MU_W, K_J = 450.0, 0.585, 0.85, 0.30, 0.40
p_inf = RHO_B * 9.81 * Dd / (4 * MU_W * K_J)
p_jan = p_inf * (1 - math.exp(-4 * MU_W * K_J * Hh / Dd))
p_hyd = RHO_B * 9.81 * Hh
p_des = max(2.0 * p_jan, p_inf, p_hyd)
a_ = PASSAGE['v611_inscribed_d_mm'] / 2
E_P, NU, t_b = 2000.0, 0.38, BLADE_Z[1] - BLADE_Z[0]
q = p_des * 1e-6
sig_b = 3 * (3 + NU) * q * a_ ** 2 / (8 * t_b ** 2)
Dp = E_P * t_b ** 3 / (12 * (1 - NU ** 2))
w_b = q * a_ ** 4 * (5 + NU) / (64 * Dp * (1 + NU))
F_col = p_des * 1e-6 * PIE.area
HOLD = {'assumptions': f'full 200 L drum (Ø{Dd*1000:.0f} x {Hh*1000:.0f} mm kibble), bulk density {RHO_B/1000:.2f}, wall friction {MU_W} (kibble on HDPE), '
                       f'Janssen K {K_J}; design pressure = max(2 x Janssen at the bottom, Janssen asymptote, hydrostatic without wall friction)',
        'p_janssen_bottom_kPa': round(p_jan / 1000, 2), 'p_janssen_asymptote_kPa': round(p_inf / 1000, 2), 'p_hydrostatic_kPa': round(p_hyd / 1000, 2),
        'p_design_kPa': round(p_des / 1000, 2), 'force_on_opening_N': round(F_col, 1),
        'blade_model': f'PETG plate {t_b:.1f} mm, simply supported over the largest inscribed circle of the opening (Ø{2*a_:.1f}); the blade rests on '
                       'the lower plate all round the pie (and on the landing floor past the far edge at full stroke)',
        'blade_bending_MPa': round(sig_b, 2), 'blade_SF': round(45.0 / sig_b, 0), 'blade_deflection_mm': round(w_b, 3),
        'creep': 'long-term stress < 1 MPa: no creep concern', 'kibble_below_blade_g': round(PIE.area * (FL_Z1 + 0.2 - FL_Z0) / 1000 * 0.45, 1),
        'closing': 'single-bevel knife leading edge (0.6 edge, 25 deg) lifts pieces into the column; over-travel 12.4 deg past the far edge into a '
                   'landing whose far end has a 1.6 mm drain slot (crumbs fall out, no crumb cake); torque at the ring ~0.1-0.5 N m',
        'closing_torque_Nm_est': round(0.5 * F_col * 0.028 + 3e3 * 0.003 * 0.05 * 5 * 0.028, 3)}
print('hold', HOLD)

# ---------------- tool access per screw (v6.2 build order) ----------------
print('\n--- tool access ---')
H = lambda lst, z, up=False: [at(cyl(5.5, z, z + 3.0, 24) if up else cyl(5.5, z - 3.0, z, 24), x, y) for x, y in lst]
EARS = list(b61.CH_EARS); TABS = list(b61.TAB_INS)
ST_TOWER = {'chiocciola_v62': ALL['chiocciola_v62'], 'linguetta_sicura': LATCH, 'colonna_v62': ALL['colonna_v62'], 'albero': SHAFT,
            'oring_shaft': BOUGHT['oring_shaft_9x2'], 'inserts_bowl': SCREWS['inserts_bowl']}
ST_CHUTE = dict(ST_TOWER, scivolo_v611=P611['scivolo_v611'])
ST_SHELL = dict(ST_CHUTE, guscio_v611=P611['guscio_v611'], pulsante_v611=P611['pulsante_v611'])
for j, hh in enumerate(H(EARS, -3.0)):
    ST_SHELL[f'chute_head_{j}'] = hh
BOXSET = {k: ALL[k] for k in ('scatola_v62', 'servo', 'board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF', 'gland_m12',
                              'vent_m12_eptfe', 'mozzo_v6@0', 'm3x8_servo', 'm3x8_hub', 'inserts_box', 'oring_face_24x2', 'cable_12v_unit')}
ST_BOX = dict(ST_SHELL, **BOXSET)
for j, hh in enumerate(H(TABS, -6.0)):
    ST_BOX[f'tab_head_{j}'] = hh
TA = {}
for j, (x, y) in enumerate(EARS):
    st = dict(ST_CHUTE); st.update({f'c{k}': hh for k, hh in enumerate(H(EARS, -3.0)) if k != j})
    TA[f'step 3 chute -> bowl M3x10 ({x:.0f}, {y:+.1f})'] = check_screw(st, (x, y, -6.0), (0, 0, -1))
for j, (x, y) in enumerate(TABS):
    st = dict(ST_SHELL); st.update({f't{k}': hh for k, hh in enumerate(H(TABS, -6.0)) if k != j})
    TA[f'step 4 shell -> bowl M3x12 @{ang_of((x, y)):.0f} deg (box not yet in)'] = check_screw(st, (x, y, -9.0), (0, 0, -1))
for j, ((x, y), zs) in enumerate(zip(P_SCREWS, head_seat_z())):
    st = dict(ST_BOX)
    for k, ((x2, y2), z2) in enumerate(zip(P_SCREWS, head_seat_z())):
        if k != j:
            st[f'stack_head_{k}'] = at(cyl(5.5, z2 - 3.0, z2, 24), x2, y2)
    TA[f'step 5 box+tower -> bowl M3x40 P{j + 1} ({x:.1f}, {y:.1f}){" sealed" if P_SEALED[j] else " via ear"}'] = check_screw(st, (x, y, zs - 3.0), (0, 0, -1))
# factory box module (box alone, cap off): servo screws from below, hub screw from above through the plateau
ST_BOXONLY = {k: v for k, v in BOXSET.items() if k not in ('m3x8_servo', 'm3x8_hub')}
tz = dt.TAB_Z0 + v6.DZ_SERVO
for j, (x, y) in enumerate(b61.SERVO_HOLES_W):
    st = dict(ST_BOXONLY); st['hub_screw'] = SCREWS['m3x8_hub']
    TA[f'factory servo -> cradle M3x8 #{j + 1}'] = check_screw(st, (x, y, tz - dt.WASHER_T - 3.0), (0, 0, -1))
st = {k: v for k, v in ST_BOXONLY.items() if k != 'mozzo_v6@0'}
st['mozzo'] = HUB; st['servo_screws'] = SCREWS['m3x8_servo']
TA['factory hub -> servo M3x8 (through the plateau hole, before the tower)'] = check_screw(st, (0, 0, v6.HUB_SCREW_HEAD_Z + 3.0), (0, 0, 1))
# flange: join screws from the shelf face (before mounting), wood screws from below (flange alone on the shelf)
ST_FL = {'flangia_piano_v62': P['flangia_piano_v62'], 'flangia_alta_v62': P['flangia_alta_v62'], 'saracinesca': BLADE[G_OPEN], 'anello': RINGP[G_OPEN],
         'passacavo': P['passacavo_v62'], 'labbro_ombra': P611['labbro_ombra_v611']}
for j, a in enumerate(JOIN['ang']):
    x, y = polar(JOIN['r'], a)
    TA[f'flange join ST2.9x9.5 @{a:.0f} deg (from the shelf face, flange on the bench)'] = check_screw(ST_FL, (x, y, FL_Z1_62 + 0.05), (0, 0, 1), key_d=3.6, hand_d=28.0)
ST_FLS = dict(ST_FL, shelf=SHELF, colletto=COLLAR, gasket=GSK_PIANO, cable=BOUGHT['cable_12v_supply'], **CH_PLACED)
for j, a in enumerate(WOOD_ANG62):
    x, y = polar(WOOD_R62, a)
    TA[f'flange -> shelf wood 5x35 @{a:.0f} deg (PZ2, from below, unit not hung)'] = check_screw(ST_FLS, (x, y, FL_Z0 - 0.5), (0, 0, -1), key_d=6.5, hand_d=32.0)
TA_V611 = json.load(open(dt.HERE + 'ref/ta_v611.json'))   # v6.1.1 baseline, measured once
for k, v in TA.items():
    print(f'  {k:78s} {v["verdict"]:12s} key>={v["key_length_min_mm"]} first={v["first_obstacle"]}')
print(f'tool access done {time.time() - t_start:.0f} s')

# ---------------- bayonet removal path with the gate CLOSED (the only state the interlock lets you unlock) ----------------
print('\n--- bayonet ---')
FIXED = U([P['flangia_piano_v62'], P['flangia_alta_v62'], COLLAR, GSK_PIANO, SHELF, P['passacavo_v62'], BLADE[G_CLOSED], RINGP[G_CLOSED]] +
          [CH_PLACED[k] for k in CH_PLACED])
latch_pressed = LATCH.copy(); latch_pressed.apply_translation([-1.6 * math.cos(ua), -1.6 * math.sin(ua), 0])
btn_pressed = P611['pulsante_v611'].copy(); btn_pressed.apply_translation([-1.5 * math.cos(ua), -1.5 * math.sin(ua), 0])
MOVING = I(U([P['chiocciola_v62'], latch_pressed, P['piastra_finestra_v62'], LIPS['labbro_pettine_win_1'], LIPS['labbro_pettine_win_2'],
              disc0, P['piastra_gate_v62'], P611['guscio_v611'], btn_pressed]), above(28.0))


def unlock_dz(a):
    return 0.0 if a <= bd.LOCK_ROT - bd.LUG_RAMP_DEG else -bd.LIFT * (a - (bd.LOCK_ROT - bd.LUG_RAMP_DEG)) / bd.LUG_RAMP_DEG


poses = [(-a, unlock_dz(a)) for a in np.linspace(0, bd.LOCK_ROT, 11)] + [(-bd.LOCK_ROT, -bd.LIFT - dz) for dz in (2, 5, 10, 20, 40, 80)]
SWEEP = []
for ang_, dz in poses:
    m = rotz(MOVING, ang_); m.apply_translation([0, 0, dz])
    SWEEP.append((round(float(ang_), 1), round(float(dz), 2), round(vol(I(m, FIXED)), 3)))
BAY_MAX = max(v for _, _, v in SWEEP)
ins = rotz(U([P['chiocciola_v62'], LATCH, P611['guscio_v611']]), -bd.LOCK_ROT); ins.apply_translation([0, 0, -bd.LIFT])
BAY_INS = round(vol(I(I(ins, above(28.0)), FIXED)), 4)
# button pressed through the window at full stroke vs the ring
BTN_THROUGH_WINDOW = round(vol(I(btn_pressed, RINGP[G_CLOSED])), 4)
print('sweep', SWEEP, '\ninsertion', BAY_INS, 'button vs ring (closed)', BTN_THROUGH_WINDOW)

# ---------------- clearances ----------------
print('\n--- clearances ---')


def min_dist(a, b, spacing=0.6, refine=300):
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


PIL = I(P['colonna_v62'], below(-0.5))
CLR = {'tower_to_chute': min_dist(PIL, P611['scivolo_v611']), 'tower_to_vent': min_dist(PIL, BOUGHT['vent_m12_eptfe']),
       'ear_to_chute': min_dist(I(P['scatola_v62'], box(-30, -15, 15, 35, EAR_Z0 - 0.1, Z_R + 0.1)), P611['scivolo_v611']),
       'P3_head_to_board': min_dist(at(cyl(5.5, Z_R - ROOF_T - 3.0, Z_R - ROOF_T, 32), *P_SCREWS[2]), BOUGHT['board_70x50']),
       'P2_head_to_vent_nut': min_dist(at(cyl(5.5, Z_R - ROOF_T - 3.0, Z_R - ROOF_T, 32), *P_SCREWS[1]), BOUGHT['vent_m12_eptfe']),
       'ring_to_shell_open': min_dist(RINGP[G_OPEN], P611['guscio_v611']), 'ring_to_shell_closed': min_dist(RINGP[G_CLOSED], P611['guscio_v611']),
       'connector_to_bowl': min_dist(BOUGHT['connector_m8_ip67'], P['chiocciola_v62']), 'connector_to_shell': min_dist(BOUGHT['connector_m8_ip67'], P611['guscio_v611']),
       'supply_cable_to_shell': min_dist(I(BOUGHT['cable_12v_supply'], box(-30, 30, -90, 0, 0, 66.0)), P611['guscio_v611']),
       'supply_cable_to_flange_skirt': min_dist(I(BOUGHT['cable_12v_supply'], box(-30, 30, -90, 0, 40, 66.0)), P['flangia_piano_v62']),
       'blade_to_pocket_wall_radial': round(POCKET_R - BLADE_R, 2), 'blade_gaps_top_bottom': [round(BLADE_Z[0] - FL_Z1, 2), round(POCKET_Z1 - BLADE_Z[1], 2)],
       'dish_to_outlet_chamfer_mm': [round(Point(x, y).buffer(TT_DISH_D62 / 2).distance(Point(CH_X, 0).buffer(b61.OUTLET['r'] + b61.OUTLET['chamfer'])), 2) for x, y in TT],
       'v611_dish_to_outlet_chamfer_mm': [round(Point(x, y).buffer(26.0 / 2).distance(Point(CH_X, 0).buffer(b61.OUTLET['r'] + b61.OUTLET['chamfer'])), 2) for x, y in TT],
       'bowl_insert_wall_mm': {}}
_bs = shapely.unary_union([Point(0, 0).buffer(0)])
for (x, y) in P_SCREWS:
    hole = at(cyl(v6.INS_D + 2.4, 0.0, INS_DEPTH62 + 1.2, 48), x, y)
    CLR['bowl_insert_wall_mm'][f'({x}, {y})'] = 'solid >= 1.2 all round' if vol(D(hole, [P['chiocciola_v62'], at(cyl(v6.INS_D, -1, INS_DEPTH62, 48), x, y),
                                                                                         at(cyl(v6.INS_D + 1.6, -1, 0.4, 48), x, y), below(0.0)])) < 0.05 else 'THIN'
print(CLR)

# ---------------- seal continuity (new + touched seals) ----------------
print('\n--- seal continuity ---')


def sectors_ok(seal, mate, centre, n=36, rmax=200.0, zlim=None):
    cx_, cy_ = centre
    lo, hi = seal.bounds[0] - 1.0, seal.bounds[1] + 1.0
    if zlim:
        lo[2], hi[2] = zlim
    mc = I(mate, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    res = []
    for k in range(n):
        a0, a1 = 360.0 * k / n, 360.0 * (k + 1) / n
        pts = [(0, 0)] + [(rmax * math.cos(math.radians(a)), rmax * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 6)]
        w = at(prism(Polygon(pts), lo[2] - 1, hi[2] + 1), cx_, cy_)
        res.append(round(vol(I(I(seal, w), mc)), 4))
    return {'sectors': n, 'min_overlap_mm3': min(res), 'all_in_contact': bool(min(res) > 0)}


CONT = {}
for (x, y) in P_SCREWS[1:]:
    orr = I(BOUGHT['oring_3x1'], at(cyl(8, -40, -25), x, y))
    CONT[f'oring_3x1 ({x}, {y}) | scatola_v62 (countersink)'] = sectors_ok(orr, P['scatola_v62'], (x, y), 24)
    CONT[f'oring_3x1 ({x}, {y}) | M3x40 (head + shank)'] = sectors_ok(orr, SCREWS['m3x40_stack'], (x, y), 24)
CONT['guarnizione_fondello_v61 | scatola_v62 (PRIMARY lip)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['scatola_v62'], b611.WALL_C.centroid.coords[0])
CONT['guarnizione_fondello_v61 | fondello_v62 (groove)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['fondello_v62'], b611.WALL_C.centroid.coords[0])
CONT['oring_seam | fondello_v62'] = sectors_ok(BOUGHT['oring_seam_2'], P['fondello_v62'], (b611.SEAM_CX, 0.0))
CONT['labbro_ombra | flangia_piano_v62 (anchor)'] = sectors_ok(P611['labbro_ombra_v611'], P['flangia_piano_v62'], (0.0, 0.0), 72)
CONT['labbro_ombra | guscio_v611'] = sectors_ok(P611['labbro_ombra_v611'], P611['guscio_v611'], (0.0, 0.0), 72)
# grommet on the cable: sectors round the local cable axis at the tunnel mouth
pts_t, _, _ = tunnel_rz(48)
zz = np.array([z for _, z in pts_t]); rr_ = np.array([r for r, _ in pts_t])
k0 = int(np.argmin(np.abs(zz - 67.0)))
p_m = np.array(rz_to_xyz([pts_t[k0]])[0]); p_n = np.array(rz_to_xyz([pts_t[k0 + 1]])[0])
tdir = (p_n - p_m) / np.linalg.norm(p_n - p_m)
Tal = trimesh.geometry.align_vectors(tdir, [0, 0, 1]); Tal[:3, 3] = -Tal[:3, :3] @ p_m
gs, cs_, fs = P['passacavo_v62'].copy(), BOUGHT['cable_12v_supply'].copy(), P['flangia_piano_v62'].copy()
for g_ in (gs, cs_, fs):
    g_.apply_transform(Tal)
slab = box(-20, 20, -20, 20, -1.2, 1.2)
CONT['passacavo_v62 | cable (local axis, 2.4 mm slab)'] = sectors_ok(I(gs, slab), I(cs_, slab), (0.0, 0.0), 24)
CONT['passacavo_v62 | flangia_piano_v62 tunnel (local axis)'] = sectors_ok(I(gs, slab), I(fs, slab), (0.0, 0.0), 24)
for k, v in CONT.items():
    print(f'  {k:62s} {v}')

# ---------------- line of sight (thumb-turn dishes changed, tunnel added, shadow gap under the ring) ----------------
print('\n--- line of sight ---')
ZS_IN, X0_IN, X1_IN = section_fn(T_SHELL + 2.0)


def interior(p):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    a, c = np.interp(z, ZS_IN, X0_IN), np.interp(z, ZS_IN, X1_IN)
    cxp, Rp = (a + c) / 2, (c - a) / 2
    inpod = ((x - cxp) ** 2 + y ** 2 < Rp ** 2) & (z > Z_BOT + T_CAP) & (z < Z_TOP)
    ex = np.zeros(len(p), bool)
    for tx, ty in TT:
        ex |= (np.hypot(x - tx, y - ty) < TT_DISH_D62 / 2 + 0.05) & (z < b611.TT_DISH_FLOOR)
        ex |= (np.hypot(x - tx, y - ty) < b611.BOSS_HI_D / 2 + 0.3) & (z < b611.BOSS_TOP + 0.2)
    rk = np.hypot(x - CH_X, y)
    kib = ((rk < RI) & (z > b611.Z_CH_END611)) | ((rk < b61.OUTLET['r']) & (z <= b611.SOCK['bore_z']))
    inpod &= ~ex
    bx = (x > BXO[0] + BX_T) & (x < BXO[1] - BX_T) & (np.abs(y) < BXO[3] - BX_T) & (z < Z_R)
    res = np.array([''] * len(p), dtype=object)
    res[inpod & ~kib] = 'pod'
    res[inpod & bx] = 'dry'
    return res


LOSM = {'fondello_v62': P['fondello_v62'], 'guscio_v611': P611['guscio_v611'], 'flangia_piano_v62': P['flangia_piano_v62'], 'flangia_alta_v62': P['flangia_alta_v62'],
        'labbro_ombra_v611': P611['labbro_ombra_v611'], 'anello': RINGP[G_OPEN], 'nottolino_A': TTS[0], 'nottolino_B': TTS[1], 'nottolino_C': TTS[2],
        'oring_tt': BOUGHT['oring_tt_8x1.5'], 'scatola_v62': P['scatola_v62'], 'keys': BOUGHT['keys_3x3x18'], 'passacavo': P['passacavo_v62'],
        'cable': BOUGHT['cable_12v_supply'], 'guarnizione_fondello_v61': R61['guarnizione_fondello_v61'], 'board': BOUGHT['board_70x50'],
        'chiocciola_v62': P['chiocciola_v62'], 'pulsante': P611['pulsante_v611'], 'labbro_scivolo': P611['labbro_scivolo_v611'], 'scivolo': P611['scivolo_v611']}


def cast(origins, dirs, lo, hi, step=0.2, cap_len=300.0):
    M = {k: crop(m, lo, hi) for k, m in LOSM.items()}
    hit, dist = first_hits(M, origins, dirs)
    dn = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    reach = []
    for o, d, t in zip(origins, dn, dist):
        t = min(t, cap_len)
        s = np.arange(0.1, max(t - 0.1, 0.1), step)
        qq = o + s[:, None] * d
        cls = interior(qq) if len(qq) else np.array([])
        reach.append('dry' if (cls == 'dry').any() else ('pod' if (cls == 'pod').any() else ''))
    return np.array(reach), hit


LOS = {}
rng = np.random.default_rng(7)
for k, (x, y) in zip('ABC', TT):
    rr2, th = np.meshgrid(np.arange(0.05, TT_DISH_D62 / 2, 0.15), np.radians(np.arange(0, 360, 3.0)))
    o = np.c_[x + (rr2 * np.cos(th)).ravel(), y + (rr2 * np.sin(th)).ravel(), np.full(rr2.size, -106.0)]
    d = np.tile([0.0, 0.0, 1.0], (len(o), 1))
    reach, hit = cast(o, d, np.array([x - 40, y - 40, -110]), np.array([x + 40, y + 40, 0]))
    n2 = 3000
    r2 = (TT_DISH_D62 / 2) * np.sqrt(rng.random(n2)); t2 = rng.random(n2) * 2 * np.pi; az = rng.integers(0, 8, n2) * np.pi / 4
    o2 = np.c_[x + r2 * np.cos(t2), y + r2 * np.sin(t2), np.full(n2, -106.0)]
    d2 = np.c_[np.sin(np.radians(20)) * np.cos(az), np.sin(np.radians(20)) * np.sin(az), np.full(n2, np.cos(np.radians(20)))]
    o2 -= d2 * 2.0
    reach2, hit2 = cast(o2, d2, np.array([x - 40, y - 40, -110]), np.array([x + 40, y + 40, 0]))
    LOS[f'thumbturn_{k}'] = {'rays': int(len(o) + n2), 'reach_pod': int((reach == 'pod').sum() + (reach2 == 'pod').sum()),
                             'reach_dry': int((reach == 'dry').sum() + (reach2 == 'dry').sum())}
    print(k, LOS[f'thumbturn_{k}'])
# shadow gap (now also behind the ring)
O_, D_ = [], []
for z in np.linspace(60.0, 66.0, 7):
    for a in np.radians(np.arange(0, 360, 3.0)):
        for e in np.radians([-15, 0, 15]):
            O_.append([97 * math.cos(a), 97 * math.sin(a), z - 13 * math.tan(e)])
            D_.append([-math.cos(a) * math.cos(e), -math.sin(a) * math.cos(e), math.sin(e)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-100, -100, 30]), np.array([100, 100, 80]))
LOS['shadow_gap_behind_ring'] = {'rays': len(O_), 'reach_pod': int((reach != '').sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
# cable tunnel: rays from the channel port inward along / round the tunnel
O_, D_ = [], []
for dy in np.linspace(-2.0, 2.0, 9):
    for dz in np.linspace(-2.0, 2.0, 9):
        for el in np.radians([0, -10, -20, -30, -45]):
            O_.append([dy, -(FL_R62 + 6.0), 74.15 + dz]); D_.append([0.0, math.cos(el), math.sin(el)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-30, -100, 40]), np.array([30, -50, 80]))
LOS['cable_tunnel'] = {'rays': len(O_), 'reach_pod': int((reach != '').sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
print('shadow', LOS['shadow_gap_behind_ring'], 'tunnel', LOS['cable_tunnel'])
print(f'checks A done {time.time() - t_start:.0f} s')

# ---------------- load case (hand calcs) ----------------
print('\n--- load case ---')
S_XY, S_Z, TAU = 45.0, 20.0, 25.0
V61 = json.load(open(OUT + 'v61.json')); V611 = json.load(open(OUT + 'v611.json'))
LC61 = V61['load_case']
W_UNIT = 12.0 + 0.6                                         # v6.1 12.0 N + v6.1.1/v6.2 additions (~60 g)
FV = 250.0 + W_UNIT + 20.0
FL_LAT = 100.0
x_fc = -13.45
Xp = np.array([p[0] for p in P_SCREWS]); Yp = np.array([p[1] for p in P_SCREWS])
Mx = np.array([[1, 1, 1], Xp, Yp], float)
F_ax = np.linalg.solve(Mx, np.array([FV, FV * x_fc, 0.0]))     # vertical shares (cap load through the box)
cx_, cy_ = Xp.mean(), Yp.mean()
worst = (0, None)
for th in np.radians(np.arange(0, 360, 5)):
    # 100 N sideways at the flat bottom carried (conservatively) through the box into the stack: moment about the bowl joint (z 0)
    M = FL_LAT * (0.0 - Z_BOT) / 1000.0
    nx_, ny_ = math.cos(th), math.sin(th)
    dl = (Xp - cx_) * nx_ + (Yp - cy_) * ny_
    Fm = M * 1000 * dl / np.sum(dl ** 2)
    tot = F_ax + Fm
    if tot.max() > worst[0]:
        worst = (float(tot.max()), round(math.degrees(th)))
F_stack = worst[0]
ear_arm = abs(P_SCREWS[0][0] - BXO[0])                      # screw axis to the wall face (ear root)
F_gov = float(max(F_ax))                                    # governing: vertical load only (the cap spigot hands the side load to the shell, as v6.1)
F_P1_cons = max(float((F_ax + M * 1000 * ((Xp - cx_) * math.cos(t) + (Yp - cy_) * math.sin(t)) / np.sum(((Xp - cx_) * math.cos(t) + (Yp - cy_) * math.sin(t)) ** 2))[0])
                for t in np.radians(np.arange(0, 360, 5)))
sig_ear = 6 * float(F_ax[0]) * ear_arm / (2 * EAR_ROOT * (Z_R - EAR_Z0) ** 2)
sig_ear_cons = 6 * F_P1_cons * ear_arm / (2 * EAR_ROOT * (Z_R - EAR_Z0) ** 2)
tau_roof = F_gov / (math.pi * 5.5 * ROOF_T)
pre = 400.0
A_pil = math.pi * (PIL_R ** 2 - 1.7 ** 2)
sig_pil = (pre + F_gov) / A_pil
# flange wood screws (prying about the rim): 4 screws at WOOD_ANG62
M_sh = FL_LAT * (FL_Z1_62 - Z_BOT) / 1000
Fw_worst = 0.0
for th in np.radians(np.arange(0, 360, 5)):
    dl = FL_R62 - WOOD_R62 * np.cos(np.radians(WOOD_ANG62) - th)
    Fw = FV / 4 + M_sh * 1000 * dl / np.sum(dl ** 2)
    Fw_worst = max(Fw_worst, float(Fw.max()))
tau_head = Fw_worst / (math.pi * 9.5 * (FL_Z1 - FL_Z0 - v5.WOOD_CB_H))
# gate ring: a fox hanging on / biting the ring's lower edge
F_fox = 250.0
A_barb = 2 * math.pi * RING_GRV['r1'] * (RING_BARB['r1'] - RING['tongue'][1])
tau_barb = F_fox / (2 * math.pi * RING_GRV['r1'] * (RING_BARB['z'][1] - RING_BARB['z'][0]))
sig_peg = 50.0 / (math.pi * PEG['d'] ** 2 / 4)
web = CLR['dish_to_outlet_chamfer_mm'][0]
LOAD = {'case': f'as v6.1: 250 N down at the flat bottom (z {Z_BOT}) + 100 N sideways there + unit weight {W_UNIT:.1f} N + 20 N kibble column',
        'materials': LC61['materials'] | {'M3_A2_70_proof_N': 2200.0},
        'stack_screws_M3x40': {'positions': P_SCREWS, 'governing_case': 'vertical 282 N through cap -> thumb-turns -> box -> stack; the 100 N side load goes '
                                                         'cap spigot -> shell -> tabs -> bowl (v6.1 load path, unchanged)',
                               'vertical_shares_N': [round(float(v), 1) for v in F_ax], 'worst_screw_N': round(F_gov, 1),
                               'SF_insert_pullout': round(600.0 / F_gov, 1), 'SF_screw_proof': round(2200.0 / F_gov, 1),
                               'v611_reference': '121 N per tower-box screw (v6.1 calc, same assumption)',
                               'upper_bound_if_side_load_went_through_the_box': {'worst_screw_N': round(F_stack, 1), 'direction_deg': worst[1],
                                                                                 'SF_insert_pullout': round(600.0 / F_stack, 1), 'SF_screw_proof': round(2200.0 / F_stack, 1),
                                                                                 'note': 'only if the 0.25 mm spigot clearance never closed; v6.1/v6.1.1 would be worse '
                                                                                         'there (screws at r 17-19 instead of 23-29)'}},
        'box_ear_P1': {'force_N': round(float(F_ax[0]), 1), 'arm_mm': round(ear_arm, 1), 'root_width_mm': 2 * EAR_ROOT, 'thickness_mm': Z_R - EAR_Z0,
                       'bending_MPa': round(sig_ear, 1), 'SF_in_layer': round(S_XY / sig_ear, 1),
                       'upper_bound_force_N': round(F_P1_cons, 1), 'upper_bound_SF': round(S_XY / sig_ear_cons, 1),
                       'layer_direction': 'in layer (box printed roof-down, the ear is on the bed)'},
        'box_roof_P2_P3': {'head_punch_shear_MPa': round(tau_roof, 1), 'SF': round(TAU / tau_roof, 1), 'note': 'the 2.4 roof is clamped between the pillar foot and the head (compression), not bent'},
        'tower_pillars': {'preload_assumed_N': pre, 'stress_MPa': round(sig_pil, 1), 'SF_compression_50MPa': round(50.0 / sig_pil, 1),
                          'note': 'Ø9 pillars with Ø3.4 holes, braced by 4 mm webs to the tube over the full 30 mm: no buckling concern'},
        'flange_wood_screws': {'moment_at_shelf_Nm': round(M_sh, 1), 'worst_screw_N': round(Fw_worst), 'SF_pullout': round(900.0 / Fw_worst, 1),
                               'head_pull_through_shear_MPa': round(tau_head, 1), 'SF_head': round(TAU / tau_head, 1),
                               'v611': f"{LC61['flange_wood_screws']['worst_screw_N']} N, SF {LC61['flange_wood_screws']['SF_pullout']} (moment arm +8 mm, screws re-angled 80/150/225/295)"},
        'bayonet_lugs_hooks': {'unchanged': 'lower flange plate keeps the v6.1 hooks and skirt; lugs unchanged',
                               'bayonet_lugs_SF': LC61['bayonet_lugs']['SF'], 'flange_hooks_SF': LC61['flange_hooks']['SF']},
        'shell_tabs': {'unchanged': True, 'SF': LC61['shell_tabs']['SF']},
        'cap_thumbturns': {'unchanged_from_v611': V611['torques_forces']['thumbturn']['key_bearing_MPa_load_case_132N']},
        'gate_blade_column': {'p_design_kPa': HOLD['p_design_kPa'], 'bending_MPa': HOLD['blade_bending_MPa'], 'SF': HOLD['blade_SF']},
        'gate_ring_fox': {'pull_or_bite_N': F_fox, 'snap_barb_shear_MPa': round(tau_barb, 2), 'SF_barb': round(S_Z / tau_barb, 1),
                          'bite_through_3mm_ring_MPa': round(F_fox / (math.pi * 3.0 * (RING['ro'] - RING['ri'])), 1),
                          'SF_bite': round(TAU / (F_fox / (math.pi * 3.0 * (RING['ro'] - RING['ri']))), 1),
                          'peg_shear_MPa_at_50N_user_overload': round(sig_peg, 1), 'SF_peg': round(TAU / sig_peg, 1),
                          'note': 'the ring hangs on a 360 deg snap barb in the lower plate; the Ø3 peg only drives the rotation'},
        'fox_bite_outlet_rim': {'assumed_N': 250, 'canine_tip_mm': 3.0, 'v611_web_mm': CLR['v611_dish_to_outlet_chamfer_mm'][0],
                                'v611_punching_shear_MPa': round(250 / (math.pi * 3.0 * CLR['v611_dish_to_outlet_chamfer_mm'][0]), 1),
                                'v611_SF': round(TAU / (250 / (math.pi * 3.0 * CLR['v611_dish_to_outlet_chamfer_mm'][0])), 2),
                                'v62_web_mm': web, 'v62_punching_shear_MPa': round(250 / (math.pi * 3.0 * web), 1),
                                'v62_SF': round(TAU / (250 / (math.pi * 3.0 * web)), 2),
                                'fix': 'thumb-turn dishes Ø26 -> Ø24 (all three; the ridge still clears 3.9 at its ends): the web between dish A/B and the outlet '
                                       'chamfer grows 1.72 -> 2.72; v6.1 method (canine tip punching through the thinnest wall); keep 100 % infill within 8 mm of the outlet'}}
print(json.dumps(LOAD, indent=1, default=str))

# ---------------- grams ----------------
print('\n--- grams ---')
G62 = {}
QTY = {'labbro_pettine_v62': 4, 'canalina_base_v62': 2, 'canalina_coperchio_v62': 2}
for k, m in P.items():
    s_, e_ = v6.grams_est(m, RHO[k])
    qn = QTY.get(k, 1)
    G62[k] = {'qty': qn, 'volume_cm3': round(abs(m.volume) / 1000 * qn, 2), 'grams_solid': round(s_ * qn, 1), 'grams_print_est': round(e_ * qn, 1),
              'material': 'TPU 95A' if RHO[k] == TPU else 'PETG', 'watertight': bool(m.is_watertight)}
g611 = V611['grams']['v611_changed_parts']; g61 = V61['grams']['v61']
REPL = {'chiocciola_v62': [('chiocciola_v61', g61)], 'colonna_v62': [('colonna_v61', g61)], 'scatola_v62': [('scatola_v611', g611)],
        'fondello_v62': [('fondello_v611', g611)], 'flangia_piano_v62': [('flangia_piano_v611', g611)], 'passacavo_v62': [('passacavo_v61', g61)],
        'piastra_gate_v62': [('piastra_gate_v61', g61)], 'piastra_finestra_v62': [('piastra_finestra_v61', g61)],
        'labbro_pettine_v62': [('labbro_uscita_v61', g61), ('labbro_uscita_v61_b', g61), ('labbro_finestra_v61', g61), ('labbro_finestra_v61_b', g61)]}
old = sum(src[k]['grams_print_est'] for v in REPL.values() for k, src in v)
new_repl = sum(G62[k]['grams_print_est'] for k in REPL)
new_add = sum(G62[k]['grams_print_est'] for k in G62 if k not in REPL)
tot611 = V611['grams']['v611_total_print_est_g']
unit_add = sum(G62[k]['grams_print_est'] for k in ('flangia_alta_v62', 'saracinesca_v62', 'anello_saracinesca_v62'))
chan = sum(G62[k]['grams_print_est'] for k in ('canalina_base_v62', 'canalina_coperchio_v62', 'canalina_tappo_v62'))
GRAMS = {'method': V611['grams']['method'], 'v62_changed_and_new_parts': G62,
         'replaced_parts_v611_print_est_g': round(old, 1), 'their_v62_versions_g': round(new_repl, 1),
         'new_parts_g': round(new_add, 1), 'of_which_gate_g': round(unit_add, 1), 'of_which_cable_channel_2_sections_g': round(chan, 1),
         'v611_total_print_est_g': tot611, 'v62_total_print_est_g': round(tot611 - old + new_repl + new_add, 1),
         'delta_g': round(new_repl + new_add - old, 1), 'delta_pct': round(100 * (new_repl + new_add - old) / tot611, 1),
         'by_part_delta_g': {k: round(G62[k]['grams_print_est'] - sum(src[kk]['grams_print_est'] for kk, src in v), 1) for k, v in REPL.items()},
         'bought_changes': '-3 M3x12 -3 M3x10 +3 M3x40 +2 O-ring 3x1; wood 5x25 -> 5x35; +3 ST2.9x9.5; +4 wood 3.5x16 (channel); connector M8 IP67 pair'}
print(json.dumps({k: v for k, v in GRAMS.items() if k != 'v62_changed_and_new_parts'}, indent=1))

# ---------------- assembled-position files ----------------
ASM_NOT_WT = []


def save(name, m):
    p_ = ASM + name + '.stl'
    v6.clean(m).export(p_)
    if not trimesh.load(p_).is_watertight:
        ASM_NOT_WT.append(name)
    return p_


FILES = {k: OUT + k + '.stl' for k in P}
FILES['saracinesca_open_green'] = save('saracinesca_v62_aperta_verde', COLOUR['saracinesca_v62'][0][1])
FILES['saracinesca_open_orange'] = save('saracinesca_v62_aperta_arancio', COLOUR['saracinesca_v62'][1][1])
FILES['saracinesca_closed_green'] = save('saracinesca_v62_chiusa_verde', gate_pose(COLOUR['saracinesca_v62'][0][1], G_CLOSED))
FILES['saracinesca_closed_orange'] = save('saracinesca_v62_chiusa_arancio', gate_pose(COLOUR['saracinesca_v62'][1][1], G_CLOSED))
FILES['anello_closed'] = save('anello_saracinesca_v62_chiuso', RINGP[G_CLOSED])
FILES['colletto'] = save('colletto_v6_v62pos', COLLAR)
FILES['gsk_piano'] = save('guarnizione_piano_v5_v62pos', GSK_PIANO)
for k, m in LIPS.items():
    FILES[k] = save(k, m)
FILES['labbri_x4'] = save('labbro_pettine_v62_x4', U(list(LIPS.values())))
for c, b_ in COLOUR['piastra_gate_v62']:
    FILES[f'piastra_gate_{c}'] = save(f'piastra_gate_v62_{c}', b_)
for c, b_ in COLOUR['piastra_finestra_v62']:
    FILES[f'piastra_finestra_{c}'] = save(f'piastra_finestra_v62_{c}', b_)
for k, m in CH_PLACED.items():
    FILES[k] = save(k, m)
for k, m in list(BOUGHT.items()) + list(SCREWS.items()):
    FILES[k] = save('bought_' + k.replace('.', '_'), m)
CAP_BANDS = [('fondello_v62_fondo', -200, -99.0), ('fondello_v62_fianco', -99.0, -86.0), ('fondello_v62_bordo', -86.0, 0.0)]
for nm, z0, z1 in CAP_BANDS:
    FILES[nm] = save(nm, I(P['fondello_v62'], box(-200, 200, -200, 200, z0, z1)))
print('assembled-position copies written; not watertight on reload:', ASM_NOT_WT)

# ---------------- render check_v62.png ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle
ELEC = U([BOUGHT[k] for k in ('board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF')])
DRAW = [('shelf', SHELF, '#E8D9B5', '#8A6D3B', '///'),
        ('electronics / servo / connector / cable', U([ELEC, BOUGHT['servo'], BOUGHT['connector_m8_ip67'], BOUGHT['cable_12v_supply'], BOUGHT['cable_12v_unit']]), '#CCCCCC', '#666666', '...'),
        ('pod: guscio v611 / fondello v62', U([P611['guscio_v611'], P['fondello_v62']]), '#2a2b2e', 'k', None),
        ('flange plates v62 / colonna v62 / scatola v62', U([P['flangia_piano_v62'], P['flangia_alta_v62'], P['colonna_v62'], P['scatola_v62']]), '#4a4a4a', 'k', None),
        ('chiocciola v62', P['chiocciola_v62'], '#606060', 'k', None),
        ('food path green: scivolo, gate blade, plates', U([P611['scivolo_v611'], COLOUR['saracinesca_v62'][0][1], COLLAR]), '#2E9D4F', 'k', None),
        ('orange: gate ring + arm, thumb-turns, button', U([RINGP[G_OPEN], COLOUR['saracinesca_v62'][1][1], P611['pulsante_v611']] + list(TTS)), '#F07A1A', '#7A3A00', None),
        ('TPU yellow: grommet, skirt lip, comb lips', U([P['passacavo_v62'], P611['labbro_ombra_v611']] + list(LIPS.values())), '#F2C81E', '#7A6A00', None),
        ('steel: M3x40 stack screws, O-rings 3x1', U([SCREWS['m3x40_stack'], BOUGHT['oring_3x1']]), '#A8ADB3', '#555555', None),
        ('channel (black)', U(list(CH_PLACED.values())), '#3a3a3a', 'k', None)]


def draw(ax, origin, u_, v_, title, xlim, ylim, items=None):
    n_ = np.cross(u_, v_)
    T = np.eye(4); T[0, :3], T[1, :3], T[2, :3] = u_, v_, n_; T[:3, 3] = -T[:3, :3] @ np.asarray(origin, float)
    for nm, m, fc_, ec, hatch in (items or DRAW):
        sct = m.section(plane_origin=origin, plane_normal=n_)
        if sct is None:
            continue
        p2, _ = sct.to_2D(to_2D=T)
        for poly in p2.polygons_full:
            ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=fc_, ec=ec, lw=0.4, hatch=hatch, alpha=0.95 if hatch is None else 0.6))
            for h in poly.interiors:
                ax.add_patch(MPoly(np.array(h.coords), closed=True, fc='white', ec=ec, lw=0.4))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=0.25); ax.set_title(title, fontsize=10)


X_, Y_, Z_ = np.array([1., 0, 0]), np.array([0, 1., 0]), np.array([0, 0, 1.])
fig, axs = plt.subplots(2, 4, figsize=(34, 17), facecolor='white')
draw(axs[0, 0], [0, 0, 0], X_, Z_, f'{VER} section Y=0: two-plate flange, gate blade, ring; tower pillars', (-100, 100), (-110, 95))
dP = np.array(P_SCREWS[2]) - np.array(P_SCREWS[1]); dP = np.r_[dP / np.linalg.norm(dP), 0]
draw(axs[0, 1], [P_SCREWS[1][0], P_SCREWS[1][1], 0], dP, Z_, 'stack P2 -> P3: M3x40 through the roof (O-ring 3x1), pillar, bowl insert', (-6, 50), (-42, 12))
draw(axs[0, 2], [P_SCREWS[0][0], P_SCREWS[0][1], 0], np.array([0.0, 1.0, 0.0]), Z_, 'P1 (outside the box): ear, pillar, insert (YZ, y rel. to P1)', (-22, 22), (-42, 12))
draw(axs[0, 3], [0, 0, 0], Y_, Z_, 'cable tunnel (YZ at x=0): R15 bend, grommet, channel, connector', (-110, -55), (0, 85))
# gate plan view
ax = axs[1, 0]
for g, col_, lab in ((0.0, '#2E9D4F', 'blade OPEN'), (G_CLOSED, '#7fbf7f', 'blade CLOSED (113 deg)')):
    bp = blade2d(g)
    ax.add_patch(MPoly(np.array(bp.exterior.coords), closed=True, fc=col_, ec='k', lw=0.6, alpha=0.55, label=lab))
ax.add_patch(MPoly(np.array(PIE.exterior.coords), closed=True, fc='none', ec='#c00', lw=1.6, label='funnel pie opening'))
pk = pocket2d()
for gg in ([pk] if pk.geom_type == 'Polygon' else pk.geoms):
    ax.add_patch(MPoly(np.array(gg.exterior.coords), closed=True, fc='none', ec='#555', lw=0.8, ls='--'))
for a in WOOD_ANG62:
    ax.add_patch(Circle(polar(WOOD_R62, a), 2.6, fc='#888', ec='k'))
ax.add_patch(Circle((0, 0), FL_R62, fc='none', ec='k', lw=1.0)); ax.add_patch(Circle((0, 0), RING['ro'], fc='none', ec='#F07A1A', lw=2.0))
for g, ls in ((0.0, '-'), (G_CLOSED, ':')):
    wa = math.radians(WIN_ANG - g); ax.plot([RING['ri'] * math.cos(wa), (RING['ro'] + 6) * math.cos(wa)], [RING['ri'] * math.sin(wa), (RING['ro'] + 6) * math.sin(wa)], ls, c='#F07A1A', lw=3)
ba = math.radians(LATCH_A); ax.plot([78 * math.cos(ba)], [78 * math.sin(ba)], 'o', ms=10, mfc='#F07A1A', mec='k', label='release button (76.5 deg)')
ax.plot([0, 100 * math.cos(math.radians(CABLE_ANG))], [0, 100 * math.sin(math.radians(CABLE_ANG))], c='k', lw=2, label='cable / channel (270 deg)')
ax.set_xlim(-100, 100); ax.set_ylim(-100, 100); ax.set_aspect('equal'); ax.legend(fontsize=8, loc='lower left'); ax.grid(alpha=0.25)
ax.set_title('gate plan (z 71.8): blade open / closed, ring window (solid open, dotted closed), screws', fontsize=10)
ax = axs[1, 1]
gg_ = [d['g_deg'] for d in INTERLOCK]
ax.plot([c[0] for c in COVER], [100 * c[1] for c in COVER], c='#2E9D4F', lw=2, label='opening covered by the blade (%)')
ax.step(gg_, [100 if d['any_fingertip_reaches'] or d['thumb_reaches_button'] else 0 for d in INTERLOCK], where='mid', c='#F07A1A', lw=2, label='button reachable (Ø10 fingertip, any offset <= 4)')
ax.axvline(g_full, c='k', ls='--', lw=1); ax.text(g_full + 0.5, 50, f'fully covered from {g_full:.0f} deg', fontsize=9)
if g_reach_first is not None:
    ax.axvline(g_reach_first, c='#F07A1A', ls=':', lw=1); ax.text(g_reach_first + 0.5, 20, f'button first reachable {g_reach_first:.0f} deg', fontsize=9)
ax.set_xlabel('gate closing angle g (deg)'); ax.set_ylim(-5, 105); ax.legend(fontsize=9, loc='center left'); ax.grid(alpha=0.25)
ax.set_title('interlock proof: the button is reachable only after the opening is 100 % covered', fontsize=10)
draw(axs[1, 2], [0, -FL_R62 - 80, 0], X_, Z_, 'cable channel cross-section (snap cover, base screwed to the shelf, Ø5 cable)', (-14, 14), (64, 82),
     items=[DRAW[0], ('channel', U(list(CH_PLACED.values())), '#3a3a3a', 'k', None), ('cable', BOUGHT['cable_12v_supply'], '#bbbbbb', '#444', '...')])
draw(axs[1, 3], [0, 0, -103.0], X_, Y_, 'cap bottom (z -103): Ø24 dishes, web to the outlet chamfer 2.72', (-75, 0), (-5, 60),
     items=[('fondello_v62', P['fondello_v62'], '#2a2b2e', 'k', None), ('thumb-turns', U(list(TTS)), '#F07A1A', '#7A3A00', None)])
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
axs[0, 0].legend(handles, [d[0] for d in DRAW], loc='upper right', fontsize=8)
plt.tight_layout()
plt.savefig(OUT + 'check_v62.png', dpi=60)
plt.close(fig)
print('check_v62.png written')

# ---------------- drilling template (SVG + PDF, A4, 1:1, view from below) ----------------
# ---------------- drilling template (SVG + PDF, A4 portrait, 1:1, VIEW FROM BELOW) ----------------
A4W, A4H = 210.0, 297.0
CXp, CYp = 105.0, 150.0                                    # unit axis on the sheet; view from below turned 180 deg so FRONT is at the top
                                                           # (a person at the front looking up reads it upright): sheet = (CX - x, CY - y)
TPL_ITEMS = []                                             # ('circle', cx, cy, r, style) / ('line', x0, y0, x1, y1, style) / ('text', x, y, s, size, anchor, weight) / ('poly', pts, style)
S_MAIN = dict(stroke='#000', w=0.35, dash=None, fill='none')


def tp(x, y):
    return CXp - x, CYp - y


def T_circle(x, y, r, **st):
    TPL_ITEMS.append(('circle', *tp(x, y), r, dict(S_MAIN, **st)))


def T_line(x0, y0, x1, y1, **st):
    TPL_ITEMS.append(('line', *tp(x0, y0), *tp(x1, y1), dict(S_MAIN, **st)))


def T_text(x, y, s, size=3.2, anchor='middle', weight='normal', sheet=False, colour='#000'):
    X, Y = (x, y) if sheet else tp(x, y)
    TPL_ITEMS.append(('text', X, Y, s, size, anchor, weight, colour))


def T_cross(x, y, L=5.0, **st):
    T_line(x - L, y, x + L, y, **st); T_line(x, y - L, x, y + L, **st)


def T_poly(pts, **st):
    TPL_ITEMS.append(('poly', [tp(*p_) for p_ in pts], dict(S_MAIN, **st)))


# frame + title (sheet coordinates)
TPL_ITEMS.append(('rect', 6.0, 6.0, A4W - 12.0, A4H - 12.0, dict(S_MAIN, w=0.2, stroke='#888')))
T_text(105, 14.0, 'Kibble Dispenser Outdoor v6.2 - drilling template 1:1', 5.0, weight='bold', sheet=True)
T_text(105, 19.5, 'VIEW FROM BELOW: tape it under the shelf with the PRINTED SIDE FACING YOU, arrow towards the room side', 3.0, sheet=True)
# cable channel strip (to the back edge of the shelf)
a = math.radians(CABLE_ANG)
r0c, r1c = FL_R62 - CH['insert'], 128.0
T_poly([(-CH['w'] / 2, -r0c), (CH['w'] / 2, -r0c), (CH['w'] / 2, -r1c + 8), (-CH['w'] / 2, -r1c + 8)], dash='2,1.2', stroke='#555', w=0.3)
T_cross(0.0, -(r0c + 25.0), 2.5, stroke='#555'); T_circle(0.0, -(r0c + 25.0), 1.25, stroke='#555')
T_text(-13.0, -(r0c + 26.0), 'channel screw', 2.4, anchor='start', colour='#555')
T_text(-13.0, -(r0c + 36.0), 'CABLE CHANNEL -> BACK EDGE', 2.8, anchor='start', weight='bold', colour='#555')
# keep-clear zone for the hand on the gate ring
T_circle(0.0, 0.0, 100.0, dash='3,2', stroke='#E06A00', w=0.4)
T_text(10.0, 42.0, 'dashed orange circle r 100: keep clear, the gate ring is turned by hand', 2.5, anchor='start', sheet=True, colour='#E06A00')
# flange outline, ring
T_circle(0.0, 0.0, FL_R62, w=0.5)
T_circle(0.0, 0.0, RING['ro'], dash='1,1', stroke='#E06A00', w=0.3)
T_text(-52.0, 62.0, f'flange outline Ø{2*FL_R62:.0f}', 2.6)
# flange centre (unit axis)
T_cross(0.0, 0.0, 4.0, w=0.25); T_text(-6.0, -4.0, 'flange centre', 2.4, anchor='start')
# hole saw Ø76
hx, hy = v6.HOLE_C
T_circle(hx, hy, 38.0, dash='4,1.5', w=0.5)
T_cross(hx, hy, 8.0, w=0.4); T_circle(hx, hy, 3.0, w=0.3)
T_text(hx, hy + 11.0, 'HOLE SAW Ø76', 3.4, weight='bold'); T_text(hx, hy + 7.0, 'centre: drill the Ø6 pilot here', 2.6)
T_line(0, 0, hx, hy, w=0.2, dash='1,1'); T_text(hx / 2, -4.0, f'{hx:.0f} mm', 2.4)
# wood screws
for k, aw in enumerate(WOOD_ANG62):
    x, y = polar(WOOD_R62, aw)
    T_cross(x, y, 4.0, w=0.35); T_circle(x, y, 1.5, w=0.3)
    ox, oy = polar(WOOD_R62 - 10.0, aw)
    T_text(ox, oy + 1.0, f'S{k + 1}', 3.0, weight='bold')
T_text(-20.0, 54.0, 'S1-S4: wood screws 5x35 pan head', 2.5); T_text(-20.0, 50.0, '(5x30 for an 18 mm shelf), pre-drill Ø3 x 25', 2.5)
# release button / front
bx_, by_ = polar(80.0, LATCH_A)
T_circle(bx_, by_, 3.0, stroke='#E06A00', w=0.4); T_text(bx_ + 5.0, by_ - 1.0, 'release button + gate window', 2.4, anchor='end', colour='#E06A00')
# outlet below (for the pet bowl)
T_circle(CH_X, 0.0, 24.5, dash='0.8,0.8', stroke='#2E9D4F', w=0.3); T_text(CH_X, 1.0, 'outlet (182 mm below)', 2.4, colour='#2E9D4F')
# orientation arrows (sheet coordinates): FRONT = room side towards the bottom of the sheet, BACK = channel side at the top
T_text(105, 27.0, 'FRONT / ROOM SIDE (you stand here; release button + gate window face you)', 3.0, weight='bold', sheet=True)
TPL_ITEMS.append(('poly', [(105.0, 30.5), (101.0, 36.5), (103.5, 36.5), (103.5, 45.0), (106.5, 45.0), (106.5, 36.5), (109.0, 36.5)], dict(S_MAIN, fill='#000')))
# scale bar 50 mm
sx0, sy0 = 18.0, 276.0
TPL_ITEMS.append(('rect', sx0, sy0, 50.0, 3.0, dict(S_MAIN, w=0.3)))
for k in range(6):
    TPL_ITEMS.append(('rect', sx0 + 10 * k, sy0, 10.0 if k < 5 else 0.0, 3.0, dict(S_MAIN, w=0.3, fill='#000' if k % 2 == 0 and k < 5 else 'none')))
    T_text(sx0 + 10 * k, sy0 + 6.5, f'{10 * k}', 2.4, sheet=True)
T_text(sx0 + 25, sy0 - 1.5, 'scale check: this bar must measure exactly 50 mm', 2.6, sheet=True)
T_text(160.0, 280.5, 'print at 100 % / actual size (no fit to page)', 2.6, sheet=True)
T_text(160.0, 285.0, 'A4 portrait, 1:1, all dimensions in mm', 2.4, sheet=True)


def _svg_style(st):
    s_ = f'stroke="{st["stroke"]}" stroke-width="{st["w"]}" fill="{st["fill"]}"'
    if st.get('dash'):
        s_ += f' stroke-dasharray="{st["dash"]}"'
    return s_


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4W}mm" height="{A4H}mm" viewBox="0 0 {A4W} {A4H}">',
       f'<rect x="0" y="0" width="{A4W}" height="{A4H}" fill="#fff"/>']
for it in TPL_ITEMS:
    if it[0] == 'circle':
        svg.append(f'<circle cx="{it[1]:.3f}" cy="{it[2]:.3f}" r="{it[3]:.3f}" {_svg_style(it[4])}/>')
    elif it[0] == 'line':
        svg.append(f'<line x1="{it[1]:.3f}" y1="{it[2]:.3f}" x2="{it[3]:.3f}" y2="{it[4]:.3f}" {_svg_style(it[5])}/>')
    elif it[0] == 'rect':
        svg.append(f'<rect x="{it[1]:.3f}" y="{it[2]:.3f}" width="{it[3]:.3f}" height="{it[4]:.3f}" {_svg_style(it[5])}/>')
    elif it[0] == 'poly':
        svg.append(f'<polygon points="{" ".join(f"{x:.3f},{y:.3f}" for x, y in it[1])}" {_svg_style(it[2])}/>')
    elif it[0] == 'text':
        esc = it[3].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg.append(f'<text x="{it[1]:.3f}" y="{it[2]:.3f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{it[4]}" text-anchor="{it[5]}" '
                   f'font-weight="{it[6]}" fill="{it[7]}">{esc}</text>')
svg.append('</svg>')
open(TPL + 'dima_foratura_v62.svg', 'w').write('\n'.join(svg))
# PDF at true scale with matplotlib (figure = A4 in inches, axes = whole page in mm)
from matplotlib.patches import Circle as MCircle, Rectangle as MRect, Polygon as MPolyT
figT = plt.figure(figsize=(A4W / 25.4, A4H / 25.4))
axT = figT.add_axes([0, 0, 1, 1]); axT.set_xlim(0, A4W); axT.set_ylim(A4H, 0); axT.axis('off')
mm2pt = 72.0 / 25.4


def _ls(st):
    return (0, tuple(float(v) * mm2pt / max(st['w'] * mm2pt, 1e-3) for v in st['dash'].split(','))) if st.get('dash') else 'solid'


for it in TPL_ITEMS:
    if it[0] == 'circle':
        st = it[4]; axT.add_patch(MCircle((it[1], it[2]), it[3], fill=False, ec=st['stroke'], lw=st['w'] * mm2pt, ls=_ls(st)))
    elif it[0] == 'line':
        st = it[5]; axT.plot([it[1], it[3]], [it[2], it[4]], c=st['stroke'], lw=st['w'] * mm2pt, ls=_ls(st))
    elif it[0] == 'rect':
        st = it[5]; axT.add_patch(MRect((it[1], it[2]), it[3], it[4], fill=st['fill'] != 'none', fc=st['fill'] if st['fill'] != 'none' else 'none', ec=st['stroke'], lw=st['w'] * mm2pt))
    elif it[0] == 'poly':
        st = it[2]; axT.add_patch(MPolyT(it[1], closed=True, fill=st['fill'] != 'none', fc=st['fill'] if st['fill'] != 'none' else 'none', ec=st['stroke'], lw=st['w'] * mm2pt, ls=_ls(st)))
    elif it[0] == 'text':
        axT.text(it[1], it[2], it[3], fontsize=it[4] * mm2pt * 1.0, ha={'middle': 'center', 'start': 'left', 'end': 'right'}[it[5]], va='baseline',
                 fontweight=it[6], color=it[7], family='DejaVu Sans')
figT.savefig(TPL + 'dima_foratura_v62.pdf')
figT.savefig(SCRATCH + 'dima_preview.png', dpi=110)
plt.close(figT)
# verify the PDF page size (points) = A4
import re as _re
_pdf = open(TPL + 'dima_foratura_v62.pdf', 'rb').read()
_mb = _re.search(rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]', _pdf)
TEMPLATE = {'svg': TPL + 'dima_foratura_v62.svg', 'pdf': TPL + 'dima_foratura_v62.pdf',
            'pdf_mediabox_pt': [float(v) for v in _mb.groups()] if _mb else None, 'a4_pt': [595.28, 841.89],
            'contents': ['flange outline Ø180 + ring', 'hole-saw Ø76 centre (27 mm from the flange centre) with pilot mark', '4 wood-screw positions S1..S4 (r 75.5 at 80/150/225/295 deg)',
                         'keep-clear circle r 100 for the hand on the gate ring', 'cable channel strip to the back edge + first channel screw',
                         'FRONT arrow (room side: release button + window)', 'outlet position for the pet bowl', '50 mm scale bar'],
            'view': 'from below (printed side facing the person below, back of the sheet against the shelf), FRONT at the top of the sheet: not mirrored'}
print('template written', TEMPLATE['pdf_mediabox_pt'])

# ---------------- v62.json ----------------
SCREW_TABLE = {k: {'verdict': v['verdict'], 'straight_key_reaches_head': v['shaft_clear'], 'key_length_min_mm': v['key_length_min_mm'],
                   'first_obstacle': v['first_obstacle']} for k, v in TA.items()}
V611_TA = {k: {'verdict': v['verdict'], 'first_obstacle': v['first_obstacle'], 'key_length_min_mm': v['key_length_min_mm']}
           for k, v in TA_V611.items() if not k.startswith('_')}
v62doc = {
    'version': VER, 'base': 'v6.1.1 (v611.json): everything not listed here is unchanged',
    'frame': 'as v6.1.1: Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED bayonet pose, gate OPEN; the shelf underside moves to z 78.1 (+8)',
    'changes': {
        '1_screw_access': {
            'v611_defects_measured': {'tower_lobe_screw_spacing_235_240_mm': TA_V611['_facts']['min_dist_top_lobe_screw_to_bottom_lobe_screw_mm'],
                                      'tool_access_v611_steps_order': V611_TA,
                                      'why_relocate': 'with the tower top screws at r 19 / 0-125-240 deg, no box-screw triangle reachable from below surrounds the '
                                                      'axis: inside the box only the servo|board corridor and the -Y bay are free; outside, the -X side is blocked '
                                                      'by the chute and the 125/240 access bores; the v6.1 factory order (tower onto box, then onto bowl) is '
                                                      'impossible because the box roof covers the tower-top screws'},
            'v62_solution': 'one set of 3x M3x40 DIN912 A2 clamps box + tower + bowl, driven from below after the shell; P1 outside the box through a '
                            '5 mm ear, P2 (-Y bay) and P3 (servo|board corridor) through the 2.4 roof with an O-ring 3x1 under the head; the tower has 3 '
                            'pillars + webs (no lobes); the bowl tower inserts move to P1..P3 (8.5 deep, old holes filled); 6 screws -> 3',
            'positions_xy': P_SCREWS, 'build_order': [
                '1 latch into the bowl (as v6.1.1)', '2 tower module (colonna_v62 + shaft + O-rings) set on the bowl base, collar in the base hole (no screws yet)',
                '3 chute: 2x M3x10 from below', '4 shell (button + O-ring fitted): 3x M3x12 from below - the box is not in yet, so the A/B cups no longer block 120/240 deg',
                '5 electronics box (cap off) lowered into the shell onto the tower: shaft into the hub (rib to the latch), pillars on the ear / roof holes; '
                '3x M3x40 from below (P2, P3 with an O-ring 3x1 under the head)', '6 cap on (thumb-turns)', '7 rim seal, comb lips, plates, disc from the top'],
            'tool_access_v62': SCREW_TABLE,
            'tool_model': 'straight key cylinder along the screw axis from the head face (2.5 mm hex: Ø3.2; PZ2 for wood screws: Ø6.5) must reach the head without '
                          'touching anything present at that step; hand = Ø28 (Ø32 for wood) cylinder beyond the key length; key_length_min = shortest straight '
                          'key/screwdriver with the hand free; verdict OK <= 60 mm, "OK long key" <= 100 mm (hex screwdriver 2.5 x 100)'},
        '2_gate_and_interlock': {
            'parts': {'flangia_piano_v62': 'lower plate = v6.1.1 bayonet plate (hooks, skirt, pins, rim-lip and skirt-lip grooves) at r 90, pie opening only, '
                                           'Ø4 pivot pin, ring groove with a 360 deg snap undercut, peg slot over the arm sweep, landing drain slot, lower half of the cable tunnel',
                      'flangia_alta_v62': 'NEW upper plate 70.1..78.1: blade pocket (sector -62.8..169.8 deg, r 70, 3.4 deep), arm channel, funnel (pie prism to 74.1 + the v6 '
                                          'morph raised 8 mm), shelf-gasket groove, collar pins, cable tunnel upper half + channel port, 3 countersunk join screws from the shelf face',
                      'saracinesca_v62': 'NEW PETG blade: green 119 deg sector r 69.5 x 3.0 (single-bevel knife leading edge) + orange arm with the peg hole',
                      'anello_saracinesca_v62': 'NEW orange ring r 85..88 x z 28.5..65.9 round the pod top, tongue + 360 deg snap barb in the lower plate, Ø3 peg into the '
                                                'blade arm, ONE Ø28 window at the button height'},
            'kinematics': {'residual_open_at_full_stroke_mm2_and_gap_d': [round(v, 2) for v in RESID_CLOSED],
                           'kibble_tight_rule': f'residual open area <= {RESID_OK} mm2 and no gap wider than 1.0 mm (the 0.15 mm pivot clearance ring)',
                           'pie_opening_half_angle_deg': OPEN_HALF, 'blade_lead_open_deg': LEAD_OPEN, 'stroke_deg': STROKE, 'fully_covered_from_deg': g_full,
                           'window_gate_frame_deg': WIN_ANG, 'closing_direction': 'anticlockwise seen from below (same hand motion as the unit removal twist)',
                           'stops': 'the arm hits the ends of its channel at 0 and 113 deg'},
            'open_passage': PASSAGE, 'closed_hold': HOLD,
            'interlock': {'logic': 'the ring covers the button except through one window that lines up with it only at the end of the closing stroke; '
                                   'the unit can only be unlatched by pressing that button',
                          'strict': INTERLOCK_OK, 'button_first_reachable_deg': g_reach_first, 'opening_fully_covered_from_deg': g_full,
                          'probes': [p_[0] for p_ in PROBES], 'table': INTERLOCK,
                          'no_unit_hung': 'NOT provided: blocking the gate when no unit is hung needs a spring or a gravity latch lifted by the unit; '
                                          'with the unit off, the ring can still be turned open by hand (a label on the ring says: close before removing, '
                                          'open only with the unit hung)'},
            'gate_sweep_mm3': {'columns': ['g', 'blade|flange', 'ring|flange', 'gate|unit (locked)', 'blade|ring'], 'rows': GATE_SWEEP},
            'printing': {'saracinesca_v62': 'flat, bottom face on the bed (the bevel is on the top); green blade + orange arm (2 colours, like the disc)',
                         'anello_saracinesca_v62': 'standing on its bottom edge, tongue and peg up; window Ø28 is a vertical hole (bridges 28 mm at the top: use the '
                                                   '0.8 chamfer side up or a light support); orange PETG; no other supports',
                         'flangia_alta_v62': 'shelf face on the bed: pocket, tunnel and port open upward, no supports',
                         'flangia_piano_v62': 'as v6.1.1 (shelf-side face on the bed); the ring groove undercut is a 0.6 internal ledge at the groove bottom'}},
        '3_cable': {
            'removed': 'Ø10 shelf hole and passacavo_v61 (a connector could not pass and the container stood on it)',
            'path': 'box gland -> unit pigtail up the -Y side of the pod -> M8 IP67 inline connector hanging from the supply cable in the pod-top annulus '
                    '(r 69.5, z 4..47) -> supply cable up at r 74 into the flange tunnel (R 15 bend, TPU grommet passacavo_v62 at the pod side) -> channel '
                    'port in the upper plate rim at 270 deg -> snap-in channel under the shelf to the shelf edge -> end cap, cable down (drip loop)',
            'connector': 'M8 A-coded 4-pin IP67 inline pair (male on the unit pigtail, female on the supply cable), pins 1+2 = +12 V, 3+4 = GND in parallel; '
                         'cable PUR 4x0.34 Ø5; when the unit is twisted off and lowered 8 cm the connector hangs free in the gap under the flange: unscrew it',
            'channel': {'profile_mm': '20 x 8 closed against the wood: base 17.2 wide screwed with 2x 3.5x16 countersunk per section (heads inside), cover snaps '
                                      'over the base barbs, R2.5 rounded outer edges, no gap at the wood (0.2)', 'sections': '150 mm, cut the last one to length',
                        'end_cap': 'tongue into the channel, cable exits downward through a rounded Ø6.2 hole', 'colour': 'black PETG',
                        'scene': f'2 sections (150 + {L2:.0f}) + end cap from the flange rim at 270 deg to the shelf edge y -360'},
            'exposure': 'no cable below the pod: it is inside the pod, the flange and the channel only'},
        '4_comb_lips': {'design': 'labbro_pettine_v62 x4: one part, length %.1f, 5 slits 0.7 symmetric about the middle -> reversible end for end; placed in all 4 grooves '
                                  'by proper rotations only (gate lips flap up, window lips flap down)' % LIP_L,
                        'lip_flap_height_mm_gate_and_window': EXTRA['lip_h'],
                        'grooves': 'the two short (skewed) edges 23.6/23.8 get their grooves lengthened inward to the common length; the long edges 26.2/26.4 unchanged '
                                   '(+0.15)', 'plates': 'piastra_gate_v62, piastra_finestra_v62 (green bands relabelled v6.2)'},
        '7_fox_bite': LOAD['fox_bite_outlet_rim'],
        '8_firmware_note': 'At power-on the disc must NOT dispense: both rest positions (0 and 180 deg) are closed (rotary airlock). The firmware must store the '
                           'last commanded rest position in non-volatile memory (NVS / flash, written only when it changes) and command exactly that position at '
                           'boot, with the servo PWM enabled only after the stored value has been loaded; a cold start without a stored value goes to 0 deg. '
                           'This complements the existing contract (boots OFF, one cycle on a commanded ON, one per press).'},
    'kit_split': {
        'pre_assembled_unit': ['chiocciola_v62 + linguetta_sicura + guarnizione_baionetta_v61', 'colonna_v62 drive module (albero_v6, 2x O-ring 9x2, O-ring 24x2, greased)',
                               'scivolo_v611 + labbro_scivolo_v611', 'scatola_v62 electronics box (servo, mozzo, board, gland, vent, M8 pigtail, 2x O-ring 3x1)',
                               '3x M3x40 stack screws', 'guscio_v611 + pulsante_v611 + O-rings', 'fondello_v62 + 3 thumb-turns + keys + O-rings + cap lip',
                               'piastra_gate_v62, disco_v61, piastra_finestra_v62, 4x labbro_pettine_v62'],
        'separate_flange_assembly': ['flangia_piano_v62 + labbro_ombra_v611 (pressed in)', 'saracinesca_v62', 'anello_saracinesca_v62 (snapped in)', 'flangia_alta_v62',
                                     '3x ST2.9x9.5 join screws (shipped joined)', 'passacavo_v62 (on the supply cable)', 'guarnizione_piano_v5', 'colletto_v6'],
        'separate': ['cable channel: 2x canalina_base_v62, 2x canalina_coperchio_v62, 1x canalina_tappo_v62, 4x wood screw 3.5x16 countersunk',
                     'supply cable with the M8 female (or with the PSU)', '4x wood screw 5x35 pan head (5x30 for an 18 mm shelf)', 'drilling template (template_v62)'],
        'diy_build_possible': 'yes: the order in 1_screw_access.build_order passes the tool-access check for every screw (straight key, hand free)'},
    'hardware_delta_vs_v611': [
        {'qty': -3, 'item': 'M3x12 DIN912 (tower -> bowl)'}, {'qty': -3, 'item': 'M3x10 DIN912 (tower -> box)'},
        {'qty': 3, 'item': 'M3x40 DIN912 A2', 'use': 'box + tower + bowl stack, from below'},
        {'qty': 2, 'item': 'O-ring NBR70 3x1', 'use': 'under the P2/P3 heads in the roof countersinks (dry box stays sealed)'},
        {'qty': -3, 'item': 'M3 heat-set insert (box plateau)'}, {'qty': 0, 'item': 'M3 heat-set inserts in the bowl: same 8, three moved to P1..P3'},
        {'qty': 4, 'item': 'wood screw 5x35 pan head instead of 5x25 (flange is 8 mm thicker)'},
        {'qty': 3, 'item': 'ST2.9x9.5 DIN 7982 countersunk', 'use': 'join the two flange plates from the shelf face'},
        {'qty': 4, 'item': 'wood screw 3.5x16 countersunk', 'use': 'cable channel bases'},
        {'qty': 1, 'item': 'M8 A-coded 4-pin IP67 inline pair + PUR 4x0.34 Ø5 cable', 'use': 'replaces the generic inline connector + Ø6 cable'},
        {'qty': -1, 'item': 'TPU grommet passacavo_v61 / Ø10 shelf hole'}],
    'shelf': {'underside_z': FL_Z1_62, 'hole_saw_d': 76.0, 'hole_centre_xy': list(v6.HOLE_C), 'cable_hole': None,
              'wood_screws_xy': [[round(v, 2) for v in polar(WOOD_R62, a)] for a in WOOD_ANG62], 'flange_outline_r': FL_R62,
              'unit_height_below_shelf_mm': round(FL_Z1_62 - Z_BOT, 1), 'v611_unit_height_below_shelf_mm': round(FL_Z1 - Z_BOT, 1),
              'template': {k_: v_ for k_, v_ in TEMPLATE.items() if k_ not in ('svg', 'pdf')} | {'svg': 'template_v62/dima_foratura_v62.svg', 'pdf': 'template_v62/dima_foratura_v62.pdf'}},
    'changed_parts': {k: v for k, v in {
        'chiocciola_v62': 'bowl: tower inserts moved to P1..P3 (8.5 deep), old r 19 holes filled',
        'colonna_v62': 'tower: 3 Ø9 pillars + 4 mm webs + top arms instead of top/bottom lobes; tube, bushing, O-ring grooves unchanged',
        'scatola_v62': 'box: no plateau inserts; 5 mm ear at P1; Ø3.4 + 90 deg countersink (O-ring 3x1) at P2/P3; vent at (12, -30)',
        'fondello_v62': 'cap: thumb-turn dishes Ø24 (fox-bite web 2.72)',
        'flangia_piano_v62': 'lower flange plate (see 2_gate_and_interlock)', 'piastra_gate_v62': 'outlet plate: lip grooves for the common lip',
        'piastra_finestra_v62': 'window plate: lip grooves for the common lip'}.items()},
    'new_parts': ['flangia_alta_v62', 'saracinesca_v62', 'anello_saracinesca_v62', 'passacavo_v62', 'labbro_pettine_v62', 'canalina_base_v62',
                  'canalina_coperchio_v62', 'canalina_tappo_v62'],
    'reused_unchanged': ['guscio_v611', 'pulsante_v611', 'labbro_ombra_v611', 'scivolo_v611', 'labbro_scivolo_v611', 'nottolino_v611', 'disco_v61',
                         'guarnizione_baionetta_v61', 'guarnizione_fondello_v61', 'colletto_v6 (8 mm higher)', 'guarnizione_piano_v5 (8 mm higher)',
                         'linguetta_sicura', 'albero_v6', 'mozzo_v6'],
    'checks': {'watertight_built': {k: bool(m.is_watertight) for k, m in P.items()}, 'watertight_exported_stl_reload': EXPORT_WT,
               'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
               'stack_screw_vs_drilled_parts_mm3': SCREW_HOLE,
               'designed_contacts_mm3': {k: {'overlap_mm3': v, 'role': SOFT[frozenset(k.split('|'))]} for k, v in soft.items()},
               'seal_continuity': CONT, 'line_of_sight': LOS,
               'bayonet': {'removal_sweep_with_gate_closed_angle_dz_mm3': SWEEP, 'max_mm3': BAY_MAX, 'unit_at_insertion_vs_flange_and_gate_mm3': BAY_INS,
                           'pressed_button_vs_ring_at_full_stroke_mm3': BTN_THROUGH_WINDOW},
               'gate_open_passage': PASSAGE, 'gate_hold': HOLD, 'interlock_strict': INTERLOCK_OK, 'tool_access': SCREW_TABLE,
               'clearances_mm': CLR, 'print_downfacing_flatter_45_mm2': OVH},
    'load_case': LOAD, 'grams': GRAMS,
    'print': {'chiocciola_v62': 'as v6.1 (flat base on the bed)', 'colonna_v62': 'upright, flange on the bed; pillars and webs vertical; top arms carried by 45 deg chamfers',
              'scatola_v62': 'as v6.1.1 (roof on the bed): the ear prints on the bed; 100 % infill; countersinks face up', 'fondello_v62': 'as v6.1.1',
              'flangia_piano_v62': 'shelf-side face on the bed (pivot pin grows up)', 'flangia_alta_v62': 'shelf face on the bed',
              'saracinesca_v62': 'flat on the bed, 2 colours', 'anello_saracinesca_v62': 'on its bottom edge', 'passacavo_v62': 'TPU 95A, lip on the bed',
              'labbro_pettine_v62': 'print 4, TPU 95A, anchor on the bed', 'piastra_gate_v62': 'as v6.1', 'piastra_finestra_v62': 'as v6.1 (flipped)',
              'canalina_base_v62': 'flat, wood face on the bed', 'canalina_coperchio_v62': 'open side up (bottom wall on the bed)', 'canalina_tappo_v62': 'on its side'},
    'open_risks': ['P3 head sits 0.375 mm from the cradle and the board in the corridor: check the first print (a low-head DIN 7984 would give 1 mm)',
                   'stack screws: governing vertical case SF %.1f on the inserts; if the side load ever went through the box instead of the cap spigot the worst '
                   'insert would be at SF %.1f (upper bound, also exceeded by v6.1.1)' % (600.0 / F_gov, 600.0 / F_stack),
                   'M3x40 pillars: printed PETG under screw preload creeps; tighten 0.4 N m and re-check after a week',
                   'gate pocket gaps 0.2: insects could walk the pocket; same class as the 0.7 comb slits (kibble path open by design)',
                   'ring window Ø28 is a 28 mm bridge when printed on edge: chamfer side up or a small support',
                   'cable R 15 bend in the flange is 3 x OD for a Ø5 PUR cable: fixed install only; a stiffer PVC cable needs R 20 (flange +5 mm)',
                   'unit height below the shelf +8 mm (182.1)'],
    'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] for k in P} |
             {'assembled_position_copies': 'v62_asm/*.stl', 'check': 'check_v62.png', 'viewer': 'v62_viewer.json', 'template': 'template_v62/'}}
_dflt = lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
json.dump(v62doc, open(OUT + 'v62.json', 'w'), indent=1, default=_dflt)
print('v62.json written')

# ---------------- v62_viewer.json (base: v611_viewer_hq.json, full-resolution files) ----------------
VH = json.load(open(OUT + 'v611_viewer.json'))


def _full(q):
    q = dict(q)
    q['file'] = q.pop('source_file', q['file'])
    q.pop('lod_note', None)
    q.pop('lod_faces', None)
    return q


def _vp(id_, name, file_, color, group, material, qty, bought, explode, rotates=False, opacity=1.0):
    return {'id': id_, 'name': name, 'file': file_, 'color': color, 'opacity': opacity, 'group': group, 'material': material, 'qty': qty,
            'bought': bought, 'explode': explode, 'rotates': rotates}


GREEN, ORANGE, BLACK, YELLOW, STEEL = '#2e9d4f', '#f07a1a', '#2a2b2e', '#f2c81e', '#a8adb3'
GATE_PARTS = lambda state: [
    _vp('saracinesca_lama', f'Saracinesca: lama ({state})', FILES['saracinesca_open_green' if state == 'aperta' else 'saracinesca_closed_green'], GREEN, 'dosatore', 'PETG verde', 1, False, [0, 0, 152]),
    _vp('saracinesca_braccio', f'Saracinesca: braccio ({state})', FILES['saracinesca_open_orange' if state == 'aperta' else 'saracinesca_closed_orange'], ORANGE, 'struttura', 'PETG arancio', 1, False, [0, 0, 152]),
    _vp('anello_saracinesca', f'Anello saracinesca con finestra ({state})', OUT + 'anello_saracinesca_v62.stl' if state == 'aperta' else FILES['anello_closed'], ORANGE,
        'struttura', 'PETG arancio', 1, False, [0, 0, 108])]
VP = []
for p_ in VH['parts']:
    q = _full(p_)
    i = q['id']
    if i == 'guarnizione_piano':
        q.update(file=FILES['gsk_piano'], explode=[0, 0, 192])
    elif i == 'colletto_v6':
        q.update(file=FILES['colletto'], explode=[0, 0, 180])
    elif i == 'flangia_piano_v611':
        VP.append(_vp('flangia_piano_v62', 'Flangia piano inferiore (baionetta)', OUT + 'flangia_piano_v62.stl', BLACK, 'struttura', 'PETG nero', 1, False, [0, 0, 138]))
        VP.extend(GATE_PARTS('aperta'))
        VP.append(_vp('flangia_alta_v62', 'Flangia piano superiore (sede saracinesca)', OUT + 'flangia_alta_v62.stl', BLACK, 'struttura', 'PETG nero', 1, False, [0, 0, 165]))
        VP.append(_vp('viti_unione_flangia', 'Viti ST2.9x9.5 unione flange (3)', FILES['st29_join'], STEEL, 'ferramenta', 'acciaio inox A2', 3, True, [0, 0, 182]))
        continue
    elif i == 'labbro_ombra_v611':
        q.update(explode=[0, 0, 128])
    elif i == 'passacavo_v61':
        q.update(id='passacavo_v62', name='Passacavo nel tunnel della flangia (TPU)', file=OUT + 'passacavo_v62.stl', explode=[0, -14, 138])
    elif i == 'viti_legno':
        q.update(name='Viti legno 5x35', file=FILES['wood_5x35'], explode=[0, 0, 200])
    elif i in ('piastra_finestra_nero', 'piastra_finestra_verde'):
        q.update(file=FILES['piastra_finestra_black' if i.endswith('nero') else 'piastra_finestra_green'])
    elif i in ('piastra_gate_nero', 'piastra_gate_verde'):
        q.update(file=FILES['piastra_gate_black' if i.endswith('nero') else 'piastra_gate_green'])
    elif i == 'labbri':
        q.update(name='Labbri a pettine (4 uguali)', file=FILES['labbri_x4'])
    elif i == 'chiocciola_v61':
        q.update(id='chiocciola_v62', name='Chiocciola (inserti spostati)', file=OUT + 'chiocciola_v62.stl')
    elif i == 'inserti_vasca':
        q.update(file=FILES['inserts_bowl'], qty=8)
    elif i in ('viti_torre_vasca', 'viti_torre_scatola'):
        if i == 'viti_torre_vasca':
            VP.append(_vp('viti_m3x40', 'Viti M3x40 pacco scatola-torre-vasca (3)', FILES['m3x40_stack'], STEEL, 'ferramenta', 'acciaio inox A2', 3, True, [0, 0, -120]))
            VP.append(_vp('oring_3x1', 'O-ring 3x1 sotto le teste (2)', FILES['oring_3x1'], '#1e1e1e', 'guarnizioni', 'NBR70', 2, True, [0, 0, -112]))
        continue
    elif i == 'colonna_v61':
        q.update(id='colonna_v62', name='Torre a 3 pilastri', file=OUT + 'colonna_v62.stl')
    elif i == 'scatola_v611':
        q.update(id='scatola_v62', name='Scatola elettronica (orecchia + fori stagni)', file=OUT + 'scatola_v62.stl')
    elif i == 'inserti_scatola':
        q.update(file=FILES['inserts_box'], qty=4)
    elif i == 'sfiato_eptfe':
        q.update(file=FILES['vent_m12_eptfe'])
    elif i == 'cavo_12v':
        VP.append(_vp('cavo_12v_unita', 'Cavo 12 V lato unita', FILES['cable_12v_unit'], '#151515', 'elettronica', 'PUR 4x0.34', 1, True, [0, -40, -60]))
        VP.append(_vp('cavo_12v_alimentazione', 'Cavo 12 V nel tunnel e in canalina', FILES['cable_12v_supply'], '#151515', 'elettronica', 'PUR 4x0.34', 1, True, [0, -40, 175]))
        continue
    elif i == 'connettore_ip67':
        q.update(name='Connettore M8 IP67 in linea', file=FILES['connector_m8_ip67'], explode=[0, -40, 60])
    elif i.startswith('fondello_v611_'):
        band = i.replace('fondello_v611_', '')
        q.update(id='fondello_v62_' + band, name=f'Fondello ({band}, conche Ø24)', file=FILES['fondello_v62_' + band])
    VP.append(q)
for k, nm, ex in (('canalina_base_1', 'Canalina: base 1', [0, -30, 205]), ('canalina_coperchio_1', 'Canalina: coperchio 1', [0, -30, 180]),
                  ('canalina_base_2', 'Canalina: base 2 (tagliata)', [0, -30, 205]), ('canalina_coperchio_2', 'Canalina: coperchio 2', [0, -30, 180]),
                  ('canalina_tappo', 'Canalina: tappo di testa', [0, -50, 192])):
    VP.append(_vp(k, nm, FILES[k], '#333436', 'struttura', 'PETG nero', 1, False, ex))
kp = []
for pt in VH['kibble_path']:
    if pt[2] > FL_Z0 + 0.01:
        kp.append([pt[0], pt[1], round(pt[2] + DZ_FL, 2)])
    else:
        if kp and kp[-1][2] > FL_Z0 + 0.01 and abs(pt[2] - FL_Z0) < 0.02:
            kp.append([pt[0], pt[1], round(FL_Z0 + DZ_FL, 2)])
        kp.append(list(pt))
viewer = {k: v for k, v in VH.items() if k not in ('parts', 'lod', 'kibble_path', 'scene')}
viewer['title'] = 'Kibble Dispenser Outdoor v6.2'
viewer['subtitle'] = 'saracinesca con interblocco ad anello, cavo in canalina, viti raggiungibili'
viewer['parts'] = VP
viewer['scene'] = dict(VH['scene'], shelf_underside_z=FL_Z1_62, shelf_cable_hole=None,
                       cable_channel={'from_xy': [0.0, -(FL_R62 - CH['insert'])], 'to_xy': [0.0, -(FL_R62 - CH['insert'] + CH['seg'] + L2_CH + 10.0)],
                                      'z_top': FL_Z1_62, 'profile_mm': [CH['w'], CH['h']], 'note': 'under the shelf, closed snap-in profile; no hole in the shelf'})
viewer['kibble_path'] = kp
json.dump(viewer, open(OUT + 'v62_viewer.json', 'w'), indent=1)
# closed-gate variant (scratch, for the screenshots)
vclosed = json.loads(json.dumps(viewer))
gc = {g['id']: g for g in GATE_PARTS('chiusa')}
for q in vclosed['parts']:
    if q['id'] in gc:
        q.update(file=gc[q['id']]['file'], name=gc[q['id']]['name'])
vclosed['subtitle'] = 'saracinesca CHIUSA: la finestra scopre il pulsante'
json.dump(vclosed, open(SCRATCH + 'v62_viewer_closed.json', 'w'), indent=1)
missing = [q['file'] for q in VP if not os.path.exists(q['file'])]
print('v62_viewer.json written:', len(VP), 'entries; missing files:', missing)
print(f'checks done in {time.time() - t_start:.0f} s')
