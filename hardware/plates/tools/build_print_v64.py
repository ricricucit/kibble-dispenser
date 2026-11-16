"""Build the print package for Kibble Dispenser Outdoor hardware 6.4.0 (Bambu Lab A1 + AMS lite).

Two products, five Bambu Studio projects (see plates_v64.PROJECTS), all under hardware/plates/:
  Kibble_Dispenser_v64_chassis_PETG.bambu.3mf        chassis, plates PETG-0..PETG-6
  Kibble_Dispenser_v64_chassis_IP66_PETG.bambu.3mf   chassis, plate PETG-7 (servo bay + cap), low-fan PETG settings
  Kibble_Dispenser_v64_chassis_TPU.bambu.3mf         chassis, TPU-0 test, TPU-1 seals, TPU-2 cap lip seal + module gasket
  Kibble_Module_case_1.0_PETG.bambu.3mf              module, MOD-1 tub + speaker ring, MOD-2 lid, low-fan PETG settings
  Kibble_Module_case_1.0_TPU.bambu.3mf               module, MOD-TPU-1 gasket alone
  plates/<KEY>_<name>.3mf               plain 3MF per plate (any slicer; colours as base materials)
  stl/                                  every printed part in print orientation (single body + colour bodies)
  preview/<KEY>_top.png, <KEY>_iso.png  plate previews
  layout.json                           positions (bed mm, deg about Z) used by all of the above
Run: python build_print_v64.py [--no-render]
"""
import copy
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v64 as pv          # noqa: E402
import plates_v64 as pl         # noqa: E402
import layout_v64 as lo         # noqa: E402
import write_3mf as w3         # noqa: E402

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/plates
APP_VERSION = '02.05.00.00'     # 3MF 'Application' tag: Bambu Studio >= 2.5 and OrcaSlicer >= 2.5 open it as a project
PROFILE_SOURCE = 'BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09'
PROFILES = os.path.join(OUT, 'tools', 'bbl_profiles_resolved.json')
MACHINE = 'Bambu Lab A1 0.4 nozzle'
PROCESS = '0.20mm Standard @BBL A1'
FIL_PETG = 'Generic PETG @BBL A1'
FIL_TPU = 'Generic TPU @BBL A1'
# sealed parts (review m17, v64.json print notes "fan <= 40 %"): part fan limited to 40 % for layer bonding; the nozzle stays at
# the 255 C of the Generic PETG profile (v64.json asks for at least 245-250 C). Bridges and overhangs steeper than about 28 deg
# keep the 90 % overhang fan; the threshold is raised from 10 % to 25 % so the leaning pod skin of the tub (about 16 deg) prints
# with the limited fan too
IP66_FILAMENT_OVERRIDES = {'fan_max_speed': ['40'], 'fan_min_speed': ['20'], 'overhang_fan_threshold': ['25%']}
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
    for plate in pl.ALL_PLATES:
        L = lo.layout_plate(plate, cache)
        res[plate['key']] = L
        print(f"{plate['key']:9s} {len(L['items'])} items, min gap {L['min_gap']:.2f} mm, tower {L['tower_xy']}, {L['positions']}")
    return res, cache


def export_stls(cache):
    d = os.path.join(OUT, 'stl')
    os.makedirs(d, exist_ok=True)
    rows = []
    for p in pv.PARTS:
        if p['id'] not in cache:
            continue
        bodies = cache[p['id']]['bodies']
        if len(bodies) > 1:
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
        rows.append(dict(id=p['id'], files=files, watertight=bool(single.is_watertight),
                         bodies=len(single.split(only_watertight=False))))
    return rows


def object_entries(L, cache, single_slot):
    """Objects for the Bambu writer: one object per (part id, rotation) with one instance per placed copy."""
    objs = {}
    for it in L['items']:
        p = pv.PART[it['pid']]
        key = (it['pid'], it['deg'])
        T = lo.pose_matrix(it['deg'], 0.0, 0.0)
        if key not in objs:
            vols = []
            multi = len(cache[it['pid']]['bodies']) > 1
            slot0 = 1
            for c, m in cache[it['pid']]['bodies']:
                mm = m.copy()
                mm.apply_transform(T)
                slot = 1 if single_slot else pv.PETG_SLOTS[c]
                slot0 = slot
                vols.append(dict(name=f"{it['pid']}_{c}" if multi else it['pid'],
                                 extruder=slot, mesh=mm, source_file=f"{it['pid']}_print{'_' + c if multi else ''}.stl"))
            for md in cache[it['pid']].get('modifiers', []):
                mm = md['mesh'].copy()
                mm.apply_transform(T)
                if md['subtype'] == 'normal_part':
                    vols.append(dict(name=md['name'], extruder=slot0, mesh=mm, source_file=''))
                else:
                    vols.append(dict(name=md['name'], extruder=0, mesh=mm, modifier=True, settings=md['settings'], subtype=md['subtype']))
            objs[key] = dict(name=it['pid'], settings=dict(p['settings']), volumes=vols, instances=[])
        objs[key]['instances'].append((it['x'], it['y']))
    return list(objs.values())


