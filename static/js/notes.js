// ========== TRAVELOOP NOTES — notes.js ==========

document.addEventListener('DOMContentLoaded', () => {
  fixToggleSVG();
  initNotesThemeToggle();
  initNotesMobileMenu();
  initModals();
  initLiveSearch();
  initFilterTabs();
});

// -------- THEME TOGGLE (SVG — overrides main.js emoji) --------

const SVG_SUN = `<svg class="icon-sun" width="12" height="12" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2.5" aria-hidden="true">
  <circle cx="12" cy="12" r="5"/>
  <line x1="12" y1="1" x2="12" y2="3"/>
  <line x1="12" y1="21" x2="12" y2="23"/>
  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
  <line x1="1" y1="12" x2="3" y2="12"/>
  <line x1="21" y1="12" x2="23" y2="12"/>
  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
</svg>`;

const SVG_MOON = `<svg class="icon-moon" width="12" height="12" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2.5" aria-hidden="true">
  <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/>
</svg>`;

function fixToggleSVG() {
  const thumb = document.getElementById('toggleThumb');
  if (!thumb) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  thumb.innerHTML = isDark ? SVG_MOON : SVG_SUN;
}

function initNotesThemeToggle() {
  // Override main.js emoji updater with SVG version
  window.updateToggleIcon = fixToggleSVG;
  fixToggleSVG();

  const toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle.click(); }
    });
  }
}

// -------- MOBILE MENU --------

function initNotesMobileMenu() {
  const btn = document.getElementById('notesMobileToggle');
  const nav = document.getElementById('notesNavLinks');
  if (!btn || !nav) return;

  btn.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !nav.contains(e.target)) {
      nav.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });
}

// -------- MODALS --------

let pendingDeleteFormId = null;

function initModals() {
  const addModal    = document.getElementById('addNoteModal');
  const editModal   = document.getElementById('editNoteModal');
  const deleteModal = document.getElementById('deleteConfirmModal');
  const backdrop    = document.getElementById('modalBackdrop');

  function openModal(modal) {
    modal.hidden = false;
    if (backdrop) backdrop.hidden = false;
    document.body.style.overflow = 'hidden';
    const focusable = modal.querySelector('input, select, textarea, button');
    if (focusable) setTimeout(() => focusable.focus(), 50);
  }

  function closeModal(modal) {
    modal.hidden = true;
    if (backdrop) backdrop.hidden = true;
    document.body.style.overflow = '';
    pendingDeleteFormId = null;
  }

  function closeAll() {
    [addModal, editModal, deleteModal].forEach(m => { if (m) m.hidden = true; });
    if (backdrop) backdrop.hidden = true;
    document.body.style.overflow = '';
    pendingDeleteFormId = null;
  }

  const bind = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };

  bind('openAddModal',    () => openModal(addModal));
  bind('closeAddModal',   () => closeModal(addModal));
  bind('cancelAddModal',  () => closeModal(addModal));
  bind('closeEditModal',  () => closeModal(editModal));
  bind('cancelEditModal', () => closeModal(editModal));
  bind('cancelDeleteModal', () => closeModal(deleteModal));

  bind('confirmDeleteBtn', () => {
    if (pendingDeleteFormId) {
      const form = document.getElementById(pendingDeleteFormId);
      if (form) form.submit();
    }
  });

  if (backdrop) backdrop.addEventListener('click', closeAll);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(); });
}

function openEditModal(pk, title, content, stopName, dayLabel, tripPk) {
  const modal = document.getElementById('editNoteModal');
  if (!modal) return;

  const form = document.getElementById('editNoteForm');
  if (form) form.action = `/notes/${pk}/edit/`;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
  set('edit_title',   title);
  set('edit_content', content);
  set('edit_stop',    stopName);
  set('edit_day',     dayLabel);
  const ts = document.getElementById('edit_trip');
  if (ts) ts.value = tripPk;

  modal.hidden = false;
  const backdrop = document.getElementById('modalBackdrop');
  if (backdrop) backdrop.hidden = false;
  document.body.style.overflow = 'hidden';
  setTimeout(() => { const t = document.getElementById('edit_title'); if (t) t.focus(); }, 50);
}

function confirmDeleteNote(pk, title) {
  const modal  = document.getElementById('deleteConfirmModal');
  const textEl = document.getElementById('deleteConfirmText');
  if (!modal) return;
  if (textEl) textEl.innerHTML = `Are you sure you want to delete <strong>"${escapeHtml(title)}"</strong>? This cannot be undone.`;
  pendingDeleteFormId = `deleteForm-${pk}`;
  modal.hidden = false;
  const backdrop = document.getElementById('modalBackdrop');
  if (backdrop) backdrop.hidden = false;
  document.body.style.overflow = 'hidden';
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}

// -------- LIVE SEARCH --------

function initLiveSearch() {
  const input = document.getElementById('notesSearchInput');
  if (!input) return;
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => filterCards(input.value.trim().toLowerCase(), getActiveGroup()), 180);
  });
}

function filterCards(query, group) {
  const cards = document.querySelectorAll('.note-card');
  let visible = 0;
  cards.forEach(card => {
    const matchQ = !query ||
      (card.dataset.title   || '').includes(query) ||
      (card.dataset.content || '').includes(query) ||
      (card.dataset.day     || '').includes(query) ||
      (card.dataset.stop    || '').includes(query);
    const matchG = group === 'all' ? true :
                   group === 'day'  ? (card.dataset.day  || '').length > 0 :
                   group === 'stop' ? (card.dataset.stop || '').length > 0 : true;
    const show = matchQ && matchG;
    card.classList.toggle('note-card--hidden', !show);
    if (show) visible++;
  });
  const empty = document.querySelector('.notes-empty');
  if (empty) empty.style.display = visible === 0 ? 'flex' : 'none';
}

function getActiveGroup() {
  const tab = document.querySelector('.filter-tab.active');
  return tab ? tab.dataset.group : 'all';
}

// -------- FILTER TABS --------

function initFilterTabs() {
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const query = (document.getElementById('notesSearchInput')?.value || '').trim().toLowerCase();
      filterCards(query, tab.dataset.group);
      const gi = document.querySelector('input[name="group"]');
      if (gi) gi.value = tab.dataset.group;
    });
  });
}
