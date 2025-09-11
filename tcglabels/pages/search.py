from typing import Sequence
from uuid import uuid4

import reflex as rx
from reflex.state import State
from reflex.vars import BooleanVar

from ..label_generator import LabelGenerator
from ..models import Card
from ..state import LabelSettingsState
from ..tcg_search import search_cards
from ..template import template


class CardsTableState(State):
    cards: rx.Field[Sequence[Card]] = rx.field(
        default_factory=list
    )  # List of card instances
    selected_card_numbers: rx.Field[list[str]] = rx.field(
        default_factory=list
    )  # List of selected card ids (unique id)
    searching: rx.Field[bool] = rx.field(default=False)

    @rx.event
    async def search_cards(self, form_data: dict) -> None:
        """Search for cards based on form data and update the state."""
        self.searching = True
        results = await search_cards(form_data)
        self.cards = results
        self.selected_card_numbers = self.selected_card_numbers + [
            card.unique_id for card in self.cards
        ]
        self.searching = False

    @rx.event
    def toggle_all_selected(self) -> None:
        """Toggle selection state of all cards."""
        if len(self.selected_card_numbers) == len(self.cards):
            self.selected_card_numbers = []
        else:
            self.selected_card_numbers = [card.unique_id for card in self.cards]

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
    def toggle_card_selected(self, card_number: str) -> None:
        if card_number in self.selected_card_numbers:
            self.selected_card_numbers.remove(card_number)
        else:
            self.selected_card_numbers.append(card_number)

    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_card_numbers)

    @rx.event
    async def generate_labels(self):
        """Generate labels for selected cards."""
        selected_cards = [
            card for card in self.cards if card.unique_id in self.selected_card_numbers
        ]
        size = await self.get_var_value(LabelSettingsState.label_dimensions)
        font = await self.get_var_value(LabelSettingsState.font_enum)
        generator = LabelGenerator(size=size, font=font)
        guid = uuid4()
        data = generator.generate_labels_pdf_bytes(cards=selected_cards)
        return rx.download(data=data, filename=f"labels_{guid}.pdf")


def search_form() -> rx.Component:
    # Search Form Component
    return rx.form(
        rx.hstack(
            rx.input(placeholder="Card Name", name="name"),
            rx.input(placeholder="Set Name", name="set_name"),
            rx.input(placeholder="Rarity", name="rarity"),
            rx.input(placeholder="ID", name="id"),
            rx.cond(
                CardsTableState.searching,
                rx.button("Searching...", type="submit"),
                rx.button("Search", type="submit"),
            ),
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
    selected = CardsTableState.selected_card_numbers.contains(card.unique_id)

    return rx.table.row(
        rx.table.cell(
            rx.icon_button(
                dynamic_select_icon(selected),
                color_scheme=rx.cond(selected, "blue", "gray"),
                on_click=lambda: CardsTableState.toggle_card_selected(
                    card_number=card.unique_id
                ),
            )
        ),
        rx.table.row_header_cell(card.name),
        rx.table.cell(card.set_name),
        rx.table.cell(card.rarity),
        rx.table.cell(card.number),
        rx.table.cell(rx.cond(card.finish, card.finish, "N/A")),
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


@rx.page(route="/search")
@template
def search() -> rx.Component:
    # Search Page
    return rx.container(
        rx.vstack(
            search_form(),
            search_config(),
            search_results(),
            spacing="5",
        ),
        width="100%",
    )
