(function () {
  'use strict';

  /* --- Header: switch from transparent hero treatment to solid ---------- */
  var header = document.querySelector('.site-header');

  if (header) {
    var ticking = false;

    var updateHeader = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 24);
      ticking = false;
    };

    updateHeader();
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateHeader);
      }
    }, { passive: true });
  }

  /* --- Reveal on scroll ------------------------------------------------ */
  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var revealItems = document.querySelectorAll('[data-reveal]');

  if (!prefersReducedMotion && 'IntersectionObserver' in window && revealItems.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });

    revealItems.forEach(function (item, index) {
      item.classList.add('will-reveal');
      item.style.transitionDelay = Math.min(index % 3, 2) * 70 + 'ms';
      observer.observe(item);
    });
  }

  /* --- Photo lightbox -------------------------------------------------- */
  var photos = Array.prototype.slice.call(document.querySelectorAll('.prose figure img'));

  if (photos.length && typeof HTMLDialogElement !== 'undefined') {
    var dialog = document.createElement('dialog');
    dialog.className = 'lightbox';
    dialog.setAttribute('aria-label', 'Photo viewer');
    dialog.innerHTML =
      '<div class="lightbox__inner">' +
        '<button class="lightbox__close" type="button" aria-label="Close photo">&times;</button>' +
        '<img class="lightbox__img" alt="">' +
        '<p class="lightbox__caption"></p>' +
      '</div>';
    document.body.appendChild(dialog);

    var bigImage = dialog.querySelector('.lightbox__img');
    var caption = dialog.querySelector('.lightbox__caption');
    var closeButton = dialog.querySelector('.lightbox__close');
    var lastFocused = null;

    var openPhoto = function (photo) {
      lastFocused = photo;
      bigImage.src = photo.currentSrc || photo.src;
      bigImage.alt = photo.alt || '';

      var figure = photo.closest('figure');
      var figcaption = figure ? figure.querySelector('figcaption') : null;
      caption.textContent = figcaption ? figcaption.textContent : '';
      caption.hidden = !figcaption;

      dialog.showModal();
      document.body.classList.add('has-lightbox');
      closeButton.focus();
    };

    photos.forEach(function (photo) {
      photo.setAttribute('tabindex', '0');
      photo.setAttribute('role', 'button');
      photo.setAttribute('aria-label', 'View larger: ' + (photo.alt || 'photo'));

      photo.addEventListener('click', function () {
        openPhoto(photo);
      });

      photo.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openPhoto(photo);
        }
      });
    });

    closeButton.addEventListener('click', function () {
      dialog.close();
    });

    dialog.addEventListener('click', function (event) {
      if (event.target === dialog || event.target === dialog.querySelector('.lightbox__inner')) {
        dialog.close();
      }
    });

    dialog.addEventListener('close', function () {
      document.body.classList.remove('has-lightbox');
      if (lastFocused) {
        lastFocused.focus();
      }
    });
  }
})();
