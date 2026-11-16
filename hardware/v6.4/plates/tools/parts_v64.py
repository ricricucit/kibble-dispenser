"""Printed parts of Kibble Dispenser Outdoor hardware 6.4.0: sources, colours, quantities and slicer settings.

Two products: 'chassis' (mechanics + electronics-case holder, 6.x) and 'module' (detachable electronics module, case 1.0).
Every part carries a status: 'unchanged' (file byte-identical to 6.3.0, same settings as print_v63), 'changed' (6.4 chassis
part that replaces a 6.3 part) or 'new' (module part).
All meshes are returned in print orientation (Z-up, bottom at z=0), in mm.
Source of truth: hardware/v6.4/cad/build/v64.json (parts, print notes, review_2026_11_15) and
docs/reviews/2026-11-15-v6.4-print-review/REVIEW.md.
"""
import os
import numpy as np
import trimesh
import manifold3d as mf

PARTS_DIR = os.environ.get('KD_V64_BUILD', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cad', 'build'))

PETG_SLOTS = {'black': 1, 'orange': 2, 'green': 3}
PETG_FILAMENTS = [
    {'slot': 1, 'colour': 'black', 'type': 'PETG', 'hex': '#1A1A1A', 'role': 'structure'},
    {'slot': 2, 'colour': 'orange', 'type': 'PETG', 'hex': '#F07A1A', 'role': 'touch points / act here'},
    {'slot': 3, 'colour': 'green', 'type': 'PETG', 'hex': '#2E9D4F', 'role': 'food path'},
]
TPU_FILAMENTS = [{'slot': 'external spool', 'colour': 'yellow', 'type': 'TPU', 'hex': '#F2C81E', 'role': 'seals / soft parts'}]
DENSITY = {'PETG': 1.27, 'TPU': 1.24}

S_STRUCT = {'wall_loops': '3', 'sparse_infill_density': '15%'}
S_SOLID = {'wall_loops': '4', 'sparse_infill_density': '100%'}
S_TPU = {'wall_loops': '2', 'sparse_infill_density': '100%'}
S_TPU_LIP = {'wall_loops': '2', 'sparse_infill_density': '100%', 'wall_generator': 'arachne',
             'outer_wall_speed': '15', 'inner_wall_speed': '15'}
S_IP66 = {'wall_loops': '5', 'inner_wall_line_width': '0.42', 'outer_wall_line_width': '0.42', 'sparse_infill_density': '100%',
          'top_shell_layers': '5', 'bottom_shell_layers': '5', 'seam_position': 'back', 'print_flow_ratio': '1.03'}
SUP_BED = {'enable_support': '1', 'support_type': 'tree(auto)', 'support_on_build_plate_only': '1'}
SUP_BED_SNUG = {'enable_support': '1', 'support_type': 'normal(auto)', 'support_on_build_plate_only': '1'}
# shell tabs (review M2): tree supports from the build plate only, 45 deg, and only where the support enforcers are
SUP_TABS = {'enable_support': '1', 'support_type': 'tree(manual)', 'support_on_build_plate_only': '1', 'support_threshold_angle': '45'}
EFC = {'elefant_foot_compensation': '0.15'}      # both parts of the 0.35 mm bottom seam (review m9)
# module tub, final 6.4.0 CAD: the boss corbels are fine, but the two upper corners of the d17 button recess, where its rim meets
# the leaning outer skin (assembly (57.1, 12.2, -82.5) and (53.1, 26.3, -82.4)), start as free slivers at print z 21.5
# (slicer: "floating regions"); normal supports only under the support enforcers placed automatically on those starts
SUP_TIPS = {'enable_support': '1', 'support_type': 'normal(manual)', 'support_on_build_plate_only': '0', 'support_threshold_angle': '45'}


def P(pid, label, material, qty, bodies, settings, note, reorient=None, source='v64.json', kind='part', module=None,
      rot=None, product='chassis', status='unchanged'):
    return dict(id=pid, label=label, material=material, qty=qty, bodies=bodies, settings=settings, note=note,
                reorient=reorient, source=source, kind=kind, module=module, modifiers=[], rot=rot, product=product, status=status)


PARTS = [
    # ================= CHASSIS, changed in 6.4 =================
    P('guscio_v64', 'Pod shell (module opening, return ribs)', 'PETG', 1, [('black', 'guscio_v64_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '6', **SUP_TABS},
      'top edge (z +64) on the bed, opening upward; 5 walls; 6 mm brim; tree supports from the build plate only (45 deg) under the '
      'inner 12 mm of the 3 bowl tabs, placed by 3 support enforcers (manual mode: nothing else gets support)',
      reorient='shell_tabs', status='changed'),
    P('scatola_v64', 'Servo bay + module holder posts', 'PETG', 1, [('black', 'scatola_v64_print.stl')],
      {**S_IP66, 'ironing_type': 'top'},
      'roof on the bed; IP66 settings; NO supports (posts, webs, bosses, the harness tie lug and the C-hook on the south post start '
      'on the bed); rim face ironed (the cap lip seals on it)',
      module='servo bay', status='changed'),
    P('fondello_v64', 'Pod cap (module opening, 4 PT screws)', 'PETG', 1, [('black', 'fondello_v64_print.stl')],
      {**S_IP66, **EFC},
      'flat bottom on the bed; IP66 settings; NO supports (45 deg chamfer under the bottom radius); elephant-foot compensation 0.15; '
      'the 2 drain holes are d1.5: check they are open', status='changed'),
    P('guarnizione_fondello_v64', 'Cap lip seal (smaller bay outline)', 'TPU', 1, [('yellow', 'guarnizione_fondello_v64_print.stl')],
      {**S_TPU, 'outer_wall_speed': '20', 'inner_wall_speed': '20'}, 'base on the bed, lip up (6.1 lip settings)', status='changed'),
    # ================= CHASSIS, unchanged since 6.3.0 (same files, same settings as print_v63) =================
    P('chiocciola_v63', 'Bowl (PT pilots, P3 insert moved)', 'PETG', 1, [('black', 'chiocciola_v63_print.stl')],
      {**S_STRUCT, **SUP_BED}, 'flat base on the bed; supports on build plate only (3 bayonet lugs)', source='6.3.0 (unchanged)'),
    P('flangia_piano_v63', 'Lower flange plate (dowel hole)', 'PETG', 1, [('black', 'flangia_piano_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'},
      'shelf-side face on the bed (d4.0 x 2.7 dowel hole); press the 4 x 6 dowel in after printing; no supports', source='6.3.0 (unchanged)'),
    P('flangia_alta_v63', 'Upper flange plate (3 press-fit pins, tie window)', 'PETG', 1, [('black', 'flangia_alta_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'}, 'shelf face on the bed, the 3 press-fit pins grow up; no supports',
      source='6.3.0 (unchanged)'),
    P('colonna_v63', 'Tower (3 pillars)', 'PETG', 1, [('black', 'colonna_v63_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '100%'},
      'upright, flange on the bed; 100 % infill (the pillars carry the M3x40 preload)', source='6.3.0 (unchanged)', module='drive tower'),
    P('albero_v6', 'Shaft', 'PETG', 1, [('black', 'albero_v6_print.stl')],
      {**S_SOLID, 'layer_height': '0.15', 'brim_type': 'outer_only', 'brim_width': '5'},
      'bottom hex on the bed; 100 % infill; 0.15 mm layers; 5 mm brim', source='6.3.0 (unchanged)', module='drive tower'),
    P('mozzo_v6', 'Servo hub', 'PETG', 1, [('black', 'mozzo_v6_print.stl')],
      dict(S_SOLID), 'spline socket on the bed (print test_scanalato first); 100 % infill', source='6.3.0 (unchanged)',
      module='servo bay (hub on the servo)'),
    P('piastra_gate_v62', 'Gate plate', 'PETG', 1, [('black', 'piastra_gate_v62_print_black.stl'), ('green', 'piastra_gate_v62_print_green.stl')],
      dict(S_STRUCT), 'bottom face on the bed; green OUT band in the top 3 layers', source='6.3.0 (unchanged)'),
    P('piastra_finestra_v62', 'Window plate', 'PETG', 1, [('black', 'piastra_finestra_v62_print_black.stl'), ('green', 'piastra_finestra_v62_print_green.stl')],
      dict(S_STRUCT), 'flipped: green FOOD IN band in the first 3 layers', source='6.3.0 (unchanged)'),
    P('saracinesca_v63', 'Gate blade (one colour)', 'PETG', 1, [('green', 'saracinesca_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '100%'}, 'flat on the bed, green only; 100 % infill (3 mm blade)', source='6.3.0 (unchanged)'),
    P('scivolo_v611', 'Chute', 'PETG', 1, [('green', 'scivolo_v611_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%'}, 'joint flange on the bed; no supports', source='6.3.0 (unchanged)'),
    P('colletto_v6', 'Funnel collar', 'PETG', 1, [('green', 'colletto_v6_print.stl')],
      dict(S_STRUCT), 'flipped, top rim on the bed; no supports', source='6.3.0 (unchanged)'),
    P('disco_v61', 'Dosing disc (self-cleaning)', 'PETG', 1, [('orange', 'disco_v61_print_orange_v611.stl'), ('black', 'disco_v61_print_black_v611.stl')],
      dict(S_STRUCT), 'flipped, disc top on the bed; black label in the first 3 layers; no supports', source='6.3.0 (unchanged)'),
    P('anello_saracinesca_v63', 'Interlock ring (teardrop window)', 'PETG', 1, [('orange', 'anello_saracinesca_v63_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '5'},
      'on its bottom edge; the window is a 45 deg teardrop: no support; 5 mm outer brim', source='6.3.0 (unchanged)'),
    P('linguetta_sicura_v63', 'Safety latch', 'PETG', 1, [('orange', 'linguetta_sicura_v63_print.stl')],
      {**S_SOLID, **SUP_BED_SNUG}, 'on its back; 100 % infill; small bed-only support under the spring tab', source='6.3.0 (unchanged)'),
    P('pulsante_v611', 'Latch push-button', 'PETG', 1, [('orange', 'pulsante_v611_print.stl')],
      dict(S_SOLID), 'standing on its head face; 100 % infill', source='6.3.0 (unchanged)'),
    P('labbro_pettine_v62', 'Comb lip (common, x4)', 'TPU', 4, [('yellow', 'labbro_pettine_v62_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed; Arachne, 15 mm/s; print 4', source='6.3.0 (unchanged)'),
    P('guarnizione_baionetta_v61', 'Rim lip seal', 'TPU', 1, [('yellow', 'guarnizione_baionetta_v61_print.stl')],
      dict(S_TPU_LIP), 'foot on the bed, 0.5 mm flap; Arachne, 15 mm/s', source='6.3.0 (unchanged)'),
    P('guarnizione_piano_v5', 'Flange-shelf gasket ring', 'TPU', 1, [('yellow', 'guarnizione_piano_v5_print.stl')],
      dict(S_TPU), 'flat ring', source='6.3.0 (unchanged)'),
    P('labbro_ombra_v611', 'Skirt lip ring', 'TPU', 1, [('yellow', 'labbro_ombra_v611_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed, 0.5 mm flap as a 20 deg cone; Arachne, 15 mm/s', source='6.3.0 (unchanged)'),
    P('labbro_scivolo_v611', 'Chute lip ring', 'TPU', 1, [('yellow', 'labbro_scivolo_v611_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed, 0.6 mm flap up; Arachne', source='6.3.0 (unchanged)'),
    P('passacavo_v63', 'Cable tunnel grommet (raised tunnel)', 'TPU', 1, [('yellow', 'passacavo_v63_print.stl')],
      dict(S_TPU), 'lip on the bed', source='6.3.0 (unchanged)'),
    # ================= MODULE, case 1.0 (new) =================
    P('modulo_vasca_v64', 'Module tub (outer skin, control panel, board slots)', 'PETG', 1, [('black', 'modulo_vasca_v64_print.stl')],
      {**S_IP66, **EFC, **SUP_TIPS},
      'standing as assembled (flat bottom on the bed); IP66 settings; elephant-foot compensation 0.15; bottom edge, rim and the 5 '
      'lid-screw bosses need no support (45 deg faces since 6.4.0); two thin support columns from the bed, outside the tub, under the '
      'two upper corners of the button recess (print z 21.5), placed by support enforcers; 2 mouse ears (d16 x 0.2) on the back corners against lifting of the 2 mm back '
      'wall: cut them off',
      reorient='tub_ears', product='module', status='new'),
    P('modulo_coperchio_v64', 'Module lid (J1 turret, gasket groove)', 'PETG', 1, [('black', 'modulo_coperchio_v64_print.stl')],
      dict(S_IP66),
      'underside on the bed, turret up; IP66 settings; NO supports; the J1 hole is closed by a 0.2 mm skin (one layer, 13 mm bridge): '
      'drill it d8.2 afterwards (or the thread size of the bought socket); the back fence on the top guides the harness loop', product='module', status='new'),
    P('modulo_anello_speaker_v64', 'Speaker ring (for a d23 speaker)', 'PETG', 1, [('black', 'modulo_anello_speaker_v64_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '100%'},
      'flat; any colour (it sits inside the sealed module; the viewer shows it orange)', product='module', status='new'),
    P('modulo_guarnizione_v64', 'Module lid lip gasket', 'TPU', 1, [('yellow', 'modulo_guarnizione_v64_print.stl')],
      dict(S_TPU_LIP), 'base on the bed, lip up; Arachne walls, 15 mm/s (the thin lip prints as one line)', product='module', status='new'),
    # ================= test pieces =================
    P('test_scanalato', 'Spline fit test (3 coupons)', 'PETG', 1, [('black', 'test_scanalato_print.stl')],
      dict(S_SOLID), 'socket on the bed; 1/2/3 notches = 0.05/0.10/0.20 mm radial clearance; mozzo_v6 is built with 0.10',
      source='drivetrain.json', kind='test'),
    P('test_groove_rim', 'Bowl rim groove coupon (30 mm cut of chiocciola_v63)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '15%'}, 'rim with the 3.0 x 2.2 lip-seal groove; cut face on the bed',
      reorient='cut_rim', source='cut from chiocciola_v63.stl', kind='test'),
    P('test_groove_cap', 'Cap upstand groove coupon (20 mm cut of fondello_v64)', 'PETG', 1, [('black', None)],
      dict(S_IP66), 'straight side of the cap upstand with the 2.2 x 1.15 retaining groove (same section as the 6.3 coupon); cut face on the bed',
      reorient='cut_cap', source='cut from fondello_v64.stl', kind='test'),
    P('test_groove_skirt', 'Flange skirt groove coupon (30 mm cut of flangia_piano_v63)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '25%'}, 'plate edge with the skirt-lip groove (groove up); shelf face on the bed',
      reorient='cut_skirt', source='cut from flangia_piano_v63.stl', kind='test'),
    P('test_rim_lip', 'TPU rim lip seal test arc (30 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU_LIP), 'same cut box as test_groove_rim; foot on the bed', reorient='cut_rim_lip', source='cut from guarnizione_baionetta_v61.stl', kind='test'),
    P('test_cap_lip', 'TPU cap lip seal test strip (20 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU), 'same cut box as test_groove_cap; base on the bed', reorient='cut_cap_lip', source='cut from guarnizione_fondello_v64.stl', kind='test'),
    P('test_skirt_lip', 'TPU skirt lip test arc (30 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU_LIP), 'same cut box as test_groove_skirt; anchor on the bed', reorient='cut_skirt_lip', source='cut from labbro_ombra_v611.stl', kind='test'),
    P('test_comb_lip', 'TPU comb lip test (spare labbro_pettine_v62)', 'TPU', 1, [('yellow', 'labbro_pettine_v62_print.stl')],
      dict(S_TPU_LIP), 'one spare comb lip: check the slits and the flap', source='labbro_pettine_v62_print.stl', kind='test'),
]
PART = {p['id']: p for p in PARTS}
SKIRT_CUT = (72.0, 92.0)   # radial cut range for the skirt groove coupon at 0 deg
LIP_DZ = 8.0               # the flange + gate stack is 8 mm higher than v6.1.1 (lip asm copy is at the v6.1.1 height)
CAP_DX = -24.75            # the straight side of the cap upstand moved from x 40.6 (6.3) to x 15.85 (6.4)
ALIAS = {}


def resolve(pid):
    return ALIAS.get(pid, pid)


def _to_manifold(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def _from_manifold(M):
    out = M.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=True)


def _manifold_clean(m, drop_fins=False):
    """Manifold round trip (as print_v63). drop_fins also removes zero-volume bodies (4-face fins left by the CAD export);
    it is used for the 6.4 parts only, so the unchanged parts stay exactly as in print_v63."""
    M = _to_manifold(m)
    if M.status() != mf.Error.NoError or M.is_empty():
        return m
    if drop_fins:
        comps = M.decompose()
        if len(comps) > 1:
            keep = [c for c in comps if abs(c.volume()) > 1e-3]
            if keep and len(keep) < len(comps):
                M = mf.Manifold.compose(keep)
    return _from_manifold(M)


def _box_cut(m, x0, x1, y0, y1, z0=-500.0, z1=500.0):
    box = mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
    return _from_manifold(_to_manifold(m) ^ box)


def load_bodies(pid):
    """[(colour, trimesh)] in print orientation, z=0 on the bed, cleaned. Colour bodies keep their common frame."""
    p = PART[pid]
    r = p['reorient']
    L = lambda f: trimesh.load(os.path.join(PARTS_DIR, f))
    FX = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    if r == 'cut_rim':
        out = [('black', _box_cut(L('chiocciola_v63.stl'), 45, 75, -15, 15, 56, 80))]
    elif r == 'cut_rim_lip':
        out = [('yellow', _box_cut(L('guarnizione_baionetta_v61.stl'), 45, 75, -15, 15, 56, 80))]
    elif r == 'cut_cap':
        out = [('black', _box_cut(L('fondello_v64.stl'), 35 + CAP_DX, 44 + CAP_DX, 14, 34, -84, -60))]
    elif r == 'cut_cap_lip':
        out = [('yellow', _box_cut(L('guarnizione_fondello_v64.stl'), 32 + CAP_DX, 50 + CAP_DX, 14, 34, -90, -60))]
    elif r == 'cut_skirt':
        c = _box_cut(L('flangia_piano_v63.stl'), SKIRT_CUT[0], SKIRT_CUT[1], -15, 15, 40, 100)
        c.apply_transform(FX)
        out = [('black', c)]
    elif r == 'cut_skirt_lip':
        lip = L('labbro_ombra_v611.stl')
        lip.apply_translation([0, 0, LIP_DZ])
        c = _box_cut(lip, SKIRT_CUT[0], SKIRT_CUT[1], -15, 15, 40, 100)
        c.apply_transform(FX)
        out = [('yellow', c)]
    else:
        out = [(c, trimesh.load(os.path.join(PARTS_DIR, f))) for c, f in p['bodies']]
    fins = p['status'] != 'unchanged' and p['kind'] == 'part'
    out = [(c, _manifold_clean(m, drop_fins=fins)) for c, m in out]
    zmin = min(m.bounds[0, 2] for _, m in out)
    for _, m in out:
        m.apply_translation([0, 0, -zmin])
    return out


# ---------------------------------------------------------------------------------------------------------------
# helper volumes
# ---------------------------------------------------------------------------------------------------------------
def shell_tab_clusters(m, z_tab=64.0):
    """Flat down-facing faces of the 3 bowl tabs of the shell in print orientation (print z 64 = assembly z 0).
    Returns (axis_xy, [dict(angle_deg, r0, r1, half_width, area)])."""
    fn, fc, ar = m.face_normals, m.triangles_center, m.area_faces
    sel = (fn[:, 2] < -0.99) & (np.abs(fc[:, 2] - z_tab) < 0.3)
    axis = np.array([(m.bounds[0, 0] + m.bounds[1, 0]) / 2, (m.bounds[0, 1] + m.bounds[1, 1]) / 2])
    tri = m.triangles[sel][:, :, :2].reshape(-1, 2) - axis
    ang = np.degrees(np.arctan2(tri[:, 1], tri[:, 0]))
    area = np.repeat(ar[sel] / 3.0, 3)
    out = []
    order = np.argsort(ang)
    ang_s = ang[order]
    gaps = np.nonzero(np.diff(ang_s) > 40.0)[0]
    groups = np.split(order, gaps + 1)
    if len(groups) > 1 and (ang_s[0] + 360.0 - ang_s[-1]) < 40.0:       # cluster wrapped at +-180
        groups[0] = np.concatenate([groups[-1], groups[0]])
        groups = groups[:-1]
    for g in groups:
        a0 = np.degrees(np.arctan2(np.sin(np.radians(ang[g])).mean(), np.cos(np.radians(ang[g])).mean()))
        u = np.array([np.cos(np.radians(a0)), np.sin(np.radians(a0))])
        v = np.array([-u[1], u[0]])
        rr, tt = tri[g] @ u, tri[g] @ v
        out.append(dict(angle_deg=float(a0), r0=float(rr.min()), r1=float(rr.max()), half_width=float(np.abs(tt).max()),
                        area=float(area[g].sum())))
    return axis, out


def floating_starts(m, z0, z1, lh=0.2, min_area=0.001):
    """Regions that start in mid-air between print z0 and z1: islands of a slicing layer that do not touch the layer below.
    Returns [(x, y, z_start)] in the frame of m, one per start (repeats within 1 mm merged)."""
    from shapely.ops import unary_union
    from shapely import affinity

    def polys(z):
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None:
            return None
        p2, T = s.to_2D()
        pg = [q for q in p2.polygons_full if q is not None and q.area > 1e-5]
        if not pg:
            return None
        return affinity.affine_transform(unary_union(pg), [T[0, 0], T[0, 1], T[1, 0], T[1, 1], T[0, 3], T[1, 3]])
    out, prev = [], None
    for i in range(max(1, int(round(z0 / lh))), int(round(z1 / lh))):
        z = (i + 0.5) * lh
        cur = polys(z)
        if cur is not None and prev is not None:
            for g in ([cur] if cur.geom_type == 'Polygon' else cur.geoms):
                if g.area > min_area and g.intersection(prev).area < 1e-4:
                    c = g.centroid
                    if not any(abs(c.x - x) < 1.0 and abs(c.y - y) < 1.0 and abs(i * lh - zz) < 1.0 for x, y, zz in out):
                        out.append((float(c.x), float(c.y), float(i * lh)))
        prev = cur
    return out


_TIPS_CACHE = {}
TUB_TIP_ZONE = (15.0, 30.0)      # print z band of the panel-opening crowns (the 0.1 mm2 knock-out slivers at z 10 do not trigger)


def load_modifiers(pid, bodies):
    """Helper volumes in the frame of load_bodies(pid): list of dict(name, mesh, settings, subtype).
    subtype 'support_enforcer' = slicer support enforcer; 'normal_part' = extra printed volume of the same object (mouse ear).
    6.4.0 final CAD: the tub bosses grow from the wall on 45 deg corbels, so the tub has no support enforcers any more."""
    r = PART[pid]['reorient']
    if r == 'shell_tabs':
        m = bodies[0][1]
        axis, tabs = shell_tab_clusters(m)
        mods = []
        for i, t in enumerate(sorted(tabs, key=lambda t: t['angle_deg'])):
            # box over the flat underside of the tab (inner part, r0..r1) with 1.5 mm margin, 3 mm tall around print z 64
            lr, lt = (t['r1'] - t['r0']) + 3.0, 2 * t['half_width'] + 3.0
            box = trimesh.creation.box(extents=[lr, lt, 3.0])
            box.apply_translation([(t['r0'] + t['r1']) / 2, 0.0, 64.0])
            box.apply_transform(trimesh.transformations.rotation_matrix(np.radians(t['angle_deg']), [0, 0, 1]))
            box.apply_translation([axis[0], axis[1], 0.0])
            mods.append(dict(name=f'guscio_v64_tab_{i + 1}_support_enforcer', mesh=box, settings={}, subtype='support_enforcer'))
        return mods
    if r == 'tub_ears':
        m = bodies[0][1]
        x_back = m.bounds[0, 0]                                   # back wall (assembly x 17.4) is the -x side of the print file
        mods = []
        for i, y in enumerate((m.bounds[0, 1], m.bounds[1, 1])):
            ear = trimesh.creation.cylinder(radius=8.0, height=0.2, sections=48)
            ear.apply_translation([x_back + 1.0, y - np.sign(y) * 1.0, 0.1])
            mods.append(dict(name=f'modulo_vasca_v64_mouse_ear_{i + 1}', mesh=ear, settings={}, subtype='normal_part'))
        key = (pid, round(float(m.bounds[0, 0]), 3), round(float(m.bounds[0, 1]), 3))
        if key not in _TIPS_CACHE:
            _TIPS_CACHE[key] = floating_starts(m, *TUB_TIP_ZONE)
        for i, (x, y, z) in enumerate(sorted(_TIPS_CACHE[key], key=lambda t: (t[1], t[0]))):
            # 4 x 4 mm box from 0.6 mm below the start to 2.6 mm above it (the sliver joins the wall about 2.5 mm higher)
            box = trimesh.creation.box(extents=[4.0, 4.0, 3.2])
            box.apply_translation([x, y, z + 1.0])
            mods.append(dict(name=f'modulo_vasca_v64_crown_{i + 1}_support_enforcer', mesh=box, settings={}, subtype='support_enforcer'))
        return mods
    return []
