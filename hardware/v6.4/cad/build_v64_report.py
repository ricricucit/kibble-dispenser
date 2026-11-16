# executed at the end of build_v64_checks.py (same namespace): check_v64.png, interface drawing (SVG + PDF), v64.json, v64_viewer.json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle

X_, Y_, Z_ = np.array([1., 0, 0]), np.array([0, 1., 0]), np.array([0, 0, 1.])
CH_DRAW = [('pod: guscio v64 / fondello v64', U([P['guscio_v64'], P['fondello_v64']]), '#3a3b3e', 'k'),
           ('servo bay + holder (scatola v64)', P['scatola_v64'], '#2E9D4F', 'k'),
           ('unchanged 6.3.0: bowl, tower, chute', U([R['chiocciola_v63'], R['colonna_v63'], R['scivolo_v611']]), '#9a9a9a', '#555'),
           ('TPU lips', U([P['guarnizione_fondello_v64'], P['modulo_guarnizione_v64'], R['labbro_scivolo_v611']]), '#F2C81E', '#7A6A00'),
           ('servo, gland, screws, harness', U([CB['servo'], CB['gland_m12'], CS['pt_k30x12_cap'], CS['m3x16_module_lock'], CB['plug_m8_5p_angled'], STACK]), '#b9c7d6', '#445')]
MOD_DRAW = [('module tub + lid (case 1.0)', U([P['modulo_vasca_v64'], P['modulo_coperchio_v64']]), '#F07A1A', '#7A3A00'),
            ('speaker ring', P['modulo_anello_speaker_v64'], '#1a8fd0', '#024'),
            ('module contents (demo): board, ESP32 stack, regulators, cap, switch, LEDs, speaker, J1', U([m for k, m in MB.items() if m.is_volume] + [MS['pt_k30x10_lid']]), '#9fb7d9', '#24456e')]


def draw(ax, origin, u_, v_, title, xlim, ylim, items, shift=None):
    n_ = np.cross(u_, v_)
    T = np.eye(4); T[0, :3], T[1, :3], T[2, :3] = u_, v_, n_; T[:3, 3] = -T[:3, :3] @ np.asarray(origin, float)
    for nm, m, fc_, ec in items:
        if shift is not None and nm in shift:
            m = m.copy(); m.apply_translation(shift[nm])
        try:
            sct = m.section(plane_origin=origin, plane_normal=n_)
            if sct is None:
                continue
            p2, _ = sct.to_2D(to_2D=T)
        except Exception:
            continue
        for poly in p2.polygons_full:
            ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=fc_, ec=ec, lw=0.4, alpha=0.95))
            for h in poly.interiors:
                ax.add_patch(MPoly(np.array(h.coords), closed=True, fc='white', ec=ec, lw=0.4))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=0.25); ax.set_title(title, fontsize=10)


print('\n--- render check_v64.png ---')
ALLD = CH_DRAW + MOD_DRAW
fig, axs = plt.subplots(2, 4, figsize=(34, 17), facecolor='white')
draw(axs[0, 0], [0, 0, 0], X_, Z_, f'{VER} section Y=0 (XZ): servo bay sealed by the cap lip; module in its opening, lid lip, top lip behind the shell', (-30, 75), (-108, -18), ALLD)
draw(axs[0, 1], [0, 0, -60.0], X_, Y_, 'plan z -60: bay (green), posts in the module sockets, board in slot A, ESP stack, lobes', (-30, 75), (-75, 75), ALLD)
draw(axs[0, 2], [0, 0, Z_E], X_, Y_, f'plan z {Z_E}: control panel on the module face (button {PANEL_AZ["btn"]:.0f} deg, LEDs, 3 flush knock-outs)', (-30, 75), (-75, 75), ALLD)
for nm_ in ('btn', 'led1', 'ko1', 'ko2', 'ko3'):
    Pk, nk, _ = PANEL['frames'][nm_]
    axs[0, 2].annotate(nm_.upper().replace('LED1', 'LEDS'), xy=(Pk[0], Pk[1]), xytext=(Pk[0] + 9 * nk[0], Pk[1] + 9 * nk[1]), fontsize=8, ha='center', arrowprops=dict(arrowstyle='-', lw=0.5))
draw(axs[0, 3], [0, POST['xy'][1], 0], X_, Z_, 'section Y=45.5: holder post in the closed socket, M3x16 lock screw from below, cap boss C', (-5, 60), (-108, -28), ALLD)
Pb, nb, phib = PANEL['frames']['btn']
ub = np.array([nb[0], nb[1], 0.0]); ub /= np.linalg.norm(ub)
ax = axs[1, 0]
draw(ax, Pb, ub, Z_, 'button recess (radial section): paw Ø30/Ø40, snout Ø25 stop short; fingertip Ø16 reaches', (-34, 14), (-18, 20), ALLD)
for lab_, d, colr in (('paw Ø30', 30.0, '#c0392b'), ('paw Ø40', 40.0, '#8e44ad'), ('snout Ø25', 25.0, '#d35400')):
    dep = PAW['btn'][lab_.replace('paw', 'paw pad sphere').replace('snout', 'snout sphere')]['deepest_mm']
    ax.add_patch(Circle((-dep + d / 2, 0.0), d / 2, fc='none', ec=colr, lw=1.2, ls='--'))
    ax.text(-dep + d / 2 + 0.5, d / 2 * 0.7, f'{lab_}: {dep:.1f} mm deep (face {REC["face"]})', fontsize=7, color=colr)
draw(axs[1, 1], [36.0, 0, 0], Y_, Z_, 'section X=36 (YZ): module between the cut edges of cap and shell (return ribs), lid, lip gasket', (-75, 75), (-108, -18), ALLD)
dz_ = np.array([0.0, 0.0, -30.0])
draw(axs[1, 2], [0, J1['xy'][1], 0], X_, Z_, 'section Y=-24, module lowered 30: J1 turret and plug stand in the window under the shell edge', (-5, 80), (-138, -5), ALLD,
     shift={MOD_DRAW[0][0]: dz_, MOD_DRAW[1][0]: dz_, MOD_DRAW[2][0]: dz_})
draw(axs[1, 3], [0, 0, Z_BOT + 0.6], X_, Y_, 'bottom (z -103.4): cap counterbores A-D, drain, outlet; module bottom with 2 lock screws and the grille', (-82, 64), (-74, 74), ALLD)
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3]) for d in ALLD]
axs[0, 0].legend(handles, [d[0] for d in ALLD], loc='lower left', fontsize=7)
plt.tight_layout()
plt.savefig(staged(OUT + 'check_v64.png'), dpi=60)
plt.close(fig)
print('check_v64.png written')

# ---------------- interface drawing (A3 landscape, dimensioned): the FIXED holder interface ----------------
ZI = dict(top=ZMT, shell_edge=ZSH, land=Z_LAND, sock=ZSOCK, n0=ZN0, bot=Z_BOT, post0=POST['z0'], post1=POST['z1'], seat=LOCK['seat_z'])
HOLDER = [('pod (cap + shell)', U([P['guscio_v64'], P['fondello_v64']]), '#d9d9d9', 'k'), ('holder (bay + posts)', P['scatola_v64'], '#bfe3c8', 'k')]
MODI = [('module envelope', U([P['modulo_vasca_v64'], P['modulo_coperchio_v64']]), '#fbd3b0', '#7A3A00')]


def dim(ax, p0, p1, txt, off=(0, 0), fs=7, col='#0b3d91'):
    ax.annotate('', xy=p0, xytext=p1, arrowprops=dict(arrowstyle='<->', lw=0.6, color=col))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], txt, fontsize=fs, color=col, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=0.6))


