from textual.app import Screen, ComposeResult
from textual.containers import Vertical, Center
from ui.components.button import Button
from ui.components.title import Title


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="welcome-container"):
            yield Title("Welcome to Python Chat!")

            with Center(id="button-row"):
                yield Button("Start Chatting", onclick=self.app.switch_screen, args=("setup",), height=3.5, width=20)