def project_config(kind, layouts_for_project):
    R = json.load(open(PROFILES))
    machine, process = R[MACHINE], R[PROCESS]
    if kind == 'ams3':
        fil = [R[FIL_PETG]] * len(pv.PETG_FILAMENTS)
        cols = [f['hex'] for f in pv.PETG_FILAMENTS]
    elif kind == 'black_ip66':
        f = copy.deepcopy(R[FIL_PETG])
        f.update(IP66_FILAMENT_OVERRIDES)
        fil = [f]
        cols = [COLOUR_HEX['black']]
    else:
        fil = [R[FIL_TPU]]
        cols = [COLOUR_HEX['yellow']]
    wt = [L['tower_xy'] if L['tower_xy'] else (15.0, 220.0) for L in layouts_for_project]
    return w3.build_project_config(machine, process, fil, cols, APP_VERSION, len(layouts_for_project), wt)


def write_projects(layouts, cache, thumbs):
    paths = {}
    for pr in pl.PROJECTS:
        plates = pr['plates']
        Ls = [layouts[p['key']] for p in plates]
        single = pr['filaments'] != 'ams3'
        bplates = [dict(name=p['name'], objects=object_entries(layouts[p['key']], cache, single)) for p in plates]
        cfg = project_config(pr['filaments'], Ls)
        th = {i: thumbs[p['key']] for i, p in enumerate(plates) if p['key'] in thumbs}
        path = os.path.join(OUT, pr['file'])
        w3.write_bambu_project(path, bplates, cfg, APP_VERSION, title=pr['title'], designer='', description=pr['description'], thumbnails=th)
        paths[pr['id']] = path
        print('wrote', path)
    return paths


def write_plain(layouts, cache):
    d = os.path.join(OUT, 'plates')
    os.makedirs(d, exist_ok=True)
    paths = {}
    for plate in pl.ALL_PLATES:
        L = layouts[plate['key']]
        objs = []
        for it in L['items']:
            vols = []
            multi = len(cache[it['pid']]['bodies']) > 1
            posed = lo.posed_bodies(it, cache)
            for c, m in posed:
                vols.append(dict(name=f"{it['name']}_{c}" if multi else it['name'], material=c, mesh=m))
            T = lo.pose_matrix(it['deg'], it['x'], it['y'])
            for md in cache[it['pid']].get('modifiers', []):
                if md['subtype'] == 'normal_part':          # mouse ears are printed geometry: keep them in the plain file
                    mm = md['mesh'].copy()
                    mm.apply_transform(T)
                    vols.append(dict(name=md['name'], material=posed[0][0], mesh=mm))
            objs.append(dict(name=it['name'], volumes=vols))
        mats = {k: MATERIALS_PLAIN[k] for k in MATERIALS_PLAIN if any(v['material'] == k for o in objs for v in o['volumes'])}
        fn = f"{plate['key']}_{slug(plate['name'].split(' - ')[-1].split(':')[0].split('(')[0])}.3mf"
        w3.write_plain_3mf(os.path.join(d, fn), objs, mats, title=f"Kibble Dispenser 6.4 {plate['key']} {plate['name']}")
        paths[plate['key']] = os.path.join('plates', fn)
    return paths


def save_layout(layouts):
    rows = {}
    for k, L in layouts.items():
        g = L['min_gap']
        rows[k] = dict(name=L['plate']['name'], tower_xy=L['tower_xy'], min_gap_mm=(round(g, 2) if np.isfinite(g) else None),
                       bed_margins=L.get('margins'), positions=L['positions'],
                       items=[dict(name=it['name'], part=it['pid'], x=round(it['x'], 3), y=round(it['y'], 3), rot_z_deg=it['deg'])
                              for it in L['items']])
    json.dump(rows, open(os.path.join(OUT, 'layout.json'), 'w'), indent=1)


if __name__ == '__main__':
    render = '--no-render' not in sys.argv
    layouts, cache = compute_layouts()
    save_layout(layouts)
    thumbs = {}
    if render:
        import render_v64
        thumbs = render_v64.render_all(layouts, cache, OUT)
    stl_rows = export_stls(cache)
    plain = write_plain(layouts, cache)
    projects = write_projects(layouts, cache, thumbs)
    json.dump(dict(stl=stl_rows, plain=plain, projects=projects), open(os.path.join(OUT, 'tools', 'build_files.json'), 'w'), indent=1)
