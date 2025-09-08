import reflex as rx

config = rx.Config(
    app_name="tcglabels",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
