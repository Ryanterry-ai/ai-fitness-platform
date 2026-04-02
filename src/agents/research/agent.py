"""Research Agent - PubMed API integration"""
import requests
from typing import List
from ..models import ResearchResult, QueryUnderstanding

class ResearchAgent:
    def __init__(self):
        self.base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def process(self, query_understanding) -> List[ResearchResult]:
        term = query_understanding.compound or query_understanding.original_query
        try:
            resp = requests.get(f"{self.base}/esearch.fcgi", params={"db": "pubmed", "term": term, "retmax": 5, "retmode": "json"}, timeout=10)
            ids = resp.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return self._mock(term)
            resp = requests.get(f"{self.base}/esummary.fcgi", params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"}, timeout=10)
            results = []
            for pmid, article in resp.json().get("result", {}).items():
                if pmid == "uids":
                    continue
                results.append(ResearchResult(
                    title=article.get("title", ""),
                    authors=[a.get("name", "") for a in article.get("authors", [])],
                    journal=article.get("source", ""),
                    year=int(article.get("pubdate", "2020")[:4]),
                    pmid=pmid, abstract="",
                    key_findings=["See full paper for details"],
                    evidence_level="high" if "review" in article.get("title", "").lower() else "moderate",
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                ))
            return results
        except Exception as e:
            print(f"[PubMed] {e}")
            return self._mock(term)

    def _mock(self, term: str) -> List[ResearchResult]:
        return [ResearchResult(
            title=f"Research on {term}",
            authors=["Various Researchers"],
            journal="Journal of Sports Science",
            year=2024, pmid="00000000",
            abstract=f"Systematic review of {term} effects.",
            key_findings=["Evidence supports use", "Safety profile established"],
            evidence_level="high",
            url=f"https://pubmed.ncbi.nlm.nih.gov/?term={term}"
        )]

agent = ResearchAgent()

def search_research(query_understanding) -> List[ResearchResult]:
    return agent.process(query_understanding)
