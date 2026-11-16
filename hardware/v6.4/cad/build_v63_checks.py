# executed by build_v63.py (exec) in its namespace: context, interference + designed contacts, gate / interlock, tool access
# per screw, bayonet sweep, clearances, seal continuity, DRY-VOLUME flood fill of the cap + panel, paw / fingertip probes,
# line of sight (cable tunnel, shadow gap), load case, grams / pieces / screws / inserts / colour swaps before-after,
# assembled copies, check_v63.png, drilling template, v63.json, v63_viewer.json
import time
import collections
import glob
from scipy.spatial import cKDTree
from scipy import ndimage
sys.path.insert(0, dt.HERE)                           # toolaccess.py and los.py live next to the scripts
from toolaccess import check_screw, axial_hits
from los import crop, first_hits
t_start = time.time()
P611, EX611 = EXTRA['P611'], EXTRA['EX611']
PANEL = EXTRA['PANEL']
LD = lambda f: trimesh.load(f)
print('\n--- context ---')
SHELF_T = 30.0
SHELF = D(box(-150, 150, -110, 110, FL_Z1_62, FL_Z1_62 + SHELF_T), [at(cyl(v5.SHELF_HOLE_D, FL_Z1_62 - 1, FL_Z1_62 + SHELF_T + 1), *v6.HOLE_C)])
R61 = {k: v6.clean(LD(OUT + k + '.stl')) for k in ('guarnizione_baionetta_v61', 'guarnizione_fondello_v61', 'disco_v61')}
R62 = {k: v6.clean(LD(OUT + k + '.stl')) for k in ('piastra_gate_v62', 'piastra_finestra_v62', 'labbro_pettine_v62')}
COLLAR = v6.build_collar(v6.fl_funnel_cavity()); COLLAR.apply_translation([0, 0, DZ_FL])
GSK_PIANO = LD(OUT + 'guarnizione_piano_v5.stl')
GSK_PIANO.apply_translation([0, 0, FL_Z1_62 - FL_Z1])
SHAFT, HUB = v6.build_shaft(), v6.build_hub()
LATCH = P['linguetta_sicura_v63']
BOUGHT, SCREWS = bought63(PANEL)
LIPS = {}
for nm, T, *_ in b62.lip_frames():
    m = R62['labbro_pettine_v62'].copy(); m.apply_transform(T); LIPS[f'labbro_pettine_{nm}'] = m
disc0, disc180 = R61['disco_v61'], rotz(R61['disco_v61'], 180)
G_OPEN, G_CLOSED = 0.0, STROKE
BLADE = {g: gate_pose(P['saracinesca_v63'], g) for g in (G_OPEN, G_CLOSED)}
RINGP = {g: gate_pose(P['anello_saracinesca_v63'], g) for g in (G_OPEN, G_CLOSED)}
ALL = {'flangia_piano_v63': P['flangia_piano_v63'], 'flangia_alta_v63': P['flangia_alta_v63'], 'saracinesca_v63@open': BLADE[G_OPEN],
       'anello_saracinesca_v63@open': RINGP[G_OPEN], 'passacavo_v63': P['passacavo_v63'], 'labbro_ombra_v611': P611['labbro_ombra_v611'],
       'colletto_v6': COLLAR, 'guarnizione_piano_v5': GSK_PIANO, 'chiocciola_v63': P['chiocciola_v63'], 'scivolo_v611': P611['scivolo_v611'],
       'labbro_scivolo_v611': P611['labbro_scivolo_v611'], 'linguetta_sicura_v63': LATCH, 'guarnizione_baionetta_v61': R61['guarnizione_baionetta_v61'],
       'piastra_gate_v62': R62['piastra_gate_v62'], 'piastra_finestra_v62': R62['piastra_finestra_v62'], 'disco_v61@0': disc0, 'disco_v61@180': disc180,
       'colonna_v63': P['colonna_v63'], 'albero_v6@0': SHAFT, 'mozzo_v6@0': HUB, 'scatola_v63': P['scatola_v63'], 'guscio_v611': P611['guscio_v611'],
       'pulsante_v611': P611['pulsante_v611'], 'fondello_v63': P['fondello_v63'], 'guarnizione_fondello_v61': R61['guarnizione_fondello_v61'], 'shelf': SHELF}
ALL.update(LIPS); ALL.update(BOUGHT); ALL.update(SCREWS)
NEWB = {'cable_12v_supply', 'cable_12v_unit', 'connector_m8_ip67', 'vent_m12_eptfe', 'oring_3x1', 'oring_3x1_cap', 'cable_tie', 'dowel_4x6',
        'switch_12mm_ip67', 'lightpipes_5mm', 'oring_5x1_lightpipe', 'leds_3mm', 'membrane_acoustic_ip67', 'speaker_20mm', 'harness_jst',
        'm3x40_stack', 'pt_k30x12_cap', 'pt_k30x10_chute', 'pt_k30x12_shell_tabs', 'wood_5x35', 'inserts_bowl', 'inserts_box'}
CHANGED = (set(P) - {'saracinesca_v63', 'anello_saracinesca_v63'}) | {'saracinesca_v63@open', 'anello_saracinesca_v63@open', 'colletto_v6',
                                                                   'guarnizione_piano_v5', 'shelf'} | NEWB
SOFT_ROLE = {
    ('flangia_piano_v63', 'guarnizione_baionetta_v61'): 'bayonet rim lip seal under the lower plate (as v6.1)',
    ('flangia_piano_v63', 'labbro_ombra_v611'): 'skirt lip anchor pressed in the lower plate groove',
    ('labbro_ombra_v611', 'guscio_v611'): 'shadow-gap skirt lip on the shell (as v6.1.1)',
    ('flangia_piano_v63', 'passacavo_v63'): 'cable grommet pressed in the tunnel mouth',
    ('passacavo_v63', 'cable_12v_supply'): 'grommet on the cable (pod second barrier)',
    ('guarnizione_piano_v5', 'shelf'): 'shelf gasket (as v6.1)', ('guarnizione_piano_v5', 'flangia_alta_v63'): 'shelf gasket in its groove',
    ('scatola_v63', 'guarnizione_fondello_v61'): 'PRIMARY dry box: cap lip on the box rim face', ('fondello_v63', 'guarnizione_fondello_v61'): 'cap lip in its groove',
    ('oring_shaft_9x2', 'colonna_v63'): 'shaft O-rings in the bushing', ('oring_shaft_9x2', 'albero_v6@0'): 'shaft O-rings in their grooves',
    ('oring_face_24x2', 'colonna_v63'): 'face O-ring in the tower groove', ('oring_face_24x2', 'scatola_v63'): 'face O-ring on the box plateau',
    ('oring_3x1', 'scatola_v63'): 'O-ring 3x1 in the roof countersink (P2/P3 keep the dry box sealed)',
    ('oring_3x1', 'm3x40_stack'): 'O-ring 3x1 squeezed by the screw head / on the shank',
    ('oring_3x1_cap', 'fondello_v63'): 'NEW: O-ring 3x1 in the cap counterbore countersink (A, C dry; B pod)',
    ('oring_3x1_cap', 'pt_k30x12_cap'): 'NEW: O-ring 3x1 squeezed by the cap screw head',
    ('pt_k30x12_cap', 'scatola_v63'): 'NEW: thread-forming engagement in the box boss pilots',
    ('pt_k30x10_chute', 'chiocciola_v63'): 'NEW: thread-forming engagement (no insert)',
    ('pt_k30x12_shell_tabs', 'chiocciola_v63'): 'NEW: thread-forming engagement (no insert)',
    ('oring_seam_2', 'fondello_v63'): 'seam O-ring in the spigot groove', ('oring_seam_2', 'guscio_v611'): 'seam O-ring on the shell',
    ('labbro_scivolo_v611', 'fondello_v63'): 'chute lip anchor', ('labbro_scivolo_v611', 'scivolo_v611'): 'chute lip on the chute',
    ('oring_btn_14x1.5', 'guscio_v611'): 'button O-ring', ('oring_btn_14x1.5', 'pulsante_v611'): 'button O-ring',
    ('switch_12mm_ip67', 'fondello_v63'): 'NEW: panel switch: front gasket on the recess floor (0.3 squeeze) + thread in the Ø12.2 hole',
    ('oring_5x1_lightpipe', 'fondello_v63'): 'NEW: light-pipe O-ring in its counterbore', ('oring_5x1_lightpipe', 'lightpipes_5mm'): 'NEW: light-pipe O-ring under the flange',
    ('lightpipes_5mm', 'fondello_v63'): 'NEW: light pipe flange on the boss face',
    ('membrane_acoustic_ip67', 'fondello_v63'): 'NEW: adhesive acoustic membrane on the dry floor over the grille',
    ('cable_tie', 'cable_12v_supply'): 'NEW: strain-relief tie cinched on the cable', ('cable_tie', 'shelf'): 'NEW: tie strap over the proud cable crown, pressed by the shelf (adds clamping)', ('dowel_4x6', 'flangia_piano_v63'): 'dowel pressed in the lower plate'}
for lk in LIPS:
    SOFT_ROLE[(lk, 'disco_v61@0')] = 'comb lip on the disc (0.15 preload)'; SOFT_ROLE[(lk, 'disco_v61@180')] = 'comb lip on the disc (0.15 preload)'
    SOFT_ROLE[(lk, 'piastra_gate_v62' if 'out' in lk else 'piastra_finestra_v62')] = 'comb lip anchor pressed in the groove'
