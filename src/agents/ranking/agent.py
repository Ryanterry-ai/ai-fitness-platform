"""Ranking Agent"""
from typing import List
from ..models import RankedResult, KnowledgeResult, WebSearchResult, ResearchResult, QueryUnderstanding

class RankingAgent:
    def __init__(self):
        self.w = {"relevance": 0.35, "authority": 0.30, "freshness": 0.15, "safety": 0.20}

    def process(self, query, knowledge: List, web: List, research: List) -> List[RankedResult]:
        results = []
        for r in knowledge:
            c = r.content
            auth = 0.9 if c.get("evidence_tier") in ["very_high", "high"] else 0.7
            score = 0.35*r.relevance_score + 0.30*auth + 0.15*0.6 + 0.20*0.8
            results.append(RankedResult(id=r.id, result_type="knowledge", content=c, combined_score=score,
                relevance_score=r.relevance_score, authority_score=auth, freshness_score=0.6, safety_score=0.8, source="knowledge"))
        for r in web:
            score = 0.35*r.relevance_score + 0.30*r.authority_score + 0.15*r.freshness_score + 0.20*r.authority_score*0.8
            results.append(RankedResult(id=r.url, result_type="web", content={"title": r.title, "url": r.url, "snippet": r.snippet, "source": r.source},
                combined_score=score, relevance_score=r.relevance_score, authority_score=r.authority_score, freshness_score=r.freshness_score,
                safety_score=r.authority_score*0.8, source=r.source))
        for r in research:
            ev = {"very_high": 0.95, "high": 0.85, "moderate": 0.7, "low": 0.5}
            rel = ev.get(r.evidence_level, 0.7)
            score = 0.35*rel + 0.30*0.95 + 0.15*0.7 + 0.20*0.9
            results.append(RankedResult(id=r.pmid or r.title, result_type="research", content={"title": r.title, "authors": r.authors, "journal": r.journal, "year": r.year, "abstract": r.abstract, "url": r.url},
                combined_score=score, relevance_score=rel, authority_score=0.95, freshness_score=0.7, safety_score=0.9, source=r.journal))
        results.sort(key=lambda x: x.combined_score, reverse=True)
        return results[:10]

agent = RankingAgent()

def rank_results(query, knowledge: List, web: List, research: List) -> List[RankedResult]:
    return agent.process(query, knowledge, web, research)
