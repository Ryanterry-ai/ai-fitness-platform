"""
Query Understanding Agent
Master SEO Query Universe understanding with pattern matching
"""
import re
from typing import List, Dict, Optional, Tuple
from ..models import (
    QueryUnderstanding, IntentType, DomainCategory, 
    RiskLevel, SEOQueryPattern
)

class QueryUnderstandingAgent:
    """
    Master SEO Query Understanding Agent
    Handles all query types from the SEO Query Universe
    """
    
    def __init__(self):
        self._build_intent_patterns()
        self._build_domain_patterns()
        self._build_compound_patterns()
        self._build_goal_patterns()
        self._build_modifier_patterns()
        self._build_risk_mapping()
    
    def _build_intent_patterns(self):
        """Build regex patterns for all SEO intent types"""
        self.intent_patterns: Dict[IntentType, List[str]] = {
            IntentType.INFORMATIONAL: [
                r"^what is", r"^what are", r"^explain", r"^tell me about",
                r"^what does", r"^define", r"^overview"
            ],
            IntentType.HOW_IT_WORKS: [
                r"^how (does|do|can|to)", r"^how (it|they|this) works?",
                r"^mechanism", r"^原理", r"^working"
            ],
            IntentType.BENEFITS: [
                r"^benefits?", r"^advantages?", r"^good for",
                r"^why (take|use)", r"^what are the benefits"
            ],
            IntentType.SIDE_EFFECTS: [
                r"^side effects?", r"^negative", r"^risks?",
                r"^harmful", r"^danger", r"^bad for", r"^adverse"
            ],
            IntentType.DOSAGE: [
                r"^dosage", r"^dose", r"^how much", r"^mg",
                r"^amount", r"^serving", r"^quantity"
            ],
            IntentType.TIMING: [
                r"^when (to|should)", r"^best time", r"^timing",
                r"^schedule", r"^before|after", r"^morning|night"
            ],
            IntentType.COMPARISON: [
                r"^vs\.?", r"^versus", r"^compare", r"^difference",
                r"^better than", r"^or", r"^which (is|one)"
            ],
            IntentType.BEGINNER: [
                r"^beginner", r"^starter", r"^first time",
                r"^new to", r"^how to start", r"^introduction"
            ],
            IntentType.ADVANCED: [
                r"^advanced", r"^experienced", r"^pro",
                r"^elite", r"^expert", r"^intermediate"
            ],
            IntentType.GOAL_BASED: [
                r"for (muscle|gain|strength|fat loss|endurance|performance)",
                r"to (build|get|gain|lose|increase|improve)"
            ],
            IntentType.CYCLE: [
                r"^cycle", r"^cycles", r"^protocol",
                r"^weeks?", r"^duration", r"^length"
            ],
            IntentType.STACK: [
                r"^stack", r"^stacking", r"^combination",
                r"^with", r"^together", r"^combine"
            ],
            IntentType.PCT: [
                r"^pct", r"^post.?cycle", r"^recovery",
                r"^testosterone recovery", r"^nolvadex", r"^clomid"
            ],
            IntentType.DIET: [
                r"^diet", r"^nutrition", r"^meal", r"^eating",
                r"^macros?", r"^calories", r"^keto", r"^cutting", r"^bulking"
            ],
            IntentType.WORKOUT: [
                r"^workout", r"^routine", r"^program",
                r"^training", r"^split", r"^schedule"
            ],
            IntentType.EXERCISE: [
                r"^exercise", r"^exercises", r"^how to (do|perform)",
                r"^form", r"^technique", r"^chest|back|legs|arms|shoulders"
            ],
            IntentType.SPORTS_PERFORMANCE: [
                r"^athlete", r"^sports?", r"^performance",
                r"^endurance", r"^power", r"^speed", r"^agility"
            ],
            IntentType.HORMONE: [
                r"^testosterone", r"^hormone", r"^booster",
                r"^levels?", r"^t booster"
            ],
            IntentType.SAFETY: [
                r"^is it safe", r"^are (they|it) safe", r"^safe\?",
                r"^dangerous", r"^harmful", r"^risk"
            ],
            IntentType.NATURAL_ALTERNATIVES: [
                r"^natural", r"^alternative", r"^without steroids",
                r"^legal", r"^over the counter"
            ],
            IntentType.BRAND: [
                r"^best brand", r"^which brand", r"^brand",
                r"^recommended", r"^top"
            ],
            IntentType.RESEARCH: [
                r"^studies?", r"^research", r"^scientific",
                r"^evidence", r"^studies on", r"^pubmed"
            ],
            IntentType.RESULTS: [
                r"^results?", r"^expect", r"^gains?",
                r"^progress", r"^transform", r"^outcomes?"
            ],
            IntentType.TIMELINE: [
                r"^how long", r"^timeframe", r"^weeks?",
                r"^days?", r"^months?", r"^when (will|do)"
            ],
            IntentType.GENDER: [
                r"for (men|women|female|male)",
                r"gender", r"man|woman"
            ],
            IntentType.AGE: [
                r"for (\d+)", r"year.?olds?", r"teenager",
                r"^age", r"over \d+", r"under \d+"
            ],
            IntentType.HEALTH_CONDITION: [
                r"^diabetes", r"^thyroid", r"^health condition",
                r"^medical", r"^condition", r"^disease"
            ],
            IntentType.SUBSTANCE_SPECIFIC: [],
            IntentType.GOAL_BASED: [
                r"muscle gain", r"fat loss", r"strength", r"endurance",
                r"weight loss", r"bulking", r"cutting", r"recomposition"
            ]
        }
    
    def _build_domain_patterns(self):
        """Build regex patterns for domain classification"""
        self.domain_patterns: Dict[DomainCategory, List[str]] = {
            DomainCategory.STEROIDS: [
                r"testosterone", r"steroid", r"anavar", r"dianabol",
                r"nandrolone", r"trenbolone", r"deca", r"winstrol",
                r"primobolan", r" equipoise", r" sustanon", r"enanthate",
                r"cypionate", r"propionate", r"anabolic"
            ],
            DomainCategory.SARMS: [
                r"sarm", r"ostarine", r"lgd", r"rad.?140",
                r"mk.?2866", r"mk.?677", r"andarine", r"cardarine",
                r"yk.?11", r"s4", r"testolone", r"ligandrol"
            ],
            DomainCategory.PEPTIDES: [
                r"peptide", r"bpc.?157", r"tb.?500", r"ipamorelin",
                r"cjc.?1295", r"mod.?grf", r"ghrp", r"hexarelin",
                r"semorelin", r"tesamorelin"
            ],
            DomainCategory.HGH: [
                r"hgh", r"growth.?hormone", r"somatropin",
                r"igf", r"igf.?1", r"norditropin", r"genotropin"
            ],
            DomainCategory.SUPPLEMENTS: [
                r"supplement", r"creatine", r"whey", r"protein",
                r"bcaa", r"pre.?workout", r"caffeine", r"beta.?alanine",
                r"citrulline", r"carnitine", r"zma", r"fish.?oil",
                r"omega.?3", r"vitamin", r"mineral"
            ],
            DomainCategory.NUTRITION: [
                r"nutrition", r"diet", r"calories", r"macros?",
                r"protein", r"carbs?", r"fat", r"meal.?prep",
                r"food", r"eating", r"bulking", r"cutting"
            ],
            DomainCategory.EXERCISES: [
                r"exercise", r"squat", r"deadlift", r"bench",
                r"press", r"row", r"curl", r"extension",
                r"pull.?up", r"push.?up", r"lunge"
            ],
            DomainCategory.WORKOUTS: [
                r"workout", r"routine", r"program", r"training",
                r"split", r"ppl", r"push.?pull", r"bro.?split",
                r"full.?body", r"5x5", r"ics"
            ],
            DomainCategory.FITNESS: [
                r"fitness", r"gym", r"training", r"exercise",
                r"muscle", r"body", r"physique"
            ],
            DomainCategory.BODYBUILDING: [
                r"bodybuilding", r"physique", r"contest",
                r"prep", r"competition", r"stage"
            ],
            DomainCategory.HEALTH: [
                r"health", r"wellness", r"medical", r"doctor",
                r"blood", r"cholesterol", r"blood.?pressure"
            ],
            DomainCategory.SPORTS_PERFORMANCE: [
                r"sport", r"athlete", r"performance", r"power",
                r"speed", r"endurance", r"agility", r"vertical"
            ],
            DomainCategory.DIET: [
                r"diet", r"nutrition", r"eating", r"meal",
                r"keto", r"paleo", r"if", r"intermittent"
            ],
            DomainCategory.PERFORMANCE_COMPOUNDS: [
                r"compound", r"enhance", r"performance",
                r"booster", r"stimulant"
            ],
            DomainCategory.GENERAL: []
        }
    
    def _build_compound_patterns(self):
        """Build patterns for compound detection"""
        self.compound_patterns: Dict[str, str] = {
            # Steroids
            "Testosterone": r"testosterone|test e|test c|test prop|test enanthate|test cypionate",
            "Anavar": r"anavar|oxandrolone",
            "Dianabol": r"dianabol|metandienone|dbol|methandrostenolone",
            "Nandrolone": r"nandrolone|deca|deca.?durabolin",
            "Trenbolone": r"trenbolone|tren",
            "Winstrol": r"winstrol|stanazolol",
            "Primobolan": r"primobolan|masteron",
            
            # SARMs
            "RAD-140": r"rad.?140|rad140|testolone",
            "LGD-4033": r"lgd.?4033|lgd4033|ligandrol",
            "Ostarine": r"ostarine|mk.?2866|mk2866|gtx",
            "MK-677": r"mk.?677|mk677|ibutamoren",
            "YK-11": r"yk.?11|yk11",
            "S4": r"andarine|s4",
            "GW-501516": r"cardarine|gw.?501516|gw501516",
            
            # Peptides
            "BPC-157": r"bpc.?157|bpc157",
            "TB-500": r"tb.?500|tb500|thymosin.?beta.?4",
            "CJC-1295": r"cjc.?1295|cjc1295",
            "Ipamorelin": r"ipamorelin",
            "Mod-GRF": r"mod.?grf|ghrp.?2",
            
            # HGH
            "HGH": r"hgh|human.?growth.?hormone|somatropin|genotropin",
            "IGF-1": r"igf|igf.?1",
            
            # Supplements
            "Creatine": r"creatine|creatine.?monohydrate",
            "Whey Protein": r"whey|protein.?powder",
            "Caffeine": r"caffeine|coffee",
            "Beta-Alanine": r"beta.?alanine",
            "Citrulline": r"citrulline",
            "BCAA": r"bcaa|branched.?chain",
            "Omega-3": r"omega.?3|fish.?oil|epa|dha",
            "Vitamin D": r"vitamin.?d|vit.?d|d3",
            "ZMA": r"zma|zinc|magnesium",
            "Pre-Workout": r"pre.?workout|preworkout",
        }
    
    def _build_goal_patterns(self):
        """Build patterns for goal detection"""
        self.goal_patterns: Dict[str, List[str]] = {
            "muscle_gain": [
                r"muscle.?gain", r"build.?muscle", r"hypertrophy",
                r"mass", r"bulking", r"lean.?mass", r"size"
            ],
            "fat_loss": [
                r"fat.?loss", r"weight.?loss", r"cutting",
                r"lean.?out", r"shred", r"burn.?fat"
            ],
            "strength": [
                r"strength", r"power", r"strong", r"1rm",
                r"max", r"powerlifting"
            ],
            "endurance": [
                r"endurance", r"stamina", r"cardio",
                r"aerobic", r"running", r"cycling"
            ],
            "performance": [
                r"performance", r"athletic", r"sports?",
                r"speed", r"agility", r"explosive"
            ],
            "recomposition": [
                r"recomp", r"body.?recomposition",
                r"lose.?fat.?gain.?muscle"
            ],
            "recovery": [
                r"recovery", r"healing", r"repair",
                r"sleep", r"rest", r"injury"
            ],
            "health": [
                r"health", r"wellness", r"general",
                r"longevity", r"anti.?aging"
            ]
        }
    
    def _build_modifier_patterns(self):
        """Build patterns for query modifiers"""
        self.modifier_patterns: Dict[str, str] = {
            "beginner": r"\b(beginner|starter|new|first.?time|novice)\b",
            "advanced": r"\b(advanced|experienced|pro|expert)\b",
            "natural": r"\b(natural|organic|plant.?based|whole.?food)\b",
            "legal": r"\b(legal|over.?the.?counter|otc)\b",
            "female": r"\b(female|women|woman|lady)\b",
            "male": r"\b(male|men|man|gentleman)\b",
            "fasted": r"\b(fasted|fasting)\b",
            "post_workout": r"\b(post.?workout|after.?training)\b",
            "pre_workout": r"\b(pre.?workout|before.?training)\b",
            "oral": r"\b(oral|pill|capsule|tablet)\b",
            "injection": r"\b(inject|subcutaneous|im|intramuscular)\b",
            "safe": r"\b(safe|safer|safety)\b",
            "cheap": r"\b(cheap|affordable|budget|inexpensive)\b",
            "best": r"\b(best|top|optimal|ideal)\b",
            "quick": r"\b(quick|fast|rapid|immediate)\b",
            "long_term": r"\b(long.?term|sustainable|permanent)\b"
        }
    
    def _build_risk_mapping(self):
        """Map compounds to risk levels"""
        self.risk_mapping: Dict[str, RiskLevel] = {
            "trenbolone": RiskLevel.EXTREME,
            "superdrol": RiskLevel.EXTREME,
            "halotestin": RiskLevel.EXTREME,
            "anadrol": RiskLevel.EXTREME,
            "testosterone": RiskLevel.HIGH,
            "nandrolone": RiskLevel.HIGH,
            "dianabol": RiskLevel.HIGH,
            "anavar": RiskLevel.MODERATE,
            "winstrol": RiskLevel.MODERATE,
            "hgh": RiskLevel.HIGH,
            "igf": RiskLevel.HIGH,
            "rad-140": RiskLevel.MODERATE,
            "lgd-4033": RiskLevel.MODERATE,
            "mk-677": RiskLevel.MODERATE,
            "ostarine": RiskLevel.LOW,
            "bpc-157": RiskLevel.LOW,
            "tb-500": RiskLevel.LOW,
            "creatine": RiskLevel.VERY_SAFE,
            "whey": RiskLevel.VERY_SAFE,
            "caffeine": RiskLevel.SAFE,
            "beta-alanine": RiskLevel.SAFE,
            "citrulline": RiskLevel.SAFE,
            "bcaa": RiskLevel.SAFE,
            "omega-3": RiskLevel.VERY_SAFE,
            "vitamin d": RiskLevel.SAFE,
            "zma": RiskLevel.SAFE
        }
    
    def process(self, query: str) -> QueryUnderstanding:
        """Process query and return understanding"""
        query_lower = query.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Detect domain
        domain = self._detect_domain(query_lower)
        
        # Extract compound
        compound = self._extract_compound(query_lower)
        
        # Detect goal
        goal = self._detect_goal(query_lower)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(query_lower)
        
        # Detect experience level
        experience_level = self._detect_experience_level(query_lower)
        
        # Detect gender
        gender = self._detect_gender(query_lower)
        
        # Detect age group
        age_group = self._detect_age_group(query_lower)
        
        # Assess risk
        risk_level = self._assess_risk(compound, domain, modifiers)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, domain, compound, entities)
        
        return QueryUnderstanding(
            original_query=query,
            intent=intent,
            domain=domain,
            compound=compound,
            goal=goal,
            experience_level=experience_level,
            gender=gender,
            age_group=age_group,
            risk_level=risk_level,
            entities=entities,
            modifiers=modifiers,
            confidence=confidence
        )
    
    def _detect_intent(self, query: str) -> IntentType:
        """Detect primary intent from query patterns"""
        scores: Dict[IntentType, float] = {}
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    scores[intent] = scores.get(intent, 0) + 1
        
        if scores:
            return max(scores, key=scores.get)
        return IntentType.INFORMATIONAL
    
    def _detect_domain(self, query: str) -> DomainCategory:
        """Detect primary domain from query"""
        scores: Dict[DomainCategory, float] = {}
        
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    scores[domain] = scores.get(domain, 0) + 1
        
        if scores:
            return max(scores, key=scores.get)
        return DomainCategory.GENERAL
    
    def _extract_compound(self, query: str) -> Optional[str]:
        """Extract compound name from query"""
        for compound, pattern in self.compound_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return compound
        return None
    
    def _detect_goal(self, query: str) -> Optional[str]:
        """Detect user goal from query"""
        for goal, patterns in self.goal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return goal
        return None
    
    def _extract_modifiers(self, query: str) -> List[str]:
        """Extract modifiers from query"""
        modifiers = []
        for modifier, pattern in self.modifier_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                modifiers.append(modifier)
        return modifiers
    
    def _detect_experience_level(self, query: str) -> Optional[str]:
        """Detect experience level"""
        if re.search(r"\bbeginner|starter|new|first.?time|novice\b", query, re.IGNORECASE):
            return "beginner"
        if re.search(r"\badvanced|experienced|pro|expert\b", query, re.IGNORECASE):
            return "advanced"
        if re.search(r"\bintermediate\b", query, re.IGNORECASE):
            return "intermediate"
        return None
    
    def _detect_gender(self, query: str) -> Optional[str]:
        """Detect gender from query"""
        if re.search(r"\bfemale|women|woman|lady\b", query, re.IGNORECASE):
            return "female"
        if re.search(r"\bmale|men|man|gentleman\b", query, re.IGNORECASE):
            return "male"
        return None
    
    def _detect_age_group(self, query: str) -> Optional[str]:
        """Detect age group from query"""
        age_match = re.search(r"(\d+)\s*year", query, re.IGNORECASE)
        if age_match:
            age = int(age_match.group(1))
            if age < 18:
                return "under_18"
            elif age < 25:
                return "18-25"
            elif age < 35:
                return "25-35"
            elif age < 50:
                return "35-50"
            else:
                return "50+"
        if re.search(r"\bteenager|teen\b", query, re.IGNORECASE):
            return "13-19"
        if re.search(r"\b(senior|older|elderly)\b", query, re.IGNORECASE):
            return "50+"
        return None
    
    def _assess_risk(self, compound: Optional[str], domain: DomainCategory, 
                     modifiers: List[str]) -> RiskLevel:
        """Assess risk level"""
        # Check compound risk
        if compound:
            compound_lower = compound.lower()
            for name, risk in self.risk_mapping.items():
                if name in compound_lower or compound_lower in name:
                    return risk
        
        # Check domain risk
        high_risk_domains = [DomainCategory.STEROIDS, DomainCategory.HGH]
        moderate_risk_domains = [DomainCategory.SARMS, DomainCategory.PEPTIDES]
        
        if domain in high_risk_domains:
            return RiskLevel.HIGH
        if domain in moderate_risk_domains:
            return RiskLevel.MODERATE
        
        # Check for safety modifiers
        if "safe" in modifiers or "natural" in modifiers:
            return RiskLevel.SAFE
        
        return RiskLevel.MODERATE
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract all entities from query"""
        entities = []
        
        # Extract compounds
        for compound, pattern in self.compound_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                if compound not in entities:
                    entities.append(compound)
        
        # Extract goals
        for goal, patterns in self.goal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    if goal not in entities:
                        entities.append(goal)
        
        return entities
    
    def _calculate_confidence(self, intent: IntentType, domain: DomainCategory,
                            compound: Optional[str], entities: List[str]) -> float:
        """Calculate confidence score"""
        confidence = 0.5
        
        if compound:
            confidence += 0.2
        if entities:
            confidence += 0.1
        if domain != DomainCategory.GENERAL:
            confidence += 0.1
        if intent != IntentType.INFORMATIONAL:
            confidence += 0.1
        
        return min(confidence, 0.95)


# Singleton instance
agent = QueryUnderstandingAgent()

def understand_query(query: str) -> QueryUnderstanding:
    """Process query and return understanding"""
    return agent.process(query)
