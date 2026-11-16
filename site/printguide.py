"""
Step-by-step print guide of the current hardware (print/), in English, Italian and German.

Sources:
  hardware/v6.4/plates/summary.json    plates, parts, products (chassis, module), status against 6.3.0, times, grams,
                                       what is left for someone who printed the 6.3.0 package
  hardware/v6.4/plates/PRINT_GUIDE.md  the detailed checks of each plate (load, supports, slicer, look at the parts, work
                                       after printing, how to judge the test coupons), in English
  site/content/print.toml              every other word of the page, in three languages
The detailed per-plate checks stay in English in every language (the page says so in Italian and German).

site/pages.py calls build(out, pages) with itself as `pages`, for its helpers (page, L, esc, hours, ...).
Writes <out>/print/index.html, a ZIP per product, the Bambu projects, the plain 3MF of each plate and the previews into
<out>/print/files/ and <out>/print/img/; single STL files are linked from GitHub to keep the Pages artifact small.
"""
import html
import json
import re
import shutil
from pathlib import Path

GUIDE_STEP = re.compile(r'^### Step (\w+) - ([A-Z0-9-]+): (.*?) \[(.*?)\](.*)$')
SKIP_LABELS = ('File', 'Parts on the plate', 'Time and filament')


def inline(text):
    """Escape, then the little Markdown the guide uses: `code` and **bold**."""
    t = html.escape(text, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)


def parse_guide(text):
    """{plate key: {'step': '2', 'notes': [...], 'items': [(label, text, [sub, ...]), ...]}} from PRINT_GUIDE.md."""
    steps, cur = {}, None
    for line in text.splitlines():
        m = GUIDE_STEP.match(line)
        if m:
            cur = {'step': m.group(1), 'notes': [], 'items': []}
            steps[m.group(2)] = cur
            continue
        if line.startswith('## ') or line.startswith('### '):
            cur = None
            continue
        if cur is None or not line.strip():
            continue
        if line.startswith('- '):
            body = line[2:]
            label, _, rest = body.partition(': ')
            if not rest and body.endswith(':'):
                label, rest = body[:-1], ''
            elif not rest:
                label, rest = '', body
            cur['items'].append((label.strip(), rest.strip(), []))
        elif line.startswith('  - ') and cur['items']:
            cur['items'][-1][2].append(line[4:].strip())
        elif not line.startswith(' '):
            cur['notes'].append(line.strip())
    return steps


