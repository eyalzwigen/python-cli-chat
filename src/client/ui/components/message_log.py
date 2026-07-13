from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static
import rich

class MessageLog(VerticalScroll):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        parent = self.screen
        if parent and hasattr(parent, "messages"):
            self.watch(parent, "messages", self.update_log)

    def compose(self) -> ComposeResult:
        yield Static("", id="messages")

    def update_log(self, new_messages: list[str]):
        container = self.query_one("#messages", Static)
        try:
            content = "\n".join(new_messages)
            container.update(content)

            self.scroll_end(animate=False)
        except TypeError:
            container.update("")