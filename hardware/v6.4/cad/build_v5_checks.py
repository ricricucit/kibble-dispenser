# executed by build_v5.py (exec) in its namespace: interference checks, section render, v5.json
print('\n--- context solids ---')
SCREW60 = U([cyl(3.0, bd.SCREW_TIP_Z, bd.CBORE_BOT, 32), cyl(dt.SCREW_HEAD_D, bd.CBORE_BOT, bd.CBORE_BOT + dt.SCREW_HEAD_H, 48)])
PASS_SCREWS = U([at(U([cyl(3.0, -ROOF_T - 5.0 + 0.0, -1.55, 32), hull_of((circle_pts(3.0, 32), -1.55), (circle_pts(6.0, 32), 0.0))]), x, y)
                 for x, y in dt.LID_HOLES])                       # 3x M3x8 ISO 10642: tip z -8
LEG_SCREWS = U([at(U([cyl(3.0, -LEG_BOSS_H - 3.0 + 3.0 - 0.0 - 0.0, 6.0, 32), cyl(5.5, -LEG_BOSS_H - 3.0, -LEG_BOSS_H, 32)]), x, y) for x, y in LEG_XY])  # 4x M3x14
COVER_SCREWS = U([at(U([cyl(3.0, CV_Z0 + 2.0, CV_Z1 + 6.0, 32), cyl(5.5, CV_Z0 - 1.0, CV_Z0 + 2.0, 32)]), x, y) for x, y in screw_xy()])  # 6x M3x10
SHELF = D(box(-140, 120, -90, 90, FL_Z1, FL_Z1 + SHELF_T), at(cyl(SHELF_HOLE_D, FL_Z1 - 1, FL_Z1 + SHELF_T + 1), *HOLE_C))
BREADBOARD = box(BB['x'][0], BB['x'][1], BB['y'][0], BB['y'][1], CV_Z1, CV_Z1 + BB['t'])
ESP32 = box(-30, 30, BB['y'][0] + 5, BB['y'][1] - 5, CV_Z1 + BB['t'], CV_Z1 + BB['t'] + 18)     # dev board plugged in
GLAND_SOLID = xprism(Point(GLAND['y'], GLAND['z']).buffer(11.0, resolution=32), WX[1] - WALL - 15.0, WX[1] + GLAND['pad_t'] + 12.0)   # M16 gland body + nut
disc0, disc180 = R['disco_v4b'], rotz(R['disco_v4b'], 180)
bowl_ins = R['chiocciola_scivolo_v4b'].copy(); bowl_ins = rotz(bowl_ins, -LOCK_ROT); bowl_ins.apply_translation([0, 0, -BAY['lugs']['lift_mm']])
latch_ins = rotz(R['linguetta_sicura'], -LOCK_ROT); latch_ins.apply_translation([0, 0, -BAY['lugs']['lift_mm']])

ALL = {'flangia_piano_v5': flange, 'guarnizione_piano_v5': fl_gsk, 'scatola_v5': scat, 'fondello_v5': cover,
       'guarnizione_scivolo_v5': ch_gsk, 'guarnizione_collare_v5': cring, 'guarnizione_fondello_v5': U([cv_g1, cv_g2]),
       'chiocciola': R['chiocciola_scivolo_v4b'], 'piastra_gate': R['piastra_gate_v4b'], 'piastra_finestra': R['piastra_finestra_v4b'],
       'disco@0': disc0, 'disco@180': disc180, 'linguetta': R['linguetta_sicura'], 'guarnizione_baionetta': R['guarnizione_baionetta'],
       'valvola_becco': R['valvola_becco'], 'ghiera_valvola': R['ghiera_valvola'],
       'lips': U([R[k] for k in R if k.startswith('labbro')]),
       'albero_mozzo': R['albero_mozzo'], 'albero_mozzo@180': rotz(R['albero_mozzo'], 180), 'passante_culla': R['passante_culla'],
       'servo': SERVO, 'screw_M3x60': SCREW60, 'passante_screws': PASS_SCREWS, 'leg_screws': LEG_SCREWS, 'cover_screws': COVER_SCREWS,
       'shelf': SHELF, 'breadboard': BREADBOARD, 'esp32': ESP32, 'gland': GLAND_SOLID}
