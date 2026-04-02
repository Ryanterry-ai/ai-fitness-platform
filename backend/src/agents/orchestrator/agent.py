"""
Orchestrator Agent - Main pipeline coordinator
"""
import time
from typing import List, Dict, Any
from datetime import datetime

class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator"
        self.agents = [
            "QueryUnderstanding",
            "KnowledgeBase",
            "WebSearch",
            "Research",
            "Ranking",
            "Safety",
            "ResponseGeneration"
        ]

    def search(self, query: str, filters: List[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        filters = filters or []
        
        # Import here to avoid circular imports
        from .query_understanding.agent import understand_query
        from .knowledge_base.agent import search_knowledge_base
        from .web_search.agent import search_web
        from .research.agent import search_research
        from .ranking.agent import rank_results
        from .safety.agent import analyze_safety
        from .response_generation.agent import generate_response
        from .caching.agent import caching_agent
        
        # Check cache
        cached = caching_agent.get(query)
        if cached:
            cached["cached"] = True
            cached["processing_time_ms"] = (time.time() - start_time) * 1000
            return cached
        
        # Step 1: Query Understanding
        query_understanding = understand_query(query)
        query_understanding.filters = filters
        
        # Step 2: Parallel Search (simulated)
        knowledge_results = search_knowledge_base(query_understanding)
        web_results = search_web(query_understanding)
        research_results = search_research(query_understanding)
        
        # Step 3: Ranking
        ranked_results = rank_results(query_understanding, knowledge_results, web_results, research_results)
        
        # Step 4: Safety Analysis
        safety = analyze_safety(query_understanding, ranked_results)
        
        # Step 5: Response Generation
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
            "processing_time_ms": (time.time() - start_time) * 1000,
            "agents_used": self.agents,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache result
        caching_agent.set(query, result)
        
        return result
    
    def get_agent_status(self) -> Dict[str, Any]:
        from .caching.agent import caching_agent
        return {
            "orchestrator": {"status": "active", "agents": self.agents},
            "knowledge_base": {"status": "active", "documents": 15},
            "web_search": {"status": "active"},
            "research": {"status": "active"},
            "caching": {"status": "active", **caching_agent.get_stats()}
        }


agent = OrchestratorAgent()

def search(query: str, filters: List[str] = None) -> Dict[str, Any]:
    return agent.search(query, filters)

def search_pipeline():
    return agent
