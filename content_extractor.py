<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>CMS Admin</h2>
            <nav>
                <a href="/admin/pages/dashboard.html">Dashboard</a>
                <a href="/admin/pages/pages.html">Pages</a>
                <a href="/admin/pages/media.html">Media</a>
                <a href="/admin/pages/projects.html" class="active">Projects</a>
                <a href="/admin/pages/settings.html">Settings</a>
                <a href="#" onclick="logout()">Logout</a>
            </nav>
        </aside>
        <main class="content">
            <div class="header">
                <h1>Projects</h1>
                <button class="btn-primary" onclick="location.reload()">Refresh</button>
            </div>
            <div id="projects-list">
                <p style="padding:20px;text-align:center;color:#666;">Loading...</p>
            </div>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>
        if (checkAuth()) {
            loadProjects();
        }
    </script>
</body>
</html>
