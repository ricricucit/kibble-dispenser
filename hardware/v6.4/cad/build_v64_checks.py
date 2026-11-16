# executed by build_v64.py (exec) in its namespace: unchanged / changed parts (hashes), interference, module insertion sweep,
# dry-volume flood fill (servo bay and module, each on its own), seals, tool access, panel probes, knock-outs, module
# envelope, load case, grams / pieces / hardware for chassis and module, assembled copies; then build_v64_report.py
import time
import glob
from scipy.spatial import cKDTree
from scipy import ndimage
sys.path.insert(0, dt.HERE)                           # toolaccess.py and los.py live next to the scripts
from toolaccess import check_screw, axial_hits
t_start = time.time()
PANEL = EXTRA['PANEL']
BOTTOM_FILL = EXTRA['BOTTOM_FILL']
LD = lambda f: v6.clean(trimesh.load(f))
V63 = json.load(open(OUT + 'v63.json'))
print('\n--- context ---')

# ---------------- unchanged parts: the 6.3.0 files themselves (hash of the print STL) ----------------
UNCHANGED = ['chiocciola_v63', 'colonna_v63', 'flangia_piano_v63', 'flangia_alta_v63', 'saracinesca_v63', 'anello_saracinesca_v63', 'passacavo_v63',
             'linguetta_sicura_v63', 'disco_v61', 'piastra_gate_v62', 'piastra_finestra_v62', 'scivolo_v611', 'colletto_v6', 'pulsante_v611', 'albero_v6',
             'mozzo_v6', 'labbro_pettine_v62', 'guarnizione_baionetta_v61', 'guarnizione_piano_v5', 'labbro_ombra_v611', 'labbro_scivolo_v611']
REPLACED = {'scatola_v63': 'scatola_v64', 'fondello_v63': 'fondello_v64', 'guscio_v611': 'guscio_v64', 'guarnizione_fondello_v61': 'guarnizione_fondello_v64'}


def sha(f):
    return hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16]


def mesh_sig(f):
    m = trimesh.load(f)
    return {'faces': int(len(m.faces)), 'volume_cm3': round(float(abs(m.volume)) / 1000, 3), 'bounds': np.round(m.bounds, 2).tolist()}


SAFE = {}
for k in UNCHANGED:
    f = OUT + k + '.stl'
    fp = OUT + k + '_print.stl'
    SAFE[k] = {'file': k + '.stl', 'sha256_16': sha(f), 'print_file': (k + '_print.stl') if os.path.exists(fp) else None,
               'print_sha256_16': sha(fp) if os.path.exists(fp) else None,
               'byte_identical_to_6_3_0': True, 'how': 'v6.4 uses the 6.3.0 file itself (not rebuilt, not re-exported)'}
# the 6.3.0 release list as recorded in v63.json: every unchanged part must be one of its files or a part it reused
_rel63 = set(V63['files'].keys()) | set(V63['reused_unchanged'])
SAFE_OK = all((k in _rel63) for k in UNCHANGED)
CHANGED = {}
for old, new in REPLACED.items():
    a, b_ = mesh_sig(OUT + old + '.stl'), {'faces': int(len(P[new].faces)), 'volume_cm3': round(float(P[new].volume) / 1000, 3), 'bounds': np.round(P[new].bounds, 2).tolist()}
    CHANGED[new] = {'replaces': old, 'v63': a, 'v64': b_, 'identical': a == b_}
print('unchanged parts', len(SAFE), 'all in the 6.3.0 release list:', SAFE_OK)

# ---------------- context solids ----------------
R = {k: LD(OUT + k + '.stl') for k in ('chiocciola_v63', 'colonna_v63', 'scivolo_v611', 'labbro_scivolo_v611', 'pulsante_v611', 'linguetta_sicura_v63',
                                         'labbro_ombra_v611', 'flangia_piano_v63')}
SHAFT, HUB = v6.build_shaft(), v6.build_hub()
CB, CS = chassis_bought()
MB, MS = module_bought(PANEL)
STACK = LD(OUT + 'v63_asm/bought_m3x40_stack.stl')
TABSCR = LD(OUT + 'v63_asm/bought_pt_k30x12_shell_tabs.stl')
CHUTESCR = LD(OUT + 'v63_asm/bought_pt_k30x10_chute.stl')
CHASSIS = {'scatola_v64': P['scatola_v64'], 'fondello_v64': P['fondello_v64'], 'guscio_v64': P['guscio_v64'], 'guarnizione_fondello_v64': P['guarnizione_fondello_v64'],
           'albero_v6': SHAFT, 'mozzo_v6': HUB, 'm3x40_stack': STACK, 'pt_k30x12_shell_tabs': TABSCR, 'pt_k30x10_chute': CHUTESCR}
