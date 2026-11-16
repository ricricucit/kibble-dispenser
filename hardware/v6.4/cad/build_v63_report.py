# executed at the end of build_v63_checks.py (same namespace): check_v63.png, drilling template v63, v63.json, v63_viewer.json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle

# ---------------- check_v63.png ----------------
print('\n--- render check_v63.png ---')
PANELB = U([BOUGHT[k] for k in ('switch_12mm_ip67', 'lightpipes_5mm', 'leds_3mm', 'speaker_20mm', 'membrane_acoustic_ip67')])
DRAW = [('shelf', SHELF, '#E8D9B5', '#8A6D3B', '///'),
        ('electronics / servo / connector / cable', U([ELEC, BOUGHT['servo'], BOUGHT['connector_m8_ip67'], BOUGHT['cable_12v_supply'], BOUGHT['cable_12v_unit']]), '#CCCCCC', '#666666', '...'),
        ('panel parts (switch, light pipes, LEDs, speaker, membrane)', PANELB, '#9fb7d9', '#24456e', None),
        ('pod: guscio v611 / fondello v63 (panel)', U([P611['guscio_v611'], P['fondello_v63']]), '#2a2b2e', 'k', None),
        ('flange v63 / colonna v63 / scatola v63', U([P['flangia_piano_v63'], P['flangia_alta_v63'], P['colonna_v63'], P['scatola_v63']]), '#4a4a4a', 'k', None),
        ('chiocciola v63', P['chiocciola_v63'], '#606060', 'k', None),
        ('food path green: scivolo, gate blade (one colour), collar', U([P611['scivolo_v611'], P['saracinesca_v63'], COLLAR]), '#2E9D4F', 'k', None),
        ('orange: gate ring, latch button', U([RINGP[G_OPEN], P611['pulsante_v611']]), '#F07A1A', '#7A3A00', None),
        ('TPU yellow: grommet, skirt lip, chute lip', U([P['passacavo_v63'], P611['labbro_ombra_v611'], P611['labbro_scivolo_v611']]), '#F2C81E', '#7A6A00', None),
        ('steel: M3x40, PT K30 cap screws, O-rings, tie', U([SCREWS['m3x40_stack'], SCREWS['pt_k30x12_cap'], BOUGHT['oring_3x1'], BOUGHT['oring_3x1_cap'], BOUGHT['cable_tie']]),
         '#A8ADB3', '#555555', None)]


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
    return T


X_, Y_, Z_ = np.array([1., 0, 0]), np.array([0, 1., 0]), np.array([0, 0, 1.])
fig, axs = plt.subplots(2, 4, figsize=(34, 17), facecolor='white')
draw(axs[0, 0], [0, 0, 0], Y_, Z_, f'{VER} section X=0 (YZ): panel in the cap (room side +Y), cable exit at -Y, no channel', (-105, 100), (-110, 95))
# panel plan at the element row
Tpl = draw(axs[0, 1], [0, 0, Z_E], X_, Y_, f'panel plan at z {Z_E}: dry pocket behind the band opens into the D under the box', (-62, 52), (8, 75))
for nm_, phi, dz_ in ELEMS:
    Pk, nk, _ = PANEL['frames'][nm_]
    axs[0, 1].annotate(nm_.upper(), xy=(Pk[0], Pk[1]), xytext=(Pk[0] + 9 * nk[0], Pk[1] + 9 * nk[1]), fontsize=8, ha='center',
                       arrowprops=dict(arrowstyle='-', lw=0.5))
for nm_, (x, y) in CAP_SCREWS.items():
    if y > 8:
        axs[0, 1].plot([x], [y], 'x', c='r', ms=8); axs[0, 1].text(x + 1.5, y + 1.5, f'cap screw {nm_}', fontsize=7, color='r')
# radial section through the button with the probes
Pb, nb, phib = PANEL['frames']['btn']
ub = np.array([nb[0], nb[1], 0.0]); ub /= np.linalg.norm(ub)
ax = axs[0, 2]
draw(ax, Pb, ub, Z_, f'button recess (radial section {phib:.0f} deg): paw Ø30/Ø40, snout Ø25 stop short; fingertip Ø16 reaches', (-34, 14), (-18, 20))
for lab_, d, colr in (('paw Ø30', 30.0, '#c0392b'), ('paw Ø40', 40.0, '#8e44ad'), ('snout Ø25', 25.0, '#d35400')):
    dep = PAW['btn'][lab_.replace('paw', 'paw pad sphere').replace('snout', 'snout sphere')]['deepest_mm']
    ax.add_patch(Circle((-dep + d / 2 * 1.0 + 0.0, 0.0), d / 2, fc='none', ec=colr, lw=1.2, ls='--'))
    ax.text(-dep + d / 2 + 0.5, d / 2 * 0.7, f'{lab_}: {dep:.1f} mm deep (face {REC["face"]})', fontsize=7, color=colr)
fd = PAW['btn']['fingertip Ø16']['deepest_mm']
ax.add_patch(Rectangle((-fd, -8.0), fd + 14, 16.0, fc='#f5cba7', ec='#a04000', alpha=0.35)); ax.text(-fd + 0.5, -10.5, f'fingertip Ø16 reaches {fd:.1f}', fontsize=7, color='#a04000')
ax.axvline(-REC['face'], c='b', lw=0.6, ls=':')
# knock-out + speaker section
Pk, nk, phik = PANEL['frames']['ko2']
uk = np.array([nk[0], nk[1], 0.0]); uk /= np.linalg.norm(uk)
draw(axs[0, 3], Pk, uk, Z_, f'flush knock-out KO2 (radial section): skin {KO_SKIN["ko2"]["plain_min_mm"]:.2f} ({KO_SKIN["ko2"]["under_engraving_min_mm"]:.2f} under the 0.3 '
     f'engraving), Ø{KO["bore"]} counterbore + Ø{KO["pad_d"]:.0f} nut seat {KO["pad"]} deep', (-32, 12), (-20, 18),
     items=DRAW + [('future switch (envelope)', U(list(future_switch(Pk, nk).values())), 'none', '#c0392b', None)])
# P3 head clearance
draw(axs[1, 0], [0, 0, Z_R - ROOF_T - 1.5], X_, Y_, f'P3 head at z {Z_R - ROOF_T - 1.5:.1f}: Ø7.5 pocket in the cradle top, board 1.15 away (v6.2: 0.375)', (8, 30), (2, 26),
     items=[DRAW[1], DRAW[4], DRAW[9]])
