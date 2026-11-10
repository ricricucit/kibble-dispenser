#!/usr/bin/env python3
"""
Bought parts ("Pezzi extra") in English, Italian and German, for the current design (v6.2) and the archived v6.

Sources, one per design (DESIGNS below):
  v6.2  hardware/v6.2/bom.json (texts and quantities), checked against the bought-parts list of the print package,
        hardware/v6.2/plates/summary.json (bought_parts, collected from v62.json, v611.json and v61.json)
  v6    hardware/v6/bom.json, checked against the hardware list of hardware/v6/cad/v6.json
Every line of the source list must appear in some item's "match", and an item's quantity must equal the sum of the
source lines it matches. Items without "match" (electronics, tools) are not in the design data.

    python site/bom.py           rewrite docs/BOM.md (v6.2) and docs/BOM-v6.md (v6)
    python site/bom.py --check   exit 1 if one of them is out of date (CI runs this)

site/build.py imports load() and render_page() to write the site pages parts/ (v6.2) and v6/parts/ (archive).
Only the Python standard library is required.
"""
import html
import json
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
REPO = 'https://github.com/ricricucit/kibble-dispenser'
SITE_URL = 'https://ricricucit.github.io/kibble-dispenser/'
LANGS = ('en', 'it', 'de')
LANG_NAMES = {'en': 'English', 'it': 'Italiano', 'de': 'Deutsch'}


def _hw_v6():
    return json.loads((ROOT / 'hardware/v6/cad/v6.json').read_text(encoding='utf-8'))['hardware']


def _hw_v62():
    return json.loads((ROOT / 'hardware/v6.2/plates/summary.json').read_text(encoding='utf-8'))['bought_parts']


DESIGNS = {
    'v6.2': dict(label='v6.2', bom='hardware/v6.2/bom.json', source=_hw_v62, source_name='plates/summary.json (bought_parts)',
                 md='docs/BOM.md', page='parts/', root='../', model='../3d/', print='../print/', archived=False,
                 printed_md='../hardware/v6.2/plates/README.md', folder='hardware/v6.2'),
    'v6': dict(label='v6', bom='hardware/v6/bom.json', source=_hw_v6, source_name='cad/v6.json (hardware)',
               md='docs/BOM-v6.md', page='v6/parts/', root='../../', model='../3d/', print='../print/', archived=True,
               printed_md='../hardware/v6/README.md', folder='hardware/v6'),
}
CURRENT = 'v6.2'


def ui(cfg):
    v = cfg['label']
    t = {
        'title': {'en': 'Bought parts', 'it': 'Pezzi extra', 'de': 'Zukaufteile'},
        'lead': {'en': f'Everything you buy for the Kibble Dispenser Outdoor {v}, besides the printed parts.',
                 'it': f'Tutto quello che si compra per il Kibble Dispenser Outdoor {v}, oltre ai pezzi stampati.',
                 'de': f'Alles, was man für den Kibble Dispenser Outdoor {v} neben den Druckteilen kauft.'},
        'status': {'en': f'Design {v} is designed, not yet printed or tested: quantities can still change.',
                   'it': f'Il progetto {v} è disegnato ma non ancora stampato né provato: le quantità possono ancora cambiare.',
                   'de': f'Entwurf {v} ist konstruiert, aber noch nicht gedruckt oder getestet: die Mengen können sich noch ändern.'},
        'source': {'en': f'Quantities and specifications come from the {v} design data. No shop links: buy wherever suits you.',
                   'it': f'Quantità e caratteristiche vengono dai dati del progetto {v}. Nessun link a negozi: comprate dove preferite.',
                   'de': f'Mengen und Angaben stammen aus den Konstruktionsdaten von {v}. Keine Shop-Links: kauft, wo es euch passt.'},
        'printed': {'en': 'Printed parts and their files', 'it': 'Pezzi stampati e i loro file', 'de': 'Druckteile und ihre Dateien'},
        'model': {'en': f'3D model {v}', 'it': f'Modello 3D {v}', 'de': f'3D-Modell {v}'},
        'print': {'en': 'Print files', 'it': 'File di stampa', 'de': 'Druckdateien'},
        'home': {'en': 'Project home', 'it': 'Pagina del progetto', 'de': 'Projektseite'},
        'licence': {'en': 'Text CC BY 4.0, design data CERN-OHL-P-2.0.',
                    'it': 'Testo CC BY 4.0, dati di progetto CERN-OHL-P-2.0.',
                    'de': 'Text CC BY 4.0, Konstruktionsdaten CERN-OHL-P-2.0.'},
    }
    if cfg['archived']:
        t['archived'] = {'en': f'Archived page: design {v}. The current design is v6.2, with its own list of bought parts.',
                         'it': f'Pagina archiviata: progetto {v}. Il progetto attuale è la v6.2, con il suo elenco di pezzi extra.',
                         'de': f'Archivseite: Entwurf {v}. Der aktuelle Entwurf ist v6.2, mit eigener Zukaufteile-Liste.'}
        t['current'] = {'en': 'Bought parts of v6.2', 'it': 'Pezzi extra della v6.2', 'de': 'Zukaufteile von v6.2'}
    return t


