/* Jacana River Lodge — interactions */
(function () {
  'use strict';

  /* ---------- sticky header shrink ---------- */
  var header = document.getElementById('siteHeader');
  function onScroll() {
    if (!header) return;
    header.classList.toggle('shrink', window.scrollY > 40);
    document.body.classList.toggle('scrolled', window.scrollY > 160);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- mobile nav ---------- */
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.classList.toggle('active', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        // on mobile the Activities link only expands its submenu
        if (a.classList.contains('nav-dd__toggle') && window.innerWidth <= 1060) return;
        nav.classList.remove('open');
        toggle.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- activities dropdown (mobile expand) ---------- */
  var dd = document.getElementById('navDd');
  if (dd) {
    var ddToggle = dd.querySelector('.nav-dd__toggle');
    ddToggle.addEventListener('click', function (e) {
      if (window.innerWidth <= 1060) {
        e.preventDefault();
        e.stopPropagation();
        dd.classList.toggle('open');
      }
    });
  }

  /* ---------- hero booking bar ---------- */
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parse(v) { var p = v.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function addDays(d, n) { var x = new Date(d.getTime()); x.setDate(x.getDate() + n); return x; }
  function longDate(v) { var d = parse(v); return d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear(); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  var bar = document.getElementById('bookBar');
  if (bar) {
    var wrap = document.getElementById('bookWrap');
    var arr = bar.elements.arrival;
    var dep = bar.elements.departure;
    var guests = bar.elements.guests;
    var go = document.getElementById('bbGo');
    var note = document.getElementById('bookBarNote');
    var msg = document.getElementById('bbMsg');
    var bbSlides = Array.prototype.slice.call(bar.querySelectorAll('.bb-slide'));
    var row = bar.querySelector('.bb-row');

    var today = new Date(); today.setHours(0, 0, 0, 0);
    arr.min = iso(today);
    arr.value = iso(addDays(today, 7));
    dep.value = iso(addDays(today, 9));

    var showDate = function (input) {
      var d = input.value ? parse(input.value) : null;
      input.parentNode.querySelector('[data-val]').textContent = d ? d.getDate() + ' ' + MONTHS[d.getMonth()] : '–';
    };
    var syncDates = function () {
      if (arr.value) {
        var minDep = addDays(parse(arr.value), 1);
        dep.min = iso(minDep);
        if (!dep.value || parse(dep.value) < minDep) dep.value = iso(addDays(parse(arr.value), 2));
      }
      showDate(arr); showDate(dep);
    };
    var setNote = function (text) {
      var open = bar.classList.contains('is-open');
      if (note) note.textContent = open ? '' : (text || '');
      if (open) { msg.classList.remove('is-ok'); msg.textContent = text || ''; }
    };
    var datesProblem = function () {
      if (!arr.value || !dep.value || parse(dep.value) <= parse(arr.value)) return 'Please choose your arrival and departure dates.';
      if (parse(arr.value) < today) return 'Your arrival date is in the past.';
      return '';
    };

    // the card is pinned to the bottom of its slot on wide screens, so the slot
    // needs the collapsed card's height
    var measure = function () {
      var cs = getComputedStyle(bar);
      wrap.style.setProperty('--bb-h', (row.offsetHeight + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom)) + 'px');
    };
    measure();
    window.addEventListener('resize', measure);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);

    var setOpen = function (open) {
      bar.classList.toggle('is-open', open);
      go.setAttribute('aria-expanded', open ? 'true' : 'false');
      bbSlides.forEach(function (sl) { sl.inert = !open; });
      if (note) note.textContent = '';
      if (open) setTimeout(function () { bar.elements.name.focus({ preventScroll: true }); }, 320);
      else go.focus({ preventScroll: true });
    };

    [arr, dep].forEach(function (input) {
      input.addEventListener('click', function () { try { input.showPicker(); } catch (err) { /* older browsers open on focus */ } });
      input.addEventListener('change', function () { setNote(''); syncDates(); });
    });
    guests.addEventListener('change', function () { bar.querySelector('[data-guests]').textContent = guests.value; });

    go.addEventListener('click', function () {
      var problem = datesProblem();
      if (problem) { setNote(problem); return; }
      setOpen(true);
    });
    document.getElementById('bbClose').addEventListener('click', function () { setOpen(false); });
    bar.addEventListener('keydown', function (e) { if (e.key === 'Escape' && bar.classList.contains('is-open')) setOpen(false); });

    bar.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!bar.classList.contains('is-open')) { go.click(); return; } // Enter pressed in the collapsed bar
      var problem = datesProblem();
      if (problem) { setNote(problem); return; }
      var d = new FormData(bar);
      var name = (d.get('name') || '').trim();
      var email = (d.get('email') || '').trim();
      var phone = (d.get('phone') || '').trim();
      var validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      if (!name || (!validEmail && !phone)) { setNote('Please add your name and an email or phone number.'); return; }
      msg.classList.add('is-ok');
      msg.textContent = 'Thank you, ' + name + '! We’ll be in touch shortly about ' +
        longDate(arr.value) + ' – ' + longDate(dep.value) + ' (' + plural(+guests.value, 'guest', 'guests') + ').';
      ['name', 'phone', 'email'].forEach(function (n) { bar.elements[n].value = ''; });
    });

    // "Enquire" in the nav opens the card instead of leaving the page
    document.querySelectorAll('[data-enquire]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        setOpen(true);
      });
    });
    if (location.hash === '#enquire') {
      setOpen(true);
      history.replaceState(null, '', location.pathname + location.search);
    }
    syncDates();
  }

  /* ---------- hero slider ---------- */
  var slides = Array.prototype.slice.call(document.querySelectorAll('.hero__slide'));
  var dotsWrap = document.getElementById('heroDots');
  var heroIndex = 0;
  var heroTimer;
  if (slides.length && dotsWrap) {
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      if (i === 0) b.classList.add('active');
      b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      b.addEventListener('click', function () { goHero(i); resetHero(); });
      dotsWrap.appendChild(b);
    });
    var dots = Array.prototype.slice.call(dotsWrap.children);

    function goHero(i) {
      slides[heroIndex].classList.remove('active');
      dots[heroIndex].classList.remove('active');
      heroIndex = (i + slides.length) % slides.length;
      slides[heroIndex].classList.add('active');
      dots[heroIndex].classList.add('active');
    }
    function nextHero() { goHero(heroIndex + 1); }
    function resetHero() { clearInterval(heroTimer); heroTimer = setInterval(nextHero, 6000); }
    resetHero();
  }

  /* ---------- testimonials slider ---------- */
  var tSlides = Array.prototype.slice.call(document.querySelectorAll('.testi__slide'));
  var tIndex = 0, tTimer;
  function goTesti(i) {
    tSlides[tIndex].classList.remove('active');
    tIndex = (i + tSlides.length) % tSlides.length;
    tSlides[tIndex].classList.add('active');
  }
  function resetTesti() { clearInterval(tTimer); tTimer = setInterval(function () { goTesti(tIndex + 1); }, 7000); }
  var tPrev = document.getElementById('testiPrev');
  var tNext = document.getElementById('testiNext');
  if (tSlides.length && tPrev && tNext) {
    tPrev.addEventListener('click', function () { goTesti(tIndex - 1); resetTesti(); });
    tNext.addEventListener('click', function () { goTesti(tIndex + 1); resetTesti(); });
    resetTesti();
  }

  /* ---------- newsletter (front-end validation only) ---------- */
  var nlForm = document.getElementById('nlForm');
  var nlMsg = document.getElementById('nlMsg');
  if (nlForm) {
    nlForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(nlForm);
      var name = (data.get('name') || '').trim();
      var email = (data.get('email') || '').trim();
      var validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      if (!name || !validEmail) {
        nlMsg.style.color = '#ffe2d6';
        nlMsg.textContent = 'Please enter your name and a valid email address.';
        return;
      }
      nlMsg.style.color = '#fff';
      nlMsg.textContent = 'Thank you, ' + name + '! You are on the list — watch your inbox for bush inspiration.';
      nlForm.reset();
    });
  }

  /* ---------- scroll reveal ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- gallery lightbox ---------- */
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightboxImg');
  var galleryImgs = Array.prototype.slice.call(document.querySelectorAll('#galleryGrid img'));
  var lbIndex = 0;
  function showLb(i) {
    lbIndex = (i + galleryImgs.length) % galleryImgs.length;
    var src = galleryImgs[lbIndex].getAttribute('src');
    lbImg.setAttribute('src', src);
    lbImg.setAttribute('alt', galleryImgs[lbIndex].getAttribute('alt') || '');
  }
  function openLb(i) { showLb(i); lb.classList.add('open'); lb.setAttribute('aria-hidden', 'false'); document.body.style.overflow = 'hidden'; }
  function closeLb() { lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; }
  if (lb && galleryImgs.length) {
    galleryImgs.forEach(function (img, i) {
      img.addEventListener('click', function () { openLb(i); });
    });
    document.getElementById('lightboxClose').addEventListener('click', closeLb);
    document.getElementById('lightboxNext').addEventListener('click', function () { showLb(lbIndex + 1); });
    document.getElementById('lightboxPrev').addEventListener('click', function () { showLb(lbIndex - 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') closeLb();
      else if (e.key === 'ArrowRight') showLb(lbIndex + 1);
      else if (e.key === 'ArrowLeft') showLb(lbIndex - 1);
    });
  }

  /* ---------- google reviews carousel ---------- */
  var rTrack = document.getElementById('reviewsTrack');
  if (rTrack) {
    var rPrev = document.getElementById('reviewsPrev');
    var rNext = document.getElementById('reviewsNext');
    var rAuto;
    function cardStep() {
      var c = rTrack.querySelector('.review-card');
      if (!c) return 320;
      var gap = parseInt(getComputedStyle(rTrack).gap) || 24;
      return c.offsetWidth + gap;
    }
    function rScroll(dir) { rTrack.scrollBy({ left: dir * cardStep(), behavior: 'smooth' }); }
    function autoAdvance() {
      var maxScroll = rTrack.scrollWidth - rTrack.clientWidth - 4;
      if (rTrack.scrollLeft >= maxScroll) rTrack.scrollTo({ left: 0, behavior: 'smooth' });
      else rScroll(1);
    }
    function resetAuto() { clearInterval(rAuto); rAuto = setInterval(autoAdvance, 4500); }
    if (rPrev) rPrev.addEventListener('click', function () { rScroll(-1); resetAuto(); });
    if (rNext) rNext.addEventListener('click', function () { rScroll(1); resetAuto(); });
    rTrack.addEventListener('mouseenter', function () { clearInterval(rAuto); });
    rTrack.addEventListener('mouseleave', resetAuto);
    resetAuto();
  }

  /* ---------- year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