axs[1, 0].add_patch(Circle(P_SCREWS[2], 2.75, fc='none', ec='r', lw=1.0))
axs[1, 0].add_patch(Rectangle((BB['x'][0], 2.0), BB['x'][1] - BB['x'][0], 24.0, fc='#3d7a3d', ec='k', alpha=0.8))
axs[1, 0].text(BB['x'][1] + 0.4, 20.0, '70x50 board', fontsize=8, rotation=90)
# cable exit
draw(axs[1, 1], [0, 0, 0], Y_, Z_, 'cable exit (YZ at x=0): tunnel raised, tie window, bell mouth, 0.4 proud of the shelf face', (-100, -60), (45, 85))
# gate interlock plot
ax = axs[1, 2]
gg_ = [d['g_deg'] for d in INTERLOCK]
ax.plot([c[0] for c in COVER], [100 * c[1] for c in COVER], c='#2E9D4F', lw=2, label='opening covered by the blade (%)')
ax.step(gg_, [100 if d['any_fingertip_reaches'] or d['thumb_reaches_button'] else 0 for d in INTERLOCK], where='mid', c='#F07A1A', lw=2,
        label='release button reachable through the teardrop window')
ax.axvline(g_full, c='k', ls='--', lw=1); ax.text(g_full + 0.5, 50, f'fully covered from {g_full:.0f} deg', fontsize=9)
if g_reach_first is not None:
    ax.axvline(g_reach_first, c='#F07A1A', ls=':', lw=1); ax.text(g_reach_first + 0.5, 20, f'button first reachable {g_reach_first:.0f} deg', fontsize=9)
ax.set_xlabel('gate closing angle g (deg)'); ax.set_ylim(-5, 105); ax.legend(fontsize=9, loc='center left'); ax.grid(alpha=0.25)
ax.set_title(f'interlock (strict = {INTERLOCK_OK}): button reachable only after the opening is covered', fontsize=10)
# cap bottom
draw(axs[1, 3], [0, 0, Z_BOT + 0.6], X_, Y_, 'cap bottom (z -103.4): screw counterbores A/B/C, drains 1 + 2 (new, +X sump), grille', (-82, 64), (-72, 72),
     items=[('fondello_v63', P['fondello_v63'], '#2a2b2e', 'k', None), ('screws', U([SCREWS['pt_k30x12_cap']]), '#A8ADB3', '#555', None)])
handles = [Rectangle((0, 0), 1, 1, fc=d[2], ec=d[3], hatch=d[4]) for d in DRAW]
axs[0, 0].legend(handles, [d[0] for d in DRAW], loc='upper right', fontsize=7)
plt.tight_layout()
plt.savefig(staged(OUT + 'check_v63.png'), dpi=60)
plt.close(fig)
print('check_v63.png written')

# ---------------- drilling template (SVG + PDF, A4 portrait, 1:1, VIEW FROM BELOW) ----------------
A4W, A4H = 210.0, 297.0
CXp, CYp = 105.0, 150.0
TPL_ITEMS = []
S_MAIN = dict(stroke='#000', w=0.35, dash=None, fill='none')
tp = lambda x, y: (CXp - x, CYp - y)
T_circle = lambda x, y, r, **st: TPL_ITEMS.append(('circle', *tp(x, y), r, dict(S_MAIN, **st)))
T_line = lambda x0, y0, x1, y1, **st: TPL_ITEMS.append(('line', *tp(x0, y0), *tp(x1, y1), dict(S_MAIN, **st)))


def T_text(x, y, s, size=3.2, anchor='middle', weight='normal', sheet=False, colour='#000'):
    X, Y = (x, y) if sheet else tp(x, y)
    TPL_ITEMS.append(('text', X, Y, s, size, anchor, weight, colour))


def T_cross(x, y, L=5.0, **st):
    T_line(x - L, y, x + L, y, **st); T_line(x, y - L, x, y + L, **st)


TPL_ITEMS.append(('rect', 6.0, 6.0, A4W - 12.0, A4H - 12.0, dict(S_MAIN, w=0.2, stroke='#888')))
T_text(105, 14.0, f'Kibble Dispenser Outdoor {VER} - drilling template 1:1', 5.0, weight='bold', sheet=True)
T_text(105, 19.5, 'VIEW FROM BELOW: tape it under the shelf with the PRINTED SIDE FACING YOU, arrow towards the room side', 3.0, sheet=True)
# cable exit (no channel any more)
T_line(0.0, -FL_R62, 0.0, -(FL_R62 + 28.0), w=0.5, dash='2,1.2', stroke='#555')
TPL_ITEMS.append(('poly', [tp(0.0, -(FL_R62 + 30.0)), tp(-2.5, -(FL_R62 + 25.0)), tp(2.5, -(FL_R62 + 25.0))], dict(S_MAIN, fill='#555', stroke='#555')))
T_text(-6.0, -(FL_R62 + 12.0), 'CABLE EXIT (back): route the cable with ordinary clips', 2.7, anchor='start', weight='bold', colour='#555')
T_text(-6.0, -(FL_R62 + 17.0), 'along the shelf, leave a drip loop before it goes down', 2.5, anchor='start', colour='#555')
T_circle(0.0, 0.0, 100.0, dash='3,2', stroke='#E06A00', w=0.4)
T_text(10.0, 42.0, 'dashed orange circle r 100: keep clear, the gate ring is turned by hand', 2.5, anchor='start', sheet=True, colour='#E06A00')
T_circle(0.0, 0.0, FL_R62, w=0.5)
T_circle(0.0, 0.0, RING['ro'], dash='1,1', stroke='#E06A00', w=0.3)
T_text(-52.0, 62.0, f'flange outline Ø{2*FL_R62:.0f}', 2.6)
T_cross(0.0, 0.0, 4.0, w=0.25); T_text(-6.0, -4.0, 'flange centre', 2.4, anchor='start')
hx, hy = v6.HOLE_C
T_circle(hx, hy, 38.0, dash='4,1.5', w=0.5)
T_cross(hx, hy, 8.0, w=0.4); T_circle(hx, hy, 3.0, w=0.3)
T_text(hx, hy + 11.0, 'HOLE SAW Ø76', 3.4, weight='bold'); T_text(hx, hy + 7.0, 'centre: drill the Ø6 pilot here', 2.6)
T_line(0, 0, hx, hy, w=0.2, dash='1,1'); T_text(hx / 2, -4.0, f'{hx:.0f} mm', 2.4)
for k, aw in enumerate(WOOD_ANG62):
    x, y = polar(WOOD_R62, aw)
    T_cross(x, y, 4.0, w=0.35); T_circle(x, y, 1.5, w=0.3)
    ox, oy = polar(WOOD_R62 - 10.0, aw)
    T_text(ox, oy + 1.0, f'S{k + 1}', 3.0, weight='bold')
