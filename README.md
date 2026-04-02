# FitSearch AI - Multi-Agent Platform

AI-powered search engine for fitness, bodybuilding, supplements, and performance compounds.

## Features

- Multi-agent search pipeline (10 specialized agents)
- Knowledge base with 15+ compound profiles
- Live web search (DuckDuckGo, Serper.dev, Google CSE)
- PubMed research integration
- Safety analysis and warnings
- FastAPI backend

## Quick Deploy to Render

1. Upload to GitHub
2. Connect to Render Blueprint
3. Deploy!

## API Endpoints

- `POST /search` - Main search
- `GET /search/simple?q=` - Simple search
- `GET /search/suggestions?q=` - Autocomplete
- `GET /knowledge-search?q=` - Knowledge base
- `GET /web-search?q=` - Web search
- `GET /research-search?q=` - PubMed research
- `GET /health` - Health check

## Example

```bash
curl -X POST https://your-app.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "RAD-140 dosage"}'
```
