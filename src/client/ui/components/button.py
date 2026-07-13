from textual import events
from textual.app import RenderResult
from textual.widget import Widget
from typing import Any, Callable, Tuple
from .theme import dracula_theme

class Button(Widget):
    def __init__(
        self,
        text: str,
        onclick: Callable[..., Any] | None = None,
        args: Tuple[Any, ...] | None = None,
        height: int | float | None = None,
        width: int | float  | None = None,
        border_weight: str = "tall",
        border_color: str = dracula_theme.primary,
        padding: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.styles.height = height if height else self.styles.height
        self.styles.width = width if width else self.styles.width
        self.styles.border = (border_weight, border_color)
        self.styles.padding = padding
        self.onclick = onclick
        self.args = args


    def render(self) -> RenderResult:
        return self.text

    def _on_click(self, event: events.Click) -> None:
        if self.onclick:
            if self.args:
                self.onclick(*self.args)
            else:
                self.onclick()