figI = plt.figure(figsize=(420 / 25.4, 297 / 25.4), facecolor='white')
figI.suptitle(f'Kibble Dispenser Outdoor {VER} - electronics module interface (holder side FIXED; module "{CASE_VER}")   frame: Z up, shaft axis x=y=0, mm', fontsize=11, y=0.985)
ax1 = figI.add_axes([0.03, 0.40, 0.30, 0.54]); ax2 = figI.add_axes([0.35, 0.40, 0.30, 0.54]); ax3 = figI.add_axes([0.67, 0.40, 0.31, 0.54])
draw(ax1, [0, 0, -60.0], X_, Y_, 'A  plan section z -60 (module shown in orange)', (-22, 78), (-70, 70), HOLDER + MODI)
dim(ax1, (XM0, -62), (0, -62), f'{XM0}', (0, 2.5)); dim(ax1, (72, -YM), (72, YM), f'{2 * YM:.0f} module\n{2 * (YM + GAP):.1f} opening', (-1, 0))
dim(ax1, (0, POST['xy'][1]), (POST['xy'][0], POST['xy'][1]), f'{POST["xy"][0]}', (0, 3)); dim(ax1, (POST['xy'][0], 0), (POST['xy'][0], POST['xy'][1]), f'{POST["xy"][1]}', (5, 0))
dim(ax1, (XM0, NY0), (NX1, NY0), f'{NX1 - XM0:.1f}', (0, -3)); dim(ax1, (NX1 + 3, NY0), (NX1 + 3, YM), f'{YM - NY0:.0f}', (4, 0))
ax1.plot([0], [0], '+', c='k', ms=10); ax1.text(1, -4, 'shaft axis', fontsize=6)
for s in (1, -1):
    ax1.add_patch(Circle(post_xy(s), POST['d'] / 2, fc='none', ec='#c0392b', lw=1.0))
ax1.text(POST['xy'][0] + 6, -POST['xy'][1] - 6, f'2 posts Ø{POST["d"]:.0f}\nM3 insert, from below', fontsize=6, color='#c0392b')
ax1.add_patch(Circle(P_SCREWS[2], P3_PAD['r'], fc='none', ec='#555', lw=0.8, ls='--')); ax1.text(P_SCREWS[2][0] + 7, P_SCREWS[2][1] - 1, f'P3 pad (keep-out above z {P3_PAD["z0"]:.0f})', fontsize=6)
ax1.add_patch(Circle(J1['xy'], J1['tur_d'] / 2, fc='none', ec='#0b3d91', lw=0.8)); ax1.text(J1['xy'][0] - 2, J1['xy'][1] - 13, f'J1 {J1["xy"]}', fontsize=6, color='#0b3d91')
draw(ax2, [0, POST['xy'][1], 0], X_, Z_, f'B  section y {POST["xy"][1]} (post, socket, lock screw)', (-5, 78), (-110, -20), HOLDER + MODI)
for nm, z in (('module top / lid top', ZI['top']), ('shell edge', ZI['shell_edge']), ('socket top', ZI['sock']), ('post end = insert face', ZI['post0']), ('pod bottom', ZI['bot'])):
    ax2.axhline(z, c='#0b3d91', lw=0.4, ls=':'); ax2.text(77, z + 0.6, f'{nm}  z {z:.2f}', fontsize=6, color='#0b3d91', ha='right')
dim(ax2, (8, ZI['bot']), (8, ZI['top']), f'{ZI["top"] - ZI["bot"]:.0f}', (-3, 0)); dim(ax2, (XM0, -24), (0, -24), f'{XM0}', (0, 2))
draw(ax3, [0, 0, 0], X_, Z_, 'C  section y 0 (seal faces, keep-outs)', (-5, 78), (-110, -5), HOLDER + MODI)
ax3.add_patch(Rectangle((XM0 + 6, ZMT), 45, 27, fc='none', ec='#c0392b', lw=0.8, ls='--', hatch='//', alpha=0.5))
ax3.text(XM0 + 8, ZMT + 20, f'KEEP FREE: J1 turret + angled\nM8 plug + parked harness loop\n(tail {L_TAIL:.0f} mm, lid top to z -12)', fontsize=6, color='#c0392b')
ax3.text(XM0 + 1, -70, f'back face x {XM0}\ngap {GAP} to the cap upstand', fontsize=6, rotation=90, va='center')
ax3.text(52, ZSH + 2.5, f'lip {LIP["h"]} behind the shell wall', fontsize=6)
dim(ax3, (70, ZSH), (70, Z_BOT), f'opening\n{ZSH - Z_BOT:.2f}', (-5, 0))
axt = figI.add_axes([0.03, 0.02, 0.95, 0.35]); axt.axis('off')
SPEC_LINES = [
    ('1 Opening in the pod', f'vertical prism x >= {XM0 - GAP:.2f}, |y| <= {YM + GAP:.2f}; in the cap from z {Z_BOT:.0f} to {Z_S - b611.SEAM:.1f}, in the shell from z {Z_S:.0f} to {ZSH:.2f}. Cut edges with return ribs '
                             f'{RIB["t"]:.0f} x {RIB["depth"]:.0f}. The module outer face = the pod skin (loft of circles, see pod_circle in build_v61.py) inside this prism: flush, gap {GAP}.'),
    ('2 Insertion', f'straight up from below, travel {ZMT - Z_BOT:.0f} mm; nothing of the chassis lies inside the prism below z {P3_PAD["z0"]:.0f} except the two posts (in the module corner notches '
                    f'x {XM0}..{NX1}, |y| {NY0:.0f}..{YM:.0f}, open above z {ZN0}).'),
    ('3 Locating / locking', f'2 posts Ø{POST["d"]:.0f} at ({POST["xy"][0]}, +-{POST["xy"][1]}), z {POST["z0"]:.0f}..{POST["z1"]:.0f} (up to the roof plane), M3 heat-set insert in the lower end. Module: closed sockets Ø{POST["d"] + 2 * SOCK_GAP:.1f} from z {ZN0} to {ZSOCK}; the post ends on the socket floors are the VERTICAL STOP, '
                             f'2 x M3x16 ISO 4762 from below, head seat z {LOCK["seat_z"]:.1f} in a Ø{LOCK["cb_d"]} counterbore (hex 2.5). Top: lip {LIP["h"]:.0f} x {LIP["t"]:.0f} tucked {LIP["gap"]} mm inside the shell wall above z {ZMT:.0f}.'),
    ('4 Seal faces', f'the module is sealed on its own (IP66 target): lid lip gasket on the tub land z {Z_LAND:.1f}; no seal between module and chassis. The servo bay is sealed by the cap lip on the bay rim (z {Z_W:.0f}), '
                     f'tower face O-ring 24x2, shaft O-rings 2 x 9x2, O-ring 3x1 under P2, M12 gland (servo lead), ePTFE vent patch. The pod is a closed second barrier with the drain, not sealed.'),
    ('5 Electrical interface J1', f'one M8 5-pin A-coded panel socket (female) in a turret on the lid at ({J1["xy"][0]}, {J1["xy"][1]}), mating face z {ZMT + J1["tur_h"]:.0f}; chassis harness = angled M8 5-pin plug, Y into the 12 V pigtail '
                                  f'(pod-top M8, unchanged) and the servo lead (through the bay gland). Pins: 1 +12 V in, 2 servo PWM (3.3 V logic), 3 GND, 4 servo +6 V out, 5 spare. Harness slack >= 35 mm.'),
    ('6 Keep-outs for any future module', f'stay inside the prism and below z {ZMT:.0f} (lip to {ZMT + LIP["h"]:.0f} only behind the shell wall; J1 turret Ø{J1["tur_d"]:.0f} to z {ZMT + J1["tur_h"]:.0f}); keep x >= {XM0}; keep the notches free for the posts and the '
                                          f'webs (above z {POST["web_z0"]}: y >= {NY0 + RIM_T:.0f}); P3 pad Ø{2 * P3_PAD["r"]:.0f} at {tuple(P_SCREWS[2])} reaches down to z {P3_PAD["z0"]:.0f}; zone above the lid (z {ZMT:.0f}..-10, x > {XM0 + 6:.0f}) is for the plug and the harness.'),
    ('7 Removal', f'unit hanging or taken down by the bayonet: 2 screws out (hex 2.5), lower the module ~30 mm, unscrew the M8 ring through the {ZSH - (ZMT - 30):.0f} mm window, slide the module out. No chassis part is opened. '
                  f'Mass budget for the two inserts: module <= 1 kg (SF {LOAD["module_lock_M3x16"]["SF_insert"]} at 250 N + weight).')]
yy = 0.97
for hd, tx in SPEC_LINES:
    axt.text(0.0, yy, hd, fontsize=7.5, fontweight='bold', va='top');
    import textwrap as _tw
    wrapped = _tw.fill(tx, 215)
    axt.text(0.115, yy, wrapped, fontsize=7.0, va='top')
    yy -= 0.045 + 0.047 * (wrapped.count('\n') + 1)
