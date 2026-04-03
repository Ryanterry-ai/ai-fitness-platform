"""
AI Website Builder + Cloner Platform
Production Backend - Complete System
"""
import os
from pathlib import Path

# Base directory setup
BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / "public"
ADMIN_DIR = BASE_DIR / "admin"
ASSETS_DIR = BASE_DIR / "assets"
CLONED_SITES_DIR = BASE_DIR / "cloned_sites"
PROJECTS_DIR = BASE_DIR / "projects"
DB_PATH = BASE_DIR / "database" / "platform.db"

# Create directories
for d in [PUBLIC_DIR, ADMIN_DIR, ASSETS_DIR, CLONED_SITES_DIR, PROJECTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

(ASSETS_DIR / "css").mkdir(exist_ok=True)
(ASSETS_DIR / "js").mkdir(exist_ok=True)
(ASSETS_DIR / "images").mkdir(exist_ok=True)

# Now import FastAPI after directory setup
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
import shutil
import zipfile
from datetime import datetime
import hashlib
import uuid
import re

app = FastAPI(title="AI Website Builder + Cloner", version="3.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files AFTER directories are created
app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")
app.mount("/admin", StaticFiles(directory=str(ADMIN_DIR)), name="admin")
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'clone',
            original_url TEXT,
            prompt TEXT,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            pages_count INTEGER DEFAULT 0,
            files_data TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL,
            content TEXT,
            file_path TEXT,
            file_size INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            mimetype TEXT,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            prompt TEXT,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    for sql in tables:
        c.execute(sql)
    
    c.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@admin.com'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                  ('admin@admin.com', 'admin123', 'admin'))
    
    conn.commit()
    conn.close()

init_db()

# Pydantic Models
class CloneRequest(BaseModel):
    url: str
    max_pages: int = 50
    max_depth: int = 3
    project_name: Optional[str] = None

class GenerateRequest(BaseModel):
    prompt: str
    project_name: Optional[str] = None
    template: Optional[str] = None

class PageRequest(BaseModel):
    title: str
    slug: str
    content: str = ""
    file_path: Optional[str] = None
    project_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

# Routes
@app.get("/")
async def root():
    return FileResponse(PUBLIC_DIR / "index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/clone")
async def start_clone(request: CloneRequest, background_tasks: BackgroundTasks):
    project_id = str(uuid.uuid4())
    project_name = request.project_name or f"clone_{project_id[:8]}"
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO projects (id, name, type, original_url, status, progress)
        VALUES (?, ?, 'clone', ?, 'initializing', 0)
    """, (project_id, project_name, request.url))
    conn.commit()
    conn.close()
    
    try:
        from backend.agents.crawler_agent import CrawlerAgent
        crawler = CrawlerAgent(request.url, project_id, request.max_pages, request.max_depth)
        background_tasks.add_task(crawler.run)
    except ImportError:
        pass
    
    return {
        "success": True,
        "project_id": project_id,
        "project_name": project_name,
        "status": "started"
    }

@app.post("/api/generate")
async def generate_website(request: GenerateRequest, background_tasks: BackgroundTasks):
    project_id = str(uuid.uuid4())
    project_name = request.project_name or f"project_{project_id[:8]}"
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO projects (id, name, type, prompt, status, progress)
        VALUES (?, ?, 'generate', ?, 'initializing', 0)
    """, (project_id, project_name, request.prompt))
    conn.commit()
    conn.close()
    
    try:
        from backend.agents.ai_generator import AIGenerator
        generator = AIGenerator(request.prompt, project_id, request.template)
        background_tasks.add_task(generator.run)
    except ImportError:
        pass
    
    return {
        "success": True,
        "project_id": project_id,
        "project_name": project_name,
        "status": "started"
    }

@app.get("/api/projects")
async def get_projects():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in c.fetchall()]
    conn.close()
    return projects

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = c.fetchone()
    conn.close()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return dict(project)

