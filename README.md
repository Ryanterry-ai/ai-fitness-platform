# FitSearch AI - Multi-Agent Platform

Production-grade AI search engine for fitness, bodybuilding, supplements, and performance compounds.

## Features

- **Multi-Agent Pipeline**: 10 specialized agents working in coordination
- **Knowledge Base**: 19+ compound profiles (SARMs, steroids, peptides, supplements)
- **Web Search**: DuckDuckGo integration with authority scoring
- **Research Search**: PubMed integration for scientific papers
- **Safety Analysis**: Automatic risk assessment and warnings
- **Response Ranking**: Multi-factor ranking (relevance, authority, safety, freshness)
- **Caching**: SQLite-based caching for performance

## Domains Covered

- SARMs (RAD-140, LGD-4033, Ostarine, MK-677, etc.)
- Anabolic Steroids (Testosterone, Nandrolone, Anavar, etc.)
- Peptides (BPC-157, TB-500, CJC-1295, etc.)
- HGH/Growth Hormone
- Supplements (Creatine, Whey, Caffeine, etc.)
- Exercise & Workouts
- Nutrition & Diet
- Fat Loss & Muscle Gain

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python app.py
```

### Deploy to Render

1. Fork/clone this repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repo
5. Deploy!

The `render.yaml` file handles all configuration automatically.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/search` | POST | Main search (multi-agent pipeline) |
| `/search/simple` | GET | Simple search query |
| `/search/suggestions` | GET | Query autocomplete |
| `/knowledge-search` | GET | Knowledge base only |
| `/web-search` | GET | Web search only |
| `/research-search` | GET | PubMed research only |
| `/related` | GET | Related topics |
| `/cache/stats` | GET | Cache statistics |
| `/cache/clear` | DELETE | Clear cache |
| `/health` | GET | Health check |
| `/agents/status` | GET | Agent status |
| `/info` | GET | Platform info |

## Example Usage

```bash
# Health check
curl https://your-app.onrender.com/health

# Search
curl -X POST https://your-app.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAD-140?", "max_results": 10}'

# Simple search
curl "https://your-app.onrender.com/search/simple?q=RAD-140"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `ENVIRONMENT` | production | Environment mode |
| `ALLOWED_ORIGINS` | * | CORS origins |
| `OPENAI_API_KEY` | - | OpenAI for embeddings (optional) |
| `SERP_API_KEY` | - | SerpAPI key (optional) |
| `PUBMED_API_KEY` | - | PubMed API key (optional) |

## Architecture

```
Query → Query Understanding Agent
                    ↓
         ┌──────────┼──────────┐
         ↓          ↓          ↓
   Knowledge    Web Search   Research
     Base                          
         └──────────┼──────────┘
                    ↓
              Ranking Agent
                    ↓
             Safety Agent
                    ↓
      Response Generation Agent
                    ↓
                Response
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This platform provides general information about fitness, supplements, and related topics. Always consult healthcare professionals before making decisions about supplements, medications, or training programs.
