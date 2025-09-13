from typing import Sequence

from tcgdexsdk import Query, TCGdex

from .models import Card


async def search_cards(form_data) -> Sequence[Card]:
    sdk = TCGdex()
    query = Query()
    response = []
    if form_data.get("name"):
        query = query.contains("name", form_data["name"])

    if form_data.get("set_name"):
        query = query.contains("set.name", form_data["set_name"])

    if form_data.get("rarity"):
        query = query.contains("rarity", form_data["rarity"])

    if form_data.get("id"):
        query = query.contains("id", form_data["id"])

    if len(query.params) == 0:
        return []

    response += await sdk.card.list(query)

    cards = [
        card
        for card in [await card.get_full_card() for card in response]
        if card is not None
    ]

    # convert TCGCard to our Card model
    # for each true variant, create a new card with the variant
    # name appended to the card name
    extended_cards = []
    for card in cards:
        card_variants = []
        if card.variants.firstEdition:
            card_variants.append("1stEd")
        if card.variants.holo:
            card_variants.append("Holo")
        if card.variants.normal:
            card_variants.append("Normal")
        if card.variants.reverse:
            card_variants.append("RevHolo")
        if card.variants.wPromo:
            card_variants.append("Promo")
        temp_cards = [
            Card(
                number=card.id,
                name=card.name,
                rarity=card.rarity,
                set_name=card.set.name,
                finish=variant,
            )
            for variant in card_variants
        ]
        if len(temp_cards) > 0:
            extended_cards += temp_cards
        else:
            extended_cards.append(
                Card(
                    number=card.id,
                    name=card.name,
                    rarity=card.rarity,
                    set_name=card.set.name,
                    finish="",
                )
            )

    return extended_cards