T_text(-20.0, 54.0, 'S1-S4: wood screws 5x35 pan head', 2.5); T_text(-20.0, 50.0, '(5x30 for an 18 mm shelf), pre-drill Ø3 x 25', 2.5)
bx_, by_ = polar(80.0, LATCH_A)
T_circle(bx_, by_, 3.0, stroke='#E06A00', w=0.4); T_text(bx_ + 5.0, by_ - 1.0, 'release button + gate window', 2.4, anchor='end', colour='#E06A00')
T_text(4.0, 41.5, 'control panel: 182 mm below, low on the room side,', 2.4, colour='#24456e')
T_text(4.0, 38.0, 'keep 150 mm free in front of it for a finger', 2.4, colour='#24456e')
T_circle(CH_X, 0.0, 24.5, dash='0.8,0.8', stroke='#2E9D4F', w=0.3); T_text(CH_X, 1.0, 'outlet (182 mm below)', 2.4, colour='#2E9D4F')
T_text(105, 27.0, 'FRONT / ROOM SIDE (you stand here; release button, gate window and control panel face you)', 3.0, weight='bold', sheet=True)
TPL_ITEMS.append(('poly', [(105.0, 30.5), (101.0, 36.5), (103.5, 36.5), (103.5, 45.0), (106.5, 45.0), (106.5, 36.5), (109.0, 36.5)], dict(S_MAIN, fill='#000')))
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
open(staged(TPL + 'dima_foratura_v63.svg'), 'w').write('\n'.join(svg))
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
_tpl_pdf = staged(TPL + 'dima_foratura_v63.pdf')                 # read back below before commit_staged() renames it
figT.savefig(_tpl_pdf, metadata={'CreationDate': None})        # no timestamp: the same input gives the same PDF
figT.savefig(SCRATCH + 'dima_preview_v63.png', dpi=110)
plt.close(figT)
import re as _re
_pdf = open(_tpl_pdf, 'rb').read()
_mb = _re.search(rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]', _pdf)
TEMPLATE = {'svg': 'template_v63/dima_foratura_v63.svg', 'pdf': 'template_v63/dima_foratura_v63.pdf',
            'pdf_mediabox_pt': [float(v) for v in _mb.groups()] if _mb else None, 'a4_pt': [595.28, 841.89],
            'contents': ['flange outline Ø180 + ring', 'hole-saw Ø76 centre (27 mm from the flange centre) with pilot mark', '4 wood-screw positions S1..S4 (r 75.5 at 80/150/225/295 deg)',
                         'keep-clear circle r 100 for the hand on the gate ring', 'cable exit arrow at the back (270 deg) - no channel strip any more',
                         'FRONT arrow (room side: release button, gate window, control panel)', 'outlet position for the pet bowl', '50 mm scale bar'],
            'view': 'from below, printed side facing the person below, FRONT at the top of the sheet: not mirrored (as v6.2)',
            'text_line': 'VIEW FROM BELOW: tape it under the shelf with the PRINTED SIDE FACING YOU, arrow towards the room side'}
print('template written', TEMPLATE['pdf_mediabox_pt'])

# ---------------- v63.json ----------------
SCREW_TABLE = {k: {'verdict': v['verdict'], 'straight_key_reaches_head': v['shaft_clear'], 'key_length_min_mm': v['key_length_min_mm'], 'first_obstacle': v['first_obstacle']}
               for k, v in TA.items()}