SOFT = {frozenset(k): v for k, v in SOFT_ROLE.items()}
_skip = [('disco_v61@0', 'disco_v61@180'), ('disco_v61@0', 'mozzo_v6@0'), ('mozzo_v6@0', 'albero_v6@0'), ('mozzo_v6@0', 'servo'), ('mozzo_v6@0', 'm3x8_hub'),
         ('shelf', 'wood_5x35'), ('inserts_bowl', 'm3x40_stack'), ('inserts_box', 'm3x8_servo'), ('servo', 'm3x8_hub'), ('servo', 'm3x8_servo'),
         ('scatola_v63', 'gland_m12'), ('scatola_v63', 'vent_m12_eptfe'), ('cable_12v_unit', 'gland_m12'), ('cable_12v_unit', 'connector_m8_ip67'),
         ('cable_12v_supply', 'connector_m8_ip67'), ('inserts_bowl', 'chiocciola_v63'), ('inserts_box', 'scatola_v63'),
         ('wood_5x35', 'flangia_alta_v63'), ('wood_5x35', 'flangia_piano_v63'), ('cable_12v_supply', 'shelf'),
         ('m3x40_stack', 'chiocciola_v63'), ('m3x40_stack', 'colonna_v63'), ('m3x40_stack', 'scatola_v63'),
         ('leds_3mm', 'lightpipes_5mm'), ('harness_jst', 'switch_12mm_ip67'), ('harness_jst', 'board_70x50'), ('speaker_20mm', 'membrane_acoustic_ip67'),
         ('dowel_4x6', 'saracinesca_v63@open')]
SKIP = {frozenset(p) for p in _skip}


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
SCREW_HOLE = {k: round(vol(I(SCREWS['m3x40_stack'], ALL[k])), 4) for k in ('chiocciola_v63', 'colonna_v63', 'scatola_v63')}
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3; stack screw vs drilled parts {SCREW_HOLE}')
print(f'interference done {time.time() - t_start:.0f} s')

# ---------------- gate sweep ----------------
print('\n--- gate sweep ---')
GATE_FIXED = U([P['flangia_piano_v63'], P['flangia_alta_v63'], BOUGHT['dowel_4x6']])
UNIT_TOP = I(U([P611['guscio_v611'], P611['pulsante_v611'], P611['labbro_ombra_v611'], P['chiocciola_v63'], LATCH]), above(28.0))
GATE_SWEEP = []
for g in np.r_[np.arange(0.0, STROKE, 8.0), STROKE]:
    bl, rg = gate_pose(P['saracinesca_v63'], g), gate_pose(P['anello_saracinesca_v63'], g)
    GATE_SWEEP.append([round(float(g), 1), round(vol(I(bl, U([P['flangia_piano_v63'], P['flangia_alta_v63']]))), 4),
                       round(vol(I(rg, U([P['flangia_piano_v63'], P['flangia_alta_v63']]))), 4), round(vol(I(U([bl, rg]), UNIT_TOP)), 4),
                       round(vol(I(bl, rg)), 4), round(vol(I(U([bl, rg]), U([BOUGHT['cable_12v_supply'], BOUGHT['cable_tie']]))), 4)])
print('g, blade|flange, ring|flange, gate|unit, blade|ring(peg), gate|cable+tie', GATE_SWEEP)

# ---------------- open passage, coverage, interlock (ring window now a teardrop) ----------------
from shapely.ops import polylabel
PIE = OPENING63                                              # 6.3.0: funnel opening with the apex pulled back to r 4.6
PIN2D = Point(0, 0).buffer(PIVOT_D / 2, resolution=64)


def blade2d(g):
    return blade_sector(LEAD_OPEN - g, LEAD_OPEN + b62.BLADE_W - g).difference(Point(0, 0).buffer(b62.PIVOT_HOLE / 2, resolution=32))


open_free = PIE.difference(blade2d(0.0)).difference(PIN2D)
pl = polylabel(open_free, 0.02)
PASSAGE = {'v611_area_mm2': round(v5.OPENING.area, 1), 'v63_gate_open_area_mm2': round(open_free.area, 1), 'area_ratio_vs_v611': round(open_free.area / v5.OPENING.area, 4),
           'inscribed_d_mm': round(2 * open_free.exterior.distance(pl), 2), 'pivot_dowel_takes_mm2': round(PIE.intersection(PIN2D).area, 2),
           'note': '6.3.0: the opening apex is pulled back to r 4.6 round the dowel seat (-17.3 mm2, inside the narrow tip no kibble passes); '
                   'the largest inscribed circle is unchanged'}
COVER = [(round(float(g), 1), round(PIE.intersection(blade2d(g).union(PIN2D)).area / PIE.area, 4)) for g in np.arange(0.0, STROKE + 0.01, 1.0)]
RESID_OK = 3.0


def residual(g):
    r_ = PIE.difference(blade2d(g).union(PIN2D))
    if r_.is_empty:
        return 0.0, 0.0
    gs_ = [r_] if r_.geom_type == 'Polygon' else list(r_.geoms)
    big = [gg for gg in gs_ if gg.area > 1e-6]
    return r_.area, (max(2 * gg.exterior.distance(polylabel(gg, 0.01)) for gg in big) if big else 0.0)


def covered(g):
    a_, d_ = residual(g)
    return a_ <= RESID_OK and d_ <= 1.0


g_full = min(g for g, c in COVER if covered(g))
r_out_btn = shell_r_at(LATCH_A, BTN_Z, 0.0)
u_face = r_out_btn - b611.BTN611['dish_h']
ua = math.radians(LATCH_A)
uvec = np.array([math.cos(ua), math.sin(ua), 0.0]); wvec = np.array([-math.sin(ua), math.cos(ua), 0.0]); zvec = np.array([0, 0, 1.0])
PROBES = [('thumb Ø16 centred', 16.0, 0.0, 0.0)] + [('fingertip Ø10 offset 4 mm', 10.0, 4.0 * math.cos(t), 4.0 * math.sin(t)) for t in np.radians(np.arange(0, 360, 45))] + \
         [('fingertip Ø10 centred', 10.0, 0.0, 0.0), ('fingertip Ø10 offset 6 mm up', 10.0, 0.0, 6.0)]


def reachable(ring_m):
    rc = I(ring_m, box(-60, 80, 20, 120, 20, 75))
    out = []
    for nm_, dpr, ow, oz in PROBES:
        p0 = np.array([0, 0, BTN_Z]) + (u_face + 0.3) * uvec + ow * wvec + oz * zvec
        out.append(not axial_hits({'ring': rc}, p0, uvec, dpr / 2, 0.0, 40.0))
    return out


INTERLOCK = []
for g in np.r_[np.arange(0.0, 96.0, 8.0), np.arange(96.0, STROKE + 0.01, 1.0)]:
    rr = reachable(gate_pose(P['anello_saracinesca_v63'], g))
    cov = PIE.intersection(blade2d(g).union(PIN2D)).area / PIE.area
    ra_, rd_ = residual(g)
    INTERLOCK.append({'g_deg': round(float(g), 1), 'opening_covered': round(cov, 4), 'residual_open_mm2': round(ra_, 2), 'residual_gap_d_mm': round(rd_, 2),
                      'kibble_tight': bool(covered(g)), 'thumb_reaches_button': bool(rr[0]), 'any_fingertip_reaches': bool(any(rr[1:]))})
reach_g = [d['g_deg'] for d in INTERLOCK if d['any_fingertip_reaches'] or d['thumb_reaches_button']]
g_reach_first = min(reach_g) if reach_g else None
INTERLOCK_OK = bool(reach_g and all(d['kibble_tight'] for d in INTERLOCK if d['any_fingertip_reaches'] or d['thumb_reaches_button'])
                    and INTERLOCK[-1]['thumb_reaches_button'])
RESID_CLOSED = residual(STROKE)
print('full cover from g', g_full, '; button first reachable at g', g_reach_first, '; interlock strict:', INTERLOCK_OK)
V62 = json.load(open(OUT + 'v62.json'))
HOLD = V62['checks']['gate_hold']                            # blade, opening and column unchanged

# ---------------- tool access per screw (v6.3 build order) ----------------
print('\n--- tool access ---')
H = lambda lst, z, d=6.0: [at(cyl(d, z - 2.4, z, 24), x, y) for x, y in lst]
EARS = list(b61.CH_EARS); TABS = list(b61.TAB_INS)
ST_TOWER = {'chiocciola_v63': ALL['chiocciola_v63'], 'linguetta_sicura': LATCH, 'colonna_v63': ALL['colonna_v63'], 'albero': SHAFT,
            'oring_shaft': BOUGHT['oring_shaft_9x2'], 'inserts_bowl': SCREWS['inserts_bowl']}
ST_CHUTE = dict(ST_TOWER, scivolo_v611=P611['scivolo_v611'])
ST_SHELL = dict(ST_CHUTE, guscio_v611=P611['guscio_v611'], pulsante_v611=P611['pulsante_v611'])
for j, hh in enumerate(H(EARS, -b61.CH_FL_T)):
    ST_SHELL[f'chute_head_{j}'] = hh
BOXSET = {k: ALL[k] for k in ('scatola_v63', 'servo', 'board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF', 'gland_m12',
                              'vent_m12_eptfe', 'mozzo_v6@0', 'm3x8_servo', 'm3x8_hub', 'inserts_box', 'oring_face_24x2', 'cable_12v_unit')}
ST_BOX = dict(ST_SHELL, **BOXSET)
for j, hh in enumerate(H(TABS, -TAB_T)):
    ST_BOX[f'tab_head_{j}'] = hh
TA = {}
for j, (x, y) in enumerate(EARS):
    st = dict(ST_CHUTE); st.update({f'c{k}': hh for k, hh in enumerate(H(EARS, -b61.CH_FL_T)) if k != j})
    TA[f'step 3 chute -> bowl PT K30x10 ({x:.0f}, {y:+.1f})'] = check_screw(st, (x, y, -b61.CH_FL_T - PT['head_h']), (0, 0, -1), key_d=3.6)
