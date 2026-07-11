import json
from .utils import disconnect_sockets, sanitize_text, color_text, generate_user_session_id
import threading
from SocketUtils.client import TCP_Client
from SocketUtils.server import TCP_Server

CANT_CONNECT_TO_SERVER = "Can't connect to server!"
USERNAME_EXISTS = "Username already exists!"
ERROR_CONNECTING_RECEIVER = "Error connecting receiver socket"
NO_ROOMS_FOUND = "No rooms found"
ROOM_ALREADY_EXISTS = "A room with that name already exists"
ROOM_CREATED = "ROOM_CREATED"
MAX_ROOM_NAME_LENGTH = 32
TOO_MUCH_LETTERS = f"A room name can be up to {MAX_ROOM_NAME_LENGTH} characters"

def listen_for_sockets(server: Server, awaiting_login: list[TCP_Client], close_event):
    listen_sock = server.listen_sock
    while not close_event.is_set():
        if listen_sock:
            listen_sock.listen(1)
            client_soc, _ = listen_sock.accept()
            tcp_client = TCP_Client(server.get_info())
            tcp_client.sock = client_soc
            awaiting_login.append(tcp_client)
    disconnect_sockets(listen_sock, awaiting_login)

def listen_for_messages(client: "User", close_event):
    while not close_event.is_set():
        message = client.getSockets()["recv_sock"].listen_to_message()
        if message:
            print(message)

def manage_client(server: Server, users: dict, user: "User", close_event):
    """
    Where the magic happens: This functions manages
    a conversation with each socket (concurrently).
    Here the functions listens for messages and commands
    from the client and does stuff.

    :param users: a dict of the connected users
    :param server: - The server object
    :param user: A User object with the data of the current user.
    :param close_event: the event that says to close the conversation
    :return: None
    """
    sockets = user.getSockets()
    send_sock: TCP_Client = sockets["send_sock"]
    recv_sock: TCP_Client = sockets["recv_sock"]
    try:
        while not close_event.is_set():
            message = send_sock.listen_to_message()
            if not message:
                continue
            print(message)
            data = message.split(":")
            server.execute(data, user)
        disconnect_sockets(send_sock.sock, recv_sock.sock)
    except Exception as e:
        users.pop(user.getSessionId())
        import traceback
        traceback.print_exc()
        if send_sock:
            disconnect_sockets(send_sock.sock)
        if recv_sock:
            disconnect_sockets(recv_sock.sock)
def log_user_in(server: Server, client_soc: TCP_Client, users, close_event):
    if close_event.is_set():
        return

    client_soc.send_message("START")
    message = client_soc.listen_to_message()
    if message:
        items = message.split(":")
        if items[0] == "INIT":
            username, paraphrase = items[1:]
            for user_id, user in users.items():
                if username == user["user"].getUsername():
                    client_soc.send_message(USERNAME_EXISTS)
                    return

            session_id = generate_user_session_id(paraphrase)
            client_soc.send_message(session_id)

            user: "User" = User(username, paraphrase, None)
            user.session_id = session_id
            user.connected = True
            user.send_sock = client_soc
            users[session_id] = {
                "user": user,
                "thread": None
            }
            client_thread = threading.Thread(target=manage_client, args=(server, users, users[session_id]["user"], close_event,))
            client_thread.start()
            users[session_id]["thread"] = client_thread
        elif items[0] == "RECV_SOC":
            session_id = items[1]
            if session_id in users.keys() and not users[session_id]["user"].recv_sock:
                users[session_id]["user"].recv_sock = client_soc
                return
            client_soc.send_message(ERROR_CONNECTING_RECEIVER)
        return
    client_soc.send_message(CANT_CONNECT_TO_SERVER)


class Room:
    def __init__(self, room_id: str, users: list["User"] | None = None):
        self.room_id = room_id
        self.members = users

    def getRoomId(self):
        return self.room_id

    def getMembers(self):
        return self.members
    def addMember(self, user: "User"):
        if self.members:
            self.members.append(user)
    def removeMember(self, user: "User"):
        if not self.members:
            return

        for i in range(len(self.members)):
            curr_user = self.members[i]
            if curr_user.getSessionId() == user.getSessionId():
                self.members.pop(i)


