from textual import events
from textual.app import ComposeResult, App
from textual.containers import Horizontal, Vertical, Center, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Label
from shared.entities import User
from ui.components.button import Button
from ui.components.card import Card
from ui.components.title import Title


def joinRoom(app: App, user: "User", room_id: str):
    user.joinRoom(room_id)
    app.push_screen("main")

class Rooms(Screen):
    def __init__(self):
        super().__init__()

    def _on_mount(self, event: events.Mount) -> None:
        self.app.rooms = self.app.user.fetch_rooms()
    def refresh_rooms(self):
        if self.app.user:
            self.app.rooms = self.app.user.fetch_rooms()
            self.screen.refresh(recompose=True)
    def compose(self) -> ComposeResult:
        with Center():
            yield Title("Rooms")

        with Horizontal():
            yield Button(text="Create Room", onclick=self.app.push_screen, args=("create_room",))
            yield Button(text="Refresh", onclick=self.refresh_rooms)

        if self.app.rooms:
            with ScrollableContainer():
                with Vertical():
                    for room in self.app.rooms:
                        if not room:
                            continue

                        with Card("horizontal"):
                            with Horizontal():
                                with Vertical():
                                    yield Label(f"[bold]{room["id"]}[/bold]")
                                    yield Label(f'{room["people_count"]} people')
                                yield Button(text="Join", onclick=joinRoom, args=(self.app, self.app.user, room["id"],))