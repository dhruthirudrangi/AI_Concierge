from app.db.mongo import cards_collection


def filter_eligible_cards(min_balance, region):

    cards = list(cards_collection.find())

    eligible_cards = []

    for card in cards:

        if not card["active"]:
            continue

        if card["region"].lower() != region.lower():
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