import random
from uuid import uuid4

import reflex as rx
from reflex.vars import BooleanVar

from ..label_generator import Font, LabelGenerator
from ..models import Card
from ..template import template


class LabelSettingsState(rx.State):
    label_size: rx.Field[str] = rx.field(default='Medium (3"x2")')
    font: rx.Field[str] = rx.field(default="Arial")

    @rx.var
    def label_dimensions(self) -> tuple[int, int]:
        size_map = {
            '1.2"x0.8"': (360, 240),
            '1.5"x0.5"': (450, 150),
            '2.0"x1.0"': (600, 300),
            '2.25"x1.5"': (675, 450),
        }
        return size_map.get(
            self.label_size, (300, 200)
        )  # Default to Medium if not found

    @rx.event
    def set_label_size(self, size: str) -> None:
        self.label_size = size

    @rx.var
    def font_enum(self) -> Font:
        font_map = {
            "Arial": Font.ARIAL,
            "Opensans": Font.OPENSANS,
            "Opensans Bold": Font.OPENSANS_BOLD,
        }
        return font_map.get(self.font, Font.ARIAL)  # Default to ARIAL if not found

    @rx.event
    def set_font(self, font: str) -> None:
        self.font = font


class CardsTableState(rx.State):
    cards: rx.Field[list[Card]] = rx.field(
        default_factory=list
    )  # List of card instances
    selected_card_numbers: rx.Field[list[str]] = rx.field(
        default_factory=list
    )  # List of selected card numbers (unique id)

    @rx.event
    def search_cards(self, form_data: dict) -> None:
        """Search for cards based on form data and update the state."""
        # Example: populate with dicts
        self.cards = [
            Card(
                name="Pikachu",
                set_name="Base Set",
                rarity="Common",
                number="58",
                finish="Holo",
            ),
            Card(
                name="Charizard",
                set_name="Base Set",
                rarity="Rare",
                number="4",
                finish="Holo",
            ),
            Card(
                name="Bulbasaur",
                set_name="Base Set",
                rarity="Common",
                number="1",
                finish="Non-Holo",
            ),
        ]
        self.selected_card_numbers = []

    @rx.event
    def toggle_all_selected(self) -> None:
        """Toggle selection state of all cards."""
        if len(self.selected_card_numbers) == len(self.cards):
            self.selected_card_numbers = []
        else:
            self.selected_card_numbers = [card.number for card in self.cards]

    @rx.var
    def all_selected(self) -> bool:
        return (
            len(self.selected_card_numbers) == len(self.cards) and len(self.cards) > 0
        )

    @rx.var
    def any_selected(self) -> bool:
        return len(self.selected_card_numbers) > 0

    @rx.var
    def indeterminate(self) -> bool:
        return self.any_selected and not self.all_selected

    @rx.event
    def toggle_card_selected(self, number: str) -> None:
        if number in self.selected_card_numbers:
            self.selected_card_numbers.remove(number)
        else:
            self.selected_card_numbers.append(number)

    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_card_numbers)

    @rx.event
    async def generate_labels(self):
        """Generate labels for selected cards."""
        selected_cards = [
            card for card in self.cards if card.number in self.selected_card_numbers
        ]
        size = await self.get_var_value(LabelSettingsState.label_dimensions)
        font = await self.get_var_value(LabelSettingsState.font_enum)
        generator = LabelGenerator(size=size, font=font)
        guid = uuid4()
        data = generator.generate_labels_pdf_bytes(cards=selected_cards)
        return rx.download(data=data, filename=f"labels_{guid}.pdf")

    @rx.event
    def download_random_data(self):
        return rx.download(
            data=",".join([str(random.randint(0, 100)) for _ in range(10)]),
            filename="random_numbers.csv",
        )


def search_form() -> rx.Component:
    # Search Form Component
    return rx.form(
        rx.hstack(
            rx.input(placeholder="Card Name", name="name"),
            rx.input(placeholder="Set Name", name="set_name"),
            rx.input(placeholder="Rarity", name="rarity"),
            rx.input(placeholder="Number", name="number"),
            rx.input(placeholder="Finish", name="finish"),
            rx.button("Search", type="submit"),
            spacing="4",
        ),
        on_submit=CardsTableState.search_cards,
        padding="4",
    )


def dynamic_select_icon(selected: bool | BooleanVar):
    return rx.match(
        selected,
        (True, rx.icon("check")),
        (False, rx.icon("circle")),
    )


def show_card_row(card: Card) -> rx.Component:
    selected = CardsTableState.selected_card_numbers.contains(card.number)

    return rx.table.row(
        rx.table.cell(
            rx.icon_button(
                dynamic_select_icon(selected),
                color_scheme=rx.cond(selected, "blue", "gray"),
                on_click=lambda: CardsTableState.toggle_card_selected(
                    number=card.number
                ),
            )
        ),
        rx.table.row_header_cell(card.name),
        rx.table.cell(card.set_name),
        rx.table.cell(card.rarity),
        rx.table.cell(card.number),
        rx.table.cell(card.finish),
    )


def select_all_checkbox() -> rx.Component:
    return rx.icon_button(
        dynamic_select_icon(CardsTableState.all_selected),
        color_scheme=rx.cond(CardsTableState.all_selected, "blue", "gray"),
        on_click=CardsTableState.toggle_all_selected,
        aria_label="Select All",
    )


def search_results() -> rx.Component:
    # Search Results Component
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(select_all_checkbox()),
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Set Name"),
                    rx.table.column_header_cell("Rarity"),
                    rx.table.column_header_cell("Number"),
                    rx.table.column_header_cell("Finish"),
                )
            ),
            rx.table.body(
                rx.foreach(CardsTableState.cards, show_card_row),
            ),
            width="100%",
        ),
        margin_top="4",
        width="100%",
    )


def search_config() -> rx.Component:
    return rx.box(
        rx.form(
            rx.hstack(
                rx.hstack(
                    rx.text("Label Size"),
                    rx.select(
                        ['1.2"x0.8"', '1.5"x0.5"', '2.0"x1.0"', '2.25"x1.5"'],
                        name="label_size",
                        default_value='1.5"x0.5"',
                        width="200px",
                        on_change=LabelSettingsState.set_label_size,
                    ),
                    align="center",
                ),
                rx.hstack(
                    rx.text("Font"),
                    rx.select(
                        ["Arial", "Opensans", "Opensans Bold"],
                        name="font",
                        default_value="Arial",
                        width="200px",
                        on_change=LabelSettingsState.set_font,
                    ),
                    align="center",
                ),
                rx.button(
                    f"Generate Labels for {CardsTableState.selected_count} Cards",
                    disabled=~CardsTableState.any_selected,
                    color_scheme="green",
                    margin_bottom="4",
                    on_click=CardsTableState.generate_labels,
                ),
                spacing="8",
            )
        ),
        padding="4",
        margin_top="4",
    )


@rx.page(route="/")
@template
def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            search_form(),
            search_config(),
            search_results(),
            spacing="5",
        ),
        width="100%",
    )
