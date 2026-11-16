#!/usr/bin/env python3
"""
Home page and manual page of the website, in English, Italian and German; shared helpers for the print guide
(site/printguide.py) and the module page (site/modulepage.py).

site/build.py calls build(out) after copying site/ to the output folder. It writes:
  <out>/index.html            home page, texts from site/content/home.toml
  <out>/print/                the step-by-step print guide (site/printguide.py, from hardware/plates/)
  <out>/module/               the electronics module page (site/modulepage.py)
  <out>/manual/               the manuals (A6 booklet and A4 print version per language, docs/manual/) and the
                              drilling template (hardware/template/), texts from home.toml [manual]
The site shows only the current design. Grams, times, plates, parts and file names come from
hardware/plates/summary.json. Every text is written once per language; the language switch (js/lang.js) shows one
of them. Standard library only; Pillow is optional.
"""
import html
import json
import sys
import re
import shutil
import tomllib
import zipfile
from pathlib import Path

import versions

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
CURRENT = 'v6.4'
PLATES = ROOT / 'hardware/plates'               # print package of the current design (chassis 6.4 + module case 1.0)
REPO = 'https://github.com/ricricucit/kibble-dispenser'
LANGS = ('en', 'it', 'de')
LANG_NAMES = {'en': 'English', 'it': 'Italiano', 'de': 'Deutsch'}
MANUALS = ROOT / 'docs/manual'
TEMPLATE_PDF = ROOT / 'hardware/template/dima_foratura_v64.pdf'
TEMPLATE_NAME = 'kibble-dispenser-drilling-template.pdf'

NAV_HOME = {'en': 'Project home', 'it': 'Pagina del progetto', 'de': 'Projektseite'}
COLOUR_VAR = {'black': 'var(--petg-black)', 'orange': 'var(--orange)', 'green': 'var(--green)', 'yellow': 'var(--tpu)'}
# bench photos on the home page (docs/photos/, thumbnails made by build.py)
BENCH = [('2026-11-08-bench-wrover-breadboard-servo-overview.jpg', 'overview'),
         ('2026-11-08-breadboard-servo-speaker-buttons.jpg', 'buttons'),
         ('2026-10-04-orange-disc-in-bowl-on-box.jpg', 'disc')]

esc = html.escape


# ---------------------------------------------------------------- helpers
def load_toml(name):
    with open(SITE / 'content' / name, 'rb') as f:
        return tomllib.load(f)


def per_lang(texts):
    """A dict {en, it, de}, a callable lang -> text, or a plain string (same in every language)."""
    if callable(texts):
        return {lang: texts(lang) for lang in LANGS}
    if isinstance(texts, str):
        return {lang: texts for lang in LANGS}
    return {lang: texts.get(lang, texts['en']) for lang in LANGS}


def L(texts):
    """Escaped text, one <span> per language; CSS shows the current one."""
    t = per_lang(texts)
    return ''.join(f'<span data-l="{lang}" lang="{lang}">{esc(t[lang])}</span>' for lang in LANGS)


def Lh(texts):
    """Like L() for texts that already are HTML."""
    t = per_lang(texts)
    return ''.join(f'<span data-l="{lang}" lang="{lang}">{t[lang]}</span>' for lang in LANGS)


def num(x, lang, nd=0):
    s = f'{x:,.{nd}f}'
    if lang != 'en':
        s = s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')
    return s


def hours(minutes):
    h, m = divmod(int(minutes), 60)            # whole minutes, as time_hm in summary.json and the print guides
    return f'{h} h {m:02d} min' if h else f'{m} min'


def size_text(nbytes, lang):
    mb = nbytes / 1e6
    return f'{num(mb, lang, 1)} MB' if mb >= 0.1 else f'{num(nbytes / 1e3, lang)} kB'


def alt_attrs(texts):
    """alt in English plus data-alt-<lang>; js/lang.js swaps the alt with the language."""
    t = per_lang(texts)
    return f'alt="{esc(t["en"])}" ' + ' '.join(f'data-alt-{lang}="{esc(t[lang])}"' for lang in LANGS)


def lang_switch():
    return ('<div class="lang-switch" role="group" aria-label="Language / Lingua / Sprache">'
            + ''.join(f'<button type="button" data-set-lang="{lang}" lang="{lang}" aria-pressed="{str(lang == "en").lower()}">'
                      f'{lang.upper()}</button>' for lang in LANGS) + '</div>')


