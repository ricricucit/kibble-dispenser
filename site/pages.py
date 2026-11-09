#!/usr/bin/env python3
"""
Home page and print-files page of the website, in English, Italian and German.

site/build.py calls build(out) after copying site/ to the output folder. It writes:
  <out>/index.html            home page, texts from site/content/home.toml
  <out>/v6/print/index.html   print files of design v6, texts from site/content/print.toml
  <out>/v6/print/files/       the downloads (Bambu projects, plate 3MFs, STL files, one ZIP with everything)
  <out>/v6/print/img/         plate previews, trimmed (WebP with Pillow, the original PNG otherwise)

Grams, times, plates, parts and file names come from hardware/v6/plates/summary.json, the bought
hardware counts from hardware/v6/cad/v6.json. Every text is written once per language; the language
switch (js/lang.js) shows one of them. Standard library only; Pillow is optional.
"""
import html
import json
import re
import shutil
import tomllib
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
PLATES = ROOT / 'hardware/v6/plates'
REPO = 'https://github.com/ricricucit/kibble-dispenser'
LANGS = ('en', 'it', 'de')
ZIP_NAME = 'Kibble_Dispenser_v6_print_files.zip'
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
    h, m = divmod(round(minutes), 60)
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
      <a href="{root}earlier/">{L(f['earlier'])}</a>
      <a href="{root}v6/3d/" data-keep-lang>{L({'en': '3D model', 'it': 'Modello 3D', 'de': '3D-Modell'})}</a>
      <a href="{root}v6/print/" data-keep-lang>{L({'en': 'Print files', 'it': 'File di stampa', 'de': 'Druckdateien'})}</a>
      <a href="{root}v6/parts/" data-keep-lang>{L({'en': 'Bought parts', 'it': 'Pezzi da comprare', 'de': 'Zukaufteile'})}</a>
      <a href="{REPO}">GitHub</a>
    </p>
    <p class="foot-note">{L(f['licence'])} {L(f['privacy'])} © 2026 Enrico Icardi {L({'en': 'and contributors', 'it': 'e contributori', 'de': 'und Mitwirkende'})}</p>
  </footer>'''


# ---------------------------------------------------------------- data
def load_data():
    summary = json.loads((PLATES / 'summary.json').read_text(encoding='utf-8'))
    v6 = json.loads((ROOT / 'hardware/v6/cad/v6.json').read_text(encoding='utf-8'))
    counts = {'screws': 0, 'inserts': 0, 'orings': 0}
    for h in v6['hardware']:
        item = h['item'].lower()
        if 'o-ring' in item:
            counts['orings'] += int(h['qty'])
        elif 'insert' in item:
            counts['inserts'] += int(h['qty'])
        elif 'screw' in item or item.startswith('m3x'):
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
    """Side view: container on a shelf, the dispenser underneath, the green food path to the bowl."""
    return f'''<svg class="idea-svg" viewBox="0 0 360 350" role="img" aria-labelledby="idea-svg-t">
  <title id="idea-svg-t">{esc(d['drum']['en'])}, {esc(d['shelf']['en'])}, {esc(d['unit']['en'])}, {esc(d['food']['en'])}</title>
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
  {svg_text(74, 186, d['hole'], 'lbl dim', 'end')}
  <!-- dispenser: flange, bowl with the orange disc, tower, box, TPU seal, green chute -->
  <rect x="72" y="162" width="76" height="7" class="petg"/>
  <path d="M76 169h68l-6 43H82z" class="petg"/>
  <rect x="90" y="180" width="40" height="8" rx="2" class="touch"/>
  <rect x="104" y="212" width="12" height="18" class="petg"/>
  <rect x="84" y="230" width="52" height="50" rx="2" class="petg"/>
  <rect x="82" y="280" width="56" height="5" class="tpu"/>
  <path d="M82 196 46 248l12 8 30-42z" class="chute"/>
  <path d="M141 252H182" class="dimline"/>
  {svg_text(186, 256, d['unit'])}
  <!-- food path -->
  <path d="M110 40V184q-14 12-28 22L54 246q-4 8-4 16v50" class="food" marker-end="url(#arg)"/>
  <path d="M58 300H182" class="foodline"/>
  {svg_text(186, 304, d['food'], 'lbl food-t')}
  <!-- bowl -->
  <path d="M26 322q24 13 48 0z" class="bowl"/>
  {svg_text(82, 330, d['bowl'])}
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
    # twist and lower
    'twist': '<rect x="9" y="8" width="30" height="5" class="i-petg"/><path d="M13 13h22l-3 14H16z" class="i-petg"/>'
             '<rect x="20" y="17" width="8" height="4" rx="1" class="i-touch"/>'
             '<path d="M8 33a17 6 0 0 0 32 0" class="i-line" marker-end="url(#iar)"/><path d="M24 31v13" class="i-line" marker-end="url(#iar)"/>',
    # rain drop kept out by a seal, openings facing down
    'seal': '<path d="M24 4c5 7 8 11 8 15a8 8 0 0 1-16 0c0-4 3-8 8-15z" class="i-drop"/>'
            '<path d="M8 30h32v12H8z" class="i-petg"/><path d="M8 30h32" class="i-tpu-l w"/><path d="M20 42v4M28 42v4" class="i-line"/>',
    # chute with hood and drip ring
    'outlet': '<path d="M10 6h14l14 24-8 5L18 14H10z" class="i-chute"/><path d="M26 32l12-7" class="i-line w"/>'
              '<path d="M33 38v3M29 41v3" class="i-food"/>',
    # optional pipe down to the bowl
    'pipe': '<path d="M20 2h8v34h-8z" class="i-pipe"/><path d="M14 38q10 8 20 0z" class="i-bowl"/><path d="M24 30v4" class="i-food"/>',
    # v6.1
    'shell': '<path d="M10 14q14-10 28 0v20q-14 10-28 0z" class="i-petg"/><path d="M14 18q10-6 20 0" class="i-sheen"/>',
    'flush': '<rect x="6" y="16" width="36" height="16" rx="8" class="i-petg"/><rect x="18" y="20" width="12" height="8" rx="4" class="i-touch"/>',
    'cable': '<path d="M6 8h36" class="i-line w"/><rect x="14" y="22" width="20" height="16" rx="3" class="i-petg"/>'
             '<path d="M24 22V8" class="i-cable"/>',
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


