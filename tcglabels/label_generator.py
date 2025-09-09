import os
from enum import Enum
from importlib.resources import files
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from tcgdexsdk.models.Card import Card


def truncate_string(s, max_length):
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s


class Font(Enum):
    OPENSANS = "OpenSans-Regular.ttf"
    ARIAL = "Arial Unicode.ttf"
    OPENSANS_BOLD = "OpenSans-Bold.ttf"

    @property
    def path(self):
        package_dir = Path(str(files("tcglabels")))
        return str(package_dir.parent / "assets/fonts" / self.value)


class LabelGenerator:
    def __init__(
        self,
        size: tuple[int, int] | list[int],
        font: Font,
    ):
        """Initialize the LabelGenerator.

        Args:
            size (tuple[int, int]): The size of the label in pixels (width, height).
            font (Font | None, optional): The font to use for the label.
                Defaults to None.
        """
        self.size = size
        self.font = font
        print(size, font)
        self._starting_x = int(size[0] * 0.05)

    def generate_label(self, card: Card, output_path: str) -> None:
        """Generate a label image and save it to the specified path.

        Args:
            card (Card): The card for which to generate the label.
            output_path (str): The path where the label image will be saved.

        """
        img = Image.new("RGB", size=self.size, color="white")

        draw = ImageDraw.Draw(img)

        # Load the font
        font_height = int(self.size[1] * 0.25)
        fnt = ImageFont.truetype(self.font.path, font_height)

        # Draw the first line of text
        line1_y = int(self.size[1] * 0.05)
        draw.text(
            (self._starting_x, line1_y),
            card.name,
            font=fnt,
            fill=(0, 0, 0),
            align="center",
        )

        # Draw the second line of text
        line2 = [str(card.id).upper(), str(card.rarity).upper()]
        line2 = " ".join(line2)
        line2 = truncate_string(line2, 29)
        line2_y = int(self.size[1] * 0.35)
        draw.text(
            (self._starting_x, line2_y),
            line2,
            font=fnt,
            fill=(0, 0, 0),
            align="center",
        )

        # Draw third line
        line3 = truncate_string(card.set.name, 29)
        line3_y = int(self.size[1] * 0.65)
        draw.text(
            (self._starting_x, line3_y),
            line3,
            font=fnt,
            fill=(0, 0, 0),
            align="center",
        )

        # Save the image
        img.save(output_path)
        img.close()

    def generate_labels(self, cards: list[Card], output_dir: str) -> None:
        """Generate labels for a list of cards and save them to the specified directory.

        Args:
            cards (list[Card]): List of Card objects to generate labels for.
            output_dir (str): Directory where the label images will be saved.

        """
        os.makedirs(output_dir, exist_ok=True)
        for card in cards:
            output_path = f"{output_dir}/label_{card.id}.png"
            self.generate_label(card, output_path)

    def generate_labels_pdf(
        self,
        cards: list[Card],
        output_path: str = "labels.pdf",
    ) -> None:
        """Generate a PDF of labels for the given cards.

        Args:
            cards (list[Card]): List of Card objects to generate labels for.
            output_path (str, optional): Path to save the generated PDF.
                Defaults to "labels.pdf".

        """
        images = []
        for card in cards:
            img_path = f"/tmp/label_{card.id}.png"
            self.generate_label(card, img_path)
            img = Image.open(img_path).convert("RGB")
            images.append(img)

        if images:
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                resolution=100.0,
                quality=95,
            )

        for img in images:
            img.close()

    def generate_labels_pdf_bytes(
        self,
        cards: list[Card],
    ) -> bytes:
        """Generate a PDF of labels for the given cards and return it as bytes.

        Args:
            cards (list[Card]): List of Card objects to generate labels for.

        Returns:
            bytes: The generated PDF as bytes.

        """

        images = []
        for card in cards:
            img_path = f"/tmp/label_{card.id}.png"
            self.generate_label(card, img_path)
            img = Image.open(img_path).convert("RGB")
            images.append(img)

        pdf_bytes = BytesIO()
        if images:
            images[0].save(
                pdf_bytes,
                format="PDF",
                save_all=True,
                append_images=images[1:],
                resolution=100.0,
                quality=95,
            )

        for img in images:
            img.close()

        pdf_bytes.seek(0)
        return pdf_bytes.read()
