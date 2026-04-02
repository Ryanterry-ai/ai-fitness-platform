"""
SEO Intent Agent
Specialized agent for understanding SEO query patterns and user intent
"""
import re
from typing import Dict, List, Tuple
from ..models import IntentType, DomainCategory

class SEOIntentAgent:
    """
    SEO Intent Classification Agent
    Maps queries to specific SEO intent categories
    """
    
    def __init__(self):
        self._build_intent_keywords()
        self._build_seo_query_templates()
        self._build_question_patterns()
    
    def _build_intent_keywords(self):
        """Build keyword-to-intent mappings"""
        self.intent_keywords: Dict[IntentType, List[str]] = {
            IntentType.INFORMATIONAL: [
                "what is", "what are", "explain", "tell me about", "definition",
                "overview", "guide", "introduction", "basic", "basics"
            ],
            IntentType.HOW_IT_WORKS: [
                "how does", "how do", "how can", "how to", "mechanism of action",
                "works in", "biological", "physiological", "process"
            ],
            IntentType.BENEFITS: [
                "benefit", "advantages", "good for", "why take", "helps with",
                "positive effects", "gains", "improves", "enhances"
            ],
            IntentType.SIDE_EFFECTS: [
                "side effect", "negative", "risk", "harmful", "danger",
                "adverse", "bad for", "toxicity", "warning"
            ],
            IntentType.DOSAGE: [
                "dosage", "dose", "how much", "mg", "iu", "grams",
                "serving size", "amount", "quantity", "daily intake"
            ],
            IntentType.TIMING: [
                "when to take", "best time", "timing", "schedule",
                "before workout", "after workout", "morning", "night", "with food"
            ],
            IntentType.COMPARISON: [
                "vs", "versus", "compare", "difference between", "better than",
                "or", "which is better", "comparison"
            ],
            IntentType.BEGINNER: [
                "beginner", "starter", "first time", "new to", "starting",
                "introduction", "getting started", "basics for"
            ],
            IntentType.ADVANCED: [
                "advanced", "experienced", "pro", "elite", "expert",
                "optimized", "enhanced", "powerful"
            ],
            IntentType.GOAL_BASED: [
                "for muscle", "for fat loss", "for strength", "for endurance",
                "for performance", "to gain", "to lose", "to build"
            ],
            IntentType.CYCLE: [
                "cycle", "cycles", "protocol", "weeks", "duration",
                "length of", "cycle length", "how long to run"
            ],
            IntentType.STACK: [
                "stack", "stacking", "combination", "with", "combine",
                "along with", "paired with", "synergy"
            ],
            IntentType.PCT: [
                "pct", "post cycle", "post-cycle", "recovery",
                "nolvadex", "clomid", "serm", "restart", "restore"
            ],
            IntentType.DIET: [
                "diet", "nutrition", "meal plan", "eating plan", "macros",
                "calories", "cutting diet", "bulking diet", "meal prep"
            ],
            IntentType.WORKOUT: [
                "workout", "routine", "program", "training plan",
                "split", "schedule", "frequency"
            ],
            IntentType.EXERCISE: [
                "exercise", "how to do", "form", "technique", "proper",
                "execution", "movement"
            ],
            IntentType.SPORTS_PERFORMANCE: [
                "sports", "athlete", "performance", "endurance", "power",
                "speed", "agility", "vertical jump"
            ],
            IntentType.HORMONE: [
                "testosterone", "hormone", "booster", "levels",
                "t booster", "test levels", "hormonal"
            ],
            IntentType.SAFETY: [
                "is it safe", "are they safe", "safe?", "dangerous?",
                "harmful?", "risk?", "side effects safety"
            ],
            IntentType.NATURAL_ALTERNATIVES: [
                "natural", "alternative", "without steroids", "legal",
                "over the counter", "otc", "natural substitute"
            ],
            IntentType.BRAND: [
                "brand", "which brand", "best brand", "recommended brand",
                "brand name", "manufacturer"
            ],
            IntentType.RESEARCH: [
                "research", "studies", "scientific", "evidence",
                "clinical trial", "pubmed", "peer reviewed"
            ],
            IntentType.RESULTS: [
                "results", "expect", "gains", "progress", "transformation",
                "outcome", "what to expect"
            ],
            IntentType.TIMELINE: [
                "how long", "timeframe", "weeks", "months", "days",
                "when will", "timeline", "duration"
            ],
            IntentType.GENDER: [
                "for men", "for women", "male", "female", "gender",
                "man", "woman", "ladies", "gentlemen"
            ],
            IntentType.AGE: [
                "year old", "age", "teenager", "young", "older",
                "senior", "middle aged"
            ],
            IntentType.HEALTH_CONDITION: [
                "diabetes", "thyroid", "condition", "medical",
                "health issue", "disease", "disorder"
            ]
        }
    
    def _build_seo_query_templates(self):
        """Build SEO query templates"""
        self.seo_templates = {
            "informational_compound": "{compound} - What is {compound}?",
            "benefits_compound": "{compound} Benefits - What are the benefits of {compound}?",
            "dosage_compound": "{compound} Dosage - What is the recommended {compound} dosage?",
            "side_effects_compound": "{compound} Side Effects - What are the side effects?",
            "how_it_works": "How Does {compound} Work?",
            "cycle_compound": "{compound} Cycle - Complete Protocol Guide",
            "stack_compound": "{compound} Stack - Best Combinations",
            "comparison": "{compound} vs {compound2} - Which is Better?",
            "beginner_guide": "{compound} for Beginners - Complete Guide",
            "results_timeline": "{compound} Results - How Long Until I See Results?",
            "natural_alternative": "Natural Alternatives to {compound}",
            "pct_guide": "{compound} PCT - Post Cycle Therapy Guide",
            "safety_review": "Is {compound} Safe? - Complete Safety Analysis",
            "research_studies": "{compound} Studies - Scientific Research",
            "brand_comparison": "Best {compound} Brands - Top 2024"
        }
    
    def _build_question_patterns(self):
        """Build question detection patterns"""
        self.question_patterns = [
            r"^what", r"^how", r"^why", r"^when", r"^where",
            r"^which", r"^who", r"^is ", r"^are ", r"^do ",
            r"^does ", r"^can ", r"^should ", r"\?$"
        ]
    
    def classify_intent(self, query: str) -> Tuple[IntentType, float]:
        """Classify query intent with confidence"""
        query_lower = query.lower()
        scores: Dict[IntentType, float] = {}
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[intent] = scores.get(intent, 0) + 1.0
        
        if not scores:
            # Check for question patterns
            for pattern in self.question_patterns:
                if re.search(pattern, query_lower):
                    scores[IntentType.INFORMATIONAL] = 0.5
                    break
        
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(scores[best_intent] / 3.0, 0.95)
            return best_intent, confidence
        
        return IntentType.INFORMATIONAL, 0.5
    
    def extract_intent_keywords(self, query: str) -> List[str]:
        """Extract keywords that indicate intent"""
        query_lower = query.lower()
        found_keywords = []
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def generate_related_queries(self, query: str, intent: IntentType) -> List[str]:
        """Generate related SEO queries"""
        related = []
        
        if intent == IntentType.INFORMATIONAL:
            related.append(f"{query} benefits")
            related.append(f"{query} dosage")
            related.append(f"{query} side effects")
        elif intent == IntentType.DOSAGE:
            related.append(f"{query} cycle")
            related.append(f"{query} timing")
            related.append(f"best time to take {query}")
        elif intent == IntentType.SIDE_EFFECTS:
            related.append(f"{query} safety")
            related.append(f"is {query} safe")
            related.append(f"{query} PCT")
        
        return related[:5]


# Singleton
agent = SEOIntentAgent()

def classify_seo_intent(query: str) -> Tuple[IntentType, float]:
    """Classify SEO intent"""
    return agent.classify_intent(query)

def get_intent_keywords(query: str) -> List[str]:
    """Get intent keywords from query"""
    return agent.extract_intent_keywords(query)
