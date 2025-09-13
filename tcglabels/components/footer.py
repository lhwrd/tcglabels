import reflex as rx


def footer() -> rx.Component:
    return rx.el.footer(
        rx.vstack(
            rx.text(
                "This website is not produced, endorsed, supported,"
                + " or affiliated with Nintendo or The Pokémon Company.",
                font_size="0.8em",
                color="gray",
                padding_y="0.5em",
                align="center",
            ),
            width="100%",
            justify="center",
        )
    )
