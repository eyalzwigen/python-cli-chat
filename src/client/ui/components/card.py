from typing import Literal

from textual.app import ComposeResult
from textual.widget import Widget
from .theme import dracula_theme

LayoutDirection = Literal["vertical", "horizontal"]
class Card(Widget):
    def __init__(
        self,
        layout: LayoutDirection = "vertical",
        height: int | str = "auto",
        width: int | str = "auto",
        border_weight: str = "tall",
        border_color: str = dracula_theme.secondary,
        padding: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.styles.height = height
        self.styles.width = width
        self.styles.border = (border_weight, border_color)
        self.styles.padding = padding
        self.styles.overflow = "hidden hidden"

    def compose(self) -> ComposeResult:
        yield from self.children
