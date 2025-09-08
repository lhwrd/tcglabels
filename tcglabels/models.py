import reflex as rx


class Card(rx.Model):
    name: str
    set_name: str
    rarity: str
    number: str  # Unique identifier
    finish: str
