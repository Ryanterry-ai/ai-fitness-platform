"""
FastAPI Application for Multi-Agent AI Search Platform
======================================================
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn

# Import orchestrator
from agents.orchestrator.agent import search, search_pipeline

# Import caching
from agents.caching.agent import get_cache_stats, caching_agent

# Create FastAPI app
app = FastAPI(
    title="FitSearch AI - Multi-Agent Platform",
    description="Production-grade AI search engine for fitness, bodybuilding, and performance compounds",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
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


class SuggestionResponse(BaseModel):
    suggestions: List[str]


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
    agents_active: int
    cache_stats: Dict[str, Any]
    timestamp: str


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "FitSearch AI - Multi-Agent Platform",
        "version": "1.0.0",
        "description": "Production-grade AI search engine for fitness, bodybuilding, and performance compounds",
        "docs": "/docs",
        "health": "/health",
        "search": "/search"
    }


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_endpoint(request: SearchRequest):
    """
    Main search endpoint.
    
    Processes search queries through the multi-agent pipeline:
    1. Query Understanding
    2. Knowledge Base Search
    3. Web Search
    4. Research Search
    5. Ranking
    6. Safety Analysis
    7. Response Generation
    """
    try:
        result = search(request.query, request.filters)
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/suggestions", response_model=SuggestionResponse, tags=["Search"])
async def get_suggestions(q: str = Query(..., min_length=2, max_length=100)):
    """
    Get search suggestions based on query prefix.
    """
    # Pre-defined suggestions
    suggestions = [
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
        "Progressive overload training"
    ]
    
    # Filter suggestions by query
    filtered = [s for s in suggestions if q.lower() in s.lower()]
    return SuggestionResponse(suggestions=filtered[:6])


@app.get("/knowledge-search", tags=["Search"])
async def knowledge_search(
    q: str = Query(..., description="Search query"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    max_results: int = Query(5, ge=1, le=20)
):
    """
    Search only the knowledge base.
    """
    from agents.query_understanding.agent import understand_query
    from agents.knowledge_base.agent import search_knowledge_base
    
    query_understanding = understand_query(q)
    results = search_knowledge_base(query_understanding)
    
    return {
        "query": q,
        "domain": domain,
        "results": [r.model_dump() for r in results[:max_results]],
        "count": len(results)
    }


@app.get("/web-search", tags=["Search"])
async def web_search(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50)
):
    """
    Search only the web.
    """
    from agents.query_understanding.agent import understand_query
    from agents.web_search.agent import search_web
    
    query_understanding = understand_query(q)
    results = search_web(query_understanding)
    
    return {
        "query": q,
        "results": [r.model_dump() for r in results[:max_results]],
        "count": len(results)
    }


@app.get("/research-search", tags=["Search"])
async def research_search(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50)
):
    """
    Search only research databases (PubMed).
    """
    from agents.query_understanding.agent import understand_query
    from agents.research.agent import search_research
    
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
    """
    Get related topics based on query.
    """
    from agents.query_understanding.agent import understand_query
    
    query_understanding = understand_query(q)
    
    # Get related topics based on domain
    related_topics = {
        "sarms": ["steroids", "peptides", "testosterone", "supplements"],
        "steroids": ["sarms", "pct", "testosterone", "anavar"],
        "peptides": ["bpc157", "tb500", "growth hormone", "recovery"],
        "hgh": ["igf", "peptides", "somatropin"],
        "supplements": ["creatine", "whey", "caffeine", "pre-workout"],
        "exercise": ["training", "workout", "hypertrophy"],
        "nutrition": ["diet", "macros", "protein", "calories"]
    }
    
    domain = query_understanding.domain.value
    related = related_topics.get(domain, ["supplements", "exercise", "nutrition"])
    
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
    caching_agent.clear_all()
    return {"status": "cleared", "message": "All cache entries cleared"}


@app.delete("/cache/expired", tags=["System"])
async def clear_expired_cache():
    """Clear expired cache entries"""
    count = caching_agent.clear_expired()
    return {"status": "cleared", "entries_removed": count}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    stats = get_cache_stats()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_active=9,  # All 9 agents are active
        cache_stats=stats,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/agents/status", tags=["System"])
async def get_agent_status():
    """Get status of all agents"""
    return search_pipeline.get_agent_status()


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
