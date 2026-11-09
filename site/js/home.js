// Home and print-files pages: the print check list keeps its ticks in this browser (localStorage).
// Everything else on these pages works without JavaScript.
(function () {
  'use strict';
  const KEY = 'kd-v6-print-check';
  const boxes = Array.from(document.querySelectorAll('input[data-check]'));
  if (!boxes.length) return;
  const count = document.querySelector('[data-check-count]');
  let state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (_) { state = {}; }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) { /* storage blocked: ticks last for this visit */ }
  }
  function update() {
    if (count) count.textContent = String(boxes.filter((b) => b.checked).length);
  }

  boxes.forEach((b) => {
    b.checked = !!state[b.dataset.check];
    b.addEventListener('change', () => {
      if (b.checked) state[b.dataset.check] = 1; else delete state[b.dataset.check];
      save();
      update();
    });
  });
  const reset = document.querySelector('[data-check-reset]');
  if (reset) {
    reset.addEventListener('click', () => {
      state = {};
      boxes.forEach((b) => { b.checked = false; });
      save();
      update();
    });
  }
  update();
})();
