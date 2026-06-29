from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class RecommendRequest(BaseModel):
    user_id: str
    spending_categories: Dict[str, float]
    region: str
    min_balance: float
    preference_text: Optional[str] = ""
    semantic_method: Optional[str] = "sentence_transformer"  # "tfidf", "sentence_transformer", "faiss"
    weight_semantic: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    weight_spending: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)


class CardResponse(BaseModel):
    card_id: str
    name: str
    final_score: float
    spending_score: float
    semantic_score: float
    match_reason: str


class RecommendResponse(BaseModel):
    recommendations: List[CardResponse]


# Evaluation Schemas
class MetricScore(BaseModel):
    method: str
    precision_at_k: float
    mrr: float
    ndcg: float


class EvaluationResponse(BaseModel):
    k: int
    results: List[MetricScore]


# Benchmarking Schemas
class LatencyMetrics(BaseModel):
    method: str
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float


class BenchmarkResponse(BaseModel):
    num_queries: int
    metrics: List[LatencyMetrics]