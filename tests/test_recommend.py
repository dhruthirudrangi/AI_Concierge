import pytest
from fastapi.testclient import TestClient
import numpy as np

from app.main import app
from app.services.semantic_service import get_tfidf_scores, get_transformer_scores, EmbeddingService
from app.services.faiss_service import get_faiss_scores
from app.services.hybrid_service import compute_hybrid_recommendations
from app.services.evaluation_service import (
    calculate_precision_at_k,
    calculate_reciprocal_rank,
    calculate_ndcg_at_k,
    evaluate_method
)

client = TestClient(app)

# Dummy card dataset for testing
TEST_CARDS = [
    {
        "card_id": "CARD_T1",
        "name": "Test Cashback Card",
        "min_balance_required": 5000,
        "region": "India",
        "active": True,
        "preferred_categories": ["shopping"],
        "description": "Earn cashback on shopping and grocery stores."
    },
    {
        "card_id": "CARD_T2",
        "name": "Test Travel Card",
        "min_balance_required": 10000,
        "region": "India",
        "active": True,
        "preferred_categories": ["travel"],
        "description": "Premium rewards on travel and airport lounge access."
    }
]


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Credit Card Recommendation" in response.json()["message"]


def test_tfidf_similarity():
    scores = get_tfidf_scores("I want a shopping card", TEST_CARDS)
    # The shopping card description has "shopping", travel card does not.
    # Therefore, CARD_T1 should have a higher similarity score than CARD_T2.
    assert scores["CARD_T1"] > scores["CARD_T2"]


def test_sentence_transformer_similarity():
    scores = get_transformer_scores("I love travelling and flights", TEST_CARDS)
    # "travelling" should have high semantic similarity with CARD_T2 ("travel", "lounge access")
    assert scores["CARD_T2"] > scores["CARD_T1"]


def test_faiss_similarity():
    scores = get_faiss_scores("I love travelling and flights", TEST_CARDS)
    # FAISS scores should be similar and rank CARD_T2 higher than CARD_T1
    assert scores["CARD_T2"] > scores["CARD_T1"]


def test_hybrid_recommendation():
    # If we have 100% weight on spending
    results_spending = compute_hybrid_recommendations(
        cards=TEST_CARDS,
        spending_categories={"shopping": 5000},
        preference_text="",
        weight_semantic=0.0,
        weight_spending=1.0
    )
    # CARD_T1 has shopping as preferred, CARD_T2 has travel.
    # So CARD_T1 should be first, and its final_score should be 1.0 (normalized)
    assert results_spending[0]["card_id"] == "CARD_T1"
    assert results_spending[0]["final_score"] == 1.0

    # If we have 100% weight on semantic
    results_semantic = compute_hybrid_recommendations(
        cards=TEST_CARDS,
        spending_categories={},
        preference_text="lounge access",
        weight_semantic=1.0,
        weight_spending=0.0
    )
    assert results_semantic[0]["card_id"] == "CARD_T2"


def test_academic_metrics():
    # Precision@1
    recs = ["CARD1", "CARD2", "CARD3"]
    gt = ["CARD2"]
    assert calculate_precision_at_k(recs, gt, 1) == 0.0
    assert calculate_precision_at_k(recs, gt, 2) == 0.5

    # Reciprocal Rank
    assert calculate_reciprocal_rank(recs, gt) == 0.5  # CARD2 is at index 1 (rank 2)
    assert calculate_reciprocal_rank(recs, ["CARD4"]) == 0.0

    # NDCG@2
    # Recommendations: CARD1 (not relevant), CARD2 (relevant).
    # dcg@2 = 0 / log2(2) + 1 / log2(3) = 0 + 1 / 1.58496 = 0.6309
    # idcg@2 = 1 / log2(2) = 1.0
    # ndcg@2 = 0.6309 / 1.0 = 0.6309
    assert abs(calculate_ndcg_at_k(recs, gt, 2) - 0.6309) < 0.001


def test_recommend_api():
    payload = {
        "user_id": "U001",
        "spending_categories": {
            "shopping": 5000,
            "dining": 3000
        },
        "region": "India",
        "min_balance": 15000,
        "preference_text": "shopping and cashback card",
        "semantic_method": "sentence_transformer",
        "weight_semantic": 0.5,
        "weight_spending": 0.5
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    # Verify the structure has our new explainability fields
    rec = data["recommendations"][0]
    assert "card_id" in rec
    assert "spending_score" in rec
    assert "semantic_score" in rec
    assert "match_reason" in rec


def test_evaluate_api():
    response = client.post("/evaluate?k=3")
    assert response.status_code == 200
    data = response.json()
    assert "k" in data
    assert data["k"] == 3
    assert "results" in data
    assert len(data["results"]) == 3
    methods = [res["method"] for res in data["results"]]
    assert "tfidf" in methods
    assert "sentence_transformer" in methods
    assert "faiss" in methods


def test_benchmark_api():
    response = client.post("/benchmark?num_queries=5")
    assert response.status_code == 200
    data = response.json()
    assert "num_queries" in data
    assert data["num_queries"] == 5
    assert "metrics" in data
    assert len(data["metrics"]) == 3