CTX = {'albero_mozzo', 'albero_mozzo@180', 'passante_culla', 'servo', 'screw_M3x60', 'passante_screws', 'leg_screws',
       'cover_screws', 'shelf', 'breadboard', 'esp32', 'gland', 'chiocciola', 'piastra_gate', 'piastra_finestra', 'disco@0',
       'disco@180', 'linguetta', 'guarnizione_baionetta', 'valvola_becco', 'ghiera_valvola', 'lips'}
NEW = [k for k in ALL if k not in CTX]
# designed soft contacts (TPU interference / compression) and parts sharing a fastener: reported separately
SOFT = {('guarnizione_scivolo_v5', 'chiocciola'), ('guarnizione_scivolo_v5', 'scatola_v5'), ('guarnizione_collare_v5', 'chiocciola'),
        ('guarnizione_fondello_v5', 'scatola_v5'), ('guarnizione_piano_v5', 'shelf'), ('guarnizione_piano_v5', 'flangia_piano_v5'),
        ('guarnizione_scivolo_v5', 'passante_culla'), ('flangia_piano_v5', 'guarnizione_baionetta')}
SKIP = {('disco@0', 'albero_mozzo@180'), ('disco@180', 'albero_mozzo'), ('disco@0', 'disco@180'),
        ('fondello_v5', 'cover_screws'), ('scatola_v5', 'cover_screws'), ('scatola_v5', 'leg_screws'), ('flangia_piano_v5', 'leg_screws'),
        ('scatola_v5', 'passante_screws'), ('passante_culla', 'passante_screws'), ('scatola_v5', 'gland'), ('fondello_v5', 'breadboard')}
print('\n--- interference (mm3): new parts vs everything ---')
inter, soft = {}, {}
names = list(ALL)
for a in NEW:
    for b in names:
        if a == b or (b in NEW and names.index(b) < names.index(a)):
            continue
        key = (a, b) if (a, b) in SKIP or (a, b) in SOFT else (b, a)
        if (a, b) in SKIP or (b, a) in SKIP:
            continue
        im = I(ALL[a], ALL[b])
        v = round(vol(im), 4)
        if (a, b) in SOFT or (b, a) in SOFT:
            soft[f'{a}|{b}'] = v
        else:
            inter[f'{a}|{b}'] = v
            if v > 1e-3:
                print(f'  HARD {a:26s}|{b:22s} {v:.4f}  bounds {np.round(im.bounds, 2).tolist()}')
HARD_MAX = max(inter.values())
print(f'{len(inter)} hard pairs, max {HARD_MAX:.4f} mm3;  soft (designed):', soft)
INS_CHECK = {'bowl@insertion|flangia': round(vol(I(bowl_ins, flange)), 4), 'linguetta@insertion|flangia': round(vol(I(latch_ins, flange)), 4),
             'bowl@locked|flangia': inter.get('flangia_piano_v5|chiocciola'), 'linguetta@locked|flangia': inter.get('flangia_piano_v5|linguetta')}
print('bayonet:', INS_CHECK)
# chimney bridge wall thickness / clearances near the passante
sec = scat.section(plane_origin=[0, 0, -20.0], plane_normal=[0, 0, 1])
CLR = {'chimney_outer_x_at_y0_z-20': None}
if sec is not None:
    p2, _ = sec.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 20.0], [0, 0, 0, 1]], float))
    line = LineString([(-60, 0), (0, 0)])
    hit = shapely.unary_union(list(p2.polygons_full)).intersection(line)
    CLR['chimney_outer_x_at_y0_z-20'] = round(max(g.bounds[2] for g in (hit.geoms if hasattr(hit, 'geoms') else [hit])), 2)
CLR['passante_cage_x'] = dt.CAGE_X_OUT0
CLR['chimney_to_cage_mm'] = round(dt.CAGE_X_OUT0 - CLR['chimney_outer_x_at_y0_z-20'], 2)
CLR['collar_ring_OD_edge_x'] = CHUTE_AX[0] + CRING_OD / 2
CLR['passante_bell_r_at_ring_top'] = dt.FL_D / 2 - (dt.FL_Z0 - (LIP_Z1 + CRING_T))
print('clearances:', CLR)
# funnel slope in the flange
fun_cav = funnel_cavity()
FUNNEL_SLOPE = round(bd.floor_slope_min(fun_cav, FL_Z0 + 0.2, NECK_Z1 - 0.2), 1)
print('flange funnel min kibble-face slope:', FUNNEL_SLOPE, 'deg')
# roof drainage
ROOF_DROP = round(-min(ztop(x, y) for x, y in np.array(ROOF_OUT.exterior.coords)), 2)
print('roof: plateau flat (bowl seat), slope', SLOPE_DEG, 'deg outside it, drop at the edge up to', ROOF_DROP, 'mm')

