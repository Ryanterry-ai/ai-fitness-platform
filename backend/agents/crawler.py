"""
Website Crawler Agent
Crawls and downloads website content
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import re
import hashlib
from typing import List, Dict, Set
import os

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 50, max_depth: int = 3):
        self.base_url = base_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.pages_data: List[Dict] = []
        self.assets: List[Dict] = []
        self.domain = urlparse(base_url).netloc
        self.scheme = urlparse(base_url).scheme
        
    def get_domain_name(self) -> str:
        name = self.domain.replace('www.', '').replace('.', '_')
        return f"cloned_{name}_{hashlib.md5(self.base_url.encode()).hexdigest()[:8]}"
    
    async def fetch_page(self, session: aiohttp.ClientSession, url: str, depth: int = 0) -> Dict:
        if url in self.visited or depth > self.max_depth or len(self.visited) >= self.max_pages:
            return None
            
        self.visited.add(url)
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    return None
                    
                content = await response.text()
                content_type = response.headers.get('content-type', '')
                
                page_data = {
                    'url': url,
                    'content': content,
                    'content_type': content_type,
                    'status': response.status,
                    'depth': depth
                }
                
                if 'text/html' in content_type:
                    soup = BeautifulSoup(content, 'html.parser')
                    page_data['soup'] = soup
                    page_data['title'] = soup.title.string if soup.title else 'Untitled'
                    page_data['links'] = self._extract_links(soup, url)
                    page_data['assets'] = self._extract_assets(soup, url)
                    page_data['scripts'] = self._extract_scripts(soup, url)
                    page_data['styles'] = self._extract_styles(soup, url)
                    
                return page_data
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            if parsed.netloc == self.domain and full_url not in self.visited:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                links.append(clean_url)
                
        return list(set(links))
    
    def _extract_assets(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        assets = []
        patterns = ['img', 'video', 'audio', 'source', 'embed', 'object', 'iframe']
        
        for tag_name in patterns:
            for tag in soup.find_all(tag_name):
                url = tag.get('src') or tag.get('href') or tag.get('data')
                if url and not url.startswith('data:'):
                    full_url = urljoin(base_url, url)
                    asset_type = tag_name
                    
                    if tag_name == 'img':
                        asset_type = 'image'
                        alt = tag.get('alt', '')
                    else:
                        alt = ''
                        
                    assets.append({
                        'url': full_url,
                        'type': asset_type,
                        'alt': alt,
                        'tag': tag_name
                    })
                    
        return assets
    
    def _extract_scripts(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        scripts = []
        for script in soup.find_all('script', src=True):
            full_url = urljoin(base_url, script['src'])
            scripts.append({
                'url': full_url,
                'type': 'external'
            })
        return scripts
    
    def _extract_styles(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        styles = []
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                full_url = urljoin(base_url, link['href'])
                styles.append({
                    'url': full_url,
                    'type': 'external'
                })
        return styles
    
    async def crawl_page(self, session: aiohttp.ClientSession, url: str, depth: int = 0):
        page_data = await self.fetch_page(session, url, depth)
        
        if page_data:
            self.pages_data.append(page_data)
            
            if page_data.get('assets'):
                self.assets.extend(page_data['assets'])
            
            if page_data.get('links'):
                tasks = []
                for link in page_data['links'][:10]:
                    if link not in self.visited:
                        tasks.append(self.crawl_page(session, link, depth + 1))
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
    
    async def crawl(self) -> List[Dict]:
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            await self.crawl_page(session, self.base_url, 0)
        
        return self.pages_data
    
    def download_asset(self, asset_url: str, download_dir: Path) -> str:
        parsed = urlparse(asset_url)
        filename = parsed.path.split('/')[-1] or f"asset_{hashlib.md5(asset_url.encode()).hexdigest()[:8]}"
        
        if not filename or '.' not in filename:
            ext = self._get_extension(asset_url)
            filename = f"{hashlib.md5(asset_url.encode()).hexdigest()[:8]}{ext}"
        
        local_path = download_dir / filename
        return f"/assets/{filename}", local_path
    
    def _get_extension(self, url: str) -> str:
        path = urlparse(url).path
        if '.' in path:
            return '.' + path.split('.')[-1]
        return '.bin'
