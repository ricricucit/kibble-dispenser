#!/usr/bin/env python3
"""Build an interactive 3D viewer page (modes "Workshop" and "In the woods") from a parts manifest.

Usage:
    python make_viewer.py manifest.json out.html [--max-faces 10000] [--budget-mb 9.0]
           [--mesh-dir DIR --mesh-url PREFIX] [--three-src URL]

Two output modes:
  - embedded (default): one self-contained HTML file with every mesh inside as base64, for previews;
  - by URL (--mesh-dir): every decimated mesh is written as a binary STL file <id>.<hash>.stl in DIR,
    and the page fetches it from PREFIX + file name. The project site uses this mode.
--three-src sets where the page loads three.js r128 (the UMD build three.min.js) from: the cdnjs URL by
default, a local copy on the site (site/vendor/three-r128/three.min.js).

Manifest (only parts[].id/name/file/color are required). Every text field (title, subtitle,
status_short (shown in the control sheet header, also on phones), group
labels, part name, label and material, link labels) is a string or {"en": ..., "it": ..., "de": ...};
the page shows the language picked by ?lang=, the visitor's last choice or the browser, else English.
{
  "title": "...", "subtitle": "...", "status_short": "...", "units": "mm", "frame": "Z-up, shaft axis x=y=0", "rotation_axis_xy": [0, 0],
  "groups": {"struttura": {"en": "Structure", "it": "Struttura", "de": "Struktur"}, ...},
  "parts": [{"id", "name", "file", "color", "opacity", "group", "material", "qty",
             "bought", "explode": [dx, dy, dz], "rotates", "ghost", "label"}],
  "scene": {"shelf_underside_z", "shelf_thickness", "shelf_hole_xy", "shelf_hole_d",
            "outlet_xyz", "outlet_dir", "table_top_z"},
  "kibble_path": [[x, y, z], ...],
  "links": [{"href": "...", "label": "..."}]
}
All STL files are expected in assembled position, in the manifest frame (Z up, mm); relative paths
are relative to the manifest. Needs numpy; fast_simplification (decimation) and trimesh (ASCII STL)
are optional.
"""
import argparse
import base64
import hashlib
import html
import json
import math
import os
import re
import struct
import sys

import numpy as np

try:
    import fast_simplification
except ImportError:  # decimation is skipped when the library is missing
    fast_simplification = None
try:
    import trimesh
except ImportError:
    trimesh = None

HERE = os.path.dirname(os.path.abspath(__file__))
THREE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

DEFAULT_GROUPS = {
    "struttura": {"en": "Structure", "it": "Struttura", "de": "Struktur"},
    "dosatore": {"en": "Dosing", "it": "Dosatore", "de": "Dosierung"},
    "trasmissione": {"en": "Drive", "it": "Trasmissione", "de": "Antrieb"},
    "elettronica": {"en": "Electronics", "it": "Elettronica", "de": "Elektronik"},
    "guarnizioni": {"en": "Seals", "it": "Guarnizioni", "de": "Dichtungen"},
    "ferramenta": {"en": "Fasteners", "it": "Ferramenta", "de": "Befestigung"},
}
# Keyword -> group, used when a part has no "group" field. Order matters.
KEYWORD_GROUPS = [
    (("guarniz", "oring", "o-ring", "valvola", "labbro", "tpu", "gasket", "seal"), "guarnizioni"),
    (("servo", "esp32", "esp", "breadboard", "pcb", "batter", "cavo", "regolat", "elettron", "speaker", "led"), "elettronica"),
    (("vite", "viti", "screw", "inserto", "insert", "dado", "rondella", "bullone", "nut", "washer"), "ferramenta"),
    (("disco", "piastra", "dosat", "linguetta", "ghiera"), "dosatore"),
    (("albero", "mozzo", "passante", "culla", "ingran", "trasm", "pignone", "gear", "shaft"), "trasmissione"),
]
DEFAULT_MATERIAL = {
    "struttura": "PETG",
    "dosatore": "PETG",
    "trasmissione": "PETG",
    "elettronica": {"en": "component", "it": "componente", "de": "Bauteil"},
    "guarnizioni": "TPU 95A",
    "ferramenta": {"en": "stainless steel A2", "it": "acciaio inox A2", "de": "Edelstahl A2"},
}
# Extra vertical push per group for the default explode vectors (mm).
GROUP_Z_BIAS = {
    "struttura": 0.0,
    "dosatore": 35.0,
    "trasmissione": -45.0,
    "elettronica": -80.0,
    "guarnizioni": 20.0,
    "ferramenta": 55.0,
}


def die(msg):
    print("make_viewer: " + msg, file=sys.stderr)
    sys.exit(1)


