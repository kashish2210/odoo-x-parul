document.addEventListener('DOMContentLoaded', () => {
  initChecklistToggles();
  initChecklistModals();
  initChecklistSearch();
  initShareChecklist();
});

function initChecklistToggles() {
  const checkboxes = document.querySelectorAll('.item-checkbox');
  
  checkboxes.forEach(box => {
    box.addEventListener('change', async (e) => {
      const itemId = e.target.dataset.id;
      const isChecked = e.target.checked;
      
      try {
        const response = await fetch(`/checklists/toggle/${itemId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          updateProgress(data);
        } else {
          // Revert on failure
          e.target.checked = !isChecked;
          console.error("Failed to toggle item.");
        }
      } catch (err) {
        e.target.checked = !isChecked;
        console.error("Error toggling item:", err);
      }
    });
  });
}

function updateProgress(data) {
  // Update overall progress
  const packedEl = document.getElementById('packedCount');
  const totalEl = document.getElementById('totalCount');
  const barEl = document.getElementById('progressBarFill');
  
  if (packedEl) packedEl.textContent = data.packed_items;
  if (totalEl) totalEl.textContent = data.total_items;
  
  if (barEl && data.total_items > 0) {
    const percent = (data.packed_items / data.total_items) * 100;
    barEl.style.width = `${percent}%`;
  }
  
  // Update category progress
  const catPackedEl = document.getElementById(`catPacked-${data.category}`);
  if (catPackedEl) {
    catPackedEl.textContent = data.cat_packed;
  }
}

function initChecklistModals() {
  const addModal = document.getElementById('addItemModal');
  const resetModal = document.getElementById('resetConfirmModal');
  const backdrop = document.getElementById('modalBackdrop');
  
  const openAddBtn = document.getElementById('openAddItemModal');
  const closeAddBtn = document.getElementById('closeAddItemModal');
  const cancelAddBtn = document.getElementById('cancelAddItemModal');
  
  const resetBtn = document.getElementById('resetChecklistBtn');
  const cancelResetBtn = document.getElementById('cancelResetModal');
  
  function openModal(modal) {
    if (!modal) return;
    modal.hidden = false;
    if (backdrop) backdrop.hidden = false;
    document.body.style.overflow = 'hidden';
    const focusable = modal.querySelector('input, select');
    if (focusable) setTimeout(() => focusable.focus(), 50);
  }
  
  function closeModal(modal) {
    if (!modal) return;
    modal.hidden = true;
    if (backdrop) backdrop.hidden = true;
    document.body.style.overflow = '';
  }
  
  if (openAddBtn) openAddBtn.addEventListener('click', () => openModal(addModal));
  if (closeAddBtn) closeAddBtn.addEventListener('click', () => closeModal(addModal));
  if (cancelAddBtn) cancelAddBtn.addEventListener('click', () => closeModal(addModal));
  
  if (resetBtn) resetBtn.addEventListener('click', () => openModal(resetModal));
  if (cancelResetBtn) cancelResetBtn.addEventListener('click', () => closeModal(resetModal));
  
  if (backdrop) {
    backdrop.addEventListener('click', () => {
      closeModal(addModal);
      closeModal(resetModal);
    });
  }
}

function initChecklistSearch() {
  const input = document.getElementById('notesSearchInput');
  if (!input) return;
  
  input.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const items = document.querySelectorAll('.item-row');
    
    items.forEach(item => {
      const name = item.querySelector('.item-name').textContent.toLowerCase();
      if (name.includes(query)) {
        item.style.display = 'flex';
      } else {
        item.style.display = 'none';
      }
    });
    
    // Hide categories that have no visible items
    document.querySelectorAll('.category-section').forEach(cat => {
      const visibleItems = Array.from(cat.querySelectorAll('.item-row')).filter(i => i.style.display !== 'none');
      if (visibleItems.length === 0 && query !== '') {
        cat.style.display = 'none';
      } else {
        cat.style.display = 'block';
      }
    });
  });
}

function initShareChecklist() {
  const shareBtn = document.getElementById('shareChecklistBtn');
  if (!shareBtn) return;
  
  shareBtn.addEventListener('click', () => {
    let text = "My Packing Checklist:\n\n";
    
    document.querySelectorAll('.category-section').forEach(cat => {
      if (cat.style.display === 'none') return; // Skip hidden categories if searching
      
      const title = cat.querySelector('.category-title').textContent;
      text += `--- ${title} ---\n`;
      
      cat.querySelectorAll('.item-row').forEach(row => {
        if (row.style.display === 'none') return;
        
        const isChecked = row.querySelector('.item-checkbox').checked;
        const name = row.querySelector('.item-name').textContent;
        text += `[${isChecked ? 'x' : ' '}] ${name}\n`;
      });
      text += '\n';
    });
    
    navigator.clipboard.writeText(text).then(() => {
      const originalText = shareBtn.textContent;
      shareBtn.textContent = "Copied to clipboard!";
      setTimeout(() => {
        shareBtn.textContent = originalText;
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy text: ', err);
      alert("Failed to copy checklist to clipboard.");
    });
  });
}
