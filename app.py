"""
FitSearch AI - Multi-Agent Platform
====================================
Production FastAPI application for fitness, bodybuilding, and performance compounds.
Deploys to Render with gunicorn.

Run locally:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

Deploy to Render:
    gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# ── Path Setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── FastAPI Setup ────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ── Import Agents ─────────────────────────────────────────────────────────────
try:
    from agents.orchestrator.agent import search, search_pipeline
    from agents.query_understanding.agent import understand_query
    from agents.knowledge_base.agent import search_knowledge_base
    from agents.web_search.agent import search_web
    from agents.research.agent import search_research
    from agents.caching.agent import get_cache_stats, caching_agent
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] Agent imports failed: {e}")
    AGENTS_AVAILABLE = False

# ── Application Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    print(f"[FitSearch AI] Starting Multi-Agent Platform...")
    print(f"[FitSearch AI] Agents available: {AGENTS_AVAILABLE}")
    yield
    print(f"[FitSearch AI] Shutting down...")

# ── Create FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="FitSearch AI - Multi-Agent Platform",
    description="Production-grade AI search engine for fitness, bodybuilding, supplements, and performance compounds",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS Configuration ────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ──────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[List[str]] = Field(default_factory=list, description="Filter tags")
    include_research: bool = Field(default=True, description="Include research results")
    include_web: bool = Field(default=True, description="Include web results")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results")

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

class CacheStatsResponse(BaseModel):
    total_entries: int
    total_hits: int
    max_hits: int
    avg_hits: float
    expired_entries: int
    active_entries: int
    cache_ttl_seconds: int

class HealthResponse(BaseModel):
    status: str
    version: str
    agents_active: bool
    cache_stats: Dict[str, Any]
    timestamp: str

# ── Static Suggestions ────────────────────────────────────────────────────────
STATIC_SUGGESTIONS = [
    "What is RAD140?",
    "Testosterone enanthate cycle",
    "Best supplements for muscle gain",
    "Creatine monohydrate guide",
    "BPC-157 injury healing",
    "Fat loss exercises for women",
    "Beginner workout plan",
    "Ostarine MK-2866 dosage",
    "LGD-4033 cycle protocol",
    "HGH human growth hormone",
    "Pre workout supplement stack",
    "Whey protein guide",
    "HIIT cardio fat loss",
    "Anavar oxandrolone cutting",
    "MK-677 ibutamoren dosage",
    "Nandrolone deca durabolin",
    "Vitamin D3 testosterone",
    "Omega-3 fish oil benefits",
    "High protein diet plan",
    "Strength training program",
    "Peptides for fat loss",
    "SARMs beginner guide",
    "Best steroids for muscle gain",
    "Peptide stack for fat loss",
    "Beginner cutting diet",
    "Progressive overload training",
]

# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "FitSearch AI - Multi-Agent Platform",
        "version": "1.0.0",
        "description": "AI-powered search engine for fitness, bodybuilding, and performance compounds",
        "docs": "/docs",
        "health": "/health",
        "search": "/search",
        "status": "operational"
    }


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_endpoint(request: SearchRequest):
    """
    Main search endpoint using multi-agent pipeline.
    
    Processes queries through:
    1. Query Understanding → Knowledge Base → Web Search → Research
    2. Ranking → Safety Analysis → Response Generation
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agents not available")
    
    try:
        start_time = time.time()
        result = search(request.query, request.filters)
        result["processing_time_ms"] = (time.time() - start_time) * 1000
        return SearchResponse(**result)
    except Exception as e:
        print(f"[Search Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/simple", tags=["Search"])
async def search_simple(
    q: str = Query(..., min_length=1, max_length=500),
    max_results: int = Query(10, ge=1, le=50)
):
    """
    Simple search endpoint - returns raw results without full response formatting.
    """
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "results": []}
    
    try:
        from agents.orchestrator.agent import search
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


@app.get("/search/suggestions", tags=["Search"])
async def get_suggestions(
    q: str = Query(..., min_length=2, max_length=100)
):
    """Get search suggestions based on query prefix"""
    filtered = [s for s in STATIC_SUGGESTIONS if q.lower() in s.lower()]
    return {"suggestions": filtered[:6]}


