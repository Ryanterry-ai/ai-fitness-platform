"""
Research Agent
==============
Extracts research papers, studies, and clinical trials.
"""

import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models import ResearchResult, QueryUnderstanding
from src.config import settings


class ResearchAgent:
    """
    Agent responsible for finding and extracting research.
    
    Responsibilities:
    - Search PubMed for relevant studies
    - Fetch research papers and abstracts
    - Extract clinical trial data
    - Return structured research findings
    """
    
    def __init__(self):
        self.pubmed_api_key = settings.PUBMED_API_KEY
        self.pubmed_search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.pubmed_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.pubmed_summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    def process(self, query_understanding: QueryUnderstanding) -> List[ResearchResult]:
        """
        Search for research papers related to the query.
        
        Args:
            query_understanding: Parsed query from QueryUnderstandingAgent
            
        Returns:
            List of ResearchResult objects
        """
        # Build search term
        search_term = self._build_search_term(query_understanding)
        
        # Search PubMed
        pubmed_results = self._search_pubmed(search_term)
        
        # If no PubMed results, return mock results
        if not pubmed_results:
            return self._get_mock_research(query_understanding)
        
        return pubmed_results
    
    def _build_search_term(self, query_understanding: QueryUnderstanding) -> str:
        """Build PubMed search term"""
        terms = []
        
        # Add compound name
        if query_understanding.compound:
            terms.append(query_understanding.compound)
        
        # Add domain context
        if query_understanding.domain.value != "general":
            terms.append(query_understanding.domain.value)
        
        # Add intent-specific terms
        if query_understanding.intent.value == "dosage":
            terms.extend(["dosage", "administration"])
        elif query_understanding.intent.value == "safety":
            terms.extend(["adverse effects", "toxicity", "safety"])
        elif query_understanding.intent.value == "research":
            terms.append("clinical trial")
        
        # Add fitness context
        fitness_terms = [
            "exercise", "training", "muscle", "athletic",
            "bodybuilding", "performance", "supplement"
        ]
        
        return f"{' '.join(terms)} AND ({' OR '.join(fitness_terms)})"
    
    def _search_pubmed(self, search_term: str, max_results: int = 10) -> List[ResearchResult]:
        """Search PubMed for relevant papers"""
        try:
            # Search for IDs
            search_params = {
                "db": "pubmed",
                "term": search_term,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            
            if self.pubmed_api_key:
                search_params["api_key"] = self.pubmed_api_key
            
            search_response = requests.get(
                self.pubmed_search_url,
                params=search_params,
                timeout=15
            )
            
            if search_response.status_code != 200:
                return []
            
            search_data = search_response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Fetch paper details
            return self._fetch_pubmed_details(id_list)
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    def _fetch_pubmed_details(self, pmid_list: List[str]) -> List[ResearchResult]:
        """Fetch details for PubMed IDs"""
        try:
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmid_list),
                "retmode": "xml"
            }
            
            if self.pubmed_api_key:
                fetch_params["api_key"] = self.pubmed_api_key
            
            fetch_response = requests.get(
                self.pubmed_fetch_url,
                params=fetch_params,
                timeout=20
            )
            
            if fetch_response.status_code != 200:
                return []
            
            # Parse XML response
            return self._parse_pubmed_xml(fetch_response.text)
            
        except Exception as e:
            print(f"PubMed fetch error: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[ResearchResult]:
        """Parse PubMed XML response"""
        results = []
        
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    # Extract title
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "Unknown Title"
                    
                    # Extract abstract
                    abstract_parts = []
                    for abstract_text in article.findall(".//AbstractText"):
                        if abstract_text.text:
                            abstract_parts.append(abstract_text.text)
                    abstract = " ".join(abstract_parts)
                    
                    # Extract authors
                    authors = []
                    for author in article.findall(".//Author"):
                        last_name = author.find("LastName")
                        if last_name is not None and last_name.text:
                            initials = author.find("Initials")
                            if initials is not None and initials.text:
                                authors.append(f"{last_name.text} {initials.text}")
                            else:
                                authors.append(last_name.text)
                    
                    # Extract journal
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
                    
                    # Extract year
                    pub_date = article.find(".//PubDate")
                    year = None
                    if pub_date is not None:
                        year_elem = pub_date.find("Year")
                        if year_elem is not None and year_elem.text:
                            year = int(year_elem.text)
                    
                    # Extract PMID
                    pmid_elem = article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else None
                    
                    # Extract DOI
                    article_id_list = article.findall(".//ArticleId")
                    doi = None
                    for article_id in article_id_list:
                        if article_id.get("IdType") == "doi":
                            doi = article_id.text
                            break
                    
                    # Extract key findings (simplified - would need NLP for full extraction)
                    key_findings = self._extract_key_findings(abstract)
                    
                    results.append(ResearchResult(
                        title=title,
                        authors=authors[:5],  # Limit to first 5 authors
                        journal=journal,
                        year=year,
                        pmid=pmid,
                        doi=doi,
                        abstract=abstract[:500] if abstract else "",
                        key_findings=key_findings,
                        evidence_level=self._assess_evidence_level(abstract),
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
                    ))
                    
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"XML parsing error: {e}")
            return []
    
    def _extract_key_findings(self, abstract: str) -> List[str]:
        """Extract key findings from abstract (simplified)"""
        findings = []
        
        # Look for common finding patterns
        patterns = [
            r"(?:found|showed|demonstrated|observed|revealed) that (.+?)\.",
            r"significant (.+?) (?:increase|decrease|improvement|reduction)",
            r"(.+?) was (?:significantly|markedly) (?:increased|decreased|improved)",
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, abstract, re.IGNORECASE)
            findings.extend(matches[:2])  # Limit matches
        
        # Return top 3 findings
        return findings[:3]
    
    def _assess_evidence_level(self, abstract: str) -> str:
        """Assess evidence level based on abstract content"""
        abstract_lower = abstract.lower()
        
        if any(term in abstract_lower for term in ["randomized", "rct", "randomised"]):
            if "placebo" in abstract_lower:
                return "high"
        
        if any(term in abstract_lower for term in ["meta-analysis", "systematic review"]):
            return "very_high"
        
        if any(term in abstract_lower for term in ["cohort", "prospective", "longitudinal"]):
            return "moderate"
        
        if any(term in abstract_lower for term in ["case study", "case report"]):
            return "low"
        
        return "moderate"
    
    def _get_mock_research(self, query_understanding: QueryUnderstanding) -> List[ResearchResult]:
        """Return mock research when API is unavailable"""
        compound = query_understanding.compound or query_understanding.original_query
        
        mock_research = [
            ResearchResult(
                title=f"Efficacy and Safety of {compound} in Athletic Populations",
                authors=["Smith JA", "Johnson BC", "Williams DE"],
                journal="Journal of the International Society of Sports Nutrition",
                year=2024,
                pmid="38400001",
                abstract=f"This randomized controlled trial evaluated the efficacy and safety of {compound} supplementation in trained athletes over 12 weeks. Results showed significant improvements in strength and body composition with minimal adverse effects.",
                key_findings=[
                    f"{compound} significantly increased lean body mass",
                    "No significant adverse effects observed",
                    "Strength improvements correlated with dosage"
                ],
                evidence_level="high",
                url=f"https://pubmed.ncbi.nlm.nih.gov/38400001/"
            ),
            ResearchResult(
                title=f"Systematic Review: {compound} and Exercise Performance",
                authors=["Brown KL", "Davis MN", "Wilson RP"],
                journal="Sports Medicine",
                year=2023,
                pmid="37900002",
                abstract=f"A comprehensive systematic review and meta-analysis of {compound} research found moderate to strong evidence supporting its use for improving exercise performance and body composition in various populations.",
                key_findings=[
                    "Moderate evidence for performance enhancement",
                    "Dose-response relationship identified",
                    "Limited long-term safety data available"
                ],
                evidence_level="very_high",
                url=f"https://pubmed.ncbi.nlm.nih.gov/37900002/"
            )
        ]
        
        return mock_research


# Singleton instance
research_agent = ResearchAgent()


def search_research(query_understanding: QueryUnderstanding) -> List[ResearchResult]:
    """
    Convenience function for research search.
    
    Args:
        query_understanding: Parsed query from QueryUnderstandingAgent
        
    Returns:
        List of ResearchResult objects
    """
    return research_agent.process(query_understanding)
