/* AFP blog tools: keep the day/night choice across pages, smooth back-to-top. */
(function () {
  var KEY = 'afp-dark';
  var box = document.getElementById('afp-dark');
  if (box) {
    try { if (localStorage.getItem(KEY) === '1') { box.checked = true; } } catch (e) {}
    box.addEventListener('change', function () {
      try { localStorage.setItem(KEY, box.checked ? '1' : '0'); } catch (e) {}
      var lbl = document.querySelector('.afp-theme');
      if (lbl) { lbl.setAttribute('aria-label', box.checked ? 'حالت روز' : 'حالت شب'); }
    });
  }
  var bt = document.querySelector('.afp-backtop');
  if (bt) {
    bt.addEventListener('click', function (ev) {
      ev.preventDefault();
      try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); }
    });
  }
})();