GITHUB_SVG = ('<svg viewBox="0 0 16 16" aria-hidden="true" width="16" height="16"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 '
              '3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13'
              '-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
              '0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 '
              '2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 '
              '1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' "
           "fill='%23ee6a1f'/%3E%3Cpath d='M13.5 13h5l3.5 15h-12z' fill='%23fff'/%3E%3Ccircle cx='16' cy='16' r='2.6' fill='%2326282c'/%3E%3C/svg%3E")


def page(*, root, titles, description, nav, body, footer, cls, og_image=None):
    """Common shell: head, masthead with section links and language switch, footer."""
    t = per_lang(titles)
    data_titles = ' '.join(f'data-title-{lang}="{esc(t[lang])}"' for lang in LANGS)
    links = ''.join(f'<li><a href="{esc(href)}"{" data-keep-lang" if keep else ""}>{L(label)}</a></li>'
                    for href, label, keep in nav)
    og = (f'\n  <meta property="og:image" content="https://ricricucit.github.io/kibble-dispenser/{og_image}">'
          if og_image else '')
    return f'''<!doctype html>
<html lang="en" data-lang="en" {data_titles}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(t['en'])}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#e1e6e5" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121a1f" media="(prefers-color-scheme: dark)">
  <meta property="og:title" content="{esc(t['en'])}">
  <meta property="og:description" content="{esc(description)}">{og}
  <link rel="icon" href="{FAVICON}">
  <link rel="stylesheet" href="{root}css/site.css">
  <link rel="stylesheet" href="{root}css/home.css">
  <script src="{root}js/lang.js" defer></script>
  <script src="{root}js/home.js" defer></script>
</head>
<body class="{cls}">
  <a class="skip" href="#main">{L({'en': 'Skip to content', 'it': 'Vai al contenuto', 'de': 'Zum Inhalt'})}</a>
  <header class="mast">
    <p class="wordmark"><a href="{root}" data-keep-lang><span class="mark" aria-hidden="true"></span>Kibble Dispenser</a></p>
    <nav class="mast-nav" aria-label="Sections"><ul>{links}</ul></nav>
    {lang_switch()}
    <a class="mast-gh" href="{REPO}" aria-label="GitHub">{GITHUB_SVG}<span>GitHub</span></a>
  </header>
  <main id="main">
{body}
  </main>
{footer}
</body>
</html>
'''


def footer_html(root, H):
    f = H['footer']
    return f'''  <footer class="foot">
    <dl class="tblock">
      <div class="tb-name"><dt>{L({'en': 'Title', 'it': 'Titolo', 'de': 'Titel'})}</dt><dd>{L(f['title'])}</dd></div>
      <div><dt>{L({'en': 'Revision', 'it': 'Revisione', 'de': 'Revision'})}</dt><dd>{L(f['revision'])}</dd></div>
      <div><dt>{L({'en': 'Licences', 'it': 'Licenze', 'de': 'Lizenzen'})}</dt><dd>MIT · CERN-OHL-P-2.0 · CC BY 4.0</dd></div>
      <div><dt>{L({'en': 'Source', 'it': 'Sorgenti', 'de': 'Quellen'})}</dt><dd><a href="{REPO}">github.com/ricricucit/kibble-dispenser</a></dd></div>
    </dl>
    <p class="foot-links">
      <a href="{root}3d/" data-keep-lang>{L({'en': '3D model', 'it': 'Modello 3D', 'de': '3D-Modell'})}</a>
      <a href="{root}print/" data-keep-lang>{L({'en': 'Print files', 'it': 'File di stampa', 'de': 'Druckdateien'})}</a>
      <a href="{root}parts/" data-keep-lang>{L({'en': 'Bought parts', 'it': 'Pezzi da comprare', 'de': 'Zukaufteile'})}</a>
      <a href="{root}assembly/">{L({'en': 'Assembly', 'it': 'Montaggio', 'de': 'Montage'})}</a>
      <a href="{root}manual/" data-keep-lang>{L({'en': 'Manual', 'it': 'Manuale', 'de': 'Handbuch'})}</a>
      <a href="{REPO}">GitHub</a>
    </p>
    <p class="foot-note">{L(f['licence'])} {L(f['privacy'])} © 2026 Enrico Icardi {L({'en': 'and contributors', 'it': 'e contributori', 'de': 'und Mitwirkende'})}</p>
    {versions.html_line(VERSIONS)}
  </footer>'''


