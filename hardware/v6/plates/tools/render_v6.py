"""Plate previews: top view with labels and colours, iso view, and Bambu plate thumbnails."""
import io
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
from PIL import Image

import parts_v6 as pv
import layout_v6 as lo
import pack

FILL = {'black': '#2a2b2e', 'orange': '#f07a1a', 'green': '#2e9d4f', 'yellow': '#f2c81e'}
EDGE = {'black': '#000000', 'orange': '#8a3f00', 'green': '#145c2a', 'yellow': '#8a6d00'}
SLOT_TXT = {'black': 'slot 1 PETG black', 'orange': 'slot 2 PETG orange', 'green': 'slot 3 PETG green', 'yellow': 'external spool TPU 95A'}


def _polys(g):
    if g.is_empty:
        return []
    return [g] if g.geom_type == 'Polygon' else [p for p in g.geoms if p.geom_type == 'Polygon']


def top_view(L, cache, path, title):
    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    ax.add_patch(Rectangle((0, 0), 256, 256, fc='#e9e6df', ec='#555', lw=1.2))
    ux0, uy0, ux1, uy1 = pack.USABLE.bounds
    ax.add_patch(Rectangle((ux0, uy0), ux1 - ux0, uy1 - uy0, fc='none', ec='#999', lw=0.8, ls=(0, (4, 3))))
    ax.add_patch(Rectangle((108, -0.5), 52, 1.5, fc='#bbb', ec='none'))
    ax.text(134, 3.0, 'A1 calibration line', fontsize=6, ha='center', color='#777')
    colours_used = []
    for it in L['items']:
        posed = lo.posed_bodies(it, cache)
        # body (largest volume) first, inlays on top
        posed.sort(key=lambda cm: -cm[1].volume)
        for k, (c, m) in enumerate(posed):
            if c not in colours_used:
                colours_used.append(c)
            fp = pack.footprint([(c, m)])
            for pg in _polys(fp):
                ax.add_patch(MPoly(np.asarray(pg.exterior.coords), closed=True, fc=FILL[c], ec=EDGE[c], lw=0.6,
                                   alpha=1.0 if k == 0 else 0.95, zorder=2 + k))
                for ring in pg.interiors:
                    ax.add_patch(MPoly(np.asarray(ring.coords), closed=True, fc='#e9e6df', ec=EDGE[c], lw=0.4, zorder=2 + k))
        g = it['geom']
        cx, cy = g.centroid.x, g.centroid.y
        va = 'center'
        if not g.buffer(-1).contains(g.centroid):
            # rings / frames: label just outside the top-most point of the outline
            ext = np.concatenate([np.asarray(pg.exterior.coords) for pg in _polys(g)])
            k = int(np.argmax(ext[:, 1]))
            cx, cy = ext[k, 0], ext[k, 1] + 2.0
            va = 'bottom'
        p = pv.PART[it['pid']]
        h = max(m.bounds[1, 2] for _, m in posed)
        ax.text(cx, cy, f"{it['name']}\n{h:.1f} mm", fontsize=6.5, ha='center', va=va, zorder=20,
                bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#666', lw=0.5, alpha=0.9))
    if L.get('tower_xy'):
        tx, ty = L['tower_xy']
        ax.add_patch(Rectangle((tx, ty), 35, 30, fc='#d0cde6', ec='#5a4fa0', lw=0.8, hatch='////', zorder=3))
        ax.text(tx + 17.5, ty + 15, 'prime\ntower', fontsize=6, ha='center', va='center', zorder=20)
    ax.set_xlim(-6, 262)
    ax.set_ylim(-6, 262)
    ax.set_aspect('equal')
    ax.set_xlabel('X mm (A1 bed, front = Y 0)', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.set_title(title, fontsize=9)
    handles = [Rectangle((0, 0), 1, 1, fc=FILL[c], ec=EDGE[c]) for c in colours_used]
    ax.legend(handles, [SLOT_TXT[c] for c in colours_used], loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=3, fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _view_basis(azim_deg=-60.0, elev_deg=32.0):
    a, e = np.radians(azim_deg), np.radians(elev_deg)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])     # towards the camera
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(d, right)
    return d, right, up


def iso_view(L, cache, path, title=None, size=(8, 6.5), dpi=120, labels=True):
    """Orthographic iso render with a painter's algorithm over all triangles (bed included)."""
    from matplotlib.collections import PolyCollection
    d, right, up = _view_basis()
    light = np.array([0.35, -0.45, 0.82])
    light /= np.linalg.norm(light)
    tris, cols = [], []
    bg = [np.array([[0, 0, 0], [256, 0, 0], [256, 256, 0], [0, 256, 0]], float)]
    bgc = [(0.91, 0.90, 0.87, 1.0)]
    lab = []
    for it in L['items']:
        posed = lo.posed_bodies(it, cache)
        vmax = max(mm.volume for _, mm in posed)
        for c, m in posed:
            if m.volume < vmax and m.bounds[1, 2] <= 0.65:
                continue                   # bottom inlay, hidden under the part in this view
            t = m.triangles
            n = m.face_normals
            vis = (n @ d) > -0.05          # back-face culling (closed solids)
            t, n = t[vis], n[vis]
            shade = 0.40 + 0.60 * np.clip(n @ light, 0, 1)
            base = np.array(matplotlib.colors.to_rgb(FILL[c]))
            if c == 'black':
                base = np.array([0.30, 0.31, 0.34])
            cc = np.clip(base[None, :] * shade[:, None] * 1.2, 0, 1)
            tris += list(t)
            cols += [tuple(x) + (1.0,) for x in cc]
        h = max(mm.bounds[1, 2] for _, mm in posed)
        g = it['geom']
        lab.append((it['name'], np.array([g.centroid.x, g.centroid.y, h + 4.0])))
    if L.get('tower_xy'):
        tx, ty = L['tower_xy']
        bg.append(np.array([[tx, ty, 0], [tx + 35, ty, 0], [tx + 35, ty + 30, 0], [tx, ty + 30, 0]], float))
        bgc.append((0.72, 0.70, 0.88, 1.0))
    T = np.asarray(tris)
    depth = (T.mean(axis=1) @ d)
    order = np.argsort(depth)            # far (small) first
    P2 = np.stack([T @ right, T @ up], axis=-1)[order]
    C = np.asarray(cols)[order]
    fig, ax = plt.subplots(figsize=size)
    B2 = [np.stack([q @ right, q @ up], -1) for q in bg]
    ax.add_collection(PolyCollection(B2, facecolors=bgc, edgecolors=['#777'] + ['#5a4fa0'] * (len(bg) - 1), linewidths=0.6))
    ax.add_collection(PolyCollection(P2, facecolors=C, edgecolors=C, linewidths=0.15))
    P2 = np.concatenate([P2.reshape(-1, 2), np.concatenate(B2)])
    allp = P2.reshape(-1, 2)
    ax.set_xlim(allp[:, 0].min() - 5, allp[:, 0].max() + 5)
    ax.set_ylim(allp[:, 1].min() - 5, allp[:, 1].max() + 12)
    if labels:
        for name, p3 in lab:
            ax.text(p3 @ right, p3 @ up, name, fontsize=6.5, ha='center', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#888', lw=0.4, alpha=0.85))
    ax.set_aspect('equal')
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=9)
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.95 if title else 0.99)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format='png')
    plt.close(fig)
    if path:
        with open(path, 'wb') as f:
            f.write(buf.getvalue())
    return buf.getvalue()


def _square(png, px):
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((px, px), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, format='PNG')
    return b.getvalue()


def render_all(layouts, cache, out_dir):
    d = os.path.join(out_dir, 'preview')
    os.makedirs(d, exist_ok=True)
    thumbs = {}
    for key, L in layouts.items():
        title = f"{key}  {L['plate']['name']}"
        top_view(L, cache, os.path.join(d, f'{key}_top.png'), title)
        iso_view(L, cache, os.path.join(d, f'{key}_iso.png'), title)
        th = iso_view(L, cache, None, None, size=(6, 6), dpi=100, labels=False)
        thumbs[key] = dict(big=_square(th, 512), small=_square(th, 128))
        print('rendered', key)
    return thumbs
