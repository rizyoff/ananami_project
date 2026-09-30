/* =========================================================
   components.js — Modal, Lightbox, Form handling, Toast
   ========================================================= */
(function () {
  'use strict';

  /* =========================================================
     MODAL
     ========================================================= */
  var modals = document.querySelectorAll('.modal');

  function openModal(modal) {
    if (!modal) return;
    modal.classList.add('is-active');
    document.body.style.overflow = 'hidden';
    var closeBtn = modal.querySelector('.modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('is-active');
    document.body.style.overflow = '';
  }

  // Open modal triggers
  var modalTriggers = document.querySelectorAll('[data-modal-target]');
  modalTriggers.forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      var targetId = trigger.getAttribute('data-modal-target');
      var modal = document.getElementById(targetId);
      openModal(modal);
    });
  });

  // Close modal buttons
  var modalCloseButtons = document.querySelectorAll('.modal__close');
  modalCloseButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var modal = btn.closest('.modal');
      closeModal(modal);
    });
  });

  // Close modal on backdrop click
  modals.forEach(function (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal(modal);
    });
  });

  // Close modal on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      modals.forEach(function (modal) {
        if (modal.classList.contains('is-active')) closeModal(modal);
      });
    }
  });

  /* =========================================================
     LIGHTBOX
     ========================================================= */
  var lightboxTriggers = document.querySelectorAll('[data-lightbox]');
  var lightbox = document.getElementById('lightbox');
  var lightboxImage = document.getElementById('lightboxImage');
  var lightboxClose = document.getElementById('lightboxClose');

  function openLightbox(src, alt) {
    if (!lightbox || !lightboxImage) return;
    lightboxImage.src = src;
    lightboxImage.alt = alt || '';
    lightbox.classList.add('is-active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('is-active');
    document.body.style.overflow = '';
  }

  lightboxTriggers.forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      var src = trigger.getAttribute('data-lightbox');
      var alt = trigger.getAttribute('data-alt') || '';
      openLightbox(src, alt);
    });
  });

  if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
  if (lightbox) {
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) closeLightbox();
    });
  }

  /* =========================================================
     FORM HANDLING
     ========================================================= */
  var contactForm = document.getElementById('contactForm');

  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      var name = contactForm.querySelector('#formName');
      var email = contactForm.querySelector('#formEmail');
      var message = contactForm.querySelector('#formMessage');
      var service = contactForm.querySelector('#formService');
      var submitBtn = document.getElementById('submitBtn');
      var formStatus = document.getElementById('formStatus');
      var nameError = document.getElementById('nameError');
      var emailError = document.getElementById('emailError');
      var messageError = document.getElementById('messageError');

      // Reset errors
      name.classList.remove('is-error');
      email.classList.remove('is-error');
      message.classList.remove('is-error');
      nameError.textContent = '';
      emailError.textContent = '';
      messageError.textContent = '';
      formStatus.className = 'form__status';
      formStatus.textContent = '';

      var hasError = false;

      // Validate name
      if (!name.value.trim()) {
        name.classList.add('is-error');
        nameError.textContent = 'Please enter your name';
        hasError = true;
      }

      // Validate email
      if (!email.value.trim()) {
        email.classList.add('is-error');
        emailError.textContent = 'Please enter your email';
        hasError = true;
      } else if (!isValidEmail(email.value)) {
        email.classList.add('is-error');
        emailError.textContent = 'Please enter a valid email address';
        hasError = true;
      }

      // Validate message
      if (!message.value.trim()) {
        message.classList.add('is-error');
        messageError.textContent = 'Please enter your message';
        hasError = true;
      }

      if (hasError) {
        formStatus.className = 'form__status is-error';
        formStatus.textContent = 'Please fix the errors above.';
        return;
      }

      // Show loading state
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="form__submit-text">Sending...</span><i class="fa-solid fa-spinner fa-spin"></i>';

      // Build mailto link
      var subject = encodeURIComponent('Landscape Inquiry from ' + name.value + (service.value ? ' - ' + service.value : ''));
      var body = encodeURIComponent(
        'Name: ' + name.value + '\n' +
        'Email: ' + email.value + '\n' +
        (service.value ? 'Service: ' + service.value + '\n' : '') + '\n' +
        message.value
      );

      // Simulate delay then open mailto
      setTimeout(function () {
        window.location.href = 'mailto:ananamilandscape@gmail.com?subject=' + subject + '&body=' + body;

        // Show success state
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="form__submit-text">Send Message</span><i class="fa-solid fa-paper-plane"></i>';
        formStatus.className = 'form__status is-success';
        formStatus.textContent = 'Opening your email client... Please complete sending your message.';
        contactForm.reset();
      }, 800);
    });
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  /* =========================================================
     TOAST NOTIFICATION
     ========================================================= */
  var toast = document.getElementById('toast');
  var toastTimeout;

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(function () {
      toast.classList.remove('is-visible');
    }, 3000);
  }

  /* =========================================================
     COPY TO CLIPBOARD
     ========================================================= */
  var copyButtons = document.querySelectorAll('[data-copy]');
  copyButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy');
      copyToClipboard(text);
    });
  });

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        showToast('Copied: ' + text);
      }).catch(function () {
        fallbackCopy(text);
      });
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      showToast('Copied: ' + text);
    } catch (err) {
      showToast('Failed to copy');
    }
    document.body.removeChild(textarea);
  }

  /* =========================================================
     BACK TO TOP
     ========================================================= */
  var backToTop = document.getElementById('backToTop');

  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.pageYOffset > 500) {
        backToTop.classList.add('is-visible');
      } else {
        backToTop.classList.remove('is-visible');
      }
    }, { passive: true });

    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* =========================================================
     SCROLL REVEAL ANIMATION
     ========================================================= */
  var revealElements = document.querySelectorAll('[data-reveal]');

  if ('IntersectionObserver' in window && revealElements.length > 0) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // Fallback: show all elements
    revealElements.forEach(function (el) {
      el.classList.add('is-revealed');
    });
  }
})();
