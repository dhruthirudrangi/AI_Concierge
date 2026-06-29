from fastapi import APIRouter
from app.models.schemas import (
    RecommendRequest,
    RecommendResponse,
    CardResponse,
)
from app.services.eligibility_service import filter_eligible_cards
from app.services.hybrid_service import compute_hybrid_recommendations

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend_cards(request: RecommendRequest):
    # 1. Eligibility Filtering
    eligible_cards = filter_eligible_cards(
        min_balance=request.min_balance,
        region=request.region,
    )

    if not eligible_cards:
        return RecommendResponse(recommendations=[])

    # 2. Compute Hybrid Recommendation scores
    hybrid_results = compute_hybrid_recommendations(
        cards=eligible_cards,
        spending_categories=request.spending_categories,
        preference_text=request.preference_text,
        semantic_method=request.semantic_method,
        weight_semantic=request.weight_semantic,
        weight_spending=request.weight_spending,
    )

    # 3. Build response
    recommendations = [
        CardResponse(
            card_id=item["card_id"],
            name=item["name"],
            final_score=item["final_score"],
            spending_score=item["spending_score"],
            semantic_score=item["semantic_score"],
            match_reason=item["match_reason"],
        )
        for item in hybrid_results
    ]

    return RecommendResponse(recommendations=recommendations)