figI.savefig(staged(IFD + 'interfaccia_modulo_v64.pdf'), metadata={'CreationDate': None})   # no timestamps: reproducible
figI.savefig(staged(IFD + 'interfaccia_modulo_v64.svg'), metadata={'Date': None})
figI.savefig(staged(IFD + 'interfaccia_modulo_v64.png'), dpi=110)                         # for the website
figI.savefig(SCRATCH + 'interfaccia_preview.png', dpi=80)
plt.close(figI)
print('interface drawing written')

HARNESS_SPEC = {
    'tail': {'part': 'M8 5-pin A-coded MALE cordset, angled, PUR Ø4.5 (ready-made 0.5 m, cut)', 'length_mm': L_TAIL,
             'measured': 'from the plug body (cable exit) to the centre of the Y splice', 'parked': f'service loop on the module lid: {HARNESS["tail_parked_path_mm"]} mm of path, '
             'over the module south rim, north along the back fence, U-turn R 11.5 (>= 2.5 x D, static), back south and up into the plug',
             'lowered': f'reaches the plug with the module lowered up to {D_MAX} mm (5 mm spare); 80 mm needs {REACH[80]} mm',
             'anchor': f'cable tie 2.5 x 100 round the lug bar on the bay (south of cap boss D) at {tuple(HARN["anchor"])}',
             'guide': f'snapped into the C-hook on the south post top at {tuple(EYELET["xy"])} (slit {EYELET["slit"]} mm): from there it always drops inside the opening, never into the pod pocket south of it',
             'min_bend_radius_mm': 11.5},
    'splice_y': {'where': list(HARN['splice']), 'size': f'Ø{HARN["splice_d"]:.0f} x {HARN["splice_len"]:.0f} adhesive-lined heat shrink over solder joints',
                 'pins': 'tail 1 -> 12 V +, tail 3 -> 12 V GND and servo GND, tail 2 -> servo signal, tail 4 -> servo +6 V, tail 5 not connected'},
    'branch_12v': {'part': '2-core PUR (or the pigtail of an M8 4-pin A-coded male field connector) to the pod-top M8 IP67 pair', 'length_mm': 90,
                   'route': 'splice -> up along the shell inside -> M8 unit half at (0, -69.2, 6)'},
    'branch_servo': {'part': 'round 3-core PUR 3 x 0.25 mm2, Ø4.0', 'length_mm': 100, 'route': 'splice -> M12 gland -> 12 mm inside the bay -> JR 3-pin female',
                     'spare': '40 mm so the JR pair can be pulled out under the bay when the cap is off'},
    'checks': HARNESS}
# ---------------- drilling template 6.4 (A4 portrait 1:1, VIEW FROM BELOW, drawing turned so the CONTROL PANEL arrow points up) ----------------
TPL = OUT + 'template_v64/'
os.makedirs(TPL, exist_ok=True)
A4W, A4H = 210.0, 297.0
CXp, CYp = 105.0, 152.0
AZ_PANEL = PANEL_AZ['btn']
ROT = math.radians(90.0 - AZ_PANEL)                           # world -> sheet: the panel direction ends at the top of the sheet


def tp(x, y):
    xr, yr = x * math.cos(ROT) - y * math.sin(ROT), x * math.sin(ROT) + y * math.cos(ROT)
    return (CXp - xr, CYp - yr)


TPL_ITEMS = []
S_MAIN = dict(stroke='#000', w=0.35, dash=None, fill='none')
T_circle = lambda x, y, r_, **st: TPL_ITEMS.append(('circle', *tp(x, y), r_, dict(S_MAIN, **st)))
T_line = lambda x0, y0, x1, y1, **st: TPL_ITEMS.append(('line', *tp(x0, y0), *tp(x1, y1), dict(S_MAIN, **st)))


def T_text(x, y, s_, size=3.2, anchor='middle', weight='normal', sheet=False, colour='#000'):
    X, Y = (x, y) if sheet else tp(x, y)
    TPL_ITEMS.append(('text', X, Y, s_, size, anchor, weight, colour))


def T_cross(x, y, L=5.0, **st):
    T_line(x - L, y, x + L, y, **st); T_line(x, y - L, x, y + L, **st)


def T_arrow(az, r0, r1, colour, w=0.6, head=3.5):
    a = math.radians(az)
    T_line(r0 * math.cos(a), r0 * math.sin(a), r1 * math.cos(a), r1 * math.sin(a), w=w, stroke=colour)
    tip = (r1 + head) * math.cos(a), (r1 + head) * math.sin(a)
    n_ = (-math.sin(a), math.cos(a))
    p1 = (r1 * math.cos(a) + 2.0 * n_[0], r1 * math.sin(a) + 2.0 * n_[1]); p2 = (r1 * math.cos(a) - 2.0 * n_[0], r1 * math.sin(a) - 2.0 * n_[1])
    TPL_ITEMS.append(('poly', [tp(*tip), tp(*p1), tp(*p2)], dict(S_MAIN, fill=colour, stroke=colour)))


FL_R, WOOD_R, WOOD_A, HOLE_C, RING_RO = b62.FL_R62, b62.WOOD_R62, b62.WOOD_ANG62, v6.HOLE_C, b62.RING['ro']
TPL_ITEMS.append(('rect', 6.0, 6.0, A4W - 12.0, A4H - 12.0, dict(S_MAIN, w=0.2, stroke='#888')))
T_text(105, 14.0, f'Kibble Dispenser Outdoor {VER} - drilling template 1:1', 5.0, weight='bold', sheet=True)
T_text(105, 19.5, 'VIEW FROM BELOW: tape it under the shelf with the PRINTED SIDE FACING YOU', 3.0, sheet=True)
T_text(105, 24.0, 'TURN THE SHEET so the blue CONTROL PANEL arrow points to where you stand (the room)', 3.0, weight='bold', sheet=True, colour='#1f4e9a')
T_line(0.0, 0.0, 0.0, 0.0)
T_circle(0.0, 0.0, 100.0, dash='3,2', stroke='#E06A00', w=0.4)
T_circle(0.0, 0.0, FL_R, w=0.5)
T_circle(0.0, 0.0, RING_RO, dash='1,1', stroke='#E06A00', w=0.3)
T_text(*polar(FL_R + 6.0, AZ_PANEL + 200.0), f'flange outline Ø{2 * FL_R:.0f}', 2.6)
T_cross(0.0, 0.0, 4.0, w=0.25)
T_text(*polar(8.0, AZ_PANEL - 120.0), 'flange centre', 2.4)
hx, hy = HOLE_C
T_circle(hx, hy, 38.0, dash='4,1.5', w=0.5)
T_cross(hx, hy, 8.0, w=0.4); T_circle(hx, hy, 3.0, w=0.3)
T_text(*np.add(tp(hx, hy), (0, -10.0)), 'HOLE SAW Ø76', 3.4, weight='bold', sheet=True)
T_text(*np.add(tp(hx, hy), (0, -6.0)), 'centre: drill the Ø6 pilot here', 2.6, sheet=True)
T_line(0, 0, hx, hy, w=0.2, dash='1,1')
for k, aw in enumerate(WOOD_A):
    x, y = polar(WOOD_R, aw)
    T_cross(x, y, 4.0, w=0.35); T_circle(x, y, 1.5, w=0.3)
    T_text(*polar(WOOD_R - 10.0, aw), f'S{k + 1}', 3.0, weight='bold')
