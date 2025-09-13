import reflex as rx

from ..template import template


@rx.page(route="/")
@template
def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.vstack(
        rx.heading("Welcome to TCG Labels", size="5"),
        rx.text(
            "Create and print custom labels for your trading "
            + "card collection with ease.",
            size="3",
        ),
        rx.link(
            "Get Started",
            href="/search",
            color=rx.color("white", 5),
            size="2",
            font_weight="bold",
            padding="1.5em 3em",
            border_radius="8px",
            bg=rx.color("blue", 3),
            _hover={
                "text_decoration": "none",
                "bg": rx.color("blue", 4),
            },
        ),
        spacing="5",
        align_items="center",
        justify_content="center",
        height="25vh",
    )
