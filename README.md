# FitSearch AI - Production-Grade AI Search Platform

AI-powered search engine covering the entire SEO Query Universe for fitness, bodybuilding, and performance compounds.

## Features

- **Multi-Agent Pipeline**: 11 specialized agents working in coordination
- **SEO Query Mastery**: Handles all query types (informational, dosage, comparison, etc.)
- **Knowledge Base**: Comprehensive database of 15+ compounds with detailed profiles
- **Live Web Search**: DuckDuckGo, Serper.dev, Google CSE integration
- **PubMed Research**: Real scientific papers and clinical studies
- **Safety Analysis**: Automatic risk assessment and warnings

## Deploy to Render

1. Upload to GitHub
2. Connect to Render Blueprint
3. Deploy!

## API Endpoints

- `POST /search` - Main multi-agent search
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
  -d '{"query": "RAD-140 dosage for beginners"}'
```