def build(out, pg):
    """pg: the site/pages.py module (helpers and constants)."""
    L, esc, hours, num, size_text = pg.L, pg.esc, pg.hours, pg.num, pg.size_text
    P = pg.load_toml('print.toml')
    plates_dir = pg.PLATES
    summary = json.loads((plates_dir / 'summary.json').read_text(encoding='utf-8'))
    guide = parse_guide((plates_dir / 'PRINT_GUIDE.md').read_text(encoding='utf-8'))
    part_name, colour = P['part'], P['colour']
    for pl in summary['plates']:
        if pl['key'] not in guide:
            raise SystemExit(f"PRINT_GUIDE.md has no step for plate {pl['key']}")
        if pl['key'] not in P['plate']:
            raise SystemExit(f"site/content/print.toml has no title for plate {pl['key']}")
        for x in pl['parts']:
            if x['id'] not in part_name:
                raise SystemExit(f"site/content/print.toml has no name for part {x['id']}")
    tot = summary['totals']
    page_dir = out / 'print'
    files, img = page_dir / 'files', page_dir / 'img'
    for d in (files / 'plates', files / 'preview', img):
        d.mkdir(parents=True, exist_ok=True)
    gh = 'hardware/v6.4/plates'
    raw = f'{pg.REPO}/raw/main/{gh}/'
    plates = {pl['key']: pl for pl in summary['plates']}
    stamp = tuple(int(x) for x in summary['generated'].split('-')) + (0, 0, 0)
    lic = [(pg.ROOT / 'LICENSES/CERN-OHL-P-2.0.txt', 'LICENSES/CERN-OHL-P-2.0.txt'), (pg.ROOT / 'LICENSES/CC-BY-4.0.txt', 'LICENSES/CC-BY-4.0.txt')]

    def sz(path):
        n = path.stat().st_size
        return L(lambda lang: size_text(n, lang))

    def g_text(g, nd=None):
        return L(lambda lang: num(g, lang, (0 if g >= 10 else 1) if nd is None else nd) + ' g')

    # ---- files: Bambu projects, plain 3MF and previews, one ZIP per product
    products = {k: v for k, v in summary['products'].items() if 'bambu_projects' in v}   # chassis, module
    for f in summary['files']['bambu_projects']:
        shutil.copy2(plates_dir / f, files / f)
    for sub in ('plates', 'preview'):
        for f in sorted((plates_dir / sub).iterdir()):
            shutil.copy2(f, files / sub / f.name)
    zips = {}
    for pid, prod in products.items():
        stl = sorted({f for c in summary['parts_checklist'] if c.get('product') == pid for f in c.get('stl', [])})
        if pid == 'chassis':        # the test pieces belong to the chassis package
            stl = sorted(set(stl) | {f for c in summary['parts_checklist'] if c['kind'] == 'test' for f in c.get('stl', [])})
        plain = [plates[k]['plain_3mf'] for k in prod['plates'] if k in plates]
        name = f'Kibble_Dispenser_6.4_{pid}_print_files.zip'
        members = ([(plates_dir / f, f) for f in prod['bambu_projects']] + [(plates_dir / f, f) for f in plain]
                   + [(plates_dir / f, f) for f in stl] + [(plates_dir / 'PRINT_GUIDE.md', 'PRINT_GUIDE.md'),
                                                           (plates_dir / 'summary.json', 'summary.json')] + lic)
        pg.write_zip(files / name, name[:-4], members, stamp)
        zips[pid] = name

    def dots(cols):
        return ''.join(f'<span class="cdot" style="--c:{pg.COLOUR_VAR[c]}" title="{esc(colour[c]["en"])}"></span>' for c in cols)

    fil_names = {'black': P['ams']['black']['name'], 'orange': P['ams']['orange']['name'], 'green': P['ams']['green']['name'],
                 'yellow': P['ams']['tpu']['name']}

    # ---- head
    facts = f'''<dl class="facts big">
          <div><dt>{L(P['facts']['plates'])}</dt><dd>{tot['plates']}</dd></div>
          <div><dt>{L(P['facts']['time'])}</dt><dd>{esc(hours(tot['time_min']))}</dd></div>
          <div><dt>{L(P['facts']['petg'])}</dt><dd>{g_text(tot['grams_PETG'], 0)}</dd></div>
          <div><dt>{L(P['facts']['tpu'])}</dt><dd>{g_text(tot['grams_TPU'], 1)}</dd></div>
          <div><dt>{L(P['facts']['swaps'])}</dt><dd>{tot['colour_swaps']}</dd></div>
        </dl>'''
    toc_keys = ['done63', 'downloads', 'ams', 'step0', 'step1', 'plates', 'final', 'checklist']
    review = f'{pg.REPO}/blob/main/docs/reviews/2026-11-15-v6.4-print-review/REVIEW.md'
    head = f'''    <section class="phead" aria-labelledby="p-title">
      <p class="kicker">{L(P['head']['kicker'])}</p>
      <h1 id="p-title">{L(P['head']['title'])}</h1>
      <p class="lead">{L(P['head']['lead'])}</p>
      <p>{L(P['head']['products'])}</p>
      <div class="banner" role="note">
        <p class="banner-t">{L(P['banner']['title'])}</p>
        <p>{L(P['banner']['body'])} <a href="{review}">{L(P['banner']['review'])}</a></p>
      </div>
      {facts}
      <nav class="toc" aria-label="On this page"><ul>
        {''.join(f'<li><a href="#{k}">{L(P["toc"][k])}</a></li>' for k in toc_keys)}
      </ul></nav>
    </section>'''

    # ---- already printed 6.3.0
    todo = summary['to_print_if_print_v63_is_done']
    tt = todo['totals']
    todo_plates = {lang: ', '.join(f'<a href="#plate-{k}">{k}</a>' for k in todo['plates']) for lang in pg.LANGS}
    todo_text = {lang: P['done63']['todo'][lang].replace('{plates}', todo_plates[lang]).replace('{time}', hours(tt['time_min']))
                 .replace('{petg}', num(tt['grams_PETG'], lang) + ' g').replace('{tpu}', num(tt['grams_TPU'], lang, 1) + ' g')
                 for lang in pg.LANGS}
    todo_html = pg.Lh(todo_text)
    done63 = f'''    <section class="psec" id="done63" aria-labelledby="d63-title">
      <h2 id="d63-title">{L(P['done63']['title'])}</h2>
      <p class="lead">{L(P['done63']['lead'])}</p>
      <ul class="d63">
        <li class="d63-keep">{L(P['done63']['keep'])}</li>
        <li class="d63-drop">{L(P['done63']['drop'])}</li>
        <li class="d63-todo"><strong>{todo_html}</strong></li>
      </ul>
      <p class="aside">{L(P['done63']['skip'])} <a href="#plates">{L(P['done63']['jump'])} →</a></p>
    </section>'''

    # ---- downloads per product
    blocks = []
    for pid, prod in products.items():
        rows = [f'<li class="dl-main"><a href="files/{zips[pid]}" download><span class="ft">ZIP</span><span class="dl-t">{L(P["dl"]["zip"])}</span>'
                f'<span class="dl-s">{esc(zips[pid])} · {sz(files / zips[pid])}</span></a></li>']
        for f in prod['bambu_projects']:
            rows.append(f'<li><a href="files/{esc(f)}" download><span class="ft">3MF</span><span class="dl-t">{L(P["dl"]["project"][f])}</span>'
                        f'<span class="dl-s">{esc(f)} · {sz(plates_dir / f)}</span></a></li>')
        blocks.append(f'<div class="dl-prod"><h3>{L(P["dl"][pid])}</h3><ul class="dl-list">{"".join(rows)}</ul></div>')
    dl = f'''    <section class="psec" id="downloads" aria-labelledby="dl-title">
      <h2 id="dl-title">{L(P['dl']['title'])}</h2>
      <p class="lead">{L(P['dl']['lead'])}</p>
      <div class="dl-prods">{''.join(blocks)}</div>
      <p class="aside"><a href="{pg.REPO}/releases/tag/hw-v6.4.0">{L(P['dl']['release'])}</a></p>
      <p class="check-note">{L(P['dl']['check'])}</p>
    </section>'''

    # ---- AMS lite
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
      <ul class="notes"><li>{L(P['ams_spare'])}</li><li>{L(a['note_tpu'])}</li></ul>
    </section>'''

    # ---- step 0
    g = tot['grams_per_filament']
    fill0 = {'black': g['PETG black'], 'green': g['PETG green'], 'orange': g['PETG orange'], 'tpu': g['TPU yellow']}

    def filled(texts):
        out_ = {}
        for lang in pg.LANGS:
            v = texts[lang]
            for k, x in fill0.items():
                v = v.replace('{' + k + '}', num(x, lang, 0 if x >= 10 else 1) + ' g')
            out_[lang] = v
        return out_
    step0 = f'''    <section class="psec" id="step0" aria-labelledby="s0-title">
      <h2 id="s0-title">{L(P['step0']['title'])}</h2>
      <ol class="gsteps0">{''.join(f'<li>{L(filled(i))}</li>' for i in P['step0']['items'])}</ol>
    </section>'''

    # ---- plate steps
    T = P['plates']
    english = P['plates']['english']

    def guide_lists(key):
        st = guide[key]
        load = sup = ''
        lists = []
        notes = [n for n in st['notes']]
        for label, text, sub in st['items']:
            if label in SKIP_LABELS:
                continue
            if label == 'Load':
                load = text
            elif label == 'Supports':
                sup = text
            elif label == 'Status note':
                notes.append(text)
            elif sub:
                lab = (T['judge'] if label.startswith('How to judge') else T['slicer'] if label.startswith('Check in the slicer')
                       else T['look'] if label.startswith('Look at') else T['after'] if label.startswith('Work after') else None)
                head_ = L(lab) if lab else f'<span lang="en">{inline(label)}</span>'
                extra = f' <span class="g-sub" lang="en">({inline(label[len("How to judge"):].strip())})</span>' if label.startswith('How to judge') and len(label) > 12 else ''
                lists.append(f'<div class="glist{" gjudge" if label.startswith("How to judge") else ""}"><h4>{head_}{extra}</h4>'
                             f'<ul lang="en">{"".join(f"<li>{inline(s)}</li>" for s in sub)}</ul></div>')
            else:
                lists.append(f'<p class="gline" lang="en">{inline(label + ": " if label else "")}{inline(text)}</p>')
        return load, sup, notes, lists

    def step_card(key):
        pl = plates[key]
        st = guide[key]
        name, w, h = pg.trim_preview(plates_dir / pl['preview_iso'], img / f'{key}_iso.webp')
        size = f' width="{w}" height="{h}"' if w else ''
        parts = ''.join(f'<li>{dots(x["colours"])}<span class="pn">{L(part_name[x["id"]])}</span>'
                        f'<span class="q">×{x["qty"]}</span></li>' for x in pl['parts'])
        fils = []
        for fil, gg in pl['est_grams_per_filament'].items():
            c = fil.split()[-1]
            fils.append(f'<li><span class="cdot" style="--c:{pg.COLOUR_VAR[c]}"></span>{L(fil_names[c])} <strong>{g_text(gg["grams"])}</strong></li>')
        load, sup, notes, lists = guide_lists(key)
        status = pl['status']
        prod = T['chassis'] if pl['product'] == 'chassis' else T['module']
        note_html = ''.join(f'<p class="pnote" lang="en">{inline(n)}</p>' for n in notes)
        if key == 'MOD-TPU-1':
            note_html = f'<p class="pnote">{L(T["only_alone"])}</p>'
        plain = Path(pl['plain_3mf']).name
        return f'''<li class="gstep gstep-{status}" id="plate-{esc(key)}">
          <div class="gstep-head">
            <p class="gnum">{L(T['step'])} {esc(st['step'])}</p>
            <div><p class="pkey">{esc(key)} · {L(prod)} · <span class="gbadge gbadge-{status}">{L(T[status])}</span></p>
              <h3>{L(P['plate'][key])}</h3></div>
          </div>
          <div class="gstep-body">
            <a class="pimg" href="files/{esc(pl['preview_top'])}"><img src="img/{esc(name)}"{size} loading="lazy" decoding="async" alt="{esc(key)}"></a>
            <div class="pbody">
              <ul class="pparts">{parts}</ul>
              <ul class="pfils">{''.join(fils)}</ul>
              <p class="pmeta"><span>{esc(pl['est_time_hm'])}</span><span>{pl['colour_swaps']} {L(T['swaps'])}</span>
                <span>{esc(pl['bambu_project'])} · {L(T['in_project'])} {pl['plate_in_project']}</span></p>
              {note_html}
              <dl class="gkv">
                <div><dt>{L(T['load'])}</dt><dd lang="en">{inline(load)}</dd></div>
                <div><dt>{L(T['supports'])}</dt><dd lang="en">{inline(sup)}</dd></div>
              </dl>
              <p class="pdl"><a class="btn btn-sm" href="files/plates/{esc(plain)}" download>{L(T['download'])} · {sz(plates_dir / 'plates' / plain)}</a></p>
            </div>
          </div>
          <div class="gstep-lists">{''.join(lists)}</div>
        </li>'''

    order = sorted(guide, key=lambda k: (int(re.sub(r'\D', '', guide[k]['step']) or 0), guide[k]['step']))
    tests = [k for k in order if re.fullmatch(r'1[a-z]', guide[k]['step'])]
    rest = [k for k in order if k not in tests]
    eng = f'<p class="aside g-en">{L(english)}</p>'
    step1 = f'''    <section class="psec" id="step1" aria-labelledby="s1-title">
      <h2 id="s1-title">{L(P['step1']['title'])}</h2>
      <p class="lead">{L(P['step1']['lead'])}</p>
      {eng}
      <ol class="gsteps">{''.join(step_card(k) for k in tests)}</ol>
    </section>'''
    steps = f'''    <section class="psec" id="plates" aria-labelledby="plates-title">
      <h2 id="plates-title">{L(T['title'])}</h2>
      <p class="lead">{L(T['lead'])}</p>
      {eng}
      <ol class="gsteps">{''.join(step_card(k) for k in rest)}</ol>
    </section>'''

    final = f'''    <section class="psec" id="final" aria-labelledby="fin-title">
      <h2 id="fin-title">{L(P['final']['title'])}</h2>
      <ol class="gsteps0">{''.join(f'<li>{L(i)}</li>' for i in P['final']['items'])}</ol>
    </section>'''

    # ---- bought parts, by product
    import bom
    b = bom.load('v6.4')
    prods = {p['id']: p for p in b['products']}
    cols = []
    for pid in prods:
        groups = ''.join(f'<h4>{L(gr["title"])}</h4><ul class="blist">'
                         + ''.join(f'<li><span class="q">{it["qty"]} ×</span><span class="pn">{L(it["item"])}</span></li>' for it in gr['items'] if 'qty' in it)
                         + '</ul>' for gr in b['groups'] if gr.get('product') == pid)
        cols.append(f'<div class="sblock"><h3>{L(prods[pid]["title"])}</h3>{groups}</div>')
    bought = f'''    <section class="psec" id="bought" aria-labelledby="bought-title">
      <h2 id="bought-title">{L(P['bought']['title'])}</h2>
      <p class="lead">{L(P['bought']['lead'])}</p>
      <div class="sgrid two">{''.join(cols)}</div>
      <p class="cta-row"><a class="btn" href="../parts/" data-keep-lang>{L(P['bought']['link'])} →</a></p>
    </section>'''

    # ---- check list (ticks kept in the browser by js/main.js, as on the other print pages)
    ck = P['check']
    groups_ck = {'chassis': [], 'module': [], 'test': []}
    for c in summary['parts_checklist']:
        k = 'test' if c['kind'] == 'test' else c.get('product', 'chassis')
        groups_ck[k].append(
            f'<li><label><input type="checkbox" data-check="{esc(c["id"])}"> {dots(c["colours"])}'
            f'<span class="pn">{L(part_name[c["id"]])}</span><span class="q">×{c["qty"]}</span>'
            f'<span class="pk">{esc(", ".join(c["plates"]))}</span></label></li>')
    checklist = f'''    <section class="psec" id="checklist" aria-labelledby="ck-title">
      <h2 id="ck-title">{L(ck['title'])}</h2>
      <p class="lead">{L(ck['lead'])}</p>
      <p class="ck-count" aria-live="polite"><strong data-check-count>0</strong> / {len(summary['parts_checklist'])} {L(ck['done'])}
        <button type="button" class="btn btn-sm" data-check-reset>{L(ck['reset'])}</button></p>
      <h3 class="ck-h">{L(P['dl']['chassis'])}</h3>
      <ul class="cklist">{''.join(groups_ck['chassis'])}</ul>
      <h3 class="ck-h">{L(P['dl']['module'])}</h3>
      <ul class="cklist">{''.join(groups_ck['module'])}</ul>
      <h3 class="ck-h">{L(ck['tests'])}</h3>
      <ul class="cklist">{''.join(groups_ck['test'])}</ul>
    </section>'''

    stl = sorted((plates_dir / 'stl').iterdir())
    stl_items = ''.join(f'<li><a href="{raw}stl/{esc(f.name)}">{esc(f.name)}</a> <span>{sz(f)}</span></li>' for f in stl)
    stl_html = f'''    <section class="psec" id="stl" aria-labelledby="stl-title">
      <h2 id="stl-title">{L(P['files']['title'])}</h2>
      <p class="lead">{L(P['files']['lead'])}</p>
      <details class="stl"><summary>{L(P['files']['show'])} ({len(stl)})</summary><ul>{stl_items}</ul></details>
    </section>'''

    notes = ''.join(f'<li>{L(i)}</li>' for i in P['notes']['items'])
    notes_html = f'''    <section class="psec" id="notes" aria-labelledby="notes-title">
      <h2 id="notes-title">{L(P['notes']['title'])}</h2>
      <ul class="notes">{notes}</ul>
      <p class="cta-row">
        <a class="btn" href="{pg.REPO}/blob/main/{gh}/PRINT_GUIDE.md">{L(P['notes']['guide'])}</a>
        <a class="btn" href="{pg.REPO}/tree/main/{gh}">{L(P['notes']['github'])}</a>
      </p>
      <p class="aside">{L(P['footer']['licence'])}</p>
    </section>'''

    H = pg.load_toml('home.toml')
    nav = [('../', pg.NAV_HOME, True), ('../3d/', P['nav']['model'], True), ('../parts/', P['nav']['parts'], True),
           ('../module/', P['nav']['module'], True), ('../assembly/', P['nav']['assembly'], False)]
    body = '\n'.join([head, done63, dl, ams, step0, step1, steps, final, bought, checklist, stl_html, notes_html])
    s = pg.page(root='../', titles=P['meta']['title'], description=P['meta']['description']['en'], nav=nav, body=body,
                footer=pg.footer_html('../', H), cls='print guide')
    (page_dir / 'index.html').write_text(s, encoding='utf-8')
    return page_dir / 'index.html'