# ---------------------------------------------------------------- data
def load_data():
    summary = json.loads((PLATES / 'summary.json').read_text(encoding='utf-8'))
    counts = {'screws': 0, 'inserts': 0, 'orings': 0}
    for h in summary['bought_parts']:
        item = h['item'].lower()
        if 'o-ring' in item:
            counts['orings'] += int(h['qty'])
        elif 'insert' in item:
            counts['inserts'] += int(h['qty'])
        elif 'screw' in item or item.startswith(('m3x', 'st2.9')):
            counts['screws'] += int(h['qty'])
    g = summary['totals']['grams_per_filament']
    grams = {'black': g['PETG black'], 'orange': g['PETG orange'], 'green': g['PETG green'], 'yellow': g['TPU yellow']}
    return summary, counts, grams


# ---------------------------------------------------------------- drawings (inline SVG, drafting style)
def svg_text(x, y, texts, cls='lbl', anchor='start'):
    t = per_lang(texts)
    return ''.join(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" data-l="{lang}">{esc(t[lang])}</text>'
                   for lang in LANGS)


def idea_svg(d):
    """Side view of hardware 6.4: container on a shelf, the flange with the orange ring and the closed pod underneath with
    the electronics module (dashed) and its control panel, the green food path to the bowl, the cable leaving at the back."""
    return f'''<svg class="idea-svg" viewBox="0 0 360 350" role="img" aria-labelledby="idea-svg-t">
  <title id="idea-svg-t">{esc(d['drum']['en'])}, {esc(d['shelf']['en'])}, {esc(d['unit']['en'])}, {esc(d['food']['en'])}, {esc(d['cable']['en'])}</title>
  <defs>
    <pattern id="wood" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0v7" class="hatch"/></pattern>
    <marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 8 4 0 8z" class="ink-fill"/></marker>
    <marker id="arg" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 8 4 0 8z" class="food-fill"/></marker>
  </defs>
  <!-- container on the shelf, its weight goes into the wood -->
  <rect x="50" y="18" width="120" height="128" rx="9" class="drum"/>
  <path d="M50 50h120M50 114h120" class="thin"/>
  <path d="M62 98v42M158 98v42" class="load" marker-end="url(#ar)"/>
  {svg_text(186, 64, d['drum'])}
  {svg_text(186, 112, d['load'], 'lbl dim')}
  <!-- shelf with the hole, legs, ground -->
  <rect x="10" y="146" width="88" height="16" class="wood"/>
  <rect x="122" y="146" width="228" height="16" class="wood"/>
  <path d="M10 146h88M122 146h228M10 162h88M122 162h228" class="ink"/>
  <path d="M22 162v174M338 162v174" class="leg"/>
  <path d="M4 336h352" class="ground"/>
  {svg_text(186, 139, d['shelf'])}
  <path d="M76 177 97 164" class="dimline"/>
  {svg_text(64, 186, d['hole'], 'lbl dim', 'end')}
  <!-- the 12 V cable leaves at the back of the flange, held by a tie, and is clipped along the shelf -->
  <path d="M158 166H232q8 0 8 8v40" class="cable"/>
  <circle cx="186" cy="166" r="1.6" class="ink-fill"/><circle cx="214" cy="166" r="1.6" class="ink-fill"/>
  {svg_text(246, 196, d['cable'], 'lbl dim')}
  <!-- dispenser: two flange plates, the closed pod with the orange ring round its top, flat bottom with the outlet -->
  <rect x="66" y="162" width="92" height="8" class="petg"/>
  <path d="M74 170h76v92q0 12-12 12H86q-12 0-12-12z" class="petg"/>
  <rect x="70" y="172" width="84" height="12" rx="2" class="touch"/>
  <rect x="90" y="272" width="14" height="3" class="tpu"/>
  <path d="M120 218h30v44q0 12-12 12h-18z" class="modline"/>
  <rect x="140" y="232" width="6" height="22" rx="2" class="panel"/>
  <circle cx="143" cy="237" r="1.3" class="led"/><circle cx="143" cy="242" r="1.3" class="led"/><circle cx="143" cy="249" r="2" class="touch"/>
  <path d="M156 236H182" class="dimline"/>
  {svg_text(186, 240, d['unit'])}
  <!-- food path: through the hole and the gate, down inside the pod, out of the outlet -->
  <path d="M110 40V212q0 8-6 12L97 230V308" class="food" marker-end="url(#arg)"/>
  <path d="M100 296H182" class="foodline"/>
  {svg_text(186, 300, d['food'], 'lbl food-t')}
  <!-- bowl -->
  <path d="M73 322q24 13 48 0z" class="bowl"/>
  {svg_text(128, 331, d['bowl'])}
</svg>'''