def load_stl(path):
    """Return (vertices Nx3 float64, faces Mx3 int) with duplicate vertices merged."""
    data = open(path, "rb").read()
    tris = None
    if len(data) >= 84:
        n = struct.unpack_from("<I", data, 80)[0]
        if 84 + n * 50 == len(data):
            rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
            tris = np.frombuffer(data, dtype=rec, count=n, offset=84)["v"].astype(np.float64)
    if tris is None:
        if trimesh is None:
            die("ASCII STL needs trimesh: " + path)
        m = trimesh.load(path, file_type="stl", force="mesh")
        tris = np.asarray(m.triangles, dtype=np.float64)
    if len(tris) == 0:
        die("empty STL: " + path)
    flat = tris.reshape(-1, 3)
    # Merge identical vertices (quantised to 1 micron) so decimation sees a connected mesh.
    q = np.round(flat * 1000.0).astype(np.int64)
    uniq, inverse = np.unique(q, axis=0, return_inverse=True)
    verts = np.zeros((len(uniq), 3))
    np.add.at(verts, inverse.reshape(-1), flat)
    counts = np.bincount(inverse.reshape(-1), minlength=len(uniq)).reshape(-1, 1)
    verts /= counts
    faces = inverse.reshape(-1, 3)
    # Drop degenerate faces created by the merge.
    ok = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    return verts, faces[ok]


def cluster_vertices(verts, faces, cell):
    """Merge vertices closer than `cell` mm; drop degenerate faces and cancel coincident face pairs."""
    q = np.round(verts / cell).astype(np.int64)
    uniq, inv = np.unique(q, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    nv = np.zeros((len(uniq), 3))
    np.add.at(nv, inv, verts)
    nv /= np.bincount(inv)[:, None]
    nf = inv[faces]
    ok = (nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])
    nf = nf[ok]
    srt = np.sort(nf, axis=1)
    _, first, inv2, cnt = np.unique(srt, axis=0, return_index=True, return_inverse=True, return_counts=True)
    inv2 = inv2.reshape(-1)
    keep = (cnt[inv2] % 2 == 1) & (np.arange(len(nf)) == first[inv2])
    return nv, nf[keep]


def decimate(verts, faces, max_faces):
    """Quadric decimation to <= max_faces. CAD tessellations full of sliver fans make the
    quadric collapse stall, so when that happens vertices are first clustered on a tiny grid
    (0.01..0.15 mm, invisible at print scale) and the decimation is retried."""
    if len(faces) <= max_faces or fast_simplification is None:
        return verts, faces

    def simp(v, f):
        if len(f) <= max_faces:
            return v, f
        v2, f2 = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int64), target_count=int(max_faces * 0.98))
        if len(f2) == 0:
            return v, f
        return np.asarray(v2, dtype=np.float64), np.asarray(f2, dtype=np.int64)

    want_closed = is_closed(verts, faces)
    best = simp(verts, faces)
    if len(best[1]) <= max_faces:
        return best
    for cell in (0.01, 0.02, 0.04, 0.08, 0.15):
        vc, fc = cluster_vertices(verts, faces, cell)
        if len(fc) < 4:
            break
        vc, fc = simp(vc, fc)
        if want_closed and not is_closed(vc, fc):
            continue
        if len(fc) < len(best[1]):
            best = (vc, fc)
        if len(fc) <= max_faces:
            break
    return best


def is_closed(verts, faces):
    """True when every edge is shared by an even number of faces: enough for stencil section caps."""
    if len(faces) == 0:
        return False
    e = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, c = np.unique(e, axis=0, return_counts=True)
    return bool(np.all(c % 2 == 0))


