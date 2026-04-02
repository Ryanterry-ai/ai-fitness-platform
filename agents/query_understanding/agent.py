"""
Query Understanding Agent
=========================
Analyzes user queries to understand intent, domain, entities, and risk level.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from models import QueryUnderstanding, IntentType, DomainCategory, RiskLevel
from config import settings


class QueryUnderstandingAgent:
    """
    Agent responsible for understanding and parsing user search queries.
    
    Responsibilities:
    - Intent detection
    - Domain/category classification
    - Entity extraction (compounds, exercises, etc.)
    - Goal identification
    - Risk level assessment
    - Experience level detection
    """
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.domain_patterns = self._build_domain_patterns()
        self.goal_patterns = self._build_goal_patterns()
        self.risk_compounds = self._build_risk_compounds()
        self.entity_aliases = self._build_entity_aliases()
    
    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Build regex patterns for intent detection"""
        return {
            IntentType.DOSAGE: [
                r"(?:dosage|dose|how much|how many|mg|mcg|iu|ml|cc)",
                r"(?:serving|portion|amount)",
                r"(?:per day|per week|daily|weekly)",
            ],
            IntentType.CYCLE: [
                r"(?:cycle|protocol|weeks?|pct|post.?cycle|on.?cycle)",
                r"(?:stack|stacking|combination)",
                r"(?:blast|cruise|blast.?and.?cruise)",
            ],
            IntentType.PRODUCT: [
                r"(?:best|top|buy|price|brand|recommend|which)",
                r"(?:product|supplement|stack)",
                r"(?:india|inr|cheap|affordable|value)",
            ],
            IntentType.COMPARE: [
                r"(?:vs|versus|compare|comparison|better|which one|difference)",
            ],
            IntentType.SAFETY: [
                r"(?:safe|safety|side effect|risk|danger|harm|toxic|warning)",
                r"(?:dangerous|adverse|effect|health)",
            ],
            IntentType.EXERCISE: [
                r"(?:exercise|workout|training|gym|routine|sets?|reps?|lift)",
                r"(?:program|plan|split|ppl|push.?pull)",
            ],
            IntentType.NUTRITION: [
                r"(?:diet|nutrition|meal|food|calories|macros?|protein|carb)",
                r"(?:eating|what to eat|dietary|nutrient)",
            ],
            IntentType.RECOMMEND: [
                r"(?:should i|advice|suggest|help|guide)",
                r"(?:beginner|start|first time)",
            ],
        }
    
    def _build_domain_patterns(self) -> Dict[DomainCategory, List[str]]:
        """Build regex patterns for domain classification"""
        return {
            DomainCategory.SARMS: [
                r"ostarine|mk.?2866|lgd.?4033|rad.?140|andarine|s4",
                r"mk.?677|ibutamoren|cardarine|gw.?501516|sarm",
            ],
            DomainCategory.STEROIDS: [
                r"testosterone|anavar|oxandrolone|nandrolone|deca|dianabol",
                r"trenbolone|winstrol|primobolan| Equipoise",
                r"steroid|anabolic|tren|var|dbol",
            ],
            DomainCategory.PEPTIDES: [
                r"bpc.?157|tb.?500|ipamorelin|cjc.?1295",
                r"semorelin|ghrp|hexarelin|mod.?grf|peptide",
            ],
            DomainCategory.HGH: [
                r"hgh|growth.?hormone|somatropin|igf|igf.?1",
                r"human.?growth|syntropin|norditropin",
            ],
            DomainCategory.SUPPLEMENTS: [
                r"creatine|whey|protein|caffeine|beta.?alanine",
                r"citrulline|pre.?workout|bcaa|omega.?3|vitamin",
                r"supplement|zma|fish.?oil|vitamin.?d|zinc|magnesium",
            ],
            DomainCategory.EXERCISE: [
                r"exercise|workout|training|gym|lifting|squat|deadlift",
                r"bench|press|row|curl|extension",
            ],
            DomainCategory.NUTRITION: [
                r"diet|nutrition|meal|macros?|calories|protein",
                r"carb|fat|cutting|bulking|cardio",
            ],
            DomainCategory.FAT_LOSS: [
                r"fat.?loss|weight.?loss|cutting|burn.?fat|shred",
                r"lean.?down|body.?fat|deflcit",
            ],
            DomainCategory.MUSCLE_GAIN: [
                r"muscle.?gain|bulking|hypertrophy|build.?muscle",
                r"mass.?gain|lean.?mass|anabolic",
            ],
            DomainCategory.BODYBUILDING: [
                r"bodybuilding|physique|contest|prep|competition",
                r"competition.?prep|stage.?ready",
            ],
            DomainCategory.SPORTS_PERFORMANCE: [
                r"athletic|performance|sport|strength|speed|power",
                r"endurance|agility|vertical.?jump",
            ],
            DomainCategory.RECOVERY: [
                r"recovery|healing|injury|tendon|ligament",
                r"rehab|sleep|rest|repair|recovery.?time",
            ],
        }
    
    def _build_goal_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for goal identification"""
        return {
            "muscle_gain": [
                r"muscle.?gain|bulking|hypertrophy|build.?muscle",
                r"mass|gain.?weight|lean.?mass",
            ],
            "fat_loss": [
                r"fat.?loss|weight.?loss|cutting|burn.?fat|shred",
                r"lean|deflcit|lose.?weight",
            ],
            "strength": [
                r"strength|power|strong|max.?1rm|1rm|powerlifting",
            ],
            "endurance": [
                r"endurance|stamina|cardio|aerobic|marathon",
            ],
            "recovery": [
                r"recovery|healing|rehab|injury|sleep|rest",
            ],
            "recomposition": [
                r"recomp|body.?recomposition|lean.?out",
            ],
        }
    
    def _build_risk_compounds(self) -> Dict[str, RiskLevel]:
        """Define risk levels for known compounds"""
        return {
            "testosterone": RiskLevel.HIGH,
            "trenbolone": RiskLevel.EXTREME,
            "nandrolone": RiskLevel.HIGH,
            "anavar": RiskLevel.MODERATE,
            "dianabol": RiskLevel.HIGH,
            "hgh": RiskLevel.HIGH,
            "rad140": RiskLevel.MODERATE,
            "lgd4033": RiskLevel.MODERATE,
            "mk677": RiskLevel.MODERATE,
            "bpc157": RiskLevel.LOW,
            "creatine": RiskLevel.LOW,
            "whey": RiskLevel.LOW,
            "caffeine": RiskLevel.LOW,
        }
    
    def _build_entity_aliases(self) -> Dict[str, str]:
        """Map compound aliases to canonical names"""
        return {
            "rad140": "RAD-140",
            "rad-140": "RAD-140",
            "testolone": "RAD-140",
            "lgd4033": "LGD-4033",
            "lgd-4033": "LGD-4033",
            "ligandrol": "LGD-4033",
            "mk2866": "Ostarine",
            "mk-2866": "Ostarine",
            "ostarine": "Ostarine",
            "mk677": "MK-677",
            "mk-677": "MK-677",
            "ibutamoren": "MK-677",
            "bpc157": "BPC-157",
            "bpc-157": "BPC-157",
            "tb500": "TB-500",
            "tb-500": "TB-500",
            "test e": "Testosterone Enanthate",
            "testosterone e": "Testosterone Enanthate",
            "deca": "Nandrolone Decanoate",
            "nandrolone": "Nandrolone",
            "anavar": "Oxandrolone",
            "dbol": "Methandrostenolone",
            "tren": "Trenbolone",
        }
    
    def process(self, query: str) -> QueryUnderstanding:
        """
        Process a user query and return structured understanding.
        
        Args:
            query: Raw user query string
            
        Returns:
            QueryUnderstanding object with parsed query information
        """
        query_lower = query.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Detect domain
        domain = self._detect_domain(query_lower)
        
        # Extract entities (compounds, etc.)
        entities = self._extract_entities(query_lower)
        
        # Find primary compound
        compound = self._find_primary_compound(entities, query_lower)
        
        # Detect goal
        goal = self._detect_goal(query_lower)
        
        # Detect experience level
        experience_level = self._detect_experience_level(query_lower)
        
        # Assess risk
        risk_level = self._assess_risk(compound, domain, entities)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(query_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, domain, entities)
        
        return QueryUnderstanding(
            original_query=query,
            intent=intent,
            domain=domain,
            compound=compound,
            goal=goal,
            experience_level=experience_level,
            risk_level=risk_level,
            entities=entities,
            modifiers=modifiers,
            language="en",  # Could extend to detect other languages
            confidence=confidence
        )
    
    def _detect_intent(self, query: str) -> IntentType:
        """Detect the primary intent of the query"""
        scores: Dict[IntentType, float] = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return IntentType.INFORMATIONAL
        
        # Return intent with highest score, defaulting to research
        return max(scores.items(), key=lambda x: x[1])[0] if scores else IntentType.RESEARCH
    
    def _detect_domain(self, query: str) -> DomainCategory:
        """Detect the primary domain category"""
        scores: Dict[DomainCategory, float] = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return DomainCategory.GENERAL
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract all known entities from query"""
        entities = []
        
        # Check for known compound names
        for alias, canonical in self.entity_aliases.items():
            if alias.lower() in query:
                if canonical not in entities:
                    entities.append(canonical)
        
        # Also check for direct matches in alias keys
        for alias in self.entity_aliases.keys():
            if alias.lower() in query:
                canonical = self.entity_aliases[alias]
                if canonical not in entities:
                    entities.append(canonical)
        
        # Add generic entity detection
        exercise_patterns = [
            r"(?:squat|deadlift|bench|press|row|curl|extension)",
            r"(?:push.?up|pull.?up|chin.?up|dip|lunge)",
        ]
        
        for pattern in exercise_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if match.title() not in entities:
                    entities.append(match.title())
        
        return entities
    
    def _find_primary_compound(self, entities: List[str], query: str) -> Optional[str]:
        """Find the primary compound being queried"""
        if not entities:
            return None
        
        # If there's a known compound, return the first one
        known_compounds = [
            "RAD-140", "LGD-4033", "Ostarine", "MK-677",
            "Testosterone", "Nandrolone", "Anavar", "BPC-157",
            "TB-500", "HGH", "Creatine", "Whey", "Caffeine"
        ]
        
        for entity in entities:
            if entity in known_compounds:
                return entity
        
        return entities[0] if entities else None
    
    def _detect_goal(self, query: str) -> Optional[str]:
        """Detect the user's goal from the query"""
        for goal, patterns in self.goal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return goal
        return None
    
    def _detect_experience_level(self, query: str) -> Optional[str]:
        """Detect user's experience level"""
        if any(x in query for x in ["beginner", "new", "first time", "starter", "novice"]):
            return "beginner"
        if any(x in query for x in ["intermediate", "experienced", "advanced", "expert"]):
            return "advanced"
        return None
    
    def _assess_risk(self, compound: Optional[str], domain: DomainCategory, 
                     entities: List[str]) -> RiskLevel:
        """Assess the risk level of the query"""
        # Check if compound has known risk level
        if compound:
            compound_lower = compound.lower().replace("-", "").replace(" ", "")
            for known, risk in self.risk_compounds.items():
                if known in compound_lower or compound_lower in known:
                    return risk
        
        # Assess by domain
        high_risk_domains = [DomainCategory.STEROIDS, DomainCategory.HGH]
        moderate_risk_domains = [DomainCategory.SARMS, DomainCategory.PEPTIDES]
        
        if domain in high_risk_domains:
            return RiskLevel.HIGH
        if domain in moderate_risk_domains:
            return RiskLevel.MODERATE
        
        return RiskLevel.LOW
    
    def _extract_modifiers(self, query: str) -> List[str]:
        """Extract query modifiers like 'best', 'safe', 'natural', etc."""
        modifiers = []
        
        modifier_patterns = {
            "best": r"\bbest\b",
            "safe": r"\bsafe\b",
            "natural": r"\bnatural\b",
            "beginner": r"\bbeginner\b",
            "advanced": r"\badvanced\b",
            "female": r"\b(female|women|woman)\b",
            "fasted": r"\bfasted\b",
            "before_bed": r"\b(before bed|nighttime)\b",
            "post_workout": r"\b(post.?workout|after training)\b",
            "pre_workout": r"\b(pre.?workout|before training)\b",
            "oral": r"\b(oral|pill|capsule)\b",
            "injection": r"\b(inject|subq|im)\b",
        }
        
        for modifier, pattern in modifier_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                modifiers.append(modifier)
        
        return modifiers
    
    def _calculate_confidence(self, intent: IntentType, domain: DomainCategory, 
                             entities: List[str]) -> float:
        """Calculate confidence score for the understanding"""
        base_confidence = 0.5
        
        # Higher confidence if entity detected
        if entities:
            base_confidence += 0.15
        
        # Higher confidence if clear domain match
        if domain != DomainCategory.GENERAL:
            base_confidence += 0.15
        
        # Higher confidence if clear intent
        if intent != IntentType.INFORMATIONAL:
            base_confidence += 0.1
        
        # Cap at 0.95
        return min(base_confidence, 0.95)


# Singleton instance
query_understanding_agent = QueryUnderstandingAgent()


def understand_query(query: str) -> QueryUnderstanding:
    """
    Convenience function to process a query.
    
    Args:
        query: Raw user query string
        
    Returns:
        QueryUnderstanding object
    """
    return query_understanding_agent.process(query)