ICONS = {
    # two-pocket disc seen from above, with the turn arrow
    'disc': '<circle cx="24" cy="24" r="17" class="i-touch"/><path d="M24 24 13 13a15.5 15.5 0 0 1 22 0z" class="i-hole"/>'
            '<path d="M24 24 35 35a15.5 15.5 0 0 1-22 0z" class="i-hole"/><circle cx="24" cy="24" r="2.4" class="i-ink-f"/>'
            '<path d="M41 15a19 19 0 0 1 1 14" class="i-line" marker-end="url(#iar)"/>',
    # coaxial stack: disc, shaft, servo
    'drive': '<rect x="11" y="6" width="26" height="6" rx="1.5" class="i-touch"/><rect x="21" y="12" width="6" height="16" class="i-petg"/>'
             '<path d="M19 18h10M19 23h10" class="i-tpu-l"/><rect x="13" y="28" width="22" height="15" rx="1.5" class="i-servo"/>'
             '<path d="M24 2v44" class="i-axis"/>',
    # shut-off gate: orange ring round a green sector blade, seen from below
    'gate': '<circle cx="24" cy="24" r="19" class="i-touch"/><circle cx="24" cy="24" r="14.5" class="i-hole"/>'
            '<path d="M24 24 24 9.5a14.5 14.5 0 0 1 12.6 21.7z" class="i-chute"/><circle cx="24" cy="24" r="2.2" class="i-ink-f"/>'
            '<circle cx="24" cy="5" r="2.4" class="i-petg"/>',
    # twist and lower
    'twist': '<rect x="9" y="8" width="30" height="5" class="i-petg"/><path d="M13 13h22l-3 14H16z" class="i-petg"/>'
             '<rect x="20" y="17" width="8" height="4" rx="1" class="i-touch"/>'
             '<path d="M8 33a17 6 0 0 0 32 0" class="i-line" marker-end="url(#iar)"/><path d="M24 31v13" class="i-line" marker-end="url(#iar)"/>',
    # closed smooth pod with the orange ring and a hidden chute
    'shell': '<path d="M10 10h28v26q0 6-6 6H16q-6 0-6-6z" class="i-petg"/><rect x="9" y="12" width="30" height="5" rx="1" class="i-touch"/>'
             '<path d="M14 21q10-5 20 0" class="i-sheen"/><path d="M21 42v4" class="i-food"/>',
    # cable leaving at the back of the flange, clipped along the shelf
    'cable': '<path d="M4 9h40" class="i-line w"/><rect x="10" y="11" width="16" height="22" rx="3" class="i-petg"/>'
             '<path d="M26 14h10q4 0 4 4v20" class="i-cable"/><circle cx="33" cy="14" r="2" class="i-ink-f"/>',
    # control panel: one recessed button, two LEDs, the speaker grille
    'panel': '<rect x="12" y="4" width="24" height="40" rx="6" class="i-petg"/><circle cx="24" cy="12" r="2.6" class="i-led"/>'
             '<circle cx="24" cy="20" r="2.6" class="i-led2"/><circle cx="24" cy="31" r="5" class="i-hole"/><circle cx="24" cy="31" r="3.2" class="i-touch"/>'
             '<path d="M19 40h2M23 40h2M27 40h2" class="i-line"/>',
    # detachable module sliding out of the pod from below, with the panel on its outer face
    'module': '<path d="M8 6h32v20q0 5-5 5H13q-5 0-5-5z" class="i-petg"/><rect x="24" y="16" width="14" height="22" rx="3" class="i-petg"/>'
              '<circle cx="34" cy="22" r="1.8" class="i-led"/><circle cx="34" cy="27" r="1.8" class="i-led2"/><circle cx="34" cy="33" r="2.4" class="i-touch"/>'
              '<path d="M18 36v9" class="i-line" marker-end="url(#iar)"/>',
    'care': '<circle cx="24" cy="24" r="15" class="i-touch"/><path d="M24 24 15 15a12.7 12.7 0 0 1 18 0z" class="i-hole"/>'
            '<path d="M11 39 37 9" class="i-line"/><path d="M33 8l5 1-1 5" class="i-line"/>',
}


def icon(key):
    return (f'<svg class="icon" viewBox="0 0 48 48" aria-hidden="true"><defs><marker id="iar" viewBox="0 0 8 8" refX="6" refY="4" '
            f'markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 8 4 0 8z" class="i-ink-f"/></marker></defs>{ICONS[key]}</svg>')


