from fastapi import APIRouter
from app.models.schemas import (
    RecommendRequest,
    RecommendResponse,
    CardResponse,
)

from app.services.eligibility_service import (
    filter_eligible_cards,
    calculate_card_score,
)

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend_cards(request: RecommendRequest):

    eligible_cards = filter_eligible_cards(
        min_balance=request.min_balance,
        region=request.region,
    )

    recommendations = []

    for card in eligible_cards:

        score = calculate_card_score(
            card,
            request.spending_categories,
        )

        recommendations.append(
            CardResponse(
                card_id=card["card_id"],
                name=card["name"],
                final_score=score,
                match_reason="Score generated using spending behavior",
            )
        )

    recommendations.sort(
        key=lambda x: x.final_score,
        reverse=True
    )

    return RecommendResponse(
        recommendations=recommendations
    )