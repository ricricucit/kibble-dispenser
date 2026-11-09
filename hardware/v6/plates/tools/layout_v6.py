"""Compute plate layouts (positions in A1 bed coordinates) and keep the posed meshes."""
import numpy as np
import trimesh
from shapely.geometry import box
from shapely import affinity

import parts_v6 as pv
import pack
import plates_v6 as pl


def pose_matrix(deg, x, y):
    T = trimesh.transformations.rotation_matrix(np.radians(deg), [0, 0, 1])
    T[0, 3], T[1, 3] = x, y
    return T


def layout_plate(plate, cache, tower_corner='br'):
    items = []
    for pid, qty in plate['parts']:
        pid = pv.resolve(pid)
        if pid not in cache:
            bodies = pv.load_bodies(pid)
            fp = pack.footprint(bodies)
            height = max(m.bounds[1, 2] for _, m in bodies)
            if height > 10.0:
                # do not nest other parts inside the openings of tall parts (nozzle/removal clearance)
                from shapely.geometry import Polygon as _Pg
                from shapely.ops import unary_union as _uu
                fp = _uu([_Pg(g.exterior) for g in ([fp] if fp.geom_type == 'Polygon' else fp.geoms)])
            # local frame: footprint bbox centre at the origin
            cx, cy = (fp.bounds[0] + fp.bounds[2]) / 2, (fp.bounds[1] + fp.bounds[3]) / 2
            for _, m in bodies:
                m.apply_translation([-cx, -cy, 0])
            fp = affinity.translate(fp, -cx, -cy)
            cache[pid] = dict(bodies=bodies, fp=fp)
        for k in range(qty):
            items.append(dict(name=f'{pid}#{k + 1}' if qty > 1 else pid, pid=pid, fp=cache[pid]['fp'],
                              rotations=None))
    import itertools
    ks = pl.TOWER_KEEPOUT if plate['tower'] else None

    def run(rots):
        its = [dict(it, rotations=rots) for it in items]
        work = its + ([dict(name='__tower__', fp=box(0, 0, ks[0], ks[1]), rotations=(0,))] if ks else [])
        base = sorted(work, key=lambda it: -it['fp'].area)
        head, tail = base[:4], base[4:]
        orders = [list(p_) + tail for p_ in itertools.permutations(head)]
        return pack.place(its, keepout_size=ks, orders=orders)

    try:   # right angles first (tidy plates), free 15 deg steps only if needed
        placed = run((0, 90, 180, 270))
    except RuntimeError:
        placed = run(None)
    by = {p['name']: p for p in placed}
    out = []
    for it in items:
        p = by[it['name']]
        out.append(dict(name=it['name'], pid=it['pid'], x=p['x'], y=p['y'], deg=p['deg'], geom=p['geom']))
    keepout, tower_xy = None, None
    if ks:
        keepout = by['__tower__']['geom']
        tower_xy = (keepout.bounds[0] + 5.0, keepout.bounds[1] + 5.0)
    gap = pack.min_gap([p for p in placed])
    return dict(plate=plate, items=out, keepout=keepout, tower_xy=tower_xy, min_gap=gap)


def posed_bodies(item, cache):
    T = pose_matrix(item['deg'], item['x'], item['y'])
    res = []
    for colour, m in cache[item['pid']]['bodies']:
        mm = m.copy()
        mm.apply_transform(T)
        res.append((colour, mm))
    return res