PANEL_SPEC = {
    'location': 'pod cap (fondello_v63), room side: band centred on the release-button azimuth (button at 76.6 deg from the shaft axis), 182 mm '
                'below the shelf; the cap is the dry-box floor, so the band wall IS the dry-box wall: no new joint, no gasket frame',
    'band': {'creases_z': [ZB0, ZB1], 'section_frame_deg': [PHI_A, PHI_B], 'side_ramps_deg': PHI_RAMP, 'max_recess_mm': round(max(pod_circle(0.0, z)[1] - band_rho(z) for z in np.linspace(ZB0, ZB1, 60)), 2),
             'shape': 'straight-ruled band (vertical generatrices between the creases, follows the pod in plan): flatter than the skin, smooth convex '
                      'creases top and bottom, 6 deg ramps at the ends; regular rectangle in the unrolled view, 23.4 mm tall x ~110 mm long',
             'wall_mm': BAND_WALL},
    'layout_room_view_left_to_right': [f'LED pair at 51 deg: LED1 status/ON-OFF on top (z {Z_E + ELEMS[0][2]}), LED2 Wi-Fi/feedback below (z {Z_E + ELEMS[1][2]})', 'BUTTON (67 deg)',
                                       f'KO1 ({ELEMS[3][1]:.0f} deg)', f'KO2 ({ELEMS[4][1]:.0f} deg)', f'KO3 ({ELEMS[5][1]:.0f} deg)'],
    'grid': f'button at z {Z_E} (axis radial, 3 deg down-outward); 3 knock-outs on a row at z {Z_E + KO_DZ} (axes on the facet normal, '
            f'10-14 deg down-outward, so a future switch seats square), {PITCH:.0f} deg pitch = '
            f'{round(math.radians(PITCH) * band_rho(Z_E), 1)} mm on the band, KO1 {BTN_KO_GAP:.0f} deg = {round(math.radians(BTN_KO_GAP) * band_rho(Z_E), 1)} mm '
            f'from the button (radial axes converge inward: a future switch in KO1 must clear the button boss and nut; v6.3 first issue: 17 deg everywhere)',
    'button_recess': {'bore_d_mm': REC['d'], 'switch_face_depth_mm': REC['face'], 'floor_depth_mm': REC['floor'], 'mount_wall_mm': REC['wall'], 'rim_chamfer_mm': REC['ch'],
                      'why': 'a Ø17 bore admits a Ø12-16 fingertip (cylinder, 0.5 mm clearance at Ø16) to the full depth; a paw pad or a snout '
                             '(spheres Ø25-40) sinks only by its sagitta over the rim (Ø30: 2.6 mm on a flat rim, measured with 15 deg tilted approaches '
                             'below), so the switch face 8 mm down stays out of reach; the bore drains (axis 3 deg down-outward)',
                      'probes': PAW, 'all_ok': PANEL_OK, 'min_margin_paw_snout_to_actuator_mm': PAW_MARGIN},
    'knock_outs': {'positions': 3, 'qc_2026_11_10': 'FLUSH with the band (the first issue had three open Ø17 x 9.5 cups with a 0.8 mm skin: they read as '
                                                    'holes, gave claws a hook and were fox-bite weak)',
                   'outside': f'flush; only a {KO["engr"]} mm deep engraved ring Ø{KO["ring_d"]:.0f} (line {KO["ring_w"]}) = the future hole, and a '
                              f'Ø{KO["dot_d"]} x {KO["engr"]} centre dot = pilot mark; nothing to hook a claw into',
                   'skin': f'the outer wall itself: {KO["skin"]} mm ({round(KO["skin"] - KO["engr"], 1)} under the engraving), thinned only from the inside',
                   'inside': f'blind Ø{KO["bore"]} counterbore whose floor follows the facet (uniform skin), then a flat Ø{KO["pad_d"]:.0f} nut-seat face '
                             f'perpendicular to the axis {KO["pad"]} mm behind the outer face (the wall is {BAND_WALL} mm elsewhere)',
                   'measured': KO_SKIN, 'flushness_voids_mm3': KO_FLUSH,
                   'drilling_recipe': ['1 cap off, dry, on a soft pad, room side up; pick the knock-out (KO1 first)',
                                       f'2 pilot Ø3 mm at the centre dot, square to the band face (it faces 10-14 deg downward; the dot and the Ø{KO["ring_d"]:.0f} ring are the marks)',
                                       f'3 step drill (4-12 or 4-20 mm) from the front up to the Ø12 step: one step cuts the {KO["skin"]} mm skin and breaks '
                                       f'into the Ø{KO["bore"]} counterbore, so the hole is round and burr-free; low speed, no coolant',
                                       '4 deburr the inside edge lightly; blow out the chips, check the dry pocket is clean',
                                       f'5 fit a 12 mm IP67 switch (M12 front mount, nut <= 14 AF): front gasket on the outer face, nut on the flat seat; '
                                       f'clamp thickness {KO["pad"]} mm (check the switch takes it). The outer face is curved in plan (sagitta ~0.4 mm '
                                       f'over a Ø15 head): add a thin bead of neutral-cure silicone under the gasket, or',
                                       '6 if a paw-proof recess is wanted (unit at paw/snout height): glue on a printed bezel ring (Ø17 bore x 8 deep, '
                                       'like the real button) with PETG-compatible adhesive/sealant over the drilled hole; it also gives the gasket a flat seat',
                                       '7 harness: the spare JST position (KO1) goes to GPIO13 (proposal)'],
                   'future_switch_fit': {'envelope': f'thread Ø12 through the wall, nut {KO["nut_d"]} across corners swinging with {KO["nut_swing"]} clearance '
                                                     f'x {KO["nut_h"]} on the seat, body Ø{KO["body_d"]:.0f} x {KO["body_len"]} behind the nut',
                                         'result': FUTURE_KO},
                   'ip': 'the dry box stays sealed until a knock-out is drilled'},
    'light_windows': {'type': 'Ø5 clear PC light pipe, flat flush lens, flange Ø8 inside, O-ring 5x1 NBR in a Ø7.2 x 0.75 counterbore (25 % squeeze), '
                              'retained by its snap barbs or a dab of neutral-cure silicone; LED 3 mm on a 2-wire lead behind it',
                      'hole_d': LED['hole'], 'boss': f'Ø{LED["boss_d"]} x {LED["len"]}', 'flush': True,
                      'axis': 'square to the band face (facet normal) since 6.3.0, so the flat lens sits flush all round', 'measured': LED_FIX},
    'acoustic_opening': {'type': 'protected grille + membrane: 7 x Ø1.5 holes (hex, Ø8 active area) through the 2 mm flat bottom, facing straight down, '
                                 '0.5 x 45 deg outer chamfer; IP67 adhesive ePTFE acoustic membrane Ø15 (active Ø8) on the inside; speaker on a foam ring '
                                 'in a printed cup', 'position_xy': [SPK['x'], SPK['y']], 'water_trap': 'none (down-facing holes, nothing above them holds water)'},
    'dry_pocket': {'plan': f'annular sector behind the band from {POCKET["phi0"]:.0f} to {POCKET["phi1"]:.0f} deg (section frame; west end 128 since the flush-KO QC so a future KO3 switch body clears it), floor = cap floor, roof 2 mm falling 1 deg westward, '
                           'opens into the D interior below the cap-lip beam (the lip groove stays continuous on a 2.8 mm beam over the opening)',
                   'flood_fill': DRY, 'ceiling_z_east_west': [POCKET['roof_top'] - POCKET['roof_t'], round(POCKET['roof_top'] - POCKET['roof_t'] - math.tan(math.radians(POCKET['slope_deg'])) * 96, 2)]},
    'bought_parts': [
        {'qty': 1, 'item': 'IP67 12 mm momentary pushbutton, flush flat head, M12x1 front mount, panel 1-5 mm, <= 14 mm behind the panel (Ø13 body), front gasket',
         'note': 'several makers\' short-body 12 mm "anti-vandal" types; confirm IP67 and the depth on the datasheet (14 mm is the free depth behind the mount wall)'},
        {'qty': 2, 'item': 'panel light pipe Ø5 x 9-10 mm, flat flush lens, flange Ø8 (clear PC)', 'with': '2 x O-ring 5x1 NBR70'},
        {'qty': 2, 'item': 'LED 3 mm (status green, Wi-Fi blue) + series resistors on the board'},
        {'qty': 1, 'item': 'IP67 adhesive acoustic vent / membrane, ePTFE, Ø15 disc with Ø8 active area (GORE acoustic-vent class)'},
        {'qty': 1, 'item': 'mylar speaker Ø20 x 4.5, 8 ohm 0.5 W (water-resistant type preferred), foam ring Ø20/12 x 1'},
        {'qty': 1, 'item': 'harness JST-XH 2.54 8-pin (button 2, LED 3, speaker 2, 1 spare for KO1) to the 70x50 board, plugged before the cap goes on'}],
    'mounting_side': 'all panel parts are fitted from the inside of the cap (dry side) at the factory; the cap is the last part, the harness '
                     'plugs into the board edge connector just above the cap D interior'}
