from textual.app import App
from SocketUtils.general import ServerInfo
from shared.entities import User
from shared.utils import disconnect_sockets
from ui.components.theme import dracula_theme
from ui.pages.create_room import CreateRoom
from ui.pages.chat import Chat
from ui.pages.setup import Setup
from ui.pages.welcome import WelcomeScreen
from ui.pages.rooms import Rooms

CSS_PATH = "ui/styles/styles.css"
LEAVE_COMMAND = "/leave"

class ClientApp(App):
    CSS_PATH = CSS_PATH

    SCREENS = {
        "welcome_screen": WelcomeScreen,
        "setup": Setup,
        "rooms": Rooms,
        "create_room": CreateRoom,
        "chat": Chat
    }

    def __init__(self):
        super().__init__()
        self.user = None
        self.rooms = []

    def on_mount(self):
        self.register_theme(dracula_theme)
        self.theme = "dracula"
        self.push_screen("welcome_screen")


if __name__ == "__main__":
    app = None
    try:
        app = ClientApp()
        app.run()
    except Exception as e:
        if app:
            disconnect_sockets(app.user.getSockets()["send_sock"].sock, app.user.getSockets()["recv_sock"].sock)
            app.push_screen("setup")
            app.notify(str(e), severity="error")