def load(design=CURRENT):
    """Read the design's bom.json and check it against its source list."""
    cfg = DESIGNS[design]
    bom = json.loads((ROOT / cfg['bom']).read_text(encoding='utf-8'))
    qty_of = {}
    for h in cfg['source']():
        qty_of[h['item']] = qty_of.get(h['item'], 0) + int(h['qty'])
    matched, errors = set(), []
    for g in bom['groups']:
        for it in g['items']:
            for lang in LANGS:
                if not it['item'].get(lang) or not it.get('use', {}).get(lang):
                    errors.append(f"{g['id']}: '{it['item'].get('en')}' has no {lang} text")
            if 'match' not in it:
                continue
            unknown = [m for m in it['match'] if m not in qty_of]
            if unknown:
                errors.append(f"{g['id']}: {unknown} not in {cfg['source_name']}")
                continue
            matched.update(it['match'])
            want = sum(qty_of[m] for m in it['match'])
            if it['qty'] != want:
                errors.append(f"{g['id']}: '{it['item']['en']}' qty {it['qty']}, {cfg['source_name']} says {want}")
    missing = [k for k in qty_of if k not in matched]
    if missing:
        errors.append(f"{cfg['source_name']} lines missing from {cfg['bom']}: {missing}")
    if errors:
        sys.exit(f"{cfg['bom']} does not match {cfg['source_name']}:\n  " + '\n  '.join(errors))
    bom['_design'] = design
    return bom


def qty_text(it):
    return f"{it['qty']} ×" if 'qty' in it else ''


# ---------------------------------------------------------------- Markdown
def render_markdown(bom):
    cfg = DESIGNS[bom['_design']]
    U = ui(cfg)
    out = [f"<!-- Generated by site/bom.py from {cfg['bom']}; edit that, then run python site/bom.py -->",
           '',
           f"# Bought parts, design {cfg['label']} / Pezzi extra / Zukaufteile",
           '',
           ' · '.join(f'[{LANG_NAMES[lang]}](#{LANG_NAMES[lang].lower()})' for lang in LANGS),
           '',
           f"Website: <{SITE_URL}{cfg['page']}>",
           '']
    if cfg['archived']:
        out += [f"Archived: this is design {cfg['label']}. The current design is v6.2: [docs/BOM.md](BOM.md).", '']
    for lang in LANGS:
        out += [f'## {LANG_NAMES[lang]}', '', f"**{U['status'][lang]}**", '',
                f"{U['lead'][lang]} {U['source'][lang]}", '']
        for g in bom['groups']:
            out += [f"### {g['title'][lang]}", '']
            if g.get('note'):
                out += [g['note'][lang], '']
            for it in g['items']:
                q = qty_text(it)
                out.append(f"- {'**' + q + '** ' if q else ''}{it['item'][lang]}: {it['use'][lang]}")
            out.append('')
        out += [f"{U['printed'][lang]}: [{cfg['folder']}/]({cfg['printed_md']})", '']
    return '\n'.join(out).rstrip('\n') + '\n'


# ---------------------------------------------------------------- HTML page
def _spans(texts, tag='span'):
    """One element per language; CSS shows only the current one."""
    return ''.join(f'<{tag} data-l="{lang}" lang="{lang}">{html.escape(texts[lang])}</{tag}>' for lang in LANGS)


