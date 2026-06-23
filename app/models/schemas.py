from pydantic import BaseModel
from typing import Dict, List


class RecommendRequest(BaseModel):
    user_id: str
    spending_categories: Dict[str, float]
    region: str
    min_balance: float


class CardResponse(BaseModel):
    card_id: str
    name: str
    final_score: float
    match_reason: str


class RecommendResponse(BaseModel):
    recommendations: List[CardResponse]