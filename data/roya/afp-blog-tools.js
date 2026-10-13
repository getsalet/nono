/* AFP tools v2: accessible theme button; never focus the hidden footer checkbox. */
(function () {
  'use strict';
  var KEY = 'afp-dark';
  var box = document.getElementById('afp-dark');
  var button = document.querySelector('.afp-theme');
  function sync() {
    if (!box || !button) return;
    button.setAttribute('aria-label', box.checked ? 'حالت روز' : 'حالت شب');
    button.setAttribute('aria-pressed', box.checked ? 'true' : 'false');
    try { localStorage.setItem(KEY, box.checked ? '1' : '0'); } catch (e) {}
  }
  if (box) {
    try { box.checked = localStorage.getItem(KEY) === '1'; } catch (e) {}
    sync();
    box.addEventListener('change', sync);
  }
  if (box && button) {
    button.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      box.checked = !box.checked;
      sync();
    });
  }
  var backtop = document.querySelector('.afp-backtop');
  if (backtop) backtop.addEventListener('click', function (ev) {
    ev.preventDefault();
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try { window.scrollTo({ top: 0, behavior: reduce ? 'instant' : 'smooth' }); }
    catch (e) { window.scrollTo(0, 0); }
  });
})();