T_text(105, 262.0, 'S1-S4: wood screws 5x35 pan head (5x30 for an 18 mm shelf), pre-drill Ø3 x 25', 2.6, sheet=True)
T_text(105, 266.0, 'dashed orange circle r 100: keep clear, the gate ring is turned by hand', 2.5, sheet=True, colour='#E06A00')
# arrows: CONTROL PANEL (up on the sheet), FRONT = release button + gate window, cable exit (back)
T_arrow(AZ_PANEL, FL_R + 1.0, 104.0, '#1f4e9a', w=0.9, head=5.0)
T_text(*np.add(tp(*polar(122.0, AZ_PANEL)), (0, -1.0)), f'CONTROL PANEL (button + LEDs, 182 mm below the shelf) - face it towards you', 3.0, weight='bold', sheet=True, colour='#1f4e9a')
T_arrow(b63.LATCH_A, FL_R + 1.0, 97.0, '#E06A00', w=0.7)
fx, fy = tp(*polar(97.0, b63.LATCH_A))
T_text(min(fx, A4W - 9.0), fy + 8.0, 'FRONT: release button + gate window', 2.6, anchor='end', weight='bold', sheet=True, colour='#E06A00')
T_text(min(fx, A4W - 9.0), fy + 11.5, f'({b63.LATCH_A - AZ_PANEL:.0f} deg from the control panel)', 2.4, anchor='end', sheet=True, colour='#E06A00')
T_arrow(270.0, FL_R - 12.0, FL_R + 4.0, '#555', w=0.5)
cx_, cy_ = tp(*polar(FL_R - 16.0, 270.0))
T_text(cx_ + 2.0, cy_ - 2.0, 'CABLE EXIT (back): clip the cable', 2.5, anchor='start', weight='bold', sheet=True, colour='#555')
T_text(cx_ + 2.0, cy_ + 1.5, 'along the shelf, leave a drip loop', 2.4, anchor='start', sheet=True, colour='#555')
T_circle(CH_X, 0.0, 24.5, dash='0.8,0.8', stroke='#2E9D4F', w=0.3); T_text(*np.add(tp(CH_X, 0.0), (0, 1.0)), 'outlet (bowl, 182 mm below)', 2.4, sheet=True, colour='#2E9D4F')
T_text(105, 271.0, 'keep 150 mm free in front of the control panel for a finger; the module comes out downward (90 mm clear below the unit)', 2.5, sheet=True, colour='#1f4e9a')
sx0, sy0 = 18.0, 278.0
TPL_ITEMS.append(('rect', sx0, sy0, 50.0, 3.0, dict(S_MAIN, w=0.3)))
for k in range(6):
    TPL_ITEMS.append(('rect', sx0 + 10 * k, sy0, 10.0 if k < 5 else 0.0, 3.0, dict(S_MAIN, w=0.3, fill='#000' if k % 2 == 0 and k < 5 else 'none')))
    T_text(sx0 + 10 * k, sy0 + 6.5, f'{10 * k}', 2.4, sheet=True)
T_text(sx0 + 25, sy0 - 1.5, 'scale check: this bar must measure exactly 50 mm', 2.6, sheet=True)
T_text(160.0, 282.5, 'print at 100 % / actual size (no fit to page)', 2.6, sheet=True)
T_text(160.0, 287.0, 'A4 portrait, 1:1, all dimensions in mm', 2.4, sheet=True)


def _svg_style(st):
    s_ = f'stroke="{st["stroke"]}" stroke-width="{st["w"]}" fill="{st["fill"]}"'
    return s_ + (f' stroke-dasharray="{st["dash"]}"' if st.get('dash') else '')


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4W}mm" height="{A4H}mm" viewBox="0 0 {A4W} {A4H}">', f'<rect x="0" y="0" width="{A4W}" height="{A4H}" fill="#fff"/>']
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
open(staged(TPL + 'dima_foratura_v64.svg'), 'w').write('\n'.join(svg))
from matplotlib.patches import Circle as MCircle, Rectangle as MRect, Polygon as MPolyT
figT = plt.figure(figsize=(A4W / 25.4, A4H / 25.4))
axT = figT.add_axes([0, 0, 1, 1]); axT.set_xlim(0, A4W); axT.set_ylim(A4H, 0); axT.axis('off')
mm2pt = 72.0 / 25.4
_ls = lambda st: (0, tuple(float(v) * mm2pt / max(st['w'] * mm2pt, 1e-3) for v in st['dash'].split(','))) if st.get('dash') else 'solid'
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
        axT.text(it[1], it[2], it[3], fontsize=it[4] * mm2pt, ha={'middle': 'center', 'start': 'left', 'end': 'right'}[it[5]], va='baseline',
                 fontweight=it[6], color=it[7], family='DejaVu Sans')
figT.savefig(staged(TPL + 'dima_foratura_v64.pdf'), metadata={'CreationDate': None})
figT.savefig(SCRATCH + 'dima_preview_v64.png', dpi=110)
plt.close(figT)
TEMPLATE = {'svg': 'template_v64/dima_foratura_v64.svg', 'pdf': 'template_v64/dima_foratura_v64.pdf', 'a4_pt': [595.28, 841.89],
            'orientation': f'view from below, printed side facing the person below, drawing turned so the CONTROL PANEL arrow ({AZ_PANEL:.0f} deg) points to the top of the sheet; '
                           f'FRONT (release button, 76.5 deg) is drawn {76.5 - AZ_PANEL:.0f} deg away from it',
            'text_lines': ['VIEW FROM BELOW: tape it under the shelf with the PRINTED SIDE FACING YOU',
                           'TURN THE SHEET so the blue CONTROL PANEL arrow points to where you stand (the room)'],
            'contents': ['flange outline Ø180 + ring', 'hole-saw Ø76 centre with pilot mark', '4 wood-screw positions S1..S4', 'keep-clear circle r 100 (hand on the gate ring)',
                         'CONTROL PANEL arrow (blue) and FRONT / release-button arrow (orange)', 'cable exit arrow (back)', 'outlet position', '50 mm scale bar'],
            'flange_geometry': 'unchanged from 6.3 (same holes and outline as template_v63)'}
print('template written')

# ---------------- v64.json ----------------
INTERFACE = {
    'status': 'FIXED on the holder side from 6.4: a new module version must fit it; the chassis is not touched when the electronics change',
    'frame': 'Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside',
    'opening': {'prism_plan': f'x >= {XM0 - GAP:.2f}, |y| <= {YM + GAP:.2f}', 'cap_z': [Z_BOT, round(Z_S - b611.SEAM, 2)], 'shell_z': [Z_S, round(ZSH, 2)], 'gap_mm': GAP, 'top_seam_mm': TOP_SEAM,
                'outer_face': 'the pod skin inside the prism (flush); the band of the control panel (z -98..-74.6) is a module feature, not part of the interface',
                'return_ribs': RIB, 'opening_width_mm': round(2 * (YM + GAP), 1), 'opening_height_mm': round(ZSH - Z_BOT, 2)},
    'module_envelope': {'back_face_x': XM0, 'half_width_y': YM, 'top_z': ZMT, 'bottom_z': Z_BOT, 'top_lip': dict(LIP, where='behind the shell wall, z %.0f..%.0f' % (ZMT, ZMT + LIP['h'])),
                        'corner_notches': {'x': [XM0, NX1], 'abs_y': [NY0, YM], 'open_above_z': ZN0, 'rim_thickening_allowed_to_abs_y': NY0 + RIM_T}},
    'locating_locking': {'posts': {'xy': [list(post_xy(1)), list(post_xy(-1))], 'd': POST['d'], 'z': [POST['z0'], POST['z1']], 'web_above_z': POST['web_z0'], 'insert': 'M3 heat-set (Ø4.0 x 6.5 hole) in the lower end'},
                         'module_sockets': {'d': POST['d'] + 2 * SOCK_GAP, 'z': [ZN0, ZSOCK]}, 'vertical_stop': f'post ends (z {POST["z0"]}) on the socket floors; top seam {TOP_SEAM} mm',
                         'screws': {'type': 'M3x16 ISO 4762 A2', 'qty': 2, 'from': 'below', 'head_seat_z': LOCK['seat_z'], 'counterbore_d': LOCK['cb_d'], 'tool': 'hex 2.5', 'torque': '0.5 N m, by hand'},
                         'insertion': f'straight up, {ZMT - Z_BOT:.0f} mm travel', 'removal_sweep_mm3': SWEEP_M},
    'seal_faces': {'module': 'self-contained: lid lip gasket on the tub land; panel parts, J1 and lid screws sealed in the module', 'module_to_chassis': 'none (0.35 mm seams, top lip, return ribs)',
                   'servo_bay': 'cap lip on the bay rim, face O-ring 24x2, shaft O-rings, O-ring 3x1 under P2, M12 gland, ePTFE vent patch'},
    'electrical_J1': {'connector': 'M8 5-pin A-coded panel socket (female) on the module lid, in a turret', 'xy': list(J1['xy']), 'mating_face_z': ZMT + J1['tur_h'], 'lid_hole_d': J1['hole'],
                      'pins': {'1': '+12 V in (from the pod-top M8)', '2': 'servo PWM (3.3 V logic, 50 Hz)', '3': 'GND (12 V return and servo return)', '4': 'servo +6 V out (from the module regulator)', '5': 'spare'},
                      'chassis_harness': 'angled M8 5-pin plug (cable exit towards +y) -> tail with service loop -> tie on the bay lug -> Y splice: (a) 12 V branch to the M8 IP67 connector in the pod top '
                                         '(unchanged), (b) round servo branch through the M12 gland into the bay, JR female inside',
                      'harness': HARNESS_SPEC,
                      'current': 'M8 5-pin contacts are 3 A class: enough for a standard servo (stall ~2.5 A at 6 V); use the 4-pin 4 A version + PWM on a separate M8 if a stronger servo is ever fitted',
                      'access': PLUG_ACCESS},
    'servo_lead_pass_through': {'where': f'M12x1.5 gland (IP68, cable range 3-6.5 mm) in the bay south wall at x {GLAND["x"]}, z {GLAND["z"]} (the 6.3 gland position)',
                                'solution': 'the servo lead does NOT pass the gland. A ROUND 3-core cable (the harness servo branch, PUR 3 x 0.25 mm2, Ø4.0) goes through the gland, which seals '
                                            'on it as designed; inside the bay it is terminated with a JR/Futaba 3-pin female (crimped after passing the gland) and the servo plugs into it '
                                            'in the dry south room of the bay (mated pair parked vertically at x -5..2.6, y -31..-27.4). The servo and its flat lead stay untouched and '
                                            'replaceable; no new printed part',
                                'crimp_connector': 'JR/Futaba-style 3-pin servo housing, female, 2.54 mm pitch + 3 female crimp terminals for 22-26 AWG (servo-lead type); '
                                                   'pin order: signal (orange/white) - +6 V (red) - GND (brown/black); crimp with an open-barrel crimper (e.g. Engineer PA-09)',
                                'order': 'pass the stripped round cable through the dome nut, seal insert and gland body from outside, crimp and insert the 3 terminals, tighten the dome nut (2.5 N m), '
                                         'plug the servo; then fit the cap'},
    'keep_out': {'above_the_lid': f'z {ZMT}..-10, x > {XM0 + 6}: J1 turret, angled plug and harness loop', 'P3_pad': {'xy': list(P_SCREWS[2]), 'r': P3_PAD['r'], 'down_to_z': P3_PAD['z0']},
                 'posts_and_webs': 'the corner notches', 'behind_the_back_face': f'x < {XM0}: cap upstand and bay wall'},
    'mass_budget': 'module <= 1 kg', 'drawing': ['interface_v64/interfaccia_modulo_v64.pdf', 'interface_v64/interfaccia_modulo_v64.svg']}
