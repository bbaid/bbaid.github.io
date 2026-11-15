/* Portfolio interactions: theme toggle, project filter, lightbox, scroll reveal. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');

  /* ── Theme toggle ── */
  var toggle = document.getElementById('themeToggle');
  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) { /* storage unavailable */ }
    });
  }

  /* ── Project filter ── */
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('#projectGrid .card'));
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var f = chip.dataset.filter;
      chips.forEach(function (c) {
        var on = c === chip;
        c.classList.toggle('is-active', on);
        c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      cards.forEach(function (card) {
        var cats = (card.dataset.cat || '').split(' ');
        card.hidden = !(f === 'all' || cats.indexOf(f) !== -1);
        if (!card.hidden) card.classList.add('is-in');
      });
    });
  });

  /* ── Lightbox ── */
  var dialog = document.getElementById('lightbox');
  var img = document.getElementById('lbImg');
  var caption = document.getElementById('lbCaption');
  var count = document.getElementById('lbCount');
  var prev = document.getElementById('lbPrev');
  var next = document.getElementById('lbNext');
  var closeBtn = document.getElementById('lbClose');
  var triggers = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
  var items = [];
  var index = 0;
  var opener = null;

  function groupItems(group) {
    var seen = {};
    var list = [];
    triggers.forEach(function (t) {
      if (t.dataset.group !== group || seen[t.dataset.full]) return;
      seen[t.dataset.full] = true;
      var thumb = t.querySelector('img');
      list.push({ full: t.dataset.full, caption: t.dataset.caption || '', alt: thumb ? thumb.alt : (t.dataset.caption || '') });
    });
    return list;
  }

  function show(i) {
    index = (i + items.length) % items.length;
    var item = items[index];
    img.src = item.full;
    img.alt = item.alt;
    caption.textContent = item.caption;
    var many = items.length > 1;
    prev.hidden = next.hidden = !many;
    count.textContent = many ? (index + 1) + ' / ' + items.length : '';
  }

  function open(trigger) {
    if (!dialog || typeof dialog.showModal !== 'function') {
      window.open(trigger.dataset.full, '_blank', 'noopener');
      return;
    }
    opener = trigger;
    items = groupItems(trigger.dataset.group);
    var start = 0;
    items.forEach(function (it, i) { if (it.full === trigger.dataset.full) start = i; });
    show(start);
    dialog.showModal();
    closeBtn.focus();
  }

  triggers.forEach(function (t) {
    t.addEventListener('click', function () { open(t); });
  });

  if (dialog) {
    closeBtn.addEventListener('click', function () { dialog.close(); });
    prev.addEventListener('click', function () { show(index - 1); });
    next.addEventListener('click', function () { show(index + 1); });
    dialog.addEventListener('click', function (e) {
      /* Close when the dark area around the image is clicked. */
      if (e.target === dialog || e.target.classList.contains('lb-stage')) dialog.close();
    });
    dialog.addEventListener('keydown', function (e) {
      if (items.length < 2) return;
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
    dialog.addEventListener('close', function () {
      img.removeAttribute('src');
      if (opener) opener.focus();
    });
  }

  /* ── Scroll reveal ── */
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ── Current section in the nav ── */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a'));
  var sections = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });
  if ('IntersectionObserver' in window) {
    var navIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a, i) { a.classList.toggle('is-current', sections[i] === entry.target); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { if (s) navIo.observe(s); });
  }
})();
