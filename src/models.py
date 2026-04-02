"""
Data models and schemas for Multi-Agent AI Search Platform
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class IntentType(str, Enum):
    """Query intent types"""
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
    """Domain categories for fitness content"""
    SUPPLEMENTS = "supplements"
    SARMS = "sarms"
    STEROIDS = "steroids"
    PEPTIDES = "peptides"
    HGH = "hgh"
    EXERCISE = "exercise"
    NUTRITION = "nutrition"
    BODYBUILDING = "bodybuilding"
    SPORTS_PERFORMANCE = "sports_performance"
    RECOVERY = "recovery"
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    GENERAL = "general"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class SafetyStatus(str, Enum):
    """Safety check status"""
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"


class QueryUnderstanding(BaseModel):
    """Output from Query Understanding Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    original_query: str
    intent: IntentType
    domain: DomainCategory
    compound: Optional[str] = None
    goal: Optional[str] = None
    experience_level: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MODERATE
    entities: List[str] = Field(default_factory=list)
    modifiers: List[str] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)
    language: str = "en"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class KnowledgeResult(BaseModel):
    """Result from Knowledge Base Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    category: DomainCategory
    content: Dict[str, Any]
    relevance_score: float = Field(ge=0.0, le=1.0)
    source: str = "knowledge_base"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WebSearchResult(BaseModel):
    """Result from Web Search Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    url: str
    snippet: str
    source: str
    authority_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    published_date: Optional[datetime] = None


class ResearchResult(BaseModel):
    """Result from Research Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: str
    year: Optional[int] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None
    abstract: str
    key_findings: List[str] = Field(default_factory=list)
    evidence_level: str = "moderate"
    url: Optional[str] = None


class RankedResult(BaseModel):
    """Result from Ranking Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    result_type: str  # "knowledge", "web", "research"
    content: Dict[str, Any]
    combined_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    authority_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    safety_score: float = Field(ge=0.0, le=1.0)
    source: str


class SafetyWarning(BaseModel):
    """Safety warning from Safety Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    status: SafetyStatus
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)
    severity: str = "moderate"


class SearchResponse(BaseModel):
    """Final response from Response Generation Agent"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    query: str
    query_understanding: QueryUnderstanding
    results: List[RankedResult] = Field(default_factory=list)
    safety: SafetyWarning
    ai_summary: Optional[str] = None
    sections: Dict[str, Any] = Field(default_factory=dict)
    references: List[Dict[str, Any]] = Field(default_factory=list)
    cached: bool = False
    processing_time_ms: float = 0.0
    agents_used: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SearchRequest(BaseModel):
    """Incoming search request"""
    query: str = Field(..., min_length=1, max_length=500)
    filters: List[str] = Field(default_factory=list)
    domain: Optional[DomainCategory] = None
    include_research: bool = True
    include_web: bool = True
    max_results: int = Field(default=10, ge=1, le=50)


class CachedResult(BaseModel):
    """Cached search result"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    cache_key: str
    query: str
    response: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0


class EmbeddingDocument(BaseModel):
    """Document for embedding storage"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_type: str  # "compound", "exercise", "nutrition", "research"
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
