from textual.app import ComposeResult
from textual.containers import Vertical, Center
from textual.screen import Screen
from textual.widgets import Input, Static

from shared.entities import User, MAX_ROOM_NAME_LENGTH, TOO_MUCH_LETTERS
from ui.components.button import Button
from ui.components.title import Title



class CreateRoom(Screen):
    def __init__(self):
        super().__init__()

    def create_room(self):
        room_name_input = self.query_one("#room_name", Input)
        room_name = room_name_input.value
        if not room_name:
            self.notify("Room Name cannot be empty!", severity="error")
            return
        if room_name > MAX_ROOM_NAME_LENGTH:
            self.notify(TOO_MUCH_LETTERS, severity="error")

        user: "User" = self.app.user
        res = user.createRoom(room_name)
        if res:
            self.notify(res, severity="error")
    def compose(self) -> ComposeResult:
        with Vertical(id="form"):
            with Center(id="title-row"):
                yield Title("Create Room")

            with Vertical(id="form-details"):
                yield Static("Enter room name")
                yield Input(placeholder="room name...", id="room_name")

                with Center():
                    yield Button("Connect", onclick=self.create_room, height=3)
    def on_input_submitted(self, event: Input.Submitted):
        self.create_room()