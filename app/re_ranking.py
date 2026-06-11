from typing import List, Dict, Tuple, Any
from app.config import WEIGHT_SIMILARITY, WEIGHT_MULTIPLIER, WEIGHT_FEEDBACK, DEFAULT_RECOMMENDATION_COUNT
from app.data_store import RewardCard, UserProfile

class ReRanker:
    @staticmethod
    def calculate_multiplier_bonus(user: UserProfile, card: RewardCard) -> float:
        """
        Compute category spending multiplier benefit.
        Sum (User Spend Share * Card Multiplier) for card categories, normalized to [0.0, 1.0].
        Assumes max multiplier is 5.0.
        """
        raw_bonus = 0.0
        # If user has no spending habits, default to equal weights
        user_spend = user.spending_habits
        if not user_spend:
            user_spend = {cat: 1.0 / len(card.categories) for cat in card.categories}
            
        for category, multiplier in card.multipliers.items():
            spend_share = user_spend.get(category, 0.0)
            raw_bonus += spend_share * multiplier
            
        # Normalize assuming max multiplier is 5.0x
        normalized_bonus = raw_bonus / 5.0
        return min(1.0, max(0.0, normalized_bonus))

    @staticmethod
    def calculate_feedback_bonus(category_affinity: Dict[str, float], card: RewardCard) -> float:
        """
        Sum user affinity scores for the card's categories.
        Affinity ranges from [-5.0, 5.0] and is normalized/clamped to [-1.0, 1.0].
        """
        if not category_affinity:
            return 0.0
            
        affinity_sum = 0.0
        # Check card specialized categories
        for cat in card.categories:
            affinity_sum += category_affinity.get(cat, 0.0)
            
        # Standardize score to [-1.0, 1.0] range
        normalized_bonus = affinity_sum / 5.0
        return max(-1.0, min(1.0, normalized_bonus))

    @classmethod
    def generate_explanation(
        cls, 
        card: RewardCard, 
        user: UserProfile, 
        similarity: float, 
        mult_bonus: float, 
        feed_bonus: float, 
        flags: List[str]
    ) -> List[str]:
        """Generate human-readable explanations for why the card was recommended."""
        reasons = []
        
        # 1. Semantic match
        if similarity > 0.75:
            reasons.append("Highly matches your stated search query and preferences.")
        elif similarity > 0.6:
            reasons.append("Good match with your profile description.")
            
        # 2. Spend Category match
        top_user_categories = sorted(user.spending_habits.items(), key=lambda x: x[1], reverse=True)
        if top_user_categories:
            top_cat, top_share = top_user_categories[0]
            if top_cat in card.multipliers and card.multipliers[top_cat] > 1.0:
                reasons.append(
                    f"Earns {card.multipliers[top_cat]}x on {top_cat.capitalize()}, aligning with your highest spend share ({int(top_share * 100)}%)."
                )
                
        # 3. Feedback match
        if feed_bonus > 0.2:
            reasons.append("Matches your previously liked rewards categories.")
            
        # 4. Warnings/Flags annotation
        if "insufficient_points" in flags:
            points_diff = card.points_cost - user.balance
            reasons.append(f"Requires {card.points_cost:,} points (you are short by {points_diff:,} points).")
        if "tier_upgrade_required" in flags:
            reasons.append(f"Requires {card.eligibility_tier} tier membership (current: {user.eligibility_tier}).")
        if "region_mismatch" in flags:
            reasons.append(f"Note: This card is localized for region {card.region} (your region: {user.region}).")
            
        return reasons

    @classmethod
    def re_rank(
        cls,
        candidates: List[Tuple[RewardCard, List[str]]],  # Outputs from BusinessRulesEngine: (card, flags)
        similarity_map: Dict[str, float],               # card_id -> similarity score
        user: UserProfile,
        category_affinity: Dict[str, float],
        disliked_card_ids: set,
        top_n: int = DEFAULT_RECOMMENDATION_COUNT
    ) -> List[Dict[str, Any]]:
        """
        Rank candidate cards and build detailed recommendations.
        FinalScore = w_sim * Similarity + w_mult * MultiplierBonus + w_feed * FeedbackBonus - Penalties
        """
        ranked_results = []

        for card, flags in candidates:
            # Exclude card if explicitly disliked
            if card.card_id in disliked_card_ids:
                continue

            similarity = similarity_map.get(card.card_id, 0.0)
            mult_bonus = cls.calculate_multiplier_bonus(user, card)
            feed_bonus = cls.calculate_feedback_bonus(category_affinity, card)

            # Apply rule warning penalties
            penalties = 0.0
            if "region_mismatch" in flags:
                penalties += 0.5
            if "insufficient_points" in flags:
                penalties += 0.3
            if "tier_upgrade_required" in flags:
                penalties += 0.1

            # Combined scoring
            final_score = (
                WEIGHT_SIMILARITY * similarity +
                WEIGHT_MULTIPLIER * mult_bonus +
                WEIGHT_FEEDBACK * feed_bonus -
                penalties
            )

            # Normalize final score between 0.0 and 1.0 (or clamp it)
            final_score = max(0.0, min(1.0, final_score))

            explanations = cls.generate_explanation(card, user, similarity, mult_bonus, feed_bonus, flags)

            ranked_results.append({
                "card": card,
                "similarity_score": round(similarity, 4),
                "multiplier_bonus": round(mult_bonus, 4),
                "feedback_bonus": round(feed_bonus, 4),
                "final_score": round(final_score, 4),
                "warning_flags": flags,
                "explanations": explanations
            })

        # Sort by final score descending, and resolve ties using similarity
        ranked_results.sort(key=lambda x: (x["final_score"], x["similarity_score"]), reverse=True)

        return ranked_results[:top_n]