for j, (x, y) in enumerate(TABS):
    st = dict(ST_SHELL); st.update({f't{k}': hh for k, hh in enumerate(H(TABS, -TAB_T)) if k != j})
    TA[f'step 4 shell -> bowl PT K30x12 @{ang_of((x, y)):.0f} deg (box not yet in)'] = check_screw(st, (x, y, -TAB_T - PT['head_h']), (0, 0, -1), key_d=3.6)
zs_stack = [EAR_Z0, Z_R - ROOF_T, Z_R - ROOF_T]
for j, ((x, y), zs) in enumerate(zip(P_SCREWS, zs_stack)):
    st = dict(ST_BOX)
    for k, ((x2, y2), z2) in enumerate(zip(P_SCREWS, zs_stack)):
        if k != j:
            st[f'stack_head_{k}'] = at(cyl(5.5, z2 - 3.0, z2, 24), x2, y2)
    TA[f'step 5 box+tower -> bowl M3x40 P{j + 1} ({x:.2f}, {y:.1f}){" sealed" if P_SEALED[j] else " via ear"}'] = check_screw(st, (x, y, zs - 3.0), (0, 0, -1))
ST_CAP = dict(ST_BOX, fondello_v63=P['fondello_v63'], guarnizione_fondello_v61=R61['guarnizione_fondello_v61'], oring_seam=BOUGHT['oring_seam_2'],
              labbro_scivolo=P611['labbro_scivolo_v611'], switch=BOUGHT['switch_12mm_ip67'], speaker=BOUGHT['speaker_20mm'])
for k, ((x2, y2), z2) in enumerate(zip(P_SCREWS, zs_stack)):
    ST_CAP[f'stack_head_{k}'] = at(cyl(5.5, z2 - 3.0, z2, 24), x2, y2)
for nm_, (x, y) in CAP_SCREWS.items():
    st = dict(ST_CAP)
    for nm2, (x2, y2) in CAP_SCREWS.items():
        if nm2 != nm_:
            st[f'cap_head_{nm2}'] = at(cyl(PT['head_d'], CAP_SEAT_Z - PT['head_h'], CAP_SEAT_Z, 32), x2, y2)
    TA[f'step 6 cap -> box PT K30x12 {nm_} ({x:.2f}, {y:.1f}) from below (T10)'] = check_screw(st, (x, y, CAP_SEAT_Z - PT['head_h']), (0, 0, -1), key_d=3.6)
ST_BOXONLY = {k: v for k, v in BOXSET.items() if k not in ('m3x8_servo', 'm3x8_hub')}
tz = dt.TAB_Z0 + v6.DZ_SERVO
for j, (x, y) in enumerate(b61.SERVO_HOLES_W):
    st = dict(ST_BOXONLY); st['hub_screw'] = SCREWS['m3x8_hub']
    TA[f'factory servo -> cradle M3x8 #{j + 1}'] = check_screw(st, (x, y, tz - dt.WASHER_T - 3.0), (0, 0, -1))
st = {k: v for k, v in ST_BOXONLY.items() if k != 'mozzo_v6@0'}
st['mozzo'] = HUB; st['servo_screws'] = SCREWS['m3x8_servo']
TA['factory hub -> servo M3x8 (through the plateau hole, before the tower)'] = check_screw(st, (0, 0, v6.HUB_SCREW_HEAD_Z + 3.0), (0, 0, 1))
ST_FLS = {'flangia_piano_v63': P['flangia_piano_v63'], 'flangia_alta_v63': P['flangia_alta_v63'], 'saracinesca': BLADE[G_OPEN], 'anello': RINGP[G_OPEN],
          'passacavo': P['passacavo_v63'], 'labbro_ombra': P611['labbro_ombra_v611'], 'shelf': SHELF, 'colletto': COLLAR, 'gasket': GSK_PIANO,
          'cable': BOUGHT['cable_12v_supply'], 'tie': BOUGHT['cable_tie'], 'dowel': BOUGHT['dowel_4x6']}
for j, a in enumerate(WOOD_ANG62):
    x, y = polar(WOOD_R62, a)
    TA[f'flange -> shelf wood 5x35 @{a:.0f} deg (PZ2, from below, unit not hung)'] = check_screw(ST_FLS, (x, y, FL_Z0 - 0.5), (0, 0, -1), key_d=6.5, hand_d=32.0)
for k, v in TA.items():
    print(f'  {k:78s} {v["verdict"]:12s} key>={v["key_length_min_mm"]} first={v["first_obstacle"]}')
print(f'tool access done {time.time() - t_start:.0f} s')

# ---------------- bayonet removal path with the gate CLOSED (cable, tie and grommet now part of the fixed set) ----------------
print('\n--- bayonet ---')
FIXED = U([P['flangia_piano_v63'], P['flangia_alta_v63'], COLLAR, GSK_PIANO, SHELF, P['passacavo_v63'], BLADE[G_CLOSED], RINGP[G_CLOSED],
           BOUGHT['dowel_4x6'], BOUGHT['cable_tie'], I(BOUGHT['cable_12v_supply'], above(52.5))])
latch_pressed = LATCH.copy(); latch_pressed.apply_translation([-1.6 * math.cos(ua), -1.6 * math.sin(ua), 0])
btn_pressed = P611['pulsante_v611'].copy(); btn_pressed.apply_translation([-1.5 * math.cos(ua), -1.5 * math.sin(ua), 0])
MOVING = I(U([P['chiocciola_v63'], latch_pressed, R62['piastra_finestra_v62'], LIPS['labbro_pettine_win_1'], LIPS['labbro_pettine_win_2'],
              disc0, R62['piastra_gate_v62'], P611['guscio_v611'], btn_pressed]), above(28.0))


def unlock_dz(a):
    return 0.0 if a <= bd.LOCK_ROT - bd.LUG_RAMP_DEG else -bd.LIFT * (a - (bd.LOCK_ROT - bd.LUG_RAMP_DEG)) / bd.LUG_RAMP_DEG


poses = [(-a, unlock_dz(a)) for a in np.linspace(0, bd.LOCK_ROT, 11)] + [(-bd.LOCK_ROT, -bd.LIFT - dz) for dz in (2, 5, 10, 20, 40, 80)]
SWEEP = []
for ang_, dz in poses:
    m = rotz(MOVING, ang_); m.apply_translation([0, 0, dz])
    SWEEP.append((round(float(ang_), 1), round(float(dz), 2), round(vol(I(m, FIXED)), 3)))
BAY_MAX = max(v for _, _, v in SWEEP)
ins = rotz(U([P['chiocciola_v63'], LATCH, P611['guscio_v611']]), -bd.LOCK_ROT); ins.apply_translation([0, 0, -bd.LIFT])
BAY_INS = round(vol(I(I(ins, above(28.0)), FIXED)), 4)
BTN_THROUGH_WINDOW = round(vol(I(btn_pressed, RINGP[G_CLOSED])), 4)
print('sweep max', BAY_MAX, 'insertion', BAY_INS, 'button vs ring (closed)', BTN_THROUGH_WINDOW)

# ---------------- clearances ----------------
print('\n--- clearances ---')


def min_dist(a, b, spacing=0.5, refine=300):
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


P3HEAD = at(cyl(5.5, Z_R - ROOF_T - 3.0, Z_R - ROOF_T, 48), *P_SCREWS[2])
P3POCKET_WALL = round(P3_POCKET_D / 2 - 5.5 / 2, 3)
ELEC = U([BOUGHT[k] for k in ('board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF')])
SW_BODY = BOUGHT['switch_12mm_ip67']
CLR = {'P3_head_to_board': min_dist(P3HEAD, BOUGHT['board_70x50']),
       'P3_head_to_box_pocket_wall_radial': P3POCKET_WALL,
       'P2_head_to_vent_nut': min_dist(at(cyl(5.5, Z_R - ROOF_T - 3.0, Z_R - ROOF_T, 32), *P_SCREWS[1]), BOUGHT['vent_m12_eptfe']),
       'tower_to_chute': min_dist(I(P['colonna_v63'], below(-0.5)), P611['scivolo_v611']),
       'switch_to_servo': min_dist(SW_BODY, BOUGHT['servo']), 'switch_to_box': min_dist(SW_BODY, P['scatola_v63']),
       'switch_to_electronics': min_dist(SW_BODY, ELEC),
       'leds_to_electronics_and_A_column': min_dist(U([BOUGHT['leds_3mm'], BOUGHT['lightpipes_5mm']]), U([ELEC, P['scatola_v63']])),
       'speaker_to_servo': min_dist(BOUGHT['speaker_20mm'], BOUGHT['servo']),
       'cap_screw_C_tip_to_board': min_dist(at(cyl(3.0, CAP_SEAT_Z, CAP_SEAT_Z + PT['len_cap'], 24), *CAP_SCREWS['C']), BOUGHT['board_70x50']),
       'A_column_to_servo': min_dist(I(P['scatola_v63'], box(11.0, 19.9, 25.0, 35.0, -97, -60)), BOUGHT['servo']),
       'A_column_to_board': min_dist(I(P['scatola_v63'], box(11.0, 19.9, 25.0, 34.0, -97, -36)), BOUGHT['board_70x50']),
       'ring_to_shell_open': min_dist(RINGP[G_OPEN], P611['guscio_v611']), 'ring_to_shell_closed': min_dist(RINGP[G_CLOSED], P611['guscio_v611']),
       'connector_to_shell': min_dist(BOUGHT['connector_m8_ip67'], P611['guscio_v611']),
       'supply_cable_to_shell': min_dist(I(BOUGHT['cable_12v_supply'], box(-30, 30, -90, 0, 0, 66.0)), P611['guscio_v611']),
       'supply_cable_to_flange_skirt': min_dist(I(BOUGHT['cable_12v_supply'], box(-30, 30, -90, 0, 40, 66.0)), P['flangia_piano_v63']),
       'cable_tunnel_to_ring_groove_mm': round(min(z for r, z in tunnel_rz63(96)[0] if RING_GRV['r0'] - 3 <= r <= RING_GRV['uc'][0] + 3) - CABLE_D / 2 - RING_GRV['z1'], 2),
       'cable_top_proud_of_shelf_face_mm': round(TUN63['zh'] + CABLE_D / 2 - FL_Z1_62, 2),
       'tie_to_flange_plates': min_dist(BOUGHT['cable_tie'], U([P['flangia_piano_v63'], P['flangia_alta_v63']])),
       'bowl_insert_wall_mm': {}, 'bowl_pilot_wall_mm': {}}
