"""
Response Generation Agent
"""
from typing import List, Dict, Any
from ..models import RankedResult, QueryUnderstanding, SafetyWarning

class ResponseGenerationAgent:
    def generate(self, query: QueryUnderstanding, results: List[RankedResult], safety: SafetyWarning) -> Dict[str, Any]:
        sections = self._build_sections(results, query)
        
        summary = self._generate_summary(query, results)
        
        references = self._build_references(results)
        
        return {
            "sections": sections,
            "ai_summary": summary,
            "references": references,
            "safety": {
                "status": safety.status.value,
                "level": safety.level.value,
                "warnings": safety.warnings,
                "precautions": safety.precautions,
                "disclaimer": safety.disclaimer
            }
        }

    def _build_sections(self, results: List[RankedResult], query: QueryUnderstanding) -> Dict[str, Any]:
        sections = {}
        
        # Knowledge section
        knowledge_results = [r for r in results if r.result_type == "knowledge"]
        if knowledge_results:
            sections["overview"] = {
                "title": f"About {query.compound or query.domain.value}",
                "content": knowledge_results[0].content.get("description", ""),
                "data": {k: v for k, v in knowledge_results[0].content.items() if k != "description"}
            }
        
        # Web results section
        web_results = [r for r in results if r.result_type == "web"]
        if web_results:
            sections["resources"] = {
                "title": "Web Resources",
                "items": [{"title": r.content.get("title", ""), "url": r.content.get("url", ""), "snippet": r.content.get("snippet", "")} for r in web_results[:5]]
            }
        
        # Research section
        research_results = [r for r in results if r.result_type == "research"]
        if research_results:
            sections["research"] = {
                "title": "Research Papers",
                "items": [{"title": r.content.get("title", ""), "journal": r.content.get("journal", ""), "year": r.content.get("year", ""), "url": r.content.get("url", "")} for r in research_results[:3]]
            }
        
        return sections

    def _generate_summary(self, query: QueryUnderstanding, results: List[RankedResult]) -> str:
        compound = query.compound or query.domain.value
        intent = query.intent.value
        
        summary_parts = [f"Information about {compound}:"]
        
        if query.intent.value == "dosage":
            for r in results:
                if "dosage" in r.content:
                    summary_parts.append(f"- Typical dosage: {r.content['dosage']}")
                    break
        
        if query.intent.value == "safety":
            summary_parts.append("- Safety considerations are important for this compound.")
        
        if results:
            top_result = results[0]
            if top_result.result_type == "knowledge":
                desc = top_result.content.get("description", "")
                if desc:
                    summary_parts.append(f"\n{desc}")
        
        return " ".join(summary_parts)

    def _build_references(self, results: List[RankedResult]) -> List[Dict[str, Any]]:
        refs = []
        for r in results:
            if r.result_type == "web":
                refs.append({"title": r.content.get("title", ""), "url": r.content.get("url", ""), "source": r.source})
            elif r.result_type == "research":
                refs.append({"title": r.content.get("title", ""), "url": r.content.get("url", ""), "source": r.source, "journal": r.content.get("journal", "")})
        return refs[:10]


agent = ResponseGenerationAgent()

def generate_response(query: QueryUnderstanding, results: List[RankedResult], safety: SafetyWarning) -> Dict[str, Any]:
    return agent.generate(query, results, safety)
