"""
Research Agent - PubMed search
"""
import requests
from typing import List
from ..models import ResearchResult, QueryUnderstanding

class ResearchAgent:
    def __init__(self):
        self.pubmed_api_key = None  # Optional
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def process(self, query_understanding: QueryUnderstanding) -> List[ResearchResult]:
        query = query_understanding.original_query
        compound = query_understanding.compound
        
        search_term = compound if compound else query
        return self._search_pubmed(search_term)

    def _search_pubmed(self, term: str, max_results: int = 5) -> List[ResearchResult]:
        try:
            # Search for IDs
            search_url = f"{self.base_url}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": term,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            resp = requests.get(search_url, params=params, timeout=10)
            if resp.status_code != 200:
                return []
            
            ids = resp.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []
            
            # Fetch details
            fetch_url = f"{self.base_url}/esummary.fcgi"
            params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
            resp = requests.get(fetch_url, params=params, timeout=10)
            
            if resp.status_code != 200:
                return []
            
            results = []
            data = resp.json().get("result", {})
            for pmid in ids:
                article = data.get(pmid, {})
                if article:
                    results.append(ResearchResult(
                        title=article.get("title", ""),
                        authors=[a.get("name", "") for a in article.get("authors", [])],
                        journal=article.get("source", ""),
                        year=int(article.get("pubdate", "0")[:4]) or 2020,
                        pmid=pmid,
                        abstract=article.get("elocationid", ""),
                        key_findings=["See full paper for details"],
                        evidence_level="high" if "review" in article.get("title", "").lower() else "moderate",
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    ))
            return results
        except Exception as e:
            print(f"[PubMed Error] {e}")
            return []

    def _get_mock_results(self, query: str) -> List[ResearchResult]:
        return [
            ResearchResult(
                title=f"Research on {query} - Systematic Review",
                authors=["Various Researchers"],
                journal="Journal of Sports Science",
                year=2024,
                pmid="12345678",
                abstract=f"Systematic review of {query} effects and mechanisms.",
                key_findings=["Evidence supports use", "Dosing recommendations provided", "Safety profile established"],
                evidence_level="high",
                url=f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"
            )
        ]


agent = ResearchAgent()

def search_research(query_understanding: QueryUnderstanding) -> List[ResearchResult]:
    return agent.process(query_understanding)
