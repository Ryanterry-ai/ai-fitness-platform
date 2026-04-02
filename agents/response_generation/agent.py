"""
Response Generation Agent
========================
Generates structured AI responses from ranked results.
"""

from typing import List, Dict, Any, Optional
from models import RankedResult, QueryUnderstanding, SafetyWarning, SafetyStatus


class ResponseGenerationAgent:
    """
    Agent responsible for generating structured responses.
    
    Responsibilities:
    - Generate comprehensive AI responses
    - Structure output into sections
    - Include all relevant information
    - Format for different intents
    - Add references and sources
    """
    
    # Section templates for different content types
    SECTION_TEMPLATES = {
        "compound": [
            "overview",
            "what_it_is",
            "how_it_works",
            "types",
            "dosage",
            "timing",
            "benefits",
            "side_effects",
            "safety",
            "cycling",
            "stacking",
            "references"
        ],
        "exercise": [
            "overview",
            "what_it_is",
            "how_it_works",
            "proper_form",
            "variations",
            "programming",
            "common_mistakes",
            "references"
        ],
        "nutrition": [
            "overview",
            "macros",
            "timing",
            "food_sources",
            "supplements",
            "meal_planning",
            "references"
        ],
        "research": [
            "overview",
            "key_findings",
            "study_details",
            "implications",
            "limitations",
            "references"
        ]
    }
    
    def process(
        self,
        query_understanding: QueryUnderstanding,
        ranked_results: List[RankedResult],
        safety_warning: SafetyWarning
    ) -> Dict[str, Any]:
        """
        Generate structured response from ranked results.
        
        Args:
            query_understanding: Parsed query understanding
            ranked_results: Ranked results from Ranking agent
            safety_warning: Safety warning from Safety agent
            
        Returns:
            Structured response dictionary
        """
        if not ranked_results:
            return self._generate_empty_response(query_understanding)
        
        # Determine content type
        content_type = self._determine_content_type(query_understanding, ranked_results)
        
        # Get primary result
        primary_result = ranked_results[0]
        
        # Generate sections
        sections = self._generate_sections(
            primary_result,
            content_type,
            query_understanding,
            ranked_results
        )
        
        # Generate AI summary
        ai_summary = self._generate_ai_summary(
            primary_result,
            query_understanding
        )
        
        # Collect references
        references = self._collect_references(ranked_results)
        
        # Build final response
        response = {
            "query": query_understanding.original_query,
            "query_understanding": {
                "intent": query_understanding.intent.value,
                "domain": query_understanding.domain.value,
                "compound": query_understanding.compound,
                "goal": query_understanding.goal,
                "risk_level": query_understanding.risk_level.value,
                "confidence": query_understanding.confidence
            },
            "results": ranked_results,
            "sections": sections,
            "ai_summary": ai_summary,
            "safety": {
                "status": safety_warning.status.value,
                "warnings": safety_warning.warnings,
                "recommendations": safety_warning.recommendations,
                "disclaimers": safety_warning.disclaimers
            },
            "references": references,
            "content_type": content_type
        }
        
        return response
    
    def _generate_empty_response(self, query_understanding: QueryUnderstanding) -> Dict[str, Any]:
        """Generate response when no results found"""
        return {
            "query": query_understanding.original_query,
            "query_understanding": {
                "intent": query_understanding.intent.value,
                "domain": query_understanding.domain.value,
                "compound": query_understanding.compound,
                "goal": query_understanding.goal,
                "risk_level": query_understanding.risk_level.value
            },
            "results": [],
            "sections": {
                "overview": "No results found for your query. Try different keywords or broaden your search."
            },
            "ai_summary": "I couldn't find specific information for your query. Please try rephrasing or contact support.",
            "safety": {
                "status": "safe",
                "warnings": [],
                "recommendations": ["Try different search terms"],
                "disclaimers": ["This information is for educational purposes only"]
            },
            "references": [],
            "content_type": "general"
        }
    
    def _determine_content_type(
        self,
        query_understanding: QueryUnderstanding,
        ranked_results: List[RankedResult]
    ) -> str:
        """Determine the content type for section generation"""
        # Check query understanding first
        domain = query_understanding.domain.value
        
        if domain in ["sarms", "steroids", "peptides", "hgh"]:
            return "compound"
        elif domain in ["supplements"]:
            if query_understanding.intent.value == "research":
                return "research"
            return "compound"
        elif domain == "exercise":
            return "exercise"
        elif domain == "nutrition":
            return "nutrition"
        
        # Check primary result type
        if ranked_results:
            result_type = ranked_results[0].result_type
            if result_type == "research":
                return "research"
            elif result_type == "knowledge":
                content = ranked_results[0].content
                category = content.get("category", "")
                if category in ["sarms", "steroids", "peptides"]:
                    return "compound"
        
        return "general"
    
    def _generate_sections(
        self,
        primary_result: RankedResult,
        content_type: str,
        query_understanding: QueryUnderstanding,
        ranked_results: List[RankedResult]
    ) -> Dict[str, Any]:
        """Generate sections for the response"""
        content = primary_result.content
        sections = {}
        
        if content_type == "compound":
            sections = self._generate_compound_sections(content, query_understanding)
        elif content_type == "exercise":
            sections = self._generate_exercise_sections(content, query_understanding)
        elif content_type == "nutrition":
            sections = self._generate_nutrition_sections(content, query_understanding)
        elif content_type == "research":
            sections = self._generate_research_sections(content)
        else:
            sections = self._generate_general_sections(content, query_understanding)
        
        return sections
    
    def _generate_compound_sections(
        self,
        content: Dict[str, Any],
        query_understanding: QueryUnderstanding
    ) -> Dict[str, Any]:
        """Generate sections for compound content"""
        sections = {
            "overview": {
                "name": content.get("name", ""),
                "tagline": content.get("summary", content.get("tagline", "")),
                "category": content.get("category", ""),
                "evidence_tier": content.get("evidence_tier", "moderate"),
                "safe_for_beginners": content.get("safe_for_beginners", False)
            },
            "what_it_is": content.get("what_it_is", content.get("summary", "")),
            "how_it_works": content.get("how_it_works", "Mechanism of action not available."),
            "types": content.get("types", []),
            "dosage": {
                "text": content.get("dosage", "Dosage information not available."),
                "note": "Always consult a healthcare professional before starting any compound."
            },
            "timing": content.get("timing", "Timing information not available."),
            "benefits": content.get("benefits", []),
            "side_effects": content.get("side_effects", []),
            "cycling": content.get("cycling", "Cycling information not available."),
            "stacking": content.get("stacking", []),
            "references": content.get("references", [])
        }
        
        # Add legal status if available
        if "legal_status" in content:
            sections["legal_status"] = content["legal_status"]
        
        # Add products if relevant
        if "products" in content:
            sections["products"] = content["products"]
        
        return sections
    
    def _generate_exercise_sections(
        self,
        content: Dict[str, Any],
        query_understanding: QueryUnderstanding
    ) -> Dict[str, Any]:
        """Generate sections for exercise content"""
        return {
            "overview": {
                "name": content.get("name", ""),
                "muscles": content.get("muscles", []),
                "evidence_tier": content.get("evidence_tier", "moderate")
            },
            "what_it_is": content.get("summary", "Exercise information not available."),
            "proper_form": content.get("setup", ""),
            "cues": content.get("cues", []),
            "variations": content.get("variations", []),
            "programming": {
                "sets": "3-4",
                "reps": content.get("reps", "8-12"),
                "frequency": "2-3x per week"
            }
        }
    
    def _generate_nutrition_sections(
        self,
        content: Dict[str, Any],
        query_understanding: QueryUnderstanding
    ) -> Dict[str, Any]:
        """Generate sections for nutrition content"""
        return {
            "overview": {
                "name": content.get("name", ""),
                "summary": content.get("summary", "")
            },
            "macros": content.get("recommendations", {}),
            "timing": content.get("timing", ""),
            "food_sources": content.get("food_sources", []),
            "supplements": content.get("supplements", [])
        }
    
    def _generate_research_sections(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sections for research content"""
        return {
            "overview": {
                "title": content.get("title", ""),
                "journal": content.get("journal", ""),
                "year": content.get("year", ""),
                "authors": content.get("authors", [])
            },
            "key_findings": content.get("key_findings", []),
            "abstract": content.get("abstract", ""),
            "evidence_level": content.get("evidence_level", "moderate"),
            "url": content.get("url", "")
        }
    
    def _generate_general_sections(
        self,
        content: Dict[str, Any],
        query_understanding: QueryUnderstanding
    ) -> Dict[str, Any]:
        """Generate sections for general content"""
        return {
            "overview": content.get("summary", content.get("name", "")),
            "details": content.get("what_it_is", content.get("summary", "")),
            "recommendations": content.get("best_ways_to_use", [])
        }
    
    def _generate_ai_summary(
        self,
        primary_result: RankedResult,
        query_understanding: QueryUnderstanding
    ) -> str:
        """Generate AI summary from primary result"""
        content = primary_result.content
        
        # Build summary based on content type
        name = content.get("name", content.get("title", ""))
        
        summary_parts = []
        
        # Add summary/description
        if "summary" in content:
            summary_parts.append(content["summary"])
        elif "ai_summary" in content:
            summary_parts.append(content["ai_summary"])
        
        # Add key recommendation
        if "final_recommendation" in content:
            summary_parts.append(f"\n\nRecommendation: {content['final_recommendation']}")
        
        # Add dosage if applicable
        if "dosage" in content and query_understanding.intent.value in ["dosage", "informational"]:
            summary_parts.append(f"\n\nDosage: {content['dosage']}")
        
        return " ".join(summary_parts) if summary_parts else f"Information about {name} is available above."
    
    def _collect_references(self, ranked_results: List[RankedResult]) -> List[Dict[str, Any]]:
        """Collect all references from results"""
        references = []
        seen_urls = set()
        
        for result in ranked_results:
            content = result.content
            
            # Add PubMed references
            if content.get("pmid"):
                pmid = content["pmid"]
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                if url not in seen_urls:
                    references.append({
                        "type": "pubmed",
                        "id": pmid,
                        "url": url,
                        "title": content.get("title", ""),
                        "journal": content.get("journal", "")
                    })
                    seen_urls.add(url)
            
            # Add Examine.com references
            if content.get("examine_url") and content["examine_url"] not in seen_urls:
                references.append({
                    "type": "examine",
                    "url": content["examine_url"],
                    "title": "Examine.com"
                })
                seen_urls.add(content["examine_url"])
            
            # Add web sources
            if content.get("url") and content.get("type") == "web_result":
                url = content["url"]
                if url not in seen_urls:
                    references.append({
                        "type": "web",
                        "url": url,
                        "title": content.get("title", "")
                    })
                    seen_urls.add(url)
        
        return references


# Singleton instance
response_generation_agent = ResponseGenerationAgent()


def generate_response(
    query_understanding: QueryUnderstanding,
    ranked_results: List[RankedResult],
    safety_warning: SafetyWarning
) -> Dict[str, Any]:
    """
    Convenience function for generating responses.
    
    Args:
        query_understanding: Parsed query understanding
        ranked_results: Ranked results from Ranking agent
        safety_warning: Safety warning from Safety agent
        
    Returns:
        Structured response dictionary
    """
    return response_generation_agent.process(
        query_understanding,
        ranked_results,
        safety_warning
    )
