"""
AI Website Generator Agent
Generates full-stack websites from prompts
"""
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class AIGenerator:
    def __init__(self, prompt: str, project_id: str, template: str = None):
        self.prompt = prompt
        self.project_id = project_id
        self.template = template
        self.project_dir = Path(__file__).parent.parent.parent / "projects" / project_id
        self.files: List[Dict] = []
    
    def get_db(self):
        conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "database" / "platform.db"))
        conn.row_factory = sqlite3.Row
        return conn
    
    async def run(self):
        try:
            await self._update_status("generating", 10)
            
            await self._analyze_prompt()
            
            await self._update_status("generating_frontend", 30)
            await self._generate_frontend()
            
            await self._update_status("generating_backend", 60)
            await self._generate_backend()
            
            await self._update_status("generating_admin", 80)
            await self._generate_admin()
            
            await self._update_status("creating_assets", 90)
            await self._generate_assets()
            
            await self._update_status("completed", 100)
            
        except Exception as e:
            await self._update_status("failed", 0, str(e))
    
    async def _analyze_prompt(self):
        prompt_lower = self.prompt.lower()
        
        self.website_type = "landing"
        if any(k in prompt_lower for k in ["saas", "software", "app"]):
            self.website_type = "saas"
        elif any(k in prompt_lower for k in ["ecommerce", "shop", "store"]):
            self.website_type = "ecommerce"
        elif any(k in prompt_lower for k in ["blog", "news"]):
            self.website_type = "blog"
        elif any(k in prompt_lower for k in ["portfolio", "personal"]):
            self.website_type = "portfolio"
        elif any(k in prompt_lower for k in ["fitness", "gym", "health"]):
            self.website_type = "fitness"
        
        self.pages = self._determine_pages()
        self.features = self._extract_features()
    
    def _determine_pages(self) -> List[str]:
        pages = ["home"]
        
        if self.website_type == "saas":
            pages.extend(["features", "pricing", "about", "contact"])
        elif self.website_type == "ecommerce":
            pages.extend(["products", "cart", "checkout", "contact"])
        elif self.website_type == "blog":
            pages.extend(["blog", "about", "contact"])
        elif self.website_type == "portfolio":
            pages.extend(["work", "about", "contact"])
        else:
            pages.extend(["about", "services", "contact"])
        
        return pages
    
    def _extract_features(self) -> List[str]:
        features = []
        prompt_lower = self.prompt.lower()
        
        if any(k in prompt_lower for k in ["dark", "dark mode"]):
            features.append("dark_mode")
        if any(k in prompt_lower for k in ["animation", "animated", "smooth"]):
            features.append("animations")
        if any(k in prompt_lower for k in ["responsive", "mobile"]):
            features.append("responsive")
        if any(k in prompt_lower for k in ["modern", "clean"]):
            features.append("modern_ui")
        if any(k in prompt_lower for k in ["fast", "lightweight"]):
            features.append("performance")
        
        return features
    
    async def _generate_frontend(self):
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "frontend").mkdir(exist_ok=True)
        (self.project_dir / "frontend" / "src").mkdir(exist_ok=True)
        (self.project_dir / "frontend" / "src" / "components").mkdir(exist_ok=True)
        (self.project_dir / "frontend" / "public").mkdir(exist_ok=True)
        
        await self._generate_index_html()
        await self._generate_main_css()
        await self._generate_main_js()
        await self._generate_page_components()
    
    async def _generate_index_html(self):
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.prompt[:50]} | AI Generated</title>
    <meta name="description" content="Website generated from prompt: {self.prompt[:100]}">
    <link rel="stylesheet" href="/frontend/src/styles.css">
    <link rel="stylesheet" href="/frontend/src/components.css">