# ---------------- section render ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
DRAW = [('shelf (wood, drawn 20)', SHELF, '#E8D9B5', '#8A6D3B', '///'), ('breadboard/ESP32 (ghost)', U([BREADBOARD, ESP32]), '#DDDDDD', '#888888', '...'),
        ('gland (ghost)', GLAND_SOLID, '#DDDDDD', '#888888', 'xx'),
        ('flangia_piano_v5', flange, '#2B2B2B', 'k', None), ('scatola_v5', scat, '#3A3A3A', 'k', None), ('fondello_v5', cover, '#4A4A4A', 'k', None),
        ('servo', SERVO, '#8FB3E0', '#2F5D8A', None), ('passante_culla', R['passante_culla'], '#666666', 'k', None),
        ('albero_mozzo', R['albero_mozzo'], '#9A9A9A', 'k', None),
        ('chiocciola (black/green)', R['chiocciola_scivolo_v4b'], '#2E9E4F', 'k', None),
        ('plates', U([R['piastra_gate_v4b'], R['piastra_finestra_v4b']]), '#7A7A7A', 'k', None),
        ('disco', disc0, '#E8792B', 'k', None), ('orange: linguetta, ghiera', U([R['linguetta_sicura'], R['ghiera_valvola']]), '#E8792B', '#7A3A00', None),
        ('TPU (yellow)', U([fl_gsk, ch_gsk, cring, cv_g1, cv_g2, R['guarnizione_baionetta'], R['valvola_becco']] + [R[k] for k in R if k.startswith('labbro')]), '#E8D44D', '#7A6A00', None),
        ('screws', U([SCREW60, PASS_SCREWS, LEG_SCREWS, COVER_SCREWS]), '#C9A227', '#6B5410', None)]


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
fig, axs = plt.subplots(1, 3, figsize=(30, 11), facecolor='white', gridspec_kw={'width_ratios': [1.5, 1, 1]})
draw(axs[0], [0, 0, 0], [0, 1, 0], Txz, f'{VER} section Y=0 (XZ): shelf, flange+neck, dosing v4b, roof, chimney, passante/servo, cover',
     (-125, 100), (-80, 95), 'X [mm]', 'Z [mm]')
axs[0].text(-120, 91, f'shelf hole Ø{SHELF_HOLE_D:.0f} at x={HOLE_C[0]:.0f}; funnel min slope {FUNNEL_SLOPE} deg; hooks {HOOKS}; hard interference max {HARD_MAX:.3f} mm3', fontsize=8)
Tl = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float) @ np.array([[1, 0, 0, 0], [0, 1, 0, -LEG_XY[1][1]], [0, 0, 1, 0], [0, 0, 0, 1]], float)
draw(axs[1], [0, LEG_XY[1][1], 0], [0, 1, 0], Txz, f'Section Y={LEG_XY[1][1]:.0f} (XZ): legs, leg bosses + screws, rim, cover skirt, breadboard', (-125, 100), (-80, 95), 'X [mm]', 'Z [mm]')
draw(axs[2], [CHUTE_AX[0], 0, 0], [1, 0, 0], Tyz, f'Section X={CHUTE_AX[0]} (YZ) through the drop axis: chute, roof gasket, chimney, collar ring, cover', (-70, 110), (-80, 95), 'Y [mm]', 'Z [mm]')
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
axs[0].legend(handles, [d[0] for d in DRAW], loc='lower right', fontsize=7)
plt.tight_layout()
plt.savefig(OUT + 'check_v5.png', dpi=80)
plt.close(fig)
print('check_v5.png written')

