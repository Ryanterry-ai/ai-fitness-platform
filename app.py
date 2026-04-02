# FitSearch AI - Multi-Agent Platform
"""
Main application entry point for Render deployment.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator.agent import search, search_pipeline
from src.agents.query_understanding.agent import understand_query
from src.agents.knowledge_base.agent import search_knowledge_base
from src.agents.web_search.agent import search_web
from src.agents.research.agent import search_research
from src.agents.caching.agent import get_cache_stats, caching_agent

# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FitSearch AI - Multi-Agent Platform",
    description="AI-powered search for fitness, bodybuilding, supplements, and performance compounds",
    version="1.0.0"
)

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Suggestions ────────────────────────────────────────────────────────
SUGGESTIONS = [
    "What is RAD140?", "Testosterone enanthate cycle", "Best supplements for muscle gain",
    "Creatine monohydrate guide", "BPC-157 injury healing", "Fat loss exercises for women",
    "Beginner workout plan", "Ostarine MK-2866 dosage", "LGD-4033 cycle protocol",
    "HGH human growth hormone", "Pre workout supplement stack", "Whey protein guide",
    "HIIT cardio fat loss", "Anavar oxandrolone cutting", "MK-677 ibutamoren dosage",
    "Nandrolone deca durabolin", "Vitamin D3 testosterone", "Omega-3 fish oil benefits",
    "High protein diet plan", "Strength training program", "Peptides for fat loss",
    "SARMs beginner guide", "Best steroids for muscle gain", "Peptide stack for fat loss",
    "Beginner cutting diet", "Progressive overload training",
]

# ── Models ────────────────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[List[str]] = Field(default_factory=list)
    include_research: bool = True
    include_web: bool = True
    max_results: int = Field(default=10, ge=1, le=50)

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    sections: Dict[str, Any]
    ai_summary: Optional[str] = None
    safety: Dict[str, Any]
    references: List[Dict[str, Any]]
    content_type: str
    cached: bool = False
    processing_time_ms: float
    agents_used: List[str]
    timestamp: str

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "FitSearch AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    try:
        start = time.time()
        result = search(request.query, request.filters)
        result["processing_time_ms"] = (time.time() - start) * 1000
        return SearchResponse(**result)
    except Exception as e:
        print(f"[Search Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/simple")
async def search_simple(q: str = Query(...), max_results: int = Query(10, ge=1, le=50)):
    try:
        result = search(q, [])
        return {
            "query": q,
            "results": result.get("results", [])[:max_results],
            "count": min(len(result.get("results", [])), max_results),
            "content_type": result.get("content_type", "general"),
            "safety": result.get("safety", {}),
            "cached": result.get("cached", False)
        }
    except Exception as e:
        return {"error": str(e), "results": [], "query": q}

@app.get("/search/suggestions")
async def suggestions(q: str = Query(..., min_length=2)):
    filtered = [s for s in SUGGESTIONS if q.lower() in s.lower()]
    return {"suggestions": filtered[:6]}

@app.get("/knowledge-search")
async def knowledge_search(q: str = Query(...), max_results: int = Query(5, ge=1, le=20)):
    query_understanding = understand_query(q)
    results = search_knowledge_base(query_understanding)
    return {"query": q, "results": [r.model_dump() for r in results[:max_results]], "count": len(results)}

@app.get("/web-search")
async def web_search(q: str = Query(...), max_results: int = Query(10, ge=1, le=50)):
    query_understanding = understand_query(q)
    results = search_web(query_understanding)
    return {"query": q, "results": [r.model_dump() for r in results[:max_results]], "count": len(results)}

@app.get("/research-search")
async def research_search(q: str = Query(...), max_results: int = Query(10, ge=1, le=50)):
    query_understanding = understand_query(q)
    results = search_research(query_understanding)
    return {"query": q, "results": [r.model_dump() for r in results[:max_results]], "count": len(results)}

@app.get("/related")
async def related(q: str = Query(...), max_results: int = Query(5, ge=1, le=20)):
    query_understanding = understand_query(q)
    domain = query_understanding.domain.value
    related_map = {
        "sarms": ["steroids", "peptides", "testosterone", "supplements"],
        "steroids": ["sarms", "pct", "testosterone", "anavar"],
        "peptides": ["bpc157", "tb500", "growth hormone", "recovery"],
        "hgh": ["igf", "peptides", "somatropin"],
        "supplements": ["creatine", "whey", "caffeine", "pre-workout"],
        "exercise": ["training", "workout", "hypertrophy"],
        "nutrition": ["diet", "macros", "protein", "calories"],
        "general": ["supplements", "exercise", "nutrition", "fitness"]
    }
    return {"query": q, "domain": domain, "compound": query_understanding.compound, "related_topics": related_map.get(domain, related_map["general"])[:max_results]}

@app.get("/cache/stats")
async def cache_stats():
    return get_cache_stats()

@app.delete("/cache/clear")
async def clear_cache():
    caching_agent.clear_all()
    return {"status": "cleared"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents_active": True,
        "cache_stats": get_cache_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/agents/status")
async def agent_status():
    return search_pipeline.get_agent_status()

@app.get("/info")
async def info():
    return {
        "name": "FitSearch AI",
        "version": "1.0.0",
        "platform": "Fitness & Bodybuilding AI Search",
        "features": ["Multi-agent pipeline", "Knowledge base", "Web search", "PubMed research", "Safety analysis"],
        "domains": ["SARMs", "Steroids", "Peptides", "HGH", "Supplements", "Exercise", "Nutrition"]
    }

# ── Error Handlers ────────────────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(Exception)
async def general_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})

# ── Run Locally ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
