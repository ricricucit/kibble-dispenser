// Language switch for the static multilingual pages (English, Italian, German).
// The page carries every text once per language (elements with data-l="en|it|de"); CSS shows the
// language in <html data-lang>. Order: ?lang= in the URL, the visitor's last choice, the browser, English.
// Without JavaScript the page stays in English. The 3D viewer uses the same storage key.
(function () {
  'use strict';
  const LANGS = ['en', 'it', 'de'];
  const KEY = 'kd-lang';
  const root = document.documentElement;

  function pick() {
    let q = null;
    try { q = new URLSearchParams(location.search).get('lang'); } catch (_) { /* old browser */ }
    if (q && LANGS.includes(q.toLowerCase())) return q.toLowerCase();
    try { const s = localStorage.getItem(KEY); if (LANGS.includes(s)) return s; } catch (_) { /* storage blocked */ }
    for (const l of navigator.languages || [navigator.language || '']) {
      const b = String(l).slice(0, 2).toLowerCase();
      if (LANGS.includes(b)) return b;
    }
    return 'en';
  }

  function apply(lang) {
    root.dataset.lang = lang;
    root.lang = lang;
    const title = root.getAttribute('data-title-' + lang);
    if (title) document.title = title;
    document.querySelectorAll('[data-set-lang]').forEach((b) => {
      b.setAttribute('aria-pressed', String(b.dataset.setLang === lang));
    });
    // carry the language to the other multilingual pages
    document.querySelectorAll('a[data-keep-lang]').forEach((a) => {
      try { const u = new URL(a.getAttribute('href'), location.href); u.searchParams.set('lang', lang); a.href = u.href; } catch (_) { /* keep href */ }
    });
  }

  function choose(lang) {
    apply(lang);
    try { localStorage.setItem(KEY, lang); } catch (_) { /* storage blocked */ }
    try { const u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState(null, '', u); } catch (_) { /* file:// */ }
  }

  apply(pick());
  document.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest('[data-set-lang]');
    if (b) choose(b.dataset.setLang);
  });
})();
