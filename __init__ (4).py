"""
Content Extractor Agent
Extracts and processes website content
"""
from bs4 import BeautifulSoup
from typing import Dict, List
import re

class ContentExtractor:
    def __init__(self, html: str, url: str):
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, 'html.parser')
    
    def extract_text_content(self) -> Dict[str, str]:
        content_blocks = {}
        
        for i, tag in enumerate(self.soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])):
            text = tag.get_text(strip=True)
            if text:
                block_id = f"block_{i}_{tag.name}"
                content_blocks[block_id] = {
                    'type': tag.name,
                    'content': text,
                    'html': str(tag)
                }
        
        return content_blocks
    
    def extract_images(self) -> List[Dict]:
        images = []
        
        for img in self.soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'class': img.get('class', []),
                'style': img.get('style', '')
            }
            images.append(img_data)
        
        return images
    
    def extract_links(self) -> List[Dict]:
        links = []
        
        for link in self.soup.find_all('a', href=True):
            link_data = {
                'href': link.get('href', ''),
                'text': link.get_text(strip=True),
                'target': link.get('target', ''),
                'rel': link.get('rel', [])
            }
            links.append(link_data)
        
        return links
    
    def extract_forms(self) -> List[Dict]:
        forms = []
        
        for form in self.soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'placeholder': input_tag.get('placeholder', ''),
                    'required': input_tag.has_attr('required')
                }
                form_data['inputs'].append(input_data)
            
            forms.append(form_data)
        
        return forms
    
    def extract_scripts(self) -> List[Dict]:
        scripts = []
        
        for script in self.soup.find_all('script'):
            script_data = {
                'src': script.get('src', ''),
                'type': script.get('type', 'text/javascript'),
                'content': script.string or ''
            }
            scripts.append(script_data)
        
        return scripts
    
    def extract_metadata(self) -> Dict:
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'og_tags': {},
            'meta_tags': {}
        }
        
        if self.soup.title:
            metadata['title'] = self.soup.title.string or ''
        
        for meta in self.soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif name.startswith('og:'):
                metadata['og_tags'][name] = content
            else:
                metadata['meta_tags'][name] = content
        
        return metadata
    
    def extract_structure(self) -> Dict:
        structure = {
            'headings': {},
            'navigation': [],
            'sections': [],
            'footer': None
        }
        
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings = []
            for heading in self.soup.find_all(level):
                headings.append({
                    'text': heading.get_text(strip=True),
                    'id': heading.get('id', ''),
                    'class': heading.get('class', [])
                })
            structure['headings'][level] = headings
        
        nav = self.soup.find('nav')
        if nav:
            for link in nav.find_all('a', href=True):
                structure['navigation'].append({
                    'text': link.get_text(strip=True),
                    'href': link.get('href', '')
                })
        
        for section in self.soup.find_all('section'):
            structure['sections'].append({
                'id': section.get('id', ''),
                'class': section.get('class', []),
                'heading': section.find(['h1', 'h2', 'h3']) and section.find(['h1', 'h2', 'h3']).get_text(strip=True) or ''
            })
        
        footer = self.soup.find('footer')
        if footer:
            structure['footer'] = str(footer)
        
        return structure
    
    def extract_all(self) -> Dict:
        return {
            'url': self.url,
            'metadata': self.extract_metadata(),
            'content': self.extract_text_content(),
            'images': self.extract_images(),
            'links': self.extract_links(),
            'forms': self.extract_forms(),
            'scripts': self.extract_scripts(),
            'structure': self.extract_structure()
        }
    
    def clean_html(self) -> str:
        scripts = self.soup.find_all('script')
        for script in scripts:
            script.decompose()
        
        styles = self.soup.find_all('style')
        for style in styles:
            style.decompose()
        
        return str(self.soup)
    
    def make_editable(self) -> str:
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'li']):
            text = tag.get_text(strip=True)
            if text and len(text) > 0:
                tag['data-cms-editable'] = 'true'
        
        for img in self.soup.find_all('img'):
            img['data-cms-editable'] = 'image'
        
        return str(self.soup)
