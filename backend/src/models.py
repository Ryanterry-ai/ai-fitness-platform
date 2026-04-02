"""
Data models for FitSearch AI
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class IntentType(str, Enum):
    INFORMATIONAL = "informational"
    DOSAGE = "dosage"
    CYCLE = "cycle"
    PRODUCT = "product"
    COMPARE = "compare"
    RESEARCH = "research"
    EXERCISE = "exercise"
    NUTRITION = "nutrition"
    SAFETY = "safety"
    RECOMMEND = "recommend"

class DomainCategory(str, Enum):
    SARMS = "sarms"
    STEROIDS = "steroids"
    PEPTIDES = "peptides"
    HGH = "hgh"
    SUPPLEMENTS = "supplements"
    EXERCISE = "exercise"
    NUTRITION = "nutrition"
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    BODYBUILDING = "bodybuilding"
    SPORTS_PERFORMANCE = "sports_performance"
    RECOVERY = "recovery"
    GENERAL = "general"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

class SafetyStatus(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"

class QueryUnderstanding(BaseModel):
    original_query: str
    intent: IntentType = IntentType.INFORMATIONAL
    domain: DomainCategory = DomainCategory.GENERAL
    compound: Optional[str] = None
    goal: Optional[str] = None
    experience_level: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MODERATE
    entities: List[str] = Field(default_factory=list)
    modifiers: List[str] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)
    confidence: float = 0.8

class KnowledgeResult(BaseModel):
    id: str
    name: str
    category: DomainCategory
    content: Dict[str, Any]
    relevance_score: float = 0.8
    source: str = "knowledge_base"

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    authority_score: float = 0.5
    freshness_score: float = 0.6
    relevance_score: float = 0.7

class ResearchResult(BaseModel):
    title: str
    authors: List[str]
    journal: str
    year: int
    pmid: Optional[str] = None
    abstract: str
    key_findings: List[str] = []
    evidence_level: str = "moderate"
    url: str = ""

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

class SafetyWarning(BaseModel):
    status: SafetyStatus
    level: RiskLevel
    warnings: List[str] = []
    precautions: List[str] = []
    disclaimer: str = "Consult healthcare professional before use."

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