MODULE_SPEC = {
    'name': 'modulo elettronica', 'version': CASE_VER, 'printed_parts': {k: {'grams_print_est': g_mod[k], 'material': 'TPU 95A' if RHO[k] == TPU else 'PETG'} for k in MODULE_NEW},
    'concept': 'one sealed case; its outer wall is the missing piece of the pod skin and carries the control panel; lid on top with a TPU lip gasket and 5 PT K30x10 screws (O-ring 3x1 under each head); '
               'the inside is generic: two board slots in the guide walls, free lobes, a floor collar for the speaker ring',
    'ip_target': 'IP66 on its own (flood fill: one closed volume, separate from the pod and outside)',
    'walls_mm': {'skin': WALL_M, 'panel_band': BAND_WALL, 'back': WALL_B, 'sides': WALL_S, 'floor': FLOOR_M, 'lid': LID_T},
    'internal_envelope': ENVELOPE,
    'board_slots': {'boards': '50 x 70 mm perfboard standing, 70 across (y), 50 tall (z), slides in from the top; slots 1.9 wide, 1.3 deep in the guide walls, board bottom edge at z %.1f' % SLOTS['z0'],
                    'A': f'board back face at x {SLOTS["A"]}: {round(SLOTS["A"] - X_BACK, 1)} mm behind for the pins',
                    'B': f'board back face at x {SLOTS["B"]}', 'see': 'internal_envelope.slots'},
    'demo_layout (shown in the viewer, not part of the case)': {
        'board A': '5x7 perfboard in slot A', 'ESP32-WROVER on socket strips': 'stack 61 x 28 x 25 at z -74.5..-46.5 (estimate from photos)', 'regulator 6 V 25x20': 'lying under the ESP zone, south',
        'regulator 5 V': 'on board A, north bottom', 'capacitor Ø10 x 20': 'standing in the north lobe', 'speaker': 'Ø23 in the floor ring'},
    'control_panel': {
        'where': f'on the module outer face (band z {ZB0}..{ZB1}, straight-ruled as 6.3); azimuths from the shaft axis: ' + ', '.join(f'{k} {v:.0f} deg' for k, v in PANEL_AZ.items()),
        'vs_6_3': 'the panel moves with the electronics from the room side (button at 77 deg, under the release button) to the side away from the bowl: the button now faces %.0f deg, i.e. %.0f deg '
                  'clockwise from the release button seen from above. The room side is blocked by the servo body (the servo cannot be turned: P2 would fall under it)' % (PANEL_AZ['btn'], 76.5 - PANEL_AZ['btn']),
        'button': {'recess': f'Ø{REC["d"]} x {REC["face"]} to the switch face (as 6.3)', 'probes': PAW, 'ok': PANEL_OK, 'min_margin_paw_snout_mm': PAW_MARGIN},
        'leds': {'flush_max_mm': LED_FLUSH, 'type': '2 x Ø5 light pipe + O-ring 5x1, square to the face'},
        'knock_outs': {'style': 'flush, 0.3 mm engraved Ø12 ring + dot, skin 2.0 (as 6.3.0)', 'skin_measured': KO_SKIN, 'future_switch': FUTURE_KO,
                       'KO1': 'reserved as a possible CAMERA window (Ø12 clear window bonded from inside; %.0f mm free behind)' % FUTURE_KO['ko1']['free_depth_behind_the_seat_mm_empty_case'],
                       'KO2': 'free for a second switch', 'KO3': 'shallow: %.1f mm behind the seat (next to the guide wall): LED / sensor / window only' % FUTURE_KO['ko3']['free_depth_behind_the_seat_mm_empty_case']},
        'speaker': {'seat': f'floor collar Ø{SPK64["collar_id"]} at ({SPK64["x"]}, {SPK64["y"]}); printed ring insert (modulo_anello_speaker_v64) sets the diameter: bore = speaker Ø + 0.4, the part shown is for Ø{SPK64["spk_d"]:.0f}',
                    'range': 'Ø20..24 on the floor seat (the flat floor is only 21 mm deep before the bottom radius). Ø26-28: print the tall ring variant (seat 5 mm higher); it then needs a 30 x 4 mm notch '
                             'in the bottom edge of the board in slot A',
                    'grille': '7 x Ø1.5 through the 2.5 mm floor, facing straight down, IP67 acoustic membrane Ø15 inside (as 6.3)'},
        'usb_c': f'blind position on the lid top at {USB["xy"]} (engraved Ø{USB["ring_d"]:.0f} ring + dot): reachable with the module lowered or out; drill for a sealed panel USB-C when needed',
    },
    'hardware': HW['module'], 'print': {'modulo_vasca_v64': 'standing as assembled (flat bottom on the bed), IP66 settings (5 walls, 100 % infill, 245-250 C, fan <= 40 %), NO supports: the bottom edge now starts with a 45 deg chamfer, '
                                                            'rim and bosses are true 45 deg faces. Horizontal holes (light pipes Ø5.1, button Ø17) sag at the top: ream the light-pipe holes. Check the 2 mm back wall for bow',
                                        'modulo_coperchio_v64': 'underside on the bed, turret up, NO supports: the turret ceiling runs in at 45 deg to a Ø13 flat closed by a 0.2 mm skin '
                                                                'over the J1 hole (bridge 13 mm): drill Ø8.2 afterwards (or the thread size of the bought socket)',
                                        'modulo_guarnizione_v64': 'TPU, base on the bed, lip up; Arachne walls, 15 mm/s (the 0.8 mm lip prints as one line)',
                                        'modulo_anello_speaker_v64': 'flat'}}
