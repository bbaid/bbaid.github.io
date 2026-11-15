/* Portfolio interactions: theme toggle, project filter, map viewer, atlas book, scroll reveal. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');

  function toArray(list) { return Array.prototype.slice.call(list); }

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
  var chips = toArray(document.querySelectorAll('.chip'));
  var cards = toArray(document.querySelectorAll('#projectGrid .card'));
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

  /* ── Map viewer (lightbox) ── */
  var dialog = document.getElementById('lightbox');
  var img = document.getElementById('lbImg');
  var caption = document.getElementById('lbCaption');
  var count = document.getElementById('lbCount');
  var prev = document.getElementById('lbPrev');
  var next = document.getElementById('lbNext');
  var closeBtn = document.getElementById('lbClose');
  var triggers = toArray(document.querySelectorAll('[data-lightbox]'));
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

  /* Open the viewer on a list of {full, caption, alt}, starting at `start`. */
  function openViewer(list, start, from) {
    if (!list.length) return;
    if (!dialog || typeof dialog.showModal !== 'function') {
      window.open(list[start].full, '_blank', 'noopener');
      return;
    }
    opener = from || null;
    items = list;
    show(start);
    dialog.showModal();
    closeBtn.focus();
  }

  triggers.forEach(function (t) {
    t.addEventListener('click', function () {
      var list = groupItems(t.dataset.group);
      var start = 0;
      list.forEach(function (it, i) { if (it.full === t.dataset.full) start = i; });
      openViewer(list, start, t);
    });
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

  /* ── Atlas book ──
     Each <li> in .book-pages is one page. On wide screens two pages share a
     leaf (front and back) and the book opens as a spread; on narrow screens
     every page is its own leaf. `pos` counts the leaves already turned. */
  var TURN_MS = 900;

  function initBook(book) {
    var list = book.querySelector('.book-pages');
    if (!list) return;
    var wrap = book.closest('.book-wrap') || book.parentNode;
    var label = wrap.querySelector('[data-book-label]');
    var btnPrev = wrap.querySelector('[data-book-prev]');
    var btnNext = wrap.querySelector('[data-book-next]');
    var btnZoom = wrap.querySelector('[data-book-zoom]');
    var narrow = window.matchMedia('(max-width: 720px)');

    /* Turn the list items into page faces. */
    var faces = toArray(list.children).map(function (li) {
      var face = document.createElement('div');
      face.className = li.className;
      face.dataset.title = li.dataset.title || '';
      if (li.dataset.full) face.dataset.full = li.dataset.full;
      if (li.dataset.caption) face.dataset.caption = li.dataset.caption;
      while (li.firstChild) face.appendChild(li.firstChild);
      var pic = face.querySelector('img');
      if (pic) {
        /* Hold back images until their leaf is near, so a long atlas stays light. */
        pic.draggable = false;
        if (!(pic.complete && pic.naturalWidth)) {
          pic.dataset.src = pic.getAttribute('src');
          pic.removeAttribute('src');
        }
        pic.removeAttribute('loading');
      }
      return face;
    });

    var stage = document.createElement('div');
    stage.className = 'book-stage';
    list.parentNode.replaceChild(stage, list);

    var leaves = [];
    var mode = '';
    var pos = 0;

    function maxPos() { return mode === 'spread' ? leaves.length : leaves.length - 1; }

    function settledZ(i) { return i < pos ? i + 1 : leaves.length - i; }

    function visibleFaces() {
      var out = [];
      if (mode === 'spread') {
        if (pos > 0) out.push(leaves[pos - 1].lastChild);
        if (pos < leaves.length) out.push(leaves[pos].firstChild);
      } else {
        out.push(leaves[pos].firstChild);
      }
      return out;
    }

    function loadNear() {
      for (var i = Math.max(0, pos - 2); i < Math.min(leaves.length, pos + 3); i++) {
        toArray(leaves[i].querySelectorAll('img[data-src]')).forEach(function (pic) {
          pic.src = pic.dataset.src;
          pic.removeAttribute('data-src');
        });
      }
    }

    function render() {
      leaves.forEach(function (leaf, i) {
        leaf.classList.toggle('is-flipped', i < pos);
        leaf.classList.toggle('is-next', i === pos);
        leaf.classList.toggle('is-prev', i === pos - 1);
        if (!leaf.classList.contains('is-turning')) leaf.style.zIndex = settledZ(i);
      });
      book.dataset.state = pos === 0 ? 'front' : (mode === 'spread' && pos === leaves.length ? 'back' : 'open');
      if (label) {
        label.textContent = visibleFaces().map(function (f) { return f.dataset.title; }).filter(Boolean).join('  —  ');
      }
      if (btnPrev) btnPrev.disabled = pos === 0;
      if (btnNext) btnNext.disabled = pos === maxPos();
      loadNear();
    }

    function layout() {
      var newMode = narrow.matches ? 'single' : 'spread';
      if (newMode === mode) return;
      /* Keep the reader on the same page across the change. */
      if (mode === 'spread') pos = pos === 0 ? 0 : 2 * pos - 1;
      else if (mode === 'single') pos = Math.ceil(pos / 2);
      mode = newMode;
      book.dataset.mode = mode;
      stage.textContent = '';
      leaves = [];
      var per = mode === 'spread' ? 2 : 1;
      for (var i = 0; i < faces.length; i += per) {
        var leaf = document.createElement('div');
        leaf.className = 'leaf';
        var front = faces[i];
        front.classList.remove('back');
        front.classList.add('face', 'front');
        leaf.appendChild(front);
        if (per === 2) {
          var back = faces[i + 1] || document.createElement('div');
          back.classList.remove('front');
          back.classList.add('face', 'back');
          leaf.appendChild(back);
        }
        stage.appendChild(leaf);
        leaves.push(leaf);
      }
      pos = Math.min(pos, maxPos());
      render();
    }

    function go(dir) {
      var target = Math.max(0, Math.min(maxPos(), pos + dir));
      if (target === pos) return;
      var i = dir > 0 ? pos : pos - 1;
      var leaf = leaves[i];
      pos = target;
      /* The turning leaf rides above both stacks until it lands. */
      leaf.classList.add('is-turning');
      leaf.style.zIndex = 100 + (dir > 0 ? i : leaves.length - i);
      render();
      clearTimeout(leaf.turnTimer);
      leaf.turnTimer = setTimeout(function () {
        leaf.classList.remove('is-turning');
        var at = leaves.indexOf(leaf);
        if (at !== -1) leaf.style.zIndex = settledZ(at);
      }, TURN_MS + 60);
    }

    /* Click the right-hand side to go forward, the left-hand side to go back. */
    var swiped = false;
    stage.addEventListener('click', function (e) {
      if (swiped) { swiped = false; return; }
      var box = book.getBoundingClientRect();
      var split = mode === 'spread' ? 0.5 : 0.3;
      go(e.clientX - box.left > box.width * split ? 1 : -1);
    });

    var downX = null;
    stage.addEventListener('pointerdown', function (e) { downX = e.clientX; swiped = false; });
    stage.addEventListener('pointerup', function (e) {
      if (downX === null) return;
      var dx = e.clientX - downX;
      downX = null;
      if (Math.abs(dx) < 40) return;
      swiped = true;
      go(dx < 0 ? 1 : -1);
    });
    stage.addEventListener('pointercancel', function () { downX = null; });

    book.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { go(1); e.preventDefault(); }
      if (e.key === 'ArrowLeft') { go(-1); e.preventDefault(); }
    });
    if (btnPrev) btnPrev.addEventListener('click', function () { go(-1); });
    if (btnNext) btnNext.addEventListener('click', function () { go(1); });

    if (btnZoom) {
      btnZoom.addEventListener('click', function () {
        var maps = faces.filter(function (f) { return f.dataset.full; });
        var list = maps.map(function (f) {
          var pic = f.querySelector('img');
          return { full: f.dataset.full, caption: f.dataset.caption || f.dataset.title, alt: pic ? pic.alt : f.dataset.title };
        });
        /* Start at the sheet that is open, or else at the next one. */
        var shown = visibleFaces().filter(function (f) { return f.dataset.full; })[0];
        var start = shown ? maps.indexOf(shown) : 0;
        if (!shown) {
          var first = faces.indexOf(visibleFaces()[0]);
          maps.some(function (f, i) { if (faces.indexOf(f) >= first) { start = i; return true; } return false; });
        }
        openViewer(list, start, btnZoom);
      });
    }

    if (narrow.addEventListener) narrow.addEventListener('change', layout);
    else if (narrow.addListener) narrow.addListener(layout);
    layout();
  }

  toArray(document.querySelectorAll('.book')).forEach(initBook);

  /* ── Scroll reveal ── */
  var reveals = toArray(document.querySelectorAll('.reveal'));
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
  var links = toArray(document.querySelectorAll('.nav a'));
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
