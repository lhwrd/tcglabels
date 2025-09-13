from typing import Callable

import reflex as rx

# from .components.menu import menu
from .components.footer import footer
from .components.navbar import navbar


def template(
    page: Callable[[], rx.Component],
) -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.hstack(
            # menu(),
            rx.container(page()),
        ),
        footer(),
        rx.color_mode.button(position="bottom-right"),
        width="100%",
        align="center",
    )