UI_NOTE = {'controls': '1 push-button + 2 LEDs + speaker (meaning of the LEDs not final)',
           'mapping': {'single press': 'dispense exactly one portion - only while the unit is ON (behaviour contract); while OFF: a short LED blink, no dispense',
                       'double press (2 presses within 400 ms)': 'toggle ON/OFF; switching ON dispenses exactly one portion (contract), switching OFF dispenses nothing',
                       'long press 5 s': 'reset all settings except Wi-Fi (act on release after the 5 s LED pattern; no dispense)',
                       'long press 10 s': 'full reset incl. Wi-Fi (act on release after the 10 s LED pattern; no dispense)'},
           'rules': ['a single press is confirmed only after the double-press window (~400 ms) has expired: one press = one cycle, never two',
                     'holding the button never repeats a cycle', 'the meow / sound plays at every portion (speaker behind the down-facing grille)',
                     'never dispense at power-on: both disc rest positions are closed; store the last rest position in NVS and command exactly it at boot '
                     'before enabling the servo PWM; a cold start without a stored value goes to 0 deg; the unit boots OFF',
                     'debounce 20-30 ms; long-press thresholds counted from the press, LED patterns at 5 s and 10 s so the user knows when to let go'],
           'pins': 'proposal only, not electrically verified: button on GPIO27 (old dispense input, active-low with pull-up), LED1 GPIO2, LED2 a free '
                   'output (e.g. GPIO25), speaker PWM GPIO26 as today; GPIO13 (old ON/OFF input) freed for KO1'}
