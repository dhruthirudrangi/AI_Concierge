from app.db.mongo import cards_collection

cards = [
    {
        "card_id": "CARD001",
        "name": "Premium Cashback Card",
        "min_balance_required": 10000,
        "region": "India",
        "active": True,
        "preferred_categories": ["dining", "shopping"],
    },
    {
        "card_id": "CARD002",
        "name": "Travel Rewards Card",
        "min_balance_required": 50000,
        "region": "India",
        "active": True,
        "preferred_categories": ["travel", "flights"],
    },
]

cards_collection.delete_many({})

cards_collection.insert_many(cards)

print("Cards inserted successfully")