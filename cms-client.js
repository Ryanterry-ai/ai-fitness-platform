"""
Post Generator Agent
Generates blog posts and content
"""
from typing import Dict, List
import hashlib
from datetime import datetime

class PostGenerator:
    def __init__(self, base_url: str = ''):
        self.base_url = base_url
        self.posts: List[Dict] = []
    
    def generate_post(self, title: str, content: str, author: str = 'Admin', 
                      category: str = 'General', excerpt: str = None) -> Dict:
        slug = self._generate_slug(title)
        
        post = {
            'id': len(self.posts) + 1,
            'title': title,
            'slug': slug,
            'content': content,
            'excerpt': excerpt or content[:150] + '...',
            'author': author,
            'category': category,
            'featured_image': '',
            'status': 'draft',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': [],
            'views': 0
        }
        
        self.posts.append(post)
        return post
    
    def _generate_slug(self, title: str) -> str:
        slug = title.lower()
        slug = slug.replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        slug = slug.strip('-')
        return f"{slug}-{hashlib.md5(title.encode()).hexdigest()[:6]}"
    
    def get_post(self, slug: str) -> Dict:
        for post in self.posts:
            if post['slug'] == slug:
                return post
        return None
    
    def get_posts_by_category(self, category: str) -> List[Dict]:
        return [p for p in self.posts if p['category'] == category]
    
    def get_published_posts(self) -> List[Dict]:
        return [p for p in self.posts if p['status'] == 'published']
    
    def update_post(self, slug: str, updates: Dict) -> bool:
        for i, post in enumerate(self.posts):
            if post['slug'] == slug:
                self.posts[i].update(updates)
                self.posts[i]['updated_at'] = datetime.now().isoformat()
                return True
        return False
    
    def delete_post(self, slug: str) -> bool:
        for i, post in enumerate(self.posts):
            if post['slug'] == slug:
                self.posts.pop(i)
                return True
        return False
    
    def publish_post(self, slug: str) -> bool:
        return self.update_post(slug, {'status': 'published'})
    
    def unpublish_post(self, slug: str) -> bool:
        return self.update_post(slug, {'status': 'draft'})
    
    def add_tag(self, slug: str, tag: str) -> bool:
        for post in self.posts:
            if post['slug'] == slug:
                if tag not in post['tags']:
                    post['tags'].append(tag)
                return True
        return False
    
    def increment_views(self, slug: str) -> bool:
        for post in self.posts:
            if post['slug'] == slug:
                post['views'] += 1
                return True
        return False
    
    def generate_html(self, post: Dict) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']}</title>
    <meta name="description" content="{post['excerpt']}">
    <link rel="stylesheet" href="/assets/css/blog.css">
</head>
<body>
    <article class="blog-post" data-post-slug="{post['slug']}">
        <header class="post-header">
            <span class="post-category">{post['category']}</span>
            <h1 class="post-title">{post['title']}</h1>
            <div class="post-meta">
                <span class="post-author">By {post['author']}</span>
                <span class="post-date">{datetime.fromisoformat(post['created_at']).strftime('%B %d, %Y')}</span>
            </div>
        </header>
        
        {f'<img src="{post["featured_image"]}" alt="{post["title"]}" class="post-image">' if post.get('featured_image') else ''}
        
        <div class="post-content" data-cms-editable="true">
            {post['content']}
        </div>
        
        <footer class="post-footer">
            <div class="post-tags">
                {''.join(f'<span class="tag">{tag}</span>' for tag in post.get('tags', []))}
            </div>
            <div class="post-actions">
                <button class="btn-edit" onclick="window.cms && window.cms.editPost('{post['slug']}')">Edit</button>
            </div>
        </footer>
    </article>
    
    <script src="/assets/js/blog.js"></script>
</body>
</html>'''
    
    def generate_rss_feed(self, posts: List[Dict] = None) -> str:
        if posts is None:
            posts = self.get_published_posts()
        
        items = ''
        for post in posts:
            items += f'''
            <item>
                <title>{post['title']}</title>
                <link>{self.base_url}/posts/{post['slug']}</link>
                <description>{post['excerpt']}</description>
                <author>{post['author']}</author>
                <category>{post['category']}</category>
                <pubDate>{datetime.fromisoformat(post['created_at']).strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            </item>'''
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Blog Feed</title>
        <link>{self.base_url}</link>
        <description>Latest posts</description>
        {items}
    </channel>
</rss>'''
    
    def generate_sitemap(self, posts: List[Dict] = None) -> str:
        if posts is None:
            posts = self.get_published_posts()
        
        urls = ''
        for post in posts:
            urls += f'''
        <url>
            <loc>{self.base_url}/posts/{post['slug']}</loc>
            <lastmod>{datetime.fromisoformat(post['updated_at']).strftime('%Y-%m-%d')}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.8</priority>
        </url>'''
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {urls}
</urlset>'''
