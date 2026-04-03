"""
CLI Tool for Website Cloner
Command-line interface for advanced users
"""
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.crawler import WebsiteCrawler
from backend.agents.cms_generator import CMSGenerator
from backend.agents.zip_generator import ZIPGenerator

async def clone_website(url: str, max_pages: int, max_depth: int, output_dir: str):
    print(f"Starting clone of {url}")
    print(f"Max pages: {max_pages}, Max depth: {max_depth}")
    
    crawler = WebsiteCrawler(url, max_pages, max_depth)
    print("Crawling website...")
    
    pages_data = await crawler.crawl()
    print(f"Found {len(pages_data)} pages")
    
    project_name = crawler.get_domain_name()
    project_path = Path(output_dir) / project_name
    
    print(f"Generating CMS at {project_path}")
    generator = CMSGenerator(pages_data, str(project_path), url)
    generator.generate()
    
    print("Creating ZIP file...")
    zip_gen = ZIPGenerator(str(project_path))
    zip_path = zip_gen.generate()
    
    print(f"\nClone complete!")
    print(f"Project: {project_path}")
    print(f"ZIP: {zip_path}")
    print(f"Size: {zip_gen.get_size(zip_path):.2f} MB")
    
    return project_path, zip_path

def main():
    parser = argparse.ArgumentParser(description="Website Cloner CLI")
    parser.add_argument("url", help="Website URL to clone")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("-p", "--max-pages", type=int, default=50, help="Maximum pages to crawl")
    parser.add_argument("-d", "--max-depth", type=int, default=3, help="Maximum crawl depth")
    parser.add_argument("--no-zip", action="store_true", help="Skip ZIP generation")
    
    args = parser.parse_args()
    
    try:
        project_path, zip_path = asyncio.run(
            clone_website(args.url, args.max_pages, args.max_depth, args.output)
        )
        print(f"\nSuccess! Website cloned to {project_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