# ---------------- v5.json ----------------
PRINTED = {
    'flangia_piano_v5': 'PETG black: bayonet flange, funnel neck, 4 legs (new)',
    'chiocciola_scivolo_v4b': 'PETG black+green: bowl + straight chute (reused)',
    'piastra_gate_v4b': 'PETG black+green (reused)', 'piastra_finestra_v4b': 'PETG black+green (reused)',
    'disco_v4b': 'PETG orange+black (reused)', 'linguetta_sicura': 'PETG orange (reused)',
    'ghiera_valvola': 'PETG orange (reused)', 'albero_mozzo': 'PETG black (reused, drivetrain v4)',
    'passante_culla': 'PETG black (reused, drivetrain v4)', 'scatola_v5': 'PETG black: enclosure with roof + wet chimney (new)',
    'fondello_v5': 'PETG black+orange: bottom cover (new)'}
TPU = {'guarnizione_baionetta': 'rim gasket (reused)', 'valvola_becco': 'duckbill (reused)',
       'labbro_uscita_1/2, labbro_finestra_1/2': 'plate lips (reused, 4 pcs)',
       'guarnizione_piano_v5': 'flange <-> shelf, ring 2x2 in a 2.8x1.5 groove around the hole (new)',
       'guarnizione_scivolo_v5': 'roof <-> chute: D-ring in the roof rebate, 0.3 interference on the chute, 0.8 compressed by the bowl base (new)',
       'guarnizione_collare_v5': 'chimney lip <-> chute collar: ring ID 55.4 stretched on the Ø56 collar, resting on the lip (new)',
       'guarnizione_fondello_v5': 'cover <-> box rim and cover <-> chimney: two 2x2 loops in 2.8x1.5 grooves (new, one print)'}
HARDWARE = [
    {'qty': 4, 'item': 'wood screw 5x25 pan head (5x20 for an 18 mm shelf, 5x30 for >= 25 mm)', 'use': 'flange -> shelf, heads counterbored from below'},
    {'qty': 1, 'item': f'M3x{bd.SCREW_LEN} DIN912 A2', 'use': 'disc -> shaft -> servo spline (unchanged from dosing v4b)'},
    {'qty': 3, 'item': 'M3x8 ISO 10642 (DIN 7991) countersunk A2', 'use': 'roof top -> passante_culla flange inserts (engagement 4.8)'},
    {'qty': 4, 'item': 'M3x8 DIN912 A2 + M3 washer DIN 125', 'use': 'servo tabs -> cradle inserts (unchanged, drivetrain v4)'},
    {'qty': 4, 'item': 'M3x14 DIN912 A2', 'use': 'from below through the roof leg bosses (8 mm) into the leg inserts (6 mm engagement)'},
    {'qty': 6, 'item': 'M3x10 DIN912 A2', 'use': 'cover -> blind inserts in the box rim (6 mm engagement)'},
    {'qty': 3 + 4 + 4 + 6, 'item': 'M3 brass heat-set insert L 5.7 for Ø4.0 (Ruthex RX-M3x5.7)', 'use': '3 passante flange + 4 servo pads (existing) + 4 leg ends + 6 box rim'},
    {'qty': 1, 'item': 'O-ring NBR70 9x2', 'use': 'shaft (lower groove of albero_mozzo); +1 optional upper'},
    {'qty': 1, 'item': 'O-ring NBR70 45x2', 'use': 'passante face seal to the roof underside'},
    {'qty': 1, 'item': 'M16x1.5 cable gland IP68 (hole Ø16.2, pad Ø30 on the +X wall) + locknut', 'use': 'the only cable entry (12 V power)'},
    {'qty': 1, 'item': 'food-grade silicone grease NSF H1', 'use': 'shaft O-ring, face O-ring, collar ring'}]
