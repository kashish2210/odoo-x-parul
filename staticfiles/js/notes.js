// ========== TRAVELOOP NOTES — notes.js ==========
// Handles: live search, filter tabs, and modal logic.

document.addEventListener('DOMContentLoaded', () => {
  initModals();
  initLiveSearch();
  initFilterTabs();
  initNotesThemeAccessibility();
});

// -------- THEME TOGGLE ACCESSIBILITY --------
function initNotesThemeAccessibility() {
  const toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle.click();
      }
    });
  }
}

// -------- MODALS --------
let pendingDeleteFormId = null;

function initModals() {
  const addModal    = document.getElementById('addNoteModal');
  const editModal   = document.getElementById('editNoteModal');
  const deleteModal = document.getElementById('deleteConfirmModal');
  const backdrop    = document.getElementById('modalBackdrop');

  function openModal(modal) {
    if (!modal) return;
    modal.hidden = false;
    if (backdrop) backdrop.hidden = false;
    document.body.style.overflow = 'hidden';
    const focusable = modal.querySelector('input, select, textarea, button');
    if (focusable) setTimeout(() => focusable.focus(), 50);
  }

  function closeModal(modal) {
    if (!modal) return;
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

// Global functions called from HTML
window.openEditModal = function(pk, title, content, stopName, dayLabel, tripPk) {
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
};

window.confirmDeleteNote = function(pk, title) {
  const modal  = document.getElementById('deleteConfirmModal');
  const textEl = document.getElementById('deleteConfirmText');
  if (!modal) return;
  if (textEl) textEl.innerHTML = `Are you sure you want to delete <strong>"${escapeHtml(title)}"</strong>? This cannot be undone.`;
  pendingDeleteFormId = `deleteForm-${pk}`;
  modal.hidden = false;
  const backdrop = document.getElementById('modalBackdrop');
  if (backdrop) backdrop.hidden = false;
  document.body.style.overflow = 'hidden';
};

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
