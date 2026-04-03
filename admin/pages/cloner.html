<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Cloner - CMS Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
    <style>
        .cloner-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .cloner-section h2 { margin-bottom: 20px; color: #2c3e50; }
        .cloner-form input, .cloner-form select { width: 100%; padding: 12px 15px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .cloner-form button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .cloner-form button:hover { opacity: 0.9; }
        .cloner-form button:disabled { opacity: 0.5; cursor: not-allowed; }
        .cloned-sites { margin-top: 30px; }
        .site-item { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .site-info h4 { margin: 0 0 5px 0; color: #2c3e50; }
        .site-info p { margin: 0; font-size: 12px; color: #666; }
        .site-actions a { background: #667eea; color: white; padding: 8px 15px; border-radius: 6px; text-decoration: none; font-size: 12px; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <h2>CMS Admin</h2>
            <a href="/admin/pages/dashboard.html">Dashboard</a>
            <a href="/admin/pages/pages.html">Pages</a>
            <a href="/admin/pages/media.html">Media</a>
            <a href="/admin/pages/settings.html">Settings</a>
            <a href="/admin/pages/cloner.html" class="active">Website Cloner</a>
            <a href="#" onclick="logout()">Logout</a>
        </nav>
        <main class="content">
            <h1>Website Cloner</h1>
            
            <div class="cloner-section">
                <h2>Clone New Website</h2>
                <form class="cloner-form" onsubmit="startClone(event)">
                    <input type="url" id="clone-url" placeholder="https://example.com" required>
                    <select id="max-pages">
                        <option value="10">10 pages (Quick)</option>
                        <option value="50" selected>50 pages (Normal)</option>
                        <option value="100">100 pages (Large)</option>
                        <option value="200">200 pages (Full Site)</option>
                    </select>
                    <button type="submit" id="clone-btn">Start Cloning</button>
                </form>
                
                <div class="progress-bar" id="progress-bar" style="display: none; margin-top: 20px;">
                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                </div>
                <p class="progress-text" id="progress-text" style="display: none;"></p>
            </div>
            
            <div class="cloner-section cloned-sites">
                <h2>Cloned Sites</h2>
                <div id="sites-list"></div>
            </div>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>
        async function startClone(e) {
            e.preventDefault();
            
            const url = document.getElementById('clone-url').value;
            const maxPages = document.getElementById('max-pages').value;
            const btn = document.getElementById('clone-btn');
            
            btn.disabled = true;
            btn.textContent = 'Cloning...';
            document.getElementById('progress-bar').style.display = 'block';
            document.getElementById('progress-text').style.display = 'block';
            
            try {
                const response = await fetch('/api/crawl', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, max_pages: parseInt(maxPages), max_depth: 3 })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('progress-fill').style.width = '100%';
                    document.getElementById('progress-text').textContent = 'Complete! Cloned ' + data.pages_count + ' pages';
                    loadClonedSites();
                    document.getElementById('clone-url').value = '';
                } else {
                    throw new Error('Clone failed');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
            
            btn.disabled = false;
            btn.textContent = 'Start Cloning';
        }
        
        async function loadClonedSites() {
            const sites = await api('/cloned-sites');
            const container = document.getElementById('sites-list');
            
            if (sites.length === 0) {
                container.innerHTML = '<p>No websites cloned yet. Start by entering a URL above.</p>';
                return;
            }
            
            container.innerHTML = sites.map(site => `
                <div class="site-item">
                    <div class="site-info">
                        <h4>${site.name}</h4>
                        <p>Source: ${site.url}</p>
                        <p>Cloned: ${new Date(site.created_at).toLocaleDateString()}</p>
                    </div>
                    <div class="site-actions">
                        <a href="/api/cloned-sites/${site.id}/download">Download ZIP</a>
                    </div>
                </div>
            `).join('');
        }
        
        loadClonedSites();
    </script>
</body>
</html>