ASSEMBLY = [
    f'hole-saw Ø{SHELF_HOLE_D:.0f} in the shelf, centre {HOLE_C[0]:.0f} mm towards the window side (+X) from the disc axis; shelf 18..40 mm thick (neck 12 mm goes into the hole)',
    'flangia_piano_v5: press 4 inserts into the leg ends; guarnizione_piano_v5 in the top groove; neck into the hole, 4 wood screws from below',
    'dosing module pre-assembled on the bench exactly as dosing.json: latch in the wall slot, rim gasket, gate plate, disc (key rib at +Y), window plate, lips',
    'offer the bowl up between the legs: lugs at 60/180(key)/300, push up, rotate +30 deg until the orange latch clicks (chute hangs at -X)',
    'scatola_v5 pre-assembled: inserts (6 rim + passante/servo), passante+servo+shaft from below against the roof (face O-ring), 3x M3x8 countersunk from the roof top; guarnizione_scivolo_v5 in the roof rebate',
    'offer the box up: the chute collar enters the roof cutout, the shaft hex enters the disc pocket (turn the disc through the window if needed), roof plateau meets the bowl base, leg bosses meet the legs: 4x M3x14 from below',
    f'M3x{bd.SCREW_LEN} from the disc top through the flange opening + window-plate centre hole into the servo spline (hex key from above, before the drum goes on)',
    'from below through the chimney: guarnizione_collare_v5 stretched over the collar nubs up onto the lip; duckbill into the seat; ghiera quarter turn',
    'electronics: breadboard (165x55) between the cover rails, ESP32 plugged in; cable through the M16 gland; guarnizione_fondello_v5 in the two grooves',
    'cover up: inner lips enter the box and the chimney, 6x M3x10 (orange rings) into the rim inserts; drum on the shelf over the hole',
    'SERVICE: lift the drum, M3 hex key: disc screw out from above; 4 leg screws out from below (cover stays on); lower the box (shaft slides out of the disc); press the latch, rotate -30 deg, lower the bowl. Tool-free removal of the bowl alone is NOT possible with the servo in axis under it (see deviations)']
IP65 = {
    'principle': 'the only wet volumes are the bowl interior (rain through the shelf hole follows kibble to the chute) and the chimney under the chute; every joint to the dry compartment has a TPU gasket or an O-ring; openings face down',
    'openings': [
        'shelf hole -> funnel neck: open by design (kibble + rain path). Annulus neck/hole wall drains into the funnel through 6 weep slots 3x2 at the neck base; flange<->shelf: guarnizione_piano_v5 around the hole',
        'flange <-> bowl rim: labyrinth (rim tongue r 60.2..61.2 in the flange groove r 59.7..61.7) then guarnizione_baionetta compressed 1.0 by the bayonet lift (dosing v4b, unchanged)',
        'bowl base <-> roof: the base plate rests on the flat roof plateau; around the chute cutout guarnizione_scivolo_v5 (0.8 proud, compressed by the base; 0.3 interference on the chute wall where the chute is outside the base, x < -62)',
        'roof <-> passante: face O-ring 45x2 on the roof underside (flat inside Ø53), 3 countersunk screws inside the O-ring line, under the bowl base',
        'shaft: O-ring 9x2 in the passante bore + labyrinth cap of the disc over the collar (drivetrain v4, unchanged)',
        'chute <-> compartment: the chute passes through the roof into the wet chimney; guarnizione_collare_v5 on the Ø56 collar at the chimney lip (z -13.5) separates the dry collar annulus above from the wet chimney below; the chimney wall (3 mm) runs from the lip to the cover',
        'chimney bottom: open to the ground (kibble + rain), cover lip inside the bore + TPU ring under the chimney wall edge (guarnizione_fondello_v5)',
        'cover <-> box: cover skirt outside the rim (up), under the rim edge (in), 6 screws in blind inserts outside the gasket line, TPU frame 2x2 compressed 0.5 under the wall edge, inner lip inside the wall (3 direction changes, 2 before the gasket)',
        'M16 gland: the only wall opening, IP68 gland on a flat Ø30 pad, +X wall, teardrop hole Ø16.2 (printable)',
        'leg screws: through the leg bosses OUTSIDE the walls (eave) -> no roof penetration into the compartment',
        'roof: flat plateau under the bowl, 2.5 deg slope away from it beyond r 63, drip lip 1.5x1.5 all around the eave; no inspection ports, no LED windows'],
    'drain_note_v4b': 'VERIFIED, NOT PRESENT: the v4b gate plate is flat (3 annular crumb grooves 1.5x0.8 at r 28/36/44, no slope); water in the window-side pocket drains only through the outlet at 180 deg when the disc turns; the bowl base has a 1 mm floor recess around the collar and the labyrinth cap keeps water off the shaft. A sloped drain towards the chute would be a v4c change of piastra_gate (not done here: KEEP).'}
