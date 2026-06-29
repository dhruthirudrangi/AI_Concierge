"""
Dynamic Card Addition Script
Easy ways to add new credit cards to the system
"""

from app.db.mongo import cards_collection
from app.services.semantic_service import EmbeddingService


def add_single_card(
    card_id: str,
    name: str,
    description: str,
    min_balance_required: float,
    region: str,
    preferred_categories: list,
    active: bool = True
) -> dict:
    """
    Add a single credit card to the database with auto-generated embeddings
    
    Args:
        card_id: Unique card identifier (e.g., "CARD008")
        name: Card name/title
        description: Detailed card description (used for semantic matching)
        min_balance_required: Minimum account balance to get this card
        region: Geographic region (e.g., "India", "USA")
        preferred_categories: List of spending categories (e.g., ["shopping", "dining"])
        active: Whether card is currently available
    
    Returns:
        Dictionary with operation status
    
    Example:
        add_single_card(
            card_id="CARD008",
            name="Student Rewards Card",
            description="Special student card with discounts on educational materials...",
            min_balance_required=1000,
            region="India",
            preferred_categories=["education", "books", "shopping"]
        )
    """
    
    # Check if card already exists
    existing = cards_collection.find_one({"card_id": card_id})
    if existing:
        return {"error": f"Card {card_id} already exists", "status": "failed"}
    
    # Generate embedding for semantic matching
    print(f"🔄 Generating embedding for: {name}")
    embedding = EmbeddingService.encode(description)
    
    # Create card document
    card_doc = {
        "card_id": card_id,
        "name": name,
        "description": description,
        "min_balance_required": min_balance_required,
        "region": region,
        "preferred_categories": preferred_categories,
        "active": active,
        "description_embedding": embedding.tolist()
    }
    
    # Insert into MongoDB
    result = cards_collection.insert_one(card_doc)
    
    return {
        "status": "success",
        "card_id": card_id,
        "name": name,
        "message": f"✅ Card '{name}' added successfully!",
        "inserted_id": str(result.inserted_id)
    }


def add_multiple_cards(cards_list: list) -> dict:
    """
    Add multiple credit cards at once
    
    Args:
        cards_list: List of card dictionaries with fields:
            - card_id, name, description, min_balance_required, region, preferred_categories
    
    Returns:
        Summary of added cards
    
    Example:
        cards = [
            {
                "card_id": "CARD009",
                "name": "Gym Card",
                "description": "Get rewards on gym memberships...",
                "min_balance_required": 5000,
                "region": "India",
                "preferred_categories": ["fitness", "health"]
            },
            {
                "card_id": "CARD010",
                "name": "Pet Lover Card",
                "description": "Perfect for pet owners...",
                "min_balance_required": 5000,
                "region": "India",
                "preferred_categories": ["pets", "healthcare"]
            }
        ]
        
        result = add_multiple_cards(cards)
    """
    
    added_cards = []
    failed_cards = []
    
    for card in cards_list:
        result = add_single_card(
            card_id=card["card_id"],
            name=card["name"],
            description=card["description"],
            min_balance_required=card["min_balance_required"],
            region=card["region"],
            preferred_categories=card["preferred_categories"],
            active=card.get("active", True)
        )
        
        if result["status"] == "success":
            added_cards.append(result)
            print(f"✅ {result['message']}")
        else:
            failed_cards.append(result)
            print(f"❌ {result['error']}")
    
    return {
        "total_requested": len(cards_list),
        "added": len(added_cards),
        "failed": len(failed_cards),
        "added_cards": added_cards,
        "failed_cards": failed_cards
    }


def update_card(card_id: str, updates: dict) -> dict:
    """
    Update an existing card
    
    Args:
        card_id: Card ID to update
        updates: Dictionary of fields to update
        
    Returns:
        Operation status
    
    Example:
        update_card("CARD001", {
            "name": "New Card Name",
            "min_balance_required": 20000
        })
    """
    
    # Check if card exists
    existing = cards_collection.find_one({"card_id": card_id})
    if not existing:
        return {"error": f"Card {card_id} not found", "status": "failed"}
    
    # If description is being updated, regenerate embedding
    if "description" in updates:
        print(f"🔄 Regenerating embedding for updated description")
        embedding = EmbeddingService.encode(updates["description"])
        updates["description_embedding"] = embedding.tolist()
    
    result = cards_collection.update_one(
        {"card_id": card_id},
        {"$set": updates}
    )
    
    return {
        "status": "success",
        "card_id": card_id,
        "modified_count": result.modified_count,
        "message": f"✅ Card {card_id} updated successfully!"
    }