def render_page(bom, versions_html=''):
    e = html.escape
    cfg = DESIGNS[bom['_design']]
    U = ui(cfg)
    root = cfg['root']
    blocks = []
    for lang in LANGS:
        bands = []
        for g in bom['groups']:
            rows = []
            for it in g['items']:
                q = qty_text(it)
                qty = f'<span class="qty">{e(q)}</span>' if q else '<span class="qty tick" aria-hidden="true"></span>'
                rows.append(f'<li>{qty}<div><h3>{e(it["item"][lang])}</h3><p>{e(it["use"][lang])}</p></div></li>')
            note = f'<p>{e(g["note"][lang])}</p>' if g.get('note') else ''
            bands.append(f'<section class="band" id="{e(g["id"])}-{lang}" aria-labelledby="h-{e(g["id"])}-{lang}">'
                         f'<div class="band-head"><h2 id="h-{e(g["id"])}-{lang}">{e(g["title"][lang])}</h2>{note}</div>'
                         f'<ul class="kit">{"".join(rows)}</ul></section>')
        blocks.append(f'<div class="lang-block" data-l="{lang}" lang="{lang}">{"".join(bands)}</div>')
    label = cfg['label']
    titles = ' '.join(f'data-title-{lang}="{e(U["title"][lang])} · Kibble Dispenser {label}"' for lang in LANGS)
    switch = ''.join(f'<button type="button" data-set-lang="{lang}" lang="{lang}" aria-pressed="{str(lang == "en").lower()}">'
                     f'{lang.upper()}</button>' for lang in LANGS)
    archived = (f'<p class="stamp archived">{_spans(U["archived"])} <a href="{root}parts/" data-keep-lang>{_spans(U["current"])} →</a></p>'
                if cfg['archived'] else '')
    return f'''<!doctype html>
<html lang="en" data-lang="en" {titles}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(U['title']['en'])} · Kibble Dispenser {label}</title>
  <meta name="description" content="{e(U['lead']['en'])} {e(U['status']['en'])}">
  <meta name="theme-color" content="#e1e6e5" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121a1f" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' fill='%23ee6a1f'/%3E%3Cpath d='M13.5 13h5l3.5 15h-12z' fill='%23fff'/%3E%3Ccircle cx='16' cy='16' r='2.6' fill='%2326282c'/%3E%3C/svg%3E">
  <link rel="stylesheet" href="{root}css/site.css">
  <link rel="stylesheet" href="{root}css/parts.css">
  <script src="{root}js/lang.js" defer></script>
</head>
<body>
  <header class="masthead">
    <p class="wordmark"><a href="{root}" data-keep-lang>Kibble Dispenser</a></p>
    <nav aria-label="Pages">
      <ul>
        <li><a href="{cfg['model']}" data-keep-lang>{_spans(U['model'])}</a></li>
        <li><a href="{cfg['print']}" data-keep-lang>{_spans(U['print'])}</a></li>
        <li><a href="{root}" data-keep-lang>{_spans(U['home'])}</a></li>
        <li class="nav-repo"><a href="{REPO}">GitHub</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <section class="parts-head">
      <div class="lang-switch" role="group" aria-label="Language / Lingua / Sprache">{switch}</div>
      <h1>{_spans(U['title'])}</h1>
      {archived}
      <p class="lead">{_spans(U['lead'])}</p>
      <p class="stamp">{_spans(U['status'])}</p>
      <p class="source">{_spans(U['source'])}</p>
    </section>
    {''.join(blocks)}
    <section class="parts-foot">
      <p><a href="{cfg['print']}" data-keep-lang>{_spans(U['printed'])}</a> · <a href="{cfg['model']}" data-keep-lang>{_spans(U['model'])}</a></p>
      <p class="aside">{_spans(U['licence'])} <a href="{REPO}/blob/main/{cfg['bom']}">bom.json</a></p>
      {versions_html}
    </section>
  </main>
</body>
</html>
'''


def main():
    check = '--check' in sys.argv[1:]
    stale = []
    for design, cfg in DESIGNS.items():
        md = render_markdown(load(design))
        path = ROOT / cfg['md']
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != md:
                stale.append(cfg['md'])
            continue
        path.write_text(md, encoding='utf-8')
        print(f"wrote {cfg['md']}")
    if check:
        if stale:
            sys.exit(f'out of date: {", ".join(stale)}: run python site/bom.py')
        print('docs/BOM.md and docs/BOM-v6.md are up to date')


if __name__ == '__main__':
    main()
