"""
Web Search Agent - Multi-source free search
"""
import requests
import time
from typing import List
from urllib.parse import quote
from ..models import WebSearchResult, QueryUnderstanding
from ..config import settings

class WebSearchAgent:
    def __init__(self):
        self.serper_api_key = settings.SERPER_API_KEY
        self.serp_api_key = settings.SERP_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.trusted_domains = {
            "examine.com": 0.9, "pubmed.ncbi.nlm.nih.gov": 0.95,
            "nih.gov": 0.95, "ncbi.nlm.nih.gov": 0.95,
            "mayoclinic.org": 0.9, "healthline.com": 0.7,
            "webmd.com": 0.65, "jissn.biomedcentral.com": 0.9,
            "nsca.com": 0.85, "journals.lww.com": 0.85,
        }

    def process(self, query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
        query = self._build_query(query_understanding)
        
        # Try Serper.dev first
        if self.serper_api_key:
            results = self._search_serper(query)
            if results:
                return results[:10]
        
        # Try Google CSE
        if self.serp_api_key and self.cse_id:
            results = self._search_google_cse(query)
            if results:
                return results[:10]
        
        # Fallback to DuckDuckGo
        results = self._search_duckduckgo(query)
        if results:
            return results[:10]
        
        return self._get_mock_results(query_understanding)

    def _build_query(self, q: QueryUnderstanding) -> str:
        parts = [q.original_query]
        if q.compound:
            parts.append(q.compound)
        if q.domain.value != "general":
            parts.append(q.domain.value)
        return " ".join(parts)

    def _search_serper(self, query: str) -> List[WebSearchResult]:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"},
                json={"q": query, "num": 10}, timeout=10
            )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("organic", []):
                url = item.get("link", "")
                results.append(WebSearchResult(
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("snippet", ""),
                    source=self._extract_domain(url),
                    authority_score=self._get_authority(url),
                    freshness_score=0.7,
                    relevance_score=0.8
                ))
            return results
        except Exception as e:
            print(f"[Serper Error] {e}")
            return []

    def _search_google_cse(self, query: str) -> List[WebSearchResult]:
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": self.serp_api_key, "cx": self.cse_id, "q": query, "num": 10},
                timeout=10
            )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("items", []):
                url = item.get("link", "")
                results.append(WebSearchResult(
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("snippet", ""),
                    source=self._extract_domain(url),
                    authority_score=self._get_authority(url),
                    freshness_score=0.7,
                    relevance_score=0.8
                ))
            return results
        except Exception as e:
            print(f"[Google CSE Error] {e}")
            return []

    def _search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        try:
            time.sleep(1)  # Rate limit
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            url = f"https://duckduckgo.com/html/?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return []
            
            results = []
            # Simple regex parsing instead of BeautifulSoup
            import re
            html = resp.text
            pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.DOTALL)
            
            for url, title, snippet in matches[:10]:
                results.append(WebSearchResult(
                    title=title.strip(),
                    url=url,
                    snippet=snippet.strip().replace("<b>", "").replace("</b>", ""),
                    source=self._extract_domain(url),
                    authority_score=self._get_authority(url),
                    freshness_score=0.6,
                    relevance_score=0.7
                ))
            return results
        except Exception as e:
            print(f"[DuckDuckGo Error] {e}")
            return []

    def _get_mock_results(self, q: QueryUnderstanding) -> List[WebSearchResult]:
        compound = q.compound or q.domain.value
        return [
            WebSearchResult(
                title=f"Examine.com - {compound}",
                url=f"https://examine.com/supplements/{compound.replace(' ', '-').lower()}/",
                snippet=f"Scientific analysis of {compound} including dosage and benefits.",
                source="examine.com",
                authority_score=0.9,
                freshness_score=0.8,
                relevance_score=0.9
            ),
            WebSearchResult(
                title=f"PubMed Research - {compound}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/?term={quote(compound)}",
                snippet="Peer-reviewed research papers.",
                source="pubmed.ncbi.nlm.nih.gov",
                authority_score=0.95,
                freshness_score=0.7,
                relevance_score=0.85
            ),
        ]

    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url

    def _get_authority(self, url: str) -> float:
        domain = self._extract_domain(url).lower()
        for trusted, score in self.trusted_domains.items():
            if trusted in domain:
                return score
        return 0.5


agent = WebSearchAgent()

def search_web(query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
    return agent.process(query_understanding)