</head>
<body>
    <header class="header">
        <nav class="nav container">
            <a href="/" class="logo">Logo</a>
            <ul class="nav-links">
                {self._generate_nav_links()}
            </ul>
            <button class="mobile-menu-btn" onclick="toggleMobileMenu()">☰</button>
        </nav>
    </header>
    
    <main>
        {self._generate_hero_section()}
        {self._generate_content_sections()}
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} AI Generated Website. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="/frontend/src/app.js"></script>
</body>
</html>'''
        
        await self._save_file("frontend/index.html", html, "Homepage")
        
        for page in self.pages[1:]:
            page_html = self._generate_page_html(page)
            await self._save_file(f"frontend/{page}.html", page_html, page.title())
    
    def _generate_nav_links(self) -> str:
        links = ""
        for page in self.pages:
            links += f'<li><a href="/{page}.html">{page.title()}</a></li>'
        return links
    
    def _generate_hero_section(self) -> str:
        return f'''
    <section class="hero">
        <div class="container">
            <h1>{self.prompt.title()}</h1>
            <p>A modern website generated by AI Website Builder</p>
            <div class="hero-buttons">
                <a href="/contact.html" class="btn btn-primary">Get Started</a>
                <a href="/about.html" class="btn btn-secondary">Learn More</a>
            </div>
        </div>
    </section>'''
    
    def _generate_content_sections(self) -> str:
        sections = ""
        
        if "features" in self.pages:
            sections += '''
    <section class="features">
        <div class="container">
            <h2>Features</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>Feature 1</h3>
                    <p>Modern and responsive design</p>
                </div>
                <div class="feature-card">
                    <h3>Feature 2</h3>
                    <p>Fast and optimized performance</p>
                </div>
                <div class="feature-card">
                    <h3>Feature 3</h3>
                    <p>Easy to customize and maintain</p>
                </div>
            </div>
        </div>
    </section>'''
        
        if "services" in self.pages:
            sections += '''
    <section class="services">
        <div class="container">
            <h2>Our Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <h3>Service 1</h3>
                    <p>Professional solutions for your needs</p>
                </div>
                <div class="service-card">
                    <h3>Service 2</h3>
                    <p>Quality work delivered on time</p>
                </div>
            </div>
        </div>
    </section>'''
        
        return sections
    
    def _generate_page_html(self, page: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title()} | AI Generated</title>
    <link rel="stylesheet" href="/frontend/src/styles.css">
</head>
<body>
    <header class="header">
        <nav class="nav container">
            <a href="/" class="logo">Logo</a>
            <ul class="nav-links">
                {self._generate_nav_links()}
            </ul>
        </nav>
    </header>
    
    <main class="page-content">
        <div class="container">
            <h1>{page.title()}</h1>
            <p>This page was generated by AI based on your prompt.</p>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} AI Generated Website</p>
        </div>
    </footer>
    
    <script src="/frontend/src/app.js"></script>
</body>
</html>'''
    
    async def _generate_main_css(self):
        css = f'''/* AI Generated Styles - {self.website_type} website */

:root {{
    --primary: #667eea;
    --secondary: #764ba2;
    --dark: #1a1a2e;
    --light: #f8f9fa;
    --text: #333;
    --text-light: #666;
    --transition: all 0.3s ease;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    color: var(--text);
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header & Navigation */
.header {{
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 20px;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary);
    text-decoration: none;
}}

.nav-links {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-links a {{
    text-decoration: none;
    color: var(--text);
    transition: var(--transition);
}}

.nav-links a:hover {{
    color: var(--primary);
}}

/* Hero Section */
.hero {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: 100px 0;
    text-align: center;
}}

.hero h1 {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.hero p {{
    font-size: 1.25rem;
    opacity: 0.9;
    margin-bottom: 2rem;
}}

.hero-buttons {{
    display: flex;
    gap: 1rem;
    justify-content: center;
}}

/* Buttons */
.btn {{
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
}}

.btn-primary {{
    background: white;
    color: var(--primary);
}}

.btn-primary:hover {{
    transform: translateY(-2px);
}}

.btn-secondary {{
    background: transparent;
    color: white;
    border: 2px solid white;
}}

/* Sections */
section {{
    padding: 80px 0;
}}

section h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: var(--dark);
}}

/* Feature Grid */
.feature-grid, .services-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}}

.feature-card, .service-card {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
    transition: var(--transition);
}}

.feature-card:hover {{
    transform: translateY(-5px);
}}

.feature-card h3 {{
    color: var(--primary);
    margin-bottom: 1rem;
}}

/* Footer */
.footer {{
    background: var(--dark);
    color: white;
    padding: 40px 0;
    text-align: center;
}}

/* Page Content */
.page-content {{
    padding: 60px 0;
    min-height: 60vh;
}}

/* Mobile Menu */
.mobile-menu-btn {{
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
}}

/* Responsive */
@media (max-width: 768px) {{
    .nav-links {{
        display: none;
    }}
    
    .mobile-menu-btn {{
        display: block;
    }}
    
    .hero h1 {{
        font-size: 2rem;
    }}
    
    .hero-buttons {{
        flex-direction: column;
    }}
}}

/* Animations */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.hero, .feature-card {{
    animation: fadeIn 0.6s ease-out;
}}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {{
    body {{
        background: #0f0f23;
        color: #fff;
    }}
    
    .header {{
        background: #1a1a2e;
    }}
}}
'''
        
        await self._save_file("frontend/src/styles.css", css, "Main Styles")
    
    async def _generate_main_js(self):
        js = '''/* AI Generated JavaScript */

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    console.log('AI Generated Website Loaded');
    initAnimations();
    initMobileMenu();
    initSmoothScroll();
}

function initAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuBtn && navLinks) {
        menuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    if (navLinks) {
        navLinks.classList.toggle('active');
    }
}

// API Helper
async function api(endpoint, method = 'GET', data = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    
    const response = await fetch(`/api${endpoint}`, options);
    return response.json();
}

// Export for use
window.App = { initApp, api };
'''
        
        await self._save_file("frontend/src/app.js", js, "Main JavaScript")
    
    async def _generate_page_components(self):
        components_css = '''/* Component Styles */

.feature-card {
    border: 1px solid #eee;
}

.cta-section {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: 80px 0;
    text-align: center;
}

.cta-section h2 {
    color: white;
}

.contact-form {
    max-width: 600px;
    margin: 0 auto;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
}

.form-group textarea {
    min-height: 150px;
    resize: vertical;
}
'''
        
        await self._save_file("frontend/src/components.css", components_css, "Component Styles")
    
    async def _generate_backend(self):
        (self.project_dir / "backend").mkdir(exist_ok=True)
        (self.project_dir / "backend" / "routes").mkdir(exist_ok=True)
        
        await self._generate_backend_main()
        await self._generate_backend_routes()
    
    async def _generate_backend_main(self):
        main_py = f'''"""
Backend API - AI Generated
Project: {self.prompt[:50]}
Type: {self.website_type}
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3

app = FastAPI(title="API - {self.website_type.title()}", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    created_at: Optional[str] = None

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

# Database Setup
def init_db():
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.get("/")
async def root():
    return {{
        "message": "API Running",
        "project": "{self.prompt[:50]}",
        "type": "{self.website_type}",
        "timestamp": datetime.now().isoformat()
    }}

@app.get("/api/health")
async def health():
    return {{"status": "healthy"}}

@app.get("/api/items", response_model=List[Item])
async def get_items():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY created_at DESC")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

@app.post("/api/items", response_model=Item)
async def create_item(item: Item):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
        (item.name, item.description, item.price)
    )
    conn.commit()
    item.id = c.lastrowid
    conn.close()
    return item

@app.get("/api/items/{{item_id}}", response_model=Item)
async def get_item(item_id: int):
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = c.fetchone()
    conn.close()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return dict(item)

@app.delete("/api/items/{{item_id}}")
async def delete_item(item_id: int):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {{"success": True}}

@app.post("/api/contact")
async def contact(request: ContactRequest):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
        (request.name, request.email, request.message)
    )
    conn.commit()
    conn.close()
    return {{"success": True, "message": "Contact submitted"}}

@app.get("/api/contacts")
async def get_contacts():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM contacts ORDER BY created_at DESC")
    contacts = [dict(row) for row in c.fetchall()]
    conn.close()
    return contacts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        await self._save_file("backend/main.py", main_py, "Backend Main")
    
    async def _generate_backend_routes(self):
        routes_init = '''"""API Routes Package"""