for (x, y) in P_SCREWS:
    hole = at(cyl(v6.INS_D + 2.4, 0.0, INS_DEPTH62 + 1.2, 48), x, y)
    CLR['bowl_insert_wall_mm'][f'({x}, {y})'] = 'solid >= 1.2 all round' if vol(D(hole, [P['chiocciola_v63'], at(cyl(v6.INS_D, -1, INS_DEPTH62, 48), x, y),
                                                                                         at(cyl(v6.INS_D + 1.6, -1, 0.4, 48), x, y), below(0.0)])) < 0.05 else 'THIN'
for (x, y) in list(b61.CH_EARS) + list(b61.TAB_INS):         # thinnest wall round the PT pilot (rays from the pilot wall outward)
    bowl_ = I(P['chiocciola_v63'], box(x - 15, x + 15, y - 15, y + 15, -1, BOWL_PILOT['depth'] + 3))
    o_, d_ = [], []
    for zz in np.linspace(0.6, BOWL_PILOT['depth'] - 0.3, 8):
        for th in np.radians(np.arange(0, 360, 10)):
            o_.append([x + (BOWL_PILOT['d'] / 2 + 0.02) * math.cos(th), y + (BOWL_PILOT['d'] / 2 + 0.02) * math.sin(th), zz]); d_.append([math.cos(th), math.sin(th), 0.0])
    loc, ri, _ = trimesh.ray.ray_triangle.RayMeshIntersector(bowl_).intersects_location(np.array(o_), np.array(d_), multiple_hits=False)
    dd = np.full(len(o_), 99.0)
    dd[ri] = np.linalg.norm(loc - np.array(o_)[ri], axis=1)
    CLR['bowl_pilot_wall_mm'][f'({x:.1f}, {y:.1f})'] = round(float(dd.min()), 2)
print(json.dumps(CLR, indent=0, default=str))

# ---------------- seal continuity ----------------
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
    CONT[f'oring_3x1 stack ({x}, {y}) | scatola_v63'] = sectors_ok(orr, P['scatola_v63'], (x, y), 24)
    CONT[f'oring_3x1 stack ({x}, {y}) | M3x40'] = sectors_ok(orr, SCREWS['m3x40_stack'], (x, y), 24)
for nm_, (x, y) in CAP_SCREWS.items():
    orr = I(BOUGHT['oring_3x1_cap'], at(cyl(8, -105, -95), x, y))
    CONT[f'oring_3x1 cap {nm_} | fondello_v63 (countersink)'] = sectors_ok(orr, P['fondello_v63'], (x, y), 24)
    CONT[f'oring_3x1 cap {nm_} | PT K30 (head + shank)'] = sectors_ok(orr, SCREWS['pt_k30x12_cap'], (x, y), 24)
