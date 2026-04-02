"""
Ranking Agent
=============
Ranks and combines results from all search agents.
"""

from typing import List, Dict, Any, Optional
from src.models import RankedResult, KnowledgeResult, WebSearchResult, ResearchResult, QueryUnderstanding


class RankingAgent:
    """
    Agent responsible for ranking and combining search results.
    
    Responsibilities:
    - Combine results from Knowledge Base, Web Search, and Research agents
    - Rank based on relevance, authority, freshness, and safety
    - Apply user preferences and filters
    - Return optimized result list
    """
    
    def __init__(self):
        # Weight configuration
        self.weights = {
            "relevance": 0.35,
            "authority": 0.30,
            "freshness": 0.15,
            "safety": 0.20
        }
    
    def process(
        self,
        query_understanding: QueryUnderstanding,
        knowledge_results: List[KnowledgeResult],
        web_results: List[WebSearchResult],
        research_results: List[ResearchResult]
    ) -> List[RankedResult]:
        """
        Rank and combine all search results.
        
        Args:
            query_understanding: Parsed query understanding
            knowledge_results: Results from Knowledge Base agent
            web_results: Results from Web Search agent
            research_results: Results from Research agent
            
        Returns:
            List of RankedResult objects sorted by combined score
        """
        all_results = []
        
        # Process and add knowledge base results
        for result in knowledge_results:
            ranked = self._rank_knowledge_result(result, query_understanding)
            all_results.append(ranked)
        
        # Process and add web search results
        for result in web_results:
            ranked = self._rank_web_result(result, query_understanding)
            all_results.append(ranked)
        
        # Process and add research results
        for result in research_results:
            ranked = self._rank_research_result(result, query_understanding)
            all_results.append(ranked)
        
        # Apply filters
        if query_understanding.filters:
            all_results = self._apply_filters(all_results, query_understanding.filters)
        
        # Sort by combined score
        all_results.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Return top results (default 10)
        return all_results[:10]
    
    def _rank_knowledge_result(
        self,
        result: KnowledgeResult,
        query_understanding: QueryUnderstanding
    ) -> RankedResult:
        """Rank a knowledge base result"""
        content = result.content
        
        # Calculate relevance score
        relevance = result.relevance_score
        
        # Authority (knowledge base is authoritative)
        authority = 0.9 if content.get("evidence_tier") in ["very_high", "high"] else 0.7
        
        # Freshness (knowledge base may be older)
        freshness = 0.6
        
        # Safety score
        safety = self._calculate_safety_score(content, query_understanding)
        
        # Combined score
        combined = self._calculate_combined_score(
            relevance, authority, freshness, safety
        )
        
        return RankedResult(
            id=result.id,
            result_type="knowledge",
            content=content,
            combined_score=combined,
            relevance_score=relevance,
            authority_score=authority,
            freshness_score=freshness,
            safety_score=safety,
            source="knowledge_base"
        )
    
    def _rank_web_result(
        self,
        result: WebSearchResult,
        query_understanding: QueryUnderstanding
    ) -> RankedResult:
        """Rank a web search result"""
        # Use provided scores
        relevance = result.relevance_score
        authority = result.authority_score
        freshness = result.freshness_score
        
        # Safety score (estimate based on authority)
        safety = authority * 0.8
        
        # Combined score
        combined = self._calculate_combined_score(
            relevance, authority, freshness, safety
        )
        
        content = {
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet,
            "source": result.source,
            "type": "web_result"
        }
        
        return RankedResult(
            id=result.url,
            result_type="web",
            content=content,
            combined_score=combined,
            relevance_score=relevance,
            authority_score=authority,
            freshness_score=freshness,
            safety_score=safety,
            source=result.source
        )
    
    def _rank_research_result(
        self,
        result: ResearchResult,
        query_understanding: QueryUnderstanding
    ) -> RankedResult:
        """Rank a research result"""
        # Relevance based on evidence level
        evidence_to_relevance = {
            "very_high": 0.95,
            "high": 0.85,
            "moderate": 0.7,
            "low": 0.5
        }
        relevance = evidence_to_relevance.get(result.evidence_level, 0.7)
        
        # Authority (peer-reviewed papers are highly authoritative)
        authority = 0.95
        
        # Freshness (prefer recent studies)
        freshness = self._calculate_freshness(result.year)
        
        # Safety score (research is generally safe content)
        safety = 0.9
        
        # Combined score
        combined = self._calculate_combined_score(
            relevance, authority, freshness, safety
        )
        
        content = {
            "title": result.title,
            "authors": result.authors,
            "journal": result.journal,
            "year": result.year,
            "pmid": result.pmid,
            "abstract": result.abstract,
            "key_findings": result.key_findings,
            "evidence_level": result.evidence_level,
            "url": result.url,
            "type": "research_paper"
        }
        
        return RankedResult(
            id=result.pmid or result.title,
            result_type="research",
            content=content,
            combined_score=combined,
            relevance_score=relevance,
            authority_score=authority,
            freshness_score=freshness,
            safety_score=safety,
            source=result.journal
        )
    
    def _calculate_safety_score(
        self,
        content: Dict[str, Any],
        query_understanding: QueryUnderstanding
    ) -> float:
        """Calculate safety score for a result"""
        # Higher safety for evidence-backed content
        evidence_tier = content.get("evidence_tier", "moderate")
        evidence_safety = {
            "very_high": 0.95,
            "high": 0.85,
            "moderate": 0.7,
            "low": 0.5
        }
        base_safety = evidence_safety.get(evidence_tier, 0.7)
        
        # Adjust based on user filters
        if "safe" in query_understanding.modifiers:
            base_safety += 0.1
        
        if "beginner" in query_understanding.modifiers:
            if content.get("safe_for_beginners", False):
                base_safety += 0.1
        
        return min(base_safety, 1.0)
    
    def _calculate_combined_score(
        self,
        relevance: float,
        authority: float,
        freshness: float,
        safety: float
    ) -> float:
        """Calculate combined weighted score"""
        return (
            relevance * self.weights["relevance"] +
            authority * self.weights["authority"] +
            freshness * self.weights["freshness"] +
            safety * self.weights["safety"]
        )
    
    def _calculate_freshness(self, year: Optional[int]) -> float:
        """Calculate freshness score based on year"""
        if year is None:
            return 0.5
        
        current_year = 2026
        age = current_year - year
        
        if age <= 1:
            return 1.0
        elif age <= 2:
            return 0.9
        elif age <= 5:
            return 0.75
        elif age <= 10:
            return 0.6
        else:
            return 0.4
    
    def _apply_filters(
        self,
        results: List[RankedResult],
        filters: List[str]
    ) -> List[RankedResult]:
        """Apply user filters to results"""
        filtered = []
        
        for result in results:
            content = result.content
            
            # Apply each filter
            passes_filters = True
            
            for filter_str in filters:
                filter_lower = filter_str.lower()
                
                # Check tags
                tags = content.get("tags", [])
                if tags and any(filter_lower in tag.lower() for tag in tags):
                    continue
                
                # Check category
                category = content.get("category", "")
                if filter_lower in category.lower():
                    continue
                
                # Check domain
                domain = content.get("domain", "")
                if filter_lower in domain.lower():
                    continue
                
                passes_filters = False
                break
            
            if passes_filters:
                filtered.append(result)
        
        return filtered if filtered else results


# Singleton instance
ranking_agent = RankingAgent()


def rank_results(
    query_understanding: QueryUnderstanding,
    knowledge_results: List[KnowledgeResult],
    web_results: List[WebSearchResult],
    research_results: List[ResearchResult]
) -> List[RankedResult]:
    """
    Convenience function for ranking results.
    
    Args:
        query_understanding: Parsed query understanding
        knowledge_results: Results from Knowledge Base agent
        web_results: Results from Web Search agent
        research_results: Results from Research agent
        
    Returns:
        List of RankedResult objects
    """
    return ranking_agent.process(
        query_understanding,
        knowledge_results,
        web_results,
        research_results
    )