v63doc = {
    'version': VER, 'release': '6.3.0', 'base': 'v6.2 (v62.json): everything not listed here is unchanged',
    'fixes_6_3_0': {'led_light_pipes': LED_FIX, 'lower_flange_dowel_seat': DOWEL_SEAT, 'cap_seam_spigot': CAP_BODIES,
                    'knock_outs_flush': 'see 3_control_panel.knock_outs (QC 2026-11-10)',
                    'note': 'the spigot defect (separate ring) also exists in fondello_v611 / fondello_v62; those files are left as they are'},
    'frame': 'as v6.2: Z-up mm, shaft axis x=y=0, Z=0 = bowl base underside, LOCKED bayonet pose, gate OPEN, shelf underside z 78.1',
    'changes': {
        '1_cable_channel_removed': {
            'removed': ['canalina_base_v62 x2', 'canalina_coperchio_v62 x2', 'canalina_tappo_v62', '4 x wood screw 3.5x16', 'channel port in the upper plate'],
            'route': 'box gland -> unit pigtail -> M8 IP67 connector in the pod top (as v6.2) -> supply cable up at r 74 -> R 15 bend in the flange -> '
                     'rim exit at 270 deg (back), 0.4 mm proud of the shelf face -> user clips along the shelf',
            'strain_relief': {'tie': 'UV-stable PA66 cable tie 3.6 x 140 cinched round the cable in a window through the upper plate (r 81.5..86.5, '
                                     'floor = lower plate): a pull or bite outside drags the cinched tie against the 3.5 mm rim wall, the Ø5.6 bore '
                                     'cannot pass it; nothing reaches the connector',
                              'shelf_clamp': 'the last 7 mm of the cable stand 0.4 mm proud of the shelf face: the 4 wood screws clamp the jacket against the wood',
                              'bend': 'R 15 bend + TPU grommet at the pod side as v6.2', 'exit': 'bell mouth Ø5.6 -> Ø8 at the rim (no sharp edge when pulled sideways)',
                              'cable_clear_of_ring_groove_mm': CLR['cable_tunnel_to_ring_groove_mm']}},
        '2_simplification': {
            'pieces_before_after': {'v62': GRAMS['v62'], 'v63': GRAMS['v63'], 'delta_pct': GRAMS['delta_pieces_pct']},
            'removed_or_merged': [
                {'what': 'cable channel (5 printed pieces, 4 screws)', 'decision': 'removed', 'why': 'owner request 1'},
                {'what': '3 thumb-turns + 3 keys + 3 O-rings 8x1.5 + 3 cups', 'decision': '3 PT K30x12 thread-forming screws (no inserts) + O-ring 3x1 under each head',
                 'why': 'they draw the cap home (no ~130 N push), the bosses bottom on the box (hard stop, lip compression as v6.2); twist-lock rejected: '
                        'the dry-box lip is D-shaped and the outlet socket sits 31.8 mm off the seam centre, so the cap cannot rotate at all; snap-fits rejected '
                        '(keep the 130 N push and cannot be opened for service)'},
                {'what': '3 ST2.9 flange join screws', 'decision': '3 press-fit pins on the upper plate', 'why': 'the 4 wood screws clamp the set in service; the pins only hold it together in the box'},
                {'what': '5 heat-set inserts (chute ears, shell tabs)', 'decision': 'PT K30 screws straight into Ø2.5 pilots', 'why': 'assembled once, low loads; the 3 stack inserts (preload, creep) and the 4 servo inserts stay'},
                {'what': 'gate blade colours', 'decision': 'one colour (green)', 'why': f'the orange arm ran through all {SW62["saracinesca_v62"]} layers; it is hidden inside the flange'},
                {'what': 'printed pivot pin', 'decision': 'ISO 2338 4x6 dowel (print_v62 correction folded into the CAD)', 'why': 'the pin made the plate float 3.3 mm on the bed'}],
            'kept_with_reasons': [
                {'idea': 'funnel collar into the flange', 'decision': 'kept separate', 'why': 'the upper plate must print shelf face down so the blade pocket opens '
                 'upward; the collar rises 13 mm from that face (the other way up the 230 deg pocket roof would need support over ~9000 mm2)'},
                {'idea': 'two flange plates + gate -> fewer parts', 'decision': 'kept (4 pieces)', 'why': 'the ring must snap into the lower plate (its groove sits '
                 'below the cable tunnel) and the blade must sit above it; a blade-ring part needs the groove in the upper plate, where it cuts the cable path at 270 deg; '
                 'print-in-place blade impossible (flat 0.2 mm z gaps)'},
                {'idea': 'latch + push-button', 'decision': 'kept separate', 'why': 'the latch slides into the bowl before the shell goes on; a plunger on the latch '
                 'would need a slot from the button bore to the shell rim (pod seal and button O-ring lost)'},
                {'idea': 'tower into box or bowl', 'decision': 'kept separate', 'why': 'box prints roof-down and the bowl base-down: the tower would be under the bed; '
                 'flipping either gives an 82 mm / Ø120 bridge'},
                {'idea': 'chute into the cap', 'decision': 'kept separate', 'why': 'moves the sealed joint to the top of the chute, deep inside the pod where it cannot '
                 'be checked, couples electronics service with the food path and makes the largest print 180 mm tall and two-coloured'},
                {'idea': 'hub into shaft', 'decision': 'kept separate', 'why': 'blind-mate coupling when the box goes onto the tower, spline screw access'}],
            'plastic': {'v62_PETG_g': GRAMS['v62']['PETG_g'], 'v63_PETG_g': GRAMS['v63']['PETG_g'], 'delta_g': GRAMS['delta_PETG_g'], 'delta_pct': GRAMS['delta_PETG_pct'],
                        'gate_ring_upper_plate_g': GRAMS['gate_ring_upper_plate_g'],
                        'note': 'the gate and ring were not reduced: ring height is set by the Ø28 button window, the blade by the 113 deg stroke and the column load'},
            'p3_head_clearance': {'v62_mm': 0.375, 'v63_to_board_mm': CLR['P3_head_to_board'], 'v63_pocket_wall_radial_mm': P3POCKET_WALL,
                                  'how': 'P3 moved 0.775 mm -X to (17.6, 14.0) (tower pillar and bowl insert follow) + Ø7.5 head pocket in the solid cradle top'},
            'screws_inserts_orings': HW, 'colour_swaps': SWAPS},
        '3_control_panel': PANEL_SPEC,
        '3b_cap_sump_fix': {'v62_defect': 'the +X wet region of the cap (between the D upstand +X wall and the cap skin) is closed off by the D corners below '
                                          'z ~ -91 and has no drain: condensation collects there', 'measured_v62_hole_bounds_z_-95': SUMP62,
                            'v63': 'second labyrinth drain at (44.6, 0) (3 slits, chamber 0.5 under the floor, 4 x Ø0.8 exits out of line of sight), '
                                   'floor = lower of two 1.5 deg cones (one per drain)', 'flood_fill_sump_drains': DRY['sump_drains_to_exterior']},
        '4_firmware_ui_note': UI_NOTE,
        '5_print_orientations_folded_in': {'linguetta_sicura_v63_print': 'on its back (T-foot face down)', 'passacavo_v63_print': 'lip on the bed (as assembled)',
                                           'flangia_piano_v63_print': 'shelf-side face on the bed, dowel hole Ø4.0 x 2.7 (no pin)',
                                           'anello_saracinesca_v63_print': 'on its bottom edge; the window is a 45 deg teardrop (flat top at +15.2): no support',
                                           'saracinesca_v63_print': 'flat, one colour', 'channel parts': 'gone'}},
    'build_order': ['1 latch into the bowl', '2 tower module set on the bowl base', '3 chute: 2 x PT K30x10 from below', '4 shell: 3 x PT K30x12 through the tabs (box not in)',
                    '5 electronics box onto the tower: 3 x M3x40 from below (P2, P3 with an O-ring 3x1 under the head)',
                    '6 cap (panel parts and harness fitted, harness plugged into the board): push on, 3 x PT K30x12 + O-ring 3x1 from below (T10)',
                    '7 rim seal, comb lips, plates, disc from the top',
                    'flange set: ring snapped into the lower plate, dowel pressed in, blade on the dowel, upper plate pressed on (3 pins); on site: cable through the tunnel, '
                    'grommet, tie cinched in the window, 4 wood screws'],
    'kit_split': {'pre_assembled_unit': ['chiocciola_v63 + linguetta + rim seal', 'colonna_v63 drive module', 'scivolo + chute lip', 'scatola_v63 electronics box',
                                         '3 x M3x40', 'guscio + button', 'fondello_v63 with the panel (switch, 2 light pipes, 2 LEDs, speaker, membrane, harness) + 3 x PT K30x12 + O-rings',
                                         'plates, disc, 4 comb lips'],
                  'separate_flange_assembly': ['flangia_piano_v63 + skirt lip + dowel', 'saracinesca_v63', 'anello_saracinesca_v63 (snapped in)', 'flangia_alta_v63 (pressed on, 3 pins)',
                                               'passacavo_v63 (on the supply cable)', 'guarnizione_piano_v5', 'colletto_v6'],
                  'separate': ['supply cable with the M8 female', '1 cable tie 3.6 x 140 UV', '4 x wood screw 5x35', 'drilling template (template_v63)']},
    'shelf': {'underside_z': FL_Z1_62, 'hole_saw_d': 76.0, 'hole_centre_xy': list(v6.HOLE_C), 'wood_screws_xy': [[round(v, 2) for v in polar(WOOD_R62, a)] for a in WOOD_ANG62],
              'flange_outline_r': FL_R62, 'cable_exit': 'rim at 270 deg, z 76.0 (cable centre)', 'unit_height_below_shelf_mm': round(FL_Z1_62 - Z_BOT, 1), 'template': TEMPLATE},
    'changed_parts': {'chiocciola_v63': 'P3 insert moved 0.775 mm -X; chute-ear and shell-tab inserts -> PT pilots Ø2.5 x 7.5',
                      'colonna_v63': 'P3 pillar moved', 'scatola_v63': 'cups -> PT bosses (A, C on corridor columns, B on a -X web), P3 moved + Ø7.5 head pocket',
                      'fondello_v63': 'no thumb-turns; 3 PT counterbores + bosses; control panel (recessed button, 3 FLUSH knock-outs, light pipes square to the face) + dry pocket + speaker cup + grille; second drain; seam spigot joined to the wall (45 deg collar)',
                      'flangia_piano_v63': 'dowel hole with a full wall (opening apex pulled back to r 4.6), pin holes, tunnel raised', 'flangia_alta_v63': 'no channel port, 3 press-fit pins, tie window, bell mouth, tunnel raised',
                      'anello_saracinesca_v63': 'teardrop window', 'saracinesca_v63': 'one colour', 'passacavo_v63': 'follows the raised tunnel',
                      'linguetta_sicura_v63': 'geometry unchanged, print orientation corrected'},
    'reused_unchanged': ['guscio_v611', 'pulsante_v611', 'labbro_ombra_v611', 'scivolo_v611', 'labbro_scivolo_v611', 'disco_v61', 'guarnizione_baionetta_v61',
                         'guarnizione_fondello_v61', 'colletto_v6', 'guarnizione_piano_v5', 'albero_v6', 'mozzo_v6', 'piastra_gate_v62', 'piastra_finestra_v62', 'labbro_pettine_v62'],
    'checks': {'watertight_built': {k: bool(m.is_watertight) for k, m in P.items()}, 'watertight_exported_stl_reload': EXPORT_WT,
               'hard_interference_mm3_max': HARD_MAX, 'hard_pairs_checked': len(inter), 'hard_interference_nonzero': {k: v for k, v in inter.items() if v > 1e-3},
               'stack_screw_vs_drilled_parts_mm3': SCREW_HOLE,
               'designed_contacts_mm3': {k: {'overlap_mm3': v, 'role': SOFT[frozenset(k.split('|'))]} for k, v in soft.items()},
               'seal_continuity': CONT, 'dry_volume_flood_fill': DRY, 'line_of_sight': LOS,
               'bayonet': {'removal_sweep_with_gate_closed_angle_dz_mm3': SWEEP, 'max_mm3': BAY_MAX, 'unit_at_insertion_vs_flange_gate_cable_mm3': BAY_INS,
                           'pressed_button_vs_ring_at_full_stroke_mm3': BTN_THROUGH_WINDOW},
               'gate_sweep_mm3': {'columns': ['g', 'blade|flange', 'ring|flange', 'gate|unit (locked)', 'blade|ring', 'gate|cable+tie'], 'rows': GATE_SWEEP},
               'gate_open_passage': PASSAGE, 'gate_hold': HOLD, 'interlock': {'strict': INTERLOCK_OK, 'button_first_reachable_deg': g_reach_first,
                                                                            'opening_fully_covered_from_deg': g_full, 'probes': [p_[0] for p_ in PROBES], 'table': INTERLOCK},
               'tool_access': SCREW_TABLE, 'clearances_mm': CLR, 'panel_probes': PAW, 'panel_ok': PANEL_OK, 'knock_out_skin_mm': KO_SKIN, 'knock_out_flushness_voids_mm3': KO_FLUSH,
               'knock_out_future_switch_fit': FUTURE_KO, 'drainage': DRAINAGE,
               'print_downfacing_flatter_45_mm2': OVH},
    'load_case': LOAD, 'grams': GRAMS,
    'print': {'chiocciola_v63': 'as v6.2 (flat base on the bed)', 'colonna_v63': 'as v6.2', 'scatola_v63': 'roof on the bed; IP66 settings; the C boss overhangs the '
              'column by 2.5 mm (no support needed)', 'fondello_v63': 'flat bottom on the bed, IP66 settings (100 % infill, 5 walls, flow 1.03); the pocket roof '
              'bridges <= 18 mm between the bosses; the flush knock-out skins (2.0 mm) print solid inside the 5 walls, the 0.3 mm engravings face sideways (no support)',
              'flangia_piano_v63': 'shelf-side face on the bed, then press the dowel in', 'flangia_alta_v63': 'shelf face on the bed (pins grow up)',
              'saracinesca_v63': 'flat, green only - print it on the green plate', 'anello_saracinesca_v63': 'on its bottom edge, no support',
              'passacavo_v63': 'TPU, lip on the bed', 'linguetta_sicura_v63': 'on its back'},
    'open_risks': ['panel switch: the free depth behind the mount wall is 14 mm (servo at 1.7 mm): pick a short-body IP67 type and check its datasheet',
                   f'fox canine on a flush knock-out: punching SF {LOAD["fox_bite_panel"]["SF_plain"]} on the 2.0 mm skin, {LOAD["fox_bite_panel"]["SF_on_the_engraving"]} on the engraved line (250 N assumed)',
                   'a future knock-out switch needs a 12 mm IP67 type with a nut <= 14 AF and <= 14 mm behind the seat; the curved outer face needs '
                   'silicone under the gasket or a printed bezel (drilling recipe in 3_control_panel.knock_outs)',
                   'PT screws in printed PETG: pull-out estimated, not tested; tighten by hand (0.6 N m), at most ~5 re-assemblies per hole',
                   'cap service now needs a T10 driver (was tool-free) and releases the panel harness: unplug before pulling the cap off',
                   'cable proud 0.4 mm of the shelf face: on a very hard shelf the flange may stand 0.4 mm off the wood at the rim until the jacket yields',
                   'A column sits 1.75 mm from the board back: keep the perfboard back free of leads in y 26..34 (as y -5..7 for the C column)',
                   'stack screws: P3 key now OK long key (the A column is near the hand envelope)', 'unit height below the shelf 182.1 (as v6.2)'],
    'files': {k: [f'{k}.stl', f'{k}.3mf', f'{k}_print.stl', f'{k}_print.3mf'] for k in P} |
             {'assembled_position_copies': 'v63_asm/*.stl', 'check': 'check_v63.png', 'viewer': 'v63_viewer.json', 'template': 'template_v63/'}}
