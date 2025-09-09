import reflex as rx

from .label_generator import Font


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
            self.label_size, (450, 150)
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
