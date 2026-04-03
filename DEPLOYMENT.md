# Deployment Guide - Hostinger

## Quick Deployment

### Step 1: Prepare Your Files

1. Clone the website using the web interface or API
2. Download the ZIP file from the admin panel
3. Or create a ZIP manually from the `cloned_sites` folder

### Step 2: Upload to Hostinger

#### Method A: File Manager

1. Login to [Hostinger hPanel](https://hPanel.hostinger.com)
2. Navigate to **Files** → **File Manager**
3. Open the `public_html` folder
4. Click **Upload** button
5. Select your ZIP file
6. Right-click the ZIP and select **Extract**

#### Method B: FTP

1. Get FTP credentials from Hostinger
2. Connect using FileZilla or similar
3. Navigate to `public_html`
4. Upload all files

### Step 3: Database Setup

1. In hPanel, go to **Databases** → **MySQL Databases**
2. Create a new database
3. Note down: database name, username, password, hostname
4. Go to **phpMyAdmin**
5. Import `database/schema.sql`

### Step 4: Configure Application

Create a `config.php` or update the Python code to use your database:

```python
# Update database connection in backend/main.py
DATABASE_URL = "mysql://username:password@localhost/dbname"
```

### Step 5: Update Dependencies

Hostinger supports Python. Add this to your project:

```txt
# requirements.txt (already included)
fastapi==0.109.0
uvicorn==0.27.0
```

### Step 6: Set Up Python App

1. In hPanel, go to **Python** → **Python App**
2. Click **Create Application**
3. Set application root to your project folder
4. Set startup command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
5. Set Python version to 3.9+

### Step 7: Domain Configuration

1. Go to **Domains** → **DNS Zone**
2. Add A record pointing to your server IP
3. Wait for DNS propagation (up to 24 hours)

## cPanel Deployment

### Alternative: Static HTML Export

For pure HTML/CSS/JS hosting (no Python backend):

1. Clone website using the tool
2. Go to admin panel → Settings
3. Export as static HTML
4. Upload to cPanel File Manager

### Using .htaccess for SPA Routing

```apache
RewriteEngine On
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [L]
```

## Troubleshooting

### 404 Errors
- Check file permissions (644 for files, 755 for folders)
- Verify .htaccess is present

### Database Connection Errors
- Verify MySQL credentials
- Check hostname (usually `localhost`)
- Ensure database user has proper permissions

### Python Import Errors
- Check `requirements.txt` is in project root
- Verify Python version compatibility
- Restart the Python application

### Static Files Not Loading
- Check file paths are relative, not absolute
- Verify `public/` folder structure
- Clear browser cache

## Security Checklist

- [ ] Change default admin password
- [ ] Enable HTTPS (free SSL from Hostinger)
- [ ] Set proper file permissions
- [ ] Remove any test/debug files
- [ ] Configure .htaccess for security

## Performance Tips

- Enable GZIP compression
- Minify CSS/JS files
- Use CDN for static assets
- Enable browser caching
- Optimize images before upload

## Support

For Hostinger-specific issues:
- [Hostinger Help Center](https://www.hostinger.com/tutorials)
- Live chat support available 24/7
