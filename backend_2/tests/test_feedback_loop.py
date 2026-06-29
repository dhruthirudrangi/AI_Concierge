import os
import tempfile
import pytest
from app.feedback_loop import FeedbackLoopTracker

@pytest.fixture
def temp_tracker():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_feedback.sqlite")
        tracker = FeedbackLoopTracker(db_path=db_path)
        yield tracker

def test_feedback_logging_and_affinity(temp_tracker):
    user_id = "user_123"
    
    # 1. Log a 'like' event for a dining & travel card
    temp_tracker.log_feedback(user_id, "card_a", "like", ["dining", "travel"])
    
    affinity, disliked = temp_tracker.get_user_affinity(user_id)
    assert disliked == set()
    assert affinity["dining"] == 1.0
    assert affinity["travel"] == 1.0
    
    # 2. Log an 'apply' event for dining
    temp_tracker.log_feedback(user_id, "card_b", "apply", ["dining"])
    
    affinity, disliked = temp_tracker.get_user_affinity(user_id)
    # Dining should be 1.0 (like) + 2.0 (apply) = 3.0
    assert affinity["dining"] == 3.0
    assert affinity["travel"] == 1.0
    
    # 3. Log a 'dislike' event for travel (specific card card_c)
    temp_tracker.log_feedback(user_id, "card_c", "dislike", ["travel"])
    
    affinity, disliked = temp_tracker.get_user_affinity(user_id)
    assert disliked == {"card_c"}
    # Travel should be 1.0 (like) - 2.0 (dislike) = -1.0
    assert affinity["travel"] == -1.0
    assert affinity["dining"] == 3.0

def test_affinity_clamping(temp_tracker):
    user_id = "user_affinity_clamp"
    
    # Log 4 applies for the same category to accumulate 8.0 score (exceeds clamp limit of 5.0)
    for i in range(4):
        temp_tracker.log_feedback(user_id, f"card_{i}", "apply", ["shopping"])
        
    affinity, _ = temp_tracker.get_user_affinity(user_id)
    # Score should be clamped to 5.0
    assert affinity["shopping"] == 5.0
    
    # Log 4 dislikes for groceries to accumulate -8.0 score (exceeds clamp limit of -5.0)
    for i in range(4):
        temp_tracker.log_feedback(user_id, f"card_dis_{i}", "dislike", ["grocery"])
        
    affinity, _ = temp_tracker.get_user_affinity(user_id)
    assert affinity["grocery"] == -5.0
