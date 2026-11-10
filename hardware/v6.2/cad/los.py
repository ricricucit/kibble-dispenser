"""Line-of-sight helpers (no embree): cropped meshes + trimesh ray_triangle."""
import numpy as np
import trimesh


def crop(m, lo, hi):
    """faces of m with at least one vertex inside the box [lo, hi] (open mesh, ray casting only)"""
    v = m.vertices
    inside = np.all((v >= lo) & (v <= hi), axis=1)
    fm = inside[m.faces].any(axis=1)
    if not fm.any():
        return None
    return trimesh.Trimesh(v, m.faces[fm], process=False)


def first_hits(meshes, origins, dirs, max_d=1e9, batch=100):
    """for every ray: (name of the first part hit or '', distance)"""
    origins = np.asarray(origins, float)
    dirs = np.asarray(dirs, float)
    dirs = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    best = np.full(len(origins), np.inf)
    name = np.array([''] * len(origins), dtype=object)
    for k, m in meshes.items():
        if m is None:
            continue
        it = trimesh.ray.ray_triangle.RayMeshIntersector(m)
        locs, ris = [], []
        for s0 in range(0, len(origins), batch):
            lc, rr, _ = it.intersects_location(origins[s0:s0 + batch], dirs[s0:s0 + batch], multiple_hits=False)
            locs.append(np.asarray(lc, float).reshape(-1, 3)); ris.append(np.asarray(rr, int) + s0)
        loc, ri = np.vstack(locs), np.concatenate(ris)
        if len(ri) == 0:
            continue
        d = np.einsum('ij,ij->i', loc - origins[ri], dirs[ri])
        upd = d < best[ri]
        best[ri[upd]] = d[upd]
        name[ri[upd]] = k
    best[best > max_d] = np.inf
    return name, best


def free_points(origins, dirs, dist, step=0.25, cap=200.0):
    """points along every ray from its origin to its first hit (or cap)"""
    dirs = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    out = []
    for o, d, t in zip(origins, dirs, dist):
        t = min(t, cap)
        s = np.arange(0.0, max(t - 0.05, 0.0), step)
        out.append(o + s[:, None] * d)
    return out