CHASSIS.update(R); CHASSIS.update(CB); CHASSIS.update(CS)
MODULE = {k: P[k] for k in MODULE_NEW}
MODULE.update(MB); MODULE.update(MS)
MOD_KEYS = set(MODULE) | {'m3x16_module_lock'}
ALL = dict(CHASSIS); ALL.update(MODULE)
NEWSET = set(CHASSIS_NEW) | set(MODULE) | set(CB) | set(CS)
SOFT_ROLE = {
    ('guarnizione_fondello_v64', 'scatola_v64'): 'servo bay seal: cap lip on the bay rim face', ('guarnizione_fondello_v64', 'fondello_v64'): 'cap lip in its groove',
    ('modulo_guarnizione_v64', 'modulo_vasca_v64'): 'module seal: lid lip on the tub land', ('modulo_guarnizione_v64', 'modulo_coperchio_v64'): 'lid lip in its groove',
    ('oring_shaft_9x2', 'colonna_v63'): 'shaft O-rings in the bushing', ('oring_shaft_9x2', 'albero_v6'): 'shaft O-rings in their grooves',
    ('oring_face_24x2', 'colonna_v63'): 'face O-ring in the tower groove', ('oring_face_24x2', 'scatola_v64'): 'face O-ring on the bay plateau',
    ('oring_3x1', 'scatola_v64'): 'O-ring 3x1 under the stack screw heads', ('oring_3x1', 'm3x40_stack'): 'O-ring 3x1 on the shank',
    ('oring_3x1_cap', 'fondello_v64'): 'O-ring 3x1 in the cap counterbore', ('oring_3x1_cap', 'pt_k30x12_cap'): 'O-ring 3x1 under the cap screw head',
    ('pt_k30x12_cap', 'scatola_v64'): 'thread-forming engagement in the bay bosses',
    ('oring_3x1_lid', 'modulo_coperchio_v64'): 'O-ring 3x1 in the lid countersink', ('oring_3x1_lid', 'pt_k30x10_lid'): 'O-ring 3x1 under the lid screw head',
    ('pt_k30x10_lid', 'modulo_vasca_v64'): 'thread-forming engagement in the tub bosses', ('pt_k30x10_lid', 'modulo_coperchio_v64'): 'lid screw head in the O-ring countersink',
    ('switch_12mm_ip67', 'modulo_vasca_v64'): 'panel switch: front gasket on the recess floor + thread in the hole',
    ('oring_5x1_lightpipe', 'modulo_vasca_v64'): 'light-pipe O-ring in its counterbore', ('oring_5x1_lightpipe', 'lightpipes_5mm'): 'light-pipe O-ring under the flange',
    ('lightpipes_5mm', 'modulo_vasca_v64'): 'light pipe flange on the boss face', ('membrane_acoustic_ip67', 'modulo_vasca_v64'): 'adhesive acoustic membrane on the floor',
    ('labbro_scivolo_v611', 'fondello_v64'): 'chute lip anchor', ('labbro_scivolo_v611', 'scivolo_v611'): 'chute lip on the chute',
    ('labbro_ombra_v611', 'guscio_v64'): 'shadow-gap skirt lip on the shell', ('labbro_ombra_v611', 'flangia_piano_v63'): 'skirt lip anchor',
    ('socket_m8_5p', 'modulo_coperchio_v64'): 'J1 panel socket in the lid (thread in the hole, nut + O-ring)', ('gland_m12', 'scatola_v64'): 'gland thread in the bay wall',
    ('vent_patch_eptfe', 'scatola_v64'): 'adhesive vent patch on the bay wall', ('inserts_servo', 'scatola_v64'): 'heat-set inserts', ('inserts_holder', 'scatola_v64'): 'heat-set inserts',
    ('m3x16_module_lock', 'inserts_holder'): 'lock screws in the inserts', ('m3x16_module_lock', 'scatola_v64'): 'lock screw tip in the insert bore',
    ('m3x8_servo', 'inserts_servo'): 'servo screws in the inserts', ('m3x8_servo', 'scatola_v64'): 'servo screws in the insert bores', ('m3x8_servo', 'servo'): 'servo screws through the tabs',
    ('m3x8_hub', 'mozzo_v6'): 'hub screw', ('m3x8_hub', 'servo'): 'hub screw in the servo spline', ('mozzo_v6', 'servo'): 'hub on the spline', ('mozzo_v6', 'albero_v6'): 'spline coupling',
    ('m3x40_stack', 'scatola_v64'): 'stack screws through the roof', ('m3x40_stack', 'colonna_v63'): 'stack screws through the tower', ('m3x40_stack', 'chiocciola_v63'): 'stack screws in the bowl inserts',
    ('pt_k30x12_shell_tabs', 'guscio_v64'): 'shell tab screws', ('pt_k30x12_shell_tabs', 'chiocciola_v63'): 'thread-forming engagement', ('pt_k30x10_chute', 'scivolo_v611'): 'chute screws',
    ('pt_k30x10_chute', 'chiocciola_v63'): 'thread-forming engagement', ('plug_m8_5p_angled', 'socket_m8_5p'): 'J1 mated', ('harness_12v', 'plug_m8_5p_angled'): 'cable into the plug',
    ('harness_servo', 'plug_m8_5p_angled'): 'cable into the plug', ('harness_12v', 'harness_servo'): 'Y split', ('harness_12v', 'connector_m8_ip67'): 'pigtail into the pod-top M8',
    ('harness_servo', 'gland_m12'): 'servo lead through the gland', ('servo_lead_in_bay', 'gland_m12'): 'servo lead through the gland', ('servo_lead_in_bay', 'servo'): 'servo lead',
    ('board_70x50_A', 'esp32_wrover_stack'): 'on the board', ('board_70x50_A', 'reg_6v'): 'on the board', ('board_70x50_A', 'reg_5v'): 'on the board',
    ('speaker_23mm', 'modulo_anello_speaker_v64'): 'speaker in its ring', ('leds_3mm', 'lightpipes_5mm'): 'LED behind the light pipe',
    ('oring_btn_14x1.5', 'guscio_v64'): 'button O-ring',
    ('harness_tail', 'plug_m8_5p_angled'): 'tail into the plug', ('harness_tail', 'harness_12v'): 'both leave the Y splice', ('harness_tail', 'harness_splice_y'): 'tail out of the Y splice',
    ('harness_12v', 'harness_splice_y'): '12 V branch out of the Y splice', ('harness_servo', 'harness_splice_y'): 'servo branch out of the Y splice',
    ('cable_tie_harness', 'harness_tail'): 'tie round the tail', ('cable_tie_harness', 'scatola_v64'): 'tie through the lug slot',
    ('harness_servo', 'jr_3p_junction'): 'servo branch into the JR female', ('servo_lead_in_bay', 'jr_3p_junction'): 'servo lead into the JR pair'}
SOFT = {frozenset(k): v for k, v in SOFT_ROLE.items()}


def bb_overlap(a, b, pad=0.05):
    return bool(np.all(a.bounds[0] <= b.bounds[1] + pad) and np.all(b.bounds[0] <= a.bounds[1] + pad))


def vol_i(a, b):
    if not bb_overlap(a, b):
        return 0.0
    try:
        return round(vol(I(a, b)), 4)
    except Exception:
        return round(vol(I(a.convex_hull if not a.is_volume else a, b.convex_hull if not b.is_volume else b)), 4)


print('\n--- interference (mm3) ---')
inter, soft = {}, {}
names = list(ALL)
for i, a in enumerate(names):
    for b_ in names[i + 1:]:
        key = frozenset((a, b_))
        if a not in NEWSET and b_ not in NEWSET:
            continue
        v = vol_i(ALL[a], ALL[b_])
        (soft if key in SOFT else inter)[f'{a}|{b_}'] = v
        if key not in SOFT and v > 1e-3:
            print(f'  HARD {a:30s}|{b_:30s} {v:.4f}', np.round(I(ALL[a], ALL[b_]).bounds, 1).tolist())
HARD_MAX = max(inter.values())
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3; {len(soft)} designed contacts')
print(f'interference done {time.time() - t_start:.0f} s')

# ---------------- module insertion / removal sweep (straight down, connector unplugged) ----------------
MOD_SOLID = U([P['modulo_vasca_v64'], P['modulo_coperchio_v64'], MS['pt_k30x10_lid'], MB['socket_m8_5p']])
CH_SOLID = U([P['scatola_v64'], P['fondello_v64'], P['guscio_v64'], P['guarnizione_fondello_v64'], R['chiocciola_v63'], R['colonna_v63'], R['scivolo_v611'],
              CB['servo'], CB['gland_m12'], STACK, CS['pt_k30x12_cap'], TABSCR])
SWEEP_M = []
for dz in (0.0, 1.0, 2.0, 4.0, 8.0, 15.0, 30.0, 45.0, 60.0, 75.0, 100.0):
    m = MOD_SOLID.copy(); m.apply_translation([0, 0, -dz])
    SWEEP_M.append((dz, round(vol(I(m, CH_SOLID)), 4)))
SWEEP_M_MAX = max(v for _, v in SWEEP_M)
print('module removal sweep (dz, mm3):', SWEEP_M)
# plug reach: with the module lowered by 30 the J1 plug stands in the window between the module top and the shell edge
# ---------------- chassis harness: tail length, parked service loop, lowered reach, drape during the travel ----------------
print('\n--- harness ---')
L_PARK = path_len(tail_points())
L_TAIL = float(math.ceil((L_PARK + 2.0) / 5.0) * 5.0)
REACH = {}
for D_ in range(80, 161, 5):
    REACH[D_] = round(path_len(tail_points(D_)), 1)
D_MAX = max(D_ for D_, L_ in REACH.items() if L_ <= L_TAIL - 5.0)
TAIL_LOW = tube_path(tail_points(80.0), HARN['r_tail'], 16)
PLUG80 = CB['plug_m8_5p_angled'].copy(); PLUG80.apply_translation([0, 0, -80.0])
MOD80 = MOD_SOLID.copy(); MOD80.apply_translation([0, 0, -80.0])
DRAPE = []
p_fixed = np.array([EYELET['xy'][0], EYELET['xy'][1], EYELET['z0'] - 1.5])          # the tail leaves the chassis through the C-hook, inside the opening
for D_ in (0.0, 5.0, 10.0, 20.0, 30.0, 45.0, 60.0, 80.0):
    e_ = np.array([EYELET['xy'][0], EYELET['xy'][1], min(ZMT + HARN['r_tail'] + 0.6 - D_, p_fixed[2] - 0.5)])
    seg = tube_path([tuple(p_fixed), tuple(e_)], HARN['r_tail'], 16)
    mD = MOD_SOLID.copy(); mD.apply_translation([0, 0, -D_])
    DRAPE.append((D_, round(vol(I(seg, CH_SOLID)), 3), round(vol(I(seg, mD)), 3)))
PLUG_ACCESS = {'module_lowered_mm': 80.0, 'tail_allows_mm': D_MAX, 'J1_face_z_at_80': round(ZMT + J1['tur_h'] - 80.0, 1), 'pod_bottom_z': Z_BOT,
               'note': 'take the 2 lock screws out, let the module down: at 80 mm its top is 13 mm below the pod bottom and the plug ring is free in the hand; '
                       'unscrew the ring and set the module on the bench. Refit: plug, lay the loop on the lid between the back fence and the turret, push up'}
