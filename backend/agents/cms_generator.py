"""
Enhanced CMS Generator Agent - Production Version
Generates complete admin dashboard and editable CMS
"""
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
import json
import re
import hashlib
import os

class CMSGenerator:
    def __init__(self, pages_data: List[Dict], project_path: str, base_url: str):
        self.pages_data = pages_data
        self.project_path = Path(project_path)
        self.base_url = base_url
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        self.public_dir = self.project_path / "public"
        self.admin_dir = self.project_path / "admin"
        self.assets_dir = self.public_dir / "assets"
        self.css_dir = self.assets_dir / "css"
        self.js_dir = self.assets_dir / "js"
        self.images_dir = self.assets_dir / "images"
        self.pages_dir = self.public_dir / "pages"
        
        for d in [self.public_dir, self.admin_dir, self.assets_dir, 
                  self.css_dir, self.js_dir, self.images_dir, self.pages_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def generate(self):
        self._generate_index()
        self._generate_pages()
        self._generate_css()
        self._generate_javascript()
        self._generate_admin()
        self._generate_database()
        self._generate_api()
        self._generate_readme()
    
    def _generate_index(self):
        if not self.pages_data:
            return
            
        first_page = self.pages_data[0]
        soup = first_page.get('soup') or BeautifulSoup(first_page['content'], 'html.parser')
        
        html = soup.prettify()
        html = self._make_editable(html)
        
        index_path = self.public_dir / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(self._wrap_with_cms(html, 'index', 'Home'))
    
    def _generate_pages(self):
        for i, page_data in enumerate(self.pages_data):
            soup = page_data.get('soup') or BeautifulSoup(page_data['content'], 'html.parser')
            
            url = page_data['url']
            page_name = self._url_to_filename(url)
            
            html = soup.prettify()
            html = self._make_editable(html)
            
            page_path = self.pages_dir / f"{page_name}.html"
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(self._wrap_with_cms(html, page_name, page_data.get('title', 'Page')))
    
    def _wrap_with_cms(self, html: str, page_slug: str, page_title: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en" data-page-slug="{page_slug}" data-page-title="{page_title}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <link rel="stylesheet" href="/assets/css/cms.css">
    <script src="/assets/js/cms-client.js" defer></script>
</head>
<body class="cms-editable">
    {html}
    
    <div id="cms-toolbar" class="cms-toolbar">
        <button class="cms-btn" onclick="toggleEditMode()">
            <span class="cms-icon">&#9998;</span> Edit
        </button>
        <button class="cms-btn" onclick="savePage()">
            <span class="cms-icon">&#128190;</span> Save
        </button>
        <span class="cms-status" id="cms-status">Viewing</span>
    </div>
    
    <script>
        const PAGE_SLUG = '{page_slug}';
        const API_BASE = '/api';
    </script>
</body>
</html>'''
    
    def _make_editable(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'li']):
            text = tag.get_text(strip=True)
            if text and len(text) > 0:
                tag['data-cms-editable'] = 'true'
                tag['data-original'] = str(tag)
        
        for img in soup.find_all('img'):
            img['data-cms-editable'] = 'image'
            img['data-original'] = str(img)
        
        return str(soup)
    
    def _generate_css(self):
        css_content = '''
/* CMS Editable Styles */
:root {
    --cms-primary: #3b82f6;
    --cms-secondary: #10b981;
    --cms-danger: #ef4444;
    --cms-bg: rgba(59, 130, 246, 0.1);
    --cms-border: #3b82f6;
}

body.cms-editable [data-cms-editable] {
    outline: 2px dashed transparent;
    outline-offset: 4px;
    transition: all 0.2s;
    cursor: text;
    position: relative;
}

body.cms-editable [data-cms-editable]:hover {
    outline-color: var(--cms-primary);
    background-color: var(--cms-bg);
}

body.cms-editable.cms-edit-mode [data-cms-editable] {
    outline-color: var(--cms-primary);
    background-color: var(--cms-bg);
    cursor: text;
}

body.cms-editable [data-cms-editable="image"] {
    cursor: pointer;
}

body.cms-editable [data-cms-editable="image"]:hover {
    outline-color: var(--cms-secondary);
}

.cms-toolbar {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: white;
    padding: 12px 20px;
    border-radius: 50px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    display: flex;
    gap: 10px;
    align-items: center;
    z-index: 9999;
    font-family: system-ui, -apple-system, sans-serif;
}

.cms-btn {
    background: var(--cms-primary);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
}

.cms-btn:hover {
    background: #2563eb;
    transform: translateY(-2px);
}

.cms-icon {
    font-size: 16px;
}

.cms-status {
    background: var(--cms-bg);
    color: var(--cms-primary);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.cms-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 10000;
}

.cms-modal.active {
    display: flex;
}

.cms-modal-content {
    background: white;
    padding: 24px;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.cms-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    margin-bottom: 12px;
}

.cms-textarea {
    width: 100%;
    min-height: 150px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    font-family: monospace;
    margin-bottom: 12px;
}

.cms-edit-btn {
    background: var(--cms-secondary);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

.cms-cancel-btn {
    background: #6b7280;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    margin-left: 10px;
}
'''
        
        with open(self.css_dir / "cms.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _generate_javascript(self):
        js_content = '''
let editMode = false;
let originalContent = {};

function toggleEditMode() {
    editMode = !editMode;
    document.body.classList.toggle('cms-edit-mode', editMode);
    document.getElementById('cms-status').textContent = editMode ? 'Editing' : 'Viewing';
    
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
    const pageSlug = document.body.dataset.pageSlug;
    const content = document.body.innerHTML;
    
    try {
        const response = await fetch(`${API_BASE}/pages/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: pageSlug, content })
        });
        
        if (response.ok) {
            alert('Page saved successfully!');
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
'''
        
        with open(self.js_dir / "cms-client.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _generate_admin(self):
        self._generate_admin_index()
        self._generate_admin_login()
        self._generate_admin_dashboard()
        self._generate_admin_pages()
        self._generate_admin_media()
        self._generate_admin_settings()
        self._generate_admin_css()
        self._generate_admin_js()
    
    def _generate_admin_index(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - CMS</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-box">
            <h1>CMS Admin</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="Email" required value="admin@admin.com">
                <input type="password" id="password" placeholder="Password" required value="admin123">
                <button type="submit">Login</button>
            </form>
            <p class="login-info">Default: admin@admin.com / admin123</p>
        </div>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
</body>
</html>'''
        
        with open(self.admin_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_login(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - CMS</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-box">
            <h1>Admin Login</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="Email" required value="admin@admin.com">
                <input type="password" id="password" placeholder="Password" required value="admin123">
                <button type="submit">Login</button>
            </form>
            <div id="error" class="error"></div>
        </div>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
</body>
</html>'''
        
        with open(self.admin_dir / "pages" / "login.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_dashboard(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - CMS Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>CMS Admin</h2>
            <a href="/admin/dashboard.html" class="active">Dashboard</a>
            <a href="/admin/pages.html">Pages</a>
            <a href="/admin/media.html">Media</a>
            <a href="/admin/settings.html">Settings</a>
            <a href="/admin/cloner.html">Website Cloner</a>
            <a href="#" onclick="logout()">Logout</a>
        </nav>
        <main class="content">
            <h1>Dashboard</h1>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Pages</h3>
                    <p id="pages-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>Posts</h3>
                    <p id="posts-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>Media</h3>
                    <p id="media-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>Cloned Sites</h3>
                    <p id="sites-count">0</p>
                </div>
            </div>
            <div class="quick-actions">
                <h2>Quick Actions</h2>
                <button onclick="location.href='/admin/pages.html'">Manage Pages</button>
                <button onclick="location.href='/admin/media.html'">Upload Media</button>
                <button onclick="location.href='/admin/cloner.html'">Clone Website</button>
            </div>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>loadDashboard();</script>
</body>
</html>'''
        
        with open(self.admin_dir / "pages" / "dashboard.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_pages(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pages - CMS Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>CMS Admin</h2>
            <a href="/admin/dashboard.html">Dashboard</a>
            <a href="/admin/pages.html" class="active">Pages</a>
            <a href="/admin/media.html">Media</a>
            <a href="/admin/settings.html">Settings</a>
            <a href="/admin/cloner.html">Website Cloner</a>
            <a href="#" onclick="logout()">Logout</a>
        </nav>
        <main class="content">
            <div class="header">
                <h1>Pages</h1>
                <button class="btn-primary" onclick="showPageModal()">Add New Page</button>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Slug</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="pages-table"></tbody>
            </table>
        </main>
    </div>
    <div class="modal" id="page-modal">
        <div class="modal-content">
            <h2 id="modal-title">Add Page</h2>
            <form id="page-form">
                <input type="hidden" id="page-id">
                <input type="text" id="page-title" placeholder="Page Title" required>
                <input type="text" id="page-slug" placeholder="URL Slug" required>
                <textarea id="page-content" placeholder="Page Content" rows="10"></textarea>
                <input type="text" id="page-meta-title" placeholder="Meta Title">
                <input type="text" id="page-meta-desc" placeholder="Meta Description">
                <select id="page-status">
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                </select>
                <button type="submit" class="btn-primary">Save</button>
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
            </form>
        </div>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>loadPages();</script>
</body>
</html>'''
        
        with open(self.admin_dir / "pages" / "pages.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_media(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media - CMS Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>CMS Admin</h2>
            <a href="/admin/dashboard.html">Dashboard</a>
            <a href="/admin/pages.html">Pages</a>
            <a href="/admin/media.html" class="active">Media</a>
            <a href="/admin/settings.html">Settings</a>
            <a href="/admin/cloner.html">Website Cloner</a>
            <a href="#" onclick="logout()">Logout</a>
        </nav>
        <main class="content">
            <div class="header">
                <h1>Media Library</h1>
                <label class="btn-primary">
                    Upload File
                    <input type="file" id="file-input" style="display:none" onchange="uploadMedia(this.files[0])">
                </label>
            </div>
            <div class="media-grid" id="media-grid"></div>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>loadMedia();</script>
</body>
</html>'''
        
        with open(self.admin_dir / "pages" / "media.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_settings(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - CMS Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>CMS Admin</h2>
            <a href="/admin/dashboard.html">Dashboard</a>
            <a href="/admin/pages.html">Pages</a>
            <a href="/admin/media.html">Media</a>
            <a href="/admin/settings.html" class="active">Settings</a>
            <a href="/admin/cloner.html">Website Cloner</a>
            <a href="#" onclick="logout()">Logout</a>
        </nav>
        <main class="content">
            <h1>Settings</h1>
            <form id="settings-form">
                <div class="form-group">
                    <label>Site Name</label>
                    <input type="text" id="site-name" placeholder="My Website">
                </div>
                <div class="form-group">
                    <label>Site Description</label>
                    <textarea id="site-description" placeholder="Website description"></textarea>
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" id="contact-email" placeholder="contact@example.com">
                </div>
                <div class="form-group">
                    <label>Logo URL</label>
                    <input type="text" id="logo-url" placeholder="/assets/images/logo.png">
                </div>
                <button type="submit" class="btn-primary">Save Settings</button>
            </form>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>loadSettings();</script>
</body>
</html>'''
        
        with open(self.admin_dir / "pages" / "settings.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_admin_css(self):
        css = '''
* { margin: 0; padding: 0; box-sizing: border-box; }

body { font-family: system-ui, -apple-system, sans-serif; background: #f5f6fa; color: #333; }

.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

.login-container { width: 100%; max-width: 400px; padding: 20px; }

.login-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }

.login-box h1 { text-align: center; margin-bottom: 30px; color: #667eea; }

.login-box input { width: 100%; padding: 12px 15px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }

.login-box button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; transition: transform 0.2s; }

.login-box button:hover { transform: translateY(-2px); }

.login-info { margin-top: 15px; text-align: center; font-size: 12px; color: #666; }

.admin-layout { display: flex; min-height: 100vh; }

.sidebar { width: 250px; background: #2c3e50; color: white; padding: 20px; position: fixed; height: 100vh; overflow-y: auto; }

.sidebar h2 { margin-bottom: 30px; font-size: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }

.sidebar a { display: block; color: rgba(255,255,255,0.7); padding: 12px 15px; text-decoration: none; border-radius: 8px; margin-bottom: 5px; transition: all 0.2s; }

.sidebar a:hover, .sidebar a.active { background: rgba(255,255,255,0.1); color: white; }

.content { flex: 1; margin-left: 250px; padding: 30px; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }

.stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }

.stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }

.stat-card p { font-size: 32px; font-weight: bold; color: #667eea; }

.data-table { width: 100%; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }

.data-table th, .data-table td { padding: 15px 20px; text-align: left; }

.data-table th { background: #f8f9fa; font-weight: 600; color: #666; }

.data-table tr:not(:last-child) td { border-bottom: 1px solid #f0f0f0; }

.btn-primary { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: all 0.2s; }

.btn-primary:hover { background: #5568d3; transform: translateY(-2px); }

.btn-secondary { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }

.btn-danger { background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }

.modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; justify-content: center; align-items: center; z-index: 1000; }

.modal.active { display: flex; }

.modal-content { background: white; padding: 30px; border-radius: 12px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; }

.modal-content h2 { margin-bottom: 20px; }

.modal-content input, .modal-content textarea, .modal-content select { width: 100%; padding: 10px 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }

.modal-content textarea { min-height: 150px; resize: vertical; }

.form-group { margin-bottom: 20px; }

.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #666; }

.form-group input, .form-group textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }

.media-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }

.media-item { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }

.media-item img { width: 100%; height: 150px; object-fit: cover; }

.media-item-info { padding: 15px; }

.media-item-info p { font-size: 12px; color: #666; margin-top: 5px; }

.quick-actions { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }

.quick-actions h2 { margin-bottom: 15px; font-size: 18px; }

.quick-actions button { margin-right: 10px; margin-bottom: 10px; }

.error { color: #dc3545; margin-top: 10px; font-size: 14px; }

.cloner-form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); max-width: 600px; }

.cloner-form input, .cloner-form select { width: 100%; padding: 12px 15px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }

.progress-bar { width: 100%; height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden; margin-top: 20px; }

.progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.3s; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; }
'''
        
        with open(self.admin_dir / "assets" / "css" / "admin.css", 'w', encoding='utf-8') as f:
            f.write(css)
    
    def _generate_admin_js(self):
        js = '''
const API_BASE = '/api';

async function api(endpoint, method = 'GET', data = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    return response.json();
}

async function login(email, password) {
    const result = await api('/login', 'POST', { email, password });
    if (result.success) {
        localStorage.setItem('cms_token', result.token);
        localStorage.setItem('cms_user', JSON.stringify(result.user));
        location.href = '/admin/pages/dashboard.html';
    }
    return result;
}

function logout() {
    localStorage.removeItem('cms_token');
    localStorage.removeItem('cms_user');
    location.href = '/admin/index.html';
}

function checkAuth() {
    const token = localStorage.getItem('cms_token');
    if (!token) {
        location.href = '/admin/index.html';
        return false;
    }
    return true;
}

async function loadDashboard() {
    if (!checkAuth()) return;
    
    const stats = await api('/dashboard/stats');
    document.getElementById('pages-count').textContent = stats.pages || 0;
    document.getElementById('posts-count').textContent = stats.posts || 0;
    document.getElementById('media-count').textContent = stats.media || 0;
    document.getElementById('sites-count').textContent = stats.cloned_sites || 0;
}

async function loadPages() {
    if (!checkAuth()) return;
    
    const pages = await api('/pages');
    const tbody = document.getElementById('pages-table');
    
    tbody.innerHTML = pages.map(page => `
        <tr>
            <td>${page.title}</td>
            <td>/${page.slug}</td>
            <td><span class="badge">${page.status}</span></td>
            <td>
                <button class="btn-primary" onclick="editPage(${page.id})">Edit</button>
                <button class="btn-danger" onclick="deletePage(${page.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function loadMedia() {
    if (!checkAuth()) return;
    
    const media = await api('/media');
    const grid = document.getElementById('media-grid');
    
    grid.innerHTML = media.map(item => `
        <div class="media-item">
            <img src="${item.filepath}" alt="${item.alt_text || ''}">
            <div class="media-item-info">
                <strong>${item.filename}</strong>
                <p>${(item.size / 1024).toFixed(1)} KB</p>
                <button class="btn-danger" onclick="deleteMedia(${item.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function uploadMedia(file) {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/media/upload`, {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        loadMedia();
    }
}

async function deleteMedia(id) {
    if (!confirm('Delete this media?')) return;
    await api(`/media/${id}`, 'DELETE');
    loadMedia();
}

function showPageModal(page = null) {
    const modal = document.getElementById('page-modal');
    modal.classList.add('active');
    
    if (page) {
        document.getElementById('modal-title').textContent = 'Edit Page';
        document.getElementById('page-id').value = page.id;
        document.getElementById('page-title').value = page.title;
        document.getElementById('page-slug').value = page.slug;
        document.getElementById('page-content').value = page.content || '';
        document.getElementById('page-meta-title').value = page.meta_title || '';
        document.getElementById('page-meta-desc').value = page.meta_description || '';
        document.getElementById('page-status').value = page.status || 'draft';
    } else {
        document.getElementById('modal-title').textContent = 'Add Page';
        document.getElementById('page-form').reset();
        document.getElementById('page-id').value = '';
    }
}

async function editPage(id) {
    const page = await api(`/pages/${id}`);
    showPageModal(page);
}

async function deletePage(id) {
    if (!confirm('Delete this page?')) return;
    await api(`/pages/${id}`, 'DELETE');
    loadPages();
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
}

async function savePage(formData) {
    const id = document.getElementById('page-id').value;
    const data = {
        title: document.getElementById('page-title').value,
        slug: document.getElementById('page-slug').value,
        content: document.getElementById('page-content').value,
        meta_title: document.getElementById('page-meta-title').value,
        meta_description: document.getElementById('page-meta-desc').value,
        status: document.getElementById('page-status').value
    };
    
    if (id) {
        await api(`/pages/${id}`, 'PUT', data);
    } else {
        await api('/pages', 'POST', data);
    }
    
    closeModal();
    loadPages();
}

async function loadSettings() {
    if (!checkAuth()) return;
    
    const settings = await api('/settings');
    document.getElementById('site-name').value = settings['site_name'] || '';
    document.getElementById('site-description').value = settings['site_description'] || '';
    document.getElementById('contact-email').value = settings['contact_email'] || '';
    document.getElementById('logo-url').value = settings['logo_url'] || '';
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

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const result = await login(email, password);
    if (!result.success) {
        document.getElementById('error').textContent = 'Invalid credentials';
    }
});

document.getElementById('page-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    savePage();
});

document.getElementById('settings-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    saveSettings();
});
'''
        
        with open(self.admin_dir / "assets" / "js" / "admin.js", 'w', encoding='utf-8') as f:
            f.write(js)
    
    def _generate_database(self):
        db_sql = '''
-- CMS Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    meta_title TEXT,
    meta_description TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,
    featured_image TEXT,
    status TEXT DEFAULT 'draft',
    category TEXT,
    author TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    mimetype TEXT,
    size INTEGER,
    alt_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    items TEXT,
    location TEXT DEFAULT 'main',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin user
INSERT OR IGNORE INTO users (email, password, role) VALUES ('admin@admin.com', 'admin123', 'admin');

-- Default settings
INSERT OR IGNORE INTO settings (key, value) VALUES ('site_name', 'My CMS Website');
INSERT OR IGNORE INTO settings (key, value) VALUES ('site_description', 'A modern content management system');
INSERT OR IGNORE INTO settings (key, value) VALUES ('contact_email', 'admin@example.com');
'''
        
        with open(self.project_path / "database" / "schema.sql", 'w', encoding='utf-8') as f:
            f.write(db_sql)
    
    def _generate_api(self):
        api_js = '''
const API_BASE = '/api';

class CMS {
    constructor() {
        this.pages = [];
        this.posts = [];
        this.media = [];
        this.settings = {};
    }

    async init() {
        await this.loadPages();
        await this.loadPosts();
        await this.loadMedia();
        await this.loadSettings();
    }

    async loadPages() {
        const response = await fetch(`${API_BASE}/pages`);
        this.pages = await response.json();
    }

    async loadPosts() {
        const response = await fetch(`${API_BASE}/posts`);
        this.posts = await response.json();
    }

    async loadMedia() {
        const response = await fetch(`${API_BASE}/media`);
        this.media = await response.json();
    }

    async loadSettings() {
        const response = await fetch(`${API_BASE}/settings`);
        this.settings = await response.json();
    }

    async savePage(page) {
        const method = page.id ? 'PUT' : 'POST';
        const url = page.id ? `${API_BASE}/pages/${page.id}` : `${API_BASE}/pages`;
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(page)
        });
        
        return response.json();
    }

    getPage(slug) {
        return this.pages.find(p => p.slug === slug);
    }

    getPublishedPages() {
        return this.pages.filter(p => p.status === 'published');
    }

    async uploadMedia(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/media/upload`, {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    }
}

window.CMS = CMS;
'''
        
        with open(self.public_dir / "assets" / "js" / "cms-api.js", 'w', encoding='utf-8') as f:
            f.write(api_js)
    
    def _generate_readme(self):
        readme = f'''# Cloned Website - {self.base_url}

This website was cloned using the Website Cloner AI System.

## Project Structure

```
{self.project_path.name}/
├── public/
│   ├── index.html
│   ├── pages/
│   └── assets/
│       ├── css/
│       ├── js/
│       └── images/
├── admin/
│   ├── index.html
│   ├── pages/
│   └── assets/
├── database/
│   └── schema.sql
└── README.md
```

## Installation

1. Upload all files to your Hostinger hosting (public_html folder)
2. Import the database schema from `database/schema.sql`
3. Configure your database connection
4. Access the admin panel at `/admin`

## Default Admin Login

- Email: admin@admin.com
- Password: admin123

## Features

- Editable content blocks
- Image editing
- Page management
- Media library
- SEO settings
- Website cloning from any URL

## Deployment on Hostinger

1. Log into Hostinger hPanel
2. Go to File Manager
3. Navigate to public_html
4. Upload and extract the ZIP file
5. Create database and import schema
6. Update database configuration
7. Access your site!

## License

This is a demonstration project. Please respect copyright and intellectual property rights when cloning websites.
'''
        
        with open(self.project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme)
    
    def _url_to_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        
        if not path or path == '':
            return 'index'
        
        path = path.replace('/', '-')
        path = re.sub(r'[^a-zA-Z0-9\-_]', '-', path)
        path = re.sub(r'-+', '-', path)
        
        return path[:50]
