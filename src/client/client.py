from textual.app import App
from SocketUtils.general import ServerInfo
from shared.entities import User
from ui.components.theme import dracula_theme
from ui.pages.create_room import CreateRoom
from ui.pages.main import Main
from ui.pages.setup import Setup
from ui.pages.welcome import WelcomeScreen
from ui.pages.rooms import Rooms

CSS_PATH = "ui/styles/styles.css"
LEAVE_COMMAND = "/leave"

def start_menu():
    print("Welcome to Python Chat Room!")
    server_add = input("Enter your server address: ")
    server_port = int(input("Enter your server port: "))

    server_info = ServerInfo(server_add, server_port)
    username = input("Enter Username: ")
    paraphrase = input("Enter Paraphrase: ")
    client = User(username=username, paraphrase=paraphrase, server_info=server_info)
    client.connect()
    return client

def action_menu():
    print("What would you like to do?")
    print("1. Join a room")
    print("2. Create a room")

    choice = 1
    while True:
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a number")
            continue
        if choice < 1 or choice > 2:
            print("Please choose a number between 1 and 2")
            continue
    return choice

def create_room(client: "User"):
    while True:
        room_id = input("Enter Name: ")
        print("Creating room...")
        res = client.createRoom(room_id)
        if res:
            print(res)
            continue
        break
def print_rooms(client: "User") -> dict:
    """
    Prints the rooms of the client
    :param client:
    :return: a dictionary with all rooms of the client
    """
    choices = {}
    rooms = client.fetch_rooms()
    if not rooms:
        print("No rooms available :(")
        return choices

    print("Please choose a room:")
    for i in range(len(rooms)):
        print(f"{i+1}. {rooms[i]}")
        choices[i + 1] = rooms[i]
    return choices
def main():
    actions = {
        1: print_rooms,
        2: create_room,
    }
    client = None
    try:
        client = start_menu()
        actions[action_menu()](client)

        print(f"type {LEAVE_COMMAND} to leave the room")
        # Actual messaging loop
        while True:
            message = input()
            if message == LEAVE_COMMAND:
                actions[action_menu()](client)


    except KeyboardInterrupt:
        print("\nExiting...")
        if client:
            client.disconnect()

class ClientApp(App):
    CSS_PATH = CSS_PATH

    SCREENS = {
        "welcome_screen": WelcomeScreen,
        "setup": Setup,
        "rooms": Rooms,
        "create_room": CreateRoom,
        "main": Main
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
    app = ClientApp()
    app.run()