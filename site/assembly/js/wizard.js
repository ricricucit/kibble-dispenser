/* Kibble Dispenser Outdoor v6.3 - assembly wizard (three.js r128, no other libraries).
   Data: window.WIZ_DATA = {steps: <steps.json>, parts: [...], geomsB64 | modelBase, version, mode, templateHref}.
   Two reading orders (steps.json meta.flows): "kit" (install the ready-made unit) and "diy" (build it yourself);
   the reader's position S.i counts inside the chosen flow, STEPS indexes stay global (stills, 3D state).
   Frame: Z-up, mm, shaft axis x=y=0 (same as the CAD and the existing viewer). */
(function () {
  'use strict';
  const D = window.WIZ_DATA || {};
  const ST = D.steps || { steps: [], items: {}, glossary: {}, ui: {}, meta: {} };
  const STEPS = ST.steps || [];
  const GL = ST.glossary || {};
  const ITEMS = ST.items || {};
  const STILL = D.mode === 'stills';
  const LANGS = ['en', 'it', 'de'];
  const $ = (id) => document.getElementById(id);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  const DEG = Math.PI / 180;

  /* ------------------------------------------------------------------ language */
  function pickLang() {
    let q = null;
    try { q = new URLSearchParams(location.search).get('lang'); } catch (e) { q = null; }
    if (q && LANGS.includes(q.toLowerCase())) return q.toLowerCase();
    const nav = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en'];
    for (const l of nav) { const s = String(l || '').slice(0, 2).toLowerCase(); if (LANGS.includes(s)) return s; }
    return 'en';
  }
  let LANG = pickLang();
  const tr = (o) => (o == null ? '' : typeof o === 'string' ? o : (o[LANG] != null ? o[LANG] : (o.en != null ? o.en : '')));
  const ui = (k) => tr((ST.ui || {})[k]) || k;
  const cap1 = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
  function gEntry(key) {
    for (const sec of ['parts', 'diy_parts', 'hardware', 'tools', 'terms']) if (GL[sec] && GL[sec][key]) return { sec, e: GL[sec][key] };
    return null;
  }
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function balloon(ref, small) { return el('span', 'bal' + (/^\d/.test(ref) ? ' hw' : '') + (small ? ' sm' : ''), ref); }
  /* "{G}" / "{A1}" in a text become part balloons, "{3}" / "{12}" hardware balloons */
  function rich(str) {
    const f = document.createDocumentFragment();
    const re = /\{([A-Z]\d?|\d{1,2})\}/g; let last = 0, m;
    str = String(str || '');
    while ((m = re.exec(str))) {
      if (m.index > last) f.append(document.createTextNode(str.slice(last, m.index)));
      f.append(balloon(m[1], true)); last = re.lastIndex;
    }
    if (last < str.length) f.append(document.createTextNode(str.slice(last)));
    return f;
  }
  const svgNS = 'http://www.w3.org/2000/svg';
  function svgIcon(paths, cls) {
    const s = document.createElementNS(svgNS, 'svg'); s.setAttribute('viewBox', '0 0 32 32'); s.setAttribute('aria-hidden', 'true'); if (cls) s.setAttribute('class', cls);
    s.innerHTML = paths; return s;
  }
  /* tool pictograms, 32x32 stroke drawings */
  const TOOL_SVG = {
    drill: '<path d="M6 10h15l3 3v3l-3 3H11"/><path d="M11 19l-2 9h5l2-9"/><path d="M24 14.5h5"/><path d="M8 13h6"/>',
    holesaw: '<ellipse cx="16" cy="9" rx="10" ry="3.2"/><path d="M6 9v13c0 1.8 4.5 3.2 10 3.2s10-1.4 10-3.2V9"/><path d="M6 22l1.6 2 1.8-1.6 2 2 1.8-1.7 2 2 1.8-1.7 2 1.7 1.8-1.7 2 1.6L26 22"/><path d="M16 2v4"/><path d="M16 25v5"/>',
    bit: '<path d="M16 3v6"/><path d="M13.5 9h5v4h-5z"/><path d="M15 13l-1.5 4 3 3-3 3 3 3-1.5 3"/><path d="M17 13l1.5 4-3 3 3 3-3 3"/>',
    hexkey: '<path d="M8 5l-2 2 4.2 4.2v14a2.2 2.2 0 0 0 2.2 2.2h0a2.2 2.2 0 0 0 2.2-2.2V9.8L10 5z"/><path d="M14.6 9.8L26 9.8"/><path d="M26 7.6v4.4"/>',
    screwdriver: '<path d="M13 3h6v10l-1.5 2h-3L13 13z"/><path d="M15 15h2v10h-2z"/><path d="M15 25l1 4 1-4"/><path d="M14.5 6h3M14.5 9h3"/>',
    pencil: '<path d="M22 4l6 6L12 26l-7 2 2-7z"/><path d="M19 7l6 6"/><path d="M7 21l4 4"/>',
    ruler: '<path d="M3 21L21 3l8 8-18 18z"/><path d="M8 16l3 3M11 13l2 2M14 10l3 3M17 7l2 2M20 4l3 3"/>',
    level: '<rect x="3" y="11" width="26" height="10" rx="2"/><rect x="12.5" y="13.5" width="7" height="5" rx="2.5"/><path d="M16 14.6v2.8"/>',
    glasses: '<path d="M3 13h26"/><path d="M5 13c0 4 1.5 6 5 6s5-2 5.5-5"/><path d="M27 13c0 4-1.5 6-5 6s-5-2-5.5-5"/><path d="M3 13l-1-3M29 13l1-3"/>',
    cloth: '<path d="M6 8c4-2 8 2 12 0s6-2 8-1v17c-2-1-4-1-8 1s-8-2-12 0z"/><path d="M10 13h10M10 18h8"/>',
    cutter: '<path d="M14 4l2 10 2-10"/><path d="M16 14l-5 9a3 3 0 1 0 2 1.5l3-6.5 3 6.5a3 3 0 1 0 2-1.5z"/>',
    clip: '<path d="M4 24h24"/><path d="M10 24v-9a6 6 0 0 1 12 0v9"/><circle cx="16" cy="15" r="2.6"/><path d="M7 24v4M25 24v4"/>'
  };
  const ICON_WARN = '<path d="M16 4l13 23H3z"/><path d="M16 13v7"/><path d="M16 23.5v.5"/>';
  const ICON_CHECK = '<path d="M6 17l6 6L26 9"/>';
  const ICON_DOC = '<path d="M8 3h11l6 6v20H8z"/><path d="M19 3v6h6"/><path d="M12 16h9M12 20h9M12 24h6"/>';

  /* ------------------------------------------------------------------ UI */
  const S = { i: 0, t: 0, playing: false, hold: 0, auto: !reduce, ready3d: false, drawerOpen: false, flow: 'kit' };
  const IDX = {}; STEPS.forEach((s, k) => { IDX[s.id] = k; });
  const FLOWS = {}; Object.entries((ST.meta && ST.meta.flows) || { kit: STEPS.map((s) => s.id) }).forEach(([f, ids]) => { FLOWS[f] = ids.filter((id) => IDX[id] != null).map((id) => IDX[id]); });
  if (!FLOWS.kit) FLOWS.kit = STEPS.map((s, k) => k);
  const HASH = { kit: 'step', diy: 'diy' };
  let ORDER = FLOWS.kit, nStep = ORDER.length;
  const gi = (i) => ORDER[i];                       // flow position -> global step index
  function setOrder(f) { S.flow = FLOWS[f] ? f : 'kit'; ORDER = FLOWS[S.flow]; nStep = ORDER.length; document.body.dataset.flow = S.flow; }
  function chapterName(ch) { const c = (ST.chapters || {})[ch]; return c ? tr(c) : ''; }
  /* texts that name other steps carry the kit numbering; ref_template + ref_numbers re-number them for the flow */
  function view(s) {
    if (!s.ref_template || !s.ref_numbers) return s;
    const nums = s.ref_numbers[S.flow] || {};
    const sub = (o) => (typeof o === 'string' ? o.replace(/\[\[step:(\w+)\]\]/g, (m, id) => (nums[id] != null ? String(nums[id]) : '')) : Array.isArray(o) ? o.map(sub) : o && typeof o === 'object' ? Object.fromEntries(Object.entries(o).map(([k, v]) => [k, sub(v)])) : o);
    return Object.assign({}, s, sub(s.ref_template));
  }
  function flowChooser(compact) {
    const g = el('div', 'flows' + (compact ? ' compact' : '')); g.setAttribute('role', 'group'); g.setAttribute('aria-label', ui('flow'));
    ['kit', 'diy'].filter((f) => FLOWS[f]).forEach((f) => {
      const b = el('button', 'flowbtn'); b.type = 'button'; b.setAttribute('aria-pressed', String(S.flow === f));
      b.append(el('b', null, ui('flow_' + f))); if (!compact) b.append(el('span', null, ui('flow_' + f + '_sub')));
      b.addEventListener('click', () => switchFlow(f)); g.append(b);
    });
    return g;
  }
  function switchFlow(f) {
    if (f === S.flow || !FLOWS[f]) return;
    const id = STEPS[gi(S.i)].id; setOrder(f);
    const k = ORDER.indexOf(IDX[id]); goTo(k > 0 ? k : 0);
    if (S.drawerOpen) renderList();
  }

  function renderText(i) {
    const s = view(STEPS[gi(i)]); const art = $('stepArticle'); art.textContent = '';
    const eb = el('p', 'eyebrow'); eb.append(el('span', null, chapterName(s.chapter)), el('span', 'num', ui('step') + ' ' + i + ' / ' + (nStep - 1)));
    art.append(eb, el('h1', null, tr(s.title)));
    if (s.lede) { const p = el('p', 'lede'); p.append(rich(tr(s.lede))); art.append(p); }
    if ((s.uses && s.uses.length) || (s.tools && s.tools.length)) {
      const need = el('div', 'need');
      if (s.uses && s.uses.length) {
        const wrap = el('div', 'uses');
        s.uses.forEach(([key, qty]) => {
          const g = gEntry(key); if (!g) return;
          const c = el('button', 'chip'); c.type = 'button';
          c.append(balloon(g.e.ref || '·'), el('span', null, cap1(tr(g.e))), el('span', 'q', '×' + qty));
          c.addEventListener('click', () => flashItems(g.e.items || [key]));
          wrap.append(c);
        });
        need.append(wrap);
      }
      if (s.tools && s.tools.length) {
        const tw = el('div', 'tools');
        s.tools.forEach((k) => { const g = GL.tools[k]; if (!g) return; const t = el('span', 'tool'); t.append(svgIcon(TOOL_SVG[g.icon || k] || TOOL_SVG.ruler), el('span', null, cap1(tr(g)))); tw.append(t); });
        need.append(tw);
      }
      art.append(need);
    }
    const body = tr(s.body);
    if (Array.isArray(body) && body.length) {
      const ol = el('ol', 'body'); body.forEach((b) => { const li = el('li'); const sp = el('span'); sp.append(rich(b)); li.append(sp); ol.append(li); }); art.append(ol);
    }
    if (s.link === 'template' && D.templateHref) {
      const p = el('p', 'doclink'); const a = el('a'); a.href = D.templateHref; a.target = '_blank'; a.rel = 'noopener';
      if (/^data:/.test(D.templateHref)) a.setAttribute('download', 'drilling-template-v62.pdf');
      a.append(svgIcon(ICON_DOC), el('span', null, ui('template_link'))); p.append(a); art.append(p);
    }
    if (s.warn) { const w = el('p', 'warn'); w.setAttribute('role', 'note'); w.append(svgIcon(ICON_WARN)); const sp = el('span'); sp.append(rich(tr(s.warn))); w.append(sp); art.append(w); }
    if (s.check) { const c = el('p', 'check'); c.append(svgIcon(ICON_CHECK)); const sp = el('span'); sp.append(rich(tr(s.check))); c.append(sp); art.append(c); }
    if (s.note) { const n = el('p', 'note'); n.append(rich(tr(s.note))); art.append(n); }
    (s.blocks || []).forEach((b) => art.append(renderBlock(b)));
    $('foot').textContent = tr(ST.meta.footer).replace('{version}', tr(ST.meta.version_label) || ST.meta.version);
    $('textScroll').scrollTop = 0;
  }

  function renderBlock(b) {
    const wrap = el('section', 'blk');
    if (b.h) wrap.append(el('h2', null, tr(b.h)));
    if (b.type === 'choose') { wrap.classList.add('choose'); wrap.append(el('h2', null, ui('flow')), flowChooser(false)); return wrap; }
    if (b.type === 'kit' || b.type === 'diy_kit' || b.type === 'hardware') {
      const ul = el('ul', 'kit');
      const src = (b.type === 'kit' ? GL.parts : b.type === 'diy_kit' ? GL.diy_parts : GL.hardware) || {};
      Object.keys(src).forEach((k) => {
        const e = src[k]; if (!e.ref) return; if (b.only && !b.only.includes(k)) return;
        const li = el('li'); li.tabIndex = 0;
        const nm = el('span', 'nm'); const bn = el('b', null, cap1(tr(e))); nm.append(bn);
        if (e.desc) nm.append(el('span', null, tr(e.desc)));
        li.append(balloon(e.ref), nm, el('span', 'q', '×' + (e.qty || 1)));
        const go = () => flashItems(e.items || [k]);
        li.addEventListener('click', go); li.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); go(); } });
        ul.append(li);
      });
      wrap.append(ul);
    } else if (b.type === 'tools') {
      const tw = el('div', 'tools');
      (b.tools || Object.keys(GL.tools)).forEach((k) => { const g = GL.tools[k]; const t = el('span', 'tool'); t.append(svgIcon(TOOL_SVG[g.icon || k] || TOOL_SVG.ruler), el('span', null, cap1(tr(g)))); tw.append(t); });
      wrap.append(tw);
    } else if (b.type === 'list') {
      const ul = el('ul'); (tr(b.items) || []).forEach((x) => { const li = el('li'); li.append(rich(x)); ul.append(li); }); wrap.append(ul);
    } else if (b.type === 'qa') {
      const ul = el('ul', 'qa');
      (b.pairs || []).forEach(([q, a]) => { const li = el('li'); const qb = el('b'); qb.append(rich(tr(q))); const as = el('span'); as.append(rich(tr(a))); li.append(qb, as); ul.append(li); });
      wrap.append(ul);
    } else if (b.type === 'dl') {
      const dl = el('dl', 'data');
      (b.pairs || []).forEach(([k, v]) => { dl.append(el('dt', null, tr(k)), el('dd', null, tr(v))); });
      wrap.append(dl);
    } else if (b.type === 'text') {
      const p = el('p'); p.append(rich(tr(b.text))); wrap.append(p);
    } else if (b.type === 'trouble') {
      const list = el('div', 'trouble');
      (b.rows || []).forEach((r) => {
        const it = el('div', 'tr'); const h = el('h3'); h.append(rich(tr(r.problem))); it.append(h);
        const dl = el('dl'); dl.append(el('dt', null, ui('cause'))); const dc = el('dd'); dc.append(rich(tr(r.cause))); dl.append(dc);
        dl.append(el('dt', null, ui('remedy'))); const dr = el('dd'); dr.append(rich(tr(r.remedy))); dl.append(dr);
        it.append(dl); list.append(it);
      });
      wrap.append(list);
    }
    return wrap;
  }

  function renderList() {
    const nav = $('stepList'); nav.textContent = '';
    nav.append(flowChooser(true));
    let cur = null, ol = null;
    ORDER.forEach((g, i) => {
      const s = STEPS[g];
      if (s.chapter !== cur) { cur = s.chapter; nav.append(el('h3', null, chapterName(cur))); ol = el('ol'); nav.append(ol); }
      const li = el('li'); const b = el('button'); b.type = 'button';
      b.append(el('span', 'n', String(i)), el('span', null, tr(s.title)));
      if (i === S.i) b.setAttribute('aria-current', 'step');
      b.addEventListener('click', () => { closeDrawer(); goTo(i); });
      li.append(b); ol.append(li);
    });
  }
  function openDrawer() { S.drawerOpen = true; $('drawer').hidden = false; $('scrim').hidden = false; $('bList').setAttribute('aria-expanded', 'true'); renderList(); const c = $('stepList').querySelector('[aria-current]'); if (c) { c.scrollIntoView({ block: 'center' }); c.focus(); } }
  function closeDrawer() { S.drawerOpen = false; $('drawer').hidden = true; $('scrim').hidden = true; $('bList').setAttribute('aria-expanded', 'false'); }

  function applyLangUI() {
    document.documentElement.lang = LANG;
    document.querySelectorAll('#langSw button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === LANG)));
    $('langSw').setAttribute('aria-label', ui('language'));
    $('brandName').textContent = tr(ST.meta.product);
    $('brandSub').textContent = tr(ST.meta.subtitle);
    $('lPrev').textContent = ui('back'); $('lNext').textContent = ui('next');
    $('drawerTitle').textContent = ui('steps');
    $('bList').setAttribute('aria-label', ui('steps'));
    $('bClose').setAttribute('aria-label', ui('close'));
    $('bReplay').setAttribute('aria-label', ui('replay')); $('bReplay').title = ui('replay');
    $('bAuto').setAttribute('aria-label', ui('autoplay')); $('bAuto').title = ui('autoplay');
    $('bFull').setAttribute('aria-label', ui('fullscreen')); $('bFull').title = ui('fullscreen');
    $('hint').textContent = ui('hint');
    $('stage').setAttribute('aria-label', ui('view3d'));
    if (!S.ready3d && !$('stageMsg').dataset.err) $('stageMsg').textContent = ui('loading');
  }
  function setLang(l) {
    if (!LANGS.includes(l) || l === LANG) return; LANG = l;
    try { const u = new URL(location.href); u.searchParams.set('lang', l); history.replaceState(null, '', u.pathname + u.search + location.hash); } catch (e) { /* sandboxed */ }
    applyLangUI(); renderText(S.i); updateNav(); if (S.drawerOpen) renderList(); if (S.ready3d) buildLabels(gi(S.i));
  }

  function updateNav() {
    $('bPrev').disabled = S.i <= 0; $('bNext').disabled = S.i >= nStep - 1;
    $('navCount').textContent = S.i + ' / ' + (nStep - 1);
    $('progFill').style.width = (nStep > 1 ? (S.i / (nStep - 1)) * 100 : 100) + '%';
  }
  /* deep links: #step-N = kit flow, #diy-N = build-it-yourself flow (N = position inside the flow) */
  function readHash() {
    const m = /^#(step|diy)-(\d+)$/.exec(location.hash || ''); if (!m) return null;
    const f = m[1] === 'diy' ? 'diy' : 'kit'; return FLOWS[f] ? { f, i: +m[2] } : null;
  }
  function goTo(i, fromHash) {
    i = clamp(i | 0, 0, nStep - 1);
    S.i = i;
    const h = HASH[S.flow] + '-' + i;
    if (!fromHash) { try { history.replaceState(null, '', location.pathname + location.search + '#' + h); } catch (e) { try { location.hash = h; } catch (e2) { /* ignore */ } } }
    renderText(i); updateNav(); if (S.drawerOpen) renderList();
    if (S.ready3d) enterStep(gi(i));
  }

  /* ------------------------------------------------------------------ wire UI */
  document.querySelectorAll('#langSw button').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));
  $('bPrev').addEventListener('click', () => goTo(S.i - 1));
  $('bNext').addEventListener('click', () => goTo(S.i + 1));
  $('bList').addEventListener('click', () => (S.drawerOpen ? closeDrawer() : openDrawer()));
  $('bClose').addEventListener('click', closeDrawer);
  $('scrim').addEventListener('click', closeDrawer);
  addEventListener('hashchange', () => { const h = readHash(); if (!h) return; if (h.f !== S.flow) { setOrder(h.f); goTo(h.i, true); } else if (h.i !== S.i) goTo(h.i, true); });
  addEventListener('keydown', (e) => {
    if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
    if (e.key === 'Escape') { if (S.drawerOpen) closeDrawer(); else if ($('stage').classList.contains('fs')) toggleFull(false); }
    else if (e.key === 'ArrowRight' || e.key === 'PageDown') { goTo(S.i + 1); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { goTo(S.i - 1); }
  });
  $('bReplay').addEventListener('click', () => replay());
  $('bAuto').addEventListener('click', () => { S.auto = !S.auto; $('bAuto').setAttribute('aria-pressed', String(S.auto)); if (S.auto && !S.playing) replay(); });
  $('bAuto').setAttribute('aria-pressed', String(S.auto));

  /* fullscreen: Fullscreen API where it exists, a fixed-position CSS fallback elsewhere (iOS) */
  function toggleFull(on) {
    const st = $('stage');
    const isOn = !!(document.fullscreenElement || document.webkitFullscreenElement) || st.classList.contains('fs');
    if (on == null) on = !isOn;
    if (on) {
      const req = st.requestFullscreen || st.webkitRequestFullscreen;
      if (req && document.fullscreenEnabled !== false) {
        try { const p = req.call(st); if (p && p.catch) p.catch(() => cssFull(true)); } catch (e) { cssFull(true); }
      } else cssFull(true);
    } else {
      if (document.fullscreenElement || document.webkitFullscreenElement) { const ex = document.exitFullscreen || document.webkitExitFullscreen; try { ex.call(document); } catch (e) { /* ignore */ } }
      cssFull(false);
    }
  }
  function cssFull(on) { $('stage').classList.toggle('fs', on); document.body.classList.toggle('fs-on', on); $('bFull').setAttribute('aria-pressed', String(on)); }
  ['fullscreenchange', 'webkitfullscreenchange'].forEach((ev) => document.addEventListener(ev, () => {
    const on = !!(document.fullscreenElement || document.webkitFullscreenElement); $('bFull').setAttribute('aria-pressed', String(on || $('stage').classList.contains('fs')));
  }));
  $('bFull').addEventListener('click', () => toggleFull());

  applyLangUI();
  const h0 = readHash();
  let f0 = h0 ? h0.f : null;
  if (!f0) { try { const q = new URLSearchParams(location.search).get('flow'); if (q && FLOWS[q]) f0 = q; } catch (e) { /* ignore */ } }
  setOrder(f0 || 'kit');
  S.i = h0 ? clamp(h0.i, 0, nStep - 1) : 0;
  renderText(S.i); updateNav();
  if (STILL) document.body.classList.add('still');

  /* ================================================================== 3D */
  let flashItems = () => {}, enterStep = () => {}, replay = () => {}, buildLabels = () => {};
  if (typeof THREE === 'undefined') { $('stageMsg').textContent = ui('no3d'); $('stageMsg').dataset.err = '1'; return; }
  try { init3D(); } catch (e) { console.error(e); $('stageMsg').textContent = ui('no3d') + ' (' + ((e && e.message) || e) + ')'; $('stageMsg').dataset.err = '1'; }

  function init3D() {
    const V3 = THREE.Vector3;
    const stage = $('stage'), canvas = $('c'), labelsEl = $('labels');
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: STILL, powerPreference: 'high-performance' });
    renderer.setClearColor(0x000000, 0);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = STILL ? THREE.NoToneMapping : THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = !STILL;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(30, 1, 1, 20000); camera.up.set(0, 0, 1);
    const lin = (h) => new THREE.Color(h).convertSRGBToLinear();
    const SC = ST.scene || {};

    /* ---------- environment (studio gradient, from the viewer) ---------- */
    const pmrem = new THREE.PMREMGenerator(renderer);
    function envGradient(stops, extra) {
      const s = new THREE.Scene(), g = new THREE.SphereGeometry(50, 48, 24); g.rotateX(Math.PI / 2);
      const pos = g.attributes.position, col = new Float32Array(pos.count * 3), cs = stops.map((t) => [t[0], lin(t[1]).multiplyScalar(t[2])]);
      for (let i = 0; i < pos.count; i++) {
        const e = Math.asin(clamp(pos.getZ(i) / 50, -1, 1)) / DEG; let k = 0; while (k < cs.length - 2 && e > cs[k + 1][0]) k++;
        const tt = clamp((e - cs[k][0]) / (cs[k + 1][0] - cs[k][0]), 0, 1), c = cs[k][1].clone().lerp(cs[k + 1][1], tt);
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      g.setAttribute('color', new THREE.BufferAttribute(col, 3));
      s.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide })));
      if (extra) extra(s);
      return pmrem.fromScene(s, 0.02).texture;
    }
    function softbox(s, w, h, pos, color, k) { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: lin(color).multiplyScalar(k), side: THREE.DoubleSide })); m.position.copy(pos); m.lookAt(0, 0, 0); s.add(m); }
    if (!STILL) scene.environment = envGradient([[-90, '#26292f', .5], [-8, '#5d626c', .8], [0, '#9aa1ac', 1], [30, '#dfe3e9', 1.05], [90, '#ffffff', 1.25]], (s) => {
      softbox(s, 36, 22, new V3(18, -32, 30), '#ffffff', 2.2); softbox(s, 10, 40, new V3(-38, 22, 8), '#e8f4ff', 1.2);
    });
    const hemi = new THREE.HemisphereLight(lin('#ffffff'), lin(STILL ? '#c4c9cf' : '#8a8f96'), STILL ? 0.9 : 0.35); hemi.position.set(0, 0, 1); scene.add(hemi);
    const key = new THREE.DirectionalLight(lin('#ffffff'), STILL ? 0.8 : 1.35); scene.add(key, key.target);
    key.castShadow = !STILL; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.6;
    const fill = new THREE.DirectionalLight(lin('#dfefff'), STILL ? 0.25 : 0.45); scene.add(fill, fill.target);
    const amb = new THREE.AmbientLight(0xffffff, STILL ? 0.22 : 0.0); scene.add(amb);

    /* ---------- STL parsing with creased normals (from the viewer) ---------- */
    function b64ToBytes(s) { const bin = atob(s); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u; }
    function creaseNormals(pos, deg) {
      const nF = pos.length / 9, nV = nF * 3, cosT = Math.cos(deg * DEG), fa = new Float32Array(nF * 3), fu = new Float32Array(nF * 3);
      for (let f = 0; f < nF; f++) {
        const o = f * 9, ax = pos[o + 3] - pos[o], ay = pos[o + 4] - pos[o + 1], az = pos[o + 5] - pos[o + 2], bx = pos[o + 6] - pos[o], by = pos[o + 7] - pos[o + 1], bz = pos[o + 8] - pos[o + 2];
        const x = ay * bz - az * by, y = az * bx - ax * bz, z = ax * by - ay * bx, l = Math.hypot(x, y, z) || 1; fa[f * 3] = x; fa[f * 3 + 1] = y; fa[f * 3 + 2] = z; fu[f * 3] = x / l; fu[f * 3 + 1] = y / l; fu[f * 3 + 2] = z / l;
      }
      const vid = new Int32Array(nV), map = new Map(); let cnt = 0;
      for (let v = 0; v < nV; v++) { const k = Math.round(pos[v * 3] * 500) + ',' + Math.round(pos[v * 3 + 1] * 500) + ',' + Math.round(pos[v * 3 + 2] * 500); let id = map.get(k); if (id === undefined) { id = cnt++; map.set(k, id); } vid[v] = id; }
      const start = new Int32Array(cnt + 1); for (let v = 0; v < nV; v++) start[vid[v] + 1]++; for (let i = 0; i < cnt; i++) start[i + 1] += start[i];
      const cur = start.slice(0, cnt), adj = new Int32Array(nV); for (let v = 0; v < nV; v++) adj[cur[vid[v]]++] = (v / 3) | 0;
      const out = new Float32Array(nV * 3);
      for (let v = 0; v < nV; v++) {
        const f = (v / 3) | 0, id = vid[v], ux = fu[f * 3], uy = fu[f * 3 + 1], uz = fu[f * 3 + 2]; let sx = 0, sy = 0, sz = 0;
        for (let k = start[id]; k < start[id + 1]; k++) { const g = adj[k]; if (ux * fu[g * 3] + uy * fu[g * 3 + 1] + uz * fu[g * 3 + 2] >= cosT) { sx += fa[g * 3]; sy += fa[g * 3 + 1]; sz += fa[g * 3 + 2]; } }
        const l = Math.hypot(sx, sy, sz); if (l > 0) { out[v * 3] = sx / l; out[v * 3 + 1] = sy / l; out[v * 3 + 2] = sz / l; } else { out[v * 3] = ux; out[v * 3 + 1] = uy; out[v * 3 + 2] = uz; }
      }
      return out;
    }
    function parseSTL(bytes) {
      const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength), n = dv.getUint32(80, true), pos = new Float32Array(n * 9);
      for (let i = 0; i < n; i++) { const o = 84 + i * 50 + 12; for (let k = 0; k < 9; k++) pos[i * 9 + k] = dv.getFloat32(o + k * 4, true); }
      let vol = 0; for (let i = 0; i < pos.length; i += 9) vol += pos[i] * (pos[i + 4] * pos[i + 8] - pos[i + 5] * pos[i + 7]) - pos[i + 1] * (pos[i + 3] * pos[i + 8] - pos[i + 5] * pos[i + 6]) + pos[i + 2] * (pos[i + 3] * pos[i + 7] - pos[i + 4] * pos[i + 6]);
      if (vol < 0) for (let i = 0; i < pos.length; i += 9) for (let k = 0; k < 3; k++) { const t = pos[i + 3 + k]; pos[i + 3 + k] = pos[i + 6 + k]; pos[i + 6 + k] = t; }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      g.setAttribute('normal', new THREE.BufferAttribute(creaseNormals(pos, 34), 3));
      g.computeBoundingBox(); g.computeBoundingSphere(); return g;
    }
    const geoCache = {};
    async function getGeo(gid) {
      if (geoCache[gid]) return geoCache[gid];
      let bytes;
      if (D.geomsB64 && D.geomsB64[gid]) bytes = b64ToBytes(D.geomsB64[gid]);
      else { const r = await fetch((D.modelBase || 'models/') + gid + '.stl'); if (!r.ok) throw new Error('model ' + gid + ' ' + r.status); bytes = new Uint8Array(await r.arrayBuffer()); }
      return (geoCache[gid] = parseSTL(bytes));
    }

    /* ---------- items: one transform group per kit item ---------- */
    const root = new THREE.Group(); scene.add(root);
    const IT = {};             // iid -> {def, g, meshes:[{mesh, part, o, j}], box:Box3 (local), proc}
    const PART = {};
    (D.parts || []).forEach((p) => { PART[p.id] = p; });
    Object.entries(ITEMS).forEach(([iid, def]) => {
      const g = new THREE.Group(); g.matrixAutoUpdate = false; g.visible = false; root.add(g);
      IT[iid] = { iid, def, g, meshes: [], box: new THREE.Box3() };
    });
    function matFor(p) {
      const metal = /acciaio|ottone|steel|brass/.test(p.material || '') && !/PA/.test(p.material || '');
      return new THREE.MeshStandardMaterial({ color: lin(p.color), roughness: metal ? 0.38 : 0.52, metalness: metal ? 0.65 : 0.02, envMapIntensity: 0.9 });
    }

    /* ---------- fat lines (screen-space quads) for outlines, marks and dimensions ---------- */
    const RES = new THREE.Vector2(1, 1);
    function fatLineMaterial(color, widthPx, opts) {
      const u = { color: { value: lin(color) }, width: { value: widthPx }, resolution: { value: RES }, opacity: { value: 1 }, zbias: { value: (opts && opts.zbias) || 0 } };
      return new THREE.ShaderMaterial({
        uniforms: u, side: THREE.DoubleSide, transparent: !!(opts && opts.transparent), depthTest: !(opts && opts.noDepth), depthWrite: false,
        vertexShader: 'attribute vec3 other; attribute float side; uniform vec2 resolution; uniform float width; uniform float zbias;\n' +
          'void main(){ vec4 p = projectionMatrix*modelViewMatrix*vec4(position,1.0); vec4 q = projectionMatrix*modelViewMatrix*vec4(other,1.0);\n' +
          ' vec2 ps = p.xy/max(p.w,1e-4), qs = q.xy/max(q.w,1e-4); vec2 d = (qs-ps)*resolution; float L = length(d); vec2 dir = L>1e-5 ? d/L : vec2(1.0,0.0);\n' +
          ' vec2 n = vec2(-dir.y, dir.x); p.xy += n*side*width/resolution*p.w; p.z -= zbias*p.w; gl_Position = p; }',
        fragmentShader: 'uniform vec3 color; uniform float opacity; void main(){ gl_FragColor = vec4(color, opacity); }'
      });
    }
    function fatLineGeometry(segs) {
      const n = segs.length / 6, pos = new Float32Array(n * 12), oth = new Float32Array(n * 12), side = new Float32Array(n * 4), idx = new Uint32Array(n * 6);
      for (let i = 0; i < n; i++) {
        const a = [segs[i * 6], segs[i * 6 + 1], segs[i * 6 + 2]], b = [segs[i * 6 + 3], segs[i * 6 + 4], segs[i * 6 + 5]];
        const P = [a, a, b, b], O = [b, b, a, a], Sd = [-1, 1, 1, -1];
        for (let k = 0; k < 4; k++) { for (let c = 0; c < 3; c++) { pos[(i * 4 + k) * 3 + c] = P[k][c]; oth[(i * 4 + k) * 3 + c] = O[k][c]; } side[i * 4 + k] = Sd[k]; }
        const v = i * 4; idx.set([v, v + 2, v + 1, v + 1, v + 2, v + 3], i * 6);
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('other', new THREE.BufferAttribute(oth, 3)); g.setAttribute('side', new THREE.BufferAttribute(side, 1));
      g.setIndex(new THREE.BufferAttribute(idx, 1)); return g;
    }
    function fatLines(points, color, width, opts) { const m = new THREE.Mesh(fatLineGeometry(new Float32Array(points)), fatLineMaterial(color, width, opts)); m.frustumCulled = false; return m; }
    /* silhouette: back faces pushed out along smooth normals by a fixed number of pixels */
    const hullMat = new THREE.ShaderMaterial({
      uniforms: { width: { value: 2.4 }, resolution: { value: RES } }, side: THREE.BackSide,
      vertexShader: 'uniform vec2 resolution; uniform float width; void main(){ vec4 p = projectionMatrix*modelViewMatrix*vec4(position,1.0);\n' +
        ' vec3 nv = normalize(normalMatrix*normal); vec2 ns = (projectionMatrix*vec4(nv,0.0)).xy; float l = length(ns); ns = l>1e-6 ? ns/l : vec2(0.0);\n' +
        ' p.xy += ns*width*2.0/resolution*p.w; gl_Position = p; }',
      fragmentShader: 'void main(){ gl_FragColor = vec4(0.067,0.067,0.067,1.0); }'
    });
    function toIndexed(g0) {
      const p = g0.attributes.position, map = new Map(), pos = [], idx = [];
      for (let i = 0; i < p.count; i++) { const k = Math.round(p.getX(i) * 1e3) + ',' + Math.round(p.getY(i) * 1e3) + ',' + Math.round(p.getZ(i) * 1e3); let id = map.get(k); if (id === undefined) { id = pos.length / 3; map.set(k, id); pos.push(p.getX(i), p.getY(i), p.getZ(i)); } idx.push(id); }
      const o = new THREE.BufferGeometry(); o.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); o.setIndex(idx); o.computeVertexNormals(); return o;
    }
    const outlineCache = new Map();
    const edgeMat = fatLineMaterial('#111111', 1.5, { zbias: STILL ? 0.00012 : 0.00025 });
    function addOutlines(mesh) {
      if (mesh.userData.outl) return;
      const geo = mesh.geometry; let rec = outlineCache.get(geo);
      if (!rec) {
        const src = geo.index ? geo.toNonIndexed() : geo;
        const eg = new THREE.EdgesGeometry(src, 32); const ep = eg.attributes.position.array;
        rec = { edges: fatLineGeometry(new Float32Array(ep)), hull: toIndexed(src) }; outlineCache.set(geo, rec);
      }
      const e = new THREE.Mesh(rec.edges, edgeMat); e.frustumCulled = false; e.renderOrder = 2;
      if (mesh.userData.outline === 'edges') { mesh.add(e); mesh.userData.outl = [e]; return; }
      const h = new THREE.Mesh(rec.hull, hullMat); h.renderOrder = 1;
      mesh.add(e, h); mesh.userData.outl = [e, h];
    }

    /* ---------- procedural objects: shelf, container, pet bowl, power supply, cables, tools ---------- */
    const SH = SC.shelf || { underside_z: 70.1, thickness: 30, hole_xy: [27, 0], hole_d: 76, size: [640, 460], centre: [0, 0] };
    const SH_TOP = SH.underside_z + SH.thickness;
    const FLOOR_Z = SC.floor_z != null ? SC.floor_z : -280;
    function pm(color, o) { const m = new THREE.MeshStandardMaterial(Object.assign({ color: lin(color), roughness: 0.7, metalness: 0 }, o || {})); m.userData.base = color; return m; }
    function mkMesh(geo, mat, shadow) { const m = new THREE.Mesh(geo, mat); m.castShadow = !!shadow; m.receiveShadow = true; return m; }
    function woodTexture() {
      const c = document.createElement('canvas'); c.width = 512; c.height = 128; const x = c.getContext('2d');
      x.fillStyle = '#d8bf96'; x.fillRect(0, 0, 512, 128);
      for (let i = 0; i < 70; i++) { const y = (Math.sin(i * 12.9898) * 43758.5453 % 1 + 1) % 1 * 128; x.strokeStyle = 'rgba(120,80,40,' + (0.05 + ((i * 37) % 10) / 100) + ')'; x.lineWidth = 0.6 + ((i * 13) % 16) / 10; x.beginPath(); x.moveTo(0, y); for (let k = 0; k <= 8; k++) x.lineTo(k * 64, y + Math.sin(k + i) * 2.5); x.stroke(); }
      const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.encoding = THREE.sRGBEncoding; return t;
    }
    const woodTex = STILL ? null : woodTexture();
    function shelfObj(withHoles) {
      const [w, d] = SH.size, [cx, cy] = SH.centre;
      const s = new THREE.Shape(); s.moveTo(cx - w / 2, cy - d / 2); s.lineTo(cx + w / 2, cy - d / 2); s.lineTo(cx + w / 2, cy + d / 2); s.lineTo(cx - w / 2, cy + d / 2); s.lineTo(cx - w / 2, cy - d / 2);
      if (withHoles) {
        const h = new THREE.Path(); h.absarc(SH.hole_xy[0], SH.hole_xy[1], SH.hole_d / 2, 0, Math.PI * 2, true); s.holes.push(h);
        if (SH.cable_xy) { const c = new THREE.Path(); c.absarc(SH.cable_xy[0], SH.cable_xy[1], (SH.cable_d || 10) / 2, 0, Math.PI * 2, true); s.holes.push(c); }
      }
      const g = new THREE.ExtrudeGeometry(s, { depth: SH.thickness, bevelEnabled: false, curveSegments: 72 });
      g.translate(0, 0, SH.underside_z);
      const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / 600, uv.getY(i) / 150);
      const m = pm(STILL ? '#efe4cf' : '#ffffff', { map: woodTex, roughness: 0.8 }); m.userData.base = STILL ? '#efe4cf' : '#d8bf96';
      const mesh = mkMesh(g, m, false); mesh.userData.outline = true; return mesh;
    }
    function containerObj() { // generic hopper on 3 legs over the hole (the user's container)
      const g = new THREE.Group(); const R = 150, H = 330, NECK = 31, top = SH_TOP;
      const pts = [[NECK, -10], [NECK, 22], [R, 120], [R, 120 + H], [R - 8, 128 + H], [0, 128 + H]].map((p) => new THREE.Vector2(p[0], p[1]));
      const lg = new THREE.LatheGeometry(pts, 64); lg.rotateX(Math.PI / 2);
      const m = pm('#5d86b5', { transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide, roughness: 0.4 });
      const body = new THREE.Mesh(lg, m); body.position.set(SH.hole_xy[0], SH.hole_xy[1], top); body.renderOrder = 5; g.add(body);
      const legM = pm('#5d86b5', { transparent: true, opacity: 0.35, depthWrite: false });
      for (let k = 0; k < 3; k++) {
        const a = (k * 120 + 30) * DEG; const leg = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 120, 12).rotateX(Math.PI / 2), legM);
        leg.position.set(SH.hole_xy[0] + Math.cos(a) * (R - 12), SH.hole_xy[1] + Math.sin(a) * (R - 12), top + 60); g.add(leg);
      }
      g.userData.ghost = true; return g;
    }
    function petBowlObj() {
      const pts = [[0, 0], [62, 0], [66, 2], [92, 58], [95, 60], [90, 61], [64, 6], [0, 6]].map((p) => new THREE.Vector2(p[0], p[1]));
      const g = new THREE.LatheGeometry(pts, 72); g.rotateX(Math.PI / 2);
      const m = mkMesh(g, pm('#c8cdd3', { metalness: 0.55, roughness: 0.32 }), true);
      const o = SC.outlet_xyz || [-42, 0, -104]; m.position.set(o[0], o[1], FLOOR_Z); m.userData.outline = 'edges'; return m;
    }
    function floorObj() {
      const g = new THREE.Group();
      const m = new THREE.Mesh(new THREE.CircleGeometry(900, 64), new THREE.ShadowMaterial({ opacity: 0.18 })); m.position.set(0, 0, FLOOR_Z - 0.2); m.receiveShadow = true; g.add(m);
      const ring = new THREE.Mesh(new THREE.RingGeometry(140, 700, 64), pm('#cfd6cf', { transparent: true, opacity: 0.35, depthWrite: false })); ring.position.set(-40, 0, FLOOR_Z - 0.4); g.add(ring);
      return g;
    }
    function tubeGeo(points, r, seg) {
      const curve = new THREE.CatmullRomCurve3(points.map((p) => new V3(p[0], p[1], p[2])), false, 'centripetal');
      return new THREE.TubeGeometry(curve, seg || Math.max(24, points.length * 14), r, 10, false);
    }
    function tube(points, r, color, seg) { const m = mkMesh(tubeGeo(points, r, seg), pm(color, { roughness: 0.55 }), true); m.userData.outline = true; return m; }
    function psuObj() {
      const g = new THREE.Group(); const P = SC.psu_xyz || [205, -150, SH_TOP];
      const body = mkMesh(new THREE.BoxGeometry(110, 58, 34), pm('#2b2e33', { roughness: 0.6 }), true); body.position.set(P[0], P[1], P[2] + 17); body.userData.outline = true; g.add(body);
      const lab = mkMesh(new THREE.BoxGeometry(50, 30, 0.6), pm('#e9ecef'), false); lab.position.set(P[0] - 12, P[1], P[2] + 34.3); g.add(lab);
      // DC lead from the brick to the screw-terminal adapter
      g.add(tube([[P[0] - 55, P[1], P[2] + 12], [P[0] - 62, P[1] + 4, P[2] + 9], [P[0] - 66, P[1] + 6, P[2] + 9]], 2.4, '#1d1f22', 16));
      const ad = mkMesh(new THREE.BoxGeometry(22, 16, 13), pm('#26282b', { roughness: 0.5 }), true); ad.position.set(P[0] - 72, P[1] + 6, P[2] + 7.5); ad.userData.outline = true; g.add(ad);
      const term = mkMesh(new THREE.BoxGeometry(8, 14, 6), pm('#2f9550'), false); term.position.set(P[0] - 85, P[1] + 6, P[2] + 6); term.userData.outline = true; g.add(term);
      // mains cable: over the back edge of the shelf (-Y), down in a drip loop, up into a socket below the edge
      const yE = (SH.centre[1] - SH.size[1] / 2), sy = -1;
      const sx = P[0] + 50, T0 = P[2] - SH.thickness;
      g.add(tube([[P[0] + 55, P[1], P[2] + 12], [P[0] + 68, P[1] + sy * 40, P[2] + 6], [sx + 22, yE - sy * 2, P[2] + 3.5], [sx + 26, yE + sy * 9, P[2] - 22],
        [sx + 18, yE + sy * 12, T0 - 92], [sx, yE + sy * 11, T0 - 100], [sx - 6, yE + sy * 9, T0 - 78], [sx - 6, yE + sy * 7, T0 - 54]], 2.6, '#1d1f22', 80));
      const sock = mkMesh(new THREE.BoxGeometry(52, 14, 52), pm('#e3e6e9', { roughness: 0.6 }), true); sock.position.set(sx - 6, yE + sy * 7, T0 - 22); sock.userData.outline = true; g.add(sock);
      const plug = mkMesh(new THREE.CylinderGeometry(9, 9, 18, 20).rotateX(Math.PI / 2), pm('#2b2e33'), true); plug.position.set(sx - 6, yE + sy * 7, T0 - 54); plug.userData.outline = true; g.add(plug);
      return g;
    }
    function holeSawObj() {
      const g = new THREE.Group(); const r = SH.hole_d / 2;
      const cup = mkMesh(new THREE.CylinderGeometry(r, r, 42, 64, 1, true).rotateX(Math.PI / 2), pm('#4f6b8a', { metalness: 0.5, roughness: 0.4, side: THREE.DoubleSide }), true); cup.position.z = 21; g.add(cup);
      const lid = mkMesh(new THREE.CylinderGeometry(r, r, 3, 64).rotateX(Math.PI / 2), pm('#4f6b8a', { metalness: 0.5, roughness: 0.4 }), true); lid.position.z = 43; g.add(lid);
      const arbor = mkMesh(new THREE.CylinderGeometry(6, 6, 50, 6).rotateX(Math.PI / 2), pm('#9ea5ad', { metalness: 0.7, roughness: 0.3 }), true); arbor.position.z = 69; g.add(arbor);
      const pilot = mkMesh(new THREE.CylinderGeometry(3, 3, 56, 16).rotateX(Math.PI / 2), pm('#9ea5ad', { metalness: 0.7, roughness: 0.3 }), true); pilot.position.z = 14; g.add(pilot);
      g.children.forEach((c) => { c.userData.outline = true; });
      g.position.set(SH.hole_xy[0], SH.hole_xy[1], SH_TOP); return g;
    }
    function bitObj() {
      const g = new THREE.Group(); const r = (SH.cable_d || 10) / 2;
      const b = mkMesh(new THREE.CylinderGeometry(r, r, 90, 20).rotateX(Math.PI / 2), pm('#9ea5ad', { metalness: 0.7, roughness: 0.3 }), true); b.position.z = 45; b.userData.outline = true; g.add(b);
      const ch = mkMesh(new THREE.CylinderGeometry(12, 12, 30, 6).rotateX(Math.PI / 2), pm('#4f6b8a', { metalness: 0.5, roughness: 0.4 }), true); ch.position.z = 105; ch.userData.outline = true; g.add(ch);
      const c = SH.cable_xy || [71, -26]; g.position.set(c[0], c[1], SH_TOP); return g;
    }
    function psuKitObj() { // power supply as delivered: brick, adapter, coiled cable with the round connector
      const g = new THREE.Group();
      const body = mkMesh(new THREE.BoxGeometry(110, 58, 34), pm('#2b2e33', { roughness: 0.6 }), true); body.position.set(0, 0, 17); body.userData.outline = true; g.add(body);
      const lab = mkMesh(new THREE.BoxGeometry(50, 30, 0.6), pm('#e9ecef'), false); lab.position.set(-12, 0, 34.3); g.add(lab);
      const ad = mkMesh(new THREE.BoxGeometry(22, 16, 13), pm('#26282b', { roughness: 0.5 }), true); ad.position.set(-72, 6, 7.5); ad.userData.outline = true; g.add(ad);
      g.add(tube([[-55, 0, 12], [-62, 4, 9], [-66, 6, 9]], 2.4, '#1d1f22', 12));
      const coil = []; for (let k = 0; k <= 96; k++) { const a = k / 96 * Math.PI * 6; coil.push([95 + 34 * Math.cos(a), 34 * Math.sin(a), 3 + k * 0.07]); }
      g.add(tube([[-85, 6, 6], [-100, 30, 4], [-60, 62, 3], [40, 50, 3], [61, 0, 3]].concat(coil), 2.6, '#1d1f22', 240));
      const c0 = new V3(129, 0, 9.7), c1 = new V3(129, -40, 9.7);
      const mid = c0.clone().lerp(c1, 0.35); g.add(cylBetween(c0, mid, 8.2, ringMat)); g.add(cylBetween(mid, c1, 7.0, connMatB));
      return g;
    }
    /* the 1:1 drilling template (SVG from the design) on paper under the shelf: the drawing is the view from below,
       so the plane faces -Z and is read unmirrored from below; SVG mm -> world: X = -(x - cx), Y = -(y - cy) */
    let templateReady = null;
    function templateObj() {
      const g = new THREE.Group(); const svg = SC.template_svg; if (!svg) return g;
      const W0 = 210, H0 = 297, K = 5; const cvs = document.createElement('canvas'); cvs.width = W0 * K; cvs.height = H0 * K;
      const ctx = cvs.getContext('2d'); ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, cvs.width, cvs.height);
      const tex = new THREE.CanvasTexture(cvs); tex.encoding = THREE.sRGBEncoding; tex.anisotropy = 8;
      const img = new Image();
      templateReady = new Promise((res) => { img.onload = () => { ctx.drawImage(img, 0, 0, cvs.width, cvs.height); tex.needsUpdate = true; res(); }; img.onerror = () => res(); });
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
      const mat = new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide }); mat.toneMapped = false;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(W0, H0), mat); m.rotation.y = Math.PI;
      const c = SC.template_centre_svg || [105, 150]; m.position.set(-(W0 / 2 - c[0]), -(H0 / 2 - c[1]), SC.template_z != null ? SC.template_z : SH.underside_z - 0.4);
      m.userData.outline = 'edges'; m.renderOrder = 2; g.add(m); return g;
    }
    function smallScrewsObj() { // the 4 countersunk 3.5 x 16 screws of the channel, laid side by side
      const g = new THREE.Group(); const mat = pm('#a8adb3', { metalness: 0.6, roughness: 0.38 });
      for (let k = 0; k < 4; k++) {
        const sh = mkMesh(new THREE.CylinderGeometry(1.75, 1.75, 13, 16).rotateZ(Math.PI / 2), mat, true); sh.position.set(k * 0, k * 14, 3.5); sh.position.x = 6.5;
        const hd = mkMesh(new THREE.CylinderGeometry(3.5, 1.75, 3, 20).rotateZ(Math.PI / 2), mat, true); hd.position.set(-1.5, k * 14, 3.5);
        sh.userData.outline = true; hd.userData.outline = true; g.add(sh, hd);
      }
      return g;
    }
    function clipsObj() { // the user's own cable clips along the shelf underside (positions from steps.json scene.clips_y)
      const g = new THREE.Group(); const mat = pm('#eef0f2', { roughness: 0.6 });
      (SC.clips_y || []).forEach((y) => {
        const c = mkMesh(new THREE.BoxGeometry(12, 7, 6.5), mat, true); c.position.set(SC.cable_x || 0, y, SH.underside_z - 3.25); c.userData.outline = true; g.add(c);
        const n = mkMesh(new THREE.CylinderGeometry(1.4, 1.4, 4, 10).rotateX(Math.PI / 2), pm('#9aa1a8', { metalness: 0.6, roughness: 0.4 }), false);
        n.position.set((SC.cable_x || 0) + 4, y, SH.underside_z - 6.6); g.add(n);
      });
      return g;
    }
    const PROC = { clips: clipsObj, psu_kit: psuKitObj, shelf: () => shelfObj(true), shelf_plain: () => shelfObj(false), container: containerObj, petbowl: petBowlObj, floor: floorObj,
      psu: psuObj, holesaw: holeSawObj, bit: bitObj, template: templateObj, small_screws: smallScrewsObj };

    /* ---------- dynamic cables: points in the frame of a unit item ('u') or in the world ('w') ---------- */
    const CAB = SC.cables || {};
    const cableMat = pm('#1d1f22', { roughness: 0.55 });
    const connMatA = pm('#2b2d31', { roughness: 0.5 }), connMatB = pm('#3b3f45', { roughness: 0.5 }), ringMat = pm('#5a6068', { roughness: 0.45, metalness: 0.2 });
    const wireR = pm('#c8322b'), wireK = pm('#151515');
    function cableObj(name) {
      const g = new THREE.Group(); g.userData.cable = name; return g;
    }
    function cableWorldPts(spec, list, off) {
      const ref = spec.ref && IT[spec.ref] ? IT[spec.ref].g.matrix : null; const out = [];
      (list || []).forEach((p) => {
        const fr = p.length > 3 ? p[3] : spec.frame || 'u'; const v = new V3(p[0], p[1], p[2]);
        if (fr === 'u' && ref) v.applyMatrix4(ref); else if (off) v.add(off);
        out.push(v);
      });
      return out;
    }
    function cylBetween(a, b, r, mat) {
      const d = b.clone().sub(a); const L = d.length(); const m = mkMesh(new THREE.CylinderGeometry(r, r, Math.max(L, 0.1), 24), mat, true);
      m.position.copy(a).add(b).multiplyScalar(0.5); m.quaternion.setFromUnitVectors(new V3(0, 1, 0), d.normalize()); m.userData.outline = true; return m;
    }
    function updateCable(I) {
      const spec = CAB[I.def.cable]; if (!spec) return;
      const ref = spec.ref && IT[spec.ref] ? IT[spec.ref].g.matrix.elements : [];
      const o = I.st && I.st.off ? I.st.off : [0, 0, 0]; const off = new V3(o[0], o[1], o[2]);
      const sig = Array.prototype.map.call(ref, (x) => x.toFixed(2)).join(',') + '|' + o.map((x) => x.toFixed(2)).join(',');
      if (I.cabSig === sig && I.g.children.length) return;
      I.cabSig = sig;
      while (I.g.children.length) { const c = I.g.children.pop(); c.traverse((m) => { if (m.geometry) m.geometry.dispose(); }); }
      const r = spec.r || 3;
      const conn = spec.conn ? cableWorldPts(spec, spec.conn, off) : null;
      const p1 = cableWorldPts(spec, spec.pts, off);
      if (conn && spec.half !== 'B') p1.push(conn[0]);
      if (conn && spec.half === 'B') p1.push(conn[0]);
      if (p1.length > 1) { const m = mkMesh(tubeGeo(p1.map((v) => v.toArray()), r), cableMat, true); m.userData.outline = true; I.g.add(m); }
      if (spec.pts2) { const p2 = [conn[1]].concat(cableWorldPts(spec, spec.pts2, off)); const m = mkMesh(tubeGeo(p2.map((v) => v.toArray()), r), cableMat, true); m.userData.outline = true; I.g.add(m); }
      if (conn) {
        const a = conn[0], b = conn[1];
        if (spec.half === 'A') I.g.add(cylBetween(a, b, 6.5, connMatA));
        else if (spec.half === 'B') { const mid = a.clone().lerp(b, 0.35); I.g.add(cylBetween(a, mid, 8.2, ringMat)); I.g.add(cylBetween(mid, b, 7.0, connMatB)); }
        else { const m1 = a.clone().lerp(b, 0.48), m2 = a.clone().lerp(b, 0.66); I.g.add(cylBetween(a, m1, 6.5, connMatA)); I.g.add(cylBetween(m1, m2, 8.2, ringMat)); I.g.add(cylBetween(m2, b, 7.0, connMatB)); }
      }
      if (spec.ends === 'wires') {
        const e = cableWorldPts(spec, [spec.pts[0]], off)[0]; const e2 = cableWorldPts(spec, [spec.pts[1]], off)[0]; const dir = e.clone().sub(e2).normalize();
        const side = new V3(-dir.y, dir.x, 0).multiplyScalar(1.6);
        I.g.add(cylBetween(e.clone().add(side), e.clone().add(side).addScaledVector(dir, 14), 1.1, wireR));
        I.g.add(cylBetween(e.clone().sub(side), e.clone().sub(side).addScaledVector(dir, 14), 1.1, wireK));
      }
      I.g.children.forEach((m) => { m.castShadow = true; });
      I.meshes = I.g.children.map((m) => ({ mesh: m, part: null, o: new V3(), proc: true }));
      I.box.makeEmpty(); I.g.children.forEach((m) => { m.geometry.computeBoundingBox(); I.box.union(m.geometry.boundingBox.clone().applyMatrix4(m.matrix)); });
      if (STILL) I.g.children.forEach((m) => { m.updateMatrix(); m.material.polygonOffset = true; m.material.polygonOffsetFactor = 1; m.material.polygonOffsetUnits = 1; addOutlines(m); });
      if (I.lookRole) setLook(I, I.lookRole);
    }

    Object.values(IT).forEach((I) => {
      const pr = I.def.proc; if (!pr) return;
      if (pr === 'cable') { I.proc = cableObj(I.def.cable); I.isCable = true; return; }
      if (!PROC[pr]) return;
      const o = PROC[pr](); I.g.add(o); I.proc = o;
      I.box.setFromObject(o);
      o.traverse((m) => { if (m.isMesh) I.meshes.push({ mesh: m, part: null, o: m.position.clone(), proc: true }); });
    });

    /* ---------- marks, dimensions, arrows (rebuilt per step) ---------- */
    const overlay = new THREE.Group(); scene.add(overlay);
    function clearOverlay() { while (overlay.children.length) { const c = overlay.children.pop(); c.traverse((m) => { if (m.geometry && !m.userData.keepGeo) m.geometry.dispose(); }); } }
    const markMat = (thin) => fatLineMaterial('#3c4248', STILL ? (thin ? 1.6 : 2.6) : (thin ? 1.3 : 2.2), { zbias: 0.0006 });
    function circlePts(cx, cy, z, r, n, dashed) {
      const out = []; for (let i = 0; i < n; i++) { if (dashed && i % 2) continue; const a0 = (i / n) * Math.PI * 2, a1 = ((i + 1) / n) * Math.PI * 2; out.push(cx + r * Math.cos(a0), cy + r * Math.sin(a0), z, cx + r * Math.cos(a1), cy + r * Math.sin(a1), z); }
      return out;
    }
    function buildMarks(list) {
      (list || []).forEach((mk) => {
        const z = mk.z != null ? mk.z : SH_TOP + 0.3; let pts = [];
        if (mk.type === 'cross') { const [x, y] = mk.at, s = mk.size || 9; pts = [x - s, y, z, x + s, y, z, x, y - s, z, x, y + s, z]; }
        else if (mk.type === 'line') pts = [mk.a[0], mk.a[1], z, mk.b[0], mk.b[1], z];
        else if (mk.type === 'circle') pts = circlePts(mk.c[0], mk.c[1], z, mk.r, mk.dashed ? 56 : 96, mk.dashed);
        if (pts.length) { const m = new THREE.Mesh(fatLineGeometry(new Float32Array(pts)), markMat(mk.thin)); m.frustumCulled = false; m.renderOrder = 3; m.userData.until = mk.until; m.userData.after = mk.after; overlay.add(m); }
      });
    }
    const arrowCol = () => (STILL ? '#1f6fd1' : (getComputedStyle(document.documentElement).getPropertyValue('--arrow').trim() || '#1f6fd1'));
    function arrowMesh(a, b, opts) {
      const g = new THREE.Group(); const dir = b.clone().sub(a); const L = dir.length(); if (L < 1) return g;
      const r = (opts && opts.r) || 2.2, hl = Math.min(L * 0.45, r * 6.5), hr = r * 2.6;
      const mat = new THREE.MeshBasicMaterial({ color: lin(arrowCol()), transparent: true, opacity: 1, depthTest: !STILL });
      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(r, r, L - hl, 12), mat); shaft.position.y = (L - hl) / 2;
      const head = new THREE.Mesh(new THREE.ConeGeometry(hr, hl, 18), mat); head.position.y = L - hl / 2;
      g.add(shaft, head); g.position.copy(a); g.quaternion.setFromUnitVectors(new V3(0, 1, 0), dir.normalize()); g.renderOrder = 20;
      return g;
    }
    function arcArrow(center, axis, r, a0, a1, ref, opts) {
      const g = new THREE.Group(); const ax = axis.clone().normalize(); const u = ref.clone().sub(ax.clone().multiplyScalar(ref.dot(ax))).normalize(); const v = ax.clone().cross(u);
      const pts = []; const n = 40; const tube_r = (opts && opts.r) || 2.0;
      const sgn = Math.sign(a1 - a0) || 1, headA = (tube_r * 6.5) / r; const aEnd = a1 - sgn * headA;
      for (let i = 0; i <= n; i++) { const a = a0 + (aEnd - a0) * (i / n); pts.push(center.clone().add(u.clone().multiplyScalar(Math.cos(a) * r)).add(v.clone().multiplyScalar(Math.sin(a) * r))); }
      const mat = new THREE.MeshBasicMaterial({ color: lin(arrowCol()), transparent: true, opacity: 1, depthTest: !STILL });
      if (pts.length > 1) g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, tube_r, 8, false), mat));
      const pA = pts[pts.length - 1], pB = center.clone().add(u.clone().multiplyScalar(Math.cos(a1) * r)).add(v.clone().multiplyScalar(Math.sin(a1) * r));
      const head = new THREE.Mesh(new THREE.ConeGeometry(tube_r * 2.6, pA.distanceTo(pB) * 1.15, 18), mat);
      head.position.copy(pA.clone().add(pB).multiplyScalar(0.5)); head.quaternion.setFromUnitVectors(new V3(0, 1, 0), pB.clone().sub(pA).normalize()); g.add(head);
      g.renderOrder = 20; return g;
    }

    /* ---------- step state ---------- */
    let cur = null;
    const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
    function expandTrack(tr0) {
      const t = tr0.t || [0, 1]; const T = Object.assign({}, tr0);
      if (tr0.keys) T.keys = tr0.keys.map((k) => Object.assign({}, k));
      else if (tr0.screw) { const d = tr0.screw.dir || [0, 0, 1], L = tr0.screw.dist || 10, n = tr0.screw.turns || 3; T.keys = [{ t: t[0], off: [-d[0] * L, -d[1] * L, -d[2] * L], spin: n * 360 }, { t: t[1], off: [0, 0, 0], spin: 0 }]; T.kind = 'screw'; }
      else T.keys = [];
      T.keys.sort((a, b) => a.t - b.t);
      T.t0 = T.keys.length ? T.keys[0].t : 0; T.t1 = T.keys.length ? T.keys[T.keys.length - 1].t : 0;
      return T;
    }
    function sample(keys, prop, t) {
      const ks = keys.filter((k) => k[prop] != null); if (!ks.length) return undefined;
      if (t <= ks[0].t) return ks[0][prop]; if (t >= ks[ks.length - 1].t) return ks[ks.length - 1][prop];
      for (let i = 1; i < ks.length; i++) if (t <= ks[i].t) { const a = ks[i - 1], b = ks[i], u = ease((t - a.t) / Math.max(1e-6, b.t - a.t)); const va = a[prop], vb = b[prop]; return Array.isArray(va) ? va.map((x, j) => x + (vb[j] - x) * u) : va + (vb - va) * u; }
      return ks[ks.length - 1][prop];
    }
    function resolveStep(i) {
      const s = STEPS[i];
      const show = [...(s.in_place || []), ...(s.added || [])];
      const tracks = (s.anim || []).map(expandTrack);
      let dur = 0; tracks.forEach((tk) => { dur = Math.max(dur, Math.min(tk.t1, 8)); });
      (s.swap || []).forEach((w) => { dur = Math.max(dur, w.t + 0.6); });
      if (s.kibble) dur = Math.max(dur, s.kibble.until || 6);
      dur = Math.max(dur, s.min_dur || 0.01);
      const hl = new Set(s.highlight || s.added || []);
      return { i, s, show: new Set(show), tracks, dur, hl, pose: s.pose || null, place: s.place || {}, ghost: new Set(s.ghost || []) };
    }
    function stateAt(iid, t) {
      const R = cur; const st = { off: [0, 0, 0], rz: 0, rx: 0, spin: 0, about: [0, 0], pivot: [0, 0, 30], inMotion: false };
      const P = R.pose;
      if (P && (P.items === 'all' ? R.show.has(iid) : (P.items || []).includes(iid))) { if (P.rx != null) st.rx = P.rx; if (P.rz != null) st.rz = P.rz; if (P.off) st.off = P.off.slice(); if (P.pivot) st.pivot = P.pivot; }
      const PL = R.place[iid]; if (PL) { if (PL.off) st.off = PL.off.slice(); if (PL.rx != null) st.rx = PL.rx; if (PL.rz != null) st.rz = PL.rz; if (PL.pivot) st.pivot = PL.pivot; }
      const base = st.off.slice();
      R.tracks.forEach((tk) => {
        if (!(tk.items || []).includes(iid)) return;
        ['rz', 'rx', 'spin'].forEach((k) => { const v = sample(tk.keys, k, t); if (v !== undefined) st[k] = v; });
        const o = sample(tk.keys, 'off', t); if (o !== undefined) st.off = [base[0] + o[0], base[1] + o[1], base[2] + o[2]];
        if (tk.about) st.about = tk.about; if (tk.pivot) st.pivot = tk.pivot;
        if (t > tk.t0 - 1e-3 && t < tk.t1 + 1e-3) st.inMotion = true;
      });
      const L = R.s.layout && LAYOUT[iid]; if (L) { st.off = [st.off[0] + L.off[0], st.off[1] + L.off[1], st.off[2] + L.off[2]]; }
      return st;
    }
    const mA = new THREE.Matrix4(), mB = new THREE.Matrix4();
    function matrixOf(st, out) {
      out.makeTranslation(st.off[0], st.off[1], st.off[2]);
      if (st.rx) { const [px, py, pz] = st.pivot; mA.makeTranslation(px, py, pz); out.multiply(mA); mB.makeRotationX(st.rx * DEG); out.multiply(mB); mA.makeTranslation(-px, -py, -pz); out.multiply(mA); }
      if (st.rz) { const [ax, ay] = st.about; mA.makeTranslation(ax, ay, 0); out.multiply(mA); mB.makeRotationZ(st.rz * DEG); out.multiply(mB); mA.makeTranslation(-ax, -ay, 0); out.multiply(mA); }
      return out;
    }
    function applyItem(I, t) {
      const st = stateAt(I.iid, t);
      if (I.isCable) { I.g.matrix.identity(); I.g.matrixWorldNeedsUpdate = true; I.st = st; return st; }
      matrixOf(st, I.g.matrix); I.g.matrixWorldNeedsUpdate = true;
      const L = cur.s.layout && LAYOUT[I.iid];
      I.meshes.forEach((m, j) => {
        if (m.proc) return;
        if (L && L.inst) { const q = L.inst[j] || m.o.toArray(); m.mesh.position.set(q[0], q[1], q[2]); m.mesh.rotation.set(L.rx || 0, L.ry || 0, (st.spin || 0) * DEG); }
        else { m.mesh.position.copy(m.o); m.mesh.rotation.set(0, 0, (st.spin || 0) * DEG); }
      });
      I.st = st;
      return st;
    }

    /* ---------- looks: new parts in colour, installed parts calm ---------- */
    const CALM = new THREE.Color(), tmpC = new THREE.Color();
    const STILL_CALM = '#d5d9de';
    function stillColour(hex) { const c = new THREE.Color(hex); const hsl = {}; c.getHSL(hsl); if (hsl.l < 0.2) c.setHSL(hsl.h, hsl.s * 0.4, 0.33); return c; }
    function stillProcCol(hex) { const c = new THREE.Color(hex); const hsl = {}; c.getHSL(hsl); c.setHSL(hsl.h, hsl.s * 0.5, Math.max(0.78, hsl.l)); return '#' + c.getHexString(); }
    function setLook(I, role) {
      I.lookRole = role;
      I.meshes.forEach((m) => {
        const mat = m.mesh.material; if (!mat || !mat.color) return;
        if (m.proc) {
          if (!mat.userData.base) return;
          if (STILL && !mat.transparent) {
            const c = I.def.still_color || (role === 'new' ? stillColour(mat.userData.base).getStyle() : stillProcCol(mat.userData.base));
            mat.color.copy(lin(c)); if (mat.emissive) mat.emissive.copy(mat.color).multiplyScalar(role === 'new' ? 0.12 : 0.35);
          } else if (!STILL && I.isCable) {
            if (role === 'new') mat.color.copy(lin(mat.userData.base)); else { tmpC.set(mat.userData.base); CALM.set('#c6ccd2'); tmpC.lerp(CALM, 0.5); mat.color.copy(tmpC.convertSRGBToLinear()); }
          }
          return;
        }
        const base = PART[m.part].color;
        if (STILL) { mat.color.copy(role === 'new' ? lin(stillColour(base).getStyle()) : lin(STILL_CALM)); mat.roughness = 1; mat.metalness = 0; mat.envMapIntensity = 0; }
        else if (role === 'new') { mat.color.copy(lin(base)); }
        else { tmpC.set(base); CALM.set('#c6ccd2'); tmpC.lerp(CALM, 0.66); mat.color.copy(tmpC.convertSRGBToLinear()); }
        mat.emissive && mat.emissive.setRGB(0, 0, 0);
      });
    }

    /* ---------- layouts for the kit and hardware pages ---------- */
    let LAYOUT = {};
    function computeLayout(spec) {
      const out = {}; const gap = spec.gap || 30; let y = 0;
      const rows = spec.rows || [];
      const rowBoxes = rows.map((row) => row.map((entry) => {
        const ids = String(entry).split('+'); const I0 = IT[ids[0]];
        const lie = Array.isArray(spec.lie) ? spec.lie.includes(ids[0]) : !!spec.lie;
        if (spec.spread && I0 && I0.meshes.length > 1 && !I0.def.proc) {
          const g = new THREE.Box3(); const sizes = I0.meshes.map((m) => { const b = m.mesh.geometry.boundingBox.clone(); if (lie) b.set(new V3(b.min.z, b.min.y, -b.max.x), new V3(b.max.z, b.max.y, -b.min.x)); return b; });
          let x = 0; const inst = []; sizes.forEach((b) => { const w = b.max.x - b.min.x; inst.push([x - b.min.x, 0, -b.min.z]); x += w + (spec.igap || 10); });
          const W = x - (spec.igap || 10); inst.forEach((p) => { p[0] -= W / 2; });
          const D2 = Math.max(...sizes.map((b) => b.max.y - b.min.y)); const Hh = Math.max(...sizes.map((b) => b.max.z - b.min.z));
          g.set(new V3(-W / 2, -D2 / 2, 0), new V3(W / 2, D2 / 2, Hh));
          return { ids, box: g, inst, lie };
        }
        const b = new THREE.Box3(); ids.forEach((k) => { if (IT[k]) b.union(IT[k].box); });
        return { ids, box: b };
      }));
      rowBoxes.forEach((row) => {
        const depth = Math.max(...row.map((r) => r.box.max.y - r.box.min.y)); const W = row.reduce((a, r) => a + (r.box.max.x - r.box.min.x), 0) + gap * (row.length - 1);
        let x = -W / 2;
        row.forEach((r) => {
          const w = r.box.max.x - r.box.min.x; const cx = x + w / 2, cy = y - depth / 2;
          const bc = r.box.getCenter(new V3());
          r.ids.forEach((k) => {
            if (r.inst) out[k] = { off: [cx, cy, 0], inst: r.inst, ry: r.lie ? Math.PI / 2 : 0 };
            else out[k] = { off: [cx - bc.x, cy - bc.y, -r.box.min.z] };
          });
          x += w + gap;
        });
        y -= depth + gap;
      });
      const ys = Object.values(out).map((L) => L.off[1]); const cy = (Math.max(...ys) + Math.min(...ys)) / 2; Object.values(out).forEach((L) => { L.off[1] -= cy; });
      return out;
    }

    /* ---------- labels (balloons, dimension texts, callouts) ---------- */
    let labs = [];
    function bboxWorld(I) { const b = new THREE.Box3(); I.g.updateMatrixWorld(true); I.meshes.forEach((m) => { const g = m.mesh.geometry; if (!g.boundingBox) g.computeBoundingBox(); b.union(g.boundingBox.clone().applyMatrix4(m.mesh.matrixWorld)); }); return b; }
    function makeLabels(i, noCallouts) {
      labelsEl.textContent = ''; labs = [];
      if (!cur) return; const s = STEPS[i];
      const list = s.labels != null ? s.labels : (s.added || []).filter((k) => ITEMS[k] && ITEMS[k].ref);
      list.forEach((ent) => {
        const e = typeof ent === 'string' ? { item: ent } : ent; const I = IT[e.item]; if (!I || !I.def.ref) return;
        const div = el('div', 'lab'); div.append(balloon(e.ref || I.def.ref)); const q = e.qty != null ? e.qty : I.def.qty; if (q && q > 1) div.append(el('span', 'qty', q + '×'));
        labelsEl.append(div); labs.push({ div, kind: 'item', I, at: e.at || 'top', pt: e.pt || null, dx: e.dx || 0, dy: e.dy || 0 });
      });
      (s.dims || []).forEach((d) => { const div = el('div', 'lab dim', tr(d.text)); labelsEl.append(div); labs.push({ div, kind: 'pt', after: d.after, p: new V3(...(d.label_at || [(d.a[0] + d.b[0]) / 2, (d.a[1] + d.b[1]) / 2, (d.a[2] + d.b[2]) / 2])) }); });
      if (!noCallouts) (s.callouts || []).forEach((c) => {
        const div = el('div', 'lab call', tr(c.text)); labelsEl.append(div);
        const o = { div, kind: 'pt', until: c.until, after: c.after, p: new V3(...c.at) };
        if (c.dx != null || c.dy != null) {            // leader: dot at the point, text offset by (dx, dy) still-px
          o.lead = [c.dx || 0, c.dy || 0]; o.dot = el('div', 'lab-dot'); o.line = el('div', 'lab-line'); labelsEl.append(o.line, o.dot);
        }
        labs.push(o);
      });
    }
    const pv = new V3();
    function drawLabels() {
      const W0 = stage.clientWidth, H0 = stage.clientHeight; const placed = [];
      labs.forEach((o) => {
        let p;
        const hideLead = () => { if (o.dot) { o.dot.style.display = 'none'; o.line.style.display = 'none'; } };
        if (o.hide) { o.div.style.display = 'none'; hideLead(); return; }
        if (o.kind === 'item') {
          if (!o.I.g.visible) { o.div.style.display = 'none'; return; }
          if (o.pt) { o.I.g.updateMatrixWorld(true); p = new V3(o.pt[0], o.pt[1], o.pt[2]).applyMatrix4(o.I.g.matrixWorld); }   // anchor in the item's own frame
          else { const b = bboxWorld(o.I); p = new V3((b.min.x + b.max.x) / 2, (b.min.y + b.max.y) / 2, o.at === 'bottom' ? b.min.z : b.max.z); }
        } else p = o.p.clone();
        pv.copy(p).project(camera);
        if (pv.z > 1 || Math.abs(pv.x) > 1.05 || Math.abs(pv.y) > 1.05) { o.div.style.display = 'none'; hideLead(); return; }
        o.div.style.display = 'flex';
        let x = (pv.x * 0.5 + 0.5) * W0 + (o.dx || 0), y = (-pv.y * 0.5 + 0.5) * H0 + (o.dy || 0);
        if (o.lead) {
          const k = STILL ? 1 : 0.55, ax = x, ay = y; x += o.lead[0] * k; y += o.lead[1] * k;
          const L = Math.hypot(x - ax, y - ay), ang = Math.atan2(y - ay, x - ax);
          o.dot.style.display = 'block'; o.dot.style.transform = 'translate(' + ax.toFixed(1) + 'px,' + ay.toFixed(1) + 'px)';
          o.line.style.display = 'block'; o.line.style.width = L.toFixed(1) + 'px';
          o.line.style.transform = 'translate(' + ax.toFixed(1) + 'px,' + ay.toFixed(1) + 'px) rotate(' + ang.toFixed(4) + 'rad)';
        }
        if (o.kind === 'item' && !o.pt) { y -= STILL ? 34 : 22; }
        const w = o.div.offsetWidth || 30, h = o.div.offsetHeight || 24;
        x = clamp(x, w / 2 + 4, W0 - w / 2 - 4); y = clamp(y, h / 2 + 4, H0 - h / 2 - 4);
        for (let it = 0; it < 8; it++) { const hit = placed.find((r) => Math.abs(r.x - x) < (r.w + w) / 2 + 3 && Math.abs(r.y - y) < (r.h + h) / 2 + 3); if (!hit) break; y = hit.y - (hit.h + h) / 2 - 4; }
        placed.push({ x, y, w, h });
        o.div.style.transform = 'translate(' + (x - w / 2).toFixed(1) + 'px,' + (y - h / 2).toFixed(1) + 'px)';
      });
    }
    buildLabels = (i) => makeLabels(i);

    /* ---------- camera ---------- */
    const C = { t: new V3(0, 0, 0), r: 800, az: -1.2, el: 0.5 }; const goal = { t: null, r: null, az: null, el: null };
    let W = 1, H = 1;
    function camBasis(az, el) {
      const back = new V3(Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el));
      const right = new V3(0, 0, 1).cross(back).normalize(); if (right.lengthSq() < 1e-6) right.set(1, 0, 0);
      const up = back.clone().cross(right).normalize(); return { back, right, up };
    }
    function fitBoxes(boxes, az, el, aspect, margin) {
      const { back, right, up } = camBasis(az, el); const pts = [];
      boxes.forEach((b) => { if (b.isEmpty()) return; for (let k = 0; k < 8; k++) pts.push(new V3(k & 1 ? b.max.x : b.min.x, k & 2 ? b.max.y : b.min.y, k & 4 ? b.max.z : b.min.z)); });
      if (!pts.length) return { t: new V3(), r: 600 };
      const tv = Math.tan((camera.fov * DEG) / 2) / margin, th = tv * aspect;
      let cx = 0, cy = 0, cz = 0; pts.forEach((p) => { cx += p.x; cy += p.y; cz += p.z; }); let t = new V3(cx / pts.length, cy / pts.length, cz / pts.length);
      for (let pass = 0; pass < 3; pass++) {
        let d = 0; const xs = [], ys = [];
        pts.forEach((p) => { const q = p.clone().sub(t); const x = q.dot(right), y = q.dot(up), z = q.dot(back); d = Math.max(d, z + Math.abs(x) / th, z + Math.abs(y) / tv); xs.push([x, z]); ys.push([y, z]); });
        let xl = Infinity, xr = -Infinity, yb = Infinity, yt = -Infinity;
        xs.forEach(([x, z]) => { const s = x / (d - z); xl = Math.min(xl, s); xr = Math.max(xr, s); });
        ys.forEach(([y, z]) => { const s = y / (d - z); yb = Math.min(yb, s); yt = Math.max(yt, s); });
        t = t.add(right.clone().multiplyScalar(((xl + xr) / 2) * d)).add(up.clone().multiplyScalar(((yb + yt) / 2) * d));
        if (pass === 2) return { t, r: d };
      }
      return { t, r: 600 };
    }
    function stepBoxes(R, times) {
      const cam = R.s.camera || {}; const ids = cam.fit || [...R.show].filter((k) => !(ITEMS[k] && ITEMS[k].nofit));
      const boxes = []; times = times || [0, R.dur * 0.5, R.dur];
      times.forEach((t) => { ids.forEach((k) => { const I = IT[k]; if (!I) return; applyItem(I, t); I.g.updateMatrixWorld(true); if (I.isCable) updateCable(I); const b = bboxWorld(I); if (!b.isEmpty()) boxes.push(b); }); });
      (R.s.dims || []).forEach((d) => { boxes.push(new THREE.Box3().setFromPoints([new V3(...d.a), new V3(...d.b)])); });
      return boxes;
    }
    function aspectNow() { return Math.max(0.3, W / Math.max(1, H)); }
    function camGoalFor(R, aspect, times) {
      const cam = R.s.camera || {}; const az = (cam.az != null ? cam.az : -60) * DEG, el = (cam.el != null ? cam.el : 25) * DEG;
      const narrow = !STILL && aspect < 0.9 ? 1.06 : 1;
      const f = fitBoxes(stepBoxes(R, times), az, el, aspect, ((cam.margin || 1.12) * (STILL ? (cam.still_margin || 1.04) : 1) * narrow) / (cam.zoom || 1));
      if (cam.target) { const tg = new V3(...cam.target); const ext = f.t.distanceTo(tg); f.t.copy(tg); f.r += ext * 0.8; }
      if (cam.dist) f.r = cam.dist;
      if (cam.shift) f.t.add(new V3(...cam.shift));
      return { t: f.t, r: f.r, az, el };
    }
    function camHome(instant) {
      if (!cur) return; const g = camGoalFor(cur, aspectNow());
      if (instant) { C.t.copy(g.t); C.r = g.r; C.az = g.az; C.el = g.el; goal.t = goal.r = goal.az = goal.el = null; }
      else { goal.t = g.t; goal.r = g.r; goal.az = g.az; goal.el = g.el; }
    }

    /* ---------- orbit / zoom / pan (mouse + touch, from the viewer) ---------- */
    const tR = new V3(), tU = new V3();
    function zoomBy(f) { C.r = clamp(C.r * f, 40, 12000); goal.r = null; }
    function pan(dx, dy) { camera.updateMatrixWorld(); const k = (2 * C.r * Math.tan((camera.fov * DEG) / 2)) / H; tR.setFromMatrixColumn(camera.matrixWorld, 0); tU.setFromMatrixColumn(camera.matrixWorld, 1); C.t.addScaledVector(tR, -dx * k).addScaledVector(tU, dy * k); goal.t = null; }
    const ptrs = new Map(); let pinchD = 0, mid = null, lastTap = 0;
    const dist2 = () => { const a = [...ptrs.values()]; return Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y); };
    const midp = () => { const a = [...ptrs.values()]; return { x: (a[0].x + a[1].x) / 2, y: (a[0].y + a[1].y) / 2 }; };
    canvas.addEventListener('pointerdown', (e) => { S.userCam = true; try { canvas.setPointerCapture(e.pointerId); } catch (_) { /* ignore */ } ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey }); if (ptrs.size === 2) { pinchD = dist2(); mid = midp(); } goal.az = goal.el = null; });
    canvas.addEventListener('pointermove', (e) => {
      const p = ptrs.get(e.pointerId); if (!p) return; const dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
      if (ptrs.size === 1) { if (p.pan) pan(dx, dy); else { C.az -= dx * 0.0075; C.el = clamp(C.el + dy * 0.0075, -1.5, 1.5); } }
      else if (ptrs.size === 2) { const d = dist2(); if (pinchD > 0 && d > 0) zoomBy(pinchD / d); pinchD = d; const m = midp(); pan(m.x - mid.x, m.y - mid.y); mid = m; }
    });
    function endPtr(e) {
      if (!ptrs.has(e.pointerId)) return; ptrs.delete(e.pointerId); if (ptrs.size < 2) { pinchD = 0; mid = null; }
      if (e.type === 'pointerup' && e.pointerType !== 'mouse') { const now = performance.now(); if (now - lastTap < 320) { camHome(false); lastTap = 0; } else lastTap = now; }
    }
    canvas.addEventListener('pointerup', endPtr); canvas.addEventListener('pointercancel', endPtr);
    canvas.addEventListener('dblclick', (e) => { e.preventDefault(); camHome(false); });
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    canvas.addEventListener('wheel', (e) => { e.preventDefault(); S.userCam = true; zoomBy(Math.exp(clamp(e.deltaY, -200, 200) * 0.0012)); }, { passive: false });

    /* ---------- grid / bench floor ---------- */
    const benchG = new THREE.Group(); scene.add(benchG);
    const grid = new THREE.GridHelper(1600, 80, 0x9aa6ab, 0xc5cdd0); grid.rotation.x = Math.PI / 2; grid.material.transparent = true; grid.material.opacity = 0.45; grid.material.depthWrite = false; benchG.add(grid);
    const catcher = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), new THREE.ShadowMaterial({ opacity: 0.16 })); catcher.receiveShadow = true; catcher.position.z = 0.3; benchG.add(catcher);
    let benchZ = 0;

    /* ---------- kibble (first test / use) ---------- */
    const kibGeo = new THREE.IcosahedronGeometry(1, 1); kibGeo.scale(5.5, 4.6, 3.8);
    const kibMat = new THREE.MeshStandardMaterial({ color: lin('#8a5528'), roughness: 0.8 });
    const NK = 48; const kib = new THREE.InstancedMesh(kibGeo, kibMat, NK); kib.visible = false; kib.castShadow = true; kib.frustumCulled = false; scene.add(kib);
    function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
    const kM = new THREE.Matrix4(), kQ = new THREE.Quaternion(), kE = new THREE.Euler(), kS = new V3(), kP = new V3();
    function placeKibble(t) {
      const K = cur && cur.s.kibble; if (!K) { kib.visible = false; return; }
      const o = SC.outlet_xyz || [-42, 0, -104]; const floor = FLOOR_Z + 7; const per = K.per || 12; const starts = K.portions || [0.8];
      let n = 0;
      starts.forEach((t0, p) => {
        for (let j = 0; j < per && n < NK; j++, n++) {
          const id = p * per + j; const td = t0 + rnd(id) * 0.25; const h = o[2] - floor; const tf = Math.sqrt((2 * h) / 3200);
          const lx = o[0] + (rnd(id + 7) - 0.5) * 60, ly = o[1] + (rnd(id + 13) - 0.5) * 60, lz = floor + rnd(id + 3) * 6 + p * 2;
          if (t < td) { kS.set(0.0001, 0.0001, 0.0001); kP.set(o[0], o[1], o[2]); }
          else { const u = Math.min(1, (t - td) / tf); kP.set(o[0] + (lx - o[0]) * u, o[1] + (ly - o[1]) * u, o[2] - (o[2] - lz) * u * u); kS.set(1, 1, 1); }
          kE.set(rnd(id + 1) * 6, rnd(id + 2) * 6, rnd(id + 4) * 6 + (t - td) * 4 * (t < td + tf ? 1 : 0)); kQ.setFromEuler(kE);
          kM.compose(kP, kQ, kS); kib.setMatrixAt(n, kM);
        }
      });
      for (; n < NK; n++) { kM.makeScale(0.0001, 0.0001, 0.0001); kib.setMatrixAt(n, kM); }
      kib.instanceMatrix.needsUpdate = true; kib.visible = true;
    }

    /* ---------- enter a step ---------- */
    let arrows = [];
    /* Arrows follow the keyframe segments of each track: one straight arrow per translation segment,
       one arc per rotation (rz) segment, one small arrow per screw. Wizard: each arrow shows during its
       own time window. Stills: only the segment that is running (or next) at the still's time. */
    function buildArrows(R, tNow) {
      arrows.forEach((a) => overlay.remove(a.g)); arrows = [];
      const s = R.s; if (s.arrows === false) return;
      const camAz = ((s.camera && s.camera.az) != null ? s.camera.az : -60);
      R.tracks.forEach((tk) => {
        if (tk.arrow === false || !tk.items || !tk.items.length) return;
        const A = tk.arrow || {}; const I = IT[tk.items[0]]; if (!I || I.isCable || !R.show.has(I.iid)) return;
        const apT = (s.appear || {})[I.iid];
        if (STILL && apT != null && tNow < apT - 1e-3 && !R.noAppear) return;     // not on screen yet
        const centreAt = (t) => { applyItem(I, t); I.g.updateMatrixWorld(true); return bboxWorld(I).getCenter(new V3()); };
        const pick = (segs) => {
          if (!STILL) return segs;
          if (R.arrowMode === 'current') return segs.filter((g) => g.t0 <= tNow + 1e-3 && g.t1 > tNow + 1e-3);
          const sg = segs.find((g) => g.t1 > tNow + 1e-3); return sg ? [sg] : [];
        };
        if (tk.kind === 'screw') {
          const d = new V3(...(tk.screw.dir || [0, 0, 1])).normalize();
          if (!STILL || tNow >= tk.t1 - 1e-3) return;
          applyItem(I, Math.max(tNow, tk.t0)); I.g.updateMatrixWorld(true);
          const remain = sample(tk.keys, 'off', Math.max(tNow, tk.t0)) || [0, 0, 0];
          const remL = Math.hypot(remain[0], remain[1], remain[2]);
          I.meshes.forEach((m) => {
            const bb = m.mesh.geometry.boundingBox; const half = (bb.max.z - bb.min.z) / 2;
            const c = new V3().setFromMatrixPosition(m.mesh.matrixWorld); const tip = c.clone().add(d.clone().multiplyScalar(half + 1.5));
            const L = Math.max(remL - 3, 9); const g = arrowMesh(tip, tip.clone().add(d.clone().multiplyScalar(L)), { r: 1.15 });
            overlay.add(g); arrows.push({ g, t0: tk.t0 - 0.4, t1: tk.t1 });
          });
          return;
        }
        const ks = tk.keys;
        if (!A.none && ks.some((q) => q.off)) {
          const segs = [];
          for (let j = 1; j < ks.length; j++) {
            const ka = ks[j - 1], kb = ks[j]; const oa = sample(ks, 'off', ka.t), ob = sample(ks, 'off', kb.t);
            if (!oa || !ob || Math.hypot(ob[0] - oa[0], ob[1] - oa[1], ob[2] - oa[2]) < 10) continue;
            segs.push({ t0: ka.t, t1: kb.t });
          }
          pick(segs).forEach((sg) => {
            const a = centreAt(STILL ? Math.max(tNow, sg.t0) : sg.t0), b = centreAt(sg.t1);
            const d = b.clone().sub(a); const L = d.length(); if (L < 10) return;
            const dir = d.clone().normalize(); const sz = I.box.getSize(new V3()); const along = Math.abs(new V3(Math.abs(dir.x), Math.abs(dir.y), Math.abs(dir.z)).dot(sz)) / 2;
            let p0 = a.clone().add(dir.clone().multiplyScalar(Math.min(along * 0.6, L * 0.25)));
            let p1 = b.clone().sub(dir.clone().multiplyScalar(Math.min(along + 4, L * 0.75)));
            if (A.side) { const sh = new V3(...A.side); p0.add(sh); p1.add(sh); }
            if (p1.clone().sub(p0).dot(dir) < 8) { p0 = a.clone().add(dir.clone().multiplyScalar(L * 0.2)); p1 = a.clone().add(dir.clone().multiplyScalar(L * 0.8)); }
            const g = arrowMesh(p0, p1, { r: A.r || 2.4 }); overlay.add(g); arrows.push({ g, t0: sg.t0 - 0.4, t1: sg.t1 });
          });
        }
        if (!A.none && ks.some((q) => q.rz != null)) {
          const segs = [];
          for (let j = 1; j < ks.length; j++) { const ra = sample(ks, 'rz', ks[j - 1].t), rb = sample(ks, 'rz', ks[j].t); if (ra != null && rb != null && Math.abs(rb - ra) > 4) segs.push({ t0: ks[j - 1].t, t1: ks[j].t, ra, rb }); }
          pick(segs).forEach((sg) => {
            applyItem(I, sg.t1); I.g.updateMatrixWorld(true); const bw = bboxWorld(I);
            const ab = tk.about || [0, 0]; const r = A.radius || Math.max(bw.max.x - ab[0], bw.max.y - ab[1], ab[0] - bw.min.x, ab[1] - bw.min.y) + 12;
            const z = A.z != null ? A.z : (A.top ? bw.max.z + 6 : bw.min.z - 6);
            const a0 = (A.a0 != null ? A.a0 : camAz - 35) * DEG; const span = (sg.rb - sg.ra) * DEG * (A.scale || 1.6);
            const flipped = I.st && Math.abs(((I.st.rx || 0) % 360 + 360) % 360 - 180) < 1;
            const g = arcArrow(new V3(ab[0], flipped ? -ab[1] : ab[1], z), new V3(0, 0, flipped ? -1 : 1), r, a0, a0 + span, new V3(1, 0, 0), { r: A.r || 2.8 });
            overlay.add(g); arrows.push({ g, t0: sg.t0 - 0.4, t1: sg.t1 });
          });
        }
        if (!A.none && ks.some((q) => q.spin != null) && tk.kind !== 'screw') {
          const segs = [];
          for (let j = 1; j < ks.length; j++) { const ra = sample(ks, 'spin', ks[j - 1].t), rb = sample(ks, 'spin', ks[j].t); if (ra != null && rb != null && Math.abs(rb - ra) > 4) segs.push({ t0: ks[j - 1].t, t1: ks[j].t, ra, rb }); }
          pick(segs).forEach((sg) => {
            applyItem(I, sg.t0); I.g.updateMatrixWorld(true);
            const q = new THREE.Quaternion().setFromRotationMatrix(I.g.matrixWorld); const ax = new V3(0, 0, 1).applyQuaternion(q);
            const seen = [];                       // one arc per turning instance (keys / O-rings on the same axis are skipped)
            I.meshes.forEach((m) => {
              const cxy = new V3().setFromMatrixPosition(m.mesh.matrixWorld);
              if (seen.some((p) => Math.hypot(p.x - cxy.x, p.y - cxy.y) < 3)) return; seen.push(cxy);
              const bb = m.mesh.geometry.boundingBox; const c = new V3().setFromMatrixPosition(m.mesh.matrixWorld);
              const lift = (A.lift != null ? A.lift : (bb.max.z - bb.min.z) / 2 + 3);
              const g = arcArrow(c.clone().add(ax.clone().multiplyScalar(-lift)), ax, A.radius || 13, (A.a0 || 20) * DEG, ((A.a0 || 20) + (sg.rb - sg.ra)) * DEG, new V3(1, 0, 0).applyQuaternion(q), { r: 1.5 });
              overlay.add(g); arrows.push({ g, t0: sg.t0 - 0.4, t1: sg.t1 });
            });
          });
        }
      });
      (s.arrows_extra || []).forEach((x) => {
        if (STILL && x.still === false) return; if (!STILL && x.wizard === false) return;
        let g = null;
        if (x.type === 'line') g = arrowMesh(new V3(...x.from), new V3(...x.to), { r: x.r || 2.4 });
        else if (x.type === 'arc') g = arcArrow(new V3(...x.center), new V3(...(x.axis || [0, 0, 1])), x.radius, x.a0 * DEG, x.a1 * DEG, new V3(...(x.ref || [1, 0, 0])), { r: x.r || 2.6 });
        if (g) { overlay.add(g); arrows.push({ g, t0: x.t ? x.t[0] : -1, t1: x.t ? x.t[1] : R.dur + 99, keep: !x.t, stillKeep: true }); }
      });
    }
    function buildDims(s) {
      (s.dims || []).forEach((d) => {
        const grp = new THREE.Group(); grp.userData.after = d.after;
        const a = new V3(...d.a), b = new V3(...d.b); const dir = b.clone().sub(a).normalize(); const L = a.distanceTo(b);
        const col = '#2a3237'; const ah = Math.min(9, L * 0.3);
        const m = fatLines([a.x, a.y, a.z, b.x, b.y, b.z], col, STILL ? 2.4 : 1.8, { zbias: 0.001 }); m.renderOrder = 4; grp.add(m);
        [[a, dir], [b, dir.clone().negate()]].forEach(([p, dv]) => { const cone = new THREE.Mesh(new THREE.ConeGeometry(2.6, ah, 12), new THREE.MeshBasicMaterial({ color: lin(col) })); cone.position.copy(p.clone().add(dv.clone().multiplyScalar(ah / 2))); cone.quaternion.setFromUnitVectors(new V3(0, -1, 0), dv); grp.add(cone); });
        (d.ext || []).forEach((e) => { grp.add(fatLines(e, col, STILL ? 1.6 : 1.2, { zbias: 0.001 })); });
        overlay.add(grp);
      });
    }
    function itemsVisible(R) { Object.values(IT).forEach((I) => { I.g.visible = R.show.has(I.iid); }); }
    function lookStep(R) {
      const real = R.s.look === 'real';
      Object.values(IT).forEach((I) => { if (!R.show.has(I.iid)) return; setLook(I, real || R.hl.has(I.iid) ? 'new' : 'calm'); setGhost(I, R.ghost.has(I.iid)); });
    }
    function setGhost(I, on) {
      I.meshes.forEach((m) => {
        if (m.proc) return; const mat = m.mesh.material; const want = !!on;
        if (!!mat.userData.ghost !== want) { mat.userData.ghost = want; mat.transparent = want; mat.depthWrite = !want; mat.opacity = want ? (STILL ? 0.16 : 0.2) : 1; mat.needsUpdate = true; }
        m.mesh.castShadow = !want; (m.mesh.userData.outl || []).forEach((o) => { o.visible = !want; });
        if (want && !STILL) { const c = mat.color; c.lerp(new THREE.Color(0.5, 0.55, 0.6), 0.3); }
      });
    }
    function swapState(t) { // items hidden / shown by swaps at time t
      const hide = new Set(), show = new Set();
      ((cur && cur.s.swap) || []).forEach((w) => { const done = t >= w.t; (w.from || []).forEach((k) => (done ? hide : show).add(k)); (w.to || []).forEach((k) => (done ? show : hide).add(k)); });
      show.forEach((k) => { if (hide.has(k)) hide.delete(k); });
      return hide;
    }
    enterStep = function (i) {
      cur = resolveStep(i);
      LAYOUT = cur.s.layout ? computeLayout(cur.s.layout) : {};
      itemsVisible(cur); lookStep(cur);
      clearOverlay(); arrows = []; buildMarks(cur.s.marks); buildDims(cur.s);
      S.t = (reduce || !S.auto) && !STILL ? cur.dur : 0; S.playing = !reduce; S.hold = 0;
      if (!S.auto && !reduce) { S.t = 0; S.playing = true; }
      applyAll(S.t);
      buildArrows(cur, S.t);
      const bench = ['bench', 'kit', 'hardware', 'box', 'shellbench', 'plates', 'clean', 'info', 'flangebench', 'panel'].includes(cur.s.context);
      benchG.visible = bench && !STILL;
      S.userCam = false; camHome(!S.everEntered); S.everEntered = true;
      makeLabels(i, STILL && !cur.s.still_callouts);
      applyAll(S.t);
    };
    replay = function () { if (!cur) return; S.t = 0; S.playing = true; S.hold = 0; };
    function applyAll(t) {
      const ap = (cur && cur.s.appear) || {}, va = (cur && cur.s.vanish) || {};
      const hidden = swapState(t);
      Object.values(IT).forEach((I) => {
        if (!cur.show.has(I.iid) || (cur.hidden && cur.hidden.has(I.iid))) { I.g.visible = false; return; }
        let vis = !(ap[I.iid] != null && t < ap[I.iid] && !cur.noAppear);
        if (va[I.iid] != null && t >= va[I.iid]) vis = false;
        if (hidden.has(I.iid)) vis = false;
        I.g.visible = vis;
        if (vis || I.isCable) applyItem(I, t);
      });
      Object.values(IT).forEach((I) => { if (I.isCable && I.g.visible) { const ref = CAB[I.def.cable] && CAB[I.def.cable].ref; if (ref && IT[ref]) { applyItem(IT[ref], t); } updateCable(I); } });
      placeKibble(t);
      overlay.children.forEach((m) => { if (m.userData.until != null || m.userData.after != null) m.visible = (m.userData.until == null || t < m.userData.until) && (m.userData.after == null || t >= m.userData.after); });
      labs.forEach((o) => { o.hide = (o.until != null && t >= o.until) || (o.after != null && t < o.after); });
      arrows.forEach((a) => {
        let op = 1; if (!STILL && !a.keep) { if (t > a.t1 || t < a.t0 - 0.6) op = 0; else if (t > a.t0 + 0.4) op = 1 - (t - a.t0 - 0.4) / Math.max(0.2, a.t1 - a.t0 - 0.4); op = clamp(op, 0, 1) * 0.92; }
        if (STILL && !a.stillKeep && a.t1 != null && t > a.t1 + 1e-3 && !a.keep) op = 0;
        a.g.visible = op > 0.02; a.g.traverse((m) => { if (m.material) m.material.opacity = op; });
      });
    }
    let flashT = 0, flashSet = new Set();
    flashItems = function (ids) {
      if (!S.ready3d) return; flashSet = new Set(ids.filter((k) => IT[k] && IT[k].g.visible)); flashT = 1.4;
    };

    /* ---------- loading ---------- */
    function resize() {
      W = Math.max(1, stage.clientWidth); H = Math.max(1, stage.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, STILL ? 3 : 2)); renderer.setSize(W, H, false);
      camera.aspect = W / H; camera.updateProjectionMatrix();
      const pr = renderer.getPixelRatio(); RES.set(W * pr, H * pr);
    }
    new ResizeObserver(() => { resize(); if (cur && !STILL && !S.userCam) camHome(true); }).observe(stage);
    resize();

    async function load() {
      const jobs = []; const geomIds = new Set();
      Object.values(IT).forEach((I) => (I.def.parts || []).forEach((pid) => { const p = PART[pid]; if (!p) return; p.geoms.forEach((g, j) => { jobs.push([I, p, g, j]); geomIds.add(g.g); }); }));
      let done = 0; const all = [...geomIds];
      await Promise.all(all.map(async (gid) => { await getGeo(gid); done++; if (done % 8 === 0) $('stageMsg').textContent = ui('loading') + ' ' + Math.round((done / all.length) * 100) + '%'; }));
      if (templateReady) await templateReady;
      jobs.forEach(([I, p, g, j]) => {
        if (!I.mats) I.mats = {};
        const mat = I.mats[p.id] || (I.mats[p.id] = matFor(p));
        const mesh = new THREE.Mesh(geoCache[g.g], mat); mesh.castShadow = true; mesh.receiveShadow = true; mesh.position.set(g.o[0], g.o[1], g.o[2]);
        I.g.add(mesh); I.meshes.push({ mesh, part: p.id, o: new V3(g.o[0], g.o[1], g.o[2]), j });
      });
      Object.values(IT).forEach((I) => {
        if (I.def.proc) return;
        I.box.makeEmpty(); I.meshes.forEach((m) => { const b = m.mesh.geometry.boundingBox.clone().translate(m.o); I.box.union(b); });
      });
      if (STILL) Object.values(IT).forEach((I) => I.meshes.forEach((m) => { if (!m.proc || m.mesh.userData.outline) { if (m.mesh.material && !m.mesh.material.transparent) { m.mesh.material.polygonOffset = true; m.mesh.material.polygonOffsetFactor = 1; m.mesh.material.polygonOffsetUnits = 1; addOutlines(m.mesh); } } }));
    }

    /* ---------- frame loop ---------- */
    let last = performance.now();
    function frame(now) {
      const dt = Math.min(0.05, Math.max(0, (now - last) / 1000)); last = now;
      if (cur && !STILL) {
        if (S.playing) {
          S.t += dt;
          if (S.t >= cur.dur) { S.t = cur.dur; if (S.auto) { S.hold += dt; if (S.hold > 2.2) { S.t = 0; S.hold = 0; } } else S.playing = false; }
        }
        applyAll(S.t);
        $('tlFill').style.width = (cur.dur > 0.05 ? (S.t / cur.dur) * 100 : 100) + '%';
        Object.values(IT).forEach((I) => {
          if (!I.g.visible || I.def.proc) return; const moving = I.st && I.st.inMotion && cur.hl.has(I.iid); const fl = flashT > 0 && flashSet.has(I.iid);
          const k = fl ? 0.5 * (0.5 + 0.5 * Math.sin(now / 90)) : moving ? 0.035 * (0.5 + 0.5 * Math.sin(now / 160)) : 0;
          I.meshes.forEach((m) => { if (m.mesh.material.emissive) { if (fl) m.mesh.material.emissive.setRGB(k, k * 0.55, k * 0.15); else m.mesh.material.emissive.setRGB(k, k, k); } });
        });
        if (flashT > 0) flashT -= dt;
      }
      const kk = reduce ? 1 : 1 - Math.pow(0.002, dt);
      if (goal.t) { C.t.lerp(goal.t, kk); if (C.t.distanceTo(goal.t) < 0.05) { C.t.copy(goal.t); goal.t = null; } }
      if (goal.r != null) { C.r += (goal.r - C.r) * kk; if (Math.abs(goal.r - C.r) < 0.05) { C.r = goal.r; goal.r = null; } }
      if (goal.az != null) { let d = goal.az - C.az; d = Math.atan2(Math.sin(d), Math.cos(d)); C.az += d * kk; if (Math.abs(d) < 1e-3) { C.az = goal.az; goal.az = null; } }
      if (goal.el != null) { const d = goal.el - C.el; C.el += d * kk; if (Math.abs(d) < 1e-3) { C.el = goal.el; goal.el = null; } }
      const ce = Math.cos(C.el);
      camera.position.set(C.t.x + C.r * ce * Math.cos(C.az), C.t.y + C.r * ce * Math.sin(C.az), C.t.z + C.r * Math.sin(C.el));
      camera.lookAt(C.t);
      const near = STILL ? clamp(C.r / 10, 0.5, 200) : clamp(C.r / 50, 0.5, 60); if (Math.abs(camera.near - near) > near * 0.2) { camera.near = near; camera.far = Math.max(6000, C.r * 30); camera.updateProjectionMatrix(); }
      const b = camBasis(C.az, C.el);
      key.position.copy(C.t).add(b.back.clone().multiplyScalar(900).add(b.right.clone().multiplyScalar(500)).add(new V3(0, 0, 900))); key.target.position.copy(C.t);
      fill.position.copy(C.t).add(b.back.clone().multiplyScalar(600).add(b.right.clone().multiplyScalar(-700)).add(new V3(0, 0, -200))); fill.target.position.copy(C.t);
      { const sc = key.shadow.camera, h = Math.max(300, C.r * 0.9); sc.left = -h; sc.right = h; sc.top = h; sc.bottom = -h; sc.near = 10; sc.far = 6000; sc.updateProjectionMatrix(); }
      if (cur && benchG.visible) {
        let mz = Infinity; Object.values(IT).forEach((I) => { if (I.g.visible && !I.def.proc) mz = Math.min(mz, bboxWorld(I).min.z); });
        if (isFinite(mz)) { const goalZ = mz - 0.5; if (!S.benchInit) { benchZ = goalZ; S.benchInit = true; } benchZ += (goalZ - benchZ) * Math.min(1, dt * 3); benchG.position.set(C.t.x, C.t.y, benchZ); }
      }
      renderer.render(scene, camera);
      drawLabels();
      if (!STILL) requestAnimationFrame(frame);
    }

    load().then(() => {
      S.ready3d = true; $('stageMsg').hidden = true;
      enterStep(gi(S.i));
      if (!STILL) requestAnimationFrame(frame);
      window.__wiz.ready = true;
    }).catch((e) => { console.error(e); $('stageMsg').textContent = ui('no3d') + ' (' + e.message + ')'; $('stageMsg').dataset.err = '1'; });

    /* ---------- automation hooks: tests and the PDF still renderer ---------- */
    window.__wiz = {
      ready: false,
      steps: STEPS.length,
      flows: FLOWS,
      go: (i) => goTo(i),
      flow: (f) => { switchFlow(f); return S.flow; },
      /* render one still: step i, spec k (from steps.json "stills"), returns the file name */
      still: (i, k) => {
        cur = resolveStep(i); LAYOUT = cur.s.layout ? computeLayout(cur.s.layout) : {};
        const spec = (cur.s.stills || [{}])[k || 0] || {};
        const t = spec.t === 'end' || spec.t == null ? cur.dur : spec.t === 'start' ? 0 : +spec.t;
        if (spec.only) cur.show = new Set(spec.only);
        cur.hidden = new Set(spec.hide || []); cur.noAppear = spec.appear === false;
        if (spec.ghost) cur.ghost = new Set([...cur.ghost, ...spec.ghost]);
        itemsVisible(cur);
        if (spec.highlight) cur.hl = new Set(spec.highlight);
        lookStep(cur);
        clearOverlay(); buildMarks(cur.s.marks); if (spec.dims !== false) buildDims(cur.s);
        S.t = t; applyAll(t);
        cur.arrowMode = spec.arrows_mode || cur.s.arrows_mode || null;
        if (spec.arrows !== false) { buildArrows(cur, t); applyAll(t); }
        const cam = Object.assign({}, cur.s.camera || {}, spec.camera || {}); const saved = cur.s.camera; cur.s.camera = cam;
        const g = camGoalFor(cur, aspectNow(), spec.fit_all ? null : (spec.fit_t || [t, cur.dur])); C.t.copy(g.t); C.r = g.r; C.az = g.az; C.el = g.el; goal.t = goal.r = goal.az = goal.el = null; cur.s.camera = saved;
        applyAll(t);
        const sl = cur.s.labels; if (spec.labels !== undefined) cur.s.labels = spec.labels; makeLabels(i, !cur.s.still_callouts); cur.s.labels = sl;
        applyAll(t);
        frame(performance.now()); frame(performance.now());
        return spec.file || '';
      },
      /* one item alone, for the kit thumbnails */
      item: (iid, az, el) => {
        cur = resolveStep(0); cur.s = Object.assign({}, STEPS[0], { layout: null, camera: { az: az != null ? az : -55, el: el != null ? el : 28, fit: [iid, ...(ITEMS[iid].with || [])], margin: 1.12 }, labels: [] });
        LAYOUT = {}; Object.values(IT).forEach((I) => { I.g.visible = I.iid === iid || (ITEMS[iid].with || []).includes(I.iid); });
        cur.show = new Set([iid, ...(ITEMS[iid].with || [])]); cur.hl = new Set(cur.show); cur.tracks = []; cur.place = {}; cur.pose = null; cur.ghost = new Set();
        lookStep(cur); clearOverlay(); arrows = []; applyAll(0);
        const g = camGoalFor(cur, aspectNow()); C.t.copy(g.t); C.r = g.r; C.az = g.az; C.el = g.el; applyAll(0);
        labelsEl.textContent = ''; labs = [];
        frame(performance.now()); frame(performance.now());
      },
      state: () => ({ i: S.i, flow: S.flow, id: STEPS[gi(S.i)].id, n: nStep, t: S.t, dur: cur && cur.dur, lang: LANG, cam: { t: C.t.toArray().map(Math.round), r: Math.round(C.r), az: C.az, el: C.el }, W, H })
    };
  }
})();
