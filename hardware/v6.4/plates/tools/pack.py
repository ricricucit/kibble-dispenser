"""Greedy 2D placement of parts on a Bambu Lab A1 plate (256 x 256 mm) using real footprints.

Footprint = projection of all bodies on XY (holes kept, so small parts may nest inside rings).
Spacing: footprints are buffered by GAP/2 each, so two parts are >= GAP apart.
"""
import math
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, box
from shapely import affinity
from shapely.ops import unary_union
from shapely.prepared import prep
from trimesh.path.polygons import projected

BED = 256.0
GAP = 5.0
# usable area: A1 draws its extrusion-calibration lines at Y -0.5..1 and X 108..160 (front edge);
# keep 12 mm from the front, 8 mm from the other edges
USABLE = box(8.0, 12.0, BED - 8.0, BED - 8.0)
# relaxed margins for plates with two big parts (the A1 can print to the bed edge; its calibration line is
# at Y -0.5..1, X 108..160)
USABLE_RELAXED = box(4.0, 6.0, BED - 4.0, BED - 4.0)


def footprint(bodies):
    polys = []
    for _, m in bodies:
        try:
            p = projected(m, normal=[0, 0, 1], ignore_sign=True)
        except Exception:
            p = None
        if p is None or p.is_empty or not p.is_valid:
            # robust fallback: union of the projected triangles
            tri = m.triangles[:, :, :2]
            e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
            area = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
            tp = [Polygon(t).buffer(0.01) for t, a in zip(tri, area) if a > 1e-6]
            p = shapely.make_valid(unary_union(tp))
        polys.append(p)
    fp = unary_union(polys).buffer(0.05).buffer(-0.05)
    return fp.simplify(0.2)


def _rot(geom, deg):
    return affinity.rotate(geom, deg, origin=(0, 0), use_radians=False)


def _mask(geom, res, pad):
    """Rasterise a (multi)polygon, buffered by pad, into a boolean grid at res mm/cell.
    Returns (mask, ox, oy): cell (r, c) covers x = ox + c*res, y = oy + r*res."""
    from PIL import Image, ImageDraw
    g = geom.buffer(pad, quad_segs=4)
    minx, miny, maxx, maxy = g.bounds
    ox, oy = math.floor(minx / res) * res, math.floor(miny / res) * res
    w, h = int(math.ceil((maxx - ox) / res)) + 2, int(math.ceil((maxy - oy) / res)) + 2
    img = Image.new('1', (w, h), 0)
    d = ImageDraw.Draw(img)
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for pg in polys:
        d.polygon([((x - ox) / res, (y - oy) / res) for x, y in pg.exterior.coords], fill=1, outline=1)
        for ring in pg.interiors:
            d.polygon([((x - ox) / res, (y - oy) / res) for x, y in ring.coords], fill=0, outline=0)
    return np.array(img, dtype=np.float32), ox, oy


def place(items, keepout_size=None, res=1.0, rot_step=15, orders=None, usable=None):
    """Compact placement on a raster with FFT correlation.
    items: dict(name, fp, rotations optional). keepout_size: (w, h) of a rectangle (prime tower) placed like a part.
    Every candidate is scored by the bounding box of everything placed so far (smaller and squarer is better).
    Returns list of dict(name, x, y, deg, geom) with geom in bed coordinates; the keep-out comes back as name '__tower__'.
    """
    from scipy.signal import fftconvolve
    ux0, uy0, ux1, uy1 = (usable or USABLE).bounds
    W, H = int(round((ux1 - ux0) / res)), int(round((uy1 - uy0) / res))
    work = list(items)
    if keepout_size is not None:
        work.append(dict(name='__tower__', fp=box(0, 0, keepout_size[0], keepout_size[1]), rotations=(0,)))
    base = sorted(work, key=lambda it: -it['fp'].area)
    orders = orders or [base]
    best_sol = None
    for order in orders:
        occ = np.zeros((H, W), np.float32)
        bb = None
        sol = []
        ok = True
        for it in order:
            rots = it.get('rotations') or tuple(range(0, 360, rot_step))
            cand = None
            for d in rots:
                g = _rot(it['fp'], d)
                m, ox, oy = _mask(g, res, GAP / 2 + 0.75 * res)
                mh, mw = m.shape
                if mh > H or mw > W:
                    continue
                if occ.any():
                    corr = fftconvolve(occ, m[::-1, ::-1], mode='valid')
                    free = corr < 0.5
                else:
                    free = np.ones((H - mh + 1, W - mw + 1), bool)
                if not free.any():
                    continue
                rr, cc = np.nonzero(free)
                # candidate bbox (in grid cells) of the mask's filled extent
                fr, fc = np.nonzero(m > 0.5)
                r0, r1, c0, c1 = fr.min(), fr.max() + 1, fc.min(), fc.max() + 1
                if bb is None:
                    nb = np.stack([cc + c0, rr + r0, cc + c1, rr + r1], 1)
                else:
                    nb = np.stack([np.minimum(bb[0], cc + c0), np.minimum(bb[1], rr + r0),
                                   np.maximum(bb[2], cc + c1), np.maximum(bb[3], rr + r1)], 1)
                wspan, hspan = nb[:, 2] - nb[:, 0], nb[:, 3] - nb[:, 1]
                score = np.maximum(wspan, hspan) * 1000.0 + wspan * hspan / 100.0 + rr * 0.01 + cc * 0.001
                k = int(np.argmin(score))
                if cand is None or score[k] < cand[0]:
                    cand = (float(score[k]), d, int(rr[k]), int(cc[k]), m, ox, oy, nb[k])
            if cand is None:
                ok = False
                break
            _, d, r, c, m, ox, oy, nbk = cand
            occ[r:r + m.shape[0], c:c + m.shape[1]] = np.maximum(occ[r:r + m.shape[0], c:c + m.shape[1]], m)
            bb = nbk
            # translation mapping local geometry (rotated) into bed coordinates
            tx, ty = ux0 + c * res - ox, uy0 + r * res - oy
            sol.append(dict(name=it['name'], deg=float(d), x=float(tx), y=float(ty)))
        if not ok:
            continue
        area = (bb[2] - bb[0]) * (bb[3] - bb[1])
        if best_sol is None or area < best_sol[0]:
            best_sol = (area, sol, bb)
    if best_sol is None:
        raise RuntimeError('cannot place: ' + ', '.join(it['name'] for it in work))
    _, sol, bb = best_sol
    # centre the group in the usable area
    gx0, gy0, gx1, gy1 = ux0 + bb[0] * res, uy0 + bb[1] * res, ux0 + bb[2] * res, uy0 + bb[3] * res
    dx = round(((ux0 + ux1) / 2 - (gx0 + gx1) / 2) / res) * res
    dy = round(((uy0 + uy1) / 2 - (gy0 + gy1) / 2) / res) * res
    byname = {it['name']: it for it in work}
    out = []
    for s_ in sol:
        s_['x'] += dx
        s_['y'] += dy
        s_['geom'] = affinity.translate(_rot(byname[s_['name']]['fp'], s_['deg']), s_['x'], s_['y'])
        out.append(s_)
    return out


def min_gap(placed):
    g = math.inf
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            g = min(g, placed[i]['geom'].distance(placed[j]['geom']))
    return g
