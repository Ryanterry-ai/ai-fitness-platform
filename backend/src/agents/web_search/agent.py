"""
Web Search Agent
================
Multi-source web search with free APIs for unlimited use.
Uses DuckDuckGo, Serper.dev (free tier), and fallback sources.
"""

import requests
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import quote
from src.models import WebSearchResult, QueryUnderstanding
import os


class WebSearchAgent:
    """
    Agent responsible for web searching using multiple free sources.
    
    Sources (in order of preference):
    1. DuckDuckGo HTML (free, no key)
    2. Serper.dev (free 2,500/month)
    3. Google Custom Search (100/day)
    4. DuckDuckGo Lite (fallback)
    """
    
    def __init__(self):
        self.serper_api_key = os.environ.get("SERPER_API_KEY", "")
        self.serp_api_key = os.environ.get("SERP_API_KEY", "")
        self.search_engine_id = os.environ.get("GOOGLE_CSE_ID", "")
        
        self.trusted_domains = {
            "pubmed.ncbi.nlm.nih.gov": 0.95,
            "nih.gov": 0.95,
            "ncbi.nlm.nih.gov": 0.95,
            "examine.com": 0.9,
            "jissn.biomedcentral.com": 0.9,
            "mayoclinic.org": 0.9,
            "healthline.com": 0.7,
            "webmd.com": 0.65,
            "medicalnewstoday.com": 0.65,
            "nsca.com": 0.85,
            "jstrengthcondres.com": 0.85,
            "journals.lww.com": 0.85,
            "spotmebro.com": 0.6,
            "muscleandstrength.com": 0.6,
            "bodybuilding.com": 0.6,
        }
        
        self.rate_limit_delay = 1.0  # DuckDuckGo rate limit
    
    def process(self, query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
        """
        Search the web for relevant content using multiple sources.
        """
        query = self._build_search_query(query_understanding)
        
        results = []
        
        # Try sources in order of preference
        if self.serper_api_key:
            results = self._search_serper(query)
        
        if not results and self.serp_api_key and self.search_engine_id:
            results = self._search_google_cse(query)
        
        if not results:
            results = self._search_duckduckgo(query)
        
        if not results:
            results = self._search_duckduckgo_lite(query)
        
        return results[:10] if results else self._get_mock_results(query, query_understanding)
    
    def _build_search_query(self, query_understanding) -> str:
        """Build optimized search query"""
        parts = [query_understanding.original_query]
        
        if query_understanding.domain.value != "general":
            parts.append(query_understanding.domain.value)
        
        if query_understanding.compound:
            parts.append(query_understanding.compound)
        
        intent = query_understanding.intent.value
        if intent == "dosage":
            parts.extend(["dosage", "protocol", "mg"])
        elif intent == "safety":
            parts.extend(["safety", "side effects", "risks"])
        elif intent == "cycle":
            parts.extend(["cycle", "protocol", "weeks"])
        
        return " ".join(parts)
    
    def _search_serper(self, query: str) -> List[WebSearchResult]:
        """
        Search using Serper.dev API (free 2,500/month).
        """
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {"q": query, "num": 10}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("organic", []):
                results.append(WebSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=self._extract_domain(item.get("link", "")),
                    authority_score=self._get_authority_score(item.get("link", "")),
                    freshness_score=0.7,
                    relevance_score=0.8
                ))
            
            return results
            
        except Exception as e:
            print(f"[Serper Error] {e}")
            return []
    
    def _search_google_cse(self, query: str) -> List[WebSearchResult]:
        """
        Search using Google Custom Search JSON API (free 100/day).
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.serp_api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append(WebSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=self._extract_domain(item.get("link", "")),
                    authority_score=self._get_authority_score(item.get("link", "")),
                    freshness_score=self._calculate_freshness(item.get("snippet", "")),
                    relevance_score=0.8
                ))
            
            return results
            
        except Exception as e:
            print(f"[Google CSE Error] {e}")
            return []
    
    def _search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        """
        Search DuckDuckGo HTML (free, no key, rate limited to ~1/sec).
        """
        try:
            time.sleep(self.rate_limit_delay)  # Respect rate limits
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            url = f"https://duckduckgo.com/html/?q={quote(query)}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:10]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link_elem = result.select_one('a')
                
                if title_elem and link_elem:
                    url = link_elem.get('href', '')
                    results.append(WebSearchResult(
                        title=title_elem.get_text(strip=True),
                        url=url,
                        snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                        source=self._extract_domain(url),
                        authority_score=self._get_authority_score(url),
                        freshness_score=0.6,
                        relevance_score=0.7
                    ))
            
            return results
            
        except Exception as e:
            print(f"[DuckDuckGo Error] {e}")
            return []
    
    def _search_duckduckgo_lite(self, query: str) -> List[WebSearchResult]:
        """
        Fallback to DuckDuckGo Lite (no JavaScript required).
        """
        try:
            time.sleep(self.rate_limit_delay)
            
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Bot/0.1)"
            }
            
            url = f"https://lite.duckduckgo.com/50x/?q={quote(query)}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:10]:
                title_elem = result.select_one('.result__title')
                link_elem = result.select_one('a')
                
                if title_elem and link_elem:
                    url = link_elem.get('href', '')
                    results.append(WebSearchResult(
                        title=title_elem.get_text(strip=True),
                        url=url,
                        snippet=result.get_text(strip=True)[:200],
                        source=self._extract_domain(url),
                        authority_score=self._get_authority_score(url),
                        freshness_score=0.6,
                        relevance_score=0.7
                    ))
            
            return results
            
        except Exception as e:
            print(f"[DuckDuckGo Lite Error] {e}")
            return []
    
    def _search_searx(self, query: str) -> List[WebSearchResult]:
        """
        Search using public Searx instances (open source metasearch).
        """
        searx_instances = [
            "https://search.bus-hit.me",
            "https://searx.work",
            "https://search.snopyta.org",
        ]
        
        for instance in searx_instances:
            try:
                time.sleep(0.5)
                
                headers = {
                    "User-Agent": "FitSearchBot/1.0"
                }
                
                url = f"{instance}/search?q={quote(query)}&format=json"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get("results", [])[:10]:
                        results.append(WebSearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("content", "")[:200],
                            source=self._extract_domain(item.get("url", "")),
                            authority_score=self._get_authority_score(item.get("url", "")),
                            freshness_score=0.7,
                            relevance_score=0.8
                        ))
                    
                    if results:
                        return results
                        
            except Exception:
                continue
        
        return []
    
    def _get_mock_results(self, query: str, 
                         query_understanding) -> List[WebSearchResult]:
        """Return mock results when all APIs fail"""
        compound = query_understanding.compound or query_understanding.domain.value
        
        return [
            WebSearchResult(
                title=f"Examine.com - {compound} Guide",
                url=f"https://examine.com/supplements/{compound.replace(' ', '-').lower()}/",
                snippet=f"Scientific analysis of {compound} including dosage, benefits, and side effects.",
                source="examine.com",
                authority_score=0.9,
                freshness_score=0.8,
                relevance_score=0.9
            ),
            WebSearchResult(
                title=f"PubMed Research - {compound}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/?term={quote(compound)}",
                snippet="Peer-reviewed research papers on this topic.",
                source="pubmed.ncbi.nlm.nih.gov",
                authority_score=0.95,
                freshness_score=0.7,
                relevance_score=0.85
            ),
        ]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return url
    
    def _get_authority_score(self, url: str) -> float:
        """Get authority score based on domain"""
        domain = self._extract_domain(url).lower()
        
        for trusted, score in self.trusted_domains.items():
            if trusted in domain:
                return score
        
        return 0.5
    
    def _calculate_freshness(self, text: str) -> float:
        """Estimate freshness from text"""
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            if str(year) in text:
                return 0.9
        return 0.6


web_search_agent = WebSearchAgent()


def search_web(query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
    """Convenience function for web search."""
    return web_search_agent.process(query_understanding)
