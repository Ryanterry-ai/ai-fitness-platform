"""
Query Understanding Agent
"""
import re
from typing import List
from ..models import QueryUnderstanding, IntentType, DomainCategory, RiskLevel

class QueryUnderstandingAgent:
    def __init__(self):
        self.compound_patterns = {
            "RAD-140": r"rad.?140|rad140|testolone",
            "LGD-4033": r"lgd.?4033|lgd4033|ligandrol",
            "Ostarine": r"mk.?2866|ostarine|gtx",
            "MK-677": r"mk.?677|ibutamoren",
            "BPC-157": r"bpc.?157",
            "Testosterone": r"testosterone|test e|test c",
            "Anavar": r"anavar|oxandrolone",
            "Creatine": r"creatine",
            "Whey": r"whey|protein",
            "HGH": r"hgh|growth.?hormone|somatropin",
        }
        
        self.intent_patterns = {
            IntentType.DOSAGE: r"dosage|dose|mg|iu|how much",
            IntentType.CYCLE: r"cycle|weeks|protocol|pct",
            IntentType.SAFETY: r"safe|safety|side effect|risk",
            IntentType.EXERCISE: r"exercise|workout|training|gym",
            IntentType.NUTRITION: r"diet|nutrition|calories|protein",
        }
        
        self.domain_keywords = {
            DomainCategory.SARMS: ["sarm", "rad", "lgd", "ostarine"],
            DomainCategory.STEROIDS: ["steroid", "testosterone", "anavar", "nandrolone"],
            DomainCategory.PEPTIDES: ["peptide", "bpc", "tb500"],
            DomainCategory.HGH: ["hgh", "growth hormone", "igf"],
            DomainCategory.SUPPLEMENTS: ["supplement", "creatine", "whey"],
            DomainCategory.EXERCISE: ["exercise", "workout", "training"],
            DomainCategory.NUTRITION: ["diet", "nutrition", "calories"],
            DomainCategory.FAT_LOSS: ["fat loss", "cutting", "weight loss"],
            DomainCategory.MUSCLE_GAIN: ["muscle", "bulking", "gain"],
        }
        
        self.risk_compounds = {
            "trenbolone": RiskLevel.EXTREME,
            "testosterone": RiskLevel.HIGH,
            "nandrolone": RiskLevel.HIGH,
            "hgh": RiskLevel.HIGH,
            "dianabol": RiskLevel.HIGH,
            "anavar": RiskLevel.MODERATE,
            "rad140": RiskLevel.MODERATE,
            "lgd4033": RiskLevel.MODERATE,
            "mk677": RiskLevel.MODERATE,
            "creatine": RiskLevel.LOW,
            "whey": RiskLevel.LOW,
        }

    def process(self, query: str) -> QueryUnderstanding:
        query_lower = query.lower()
        
        # Detect domain
        domain = self._detect_domain(query_lower)
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Extract compound
        compound = self._extract_compound(query_lower)
        
        # Assess risk
        risk_level = self._assess_risk(compound, domain)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        return QueryUnderstanding(
            original_query=query,
            intent=intent,
            domain=domain,
            compound=compound,
            risk_level=risk_level,
            entities=entities,
            confidence=0.85
        )
    
    def _detect_domain(self, query: str) -> DomainCategory:
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            for kw in keywords:
                if kw in query:
                    scores[domain] = scores.get(domain, 0) + 1
        if scores:
            return max(scores, key=scores.get)
        return DomainCategory.GENERAL
    
    def _detect_intent(self, query: str) -> IntentType:
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return intent
        return IntentType.INFORMATIONAL
    
    def _extract_compound(self, query: str) -> str:
        for compound, pattern in self.compound_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return compound
        return None
    
    def _assess_risk(self, compound: str, domain: DomainCategory) -> RiskLevel:
        if compound:
            for name, risk in self.risk_compounds.items():
                if name in compound.lower():
                    return risk
        if domain in [DomainCategory.STEROIDS, DomainCategory.HGH]:
            return RiskLevel.HIGH
        if domain in [DomainCategory.SARMS, DomainCategory.PEPTIDES]:
            return RiskLevel.MODERATE
        return RiskLevel.LOW
    
    def _extract_entities(self, query: str) -> List[str]:
        entities = []
        for compound in self.compound_patterns:
            if re.search(self.compound_patterns[compound], query, re.IGNORECASE):
                entities.append(compound)
        return entities


agent = QueryUnderstandingAgent()

def understand_query(query: str) -> QueryUnderstanding:
    return agent.process(query)
