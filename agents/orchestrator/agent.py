"""
Orchestrator Agent
==================
Coordinates all agents in the search pipeline.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from agents.query_understanding.agent import QueryUnderstandingAgent, understand_query
from agents.knowledge_base.agent import KnowledgeBaseAgent, search_knowledge_base
from agents.web_search.agent import WebSearchAgent, search_web
from agents.research.agent import ResearchAgent, search_research
from agents.ranking.agent import RankingAgent, rank_results
from agents.response_generation.agent import ResponseGenerationAgent, generate_response
from agents.safety.agent import SafetyAgent, analyze_safety
from agents.caching.agent import CachingAgent, get_cached_response, cache_response
from agents.embedding.agent import EmbeddingAgent

from models import (
    QueryUnderstanding,
    KnowledgeResult,
    WebSearchResult,
    ResearchResult,
    RankedResult,
    SafetyWarning,
    SearchResponse
)


class OrchestratorAgent:
    """
    Master agent that coordinates the entire search pipeline.
    
    Pipeline:
    1. Check cache
    2. Query Understanding Agent
    3. Parallel execution:
       - Knowledge Base Agent
       - Web Search Agent
       - Research Agent
    4. Ranking Agent
    5. Safety Agent
    6. Response Generation Agent
    7. Cache result
    8. Return response
    """
    
    def __init__(self):
        # Initialize all agents
        self.query_agent = QueryUnderstandingAgent()
        self.knowledge_agent = KnowledgeBaseAgent()
        self.web_agent = WebSearchAgent()
        self.research_agent = ResearchAgent()
        self.ranking_agent = RankingAgent()
        self.response_agent = ResponseGenerationAgent()
        self.safety_agent = SafetyAgent()
        self.cache_agent = CachingAgent()
        self.embedding_agent = EmbeddingAgent()
    
    def process(self, query: str, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a search query through the entire pipeline.
        
        Args:
            query: User's search query
            filters: Optional list of filters
            
        Returns:
            Complete search response
        """
        start_time = time.time()
        agents_used = []
        
        # Step 1: Check cache
        cached = get_cached_response(query, filters)
        if cached:
            cached["cached"] = True
            cached["processing_time_ms"] = (time.time() - start_time) * 1000
            return cached
        
        # Step 2: Query Understanding
        query_understanding = self.query_agent.process(query)
        agents_used.append("query_understanding")
        
        # Apply filters from request
        if filters:
            query_understanding.filters = filters
        
        # Step 3: Parallel search execution
        # Knowledge Base Search
        knowledge_results = self.knowledge_agent.process(query_understanding)
        agents_used.append("knowledge_base")
        
        # Web Search
        web_results = self.web_agent.process(query_understanding)
        agents_used.append("web_search")
        
        # Research Search
        research_results = self.research_agent.process(query_understanding)
        agents_used.append("research")
        
        # Step 4: Ranking
        ranked_results = self.ranking_agent.process(
            query_understanding,
            knowledge_results,
            web_results,
            research_results
        )
        agents_used.append("ranking")
        
        # Step 5: Safety Analysis
        safety_warning = self.safety_agent.process(query_understanding)
        agents_used.append("safety")
        
        # Step 6: Response Generation
        response = self.response_agent.process(
            query_understanding,
            ranked_results,
            safety_warning
        )
        agents_used.append("response_generation")
        
        # Step 7: Cache result
        cache_response(query, response, filters)
        
        # Add metadata
        processing_time = (time.time() - start_time) * 1000
        response["cached"] = False
        response["processing_time_ms"] = processing_time
        response["agents_used"] = agents_used
        response["timestamp"] = datetime.utcnow().isoformat()
        
        return response
    
    def process_async(self, query: str, filters: Optional[List[str]] = None):
        """
        Async version of process for use with async frameworks.
        """
        # This would use asyncio for true async execution
        return self.process(query, filters)


# Singleton instance
orchestrator = OrchestratorAgent()


def search(query: str, filters: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Main search function.
    
    Args:
        query: User's search query
        filters: Optional list of filters
        
    Returns:
        Complete search response
    """
    return orchestrator.process(query, filters)


class SearchPipeline:
    """
    Search pipeline for more granular control.
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
    
    async def execute(
        self,
        query: str,
        filters: Optional[List[str]] = None,
        include_research: bool = True,
        include_web: bool = True
    ) -> Dict[str, Any]:
        """
        Execute search with options.
        
        Args:
            query: Search query
            filters: Optional filters
            include_research: Whether to include research results
            include_web: Whether to include web results
            
        Returns:
            Search response
        """
        # For now, just use sync version
        # In production, would use async versions of agents
        return self.orchestrator.process(query, filters)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "query_understanding": "active",
            "knowledge_base": "active",
            "web_search": "active",
            "research": "active",
            "ranking": "active",
            "response_generation": "active",
            "safety": "active",
            "caching": "active",
            "embedding": "active"
        }


# Pipeline instance
search_pipeline = SearchPipeline()
