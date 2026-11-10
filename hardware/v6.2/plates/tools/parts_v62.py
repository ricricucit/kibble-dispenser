"""Printed parts of Kibble Dispenser Outdoor v6.2: sources, colours, quantities and slicer settings.

All meshes are returned in print orientation (Z-up, bottom at z=0), in mm.
Source of truth: v62.json in the CAD build folder (hardware/v6.2/cad/build/, written by build_v62.py)
(changed_parts, new_parts, reused_unchanged, print notes).

Print-orientation fixes against the CAD exports (*_v62_print.stl), each checked by overhang area:
  flangia_piano_v62   CAD flips it shelf face down, but the d4 x 3.3 pivot pin sits on that face, so the whole plate
                      would float 3.3 mm above the bed (22 400 mm2 of overhang). Here: pin cut off, d4.0 x 2.7 blind hole
                      at the centre for a 4 x 6 stainless dowel pin, then shelf face down (see the guide; designer to confirm).
  canalina_base_v62   CAD not flipped (wood face up, 2079 mm2 overhang); note says wood face on the bed -> flipped (180 mm2).
  canalina_coperchio  CAD flipped (open side down, 150 mm bridge); note says open side up -> as assembled.
  canalina_tappo      CAD +90 deg about X (115 mm2 overhang); -90 deg about X is also "on its side" with 1.9 mm2.
  passacavo_v62       CAD flipped (7.5 mm2 on the bed, 70 mm2 overhang); "lip on the bed" = as assembled (74 mm2 base).
"""
import os
import numpy as np
import trimesh
import manifold3d as mf

