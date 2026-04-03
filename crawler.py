<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>AI Builder</h2>
            <nav>
                <a href="/admin/pages/dashboard.html">Dashboard</a>
                <a href="/admin/pages/pages.html">Pages</a>
                <a href="/admin/pages/media.html">Media</a>
                <a href="/admin/pages/projects.html">Projects</a>
                <a href="/admin/pages/settings.html" class="active">Settings</a>
                <a href="#" onclick="logout()">Logout</a>
            </nav>
        </aside>
        <main class="content">
            <div class="header">
                <h1>Settings</h1>
            </div>
            <form id="settings-form" style="max-width:500px;">
                <div class="form-group">
                    <label>Site Name</label>
                    <input type="text" id="site-name">
                </div>
                <div class="form-group">
                    <label>Site Description</label>
                    <textarea id="site-description" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" id="contact-email">
                </div>
                <button type="submit" class="btn-primary">Save</button>
            </form>
        </main>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>
        if (checkAuth()) { loadSettings(); }
    </script>
</body>
</html>