@app.get("/api/projects/{project_id}/status")
async def get_project_status(project_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT status, progress, pages_count, error_message 
        FROM projects WHERE id = ?
    """, (project_id,))
    project = c.fetchone()
    conn.close()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return dict(project)

@app.get("/api/projects/{project_id}/files")
async def get_project_files(project_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM pages WHERE project_id = ?", (project_id,))
    pages = [dict(row) for row in c.fetchall()]
    conn.close()
    return pages

@app.post("/api/projects/{project_id}/files")
async def create_file(project_id: str, request: PageRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pages (project_id, title, slug, content, file_path)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, request.title, request.slug, request.content, request.file_path))
    conn.commit()
    file_id = c.lastrowid
    conn.close()
    return {"success": True, "id": file_id}

@app.get("/api/projects/{project_id}/download")
async def download_project(project_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = c.fetchone()
    c.execute("SELECT * FROM pages WHERE project_id = ?", (project_id,))
    pages = [dict(row) for row in c.fetchall()]
    conn.close()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    _create_project_structure(project_dir, dict(project), pages)
    
    zip_path = PROJECTS_DIR / f"{project_id}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(project_dir)
                zipf.write(file_path, arcname)
    
    return FileResponse(zip_path, filename=f"{project['name']}.zip", media_type='application/zip')

def _create_project_structure(project_dir: Path, project: dict, pages: List[dict]):
    dirs = ["frontend", "frontend/src", "frontend/src/components",
            "frontend/public", "backend", "admin", "database", "assets"]
    
    for d in dirs:
        (project_dir / d).mkdir(parents=True, exist_ok=True)
    
    for page in pages:
        if page.get('file_path'):
            file_path = project_dir / page['file_path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page.get('content', '') or '')
    
    readme = f'''# {project.get('name', 'Project')}

Generated by AI Website Builder + Cloner Platform

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend
uvicorn main:app --reload
```

## Structure
- /frontend - Frontend files
- /backend - Backend API
- /admin - Admin dashboard
'''

    with open(project_dir / "README.md", 'w') as f:
        f.write(readme)

@app.post("/api/login")
async def login(request: LoginRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, email, role FROM users WHERE email = ? AND password = ?",
               (request.email, request.password))
    user = c.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = hashlib.md5(f"{user['id']}{datetime.now()}".encode()).hexdigest()
    return {"success": True, "user": dict(user), "token": token}

@app.get("/api/pages")
async def get_pages(project_id: Optional[str] = None):
    conn = get_db()
    c = conn.cursor()
    
    if project_id:
        c.execute("SELECT * FROM pages WHERE project_id = ? ORDER BY updated_at DESC", (project_id,))
    else:
        c.execute("SELECT * FROM pages ORDER BY updated_at DESC")
    
    pages = [dict(row) for row in c.fetchall()]
    conn.close()
    return pages

@app.post("/api/pages")
async def create_page(request: PageRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pages (title, slug, content, file_path, project_id)
        VALUES (?, ?, ?, ?, ?)
    """, (request.title, request.slug, request.content, request.file_path, request.project_id))
    conn.commit()
    page_id = c.lastrowid
    conn.close()
    return {"success": True, "id": page_id}

@app.put("/api/pages/{page_id}")
async def update_page(page_id: int, request: PageRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE pages SET title = ?, slug = ?, content = ?, file_path = ?,
        updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (request.title, request.slug, request.content, request.file_path, page_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/pages/{page_id}")
async def delete_page(page_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM pages WHERE id = ?", (page_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/media")
async def get_media(project_id: Optional[str] = None):
    conn = get_db()
    c = conn.cursor()
    
    if project_id:
        c.execute("SELECT * FROM media WHERE project_id = ?", (project_id,))
    else:
        c.execute("SELECT * FROM media")
    
    media = [dict(row) for row in c.fetchall()]
    conn.close()
    return media

@app.post("/api/media/upload")
async def upload_media(file: UploadFile = File(...), project_id: Optional[str] = Form(None)):
    upload_dir = ASSETS_DIR / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{datetime.now().timestamp()}_{file.filename}"
    filepath = upload_dir / filename
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO media (filename, filepath, mimetype, size, project_id)
        VALUES (?, ?, ?, ?, ?)
    """, (file.filename, f"/assets/images/{filename}", file.content_type,
          filepath.stat().st_size, project_id))
    conn.commit()
    media_id = c.lastrowid
    conn.close()
    
    return {"success": True, "id": media_id, "filepath": f"/assets/images/{filename}"}

@app.delete("/api/media/{media_id}")
async def delete_media(media_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM media WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/settings")
async def get_settings():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    settings = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return settings

@app.post("/api/settings")
async def update_setting(key: str = Form(...), value: str = Form(...)):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    project_dir = PROJECTS_DIR / project_id
    if project_dir.exists():
        shutil.rmtree(project_dir)
    
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    c.execute("DELETE FROM pages WHERE project_id = ?", (project_id,))
    c.execute("DELETE FROM media WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.get("/api/dashboard/stats")
async def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM projects")
    projects = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM pages")
    pages = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM media")
    media = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM templates")
    templates = c.fetchone()[0]
    
    conn.close()
    
    return {"projects": projects, "pages": pages, "media": media, "templates": templates}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
