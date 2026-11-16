"""Compute plate layouts (positions in A1 bed coordinates) and keep the posed meshes.

Plates with from_v63 reuse the positions stored in print_v63/layout.json, so unchanged plates are identical to print_v63."""
import itertools
import json
import numpy as np
import trimesh
from shapely.geometry import box, Polygon as _Pg
from shapely.ops import unary_union as _uu
from shapely import affinity

import parts_v64 as pv
import pack
import plates_v64 as pl

_V63 = None


def pose_matrix(deg, x, y):
    T = trimesh.transformations.rotation_matrix(np.radians(deg), [0, 0, 1])
    T[0, 3], T[1, 3] = x, y
    return T


def _load(pid, cache):
    if pid in cache:
        return
    bodies = pv.load_bodies(pid)
    mods = pv.load_modifiers(pid, bodies)
    ears = [('ear', md['mesh']) for md in mods if md['subtype'] == 'normal_part']
    fp_body = pack.footprint(bodies)                    # frame reference: the part alone (as print_v63)
    fp = pack.footprint(bodies + ears) if ears else fp_body
    height = max(m.bounds[1, 2] for _, m in bodies)
    if height > 10.0:
        # do not nest other parts inside the openings of tall parts (nozzle/removal clearance),
        # except very large openings (inscribed radius > 40 mm, e.g. the d166 interlock ring), which stay usable
        polys = []
        for g in ([fp] if fp.geom_type == 'Polygon' else fp.geoms):
            keep = [r for r in g.interiors if not _Pg(r).buffer(-40.0).is_empty]
            polys.append(_Pg(g.exterior, [r.coords for r in keep]))
        fp = _uu(polys)
        if not ears:
            fp_body = fp
    # local frame: footprint bbox centre of the part at the origin
    cx, cy = (fp_body.bounds[0] + fp_body.bounds[2]) / 2, (fp_body.bounds[1] + fp_body.bounds[3]) / 2
    for _, m in bodies:
        m.apply_translation([-cx, -cy, 0])
    for md in mods:
        md['mesh'].apply_translation([-cx, -cy, 0])
    fp = affinity.translate(fp, -cx, -cy)
    bw = float(pv.PART[pid]['settings'].get('brim_width', 0) or 0)
    if bw > 0:
        # keep the 5 mm gap from the brim edge, not from the part (else the slicer reports path conflicts)
        fp = fp.buffer(bw + 1.0, quad_segs=8)
    cache[pid] = dict(bodies=bodies, fp=fp, modifiers=mods)


def layout_plate(plate, cache):
    global _V63
    items = []
    for pid, qty in plate['parts']:
        pid = pv.resolve(pid)
        _load(pid, cache)
        for k in range(qty):
            items.append(dict(name=f'{pid}#{k + 1}' if qty > 1 else pid, pid=pid, fp=cache[pid]['fp'], rotations=None))
    ks = pl.TOWER_KEEPOUT if plate['tower'] else None

    if plate.get('from_v63'):
        if _V63 is None:
            _V63 = json.load(open(pl.V63_LAYOUT))
        src = _V63[plate['from_v63']]
        pos = {it['name']: it for it in src['items']}
        out = []
        for it in items:
            s = pos[it['name']]
            geom = affinity.translate(affinity.rotate(it['fp'], s['rot_z_deg'], origin=(0, 0)), s['x'], s['y'])
            out.append(dict(name=it['name'], pid=it['pid'], x=s['x'], y=s['y'], deg=s['rot_z_deg'], geom=geom))
        keepout, tower_xy = None, None
        if src['tower_xy']:
            tower_xy = tuple(src['tower_xy'])
            keepout = box(tower_xy[0] - 5.0, tower_xy[1] - 5.0, tower_xy[0] - 5.0 + ks[0], tower_xy[1] - 5.0 + ks[1])
        gap = pack.min_gap(out + ([dict(geom=keepout)] if keepout is not None else [])) if len(out) > 1 or keepout is not None else float('inf')
        return dict(plate=plate, items=out, keepout=keepout, tower_xy=tower_xy, min_gap=gap, margins=src['bed_margins'],
                    positions='print_v63/layout.json ' + plate['from_v63'])

    def run(rots, res, usable):
        its = [dict(it, rotations=rots) for it in items]
        work = its + ([dict(name='__tower__', fp=box(0, 0, ks[0], ks[1]), rotations=(0,))] if ks else [])
        base = sorted(work, key=lambda it: -it['fp'].area)
        head, tail = base[:4], base[4:]
        orders = [list(p_) + tail for p_ in itertools.permutations(head)]
        return pack.place(its, keepout_size=ks, orders=orders, res=res, usable=usable)

    placed, margins = None, 'normal'
    for rots, res, usable, tag in (((0, 90, 180, 270), 1.0, pack.USABLE, 'normal'), (None, 1.0, pack.USABLE, 'normal'),
                                   (None, 0.5, pack.USABLE, 'normal'), ((0, 90, 180, 270), 0.5, pack.USABLE_RELAXED, 'relaxed'),
                                   (None, 0.5, pack.USABLE_RELAXED, 'relaxed')):
        try:
            placed = run(rots, res, usable)
            margins = tag
            break
        except RuntimeError:
            continue
    if placed is None:
        raise RuntimeError('cannot place plate ' + plate['key'])
    by = {p['name']: p for p in placed}
    out = []
    for it in items:
        p = by[it['name']]
        out.append(dict(name=it['name'], pid=it['pid'], x=p['x'], y=p['y'], deg=p['deg'], geom=p['geom']))
    keepout, tower_xy = None, None
    if ks:
        keepout = by['__tower__']['geom']
        tower_xy = (keepout.bounds[0] + 5.0, keepout.bounds[1] + 5.0)
    gap = pack.min_gap([p for p in placed]) if len(placed) > 1 else float('inf')
    return dict(plate=plate, items=out, keepout=keepout, tower_xy=tower_xy, min_gap=gap, margins=margins, positions='packed')


def posed_bodies(item, cache):
    T = pose_matrix(item['deg'], item['x'], item['y'])
    res = []
    for colour, m in cache[item['pid']]['bodies']:
        mm = m.copy()
        mm.apply_transform(T)
        res.append((colour, mm))
    return res
