"""Straight hex-key access check: a key shaft (cylinder) along the screw axis from the head face outward, then a hand
envelope (cylinder) beyond the key length. Works on any dict of watertight meshes (manifold3d booleans via trimesh)."""
import numpy as np
import trimesh


def _cyl_along(p0, d, r, t0, t1, n=32):
    d = np.asarray(d, float) / np.linalg.norm(d)
    c = trimesh.creation.cylinder(radius=r, height=t1 - t0, sections=n)
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d))
    c.apply_translation(np.asarray(p0, float) + d * (t0 + t1) / 2)
    return c


def axial_hits(parts, p0, d, r, t0, t1, n=32):
    """{part: (t_min, t_max, mm3)} of the parts that intersect the cylinder (axis p0 + t d, radius r, t0..t1)"""
    d = np.asarray(d, float) / np.linalg.norm(d)
    c = _cyl_along(p0, d, r, t0, t1, n)
    lo, hi = c.bounds
    out = {}
    for k, m in parts.items():
        if m is None or len(m.faces) == 0:
            continue
        if np.any(m.bounds[0] > hi + 0.01) or np.any(m.bounds[1] < lo - 0.01):
            continue
        try:
            x = trimesh.boolean.intersection([m, c], engine='manifold')
        except Exception:
            continue
        if x is None or len(x.faces) == 0 or abs(x.volume) < 1e-4:
            continue
        t = (x.vertices - np.asarray(p0, float)) @ d
        out[k] = (round(float(t.min()), 2), round(float(t.max()), 2), round(float(abs(x.volume)), 3))
    return out


def check_screw(parts, head_face, axis_out, key_d=3.2, hand_d=28.0, t_max=220.0, hand_len=100.0, own=()):
    """head_face: centre of the head top face (where the key enters); axis_out: unit vector pointing from the head
    towards the user. Returns a dict with the shaft verdict, first obstacle and the minimum key length for a free hand."""
    pr = {k: m for k, m in parts.items() if k not in own}
    sh = axial_hits(pr, head_face, axis_out, key_d / 2, 0.05, t_max)
    first = min(sh.items(), key=lambda kv: kv[1][0]) if sh else None
    hd = axial_hits(pr, head_face, axis_out, hand_d / 2, 0.05, t_max + hand_len)
    t_hand = max([v[1] for v in hd.values()], default=0.0)
    blocked = first is not None
    res = {'shaft_clear': not blocked,
           'first_obstacle': None if not blocked else {'part': first[0], 'at_mm': first[1][0], 'mm3': first[1][2]},
           'key_length_min_mm': None if blocked else round(max(t_hand, 15.0), 1),
           'hand_obstacles': {k: v[1] for k, v in sorted(hd.items(), key=lambda kv: -kv[1][1])[:3]}}
    if blocked:
        res['verdict'] = 'BLOCKED'
    elif res['key_length_min_mm'] > t_max:
        res['verdict'] = 'NO HAND ROOM'
    else:
        L = res['key_length_min_mm']
        res['verdict'] = 'OK' if L <= 60 else ('OK long key' if L <= 100 else 'TOO DEEP')
    return res
