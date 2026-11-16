# executed by build_v611.py (exec) in its namespace: context, interference + designed seal contacts, seal continuity,
# line of sight into the pod / dry box, bayonet sweep, cap removal path, torques, grams, render, v611.json, v611_viewer.json
import time
import collections
from scipy.spatial import cKDTree
sys.path.insert(0, dt.HERE)                           # los.py lives next to the scripts
from los import crop, first_hits
t_start = time.time()
print('\n--- context ---')
LD = lambda f: trimesh.load(f)
A61 = OUT + 'v61_asm/'
SHELF_T = 30.0
SHELF = D(box(-150, 150, -110, 110, FL_Z1, FL_Z1 + SHELF_T), [at(cyl(v5.SHELF_HOLE_D, FL_Z1 - 1, FL_Z1 + SHELF_T + 1), *v6.HOLE_C),
                                                              at(cyl(10.0, FL_Z1 - 1, FL_Z1 + SHELF_T + 1, 32), *CABLE_XY)])
R61 = {k: LD(OUT + k + '.stl') for k in ('chiocciola_v61', 'piastra_gate_v61', 'piastra_finestra_v61', 'disco_v61', 'labbro_uscita_v61', 'labbro_uscita_v61_b',
                                          'labbro_finestra_v61', 'labbro_finestra_v61_b', 'guarnizione_baionetta_v61', 'colonna_v61', 'passacavo_v61',
                                          'guarnizione_fondello_v61')}
COLLAR = v6.build_collar(EXTRA['FL_CAV'])                     # regenerated in memory (float32 reloads of some v6.1 copies are not volumes)
SHAFT, HUB = v6.build_shaft(), v6.build_hub()
LATCH = b61.R5['linguetta_sicura']
GSK_PIANO = v5.build_flange_gasket() if hasattr(v5, 'build_flange_gasket') else LD(OUT + 'guarnizione_piano_v5.stl')
if hasattr(v5, 'build_flange_gasket'):
    GSK_PIANO.apply_translation([0, 0, FL_Z1 - v5.FL_Z1])
for _k, _m in list(R61.items()):
    if not _m.is_volume:
        R61[_k] = v6.clean(_m)
BOUGHT, SCREWS = bought611()
TTS = EXTRA['tts']
LIPS = {k: R61[k] for k in ('labbro_uscita_v61', 'labbro_uscita_v61_b', 'labbro_finestra_v61', 'labbro_finestra_v61_b')}
disc0, disc180 = R61['disco_v61'], rotz(R61['disco_v61'], 180)
ALL = {'flangia_piano_v611': P['flangia_piano_v611'], 'labbro_ombra_v611': P['labbro_ombra_v611'], 'colletto_v6': COLLAR, 'guarnizione_piano_v5': GSK_PIANO,
       'passacavo_v61': R61['passacavo_v61'], 'chiocciola_v61': R61['chiocciola_v61'], 'scivolo_v611': P['scivolo_v611'], 'labbro_scivolo_v611': P['labbro_scivolo_v611'],
       'linguetta_sicura': LATCH, 'guarnizione_baionetta_v61': R61['guarnizione_baionetta_v61'], 'piastra_gate_v61': R61['piastra_gate_v61'],
       'piastra_finestra_v61': R61['piastra_finestra_v61'], 'disco_v61@0': disc0, 'disco_v61@180': disc180, 'colonna_v61': R61['colonna_v61'],
       'albero_v6@0': SHAFT, 'mozzo_v6@0': HUB, 'scatola_v611': P['scatola_v611'], 'guscio_v611': P['guscio_v611'], 'pulsante_v611': P['pulsante_v611'],
       'fondello_v611': P['fondello_v611'], 'guarnizione_fondello_v61': R61['guarnizione_fondello_v61'],
       'nottolino_A': TTS[0], 'nottolino_B': TTS[1], 'nottolino_C': TTS[2], 'shelf': SHELF}
ALL.update(LIPS)
ALL.update(BOUGHT)
ALL.update(SCREWS)
CHANGED = ['flangia_piano_v611', 'labbro_ombra_v611', 'scivolo_v611', 'labbro_scivolo_v611', 'scatola_v611', 'guscio_v611', 'pulsante_v611', 'fondello_v611',
           'nottolino_A', 'nottolino_B', 'nottolino_C', 'oring_tt_8x1.5', 'keys_3x3x18', 'oring_seam_2', 'oring_btn_14x1.5']
_soft = [('flangia_piano_v611', 'guarnizione_baionetta_v61'), ('guarnizione_piano_v5', 'shelf'), ('guarnizione_fondello_v61', 'scatola_v611'),
         ('guarnizione_fondello_v61', 'fondello_v611'), ('oring_shaft_9x2', 'colonna_v61'), ('oring_face_24x2', 'colonna_v61'), ('oring_face_24x2', 'scatola_v611'),
         ('oring_shaft_9x2', 'albero_v6@0'), ('passacavo_v61', 'flangia_piano_v611'), ('cable_12v', 'passacavo_v61'),
         ('oring_tt_8x1.5', 'fondello_v611'), ('oring_tt_8x1.5', 'nottolino_A'), ('oring_tt_8x1.5', 'nottolino_B'), ('oring_tt_8x1.5', 'nottolino_C'),
         ('keys_3x3x18', 'nottolino_A'), ('keys_3x3x18', 'nottolino_B'), ('keys_3x3x18', 'nottolino_C'), ('keys_3x3x18', 'scatola_v611'),
         ('oring_seam_2', 'fondello_v611'), ('oring_seam_2', 'guscio_v611'), ('labbro_scivolo_v611', 'fondello_v611'), ('labbro_scivolo_v611', 'scivolo_v611'),
         ('labbro_ombra_v611', 'flangia_piano_v611'), ('labbro_ombra_v611', 'guscio_v611'), ('oring_btn_14x1.5', 'guscio_v611'), ('oring_btn_14x1.5', 'pulsante_v611')]
for lk in LIPS:
    _soft += [(lk, 'disco_v61@0'), (lk, 'disco_v61@180'), (lk, 'piastra_gate_v61' if 'uscita' in lk else 'piastra_finestra_v61')]
SOFT = {frozenset(p) for p in _soft}
SEAL_ROLE = {frozenset(('guarnizione_fondello_v61', 'scatola_v611')): 'PRIMARY dry box: cap lip on the box rim face',
             frozenset(('guarnizione_fondello_v61', 'fondello_v611')): 'lip base pressed in the new 2.1 retaining groove',
             frozenset(('oring_tt_8x1.5', 'fondello_v611')): 'O-ring 8x1.5 x3 on the shaft bores (C = primary dry box, A/B = pod)',
             frozenset(('oring_seam_2', 'guscio_v611')): 'seam O-ring 132x2 on the shell inner wall (pod)',
             frozenset(('oring_seam_2', 'fondello_v611')): 'seam O-ring in the spigot groove',
             frozenset(('labbro_scivolo_v611', 'scivolo_v611')): 'chute lip ring on the chute OD (pod vs outlet bore)',
             frozenset(('labbro_scivolo_v611', 'fondello_v611')): 'chute lip anchor pressed in the socket groove',
             frozenset(('labbro_ombra_v611', 'guscio_v611')): 'shadow-gap skirt lip on the shell outer cylinder (pod top)',
             frozenset(('labbro_ombra_v611', 'flangia_piano_v611')): 'skirt lip anchor pressed in the flange groove',
             frozenset(('oring_btn_14x1.5', 'guscio_v611')): 'button O-ring in the shell bore groove (pod)',
             frozenset(('oring_btn_14x1.5', 'pulsante_v611')): 'button O-ring on the head (pod)'}
_skip = [('disco_v61@0', 'disco_v61@180'), ('disco_v61@0', 'mozzo_v6@0'), ('mozzo_v6@0', 'albero_v6@0'), ('mozzo_v6@0', 'servo'), ('mozzo_v6@0', 'm3x8_hub'),
         ('shelf', 'wood_5x25'), ('inserts_bowl', 'm3x12_tower_top'), ('inserts_box', 'm3x10_tower_box'), ('inserts_bowl', 'm3x10_chute'),
         ('inserts_bowl', 'm3x12_shell_tabs'), ('inserts_box', 'm3x8_servo'), ('servo', 'm3x8_hub'), ('servo', 'm3x8_servo'),
         ('scatola_v611', 'gland_m12'), ('scatola_v611', 'vent_m12_eptfe'), ('cable_12v', 'gland_m12'), ('cable_12v', 'connector_ip67'), ('cable_12v', 'shelf')]
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
        try:
            v = round(vol(I(ALL[a], ALL[b_])), 4) if bb_overlap(ALL[a], ALL[b_]) else 0.0
        except ValueError:
            print('  not a volume:', a if not ALL[a].is_volume else b_)
            raise
        (soft if key in SOFT else inter)[f'{a}|{b_}'] = v
        if key not in SOFT and v > 1e-3:
            print(f'  HARD {a:26s}|{b_:26s} {v:.4f}')