REVIEW = {
    'source': 'docs/reviews/2026-11-15-v6.4-print-review/REVIEW.md (0 blocker, 3 major, 19 minor)',
    'M1 scatola posts in mid-air': 'FIXED in CAD: posts and webs run up to the roof plane (the bed); nothing of the module is in that column',
    'M2 guscio tabs': 'PARTLY: 45 deg corbels added from the wall in to r 62.6 (the bowl is at r 62.0 there), rib ends got a 45 deg lead-in; the inner 12 mm of each tab still needs tree supports '
                      '(build plate only, 45 deg): a corbel there would be inside the bowl, and turning the shell over would make the 105 mm opening edge a bridge',
    'M3 bottom edge of tub and cap': 'FIXED in CAD: 45 deg chamfer under the R15 bottom radius on both parts (bottom flat grows by %.1f mm, chamfer %.1f mm high); no supports' % (BOTTOM_FILL[2] - 53.8, BOTTOM_FILL[1] - Z_BOT),
    'm1 vertical stop': 'FIXED: socket floor at z -89.0 = post end; top seam opened to 0.5 mm',
    'm2 board to lid': 'FIXED: slot floor z -91.5 (1.3 mm above a 50.0 board)', 'm3 lid screws': 'FIXED: PT K30x10 (6.8 mm in the boss), now 5 screws',
    'm4 rim corbel stairs': 'FIXED: rim, notch-wall thickening and bay rim flange are 0.1 mm-step 45 deg faces (finer than a layer)',
    'm5 slot B jaw': 'FIXED: 1.75 mm', 'm6 lid groove outer wall': 'FIXED: 1.2 mm', 'm7 turret ceiling': 'FIXED: 45 deg run-in + 0.2 mm sacrificial skin, no supports',
    'm8 J1 nut access': 'FIXED: bore Ø16.5 (turret Ø21); bought part assumed: M8 5-pin A-coded female panel receptacle, front mount, nut 10-13 mm AF, TO VERIFY on the part',
    'm9 bottom seam edges': 'FIXED: 0.4 x 45 deg on the module bottom back edge, its two vertical back corners and the cap floor edge',
    'm10 feather edges': 'FIXED: cut edges of cap and shell blunted (0.9 mm), module lip shortened 3 mm each end',
    'm11 drain holes': 'FIXED: 2 x Ø1.5 instead of 4 x Ø0.8; the three 0.8 mm labyrinth slits stay as the insect barrier',
    'm12 post sockets': 'FIXED: Ø10.0', 'm13 colletto_v6 pads': 'NOT TOUCHED: 6.3.0 part already being printed; the two pads print as they are',
    'm14 lock screw heads': 'FIXED: counterbore 1.5 mm deeper', 'm15 TPU lid gasket': 'print note (Arachne, 15 mm/s)', 'm16 horizontal holes': 'print note', 'm17 thin walls': 'print note',
    'm18 P3 O-ring': 'FIXED: no O-ring and no countersink at P3; 3x1 list = P2 1 + cap 4',
    'm19 wording': 'FIXED: cap-shell seam 0.6 stated; grams at solid mass for the IP66 parts; print files cleaned and re-checked after vertex merge; shell orientation wording',
    'lid gasket run without screws': 'PARTLY: 5th screw in the north lobe, ribs on the lid top along the back and notch edges, lip tips now point outward. No screw fits on the back edge '
                                     '(the board plane is 5 mm from it), so ~105 mm of gasket still relies on the ribbed lid: water test before trusting IP66',
    'slicer_check_6_4_0 (a) tub lid-screw bosses': {'status': 'FIXED: each boss grows out of the nearest wall on a 45 deg corbel (no free cone tips)', 'bosses': CORBEL_INFO},
    'slicer_check_6_4_0 (b) zero-volume fins': 'FIXED: closed zero-volume slivers are dropped from every exported mesh (assembled and _print) before the watertight check',
    'slicer_check_6_4_0 (c) cap groove ceiling': 'PARTLY: the 2.1 mm ledge is the seat of the unchanged TPU chute lip (anchor r 24.95..26.5). The 0.6 mm bore-side strip the lip '
                                                 'does not touch is now a 45 deg chamfer; the 1.5 mm flat ring that retains the lip stays (prints as a short overhang, no support): '
                                                 'a full chamfer would let the lip ride out of its groove when the cap is pulled off',
    'assembly_issues_6_4_0': {'module plug reach': 'FIXED: tail %d mm with a service loop parked on the lid; the module can be lowered %d mm (80 needed) and unplugged below the pod' % (L_TAIL, D_MAX),
                              'servo lead through the gland': 'FIXED: round 3-core branch through the M12 gland, JR female crimped inside the bay; the flat servo lead never passes the gland',
                              'drilling template 6.4': 'template_v64/ (panel arrow up, FRONT arrow 60 deg away, turn-the-sheet instruction)'},
    'assembly advice': 'hold the module when it leaves the posts (last 18 mm of travel are guided); fold the harness loop above the lid before pushing up (1.0 mm lid to P3 pad)'}
