from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from app.services.eligibility_service import filter_eligible_cards
from app.services.hybrid_service import compute_hybrid_recommendations
import traceback

router = APIRouter()

# Frontend Schemas
class UserPreferences(BaseModel):
    categories: List[str]
    monthlySpend: float
    region: str
    balance: float

class FrontendRecommendRequest(BaseModel):
    preferences: UserPreferences
    query: Optional[str] = ""
    topN: Optional[int] = 10

class FrontendFeedbackPayload(BaseModel):
    cardId: str
    cardName: str
    userId: str
    feedback: str
    timestamp: str

@router.post("/api/recommend")
def recommend_for_frontend(request: FrontendRecommendRequest):
    try:
        # 1. Translate frontend payload to backend logic
        spending_categories = {cat: request.preferences.monthlySpend for cat in request.preferences.categories}
        if not spending_categories:
            spending_categories = {"general": request.preferences.monthlySpend}
            
        region = request.preferences.region
        if not region:
            region = "Global"

        # 2. Eligibility Filtering
        eligible_cards = filter_eligible_cards(
            min_balance=request.preferences.balance,
            region=region,
        )

        if not eligible_cards:
            return {"cards": [], "model": "tfidf", "timestamp": ""}

        # 3. Compute Hybrid Recommendation scores
        hybrid_results = compute_hybrid_recommendations(
            cards=eligible_cards,
            spending_categories=spending_categories,
            preference_text=request.query or "",
            semantic_method="sentence_transformer" if len(request.query or "") > 20 else "tfidf",
            weight_semantic=0.6,
            weight_spending=0.4,
        )

        # 4. Map back to frontend expected structure
        # Create a lookup for fast access to full card data
        card_lookup = {c["card_id"]: c for c in eligible_cards}
        
        frontend_cards = []
        for i, item in enumerate(hybrid_results[:request.topN]):
            full_card = card_lookup[item["card_id"]]
            
            # Map DB fields to Frontend fields
            frontend_card = {
                "id": full_card.get("card_id", ""),
                "name": full_card.get("name", ""),
                "issuer": full_card.get("issuer", "Kobie Bank"), # default if missing
                "benefits": full_card.get("benefits", []),
                "description": full_card.get("description", ""),
                "annualFee": full_card.get("annual_fee", 0),
                "minBalance": full_card.get("min_balance_required", 0),
                "regions": [full_card.get("region", "Global")],
                "categories": full_card.get("preferred_categories", []),
                "applyUrl": full_card.get("apply_url", "#"),
                
                # Computed scores
                "score": item.get("final_score", 0),
                "similarityScore": item.get("semantic_score", 0),
                "businessRuleWeight": item.get("spending_score", 0),
                "rank": i + 1
            }
            frontend_cards.append(frontend_card)

        return {
            "cards": frontend_cards,
            "model": "sentence_transformer" if len(request.query or "") > 20 else "tfidf",
            "timestamp": ""
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/feedback")
def submit_feedback(payload: FrontendFeedbackPayload):
    try:
        from backend_2.app.feedback_loop import FeedbackLoopTracker
        tracker = FeedbackLoopTracker()
        tracker.log_feedback(
            user_id=payload.userId,
            card_id=payload.cardId,
            action=payload.feedback,
            categories=[] # We don't have categories from frontend feedback easily, so empty for now
        )
        return {"status": "success"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
