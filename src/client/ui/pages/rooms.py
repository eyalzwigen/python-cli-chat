from textual.app import ComposeResult, App
from textual.containers import Horizontal, Vertical, Center, ScrollableContainer
from textual.events import ScreenResume
from textual.screen import Screen
from textual.widgets import Label
from shared.entities import User
from client.ui.components.button import Button
from client.ui.components.card import Card
from client.ui.components.title import Title


def joinRoom(app: App, user: "User", room_id: str):
    res = user.joinRoom(room_id)
    if not res:
        app.switch_screen("chat")
    else:
        app.notify(res, severity="error")

class Rooms(Screen):
    def __init__(self):
        super().__init__()

    def on_screen_resume(self, event: ScreenResume) -> None:
        self.app.rooms = self.app.user.fetch_rooms()
        self.refresh(recompose=True)
    def refresh_rooms(self):
        if self.app.user:
            self.app.rooms = self.app.user.fetch_rooms()
            self.refresh(recompose=True)
    def compose(self) -> ComposeResult:
        with Vertical(id="rooms-page"):
            with Center(id="rooms-title"):
                yield Title("Rooms")
            with Center():
                with Horizontal(id="rooms-actions"):
                    yield Button(text="Create Room", onclick=self.app.push_screen, args=("create_room",), height=3, width=20)
                    yield Button(text="Refresh", onclick=self.refresh_rooms, height=3, width=20)

            if self.app.rooms:
                with Center():
                    with ScrollableContainer(id="rooms-list"):
                                for room in self.app.rooms:
                                    if not room:
                                        continue
                                    with Card("horizontal", classes="room-card", width="70%", height=5):
                                        with Horizontal(classes="room-info"):
                                            with Vertical(classes="room-details"):
                                                yield Label(f"[bold]{room["room_id"]}[/bold]", classes="room-name")
                                                yield Label(f'{room["people_count"]} people', classes="people-count")
                                            yield Button(text="Join", onclick=joinRoom, args=(self.app, self.app.user, room["room_id"],), classes="join-button", height=3, width=11)
            else:
                with Center():
                    yield Label("No rooms yet.", classes="no-rooms")