"""
FitSearch AI - Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ── Intent Types ──────────────────────────────────────────────────────────────
class IntentType(str, Enum):
    INFORMATIONAL = "informational"
    HOW_IT_WORKS = "how_it_works"
    BENEFITS = "benefits"
    SIDE_EFFECTS = "side_effects"
    DOSAGE = "dosage"
    TIMING = "timing"
    COMPARISON = "comparison"
    BEGINNER = "beginner"
    ADVANCED = "advanced"
    GOAL_BASED = "goal_based"
    CYCLE = "cycle"
    STACK = "stack"
    PCT = "pct"
    DIET = "diet"
    WORKOUT = "workout"
    EXERCISE = "exercise"
    SPORTS_PERFORMANCE = "sports_performance"
    HORMONE = "hormone"
    SAFETY = "safety"
    NATURAL_ALTERNATIVES = "natural_alternatives"
    BRAND = "brand"
    RESEARCH = "research"
    RESULTS = "results"
    TIMELINE = "timeline"
    GENDER = "gender"
    AGE = "age"
    HEALTH_CONDITION = "health_condition"
    SUBSTANCE_SPECIFIC = "substance_specific"

# ── Domain Categories ─────────────────────────────────────────────────────────
class DomainCategory(str, Enum):
    HEALTH = "health"
    FITNESS = "fitness"
    BODYBUILDING = "bodybuilding"
    NUTRITION = "nutrition"
    SUPPLEMENTS = "supplements"
    STEROIDS = "steroids"
    SARMS = "sarms"
    PEPTIDES = "peptides"
    HGH = "hgh"
    EXERCISES = "exercises"
    WORKOUTS = "workouts"
    DIET = "diet"
    SPORTS_PERFORMANCE = "sports_performance"
    PERFORMANCE_COMPOUNDS = "performance_compounds"
    GENERAL = "general"

# ── Risk Levels ───────────────────────────────────────────────────────────────
class RiskLevel(str, Enum):
    VERY_SAFE = "very_safe"
    SAFE = "safe"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

# ── Safety Status ─────────────────────────────────────────────────────────────
class SafetyStatus(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"

# ── Query Understanding ───────────────────────────────────────────────────────
class QueryUnderstanding(BaseModel):
    original_query: str
    intent: IntentType = IntentType.INFORMATIONAL
    domain: DomainCategory = DomainCategory.GENERAL
    compound: Optional[str] = None
    goal: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    experience_level: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MODERATE
    entities: List[str] = Field(default_factory=list)
    modifiers: List[str] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)
    language: str = "en"
    confidence: float = 0.8

# ── Knowledge Result ───────────────────────────────────────────────────────────
class KnowledgeResult(BaseModel):
    id: str
    name: str
    category: DomainCategory
    content: Dict[str, Any]
    relevance_score: float = 0.8
    source: str = "knowledge_base"

# ── Web Search Result ──────────────────────────────────────────────────────────
class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    authority_score: float = 0.5
    freshness_score: float = 0.6
    relevance_score: float = 0.7

# ── Research Result ────────────────────────────────────────────────────────────
class ResearchResult(BaseModel):
    title: str
    authors: List[str] = []
    journal: str = ""
    year: int = 2020
    pmid: Optional[str] = None
    abstract: str = ""
    key_findings: List[str] = []
    evidence_level: str = "moderate"
    url: str = ""

# ── Ranked Result ─────────────────────────────────────────────────────────────
class RankedResult(BaseModel):
    id: str
    result_type: str
    content: Dict[str, Any]
    combined_score: float
    relevance_score: float
    authority_score: float
    freshness_score: float
    safety_score: float
    source: str

# ── Safety Warning ─────────────────────────────────────────────────────────────
class SafetyWarning(BaseModel):
    status: SafetyStatus
    level: RiskLevel
    warnings: List[str] = []
    precautions: List[str] = []
    disclaimer: str = "Consult healthcare professional before use."

# ── Search Response ────────────────────────────────────────────────────────────
class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    sections: Dict[str, Any] = {}
    ai_summary: Optional[str] = None
    safety: Dict[str, Any] = {}
    references: List[Dict[str, Any]] = []
    content_type: str = "general"
    cached: bool = False
    processing_time_ms: float = 0.0
    agents_used: List[str] = []
    timestamp: str = ""

# ── SEO Query Pattern ──────────────────────────────────────────────────────────
class SEOQueryPattern(BaseModel):
    pattern: str
    intent: IntentType
    examples: List[str] = []
