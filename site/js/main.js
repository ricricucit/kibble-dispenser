// Page wiring: viewer controls, parts list, shortcuts, full screen, photo lightbox.
const REPO = 'https://github.com/ricricucit/kibble-dispenser';
const $ = (s, el = document) => el.querySelector(s);
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const STATUS = { designed: 'Designed, ready to print', bought: 'Bought', reused: 'Reused', 'to design': 'Not designed yet' };

const stage = $('#stage');
const ui = {
  fs: $('#btn-fullscreen'), section: $('#btn-section'), explodeBtn: $('#btn-explode'), labels: $('#btn-labels'), reset: $('#btn-reset'),
  servo: $('#servo'), servoOut: $('#servo-out'), explode: $('#explode'), explodeOut: $('#explode-out'), dispense: $('#btn-dispense'),
  list: $('#parts-list'), count: $('#parts-count'), panel: $('#parts-panel'),
  info: $('#info'), infoBom: $('#info-bom'), infoName: $('#info-name'), infoMeta: $('#info-meta'), infoDesc: $('#info-desc'),
  infoFile: $('#info-file'), infoAll: $('#info-all'),
  loading: $('#loading'), loadingFill: $('#loading-fill'), tip: $('#tip'), toast: $('#toast'),
  fallback: $('#fallback'), fallbackText: $('#fallback-text'),
};

let viewer = null;
let toastTimer = 0;

function toast(msg, ms = 4200) {
  ui.toast.textContent = msg;
  ui.toast.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove('on'), ms);
}

function fail(msg) {
  ui.loading.hidden = true;
  ui.fallback.hidden = false;
  ui.fallbackText.textContent = msg;
  stage.classList.add('no-3d');
}

function meta(p) {
  if (p.material) return `${p.material}, ${p.spool} spool. ${STATUS[p.status] || p.status}.`;
  return `${STATUS[p.status] || p.status}.`;
}

/* ---------- parts list ---------- */
function buildList(data) {
  const all = [...data.parts, ...data.context].sort((a, b) => a.bom - b.bom);
  ui.count.textContent = `(${all.length})`;
  for (const p of all) {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.dataset.id = p.id;
    b.setAttribute('aria-pressed', 'false');
    b.innerHTML = `<span class="balloon static" aria-hidden="true">${p.bom}</span><span class="pl-name"></span>`
      + `<span class="pl-meta"></span>`;
    b.querySelector('.pl-name').textContent = p.name;
    const m = b.querySelector('.pl-meta');
    if (p.material) {
      m.innerHTML = `<span class="spool" style="--c:${p.colour}" aria-hidden="true"></span>`;
      m.append(`${p.material} ${p.spool}`);
    } else m.textContent = STATUS[p.status] || p.status;
    b.addEventListener('click', () => {
      if (!viewer) return;
      viewer.isolate(viewer.state.isolated === p.id ? null : p.id);
      // on phones the list sits below the model: bring the model back into view
      if (window.matchMedia('(max-width: 760px)').matches) scrollToModel();
    });
    li.append(b);
    ui.list.append(li);
  }
  return Object.fromEntries(all.map((p) => [p.id, p]));
}

function showInfo(p) {
  if (!p) { ui.info.hidden = true; return; }
  ui.info.hidden = false;
  ui.infoBom.textContent = p.bom;
  ui.infoName.textContent = p.name;
  ui.infoMeta.textContent = meta(p);
  ui.infoDesc.textContent = p.description;
  if (p.file) {
    ui.infoFile.hidden = false;
    ui.infoFile.href = `${REPO}/blob/main/hardware/stl/${p.id}.stl`;
  } else ui.infoFile.hidden = true;
}

/* ---------- full screen ---------- */
const fsElement = () => document.fullscreenElement || document.webkitFullscreenElement || null;

function setPseudo(on) {
  stage.classList.toggle('is-pseudo-fs', on);
  document.documentElement.classList.toggle('lock-scroll', on);
  syncFs();
}

function syncFs() {
  const on = fsElement() === stage || stage.classList.contains('is-pseudo-fs');
  ui.fs.setAttribute('aria-pressed', String(on));
  ui.fs.querySelector('.t').textContent = on ? 'Exit full screen' : 'Full screen';
  stage.classList.toggle('is-fs', on);
  requestAnimationFrame(updateInsets);
}

