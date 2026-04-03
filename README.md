# AI Website Builder + Cloner Platform v3.0

A production-grade platform for cloning websites and generating AI-powered websites from prompts.

## Features

### Website Cloning
- Clone any website completely with Playwright-powered rendering
- Preserve HTML, CSS, JavaScript, images, and functionality
- Multi-page crawling with configurable depth
- Editable CMS conversion

### AI Website Generation
- Generate full-stack websites from text prompts
- SaaS, E-commerce, Blog, Portfolio templates
- Auto-generated frontend and backend
- Complete admin dashboard

### Full-Stack Export
- Download complete projects as ZIP
- Individual file download support
- Large file support (up to 10k lines)
- Render/Hostinger deployment ready

### Admin Dashboard
- Pages management
- Media library
- Settings configuration
- Project tracking

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright (for cloning)
playwright install chromium --with-deps

# Run server
uvicorn backend.app:app --reload --port 10000
```

### Deploy to Render

1. Push to GitHub
2. Connect to Render
3. Use `render.yaml` or set:
   - Build: `pip install -r requirements.txt && playwright install chromium`
   - Start: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

## API Endpoints

### Clone Website
```bash
POST /api/clone
{
  "url": "https://example.com",
  "max_pages": 50,
  "project_name": "my-clone"
}
```

### Generate Website
```bash
POST /api/generate
{
  "prompt": "Build a modern SaaS landing page",
  "template": "saas",
  "project_name": "my-saas"
}
```

### Download Project
```bash
GET /api/projects/{project_id}/download
```

### Individual Files
```bash
GET /api/projects/{project_id}/files
GET /api/projects/{project_id}/files/{file_id}/download
```

## Admin Login

- Email: admin@admin.com
- Password: admin123

Access: `http://localhost:10000/admin`

## Project Structure

```
website-cloner/
├── backend/
│   ├── app.py              # Main FastAPI app
│   └── agents/
│       ├── crawler_agent.py   # Website crawler
│       └── ai_generator.py    # AI generator
├── public/
│   └── index.html         # Main UI
├── admin/                 # Admin dashboard
├── projects/              # Generated projects
├── database/             # SQLite database
├── requirements.txt
├── render.yaml
└── Dockerfile
```

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: SQLite
- **Crawler**: Playwright, BeautifulSoup, aiohttp
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Docker, Render

## License

MIT License