_dflt = lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
json.dump(v63doc, open(staged(OUT + 'v63.json'), 'w'), indent=1, default=_dflt)
print('v63.json written')

# ---------------- v63_viewer.json (base: v62_viewer.json, full-resolution files) ----------------
V62V = json.load(open(OUT + 'v62_viewer.json'))
GREEN, ORANGE, BLACK, YELLOW, STEEL = '#2e9d4f', '#f07a1a', '#2a2b2e', '#f2c81e', '#a8adb3'


def _vp(id_, name, file_, color, group, material, qty, bought, explode, rotates=False, opacity=1.0):
    return {'id': id_, 'name': name, 'file': file_, 'color': color, 'opacity': opacity, 'group': group, 'material': material, 'qty': qty,
            'bought': bought, 'explode': explode, 'rotates': rotates}


DROP = {'saracinesca_braccio', 'viti_unione_flangia', 'nottolino_v611_A', 'nottolino_v611_B', 'nottolino_v611_C', 'oring_nottolini', 'chiavette',
        'canalina_base_1', 'canalina_coperchio_1', 'canalina_base_2', 'canalina_coperchio_2', 'canalina_tappo'}
VP = []
for q in V62V['parts']:
    i = q['id']
    if i in DROP:
        continue
    q = dict(q)
    if i == 'guarnizione_piano':
        q.update(file=FILES['gsk_piano'])
    elif i == 'colletto_v6':
        q.update(file=FILES['colletto'])
    elif i == 'flangia_piano_v62':
        q.update(id='flangia_piano_v63', name='Flangia piano inferiore (baionetta, perno spina)', file=FILES['flangia_piano_v63'])
        VP.append(q)
        VP.append(_vp('spina_4x6', 'Spina ISO 2338 4x6 (perno saracinesca)', FILES['dowel_4x6'], STEEL, 'ferramenta', 'acciaio inox A2', 1, True, [0, 0, 145]))
        continue
    elif i == 'saracinesca_lama':
        q.update(id='saracinesca_v63', name='Saracinesca (un colore, aperta)', file=FILES['saracinesca_v63'])
    elif i == 'anello_saracinesca':
        q.update(id='anello_saracinesca_v63', name='Anello saracinesca (finestra a goccia, aperta)', file=FILES['anello_saracinesca_v63'])
    elif i == 'flangia_alta_v62':
        q.update(id='flangia_alta_v63', name='Flangia piano superiore (3 spine, finestra fascetta)', file=FILES['flangia_alta_v63'])
    elif i == 'passacavo_v62':
        q.update(id='passacavo_v63', name='Passacavo nel tunnel della flangia (TPU)', file=FILES['passacavo_v63'])
    elif i == 'viti_legno':
        q.update(file=FILES['wood_5x35'])
    elif i == 'labbri':
        q.update(file=FILES['labbri_x4'])
    elif i == 'chiocciola_v62':
        q.update(id='chiocciola_v63', name='Chiocciola (P3 spostato, fori per viti PT)', file=FILES['chiocciola_v63'])
    elif i == 'inserti_vasca':
        q.update(name='Inserti M3 (vasca, 3)', file=FILES['inserts_bowl'], qty=3)
    elif i == 'viti_guscio':
        q.update(name='Viti PT K30x12 guscio-vasca (3)', file=FILES['pt_k30x12_shell_tabs'])
    elif i == 'viti_scivolo':
        q.update(name='Viti PT K30x10 scivolo (2)', file=FILES['pt_k30x10_chute'])
    elif i == 'viti_m3x40':
        q.update(file=FILES['m3x40_stack'])
    elif i == 'oring_3x1':
        q.update(file=FILES['oring_3x1'])
    elif i == 'colonna_v62':
        q.update(id='colonna_v63', name='Torre a 3 pilastri (P3 spostato)', file=FILES['colonna_v63'])
    elif i == 'scatola_v62':
        q.update(id='scatola_v63', name='Scatola elettronica (bossoli viti fondello)', file=FILES['scatola_v63'])
    elif i == 'sfiato_eptfe':
        q.update(file=FILES['vent_m12_eptfe'])
    elif i == 'cavo_12v_unita':
        q.update(file=FILES['cable_12v_unit'])
    elif i == 'cavo_12v_alimentazione':
        q.update(name='Cavo 12 V nel tunnel, fissato con fascetta', file=FILES['cable_12v_supply'], explode=[0, -40, 175])
    elif i == 'connettore_ip67':
        q.update(file=FILES['connector_m8_ip67'])
    elif i == 'linguetta_sicura':
        q.update(file=FILES['linguetta_sicura_v63'])
    elif i.startswith('fondello_v62_'):
        band = i.replace('fondello_v62_', '')
        q.update(id='fondello_v63_' + band, name=f'Fondello ({band}, pannello comandi)', file=FILES['fondello_v63_' + band])
    VP.append(q)
