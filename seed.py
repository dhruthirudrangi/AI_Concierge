import sys
from sentence_transformers import SentenceTransformer
from app.db.mongo import cards_collection

print("Loading Sentence Transformer model 'all-MiniLM-L6-v2'...")
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

import json

print("Loading cards from credit_card_recommendation.cards.json...")
try:
    with open("credit_card_recommendation.cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except FileNotFoundError:
    print("Error: credit_card_recommendation.cards.json not found!")
    sys.exit(1)

# Remove the MongoDB ObjectId from the exported JSON so they get new IDs or are inserted cleanly
for card in cards:
    if "_id" in card:
        del card["_id"]

print("Clearing collection and inserting new cards into MongoDB...")
cards_collection.delete_many({})
if cards:
    cards_collection.insert_many(cards)


print("Cards successfully seeded with embeddings!")