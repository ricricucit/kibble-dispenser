"""Build the print package for Kibble Dispenser Outdoor v6.2 (Bambu Lab A1 + AMS lite).

Outputs (all under hardware/v6.2/plates/):
  Kibble_Dispenser_v62_PETG.bambu.3mf   Bambu Studio project, all PETG plates (test plate + 5 plates), AMS slots preset
  Kibble_Dispenser_v62_TPU.bambu.3mf    Bambu Studio project, TPU plates (test strip + all seals), external spool
  plates/<KEY>_<name>.3mf               plain 3MF per plate (any slicer; colours as base materials)
  stl/                                  every printed part in print orientation (single body + colour bodies)
  preview/<KEY>_top.png, <KEY>_iso.png  plate previews
  layout.json                           positions (bed mm, deg about Z) used by all of the above
Run: python build_print_v62.py [--no-render]
"""
import io
import json
import os
import shutil
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v62 as pv          # noqa: E402
import plates_v62 as pl         # noqa: E402
import layout_v62 as lo         # noqa: E402
import write_3mf as w3         # noqa: E402

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/v6.2/plates
APP_VERSION = '02.05.00.00'     # 3MF 'Application' tag: Bambu Studio >= 2.5 and OrcaSlicer >= 2.5 open it as a project
PROFILE_SOURCE = 'BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09'
PROFILES = os.path.join(OUT, 'tools', 'bbl_profiles_resolved.json')
MACHINE = 'Bambu Lab A1 0.4 nozzle'
PROCESS = '0.20mm Standard @BBL A1'
FIL_PETG = 'Generic PETG @BBL A1'
FIL_TPU = 'Generic TPU @BBL A1'
COLOUR_HEX = {'black': '#1A1A1A', 'orange': '#F07A1A', 'green': '#2E9D4F', 'yellow': '#F2C81E'}
MATERIALS_PLAIN = {'black': ('PETG black (structure)', COLOUR_HEX['black']),
                   'orange': ('PETG orange (touch points)', COLOUR_HEX['orange']),
                   'green': ('PETG green (food path)', COLOUR_HEX['green']),
                   'yellow': ('TPU 95A yellow (seals)', COLOUR_HEX['yellow'])}


def slug(s):
    return ''.join(c if c.isalnum() else '_' for c in s).strip('_').replace('__', '_')


def compute_layouts():
    cache = {}
    res = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        L = lo.layout_plate(plate, cache)
        res[plate['key']] = L
        print(f"{plate['key']:7s} {len(L['items'])} items, min gap {L['min_gap']:.2f} mm, tower {L['tower_xy']}")
    return res, cache


def export_stls(cache):
    d = os.path.join(OUT, 'stl')
    os.makedirs(d, exist_ok=True)
    rows = []
    for p in pv.PARTS:
        bodies = cache[p['id']]['bodies']
        if len(bodies) > 1:
            # single-body file for single-colour printing: the original *_print.stl (same frame as the colour
            # bodies), cleaned and moved by the same translation as the colour bodies
            fresh0 = pv.load_bodies(p['id'])[0][1]
            off = bodies[0][1].bounds[0] - fresh0.bounds[0]
            single = pv._manifold_clean(trimesh.load(os.path.join(pv.PARTS_DIR, p['id'] + '_print.stl')))
            single.apply_translation(off)
        else:
            single = bodies[0][1]
        fn = f"{p['id']}_print.stl"
        single.export(os.path.join(d, fn))
        files = [fn]
        if len(bodies) > 1:
            for c, m in bodies:
                f2 = f"{p['id']}_print_{c}.stl"
                m.export(os.path.join(d, f2))
                files.append(f2)
        rows.append(dict(id=p['id'], files=files, watertight=bool(single.is_watertight)))
    return rows


def object_entries(L, cache, material):
    """Objects for the Bambu writer: one object per part id with one instance per placed copy.
    Rotation is baked into the local mesh per copy, so identical parts with different rotations become
    separate objects."""
    objs = {}
    for it in L['items']:
        p = pv.PART[it['pid']]
        key = (it['pid'], it['deg'])
        T = lo.pose_matrix(it['deg'], 0.0, 0.0)
        if key not in objs:
            vols = []
            for c, m in cache[it['pid']]['bodies']:
                mm = m.copy()
                mm.apply_transform(T)
                slot = pv.PETG_SLOTS[c] if material == 'PETG' else 1
                vols.append(dict(name=f"{it['pid']}_{c}" if len(cache[it['pid']]['bodies']) > 1 else it['pid'],
                                 extruder=slot, mesh=mm, source_file=f"{it['pid']}_print{'_' + c if len(cache[it['pid']]['bodies']) > 1 else ''}.stl"))
            for md in cache[it['pid']].get('modifiers', []):
                mm = md['mesh'].copy()
                mm.apply_transform(T)
                vols.append(dict(name=md['name'], extruder=0, mesh=mm, modifier=True, settings=md['settings'],
                                 subtype=md.get('subtype', 'modifier_part')))
            objs[key] = dict(name=it['pid'], settings=dict(p['settings']), volumes=vols, instances=[])
        objs[key]['instances'].append((it['x'], it['y']))
    out = list(objs.values())
    # tidy names for multiple instances / rotations
    seen = {}
    for o in out:
        seen[o['name']] = seen.get(o['name'], 0) + 1
    return out


