"""
Enhanced Crawler Agent for Website Cloning
Production-grade with Playwright support
"""
import sqlite3
import json
import re
import asyncio
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Optional
from datetime import datetime

class CrawlerAgent:
    def __init__(self, base_url: str, project_id: str, max_pages: int = 50, max_depth: int = 3):
        self.base_url = base_url
        self.project_id = project_id
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.domain = urlparse(base_url).netloc
        self.visited: Set[str] = set()
        self.pages_data: List[Dict] = []
        self.assets: Set[str] = set()
        self.project_dir = Path(__file__).parent.parent.parent.parent / "projects" / project_id
    
    def get_db(self):
        conn = sqlite3.connect(str(Path(__file__).parent.parent.parent.parent / "database" / "platform.db"))
        conn.row_factory = sqlite3.Row
        return conn
    
    async def run(self):
        try:
            await self._update_status("crawling", 0)
            
            await self._crawl_page(self.base_url, depth=0)
            
            await self._update_status("processing", 80)
            await self._process_and_save()
            
            await self._update_status("completed", 100)
            
        except Exception as e:
            await self._update_status("failed", 0, str(e))
    
    async def _crawl_page(self, url: str, depth: int = 0):
        if url in self.visited or depth > self.max_depth or len(self.visited) >= self.max_pages:
            return
        
        self.visited.add(url)
        
        try:
            page_data = await self._fetch_with_playwright(url)
            
            if page_data:
                self.pages_data.append(page_data)
                
                for asset in page_data.get('assets', []):
                    if asset and not asset.startswith('data:'):
                        self.assets.add(asset)
                
                links_to_follow = []
                for link in page_data.get('links', []):
                    if self._should_follow(link):
                        links_to_follow.append(link)
                
                for link in links_to_follow[:10]:
                    await self._crawl_page(link, depth + 1)
                
                progress = int((len(self.visited) / self.max_pages) * 70)
                await self._update_progress(progress)
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            fallback_data = await self._fetch_with_aiohttp(url)
            if fallback_data:
                self.pages_data.append(fallback_data)
    
    async def _fetch_with_playwright(self, url: str) -> Optional[Dict]:
        try:
            script = f'''
import asyncio
from playwright.async_api import async_playwright
import json

async def fetch(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
            title = await page.title()
            
            links = await page.evaluate("""
                () => {{
                    const links = [];
                    document.querySelectorAll('a[href]').forEach(a => {{
                        links.push(a.href);
                    }});
                    return links;
                }}
            """)
            
            assets = await page.evaluate("""
                () => {{
                    const assets = [];
                    document.querySelectorAll('img[src], script[src], link[href]').forEach(el => {{
                        const src = el.src || el.href;
                        if (src && !src.startsWith('data:')) {{
                            assets.push(src);
                        }}
                    }});
                    return assets;
                }}
            """)
            
            return json.dumps({{
                "html": html,
                "title": title,
                "links": links,
                "assets": assets,
                "status": 200
            }})
        except Exception as e:
            return json.dumps({{"error": str(e)}})
        finally:
            await browser.close()

result = asyncio.run(fetch("{url}"))
print(result)
'''
            
            result = subprocess.run(
                ['python', '-c', script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                if 'error' not in data:
                    return {
                        'url': url,
                        'html': data.get('html', ''),
                        'title': data.get('title', ''),
                        'links': data.get('links', []),
                        'assets': data.get('assets', [])
                    }
        
        except Exception as e:
            print(f"Playwright fetch failed for {url}: {e}")
        
        return None
    
    async def _fetch_with_aiohttp(self, url: str) -> Optional[Dict]:
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        links = []
                        for a in soup.find_all('a', href=True):
                            href = a['href']
                            full_url = urljoin(url, href)
                            if urlparse(full_url).netloc == self.domain:
                                links.append(full_url)
                        
                        assets = []
                        for tag in soup.find_all(['img', 'script', 'link']):
                            src = tag.get('src') or tag.get('href')
                            if src and not src.startswith('data:'):
                                assets.append(urljoin(url, src))
                        
                        return {
                            'url': url,
                            'html': html,
                            'title': soup.title.string if soup.title else '',
                            'links': list(set(links)),
                            'assets': list(set(assets))
                        }
        
        except Exception as e:
            print(f"aiohttp fetch failed for {url}: {e}")
        
        return None
    
    def _should_follow(self, url: str) -> bool:
        if not url:
            return False
        
        parsed = urlparse(url)
        
        if parsed.netloc != self.domain:
            return False
        
        if url in self.visited:
            return False
        
        if any(ext in parsed.path for ext in ['.pdf', '.zip', '.mp3', '.mp4', '.avi', '.exe']):
            return False
        
        if any(x in parsed.path for x in ['/cdn-cgi/', '/wp-admin/', '/wp-includes/', '/wp-content/']):
            return True
        
        return True
    
    async def _process_and_save(self):
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        (self.project_dir / "frontend").mkdir(exist_ok=True)
        (self.project_dir / "frontend" / "src").mkdir(exist_ok=True)
        (self.project_dir / "frontend" / "public").mkdir(exist_ok=True)
        (self.project_dir / "backend").mkdir(exist_ok=True)
        (self.project_dir / "admin").mkdir(exist_ok=True)
        (self.project_dir / "database").mkdir(exist_ok=True)
        (self.project_dir / "assets").mkdir(exist_ok=True)
        
        index_created = False
        
        for i, page in enumerate(self.pages_data):
            if not index_created:
                html = self._process_html(page['html'], page['url'])
                await self._save_page("frontend/index.html", page['title'] or 'Home', html, page['url'])
                index_created = True
            else:
                page_name = self._url_to_filename(page['url'])
                html = self._process_html(page['html'], page['url'])
                await self._save_page(f"frontend/{page_name}.html", page['title'] or page_name, html, page['url'])
        
        await self._generate_backend_files()
        await self._generate_admin_files()
        await self._generate_database_schema()
        await self._generate_readme()
        
        conn = self.get_db()
        c = conn.cursor()
        c.execute("""
            UPDATE projects SET pages_count = ?
            WHERE id = ?
        """, (len(self.pages_data), self.project_id))
        conn.commit()
        conn.close()
    
    def _process_html(self, html: str, url: str) -> str:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'li']):
            text = tag.get_text(strip=True)
            if text:
                tag['data-cms-editable'] = 'true'
        
        for img in soup.find_all('img'):
            img['data-cms-editable'] = 'image'
        
        head = soup.find('head')
        if head:
            cms_css = soup.new_tag('link', rel='stylesheet', href='/frontend/src/cms.css')
            head.append(cms_css)
            
            cms_js = soup.new_tag('script', src='/frontend/src/cms.js')
            head.append(cms_js)
        
        return str(soup)
    
    async def _save_page(self, filepath: str, title: str, content: str, source_url: str):
        full_path = self.project_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        conn = self.get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO pages (project_id, title, slug, content, file_path, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.project_id, title, filepath, content, filepath, len(content)))
        conn.commit()
        conn.close()
    
    async def _generate_backend_files(self):
        backend_main = f'''"""Cloned Website Backend"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3

app = FastAPI(title="Cloned Site API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PageContent(BaseModel):
    slug: str
    content: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

def get_db():
    conn = sqlite3.connect('database/content.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    return {{"message": "API Running", "source": "{self.base_url}"}}

@app.get("/api/pages")
async def get_pages():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM pages")
    pages = [dict(row) for row in c.fetchall()]
    conn.close()
    return pages

@app.post("/api/pages")
async def save_page(page: PageContent):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO pages (slug, content, meta_title, meta_description)
        VALUES (?, ?, ?, ?)
    """, (page.slug, page.content, page.meta_title, page.meta_description))
    conn.commit()
    conn.close()
    return {{"success": True}}

@app.get("/api/pages/{{slug}}")
async def get_page(slug: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM pages WHERE slug = ?", (slug,))
    page = c.fetchone()
    conn.close()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return dict(page)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        full_path = self.project_dir / "backend" / "main.py"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(backend_main)
        
        cms_css = '''/* CMS Editable Styles */