# ---------------------------------------------------------------- home page
def photo_img(out, name, alt):
    """Thumbnail made by build.py (photos/thumb/), with its size when Pillow can read it."""
    size = ''
    try:
        from PIL import Image
        with Image.open(out / 'photos/thumb' / name) as im:
            size = f' width="{im.width}" height="{im.height}"'
    except Exception:
        pass
    return (f'<a href="photos/{esc(name)}" class="ph"><img src="photos/thumb/{esc(name)}"{size} loading="lazy" decoding="async" '
            f'{alt_attrs(alt)}></a>')


def img_size(path, default):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:
        return default


def home(out, summary, counts, grams):
    H = load_toml('home.toml')
    tot = summary['totals']
    n_plates = len(summary['plates'])
    all_grams = tot['grams_PETG'] + tot['grams_TPU']
    hero, idea, how, mat, b, st, op = (H[k] for k in ('hero', 'idea', 'how', 'materials', 'build', 'status', 'open'))

    hero_html = f'''    <section class="hero2" aria-labelledby="hero-title">
      <div class="hero-text">
        <p class="kicker">{L(hero['kicker'])}</p>
        <h1 id="hero-title">{L(hero['title'])}</h1>
        <p class="hero-lead">{L(hero['lead'])}</p>
        <p class="cta-row">
          <a class="btn btn-act" href="3d/" data-keep-lang>{L(hero['cta_3d'])}</a>
          <a class="btn" href="print/" data-keep-lang>{L(hero['cta_print'])}</a>
          <a class="btn" href="parts/" data-keep-lang>{L(hero['cta_parts'])}</a>
          <a class="btn" href="assembly/">{L(hero['cta_assembly'])}</a>
        </p>
        <p class="hero-status"><span class="dot" aria-hidden="true"></span>{L(hero['status'])}</p>
      </div>
      <figure class="hero-fig">
        <picture>
          <source media="(max-width: 700px)" srcset="img/hero-tall-780.webp" width="780" height="975">
          <img src="img/hero-wide-1440.webp" srcset="img/hero-wide-1440.webp 1440w, img/hero-wide-2880.webp 2880w"
               sizes="(min-width: 1000px) 62vw, 100vw" width="1440" height="900" fetchpriority="high" decoding="async"
               {alt_attrs(hero['img_alt'])}>
        </picture>
        <figcaption>{L(hero['img_note'])}</figcaption>
      </figure>
    </section>'''

    points = ''.join(f'<li><h3>{L(p["title"])}</h3><p>{L(p["body"])}</p></li>' for p in idea['points'])
    idea_html = f'''    <section class="sec" id="idea" aria-labelledby="idea-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">01</p>
        <h2 id="idea-title">{L(idea['title'])}</h2>
        <p class="lead">{L(idea['lead'])}</p>
      </div>
      <div class="idea-grid">
        <figure class="sheet">{idea_svg(idea['diagram'])}</figure>
        <ul class="points">{points}</ul>
      </div>
    </section>'''

    sw, sh = img_size(SITE / 'img/v64-section.webp', (580, 610))
    steps = ''.join(f'<li>{icon(s["key"])}<div><h3>{L(s["title"])}</h3><p>{L(s["body"])}</p></div></li>' for s in how['steps'])
    how_html = f'''    <section class="sec" id="how" aria-labelledby="how-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">02</p>
        <h2 id="how-title">{L(how['title'])}</h2>
        <p class="lead">{L(how['lead'])}</p>
      </div>
      <div class="how-grid">
        <figure class="sheet section-fig">
          <img src="img/v64-section.webp" width="{sw}" height="{sh}" loading="lazy" decoding="async" {alt_attrs(how['img_section'])}>
          <figcaption>{L(how['cap_section'])}</figcaption>
        </figure>
        <ol class="how-steps">{steps}</ol>
      </div>
      <p class="sec-cta cta-row"><a class="btn btn-act" href="3d/" data-keep-lang>{L(hero['cta_3d'])}</a>
        <a class="btn" href="module/" data-keep-lang>{L(how['cta_module'])}</a></p>
    </section>'''

    total = sum(grams.values())
    bars = ''.join(f'<span class="seg seg-{c}" style="flex-grow:{grams[c]:.1f}" title="{esc(mat[c]["name"]["en"])}"></span>'
                   for c in ('black', 'orange', 'green', 'yellow'))
    swatches = ''.join(
        f'<li class="sw sw-{c}"><span class="chip" aria-hidden="true"></span>'
        f'<div><h3>{L(mat[c]["name"])}</h3><p>{L(mat[c]["role"])}</p></div>'
        f'<p class="g">{L(lambda lang, c=c: num(grams[c], lang, 0 if grams[c] >= 10 else 1) + " g")}</p></li>'
        for c in ('black', 'orange', 'green', 'yellow'))
    mat_html = f'''    <section class="sec" id="colours" aria-labelledby="mat-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">03</p>
        <h2 id="mat-title">{L(mat['title'])}</h2>
        <p class="lead">{L(mat['lead'])}</p>
      </div>
      <div class="mat-grid">
        <ul class="swatches">{swatches}</ul>
        <div class="bar-wrap">
          <div class="bar" role="img" aria-label="{esc(mat['lead']['en'])}">{bars}</div>
          <p class="bar-total">{L(mat['total'])} <strong>{L(lambda lang: num(total, lang) + ' g')}</strong></p>
        </div>
        <p class="aside">{L(mat['note'])}</p>
      </div>
    </section>'''

    bp, bparts, bw, bm, kit = b['print'], b['parts'], b['wizard'], b['manual'], b['kit']
    kit_items = ''.join(f'<li>{L(i)}</li>' for i in kit['items'])
    build_html = f'''    <section class="sec" id="build" aria-labelledby="build-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">04</p>
        <h2 id="build-title">{L(b['title'])}</h2>
        <p class="lead">{L(b['lead'])}</p>
      </div>
      <ul class="cards">
        <li class="card card-go">
          <h3><a href="print/" data-keep-lang>{L(bp['title'])}</a></h3>
          <p>{L(bp['body'])}</p>
          <dl class="facts">
            <div><dt>{L(bp['plates'])}</dt><dd>{n_plates}</dd></div>
            <div><dt>{L(bp['hours'])}</dt><dd>{esc(hours(tot['time_min']))}</dd></div>
            <div><dt>{L(bp['grams'])}</dt><dd>{L(lambda lang: num(all_grams, lang) + ' g')}</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bp['cta'])} →</span>
        </li>
        <li class="card card-go">
          <h3><a href="parts/" data-keep-lang>{L(bparts['title'])}</a></h3>
          <p>{L(bparts['body'])}</p>
          <dl class="facts">
            <div><dt>{L(bparts['screws'])}</dt><dd>{counts['screws']}</dd></div>
            <div><dt>{L(bparts['inserts'])}</dt><dd>{counts['inserts']}</dd></div>
            <div><dt>{L(bparts['orings'])}</dt><dd>{counts['orings']}</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bparts['cta'])} →</span>
        </li>
        <li class="card card-go">
          <h3><a href="assembly/">{L(bw['title'])}</a></h3>
          <p>{L(bw['body'])}</p>
          <dl class="facts">
            <div><dt>{L(bw['flows'])}</dt><dd>2</dd></div>
            <div><dt>{L(bw['langs'])}</dt><dd>3</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bw['cta'])} →</span>
        </li>
        <li class="card card-go">
          <h3><a href="manual/" data-keep-lang>{L(bm['title'])}</a></h3>
          <p>{L(bm['body'])}</p>
          <dl class="facts">
            <div><dt>PDF</dt><dd>A6 · A4</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bm['cta'])} →</span>
        </li>
      </ul>
      <div class="kitbox">
        <div><h3>{L(kit['title'])}</h3><p>{L(kit['body'])}</p></div>
        <ul>{kit_items}</ul>
      </div>
      <p class="aside"><a href="3d/" data-keep-lang>{L(b['model'])}</a></p>
    </section>'''

    photos = ''.join(f'<li>{photo_img(out, name, st["photos"][key])}</li>' for name, key in BENCH)
    road = ''.join(f'<li{" class=now" if i == 0 else ""}>{L(it)}'
                   f'{" <span class=badge-now>" + L(st["roadmap"]["now"]) + "</span>" if i == 0 else ""}</li>'
                   for i, it in enumerate(st['roadmap']['items']))
    status_html = f'''    <section class="sec" id="status" aria-labelledby="status-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">05</p>
        <h2 id="status-title">{L(st['title'])}</h2>
        <p class="stamp">{L(st['stamp'])}</p>
      </div>
      <div class="status-grid">
        <article class="st-card">
          <h3>{L(st['v6']['title'])}</h3>
          <p>{L(st['v6']['body'])}</p>
          <p class="more"><a href="{REPO}/blob/main/hardware/README.md">hardware</a></p>
        </article>
        <article class="st-card">
          <h3>{L(st['bench']['title'])}</h3>
          <p>{L(st['bench']['body'])}</p>
          <ul class="bench">{photos}</ul>
          <p class="more"><a href="{REPO}/tree/main/firmware/micropython">{L(st['bench']['firmware'])}</a> ·
            <a href="{REPO}/issues/2">{L(st['bench']['issue'])}</a></p>
        </article>
        <article class="st-card road">
          <h3>{L(st['roadmap']['title'])}</h3>
          <ol class="roadmap">{road}</ol>
        </article>
      </div>
    </section>'''

    lic = [('software', 'MIT', 'LICENSES/MIT.txt'), ('hardware', 'CERN-OHL-P-2.0', 'LICENSES/CERN-OHL-P-2.0.txt'),
           ('docs', 'CC BY 4.0', 'LICENSES/CC-BY-4.0.txt')]
    lics = ''.join(f'<li><h3>{L(op[k]["title"])}</h3><p>{L(op[k]["body"])}</p><a href="{REPO}/blob/main/{p}">{name}</a></li>'
                   for k, name, p in lic)
    open_html = f'''    <section class="sec" id="open" aria-labelledby="open-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">06</p>
        <h2 id="open-title">{L(op['title'])}</h2>
        <p class="lead">{L(op['lead'])}</p>
      </div>
      <ul class="lics">{lics}</ul>
      <div class="join">
        <h3>{L(op['contribute']['title'])}</h3>
        <p>{L(op['contribute']['body'])}</p>
        <p class="cta-row">
          <a class="btn btn-act" href="{REPO}">{GITHUB_SVG} {L(op['github'])}</a>
          <a class="btn" href="{REPO}/issues/new/choose">{L(op['issue'])}</a>
          <a class="btn" href="{REPO}/blob/main/CONTRIBUTING.md">{L(op['guide'])}</a>
        </p>
      </div>
    </section>'''

    nav = [('#idea', H['nav']['idea'], False), ('#how', H['nav']['how'], False), ('#build', H['nav']['build'], False),
           ('#status', H['nav']['status'], False), ('#open', H['nav']['open'], False)]
    body = '\n'.join([hero_html, idea_html, how_html, mat_html, build_html, status_html, open_html])
    s = page(root='', titles=H['meta']['title'], description=H['meta']['description']['en'], nav=nav, body=body,
             footer=footer_html('', H), cls='home', og_image='img/hero-wide-1440.webp')
    (out / 'index.html').write_text(s, encoding='utf-8')


