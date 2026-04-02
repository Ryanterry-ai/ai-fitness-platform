"""Response Generation Agent"""
from typing import List, Dict, Any
from ..models import RankedResult, QueryUnderstanding, SafetyWarning

class ResponseAgent:
    def generate(self, query: QueryUnderstanding, results: List[RankedResult], safety: SafetyWarning) -> Dict[str, Any]:
        sections = self._build_sections(query, results)
        return {
            "sections": sections,
            "ai_summary": self._summarize(query, results),
            "references": [{"title": r.content.get("title", ""), "url": r.content.get("url", ""), "source": r.source} for r in results if r.result_type in ["web", "research"]],
            "safety": {"status": safety.status.value, "level": safety.level.value, "warnings": safety.warnings, "precautions": safety.precautions, "disclaimer": safety.disclaimer}
        }

    def _build_sections(self, query, results: List[RankedResult]) -> Dict[str, Any]:
        sections = {}
        knowledge = [r for r in results if r.result_type == "knowledge"]
        if knowledge:
            k = knowledge[0].content
            sections["overview"] = {"title": f"About {query.compound or query.domain.value}", "content": k.get("description", k.get("full_description", ""))[:500]}
            if "dosage" in k:
                sections["dosage"] = {"title": "Recommended Dosage", "content": k.get("dosage", {})}
            if "benefits" in k:
                sections["benefits"] = {"title": "Benefits", "items": k.get("benefits", [])}
            if "side_effects" in k:
                sections["side_effects"] = {"title": "Side Effects", "items": k.get("side_effects", [])}
            if "timing" in k:
                sections["timing"] = {"title": "Timing", "content": k.get("timing", "")}
            if "cycle" in k:
                sections["cycle"] = {"title": "Cycle Protocol", "content": k.get("cycle", {})}
            if "stacks" in k:
                sections["stacks"] = {"title": "Popular Stacks", "items": k.get("stacks", [])}
        web = [r for r in results if r.result_type == "web"]
        if web:
            sections["resources"] = {"title": "Web Resources", "items": [{"title": r.content.get("title", ""), "url": r.content.get("url", ""), "snippet": r.content.get("snippet", "")[:200]} for r in web[:5]]}
        return sections

    def _summarize(self, query, results: List[RankedResult]) -> str:
        compound = query.compound or query.domain.value
        intent = query.intent.value.replace("_", " ")
        parts = [f"Information about {compound} ({intent}):"]
        for r in results:
            if r.result_type == "knowledge" and "description" in r.content:
                parts.append(r.content["description"][:300])
                break
        return " ".join(parts)

agent = ResponseAgent()

def generate_response(query, results, safety) -> Dict[str, Any]:
    return agent.generate(query, results, safety)
