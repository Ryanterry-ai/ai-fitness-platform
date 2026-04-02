"""
Web Search Agent
================
Searches the web for relevant fitness and health content.
"""

import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import WebSearchResult, QueryUnderstanding
from config import settings
import time


class WebSearchAgent:
    """
    Agent responsible for web searching.
    
    Responsibilities:
    - Search Google API for web results
    - Fetch content from trusted sources
    - Prioritize authoritative sources
    - Return top results with snippets
    """
    
    def __init__(self):
        self.serp_api_key = settings.SERP_API_KEY
        self.trusted_domains = [
            "pubmed.ncbi.nlm.nih.gov",
            "nih.gov",
            "examine.com",
            "jissn.biomedcentral.com",
            "ncbi.nlm.nih.gov",
            "mayoclinic.org",
            "healthline.com",
            "webmd.com",
            "medicalnewstoday.com",
            "nsca.com",
            "j strengthcondres.com",
            " journals.lww.com",
        ]
        self.authority_weights = {
            "pubmed.ncbi.nlm.nih.gov": 0.95,
            "nih.gov": 0.95,
            "examine.com": 0.9,
            "jissn.biomedcentral.com": 0.9,
            "ncbi.nlm.nih.gov": 0.95,
            "mayoclinic.org": 0.9,
            "healthline.com": 0.7,
            "webmd.com": 0.7,
            "medicalnewstoday.com": 0.7,
            "nsca.com": 0.85,
            "j strengthcondres.com": 0.85,
            "journals.lww.com": 0.85,
            "youtube.com": 0.4,
            "reddit.com": 0.3,
            "quora.com": 0.25,
        }
    
    def process(self, query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
        """
        Search the web for relevant content.
        
        Args:
            query_understanding: Parsed query from QueryUnderstandingAgent
            
        Returns:
            List of WebSearchResult objects
        """
        query = self._build_search_query(query_understanding)
        
        # Try Google Search API first
        if self.serp_api_key:
            results = self._search_google_api(query)
            if results:
                return results[:10]
        
        # Fallback to DuckDuckGo or mock results
        results = self._search_duckduckgo(query)
        if results:
            return results[:10]
        
        # Return mock authoritative results
        return self._get_mock_results(query, query_understanding)
    
    def _build_search_query(self, query_understanding) -> str:
        """Build optimized search query from understanding"""
        query_parts = [query_understanding.original_query]
        
        # Add domain context
        if query_understanding.domain.value != "general":
            query_parts.append(query_understanding.domain.value)
        
        # Add compound name
        if query_understanding.compound:
            query_parts.append(query_understanding.compound)
        
        # Add intent context
        if query_understanding.intent.value == "dosage":
            query_parts.extend(["dosage", "protocol"])
        elif query_understanding.intent.value == "safety":
            query_parts.extend(["safety", "side effects", "risks"])
        elif query_understanding.intent.value == "research":
            query_parts.append("research study")
        
        return " ".join(query_parts)
    
    def _search_google_api(self, query: str) -> List[WebSearchResult]:
        """Search using Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.serp_api_key,
                "cx": "SEARCH_ENGINE_ID",  # Would need actual search engine ID
                "q": query,
                "num": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                result = WebSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=self._extract_domain(item.get("link", "")),
                    authority_score=self._get_authority_score(item.get("link", "")),
                    freshness_score=0.7,
                    relevance_score=self._calculate_relevance(item)
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Google API search error: {e}")
            return []
    
    def _search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        """Search using DuckDuckGo (no API key required)"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; FitSearchBot/1.0)"
            }
            
            # DuckDuckGo HTML search
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            results = []
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.select('.result')[:10]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link = result.select_one('a')
                
                if title_elem and link:
                    url = link.get('href', '')
                    results.append(WebSearchResult(
                        title=title_elem.get_text(strip=True),
                        url=url,
                        snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                        source=self._extract_domain(url),
                        authority_score=self._get_authority_score(url),
                        freshness_score=0.6,
                        relevance_score=0.5
                    ))
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def _get_mock_results(self, query: str, 
                         query_understanding) -> List[WebSearchResult]:
        """Return mock authoritative results when APIs are unavailable"""
        mock_results = [
            WebSearchResult(
                title=f"Examine.com - {query_understanding.compound or query_understanding.domain.value}",
                url=f"https://examine.com/supplements/{query_understanding.compound or query_understanding.domain.value}/",
                snippet=f"Comprehensive scientific analysis of {query_understanding.compound or query_understanding.domain.value} including dosage, benefits, and side effects.",
                source="examine.com",
                authority_score=0.9,
                freshness_score=0.8,
                relevance_score=0.9
            ),
            WebSearchResult(
                title=f"PubMed - {query_understanding.compound or query_understanding.original_query} research",
                url=f"https://pubmed.ncbi.nlm.nih.gov/?term={requests.utils.quote(query_understanding.original_query)}",
                snippet="Peer-reviewed research papers on the topic.",
                source="pubmed.ncbi.nlm.nih.gov",
                authority_score=0.95,
                freshness_score=0.7,
                relevance_score=0.85
            ),
            WebSearchResult(
                title=f"Healthline - {query_understanding.compound or query_understanding.domain.value} Guide",
                url=f"https://www.healthline.com/nutrition/{query_understanding.compound or query_understanding.domain.value}",
                snippet="Evidence-based guide with practical recommendations.",
                source="healthline.com",
                authority_score=0.75,
                freshness_score=0.7,
                relevance_score=0.8
            ),
        ]
        
        return mock_results
    
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
        
        for trusted, score in self.authority_weights.items():
            if trusted in domain:
                return score
        
        return 0.5  # Default score for unknown domains
    
    def _calculate_relevance(self, item: Dict[str, Any]) -> float:
        """Calculate relevance score for a search result"""
        score = 0.5
        
        title = item.get("title", "").lower()
        snippet = item.get("snippet", "").lower()
        
        # Boost for specific keywords
        if "study" in title or "research" in title:
            score += 0.1
        if "review" in title or "meta-analysis" in title:
            score += 0.15
        if "dosage" in title or "protocol" in title:
            score += 0.1
        
        return min(score, 1.0)


# Singleton instance
web_search_agent = WebSearchAgent()


def search_web(query_understanding: QueryUnderstanding) -> List[WebSearchResult]:
    """
    Convenience function for web search.
    
    Args:
        query_understanding: Parsed query from QueryUnderstandingAgent
        
    Returns:
        List of WebSearchResult objects
    """
    return web_search_agent.process(query_understanding)