# ---------------------------------------------------------------- helpers for the print guide
def trim_preview(src, dst):
    """Crop the white margin and the English title line of a plate preview. Returns (path, w, h)."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        shutil.copy2(src, dst.with_suffix('.png'))
        return dst.with_suffix('.png').name, None, None
    with Image.open(src) as im:
        im = im.convert('RGB')
        diff = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 18 else 0)
        rows = [any(diff.crop((0, y, im.width, y + 1)).getdata()) for y in range(im.height)]
        bands, y = [], 0
        while y < im.height:
            if rows[y]:
                y0 = y
                while y < im.height and rows[y]:
                    y += 1
                bands.append((y0, y))
            y += 1
        if len(bands) > 1 and bands[0][1] - bands[0][0] < 30:   # the title line on top
            diff = diff.crop((0, bands[1][0], im.width, im.height))
            top = bands[1][0]
        else:
            top = 0
        x0, y0, x1, y1 = diff.getbbox()
        pad = 14
        box = (max(0, x0 - pad), max(0, top + y0 - pad), min(im.width, x1 + pad), min(im.height, top + y1 + pad))
        c = im.crop(box)
        c.save(dst, quality=84, method=6)
        return dst.name, c.width, c.height


def write_zip(path, prefix, members, stamp):
    """members: [(source Path, name in the ZIP)]; fixed dates so the build is reproducible."""
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src, name in members:
            zi = zipfile.ZipInfo(f'{prefix}/{name}', date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, src.read_bytes(), compresslevel=9)


# ---------------------------------------------------------------- manual pages
def fill(texts, **kw):
    """per-language texts with {name} placeholders filled in"""
    t = per_lang(texts)
    out = {}
    for lang in LANGS:
        v = t[lang]
        for k, x in kw.items():
            v = v.replace('{' + k + '}', x)
        out[lang] = v
    return out


def manual_page(out, label=CURRENT):
    """Manual page (manual/): PDFs copied from docs/manual/ and the drilling template from hardware/template/."""
    H = load_toml('home.toml')
    M = H['manual']
    root = '../'
    page_dir = out / 'manual'
    files = page_dir / 'files'
    files.mkdir(parents=True, exist_ok=True)
    cover = 'manual-cover'

    def link(name, src):
        if not src.exists():
            raise SystemExit(f'missing {src.relative_to(ROOT)}')
        shutil.copy2(src, files / name)
        return f'files/{name}', src.stat().st_size

    cards = []
    for lang in LANGS:
        rows = []
        for ft, key, name in (('A6', 'booklet', f'kibble-dispenser-manual-{lang}.pdf'), ('A4', 'print', f'kibble-dispenser-manual-{lang}-print-a4.pdf')):
            url, n = link(name, MANUALS / name)
            size_html = L(lambda lg, n=n: f'PDF · {size_text(n, lg)}')
            rows.append(f'<li><a href="{url}" download><span class="ft">{ft}</span><span class="dl-t">{L(M[key])}</span>'
                        f'<span class="dl-s">{size_html}</span></a></li>')
        w, h = img_size(SITE / f'img/{cover}-{lang}.webp', (360, 508))
        first = rows[0].split('href="', 1)[1].split('"', 1)[0]
        cards.append(f'''<li class="man" lang="{lang}">
          <a class="man-cover" href="{first}"><img src="{root}img/{cover}-{lang}.webp" width="{w}" height="{h}" loading="lazy" decoding="async"
            alt="{esc(LANG_NAMES[lang])}: Kibble Dispenser Outdoor, manual cover"></a>
          <div class="man-body">
            <h2>{esc(LANG_NAMES[lang])}</h2>
            <ul class="dl-list">{''.join(rows)}</ul>
          </div>
        </li>''')
    tpl_url, n = link(TEMPLATE_NAME, TEMPLATE_PDF)
    tpl_size = L(lambda lg: size_text(n, lg))
    tpl_dir = f'{REPO}/tree/main/hardware/template'
    status = f'<div class="banner" role="note"><p>{L(fill(M["status"], v=label))}</p></div>'
    body = f'''    <section class="phead" aria-labelledby="m-title">
      <p class="kicker">Kibble Dispenser Outdoor · {label}</p>
      <h1 id="m-title">{L(M['title'])}</h1>
      <p class="lead">{L(fill(M['lead'], v=label))}</p>
      {status}
    </section>
    <section class="psec" aria-label="PDF">
      <ul class="mans">{''.join(cards)}</ul>
      <p class="aside">{L(M['print_note'])}</p>
    </section>
    <section class="psec" id="template" aria-labelledby="tpl-title">
      <h2 id="tpl-title">{L(M['template_title'])}</h2>
      <p class="lead">{L(M['template_body'])}</p>
      <ul class="dl-list">
        <li class="dl-main"><a href="{tpl_url}" download><span class="ft">PDF</span><span class="dl-t">{L(M['template_title'])} · A4 · 1:1</span>
          <span class="dl-s">{TEMPLATE_NAME} · {tpl_size}</span></a></li>
      </ul>
    </section>
    <section class="psec">
      <p class="cta-row"><a class="btn btn-act" href="../assembly/">{L(H['build']['wizard']['cta'])}</a></p>
      <p class="aside">{L(M['also'])}</p>
      <p class="aside">{L(M['licence'])} <a href="{REPO}/tree/main/docs/manual">docs/manual</a> · <a href="{tpl_dir}">hardware/template</a></p>
    </section>'''
    nav = [(root, NAV_HOME, True), ('../assembly/', {'en': 'Assembly', 'it': 'Montaggio', 'de': 'Montage'}, False),
           ('../parts/', {'en': 'Bought parts', 'it': 'Pezzi da comprare', 'de': 'Zukaufteile'}, True)]
    s = page(root=root, titles=fill(M['meta'], v=label), description=fill(M['lead'], v=label)['en'], nav=nav, body=body,
             footer=footer_html(root, H), cls='print manual')
    (page_dir / 'index.html').write_text(s, encoding='utf-8')
    return page_dir / 'index.html'


VERSIONS = None


def build(out):
    global VERSIONS
    VERSIONS = versions.load()
    out = Path(out)
    summary, counts, grams = load_data()
    home(out, summary, counts, grams)
    written = [out / 'index.html']
    import modulepage
    import printguide
    me = sys.modules[__name__]
    written.append(printguide.build(out, me))
    written.append(modulepage.build(out, me))
    written.append(manual_page(out))
    # catch unfilled markers and stray format braces
    for f in written:
        s = f.read_text(encoding='utf-8')
        if re.search(r'\{[a-z_]+\}', s):
            raise SystemExit(f'unfilled placeholder in {f}')


if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else SITE / '_build')