:root {
    --cms-primary: #3b82f6;
    --cms-secondary: #10b981;
    --cms-bg: rgba(59, 130, 246, 0.05);
}

[data-cms-editable] {
    outline: 2px dashed transparent;
    outline-offset: 4px;
    transition: all 0.2s;
    cursor: text;
}

[data-cms-editable]:hover {
    outline-color: var(--cms-primary);
    background: var(--cms-bg);
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
    z-index: 9999;
}

.cms-btn {
    background: var(--cms-primary);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 25px;
    cursor: pointer;
}
'''
        
        full_path = self.project_dir / "frontend" / "src" / "cms.css"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(cms_css)
        
        cms_js = '''/* CMS Client JavaScript */
let editMode = false;

function toggleEditMode() {
    editMode = !editMode;
    document.body.classList.toggle('cms-edit-mode', editMode);
}

document.addEventListener('click', (e) => {
    if (editMode && e.target.hasAttribute('data-cms-editable')) {
        e.preventDefault();
        const original = e.target.textContent;
        const newText = prompt('Edit content:', original);
        if (newText !== null) {
            e.target.textContent = newText;
        }
    }
});

window.toggleEditMode = toggleEditMode;
'''
        
        full_path = self.project_dir / "frontend" / "src" / "cms.js"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(cms_js)
    
    async def _generate_admin_files(self):
        admin_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <link rel="stylesheet" href="/admin/src/styles.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>CMS Admin</h2>
            <nav>
                <a href="/admin/" class="active">Dashboard</a>
                <a href="/admin/pages.html">Pages</a>
                <a href="/admin/settings.html">Settings</a>
            </nav>
        </aside>
        <main class="content">
            <h1>Dashboard</h1>
            <p>Manage your cloned website</p>
        </main>
    </div>
    <script src="/admin/src/app.js"></script>
</body>
</html>'''
        
        full_path = self.project_dir / "admin" / "index.html"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(admin_html)
    
    async def _generate_database_schema(self):
        schema = f'''-- Cloned Website Database Schema
-- Source: {self.base_url}

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    meta_title TEXT,
    meta_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
        
        full_path = self.project_dir / "database" / "schema.sql"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(schema)
    
    async def _generate_readme(self):
        readme = f'''# Cloned Website

