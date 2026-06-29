from typing import List, Tuple, Dict
from app.config import MIN_RECOMMENDATIONS
from app.data_store import RewardCard, UserProfile

class BusinessRulesEngine:
    TIER_ORDER = {"None": 0, "Gold": 1, "Platinum": 2}

    @classmethod
    def is_tier_eligible(cls, user_tier: str, card_tier: str) -> bool:
        """Check if user tier is equal to or higher than the card's required tier."""
        u_val = cls.TIER_ORDER.get(user_tier, 0)
        c_val = cls.TIER_ORDER.get(card_tier, 0)
        return u_val >= c_val

    @classmethod
    def matches_region(cls, user_region: str, card_region: str) -> bool:
        """Check if card is available in user's region or globally."""
        if card_region == "GLOBAL":
            return True
        return user_region == card_region

    def filter_strict(self, cards: List[RewardCard], user: UserProfile) -> List[RewardCard]:
        """Apply strict filtering where all business rules must pass."""
        passed_cards = []
        for card in cards:
            # Check availability
            if not card.is_available:
                continue
            # Check points cost
            if card.points_cost > user.balance:
                continue
            # Check region
            if not self.matches_region(user.region, card.region):
                continue
            # Check eligibility tier
            if not self.is_tier_eligible(user.eligibility_tier, card.eligibility_tier):
                continue
                
            passed_cards.append(card)
        return passed_cards

    def filter_relaxed(self, cards: List[RewardCard], user: UserProfile) -> List[Tuple[RewardCard, List[str]]]:
        """
        Run relaxed filtering where cards are annotated with warning flags if they fail a rule,
        allowing them to be shown as near-misses.
        Returns: List of (RewardCard, List[warning_flags])
        """
        annotated_cards = []
        for card in cards:
            if not card.is_available:
                continue
                
            flags = []
            
            # Points check flag
            if card.points_cost > user.balance:
                flags.append("insufficient_points")
                
            # Region check flag
            if not self.matches_region(user.region, card.region):
                flags.append("region_mismatch")
                
            # Tier check flag
            if not self.is_tier_eligible(user.eligibility_tier, card.eligibility_tier):
                flags.append("tier_upgrade_required")
                
            # Add card even if it has flags, as long as it's not completely blocked
            annotated_cards.append((card, flags))
            
        return annotated_cards

    def run_filtering_pipeline(
        self, cards: List[RewardCard], user: UserProfile
    ) -> List[Tuple[RewardCard, List[str]]]:
        """
        Run the filtering pipeline. If strict results are sufficient, return them.
        Otherwise, fall back to relaxed results and sort them so that cards with fewer
        warnings or easier-to-fix warnings are preferred.
        """
        strict_passed = self.filter_strict(cards, user)
        
        # If we have enough recommendations, wrap them with empty flag lists
        if len(strict_passed) >= MIN_RECOMMENDATIONS:
            return [(card, []) for card in strict_passed]
            
        print(f"Strict filtering returned only {len(strict_passed)} cards (threshold is {MIN_RECOMMENDATIONS}). Activating relaxed fallback rules.")
        
        # Get all cards with flags
        relaxed_results = self.filter_relaxed(cards, user)
        
        # Sort relaxed results so that:
        # 1. Cards with 0 flags (strict passes) are first
        # 2. Cards with fewer warning flags are next
        # 3. Priority of warnings: tier upgrade is easier (can upgrade status) than insufficient points (cannot redeem)
        def sort_key(item: Tuple[RewardCard, List[str]]):
            flags = item[1]
            card = item[0]
            # Score penalty based on flags
            penalty = 0
            if "region_mismatch" in flags:
                penalty += 1000  # Harder mismatch
            if "insufficient_points" in flags:
                # Penalty scales with how much they are short
                excess_ratio = card.points_cost / max(1, user.balance)
                penalty += 100 * excess_ratio
            if "tier_upgrade_required" in flags:
                penalty += 10  # Easiest to resolve
            return (len(flags), penalty)
            
        relaxed_results.sort(key=sort_key)
        return relaxed_results