v64doc = {
    'version': VER, 'release': '6.4.0', 'module_version': CASE_VER, 'base': '6.3.0 (v63.json): everything not listed here is unchanged',
    'split': 'product = (1) mechanics + electronics-case holder [6.x], (2) detachable electronics module [case 1.x]: the mechanics can be printed now',
    'frame': 'as 6.3: Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED bayonet pose',
    'decisions': {
        'servo': 'stays in the chassis (coaxial cradle, structural). OWN SEALED BAY: scatola_v64 is the 6.3 box cut down to the cradle width; sealed by the cap lip on its rim, the tower face O-ring, the shaft O-rings, '
                 'an O-ring under P2, the M12 gland and an ePTFE vent patch. Flood fill: one closed volume (%.0f cm3 free) separate from the module, the pod and outside' % (DRY['servo_bay_free_volume_cm3'] or 0),
        'module_removal': 'achieved: from BELOW, unit hanging or taken down, WITHOUT opening the chassis: 2 screws (hex 2.5) + 1 M8 plug. Not tool-free: a tool-free latch would also open for a fox',
        'panel_side': MODULE_SPEC['control_panel']['vs_6_3'],
        'envelope': ENVELOPE['target_80x60x45'],
        'second_board': 'slot B is real but shares the depth: with the ESP32 stack at 25 mm the board in slot A fills the depth in front of it, so a second FULL board only fits when the stack in A is <= %.1f mm '
                        '(regulator board in A, ESP board on low sockets in B: %s mm in front of B). The 6 V / 5 V regulators and the capacitor fit beside / under the ESP stack and in the lobes (demo layout)'
                        % (ENVELOPE['slots']['between_A_and_B_mm'], ENVELOPE['slots']['in_front_of_B_mm (z -86..-46, 68 wide / 40 wide)']),
        'pod_seam_oring': 'dropped: the opening crosses the cap / shell seam, and nothing in the pod needs the pod to be sealed any more (bay and module are sealed on their own); the pod stays closed (gaps <= 0.4 mm) with its drain'},
    'review_2026_11_15': REVIEW, 'interface': INTERFACE, 'module': MODULE_SPEC,
    'parts': {
        'safe_to_print_now (byte-identical to 6.3.0)': SAFE, 'safe_list_matches_the_6_3_0_release': SAFE_OK,
        'changed_chassis_parts': {'scatola_v64': 'servo bay + holder posts (was the electronics box)', 'fondello_v64': 'cap with the module opening; no panel, no pocket, 4 screws',
                                  'guscio_v64': 'shell with the module opening (z -72..-36.65) and return ribs; otherwise the 6.1.1 shell', 'guarnizione_fondello_v64': 'TPU lip for the smaller bay outline'},
        'changed_vs_6_3_meshes': CHANGED, 'new_module_parts': MODULE_NEW,
        'also_safe': 'the chassis parts above are final too unless the interface changes: print them now, the module later'},
    'build_order': ['1-4 as 6.3 (latch, tower module, chute, shell)', '5 servo bay onto the tower: 3 x M3x40 from below (P3 now outside the bay)',
                    '5b harness: servo branch through the gland, JR female crimped on and plugged to the servo; 12 V branch to the pod-top M8; tail tied to the bay lug (cable tie 2.5 x 100)',
                    '6 cap: push on, 4 x PT K30x12 + O-ring 3x1 from below (T10); the M8 plug hangs out of the opening on its 180 mm tail',
                    '7 rim seal, comb lips, plates, disc from the top',
                    '8 module: plug J1 with the module below the pod, lay the tail loop on the lid (between the back fence and the turret, U-turn to the north), slide up, 2 x M3x16 from below'],
    'checks': {'watertight_built': {k: bool(m.is_watertight) for k, m in P.items()}, 'watertight_exported_stl_reload': EXPORT_WT,
               'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
               'designed_contacts_mm3': {k: {'overlap_mm3': v, 'role': SOFT[frozenset(k.split('|'))]} for k, v in soft.items()},
               'module_removal_sweep_mm3': SWEEP_M, 'module_removal_sweep_max_mm3': SWEEP_M_MAX,
               'seal_continuity': CONT, 'seals_ok': SEALS_OK, 'dry_volume_flood_fill': DRY, 'dry_ok': DRY_OK,
               'tool_access': {k: {'verdict': v['verdict'], 'key_length_min_mm': v['key_length_min_mm'], 'first_obstacle': v['first_obstacle']} for k, v in TA.items()}, 'tool_access_ok': TA_OK,
               'clearances_mm': CLR, 'panel_probes': PAW, 'panel_ok': PANEL_OK, 'knock_out_skin_mm': KO_SKIN, 'led_flush_mm': LED_FLUSH, 'pod_seams': SEAMS,
               'print_downfacing_flatter_45_mm2': OVH,
               'inherited_from_6_3_0 (parts and outer envelope unchanged)': {
                   'why': 'bowl, flange plates, gate blade and ring, disc, plates, chute, latch, button are the 6.3.0 files; the shell keeps its outer skin, tabs, button boss and top edge, and the module fills the opening flush',
                   'gate_open_passage': V63['checks']['gate_open_passage'], 'gate_hold': V63['checks']['gate_hold'], 'interlock': {k: v for k, v in V63['checks']['interlock'].items() if k != 'table'},
                   'bayonet': {'max_mm3': V63['checks']['bayonet']['max_mm3']}, 'gate_sweep_max_mm3': max(max(r_[1:]) for r_ in V63['checks']['gate_sweep_mm3']['rows']),
                   'line_of_sight': V63['checks']['line_of_sight'], 'tool_access': INHERIT_TA, 'drainage': 'drain 1 and floor screed as 6.3; drain 2 (the +X sump) is gone with the sump: the module stands there'}},
    'load_case': LOAD, 'grams': GRAMS, 'hardware': HW,
    'print': {'scatola_v64': 'roof on the bed, NO supports: posts, webs and bosses now start on the bed, the rim flange has a 45 deg run-out; IP66 settings. Check the gland pad for flatness',
              'fondello_v64': 'flat bottom on the bed, NO supports (45 deg chamfer under the bottom radius); IP66 settings; elephant-foot compensation 0.15; the 2 drain holes are Ø1.5 (check they are open)',
              'guscio_v64': 'top edge (z +64) on the bed, opening upward; SUPPORTS NEEDED for the 3 bowl tabs only: tree supports, on build plate only, threshold 45 deg. The new 45 deg corbels carry the outer '
                            '10 mm of each tab; the inner 12 mm (r 50..62.6) sit where the bowl is and cannot have a corbel. Block supports elsewhere (button boss prints without); brim 6 mm',
              'guarnizione_fondello_v64': 'TPU, base on the bed, lip up (6.1 lip settings)',
              **MODULE_SPEC['print']},
    'open_risks': ['panel no longer on the room side (see decisions.panel_side): if that matters more than the module depth, the alternative is a module without the panel plus a panel left in the cap',
                   'second full board only with a low ESP stack; the 80 x 60 x 45 target is not reachable in this pod',
                   'J1: M8 5-pin is a 3 A connector; fine for a standard servo, not for a high-torque one',
                   'lid: 5 screws; the back edge and the two notch edges (~105 mm) have no screw and rely on the ribbed 3.2 mm lid and the soft outward lip. Water test before trusting IP66',
                   'guscio_v64 needs tree supports under the inner part of the 3 bowl tabs', 'J1 socket and its nut size are assumed, verify on the bought part before printing the lid',
                   'PT screws in the lid bosses: ~5-10 openings; for a development module melt M3 inserts into the 5 bosses (Ø7.5) instead',
                   'speakers Ø26-28 need the tall ring and a board notch', 'KO3 is shallow (guide wall behind it)',
                   'pod seams are 0.35 mm gaps without a seal: dust and insects are stopped by the ribs only; everything behind them is sealed or drains',
                   'the module weighs on two M3 inserts in printed posts (SF %.1f at 250 N); do not hang anything from the module' % LOAD['module_lock_M3x16']['SF_insert']],
    'shelf_template': TEMPLATE,
    'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] for k in P} |
             {'assembled_position_copies': 'v64_asm/*.stl', 'check': 'check_v64.png', 'viewer': 'v64_viewer.json', 'interface_drawing': 'interface_v64/', 'drilling_template': 'template_v64/'}}
_dflt = lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
json.dump(v64doc, open(staged(OUT + 'v64.json'), 'w'), indent=1, default=_dflt)
print('v64.json written')

# ---------------- v64_viewer.json (base: v63_viewer.json) ----------------
V63V = json.load(open(OUT + 'v63_viewer.json'))
GREEN, ORANGE, BLACK, YELLOW, STEEL, DARK = '#2e9d4f', '#f07a1a', '#2a2b2e', '#f2c81e', '#a8adb3', '#1e1e1e'


def _vp(id_, name, file_, color, group, material, qty, bought, explode, rotates=False, opacity=1.0):
    return {'id': id_, 'name': name, 'file': file_, 'color': color, 'opacity': opacity, 'group': group, 'material': material, 'qty': qty,
            'bought': bought, 'explode': explode, 'rotates': rotates}


DROP = {'scatola_v63', 'inserti_scatola', 'pressacavo', 'sfiato_eptfe', 'cavo_12v_unita', 'scheda', 'esp32', 'reg_12v', 'reg_5v', 'condensatore', 'guarnizione_fondello_v61',
        'fondello_v63_fondo', 'fondello_v63_fianco', 'fondello_v63_bordo', 'oring_giunto', 'fondello_v63_pannello', 'fondello_v63_pannello_2', 'fondello_v63_pannello_3',
        'fondello_v63_pannello_4', 'fondello_v63_pannello_5', 'switch_12mm_ip67', 'lightpipes_5mm', 'oring_5x1_lightpipe', 'leds_3mm', 'speaker_20mm', 'membrane_acoustic_ip67',
        'harness_jst', 'pt_k30x12_cap', 'oring_3x1_cap', 'guscio_v611_basso', 'guscio_v611_alto'}
VP = []
EXM = [70.0, 0.0, -150.0]                                    # the whole module moves as one block: down and out
for q in V63V['parts']:
    if q['id'] in DROP:
        continue
    VP.append(dict(q))
