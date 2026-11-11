"""Printed parts of Kibble Dispenser Outdoor v6.3: sources, colours, quantities and slicer settings.

All meshes are returned in print orientation (Z-up, bottom at z=0), in mm.
Source of truth: v63.json in the CAD build folder (hardware/v6.3/cad/build/, written by build_v63.py) (changed_parts, reused_unchanged, print notes). Cable channel and
thumb-turns are gone. The v6.3 CAD print files carry the corrected orientations (lower flange with the dowel hole and no
pin, latch on its back, grommet lip down, one-colour blade, teardrop ring window); each was verified here by overhang
area and footprint before use, so no part is re-oriented or patched in this package.
"""
import os
import numpy as np
import trimesh
import manifold3d as mf

# CAD build output of hardware/v6.3/cad/build_v63.py (gitignored): *_print.stl, v6x.json, v63_viewer.json, v6x_asm/
PARTS_DIR = os.environ.get('KD_V63_BUILD', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cad', 'build'))

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



def P(pid, label, material, qty, bodies, settings, note, reorient=None, source='v63.json', kind='part', module=None, modifiers=None, rot=None):
    return dict(id=pid, label=label, material=material, qty=qty, bodies=bodies, settings=settings, note=note,
                reorient=reorient, source=source, kind=kind, module=module, modifiers=modifiers or [], rot=rot)


PARTS = [
    # ---------------- PETG black ----------------
    P('guscio_v611', 'Pod shell', 'PETG', 1, [('black', 'guscio_v611_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '6'},
      'as v6.1.1: seam edge on the bed, rim up; 5 walls; no supports; 6 mm brim', source='v6.1.1 (reused)'),
    P('fondello_v63', 'Pod cap (control panel, PT screw bosses)', 'PETG', 1, [('black', 'fondello_v63_print.stl')],
      {**S_IP66, **SUP_BED_SNUG, 'support_threshold_angle': '45'},
      'flat bottom on the bed; IP66 settings (knock-out skins print solid); bed-only support ring under the R15 bottom edge only '
      '(the pocket roof bridges <= 18 mm, the button bore and engravings need none); clear the drain holes (d0.8) with a drill'),
    P('chiocciola_v63', 'Bowl (PT pilots, P3 insert moved)', 'PETG', 1, [('black', 'chiocciola_v63_print.stl')],
      {**S_STRUCT, **SUP_BED}, 'as v6.2: flat base on the bed; supports on build plate only (3 bayonet lugs)'),
    P('flangia_piano_v63', 'Lower flange plate (dowel hole)', 'PETG', 1, [('black', 'flangia_piano_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'},
      'shelf-side face on the bed (CAD: no pin, d4.0 x 2.7 dowel hole); press the 4 x 6 dowel in after printing; no supports'),
    P('flangia_alta_v63', 'Upper flange plate (3 press-fit pins, tie window)', 'PETG', 1, [('black', 'flangia_alta_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'}, 'shelf face on the bed, the 3 press-fit pins grow up; no supports'),
    P('colonna_v63', 'Tower (3 pillars, P3 moved)', 'PETG', 1, [('black', 'colonna_v63_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '100%'},
      'as v6.2: upright, flange on the bed; 100 % infill (the pillars carry the M3x40 preload)', module='drive tower'),
    P('albero_v6', 'Shaft', 'PETG', 1, [('black', 'albero_v6_print.stl')],
      {**S_SOLID, 'layer_height': '0.15', 'brim_type': 'outer_only', 'brim_width': '5'},
      'bottom hex on the bed; 100 % infill; 0.15 mm layers; 5 mm brim', source='v6 (reused)', module='drive tower'),
    P('mozzo_v6', 'Servo hub', 'PETG', 1, [('black', 'mozzo_v6_print.stl')],
      dict(S_SOLID), 'spline socket on the bed (print test_scanalato first); 100 % infill', source='v6 (reused)',
      module='electronics box (hub on the servo)'),
    P('scatola_v63', 'Electronics box (PT bosses)', 'PETG', 1, [('black', 'scatola_v63_print.stl')],
      {**S_IP66, 'ironing_type': 'top'},
      'roof on the bed; IP66 settings; the C boss overhangs its column by 2.5 mm: no support at all', module='electronics box'),
    # ---------------- PETG green (food path + gate) ----------------
    P('piastra_gate_v62', 'Gate plate', 'PETG', 1, [('black', 'piastra_gate_v62_print_black.stl'), ('green', 'piastra_gate_v62_print_green.stl')],
      dict(S_STRUCT), 'as v6.1: bottom face on the bed; green OUT band in the top 3 layers', source='v6.2 (reused)'),
    P('piastra_finestra_v62', 'Window plate', 'PETG', 1, [('black', 'piastra_finestra_v62_print_black.stl'), ('green', 'piastra_finestra_v62_print_green.stl')],
      dict(S_STRUCT), 'as v6.1 (flipped): green FOOD IN band in the first 3 layers', source='v6.2 (reused)'),
    P('saracinesca_v63', 'Gate blade (one colour)', 'PETG', 1, [('green', 'saracinesca_v63_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '100%'}, 'flat on the bed, green only; 100 % infill (3 mm blade)'),
    P('scivolo_v611', 'Chute', 'PETG', 1, [('green', 'scivolo_v611_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%'}, 'as v6.1.1: joint flange on the bed; no supports', source='v6.1.1 (reused)'),
    P('colletto_v6', 'Funnel collar', 'PETG', 1, [('green', 'colletto_v6_print.stl')],
      dict(S_STRUCT), 'flipped, top rim on the bed; no supports', source='v6 (reused)'),
    # ---------------- PETG orange ----------------
    P('disco_v61', 'Dosing disc (self-cleaning)', 'PETG', 1, [('orange', 'disco_v61_print_orange_v611.stl'), ('black', 'disco_v61_print_black_v611.stl')],
      dict(S_STRUCT), 'flipped, disc top on the bed; black label in the first 3 layers; no supports', source='v6.1 (reused, v6.1.1 colour bodies)'),
    P('anello_saracinesca_v63', 'Interlock ring (teardrop window)', 'PETG', 1, [('orange', 'anello_saracinesca_v63_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '5'},
      'on its bottom edge; the window is a 45 deg teardrop: no support; 5 mm outer brim'),
    P('linguetta_sicura_v63', 'Safety latch', 'PETG', 1, [('orange', 'linguetta_sicura_v63_print.stl')],
      {**S_SOLID, **SUP_BED_SNUG}, 'on its back (CAD print file now matches the note); 100 % infill; small bed-only support under the spring tab'),
    P('pulsante_v611', 'Latch push-button', 'PETG', 1, [('orange', 'pulsante_v611_print.stl')],
      dict(S_SOLID), 'as v6.1.1: standing on its head face; 100 % infill', source='v6.1.1 (reused)'),
    # ---------------- TPU 95A ----------------
    P('labbro_pettine_v62', 'Comb lip (common, x4)', 'TPU', 4, [('yellow', 'labbro_pettine_v62_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed; Arachne, 15 mm/s; print 4', source='v6.2 (reused)'),
    P('guarnizione_baionetta_v61', 'Rim lip seal', 'TPU', 1, [('yellow', 'guarnizione_baionetta_v61_print.stl')],
      dict(S_TPU_LIP), 'foot on the bed, 0.5 mm flap; Arachne, 15 mm/s', source='v6.1 (reused)'),
    P('guarnizione_fondello_v61', 'Cap lip seal (D outline)', 'TPU', 1, [('yellow', 'guarnizione_fondello_v61_print.stl')],
      {**S_TPU, 'outer_wall_speed': '20', 'inner_wall_speed': '20'}, 'base on the bed, lip up', source='v6.1 (reused)'),
    P('guarnizione_piano_v5', 'Flange-shelf gasket ring', 'TPU', 1, [('yellow', 'guarnizione_piano_v5_print.stl')],
      dict(S_TPU), 'flat ring', source='v5 (reused)'),
    P('labbro_ombra_v611', 'Skirt lip ring', 'TPU', 1, [('yellow', 'labbro_ombra_v611_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed, 0.5 mm flap as a 20 deg cone; Arachne, 15 mm/s', source='v6.1.1 (reused)'),
    P('labbro_scivolo_v611', 'Chute lip ring', 'TPU', 1, [('yellow', 'labbro_scivolo_v611_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed, 0.6 mm flap up; Arachne', source='v6.1.1 (reused)'),
    P('passacavo_v63', 'Cable tunnel grommet (raised tunnel)', 'TPU', 1, [('yellow', 'passacavo_v63_print.stl')],
      dict(S_TPU), 'lip on the bed (CAD print file now as assembled)'),
    # ---------------- test pieces ----------------
    P('test_scanalato', 'Spline fit test (3 coupons)', 'PETG', 1, [('black', 'test_scanalato_print.stl')],
      dict(S_SOLID), 'socket on the bed; 1/2/3 notches = 0.05/0.10/0.20 mm radial clearance; mozzo_v6 is built with 0.10',
      source='drivetrain.json', kind='test'),
    P('test_groove_rim', 'Bowl rim groove coupon (30 mm cut of chiocciola_v63)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '15%'}, 'rim with the 3.0 x 2.2 lip-seal groove; cut face on the bed',
      reorient='cut_rim', source='cut from chiocciola_v63.stl', kind='test'),
    P('test_groove_cap', 'Cap upstand groove coupon (20 mm cut of fondello_v63)', 'PETG', 1, [('black', None)],
      dict(S_IP66), 'straight side of the D upstand with the 2.1 retaining groove; cut face on the bed',
      reorient='cut_cap', source='cut from fondello_v63.stl', kind='test'),
    P('test_groove_skirt', 'Flange skirt groove coupon (30 mm cut of flangia_piano_v63)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '25%'}, 'plate edge with the skirt-lip groove (groove up); shelf face on the bed',
      reorient='cut_skirt', source='cut from flangia_piano_v63.stl', kind='test'),
    P('test_rim_lip', 'TPU rim lip seal test arc (30 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU_LIP), 'same cut box as test_groove_rim; foot on the bed', reorient='cut_rim_lip', source='cut from guarnizione_baionetta_v61.stl', kind='test'),
    P('test_cap_lip', 'TPU cap lip seal test strip (20 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU), 'same cut box as test_groove_cap; base on the bed', reorient='cut_cap_lip', source='cut from guarnizione_fondello_v61.stl', kind='test'),
    P('test_skirt_lip', 'TPU skirt lip test arc (30 mm)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU_LIP), 'same cut box as test_groove_skirt; anchor on the bed', reorient='cut_skirt_lip', source='cut from labbro_ombra_v611.stl', kind='test'),
    P('test_comb_lip', 'TPU comb lip test (spare labbro_pettine_v62)', 'TPU', 1, [('yellow', 'labbro_pettine_v62_print.stl')],
      dict(S_TPU_LIP), 'one spare comb lip: check the slits and the flap', source='labbro_pettine_v62_print.stl', kind='test'),
]
PART = {p['id']: p for p in PARTS}
SKIRT_CUT = (72.0, 92.0)   # radial cut range for the skirt groove coupon at 0 deg
LIP_DZ = 8.0               # v6.2 flange + gate stack is 8 mm higher than v6.1.1
ALIAS = {}


def resolve(pid):
    return ALIAS.get(pid, pid)


def _to_manifold(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def _from_manifold(M):
    out = M.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=True)


def _manifold_clean(m):
    M = _to_manifold(m)
    if M.status() != mf.Error.NoError or M.is_empty():
        return m
    return _from_manifold(M)


def _box_cut(m, x0, x1, y0, y1, z0=-500.0, z1=500.0):
    box = mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
    return _from_manifold(_to_manifold(m) ^ box)


def _latch_on_back(m):
    """linguetta_sicura_print.stl is upright (as assembled); lay it on its back: T-foot face down, nub up."""
    a = np.radians(76.5)
    u = np.array([np.cos(a), np.sin(a), 0.0])
    R = trimesh.geometry.align_vectors(u, [0, 0, 1])
    m = m.copy()
    m.apply_transform(R)
    ext = m.bounds[1] - m.bounds[0]
    if ext[1] > ext[0]:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
    m.apply_translation(-m.bounds[0])
    return m


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
        out = [('black', _box_cut(L('fondello_v63.stl'), 35, 44, 14, 34, -84, -60))]
    elif r == 'cut_cap_lip':
        out = [('yellow', _box_cut(L('guarnizione_fondello_v61.stl'), 32, 50, 14, 34, -90, -60))]
    elif r == 'cut_skirt':
        c = _box_cut(L('flangia_piano_v63.stl'), SKIRT_CUT[0], SKIRT_CUT[1], -15, 15, 40, 100)
        c.apply_transform(FX)
        out = [('black', c)]
    elif r == 'cut_skirt_lip':
        lip = L('labbro_ombra_v611.stl')
        lip.apply_translation([0, 0, LIP_DZ])          # v6.2 flange sits 8 mm higher: lip asm copy is at the v6.1.1 height
        c = _box_cut(lip, SKIRT_CUT[0], SKIRT_CUT[1], -15, 15, 40, 100)
        c.apply_transform(FX)
        out = [('yellow', c)]
    elif r == 'asm_rot':
        m = L(pid + '.stl')
        for ax, deg in p['rot'] or []:
            m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), {'x': [1, 0, 0], 'y': [0, 1, 0]}[ax]))
        out = [(p['bodies'][0][0], m)]
    elif r == 'flange_nopin':
        m = L('flangia_piano_v63.stl')
        top = 70.1                                     # shelf-side face of the lower plate (assembly frame)
        M = _to_manifold(m)
        pin = mf.Manifold.cylinder(4.0, 2.6, 2.6, 64).translate([0, 0, top - 0.001])        # d5.2 x 4: removes the d4 pin
        hole = mf.Manifold.cylinder(2.7 + 0.01, 2.0, 2.0, 64).translate([0, 0, top - 2.7])   # d4.0 x 2.7 dowel hole
        m = _from_manifold((M - pin) - hole)
        m.apply_transform(FX)
        out = [('black', m)]
    else:
        out = [(c, trimesh.load(os.path.join(PARTS_DIR, f))) for c, f in p['bodies']]
        if r == 'latch_on_back':
            out = [(c, _latch_on_back(m)) for c, m in out]
    out = [(c, _manifold_clean(m)) for c, m in out]
    zmin = min(m.bounds[0, 2] for _, m in out)
    for _, m in out:
        m.apply_translation([0, 0, -zmin])
    return out


def load_modifiers(pid, bodies):
    """No helper volumes in v6.3: the box needs no support any more and the ring window is a self-supporting teardrop."""
    return []
