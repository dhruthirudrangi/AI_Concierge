from pymongo import MongoClient
import json
from bson import ObjectId

# Handle MongoDB ObjectIds for JSON serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def fetch_cards():
    print("Connecting to MongoDB at mongodb://localhost:27017/...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["credit_card_recommendation"]
    collection = db["cards"]
    
    total_cards = collection.count_documents({})
    print(f"Found {total_cards} cards in the database.")
    
    # Fetch first 3 cards to display
    cards = list(collection.find().limit(3))
    
    for card in cards:
        # Don't print the huge description_embedding array
        if "description_embedding" in card:
            card["description_embedding"] = f"[{len(card['description_embedding'])} dimensions]"
            
    print("\n--- Sample Cards from Database ---")
    print(json.dumps(cards, indent=2, cls=JSONEncoder))
    
if __name__ == "__main__":
    fetch_cards()
