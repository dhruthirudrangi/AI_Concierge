import json
import os
import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.config import CARDS_DB_PATH, PROFILES_DB_PATH, EMBEDDING_DIM

class RewardCard(BaseModel):
    card_id: str = Field(..., description="Unique identifier for the card")
    name: str = Field(..., description="Name of the reward card")
    issuer: str = Field(..., description="Bank or corporate issuer of the card")
    description: str = Field(..., description="Text description for embedding representation")
    points_cost: int = Field(0, description="Points cost required for redemption or enrollment")
    region: str = Field("GLOBAL", description="Regional availability, e.g., US, EU, GLOBAL")
    categories: List[str] = Field(default_factory=list, description="Categories this card specializes in")
    multipliers: Dict[str, float] = Field(default_factory=dict, description="Reward multipliers per category (e.g. 5x on travel)")
    eligibility_tier: str = Field("None", description="Membership tier required (None, Gold, Platinum)")
    is_available: bool = Field(True, description="Availability flag")
    partnership_benefits: List[str] = Field(default_factory=list, description="Special perks like lounge access or statement credits")
    terms: str = Field("", description="Terms and conditions summary")

class UserProfile(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    name: str = Field(..., description="User's name")
    balance: int = Field(0, description="Current points/balance available")
    region: str = Field("US", description="User's geographic region")
    spending_habits: Dict[str, float] = Field(default_factory=dict, description="Category spend shares (sum to ~1.0)")
    eligibility_tier: str = Field("None", description="User's membership tier (None, Gold, Platinum)")
    preferences: List[str] = Field(default_factory=list, description="General interest keywords or preferences")

class JSONDataStore:
    def __init__(self, cards_path: str = CARDS_DB_PATH, profiles_path: str = PROFILES_DB_PATH):
        self.cards_path = cards_path
        self.profiles_path = profiles_path
        self.cards: Dict[str, RewardCard] = {}
        self.profiles: Dict[str, UserProfile] = {}
        self.load_all()

    def load_all(self):
        # Load Cards
        if os.path.exists(self.cards_path):
            try:
                with open(self.cards_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cards = {item["card_id"]: RewardCard(**item) for item in data}
            except Exception as e:
                print(f"Error loading cards DB: {e}")
        
        # Load Profiles
        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.profiles = {item["user_id"]: UserProfile(**item) for item in data}
            except Exception as e:
                print(f"Error loading profiles DB: {e}")

    def save_cards(self):
        try:
            with open(self.cards_path, "w", encoding="utf-8") as f:
                json.dump([card.model_dump() for card in self.cards.values()], f, indent=2)
        except Exception as e:
            print(f"Error saving cards DB: {e}")

    def save_profiles(self):
        try:
            with open(self.profiles_path, "w", encoding="utf-8") as f:
                json.dump([profile.model_dump() for profile in self.profiles.values()], f, indent=2)
        except Exception as e:
            print(f"Error saving profiles DB: {e}")

    def get_card(self, card_id: str) -> Optional[RewardCard]:
        return self.cards.get(card_id)

    def get_all_cards(self) -> List[RewardCard]:
        return list(self.cards.values())

    def add_card(self, card: RewardCard):
        self.cards[card.card_id] = card
        self.save_cards()

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.profiles.get(user_id)

    def get_all_profiles(self) -> List[UserProfile]:
        return list(self.profiles.values())

    def add_profile(self, profile: UserProfile):
        self.profiles[profile.user_id] = profile
        self.save_profiles()


def generate_mock_cards(count: int = 100) -> List[RewardCard]:
    issuers = ["Apex Card Services", "Global Horizon Bank", "Vanguard Rewards", "Prestige Financial", "Summit Trust"]
    categories = ["travel", "dining", "grocery", "shopping", "entertainment", "gas", "utilities"]
    regions = ["US", "EU", "GLOBAL"]
    tiers = ["None", "Gold", "Platinum"]
    
    perks_pool = [
        "Airport VIP lounge access across 1200+ airports globally",
        "Complimentary high-speed WiFi at select partner locations",
        "No foreign transaction fees on international spend",
        "24/7 personal travel concierge service assistance",
        "$200 annual statement credit for airline baggage fees",
        "10% statement discount on co-branded dining partners",
        "Free premium insurance coverage for rental cars",
        "Extended warranty protection on electronics purchases",
        "Complimentary upgrade to premium rental tier",
        "Double rewards points on selected anniversary month spend"
    ]
    
    desc_templates = [
        "A premium {category} and {second_category} reward card designed for {tier} tier members. Offers high rewards multipliers on all standard spending, especially for {category} purchases.",
        "Perfect for daily expenses, this card focuses on {category} and {second_category} rebates. Get up to {mult}x points on qualifying transactions.",
        "An elite rewards card providing unmatched luxury perks including {perk_short}. Maximize your benefits on {category} with exclusive {tier} benefits.",
        "The ultimate lifestyle companion card with high multipliers on {category}. Packed with benefits such as {perk_short} and low points redemption threshold.",
        "Value-driven card offering simple flat-rate points on {second_category} and high multipliers on {category}. No annual fees and immediate activation."
    ]

    cards = []
    random.seed(42)  # For deterministic generation in testing

    for i in range(count):
        card_id = f"card_{i:05d}"
        issuer = random.choice(issuers)
        cat1 = random.choice(categories)
        # pick a different category
        cat2 = random.choice([c for c in categories if c != cat1])
        tier = random.choices(tiers, weights=[0.6, 0.3, 0.1], k=1)[0]
        region = random.choices(regions, weights=[0.7, 0.2, 0.1], k=1)[0]
        
        perks = random.sample(perks_pool, k=random.randint(1, 3))
        perk_short = perks[0].split(" at ")[0].split(" for ")[0].lower()
        
        # points cost to redeem/activate the card
        # Travel/Premium cards cost more points. None = low cost, Gold = mid cost, Platinum = high cost.
        if tier == "Platinum":
            points_cost = random.randint(5000, 15000)
        elif tier == "Gold":
            points_cost = random.randint(1500, 5000)
        else:
            points_cost = random.randint(0, 1500)

        # Let's adjust points cost based on categories: travel cards are premium
        if "travel" in [cat1, cat2]:
            points_cost += 1000

        mult1 = round(random.uniform(2.0, 5.0), 1)
        mult2 = round(random.uniform(1.5, 3.0), 1)
        multipliers = {cat1: mult1, cat2: mult2}
        
        # Add a flat rate for others
        multipliers["other"] = 1.0

        description = random.choice(desc_templates).format(
            category=cat1,
            second_category=cat2,
            tier=tier,
            mult=mult1,
            perk_short=perk_short
        )
        
        # append issuer details to description for semantic matching
        full_description = f"{issuer} {card_id}: {description}. Special perks: {', '.join(perks)}."
        
        card = RewardCard(
            card_id=card_id,
            name=f"{issuer} {cat1.capitalize()} {tier if tier != 'None' else 'Classic'}",
            issuer=issuer,
            description=full_description,
            points_cost=points_cost,
            region=region,
            categories=[cat1, cat2],
            multipliers=multipliers,
            eligibility_tier=tier,
            is_available=True,
            partnership_benefits=perks,
            terms=f"Subject to terms. Standard cash-back value of 1 cent per point. Annual fee may apply based on {tier} tier rules."
        )
        cards.append(card)

    return cards


def generate_mock_profiles() -> List[UserProfile]:
    return [
        UserProfile(
            user_id="user_frequent_traveler",
            name="Alex Morgan",
            balance=12000,
            region="US",
            spending_habits={"travel": 0.50, "dining": 0.30, "grocery": 0.10, "shopping": 0.10},
            eligibility_tier="Platinum",
            preferences=["luxury lounges", "airline credits", "flight rewards", "premium travel benefits"]
        ),
        UserProfile(
            user_id="user_foodie",
            name="Chef Chris",
            balance=4200,
            region="US",
            spending_habits={"dining": 0.60, "grocery": 0.30, "shopping": 0.10},
            eligibility_tier="Gold",
            preferences=["restaurant cash back", "dining discounts", "food delivery", "groceries rewards"]
        ),
        UserProfile(
            user_id="user_student_saver",
            name="Sam Taylor",
            balance=800,
            region="EU",
            spending_habits={"grocery": 0.40, "shopping": 0.30, "utilities": 0.20, "gas": 0.10},
            eligibility_tier="None",
            preferences=["no annual fee", "cash back shopping", "basic credit", "student discounts"]
        ),
        UserProfile(
            user_id="user_global_exec",
            name="Elena Rostova",
            balance=25000,
            region="GLOBAL",
            spending_habits={"travel": 0.40, "dining": 0.20, "entertainment": 0.20, "shopping": 0.20},
            eligibility_tier="Platinum",
            preferences=["global lounge key", "premium service", "world elite card benefits", "hotel points"]
        )
    ]
