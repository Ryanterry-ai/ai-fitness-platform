"""
Ranking Agent
"""
from typing import List
from ..models import RankedResult, KnowledgeResult, WebSearchResult, ResearchResult, QueryUnderstanding

class RankingAgent:
    def __init__(self):
        self.weights = {"relevance": 0.35, "authority": 0.30, "freshness": 0.15, "safety": 0.20}

    def process(self, query: QueryUnderstanding, knowledge: List, web: List, research: List) -> List[RankedResult]:
        results = []
        
        for r in knowledge:
            results.append(self._rank_knowledge(r))
        
        for r in web:
            results.append(self._rank_web(r))
        
        for r in research:
            results.append(self._rank_research(r))
        
        results.sort(key=lambda x: x.combined_score, reverse=True)
        return results[:10]

    def _rank_knowledge(self, result: KnowledgeResult) -> RankedResult:
        content = result.content
        authority = 0.9 if content.get("evidence_tier") in ["very_high", "high"] else 0.7
        combined = 0.35 * result.relevance_score + 0.30 * authority + 0.15 * 0.6 + 0.20 * 0.8
        return RankedResult(
            id=result.id,
            result_type="knowledge",
            content=content,
            combined_score=combined,
            relevance_score=result.relevance_score,
            authority_score=authority,
            freshness_score=0.6,
            safety_score=0.8,
            source="knowledge_base"
        )

    def _rank_web(self, result: WebSearchResult) -> RankedResult:
        combined = (0.35 * result.relevance_score + 0.30 * result.authority_score + 
                   0.15 * result.freshness_score + 0.20 * result.authority_score * 0.8)
        return RankedResult(
            id=result.url,
            result_type="web",
            content={"title": result.title, "url": result.url, "snippet": result.snippet, "source": result.source},
            combined_score=combined,
            relevance_score=result.relevance_score,
            authority_score=result.authority_score,
            freshness_score=result.freshness_score,
            safety_score=result.authority_score * 0.8,
            source=result.source
        )

    def _rank_research(self, result: ResearchResult) -> RankedResult:
        evidence_map = {"very_high": 0.95, "high": 0.85, "moderate": 0.7, "low": 0.5}
        relevance = evidence_map.get(result.evidence_level, 0.7)
        combined = 0.35 * relevance + 0.30 * 0.95 + 0.15 * 0.7 + 0.20 * 0.9
        return RankedResult(
            id=result.pmid or result.title,
            result_type="research",
            content={"title": result.title, "authors": result.authors, "journal": result.journal, "year": result.year, "abstract": result.abstract, "url": result.url},
            combined_score=combined,
            relevance_score=relevance,
            authority_score=0.95,
            freshness_score=0.7,
            safety_score=0.9,
            source=result.journal
        )


agent = RankingAgent()

def rank_results(query: QueryUnderstanding, knowledge: List, web: List, research: List) -> List[RankedResult]:
    return agent.process(query, knowledge, web, research)
