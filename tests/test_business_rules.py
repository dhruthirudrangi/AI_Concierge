import pytest
from app.data_store import RewardCard, UserProfile
from app.business_rules import BusinessRulesEngine

@pytest.fixture
def sample_user():
    return UserProfile(
        user_id="test_user",
        name="Test User",
        balance=2000,
        region="US",
        spending_habits={"dining": 0.5, "grocery": 0.5},
        eligibility_tier="Gold",
        preferences=[]
    )

@pytest.fixture
def sample_cards():
    return [
        # Strict pass
        RewardCard(
            card_id="card_1", name="Card 1", issuer="Bank", description="Desc",
            points_cost=1000, region="US", categories=["dining"], multipliers={"dining": 3.0},
            eligibility_tier="Gold", is_available=True
        ),
        # Fails points cost (strict)
        RewardCard(
            card_id="card_2", name="Card 2", issuer="Bank", description="Desc",
            points_cost=5000, region="US", categories=["dining"], multipliers={"dining": 3.0},
            eligibility_tier="None", is_available=True
        ),
        # Fails region (strict)
        RewardCard(
            card_id="card_3", name="Card 3", issuer="Bank", description="Desc",
            points_cost=500, region="EU", categories=["dining"], multipliers={"dining": 3.0},
            eligibility_tier="None", is_available=True
        ),
        # Fails tier (strict)
        RewardCard(
            card_id="card_4", name="Card 4", issuer="Bank", description="Desc",
            points_cost=500, region="US", categories=["dining"], multipliers={"dining": 3.0},
            eligibility_tier="Platinum", is_available=True
        ),
        # Fails availability
        RewardCard(
            card_id="card_5", name="Card 5", issuer="Bank", description="Desc",
            points_cost=500, region="US", categories=["dining"], multipliers={"dining": 3.0},
            eligibility_tier="None", is_available=False
        ),
        # Strict pass - GLOBAL region
        RewardCard(
            card_id="card_6", name="Card 6", issuer="Bank", description="Desc",
            points_cost=1500, region="GLOBAL", categories=["dining"], multipliers={"dining": 2.0},
            eligibility_tier="None", is_available=True
        ),
    ]

def test_tier_eligibility():
    assert BusinessRulesEngine.is_tier_eligible("Platinum", "Platinum") is True
    assert BusinessRulesEngine.is_tier_eligible("Platinum", "Gold") is True
    assert BusinessRulesEngine.is_tier_eligible("Gold", "Platinum") is False
    assert BusinessRulesEngine.is_tier_eligible("None", "Gold") is False
    assert BusinessRulesEngine.is_tier_eligible("Gold", "None") is True

def test_matches_region():
    assert BusinessRulesEngine.matches_region("US", "US") is True
    assert BusinessRulesEngine.matches_region("US", "GLOBAL") is True
    assert BusinessRulesEngine.matches_region("US", "EU") is False

def test_strict_filtering(sample_user, sample_cards):
    engine = BusinessRulesEngine()
    passed = engine.filter_strict(sample_cards, sample_user)
    
    passed_ids = [c.card_id for c in passed]
    # Only card_1 and card_6 should pass strictly
    assert "card_1" in passed_ids
    assert "card_6" in passed_ids
    assert len(passed_ids) == 2

def test_relaxed_filtering(sample_user, sample_cards):
    engine = BusinessRulesEngine()
    relaxed = engine.filter_relaxed(sample_cards, sample_user)
    
    # Check annotations
    # card_5 is unavailable, should not be returned
    relaxed_map = {item[0].card_id: item[1] for item in relaxed}
    
    assert "card_5" not in relaxed_map
    assert relaxed_map["card_1"] == []  # strict pass
    assert relaxed_map["card_2"] == ["insufficient_points"]
    assert relaxed_map["card_3"] == ["region_mismatch"]
    assert relaxed_map["card_4"] == ["tier_upgrade_required"]

def test_filtering_pipeline_activates_fallback(sample_user, sample_cards):
    engine = BusinessRulesEngine()
    
    # Since only 2 cards pass strictly, and MIN_RECOMMENDATIONS is 3,
    # the pipeline should activate relaxed fallback.
    results = engine.run_filtering_pipeline(sample_cards, sample_user)
    
    assert len(results) > 2
    # Ensure they are sorted by flags count
    assert results[0][1] == []  # First elements should be strict passes (card_1 or card_6)
    
    # Ensure easiest flags (like tier upgrade) come before harder flags (like region mismatch)
    flags_list = [item[1] for item in results]
    assert len(flags_list[0]) <= len(flags_list[-1])
