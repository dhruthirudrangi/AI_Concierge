import sys
import random
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

# MongoDB Connection
MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["credit_card_recommendation"]
cards_collection = db["cards"]
profiles_collection = db["profiles"]

print("Loading Sentence Transformer model 'all-MiniLM-L6-v2'...")
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# --- 1. Generate 150 Diverse Cards ---
print("Generating 150 diverse cards...")

banks = ["Kobie Bank", "Global Trust", "Apex Financial", "Horizon Credit", "Pioneer Bank", "Nexus Group", "Stellar Bank"]
regions = ["India", "USA", "Global", "Europe", "Asia"]
categories_pool = ["dining", "shopping", "travel", "flights", "fuel", "entertainment", "electronics", "utility", "groceries", "lifestyle"]

benefits_pool = [
    "Complimentary airport lounge access",
    "Zero forex markup",
    "1% fuel surcharge waiver",
    "Free movie tickets on weekends",
    "Concierge service 24x7",
    "Purchase protection and extended warranty",
    "Discounted dining at 5-star hotels",
    "Bonus reward points on milestone spends"
]

cards = []
for i in range(150):
    card_type = random.choice(["Cashback", "Rewards", "Travel", "Fuel", "Elite", "Student", "Shopping"])
    issuer = random.choice(banks)
    name = f"{issuer} {card_type} {random.choice(['Card', 'Plus', 'Infinite', 'Signature'])}"
    
    selected_categories = random.sample(categories_pool, random.randint(1, 3))
    selected_benefits = random.sample(benefits_pool, random.randint(1, 3))
    
    desc_base = f"A premium {card_type.lower()} card by {issuer} focusing on {', '.join(selected_categories)}. "
    desc_benefits = f"Enjoy perks like {', '.join([b.lower() for b in selected_benefits])}."
    
    card = {
        "card_id": f"DIVERSE_{i:03d}",
        "name": name,
        "issuer": issuer,
        "min_balance_required": random.choice([0, 5000, 10000, 25000, 50000, 100000, 250000]),
        "region": random.choice(regions),
        "active": random.choice([True, True, True, False]), # 75% active
        "preferred_categories": selected_categories,
        "description": desc_base + desc_benefits,
        "annual_fee": random.choice([0, 499, 999, 2999, 5000, 10000]),
        "benefits": selected_benefits,
        "apply_url": f"https://example.com/apply/DIVERSE_{i:03d}"
    }
    cards.append(card)

print("Generating description embeddings for cards...")
descriptions = [card["description"] for card in cards]
embeddings = model.encode(descriptions)

for i, card in enumerate(cards):
    card["description_embedding"] = embeddings[i].tolist()

print("Clearing and inserting cards into MongoDB...")
# We don't delete existing seeded cards, we just add these diverse ones to the stream!
cards_collection.delete_many({"card_id": {"$regex": "^DIVERSE_"}}) # remove old diverse ones if rerunning
cards_collection.insert_many(cards)

# --- 2. Generate 5 User Profiles ---
print("Generating 5 user profiles...")
profiles = []
profile_types = [
    ("Frequent Traveler", 150000, ["travel", "flights", "dining"], "Global"),
    ("Student Saver", 5000, ["utility", "groceries", "entertainment"], "India"),
    ("High Net Worth", 1000000, ["lifestyle", "travel", "dining"], "USA"),
    ("Online Shopper", 25000, ["shopping", "electronics"], "Global"),
    ("Daily Commuter", 15000, ["fuel", "utility", "groceries"], "India")
]

for i, p_info in enumerate(profile_types):
    profile = {
        "user_id": f"USER_{i:03d}",
        "name": p_info[0],
        "balance": p_info[1],
        "preferred_categories": p_info[2],
        "region": p_info[3]
    }
    profiles.append(profile)

profiles_collection.delete_many({"user_id": {"$regex": "^USER_"}})
profiles_collection.insert_many(profiles)

print(f"Successfully inserted {len(cards)} diverse cards and {len(profiles)} user profiles into MongoDB!")
