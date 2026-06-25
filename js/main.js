/* Jacana River Lodge — interactions */
(function () {
  'use strict';

  /* ---------- sticky header shrink ---------- */
  var header = document.getElementById('siteHeader');
  function onScroll() {
    if (!header) return;
    header.classList.toggle('shrink', window.scrollY > 40);
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
        nav.classList.remove('open');
        toggle.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
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

  /* ---------- year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
