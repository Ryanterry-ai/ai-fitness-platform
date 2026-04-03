"""
ZIP Generator Script
Generates deployable ZIP files from cloned projects
"""
import zipfile
import os
from pathlib import Path
from datetime import datetime

class ZIPGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate(self, output_name: str = None) -> str:
        if output_name is None:
            output_name = f"{self.project_path.name}_{self.timestamp}.zip"
        
        output_path = self.project_path.parent / output_name
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.project_path)
                    zipf.write(file_path, arcname)
        
        return str(output_path)
    
    def generate_with_exclusions(self, output_name: str = None, exclude_patterns: list = None) -> str:
        if output_name is None:
            output_name = f"{self.project_path.name}_{self.timestamp}.zip"
        
        output_path = self.project_path.parent / output_name
        exclude_patterns = exclude_patterns or [
            '__pycache__',
            '.git',
            '*.pyc',
            '.DS_Store',
            'node_modules'
        ]
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                
                for file in files:
                    if any(pattern in file for pattern in exclude_patterns):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.project_path)
                    zipf.write(file_path, arcname)
        
        return str(output_path)
    
    def get_size(self, zip_path: str) -> float:
        zip_path = Path(zip_path)
        if zip_path.exists():
            return zip_path.stat().st_size / (1024 * 1024)
        return 0

def create_deployment_package(project_path: str, output_path: str = None) -> str:
    generator = ZIPGenerator(project_path)
    return generator.generate(output_path)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python zip_generator.py <project_path> [output_name]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    generator = ZIPGenerator(project_path)
    zip_path = generator.generate(output_name)
    
    print(f"ZIP file created: {zip_path}")
    print(f"Size: {generator.get_size(zip_path):.2f} MB")