@app.get("/knowledge-search", tags=["Search"])
async def knowledge_search(
    q: str = Query(..., description="Search query"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    max_results: int = Query(5, ge=1, le=20)
):
    """Search only the knowledge base"""
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "results": []}
    
    query_understanding = understand_query(q)
    results = search_knowledge_base(query_understanding)
    
    return {
        "query": q,
        "domain": domain or query_understanding.domain.value,
        "results": [r.model_dump() for r in results[:max_results]],
        "count": len(results)
    }


@app.get("/web-search", tags=["Search"])
async def web_search_endpoint(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50)
):
    """Search only the web"""
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "results": []}
    
    query_understanding = understand_query(q)
    results = search_web(query_understanding)
    
    return {
        "query": q,
        "results": [r.model_dump() for r in results[:max_results]],
        "count": len(results)
    }


@app.get("/research-search", tags=["Search"])
async def research_search_endpoint(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50)
):
    """Search only research databases (PubMed)"""
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "results": []}
    
    query_understanding = understand_query(q)
    results = search_research(query_understanding)
    
    return {
        "query": q,
        "results": [r.model_dump() for r in results[:max_results]],
        "count": len(results)
    }


@app.get("/related", tags=["Search"])
async def get_related(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=20)
):
    """Get related topics based on query"""
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "related_topics": []}
    
    query_understanding = understand_query(q)
    domain = query_understanding.domain.value
    
    related_topics = {
        "sarms": ["steroids", "peptides", "testosterone", "supplements"],
        "steroids": ["sarms", "pct", "testosterone", "anavar"],
        "peptides": ["bpc157", "tb500", "growth hormone", "recovery"],
        "hgh": ["igf", "peptides", "somatropin"],
        "supplements": ["creatine", "whey", "caffeine", "pre-workout"],
        "exercise": ["training", "workout", "hypertrophy"],
        "nutrition": ["diet", "macros", "protein", "calories"],
        "general": ["supplements", "exercise", "nutrition", "fitness"]
    }
    
    related = related_topics.get(domain, related_topics["general"])
    
    return {
        "query": q,
        "domain": domain,
        "compound": query_understanding.compound,
        "related_topics": related[:max_results]
    }


@app.get("/cache/stats", response_model=CacheStatsResponse, tags=["System"])
async def get_cache_statistics():
    """Get cache statistics"""
    stats = get_cache_stats()
    return CacheStatsResponse(**stats)


@app.delete("/cache/clear", tags=["System"])
async def clear_cache():
    """Clear all cache entries"""
    if AGENTS_AVAILABLE:
        caching_agent.clear_all()
    return {"status": "cleared", "message": "All cache entries cleared"}


@app.delete("/cache/expired", tags=["System"])
async def clear_expired_cache():
    """Clear expired cache entries"""
    if AGENTS_AVAILABLE:
        count = caching_agent.clear_expired()
    else:
        count = 0
    return {"status": "cleared", "entries_removed": count}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    stats = get_cache_stats() if AGENTS_AVAILABLE else {}
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_active=AGENTS_AVAILABLE,
        cache_stats=stats,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/agents/status", tags=["System"])
async def get_agent_status():
    """Get status of all agents"""
    if not AGENTS_AVAILABLE:
        return {"error": "Agents not available", "agents": []}
    
    return search_pipeline.get_agent_status()


@app.get("/info", tags=["System"])
async def get_info():
    """Get platform information"""
    return {
        "name": "FitSearch AI",
        "version": "1.0.0",
        "platform": "Fitness & Bodybuilding AI Search",
        "features": [
            "Multi-agent search pipeline",
            "Knowledge base with 19+ compounds",
            "Web search integration",
            "PubMed research search",
            "Safety analysis",
            "Response ranking"
        ],
        "domains": [
            "SARMs", "Steroids", "Peptides", "HGH",
            "Supplements", "Exercise", "Nutrition",
            "Fat Loss", "Muscle Gain", "Bodybuilding"
        ]
    }


# ── Error Handlers ───────────────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# ── Gunicorn Entry Point ──────────────────────────────────────────────────────
# This allows: gunicorn app:app --bind 0.0.0.0:$PORT
def create_app():
    return app


# ── Local Development ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
