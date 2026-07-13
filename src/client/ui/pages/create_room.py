from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Center
from textual.screen import Screen
from textual.widgets import Input, Static, Footer

from shared.entities import User, MAX_ROOM_NAME_LENGTH, TOO_MUCH_LETTERS
from client.ui.components.button import Button
from client.ui.components.title import Title



class CreateRoom(Screen):

    BINDINGS = [
        Binding("escape", "go_back", "Go Back"),
    ]

    def __init__(self):
        super().__init__()

    def create_room(self):
        room_name_input = self.query_one("#room_name", Input)
        room_name = room_name_input.value
        if not room_name:
            self.notify("Room Name cannot be empty!", severity="error")
            return
        if len(room_name) > MAX_ROOM_NAME_LENGTH:
            self.notify(TOO_MUCH_LETTERS, severity="error")
            return

        user: "User" = self.app.user
        res = user.createRoom(room_name)
        if res:
            self.notify(res, severity="error")
            return
        self.query_one("#room_name", Input).clear()
        self.app.switch_screen("chat")

    def compose(self) -> ComposeResult:
        with Vertical(id="form"):
            with Center(id="title-row"):
                yield Title("Create Room")

            with Vertical(id="form-details"):
                yield Static("Enter room name")
                yield Input(placeholder="room name...", id="room_name")

                with Center():
                    yield Button("Connect", onclick=self.create_room, height=3, width=20)
        yield Footer()
    def on_input_submitted(self, event: Input.Submitted):
        self.create_room()

    def action_go_back(self):
        self.app.switch_screen("rooms")