def delete_card(card_id: str) -> dict:
    """
    Delete a card from the database
    
    Args:
        card_id: Card ID to delete
    
    Returns:
        Operation status
    
    Example:
        delete_card("CARD001")
    """
    
    result = cards_collection.delete_one({"card_id": card_id})
    
    if result.deleted_count == 0:
        return {"error": f"Card {card_id} not found", "status": "failed"}
    
    return {
        "status": "success",
        "card_id": card_id,
        "deleted_count": result.deleted_count,
        "message": f"✅ Card {card_id} deleted successfully!"
    }


def list_all_cards() -> dict:
    """Get all cards in the database with their details"""
    
    cards = list(cards_collection.find({}, {
        "card_id": 1,
        "name": 1,
        "region": 1,
        "min_balance_required": 1,
        "preferred_categories": 1,
        "active": 1
    }))
    
    return {
        "total_cards": len(cards),
        "cards": cards
    }


def search_cards(query: str) -> dict:
    """
    Search cards by name or description (text search)
    
    Args:
        query: Search query
    
    Returns:
        Matching cards
    """
    
    results = list(cards_collection.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }))
    
    return {
        "query": query,
        "total_matches": len(results),
        "results": results
    }


def get_cards_by_region(region: str) -> dict:
    """Get all active cards available in a specific region"""
    
    cards = list(cards_collection.find({
        "region": {"$regex": region, "$options": "i"},
        "active": True
    }))
    
    return {
        "region": region,
        "total_cards": len(cards),
        "cards": cards
    }


def get_cards_by_balance(max_balance: float) -> dict:
    """Get all active cards eligible for a specific balance"""
    
    cards = list(cards_collection.find({
        "min_balance_required": {"$lte": max_balance},
        "active": True
    }).sort("min_balance_required", 1))
    
    return {
        "user_balance": max_balance,
        "eligible_cards": len(cards),
        "cards": cards
    }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    
    print("\n" + "="*60)
    print("CREDIT CARD MANAGEMENT - EXAMPLES")
    print("="*60 + "\n")
    
    # Example 1: Add single card
    print("1️⃣  Adding a single card...")
    result = add_single_card(
        card_id="CARD008",
        name="Student Rewards Card",
        description="Special student card with discounts on educational materials, books, online courses, and college canteen purchases.",
        min_balance_required=1000,
        region="India",
        preferred_categories=["education", "books", "shopping"]
    )
    print(result)
    print()
    
    # Example 2: Add multiple cards
    print("2️⃣  Adding multiple cards...")
    new_cards = [
        {
            "card_id": "CARD009",
            "name": "Gym & Wellness Card",
            "description": "Get rewards on gym memberships, yoga classes, health insurance, and wellness app subscriptions.",
            "min_balance_required": 5000,
            "region": "India",
            "preferred_categories": ["fitness", "health", "wellness"]
        },
        {
            "card_id": "CARD010",
            "name": "Pet Lover Card",
            "description": "Perfect for pet owners. Get cashback on pet food, vet services, pet insurance, and pet grooming.",
            "min_balance_required": 5000,
            "region": "India",
            "preferred_categories": ["pets", "animals", "healthcare"]
        },
        {
            "card_id": "CARD011",
            "name": "Green Energy Card",
            "description": "Support green living with rewards on electric vehicle charging, renewable energy investments, and eco-friendly purchases.",
            "min_balance_required": 10000,
            "region": "India",
            "preferred_categories": ["eco", "electric", "sustainability"]
        }
    ]
    
    result = add_multiple_cards(new_cards)
    print(f"\n📊 Summary: Added {result['added']}/{result['total_requested']} cards")
    print()
    
    # Example 3: List all cards
    print("3️⃣  Listing all cards...")
    all_cards = list_all_cards()
    print(f"Total cards in database: {all_cards['total_cards']}")
    for card in all_cards['cards'][:3]:  # Show first 3
        print(f"  - {card['name']} (Region: {card['region']})")
    print()
    
    # Example 4: Search cards
    print("4️⃣  Searching for 'Cashback' cards...")
    search_results = search_cards("Cashback")
    print(f"Found {search_results['total_matches']} matching cards")
    print()
    
    # Example 5: Get cards by region
    print("5️⃣  Cards available in India...")
    india_cards = get_cards_by_region("India")
    print(f"Available: {india_cards['total_cards']} cards")
    print()
    
    # Example 6: Get cards by balance
    print("6️⃣  Cards eligible for ₹25,000 balance...")
    eligible = get_cards_by_balance(25000)
    print(f"Eligible cards: {eligible['eligible_cards']}")
    print()
    
    # Example 7: Update card
    print("7️⃣  Updating a card...")
    if all_cards['total_cards'] > 0:
        card_to_update = all_cards['cards'][0]['card_id']
        update_result = update_card(card_to_update, {
            "min_balance_required": 20000
        })
        print(update_result)
    print()
    
    print("="*60)
    print("✅ All examples completed!")
    print("="*60 + "\n")