# CAD build output of hardware/v6.2/cad/build_v62.py (gitignored): *_print.stl, v6x.json, v62_viewer.json, v6x_asm/
PARTS_DIR = os.environ.get('KD_V62_BUILD', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cad', 'build'))

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



def P(pid, label, material, qty, bodies, settings, note, reorient=None, source='v62.json', kind='part', module=None, modifiers=None, rot=None):
    return dict(id=pid, label=label, material=material, qty=qty, bodies=bodies, settings=settings, note=note,
                reorient=reorient, source=source, kind=kind, module=module, modifiers=modifiers or [], rot=rot)


PARTS = [
    # ---------------- PETG black: pod, bowl, flange (two plates), cable channel ----------------
    P('guscio_v611', 'Pod shell', 'PETG', 1, [('black', 'guscio_v611_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '6'},
      'as v6.1.1: seam edge on the bed, rim up; 5 walls; no supports; 6 mm brim', source='v6.1.1 (reused)'),
    P('fondello_v62', 'Pod cap (dishes d24)', 'PETG', 1, [('black', 'fondello_v62_print.stl')],
      {**S_IP66, **SUP_BED_SNUG, 'support_threshold_angle': '45'},
      'as v6.1.1: flat bottom on the bed; bed-only support ring under the R15 edge; IP66 settings; clear the 4 drain holes (d0.8) with a drill'),
    P('chiocciola_v62', 'Bowl (inserts at P1..P3)', 'PETG', 1, [('black', 'chiocciola_v62_print.stl')],
      {**S_STRUCT, **SUP_BED}, 'as v6.1: flat base on the bed; supports on build plate only (3 bayonet lugs)'),
    P('flangia_piano_v62', 'Lower flange plate (pivot pin as dowel)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '25%'},
      'shelf-side face on the bed; pivot pin cut off and replaced by a 4 x 6 dowel in a printed d4.0 x 2.7 hole (CAD orientation '
      'would float the plate on the pin); skirt, hooks and the skirt-lip groove grow up', reorient='flange_nopin'),
    P('flangia_alta_v62', 'Upper flange plate', 'PETG', 1, [('black', 'flangia_alta_v62_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'},
      'shelf face on the bed; the blade pocket and the cable groove (1.5 mm, bridges ~7 mm) are underneath; no supports'),
    P('canalina_base_v62', 'Cable channel base', 'PETG', 2, [('black', None)],
      dict(S_STRUCT), 'flat, wood face on the bed (CAD export was upside down)', reorient='asm_rot', rot=[('x', 180)]),
    P('canalina_coperchio_v62', 'Cable channel cover', 'PETG', 2, [('black', None)],
      dict(S_STRUCT), 'open side up, bottom wall on the bed (CAD export was upside down)', reorient='asm_rot', rot=[]),
    P('canalina_tappo_v62', 'Cable channel end cap', 'PETG', 1, [('black', None)],
      dict(S_STRUCT), 'on its side (-90 deg about X: 1.9 mm2 overhang instead of 115 in the CAD export)', reorient='asm_rot', rot=[('x', -90)]),
    # ---------------- PETG: dosing core + gate ----------------
    P('disco_v61', 'Dosing disc (self-cleaning)', 'PETG', 1, [('orange', 'disco_v61_print_orange_v611.stl'), ('black', 'disco_v61_print_black_v611.stl')],
      dict(S_STRUCT), 'flipped, disc top on the bed; black label in the first 3 layers; no supports', source='v6.1 (reused, v6.1.1 colour bodies)'),
    P('piastra_gate_v62', 'Gate plate (common lip grooves)', 'PETG', 1, [('black', 'piastra_gate_v62_print_black.stl'), ('green', 'piastra_gate_v62_print_green.stl')],
      dict(S_STRUCT), 'as v6.1: bottom face on the bed; green OUT band in the top 3 layers'),
    P('piastra_finestra_v62', 'Window plate (common lip grooves)', 'PETG', 1, [('black', 'piastra_finestra_v62_print_black.stl'), ('green', 'piastra_finestra_v62_print_green.stl')],
      dict(S_STRUCT), 'as v6.1 (flipped): green FOOD IN band in the first 3 layers'),
    P('saracinesca_v62', 'Gate blade (sector)', 'PETG', 1, [('green', 'saracinesca_v62_print_green.stl'), ('orange', 'saracinesca_v62_print_orange.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '100%'}, 'flat on the bed, 2 colours: green blade, orange arm through all 15 layers; 100 % infill'),
    P('anello_saracinesca_v62', 'Interlock ring', 'PETG', 1, [('orange', 'anello_saracinesca_v62_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'brim_type': 'outer_only', 'brim_width': '5',
       'enable_support': '1', 'support_type': 'normal(manual)', 'support_on_build_plate_only': '0'},
      'on its bottom edge; the d28 window top is a 28 mm bridge: small support from the window sill (support enforcer, manual mode); 5 mm brim',
      reorient=None),
    P('scivolo_v611', 'Chute', 'PETG', 1, [('green', 'scivolo_v611_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%'}, 'as v6.1.1: joint flange on the bed; no supports', source='v6.1.1 (reused)'),
    P('colletto_v6', 'Funnel collar', 'PETG', 1, [('green', 'colletto_v6_print.stl')],
      dict(S_STRUCT), 'flipped, top rim on the bed; no supports', source='v6 (reused)'),
    P('linguetta_sicura', 'Safety latch', 'PETG', 1, [('orange', 'linguetta_sicura_print.stl')],
      {**S_SOLID, **SUP_BED_SNUG}, 'lying on its back (T-foot face down, nub up), 100 % infill; small bed-only support under the spring tab',
      reorient='latch_on_back', source='v4b (reused)'),
    P('pulsante_v611', 'Latch push-button', 'PETG', 1, [('orange', 'pulsante_v611_print.stl')],
      dict(S_SOLID), 'as v6.1.1: standing on its head face; 100 % infill', source='v6.1.1 (reused)'),
    P('nottolino_v611', 'Flush thumb-turn (keyed)', 'PETG', 3, [('orange', 'nottolino_v611_print.stl')],
      dict(S_SOLID), 'as v6.1.1: shaft top on the bed; 100 % infill; key hole bridges; print 3', source='v6.1.1 (reused)'),
    # ---------------- PETG: drive tower + electronics box (pre-assembled unit in the kit) ----------------
    P('colonna_v62', 'Tower (3 pillars for the M3x40 stack)', 'PETG', 1, [('black', 'colonna_v62_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '100%'},
      'upright, flange on the bed; pillars and webs vertical; top arms on 45 deg chamfers; 100 % infill (the pillars carry the M3x40 preload)',
      module='drive tower'),
    P('albero_v6', 'Shaft', 'PETG', 1, [('black', 'albero_v6_print.stl')],
      {**S_SOLID, 'layer_height': '0.15', 'brim_type': 'outer_only', 'brim_width': '5'},
      'bottom hex on the bed; 100 % infill; 0.15 mm layers; 5 mm brim', source='v6 (reused)', module='drive tower'),
    P('mozzo_v6', 'Servo hub', 'PETG', 1, [('black', 'mozzo_v6_print.stl')],
      dict(S_SOLID), 'spline socket on the bed (print test_scanalato first); 100 % infill', source='v6 (reused)',
      module='electronics box (hub on the servo)'),
    P('scatola_v62', 'Electronics box (stack-screw ear + countersinks)', 'PETG', 1, [('black', 'scatola_v62_print.stl')],
      {**S_IP66, 'ironing_type': 'top', 'enable_support': '1', 'support_type': 'normal(manual)', 'support_on_build_plate_only': '0'},
      'as v6.1.1: roof on the bed (the ear prints on the bed, countersinks face up); support only under the far half of the C cup '
      '(support enforcer, manual mode); IP66 settings', reorient='box_enforcer', module='electronics box'),
    # ---------------- TPU 95A ----------------
    P('labbro_pettine_v62', 'Comb lip (common, x4)', 'TPU', 4, [('yellow', 'labbro_pettine_v62_print.stl')],
      dict(S_TPU_LIP), 'anchor on the bed; Arachne, 15 mm/s; print 4'),
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
    P('passacavo_v62', 'Cable tunnel grommet', 'TPU', 1, [('yellow', None)],
      dict(S_TPU), 'lip on the bed (as assembled; the CAD export was upside down)', reorient='asm_rot', rot=[]),
    # ---------------- test pieces ----------------
    P('test_scanalato', 'Spline fit test (3 coupons)', 'PETG', 1, [('black', 'test_scanalato_print.stl')],
      dict(S_SOLID), 'socket on the bed; 1/2/3 notches = 0.05/0.10/0.20 mm radial clearance; mozzo_v6 is built with 0.10',
      source='drivetrain.json', kind='test'),
    P('test_groove_rim', 'Bowl rim groove coupon (30 mm cut of chiocciola_v62)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '15%'}, 'rim with the 3.0 x 2.2 lip-seal groove; cut face on the bed',
      reorient='cut_rim', source='cut from chiocciola_v62.stl', kind='test'),
    P('test_groove_cap', 'Cap upstand groove coupon (20 mm cut of fondello_v62)', 'PETG', 1, [('black', None)],
      dict(S_IP66), 'straight side of the D upstand with the 2.1 retaining groove; cut face on the bed',
      reorient='cut_cap', source='cut from fondello_v62.stl', kind='test'),
    P('test_groove_skirt', 'Flange skirt groove coupon (30 mm cut of flangia_piano_v62)', 'PETG', 1, [('black', None)],
      {'wall_loops': '3', 'sparse_infill_density': '25%'}, 'plate edge with the skirt-lip groove (groove up); shelf face on the bed',
      reorient='cut_skirt', source='cut from flangia_piano_v62.stl', kind='test'),
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
        out = [('black', _box_cut(L('chiocciola_v62.stl'), 45, 75, -15, 15, 56, 80))]
    elif r == 'cut_rim_lip':
        out = [('yellow', _box_cut(L('guarnizione_baionetta_v61.stl'), 45, 75, -15, 15, 56, 80))]
    elif r == 'cut_cap':
        out = [('black', _box_cut(L('fondello_v62.stl'), 35, 44, 14, 34, -84, -60))]
    elif r == 'cut_cap_lip':
        out = [('yellow', _box_cut(L('guarnizione_fondello_v61.stl'), 32, 50, 14, 34, -90, -60))]
    elif r == 'cut_skirt':
        c = _box_cut(L('flangia_piano_v62.stl'), SKIRT_CUT[0], SKIRT_CUT[1], -15, 15, 40, 100)
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
        m = L('flangia_piano_v62.stl')
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
    """Helper volumes in the same frame as load_bodies(pid): list of dict(name, mesh, settings, subtype)."""
    r = PART[pid]['reorient']
    if r == 'box_enforcer':
        # C cup ring of scatola_v62 (unchanged from v6.1.1): down-facing ring at print z 53.6, x_asm 14..35, y +-11.
        full = trimesh.load(os.path.join(PARTS_DIR, 'scatola_v62.stl'))
        q = full.copy()
        q.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
        tx = -q.centroid[0]
        x0, x1 = 21.0 + tx, 37.0 + tx
        box = trimesh.creation.box(extents=[x1 - x0, 26.0, 6.0])
        box.apply_translation([(x0 + x1) / 2, 0.0, 53.6])
        return [dict(name='scatola_v62_C_cup_support_enforcer', mesh=box, settings={}, subtype='support_enforcer')]
    if pid == 'anello_saracinesca_v62':
        # window d28 in the ring wall (print frame): top arc at x -89..-80, y -28..-1, z 26..32
        box = trimesh.creation.box(extents=[16.0, 34.0, 9.0])
        box.apply_translation([-85.0, -14.5, 29.0])
        return [dict(name='anello_window_support_enforcer', mesh=box, settings={}, subtype='support_enforcer')]
    return []
