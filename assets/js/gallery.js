/* =========================================================
   gallery.js — Carousel untuk halaman Gallery
   ========================================================= */
(function () {
  'use strict';

  var carousel = document.getElementById('galleryCarousel');
  if (!carousel) return;

  var track = document.getElementById('carouselTrack');
  var slides = track.querySelectorAll('.gallery-slide');
  var prevBtn = document.getElementById('carouselPrev');
  var nextBtn = document.getElementById('carouselNext');
  var indicatorsContainer = document.getElementById('carouselIndicators');

  var currentSlide = 0;
  var totalSlides = slides.length;
  var autoplayInterval;
  var autoplayDelay = 5000;

  // Create indicators
  slides.forEach(function (_, index) {
    var dot = document.createElement('button');
    dot.className = 'gallery-carousel__indicator';
    dot.setAttribute('aria-label', 'Go to slide ' + (index + 1));
    if (index === 0) dot.classList.add('is-active');
    dot.addEventListener('click', function () {
      goToSlide(index);
      resetAutoplay();
    });
    indicatorsContainer.appendChild(dot);
  });

  var indicators = indicatorsContainer.querySelectorAll('.gallery-carousel__indicator');

  function goToSlide(index) {
    if (index < 0) index = totalSlides - 1;
    if (index >= totalSlides) index = 0;

    currentSlide = index;
    track.style.transform = 'translateX(-' + (currentSlide * 100) + '%)';

    // Update indicators
    indicators.forEach(function (dot, i) {
      dot.classList.toggle('is-active', i === currentSlide);
    });

    // Update slides visibility
    slides.forEach(function (slide, i) {
      slide.classList.toggle('is-active', i === currentSlide);
    });
  }

  function nextSlide() {
    goToSlide(currentSlide + 1);
  }

  function prevSlide() {
    goToSlide(currentSlide - 1);
  }

  // Event listeners
  if (nextBtn) nextBtn.addEventListener('click', function () {
    nextSlide();
    resetAutoplay();
  });

  if (prevBtn) prevBtn.addEventListener('click', function () {
    prevSlide();
    resetAutoplay();
  });

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') {
      prevSlide();
      resetAutoplay();
    } else if (e.key === 'ArrowRight') {
      nextSlide();
      resetAutoplay();
    }
  });

  // Touch/swipe support
  var touchStartX = 0;
  var touchEndX = 0;

  track.addEventListener('touchstart', function (e) {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  track.addEventListener('touchend', function (e) {
    touchEndX = e.changedTouches[0].screenX;
    var diff = touchStartX - touchEndX;

    if (Math.abs(diff) > 50) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
      resetAutoplay();
    }
  }, { passive: true });

  // Autoplay
  function startAutoplay() {
    autoplayInterval = setInterval(nextSlide, autoplayDelay);
  }

  function stopAutoplay() {
    clearInterval(autoplayInterval);
  }

  function resetAutoplay() {
    stopAutoplay();
    startAutoplay();
  }

  // Pause autoplay on hover
  carousel.addEventListener('mouseenter', stopAutoplay);
  carousel.addEventListener('mouseleave', startAutoplay);

  // Start autoplay
  startAutoplay();

  // Initialize first slide
  slides[0].classList.add('is-active');
})();