class Server(TCP_Server):
    def __init__(self, server_info):
        super().__init__(server_info)
        self.listen_thread = None
        self.close_event = threading.Event()
        self.users = {}
        self.rooms = {}
        self.target_room = None


    def getCloseEvent(self):
        return self.close_event

    def start_server(self, awaiting_login: list[TCP_Client] | []):
        self.listen_sock.bind(self.server_info.get_info())
        listen_thread = threading.Thread(target=listen_for_sockets, args=(self, awaiting_login, self.close_event))
        listen_thread.start()
        self.listen_thread = listen_thread

    def close_server(self):
        self.close_event.set()
        self.listen_sock.close()
        self.listen_sock = None

        for key, value in self.users.items():
            for thread in value["thread"]:
                thread.join()
                self.users.pop(key)

    def execute(self, data: list[str], user: "User"):
        message_types = {
            "JOIN": self.join,
            "LEAVE": self.leave_room,
            "MESSAGE": self.send_user_message,
            "DISCONNECT": self.notify_disconnection,
            "FETCH_ROOMS": self.fetch_rooms,
            "CREATE_ROOM": self.create_room
        }

        action = data[0]
        if action not in message_types:
            user.getSockets()["send_sock"].send_message(" ")

        message_types[data[0]](user, *data[1:])

    def create_room(self, user: "User", *data):
        room_id = data[0]
        client_send_soc = user.getSockets()["send_sock"]
        if room_id in self.rooms.keys():
            client_send_soc.send_message(ROOM_ALREADY_EXISTS)
            return
        elif len(room_id) > MAX_ROOM_NAME_LENGTH:
            client_send_soc.send_message(TOO_MUCH_LETTERS)
            return

        new_room = Room(room_id)
        new_room.addMember(user)
        user.room_id = room_id
        self.rooms[room_id] = new_room
        client_send_soc.send_message(ROOM_CREATED)

    def fetch_rooms(self, user: "User", *data):
        if not self.rooms:
            user.send_sock.send_message(NO_ROOMS_FOUND)
            return

        rooms = [
            {
                "id": room_id,
                "people_count": len(room.getMembers()) if room.getMembers() else 0,
            }
            for room_id, room in self.rooms.items()
        ]
        user.send_sock.send_message(json.dumps(rooms))
    def leave_room(self, user: "User", *data):
        self.rooms[user.getRoomId()].removeMember(user)
        self.notify_disconnection(user, *data)
        user.room_id = None

    def send_user_message(self, user: "User", *data):
        user_message = sanitize_text(data[0])
        full_message = f"{color_text(user.getUsername(), "BLUE")}: {user_message}"
        self.to(user.getRoomId()).emit(full_message)

    def notify_disconnection(self, user: "User", *data):
        message = f"{user.getUsername()} has left the room."
        self.to(user.getRoomId()).emit(message)

    def emit(self, s: str):
        for member in self.rooms[self.target_room]:
            member.recv_sock.send_message(s)
        self.target_room = None

    def to(self, room_id) -> Server:
        for key, room in self.rooms.items():
            if key == room_id:
                self.target_room = room_id
        return self

    def join(self, user: "User", *data):
        room_id = data[0]
        if not user or not room_id:
            return

        # User can only join 1 room at a time
        old_room = user.getRoomId()
        self.rooms[old_room].removeMember(user)
        self.rooms[room_id].addMember(user)
        user.room_id = room_id




class User:
    def __init__(self, username, paraphrase, server_info):
        self.session_id = None
        self.room_id = None
        self.username = username
        self.paraphrase = paraphrase
        self.server_info = server_info
        self.send_sock = None
        self.connected = False
        self.recv_sock = None
        self.close_event = threading.Event()
        self.listen_thread = None

    def getSessionId(self):
        return self.session_id

    def getUsername(self):
        return self.username
    def setUsername(self, username):
        self.username = username

    def getServerInfo(self):
        return self.server_info
    def setServerInfo(self, server_info):
        self.server_info = server_info

    def getSockets(self):
        return {
            "send_sock": self.send_sock,
            "recv_sock": self.recv_sock,
        }

    def getRoomId(self):
        return self.room_id
    def joinRoom(self, room_id):
        self.send_sock.send_message(f"JOIN:{room_id}")
        res = self.send_sock.listen_to_message()
        if res == "ROOM_JOINED":
            self.room_id = room_id
            return None
        return res
    def createRoom(self, room_id: str):
        self.send_sock.send_message(f"CREATE_ROOM:{room_id}")
        res = self.send_sock.listen_to_message()
        if res == ROOM_CREATED:
            self.room_id = room_id
            return None
        return res
    def connect(self):
        if self.connected:
            return " "

        if self.send_sock:
            disconnect_sockets(self.send_sock)
        if self.recv_sock:
            disconnect_sockets(self.recv_sock)

        send_sock = TCP_Client(self.server_info)
        recv_sock = TCP_Client(self.server_info)

        self.send_sock = send_sock
        self.recv_sock = recv_sock
        try:
            send_sock.connect()
            send_sock.listen_to_message()
        except ConnectionRefusedError:
            self.send_sock = None
            self.recv_sock = None
            return CANT_CONNECT_TO_SERVER

        send_sock.send_message(f"INIT:{self.username}:{self.paraphrase}")
        self.session_id = send_sock.listen_to_message()
        if self.session_id == USERNAME_EXISTS:
            disconnect_sockets(send_sock, recv_sock)
            self.send_sock = None
            self.recv_sock = None
            return USERNAME_EXISTS

        try:
            recv_sock.connect()
            recv_sock.listen_to_message()
        except ConnectionRefusedError:
            self.send_sock = None
            self.recv_sock = None
            disconnect_sockets(send_sock)

        recv_sock.send_message(f"RECV_SOC:{self.session_id}")
        self.listen_thread = threading.Thread(target=listen_for_messages, args=(self, self.close_event))
        self.connected = True
        return " "

    def disconnect(self):
        self.send_sock.send_message(f"DISCONNECT")
        self.close_event.set()
        self.listen_thread.join()
        disconnect_sockets(self.send_sock.sock, self.recv_sock.sock)
        self.send_sock = None
        self.recv_sock = None
        self.connected = False


    def fetch_rooms(self) -> list | None:
        self.send_sock.send_message(f"FETCH_ROOMS")
        res = self.send_sock.listen_to_message()
        if res == NO_ROOMS_FOUND or not res or res == "":
            return None

        rooms = json.loads(res)
        return rooms
    def sendMessage(self, message):
        if self.send_sock:
            self.send_sock.send_message(f"{self.session_id}:{message}")