HARD_MAX = max(inter.values())
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3; soft:', {k: v for k, v in soft.items() if v > 0})
print(f'interference done {time.time() - t_start:.0f} s')

# ---------------- seal continuity: designed contact present in every angular sector ----------------
print('\n--- seal continuity ---')


def sectors_ok(seal, mate, centre, n=36, rmax=200.0):
    cx_, cy_ = centre
    lo, hi = seal.bounds[0] - 1.0, seal.bounds[1] + 1.0
    mc = I(mate, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    zz0, zz1 = lo[2] - 1, hi[2] + 1
    res = []
    for k in range(n):
        a0, a1 = 360.0 * k / n, 360.0 * (k + 1) / n
        pts = [(0, 0)] + [(rmax * math.cos(math.radians(a)), rmax * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 6)]
        w = at(prism(Polygon(pts), zz0, zz1), cx_, cy_)
        res.append(round(vol(I(I(seal, w), mc)), 4))
    return {'sectors': n, 'min_overlap_mm3': min(res), 'all_in_contact': bool(min(res) > 0)}


def radial_sectors_ok(seal, mate, n=24):
    """sector test round the push-button axis (horizontal): rotate into a z-axis frame first"""
    Tm = trimesh.transformations.rotation_matrix(-math.radians(LATCH_A), [0, 0, 1])
    Ty = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
    s2, m2 = seal.copy(), mate.copy()
    for g in (s2, m2):
        g.apply_transform(Tm); g.apply_translation([0, 0, -BTN_Z]); g.apply_transform(Ty)
    return sectors_ok(s2, m2, (0.0, 0.0), n)


gc = WALL_C.centroid.coords[0]
cxs70 = SEAM_CX
CONT = {}
CONT['guarnizione_fondello_v61|scatola_v611 (PRIMARY lip on the box rim)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['scatola_v611'], gc)
CONT['guarnizione_fondello_v61|fondello_v611 (base in the retaining groove)'] = sectors_ok(R61['guarnizione_fondello_v61'], P['fondello_v611'], gc)
for k, (x, y) in zip('ABC', TT):
    orr = I(BOUGHT['oring_tt_8x1.5'], at(cyl(16, -120, 0), x, y))
    CONT[f'oring_tt_{k}|fondello_v611 (bore)'] = sectors_ok(orr, P['fondello_v611'], (x, y), 24)
CONT['oring_seam|guscio_v611'] = sectors_ok(BOUGHT['oring_seam_2'], P['guscio_v611'], (cxs70, 0.0))
CONT['oring_seam|fondello_v611 (groove)'] = sectors_ok(BOUGHT['oring_seam_2'], P['fondello_v611'], (cxs70, 0.0))
CONT['labbro_scivolo|scivolo_v611 (lip on the chute)'] = sectors_ok(P['labbro_scivolo_v611'], P['scivolo_v611'], (CH_X, 0.0))
CONT['labbro_scivolo|fondello_v611 (anchor)'] = sectors_ok(P['labbro_scivolo_v611'], P['fondello_v611'], (CH_X, 0.0))
CONT['labbro_ombra|guscio_v611 (skirt lip on the shell)'] = sectors_ok(P['labbro_ombra_v611'], P['guscio_v611'], (0.0, 0.0), 72)
CONT['labbro_ombra|flangia_piano_v611 (anchor)'] = sectors_ok(P['labbro_ombra_v611'], P['flangia_piano_v611'], (0.0, 0.0), 72)
CONT['oring_btn|guscio_v611 (bore groove)'] = radial_sectors_ok(BOUGHT['oring_btn_14x1.5'], P['guscio_v611'])
CONT['oring_btn|pulsante_v611 (head)'] = radial_sectors_ok(BOUGHT['oring_btn_14x1.5'], P['pulsante_v611'])
for k, v in CONT.items():
    print(f'  {k:60s} {v}')
print(f'continuity done {time.time() - t_start:.0f} s')

# ---------------- line of sight from outside into the pod interior / dry box ----------------
print('\n--- line of sight ---')
ZS_IN, X0_IN, X1_IN = section_fn(T_SHELL + 2.0)


def interior(p):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    a, c = np.interp(z, ZS_IN, X0_IN), np.interp(z, ZS_IN, X1_IN)
    cxp, Rp = (a + c) / 2, (c - a) / 2
    inpod = ((x - cxp) ** 2 + y ** 2 < Rp ** 2) & (z > Z_BOT + T_CAP) & (z < Z_TOP)
    gap = (x ** 2 + y ** 2 < 78.0 ** 2) & (z >= Z_TOP) & (z < FL_Z0)
    rk = np.hypot(x - CH_X, y)
    kib = ((rk < RI) & (z > Z_CH_END611)) | ((rk < OUTLET['r']) & (z <= SOCK['bore_z'])) | ((rk < SOCK['r'] + 0.05) & (z > SOCK['bore_z'] - 0.1) & (z < -79.0))
    ex = np.zeros(len(p), bool)
    for tx, ty in TT:
        ex |= (np.hypot(x - tx, y - ty) < TT_DISH_D / 2 + 0.05) & (z < TT_DISH_FLOOR)
    ua_ = math.radians(LATCH_A)
    uu, ww = x * math.cos(ua_) + y * math.sin(ua_), -x * math.sin(ua_) + y * math.cos(ua_)
    ex |= (np.hypot(ww, z - BTN_Z) < BTN611['dish_d'] / 2 + 0.5) & (uu > BTN611['u_boss'] - 0.5)
    ex |= (np.hypot(x - DRAIN_XY[0], y - DRAIN_XY[1]) < DRAIN['boss_r'] + 0.05) & (z < DRAIN['boss_top'] + 0.05)
    for tx, ty in TT:                                          # bore / countersink labyrinth inside the boss (sealed by the O-ring above)
        ex |= (np.hypot(x - tx, y - ty) < BOSS_HI_D / 2 + 0.3) & (z < BOSS_TOP + 0.2)
    zf = CH_LIP['tip'][1] + (rk - CH_LIP['tip'][0]) * (CH_LIP['root'][1] - CH_LIP['tip'][1]) / (CH_LIP['root'][0] - CH_LIP['tip'][0])
    kib |= (rk < SOCK['pocket'][2] + 0.05) & (z > SOCK['bore_z'] - 0.1) & (z < zf - CH_LIP['t'] / 2)   # outlet side of the chute lip
    inpod &= ~ex
    bx = (x > BXO[0] + BX_T) & (x < BXO[1] - BX_T) & (np.abs(y) < BXO[3] - BX_T) & (z < Z_R)
    res = np.array([''] * len(p), dtype=object)
    res[(inpod | gap) & ~kib] = 'pod'
    res[inpod & bx] = 'dry'
    return res


LOSM = {'fondello_v611': P['fondello_v611'], 'guscio_v611': P['guscio_v611'], 'flangia_piano_v611': P['flangia_piano_v611'], 'labbro_ombra_v611': P['labbro_ombra_v611'],
        'pulsante_v611': P['pulsante_v611'], 'nottolino_A': TTS[0], 'nottolino_B': TTS[1], 'nottolino_C': TTS[2], 'oring_tt': BOUGHT['oring_tt_8x1.5'],
        'oring_seam': BOUGHT['oring_seam_2'], 'oring_btn': BOUGHT['oring_btn_14x1.5'], 'labbro_scivolo_v611': P['labbro_scivolo_v611'], 'scivolo_v611': P['scivolo_v611'],
        'scatola_v611': P['scatola_v611'], 'chiocciola_v61': R61['chiocciola_v61'], 'guarnizione_fondello_v61': R61['guarnizione_fondello_v61'],
        'linguetta_sicura': LATCH, 'keys': BOUGHT['keys_3x3x18'], 'board': BOUGHT['board_70x50'], 'servo': BOUGHT['servo'], 'colonna_v61': R61['colonna_v61']}


def cast(origins, dirs, lo, hi, step=0.2, cap_len=300.0, zmax=1e9):
    M = {k: crop(m, lo, hi) for k, m in LOSM.items()}
    hit, dist = first_hits(M, origins, dirs)
    dn = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    reach = []
    for o, d, t in zip(origins, dn, dist):
        t = min(t, cap_len)
        s = np.arange(0.1, max(t - 0.1, 0.1), step)
        q = o + s[:, None] * d
        q = q[q[:, 2] < zmax]
        cls = interior(q) if len(q) else np.array([])
        reach.append('dry' if (cls == 'dry').any() else ('pod' if (cls == 'pod').any() else ''))
    return np.array(reach), hit


LOS = {}
rng = np.random.default_rng(7)
# 1. thumb-turn dishes: vertical + 20 deg in 8 azimuths
for k, (x, y) in zip('ABC', TT):
    rr, th = np.meshgrid(np.arange(0.05, 13.0, 0.1), np.radians(np.arange(0, 360, 2.0)))
    o = np.c_[x + (rr * np.cos(th)).ravel(), y + (rr * np.sin(th)).ravel(), np.full(rr.size, -106.0)]
    d = np.tile([0.0, 0.0, 1.0], (len(o), 1))
    reach, hit = cast(o, d, np.array([x - 40, y - 40, -110]), np.array([x + 40, y + 40, 0]))
    n2 = 4000
    r2 = 13.0 * np.sqrt(rng.random(n2)); t2 = rng.random(n2) * 2 * np.pi; az = rng.integers(0, 8, n2) * np.pi / 4
    o2 = np.c_[x + r2 * np.cos(t2), y + r2 * np.sin(t2), np.full(n2, -106.0)]
    d2 = np.c_[np.sin(np.radians(20)) * np.cos(az), np.sin(np.radians(20)) * np.sin(az), np.full(n2, np.cos(np.radians(20)))]
    o2 -= d2 * 2.0
    reach2, hit2 = cast(o2, d2, np.array([x - 40, y - 40, -110]), np.array([x + 40, y + 40, 0]))
    LOS[f'thumbturn_{k}'] = {'rays': int(len(o) + n2), 'reach_pod': int((reach == 'pod').sum() + (reach2 == 'pod').sum()),
                             'reach_dry': int((reach == 'dry').sum() + (reach2 == 'dry').sum()),
                             'v61_vertical_see_through_mm2': json.load(open(dt.HERE + 'ref/measure_v61.json'))['thumbturns']['line_of_sight'][k]['vertical_see_through_mm2']}
    print(k, LOS[f'thumbturn_{k}'])
# 2. outlet bore -> socket / chute lip (v6.1: 1 mm annulus + 2 drain slots)
n = 6000
r0 = 23.5 * np.sqrt(rng.random(n)); t0 = rng.random(n) * 2 * np.pi
o = np.c_[CH_X + r0 * np.cos(t0), r0 * np.sin(t0), np.full(n, -106.0)]
ta = rng.random(n) * 2 * np.pi; tr = rng.uniform(22.5, 26.5, n)
tg = np.c_[CH_X + tr * np.cos(ta), tr * np.sin(ta), rng.uniform(-104.0, -72.0, n)]
reach, hit = cast(o, tg - o, np.array([-90, -60, -110]), np.array([20, 60, 10]), zmax=-60.0)
LOS['outlet_bore'] = {'rays': n, 'reach_pod': int((reach == 'pod').sum()), 'reach_dry': int((reach == 'dry').sum()),
                      'first_part_seen': collections.Counter(hit).most_common(4)}
print('outlet', LOS['outlet_bore'])
# 3. drain: rays through the 4 exit holes at all angles up to 40 deg
xd, yd = DRAIN_XY
n = 6000
k_ = rng.integers(0, DRAIN['n_holes'], n)
hx = xd + DRAIN['holes_r'] * np.cos(np.radians(45 + 90 * k_)) + rng.uniform(-0.38, 0.38, n)
hy = yd + DRAIN['holes_r'] * np.sin(np.radians(45 + 90 * k_)) + rng.uniform(-0.38, 0.38, n)
el = np.radians(rng.uniform(0, 40, n)); az = rng.random(n) * 2 * np.pi
d = np.c_[np.sin(el) * np.cos(az), np.sin(el) * np.sin(az), np.cos(el)]
o = np.c_[hx, hy, np.full(n, Z_BOT)] - d * 3.0
reach, hit = cast(o, d, np.array([xd - 30, yd - 30, -110]), np.array([xd + 30, yd + 30, -60]), step=0.1)
LOS['drain_labyrinth'] = {'rays_through_exit_holes': n, 'reach_pod': int((reach == 'pod').sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
print('drain', LOS['drain_labyrinth'])
# 4. seam
O_, D_ = [], []
for z in np.linspace(-72.55, -72.05, 6):
    cx_, R_ = pod_circle(0.0, z)
    for a in np.radians(np.arange(0, 360, 1.0)):
        for e in np.radians([-20, -10, 0, 10, 20]):
            O_.append([cx_ + (R_ + 15) * math.cos(a), (R_ + 15) * math.sin(a), z])
            D_.append([-math.cos(a) * math.cos(e), -math.sin(a) * math.cos(e), math.sin(e)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-100, -100, -80]), np.array([100, 100, -60]))
LOS['seam'] = {'rays': len(O_), 'reach_pod': int((reach != '').sum())}
print('seam', LOS['seam'])
# 5. shadow gap
O_, D_ = [], []
for z in np.linspace(62.0, 66.0, 9):
    for a in np.radians(np.arange(0, 360, 2.0)):
        for e in np.radians([-15, -5, 0, 5, 15]):
            O_.append([97 * math.cos(a), 97 * math.sin(a), z - 13 * math.tan(e)])
            D_.append([-math.cos(a) * math.cos(e), -math.sin(a) * math.cos(e), math.sin(e)])
reach, hit = cast(np.array(O_), np.array(D_), np.array([-100, -100, 30]), np.array([100, 100, 75]))
LOS['shadow_gap'] = {'rays': len(O_), 'reach_pod': int((reach != '').sum()), 'first_part_seen': collections.Counter(hit).most_common(3)}
print('shadow', LOS['shadow_gap'])
# 6. push-button annulus
ua = math.radians(LATCH_A)
u = np.array([math.cos(ua), math.sin(ua), 0.0]); w = np.array([-math.sin(ua), math.cos(ua), 0.0]); zv = np.array([0, 0, 1.0])
O_, D_ = [], []
for rr_ in np.arange(6.95, 7.25, 0.02):
    for a in np.radians(np.arange(0, 360, 3.0)):
        for tilt in np.radians([0, 2, 4, 8]):
            for ta_ in np.radians([0, 90, 180, 270]):
                off = rr_ * (math.cos(a) * w + math.sin(a) * zv)
                dv = -u + math.tan(tilt) * (math.cos(ta_) * w + math.sin(ta_) * zv)
                O_.append(np.array([0, 0, BTN_Z]) + 90 * u + off - 5 * dv)
                D_.append(dv)
reach, hit = cast(np.array(O_), np.array(D_), np.array([-20, 40, 20]), np.array([40, 100, 70]))
LOS['push_button'] = {'rays': len(O_), 'reach_pod': int((reach != '').sum())}
print('button', LOS['push_button'])
# 7. global sweep: rays from 3 mm outside the whole skin, pointing inward within 60 deg of the inward normal, 25 mm long
SK = pod_solid(0.0)
pts, fi = trimesh.sample.sample_surface_even(SK, 10000, seed=3)
nrm = SK.face_normals[fi]
keep = pts[:, 2] < Z_TOP - 0.3                                 # above the rim the skin is the flange / shelf (not outside air)
pts, nrm = pts[keep], nrm[keep]
extra = []
for a in np.radians(np.arange(0, 360, 1.0)):                     # the shadow-gap / flange-edge band
    for z in (62.5, 63.5, 64.5, 65.5, 66.5):
        extra.append(([86 * math.cos(a), 86 * math.sin(a), z], [math.cos(a), math.sin(a), 0.0]))
pts = np.vstack([pts, [e[0] for e in extra]]); nrm = np.vstack([nrm, [e[1] for e in extra]])
dev = rng.normal(size=nrm.shape); dev -= (dev * nrm).sum(1, keepdims=True) * nrm
dev /= np.linalg.norm(dev, axis=1, keepdims=True)
ang = np.radians(rng.uniform(0, 60, len(pts)))
dirs = -nrm * np.cos(ang)[:, None] + dev * np.sin(ang)[:, None]
orig = pts + nrm * 3.0
cell = np.floor((orig + 200) / 30.0).astype(int)
keys_ = cell[:, 0] * 10000 + cell[:, 1] * 100 + cell[:, 2]
G_reach = collections.Counter()
G_ex = []
for kk in np.unique(keys_):
    sel = np.where(keys_ == kk)[0]
    lo = orig[sel].min(0) - 30.0; hi = orig[sel].max(0) + 30.0
    reach, hit = cast(orig[sel], dirs[sel], lo, hi, step=0.25, cap_len=25.0)
    G_reach.update(reach.tolist())
    for j in np.where(reach != '')[0][:5]:
        G_ex.append([np.round(orig[sel][j], 1).tolist(), str(hit[j]), str(reach[j])])
LOS['global_sweep'] = {'rays': int(len(orig)), 'reach_pod': int(G_reach.get('pod', 0)), 'reach_dry': int(G_reach.get('dry', 0)), 'examples': G_ex[:10]}
print('global', LOS['global_sweep'])
print(f'line of sight done {time.time() - t_start:.0f} s')

# ---------------- bayonet removal sweep (flange v611 + skirt lip) ----------------
print('\n--- bayonet ---')
FIXED = U([P['flangia_piano_v611'], COLLAR, GSK_PIANO, SHELF, R61['passacavo_v61']])
latch_pressed = LATCH.copy(); latch_pressed.apply_translation([-1.6 * math.cos(ua), -1.6 * math.sin(ua), 0])
btn_pressed = P['pulsante_v611'].copy(); btn_pressed.apply_translation([-1.5 * math.cos(ua), -1.5 * math.sin(ua), 0])
MOVING = I(U([R61['chiocciola_v61'], latch_pressed, R61['piastra_finestra_v61'], LIPS['labbro_finestra_v61'], LIPS['labbro_finestra_v61_b'],
              disc0, R61['piastra_gate_v61'], P['guscio_v611'], btn_pressed]), above(40.0))
SHELL_TOP = I(P['guscio_v611'], above(55.0))


def unlock_dz(a):
    return 0.0 if a <= bd.LOCK_ROT - bd.LUG_RAMP_DEG else -bd.LIFT * (a - (bd.LOCK_ROT - bd.LUG_RAMP_DEG)) / bd.LUG_RAMP_DEG


poses = [(-a, unlock_dz(a)) for a in np.linspace(0, bd.LOCK_ROT, 11)] + [(-bd.LOCK_ROT, -bd.LIFT - dz) for dz in (2, 5, 10, 20, 40, 80)]
SWEEP, LIPSWEEP = [], []
for ang_, dz in poses:
    m = rotz(MOVING, ang_); m.apply_translation([0, 0, dz])
    SWEEP.append((round(float(ang_), 1), round(float(dz), 2), round(vol(I(m, FIXED)), 3)))
    s_ = rotz(SHELL_TOP, ang_); s_.apply_translation([0, 0, dz])
    LIPSWEEP.append((round(float(ang_), 1), round(float(dz), 2), round(vol(I(s_, P['labbro_ombra_v611'])), 3)))
BAY_MAX = max(v for _, _, v in SWEEP)
ins = rotz(U([R61['chiocciola_v61'], LATCH, P['guscio_v611']]), -bd.LOCK_ROT); ins.apply_translation([0, 0, -bd.LIFT])
BAY_INS = round(vol(I(I(ins, above(40.0)), FIXED)), 4)
print('sweep', SWEEP, '\nskirt lip vs shell', LIPSWEEP, '\ninsertion', BAY_INS)

# ---------------- cap removal / fitting path with the turns in the ENTRY pose ----------------
print('\n--- cap path ---')
tt_entry = [rotz(at(m, -x, -y), -90.0) for m, (x, y) in zip(TTS, TT)]
tt_entry = [at(m, x, y) for m, (x, y) in zip(tt_entry, TT)]
keys_entry = U([at(rotz(at(build_key(x, y), -x, -y), -90.0), x, y) for x, y in TT])
CAPSET = U([P['fondello_v611']] + tt_entry + [keys_entry])
STAT = U([P['scatola_v611'], P['scivolo_v611'], P['guscio_v611']])
PATH = []
for dz in (0.3, 0.0, -1.2, -2.0, -5.0, -10.0, -20.0, -40.0):
    m = CAPSET.copy(); m.apply_translation([0, 0, dz])
    PATH.append((dz, round(vol(I(m, STAT)), 3)))
ROT = []
for a in range(0, 91, 10):                                    # cap pressed 0.3 over lock, keys swing over the ledge tops
    ks = U([at(rotz(at(build_key(x, y), -x, -y), -90.0 + a), x, y) for x, y in TT]); ks.apply_translation([0, 0, NOTCH])
    ROT.append((a, round(vol(I(ks, P['scatola_v611'])), 3)))
KEYS_LOCK = round(vol(I(BOUGHT['keys_3x3x18'], P['scatola_v611'])), 4)
print('cap path (dz, mm3)', PATH, '\nkey swing at +0.3 (deg, mm3)', ROT, '\nkeys at lock vs box', KEYS_LOCK)

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


CUPS = I(P['scatola_v611'], below(Z_W - 0.5))
CLR = {'cups_to_cap': min_dist(CUPS, P['fondello_v611']), 'turn_C_to_board': min_dist(TTS[2], BOUGHT['board_70x50']),
       'box_to_board': None, 'box_to_servo': min_dist(I(P['scatola_v611'], below(CAGE_Z0 - 1.0)), BOUGHT['servo']),
       'cup_AB_to_chute': min_dist(I(P['scatola_v611'], box(-45, -14, -60, 60, -95, -30)), P['scivolo_v611']),
       'chute_to_box': min_dist(P['scivolo_v611'], P['scatola_v611']),
       'box_to_shell': min_dist(P['scatola_v611'], P['guscio_v611']),
       'socket_lip_groove_to_gasket_groove_web_mm': round((Z_C - GRV_D) - SOCK['groove'][1], 2),
       'dish_to_outlet_chamfer_mm': [round(Point(x, y).buffer(TT_DISH_D / 2).distance(Point(CH_X, 0).buffer(OUTLET['r'] + OUTLET['chamfer'])), 2) for x, y in TT],
       'dishes_inside_flat_bottom': [bool(Point(pod_circle(0.0, Z_BOT)[0], 0).buffer(pod_circle(0.0, Z_BOT)[1] - 0.01, resolution=128).contains(Point(x, y).buffer(TT_DISH_D / 2))) for x, y in TT],
       'drain_holes_inside_flat_bottom': bool(Point(pod_circle(0.0, Z_BOT)[0], 0).buffer(pod_circle(0.0, Z_BOT)[1] - 0.01).contains(Point(*DRAIN_XY).buffer(DRAIN['holes_r'] + 0.4))),
       'key_stop_clearance_at_lock_mm': 0.13, 'key_wrong_way_rotation_deg': 5.8}
CLR['box_to_board'] = min_dist(BOUGHT['board_70x50'], I(P['scatola_v611'], box(-100, 100, -30, 30, -100, -60)))
print(CLR)
print(f'part A done in {time.time() - t_start:.0f} s')

# ---------------- forces and torques (hand calcs) ----------------
E_TPU, MU_TPU, MU_G, MU_KEY = 30.0, 0.6, 0.2, 0.15
LIP_LINE = 0.3                                                 # v6.1 assumption for the cap lip (bent 1.2, 0.3 N/mm)
F_LIP = LIP_LINE * WALL_C.length
FC_OR = {'seam_15pct': 0.07, 'tt_23pct': 0.12, 'btn_12pct': 0.05}   # running friction per mm of seal line, NBR70 greased (Parker-type estimate)


def shares(F, xy):
    """vertical reactions of A, B, C for a force F at xy (3 supports)"""
    Mx = np.array([[1, 1, 1], [TT[0][0], TT[1][0], TT[2][0]], [TT[0][1], TT[1][1], TT[2][1]]], float)
    return np.linalg.solve(Mx, np.array([F, F * xy[0], F * xy[1]]))


cx_s, R_s = SEAM_CX, SEAM_R
F_SEAM = FC_OR['seam_15pct'] * 2 * math.pi * R_s
r_gr = R_s - (0.25 + SEAM_G)
OR_ID = min(STD_ID_CS2, key=lambda v: abs(2 * r_gr / v - 1.02))
L_cl = math.hypot(CH_LIP['root'][0] - CH_LIP['tip'][0], CH_LIP['root'][1] - CH_LIP['tip'][1])
th_cl = math.atan2(CH_LIP['root'][0] - CH_LIP['tip'][0], CH_LIP['root'][1] - CH_LIP['tip'][1])
d_cl = RO - CH_LIP['tip'][0]
fw_cl = E_TPU * CH_LIP['t'] ** 3 * d_cl * math.cos(th_cl) / (4 * L_cl ** 3) * math.cos(th_cl)
F_CL = fw_cl * 2 * math.pi * RO
L_sh = math.hypot(SH_LIP['root'][0] - SH_LIP['tip'][0], FL_Z0 + 0.3 - SH_LIP['tip'][1])
th_sh = math.atan2(SH_LIP['root'][0] - SH_LIP['tip'][0], FL_Z0 + 0.3 - SH_LIP['tip'][1])
d_sh = R_TOP - SH_LIP['tip'][0]
fw_sh = E_TPU * SH_LIP['t'] ** 3 * d_sh * math.cos(th_sh) / (4 * L_sh ** 3) * math.cos(th_sh)
F_SH = fw_sh * 2 * math.pi * R_TOP
T_SH = MU_TPU * F_SH * R_TOP / 1000
sh_lip = shares(F_LIP, gc)
sh_seam = shares(F_SEAM, (cx_s, 0.0))
T_OR_TT = FC_OR['tt_23pct'] * math.pi * TT_BORE_D * TT_BORE_D / 2 / 1000
F_BTN_OR = FC_OR['btn_12pct'] * math.pi * BTN611['head_d']
a_tab = BTN_Z - 40.0
F_TAB = 3 * 2000.0 * (8.0 * 1.4 ** 3 / 12) * 1.5 / a_tab ** 3
F_hold = sh_lip
key_r = (LEDGE_Y + LEAD + KEY['l'] / 2) / 2
TORQUE = {
    'model': 'cap lip 0.3 N/mm x D outline (v6.1 assumption); O-ring running friction fc x seal length (NBR70, greased, Parker-type estimate: '
             '0.07 N/mm at 15 %, 0.12 at 23 %, 0.05 at 12 %); TPU lip flaps as cantilevers F/w = E t^3 d cos(th) / (4 L^3), E 30 MPa; '
             'mu TPU/PETG 0.6, PETG/PETG greased 0.2, steel/PETG greased 0.15',
    'cap_lip_force_N': round(F_LIP, 1), 'lip_shares_N': {k: round(float(v), 1) for k, v in zip('ABC', sh_lip)},
    'seam_oring': {'size': f'{OR_ID:.0f}x{OR_SEAM_CS:.0f} NBR70', 'groove_bottom_d': round(2 * r_gr, 1), 'stretch_pct': round(100 * (2 * r_gr / OR_ID - 1), 1),
                   'squeeze_pct': round(100 * (OR_SEAM_CS - 0.25 - SEAM_G) / OR_SEAM_CS, 1), 'drag_N': round(F_SEAM, 1),
                   'engages_mm_before_lock': round(sum(ZG_SEAM) / 2 - Z_S, 1)},
    'chute_lip': {'radial_N': round(F_CL, 2), 'axial_drag_N': round(MU_TPU * F_CL, 2), 'interference_mm': round(d_cl, 2), 'flap_L_t': [round(L_cl, 2), CH_LIP['t']]},
    'cap_push_home_N': round(F_LIP * (1.5 / 1.2) + F_SEAM + MU_TPU * F_CL, 0),
    'thumbturn': {
        'with_cap_pressed_home_Nm': round(T_OR_TT + MU_KEY * 0.05 * key_r / 1000, 3),
        'note_pressed': 'documented bench procedure (unit upside down): press the cap home with the palm, turn each orange ridge 90 deg clockwise '
                        '(seen from below), release: the key drops 0.3 into the notch (click); only the O-ring 8x1.5 drags',
        'under_lip_load': 'locked: the key sits 0.3 deep in a straight-walled notch under the lip share (A %.0f N, B %.0f N, C %.0f N) - it cannot be turned '
                          'or shaken open; to open press the cap 0.3 home and turn back' % tuple(sh_lip),
        'oring_8x1.5_Nm': round(T_OR_TT, 3), 'key_contact_per_side_mm2': round((CUP_RI - 0.6 - (LEDGE_Y + 0.7)) * KEY['w'], 1),
        'key_bearing_MPa_at_lock_C': round(max(sh_lip) / 2 / ((KEY['l'] / 2 - (LEDGE_Y + 0.7)) * KEY['w']), 1),
        'key_bearing_MPa_load_case_132N': round(132 / 2 / ((KEY['l'] / 2 - (LEDGE_Y + 0.7)) * KEY['w']), 1),
        'v61': 'arms sat UNDER the posts: no torque figure possible, the cap was not held'},
    'twist_removal_extra_Nm': {'skirt_lip': round(T_SH, 2), 'skirt_lip_radial_N': round(F_SH, 2), 'rim_lip_v61': 1.35,
                               'total_extra_vs_v6_solid_ring': round(T_SH + 1.35, 2),
                               'note': 'radial contact: no lift component; the skirt slides 26 deg on the shell cylinder, drops off with the 1.5 lug ramp'},
    'push_button': {'oring_drag_N': round(F_BTN_OR, 1), 'latch_tab_return_N_at_1.5mm': round(F_TAB, 0), 'verdict': 'tab return force >> O-ring drag'}}
print(json.dumps(TORQUE, indent=1))

# ---------------- grams ----------------
print('\n--- grams ---')
V61 = json.load(open(OUT + 'v61.json'))
G611 = {}
QTY = {'nottolino_v611': 3}
for k, m in P.items():
    s_, e_ = v6.grams_est(m, RHO[k])
    q = QTY.get(k, 1)
    G611[k] = {'qty': q, 'volume_cm3': round(abs(m.volume) / 1000 * q, 2), 'grams_solid': round(s_ * q, 1), 'grams_print_est': round(e_ * q, 1),
               'material': 'TPU 95A' if RHO[k] == TPU else 'PETG', 'watertight': bool(m.is_watertight)}
REPL = {'fondello_v611': 'fondello_v61', 'scatola_v611': 'scatola_v61', 'guscio_v611': 'guscio_v61', 'pulsante_v611': 'pulsante_v61',
        'flangia_piano_v611': 'flangia_piano_v61', 'scivolo_v611': 'scivolo_v61', 'nottolino_v611': 'nottolino_v61'}
g61 = V61['grams']['v61']
old = sum(g61[v]['grams_print_est'] for v in REPL.values())
new_ = sum(G611[k]['grams_print_est'] for k in G611)
tot61 = V61['grams']['v61_total']['grams_print_est']
GRAMS = {'method': V61['grams']['method'], 'v611_changed_parts': G611,
         'replaced_v61_parts_print_est_g': round(old, 1), 'new_v611_parts_print_est_g': round(new_, 1),
         'delta_print_est_g': round(new_ - old, 1), 'v611_total_print_est_g': round(tot61 - old + new_, 1), 'v61_total_print_est_g': tot61,
         'delta_pct': round(100 * (new_ - old) / tot61, 1),
         'by_part_delta_g': {k: round(G611[k]['grams_print_est'] - g61[REPL[k]]['grams_print_est'], 1) for k in REPL},
         'new_TPU_g': round(G611['labbro_ombra_v611']['grams_print_est'] + G611['labbro_scivolo_v611']['grams_print_est'], 1),
         'bought_added': '3 keys 3x3x18 A4 (~3.8 g), O-rings 132x2 + 14x1.5 + 2x 8x1.5'}
print(json.dumps({k: v for k, v in GRAMS.items() if k != 'v611_changed_parts'}, indent=1))

# ---------------- assembled-position files ----------------
def save(name, m):
    p = ASM + name + '.stl'
    m.export(p)
    return p


FILES = {}
for k in P:
    FILES[k] = OUT + k + '.stl'
for k, m in zip('ABC', TTS):
    FILES[f'nottolino_{k}'] = save(f'nottolino_v611_{k}', m)
for k, m in list(BOUGHT.items()) + list(SCREWS.items()):
    FILES[k] = save('bought_' + k.replace('.', '_'), m)
# the cap and the shell are split into watertight bands so that the viewer keeps them at full detail (10k faces per entry)
CAP_BANDS = [('fondello_v611_fondo', -200, -99.0), ('fondello_v611_fianco', -99.0, -86.0), ('fondello_v611_bordo', -86.0, 0.0)]
for nm, z0, z1 in CAP_BANDS:
    FILES[nm] = save(nm, I(P['fondello_v611'], box(-200, 200, -200, 200, z0, z1)))
SHELL_BANDS = [('guscio_v611_basso', -200, -10.0), ('guscio_v611_alto', -10.0, 200)]
for nm, z0, z1 in SHELL_BANDS:
    FILES[nm] = save(nm, I(P['guscio_v611'], box(-200, 200, -200, 200, z0, z1)))
print('assembled-position copies written')

# ---------------- render ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
ELEC = U([BOUGHT[k] for k in ('board_70x50', 'esp32', 'reg_12v_d36v50f6', 'reg_5v_logic', 'cap_1000uF')])
DRAW = [('shelf', SHELF, '#E8D9B5', '#8A6D3B', '///'),
        ('electronics / servo (bought)', U([ELEC, BOUGHT['servo']]), '#CCCCCC', '#666666', '...'),
        ('guscio / fondello v611 (pod)', U([P['guscio_v611'], P['fondello_v611']]), '#2a2b2e', 'k', None),
        ('flangia v611 / colonna / scatola v611', U([P['flangia_piano_v611'], R61['colonna_v61'], P['scatola_v611']]), '#4a4a4a', 'k', None),
        ('chiocciola_v61', R61['chiocciola_v61'], '#606060', 'k', None),
        ('scivolo v611 (green)', P['scivolo_v611'], '#2E9D4F', 'k', None),
        ('thumb-turns / push-button (orange)', U(TTS + [P['pulsante_v611']]), '#F07A1A', '#7A3A00', None),
        ('TPU: skirt lip, chute lip, cap lip (yellow)', U([P['labbro_ombra_v611'], P['labbro_scivolo_v611'], R61['guarnizione_fondello_v61']]), '#F2C81E', '#7A6A00', None),
        ('O-rings (black)', U([BOUGHT['oring_tt_8x1.5'], BOUGHT['oring_seam_2'], BOUGHT['oring_btn_14x1.5']]), '#111111', '#000000', None),
        ('keys 3x3x18 (steel)', BOUGHT['keys_3x3x18'], '#A8ADB3', '#555555', None)]


def draw(ax, origin, u_, v_, title, xlim, ylim):
    n_ = np.cross(u_, v_)
    T = np.eye(4); T[0, :3], T[1, :3], T[2, :3] = u_, v_, n_; T[:3, 3] = -T[:3, :3] @ np.asarray(origin, float)
    for nm, m, fc_, ec, hatch in DRAW:
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
draw(axs[0, 0], [0, 0, 0], X_, Z_, f'{VER} section Y=0: closed pod, chute in the cap socket, cup C under the board', (-95, 95), (-110, 75))
draw(axs[0, 1], [TT[0][0], TT[0][1], 0], X_, Z_, 'turn A (XZ): solid dish wall, O-ring 8x1.5, key on the bridged ledges, cup to the roof', (-16, 16), (-106, -78))
draw(axs[0, 2], [TT[2][0], 0, 0], Y_, Z_, 'turn C (YZ): key in the 0.3 notch, dry-box O-ring', (-16, 16), (-106, -78))
draw(axs[0, 3], [0, 0, 0], X_, Z_, 'outlet socket: TPU lip ring on the chute, D upstand with retaining groove', (-72, -10), (-106, -66))
cxs_, Rs_ = SEAM_CX, SEAM_R
draw(axs[1, 0], [0, 0, 0], X_, Z_, 'seam O-ring 132x2 in the vertical spigot (+X side)', (cxs_ + Rs_ - 12, cxs_ + Rs_ + 6), (-80, -62))
draw(axs[1, 1], [0, 0, 0], X_, Z_, 'shadow gap: flange r 84.5 + TPU skirt lip on the shell', (72, 90), (56, 74))
draw(axs[1, 2], [DRAIN_XY[0], DRAIN_XY[1], 0], np.array([math.cos(math.radians(45)), math.sin(math.radians(45)), 0]), Z_,
     'drain labyrinth (through 2 exit holes): slits 0.8 / holes 0.8, no line of sight', (-9, 9), (-105.5, -95))
draw(axs[1, 3], [0, 0, BTN_Z], np.array([math.cos(ua), math.sin(ua), 0]), np.array([-math.sin(ua), math.cos(ua), 0]), 'latch push-button: O-ring 14x1.5 in the bore (horizontal section)', (58, 84), (-13, 13))
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
axs[0, 0].legend(handles, [d[0] for d in DRAW], loc='upper right', fontsize=8)
plt.tight_layout()
plt.savefig(OUT + 'check_v611.png', dpi=60)
plt.close(fig)
print('check_v611.png written')

# ---------------- v611.json ----------------
MEAS61 = json.load(open(dt.HERE + 'ref/measure_v61.json'))   # v6.1 baseline, measured once
WT = {k: bool(m.is_watertight) for k, m in P.items()}
WT.update({f'nottolino_{k}': bool(m.is_watertight) for k, m in zip('ABC', TTS)})
HEX = {
    'fondello_v611': 'PETG black: v6.1 cap + solid Ø31 walls round the 3 dishes (v6.1 dish broke through the floor), round Ø10.3 bores (no keyway), '
                     'D upstand 4.4 wide with a real 2.1 retaining groove for the reused lip, thicker spigot with an O-ring groove, outlet socket '
                     'Ø48.7 with a lip-ring groove (chute enters 8.6 mm), 1.5 deg sloped wet-ring floor, labyrinth drain (no drain slots)',
    'nottolino_v611': 'PETG orange x3: ridge flush with the flat bottom, face Ø18 + 45 deg cone, Ø10 shaft with O-ring groove 8x1.5, square 3x3 hole for '
                      'the steel key (captive once pressed), 128 facets',
    'scatola_v611': 'PETG black: v6.1 box; v6.1 posts + detent bumps removed; 3 cups (tube Ø22.4/19.2, two bridged ledges with 45 deg lead-in and a 0.3 '
                    'notch, 4 stop ribs): A/B cups rise to the roof plane outside the -X wall (web to the wall), C cup under the board hung from a '
                    'column in the servo | board corridor',
    'guscio_v611': 'PETG black: v6.1 shell + vertical inner seam band (z -72..-66, constant circle: the cap spigot slides straight in), 0.8 lead-in '
                   'chamfer at the seam edge (O-ring), 0.6 chamfer at the top outer edge (skirt lip), push-button boss 1.5 longer inward with an O-ring 14x1.5 groove',
    'pulsante_v611': 'PETG orange: v6.1 push-button with the head 1.5 longer (covers the bore O-ring at rest and pressed)',
    'flangia_piano_v611': 'PETG black: v6.1 flange with the plate r 82 -> 84.5 (2.5 mm drip overhang over the shadow gap) and a 1.0 x 1.6 groove '
                          'for the skirt lip; hooks, pins, screws, grommet unchanged',
    'scivolo_v611': 'PETG green: v6.1 chute 8.3 mm longer (end z -81.3) with a 1 mm 45 deg lead-in; enters the cap socket'}
TPUD = {'labbro_ombra_v611': 'skirt lip ring: anchor 1.1 x 1.55 pressed in the flange groove, 0.5 flap hanging 20 deg in, 0.4 radial interference on '
                             'the shell outer cylinder at z ~63: closes the 2.1 shadow gap, slides during the 30 deg twist, drops off with the unit',
        'labbro_scivolo_v611': 'chute lip ring: anchor 1.55 x 2.0 pressed in the cap socket groove, 0.6 flap leaning 30 deg down-in, 0.4 radial '
                               'interference on the chute OD: the outlet bore no longer reaches the pod interior'}
HARDWARE_ADDED = [
    {'qty': 2, 'item': 'O-ring NBR70 8x1.5', 'use': 'thumb-turns A and B (v6.1 had one, on C only): now 3 in total'},
    {'qty': 3, 'item': 'parallel key DIN 6885 B 3x3x18, stainless A4 (or 3x3 stainless square bar cut to 18)', 'use': 'pressed through the thumb-turn shaft above the cap boss: captive + bears on the cup ledges'},
    {'qty': 1, 'item': f'O-ring NBR70 {OR_ID:.0f}x2', 'use': 'shell | cap seam, in the cap spigot groove (stretch %.1f %%, squeeze 15 %%)' % TORQUE['seam_oring']['stretch_pct']},
    {'qty': 1, 'item': 'O-ring NBR70 14x1.5', 'use': 'latch push-button, in the shell bore groove'},
    {'qty': 1, 'item': 'food-grade silicone grease NSF H1 (as v6.1)', 'use': 'FACTORY: all O-rings, key ledges, face cones'}]
ASSEMBLY = [
    'FACTORY cap: guarnizione_fondello_v61 pressed into the new groove; labbro_scivolo_v611 pressed into the socket groove; seam O-ring into the spigot groove (greased); '
    'each thumb-turn with its O-ring 8x1.5 pushed up through its bore from below, then the 3x3x18 key pressed through the shaft (captive)',
    'FACTORY flange: labbro_ombra_v611 pressed into the underside groove (before the flange goes on the shelf)',
    'FACTORY shell: push-button O-ring in the bore groove, button inserted from inside',
    'CLOSE (bench, unit upside down): turns in the OPEN pose (ridges along Y), lower the cap onto the box (keys pass between the ledges, chute enters the socket), '
    'press the cap home with the palm (~%d N), turn each ridge 90 deg clockwise seen from the bottom (to X), release: click' % TORQUE['cap_push_home_N'],
    'OPEN: press the cap 0.3 home, turn the ridges back to Y, lift the cap off',
    'INSTALL / REMOVE the unit: unchanged (one twist); the TPU skirt slides on the shell and lets go when the unit drops']
IP = {
    'summary': 'dry zone = the inner box, design target IP66 (primary barrier); pod = closed second barrier (no line of sight, every joint sealed by a '
               'designed TPU / O-ring contact, one insect-proof condensation drain); the kibble path (bowl -> chute -> outlet) stays open by design '
               '(rotary airlock) and is sealed off from the pod interior; all ratings are design targets until tested',
    'dry_zone_primary_barrier': {
        'boundary': 'tower bore below the 2 shaft O-rings 9x2 + face O-ring 24x2 + box walls/roof + M12 IP68 gland + M12 IP68 ePTFE vent + cap lip seal '
                    '(now in a real retaining groove) + cap floor inside the D + thumb-turn C O-ring 8x1.5 (now effective: round bore, no keyway, solid dish)',
        'v61_defect_fixed': 'v6.1 dish C broke through the cap floor (open ring r 10..13, %.0f mm2 see-through) and its keyway bypassed the O-ring: the dry box was open to the outside' % MEAS61['thumbturns']['line_of_sight']['C']['vertical_see_through_mm2'],
        'IP66_review': ['lip seal: TPU 95A lip bent 1.2 on a 3.0 mm rim face; outside pressure pushes it shut; jets do not reach it directly (inside the pod)',
                        'O-rings: 9x2 x2 (shaft), 24x2 (face), 8x1.5 (turn C): 15-25 % squeeze, greased NSF H1 at the factory',
                        'gland + vent: bought IP68 parts, M12x1.5 into 2.0-2.4 mm PETG with locknuts: use the gland O-ring on a flat, ironed face',
                        'walls: 2.0 box walls / 2.4 roof / 2.0 cap floor; printed PETG is porous at layer seams and perimeter joins unless solid',
                        'second barrier: jets hit the pod, not the box'],
        'print_settings_for_tightness': ['0.4 nozzle, 0.2 layers, >= 4 perimeters at 0.42 (fills a 2.0 wall solid: no infill pockets), 100 % infill everywhere on the box '
                                         'and the cap (both are small), >= 5 top and 5 bottom layers',
                                         '100 % solid within 5 mm of every seal face: box rim face, cap groove and upstand, socket, O-ring bores, gland and vent pads',
                                         'extrusion multiplier +2..5 % over the dimensional calibration, nozzle 245-250 C, part fan <= 40 % for layer bonding',
                                         'seam position: rear / aligned away from seal faces; ironing on the box rim face (it prints as the top surface)',
                                         'check: hold the empty box against a bright light in a dark room; pinholes glow',
                                         'optional: brush a thin coat of food-safe epoxy or PU varnish on the inside of the box and the cap D'],
        'rating': 'IP66 design target for the box; untested'},
    'pod_second_barrier': {
        'joints': ['thumb-turns A/B/C: solid dish walls, round bores, O-ring 8x1.5 each, face disc + 45 deg cone; no keyway',
                   'shell | cap seam: O-ring %dx2 in the spigot (15 %% squeeze), 0.6 visible seam stays as a shadow line' % OR_ID,
                   'shadow gap 2.1 under the flange: flange overhang 2.5 + TPU skirt lip on the shell (radial, continuous 360 deg)',
                   'latch push-button: O-ring 14x1.5 in the bore', 'chute <-> cap outlet: TPU lip ring in a socket (the outlet bore no longer opens into the pod)',
                   'cable: TPU grommet in the flange (as v6.1)', 'flange <-> bowl rim: TPU lip seal (as v6.1)', 'chute <-> bowl joint z 0: bolted face contact (as v6.1)'],
        'condensation_drain': 'one labyrinth drain at the low point (wet-ring floor sloped 1.5 deg towards it): 3 entry slits 0.8 at floor level into a sump, '
                              '4 exit holes Ø0.8 through a 1.5 web; entry and exit never line up -> no line of sight, no direct jet path; also the pressure '
                              'breather of the pod (closed volume, thermal pumping)',
        'insects': '0.8 mm stops wasps, spiders (adults), common garden ants (Lasius / Tetramorium heads 0.7-1.0 mm); the very smallest ants (pharaoh / '
                   'ghost ant workers, head ~0.4 mm) could pass the drain but find no food: the kibble path is not connected to the pod interior',
        'rating': 'closed second barrier; no IP figure claimed for the pod alone'},
    'kibble_path': 'open by design: bowl -> dosing disc (rotary airlock: a pocket never connects window and outlet) -> chute -> socket -> outlet bore; '
                   'now sealed from the pod interior by the chute lip ring',
    'home_test_procedure': {
        'prepare': ['empty unit, electronics REMOVED (or a dummy board); put dry paper-towel strips in the box: at the gland, the vent, along the cap lip, '
                    'at thumb-turn C; put a few strips inside the pod (behind the seam, round turns A/B, under the shadow gap)',
                    'weigh a 10 g silica-gel bag on a 0.01 g scale and put it in the box; mount the unit under a shelf / board as in use'],
        'IP65_like': ['garden hose with a jet nozzle at ~6 mm opening; check the flow: 12.5 L/min = a 10 L bucket in 48 s',
                      'spray from 2.5-3 m, from every direction you can reach incl. from below and the shadow gap, about 1 min per 0.1 m2 surface, '
                      '3 min minimum (the pod is ~0.1 m2: 3-4 min total)'],
        'IP66_like': ['strongest jet setting, nozzle ~12 mm if available, from 1-1.5 m to make up for the garden-hose flow (IP66 is 100 L/min; a hose '
                      'gives 15-30 L/min, so this is only an approximation), 3 min from all directions'],
        'after': ['dry the outside, remove the unit, open the cap upside down over a towel; dry strips = pass; any wet strip in the box = fail (find '
                  'the leak); wet strips in the pod tell where the second barrier lets water in',
                  'silica bag gain < 0.05 g = no ingress', 'leave the unit 24 h in the sun after the test and check for fogging inside the box'],
        'bubble_test_box': ['box + cap alone: replace the vent with a fitting + hose, pressurise to 0.05 bar (50 cm of water column in a U-tube made '
                            'of clear hose), dunk in a bucket and watch for bubbles (seams, layer lines, gland); never above 0.1 bar (the lip lifts)'],
        'note': 'a home test is a screening, not a certification'}}
DEV = ['seam spigot made vertical (and the shell inner face vertical over the 6 mm seam band): the v6.1 spigot copied the pod taper and its top was '
       '~0.5 mm wider than the shell mouth on the +X side, so the cap could only be forced on / off',
       'thumb-turn retention redesigned: v6.1 arms sat under the box posts (both contacts pushed the turn down) so the cap was not held; v6.1.1 keys rest ON '
       'bridged ledges in box cups (upward-facing, printable without supports) and the cap must be pressed home to turn (positive lock)',
       'thumb-turns A/B moved 3 mm to -X (x -29, y +-37): their cups must clear the 4.4 mm cap upstand; dish-to-outlet-chamfer web now %.2f mm (v6.1 3.27)' % CLR['dish_to_outlet_chamfer_mm'][0],
       'chute 8.3 mm longer into a cap socket instead of a 1 mm air gap (drip edge no longer needed: the joint is sealed)',
       'flange plate r 84.5: the top of the pod now shows a 2.5 mm overhang (drip edge) instead of a flush rim',
       'the box needs no supports; the C cup ring is the only part that starts in mid-air in the flipped box print over x > 21 (tree support there)']
RISKS = ['seam O-ring %dx2 on a printed spigot: groove roundness depends on the cap print; check squeeze on the first print (should feel a light drag over the last 2 mm)' % OR_ID,
         'TPU lips (skirt 0.5, chute lip 0.6): print test rings first; the skirt anchor groove is 1.0 wide',
         'drain holes Ø0.8 on the bed side: clear with a 0.8 drill after printing (first-layer squish can close them)',
         'cap push-home force ~%d N on the bench (lip + seam O-ring): acceptable by hand with the unit upside down; on the shelf the cap is not opened' % TORQUE['cap_push_home_N'],
         'key bearing on PETG ledges at lock (C): %.1f MPa, load case %.1f MPa: watch for creep marks after a summer' % (TORQUE['thumbturn']['key_bearing_MPa_at_lock_C'], TORQUE['thumbturn']['key_bearing_MPa_load_case_132N'])]
v611doc = {'version': VER, 'base': 'v6.1 (v61.json): everything not listed here is unchanged',
           'frame': 'as v6.1: Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED pose',
           'concept': 'the pod becomes a closed second barrier round the dry box: every joint sealed, no line of sight, one insect-proof drain',
           'measured_v61_gaps': MEAS61,
           'changed_parts_PETG': HEX, 'new_parts_TPU_95A': TPUD, 'reused_unchanged_from_v61': [
               'chiocciola_v61', 'piastra_gate_v61', 'piastra_finestra_v61', 'disco_v61', 'labbro_uscita_v61 (+_b)', 'labbro_finestra_v61 (+_b)', 'guarnizione_baionetta_v61',
               'colonna_v61', 'passacavo_v61', 'guarnizione_fondello_v61 (now retained in a groove)', 'colletto_v6', 'linguetta_sicura', 'albero_v6', 'mozzo_v6', 'guarnizione_piano_v5'],
           'thumbturns_xy': TT, 'hardware_added': HARDWARE_ADDED, 'assembly': ASSEMBLY, 'ip_rating': IP, 'torques_forces': TORQUE,
           'deviations': DEV, 'open_risks': RISKS,
           'checks': {'watertight_built': WT, 'watertight_exported_stl_reload': EXPORT_WT,
                      'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
                      'designed_seal_contacts_mm3': {k: {'overlap_mm3': v, 'role': SEAL_ROLE.get(frozenset(k.split('|')), 'v6.1 designed contact')} for k, v in soft.items()},
                      'seal_continuity_36_sectors': CONT, 'line_of_sight': LOS,
                      'bayonet': {'removal_sweep_angle_dz_mm3': SWEEP, 'max_mm3': BAY_MAX, 'unit_at_insertion_vs_flange': BAY_INS,
                                  'skirt_lip_vs_shell_along_sweep_mm3': LIPSWEEP},
                      'cap_path_entry_pose_dz_mm3': PATH, 'key_swing_pressed_deg_mm3': ROT, 'keys_at_lock_vs_box_mm3': KEYS_LOCK,
                      'clearances_mm': CLR, 'print_downfacing_flatter_45_mm2': OVH,
                      'v61_colour_bodies_reexported': COLFIX},
           'grams': GRAMS,
           'print': {'fondello_v611': 'as v6.1 (flat bottom on the bed); clear the 4 drain holes with a 0.8 drill; 100 % infill',
                     'nottolino_v611': 'flipped (shaft top on the bed), cone carries the face; 100 % infill; key hole bridges',
                     'scatola_v611': 'flipped (roof on the bed): A/B cups grow from the bed, ledges print as bridges, ribs vertical; tree support only under the '
                                     'far half of the C cup ring (x > 21); 100 % infill',
                     'guscio_v611': 'as v6.1 (seam edge on the bed); 5 perimeters',
                     'pulsante_v611': 'as v6.1 (standing on its head face)', 'flangia_piano_v611': 'as v6.1 (shelf face on the bed); the skirt groove opens upward',
                     'scivolo_v611': 'as v6.1 (flange on the bed)', 'labbro_ombra_v611': 'flipped: anchor on the bed, the 0.5 flap rises as a 20 deg cone; TPU 95A, 1 clean perimeter on the flap, slow',
                     'labbro_scivolo_v611': 'flipped: anchor on the bed, flap up; TPU 95A'},
           'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] for k in P} |
                    {'assembled_position_copies': 'v611_asm/*.stl', 'check': 'check_v611.png', 'viewer': 'v611_viewer.json',
                     'v61_colour_bodies_fixed': [f'{n}_print_{c}_v611.stl' for n, cs in (('disco_v61', ('orange', 'black')), ('piastra_gate_v61', ('black', 'green')),
                                                                                          ('piastra_finestra_v61', ('black', 'green'))) for c in cs] +
                                                [f'{n}_print_v611.3mf' for n in ('disco_v61', 'piastra_gate_v61', 'piastra_finestra_v61')]}}
_dflt = lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
json.dump(v611doc, open(OUT + 'v611.json', 'w'), indent=1, default=_dflt)
print('v611.json written')

# ---------------- v611_viewer.json (lod_faces = hint for the pre-decimation step; visible parts keep full detail) ----------------
V61V = json.load(open(OUT + 'v61_viewer.json'))
REPL_V = {'flangia_piano_v61': [('flangia_piano_v611', 'Flangia piano (sporgenza 2.5)', FILES['flangia_piano_v611'], None)],
          'guscio_v61': [(nm, 'Guscio (pod) ' + ('basso' if 'basso' in nm else 'alto'), FILES[nm], None) for nm, _, _ in SHELL_BANDS],
          'pulsante_v61': [('pulsante_v611', 'Pulsante sgancio (O-ring)', FILES['pulsante_v611'], None)],
          'scivolo_v61': [('scivolo_v611', 'Scivolo (entra nel fondello)', FILES['scivolo_v611'], None)],
          'scatola_v61': [('scatola_v611', 'Scatola elettronica (3 coppe)', FILES['scatola_v611'], 6000)],
          'fondello_v61': [(nm, 'Fondello ' + {'fondello_v611_fondo': '(fondo)', 'fondello_v611_fianco': '(fianco)', 'fondello_v611_bordo': '(bordo)'}[nm], FILES[nm], None) for nm, _, _ in CAP_BANDS],
          'nottolini_v61': [(f'nottolino_v611_{k}', f'Nottolino {k} (O-ring)', FILES[f'nottolino_{k}'], None) for k in 'ABC'],
          'oring_nottolino': [('oring_nottolini', 'O-ring nottolini 8x1.5 (3)', FILES['oring_tt_8x1.5'], 1500)]}
VISIBLE = {'flangia_piano_v611', 'guscio_v611_basso', 'guscio_v611_alto', 'pulsante_v611', 'fondello_v611_fondo', 'fondello_v611_fianco', 'fondello_v611_bordo',
           'nottolino_v611_A', 'nottolino_v611_B', 'nottolino_v611_C', 'labbro_ombra_v611'}
VP = []
for p_ in V61V['parts']:
    src = p_['file'].split('/')[-1].replace('.stl', '')
    key = src if src in REPL_V else p_['id'] if p_['id'] in REPL_V else None
    if key is None:
        q = dict(p_)
        q['lod_faces'] = 2500
        if q['id'] == 'cavo_12v':
            q['file'] = FILES['cable_12v']
        VP.append(q)
        continue
    for nid, nname, f, lod in REPL_V[key]:
        q = dict(p_); q['id'] = nid; q['name'] = nname; q['file'] = f
        if nid in VISIBLE:
            q['lod_faces'] = 10000
        else:
            q['lod_faces'] = lod or 2500
        if 'oring' in nid:
            q['qty'] = 3
        if nid.startswith('nottolino_v611'):
            q['qty'] = 1
        VP.append(q)
ins_at = next(i for i, q in enumerate(VP) if q['id'] == 'flangia_piano_v611') + 1
VP.insert(ins_at, {'id': 'labbro_ombra_v611', 'name': 'Labbro ombra (TPU, chiude la fessura)', 'file': FILES['labbro_ombra_v611'], 'color': '#f2c81e', 'opacity': 1.0,
                   'group': 'guarnizioni', 'material': 'TPU 95A giallo', 'qty': 1, 'bought': False, 'explode': [0.0, 0.0, 140.0], 'rotates': False, 'lod_faces': 10000})
ii = next(i for i, q in enumerate(VP) if q['id'] == 'scivolo_v611') + 1
VP.insert(ii, {'id': 'labbro_scivolo_v611', 'name': 'Labbro scivolo (TPU, nel fondello)', 'file': FILES['labbro_scivolo_v611'], 'color': '#f2c81e', 'opacity': 1.0,
               'group': 'guarnizioni', 'material': 'TPU 95A giallo', 'qty': 1, 'bought': False, 'explode': [-85.0, 0.0, -200.0], 'rotates': False, 'lod_faces': 2500})
jj = next(i for i, q in enumerate(VP) if q['id'] == 'oring_nottolini') + 1
for nid, nm, f, col, mat, ex in (('chiavette', 'Chiavette 3x3x18 inox (3)', FILES['keys_3x3x18'], '#a8adb3', 'acciaio A4', [0, 0, -255]),
                                 ('oring_giunto', f'O-ring giunto guscio-fondello {OR_ID:.0f}x2', FILES['oring_seam_2'], '#1e1e1e', 'NBR70', [0, 0, -228]),
                                 ('oring_pulsante', 'O-ring pulsante 14x1.5', FILES['oring_btn_14x1.5'], '#1e1e1e', 'NBR70', [30 * math.cos(ua), -215 + 30 * math.sin(ua), 20])):
    VP.insert(jj, {'id': nid, 'name': nm, 'file': f, 'color': col, 'opacity': 1.0, 'group': 'guarnizioni' if 'oring' in nid else 'ferramenta', 'material': mat,
                   'qty': 3 if nid == 'chiavette' else 1, 'bought': True, 'explode': ex, 'rotates': False, 'lod_faces': 2000})
for q in VP:                                                     # orange thumb-turns explode together with the cap
    if q['id'].startswith('nottolino_v611'):
        q['explode'] = [0.0, 0.0, -270.0]
viewer = dict(V61V)
viewer['title'] = 'Kibble Dispenser Outdoor v6.1.1'
viewer['subtitle'] = 'pod chiuso: seconda barriera sigillata attorno alla scatola asciutta'
viewer['parts'] = VP
viewer['scene'] = dict(V61V['scene'])
viewer['kibble_path'] = V61V['kibble_path']
json.dump(viewer, open(OUT + 'v611_viewer.json', 'w'), indent=1)
missing = [p_['file'] for p_ in VP if not os.path.exists(p_['file'])]
print('v611_viewer.json written:', len(VP), 'entries; missing files:', missing)
print(f'checks done in {time.time() - t_start:.0f} s')
