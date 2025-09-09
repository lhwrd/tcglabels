from typing import Sequence

from tcgdexsdk import Query, TCGdex
from tcgdexsdk.models.Card import Card


async def search_cards(form_data) -> Sequence[Card]:
    sdk = TCGdex()
    response = []
    if form_data.get("name"):
        response = await sdk.card.list(Query().contains("name", form_data["name"]))

    cards = [
        card
        for card in [await card.get_full_card() for card in response]
        if card is not None
    ]
    return cards
