from SocketUtils.general import ServerInfo
from textual.containers import Vertical, Center
from textual.screen import Screen
from textual.widgets import Static, Input
from shared.entities import USERNAME_EXISTS, CANT_CONNECT_TO_SERVER, User
from client.ui.components.button import Button
from client.ui.components.title import Title


class Setup(Screen):
    def __init__(self):
        super().__init__()

    def compose(self):
        with Vertical(id="form"):
            with Center(id="title-row"):
                yield Title("Setup")

            with Vertical(id="form-details"):
                yield Static("Enter username")
                yield Input(placeholder="username...", id="username")

                yield Static("Enter server address")
                yield Input(placeholder="server address...", id="server_address")

                yield Static("Enter port")
                yield Input(placeholder="port...", id="port")

                with Center():
                    yield Button("Connect", onclick=self.handle_connection, height=3, width=20)

    def handle_connection(self):
        username_input = self.query_one("#username", Input)
        username = username_input.value

        address_input = self.query_one("#server_address", Input)
        server_address = address_input.value

        port_input = self.query_one("#port", Input)
        port = port_input.value


        if not username:
            self.notify("Username is empty!", severity="error")
            username_input.focus()
            return

        if not server_address:
            self.notify("Server address is empty!", severity="error")
            address_input.focus()
            return

        if not port:
            self.notify("Port is empty!", severity="error")
            port_input.focus()
            return

        if not port.isdigit():
            self.notify("Port is invalid!", severity="error")
            port_input.focus()
            return



        server_info = ServerInfo(server_address, int(port))
        self.app.user = User(username, server_info)
        res = self.app.user.connect()
        if res == USERNAME_EXISTS:
            self.notify(USERNAME_EXISTS, severity="error")
        elif res == CANT_CONNECT_TO_SERVER:
            self.notify(CANT_CONNECT_TO_SERVER, severity="error")
        else:
            self.app.switch_screen("rooms")
    def on_mount(self):
        username_input = self.query_one("#username", Input)
        username_input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        self.handle_connection()