'''
        
        items_route = '''"""Items API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

router = APIRouter(prefix="/api/items", tags=["items"])

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Optional[float]

@router.get("", response_model=List[ItemResponse])
async def list_items():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

@router.post("", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
        (item.name, item.description, item.price)
    )
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return {{"id": item_id, **item.dict()}}

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = c.fetchone()
    conn.close()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return dict(item)

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {{"success": True}}
'''
        
        await self._save_file("backend/routes/__init__.py", routes_init, "Routes Init")
        await self._save_file("backend/routes/items.py", items_route, "Items Routes")
    
    async def _generate_admin(self):
        (self.project_dir / "admin").mkdir(exist_ok=True)
        (self.project_dir / "admin" / "src").mkdir(exist_ok=True)
        
        admin_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard | {self.prompt[:30]}</title>
    <link rel="stylesheet" href="/admin/src/styles.css">
</head>
<body>
    <div class="admin-layout">
        <aside class="sidebar">
            <h2>Admin Panel</h2>
            <nav>
                <a href="/admin/" class="active">Dashboard</a>
                <a href="/admin/items.html">Items</a>
                <a href="/admin/contacts.html">Contacts</a>
                <a href="/admin/settings.html">Settings</a>
            </nav>
        </aside>
        <main class="content">
            <header>
                <h1>Dashboard</h1>
                <p>Manage your {self.website_type} website</p>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Items</h3>
                    <p class="stat-value" id="total-items">0</p>
                </div>
                <div class="stat-card">
                    <h3>Contacts</h3>
                    <p class="stat-value" id="total-contacts">0</p>
                </div>
            </div>
            
            <section class="quick-actions">
                <h2>Quick Actions</h2>
                <button onclick="location.href='/admin/items.html'">Manage Items</button>
                <button onclick="location.href='/admin/contacts.html'">View Contacts</button>
            </section>
        </main>
    </div>
    <script src="/admin/src/app.js"></script>
    <script>loadDashboard();</script>
</body>
</html>'''
        
        await self._save_file("admin/index.html", admin_html, "Admin Dashboard")
        
        admin_css = '''/* Admin Styles */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: system-ui, sans-serif; background: #f5f6fa; }

.admin-layout { display: flex; min-height: 100vh; }

.sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 20px;
    position: fixed;
    height: 100vh;
}

.sidebar h2 { margin-bottom: 20px; font-size: 1.2rem; }

.sidebar nav a {
    display: block;
    color: rgba(255,255,255,0.7);
    padding: 12px;
    text-decoration: none;
    border-radius: 8px;
    margin-bottom: 5px;
}

.sidebar nav a:hover,
.sidebar nav a.active {
    background: rgba(255,255,255,0.1);
    color: white;
}

.content {
    flex: 1;
    margin-left: 250px;
    padding: 30px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
.stat-value { font-size: 32px; font-weight: bold; color: #667eea; }

.quick-actions button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    margin-right: 10px;
}

.quick-actions button:hover { background: #5568d3; }
'''
        
        await self._save_file("admin/src/styles.css", admin_css, "Admin Styles")
        
        admin_js = '''/* Admin JavaScript */
const API_BASE = '/api';

async function api(endpoint, method = 'GET', data = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    return fetch(`${API_BASE}${endpoint}`, options).then(r => r.json());
}

async function loadDashboard() {
    try {
        const items = await api('/items');
        const contacts = await api('/contacts');
        
        document.getElementById('total-items').textContent = items.length || 0;
        document.getElementById('total-contacts').textContent = contacts.length || 0;
    } catch (e) {
        console.error('Dashboard load error:', e);
    }
}

window.App = { api, loadDashboard };
'''
        
        await self._save_file("admin/src/app.js", admin_js, "Admin App")
    
    async def _generate_assets(self):
        (self.project_dir / "assets").mkdir(exist_ok=True)
        (self.project_dir / "assets" / "css").mkdir(exist_ok=True)
        (self.project_dir / "assets" / "js").mkdir(exist_ok=True)
        (self.project_dir / "assets" / "images").mkdir(exist_ok=True)
        (self.project_dir / "database").mkdir(exist_ok=True)
        
        db_schema = '''-- Database Schema
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
        
        await self._save_file("database/schema.sql", db_schema, "Database Schema")
        
        requirements = f'''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
aiosqlite==0.19.0
'''
        
        await self._save_file("requirements.txt", requirements, "Requirements")
    
    async def _save_file(self, filepath: str, content: str, title: str):
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
        
        self.files.append({
            'path': filepath,
            'title': title,
            'size': len(content)
        })
    
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
