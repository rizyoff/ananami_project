/* =========================================================
   main.js — Navbar, smooth scroll, scrollspy
   ========================================================= */
(function () {
  'use strict';

  /* ---------- Mobile Nav Toggle ---------- */
  var navToggle = document.getElementById('navToggle');
  var siteNav = document.getElementById('siteNav');
  var navBackdrop = document.getElementById('navBackdrop');

  function closeNav() {
    if (siteNav) siteNav.classList.remove('is-open');
    if (navToggle) {
      navToggle.classList.remove('is-active');
      navToggle.setAttribute('aria-expanded', 'false');
    }
    if (navBackdrop) navBackdrop.classList.remove('is-visible');
    document.body.classList.remove('nav-open');
  }

  function openNav() {
    if (siteNav) siteNav.classList.add('is-open');
    if (navToggle) {
      navToggle.classList.add('is-active');
      navToggle.setAttribute('aria-expanded', 'true');
    }
    if (navBackdrop) navBackdrop.classList.add('is-visible');
    document.body.classList.add('nav-open');
  }

  if (navToggle) {
    navToggle.addEventListener('click', function () {
      if (siteNav && siteNav.classList.contains('is-open')) {
        closeNav();
      } else {
        openNav();
      }
    });
  }

  if (navBackdrop) {
    navBackdrop.addEventListener('click', closeNav);
  }

  // Close nav on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeNav();
  });

  // Close nav when clicking a nav link
  if (siteNav) {
    var navLinks = siteNav.querySelectorAll('a');
    navLinks.forEach(function (link) {
      link.addEventListener('click', closeNav);
    });
  }

  /* ---------- Smooth Scroll for Anchor Links ---------- */
  var anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var href = link.getAttribute('href');
      if (href === '#' || href.length > 1) {
        var target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          var headerOffset = 80;
          var elementPosition = target.getBoundingClientRect().top;
          var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  /* ---------- Scrollspy ---------- */
  var sections = document.querySelectorAll('section[id]');
  var navAnchors = document.querySelectorAll('.site-nav a[href^="#"]');

  function updateScrollspy() {
    var scrollPosition = window.pageYOffset + 100;

    sections.forEach(function (section) {
      var sectionTop = section.offsetTop;
      var sectionHeight = section.offsetHeight;
      var sectionId = section.getAttribute('id');

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navAnchors.forEach(function (anchor) {
          anchor.classList.remove('active');
          if (anchor.getAttribute('href') === '#' + sectionId) {
            anchor.classList.add('active');
          }
        });
      }
    });
  }

  /* ---------- Header Scroll State ---------- */
  var header = document.getElementById('siteHeader');

  function updateHeaderState() {
    if (header) {
      if (window.pageYOffset > 50) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
    }
  }

  /* ---------- Throttled Scroll Handler ---------- */
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        updateScrollspy();
        updateHeaderState();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // Initial calls
  updateScrollspy();
  updateHeaderState();
})();
