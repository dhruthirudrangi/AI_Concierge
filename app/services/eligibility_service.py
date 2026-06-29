from app.db.mongo import cards_collection


def filter_eligible_cards(min_balance, region):

    cards = list(cards_collection.find())

    eligible_cards = []

    for card in cards:

        if not card["active"]:
            continue

        card_region = card.get("region", "").lower()
        pref_region = region.lower()
        
        # Map frontend region to backend region
        if pref_region == "north america":
            pref_region = "usa"
        elif pref_region == "asia pacific":
            pref_region = "asia"
            
        if card_region != pref_region and card_region != "global":
            continue

        if min_balance < card["min_balance_required"]:
            continue

        eligible_cards.append(card)

    return eligible_cards


def calculate_card_score(card, spending_categories):

    score = 0

    for category, amount in spending_categories.items():

        if category.lower() in card["preferred_categories"]:
            score += amount * 0.0001

    return round(score, 2)