def stl_bytes(verts, faces):
    tri = verts[faces].astype(np.float32)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = (n / ln).astype(np.float32)
    rec = np.zeros(len(faces), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"] = n
    rec["v"] = tri
    header = b"kibble viewer".ljust(80, b" ")
    return header + struct.pack("<I", len(faces)) + rec.tobytes()


def b64_size(nfaces):
    return int(math.ceil((84 + 50 * nfaces) / 3.0) * 4)


def stl_size(nfaces):
    return 84 + 50 * nfaces


def text(v):
    """A manifest text: a plain string, or a dict of language code -> string (kept as is)."""
    if isinstance(v, dict):
        return {str(k): str(x) for k, x in v.items() if x is not None}
    return "" if v is None else str(v)


def first_text(v, default=""):
    """English (or the first) value of a manifest text, for places that need one plain string."""
    if isinstance(v, dict):
        return str(v.get("en") or next(iter(v.values()), default))
    return str(v) if v else default


def infer_group(pid):
    s = pid.lower()
    for keys, g in KEYWORD_GROUPS:
        if any(k in s for k in keys):
            return g
    return "struttura"


def vec3(v, default):
    if isinstance(v, (list, tuple)) and len(v) >= 3:
        try:
            return [float(v[0]), float(v[1]), float(v[2])]
        except (TypeError, ValueError):
            pass
    return list(default)


def vec2(v, default):
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        try:
            return [float(v[0]), float(v[1])]
        except (TypeError, ValueError):
            pass
    return list(default)


def build(manifest, out, max_faces=10000, budget_mb=9.0, template=None, mesh_dir=None, mesh_url="",
          three_src=THREE_CDN, extra=None):
    """Write the viewer page `out` from `manifest` (path). With `mesh_dir`, meshes go there as STL files
    referenced as mesh_url + file name; otherwise they are embedded. `extra` is merged into the page data
    (for example {"links": [...]}). Returns a short summary string."""
    man = json.load(open(manifest, encoding="utf-8"))
    base_dir = os.path.dirname(os.path.abspath(manifest))
    raw_parts = man.get("parts") or []
    if not raw_parts:
        die("manifest has no parts")

    groups = dict(DEFAULT_GROUPS)
    groups.update({k: text(v) for k, v in (man.get("groups") or {}).items()})
    axis = vec2(man.get("rotation_axis_xy"), [0.0, 0.0])

    # ---- load meshes -------------------------------------------------------
    loaded = []
    seen = set()
    for i, p in enumerate(raw_parts):
        for k in ("id", "name", "file", "color"):
            if not p.get(k):
                die("part #%d is missing '%s'" % (i, k))
        if p["id"] in seen:
            die("duplicate part id: " + p["id"])
        seen.add(p["id"])
        f = p["file"] if os.path.isabs(p["file"]) else os.path.join(base_dir, p["file"])
        if not os.path.exists(f):
            die("missing STL for %s: %s" % (p["id"], f))
        v, fc = load_stl(f)
        loaded.append({"src": p, "v": v, "f": fc, "orig_faces": len(fc)})

    # ---- face caps under the size budget ------------------------------------
    size_of = stl_size if mesh_dir else b64_size
    caps = [min(len(L["f"]), max_faces) for L in loaded]
    budget = budget_mb * 1024 * 1024
    for _ in range(30):
        total = sum(size_of(c) for c in caps)
        if total <= budget:
            break
        big = [i for i, c in enumerate(caps) if c > 1500]
        if not big:
            break
        scale = max(0.5, (budget - sum(size_of(caps[i]) for i in range(len(caps)) if i not in big))
                    / max(1.0, sum(size_of(caps[i]) for i in big)))
        for i in big:
            caps[i] = max(1500, int(caps[i] * min(scale, 0.92)))

    parts = []
    all_min = np.array([np.inf] * 3)
    all_max = np.array([-np.inf] * 3)
    for L, cap in zip(loaded, caps):
        v, fc = decimate(L["v"], L["f"], cap)
        L["v"], L["f"] = v, fc
        mn, mx = v[fc.reshape(-1)].min(0), v[fc.reshape(-1)].max(0)
        L["min"], L["max"] = mn, mx
        all_min = np.minimum(all_min, mn)
        all_max = np.maximum(all_max, mx)
    centre = (all_min + all_max) / 2.0
    size = float(np.linalg.norm(all_max - all_min))

    if mesh_dir:
        os.makedirs(mesh_dir, exist_ok=True)
    for L in loaded:
        p = L["src"]
        pid = str(p["id"])
        group = p.get("group") or infer_group(pid)
        if group not in groups:
            groups[group] = group.capitalize()
        c = (L["min"] + L["max"]) / 2.0
        if "explode" in p:
            explode = vec3(p.get("explode"), [0, 0, 0])
        else:
            # Default: push away from the assembly centre (radial in XY, scaled in Z) plus a group bias.
            d = c - centre
            explode = [float(d[0]) * 0.8, float(d[1]) * 0.8, float(d[2]) * 1.1 + GROUP_Z_BIAS.get(group, 0.0)]
        rotates = p.get("rotates")
        if rotates is None:
            rotates = any(k in pid.lower() for k in ("disco", "albero", "mozzo"))
        opacity = p.get("opacity", 1.0)
        try:
            opacity = max(0.02, min(1.0, float(opacity)))
        except (TypeError, ValueError):
            opacity = 1.0
        blob = stl_bytes(L["v"], L["f"])
        entry = {
            "id": pid,
            "name": text(p["name"]),
            "label": text(p.get("label") or p["name"]),
            "color": str(p["color"]),
            "opacity": opacity,
            "group": group,
            "material": text(p.get("material") or DEFAULT_MATERIAL.get(group, "")),
            "qty": int(p.get("qty", 1) or 1),
            "bought": bool(p.get("bought", False)),
            "explode": [round(x, 2) for x in explode],
            "rotates": bool(rotates),
            "ghost": bool(p.get("ghost", group == "struttura")),
            "roughness": float(p.get("roughness", 0.5)),
            "metalness": float(p.get("metalness", 0.05)),
            "closed": is_closed(L["v"], L["f"]),
            "faces": int(len(L["f"])),
            "faces_orig": int(L["orig_faces"]),
            "bbox": [[round(float(x), 2) for x in L["min"]], [round(float(x), 2) for x in L["max"]]],
        }
        if mesh_dir:
            fname = "%s.%s.stl" % (re.sub(r"[^A-Za-z0-9_.-]+", "_", pid), hashlib.sha1(blob).hexdigest()[:10])
            with open(os.path.join(mesh_dir, fname), "wb") as fh:
                fh.write(blob)
            entry["url"] = mesh_url + fname
            entry["bytes"] = len(blob)
        else:
            entry["stl"] = base64.b64encode(blob).decode("ascii")
        parts.append(entry)

    # ---- scene defaults ------------------------------------------------------
    sc = man.get("scene") or {}
    kp = man.get("kibble_path")
    kibble_path = None
    if isinstance(kp, list):
        pts = [vec3(q, None) for q in kp if isinstance(q, (list, tuple)) and len(q) >= 3]
        if len(pts) >= 2:
            kibble_path = pts
    if sc.get("outlet_xyz") is not None:
        outlet = vec3(sc.get("outlet_xyz"), [axis[0], axis[1], float(all_min[2])])
    elif kibble_path:
        outlet = list(kibble_path[-1])
    else:
        outlet = [float(centre[0]), float(centre[1]), float(all_min[2])]
    scene = {
        "shelf_underside_z": float(sc.get("shelf_underside_z", float(all_max[2]))),
        "shelf_thickness": float(sc.get("shelf_thickness", 40.0)),
        "shelf_hole_xy": vec2(sc.get("shelf_hole_xy"), axis),
        "shelf_hole_d": float(sc.get("shelf_hole_d", 76.0)),
        "outlet_xyz": outlet,
        "outlet_dir": vec3(sc.get("outlet_dir"), [0.0, 0.0, -1.0]),
        "table_top_z": float(sc.get("table_top_z", 750.0)),
    }

    data = {
        "title": text(man.get("title") or "Kibble Dispenser"),
        "subtitle": text(man.get("subtitle") or ""),
        "status_short": text(man.get("status_short") or ""),
        "units": str(man.get("units") or "mm"),
        "frame": str(man.get("frame") or ""),
        "axis": axis,
        "groups": groups,
        "groupOrder": [g for g in groups if any(p["group"] == g for p in parts)],
        "parts": parts,
        "scene": scene,
        "kibble_path": kibble_path,
        "bbox": [[round(float(x), 2) for x in all_min], [round(float(x), 2) for x in all_max]],
        "links": [{"href": str(q.get("href", "")), "label": text(q.get("label"))}
                  for q in (man.get("links") or []) if isinstance(q, dict)],
    }
    data.update(extra or {})

    tpl = open(template or os.path.join(HERE, "template.html"), encoding="utf-8").read()
    marker = "/*__DATA__*/null"
    if marker not in tpl:
        die("template has no data marker")
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    page_title = man.get("page_title") or first_text(man.get("title"), "Kibble Dispenser") + " 3D"
    page = (tpl.replace("__PAGE_TITLE__", html.escape(page_title))
            .replace("__THREE_SRC__", html.escape(three_src, quote=True)).replace(marker, payload))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)

    tot_faces = sum(p["faces"] for p in parts)
    mesh_bytes = sum(p.get("bytes", 0) for p in parts)
    return "viewer: %s  %.2f MB page%s  %d parts  %d faces (from %d)  closed %d/%d  size %.0f mm" % (
        out, len(page.encode("utf-8")) / 1048576.0,
        "  + %.2f MB meshes in %s" % (mesh_bytes / 1048576.0, mesh_dir) if mesh_dir else "",
        len(parts), tot_faces, sum(p["faces_orig"] for p in parts), sum(1 for p in parts if p["closed"]), len(parts), size)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("out")
    ap.add_argument("--max-faces", type=int, default=10000, help="per-part face cap (default 10000)")
    ap.add_argument("--budget-mb", type=float, default=9.0, help="total budget for the meshes (default 9 MB)")
    ap.add_argument("--template", default=os.path.join(HERE, "template.html"))
    ap.add_argument("--mesh-dir", help="write the meshes as STL files into this folder instead of embedding them")
    ap.add_argument("--mesh-url", default="", help="URL prefix of --mesh-dir as seen from the page (for example meshes/)")
    ap.add_argument("--three-src", default=THREE_CDN, help="script URL of three.js r128 (three.min.js)")
    args = ap.parse_args()
    print(build(args.manifest, args.out, args.max_faces, args.budget_mb, args.template, args.mesh_dir,
                args.mesh_url, args.three_src))


if __name__ == "__main__":
    main()
