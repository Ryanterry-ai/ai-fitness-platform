<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - AI Website Builder</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>AI Builder</h2>
            <nav>
                <a href="/admin/pages/dashboard.html" class="active">Dashboard</a>
                <a href="/admin/pages/pages.html">Pages</a>
                <a href="/admin/pages/media.html">Media</a>
                <a href="/admin/pages/projects.html">Projects</a>
                <a href="/admin/pages/settings.html">Settings</a>
                <a href="#" onclick="logout()">Logout</a>
            </nav>
        </aside>
        <main class="content">
            <div class="header">
                <h1>Dashboard</h1>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Projects</h3>
                    <p id="pages-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>Pages</h3>
                    <p id="posts-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>Media</h3>
                    <p id="media-count">0</p>
                </div>
            </div>
            <div class="quick-actions">
                <h2>Quick Actions</h2>
                <button onclick="location.href='/'">Main App</button>
                <button onclick="location.href='/admin/pages/projects.html'">View Projects</button>
                <button onclick="location.href='/api/docs'">API Docs</button>
            </div>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>
        if (checkAuth()) { loadDashboard(); }
    </script>
</body>
</html>