VP += [_vp('guscio_v64_basso', 'Guscio (pod) basso, con apertura modulo', FILES['guscio_v64_basso'], BLACK, 'struttura', 'PETG nero', 1, False, [0.0, -215.0, 20.0]),
       _vp('guscio_v64_alto', 'Guscio (pod) alto', FILES['guscio_v64_alto'], BLACK, 'struttura', 'PETG nero', 1, False, [0.0, -215.0, 20.0]),
       _vp('scatola_v64', 'Vano servo + supporto modulo (2 colonnine)', OUT + 'scatola_v64.stl', BLACK, 'struttura', 'PETG nero', 1, False, [0.0, 0.0, -85.0]),
       _vp('inserti_servo', 'Inserti M3 (culla servo, 4)', FILES['inserts_servo'], '#b08d57', 'ferramenta', 'ottone', 4, True, [0.0, 0.0, -85.0]),
       _vp('inserti_supporto', 'Inserti M3 (colonnine modulo, 2)', FILES['inserts_holder'], '#b08d57', 'ferramenta', 'ottone', 2, True, [0.0, 0.0, -85.0]),
       _vp('pressacavo', 'Pressacavo M12 (cavetto servo)', FILES['gland_m12'], '#303030', 'elettronica', 'PA nero', 1, True, [0.0, -40.0, -85.0]),
       _vp('sfiato_patch', 'Sfiato ePTFE adesivo (vano servo)', FILES['vent_patch_eptfe'], '#d0d0d0', 'elettronica', 'ePTFE', 1, True, [-20.0, 0.0, -85.0]),
       _vp('cablaggio_12v', 'Cablaggio telaio: ramo 12 V al connettore M8 in alto', FILES['harness_12v'], '#151515', 'elettronica', 'PUR 2x0.34', 1, True, [0, -40, -60]),
       _vp('cablaggio_servo', 'Cablaggio telaio: ramo servo tondo nel pressacavo', FILES['harness_servo'], '#b03a2e', 'elettronica', 'PUR 3x0.25 Ø4', 1, True, [0, -40, -60]),
       _vp('cablaggio_coda', f'Cablaggio telaio: coda {L_TAIL:.0f} mm con asola di servizio sul coperchio', FILES['harness_tail'], '#202020', 'elettronica', 'PUR 5x0.34 Ø4.5', 1, True, EXM),
       _vp('giunzione_y', 'Giunzione a Y (guaina termorestringente)', FILES['harness_splice_y'], '#3a3a3a', 'elettronica', 'guaina adesiva', 1, True, [0, -40, -60]),
       _vp('fascetta_cablaggio', 'Fascetta 2.5 x 100 (ancoraggio cablaggio)', FILES['cable_tie_harness'], '#111111', 'ferramenta', 'PA66', 1, True, [0, -40, -60]),
       _vp('jr_giunzione', 'Connettore JR 3 poli (servo + ramo, nel vano)', FILES['jr_3p_junction'], '#d4b000', 'elettronica', 'acquistato', 1, True, [0.0, 0.0, -160.0]),
       _vp('cavetto_servo', 'Cavetto originale del servo (nel vano)', FILES['servo_lead_in_bay'], '#b0603a', 'elettronica', 'piattina 3 fili', 1, True, [0.0, 0.0, -160.0]),
       _vp('spina_m8_5p', 'Spina M8 5 poli a 90 gradi (J1)', FILES['plug_m8_5p_angled'], '#3b3b3b', 'elettronica', 'acquistato', 1, True, EXM),
       _vp('guarnizione_fondello_v64', 'Guarnizione a labbro vano servo', OUT + 'guarnizione_fondello_v64.stl', YELLOW, 'guarnizioni', 'TPU 95A giallo', 1, False, [0.0, 0.0, -215.0]),
       _vp('fondello_v64_fondo', 'Fondello (fondo, con apertura modulo)', FILES['fondello_v64_fondo'], BLACK, 'struttura', 'PETG nero', 1, False, [0.0, 0.0, -240.0]),
       _vp('fondello_v64_fianco', 'Fondello (fianco)', FILES['fondello_v64_fianco'], BLACK, 'struttura', 'PETG nero', 1, False, [0.0, 0.0, -240.0]),
       _vp('fondello_v64_bordo', 'Fondello (bordo)', FILES['fondello_v64_bordo'], BLACK, 'struttura', 'PETG nero', 1, False, [0.0, 0.0, -240.0]),
       _vp('pt_k30x12_cap', 'Viti PT K30x12 fondello (4)', FILES['pt_k30x12_cap'], STEEL, 'ferramenta', 'acciaio inox A2', 4, True, [0, 0, -275]),
       _vp('oring_3x1_cap', 'O-ring 3x1 sotto le viti del fondello (4)', FILES['oring_3x1_cap'], DARK, 'guarnizioni', 'NBR70', 4, True, [0, 0, -262])]
TUB_NAMES = {'modulo_vasca_alto': 'Modulo: vasca (parte alta)', 'modulo_vasca_fondo': 'Modulo: vasca (fondo, griglia altoparlante)'}
for k in TUB_PIECES:
    VP.append(_vp(k, TUB_NAMES.get(k, 'Modulo: vasca (pannello comandi)'), FILES[k], BLACK, 'modulo', 'PETG nero', 1, False, EXM))
MOD_VIEW = [('modulo_coperchio_v64', 'Modulo: coperchio con torretta J1', OUT + 'modulo_coperchio_v64.stl', BLACK, 'PETG nero', 1, False),
            ('modulo_guarnizione_v64', 'Modulo: guarnizione a labbro del coperchio', OUT + 'modulo_guarnizione_v64.stl', YELLOW, 'TPU 95A giallo', 1, False),
            ('modulo_anello_speaker_v64', 'Modulo: anello adattatore altoparlante', OUT + 'modulo_anello_speaker_v64.stl', ORANGE, 'PETG arancione', 1, False),
            ('switch_12mm_ip67', 'Pulsante pannello IP67 Ø12', FILES['switch_12mm_ip67'], '#c9ccd1', 'acciaio / IP67', 1, True),
            ('lightpipes_5mm', 'Guide luce Ø5 (2)', FILES['lightpipes_5mm'], '#e8f4ff', 'PC trasparente', 2, True),
            ('oring_5x1_lightpipe', 'O-ring guide luce 5x1 (2)', FILES['oring_5x1_lightpipe'], DARK, 'NBR70', 2, True),
            ('leds_3mm', 'LED 3 mm (stato, Wi-Fi)', FILES['leds_3mm'], '#3fd16b', 'acquistato', 2, True),
            ('speaker_23mm', 'Altoparlante Ø23 (esempio)', FILES['speaker_23mm'], '#444b55', 'acquistato', 1, True),
            ('membrane_acoustic_ip67', 'Membrana acustica IP67 ePTFE', FILES['membrane_acoustic_ip67'], '#f5f5f5', 'ePTFE', 1, True),
            ('board_70x50_A', 'Millefori 5x7 nello slot A (esempio)', FILES['board_70x50_A'], '#3d7a3d', 'acquistato', 1, True),
            ('esp32_wrover_stack', 'ESP32-WROVER su strip (ingombro 61x28x25)', FILES['esp32_wrover_stack'], '#1b1b1b', 'acquistato', 1, True),
            ('reg_6v', 'Regolatore 6 V (esempio)', FILES['reg_6v'], '#2b4a7a', 'acquistato', 1, True),
            ('reg_5v', 'Regolatore 5 V (esempio)', FILES['reg_5v'], '#2b4a7a', 'acquistato', 1, True),
            ('cap_1000uF', 'Condensatore 1000 µF', FILES['cap_1000uF'], '#1a1a2e', 'acquistato', 1, True),
            ('socket_m8_5p', 'Presa M8 5 poli da pannello (J1)', FILES['socket_m8_5p'], '#8a8f96', 'acquistato', 1, True),
            ('pt_k30x10_lid', 'Viti PT K30x10 coperchio (5)', FILES['pt_k30x10_lid'], STEEL, 'acciaio inox A2', 5, True),
            ('oring_3x1_lid', 'O-ring 3x1 viti coperchio (5)', FILES['oring_3x1_lid'], DARK, 'NBR70', 5, True),
            ('m3x16_module_lock', 'Viti M3x16 blocco modulo (2, da sotto)', FILES['m3x16_module_lock'], STEEL, 'acciaio inox A2', 2, True)]
for id_, name, f, colr, mat, qty, bought in MOD_VIEW:
    VP.append(_vp(id_, name, f, colr, 'modulo', mat, qty, bought, EXM if id_ != 'm3x16_module_lock' else [70.0, 0.0, -235.0]))
viewer = {k: v for k, v in V63V.items() if k not in ('parts', 'scene')}
viewer['title'] = 'Kibble Dispenser Outdoor v6.4'
viewer['subtitle'] = 'meccanica + modulo elettronica estraibile (case 1.0)'
viewer['groups'] = dict(V63V['groups'], modulo='Modulo elettronica')
viewer['parts'] = VP
viewer['scene'] = dict(V63V['scene'])
json.dump(viewer, open(staged(OUT + 'v64_viewer.json'), 'w'), indent=1)
vout = json.loads(json.dumps(viewer))
for q in vout['parts']:
    if q['id'] in FILES_OUT:
        q['file'] = FILES_OUT[q['id']]
vout['subtitle'] = 'modulo elettronica ESTRATTO da sotto (95 mm)'
json.dump(vout, open(SCRATCH + 'v64_viewer_out.json', 'w'), indent=1)
missing = [q['file'] for q in VP if not os.path.exists(current(q['file']))]
print('v64_viewer.json written:', len(VP), 'entries; missing files:', missing)
commit_staged()
print(f'checks done in {time.time() - t_start:.0f} s')
