# AI Website Cloner - Production Deployment Guide

A production-grade AI website cloner that can clone any website, preserve functionality, and generate an editable CMS with admin dashboard.

## Features

- **AI-Powered Crawling**: Uses Playwright for rendering JavaScript-heavy sites
- **Multi-Agent Architecture**: Dedicated agents for crawling, extraction, CMS generation
- **Editable CMS**: Convert any static site to editable content
- **Admin Dashboard**: Full-featured CMS panel
- **ZIP Export**: Download cloned sites for deployment
- **Render Ready**: One-click deployment to Render

## Quick Deploy to Render

### Option 1: Deploy via Render Blueprint

1. Click this button:
   
  [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

2. Connect your GitHub repository

3. The service will automatically:
   - Install Python dependencies
   - Install Playwright browsers
   - Start the server

### Option 2: Manual Deploy

```bash
# Clone the repository
git clone <your-repo>
cd website-cloner

# Create a new Web Service on Render
# Set the following:
# - Build Command: pip install -r requirements.txt && playwright install chromium --with-deps
# - Start Command: uvicorn backend.app:app --host 0.0.0.0 --port 10000
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium --with-deps

# Run the server
uvicorn backend.app:app --reload --host 0.0.0.0 --port 10000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/clone` | POST | Start a new clone job |
| `GET /api/projects` | GET | List all projects |
| `GET /api/projects/{id}` | GET | Get project details |
| `GET /api/projects/{id}/status` | GET | Get clone status |
| `GET /api/projects/{id}/download` | GET | Download project ZIP |
| `DELETE /api/projects/{id}` | DELETE | Delete project |
| `POST /api/login` | POST | Admin login |
| `GET /api/pages` | GET | List pages |
| `POST /api/pages` | POST | Create page |
| `GET /api/media` | GET | List media |
| `POST /api/media/upload` | POST | Upload media |

## Example Clone Request

```bash
curl -X POST https://your-app.onrender.com/api/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 50}'
```

## Admin Login

- **Email**: admin@admin.com
- **Password**: admin123

Access admin at: `https://your-app.onrender.com/admin`

## Project Structure

```
website-cloner/
├── backend/
│   ├── app.py                 # FastAPI application
│   └── agents/
│       ├── playwright_crawler.py  # Playwright-based crawler
│       └── cms_generator.py    # CMS generator
├── public/
│   └── index.html             # Main UI
├── admin/
│   ├── index.html             # Login page
│   └── pages/                 # Admin pages
├── database/                  # SQLite database
├── requirements.txt
├── render.yaml               # Render blueprint
├── Dockerfile
└── README.md
```

## Render Configuration

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `10000` | Server port (Render sets this) |
| `PYTHON_VERSION` | `3.11` | Python version |

### Health Check

The `/` endpoint returns `{"status": "running"}` for health checks.

## Docker Deployment

```bash
# Build image
docker build -t website-cloner .

# Run container
docker run -p 10000:10000 website-cloner
```

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: SQLite
- **Crawler**: Playwright (Chromium)
- **Frontend**: Vanilla JS, CSS3
- **Deployment**: Docker, Render

## License

MIT License

## Support

For issues and feature requests, please open a GitHub issue.