Source: {self.base_url}
Cloned: {datetime.now().isoformat()}

## Structure

```
/frontend   - Cloned frontend files
/backend    - Backend API
/admin     - CMS Admin Panel
/database  - Database schema
/assets    - Static assets
```

## Setup

```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```

## Admin

Access /admin/ for the CMS dashboard.
'''
        
        full_path = self.project_dir / "README.md"
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(readme)
    
    def _url_to_filename(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path or path == '':
            return 'page'
        
        path = path.replace('/', '-')
        path = re.sub(r'[^a-zA-Z0-9\-_]', '-', path)
        path = re.sub(r'-+', '-', path)
        
        return path[:50] or 'page'
    
    async def _update_status(self, status: str, progress: int, error: str = None):
        conn = self.get_db()
        c = conn.cursor()
        
        if status == "completed":
            c.execute("""
                UPDATE projects SET status = ?, progress = ?,
                completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, progress, self.project_id))
        elif status == "failed":
            c.execute("""
                UPDATE projects SET status = ?, error_message = ?
                WHERE id = ?
            """, (status, error, self.project_id))
        else:
            c.execute("""
                UPDATE projects SET status = ?, progress = ?
                WHERE id = ?
            """, (status, progress, self.project_id))
        
        conn.commit()
        conn.close()
    
    async def _update_progress(self, progress: int):
        conn = self.get_db()
        c = conn.cursor()
        c.execute("""
            UPDATE projects SET progress = ?
            WHERE id = ?
        """, (progress, self.project_id))
        conn.commit()
        conn.close()