DROPPED = {
    'saracinesca + anello_imbuto': 'shutter and separate funnel ring: the funnel is now the neck of the flange (one part, no moving part); rain through the shelf hole is accepted and drained by the chute',
    'cassa_ingranaggi, albero_disco_conico, albero_servo_conico, collare_labbro, guarnizione_collo, ghiera_baionetta': 'miter gear drive + horizontal servo neck: replaced by the in-axis servo of drivetrain v4 (albero_mozzo + passante_culla), gears were the likeliest failure point',
    'T-slot posts, fermo_slitta, fermo_servo, slitta_breadboard, piedini_modulo': 'enclosure slide-on mount and sled: the box now hangs from 4 legs of the flange with 4 plain M3 screws; rails are part of the cover',
    'vite_quarto_giro x8, anello_ritegno_vite x8, test_vite_quarto_giro': '8 printed quarter-turn screws + rings: 6 plain M3 screws in heat-set inserts (quarter-turn is a later option)',
    'speaker pocket + membrana_altoparlante, camera bay, etichetta_12v, anello_pressacavo, pettine_cavi, cordino_coperchio, cuffia_*': 'no other openings (IP65 rule); speaker/camera are phase 2 and would be new openings; the small TPU accessories were part count without function in v5',
    'anello_fusto': 'drum ring on the shelf: not part of the dispenser (the drum stands on the shelf; keep as an accessory if wanted)',
    'gocciolatoio': 'TPU drip cone on the collar: the collar is now inside the dry annulus above the chimney lip; the roof gasket does its job'}
DEVIATIONS = [
    'flangia_piano_v5 is not a plain ring plate: the window footprint (+X sector r 13..49, +-48 deg) cannot be matched by a hole-saw circle that stays inside the bowl rim (r 57), so the plate carries a 12 mm funnel neck into the Ø76 shelf hole; the opening below the funnel is a pie sector (r 0..50.6, +-50.2 deg) that also exposes the disc centre screw through the window-plate hole',
    'the enclosure cannot keep the chute outside: at the roof plane the chute collar (x -28.5) is 2.0 mm from the passante flange (r 26.5) and 0.9 mm at z -3..-4 (funnel), so no wall fits between them. The chute passes through the roof into a WET CHIMNEY (bore r 34, flattened to x -24 on the passante side) with the TPU collar ring at its lip (z -13.5) as the dry/wet boundary; the raised 4 mm roof lip of the brief is impossible under the bowl base (flat at z 0), the gasket sits in a 2 mm rebate instead',
    'the box is held by 4 legs of the flange (Ø12, z 0..66) with M3x14 from below through eave bosses, not by the dosing module: the shaft/servo stack must not carry the box',
    'hook spans trimmed to [81,102] [197,227] [321,342] (spec [78,102] [193,227] [318,342]): the 32 deg key lug is wider than the 30 deg lock rotation and the latch nub must clear the 90 deg hook at insertion',
    'passante screws come from the roof TOP (countersunk, under the bowl base) into the existing passante inserts: a 3 mm roof cannot take blind inserts from below and passante_culla is not modified',
    'tool-free dosing removal is lost: with the servo in axis under the bowl, the bowl cannot drop or turn back without lowering the box (4 screws) and removing the disc screw first',
    'cover texts are flush orange inlays (0.6 mm, first layers) rather than embossed, so the cover prints flat on its outer face']
