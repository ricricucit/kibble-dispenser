"""Printed parts of Kibble Dispenser Outdoor v6: sources, colours, quantities and slicer settings.

All meshes are returned in print orientation (Z-up, bottom at z=0), in mm.
Source of truth: v6.json in the v6 CAD build folder (hardware/v6/cad/build/, written by build_v6.py) (parts lists, quantities, print notes) plus the reused
v4b parts described in dosing.json. Colour bodies (*_print_<colour>.stl) share the frame of *_print.stl.
"""
import os
import numpy as np
import trimesh
import manifold3d as mf

# CAD build output of hardware/v6/cad/build_v6.py (gitignored): *_print.stl, v6.json, v6_viewer.json, v6_asm/
PARTS_DIR = os.environ.get('KD_V6_BUILD', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cad', 'build'))

# Filament slots of the PETG project (AMS lite) and of the TPU project (external spool).
PETG_SLOTS = {'black': 1, 'orange': 2, 'green': 3}
PETG_FILAMENTS = [  # slot order
    {'slot': 1, 'colour': 'black', 'type': 'PETG', 'hex': '#1A1A1A', 'role': 'structure'},
    {'slot': 2, 'colour': 'orange', 'type': 'PETG', 'hex': '#F07A1A', 'role': 'touch points / act here'},
    {'slot': 3, 'colour': 'green', 'type': 'PETG', 'hex': '#2E9D4F', 'role': 'food path'},
]
TPU_FILAMENTS = [{'slot': 'external spool', 'colour': 'yellow', 'type': 'TPU', 'hex': '#F2C81E', 'role': 'seals / soft parts'}]
DENSITY = {'PETG': 1.27, 'TPU': 1.24}

# Slicer overrides per part (Bambu Studio object settings; values are strings as Bambu stores them).
S_STRUCT = {'wall_loops': '3', 'sparse_infill_density': '15%'}
S_SOLID = {'wall_loops': '4', 'sparse_infill_density': '100%'}
S_TPU = {'wall_loops': '2', 'sparse_infill_density': '100%'}
SUP_BED = {'enable_support': '1', 'support_type': 'tree(auto)', 'support_on_build_plate_only': '1'}
SUP_BED_SNUG = {'enable_support': '1', 'support_type': 'normal(auto)', 'support_on_build_plate_only': '1'}


def P(pid, label, material, qty, bodies, settings, note, reorient=None, source='v6.json', kind='part'):
    return dict(id=pid, label=label, material=material, qty=qty, bodies=bodies, settings=settings, note=note,
                reorient=reorient, source=source, kind=kind)


PARTS = [
    # ---------------- PETG ----------------
    P('chiocciola_v6', 'Bowl (chiocciola)', 'PETG', 1, [('black', 'chiocciola_v6_print.stl')],
      {**S_STRUCT, **SUP_BED},
      'as assembled, flat base on the bed; supports on build plate only (under the 3 bayonet lugs); internal funnel ceiling ~52 deg prints with slight sag'),
    P('scatola_v6', 'Electronics box', 'PETG', 1, [('black', 'scatola_v6_print.stl')],
      {'wall_loops': '5', 'sparse_infill_density': '15%', 'top_shell_layers': '5', 'bottom_shell_layers': '5', **SUP_BED_SNUG},
      'flipped, roof plateau on the bed; thin bed-only support wedge under the 2.5 deg roof slopes (max 3.2 mm); 5 walls = solid 2.4 mm walls (IP65 box)'),
    P('flangia_piano_v6', 'Shelf flange', 'PETG', 1, [('black', 'flangia_piano_v6_print.stl')],
      {'wall_loops': '3', 'sparse_infill_density': '25%'},
      'flipped, shelf face on the bed; hook tongues are 4 mm ledges, no support needed (optional)'),
    P('disco_v6', 'Dosing disc', 'PETG', 1, [('orange', 'disco_v6_print_orange.stl'), ('black', 'disco_v6_print_black.stl')],
      dict(S_STRUCT),
      'flipped, disc top on the bed; black label in the first 3 layers (0.6 mm); no supports'),
    P('piastra_gate_v4b', 'Gate plate', 'PETG', 1, [('black', 'piastra_gate_v4b_print_black.stl'), ('green', 'piastra_gate_v4b_print_green.stl')],
      dict(S_STRUCT),
      'as assembled, bottom face on the bed; green OUT band + labels in the top 3 layers (0.6 mm)', source='dosing.json (reused v4b)'),
    P('piastra_finestra_v4b', 'Window plate', 'PETG', 1, [('black', 'piastra_finestra_v4b_print_black.stl'), ('green', 'piastra_finestra_v4b_print_green.stl')],
      dict(S_STRUCT),
      'flipped, top face on the bed; green window band + FOOD IN in the first 3 layers (0.6 mm)', source='dosing.json (reused v4b)'),
    P('linguetta_sicura', 'Safety latch', 'PETG', 1, [('orange', 'linguetta_sicura_print.stl')],
      {**S_SOLID, **SUP_BED_SNUG},
      'lying on its back (T-foot face down, nub up), 100 % infill, 4 walls; small bed-only support under the spring tab (1.6 mm gap)',
      reorient='latch_on_back', source='dosing.json (reused)'),
    P('fondello_v6', 'Box cover', 'PETG', 1, [('black', 'fondello_v6_print_black.stl'), ('orange', 'fondello_v6_print_orange.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'top_shell_layers': '5', 'bottom_shell_layers': '5'},
      'as assembled, outer face on the bed; orange inlays in the first 3 layers (0.6 mm); no supports'),
    P('colonna_v6', 'Tower (shaft passage)', 'PETG', 1, [('black', 'colonna_v6_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '40%'},
      'as assembled, lobed flange on the bed (O-ring groove bridges 2.7 mm); 45 deg wedges under the top lobes; no supports; >= 4 walls'),
    P('albero_v6', 'Shaft', 'PETG', 1, [('black', 'albero_v6_print.stl')],
      {**S_SOLID, 'layer_height': '0.15', 'brim_type': 'outer_only', 'brim_width': '5'},
      'as assembled, bottom hex on the bed; 100 % infill (torsion); 0.15 mm layers for the O-ring grooves; 5 mm brim (63 mm tall, 12 mm wide)'),
    P('mozzo_v6', 'Servo hub', 'PETG', 1, [('black', 'mozzo_v6_print.stl')],
      dict(S_SOLID),
      'as assembled, spline socket on the bed (print test_scanalato first), hex socket up; 100 % infill'),
    P('scivolo_v6', 'Chute', 'PETG', 1, [('green', 'scivolo_v6_print.stl')],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'enable_support': '1', 'support_type': 'tree(auto)',
       'support_on_build_plate_only': '0'},
      'flipped, joint flange on the bed, tube rises at 35 deg from vertical; SUPPORT ON (deviation from v6.json): the drip '
      'ring is square to the tilted tube, so on its low side the 45 deg chamfer becomes ~10 deg from horizontal (about '
      '300 mm2 of overhang at z 1-11 mm, reported as floating region by the slicer); auto supports, also on the flange top'),
    P('colletto_v6', 'Funnel collar', 'PETG', 1, [('green', 'colletto_v6_print.stl')],
      dict(S_STRUCT),
      'flipped, top rim on the bed, funnel widens upward; no supports'),
    P('nottolino_v6', 'Quarter-turn button', 'PETG', 4, [('orange', 'nottolino_v6_print.stl')],
      dict(S_SOLID),
      'as assembled, flat underside on the bed; 100 % infill; print 4'),
    # ---------------- TPU 95A ----------------
    P('guarnizione_baionetta', 'Rim gasket (bayonet)', 'TPU', 1, [('yellow', 'guarnizione_baionetta_print.stl')],
      dict(S_TPU), 'flat ring, 100 % infill', source='dosing.json (reused)'),
    P('guarnizione_piano_v5', 'Flange-shelf gasket ring', 'TPU', 1, [('yellow', 'guarnizione_piano_v5_print.stl')],
      dict(S_TPU), 'flat ring, 100 % infill', source='v5.json (reused)'),
    P('guarnizione_fondello_v6', 'Cover lip seal', 'TPU', 1, [('yellow', 'guarnizione_fondello_v6_print.stl')],
      {**S_TPU, 'outer_wall_speed': '20', 'inner_wall_speed': '20'},
      'as assembled, base on the bed, lip up (30 deg lean); 100 % infill, slow'),
    P('labbro_uscita_1', 'Plate lip, outlet 1', 'TPU', 1, [('yellow', 'labbro_uscita_1_print.stl')], dict(S_TPU), 'flat on its wide face', source='dosing.json (reused)'),
    P('labbro_uscita_2', 'Plate lip, outlet 2', 'TPU', 1, [('yellow', 'labbro_uscita_2_print.stl')], dict(S_TPU), 'flat on its wide face', source='dosing.json (reused)'),
    P('labbro_finestra_1', 'Plate lip, window 1', 'TPU', 1, [('yellow', 'labbro_finestra_1_print.stl')], dict(S_TPU), 'flat on its wide face', source='dosing.json (reused)'),
    P('labbro_finestra_2', 'Plate lip, window 2', 'TPU', 1, [('yellow', 'labbro_finestra_2_print.stl')], dict(S_TPU), 'flat on its wide face', source='dosing.json (reused)'),
    # ---------------- test pieces ----------------
    P('test_scanalato', 'Spline fit test (3 coupons)', 'PETG', 1, [('black', 'test_scanalato_print.stl')],
      dict(S_SOLID), 'socket on the bed; coupons with 1/2/3 notches = 0.05/0.10/0.20 mm radial clearance; mozzo_v6 is built with 0.10',
      source='drivetrain.json', kind='test'),
    P('test_groove_fondello', 'Cover groove coupon (40 mm cut of fondello_v6)', 'PETG', 1, [('black', None)],
      {'wall_loops': '4', 'sparse_infill_density': '15%', 'top_shell_layers': '5', 'bottom_shell_layers': '5'},
      'cut of fondello_v6 (y -20..20 on the +X long side, groove + inner lip + skirt); outer face on the bed', reorient='cut_fondello',
      source='new in print_v6 (cut from fondello_v6_print_black.stl)', kind='test'),
    P('test_lip_strip', 'TPU lip seal test strip (40 mm cut of guarnizione_fondello_v6)', 'TPU', 1, [('yellow', None)],
      dict(S_TPU), 'straight 40 mm cut of the cover lip seal, base on the bed, lip up', reorient='cut_lip',
      source='new in print_v6 (cut from guarnizione_fondello_v6_print.stl)', kind='test'),
]

# TPU parts being redesigned for v6 (comb-slit plate lips, low-force bayonet lip seal). When the new
# *_v6_print.stl files exist in PARTS_DIR they replace the reused v4b ones automatically.
TPU_V6_REDESIGN = {'labbro_uscita_1': 'labbro_uscita_1_v6', 'labbro_uscita_2': 'labbro_uscita_2_v6',
                   'labbro_finestra_1': 'labbro_finestra_1_v6', 'labbro_finestra_2': 'labbro_finestra_2_v6',
                   'guarnizione_baionetta': 'guarnizione_baionetta_v6'}
ALIAS = {}
for _p in PARTS:
    _new = TPU_V6_REDESIGN.get(_p['id'])
    if _new and os.path.exists(os.path.join(PARTS_DIR, _new + '_print.stl')):
        ALIAS[_p['id']] = _new
        _p['id'] = _new
        _p['bodies'] = [('yellow', _new + '_print.stl')]
        _p['source'] = 'v6 redesign (replaces the reused v4b part)'
        _p['note'] = 'v6 redesign; print as exported (*_print.stl orientation), 100 % infill'
PART = {p['id']: p for p in PARTS}


def resolve(pid):
    """Plate lists use the original ids; map them to the v6 redesign when present."""
    return ALIAS.get(pid, pid)


def _manifold_clean(m):
    """Round-trip through manifold3d: merges duplicate vertices and splits non-manifold edges
    (e.g. two colour bodies touching along an edge) so every slicer reads a clean solid."""
    mesh = mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32))
    M = mf.Manifold(mesh)
    if M.status() != mf.Error.NoError or M.is_empty():
        return m
    out = M.to_mesh()
    t = trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=True)
    return t


def _to_manifold(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def _from_manifold(M):
    out = M.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=True)


def _box_cut(m, x0, x1, y0, y1):
    box = mf.Manifold.cube([x1 - x0, y1 - y0, 200.0]).translate([x0, y0, -50.0])
    return _from_manifold(_to_manifold(m) ^ box)


def _latch_on_back(m):
    """linguetta_sicura_print.stl is upright (as assembled). Lay it on its back: the T-foot face
    (inner, radial direction -u at the latch angle 76.5 deg) goes down, the nub (outer side) up."""
    a = np.radians(76.5)
    u = np.array([np.cos(a), np.sin(a), 0.0])
    R = trimesh.geometry.align_vectors(u, [0, 0, 1])   # radial-outward -> +Z, so the inner foot face is the bottom
    m = m.copy()
    m.apply_transform(R)
    # long axis (old Z) is now horizontal; turn it along X for a tidy footprint
    ext = m.bounds[1] - m.bounds[0]
    if ext[1] > ext[0]:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
    m.apply_translation(-m.bounds[0])
    return m


def load_bodies(pid):
    """[(colour, trimesh)] in print orientation, z=0 on the bed, cleaned. Colour bodies keep their common frame."""
    p = PART[pid]
    out = []
    if p['reorient'] == 'cut_fondello':
        blk = trimesh.load(os.path.join(PARTS_DIR, 'fondello_v6_print_black.stl'))
        c = _box_cut(blk, 25.0, 60.0, -20.0, 20.0)
        out = [('black', c)]
    elif p['reorient'] == 'cut_lip':
        g = trimesh.load(os.path.join(PARTS_DIR, 'guarnizione_fondello_v6_print.stl'))
        c = _box_cut(g, 30.0, 50.0, -20.0, 20.0)
        out = [('yellow', c)]
    else:
        for colour, f in p['bodies']:
            m = trimesh.load(os.path.join(PARTS_DIR, f))
            out.append((colour, m))
        if p['reorient'] == 'latch_on_back':
            out = [(c, _latch_on_back(m)) for c, m in out]
    out = [(c, _manifold_clean(m)) for c, m in out]
    zmin = min(m.bounds[0, 2] for _, m in out)
    for _, m in out:
        m.apply_translation([0, 0, -zmin])
    return out