PLUG_ACCESS_OLD = {'lowered_by_mm': 30.0, 'window_z': [round(ZMT - 30.0, 2), round(ZSH, 2)], 'window_height_mm': round(ZSH - (ZMT - 30.0), 2), 'window_width_mm': round(2 * (YM + GAP), 1),
               'plug_top_z_when_lowered': round(ZMT + J1['tur_h'] + 15.0 - 30.0, 1), 'plug_axis_behind_the_skin_mm': round(float(sum(pod_circle(0.0, -55.0)) - math.hypot(J1['xy'][0] - pod_circle(0.0, -55.0)[0], J1['xy'][1])), 1),
               'harness_slack_needed_mm': 35, 'note': 'unscrew the knurled M8 ring through the window, then let the module slide out; no chassis part is touched'}

# ---------------- clearances ----------------
print('\n--- clearances ---')


def min_dist(a, b, spacing=0.5, refine=300):
    lo, hi = a.bounds[0] - 25.0, a.bounds[1] + 25.0
    bc = I(b, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    if bc is None or len(bc.faces) == 0:
        return [None, 'farther than 25 mm']
    pa, _ = trimesh.sample.sample_surface_even(a, int(max(300, min(40000, a.area / spacing ** 2))))
    pb, _ = trimesh.sample.sample_surface_even(bc, int(max(300, min(80000, bc.area / spacing ** 2))))
    d, _ = cKDTree(pb).query(pa)
    cand = pa[np.argsort(d)[:refine]]
    best, at_pt = 1e9, None
    for k in range(0, len(cand), 100):
        _, dd, _ = trimesh.proximity.closest_point(bc, cand[k:k + 100])
        j = int(np.argmin(dd))
        if dd[j] < best:
            best, at_pt = float(dd[j]), cand[k + j]
    return [round(best, 2), np.round(at_pt, 1).tolist()]


TUBLID = U([P['modulo_vasca_v64'], P['modulo_coperchio_v64']])
x3, y3 = P_SCREWS[2]
CLR = {'module_to_bay_and_cap': min_dist(I(TUBLID, box(XM0 - 1, XM0 + 6, -60, 60, -110, -30)), U([P['scatola_v64'], P['fondello_v64']])),
       'module_to_shell_opening_edges': min_dist(I(P['modulo_vasca_v64'], above(Z_S)), P['guscio_v64']),
       'module_to_cap_opening_edges': min_dist(I(P['modulo_vasca_v64'], below(Z_S - 1.0)), I(P['fondello_v64'], box(XM0 + 3, 200, -80, 80, -110, -70))),
       'lid_top_to_P3_pad': min_dist(P['modulo_coperchio_v64'], at(cyl(2 * P3_PAD['r'], P3_PAD['z0'], Z_R, 48), x3, y3)),
       'lid_screw_heads_to_chassis': min_dist(MS['pt_k30x10_lid'], U([P['scatola_v64'], R['colonna_v63'], R['chiocciola_v63'], P['guscio_v64']])),
       'J1_plug_to_bowl_tower_shell': min_dist(CB['plug_m8_5p_angled'], U([R['chiocciola_v63'], R['colonna_v63'], P['guscio_v64'], P['scatola_v64'], TABSCR])),
       'posts_to_module_sockets': min_dist(I(P['scatola_v64'], box(XM0, 40, -60, 60, -95, -47)), P['modulo_vasca_v64']),
       'switch_body_to_board_A': min_dist(MB['switch_12mm_ip67'], MB['board_70x50_A']),
       'esp_stack_to_tub': min_dist(MB['esp32_wrover_stack'], P['modulo_vasca_v64']),
       'esp_stack_to_switch_leds': min_dist(MB['esp32_wrover_stack'], U([MB['switch_12mm_ip67'], MB['leds_3mm'], MB['lightpipes_5mm']])),
       'speaker_to_switch': min_dist(MB['speaker_23mm'], MB['switch_12mm_ip67']),
       'J1_socket_body_to_esp_stack': min_dist(MB['socket_m8_5p'], MB['esp32_wrover_stack']),
       'servo_to_bay_walls': min_dist(CB['servo'], I(P['scatola_v64'], box(-16, 16, -42, 42, -72, -60.5))),
       'cap_boss_C_D_to_gland': min_dist(CB['gland_m12'], I(P['scatola_v64'], box(6, 16, -60, -41.5, -97, -30))),
       'P3_head_to_module_lid': min_dist(at(cyl(5.5, Z_R - ROOF_T - 3.0, Z_R - ROOF_T, 48), x3, y3), P['modulo_coperchio_v64']),
       'chute_to_cap_boss_A': min_dist(R['scivolo_v611'], I(P['scatola_v64'], box(-26, -17, 28, 38, -97, -30)))}
print(json.dumps(CLR, indent=0, default=str))
PINCH = {'tail_to_P3_pad': min_dist(CB['harness_tail'], at(cyl(2 * P3_PAD['r'], P3_PAD['z0'], Z_R, 48), *P_SCREWS[2])),
         'tail_to_shell_and_opening_edges': min_dist(CB['harness_tail'], P['guscio_v64']),
         'tail_to_posts_and_webs': min_dist(CB['harness_tail'], I(P['scatola_v64'], box(XM0 - 12, 32, -60, 60, -95, -29))),
         'tail_to_bowl_tabs_and_screws': min_dist(CB['harness_tail'], U([R['chiocciola_v63'], TABSCR])),
         'tail_to_lid_screw_heads': min_dist(CB['harness_tail'], MS['pt_k30x10_lid']),
         'splice_to_shell': min_dist(CB['harness_splice_y'], P['guscio_v64'])}
HARNESS = {'tail_parked_path_mm': round(L_PARK, 1), 'tail_length_spec_mm': L_TAIL, 'lowered_path_mm_by_D': REACH, 'max_lowering_with_5mm_spare_mm': D_MAX,
           'lowered_80_vs_chassis_mm3': round(vol(I(TAIL_LOW, CH_SOLID)), 3), 'lowered_80_vs_module_mm3': round(vol(I(TAIL_LOW, MOD80)), 3),
           'drape_during_travel (D, vs chassis mm3, vs module mm3)': DRAPE, 'parked_clearances_mm': PINCH}
print(json.dumps(HARNESS, indent=0, default=str))

# ---------------- seal continuity ----------------
print('\n--- seal continuity ---')


def sectors_ok(seal, mate, centre, n=36, rmax=200.0):
    cx_, cy_ = centre
    lo, hi = seal.bounds[0] - 1.0, seal.bounds[1] + 1.0
    mc = I(mate, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    res = []
    for k in range(n):
        a0, a1 = 360.0 * k / n, 360.0 * (k + 1) / n
        pts = [(0, 0)] + [(rmax * math.cos(math.radians(a)), rmax * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 6)]
        w = at(prism(Polygon(pts), lo[2] - 1, hi[2] + 1), cx_, cy_)
        res.append(round(vol(I(I(seal, w), mc)), 4))
    return {'sectors': n, 'min_overlap_mm3': min(res), 'all_in_contact': bool(min(res) > 0)}


CONT = {}
CONT['guarnizione_fondello_v64 | scatola_v64 (servo bay rim)'] = sectors_ok(P['guarnizione_fondello_v64'], P['scatola_v64'], (0.0, 0.0))
CONT['guarnizione_fondello_v64 | fondello_v64 (groove)'] = sectors_ok(P['guarnizione_fondello_v64'], P['fondello_v64'], (0.0, 0.0))
_lc = lid_gasket_centre().centroid.coords[0]
CONT['modulo_guarnizione_v64 | modulo_vasca_v64 (land)'] = sectors_ok(P['modulo_guarnizione_v64'], P['modulo_vasca_v64'], _lc, 48)
CONT['modulo_guarnizione_v64 | modulo_coperchio_v64 (groove)'] = sectors_ok(P['modulo_guarnizione_v64'], P['modulo_coperchio_v64'], _lc, 48)
for (x, y) in P_SCREWS[1:2]:
    orr = I(CB['oring_3x1'], at(cyl(8, -40, -25), x, y))
    CONT[f'oring_3x1 P2 ({x}, {y}) | scatola_v64'] = sectors_ok(orr, P['scatola_v64'], (x, y), 24)
for j, (x, y) in enumerate(LID_SCREWS):
    orr = I(MB['oring_3x1_lid'], at(cyl(8, ZMT - 3, ZMT + 3), x, y))
    CONT[f'oring_3x1 lid screw {j + 1} | lid countersink'] = sectors_ok(orr, P['modulo_coperchio_v64'], (x, y), 24)
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    sl = axial_cyl(Pk, nk, 12.0, LED['len'] - 1.5, LED['len'] + 0.5, 32)
    Tal = trimesh.geometry.align_vectors(-nk, [0, 0, 1]); Tal[:3, 3] = -Tal[:3, :3] @ (Pk - nk * LED['len'])
    o_, c_, l_ = [I(m, sl).copy() for m in (MB['oring_5x1_lightpipe'], P['modulo_vasca_v64'], MB['lightpipes_5mm'])]
    for m in (o_, c_, l_):
        m.apply_transform(Tal)
    CONT[f'oring_5x1 {k} | tub counterbore'] = sectors_ok(o_, c_, (0.0, 0.0), 24)
    CONT[f'oring_5x1 {k} | light pipe flange'] = sectors_ok(o_, l_, (0.0, 0.0), 24)
Pb, nb, _ = PANEL['frames']['btn']
sl = axial_cyl(Pb, nb, 20.0, REC['floor'] - 0.6, REC['floor'] + 0.4, 64)
Tal = trimesh.geometry.align_vectors(-nb, [0, 0, 1]); Tal[:3, 3] = -Tal[:3, :3] @ (Pb - nb * REC['floor'])
s_, c_ = [I(m, sl).copy() for m in (MB['switch_12mm_ip67'], P['modulo_vasca_v64'])]
for m in (s_, c_):
    m.apply_transform(Tal)
CONT['switch front gasket | recess floor'] = sectors_ok(D(s_, [cyl(12.3, -5, 5, 64)]), c_, (0.0, 0.0), 24)
for k, v in CONT.items():
    print(f'  {k:62s} {v}')
SEALS_OK = all(v['all_in_contact'] for v in CONT.values())

# ---------------- DRY VOLUMES: voxel flood fill of the pod below the tower (servo bay and module each on its own) ----------------
print('\n--- dry-volume flood fill ---')
PITCH_V = 0.4
ZV0, ZV1 = Z_BOT - 0.8, Z_R - 0.3
gx, gz = GLAND['x'], GLAND['z']
PLUGS = [b61.yprism(Point(gx, gz).buffer(8.8, resolution=24), BAY[2] - 3.0, BAY[2] - 1.0),                                           # gland hex + seal washer on the pad (covers the teardrop tip)
         box(BAY[0] - 0.3, BAY[0] + 2.6, VENT64['y'] - 1.6, VENT64['y'] + 1.6, VENT64['z'] - 1.6, VENT64['z'] + 1.6),              # vent patch over the Ø2 hole
         at(cyl(15.0, Z_BOT + FLOOR_M - 0.05, Z_BOT + FLOOR_M + 0.6, 48), SPK64['x'], SPK64['y']),                               # acoustic membrane
         at(cyl(J1['tur_id'] + 0.4, ZMT + J1['tur_h'] - J1['tur_top'] - 1.5, ZMT + J1['tur_h'] + 0.5, 32), *J1['xy'])]                                                        # J1 socket + its O-ring
PLUGS.append(axial_cyl(PANEL['frames']['btn'][0], PANEL['frames']['btn'][1], REC['hole'] + 0.3, REC['floor'] - 0.3, REC['floor'] + REC['wall'] + 0.5, 48))   # switch thread + front gasket in its hole
for x, y in LID_SCREWS:
    PLUGS.append(at(cyl(4.2, Z_LU - 0.6, ZMT + 0.6, 24), x, y))
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    PLUGS += [axial_cyl(Pk, nk, LED['hole'] + 0.02, -0.5, LED['len'] + 1.0, 32), axial_cyl(Pk, nk, LED['cb_d'] + 0.02, LED['len'] - LED['cb_depth'] - 0.02, LED['len'] + 0.3, 32)]
SOLIDS = [P[k] for k in P] + [MB['switch_12mm_ip67'], MB['lightpipes_5mm'], R['scivolo_v611'], R['labbro_scivolo_v611'], CS['pt_k30x12_cap'], CS['m3x16_module_lock']] + PLUGS
xs_ = np.arange(-86.0, 72.0, PITCH_V) + PITCH_V / 2
ys_ = np.arange(-78.0, 78.0, PITCH_V) + PITCH_V / 2
zs_ = np.arange(ZV0, ZV1, PITCH_V) + PITCH_V / 2
GX, GY = np.meshgrid(xs_, ys_, indexing='ij')
SLICE_FAIL = []
occ = np.zeros((len(xs_), len(ys_), len(zs_) + 1), bool)
occ[:, :, -1] = True                                         # closed top layer: tower face O-ring, P2 O-ring and the pod above (checked by continuity)
for k, z in enumerate(zs_):
    polys = []
    for m in SOLIDS:
        if m.bounds[0, 2] > z or m.bounds[1, 2] < z:
            continue
        for dz_ in (0.013, 0.031, -0.017, 0.05):               # never exactly on a 0.1 mm model plane                # a slice that fails to close is retried a hair higher / lower: never dropped
            try:
                s = m.section(plane_origin=[0, 0, z + dz_], plane_normal=[0, 0, 1])
                if s is None:
                    break
                T = np.eye(4); T[2, 3] = -(z + dz_)
                p2, _ = s.to_2D(to_2D=T)
                polys += list(p2.polygons_full)
                break
            except Exception:
                SLICE_FAIL.append((round(float(z), 2), dz_))
                continue
    if polys:
        un = shapely.unary_union(polys)
        shapely.prepare(un)
        occ[:, :, k] = shapely.contains_xy(un, GX, GY)
lab, nlab = ndimage.label(~occ)


def lab_at(p, search=3.0):
    i, j, k = int((p[0] - xs_[0]) / PITCH_V + 0.5), int((p[1] - ys_[0]) / PITCH_V + 0.5), int((p[2] - zs_[0]) / PITCH_V + 0.5)
    if lab[i, j, k]:
        return int(lab[i, j, k])
    rr = int(search / PITCH_V)
    sub = lab[max(i - rr, 0):i + rr + 1, max(j - rr, 0):j + rr + 1, max(k - rr, 0):k + rr + 1]
    idx = np.argwhere(sub > 0)
    if not len(idx):
        return 0
    c = np.array([min(i, rr), min(j, rr), min(k, rr)])
    return int(sub[tuple(idx[np.argmin(np.linalg.norm(idx - c, axis=1))])])


SEEDS = {'servo bay: beside the servo (south room)': (0.0, -30.0, -60.0), 'servo bay: under the servo, in the cap': (0.0, 10.0, -96.0), 'servo bay: servo void': (11.5, 10.0, -55.0),
         'module: board zone': (45.0, 10.0, -62.0), 'module: north lobe': (38.0, 44.0, -60.0), 'module: floor under the speaker ring': (33.0, -6.0, -100.6),
         'module: behind the button': tuple(PANEL['frames']['btn'][0] - PANEL['frames']['btn'][1] * 22.0 + np.array([0, 0, 8.5])),
         'pod (wet side): north of the bay': (-5.0, 55.0, -60.0), 'pod (wet side): at the drain': (-48.0, 22.0, -99.5), 'pod (wet side): post socket gap': (24.0, 51.0, -60.0),
         'exterior: outside the pod': (0.0, -76.5, -90.0), 'exterior: outlet bore': (CH_X, 0.0, -95.0), 'exterior: button recess': tuple(PANEL['frames']['btn'][0] - PANEL['frames']['btn'][1] * 3.0)}
SEED_LAB = {k: lab_at(np.array(v)) for k, v in SEEDS.items()}
bay_l = {v for k, v in SEED_LAB.items() if k.startswith('servo bay')}
mod_l = {v for k, v in SEED_LAB.items() if k.startswith('module')}
oth_l = {v for k, v in SEED_LAB.items() if k.startswith('pod') or k.startswith('exterior')}
_vol = lambda ls: round(float(np.isin(lab, list(ls)).sum()) * PITCH_V ** 3 / 1000, 1)
DRY = {'voxel_mm': PITCH_V, 'z_range': [round(ZV0, 2), round(ZV1, 2)], 'seed_labels': SEED_LAB,
       'servo_bay_is_one_volume': len(bay_l) == 1 and 0 not in bay_l, 'module_is_one_volume': len(mod_l) == 1 and 0 not in mod_l,
       'servo_bay_separate_from_module_pod_exterior': not (bay_l & (mod_l | oth_l)), 'module_separate_from_bay_pod_exterior': not (mod_l & (bay_l | oth_l)),
       'servo_bay_free_volume_cm3': _vol(bay_l) if len(bay_l) == 1 else None, 'module_free_volume_cm3': _vol(mod_l) if len(mod_l) == 1 else None,
       'pod_drains_to_exterior': SEED_LAB['pod (wet side): at the drain'] == SEED_LAB['exterior: outside the pod'],
       'method': 'all 8 new printed parts, chute + chute lip, light pipes, cap and lock screws as solids; gland, vent patch, acoustic membrane, J1, lid screws, the switch in its hole '
                 'and light-pipe O-rings drawn as closed (their contact is in the continuity check); 0.4 mm voxels from the pod bottom to just under the bay roof top '
                 '(top layer closed); free voxels labelled with 6-connectivity; seeds in the bay, the module, the pod and outside'}
def leak_path(seed_a, seed_b):
    from collections import deque
    ia = tuple(int((np.array(seed_a)[q] - g[0]) / PITCH_V + 0.5) for q, g in enumerate((xs_, ys_, zs_)))
    ib = tuple(int((np.array(seed_b)[q] - g[0]) / PITCH_V + 0.5) for q, g in enumerate((xs_, ys_, zs_)))
    free = ~occ
    par = {ia: None}; dq = deque([ia]); found = None
    while dq:
        c_ = dq.popleft()
        if abs(c_[0] - ib[0]) + abs(c_[1] - ib[1]) + abs(c_[2] - ib[2]) <= 3:
            found = c_; break
        for dv_ in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            nb_ = (c_[0] + dv_[0], c_[1] + dv_[1], c_[2] + dv_[2])
            if 0 <= nb_[0] < free.shape[0] and 0 <= nb_[1] < free.shape[1] and 0 <= nb_[2] < free.shape[2] - 1 and free[nb_] and nb_ not in par:
                par[nb_] = c_; dq.append(nb_)
    path = []
    while found is not None:
        path.append((round(float(xs_[found[0]]), 1), round(float(ys_[found[1]]), 1), round(float(zs_[found[2]]), 1))); found = par[found]
    return path[::-1][::max(1, len(path) // 30)]


if bay_l & oth_l:
    DRY['leak_bay_to_pod'] = leak_path(SEEDS['servo bay: beside the servo (south room)'], SEEDS['pod (wet side): north of the bay'])
if mod_l & oth_l:
    DRY['leak_module_to_pod'] = leak_path(SEEDS['module: board zone'], SEEDS['pod (wet side): north of the bay'])
DRY_OK = DRY['servo_bay_is_one_volume'] and DRY['module_is_one_volume'] and DRY['servo_bay_separate_from_module_pod_exterior'] and DRY['module_separate_from_bay_pod_exterior']
DRY['slices_retried'] = len(SLICE_FAIL)
print(DRY)

# ---------------- module envelope ----------------
print('\n--- module envelope ---')
X_BACK = XM0 + WALL_B


def x_in(y, z):
    """inner face of the skin wall at (y, z): pod offset WALL_M, or the band wall where the band is"""
    c, r = pod_circle(WALL_M, z)
    x = c + math.sqrt(max(r * r - y * y, 0.0))
    if ZB0 - 1.0 <= z <= ZB1 + 1.0:
        cb, _ = pod_circle(0.0, z)
        rb = band_rho(z) - BAND_WALL
        x = min(x, cb + math.sqrt(max(rb * rb - y * y, 0.0)))
    return x


def box_depth(w, z0, z1):
    return round(min(x_in(w, z) for z in np.linspace(z0, z1, 12)) - X_BACK, 1)


Z_FLOOR, Z_UNDER_RIM = Z_BOT + FLOOR_M, Z_RIM0 - (O_SKIN - WALL_M)
ENVELOPE = {'inner_height_floor_to_land_mm': round(Z_LAND - Z_FLOOR, 1), 'inner_height_under_the_rim_mm': round(Z_UNDER_RIM - Z_FLOOR, 1),
            'inner_width_between_guides_mm': 2 * GUIDE_Y, 'board_slot_width_mm': round(2 * (GUIDE_Y + SLOTS['depth']), 1), 'inner_width_front_mm': round(2 * (YM - WALL_S), 1),
            'depth_back_wall_to_skin_mm': {f'z {z:.0f}': {f'y {y:.0f}': round(x_in(y, z) - X_BACK, 1) for y in (0, 20, 30, 34)} for z in (-50, -60, -72, -87, -98)},
            'free_volume_cm3': DRY['module_free_volume_cm3'],
            'boxes_that_fit (y width x z height x x depth)': {
                '68 x 50 x d (board zone, z -96..-46)': box_depth(34.0, -96.0, -46.0), '68 x 40 x d (z -86..-46)': box_depth(34.0, -86.0, -46.0),
                '60 x 45 x d (z -95..-50)': box_depth(30.0, -95.0, -50.0), '40 x 50 x d (z -96..-46)': box_depth(20.0, -96.0, -46.0),
                '61 x 28 x d (ESP zone z -78..-50)': box_depth(30.5, -78.0, -50.0)},
            'target_80x60x45': 'not feasible in this pod: the bay wall is at x 15.25 and the skin 59-65 from the axis, so the depth is 35-43 on the centre line and falls to '
                               '25-33 at y +-34; width 68 between the guides (99 across the front lobes), height 61',
            'slots': {'A_board_back_x': SLOTS['A'], 'B_board_back_x': SLOTS['B'], 'pitch_mm': SLOTS['B'] - SLOTS['A'], 'behind_A_mm': round(SLOTS['A'] - X_BACK, 1),
                      'stack_in_front_of_A_mm (centre 61 x 28, z -78..-50)': round(box_depth(30.5, -78.0, -50.0) - (SLOTS['A'] - X_BACK) - 1.6, 1),
                      'between_A_and_B_mm': round(SLOTS['B'] - SLOTS['A'] - 1.6, 1),
                      'in_front_of_B_mm (z -86..-46, 68 wide / 40 wide)': [round(box_depth(34.0, -86.0, -46.0) - (SLOTS['B'] - X_BACK) - 1.6, 1), round(box_depth(20.0, -86.0, -46.0) - (SLOTS['B'] - X_BACK) - 1.6, 1)],
                      'use': 'A alone takes the ESP32 perfboard with its 25 mm stack; A + B together only if the board in A carries parts <= the gap between A and B (regulators) and the board in B '
                             'parts <= the depth in front of B'}}
print(json.dumps(ENVELOPE, indent=0))

# ---------------- tool access ----------------
print('\n--- tool access ---')
ST5 = {'chiocciola_v63': R['chiocciola_v63'], 'colonna_v63': R['colonna_v63'], 'scivolo_v611': R['scivolo_v611'], 'guscio_v64': P['guscio_v64'], 'pulsante_v611': R['pulsante_v611'],
       'scatola_v64': P['scatola_v64'], 'servo': CB['servo'], 'gland_m12': CB['gland_m12'], 'mozzo_v6': HUB, 'm3x8_servo': CS['m3x8_servo'], 'tab_screws': TABSCR, 'chute_screws': CHUTESCR}
zs_stack = [EAR_Z0, Z_R - ROOF_T, Z_R - ROOF_T]
TA = {}
for j, ((x, y), zs) in enumerate(zip(P_SCREWS, zs_stack)):
    st = dict(ST5)
    for k, ((x2, y2), z2) in enumerate(zip(P_SCREWS, zs_stack)):
        if k != j:
            st[f'stack_head_{k}'] = at(cyl(5.5, z2 - 3.0, z2, 24), x2, y2)
    TA[f'step 5 bay+tower -> bowl M3x40 P{j + 1} ({x:.2f}, {y:.1f}) (cap and module not in)'] = check_screw(st, (x, y, zs - 3.0), (0, 0, -1))
ST6 = dict(ST5, fondello_v64=P['fondello_v64'], lip=P['guarnizione_fondello_v64'], chute_lip=R['labbro_scivolo_v611'], stack=STACK)
for nm_, (x, y) in CAP64.items():
    st = dict(ST6)
    for nm2, (x2, y2) in CAP64.items():
        if nm2 != nm_:
            st[f'cap_head_{nm2}'] = at(cyl(PT['head_d'], CAP_SEAT_Z - PT['head_h'], CAP_SEAT_Z, 32), x2, y2)
    TA[f'step 6 cap -> bay PT K30x12 {nm_} ({x:.1f}, {y:.1f}) from below (T10)'] = check_screw(st, (x, y, CAP_SEAT_Z - PT['head_h']), (0, 0, -1), key_d=3.6)
ST7 = dict(ST6, cap_screws=CS['pt_k30x12_cap'], tub=P['modulo_vasca_v64'], lid=P['modulo_coperchio_v64'])
for s in (1, -1):
    px, py = post_xy(s)
    st = dict(ST7); st['other_lock'] = v6.screw_m3(px, -py, LOCK['seat_z'], LOCK['len'])
    TA[f'module lock M3x16 ({px:.1f}, {py:+.1f}) from below (hex 2.5), unit hanging or taken down'] = check_screw(st, (px, py, LOCK['seat_z'] - LOCK['head_h']), (0, 0, -1))
ST_BENCH = {'tub': P['modulo_vasca_v64'], 'lid': P['modulo_coperchio_v64'], 'socket': MB['socket_m8_5p']}
for j, (x, y) in enumerate(LID_SCREWS):
    st = dict(ST_BENCH)
    for k, (x2, y2) in enumerate(LID_SCREWS):
        if k != j:
            st[f'lid_head_{k}'] = at(cyl(PT['head_d'], ZMT, ZMT + PT['head_h'], 32), x2, y2)
    TA[f'module lid PT K30x10 #{j + 1} ({x:.1f}, {y:.1f}) from above, module on the bench (T10)'] = check_screw(st, (x, y, ZMT + PT['head_h']), (0, 0, 1), key_d=3.6)
tz = dt.TAB_Z0 + v6.DZ_SERVO
STB = {'scatola_v64': P['scatola_v64'], 'servo': CB['servo'], 'gland_m12': CB['gland_m12']}
for j, (x, y) in enumerate(b61.SERVO_HOLES_W):
    TA[f'factory servo -> cradle M3x8 #{j + 1}'] = check_screw(STB, (x, y, tz - dt.WASHER_T - 3.0), (0, 0, -1))
for k, v in TA.items():
    print(f'  {k:92s} {v["verdict"]:12s} key>={v["key_length_min_mm"]} first={v["first_obstacle"]}')
TA_OK = all('OK' in v['verdict'] for v in TA.values())
INHERIT_TA = {k: v for k, v in V63['checks']['tool_access'].items() if k.startswith('step 3') or k.startswith('step 4') or k.startswith('flange') or 'hub' in k}

# ---------------- panel: paw / snout / fingertip probes, knock-outs, future switches ----------------
print('\n--- panel ---')
CAPP = U([P['modulo_vasca_v64'], MB['switch_12mm_ip67']])
TUB = P['modulo_vasca_v64']


def probe_reach(name, d, approach, finger=False):
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
    if finger:
        shaft = trimesh.creation.cylinder(radius=r, height=60.0, sections=48)
        shaft.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], -dv)); shaft.apply_translation(-dv * 30.0)
        tool0 = U([trimesh.creation.icosphere(subdivisions=3, radius=r), shaft])
    else:
        tool0 = trimesh.creation.icosphere(subdivisions=3, radius=r)

    def hits(s):
        t = tool0.copy(); t.apply_translation(Pk + dv * s - dv * r)
        return vol(I(t, crop_)) > 1e-3
    lo, hi = -15.0, 25.0
    if hits(lo):
        return None
    for _ in range(22):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(mid) else (mid, hi)
    return round(float((Pk - (Pk + dv * lo)) @ nk), 2)


PAW = {}
APPROACHES = [(0.0, 'axis'), (15.0, 'up'), (-15.0, 'up'), (15.0, 'side'), (-15.0, 'side')]
row = {}
for lab_, d, fing in (('paw pad sphere Ø30', 30.0, False), ('paw pad sphere Ø40', 40.0, False), ('snout sphere Ø25', 25.0, False), ('fingertip Ø16', 16.0, True), ('fingertip Ø12', 12.0, True)):
    reach = [probe_reach('btn', d, ap, fing) for ap in (APPROACHES if not fing else APPROACHES[:1])]
    row[lab_] = {'deepest_mm': max(r for r in reach if r is not None), 'actuator_top_mm': REC['face'] - 0.3,
                 'reaches_actuator': bool(max(r for r in reach if r is not None) >= REC['face'] - 0.3 - 0.05)}
PAW['btn'] = row
PANEL_OK = all(not v['reaches_actuator'] for k, v in row.items() if 'finger' not in k) and all(v['reaches_actuator'] for k, v in row.items() if 'finger' in k)
PAW_MARGIN = round(min(REC['face'] - 0.3 - v['deepest_mm'] for k, v in row.items() if 'finger' not in k), 2)
print('button probes', row, PANEL_OK, PAW_MARGIN)
KO_SKIN, LED_FLUSH = {}, {}
for nm_ in ('ko1', 'ko2', 'ko3'):
    Pk, nk, _ = PANEL['frames'][nm_]
    sd_ = np.cross(nk, [0, 0, 1.0]); sd_ /= np.linalg.norm(sd_); up_ = np.cross(sd_, nk)

    def skin_at(off, r_=0.15):
        h_ = axial_hits({'tub': TUB}, Pk + nk * 1.0 + off, -nk, r_, 0.0, 1.0 + KO['skin'] + 1.6)
        return round(h_['tub'][1] - h_['tub'][0], 2) if 'tub' in h_ else None
    plain = [skin_at(3.0 * v) for v in (sd_, -sd_, up_, -up_)]
    marks = [skin_at(0.0 * sd_)] + [skin_at(KO['ring_d'] / 2 * v) for v in (sd_, -sd_, up_, -up_)]
    KO_SKIN[nm_] = {'plain_min_mm': min(plain), 'plain_max_mm': max(plain), 'under_engraving_min_mm': min(marks)}
for k in ('led1', 'led2'):
    Pk, nk, _ = PANEL['frames'][k]
    sd_ = np.cross(nk, [0, 0, 1.0]); sd_ /= np.linalg.norm(sd_); up_ = np.cross(sd_, nk)
    offs = []
    for th in np.radians(np.arange(0, 360, 45)):
        h_ = axial_hits({'tub': TUB}, Pk + nk * 2.0 + 2.9 * (math.cos(th) * sd_ + math.sin(th) * up_), -nk, 0.1, 0.0, 4.0)
        offs.append(round(h_['tub'][0] - 2.0, 3) if 'tub' in h_ else None)
    LED_FLUSH[k] = max(abs(v) for v in offs if v is not None)
FUT_OBST = {'modulo_vasca_v64 (except the drilled hole)': TUB, 'lid': P['modulo_coperchio_v64'], 'board A': MB['board_70x50_A'], 'ESP32 stack (demo position)': MB['esp32_wrover_stack'],
            'regulators (demo position)': U([MB['reg_6v'], MB['reg_5v']]), 'switch (real button)': MB['switch_12mm_ip67'],
            'speaker Ø23 + ring': U([MB['speaker_23mm'], P['modulo_anello_speaker_v64']]), 'leds + light pipes': U([MB['leds_3mm'], MB['lightpipes_5mm']])}
_fut = {nm_: future_switch(*PANEL['frames'][nm_][:2]) for nm_ in ('ko1', 'ko2', 'ko3')}
FUTURE_KO = {}
for nm_, env_ in _fut.items():
    row = {}
    for ek, em in env_.items():
        for ok_, om in FUT_OBST.items():
            if ek == 'thread' and ok_.startswith('modulo_vasca'):
                continue
            v_ = vol_i(em, om)
            if v_ > 1e-3:
                row[f'{ek}|{ok_}'] = v_
    for nb_, envb in _fut.items():
        if nb_ != nm_:
            v_ = round(vol(I(U(list(env_.values())), U(list(envb.values())))), 3)
            if v_ > 1e-3:
                row[f'switch|future {nb_}'] = v_
    Pk, nk, _ = PANEL['frames'][nm_]
    lo_, hi_ = 0.0, 40.0
    for _ in range(12):                                      # free depth for a Ø13 body behind the nut seat, in the empty printed case
        mid_ = (lo_ + hi_) / 2
        lo_, hi_ = (mid_, hi_) if vol_i(axial_cyl(Pk, nk, KO['body_d'], KO['pad'] + 0.05, KO['pad'] + 0.05 + mid_, 32), U([TUB, P['modulo_coperchio_v64']])) < 1e-3 else (lo_, mid_)
    FUTURE_KO[nm_] = {'free_depth_behind_the_seat_mm_empty_case': round(lo_, 1), 'collisions_mm3': row, 'fits_the_printed_case': not any(k.split('|')[1].startswith(('modulo', 'lid', 'switch', 'leds')) for k in row),
                      'fits_with_the_demo_electronics': not row}
print('knock-out skins', KO_SKIN, 'LED flush', LED_FLUSH)
print('future switches', FUTURE_KO)
PANEL_AZ = {k: round(math.degrees(math.atan2(v[1][1], v[1][0])), 1) for k, v in PANEL['frames'].items()}

# ---------------- seams of the pod (second barrier) ----------------
SEAMS = {'vertical_stop': f'post ends on the socket floors at z {ZN0}: the lock screws clamp there; top seam {TOP_SEAM} mm nominal', 'side_seams': {'gap_mm': GAP, 'path_mm': T_SHELL + RIB['depth'], 'where': f'|y| = {YM + GAP}, cap and shell, return rib {RIB["t"]} x {RIB["depth"]} behind the cut edge'},
         'top_seam': {'gap_mm': TOP_SEAM, 'behind': f'module lip {LIP["h"]} mm tall, {LIP["gap"]} mm inside the shell wall: no line of sight, an outward pull at the top is taken by the shell'},
         'bottom_seam': {'gap_mm': GAP, 'where': f'x = {XM0 - GAP:.2f} across the flat bottom, cap floor edge with a dam', 'note': 'vertical slot, faces down: water cannot rise, it is also a drain'},
         'cap_to_shell_seam_mm': 0.6, 'largest_gap_a_claw_meets_mm': 0.6, 'largest_gap_note': 'the 0.6 mm cap-to-shell seam (shell edge z -72.0, cap shoulder z -72.6) is inherited from 6.1.1; the module seams are 0.35 (sides, bottom) and 0.5 (top, backed by the lip)',
         'edges': 'cut edges of cap and shell blunted (face square to the skin 0.9 mm back from the edge), module lip stops 3 mm before its ends, 0.4 x 45 deg chamfers on the bottom seam edges', 'pod': 'closed second barrier, not sealed: the module and the servo bay are each sealed on their own; the 132x2 seam O-ring is dropped'}

# ---------------- load case (hand calculation, same assumptions as 6.3) ----------------
print('\n--- load case ---')
S_XY, S_Z, TAU = 45.0, 20.0, 25.0
FV, FS = 250.0, 100.0
LC63 = V63['load_case']
SOLID_PRINT = {'scatola_v64', 'fondello_v64', 'modulo_vasca_v64', 'modulo_coperchio_v64'}       # IP66 settings: 5 walls + 100 % infill -> ~96 % of the solid
g64 = lambda k: round(v6.grams_est(P[k], RHO[k])[0] * 0.96, 1) if k in SOLID_PRINT else v6.grams_est(P[k], RHO[k])[1]
g_mod = {k: g64(k) for k in MODULE_NEW}
W_MOD = (sum(g_mod.values()) + 120.0) * 9.81 / 1000.0          # printed case + ~120 g electronics, speaker, connectors
ins_pull = 600.0                                                # M3 heat-set insert in PETG (as 6.3)
post_A = math.pi * (POST['d'] ** 2 - POST['ins_d'] ** 2) / 4.0
F_lock = (FV + W_MOD) / 2.0
M_side = FS * (ZN0 - Z_BOT) / 1000.0
Cx = np.array([p[0] for p in CAP64.values()]); Cy = np.array([p[1] for p in CAP64.values()])
A_ = np.array([np.ones(4), Cx, Cy])
x_fc = -13.45
F_cap = np.linalg.lstsq(A_, np.array([FV, FV * x_fc, 0.0]), rcond=None)[0]
PRE = 130.0 / 4 + 40.0
pull_pt = math.pi * PT['pilot'] * 8.0 * 0.5 * S_Z
LOAD = {'case': f'as 6.3: 250 N down at the flat bottom + 100 N sideways + own weight; applied once to the cap and once to the module (worst: all on one)',
        'module_lock_M3x16': {'per_screw_N': round(F_lock, 1), 'insert_pullout_N': ins_pull, 'SF_insert': round(ins_pull / F_lock, 1),
                              'post_tension_MPa': round(F_lock / post_A, 2), 'SF_post_across_layers_20MPa': round(S_Z / (F_lock / post_A), 1),
                              'side_100N': f'taken by the two closed sockets round the posts (Ø{POST["d"]} in Ø{POST["d"] + 2 * GAP}) and the top lip behind the shell; '
                                           f'post bending at the web root {round(FS / 2 * (POST["web_z0"] - ZN0) * 32 / (math.pi * POST["d"] ** 3), 1)} MPa',
                              'module_weight_N': round(W_MOD, 2)},
        'module_pulled_outward_at_the_top_100N': {'lip_shear_area_mm2': round(LIP['t'] * 2 * YM, 0), 'shear_MPa': round(FS / (LIP['t'] * 2 * YM), 2), 'SF': round(TAU / (FS / (LIP['t'] * 2 * YM)), 0)},
        'cap_screws_PT_K30x12': {'positions': CAP64, 'vertical_shares_N': [round(float(v), 1) for v in F_cap], 'preload_per_screw_N': round(PRE, 1),
                                 'worst_screw_N': round(float(F_cap.max() + PRE), 1), 'pullout_est_N': round(pull_pt), 'SF_pullout': round(pull_pt / float(F_cap.max() + PRE), 1),
                                 'v63': f"3 screws, worst {LC63['cap_screws_PT_K30x12']['worst_screw_N']} N, SF {LC63['cap_screws_PT_K30x12']['SF_pullout']}",
                                 'note': '4 screws round the bay; the load centre (-13.5, 0) is now inside the screw polygon'},
        'stack_screws_M3x40': dict(LC63['stack_screws_M3x40'], note='unchanged positions; the module adds its weight and the 250 N case through the posts into the bay'),
        'fox_bite_panel': LC63['fox_bite_panel'], 'panel_button': LC63['panel_button'],
        'inherited_unchanged_parts': {k: LC63[k] for k in ('shell_tabs_PT_K30x12', 'chute_PT_K30x10', 'tower_pillars', 'flange_wood_screws', 'bayonet_lugs_hooks', 'gate_blade_column',
                                                           'gate_ring_fox', 'fox_bite_outlet_rim')}}
print(json.dumps({k: v for k, v in LOAD.items() if k != 'inherited_unchanged_parts'}, indent=1, default=str))

# ---------------- grams / pieces / hardware: chassis and module separately ----------------
print('\n--- grams / pieces ---')
PCS63 = {k: v for k, v in V63['grams']['per_part_v63'].items()}
G_CH = {}
for k, v in PCS63.items():
    if k in REPLACED:
        nk_ = REPLACED[k]
        G_CH[nk_] = {'qty': 1, 'material': v['material'], 'grams_print_est_each': g64(nk_), 'v63_each': v['grams_print_est_each']}
    else:
        G_CH[k] = dict(v)
G_MOD = {k: {'qty': 1, 'material': 'TPU' if RHO[k] == TPU else 'PETG', 'grams_print_est_each': g_mod[k]} for k in MODULE_NEW}
_sum = lambda G, mat: round(sum(v['qty'] * v['grams_print_est_each'] for v in G.values() if v['material'].startswith(mat)), 1)
_pcs = lambda G, mat=None: sum(v['qty'] for v in G.values() if mat is None or v['material'].startswith(mat))
GRAMS = {'method': V63['grams']['method'] + '; 6.4: bay, cap, tub and lid are printed solid (IP66 settings), so they are counted at 96 % of the solid mass. Reviewer slicer figures for the first 6.4 issue: tub 87 g, bay 84 g, cap 110 g, shell 153 g', 'v63': V63['grams']['v63'],
         'chassis_v64': {'PETG_g': _sum(G_CH, 'PETG'), 'TPU_g': _sum(G_CH, 'TPU'), 'pieces': _pcs(G_CH), 'PETG_pieces': _pcs(G_CH, 'PETG'), 'TPU_pieces': _pcs(G_CH, 'TPU')},
         'module_case_1_0': {'PETG_g': _sum(G_MOD, 'PETG'), 'TPU_g': _sum(G_MOD, 'TPU'), 'pieces': _pcs(G_MOD), 'PETG_pieces': _pcs(G_MOD, 'PETG'), 'TPU_pieces': _pcs(G_MOD, 'TPU')},
         'per_part_chassis': G_CH, 'per_part_module': G_MOD}
GRAMS['total_v64'] = {'PETG_g': round(GRAMS['chassis_v64']['PETG_g'] + GRAMS['module_case_1_0']['PETG_g'], 1), 'TPU_g': round(GRAMS['chassis_v64']['TPU_g'] + GRAMS['module_case_1_0']['TPU_g'], 1),
                      'pieces': GRAMS['chassis_v64']['pieces'] + GRAMS['module_case_1_0']['pieces']}
HW63 = V63['changes']['2_simplification']['screws_inserts_orings']
HW = {'chassis': {'screws': {'wood 5x35 pan': 4, 'PT K30x10 chute': 2, 'PT K30x12 shell tabs': 3, 'PT K30x12 cap': 4, 'M3x40 stack': 3, 'M3x8 servo + hub': 5},
                  'inserts': {'bowl (stack)': 3, 'servo cradle': 4, 'holder posts (module lock)': 2},
                  'o_rings': {'9x2': 2, '24x2': 1, '14x1.5': 1, '3x1 (P2 1, cap 4)': 5},
                  'other': {'dowel 4x6': 1, 'cable tie 3.6 x 140 UV': 1, 'gland M12x1.5 IP68, cable range 3-6.5 (servo branch)': 1, 'adhesive ePTFE vent patch Ø12': 1,
                            'cable tie 2.5 x 100 (harness anchor on the bay lug)': 1, 'chassis harness (see interface.electrical_J1.harness)': 1}},
      'module': {'screws': {'M3x16 ISO 4762 lock (stay with the module)': 2, 'PT K30x10 lid': len(LID_SCREWS)}, 'inserts': {},
                 'o_rings': {'3x1 (lid screws)': len(LID_SCREWS), '5x1 (light pipes)': 2},
                 'other': {'M8 5-pin A-coded panel socket': 1, 'IP67 12 mm push-button': 1, 'light pipe Ø5': 2, 'acoustic membrane Ø15': 1}},
      'v63_totals': {'screws': HW63['screws']['v63_total'], 'inserts': HW63['inserts']['v63'], 'o_rings': HW63['o_rings']['v63_total']}}
for grp in ('chassis', 'module'):
    for k in ('screws', 'inserts', 'o_rings'):
        HW[grp][k + '_total'] = sum(HW[grp][k].values())
print(json.dumps({k: v for k, v in GRAMS.items() if not k.startswith('per_part')}, indent=1))

# ---------------- assembled-position files for the viewer ----------------
ASM_NOT_WT = []


def save(name, m):
    p_ = ASM + name + '.stl'
    c = clean64(m) if m.is_volume else m
    c.export(staged(p_))
    if not trimesh.load(current(p_)).is_watertight:
        ASM_NOT_WT.append(name)
    return p_


FILES = {}
for k, m in list(CB.items()) + list(CS.items()) + list(MB.items()) + list(MS.items()):
    FILES[k] = save('bought_' + k.replace('.', '_'), m)
FILES['guscio_v64_basso'] = save('guscio_v64_basso', I(P['guscio_v64'], box(-200, 200, -200, 200, -200, -10.0)))
FILES['guscio_v64_alto'] = save('guscio_v64_alto', I(P['guscio_v64'], box(-200, 200, -200, 200, -10.0, 200)))
for nm, z0, z1 in (('fondello_v64_fondo', -200, -99.0), ('fondello_v64_fianco', -99.0, -86.0), ('fondello_v64_bordo', -86.0, 0.0)):
    FILES[nm] = save(nm, I(P['fondello_v64'], box(-200, 200, -200, 200, z0, z1)))
TUB_CUTS = [-60.0, -31.0, -13.0, 8.0, 27.0, 60.0]              # tub in pieces cut between the panel elements (kept crisp in the viewer)
TUB_PIECES = []
FILES['modulo_vasca_alto'] = save('modulo_vasca_v64_alto', I(TUB, box(-200, 200, -200, 200, ZB1 + 1.0, 0.0))); TUB_PIECES.append('modulo_vasca_alto')
FILES['modulo_vasca_fondo'] = save('modulo_vasca_v64_fondo', I(TUB, box(-200, 200, -200, 200, -200.0, ZB0 - 1.5))); TUB_PIECES.append('modulo_vasca_fondo')
for k, (y0, y1) in enumerate(zip(TUB_CUTS[:-1], TUB_CUTS[1:])):
    nm = f'modulo_vasca_pannello_{k + 1}'
    FILES[nm] = save(f'modulo_vasca_v64_pannello_{k + 1}', I(TUB, box(-200, 200, y0, y1, ZB0 - 1.5, ZB1 + 1.0))); TUB_PIECES.append(nm)
# module pulled out (viewer variant "modulo fuori"): the same module files moved 95 mm down
OUT_DZ = -95.0
FILES_OUT = {}
for k in TUB_PIECES + ['modulo_coperchio_v64', 'modulo_guarnizione_v64', 'modulo_anello_speaker_v64', 'plug_m8_5p_angled'] + list(MB) + list(MS) + ['m3x16_module_lock']:
    src = current(FILES[k]) if k in FILES else None
    m = trimesh.load(src) if src else P[k].copy()
    m = m.copy(); m.apply_translation([0, 0, OUT_DZ])
    p_ = SCRATCH + 'out_' + k.replace('.', '_') + '.stl'
    m.export(p_)
    FILES_OUT[k] = p_
_tl = tube_path(tail_points(min(-OUT_DZ, D_MAX)), HARN['r_tail'], 16)          # the tail as it hangs with the module out
_tl.export(SCRATCH + 'out_harness_tail.stl'); FILES_OUT['harness_tail'] = SCRATCH + 'out_harness_tail.stl'
print('assembled-position copies written; not watertight on reload:', ASM_NOT_WT)

if STAGE != 'checks':                                  # the report sits next to the scripts
    exec(open(dt.HERE + 'build_v64_report.py').read())
