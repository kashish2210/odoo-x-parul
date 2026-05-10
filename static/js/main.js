// ========== TRAVELOOP - Theme & UI ==========

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileMenu();
  initAutoMessages();
});

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
  thumb.textContent = isDark ? '🌙' : '☀️';
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
