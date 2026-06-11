import time
import numpy as np
from app.data_store import generate_mock_cards, UserProfile, JSONDataStore
from app.faiss_index import FAIRewardIndex
from app.business_rules import BusinessRulesEngine
from app.re_ranking import ReRanker
from app.feedback_loop import FeedbackLoopTracker

def print_step(num: int, title: str, content: str):
    print(f"\n======================================================================")
    print(f" STEP {num}: {title.upper()}")
    print(f"======================================================================")
    print(content)
    time.sleep(0.5)

def main():
    print("\n>>> INITIALIZING DEMO: AI REWARDS CONCIERGE SCENARIO WALKTHROUGH <<<")
    
    # Initialize components
    cards = generate_mock_cards(100)
    card_ids = [c.card_id for c in cards]
    
    # Create simple BERT-like embeddings (768-d)
    # We will embed a few concepts: index 0-10 are travel cards, 10-20 are dining cards
    np.random.seed(42)
    embeddings = np.random.randn(100, 768).astype("float32")
    
    # We'll make the first 5 cards (travel specialty) very close to a "travel getaway" concept vector
    travel_getaway_concept = np.zeros(768)
    travel_getaway_concept[0] = 5.0
    travel_getaway_concept[1] = 2.0
    
    for i in range(10):
        # Add travel concept signal to descriptions and vectors
        embeddings[i] += travel_getaway_concept
        cards[i].description += " Specializes in travel bookings, weekend hotel getaways, and airline flight redemptions."
        cards[i].categories = ["travel"]
        cards[i].multipliers = {"travel": 4.0, "other": 1.0}
        
    # Build FAISS index
    index = FAIRewardIndex(dimension=768)
    index.build_flat_index(card_ids, embeddings)
    
    # Build feedback loop
    feedback_tracker = FeedbackLoopTracker("app/data/feedback_demo.sqlite")
    feedback_tracker.clear_feedback()
    
    # Rules engine
    rules_engine = BusinessRulesEngine()
    
    # ----------------------------------------------------
    # User state
    user = UserProfile(
        user_id="user_alex",
        name="Alex",
        balance=4200,   # Exactly as shown in the slide
        region="US",
        spending_habits={"travel": 0.40, "dining": 0.30, "grocery": 0.30},
        eligibility_tier="Gold",
        preferences=["weekend getaway", "travel rewards"]
    )
    
    # Step 1: Member says
    print_step(1, "Member Statement", 
               f"Member (Alex) says:\n\"I have {user.balance:,} pts -- suggest a weekend getaway\"")
    
    # Step 2: Bot check balance
    print_step(2, "Invoke check_balance tool", 
               f"Concierge checks points database:\n"
               f"[OK] User balance confirmed: {user.balance:,} points available.")
    
    # Step 3: Vector search + Filtering
    # Represent query "weekend getaway"
    query_vector = np.zeros(768)
    query_vector[0] = 4.5
    query_vector[1] = 1.8
    query_vector += np.random.randn(768) * 0.1 # slight noise
    
    # Search nearest 10 cards in FAISS
    retrieved_results = index.search(query_vector, k=15)
    retrieved_cards = [cards[int(cid.split("_")[1])] for cid, _ in retrieved_results]
    
    # Strict filter applied: cost <= 4200, region matches, eligible tier
    filtered_results = rules_engine.run_filtering_pipeline(retrieved_cards, user)
    
    passed_strict = [item[0].name for item in filtered_results if not item[1]]
    
    print_step(3, "Search Catalog & Filter Rewards <= 4200 pts", 
               f"[FAISS] Retrieved nearest semantic card matches.\n"
               f"[RULES] Applied Business Rules (Region: {user.region}, Max Cost: {user.balance} pts, Min Tier: {user.eligibility_tier})\n\n"
               f"Passed Strict Filters:\n" + "\n".join([f"  - {name}" for name in passed_strict]))
    
    # Step 4: Get History & Category Multipliers
    category_affinity, disliked = feedback_tracker.get_user_affinity(user.user_id)
    # Mock some history: user liked travel categories in previous search
    feedback_tracker.log_feedback(user.user_id, "card_00002", "like", ["travel"])
    category_affinity, disliked = feedback_tracker.get_user_affinity(user.user_id)
    
    print_step(4, "Rank by Past Redemption Affinity & multipliers", 
               f"Feedback history loaded for user: {user.user_id}\n"
               f"  - User category affinity weights: {category_affinity}\n"
               f"  - User spending category multipliers combined with vector similarity.")
    
    # Step 5: Presents top 3 picks
    sim_map = {cid: sim for cid, sim in retrieved_results}
    top_picks = ReRanker.re_rank(
        candidates=filtered_results,
        similarity_map=sim_map,
        user=user,
        category_affinity=category_affinity,
        disliked_card_ids=disliked,
        top_n=3
    )
    
    picks_str = ""
    for idx, pick in enumerate(top_picks):
        card = pick["card"]
        picks_str += f"\n* PICK #{idx+1}: {card.name}\n"
        picks_str += f"   - Points Cost: {card.points_cost:,} pts\n"
        picks_str += f"   - Similarity Score: {pick['similarity_score']:.4f} | Re-ranked Score: {pick['final_score']:.4f}\n"
        picks_str += f"   - Reasons: {', '.join(pick['explanations'])}\n"
        
    print_step(5, "Presents Top 3 Picks in Chat", 
               f"Concierge Recommendation response:\n"
               f"\"Here are your top weekend getaway options under 4,200 points:\"" + picks_str)
    
    # Step 6: Member selects one and executes redemption
    selected_pick = top_picks[0]["card"]
    new_balance = user.balance - selected_pick.points_cost
    
    # Log the application to feed the weights
    feedback_tracker.log_feedback(user.user_id, selected_pick.card_id, "apply", selected_pick.categories)
    
    print_step(6, "Member selects one & Executes Redemption", 
               f"User selects: {selected_pick.name} ({selected_pick.points_cost:,} pts)\n"
               f"Execute Redemption API called:\n"
               f"  - Points deducted: -{selected_pick.points_cost:,} pts\n"
               f"  - Remaining balance: {new_balance:,} pts\n"
               f"  - Feedback Loop logged action 'apply' to reinforce category '{selected_pick.categories}' affinity.\n\n"
               f"=== REDEMPTION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
