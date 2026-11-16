"""
Page of the electronics module case 1.0 (module/), in English, Italian and German.

Numbers come from hardware/v6.4/cad/v64.json (interface, module) and hardware/module/VERSION; the drawing is
hardware/module/case-1.0/interface/interfaccia_modulo_v64.png (and .pdf, copied next to the page). Texts in
site/content/module.toml. site/pages.py calls build(out, pages) with itself as `pages`, for its helpers.
"""
import json
import shutil
import tomllib


def build(out, pg):
    L, Lh, esc, num = pg.L, pg.Lh, pg.esc, pg.num
    M = pg.load_toml('module.toml')
    d = json.loads((pg.ROOT / 'hardware/v6.4/cad/v64.json').read_text(encoding='utf-8'))
    ver = tomllib.loads((pg.ROOT / 'hardware/module/VERSION').read_text(encoding='utf-8'))
    I, mod = d['interface'], d['module']
    inter = pg.ROOT / 'hardware/module/case-1.0/interface'
    page_dir = out / 'module'
    files = page_dir / 'files'
    files.mkdir(parents=True, exist_ok=True)
    shutil.copy2(inter / 'interfaccia_modulo_v64.pdf', files / 'kibble-dispenser-module-interface.pdf')
    shutil.copy2(inter / 'interfaccia_modulo_v64.png', page_dir / 'interface.png')
    w, h = pg.img_size(page_dir / 'interface.png', (1200, 850))

    def f(texts, **kw):
        """per-language text with {name} placeholders; values are numbers (formatted per language) or strings"""
        out_ = {}
        for lang in pg.LANGS:
            v = texts[lang]
            for k, x in kw.items():
                if isinstance(x, (int, float)):
                    x = num(x, lang, 0 if float(x).is_integer() else 1)
                v = v.replace('{' + k + '}', x)
            out_[lang] = v
        return out_

    ll, acc, el = I['locating_locking'], I['electrical_J1'], I['electrical_J1']['harness']
    travel = float(I['locating_locking']['insertion'].split('mm')[0].split()[-1])
    torque = {'en': '0.5 N·m', 'it': '0,5 N·m', 'de': '0,5 N·m'}
    access = acc['access']
    fit_items = []
    for i, t in enumerate(M['fit']['items']):
        kw = dict(travel=travel, lowered=access['module_lowered_mm'], max=access['tail_allows_mm'])
        txt = f(t, **kw)
        if '{torque}' in t['en']:
            txt = {lang: txt[lang].replace('{torque}', torque[lang]) for lang in pg.LANGS}
        fit_items.append(f'<li>{L(txt)}</li>')

    op, env = I['opening'], I['module_envelope']
    post, sock, scr = ll['posts'], ll['module_sockets'], ll['screws']
    Dm = M['interface']['dims']

    def dim(label, en, it=None, de=None):
        vals = {'en': en, 'it': it or en.replace('.', ','), 'de': de or en.replace('.', ',')}
        return f'<div><dt>{L(label)}</dt><dd>{L(vals)}</dd></div>'
    width = round(2 * env['half_width_y'], 1)
    height = round(env['top_z'] - env['bottom_z'], 1)
    dims = ''.join([
        dim(Dm['opening'], f"{op['opening_width_mm']} × {op['opening_height_mm']} mm (x ≥ {op['prism_plan'].split('x >= ')[1].split(',')[0]}, |y| ≤ {op['prism_plan'].split('|y| <= ')[1]})"),
        dim(Dm['envelope'], f"{width:g} × {height:g} mm, back face x {env['back_face_x']}, z {env['bottom_z']} … {env['top_z']}"),
        dim(Dm['gap'], f"{op['gap_mm']} mm all round, top seam {op['top_seam_mm']} mm",
            f"{op['gap_mm']} mm tutto intorno, fessura in alto {op['top_seam_mm']} mm".replace('.', ','),
            f"{op['gap_mm']} mm rundum, obere Fuge {op['top_seam_mm']} mm".replace('.', ',')),
        dim(Dm['posts'], f"Ø{post['d']:g} at (x {post['xy'][0][0]:g}, y ±{abs(post['xy'][0][1]):g}), z {post['z'][0]:g} … {post['z'][1]:g}, M3 insert in the lower end",
            f"Ø{post['d']:g} in (x {post['xy'][0][0]:g}, y ±{abs(post['xy'][0][1]):g}), z {post['z'][0]:g} … {post['z'][1]:g}, inserto M3 nell'estremità bassa".replace('.', ','),
            f"Ø{post['d']:g} bei (x {post['xy'][0][0]:g}, y ±{abs(post['xy'][0][1]):g}), z {post['z'][0]:g} … {post['z'][1]:g}, M3-Einsatz im unteren Ende".replace('.', ',')),
        dim(Dm['sockets'], f"Ø{sock['d']:g}, z {sock['z'][0]:g} … {sock['z'][1]:g}; the post ends stop on the socket floors",
            f"Ø{sock['d']:g}, z {sock['z'][0]:g} … {sock['z'][1]:g}; le colonnine si fermano sul fondo delle sedi".replace('.', ','),
            f"Ø{sock['d']:g}, z {sock['z'][0]:g} … {sock['z'][1]:g}; die Säulenenden stehen auf den Buchsenböden".replace('.', ',')),
        dim(Dm['screws'], f"2 × {scr['type']}, from below, hex 2.5, 0.5 N·m",
            f"2 × {scr['type']}, da sotto, esagono 2,5, 0,5 N·m", f"2 × {scr['type']}, von unten, Innensechskant 2,5, 0,5 N·m"),
        dim(Dm['lip'], f"{env['top_lip']['h']:g} × {env['top_lip']['t']:g} mm, behind the shell wall ({env['top_lip']['where'].split(',')[1].strip()})",
            f"{env['top_lip']['h']:g} × {env['top_lip']['t']:g} mm, dietro la parete del guscio ({env['top_lip']['where'].split(',')[1].strip()})".replace('.', ','),
            f"{env['top_lip']['h']:g} × {env['top_lip']['t']:g} mm, hinter der Hüllenwand ({env['top_lip']['where'].split(',')[1].strip()})".replace('.', ',')),
        dim(Dm['keepout'], I['keep_out']['above_the_lid'].replace(':', ' ·', 1)),
    ])

    pins = ''.join(f'<div><dt>{L(M["j1"]["pin"])} {p}</dt><dd>{L(M["j1"]["pins"][p])}</dd></div>' for p in sorted(acc['pins']))
    tail, chk = el['tail'], el['checks']
    harness = ''.join(f'<li>{L(x)}</li>' for x in [
        f(M['harness']['tail'], tail=tail['length_mm'], parked=chk['tail_parked_path_mm'], max=chk['max_lowering_with_5mm_spare_mm'],
          lowered=access['module_lowered_mm'], need=chk['lowered_path_mm_by_D'][str(int(access['module_lowered_mm']))]),
        f(M['harness']['v12'], len=el['branch_12v']['length_mm']),
        f(M['harness']['servo'], len=el['branch_servo']['length_mm']),
        M['harness']['splice']])

    env_in = mod['internal_envelope']
    depth = env_in['depth_back_wall_to_skin_mm']
    d0, d1 = depth['z -50']['y 0'], depth['z -98']['y 34']
    slots = env_in['slots']
    b0, b1 = slots['in_front_of_B_mm (z -86..-46, 68 wide / 40 wide)']
    inside_dl = ''.join([
        f'<div><dt>{L(M["inside"]["height"])}</dt><dd>{L(f(M["inside"]["height_v"], floor=env_in["inner_height_floor_to_land_mm"], rim=env_in["inner_height_under_the_rim_mm"]))}</dd></div>',
        f'<div><dt>{L(M["inside"]["width"])}</dt><dd>{L(f(M["inside"]["width_v"], guides=env_in["inner_width_between_guides_mm"], slot=env_in["board_slot_width_mm"], front=env_in["inner_width_front_mm"]))}</dd></div>',
        f'<div><dt>{L(M["inside"]["depth"])}</dt><dd>{L(f(M["inside"]["depth_v"], d0=d0, d1=d1))}</dd></div>',
        f'<div><dt>{L(M["inside"]["volume"])}</dt><dd>≈ {env_in["free_volume_cm3"]:g} cm³</dd></div>'])
    fits = ''.join(f'<li>{L(f(x, gap=slots["between_A_and_B_mm"], b0=b0, b1=b1))}</li>' for x in M['inside']['fits'])

    toc = ''.join(f'<li><a href="#{k}">{L(M["toc"][k])}</a></li>' for k in ('fit', 'interface', 'j1', 'harness', 'inside', 'files'))
    repo = pg.REPO
    body = f'''    <section class="phead" aria-labelledby="m-title">
      <p class="kicker">{L(M['head']['kicker'])}</p>
      <h1 id="m-title">{L(M['head']['title'])}</h1>
      <p class="lead">{L(M['head']['lead'])}</p>
      <div class="banner" role="note">
        <p class="banner-t">{L(M['banner']['title'])}</p>
        <p>{L(M['banner']['body'])} <a href="{repo}/issues/2">#2</a> · <a href="{repo}/issues/3">#3</a></p>
      </div>
      <dl class="facts big">
        <div><dt>{L({'en': 'version', 'it': 'versione', 'de': 'Version'})}</dt><dd>{esc(ver['name'])}</dd></div>
        <div><dt>tag</dt><dd>case-v{esc(ver['version'])}</dd></div>
        <div><dt>{L({'en': 'fits', 'it': 'si monta su', 'de': 'passt zu'})}</dt><dd>{L({'en': 'hardware 6.4', 'it': 'hardware 6.4', 'de': 'Hardware 6.4'})}</dd></div>
        <div><dt>{L({'en': 'status', 'it': 'stato', 'de': 'Status'})}</dt><dd>{L({'en': 'designed', 'it': 'disegnato', 'de': 'konstruiert'})}</dd></div>
      </dl>
      <nav class="toc" aria-label="On this page"><ul>{toc}</ul></nav>
    </section>
    <section class="psec" id="fit" aria-labelledby="fit-title">
      <h2 id="fit-title">{L(M['fit']['title'])}</h2>
      <ol class="gsteps0">{''.join(fit_items)}</ol>
    </section>
    <section class="psec" id="interface" aria-labelledby="if-title">
      <h2 id="if-title">{L(M['interface']['title'])}</h2>
      <p class="lead">{L(M['interface']['lead'])}</p>
      <figure class="sheet if-fig"><a href="files/kibble-dispenser-module-interface.pdf"><img src="interface.png" width="{w}" height="{h}" loading="lazy" decoding="async"
        {pg.alt_attrs(M['interface']['img_alt'])}></a>
        <figcaption><a href="files/kibble-dispenser-module-interface.pdf" download>{L(M['interface']['drawing'])} · PDF</a></figcaption></figure>
      <dl class="mdims">{dims}</dl>
    </section>
    <section class="psec" id="j1" aria-labelledby="j1-title">
      <h2 id="j1-title">{L(M['j1']['title'])}</h2>
      <p class="lead">{L(M['j1']['lead'])}</p>
      <dl class="mdims pins">{pins}</dl>
      <ul class="notes"><li>{L(M['j1']['current'])}</li><li>{L(M['j1']['verify'])}</li></ul>
    </section>
    <section class="psec" id="harness" aria-labelledby="h-title">
      <h2 id="h-title">{L(M['harness']['title'])}</h2>
      <p class="lead">{L(M['harness']['lead'])}</p>
      <ul class="notes">{harness}</ul>
    </section>
    <section class="psec" id="inside" aria-labelledby="in-title">
      <h2 id="in-title">{L(M['inside']['title'])}</h2>
      <p class="lead">{L(M['inside']['lead'])}</p>
      <dl class="mdims">{inside_dl}</dl>
      <h3>{L(M['inside']['fits_title'])}</h3>
      <ul class="notes">{fits}</ul>
      <p class="aside">{L(M['inside']['not_fit'])}</p>
      <p class="aside"><a href="{repo}/blob/main/docs/PROTOTYPE_BENCH.md">{L(M['inside']['bench'])}</a></p>
    </section>
    <section class="psec" id="files" aria-labelledby="f-title">
      <h2 id="f-title">{L(M['files']['title'])}</h2>
      <ul class="links">
        <li><a href="../print/#plate-MOD-1" data-keep-lang>{L(M['files']['print'])}</a></li>
        <li><a href="files/kibble-dispenser-module-interface.pdf" download>{L(M['files']['pdf'])}</a></li>
        <li><a href="{repo}/tree/main/hardware/module/case-1.0">{L(M['files']['folder'])}</a></li>
        <li><a href="../3d/" data-keep-lang>{L(M['files']['model'])}</a></li>
        <li><a href="../assembly/">{L(M['files']['assembly'])}</a></li>
      </ul>
      <p class="aside">{L(M['files']['licence'])}</p>
    </section>'''
    H = pg.load_toml('home.toml')
    nav = [('../', pg.NAV_HOME, True), ('../3d/', M['nav']['model'], True), ('../print/', M['nav']['print'], True),
           ('../parts/', M['nav']['parts'], True)]
    s = pg.page(root='../', titles=M['meta']['title'], description=M['meta']['description']['en'], nav=nav, body=body,
                footer=pg.footer_html('../', H), cls='print module')
    (page_dir / 'index.html').write_text(s, encoding='utf-8')
    return page_dir / 'index.html'
