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

  /* ---------- silo dropdowns (Stay / Activities / Mjejane Reserve) ---------- */
  // desktop: open on hover; mobile: the top link only expands its submenu
  // (each submenu starts with a link to its hub page). One open at a time.
  var dds = Array.prototype.slice.call(document.querySelectorAll('.nav-dd'));
  dds.forEach(function (dd) {
    var ddToggle = dd.querySelector('.nav-dd__toggle');
    if (!ddToggle) return;
    ddToggle.addEventListener('click', function (e) {
      if (window.innerWidth <= 1060) {
        e.preventDefault();
        e.stopPropagation();
        var open = !dd.classList.contains('open');
        dds.forEach(function (o) {
          o.classList.remove('open');
          var t = o.querySelector('.nav-dd__toggle');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
        dd.classList.toggle('open', open);
        ddToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
    });
    dd.addEventListener('mouseenter', function () {
      ddToggle.setAttribute('aria-expanded', 'true');
      // point the panel's notch at this menu item
      var menu = dd.querySelector('.nav-dd__menu');
      if (menu && window.innerWidth > 1060) {
        var r = ddToggle.getBoundingClientRect(), m = menu.getBoundingClientRect();
        menu.style.setProperty('--notch', Math.round(r.left + r.width / 2 - m.left) + 'px');
      }
    });
    dd.addEventListener('mouseleave', function () { ddToggle.setAttribute('aria-expanded', 'false'); });
  });

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
      // TODO(back-end): submit to the CRM/NightsBridge first. The success URL must be a full page load:
      // the live site's Google Ads conversions are page views of these thank-you pages.
      window.location.href = '/thank-you-for-your-booking-enquiry/';
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

  /* ---------- hero photo slideshow: crossfade + slow zoom, every 3s ---------- */
  var heroPics = Array.prototype.slice.call(document.querySelectorAll('#heroSlides .hero__img'));
  if (heroPics.length > 1) {
    var HERO_MS = 3000, FADE_MS = 1200;
    var heroAt = 0, heroTimer = null;
    // only the first photo loads up front; the rest load once the page is ready
    var loadRest = function () {
      heroPics.forEach(function (img) { if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); } });
    };
    if (document.readyState === 'complete') loadRest(); else window.addEventListener('load', loadRest);

    var showHero = function (i) {
      var prev = heroPics[heroAt], next = heroPics[i];
      if (next === prev || !next.complete || !next.naturalWidth) return; // skip a photo that hasn't loaded yet
      prev.classList.remove('is-active');
      prev.classList.add('is-prev');            // stays fully visible underneath while the next fades in
      next.classList.add('is-active');
      heroAt = i;
      setTimeout(function () { prev.classList.remove('is-prev'); }, FADE_MS + 100);
    };
    var heroTick = function () { showHero((heroAt + 1) % heroPics.length); };
    var heroPlay = function () { clearInterval(heroTimer); heroTimer = setInterval(heroTick, HERO_MS); };
    heroPlay();
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) clearInterval(heroTimer); else heroPlay();
    });
  }

  /* ---------- explore: expanding activity cards ---------- */
  var xpTrack = document.getElementById('xpTrack');
  if (xpTrack) {
    var xCards = Array.prototype.slice.call(xpTrack.querySelectorAll('.xcard'));
    var xPrev = document.querySelector('.xp__nav--prev');
    var xNext = document.querySelector('.xp__nav--next');
    var phone = window.matchMedia('(max-width: 760px)');
    var lastPointer = 'mouse';
    var openCard = function (card) {
      xCards.forEach(function (c) { c.classList.toggle('is-open', c === card); });
    };
    xCards.forEach(function (card) {
      card.addEventListener('mouseenter', function () { openCard(card); });
      card.addEventListener('focus', function () { openCard(card); });
      card.addEventListener('pointerdown', function (e) { lastPointer = e.pointerType; });
      // on touch screens the first tap opens a closed card, the second follows the link
      card.addEventListener('click', function (e) {
        if (!phone.matches && lastPointer !== 'mouse' && !card.classList.contains('is-open')) {
          e.preventDefault();
          openCard(card);
        }
      });
    });
    var syncNav = function () {
      var max = xpTrack.scrollWidth - xpTrack.clientWidth - 2;
      xPrev.hidden = xpTrack.scrollLeft <= 2;
      xNext.hidden = xpTrack.scrollLeft >= max;
    };
    var step = function (dir) { xpTrack.scrollBy({ left: dir * (xCards[0].offsetWidth + 14) * 2, behavior: 'smooth' }); };
    xPrev.addEventListener('click', function () { step(-1); });
    xNext.addEventListener('click', function () { step(1); });
    xpTrack.addEventListener('scroll', syncNav, { passive: true });
    window.addEventListener('resize', syncNav);
    xCards.forEach(function (c) { c.addEventListener('transitionend', syncNav); });
    syncNav();
  }

  /* ---------- lodge video: load YouTube only when asked ---------- */
  var xpVideo = document.getElementById('xpVideo');
  if (xpVideo) {
    xpVideo.querySelector('.xp-video__poster').addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + xpVideo.getAttribute('data-yt') + '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
      f.title = 'Jacana River Lodge video';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.setAttribute('allowfullscreen', '');
      xpVideo.innerHTML = '';
      xpVideo.appendChild(f);
      f.focus();
    });
  }

  /* ---------- FAQ: one open at a time, smooth height animation ---------- */
  var faqItems = Array.prototype.slice.call(document.querySelectorAll('.faq__item'));
  if (faqItems.length) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var animate = function (item, open) {
      var panel = item.querySelector('.faq__a');
      if (item._anim) item._anim.cancel();
      if (reduce || !panel.animate) { item.open = open; return; }
      if (open) {
        item.open = true;
        var cs = getComputedStyle(panel), h = panel.offsetHeight;
        item._anim = panel.animate([{ height: '0px', paddingTop: '0px', paddingBottom: '0px', opacity: 0 },
          { height: h + 'px', paddingTop: cs.paddingTop, paddingBottom: cs.paddingBottom, opacity: 1 }],
          { duration: 380, easing: 'cubic-bezier(.22,.61,.36,1)' });
      } else {
        var cs2 = getComputedStyle(panel), from = panel.offsetHeight;
        item._anim = panel.animate([{ height: from + 'px', paddingTop: cs2.paddingTop, paddingBottom: cs2.paddingBottom, opacity: 1 },
          { height: '0px', paddingTop: '0px', paddingBottom: '0px', opacity: 0 }],
          { duration: 300, easing: 'cubic-bezier(.22,.61,.36,1)' });
        item._anim.onfinish = function () { item.open = false; item._anim = null; };
      }
    };
    faqItems.forEach(function (item) {
      item.querySelector('summary').addEventListener('click', function (e) {
        e.preventDefault();
        var opening = !item.open || (item._anim && item._anim.onfinish);
        faqItems.forEach(function (other) { if (other !== item && other.open) animate(other, false); });
        animate(item, opening);
      });
    });
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

  /* ---------- enquiry form below the FAQ (front-end validation only) ---------- */
  var nlForm = document.getElementById('nlForm');
  var nlMsg = document.getElementById('nlMsg');
  if (nlForm) {
    nlForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(nlForm);
      var name = (data.get('name') || '').trim();
      var email = (data.get('email') || '').trim();
      var validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      var phoneNo = (data.get('phone') || '').trim();
      if (!nlForm.elements.consent.checked) {
        nlMsg.style.color = '#ffe2d6';
        nlMsg.textContent = 'Please tick the consent box so we can respond to your enquiry.';
        return;
      }
      if (!name || phoneNo.replace(/\D/g, '').length < 9 || !validEmail) {
        nlMsg.style.color = '#ffe2d6';
        nlMsg.textContent = 'Please enter your full name, phone number and a valid email address.';
        return;
      }
      // TODO(back-end): submit to the CRM first, then go to the success page (full page load for conversions).
      window.location.href = '/thank-you/';
    });
  }

  /* ---------- scroll reveal ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0, rootMargin: '0px 0px -40px 0px' }); // threshold 0: very tall blocks never reach a % of the screen on phones
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- gallery: scroll-driven photo wall + blur-in heading ---------- */
  var agal = document.getElementById('agalScroll');
  if (agal && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var agalTick = false;
    // progress 0 when the wrapper's top reaches the top of the screen, 1 when its bottom reaches the bottom
    var agalUpdate = function () {
      agalTick = false;
      var r = agal.getBoundingClientRect();
      var span = r.height - window.innerHeight;
      var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1;
      agal.style.setProperty('--p', p.toFixed(4));
    };
    var agalOnScroll = function () { if (!agalTick) { agalTick = true; requestAnimationFrame(agalUpdate); } };
    window.addEventListener('scroll', agalOnScroll, { passive: true });
    window.addEventListener('resize', agalOnScroll);
    agalUpdate();
  }
  var agalHead = document.querySelector('.agal__head');
  if (agalHead) {
    if ('IntersectionObserver' in window) {
      var agalIo = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { agalHead.classList.add('is-in'); agalIo.disconnect(); } });
      }, { threshold: 0.25 });
      agalIo.observe(agalHead);
    } else { agalHead.classList.add('is-in'); }
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
      // homepage tiles are buttons (keyboard friendly); the gallery page binds the image itself
      (img.closest('button') || img).addEventListener('click', function () { openLb(i); });
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
  // long reviews: clamp to six lines with a "Read more" toggle (full text stays in the page)
  Array.prototype.forEach.call(document.querySelectorAll('.review-card__text'), function (t) {
    if (t.textContent.length < 260) return;
    t.classList.add('is-clamped');
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'review-card__more'; b.textContent = 'Read more';
    b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', function () {
      var open = t.classList.toggle('is-clamped') === false;
      b.textContent = open ? 'Show less' : 'Read more';
      b.setAttribute('aria-expanded', String(open));
    });
    t.parentNode.appendChild(b);
  });
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
