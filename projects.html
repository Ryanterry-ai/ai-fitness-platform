/* Admin Dashboard JavaScript */

const API_BASE = '/api';

// API Helper
async function api(endpoint, method = 'GET', data = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { error: error.message };
    }
}

// Auth Functions
async function login(email, password) {
    const result = await api('/login', 'POST', { email, password });
    
    if (result.success) {
        localStorage.setItem('cms_token', result.token);
        localStorage.setItem('cms_user', JSON.stringify(result.user));
        window.location.href = '/admin/pages/dashboard.html';
    }
    
    return result;
}

function logout() {
    localStorage.removeItem('cms_token');
    localStorage.removeItem('cms_user');
    window.location.href = '/admin/index.html';
}

function checkAuth() {
    const token = localStorage.getItem('cms_token');
    if (!token) {
        window.location.href = '/admin/index.html';
        return false;
    }
    return true;
}

// Dashboard Functions
async function loadDashboard() {
    if (!checkAuth()) return;
    
    try {
        const stats = await api('/dashboard/stats');
        
        const pagesEl = document.getElementById('pages-count');
        const postsEl = document.getElementById('posts-count');
        const mediaEl = document.getElementById('media-count');
        const projectsEl = document.getElementById('projects-count');
        
        if (pagesEl) pagesEl.textContent = stats.pages || 0;
        if (postsEl) postsEl.textContent = stats.posts || 0;
        if (mediaEl) mediaEl.textContent = stats.media || 0;
        if (projectsEl) projectsEl.textContent = stats.projects || 0;
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Pages Functions
async function loadPages() {
    if (!checkAuth()) return;
    
    try {
        const pages = await api('/pages');
        const tbody = document.getElementById('pages-table');
        
        if (tbody && Array.isArray(pages)) {
            tbody.innerHTML = pages.map(page => `
                <tr>
                    <td>${escapeHtml(page.title)}</td>
                    <td>/${escapeHtml(page.slug)}</td>
                    <td><span class="badge badge-${page.status}">${page.status}</span></td>
                    <td>
                        <button class="btn-primary" onclick="editPage(${page.id})">Edit</button>
                        <button class="btn-danger" onclick="deletePage(${page.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Load pages error:', error);
    }
}

function showPageModal(page = null) {
    const modal = document.getElementById('page-modal');
    if (modal) modal.classList.add('active');
    
    if (page) {
        const titleEl = document.getElementById('page-title');
        const slugEl = document.getElementById('page-slug');
        const contentEl = document.getElementById('page-content');
        const idEl = document.getElementById('page-id');
        const modalTitleEl = document.getElementById('modal-title');
        
        if (titleEl) titleEl.value = page.title || '';
        if (slugEl) slugEl.value = page.slug || '';
        if (contentEl) contentEl.value = page.content || '';
        if (idEl) idEl.value = page.id || '';
        if (modalTitleEl) modalTitleEl.textContent = 'Edit Page';
    } else {
        document.getElementById('page-form').reset();
        document.getElementById('page-id').value = '';
        document.getElementById('modal-title').textContent = 'Add Page';
    }
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
}

async function editPage(id) {
    const pages = await api('/pages');
    const page = pages.find(p => p.id === id);
    if (page) showPageModal(page);
}

async function deletePage(id) {
    if (!confirm('Delete this page?')) return;
    await api(`/pages/${id}`, 'DELETE');
    loadPages();
}

async function savePage() {
    const id = document.getElementById('page-id').value;
    const data = {
        title: document.getElementById('page-title').value,
        slug: document.getElementById('page-slug').value,
        content: document.getElementById('page-content').value,
        status: 'published'
    };
    
    if (id) {
        await api(`/pages/${id}`, 'PUT', data);
    } else {
        await api('/pages', 'POST', data);
    }
    
    closeModal();
    loadPages();
}

// Media Functions
async function loadMedia() {
    if (!checkAuth()) return;
    
    try {
        const media = await api('/media');
        const grid = document.getElementById('media-grid');
        
        if (grid && Array.isArray(media)) {
            grid.innerHTML = media.map(item => `
                <div class="media-item">
                    <img src="${item.filepath}" alt="${escapeHtml(item.alt_text || '')}" onerror="this.src='/assets/images/placeholder.png'">
                    <div class="media-item-info">
                        <p>${escapeHtml(item.filename)}</p>
                        <button class="btn-danger" onclick="deleteMedia(${item.id})">Delete</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load media error:', error);
    }
}

async function uploadMedia(file) {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/media/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            loadMedia();
        }
    } catch (error) {
        console.error('Upload error:', error);
    }
}

async function deleteMedia(id) {
    if (!confirm('Delete this media?')) return;
    await api(`/media/${id}`, 'DELETE');
    loadMedia();
}

// Projects Functions
async function loadProjects() {
    if (!checkAuth()) return;
    
    try {
        const projects = await api('/projects');
        const container = document.getElementById('projects-list');
        
        if (container && Array.isArray(projects)) {
            if (projects.length === 0) {
                container.innerHTML = '<p>No projects yet.</p>';
                return;
            }
            
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Progress</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${projects.map(p => `
                            <tr>
                                <td>${escapeHtml(p.name)}</td>
                                <td>${p.type || 'clone'}</td>
                                <td><span class="badge badge-${p.status}">${p.status}</span></td>
                                <td>${p.progress || 0}%</td>
                                <td>
                                    ${p.status === 'completed' ? `<a href="/api/projects/${p.id}/download" class="btn-primary" style="padding:5px 10px;font-size:12px;">Download</a>` : ''}
                                    <button class="btn-danger" onclick="deleteProject('${p.id}')">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Load projects error:', error);
    }
}

async function deleteProject(id) {
    if (!confirm('Delete this project?')) return;
    await api(`/projects/${id}`, 'DELETE');
    loadProjects();
}

// Settings Functions
async function loadSettings() {
    if (!checkAuth()) return;
    
    try {
        const settings = await api('/settings');
        
        const siteNameEl = document.getElementById('site-name');
        const siteDescEl = document.getElementById('site-description');
        const emailEl = document.getElementById('contact-email');
        const logoEl = document.getElementById('logo-url');
        
        if (siteNameEl) siteNameEl.value = settings.site_name || '';
        if (siteDescEl) siteDescEl.value = settings.site_description || '';
        if (emailEl) emailEl.value = settings.contact_email || '';
        if (logoEl) logoEl.value = settings.logo_url || '';
    } catch (error) {
        console.error('Load settings error:', error);
    }
}

async function saveSettings() {
    const settings = {
        site_name: document.getElementById('site-name').value,
        site_description: document.getElementById('site-description').value,
        contact_email: document.getElementById('contact-email').value,
        logo_url: document.getElementById('logo-url').value
    };
    
    for (const [key, value] of Object.entries(settings)) {
        await fetch(`${API_BASE}/settings?key=${key}&value=${encodeURIComponent(value)}`, {
            method: 'POST'
        });
    }
    
    alert('Settings saved!');
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const result = await login(email, password);
            if (!result.success) {
                const errorEl = document.getElementById('error');
                if (errorEl) errorEl.textContent = 'Invalid credentials';
            }
        });
    }
    
    // Page form
    const pageForm = document.getElementById('page-form');
    if (pageForm) {
        pageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            savePage();
        });
    }
    
    // Settings form
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveSettings();
        });
    }
    
    // File input
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                uploadMedia(e.target.files[0]);
            }
        });
    }
});

// Make functions globally available
window.login = login;
window.logout = logout;
window.checkAuth = checkAuth;
window.loadDashboard = loadDashboard;
window.loadPages = loadPages;
window.showPageModal = showPageModal;
window.closeModal = closeModal;
window.editPage = editPage;
window.deletePage = deletePage;
window.savePage = savePage;
window.loadMedia = loadMedia;
window.uploadMedia = uploadMedia;
window.deleteMedia = deleteMedia;
window.loadProjects = loadProjects;
window.deleteProject = deleteProject;
window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
window.api = api;