async function toggleFullscreen() {
  if (fsElement()) {
    try { await (document.exitFullscreen || document.webkitExitFullscreen).call(document); } catch { /* already left */ }
    return;
  }
  if (stage.classList.contains('is-pseudo-fs')) { setPseudo(false); return; }
  const req = stage.requestFullscreen || stage.webkitRequestFullscreen;
  if (!req) { setPseudo(true); return; }
  try {
    const r = req.call(stage, { navigationUI: 'hide' });
    if (r && typeof r.then === 'function') await r;
  } catch {
    setPseudo(true);
    toast('The browser did not allow full screen, so the model now fills the window. Press F or Esc to go back.');
  }
}

/* ---------- layout ---------- */
function updateInsets() {
  if (!viewer) return;
  const s = stage.querySelector('.canvas-wrap').getBoundingClientRect();
  const ins = { left: 0, right: 0, top: 0, bottom: 0 };
  for (const el of stage.querySelectorAll('[data-inset]')) {
    if (getComputedStyle(el).position !== 'absolute' || el.hidden) continue;
    const r = el.getBoundingClientRect();
    if (el.dataset.inset === 'left') ins.left = Math.max(ins.left, r.right - s.left + 8);
    if (el.dataset.inset === 'right') ins.right = Math.max(ins.right, s.right - r.left + 8);
    if (el.dataset.inset === 'top') ins.top = Math.max(ins.top, r.bottom - s.top + 8);
  }
  const tb = $('.toolbar', stage).getBoundingClientRect();
  ins.top = Math.max(ins.top, Math.min(tb.bottom - s.top, 80));
  viewer.setInsets(ins);
}

function sync(st) {
  ui.servo.value = Math.round(st.servo);
  const d = Math.round(st.servo);
  ui.servoOut.textContent = `${d}°, ${d === 0 ? 'closed' : d >= 180 ? 'open to the chute' : 'turning'}`;
  ui.explode.value = Math.round(st.explode * 100);
  ui.explodeOut.textContent = `${Math.round(st.explode * 100)} %`;
  ui.explodeBtn.setAttribute('aria-pressed', String(st.explode > 0.5));
  ui.section.setAttribute('aria-pressed', String(st.section));
  ui.labels.setAttribute('aria-pressed', String(st.callouts));
  for (const b of ui.list.querySelectorAll('button')) b.setAttribute('aria-pressed', String(b.dataset.id === st.isolated));
  stage.classList.toggle('is-isolated', !!st.isolated);
}

