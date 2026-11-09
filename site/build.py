#!/usr/bin/env python3
"""
Build the static site so it always reflects the repository.

Run from anywhere:  python site/build.py [OUTPUT_DIR]
OUTPUT_DIR defaults to site/_build (not committed). The script:
  - copies site/ (pages, css, js, vendored three.js) into the output folder
  - copies hardware/assembly/* (meshes and assembly.json) into <out>/assembly/
  - copies the selected process photos from docs/photos/ into <out>/photos/, with smaller
    previews in <out>/photos/thumb/ when Pillow is installed (the originals otherwise)
  - fills the printed-parts list and the photo strip in index.html from assembly.json
    and the captions in docs/photos/README.md
  - design v6: writes the full-screen 3D page <out>/v6/3d/ with site/viewer/make_viewer.py from
    hardware/v6/assembly/ (decimated meshes as separate STL files, three.js r128 from site/vendor/three-r128/),
    and the bought-parts page <out>/v6/parts/ from hardware/v6/bom.json (site/bom.py)
The v6 3D page needs numpy, and fast_simplification to decimate the meshes (without it the full
meshes are used): pip install numpy fast_simplification. Everything else is standard library.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SITE / '_build'
REPO = 'https://github.com/ricricucit/kibble-dispenser'
STATUS = {'designed': 'Designed, ready to print', 'bought': 'Bought', 'reused': 'Reused',
          'to design': 'Not designed yet'}

# Photos for the strip, in story order. Captions come from docs/photos/README.md.
PHOTOS = [
    '2026-07-04-servo-25kg-front.jpg',
    '2026-07-04-servo-25kg-three-quarter.jpg',
    '2026-07-04-aluminium-25t-clamp-horn.jpg',
    '2026-07-04-disc-v1-mockup-with-star-horn.jpg',
    'freenove-esp32-cam-board-breadboard-wiring.jpg',
    'bowl-upside-down-with-spout-on-plywood.jpg',
    '2026-10-04-bowl-with-spout-cover-removed.jpg',
    '2026-10-04-bowl-top-view-spout-opened.jpg',
    '2026-10-04-empty-bowl-on-box-lid.jpg',
    '2026-10-04-orange-disc-in-bowl-on-box.jpg',
    '2026-10-04-box-disc-and-bowl-laid-out.jpg',
    '2026-10-04-disc-lifted-out-cat-inspecting.jpg',
]

esc = html.escape


def captions():
    text = (ROOT / 'docs/photos/README.md').read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'^- `([^`]+)`: (.+)$', text, flags=re.M):
        cap = m.group(2).strip()
        out[m.group(1)] = cap[:1].upper() + cap[1:]
    return out


def photos_html():
    caps = captions()
    src, dst, thumbs = ROOT / 'docs/photos', OUT / 'photos', OUT / 'photos/thumb'
    thumbs.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
        print('Pillow not installed: the photo strip uses the full-size images')
    items = []
    for name in PHOTOS:
        f = src / name
        if not f.exists():
            print(f'warning: {f.relative_to(ROOT)} not found, skipped')
            continue
        shutil.copy2(f, dst / name)
        w = h = None
        if Image:
            with Image.open(f) as im:
                im.thumbnail((640, 640))
                im.save(thumbs / name, quality=80, optimize=True, progressive=True)
                w, h = im.size
        else:
            shutil.copy2(f, thumbs / name)
        cap = esc(caps.get(name, name))
        size = f' width="{w}" height="{h}"' if w else ''
        items.append(
            f'<li><figure><a href="photos/{esc(name)}" data-lightbox>'
            f'<img src="photos/thumb/{esc(name)}"{size} loading="lazy" decoding="async" alt="{cap}"></a>'
            f'<figcaption>{cap}</figcaption></figure></li>')
    return '<ul class="photos">\n' + '\n'.join(items) + '\n</ul>'


def parts_html(data):
    spool_colour = {p['spool']: p['colour'] for p in data['parts'] if p.get('spool')}
    rows = []
    for p in sorted(data['parts'], key=lambda q: q['bom']) + data.get('not_shown', []):
        in_view = 'file' in p
        colour = p.get('colour') or spool_colour.get(p.get('spool'), '#26282c')
        badge = (f'<span class="balloon static" title="Item {p["bom"]} in the model" aria-hidden="true">{p["bom"]}</span>'
                 if in_view else '<span class="no-balloon" aria-hidden="true"></span>')
        links = []
        for kind, folder in (('STL for printing', 'stl'), ('3MF', '3mf')):
            ext = 'stl' if folder == 'stl' else '3mf'
            if (ROOT / 'hardware' / folder / f"{p['id']}.{ext}").exists():
                links.append(f'<a href="{REPO}/blob/main/hardware/{folder}/{esc(p["id"])}.{ext}">{kind}</a>')
        if in_view:
            links.append(f'<button type="button" class="show" data-show="{esc(p["id"])}">Show in model</button>')
        if not links:
            links.append('<span>No files yet</span>')
        rows.append(
            f'<li class="bom-row">{badge}'
            f'<div class="bom-name"><h3>{esc(p["name"])}</h3><code>{esc(p["id"])}</code></div>'
            f'<p class="bom-spool"><span class="spool" style="--c:{esc(colour)}" aria-hidden="true"></span>'
            f'{esc(p.get("material", ""))}, {esc(p.get("spool", ""))} spool</p>'
            f'<p class="bom-desc">{esc(p["description"])}</p>'
            f'<p class="bom-status">{esc(STATUS.get(p["status"], p["status"]))}</p>'
            f'<p class="bom-files">{" ".join(links)}</p></li>')
    return '<ol class="bom">\n' + '\n'.join(rows) + '\n</ol>'


V6_LINKS = [
    {'href': '../../', 'label': {'en': 'Project home', 'it': 'Pagina del progetto', 'de': 'Projektseite'}},
    {'href': '../parts/', 'label': {'en': 'Bought parts', 'it': 'Pezzi extra', 'de': 'Zukaufteile'}},
    {'href': f'{REPO}/tree/main/hardware/v6', 'label': {'en': 'Files on GitHub', 'it': 'File su GitHub', 'de': 'Dateien auf GitHub'}},
]


def v6_pages():
    """Full-screen 3D page and bought-parts page of design v6."""
    sys.path.insert(0, str(SITE / 'viewer'))
    sys.path.insert(0, str(SITE))
    try:
        import make_viewer
    except ImportError as e:
        sys.exit(f'the v6 3D page needs numpy ({e}): pip install numpy fast_simplification')
    import bom
    if make_viewer.fast_simplification is None:
        print('fast_simplification not installed: the v6 3D page uses the full meshes')
    page = OUT / 'v6/3d'
    page.mkdir(parents=True)
    print(make_viewer.build(str(ROOT / 'hardware/v6/assembly/v6_viewer.json'), str(page / 'index.html'),
                            mesh_dir=str(page / 'meshes'), mesh_url='meshes/',
                            three_src='../../vendor/three-r128/three.min.js', extra={'links': V6_LINKS}))
    parts = OUT / 'v6/parts'
    parts.mkdir(parents=True)
    (parts / 'index.html').write_text(bom.render_page(bom.load()), encoding='utf-8')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    skip = {'build.py', 'bom.py', 'viewer', '_build', '__pycache__', OUT.name}
    shutil.copytree(SITE, OUT, ignore=lambda d, names: [n for n in names if n in skip or n.endswith('.pyc')])
    shutil.copytree(ROOT / 'hardware/assembly', OUT / 'assembly')
    data = json.loads((OUT / 'assembly/assembly.json').read_text(encoding='utf-8'))
    for p in data['parts']:
        if not (OUT / 'assembly' / p['file']).exists():
            sys.exit(f"missing mesh hardware/assembly/{p['file']}")
    page = OUT / 'index.html'
    s = page.read_text(encoding='utf-8')
    for marker, content in (('parts', parts_html(data)), ('photos', photos_html())):
        token = f'<!-- @{marker} -->'
        if token not in s:
            sys.exit(f'{token} not found in site/index.html')
        s = s.replace(token, content)
    page.write_text(s, encoding='utf-8')
    v6_pages()
    n = sum(1 for f in OUT.rglob('*') if f.is_file())
    print(f'site built in {OUT} ({n} files)')


if __name__ == '__main__':
    main()