def project_config(material, layouts_for_project):
    R = json.load(open(PROFILES))
    machine, process = R[MACHINE], R[PROCESS]
    if material == 'PETG':
        fil = [R[FIL_PETG]] * len(pv.PETG_FILAMENTS)
        cols = [f['hex'] for f in pv.PETG_FILAMENTS]
    else:
        fil = [R[FIL_TPU]]
        cols = [COLOUR_HEX['yellow']]
    wt = [L['tower_xy'] if L['tower_xy'] else (15.0, 220.0) for L in layouts_for_project]
    return w3.build_project_config(machine, process, fil, cols, APP_VERSION, len(layouts_for_project), wt)


def write_projects(layouts, cache, thumbs):
    paths = {}
    for material, plates, fname in (('PETG', pl.PLATES_PETG, 'Kibble_Dispenser_v62_PETG.bambu.3mf'),
                                    ('TPU', pl.PLATES_TPU, 'Kibble_Dispenser_v62_TPU.bambu.3mf')):
        Ls = [layouts[p['key']] for p in plates]
        bplates = [dict(name=p['name'], objects=object_entries(layouts[p['key']], cache, material)) for p in plates]
        cfg = project_config(material, Ls)
        th = {i: thumbs[p['key']] for i, p in enumerate(plates) if p['key'] in thumbs}
        path = os.path.join(OUT, fname)
        w3.write_bambu_project(path, bplates, cfg, APP_VERSION,
                               title=f'Kibble Dispenser Outdoor v6.2 - {material}', designer='',
                               description=f'Kibble Dispenser Outdoor v6.2, {material} plates for Bambu Lab A1'
                                           + (' + AMS lite (slot 1 black, 2 orange, 3 green)' if material == 'PETG' else ' (TPU 95A from the external spool)'),
                               thumbnails=th)
        paths[material] = path
        print('wrote', path)
    return paths


def write_plain(layouts, cache):
    d = os.path.join(OUT, 'plates')
    os.makedirs(d, exist_ok=True)
    paths = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        L = layouts[plate['key']]
        objs = []
        for it in L['items']:
            vols = []
            multi = len(cache[it['pid']]['bodies']) > 1
            for c, m in lo.posed_bodies(it, cache):
                vols.append(dict(name=f"{it['name']}_{c}" if multi else it['name'], material=c, mesh=m))
            objs.append(dict(name=it['name'], volumes=vols))
        mats = {k: MATERIALS_PLAIN[k] for k in MATERIALS_PLAIN if any(v['material'] == k for o in objs for v in o['volumes'])}
        fn = f"{plate['key']}_{slug(plate['name'].split(' - ')[-1])}.3mf"
        w3.write_plain_3mf(os.path.join(d, fn), objs, mats, title=f"Kibble Dispenser v6.2 {plate['key']} {plate['name']}")
        paths[plate['key']] = os.path.join('plates', fn)
    return paths


def save_layout(layouts):
    rows = {}
    for k, L in layouts.items():
        rows[k] = dict(name=L['plate']['name'], tower_xy=L['tower_xy'], min_gap_mm=round(L['min_gap'], 2), bed_margins=L.get('margins'),
                       items=[dict(name=it['name'], part=it['pid'], x=round(it['x'], 3), y=round(it['y'], 3), rot_z_deg=it['deg'])
                              for it in L['items']])
    json.dump(rows, open(os.path.join(OUT, 'layout.json'), 'w'), indent=1)


if __name__ == '__main__':
    render = '--no-render' not in sys.argv
    layouts, cache = compute_layouts()
    save_layout(layouts)
    thumbs = {}
    if render:
        import render_v62 as render_v6
        thumbs = render_v6.render_all(layouts, cache, OUT)
    stl_rows = export_stls(cache)
    # unmodified CAD print file of the lower flange (pivot pin on the bed face), kept for reference
    shutil.copy(os.path.join(pv.PARTS_DIR, 'flangia_piano_v62_print.stl'), os.path.join(OUT, 'stl', 'flangia_piano_v62_print_cad_original.stl'))
    plain = write_plain(layouts, cache)
    projects = write_projects(layouts, cache, thumbs)
    json.dump(dict(stl=stl_rows, plain=plain, projects=projects), open(os.path.join(OUT, 'tools', 'build_files.json'), 'w'), indent=1)
