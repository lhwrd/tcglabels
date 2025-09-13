from dataclasses import dataclass, field
from uuid import uuid4


def generate_uuid() -> str:
    return str(uuid4())


@dataclass
class Card:
    number: str
    name: str
    set_name: str
    rarity: str
    finish: str  # e.g., "Holofoil", "1st Edition", etc.
    unique_id: str = field(default_factory=generate_uuid)