def home(out, summary, counts, grams):
    H = load_toml('home.toml')
    tot = summary['totals']
    n_plates = len(summary['plates'])
    all_grams = tot['grams_PETG'] + tot['grams_TPU']
    hero, idea, how, mat, b, nx, st, op = (H[k] for k in ('hero', 'idea', 'how', 'materials', 'build', 'next', 'status', 'open'))

    hero_html = f'''    <section class="hero2" aria-labelledby="hero-title">
      <div class="hero-text">
        <p class="kicker">{L(hero['kicker'])}</p>
        <h1 id="hero-title">{L(hero['title'])}</h1>
        <p class="hero-lead">{L(hero['lead'])}</p>
        <p class="cta-row">
          <a class="btn btn-act" href="v6/3d/" data-keep-lang>{L(hero['cta_3d'])}</a>
          <a class="btn" href="v6/print/" data-keep-lang>{L(hero['cta_print'])}</a>
          <a class="btn" href="v6/parts/" data-keep-lang>{L(hero['cta_parts'])}</a>
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

    steps = ''.join(f'<li>{icon(s["key"])}<div><h3>{L(s["title"])}</h3><p>{L(s["body"])}</p></div></li>' for s in how['steps'])
    how_html = f'''    <section class="sec" id="how" aria-labelledby="how-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">02</p>
        <h2 id="how-title">{L(how['title'])}</h2>
        <p class="lead">{L(how['lead'])}</p>
      </div>
      <div class="how-grid">
        <figure class="sheet section-fig">
          <img src="img/v6-section.webp" width="769" height="667" loading="lazy" decoding="async" {alt_attrs(how['img_section'])}>
          <figcaption>{L(how['cap_section'])}</figcaption>
        </figure>
        <ol class="how-steps">{steps}</ol>
      </div>
      <p class="sec-cta"><a class="btn btn-act" href="v6/3d/" data-keep-lang>{L(hero['cta_3d'])}</a></p>
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

    bp, bparts = b['print'], b['parts']
    soon = f'<span class="badge">{L(b["soon"])}</span>'
    build_html = f'''    <section class="sec" id="build" aria-labelledby="build-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">04</p>
        <h2 id="build-title">{L(b['title'])}</h2>
        <p class="lead">{L(b['lead'])}</p>
      </div>
      <ul class="cards">
        <li class="card card-go">
          <h3><a href="v6/print/" data-keep-lang>{L(bp['title'])}</a></h3>
          <p>{L(bp['body'])}</p>
          <dl class="facts">
            <div><dt>{L(bp['plates'])}</dt><dd>{n_plates}</dd></div>
            <div><dt>{L(bp['hours'])}</dt><dd>{esc(hours(tot['time_min']))}</dd></div>
            <div><dt>{L(bp['grams'])}</dt><dd>{L(lambda lang: num(all_grams, lang) + ' g')}</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bp['cta'])} →</span>
        </li>
        <li class="card card-go">
          <h3><a href="v6/parts/" data-keep-lang>{L(bparts['title'])}</a></h3>
          <p>{L(bparts['body'])}</p>
          <dl class="facts">
            <div><dt>{L(bparts['screws'])}</dt><dd>{counts['screws']}</dd></div>
            <div><dt>{L(bparts['inserts'])}</dt><dd>{counts['inserts']}</dd></div>
            <div><dt>{L(bparts['orings'])}</dt><dd>{counts['orings']}</dd></div>
          </dl>
          <span class="go" aria-hidden="true">{L(bparts['cta'])} →</span>
        </li>
        <li class="card card-soon">{soon}<h3>{L(b['wizard']['title'])}</h3><p>{L(b['wizard']['body'])}</p></li>
        <li class="card card-soon">{soon}<h3>{L(b['manual']['title'])}</h3><p>{L(b['manual']['body'])}</p></li>
      </ul>
      <p class="aside"><a href="v6/3d/" data-keep-lang>{L(b['model'])}</a></p>
    </section>'''

    items = ''.join(f'<li>{icon(i["key"])}<div><h3>{L(i["title"])}</h3><p>{L(i["body"])}</p></div></li>' for i in nx['items'])
    next_html = f'''    <section class="sec next" id="next" aria-labelledby="next-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">05</p>
        <h2 id="next-title">{L(nx['title'])} <span class="badge badge-live">{L(nx['badge'])}</span></h2>
        <p class="lead">{L(nx['lead'])}</p>
      </div>
      <ul class="next-items">{items}</ul>
      <p class="warn" role="note">{L(nx['warning'])}</p>
    </section>'''

    photos = ''.join(f'<li>{photo_img(out, name, st["photos"][key])}</li>' for name, key in BENCH)
    road = ''.join(f'<li{" class=now" if i == 0 else ""}>{L(it)}'
                   f'{" <span class=badge-now>" + L(st["roadmap"]["now"]) + "</span>" if i == 0 else ""}</li>'
                   for i, it in enumerate(st['roadmap']['items']))
    status_html = f'''    <section class="sec" id="status" aria-labelledby="status-title">
      <div class="sec-head">
        <p class="num" aria-hidden="true">06</p>
        <h2 id="status-title">{L(st['title'])}</h2>
        <p class="stamp">{L(st['stamp'])}</p>
      </div>
      <div class="status-grid">
        <article class="st-card">
          <h3>{L(st['v6']['title'])}</h3>
          <p>{L(st['v6']['body'])}</p>
          <p class="more"><a href="{REPO}/blob/main/hardware/v6/README.md">hardware/v6</a></p>
        </article>
        <article class="st-card">
          <h3>{L(st['bench']['title'])}</h3>
          <p>{L(st['bench']['body'])}</p>
          <ul class="bench">{photos}</ul>
          <p class="more"><a href="{REPO}/tree/main/firmware/micropython">{L(st['bench']['firmware'])}</a></p>
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
        <p class="num" aria-hidden="true">07</p>
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
           ('#next', H['nav']['next'], False), ('#status', H['nav']['status'], False), ('#open', H['nav']['open'], False)]
    body = '\n'.join([hero_html, idea_html, how_html, mat_html, build_html, next_html, status_html, open_html])
    s = page(root='', titles=H['meta']['title'], description=H['meta']['description']['en'], nav=nav, body=body,
             footer=footer_html('', H), cls='home', og_image='img/hero-wide-1440.webp')
    (out / 'index.html').write_text(s, encoding='utf-8')


# ---------------------------------------------------------------- print page
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


def print_page(out, summary):
    P = load_toml('print.toml')
    tot = summary['totals']
    page_dir = out / 'v6/print'
    files, img = page_dir / 'files', page_dir / 'img'
    for d in (files / 'plates', files / 'stl', files / 'preview', img):
        d.mkdir(parents=True, exist_ok=True)
    projects = summary['files']['bambu_projects']
    for f in projects:
        shutil.copy2(PLATES / f, files / f)
    for sub in ('plates', 'stl', 'preview'):
        for f in sorted((PLATES / sub).iterdir()):
            shutil.copy2(f, files / sub / f.name)

    # one ZIP with everything, with fixed dates so the build is reproducible
    stamp = tuple(int(x) for x in summary['generated'].split('-')) + (0, 0, 0)
    members = ([(PLATES / f, f) for f in projects] + [(PLATES / 'README.md', 'README.md'), (PLATES / 'summary.json', 'summary.json')]
               + [(f, f'plates/{f.name}') for f in sorted((PLATES / 'plates').iterdir())]
               + [(f, f'stl/{f.name}') for f in sorted((PLATES / 'stl').iterdir())]
               + [(ROOT / 'LICENSES/CERN-OHL-P-2.0.txt', 'LICENSES/CERN-OHL-P-2.0.txt'),
                  (ROOT / 'LICENSES/CC-BY-4.0.txt', 'LICENSES/CC-BY-4.0.txt')])
    with zipfile.ZipFile(files / ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src, name in members:
            zi = zipfile.ZipInfo(f'Kibble_Dispenser_v6_print_files/{name}', date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, src.read_bytes(), compresslevel=9)

    def sz(path):
        n = path.stat().st_size
        return L(lambda lang: size_text(n, lang))

    part_name = P['part']
    colour = P['colour']

    def dots(cols):
        return ''.join(f'<span class="cdot" style="--c:{COLOUR_VAR[c]}" title="{esc(colour[c]["en"])}"></span>' for c in cols)

    def fil_label(fil):
        c = fil.split()[-1]
        name = {'black': P['ams']['black']['name'], 'orange': P['ams']['orange']['name'], 'green': P['ams']['green']['name'],
                'yellow': P['ams']['tpu']['name']}[c]
        return c, name

    # facts
    facts = f'''<dl class="facts big">
          <div><dt>{L(P['facts']['plates'])}</dt><dd>{len(summary['plates'])}</dd></div>
          <div><dt>{L(P['facts']['time'])}</dt><dd>{esc(hours(tot['time_min']))}</dd></div>
          <div><dt>{L(P['facts']['petg'])}</dt><dd>{L(lambda lang: num(tot['grams_PETG'], lang) + ' g')}</dd></div>
          <div><dt>{L(P['facts']['tpu'])}</dt><dd>{L(lambda lang: num(tot['grams_TPU'], lang, 1) + ' g')}</dd></div>
          <div><dt>{L(P['facts']['swaps'])}</dt><dd>{tot['colour_swaps']}</dd></div>
        </dl>'''

    head = f'''    <section class="phead" aria-labelledby="p-title">
      <p class="kicker">Kibble Dispenser Outdoor · v6</p>
      <h1 id="p-title">{L(P['head']['title'])}</h1>
      <p class="lead">{L(P['head']['lead'])}</p>
      <div class="banner" role="note">
        <p class="banner-t">{L(P['banner']['title'])}</p>
        <p>{L(P['banner']['body'])} <a href="../../#next" data-keep-lang>{L(P['banner']['link'])}</a></p>
      </div>
      {facts}
      <nav class="toc" aria-label="On this page"><ul>
        <li><a href="#downloads">{L(P['dl']['title'])}</a></li>
        <li><a href="#ams">{L(P['ams']['title'])}</a></li>
        <li><a href="#tests">{L(P['test']['title'])}</a></li>
        <li><a href="#plates">{L(P['plates']['title'])}</a></li>
        <li><a href="#settings">{L(P['settings']['title'])}</a></li>
        <li><a href="#checklist">{L(P['check']['title'])}</a></li>
      </ul></nav>
    </section>'''

    petg, tpu = projects
    dl = f'''    <section class="psec" id="downloads" aria-labelledby="dl-title">
      <h2 id="dl-title">{L(P['dl']['title'])}</h2>
      <ul class="dl-list">
        <li class="dl-main"><a href="files/{ZIP_NAME}" download><span class="ft">ZIP</span><span class="dl-t">{L(P['dl']['zip']['title'])}</span>
          <span class="dl-b">{L(P['dl']['zip']['body'])}</span><span class="dl-s">{sz(files / ZIP_NAME)}</span></a></li>
        <li><a href="files/{esc(petg)}" download><span class="ft">3MF</span><span class="dl-t">{L(P['dl']['petg']['title'])}</span>
          <span class="dl-b">{L(P['dl']['petg']['body'])}</span><span class="dl-s">{esc(petg)} · {sz(files / petg)}</span></a></li>
        <li><a href="files/{esc(tpu)}" download><span class="ft">3MF</span><span class="dl-t">{L(P['dl']['tpu']['title'])}</span>
          <span class="dl-b">{L(P['dl']['tpu']['body'])}</span><span class="dl-s">{esc(tpu)} · {sz(files / tpu)}</span></a></li>
      </ul>
      <p class="check-note">{L(P['dl']['check'])}</p>
      <p class="aside">{L(P['dl']['other'])}</p>
    </section>'''

    a = P['ams']
    slots = [('1', 'black', a['black']), ('2', 'orange', a['orange']), ('3', 'green', a['green']), ('4', 'black spare', a['spare'])]
    slot_html = ''.join(f'<li class="slot slot-{c.split()[0]}{" spare" if "spare" in c else ""}"><span class="spool-ic" aria-hidden="true"></span>'
                        f'<span class="slot-n">{L(a["slot"])} {n}</span><span class="slot-name">{L(x["name"])}</span>'
                        f'<span class="slot-role">{L(x["role"])}</span></li>' for n, c, x in slots)
    ams = f'''    <section class="psec" id="ams" aria-labelledby="ams-title">
      <h2 id="ams-title">{L(a['title'])}</h2>
      <p class="lead">{L(a['lead'])}</p>
      <div class="ams">
        <ol class="slots" aria-label="AMS lite">{slot_html}</ol>
        <div class="ext slot slot-yellow"><span class="spool-ic" aria-hidden="true"></span>
          <span class="slot-n">{L(a['tpu']['slot'])}</span><span class="slot-name">{L(a['tpu']['name'])}</span><span class="slot-role">{L(a['tpu']['role'])}</span></div>
      </div>
      <ul class="notes">
        <li>{L(a['note_spare'])}</li>
        <li>{L(a['note_tpu'])}</li>
      </ul>
    </section>'''

    steps = ''.join(f'<li><h3>{L(s["title"])}</h3><p>{L(s["body"])}</p></li>' for s in P['test']['steps'])
    tests = f'''    <section class="psec" id="tests" aria-labelledby="test-title">
      <h2 id="test-title">{L(P['test']['title'])}</h2>
      <p class="lead">{L(P['test']['lead'])}</p>
      <ol class="tsteps">{steps}</ol>
    </section>'''

    cards = []
    for pl in summary['plates']:
        key = pl['key']
        tx = P['plate'][key]
        name, w, h = trim_preview(PLATES / pl['preview_iso'], img / f'{key}_iso.webp')
        size = f' width="{w}" height="{h}"' if w else ''
        parts = ''.join(f'<li>{dots(x["colours"])}<span class="pn">{L(part_name[x["id"]])}</span>'
                        f'<span class="q">×{x["qty"]}</span></li>' for x in pl['parts'])
        fils = []
        for fil, g in pl['est_grams_per_filament'].items():
            c, nm = fil_label(fil)
            fils.append(f'<li><span class="cdot" style="--c:{COLOUR_VAR[c]}"></span>{L(nm)} '
                        f'<strong>{L(lambda lang, g=g: num(g["grams"], lang, 0 if g["grams"] >= 10 else 1) + " g")}</strong></li>')
        test = key.endswith('-0')
        note = (f'<p class="pnote">{L(P["plates"]["tpu_note"])}</p>' if key == 'TPU-1' else '')
        plain = Path(pl['plain_3mf']).name
        cards.append(f'''<li class="plate{' plate-test' if test else ''}" id="plate-{esc(key)}">
          <a class="pimg" href="files/{esc(pl['preview_top'])}"><img src="img/{esc(name)}"{size} loading="lazy" decoding="async" {alt_attrs(tx['title'])}></a>
          <div class="pbody">
            <p class="pkey">{esc(key)}{(' · <span class="badge">' + L(P['plates']['test']) + '</span>') if test else ''}</p>
            <h3>{L(tx['title'])}</h3>
            <p class="ppurpose">{L(tx['purpose'])}</p>
            <ul class="pparts">{parts}</ul>
            <ul class="pfils">{''.join(fils)}</ul>
            <p class="pmeta"><span>{esc(pl['est_time_hm'])}</span><span>{pl['colour_swaps']} {L(P['plates']['swaps'])}</span>
              <span>{L(P['plates']['in_project'])} {pl['plate_in_project']}</span></p>
            {note}
            <p class="pdl"><a class="btn btn-sm" href="files/plates/{esc(plain)}" download>{L(P['plates']['download'])} · {sz(files / 'plates' / plain)}</a></p>
          </div>
        </li>''')
    plates = f'''    <section class="psec" id="plates" aria-labelledby="plates-title">
      <h2 id="plates-title">{L(P['plates']['title'])}</h2>
      <p class="lead">{L(P['plates']['lead'])}</p>
      <ol class="plates">{''.join(cards)}</ol>
    </section>'''

    se = P['settings']
    pp = se['perpart']

    def setting_text(lang, s):
        bits = [f"{s['wall_loops']} {pp['walls'][lang]}", f"{s['sparse_infill_density'].replace('%', ' %')} {pp['infill'][lang]}"]
        if 'top_shell_layers' in s:
            bits.append(f"{s['top_shell_layers']}/{s['bottom_shell_layers']} {pp['shells'][lang]}")
        if s.get('layer_height'):
            bits.append(f"{num(float(s['layer_height']), lang, 2)} mm {pp['layer'][lang]}")
        if s.get('brim_width'):
            bits.append(f"{pp['brim'][lang]} {s['brim_width']} mm")
        if s.get('enable_support') == '1':
            bits.append(pp['support_bed'][lang] if s.get('support_on_build_plate_only') == '1' else pp['support_any'][lang])
        if s.get('outer_wall_speed'):
            bits.append(f"{pp['slow'][lang]} {s['outer_wall_speed']} mm/s")
        return ', '.join(bits)

    seen, rows = set(), []
    for pl in summary['plates']:
        for x in pl['parts']:
            if x['id'] in seen:
                continue
            seen.add(x['id'])
            rows.append(f'<li><span class="pn">{L(part_name[x["id"]])}</span>'
                        f'<span class="sv">{L(lambda lang, s=x["settings"]: setting_text(lang, s))}</span></li>')

    def blist(k):
        return f'<div class="sblock"><h3>{L(se[k]["title"])}</h3><ul>{"".join(f"<li>{L(i)}</li>" for i in se[k]["items"])}</ul></div>'
    settings = f'''    <section class="psec" id="settings" aria-labelledby="set-title">
      <h2 id="set-title">{L(se['title'])}</h2>
      <p class="lead">{L(se['lead'])}</p>
      <div class="sgrid">{blist('printer')}{blist('petg')}{blist('tpu')}</div>
      <details class="perpart"><summary>{L(pp['title'])}</summary><ul>{''.join(rows)}</ul></details>
    </section>'''

    ck = P['check']
    by_kind = {'part': [], 'test': []}
    for c in summary['parts_checklist']:
        by_kind[c['kind']].append(
            f'<li><label><input type="checkbox" data-check="{esc(c["id"])}"> {dots(c["colours"])}'
            f'<span class="pn">{L(part_name[c["id"]])}</span><span class="q">×{c["qty"]}</span>'
            f'<span class="pk">{esc(", ".join(c["plates"]))}</span></label></li>')
    checklist = f'''    <section class="psec" id="checklist" aria-labelledby="ck-title">
      <h2 id="ck-title">{L(ck['title'])}</h2>
      <p class="lead">{L(ck['lead'])}</p>
      <p class="ck-count" aria-live="polite"><strong data-check-count>0</strong> / {len(summary['parts_checklist'])} {L(ck['done'])}
        <button type="button" class="btn btn-sm" data-check-reset>{L(ck['reset'])}</button></p>
      <h3 class="ck-h">{L(ck['parts'])}</h3>
      <ul class="cklist">{''.join(by_kind['part'])}</ul>
      <h3 class="ck-h">{L(ck['tests'])}</h3>
      <ul class="cklist">{''.join(by_kind['test'])}</ul>
    </section>'''

    stl = sorted((files / 'stl').iterdir())
    stl_items = ''.join(f'<li><a href="files/stl/{esc(f.name)}" download>{esc(f.name)}</a> <span>{sz(f)}</span></li>' for f in stl)
    stl_html = f'''    <section class="psec" id="stl" aria-labelledby="stl-title">
      <h2 id="stl-title">{L(P['files']['title'])}</h2>
      <p class="lead">{L(P['files']['lead'])}</p>
      <details class="stl"><summary>{L(P['files']['show'])} ({len(stl)})</summary><ul>{stl_items}</ul></details>
    </section>'''

    notes = ''.join(f'<li>{L(i)}</li>' for i in P['notes']['items']['items'])
    notes_html = f'''    <section class="psec" id="notes" aria-labelledby="notes-title">
      <h2 id="notes-title">{L(P['notes']['title'])}</h2>
      <ul class="notes">{notes}</ul>
      <p class="cta-row">
        <a class="btn" href="{REPO}/blob/main/hardware/v6/plates/README.md">{L(P['notes']['guide'])}</a>
        <a class="btn" href="{REPO}/tree/main/hardware/v6/plates">{L(P['notes']['github'])}</a>
      </p>
      <p class="aside">{L(P['footer']['licence'])}</p>
    </section>'''

    H = load_toml('home.toml')
    nav = [('../../', P['nav']['home'], True), ('../3d/', P['nav']['model'], True), ('../parts/', P['nav']['parts'], True)]
    body = '\n'.join([head, dl, ams, tests, plates, settings, checklist, stl_html, notes_html])
    s = page(root='../../', titles=P['meta']['title'], description=P['meta']['description']['en'], nav=nav, body=body,
             footer=footer_html('../../', H), cls='print')
    (page_dir / 'index.html').write_text(s, encoding='utf-8')


def build(out):
    out = Path(out)
    summary, counts, grams = load_data()
    for k in summary['plates']:
        for x in k['parts']:
            if x['id'] not in load_toml('print.toml')['part']:
                raise SystemExit(f"site/content/print.toml has no name for part {x['id']}")
    home(out, summary, counts, grams)
    print_page(out, summary)
    # catch unfilled markers and stray format braces
    for f in (out / 'index.html', out / 'v6/print/index.html'):
        s = f.read_text(encoding='utf-8')
        if re.search(r'\{[a-z_]+\}', s):
            raise SystemExit(f'unfilled placeholder in {f}')


if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else SITE / '_build')
