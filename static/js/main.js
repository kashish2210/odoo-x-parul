// ========== TRAVELOOP - Theme & UI ==========

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileMenu();
  initAutoMessages();
  initFilterDropdowns();
});

// ---------- FILTER DROPDOWNS ----------
function initFilterDropdowns() {
  // Close all open dropdowns when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.filter-btn') && !e.target.closest('.filter-dropdown')) {
      document.querySelectorAll('.filter-dropdown.show').forEach(d => d.classList.remove('show'));
    }
  });
}

// ---------- THEME TOGGLE ----------
function initTheme() {
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;

  // Check saved preference, else use system preference
  const saved = localStorage.getItem('traveloop-theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  }

  updateToggleIcon();

  toggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('traveloop-theme', next);
    updateToggleIcon();
  });

  // Listen for system changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('traveloop-theme')) {
      document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
      updateToggleIcon();
    }
  });
}

function updateToggleIcon() {
  const thumb = document.querySelector('.toggle-thumb');
  if (!thumb) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const moonSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
  const sunSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
  thumb.innerHTML = isDark ? moonSvg : sunSvg;
}

// ---------- MOBILE MENU ----------
function initMobileMenu() {
  const btn = document.getElementById('mobileToggle');
  const nav = document.getElementById('navLinks');
  if (!btn || !nav) return;

  btn.addEventListener('click', () => {
    nav.classList.toggle('open');
    btn.textContent = nav.classList.contains('open') ? '✕' : '☰';
  });
}

// ---------- AUTO-DISMISS MESSAGES ----------
function initAutoMessages() {
  const msgs = document.querySelectorAll('.messages li');
  msgs.forEach((m, i) => {
    setTimeout(() => {
      m.style.transition = 'opacity 0.4s, transform 0.4s';
      m.style.opacity = '0';
      m.style.transform = 'translateY(-10px)';
      setTimeout(() => m.remove(), 400);
    }, 4000 + i * 500);
  });
}

// ---------- AVATAR PREVIEW ----------
function previewAvatar(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const container = document.getElementById('avatarPreview');
      if (container) {
        container.innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// ---------- BANNER SLIDER ----------
document.addEventListener('DOMContentLoaded', () => {
  const nextBtn = document.getElementById('sliderNext');
  const prevBtn = document.getElementById('sliderPrev');
  const slideContainer = document.getElementById('bannerSlide');
  
  if (nextBtn && prevBtn && slideContainer) {
    nextBtn.addEventListener('click', () => {
      let items = slideContainer.querySelectorAll('.item');
      if (items.length > 0) {
        slideContainer.appendChild(items[0]);
      }
    });

    prevBtn.addEventListener('click', () => {
      let items = slideContainer.querySelectorAll('.item');
      if (items.length > 0) {
        slideContainer.prepend(items[items.length - 1]);
      }
    });
  }
});