CONT['guarnizione_fondello_v61 | scatola_v63 (PRIMARY lip)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['scatola_v63'], b611.WALL_C.centroid.coords[0])
CONT['guarnizione_fondello_v61 | fondello_v63 (groove, incl. the beam over the panel opening)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['fondello_v63'], b611.WALL_C.centroid.coords[0])
CONT['oring_seam | fondello_v63'] = sectors_ok(BOUGHT['oring_seam_2'], P['fondello_v63'], (b611.SEAM_CX, 0.0))
CONT['labbro_ombra | flangia_piano_v63 (anchor)'] = sectors_ok(P611['labbro_ombra_v611'], P['flangia_piano_v63'], (0.0, 0.0), 72)
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    sl = axial_cyl(Pk, nk, 12.0, LED['len'] - 1.5, LED['len'] + 0.5, 32)
    Tal = trimesh.geometry.align_vectors(-nk, [0, 0, 1]); Tal[:3, 3] = -Tal[:3, :3] @ (Pk - nk * LED['len'])
    o_, c_, l_ = [I(m, sl).copy() for m in (BOUGHT['oring_5x1_lightpipe'], P['fondello_v63'], BOUGHT['lightpipes_5mm'])]
    for m in (o_, c_, l_):
        m.apply_transform(Tal)
    CONT[f'oring_5x1 {k} | fondello_v63 (counterbore)'] = sectors_ok(o_, c_, (0.0, 0.0), 24)
    CONT[f'oring_5x1 {k} | light pipe flange'] = sectors_ok(o_, l_, (0.0, 0.0), 24)
Pb, nb, _ = PANEL['frames']['btn']
sl = axial_cyl(Pb, nb, 20.0, REC['floor'] - 0.6, REC['floor'] + 0.4, 64)
Tal = trimesh.geometry.align_vectors(-nb, [0, 0, 1]); Tal[:3, 3] = -Tal[:3, :3] @ (Pb - nb * REC['floor'])
s_, c_ = [I(m, sl).copy() for m in (BOUGHT['switch_12mm_ip67'], P['fondello_v63'])]
for m in (s_, c_):
    m.apply_transform(Tal)
CONT['switch front gasket | recess floor'] = sectors_ok(D(s_, [cyl(12.3, -5, 5, 64)]), c_, (0.0, 0.0), 24)
for k, v in CONT.items():
    print(f'  {k:70s} {v}')

# ---------------- DRY VOLUME: voxel flood fill of the cap region (cap + box + bought parts as solids) ----------------
print('\n--- dry-volume flood fill ---')
PITCH_V = 0.4
ZV0, ZV1 = Z_BOT - 0.8, b61.Z_C - b61.GRV_D - 0.1             # up to just under the lip groove bottom: top layer closed
SEALS_AS_SEALED = []                                         # seals drawn as the closed state (their contact is proven by the continuity check)
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    SEALS_AS_SEALED += [axial_cyl(Pk, nk, LED['hole'] + 0.02, -0.5, LED['len'] + 1.0, 32),
                        axial_cyl(Pk, nk, LED['cb_d'] + 0.02, LED['len'] - LED['cb_depth'] - 0.02, LED['len'] + 0.3, 32)]
for x, y in CAP_SCREWS.values():
    SEALS_AS_SEALED.append(at(U([cyl(3.42, CAP_SEAT_Z - 0.1, CAP_BOSS_TOP + 0.3, 24), cyl(OR_3x1['csk_d'] + 0.02, CAP_SEAT_Z - 0.1, CAP_SEAT_Z + 0.95, 32)]), x, y))
SOLIDS = [P['fondello_v63'], P['scatola_v63'], BOUGHT['switch_12mm_ip67'], BOUGHT['lightpipes_5mm'], SCREWS['pt_k30x12_cap'],
          P611['labbro_scivolo_v611'], P611['scivolo_v611'], at(cyl(15.0, Z_BOT + T_CAP - 0.05, Z_BOT + T_CAP + 0.6, 48), SPK['x'], SPK['y'])] + SEALS_AS_SEALED
xs_ = np.arange(-84.0, 64.0, PITCH_V) + PITCH_V / 2
ys_ = np.arange(-74.0, 74.0, PITCH_V) + PITCH_V / 2
zs_ = np.arange(ZV0, ZV1, PITCH_V) + PITCH_V / 2
GX, GY = np.meshgrid(xs_, ys_, indexing='ij')
occ = np.zeros((len(xs_), len(ys_), len(zs_) + 1), bool)
occ[:, :, -1] = True                                         # closed top layer (the box rim + lip close the D above it)
for k, z in enumerate(zs_):
    polys = []
    for m in SOLIDS:
        if m.bounds[0, 2] > z or m.bounds[1, 2] < z:
            continue
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None:
            continue
        T = np.eye(4); T[2, 3] = -z
        p2, _ = s.to_2D(to_2D=T)
        polys += list(p2.polygons_full)
    if polys:
        un = shapely.unary_union(polys)
        shapely.prepare(un)
        occ[:, :, k] = shapely.contains_xy(un, GX, GY)
lab, nlab = ndimage.label(~occ)


def lab_at(p, search=3.0):
    """label of the free voxel nearest to p (within `search` mm); 0 if none"""
    i, j, k = int((p[0] - xs_[0]) / PITCH_V + 0.5), int((p[1] - ys_[0]) / PITCH_V + 0.5), int((p[2] - zs_[0]) / PITCH_V + 0.5)
    rr = int(search / PITCH_V)
    sub = lab[max(i - rr, 0):i + rr + 1, max(j - rr, 0):j + rr + 1, max(k - rr, 0):k + rr + 1]
    if lab[i, j, k]:
        return int(lab[i, j, k])
    idx = np.argwhere(sub > 0)
    if not len(idx):
        return 0
    c = np.array([min(i, rr), min(j, rr), min(k, rr)])
    q = idx[np.argmin(np.linalg.norm(idx - c, axis=1))]
    return int(sub[tuple(q)])


Pk2, nk2, _ = PANEL['frames']['ko2']
SEEDS = {'dry: D interior under the box': (5.0, 0.0, -90.0), 'dry: panel pocket behind KO2': tuple(Pk2 - nk2 * 18.0),
         'dry: panel pocket behind the button': tuple(PANEL['frames']['btn'][0] - PANEL['frames']['btn'][1] * 20.0 + np.array([0, 0, 8.5])),
         'dry: LED well': tuple(PANEL['frames']['led1'][0] - PANEL['frames']['led1'][1] * (LED['len'] + 3.0)),
         'wet: main ring at the drain': (-48.0, 22.0, -99.5), 'wet: +X sump at drain 2': (45.0, 14.0, -99.5),
         'exterior: outside the pod': (0.0, -73.5, -90.0), 'exterior: outlet bore': (CH_X, 0.0, -95.0)}
SEED_LAB = {k: lab_at(np.array(v)) for k, v in SEEDS.items()}
dry_labels = {v for k, v in SEED_LAB.items() if k.startswith('dry')}
other_labels = {v for k, v in SEED_LAB.items() if not k.startswith('dry')}
DRY = {'voxel_mm': PITCH_V, 'z_range': [round(ZV0, 2), round(ZV1, 2)], 'seed_labels': SEED_LAB,
       'dry_is_one_volume': len(dry_labels) == 1 and 0 not in dry_labels,
       'dry_separate_from_wet_and_exterior': not (dry_labels & other_labels),
       'dry_volume_cm3': round(float((lab == next(iter(dry_labels))).sum()) * PITCH_V ** 3 / 1000, 1) if len(dry_labels) == 1 else None,
       'sump_drains_to_exterior': SEED_LAB['wet: +X sump at drain 2'] == SEED_LAB['exterior: outside the pod'],
       'main_ring_drains_to_exterior': SEED_LAB['wet: main ring at the drain'] == SEED_LAB['exterior: outside the pod'],
       'method': 'cap, box, switch (front gasket 0.3 into the recess floor), light pipes + O-rings, cap screws + O-rings, chute + chute lip and '
                 'the acoustic membrane as solids; 0.4 mm voxels from the cap bottom to just under the cap-lip groove (top layer closed: the box '
                 'rim sits on the lip there); free voxels labelled with 6-connectivity; seeds in the D interior, the panel pocket, the wet ring, '
                 'the +X sump, outside and in the outlet bore'}
if not DRY['dry_separate_from_wet_and_exterior']:              # leak finder: geodesic BFS from the D interior to the exterior seed
    from collections import deque
    free = lab == SEED_LAB['dry: D interior under the box']
    st = tuple(int((np.array(SEEDS['dry: D interior under the box'])[a] - g[0]) / PITCH_V + 0.5) for a, g in enumerate((xs_, ys_, zs_)))
    tgt = tuple(int((np.array(SEEDS['exterior: outside the pod'])[a] - g[0]) / PITCH_V + 0.5) for a, g in enumerate((xs_, ys_, zs_)))
    par = {st: None}; dq = deque([st]); found = None
    while dq:
        c = dq.popleft()
        if c == tgt or (abs(c[0] - tgt[0]) + abs(c[1] - tgt[1]) + abs(c[2] - tgt[2]) <= 2):
            found = c; break
        for dv_ in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            nb_ = (c[0] + dv_[0], c[1] + dv_[1], c[2] + dv_[2])
            if 0 <= nb_[0] < free.shape[0] and 0 <= nb_[1] < free.shape[1] and 0 <= nb_[2] < free.shape[2] - 1 and free[nb_] and nb_ not in par:
                par[nb_] = c; dq.append(nb_)
    path = []
    while found is not None:
        path.append((round(xs_[found[0]], 1), round(ys_[found[1]], 1), round(zs_[found[2]], 1))); found = par[found]
    DRY['leak_path_sample'] = path[::-1][::max(1, len(path) // 40)]
print(DRY)
# v6.2 sump fact (measured on fondello_v62.stl): the +X wet region is closed off below z ~ -91 and has no drain
_c62 = LD(OUT + 'fondello_v62.stl')
_s = _c62.section(plane_origin=[0, 0, -95.0], plane_normal=[0, 0, 1]); _T = np.eye(4); _T[2, 3] = 95.0
_p2, _ = _s.to_2D(to_2D=_T)
SUMP62 = [np.round(Polygon(h).bounds, 1).tolist() for pp_ in _p2.polygons_full for h in pp_.interiors if Polygon(h).centroid.x > 40 and Polygon(h).area > 50]
print('v6.2 +X sump at z -95 (closed hole in the cap section):', SUMP62)

# ---------------- PANEL: paw / snout / fingertip probes, knock-out skin, drainage ----------------
print('\n--- panel probes ---')
CAPP = U([P['fondello_v63'], BOUGHT['switch_12mm_ip67']])


def probe_reach(name, d, approach, finger=False):
    """push a sphere (or a Ø d finger: cylinder + hemispherical tip) along -n (tilted by `approach` deg up/down/sideways) into
    the recess; returns the depth of its leading point below the facet point P along the recess axis at first contact"""
    Pk, nk, phi = PANEL['frames'][name]
    up = np.array([0, 0, 1.0]); side = np.cross(nk, up); side /= np.linalg.norm(side)
    ax_, kind = approach
    dv = -nk.copy()
    if kind == 'up':
        dv = trimesh.transformations.rotation_matrix(math.radians(ax_), side)[:3, :3] @ dv
    elif kind == 'side':
        dv = trimesh.transformations.rotation_matrix(math.radians(ax_), up)[:3, :3] @ dv
    crop_ = I(CAPP, axial_cyl(Pk, nk, 60.0, -20.0, 20.0, 48))
    r = d / 2
    if finger:                                                  # fingertip: hemispherical tip + Ø d finger behind it
        shaft = trimesh.creation.cylinder(radius=r, height=60.0, sections=48)
        shaft.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], -dv)); shaft.apply_translation(-dv * 30.0)
        tool0 = U([trimesh.creation.icosphere(subdivisions=3, radius=r), shaft])
    else:
        tool0 = trimesh.creation.icosphere(subdivisions=3, radius=r)

    def hits(s):
        c = Pk + dv * s - dv * r                                # leading point at P + dv*s
        t = tool0.copy(); t.apply_translation(c)
        return vol(I(t, crop_)) > 1e-3
    lo, hi = -15.0, 25.0
    if hits(lo):
        return None
    for _ in range(22):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(mid) else (mid, hi)
    lead = Pk + dv * lo
    return round(float((Pk - lead) @ nk), 2)


PAW = {}
APPROACHES = [(0.0, 'axis'), (15.0, 'up'), (-15.0, 'up'), (15.0, 'side'), (-15.0, 'side')]
for nm_ in ('btn',):                                        # the knock-outs are flush (no recess to probe)
    row = {}
    for lab_, d, fing in (('paw pad sphere Ø30', 30.0, False), ('paw pad sphere Ø40', 40.0, False), ('snout sphere Ø25', 25.0, False),
                          ('fingertip Ø16', 16.0, True), ('fingertip Ø12', 12.0, True)):
        reach = [probe_reach(nm_, d, ap, fing) for ap in (APPROACHES if not fing else APPROACHES[:1])]
        row[lab_] = {'deepest_mm': max(r for r in reach if r is not None), 'actuator_top_mm': REC['face'] - 0.3,
                     'reaches_actuator': bool(max(r for r in reach if r is not None) >= REC['face'] - 0.3 - 0.05)}
    PAW[nm_] = row
    print(nm_, row)
PANEL_OK = all(not v['reaches_actuator'] for nm_ in PAW for k, v in PAW[nm_].items() if 'finger' not in k) and \
           all(v['reaches_actuator'] for nm_ in PAW for k, v in PAW[nm_].items() if 'finger' in k)
PAW_MARGIN = round(min(REC['face'] - 0.3 - v['deepest_mm'] for nm_ in PAW for k, v in PAW[nm_].items() if 'finger' not in k), 2)
# flush knock-outs: skin measured on the mesh along the axis (plain, under the engraved ring, under the dot), nut-seat pad
# face depth, outer flushness, and the envelope of a future 12 mm switch in each drilled-out knock-out
KO_SKIN, KO_FLUSH = {}, {}
_BS, _BI035, _BI10 = band_solid(), band_inner_solid(0.35), band_inner_solid(1.0)
for nm_ in ('ko1', 'ko2', 'ko3'):
    Pk, nk, _ = PANEL['frames'][nm_]
    sd_ = np.cross(nk, [0, 0, 1.0]); sd_ /= np.linalg.norm(sd_); up_ = np.cross(sd_, nk)
    def skin_at(off, r_=0.15):
        h_ = axial_hits({'cap': P['fondello_v63']}, Pk + nk * 1.0 + off, -nk, r_, 0.0, 1.0 + KO['skin'] + 1.6)
        return round(h_['cap'][1] - h_['cap'][0], 2) if 'cap' in h_ else None
    plain = [skin_at(3.0 * v) for v in (sd_, -sd_, up_, -up_)] + [skin_at(4.5 / math.sqrt(2.0) * v) for v in (sd_ + up_, sd_ - up_)]
    marks = [skin_at(0.0 * sd_)] + [skin_at(KO['ring_d'] / 2 * v) for v in (sd_, -sd_, up_, -up_)]
    pad_ = []
    for v in (sd_, -sd_, up_, -up_):
        h_ = axial_hits({'cap': P['fondello_v63']}, Pk + nk * 1.0 + 7.5 * v, -nk, 0.15, 0.0, 1.0 + KO['pad'] + 1.5)
        pad_.append(round(h_['cap'][1] - 1.0, 2) if 'cap' in h_ else None)
    KO_SKIN[nm_] = {'plain_min_mm': min(plain), 'plain_max_mm': max(plain), 'under_engraving_min_mm': min(marks),
                    'nut_seat_face_depth_at_r7.5_mm': pad_}
    # flushness inside the Ø15 footprint: void in the outer 0.35 mm layer (= the engraving) and between 0.35 and 1.0 mm deep (must be 0)
    foot_ = axial_cyl(Pk, nk, 15.0, -2.0, 1.5, 96)
    lay1 = D(I(foot_, _BS), [_BI035]); lay2 = D(I(foot_, _BI035), [_BI10])
    KO_FLUSH[nm_] = {'void_0_0.35mm_mm3 (engraving)': round(vol(D(lay1, [P['fondello_v63']])), 2),
                     'void_0.35_1.0mm_mm3': round(vol(D(lay2, [P['fondello_v63']])), 3)}
FUTURE_KO = {}
FUT_OBST = {'fondello_v63 (except the drilled hole)': P['fondello_v63'], 'scatola_v63': P['scatola_v63'], 'servo': BOUGHT['servo'], 'speaker_20mm': BOUGHT['speaker_20mm'],
            'electronics': ELEC, 'switch_12mm_ip67 (real button)': BOUGHT['switch_12mm_ip67'], 'harness_jst': BOUGHT['harness_jst'],
            'leds + light pipes': U([BOUGHT['leds_3mm'], BOUGHT['lightpipes_5mm']]), 'cap screws': SCREWS['pt_k30x12_cap']}
_fut = {nm_: future_switch(*PANEL['frames'][nm_][:2]) for nm_ in ('ko1', 'ko2', 'ko3')}
for nm_, env_ in _fut.items():
    row = {}
    for ek, em in env_.items():
        for ok_, om in FUT_OBST.items():
            if ek == 'thread' and ok_.startswith('fondello'):
                continue
            v_ = round(vol(I(em, om)), 3) if bb_overlap(em, om) else 0.0
            if v_ > 1e-3:
                row[f'{ek}|{ok_}'] = v_
    for nb_, envb in _fut.items():
        if nb_ != nm_:
            v_ = round(vol(I(U(list(env_.values())), U(list(envb.values())))), 3)
            if v_ > 1e-3:
                row[f'switch|future {nb_}'] = v_
    Pk, nk, _ = PANEL['frames'][nm_]
    cap_behind = I(P['fondello_v63'], axial_cyl(Pk, nk, 70.0, KO['pad'] + 0.3, KO['pad'] + 30.0, 96))      # the cap beyond the nut-seat face
    nb_env = U([env_['nut_swing'], env_['body']])
    FUTURE_KO[nm_] = {'collisions_mm3': row, 'fits': not row,
                      'nut_and_body_to_cap_beyond_the_seat_mm': min_dist(nb_env, cap_behind),
                      'nut_and_body_to_servo_switch_box_speaker_electronics_mm': min_dist(nb_env, U([BOUGHT['servo'], BOUGHT['switch_12mm_ip67'], P['scatola_v63'],
                                                                                                    BOUGHT['speaker_20mm'], ELEC]))}
print('knock-out skins', KO_SKIN, 'flush voids', KO_FLUSH)
print('future switch in the knock-outs', FUTURE_KO)
# drainage: recess axis tilt, grille direction, roof slope
DRAINAGE = {'recess_axes_tilt_down_outward_deg': TILT, 'recess_floor_lowest_point_vs_rim_mm': round(REC['floor'] * math.tan(math.radians(TILT)), 2),
            'acoustic_grille': 'faces straight down through the flat bottom (7 x Ø1.5, 0.5 x 45 deg outer chamfer breaks the meniscus)',
            'pocket_roof': f'{POCKET["slope_deg"]} deg fall to the west end, water drips onto the wet floor next to the main drain',
            'light_pipes': 'flush with the band face, axes on the facet normal (15-17 deg down-outward)'}
# ---------------- 6.3.0 fixes: light-pipe flushness + roof clearance, dowel seat wall, cap seam spigot as one body ----------------
LED_FIX = {}
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    sd_ = np.cross(nk, [0, 0, 1.0]); sd_ /= np.linalg.norm(sd_); up_ = np.cross(sd_, nk)
    offs = []
    for th in np.radians(np.arange(0, 360, 45)):
        o_ = 2.9 * (math.cos(th) * sd_ + math.sin(th) * up_)             # just outside the Ø5.1 hole: the band face round the lens
        h_ = axial_hits({'cap': P['fondello_v63']}, Pk + nk * 2.0 + o_, -nk, 0.1, 0.0, 4.0)
        offs.append(round(h_['cap'][0] - 2.0, 3) if 'cap' in h_ else None)
    LED_FIX[k] = {'band_face_vs_lens_plane_mm (8 points at r 2.9)': offs, 'max_abs_mm': max(abs(v) for v in offs if v is not None),
                  'z_mm': round(float(Pk[2]), 2), 'axis_down_outward_deg': round(math.degrees(math.asin(-nk[2])), 1)}
LED_FIX['led_bodies_to_cap_mm'] = min_dist(BOUGHT['leds_3mm'], P['fondello_v63'])
LED_FIX['lightpipe_flanges_to_well_and_roof_mm'] = min_dist(U([axial_cyl(*PANEL['frames'][k][:2], 8.0, LED['len'] + 0.05, LED['len'] + 1.0, 32) for k in ('led1', 'led2')]),
                                                            I(P['fondello_v63'], U([axial_cyl(*PANEL['frames'][k][:2], 40.0, LED['len'] + 0.3, LED['len'] + 20.0, 64)
                                                                                     for k in ('led1', 'led2')])))      # beyond the seat on the boss face
LED_FIX['v63_first_issue'] = 'axes 3 deg down-outward on a face leaning 14-17 deg: lens edge ~0.6-0.7 mm proud / sunk'
_fs = P['flangia_piano_v63'].section(plane_origin=[0, 0, FL_Z1 - DOWEL['depth'] / 2], plane_normal=[0, 0, 1])
_T = np.eye(4); _T[2, 3] = -(FL_Z1 - DOWEL['depth'] / 2)
_p2, _ = _fs.to_2D(to_2D=_T)
_rings = [LineString(g.coords) for pp_ in _p2.polygons_full for g in list(pp_.interiors) + [pp_.exterior]]
_seat = [r_ for r_ in _rings if Polygon(r_.coords).contains(Point(0, 0)) and Polygon(r_.coords).area < 30.0]
DOWEL_SEAT = {'closed_360_deg': bool(_seat), 'seat_d_mm': round(2 * (Polygon(_seat[0].coords).area / math.pi) ** 0.5, 2) if _seat else None,
              'min_wall_to_next_edge_mm': round(min(_seat[0].distance(r_) for r_ in _rings if r_.distance(Point(0, 0)) > DOWEL['d'] / 2 + 0.2), 2) if _seat else None,
              'v63_first_issue': 'wall wrapped 72.8 % of the seat, 3.1 mm mouth into the funnel opening apex',
              'how': f'funnel opening apex pulled back to r {PIVOT_WALL_R} (opening area -{round(v5.OPENING.area - OPENING63.area, 1)} mm2 of {round(v5.OPENING.area)}); '
                     'the pivot stays on the shaft axis: blade and ring both turn about it (peg in the arm), an off-axis pivot would bind',
              'section_z': round(FL_Z1 - DOWEL['depth'] / 2, 2)}
_COLLAR_ZONE = at(D(cyl(2 * 72.5, -76.5, -72.5, 256), cyl(2 * 66.5, -77.0, -72.0, 256)), b611.SEAM_CX, 0)     # the collar only
CAP_BODIES = {'fondello_v63': len(P['fondello_v63'].split(only_watertight=False)), 'fondello_v62 (for reference)': len(LD(OUT + 'fondello_v62.stl').split(only_watertight=False)),
              'spigot_collar': f'45 deg chamfer from the ring bore (r {round(b611.SEAM_R - (b611.SPIG_IN - T_SHELL), 2)}) down into the cap wall (r {SPIG_COLLAR_RW}); groove {b611.ZG_SEAM} unchanged',
              'collar_to_box_and_cap_lip_mm': [min_dist(I(P['fondello_v63'], _COLLAR_ZONE), P['scatola_v63']),
                                               min_dist(I(P['fondello_v63'], _COLLAR_ZONE), R61['guarnizione_fondello_v61'])]}
print('6.3.0 fixes:', LED_FIX, DOWEL_SEAT, CAP_BODIES)

# ---------------- line of sight: cable tunnel (raised, tie window, bell) and shadow gap behind the (teardrop-window) ring ----------------
print('\n--- line of sight ---')
LOSM = {'fondello_v63': P['fondello_v63'], 'guscio_v611': P611['guscio_v611'], 'flangia_piano_v63': P['flangia_piano_v63'], 'flangia_alta_v63': P['flangia_alta_v63'],
        'labbro_ombra_v611': P611['labbro_ombra_v611'], 'anello': RINGP[G_OPEN], 'passacavo': P['passacavo_v63'], 'cable': BOUGHT['cable_12v_supply'],
        'tie': BOUGHT['cable_tie'], 'shelf': SHELF, 'chiocciola_v63': P['chiocciola_v63'], 'pulsante': P611['pulsante_v611']}
ZS_IN, X0_IN, X1_IN = section_fn(T_SHELL + 2.0)


def in_pod(p):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    a, c = np.interp(z, ZS_IN, X0_IN), np.interp(z, ZS_IN, X1_IN)
    return ((x - (a + c) / 2) ** 2 + y ** 2 < ((c - a) / 2) ** 2) & (z > Z_BOT + T_CAP) & (z < Z_TOP)


def cast(origins, dirs, lo, hi, step=0.2):
    M = {k: crop(m, lo, hi) for k, m in LOSM.items()}
    hit, dist = first_hits(M, origins, dirs)
    dn = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    reach = []
    for o, d, t in zip(origins, dn, dist):
        t = min(t, 300.0)
        s = np.arange(0.1, max(t - 0.1, 0.1), step)
        qq = o + s[:, None] * d
        reach.append(bool(len(qq) and in_pod(qq).any()))
    return np.array(reach), hit


LOS = {}
O_, D_ = [], []
for z in np.linspace(60.0, 66.0, 7):
    for a in np.radians(np.arange(0, 360, 3.0)):
        for e in np.radians([-15, 0, 15]):
            O_.append([97 * math.cos(a), 97 * math.sin(a), z - 13 * math.tan(e)]); D_.append([-math.cos(a) * math.cos(e), -math.sin(a) * math.cos(e), math.sin(e)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-100, -100, 30]), np.array([100, 100, 80]))