doc = {
    'version': VER, 'frame': 'Z-up mm, X=Y=0 shaft axis, Z=0 = roof top = bowl base underside; dosing/drivetrain frames unchanged',
    'parts_printed_PETG': PRINTED, 'parts_TPU_95A': TPU, 'count': {'PETG_parts': len(PRINTED), 'TPU_parts': 4 + 2 + 1 + 1 + 1 + 1, 'target': '~13 printed'},
    'hardware': HARDWARE,
    'shelf': {'hole_saw_d': SHELF_HOLE_D, 'hole_centre_from_axis_xy': list(HOLE_C), 'neck_od': NECK_OD, 'neck_into_hole_mm': NECK_H,
              'shelf_thickness_mm': [18, 40], 'wood_screws_xy': WOOD_XY, 'funnel_min_slope_deg': FUNNEL_SLOPE},
    'flange': {'plate_z': [FL_Z0, FL_Z1], 'plate_xy': [PL_X, PL_Y], 'hooks_deg': HOOKS, 'hook_r': [HOOK_R0, SKIRT_R1 - 0.5], 'hook_z': [HOOK_Z0, HOOK_Z1],
               'skirt_r': [SKIRT_R0, SKIRT_R1], 'labyrinth_groove_r': [LGROOVE_R0, LGROOVE_R1], 'labyrinth_groove_depth': LGROOVE_D,
               'top_gasket_groove': {'r_centre': FL_GSK_R, 'w': GRV_W, 'd': GRV_D, 'gasket': [GSK_W, GSK_H], 'around': list(HOLE_C)},
               'legs_xy': LEG_XY, 'leg_d': LEG_D, 'leg_z': [0.0, FL_Z0], 'opening': {'type': 'pie sector', 'r': OPEN_R, 'half_deg': OPEN_HALF}},
    'enclosure': {'wall_outer_xy': [WX, WY], 'wall': WALL, 'roof_t': ROOF_T, 'roof_outline_xy': [ROOF_X, ROOF_Y], 'roof_slope_deg': SLOPE_DEG,
                  'roof_edge_drop_max_mm': ROOF_DROP, 'drip_lip': [DRIP_W, DRIP_H], 'inner_z': [BOX_Z0, -ROOF_T], 'rim': {'out': RIM_OUT, 'h': RIM_H},
                  'chimney': {'axis_xy': list(CHUTE_AX), 'bore_r': CH_R_IN, 'flat_at_x': CH_FLAT_X, 'wall': CH_WALL, 'lip_r0': LIP_R0, 'lip_z': [LIP_Z0, LIP_Z1],
                              'collar_ring': {'id': CRING_ID, 'od': CRING_OD, 't': CRING_T, 'z': [LIP_Z1, LIP_Z1 + CRING_T]}},
                  'roof_cutout': 'chute section at z -1.5 + 2.0 (dosing.json polygon), rebate +4.0 x 2.0 deep for the gasket',
                  'passante_drilling': {'centre_hole_d': dt.LID_HOLE_D, 'screws': 'Ø3.4 csk Ø6.5 at r 17.5, 90/210/330 deg'},
                  'gland': GLAND, 'leg_bosses': {'d': LEG_BOSS_D, 'h': LEG_BOSS_H, 'xy': LEG_XY},
                  'electronics': {'breadboard_xy': [BB['x'], BB['y']], 'breadboard_z': [CV_Z1, CV_Z1 + BB['t']], 'servo_bottom_z': dt.SERVO_BOT,
                                  'clearance_servo_to_cover_mm': dt.SERVO_BOT - CV_Z1, 'clearance_servo_to_breadboard_y_mm': BB['y'][0] - dt.SERVO_W / 2}},
    'cover': {'plate_z': [CV_Z0, CV_Z1], 'skirt': [SKIRT_T, SKIRT_H, SKIRT_CLR], 'inner_lip': [LIP_T, LIP_H, LIP_CLR], 'screws_xy': screw_xy(),
              'gasket_groove': [GRV_W, GRV_D], 'gasket': [GSK_W, GSK_H], 'rails_y': [BB['y'][0] - RAIL_W, BB['y'][1] + RAIL_W], 'rail_h': RAIL_H,
              'labels': 'orange inlays: 6 screw rings + arrows, OPEN HERE, v5 (mirrored in world: read from below)'},
    'z_stack_unchanged': dt.__dict__ and json.load(open(OUT + 'drivetrain.json'))['z_stack'],
    'screw_rule_unchanged': DOSING['screw'],
    'assembly': ASSEMBLY, 'ip65': IP65, 'dropped_from_hang_v2': DROPPED, 'deviations_from_brief': DEVIATIONS,
    'checks': {'exported_stl_watertight_on_reload': EXPORT_WT, 'watertight': {n: bool(m.is_watertight) for n, (m, _, _) in BODIES.items()} | {n: bool(R[n].is_watertight) for n in R},
               'hard_interference_mm3_max': HARD_MAX, 'hard_interference_mm3': inter, 'soft_designed_overlap_mm3': soft,
               'bayonet': INS_CHECK, 'clearances': CLR, 'print_downfacing_flatter_45_mm2': OVH, 'grams_solid_est': {k: [float(a), float(b)] for k, (a, b) in GR.items()}},
    'print': PRINT_TXT,
    'files': {n: [f'{n}.stl', f'{n}.3mf', f'{n}_print.stl', f'{n}_print.3mf'] for n in BODIES}}
json.dump(doc, open(OUT + 'v5.json', 'w'), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o))
print('v5.json written')
