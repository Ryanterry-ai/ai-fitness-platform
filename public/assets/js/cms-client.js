/* CMS Client JavaScript - Static Version */

let editMode = false;
let originalContent = {};

function toggleEditMode() {
    editMode = !editMode;
    document.body.classList.toggle('cms-edit-mode', editMode);
    
    const statusEl = document.getElementById('cms-status');
    if (statusEl) {
        statusEl.textContent = editMode ? 'Editing' : 'Viewing';
    }
    
    if (editMode) {
        document.querySelectorAll('[data-cms-editable]').forEach(el => {
            el.addEventListener('click', handleElementClick);
        });
    } else {
        document.querySelectorAll('[data-cms-editable]').forEach(el => {
            el.removeEventListener('click', handleElementClick);
        });
    }
}

function handleElementClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const el = e.currentTarget;
    const type = el.dataset.cmsEditable;
    
    if (type === 'image') {
        openImageModal(el);
    } else {
        openTextModal(el);
    }
}

function openTextModal(el) {
    const original = el.dataset.original || el.outerHTML;
    const currentText = el.innerText;
    
    const modal = document.createElement('div');
    modal.className = 'cms-modal active';
    modal.id = 'cms-edit-modal';
    modal.innerHTML = `
        <div class="cms-modal-content">
            <h3>Edit Content</h3>
            <textarea class="cms-textarea" id="cms-edit-text">${currentText}</textarea>
            <button class="cms-edit-btn" onclick="saveTextEdit(this)">Save</button>
            <button class="cms-cancel-btn" onclick="closeModal()">Cancel</button>
        </div>
    `;
    document.body.appendChild(modal);
    modal.dataset.element = el.outerHTML;
}

function saveTextEdit(btn) {
    const modal = document.getElementById('cms-edit-modal');
    const textarea = document.getElementById('cms-edit-text');
    const newText = textarea.value;
    
    const elements = document.querySelectorAll('[data-cms-editable]');
    const originalEl = modal.dataset.element;
    
    elements.forEach(el => {
        if (el.outerHTML === originalEl || el.dataset.original === originalEl) {
            el.innerText = newText;
            el.dataset.original = el.outerHTML;
        }
    });
    
    closeModal();
}

function openImageModal(el) {
    const src = el.src || el.getAttribute('data-src');
    const alt = el.alt || '';
    
    const modal = document.createElement('div');
    modal.className = 'cms-modal active';
    modal.id = 'cms-edit-modal';
    modal.innerHTML = `
        <div class="cms-modal-content">
            <h3>Edit Image</h3>
            <input class="cms-input" type="text" id="cms-img-src" value="${src}" placeholder="Image URL">
            <input class="cms-input" type="text" id="cms-img-alt" value="${alt}" placeholder="Alt text">
            <input class="cms-input" type="text" id="cms-img-title" value="${el.title || ''}" placeholder="Title">
            <button class="cms-edit-btn" onclick="saveImageEdit(this)">Save</button>
            <button class="cms-cancel-btn" onclick="closeModal()">Cancel</button>
        </div>
    `;
    document.body.appendChild(modal);
    modal.dataset.element = el.outerHTML;
}

function saveImageEdit(btn) {
    const modal = document.getElementById('cms-edit-modal');
    const src = document.getElementById('cms-img-src').value;
    const alt = document.getElementById('cms-img-alt').value;
    const title = document.getElementById('cms-img-title').value;
    
    const elements = document.querySelectorAll('[data-cms-editable="image"]');
    const originalEl = modal.dataset.element;
    
    elements.forEach(el => {
        if (el.outerHTML === originalEl) {
            if (el.src !== undefined) el.src = src;
            if (el.getAttribute('data-src')) el.setAttribute('data-src', src);
            el.alt = alt;
            if (title) el.title = title;
        }
    });
    
    closeModal();
}

function closeModal() {
    const modal = document.getElementById('cms-edit-modal');
    if (modal) modal.remove();
}

async function savePage() {
    const pageSlug = document.body.dataset.pageSlug || 'index';
    const content = document.body.innerHTML;
    
    try {
        const response = await fetch(`${window.API_BASE || '/api'}/pages/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: pageSlug, content })
        });
        
        if (response.ok) {
            alert('Page saved successfully!');
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        console.error('Save error:', error);
        localStorage.setItem(`cms_${pageSlug}`, content);
        alert('Saved locally (API unavailable)');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && editMode) {
        toggleEditMode();
    }
});

// Make functions globally available
window.toggleEditMode = toggleEditMode;
window.savePage = savePage;
window.handleElementClick = handleElementClick;
window.openTextModal = openTextModal;
window.openImageModal = openImageModal;
window.saveTextEdit = saveTextEdit;
window.saveImageEdit = saveImageEdit;
window.closeModal = closeModal;
