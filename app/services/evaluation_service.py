import math
from app.db.mongo import cards_collection
from app.services.semantic_service import get_tfidf_scores, get_transformer_scores
from app.services.faiss_service import get_faiss_scores

# Academic evaluation dataset of natural language user queries and ground-truth relevant card IDs
EVALUATION_DATASET = [
    {
        "query": "I travel frequently and spend a lot on flights",
        "ground_truth": ["CARD002", "CARD007"]  # Travel Rewards Card, Globetrotter Luxury Card
    },
    {
        "query": "I want cashback on my online shopping and grocery spending",
        "ground_truth": ["CARD001", "CARD005", "CARD006"]  # Premium Cashback, Supercharger Shopping, Basic Zero Fee
    },
    {
        "query": "I love eating at premium restaurants and ordering food online",
        "ground_truth": ["CARD004", "CARD001"]  # Premium Dining & Lifestyle Card, Premium Cashback Card
    },
    {
        "query": "I drive my car to work every day and spend a lot at gas stations",
        "ground_truth": ["CARD003"]  # Fuel Saver Card
    },
    {
        "query": "I need a lifetime free card for simple utility bill payments",
        "ground_truth": ["CARD006"]  # Basic Zero Fee Card
    },
    {
        "query": "I want high reward rates on purchasing laptops and electronics online",
        "ground_truth": ["CARD005"]  # Supercharger Shopping Card
    }
]


def calculate_precision_at_k(recommendations: list, ground_truth: list, k: int) -> float:
    """
    Computes Precision@K: the fraction of recommended items in the top K that are relevant.
    """
    if not recommendations or k <= 0:
        return 0.0
    
    top_k = recommendations[:k]
    relevant_retrieved = [item for item in top_k if item in ground_truth]
    return len(relevant_retrieved) / k


def calculate_reciprocal_rank(recommendations: list, ground_truth: list) -> float:
    """
    Computes Reciprocal Rank (RR): 1 / rank of the first relevant item.
    """
    for idx, card_id in enumerate(recommendations):
        if card_id in ground_truth:
            return 1.0 / (idx + 1)
    return 0.0


def calculate_ndcg_at_k(recommendations: list, ground_truth: list, k: int) -> float:
    """
    Computes Normalized Discounted Cumulative Gain (NDCG@K) using binary relevance.
    """
    if not recommendations or k <= 0:
        return 0.0

    # Calculate DCG@K
    dcg = 0.0
    for i in range(min(k, len(recommendations))):
        card_id = recommendations[i]
        rel = 1.0 if card_id in ground_truth else 0.0
        dcg += rel / math.log2(i + 2)

    # Calculate Ideal DCG@K (all relevant items ranked at top)
    idcg = 0.0
    num_relevant = min(k, len(ground_truth))
    for i in range(num_relevant):
        idcg += 1.0 / math.log2(i + 2)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def evaluate_method(method: str, k: int = 3) -> dict:
    """
    Evaluates a specific retrieval method across all queries in the evaluation dataset.
    Returns average Precision@K, MRR, and NDCG@K.
    """
    # Fetch all active cards for pure semantic retrieval evaluation
    cards = list(cards_collection.find({"active": True}))
    if not cards:
        return {"precision_at_k": 0.0, "mrr": 0.0, "ndcg": 0.0}

    total_precision = 0.0
    total_rr = 0.0
    total_ndcg = 0.0
    num_queries = len(EVALUATION_DATASET)

    for item in EVALUATION_DATASET:
        query = item["query"]
        ground_truth = item["ground_truth"]

        # 1. Retrieve raw semantic scores
        method_lower = method.lower().strip()
        if method_lower == "tfidf":
            scores = get_tfidf_scores(query, cards)
        elif method_lower == "faiss":
            scores = get_faiss_scores(query, cards)
        else:
            scores = get_transformer_scores(query, cards)

        # 2. Rank cards based on semantic score
        ranked_cards = sorted(cards, key=lambda x: scores.get(x["card_id"], 0.0), reverse=True)
        recommendations = [card["card_id"] for card in ranked_cards]

        # 3. Compute metrics
        total_precision += calculate_precision_at_k(recommendations, ground_truth, k)
        total_rr += calculate_reciprocal_rank(recommendations, ground_truth)
        total_ndcg += calculate_ndcg_at_k(recommendations, ground_truth, k)

    return {
        "precision_at_k": round(total_precision / num_queries, 4),
        "mrr": round(total_rr / num_queries, 4),
        "ndcg": round(total_ndcg / num_queries, 4)
    }
