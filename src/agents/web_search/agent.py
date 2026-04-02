"""
Web Search Agent - Multi-source search with free APIs
"""
import requests
import time
import re
from typing import List
from urllib.parse import quote, urlparse
from ..models import WebSearchResult, QueryUnderstanding
from ..config import settings

class WebSearchAgent:
    def __init__(self):
        self.serper_key = settings.SERPER_API_KEY
        self.serp_key = settings.SERP_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.trusted = {
            "examine.com": 0.9, "pubmed.ncbi.nlm.nih.gov": 0.95,
            "nih.gov": 0.95, "ncbi.nlm.nih.gov": 0.95,
            "mayoclinic.org": 0.9, "healthline.com": 0.7,
            "webmd.com": 0.65, "jissn.biomedcentral.com": 0.9,
            "nsca.com": 0.85, "journals.lww.com": 0.85
        }

    def process(self, query_understanding) -> List[WebSearchResult]:
        query = self._build_query(query_understanding)
        
        if self.serper_key:
            results = self._search_serper(query)
            if results:
                return results[:10]
        
        if self.serp_key and self.cse_id:
            results = self._search_google(query)
            if results:
                return results[:10]
        
        return self._search_duckduckgo(query)[:10] or self._mock_results(query_understanding)

    def _build_query(self, q) -> str:
        parts = [q.original_query]
        if q.compound:
            parts.insert(0, q.compound)
        if q.intent.value != "informational":
            parts.append(q.intent.value.replace("_", " "))
        return " ".join(parts)

    def _search_serper(self, query: str) -> List[WebSearchResult]:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_key, "Content-Type": "application/json"},
                json={"q": query, "num": 10}, timeout=10
            )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("organic", []):
                url = item.get("link", "")
                results.append(WebSearchResult(
                    title=item.get("title", ""),
                    url=url, snippet=item.get("snippet", ""),
                    source=self._domain(url), authority_score=self._auth(url),
                    freshness_score=0.7, relevance_score=0.8
                ))
            return results
        except Exception as e:
            print(f"[Serper] {e}")
            return []

    def _search_google(self, query: str) -> List[WebSearchResult]:
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": self.serp_key, "cx": self.cse_id, "q": query, "num": 10},
                timeout=10
            )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("items", []):
                url = item.get("link", "")
                results.append(WebSearchResult(
                    title=item.get("title", ""), url=url, snippet=item.get("snippet", ""),
                    source=self._domain(url), authority_score=self._auth(url),
                    freshness_score=0.7, relevance_score=0.8
                ))
            return results
        except Exception as e:
            print(f"[Google] {e}")
            return []

    def _search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        try:
            time.sleep(1)
            resp = requests.get(
                f"https://duckduckgo.com/html/?q={quote(query)}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            if resp.status_code != 200:
                return []
            results = []
            for match in re.finditer(r'<a class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>', resp.text, re.DOTALL):
                url, title, snippet = match.groups()
                results.append(WebSearchResult(
                    title=title.strip(), url=url, snippet=snippet.strip().replace("<b>", "").replace("</b>", ""),
                    source=self._domain(url), authority_score=self._auth(url),
                    freshness_score=0.6, relevance_score=0.7
                ))
                if len(results) >= 10:
                    break
            return results
        except Exception as e:
            print(f"[DDG] {e}")
            return []

    def _mock_results(self, q) -> List[WebSearchResult]:
        c = q.compound or q.domain.value
        return [
            WebSearchResult(title=f"Examine.com - {c}", url=f"https://examine.com/supplements/{c.lower().replace(' ', '-')}/",
                snippet=f"Scientific analysis of {c} including dosage and benefits.", source="examine.com",
                authority_score=0.9, freshness_score=0.8, relevance_score=0.9),
            WebSearchResult(title=f"PubMed Research - {c}", url=f"https://pubmed.ncbi.nlm.nih.gov/?term={quote(c)}",
                snippet="Peer-reviewed research papers.", source="pubmed.ncbi.nlm.nih.gov",
                authority_score=0.95, freshness_score=0.7, relevance_score=0.85)
        ]

    def _domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url

    def _auth(self, url: str) -> float:
        d = self._domain(url).lower()
        for k, v in self.trusted.items():
            if k in d:
                return v
        return 0.5

agent = WebSearchAgent()

def search_web(query_understanding) -> List[WebSearchResult]:
    return agent.process(query_understanding)
