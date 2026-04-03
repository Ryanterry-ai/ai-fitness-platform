"""
Playwright-Based Website Crawler Agent
Production-grade crawler using Playwright
"""
import asyncio
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib
import sqlite3
from typing import Set, Dict, List
import json

class PlaywrightCrawler:
    def __init__(self, base_url: str, project_id: str, max_pages: int = 50, max_depth: int = 3):
        self.base_url = base_url
        self.project_id = project_id
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.domain = urlparse(base_url).netloc
        self.scheme = urlparse(base_url).scheme
        self.visited: Set[str] = set()
        self.pages_data: List[Dict] = []
        self.assets: Set[str] = set()
        self.project_dir = Path(__file__).parent.parent.parent / "cloned_sites" / project_id
        
    def get_db(self):
        conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "database" / "cloner.db"))
        conn.row_factory = sqlite3.Row
        return conn
    
    async def run(self):
        try:
            await self._update_project_status("crawling", 0)
            
            await self._crawl_page(self.base_url, depth=0)
            
            await self._update_project_status("processing", 80)
            
            await self._process_and_save()
            
            await self._update_project_status("completed", 100)
            
        except Exception as e:
            await self._update_project_status("failed", 0, str(e))
    
    async def _crawl_page(self, url: str, depth: int = 0):
        if url in self.visited or depth > self.max_depth or len(self.visited) >= self.max_pages:
            return
        
        self.visited.add(url)
        
        try:
            import subprocess
            result = subprocess.run([
                'python', '-c', f'''
import asyncio
from playwright.async_api import async_playwright

async def fetch_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
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
                        assets.push(el.src || el.href);
                    }});
                    return assets;
                }}
            """)
            
            return {{
                "html": html,
                "title": title,
                "links": links,
                "assets": assets,
                "status": response.status if response else 200
            }}
        except Exception as e:
            return {{"error": str(e)}}
        finally:
            await browser.close()

result = asyncio.run(fetch_page("{url}"))
print(json.dumps(result))
'''
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                if 'error' not in data:
                    page_info = {
                        'url': url,
                        'html': data.get('html', ''),
                        'title': data.get('title', ''),
                        'status': data.get('status', 200),
                        'depth': depth,
                        'links': data.get('links', []),
                        'assets': data.get('assets', [])
                    }
                    
                    self.pages_data.append(page_info)
                    
                    for asset in data.get('assets', []):
                        if asset and not asset.startswith('data:'):
                            self.assets.add(asset)
                    
                    links_to_follow = []
                    for link in data.get('links', []):
                        if self._should_follow(link):
                            links_to_follow.append(link)
                    
                    for link in links_to_follow[:10]:
                        await self._crawl_page(link, depth + 1)
                    
                    progress = int((len(self.visited) / self.max_pages) * 70)
                    await self._update_progress(progress)
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def _should_follow(self, url: str) -> bool:
        if not url:
            return False
        
        parsed = urlparse(url)
        
        if parsed.netloc != self.domain:
            return False
        
        if url in self.visited:
            return False
        
        if any(ext in parsed.path for ext in ['.pdf', '.zip', '.mp3', '.mp4', '.avi']):
            return False
        
        return True
    
    async def _process_and_save(self):
        public_dir = self.project_dir / "public"
        assets_dir = public_dir / "assets"
        
        for d in [self.project_dir, public_dir, assets_dir, assets_dir / "css", 
                  assets_dir / "js", assets_dir / "images", assets_dir / "fonts"]:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        index_created = False
        for page in self.pages_data:
            if not index_created:
                index_path = public_dir / "index.html"
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(page['html'])
                index_created = True
            else:
                page_name = self._url_to_filename(page['url'])
                page_path = public_dir / f"{page_name}.html"
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(page['html'])
            
            conn = self.get_db()
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO pages (title, slug, content, meta_title, project_id)
                VALUES (?, ?, ?, ?, ?)
            """, (page['title'], self._url_to_filename(page['url']), page['html'],
                  page['title'], self.project_id))
            conn.commit()
            conn.close()
        
        await self._update_project_status("saving_assets", 90)
    
    def _url_to_filename(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path or path == '':
            return 'index'
        
        path = path.replace('/', '-')
        path = re.sub(r'[^a-zA-Z0-9\-_]', '-', path)
        path = re.sub(r'-+', '-', path)
        
        return path[:50]
    
    async def _update_project_status(self, status: str, progress: int, error: str = None):
        conn = self.get_db()
        c = conn.cursor()
        
        if status == "completed":
            c.execute("""
                UPDATE projects SET status = ?, progress = ?, pages_count = ?, 
                assets_count = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, progress, len(self.pages_data), len(self.assets), self.project_id))
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
        c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, self.project_id))
        conn.commit()
        conn.close()