LOS['shadow_gap_behind_ring'] = {'rays': len(O_), 'reach_pod': int(reach.sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
O_, D_ = [], []
for dy in np.linspace(-3.0, 3.0, 9):
    for dz in np.linspace(-3.0, 2.0, 9):
        for el in np.radians([0, -10, -20, -30, -45]):
            O_.append([dy, -(FL_R62 + 6.0), TUN63['zh'] + dz]); D_.append([0.0, math.cos(el), math.sin(el)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-30, -100, 40]), np.array([30, -50, 80]))
LOS['cable_tunnel_exit'] = {'rays': len(O_), 'reach_pod': int(reach.sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
print(LOS)
print(f'checks A done {time.time() - t_start:.0f} s')

# ---------------- load case (hand calcs) ----------------
print('\n--- load case ---')
S_XY, S_Z, TAU = 45.0, 20.0, 25.0
LC62 = V62['load_case']
W_UNIT = 12.0 + 0.6
FV = 250.0 + W_UNIT + 20.0
Xp = np.array([p[0] for p in P_SCREWS]); Yp = np.array([p[1] for p in P_SCREWS])
x_fc = -13.45
F_ax = np.linalg.solve(np.array([[1, 1, 1], Xp, Yp], float), np.array([FV, FV * x_fc, 0.0]))
cxs, cys = Xp.mean(), Yp.mean()
M_side = 100.0 * (0.0 - Z_BOT) / 1000.0
F_stack_ub = max(float((F_ax + M_side * 1000 * ((Xp - cxs) * math.cos(t) + (Yp - cys) * math.sin(t)) /
                        np.sum(((Xp - cxs) * math.cos(t) + (Yp - cys) * math.sin(t)) ** 2)).max()) for t in np.radians(np.arange(0, 360, 5)))
# cap screws: vertical 282 N from the flat bottom (load centre x_fc) shared by A, B, C + the lip/O-ring preload ~130 N
Cx = np.array([p[0] for p in CAP_SCREWS.values()]); Cy = np.array([p[1] for p in CAP_SCREWS.values()])
F_cap = np.linalg.solve(np.array([[1, 1, 1], Cx, Cy], float), np.array([FV, FV * x_fc, 0.0]))
PRE = 130.0 / 3 + 40.0                                     # lip + seam share and screw preload per screw
F_cap_w = float(F_cap.max() + PRE)
pull_pt = math.pi * PT['pilot'] * 8.0 * 0.5 * S_Z           # thread shear across layers, 50 % fill, 8 mm engagement
pull_pt_tab = math.pi * PT['pilot'] * 6.0 * 0.5 * S_Z
F_tab = max(LC62['shell_tabs'].get('worst_N', 100.0) if isinstance(LC62['shell_tabs'], dict) else 100.0, 100.0)
tau_roof = float(F_ax.max()) / (math.pi * 5.5 * ROOF_T)
A_pil = math.pi * (b62.PIL_R ** 2 - 1.7 ** 2)
sig_pil = (400.0 + float(F_ax.max())) / A_pil
web_B = round(math.hypot(CAP_SCREWS['B'][0] - CH_X, CAP_SCREWS['B'][1]) - CAP_CB_D / 2 - (b61.OUTLET['r'] + b61.OUTLET['chamfer'] + 1.0), 2)
F_KO = 250.0
LOAD = {'case': f'as v6.2: 250 N down at the flat bottom (z {Z_BOT}) + 100 N sideways there + unit weight {W_UNIT:.1f} N + 20 N kibble column',
        'stack_screws_M3x40': {'positions': P_SCREWS, 'vertical_shares_N': [round(float(v), 1) for v in F_ax], 'worst_screw_N': round(float(F_ax.max()), 1),
                               'SF_insert_pullout': round(600.0 / float(F_ax.max()), 1), 'SF_screw_proof': round(2200.0 / float(F_ax.max()), 1),
                               'upper_bound_if_side_load_went_through_the_box_N': round(F_stack_ub, 1), 'upper_bound_SF_insert': round(600.0 / F_stack_ub, 1),
                               'v62': f"{LC62['stack_screws_M3x40']['worst_screw_N']} N, SF {LC62['stack_screws_M3x40']['SF_insert_pullout']} (P3 moved 0.775 mm)"},
        'cap_screws_PT_K30x12': {'positions': CAP_SCREWS, 'vertical_shares_N': [round(float(v), 1) for v in F_cap], 'preload_per_screw_N': round(PRE, 1),
                                 'worst_screw_N': round(F_cap_w, 1), 'pullout_est_N': round(pull_pt), 'SF_pullout': round(pull_pt / F_cap_w, 1),
                                 'model': 'thread shear in printed PETG across layers 20 MPa x 50 % thread fill x pi x Ø2.5 pilot x 8 mm engagement '
                                          '(EJOT PT practice in PC/ABS gives more); boss Ø8 = 3.2 x pilot',
                                 'v62_thumbturns': 'keys on bridged ledges, 8.1 MPa key bearing (v6.1.1)'},
        'shell_tabs_PT_K30x12': {'engagement_mm': 6.0, 'pullout_est_N': round(pull_pt_tab), 'worst_N_v61': F_tab, 'SF_pullout': round(pull_pt_tab / F_tab, 1)},
        'chute_PT_K30x10': {'engagement_mm': 6.0, 'pullout_est_N': round(pull_pt_tab), 'note': 'the chute carries only its own weight and the kibble friction'},
        'box_roof_P2_P3': {'head_punch_shear_MPa': round(tau_roof, 1), 'SF': round(TAU / tau_roof, 1)},
        'tower_pillars': {'stress_MPa': round(sig_pil, 1), 'SF_compression_50MPa': round(50.0 / sig_pil, 1)},
        'flange_wood_screws': LC62['flange_wood_screws'], 'bayonet_lugs_hooks': LC62['bayonet_lugs_hooks'],
        'gate_blade_column': LC62['gate_blade_column'], 'gate_ring_fox': LC62['gate_ring_fox'] | {'note': 'ring unchanged except the window shape'},
        'fox_bite_outlet_rim': {'assumed_N': 250, 'canine_tip_mm': 3.0, 'v62_web_mm': 2.76, 'v63_web_mm': web_B,
                                'v63_punching_shear_MPa': round(250 / (math.pi * 3.0 * min(web_B, 8.0)), 1), 'v63_SF': round(TAU / (250 / (math.pi * 3.0 * min(web_B, 8.0))), 1),
                                'note': 'the Ø24 thumb-turn dishes are gone; the nearest cut to the outlet chamfer is the B counterbore Ø7'},
        'fox_bite_panel': {'knock_out_skin_mm': KO['skin'], 'skin_under_engraving_mm': round(KO['skin'] - KO['engr'], 2),
                           'punching_shear_MPa_plain': round(F_KO / (math.pi * 3.0 * KO['skin']), 1),
                           'SF_plain': round(TAU / (F_KO / (math.pi * 3.0 * KO['skin'])), 2),
                           'SF_on_the_engraving': round(TAU / (F_KO / (math.pi * 3.0 * (KO['skin'] - KO['engr']))), 2),
                           'v63_first_issue': 'SF 0.75 (0.8 mm skin at the bottom of a Ø17 x 9.5 recess)',
                           'note': 'knock-outs are now flush: a canine tip meets a 2.0 mm wall (1.7 on the engraved line) at the surface instead of a 0.8 mm '
                                   'skin at the bottom of a cup; nothing to hook a claw into (0.3 mm engraving only)'},
        'panel_button': {'press_N': 10.0, 'mount_wall_mm': REC['wall'], 'note': 'the 3 mm mount wall is backed by the Ø23 boss and radial ribs of the pocket'}}
print(json.dumps(LOAD, indent=1, default=str))

# ---------------- grams, printed pieces, screws, inserts, colour swaps: before (v6.2) / after (v6.3) ----------------
print('\n--- grams / pieces ---')
PLATES62 = os.path.join(dt.HERE, '..', '..', 'v6.2', 'plates', '')   # the committed v6.2 print package (baseline)
SUM62 = json.load(open(PLATES62 + 'summary.json'))
PCS62 = [(p_['id'], p_['material'], p_['qty'], p_['colours']) for p_ in SUM62['parts_checklist'] if p_['kind'] == 'part']
STL62 = PLATES62 + 'stl/'
REUSED = ['guscio_v611', 'disco_v61', 'piastra_gate_v62', 'piastra_finestra_v62', 'scivolo_v611', 'colletto_v6', 'pulsante_v611', 'albero_v6', 'mozzo_v6',
          'labbro_pettine_v62', 'guarnizione_baionetta_v61', 'guarnizione_fondello_v61', 'guarnizione_piano_v5', 'labbro_ombra_v611', 'labbro_scivolo_v611']
PCS63 = [('guscio_v611', 'PETG', 1, ['black']), ('fondello_v63', 'PETG', 1, ['black']), ('chiocciola_v63', 'PETG', 1, ['black']),
         ('flangia_piano_v63', 'PETG', 1, ['black']), ('flangia_alta_v63', 'PETG', 1, ['black']), ('disco_v61', 'PETG', 1, ['orange', 'black']),
         ('piastra_gate_v62', 'PETG', 1, ['black', 'green']), ('piastra_finestra_v62', 'PETG', 1, ['black', 'green']), ('saracinesca_v63', 'PETG', 1, ['green']),
         ('anello_saracinesca_v63', 'PETG', 1, ['orange']), ('scivolo_v611', 'PETG', 1, ['green']), ('colletto_v6', 'PETG', 1, ['green']),
         ('linguetta_sicura_v63', 'PETG', 1, ['orange']), ('pulsante_v611', 'PETG', 1, ['orange']), ('colonna_v63', 'PETG', 1, ['black']),
         ('albero_v6', 'PETG', 1, ['black']), ('mozzo_v6', 'PETG', 1, ['black']), ('scatola_v63', 'PETG', 1, ['black']),
         ('labbro_pettine_v62', 'TPU', 4, ['yellow']), ('guarnizione_baionetta_v61', 'TPU', 1, ['yellow']), ('guarnizione_fondello_v61', 'TPU', 1, ['yellow']),
         ('guarnizione_piano_v5', 'TPU', 1, ['yellow']), ('labbro_ombra_v611', 'TPU', 1, ['yellow']), ('labbro_scivolo_v611', 'TPU', 1, ['yellow']),
         ('passacavo_v63', 'TPU', 1, ['yellow'])]


def grams_of(pid, mat, newset):
    f = current(OUT + pid + '.stl') if (pid in newset or not os.path.exists(STL62 + pid + '_print.stl')) else (STL62 + pid + '_print.stl')
    m = LD(f)
    return v6.grams_est(m, TPU if mat.startswith('TPU') else PETG)


G62 = {pid: {'qty': q, 'material': mat, 'grams_print_est_each': grams_of(pid, mat, set())[1]} for pid, mat, q, c in PCS62}
G63 = {pid: {'qty': q, 'material': mat, 'grams_print_est_each': grams_of(pid, mat, set(P))[1]} for pid, mat, q, c in PCS63}
tot = lambda G, mat: round(sum(v['qty'] * v['grams_print_est_each'] for v in G.values() if v['material'].startswith(mat)), 1)
pieces = lambda L, mat=None: sum(q for pid, m_, q, c in L if mat is None or m_.startswith(mat))
GRAMS = {'method': 'CAD estimate as v6.2: 1.2 mm shell over the whole surface + 15 % infill of the rest, PETG 1.27 / TPU 1.21 (same formula both versions); '
                   'slicer figures for v6.2 in print_v62/summary.json',
         'v62': {'PETG_g': tot(G62, 'PETG'), 'TPU_g': tot(G62, 'TPU'), 'pieces': pieces(PCS62), 'PETG_pieces': pieces(PCS62, 'PETG'), 'TPU_pieces': pieces(PCS62, 'TPU'),
                 'parts': len(PCS62), 'slicer_PETG_g': SUM62['totals']['grams_PETG'], 'slicer_colour_swaps': SUM62['totals']['colour_swaps']},
         'v63': {'PETG_g': tot(G63, 'PETG'), 'TPU_g': tot(G63, 'TPU'), 'pieces': pieces(PCS63), 'PETG_pieces': pieces(PCS63, 'PETG'), 'TPU_pieces': pieces(PCS63, 'TPU'),
                 'parts': len(PCS63)},
         'per_part_v62': G62, 'per_part_v63': G63}
GRAMS['delta_pieces_pct'] = round(100 * (GRAMS['v63']['pieces'] - GRAMS['v62']['pieces']) / GRAMS['v62']['pieces'], 1)
GRAMS['delta_PETG_g'] = round(GRAMS['v63']['PETG_g'] - GRAMS['v62']['PETG_g'], 1)
GRAMS['delta_PETG_pct'] = round(100 * GRAMS['delta_PETG_g'] / GRAMS['v62']['PETG_g'], 1)
GRAMS['gate_ring_upper_plate_g'] = {'v62': round(sum(G62[k]['grams_print_est_each'] for k in ('flangia_alta_v62', 'saracinesca_v62', 'anello_saracinesca_v62')), 1),
                                     'v63': round(sum(G63[k]['grams_print_est_each'] for k in ('flangia_alta_v63', 'saracinesca_v63', 'anello_saracinesca_v63')), 1)}


def mixed_layers(bodies_print):
    """layers (0.2 mm) in which two or more colour bodies are printed"""
    zl = []
    for m in bodies_print:
        zl.append((m.bounds[0, 2], m.bounds[1, 2]))
    hi = max(b[1] for b in zl)
    n = 0
    for z in np.arange(0.1, hi, 0.2):
        n += sum(1 for a, b in zl if a <= z <= b) >= 2
    return int(n)


SW62 = {'saracinesca_v62': mixed_layers([LD(OUT + 'saracinesca_v62_print_green.stl'), LD(OUT + 'saracinesca_v62_print_orange.stl')])}
SWAPS = {'model': 'colour swaps follow the mixed-colour layers; the v6.2 blade had green + orange in every one of its layers',
         'v62_blade_mixed_layers': SW62['saracinesca_v62'], 'v63_blade_mixed_layers': 0,
         'v62_slicer_total': SUM62['totals']['colour_swaps'], 'v63_estimate_total': SUM62['totals']['colour_swaps'] - SW62['saracinesca_v62'],
         'note': 'print the single-colour green blade on the green food-path plate; disc and the two plates keep their 3-layer inlays'}
HW = {'screws': {'v62': {'wood 5x35 pan': 4, 'ST2.9x9.5 flange join': 3, 'wood 3.5x16 channel': 4, 'M3x10 chute': 2, 'M3x12 shell tabs': 3, 'M3x40 stack': 3,
                         'M3x8 servo + hub': 5},
                  'v63': {'wood 5x35 pan': 4, 'PT K30x10 chute': 2, 'PT K30x12 shell tabs': 3, 'PT K30x12 cap': 3, 'M3x40 stack': 3, 'M3x8 servo + hub': 5}},
      'inserts': {'v62': 12, 'v63': len(P_SCREWS) + len(b61.SERVO_HOLES_W)},
      'o_rings': {'v62': {'9x2': 2, '24x2': 1, '8x1.5': 3, '132x2': 1, '14x1.5': 1, '3x1': 2},
                  'v63': {'9x2': 2, '24x2': 1, '132x2': 1, '14x1.5': 1, '3x1': 5, '5x1 (light pipes)': 2}},
      'other': {'v62': {'keys 3x3x18': 3, 'dowel 4x6 (print_v62 deviation)': 1}, 'v63': {'dowel 4x6 (in the CAD)': 1, 'cable tie 3.6 x 140 UV PA66': 1}}}
for k in ('screws', 'o_rings', 'other'):
    HW[k]['v62_total'] = sum(HW[k]['v62'].values()); HW[k]['v63_total'] = sum(HW[k]['v63'].values())
print(json.dumps({k: v for k, v in GRAMS.items() if not k.startswith('per_part')}, indent=1))
print(SWAPS, json.dumps(HW))

# ---------------- assembled-position files ----------------
ASM_NOT_WT = []


def save(name, m):
    p_ = ASM + name + '.stl'
    v6.clean(m).export(staged(p_))                         # hidden temp name, renamed with all other outputs at the end
    if not trimesh.load(current(p_)).is_watertight:
        ASM_NOT_WT.append(name)
    return p_


FILES = {k: OUT + k + '.stl' for k in P}
FILES['saracinesca_closed'] = save('saracinesca_v63_chiusa', BLADE[G_CLOSED])
FILES['anello_closed'] = save('anello_saracinesca_v63_chiuso', RINGP[G_CLOSED])
FILES['colletto'] = save('colletto_v6_v63pos', COLLAR)
FILES['gsk_piano'] = save('guarnizione_piano_v5_v63pos', GSK_PIANO)
for k, m in LIPS.items():
    FILES[k] = save(k, m)
FILES['labbri_x4'] = save('labbro_pettine_v62_x4', U(list(LIPS.values())))
for k, m in list(BOUGHT.items()) + list(SCREWS.items()):
    FILES[k] = save('bought_' + k.replace('.', '_'), m)
CAP_BANDS = [('fondello_v63_fondo', -200, -99.0), ('fondello_v63_fianco', -99.0, -86.0), ('fondello_v63_bordo', -86.0, 0.0)]
_pcx = pod_circle(0.0, Z_E)[0]


def _sector(a0, a1):
    a = np.radians(np.linspace(a0, a1, 60))
    return prism(Polygon(np.r_[[[_pcx, 0.0]], np.c_[_pcx + 200 * np.cos(a), 200 * np.sin(a)]]).intersection(sbox(-300, 20.0, 300, 300)), -120.0, -60.0)


PANEL_CUTS = [22.0, 59.0, 94.0, 110.0, 127.5, 148.0]          # viewer copies: panel in 5 pieces cut between the elements (each ~<= 16k faces, not decimated)
_rest = D(P['fondello_v63'], [_sector(PANEL_CUTS[0], PANEL_CUTS[-1])])
for nm, z0, z1 in CAP_BANDS:
    FILES[nm] = save(nm, I(_rest, box(-200, 200, -200, 200, z0, z1)))
PANEL_PIECES = []
for k, (a0, a1) in enumerate(zip(PANEL_CUTS[:-1], PANEL_CUTS[1:])):
    nm = 'fondello_v63_pannello' + ('' if k == 0 else f'_{k + 1}')
    FILES[nm] = save(nm, I(P['fondello_v63'], _sector(a0, a1)))
    PANEL_PIECES.append(nm)
print('assembled-position copies written; not watertight on reload:', ASM_NOT_WT)

exec(open(dt.HERE + 'build_v63_report.py').read())