for nm, lab in zip(PANEL_PIECES, ['LED', 'pulsante + predisposizione 1', 'predisposizione 2', 'predisposizione 3', 'estremo ovest']):
    VP.append(_vp(nm, f'Fondello (pannello comandi: {lab})', FILES[nm], BLACK, 'struttura', 'PETG nero', 1, False, [0, 0, -240]))
EXC = [0, 0, -240]
for k, nm, col, grp, mat, qty, ex in (
        ('switch_12mm_ip67', 'Pulsante pannello IP67 Ø12', '#c9ccd1', 'elettronica', 'acciaio / IP67', 1, [16, 40, -240]),
        ('lightpipes_5mm', 'Guide luce Ø5 (2)', '#e8f4ff', 'elettronica', 'PC trasparente', 2, [12, 34, -240]),
        ('oring_5x1_lightpipe', 'O-ring guide luce 5x1 (2)', '#1e1e1e', 'guarnizioni', 'NBR70', 2, [10, 28, -240]),
        ('leds_3mm', 'LED 3 mm (stato, Wi-Fi)', '#3fd16b', 'elettronica', 'acquistato', 2, [8, 20, -240]),
        ('speaker_20mm', 'Altoparlante Ø20 (miagolio)', '#444b55', 'elettronica', 'acquistato', 1, [0, 10, -205]),
        ('membrane_acoustic_ip67', 'Membrana acustica IP67 ePTFE', '#f5f5f5', 'elettronica', 'ePTFE', 1, [0, 10, -222]),
        ('harness_jst', 'Cablaggio pannello JST-XH 8 poli', '#b03a2e', 'elettronica', 'acquistato', 1, [6, 10, -195]),
        ('pt_k30x12_cap', 'Viti PT K30x12 fondello (3)', STEEL, 'ferramenta', 'acciaio inox A2', 3, [0, 0, -275]),
        ('oring_3x1_cap', 'O-ring 3x1 sotto le viti del fondello (3)', '#1e1e1e', 'guarnizioni', 'NBR70', 3, [0, 0, -262]),
        ('cable_tie', 'Fascetta antistrappo (UV)', '#111111', 'ferramenta', 'PA66 UV', 1, [0, -40, 175])):
    VP.append(_vp(k, nm, FILES[k], col, grp, mat, qty, True, ex))
viewer = {k: v for k, v in V62V.items() if k not in ('parts', 'scene', 'title', 'subtitle')}
viewer['title'] = 'Kibble Dispenser Outdoor v6.3'
viewer['subtitle'] = 'pannello comandi nel fondello, niente canalina, meno pezzi'
viewer['parts'] = VP
viewer['scene'] = {k: v for k, v in V62V['scene'].items() if k != 'cable_channel'}
viewer['scene']['cable_route'] = {'exit_xyz': [0.0, -FL_R62, TUN63['zh']], 'note': 'rim exit at the back; the user clips the cable along the shelf'}
json.dump(viewer, open(staged(OUT + 'v63_viewer.json'), 'w'), indent=1)
vclosed = json.loads(json.dumps(viewer))
for q in vclosed['parts']:
    if q['id'] == 'saracinesca_v63':
        q.update(file=FILES['saracinesca_closed'], name='Saracinesca (chiusa)')
    if q['id'] == 'anello_saracinesca_v63':
        q.update(file=FILES['anello_closed'], name='Anello saracinesca (chiuso)')
vclosed['subtitle'] = 'saracinesca CHIUSA: la finestra scopre il pulsante'
json.dump(vclosed, open(SCRATCH + 'v63_viewer_closed.json', 'w'), indent=1)
missing = [q['file'] for q in VP if not os.path.exists(current(q['file']))]
print('v63_viewer.json written:', len(VP), 'entries; missing files:', missing)
commit_staged()                                              # all outputs of this run replace the old ones together
print(f'checks done in {time.time() - t_start:.0f} s')
