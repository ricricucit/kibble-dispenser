#!/usr/bin/env python3
"""
Build the static site so it always reflects the repository.

Run from anywhere:  python site/build.py [OUTPUT_DIR]
OUTPUT_DIR defaults to site/_build (not committed). The site shows only the current design (hardware 6.4: chassis
6.4 and electronics module case 1.0), at stable URLs. The script:
  - copies site/ (css, js, img, vendored three.js, the assembly wizard site/assembly/) into the output folder
  - home page <out>/index.html, print guide print/ (site/printguide.py, from hardware/plates/), module page module/
    (site/modulepage.py) and manual page manual/ (docs/manual/ and hardware/template/), in English, Italian and
    German: site/pages.py with the texts in site/content/
  - copies the bench photos of the home page from docs/photos/ into <out>/photos/, with smaller previews in
    <out>/photos/thumb/ when Pillow is installed (the originals otherwise)
  - every footer shows the hardware, firmware and product versions (site/versions.py) and the build commit
  - full-screen 3D page <out>/3d/ from hardware/assembly/ with site/viewer/make_viewer.py (decimated meshes as
    separate STL files, three.js r128 from site/vendor/three-r128/); bought-parts page <out>/parts/
    (hardware/bom.json, chassis and module) with site/bom.py
The 3D page needs numpy, and fast_simplification to decimate the meshes (without it the full
meshes are used): pip install numpy fast_simplification. Everything else is standard library.
"""
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SITE / '_build'
REPO = 'https://github.com/ricricucit/kibble-dispenser'


def copy_photos(names):
    """Copy the photos to <out>/photos/ and write previews to <out>/photos/thumb/ (Pillow) or copy them there."""
    src, dst, thumbs = ROOT / 'docs/photos', OUT / 'photos', OUT / 'photos/thumb'
    thumbs.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
        print('Pillow not installed: the photos use the full-size images')
    for name in names:
        f = src / name
        if not f.exists():
            sys.exit(f'{f.relative_to(ROOT)} not found')
        shutil.copy2(f, dst / name)
        if Image:
            with Image.open(f) as im:
                im.thumbnail((640, 640))
                im.save(thumbs / name, quality=80, optimize=True, progressive=True)
        else:
            shutil.copy2(f, thumbs / name)


LINKS_CURRENT = [
    {'href': '../', 'label': {'en': 'Project home', 'it': 'Pagina del progetto', 'de': 'Projektseite'}},
    {'href': '../print/', 'label': {'en': 'Print guide', 'it': 'Guida di stampa', 'de': 'Druckanleitung'}},
    {'href': '../parts/', 'label': {'en': 'Bought parts', 'it': 'Pezzi extra', 'de': 'Zukaufteile'}},
    {'href': '../module/', 'label': {'en': 'Electronics module', 'it': 'Modulo elettronica', 'de': 'Elektronikmodul'}},
    {'href': '../assembly/', 'label': {'en': 'Assembly guide', 'it': 'Guida al montaggio', 'de': 'Montageanleitung'}},
    {'href': '../manual/', 'label': {'en': 'Manual', 'it': 'Manuale', 'de': 'Handbuch'}},
    {'href': f'{REPO}/tree/main/hardware', 'label': {'en': 'Files on GitHub', 'it': 'File su GitHub', 'de': 'Dateien auf GitHub'}},
]
# 3D page: (manifest, output folder, path to the site root, links, face cap per part, mesh budget MB, extra page data)
VIEWERS = [
    ('hardware/assembly/v64_viewer.json', '3d', '../', LINKS_CURRENT, 30000, 24.0, {}),
]


def design_pages():
    """Full-screen 3D page 3d/ and bought-parts page parts/."""
    sys.path.insert(0, str(SITE / 'viewer'))
    sys.path.insert(0, str(SITE))
    try:
        import make_viewer
        import versions
    except ImportError as e:
        sys.exit(f'the 3D pages need numpy ({e}): pip install numpy fast_simplification')
    import bom
    if make_viewer.fast_simplification is None:
        print('fast_simplification not installed: the 3D pages use the full meshes')
    ver = versions.load()
    for manifest, folder, root, links, max_faces, budget, extra in VIEWERS:
        page = OUT / folder
        page.mkdir(parents=True)
        print(make_viewer.build(str(ROOT / manifest), str(page / 'index.html'), max_faces=max_faces, budget_mb=budget,
                                mesh_dir=str(page / 'meshes'), mesh_url='meshes/', three_src=f'{root}vendor/three-r128/three.min.js',
                                extra={'links': links, 'version': versions.viewer_data(ver), **extra}))
    for design, cfg in bom.DESIGNS.items():
        parts = OUT / cfg['page']
        parts.mkdir(parents=True, exist_ok=True)
        (parts / 'index.html').write_text(bom.render_page(bom.load(design), versions.html_line(ver)), encoding='utf-8')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    skip = {'build.py', 'bom.py', 'pages.py', 'printguide.py', 'modulepage.py', 'versions.py', 'content', 'viewer', '_build',
            '__pycache__', OUT.name}
    shutil.copytree(SITE, OUT, ignore=lambda d, names: [n for n in names if n in skip or n.endswith('.pyc')])
    sys.path.insert(0, str(SITE))
    import pages
    copy_photos([name for name, _ in pages.BENCH])
    design_pages()
    pages.build(OUT)
    n = sum(1 for f in OUT.rglob('*') if f.is_file())
    print(f'site built in {OUT} ({n} files)')


if __name__ == '__main__':
    main()
