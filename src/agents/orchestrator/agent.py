"""
Orchestrator Agent - Main Pipeline Coordinator
"""
import time
from typing import List, Dict, Any
from datetime import datetime

class OrchestratorAgent:
    def __init__(self):
        self.agents = ["QueryUnderstanding", "SEOIntent", "KnowledgeBase", "WebSearch", "Research", "Ranking", "Safety", "ResponseGeneration"]

    def search(self, query: str, filters: List[str] = None) -> Dict[str, Any]:
        start = time.time()
        filters = filters or []
        
        # Lazy imports to avoid circular dependencies
        from ..query_understanding.agent import understand_query
        from ..knowledge_base.agent import search_knowledge_base
        from ..web_search.agent import search_web
        from ..research.agent import search_research
        from ..ranking.agent import rank_results
        from ..safety.agent import analyze_safety
        from ..response_generation.agent import generate_response
        from ..caching.agent import caching_agent
        
        # Check cache
        cached = caching_agent.get(query)
        if cached:
            cached["cached"] = True
            cached["processing_time_ms"] = (time.time() - start) * 1000
            return cached
        
        # Query Understanding
        query_understanding = understand_query(query)
        query_understanding.filters = filters
        
        # Parallel Search
        knowledge_results = search_knowledge_base(query_understanding)
        web_results = search_web(query_understanding)
        research_results = search_research(query_understanding)
        
        # Ranking
        ranked_results = rank_results(query_understanding, knowledge_results, web_results, research_results)
        
        # Safety Analysis
        safety = analyze_safety(query_understanding, ranked_results)
        
        # Response Generation
        response = generate_response(query_understanding, ranked_results, safety)
        
        # Build final response
        result = {
            "query": query,
            "results": [r.content for r in ranked_results],
            "sections": response["sections"],
            "ai_summary": response["ai_summary"],
            "safety": response["safety"],
            "references": response["references"],
            "content_type": query_understanding.domain.value,
            "cached": False,
            "processing_time_ms": (time.time() - start) * 1000,
            "agents_used": self.agents,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        caching_agent.set(query, result)
        return result
    
    def get_status(self) -> Dict[str, Any]:
        from ..caching.agent import caching_agent
        return {"orchestrator": {"status": "active", "agents": self.agents}, "caching": caching_agent.get_stats()}

agent = OrchestratorAgent()

def search(query: str, filters: List[str] = None) -> Dict[str, Any]:
    return agent.search(query, filters)

def get_agent_status() -> Dict[str, Any]:
    return agent.get_status()
