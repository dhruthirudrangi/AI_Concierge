import pytest
from app.data_store import RewardCard, UserProfile
from app.re_ranking import ReRanker

@pytest.fixture
def sample_user():
    return UserProfile(
        user_id="user_foodie",
        name="Alex Foodie",
        balance=5000,
        region="US",
        spending_habits={"dining": 0.60, "grocery": 0.40},
        eligibility_tier="Gold",
        preferences=["restaurant cash back", "dining discounts"]
    )

@pytest.fixture
def sample_cards():
    return [
        # Specializes in Dining (5x dining multiplier)
        RewardCard(
            card_id="card_dining_super", name="Dining Super Card", issuer="Bank", description="Great dining card",
            points_cost=1000, region="US", categories=["dining"], multipliers={"dining": 5.0},
            eligibility_tier="None", is_available=True
        ),
        # Specializes in Travel (no spend share travel)
        RewardCard(
            card_id="card_travel_super", name="Travel Super Card", issuer="Bank", description="Great travel card",
            points_cost=1000, region="US", categories=["travel"], multipliers={"travel": 5.0},
            eligibility_tier="None", is_available=True
        )
    ]

def test_calculate_multiplier_bonus(sample_user, sample_cards):
    dining_card = sample_cards[0]
    travel_card = sample_cards[1]
    
    # Dining Card: spend share (dining=0.6) * mult (dining=5.0) = 3.0 / 5.0 = 0.6 bonus
    dining_bonus = ReRanker.calculate_multiplier_bonus(sample_user, dining_card)
    assert abs(dining_bonus - 0.6) < 1e-5
    
    # Travel Card: spend share (travel=0.0) * mult (travel=5.0) = 0.0 bonus
    travel_bonus = ReRanker.calculate_multiplier_bonus(sample_user, travel_card)
    assert abs(travel_bonus - 0.0) < 1e-5

def test_calculate_feedback_bonus():
    card = RewardCard(
        card_id="c1", name="Card 1", issuer="B", description="D",
        points_cost=0, region="US", categories=["dining", "grocery"], multipliers={}
    )
    
    # positive feedback on dining, negative on grocery
    affinity = {"dining": 3.0, "grocery": -1.0}
    # sum = 3.0 - 1.0 = 2.0 / 5.0 = 0.4
    bonus = ReRanker.calculate_feedback_bonus(affinity, card)
    assert abs(bonus - 0.4) < 1e-5

def test_re_rank_scoring_and_exclusions(sample_user, sample_cards):
    # Setup candidate inputs (card, flags)
    candidates = [
        (sample_cards[0], []),  # dining card (no flags)
        (sample_cards[1], ["tier_upgrade_required"])  # travel card (tier mismatch)
    ]
    
    similarity_map = {
        "card_dining_super": 0.8,
        "card_travel_super": 0.8
    }
    
    # Re-rank with empty feedback
    results = ReRanker.re_rank(
        candidates=candidates,
        similarity_map=similarity_map,
        user=sample_user,
        category_affinity={},
        disliked_card_ids=set(),
        top_n=2
    )
    
    assert len(results) == 2
    # Dining card should rank first due to higher spend category match (0.6 vs 0) and no penalty
    assert results[0]["card"].card_id == "card_dining_super"
    assert results[0]["final_score"] > results[1]["final_score"]
    
    # Test exclusions: add dining card to disliked set
    results_with_dislike = ReRanker.re_rank(
        candidates=candidates,
        similarity_map=similarity_map,
        user=sample_user,
        category_affinity={},
        disliked_card_ids={"card_dining_super"},
        top_n=2
    )
    # Dining card should be filtered out
    assert len(results_with_dislike) == 1
    assert results_with_dislike[0]["card"].card_id == "card_travel_super"

def test_generate_explanation(sample_user):
    dining_card = RewardCard(
        card_id="c_din", name="Card", issuer="B", description="D",
        points_cost=3000, region="US", categories=["dining"], multipliers={"dining": 4.0}
    )
    
    explanations = ReRanker.generate_explanation(
        card=dining_card,
        user=sample_user,
        similarity=0.9,
        mult_bonus=0.48,
        feed_bonus=0.3,
        flags=["insufficient_points"]
    )
    
    explanation_str = " ".join(explanations)
    assert "Highly matches" in explanation_str
    # 4.0x on dining, user has 60% dining spend
    assert "Earns 4.0x on Dining" in explanation_str
    assert "aligning with your highest spend share (60%)" in explanation_str
    # Insufficient points warning details
    assert "Requires 3,000 points" in explanation_str
