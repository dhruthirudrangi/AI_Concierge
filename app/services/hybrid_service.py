from app.services.eligibility_service import calculate_card_score
from app.services.semantic_service import get_tfidf_scores, get_transformer_scores
from app.services.faiss_service import get_faiss_scores


def compute_hybrid_recommendations(
    cards: list,
    spending_categories: dict,
    preference_text: str = "",
    semantic_method: str = "sentence_transformer",
    weight_semantic: float = 0.5,
    weight_spending: float = 0.5
) -> list:
    """
    Computes hybrid recommendation scores combining eligibility, spending behavior,
    and semantic similarity. Returns a list of dicts with calculated scores and reasons.
    """
    if not cards:
        return []

    # 1. Compute raw spending scores
    spending_scores = {}
    for card in cards:
        spending_scores[card["card_id"]] = calculate_card_score(card, spending_categories)

    max_spending_score = max(spending_scores.values()) if spending_scores else 0.0

    # 2. Compute raw semantic similarity scores
    semantic_scores = {}
    if preference_text.strip():
        method = semantic_method.lower().strip()
        if method == "tfidf":
            semantic_scores = get_tfidf_scores(preference_text, cards)
        elif method == "faiss":
            semantic_scores = get_faiss_scores(preference_text, cards)
        else:
            # Default to sentence_transformer
            semantic_scores = get_transformer_scores(preference_text, cards)
    else:
        # No preference text provided
        semantic_scores = {card["card_id"]: 0.0 for card in cards}

    # 3. Normalize and combine scores
    scored_cards = []
    for card in cards:
        card_id = card["card_id"]
        raw_spending = spending_scores[card_id]
        raw_semantic = semantic_scores.get(card_id, 0.0)

        # Normalize spending score to [0, 1]
        if max_spending_score > 0.0:
            norm_spending = raw_spending / max_spending_score
        else:
            norm_spending = 0.0

        # Normalize semantic score (clip negative similarities to 0)
        norm_semantic = max(0.0, raw_semantic)

        # Weighted combination
        final_score = (weight_semantic * norm_semantic) + (weight_spending * norm_spending)
        final_score = round(final_score, 4)

        # Build natural language explainable match reason
        weight_sem_pct = int(weight_semantic * 100)
        weight_sp_pct = int(weight_spending * 100)
        
        if preference_text.strip():
            reason = (
                f"Combined Score: {final_score:.2f} | "
                f"{weight_sem_pct}% Semantic Match (score: {raw_semantic:.2f}) + "
                f"{weight_sp_pct}% Spending Profile Match (score: {raw_spending:.2f}, normalized: {norm_spending:.2f})"
            )
        else:
            reason = (
                f"Combined Score: {final_score:.2f} | "
                f"Based 100% on Spending Profile (score: {raw_spending:.2f}) because no preference text was provided."
            )

        scored_cards.append({
            "card_id": card_id,
            "name": card["name"],
            "final_score": final_score,
            "spending_score": float(raw_spending),
            "semantic_score": float(raw_semantic),
            "match_reason": reason
        })

    # 4. Sort cards by final score descending
    scored_cards.sort(key=lambda x: x["final_score"], reverse=True)

    return scored_cards
