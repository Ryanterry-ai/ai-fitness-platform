<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pages - Admin</title>
    <link rel="stylesheet" href="/admin/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>AI Builder</h2>
            <nav>
                <a href="/admin/pages/dashboard.html">Dashboard</a>
                <a href="/admin/pages/pages.html" class="active">Pages</a>
                <a href="/admin/pages/media.html">Media</a>
                <a href="/admin/pages/projects.html">Projects</a>
                <a href="/admin/pages/settings.html">Settings</a>
                <a href="#" onclick="logout()">Logout</a>
            </nav>
        </aside>
        <main class="content">
            <div class="header">
                <h1>Pages</h1>
                <button class="btn-primary" onclick="showPageModal()">Add Page</button>
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
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" id="page-title" required>
                </div>
                <div class="form-group">
                    <label>Slug</label>
                    <input type="text" id="page-slug" required>
                </div>
                <div class="form-group">
                    <label>Content</label>
                    <textarea id="page-content" rows="6"></textarea>
                </div>
                <button type="submit" class="btn-primary">Save</button>
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
            </form>
        </div>
    </div>
    <script src="/admin/assets/js/admin.js"></script>
    <script>
        if (checkAuth()) { loadPages(); }
    </script>
</body>
</html>
