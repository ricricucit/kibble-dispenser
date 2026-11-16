"""
Versions shown in the site footers, read at build time from the sources of truth (see VERSIONS.md):
hardware/VERSION, hardware/module/VERSION (the electronics module case), firmware/VERSION and product/product.json, plus
the commit the site is built from
(GITHUB_SHA on CI, git otherwise). Standard library only.
"""
import html
import json
import os
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/ricricucit/kibble-dispenser'
RELEASES = f'{REPO}/releases'
LANGS = ('en', 'it', 'de')
STATUS = {
    'designed': {'en': 'designed', 'it': 'disegnato', 'de': 'konstruiert'},
    'printed': {'en': 'printed', 'it': 'stampato', 'de': 'gedruckt'},
    'tested': {'en': 'tested', 'it': 'provato', 'de': 'getestet'},
    'field-proven': {'en': 'field-proven', 'it': 'collaudato sul campo', 'de': 'im Einsatz bewährt'},
}
UNRELEASED = {'en': 'Product: not released yet', 'it': 'Prodotto: non ancora rilasciato', 'de': 'Produkt: noch nicht veröffentlicht'}
PRODUCT = {'en': 'Product', 'it': 'Prodotto', 'de': 'Produkt'}
CASE = {'en': 'Module case', 'it': 'Modulo case', 'de': 'Modul case'}


def _git(*args):
    try:
        return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def load():
    hw = tomllib.loads((ROOT / 'hardware/VERSION').read_text(encoding='utf-8'))
    fw = tomllib.loads((ROOT / 'firmware/VERSION').read_text(encoding='utf-8'))
    product = json.loads((ROOT / 'product/product.json').read_text(encoding='utf-8'))
    mod_file = ROOT / 'hardware/module/VERSION'
    mod = tomllib.loads(mod_file.read_text(encoding='utf-8')) if mod_file.exists() else None
    sha = os.environ.get('GITHUB_SHA') or _git('rev-parse', 'HEAD')
    date = _git('log', '-1', '--format=%cs', sha) if sha else ''
    return {'hw': hw['version'], 'status': hw['status'], 'fw': fw['version'], 'case': mod['version'] if mod else None,
            'product': product.get('version') or 'unreleased', 'sha': sha, 'date': date}


def text(v, lang):
    """'Hardware v6.4.0 (designed) · Module case v1.0.0 · Firmware v0.1.0+dev.20260324 · Product: not released yet'"""
    status = STATUS.get(v['status'], {}).get(lang, v['status'])
    product = UNRELEASED[lang] if v['product'] == 'unreleased' else f'{PRODUCT[lang]} v{v["product"]}'
    case = f' · {CASE[lang]} v{v["case"]}' if v.get('case') else ''
    return f'Hardware v{v["hw"]} ({status}){case} · Firmware v{v["fw"]} · {product}'


def build_text(v):
    return f'build {v["sha"][:7]}, {v["date"]}' if v['sha'] else ''


def html_line(v, lang=None):
    """Footer line with links to the releases and to the commit. One language, or one <span> per language."""
    esc = html.escape
    if lang:
        label = esc(text(v, lang))
    else:
        label = ''.join(f'<span data-l="{lg}" lang="{lg}">{esc(text(v, lg))}</span>' for lg in LANGS)
    build = (f' · build <a href="{REPO}/commit/{esc(v["sha"])}">{esc(v["sha"][:7])}</a>, {esc(v["date"])}' if v['sha'] else '')
    return f'<p class="versions"><a href="{RELEASES}">{label}</a>{build}</p>'


def viewer_data(v):
    """For the 3D page (site/viewer/template.html): label per language, link, build text."""
    return {'label': {lg: text(v, lg) for lg in LANGS}, 'href': RELEASES, 'build': build_text(v),
            'commit': f'{REPO}/commit/{v["sha"]}' if v['sha'] else ''}
