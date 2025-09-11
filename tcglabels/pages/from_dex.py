import csv
import uuid

import reflex as rx

from ..label_generator import LabelGenerator
from ..models import Card
from ..state import LabelSettingsState
from ..template import template


class DexImportState(rx.State):
    uploading: rx.Field[bool] = rx.field(default=False)
    progress: rx.Field[int] = rx.field(default=0)

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload and set uploaded state."""
        # Process the uploaded files here (e.g., parse CSV, validate data)
        all_cards = []
        for file in files:
            content = await file.read()
            # Parse the CSV content
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    decoded = content.decode("utf-16")
                except UnicodeDecodeError:
                    decoded = content.decode("latin-1")
            reader = csv.DictReader(decoded.splitlines(), delimiter=";")
            cards = []
            for row in reader:
                cards.append(
                    Card(
                        number=row.get("Id", ""),
                        name=row.get("Name", ""),
                        set_name=row.get("Set", ""),
                        rarity=row.get("Rarity", ""),
                        finish=row.get("Variant", ""),
                    )
                )
            all_cards.extend(cards)

        # Generate labels for all cards
        size = await self.get_var_value(LabelSettingsState.label_dimensions)
        font = await self.get_var_value(LabelSettingsState.font_enum)
        label_gen = LabelGenerator(size=size, font=font)
        label_data = label_gen.generate_labels_pdf_bytes(all_cards)
        uuid_str = str(uuid.uuid4())
        return rx.download(data=label_data, filename=f"labels_{uuid_str}.pdf")

    @rx.event
    def handle_upload_progress(self, progress: dict):
        self.uploading = True
        self.progress = round(progress["progress"] * 100)
        if self.progress >= 100:
            self.uploading = False

    @rx.event
    def cancel_upload(self):
        self.uploading = False
        return rx.cancel_upload("file-upload")


def upload_form() -> rx.Component:
    return rx.fragment(
        rx.upload(
            rx.hstack(
                rx.text("Drag and drop files here or click to select files"),
                rx.icon(tag="upload"),
            ),
            id="file-upload",
            padding="4em",
        ),
        rx.vstack(rx.foreach(rx.selected_files("file-upload"), rx.text)),
        rx.progress(value=DexImportState.progress, max=100),
        rx.cond(
            ~DexImportState.uploading,
            rx.button(
                "Upload",
                on_click=DexImportState.handle_upload(
                    rx.upload_files(
                        upload_id="file-upload",
                        on_upload_progress=DexImportState.handle_upload_progress,
                    ),
                ),
            ),
            rx.button(
                "Cancel",
                on_click=DexImportState.cancel_upload,
            ),
        ),
    )


@rx.page(route="/from-dex")
@template
def from_dex() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.text("Import Cards from Dex App", size="2", weight="bold"),
            rx.text(
                "To import a collection, export a CSV using the 'Export as CSV'"
                + "option from the three dots icon in the Dex App. Then upload "
                + "the CSV file to this site.",
                color="gray",
                margin_bottom="4",
            ),
            rx.link(
                "Get Started with Dex App",
                href="https://dextcg.com/",
                is_external=True,
            ),
            upload_form(),
            spacing="5",
        ),
        padding="4",
        margin_top="4",
        width="100%",
    )
