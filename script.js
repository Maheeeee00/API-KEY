'use strict';

/* ============================================================
   NAVBAR — scroll shrink + hamburger
   ============================================================ */
const navbar    = document.getElementById('navbar');
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

hamburger.addEventListener('click', () => {
  mobileMenu.classList.toggle('open');
});

function closeMenu() {
  mobileMenu.classList.remove('open');
}

function scrollToContact() {
  document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
  closeMenu();
}

/* ============================================================
   ANIMATED COUNTERS — hero stats
   ============================================================ */
function animateCounter(el) {
  const target = +el.dataset.target;
  const duration = 1800;
  const startTime = performance.now();

  const step = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(step);
  };

  requestAnimationFrame(step);
}

/* ============================================================
   SKILL BARS — animate on visibility
   ============================================================ */
function animateSkillBars() {
  document.querySelectorAll('.skill-bar__fill').forEach(bar => {
    bar.style.width = bar.dataset.width + '%';
  });
}

/* ============================================================
   INTERSECTION OBSERVER — fade-up + counters + skill bars
   ============================================================ */
const observerOptions = { threshold: 0.15 };

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;

    entry.target.classList.add('visible');
    observer.unobserve(entry.target);
  });
}, observerOptions);

// Attach fade-up to all major sections & cards
const fadeTargets = document.querySelectorAll(
  '.about__card, .project, .testimonial, .skill-item, .contact__form, .contact__left, .section__header'
);

fadeTargets.forEach((el, i) => {
  el.classList.add('fade-up');
  el.style.transitionDelay = `${(i % 4) * 0.08}s`;
  observer.observe(el);
});

// Counter observer — fires once hero stats come into view
const statsEl = document.querySelector('.hero__stats');
if (statsEl) {
  const counterObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      document.querySelectorAll('.stat__num').forEach(animateCounter);
      counterObserver.disconnect();
    }
  }, { threshold: 0.5 });
  counterObserver.observe(statsEl);
}

// Skill bars observer
const skillsSection = document.querySelector('.skills');
if (skillsSection) {
  const skillObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      animateSkillBars();
      skillObserver.disconnect();
    }
  }, { threshold: 0.3 });
  skillObserver.observe(skillsSection);
}

/* ============================================================
   CONTACT FORM — simple client-side validation & success state
   ============================================================ */
const contactForm  = document.getElementById('contactForm');
const formSuccess  = document.getElementById('formSuccess');

contactForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const name    = contactForm.name.value.trim();
  const email   = contactForm.email.value.trim();
  const message = contactForm.message.value.trim();

  if (!name || !email || !message) {
    shakeForm();
    return;
  }

  if (!isValidEmail(email)) {
    contactForm.email.focus();
    contactForm.email.style.borderColor = '#ef4444';
    setTimeout(() => { contactForm.email.style.borderColor = ''; }, 2000);
    return;
  }

  // Simulate send — swap button state
  const btn = contactForm.querySelector('button[type="submit"]');
  btn.textContent = 'Sending…';
  btn.disabled = true;

  setTimeout(() => {
    contactForm.reset();
    btn.textContent = 'Send Message →';
    btn.disabled = false;
    formSuccess.classList.add('show');
    setTimeout(() => formSuccess.classList.remove('show'), 5000);
  }, 1200);
});

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function shakeForm() {
  contactForm.style.animation = 'shake 0.4s ease';
  contactForm.addEventListener('animationend', () => {
    contactForm.style.animation = '';
  }, { once: true });
}

// Inject shake keyframe dynamically
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%       { transform: translateX(-8px); }
    40%       { transform: translateX(8px); }
    60%       { transform: translateX(-5px); }
    80%       { transform: translateX(5px); }
  }
`;
document.head.appendChild(shakeStyle);

/* ============================================================
   SMOOTH SCROLL for all internal anchor links
   ============================================================ */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth' });
  });
});

/* ============================================================
   ACTIVE NAV LINK — highlights based on scroll position
   ============================================================ */
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav__links a');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(sec => {
    if (window.scrollY >= sec.offsetTop - 120) current = sec.id;
  });
  navLinks.forEach(link => {
    link.style.color = link.getAttribute('href') === `#${current}` ? 'var(--purple-600)' : '';
  });
}, { passive: true });