function scrollToModel() {
  const top = stage.getBoundingClientRect().top;
  if (Math.abs(top) > 40) window.scrollTo({ top: window.scrollY + top - 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  return new Promise((r) => setTimeout(r, reducedMotion.matches ? 0 : 450));
}

/* ---------- boot ---------- */
async function boot() {
  let data;
  try {
    const res = await fetch('assembly/assembly.json');
    if (!res.ok) throw new Error(res.status);
    data = await res.json();
  } catch {
    fail('The assembly data did not load, so the 3D model is not available. Reload the page to try again.');
    return;
  }
  const byId = buildList(data);
  if (window.matchMedia('(max-width: 760px)').matches) ui.panel.open = false;
  if (window.matchMedia('(max-width: 560px)').matches) $('#callouts').hidden = true;

  let Viewer;
  try {
    ({ Viewer } = await import('./viewer.js'));
    viewer = new Viewer({ stage, canvas: $('#view'), overlay: $('#callouts'), data, base: 'assembly/' });
  } catch (err) {
    console.error(err);
    fail('This browser could not start the 3D view (WebGL is off or unavailable). Try another browser, or turn on hardware acceleration.');
    return;
  }
  if (window.matchMedia('(max-width: 560px)').matches) viewer.setCallouts(false);

  viewer.addEventListener('progress', (e) => {
    const { done, total } = e.detail;
    ui.loadingFill.style.width = `${total ? (done / total) * 100 : 0}%`;
  });
  viewer.addEventListener('ready', (e) => {
    ui.loading.hidden = true;
    stage.classList.add('is-ready');
    setTimeout(() => stage.classList.add('has-interacted'), 9000);   // the gesture hint fades on its own
    if (e.detail.failed.length) toast(`Some parts did not load: ${e.detail.failed.join(', ')}. Reload the page to try again.`, 8000);
  });
  let shownInfo = null;
  viewer.addEventListener('state', (e) => {
    sync(e.detail);
    const id = e.detail.isolated;
    if (id !== shownInfo) { shownInfo = id; showInfo(id ? byId[id] : null); updateInsets(); }
  });
  viewer.addEventListener('pick', (e) => { if (e.detail.id) viewer.isolate(viewer.state.isolated === e.detail.id ? null : e.detail.id); });
  viewer.addEventListener('interact', () => stage.classList.add('has-interacted'), { once: true });
  viewer.addEventListener('hover', (e) => {
    const d = e.detail;
    ui.tip.hidden = !d.id;
    if (d.id) { ui.tip.textContent = d.name; ui.tip.style.transform = `translate(${d.x + 14}px, ${d.y + 16}px)`; }
  });
  viewer.addEventListener('busy', () => { ui.dispense.disabled = true; });
  viewer.addEventListener('idle', () => { ui.dispense.disabled = false; });

  ui.servo.addEventListener('input', () => viewer.setServo(+ui.servo.value));
  ui.explode.addEventListener('input', () => viewer.setExplode(+ui.explode.value / 100));
  ui.dispense.addEventListener('click', () => viewer.dispense());
  ui.section.addEventListener('click', () => viewer.setSection(!viewer.state.section));
  ui.explodeBtn.addEventListener('click', () => viewer.setExplode(viewer.state.explode > 0.5 ? 0 : 1, { animate: true, refit: true }));
  ui.labels.addEventListener('click', () => viewer.setCallouts(!viewer.state.callouts));
  ui.reset.addEventListener('click', () => viewer.reset());
  ui.fs.addEventListener('click', toggleFullscreen);
  ui.infoAll.addEventListener('click', () => viewer.isolate(null));
  document.addEventListener('fullscreenchange', syncFs);
  document.addEventListener('webkitfullscreenchange', syncFs);
  ui.panel.addEventListener('toggle', () => requestAnimationFrame(updateInsets));
  new ResizeObserver(updateInsets).observe(stage);

  // keyboard shortcuts, while the model is on screen
  let onScreen = true;
  new IntersectionObserver(([e]) => { onScreen = e.intersectionRatio > 0.25; }, { threshold: [0, 0.25, 0.5] }).observe(stage);
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.defaultPrevented) return;
    const t = e.target;
    if (t.isContentEditable || /^(TEXTAREA|SELECT)$/.test(t.tagName) || (t.tagName === 'INPUT' && t.type !== 'range')) return;
    if (e.key === 'Escape') {
      if (stage.classList.contains('is-pseudo-fs')) { setPseudo(false); return; }
      if (viewer.state.isolated && onScreen) viewer.isolate(null);
      return;
    }
    if (!onScreen && !stage.contains(t)) return;
    const k = e.key.toLowerCase();
    const act = { f: toggleFullscreen, s: () => ui.section.click(), x: () => ui.explodeBtn.click(), r: () => viewer.reset(), l: () => ui.labels.click() }[k];
    if (act) { e.preventDefault(); act(); }
  });

  // "Show in model" buttons in the sections below
  for (const b of document.querySelectorAll('[data-show], [data-action="dispense"]')) {
    b.addEventListener('click', async () => {
      await scrollToModel();
      if (b.dataset.action === 'dispense') { viewer.dispense(); return; }
      if (b.dataset.section === 'on') {
        viewer.isolate(null);
        viewer.setExplode(0);
        viewer.setSection(true);
        viewer.focus(b.dataset.show.split(' '));
        return;
      }
      viewer.isolate(b.dataset.show);
    });
  }

  updateInsets();
  viewer.frame({ animate: false, home: true });
  await viewer.loadParts();
  updateInsets();
  viewer.frame({ animate: false, home: true });
}

/* ---------- photos ---------- */
function initLightbox() {
  const dlg = $('#lightbox');
  if (!dlg || typeof dlg.showModal !== 'function') return;
  const img = $('#lightbox-img'), cap = $('#lightbox-cap');
  for (const a of document.querySelectorAll('a[data-lightbox]')) {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const caption = a.closest('figure').querySelector('figcaption').textContent;
      img.src = a.href;
      img.alt = caption;
      cap.textContent = caption;
      dlg.showModal();
    });
  }
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', () => { img.removeAttribute('src'); });
}

initLightbox();
boot();
