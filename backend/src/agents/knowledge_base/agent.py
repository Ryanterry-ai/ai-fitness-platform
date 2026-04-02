"""
Knowledge Base Agent
"""
import re
from typing import List
from ..models import KnowledgeResult, DomainCategory, QueryUnderstanding

class KnowledgeBaseAgent:
    def __init__(self):
        self.knowledge_base = {
            "RAD-140": {
                "name": "RAD-140 (Testolone)",
                "category": DomainCategory.SARMS,
                "description": "Highly anabolic SARM for muscle growth and bone health.",
                "dosage": "10-20mg/day",
                "cycle": "8-12 weeks",
                "half_life": "16-20 hours",
                "benefits": ["Increased muscle mass", "Enhanced strength", "Bone health", "Fat loss"],
                "side_effects": ["Testosterone suppression", "Potential liver toxicity"],
                "evidence_tier": "high",
                "safety_level": "moderate",
                "tags": ["sarms", "muscle gain", "strength"]
            },
            "LGD-4033": {
                "name": "LGD-4033 (Ligandrol)",
                "category": DomainCategory.SARMS,
                "description": "Potent muscle builder with high selectivity.",
                "dosage": "5-10mg/day",
                "cycle": "8 weeks",
                "half_life": "30-36 hours",
                "benefits": ["Muscle growth", "Strength gains", "Improved recovery"],
                "side_effects": ["HPTA suppression", "Headaches"],
                "evidence_tier": "high",
                "safety_level": "moderate",
                "tags": ["sarms", "muscle gain"]
            },
            "Ostarine": {
                "name": "Ostarine (MK-2866)",
                "category": DomainCategory.SARMS,
                "description": "Mild SARM for lean muscle preservation.",
                "dosage": "15-25mg/day",
                "cycle": "8-12 weeks",
                "half_life": "24 hours",
                "benefits": ["Muscle preservation", "Joint health", "Fat loss", "Mild anabolic effects"],
                "side_effects": ["Minimal suppression at low doses"],
                "evidence_tier": "high",
                "safety_level": "low",
                "tags": ["sarms", "beginner", "cutting"]
            },
            "MK-677": {
                "name": "MK-677 (Ibutamoren)",
                "category": DomainCategory.SARMS,
                "description": "Growth hormone secretagogue for muscle growth and recovery.",
                "dosage": "12.5-25mg/day",
                "cycle": "16-24 weeks",
                "half_life": "4-6 hours",
                "benefits": ["Increased GH", "Improved sleep", "Muscle growth", "Recovery"],
                "side_effects": ["Increased appetite", "Water retention", "Lethargy"],
                "evidence_tier": "high",
                "safety_level": "moderate",
                "tags": ["growth hormone", "sleep", "recovery"]
            },
            "BPC-157": {
                "name": "BPC-157",
                "category": DomainCategory.PEPTIDES,
                "description": "Healing peptide for tissue repair and gut health.",
                "dosage": "250-500mcg 2-3x/day",
                "cycle": "4-8 weeks",
                "half_life": "4 hours",
                "benefits": ["Wound healing", "Tendon repair", "Gut health", "Anti-inflammatory"],
                "side_effects": ["Minimal reported"],
                "evidence_tier": "moderate",
                "safety_level": "low",
                "tags": ["peptide", "healing", "gut"]
            },
            "Testosterone": {
                "name": "Testosterone",
                "category": DomainCategory.STEROIDS,
                "description": "Primary male sex hormone and anabolic steroid.",
                "dosage": "100-200mg/week (TRT) to 500mg/week (enhanced)",
                "cycle": "12-16 weeks",
                "half_life": "4-7 days (enanthate)",
                "benefits": ["Massive muscle growth", "Strength increase", "Improved mood", "Libido"],
                "side_effects": ["Estrogen conversion", "DHT conversion", "HPTA suppression", "Cardiovascular strain"],
                "evidence_tier": "very_high",
                "safety_level": "high",
                "tags": ["steroid", "muscle gain", "hormone"]
            },
            "Anavar": {
                "name": "Anavar (Oxandrolone)",
                "category": DomainCategory.STEROIDS,
                "description": "Mild oral steroid for cutting and lean muscle.",
                "dosage": "20-50mg/day",
                "cycle": "6-8 weeks",
                "half_life": "9 hours",
                "benefits": ["Lean muscle", "Fat loss", "Strength", "Low androgenic effects"],
                "side_effects": ["Liver toxicity", "Lipid changes", "HPTA suppression"],
                "evidence_tier": "high",
                "safety_level": "moderate",
                "tags": ["steroid", "cutting", "oral"]
            },
            "Creatine": {
                "name": "Creatine Monohydrate",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Most researched supplement for strength and power.",
                "dosage": "3-5g/day maintenance",
                "cycle": "Continuous use",
                "half_life": "3-4 hours",
                "benefits": ["Increased strength", "Power output", "Muscle volume", "Brain function"],
                "side_effects": ["Water retention", "Digestive issues (rare)"],
                "evidence_tier": "very_high",
                "safety_level": "very_safe",
                "tags": ["supplement", "strength", "beginner"]
            },
            "Whey Protein": {
                "name": "Whey Protein",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Fast-absorbing protein for muscle protein synthesis.",
                "dosage": "20-40g post-workout",
                "cycle": "Continuous use",
                "half_life": "20-30 minutes",
                "benefits": ["Muscle building", "Recovery", "Convenient protein source"],
                "side_effects": ["Lactose intolerance issues"],
                "evidence_tier": "very_high",
                "safety_level": "very_safe",
                "tags": ["supplement", "protein", "nutrition"]
            },
            "HGH": {
                "name": "Human Growth Hormone (HGH)",
                "category": DomainCategory.HGH,
                "description": "Pituitary hormone for growth, repair, and anti-aging.",
                "dosage": "2-4 IU/day (anti-aging) to 8-12 IU/day (enhanced)",
                "cycle": "6-12 months",
                "half_life": "3-4 hours",
                "benefits": ["Muscle growth", "Fat loss", "Improved skin", "Recovery", "Sleep"],
                "side_effects": ["Water retention", "Carpal tunnel", "Insulin resistance", "Organ growth"],
                "evidence_tier": "high",
                "safety_level": "high",
                "tags": ["hormone", "anti-aging", "recovery"]
            },
            "Caffeine": {
                "name": "Caffeine",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Stimulant for energy, focus, and fat burning.",
                "dosage": "100-200mg pre-workout",
                "cycle": "As needed",
                "half_life": "5-6 hours",
                "benefits": ["Energy", "Focus", "Fat oxidation", "Performance"],
                "side_effects": ["Anxiety", "Insomnia", "Heart palpitations", "Tolerance"],
                "evidence_tier": "very_high",
                "safety_level": "low",
                "tags": ["stimulant", "pre-workout", "energy"]
            },
            "Citrulline": {
                "name": "Citrulline",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Amino acid for pumps and endurance.",
                "dosage": "6-8g L-citrulline pre-workout",
                "cycle": "Continuous use",
                "half_life": "1-2 hours",
                "benefits": ["Blood flow", "Pumps", "Endurance", "Recovery"],
                "side_effects": ["Mild digestive issues"],
                "evidence_tier": "high",
                "safety_level": "very_safe",
                "tags": ["amino acid", "pump", "pre-workout"]
            },
            "Beta-Alanine": {
                "name": "Beta-Alanine",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Amino acid for endurance and power output.",
                "dosage": "3-6g/day (split doses)",
                "cycle": "Continuous use",
                "half_life": "25 minutes",
                "benefits": ["Carnosine boost", "Buffering capacity", "Endurance"],
                "side_effects": ["Tingling (paresthesia)"],
                "evidence_tier": "high",
                "safety_level": "very_safe",
                "tags": ["amino acid", "endurance", "pre-workout"]
            },
            "Vitamin D": {
                "name": "Vitamin D3",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Essential vitamin for bone, immune, and hormone health.",
                "dosage": "2000-5000 IU/day",
                "cycle": "Continuous use",
                "half_life": "2 weeks",
                "benefits": ["Bone health", "Immune function", "Testosterone support", "Mood"],
                "side_effects": ["Toxicity at very high doses"],
                "evidence_tier": "high",
                "safety_level": "safe",
                "tags": ["vitamin", "health", "hormone"]
            },
            "Omega-3": {
                "name": "Omega-3 Fish Oil",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Essential fatty acids for heart, brain, and joint health.",
                "dosage": "2-4g EPA+DHA combined",
                "cycle": "Continuous use",
                "half_life": "2 days",
                "benefits": ["Heart health", "Joint health", "Brain function", "Inflammation"],
                "side_effects": ["Fishy burps", "Blood thinning"],
                "evidence_tier": "very_high",
                "safety_level": "very_safe",
                "tags": ["fatty acid", "heart", "health"]
            }
        }

    def process(self, query_understanding: QueryUnderstanding) -> List[KnowledgeResult]:
        query = query_understanding.original_query.lower()
        compound = query_understanding.compound
        domain = query_understanding.domain
        
        results = []
        
        # Search by compound name
        if compound and compound in self.knowledge_base:
            data = self.knowledge_base[compound]
            results.append(KnowledgeResult(
                id=compound,
                name=data["name"],
                category=data["category"],
                content=data,
                relevance_score=0.95
            ))
        
        # Search by domain
        for name, data in self.knowledge_base.items():
            if data["category"] == domain and name != compound:
                if any(kw in query for kw in data.get("tags", [])):
                    results.append(KnowledgeResult(
                        id=name,
                        name=data["name"],
                        category=data["category"],
                        content=data,
                        relevance_score=0.8
                    ))
        
        # Keyword search
        for name, data in self.knowledge_base.items():
            if name not in [r.name for r in results]:
                for tag in data.get("tags", []):
                    if tag in query:
                        results.append(KnowledgeResult(
                            id=name,
                            name=data["name"],
                            category=data["category"],
                            content=data,
                            relevance_score=0.7
                        ))
                        break
        
        return results


agent = KnowledgeBaseAgent()

def search_knowledge_base(query_understanding: QueryUnderstanding) -> List[KnowledgeResult]:
    return agent.process(query_understanding)
