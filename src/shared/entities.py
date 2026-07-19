from __future__ import annotations

import socket
import json
from .utils import disconnect_sockets, sanitize_text, generate_user_session_id
import threading
from SocketUtils.client import TCP_Client
from SocketUtils.server import TCP_Server

SERVER_ADDRESS = "eilzwig.hackclub.app"
PORT = 8080

CANT_CONNECT_TO_SERVER = "Can't connect to server!"
USERNAME_EXISTS = "Username already exists!"
ERROR_CONNECTING_RECEIVER = "Error connecting receiver socket"
NO_ROOMS_FOUND = "No rooms found"
ROOM_ALREADY_EXISTS = "A room with that name already exists"
ROOM_CREATED = "ROOM_CREATED"
MAX_ROOM_NAME_LENGTH = 32
TOO_MUCH_LETTERS = f"A room name can be up to {MAX_ROOM_NAME_LENGTH} characters"
ROOM_JOINED = "ROOM_JOINED"
LEFT_ROOM = "LEFT_ROOM"

def listen_for_sockets(server: "Server", awaiting_login: list["TCP_Client"], close_event: "threading.Event"):
    listen_sock = server.listen_sock

    while not close_event.is_set():
        try:
            listen_sock.listen(1)
            client_soc, _ = listen_sock.accept()
        except OSError:
            if close_event.is_set():
                break
            raise

        tcp_client = TCP_Client(server.get_info())
        tcp_client.sock = client_soc
        awaiting_login.append(tcp_client)

def listen_for_messages(client: "User", close_event):
    while not close_event.is_set():
        message = client.getSockets()["recv_sock"].listen_to_message()
        if message:
            print(message)

def manage_client(server: "Server", users: dict, user: "User", close_event):
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
    send_sock: "TCP_Client" = sockets["send_sock"]
    recv_sock: "TCP_Client" = sockets["recv_sock"]
    try:
        while not close_event.is_set():
            message = send_sock.listen_to_message()
            if not message:
                continue
            data = message.split(":")
            server.execute(data, user)
        disconnect_sockets(send_sock.sock, recv_sock.sock)
    except Exception as e:
        if close_event.is_set():
            return

        server.leave_room(user, None)
        users.pop(user.getSessionId())
        import traceback
        log = "USER_DISCONNECTED: " + str(user)
        server.logs.append(log)
        print(log)
        log = "AT_THE_SAME_TIME:\n"
        server.logs.append(log)
        print(log)
        log = "ERROR:\n" + traceback.format_exc()
        server.logs.append(log)
        print(log)
        if send_sock:
            disconnect_sockets(send_sock.sock)
        if recv_sock:
            disconnect_sockets(recv_sock.sock)
def log_user_in(server: "Server", client_soc: "TCP_Client", close_event):
    if close_event.is_set():
        return

    client_soc.send_message("START")
    message = client_soc.listen_to_message()
    if message:
        items = message.split(":")
        if items[0] == "INIT":
            username = items[1]
            for user_id, user in server.users.items():
                if username == user["user"].getUsername():
                    client_soc.send_message(USERNAME_EXISTS)
                    return

            session_id = generate_user_session_id()
            client_soc.send_message(session_id)

            user: "User" = User(username, None)
            user.session_id = session_id
            user.connected = True
            user.send_sock = client_soc
            server.users[session_id] = {
                "user": user,
                "thread": None
            }
            client_thread = threading.Thread(target=manage_client, args=(server, server.users, server.users[session_id]["user"], close_event,))
            client_thread.start()
            server.users[session_id]["thread"] = client_thread
            log = f"NEW_CONNECTION: {str(user)}"
            server.logs.append(log)
            print(log)
        elif items[0] == "RECV_SOC":
            session_id = items[1]
            if session_id in server.users.keys() and not server.users[session_id]["user"].recv_sock:
                server.users[session_id]["user"].recv_sock = client_soc
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
        else:
            self.members = [user]
    def removeMember(self, user: "User"):
        if not self.members:
            return

        try:
            self.members.remove(user)
        except ValueError:
            pass

    def __str__(self):
        s = f"Room Name: {self.room_id}, "
        s += "Members: "
        if not self.members:
            s += "N/A"
        else:
            for member in self.members:
                s += f"{member.getUsername()} "
        return  s


class Server(TCP_Server):
    def __init__(self, server_info, logs):
        super().__init__(server_info)
        self.listen_thread = None
        self.close_event = threading.Event()
        self.users = {}
        self.rooms = {}
        self.target_room = None
        self.logs = logs


    def getCloseEvent(self):
        return self.close_event

    def start_server(self, awaiting_login: list[TCP_Client] | []):
        self.listen_sock.bind(self.server_info.get_info())
        self.listen_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )
        listen_thread = threading.Thread(target=listen_for_sockets, args=(self, awaiting_login, self.close_event))
        listen_thread.start()
        self.listen_thread = listen_thread

    def close_server(self):
        self.close_event.set()

        try:
            disconnect_sockets(self.listen_sock)
        except OSError:
            pass

        for value in list(self.users.values()):
            user = value["user"]

            sockets = user.getSockets()

            if sockets["send_sock"]:
                disconnect_sockets(sockets["send_sock"].sock)

            if sockets["recv_sock"]:
                disconnect_sockets(sockets["recv_sock"].sock)

        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)

        for value in list(self.users.values()):
            thread = value["thread"]

            if thread and thread.is_alive():
                thread.join(timeout=2)

        self.users.clear()

    def execute(self, data: list[str], user: "User"):
        message_types = {
            "JOIN": self.join,
            "LEAVE": self.leave_room,
            "MESSAGE": self.send_user_message,
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
        log = f"ROOM_CREATED:{str(new_room)}"
        self.logs.append(log)
        print(str(log))
        client_send_soc.send_message(ROOM_CREATED)

    def fetch_rooms(self, user: "User", *data):
        if not self.rooms:
            user.send_sock.send_message(NO_ROOMS_FOUND)
            return

        rooms = []

        for room_id, room in self.rooms.items():
            if not room.getMembers() or len(room.getMembers()) == 0:
                self.rooms.pop(room_id)
                continue

            room_parsed = {
                "room_id": room_id,
                "people_count": len(room.getMembers())
            }
            rooms.append(room_parsed)
        log = f"FETCHED_ROOMS:{str(rooms)}"
        self.logs.append(log)
        print(str(log))
        user.send_sock.send_message(json.dumps(rooms))
    def leave_room(self, user: "User", *data):
        try:
            if not user.getRoomId() in self.rooms.keys():
                return
            room = self.rooms[user.getRoomId()]
            room.removeMember(user)
            if not room.getMembers() or len(room.getMembers()) == 0:
                self.rooms.pop(room.getRoomId())
                user.getSockets()["send_sock"].send_message(LEFT_ROOM)
                user.getSockets()["recv_sock"].send_message(LEFT_ROOM)
                user.room_id = None
                log = f"ROOM_DELETED_UPON_LEAVE:{room.getRoomId()}:ROOMS_LEFT:"
                for r in self.rooms:
                    log += str(r) + " | "
                self.logs.append(log)
                print(log)
                return
            user.room_id = None
            user.getSockets()["send_sock"].send_message(LEFT_ROOM)
            user.getSockets()["recv_sock"].send_message(LEFT_ROOM)
            print(str(room))
        except Exception as e:
            import traceback
            traceback.print_exc()
            user.getSockets()["send_sock"].send_message(str(e))


    def send_user_message(self, user: "User", *data):
        user_message = sanitize_text(data[0])
        log = "MESSAGE_SENT: " + str({
            "room_id": user.room_id,
            "user": user.getUsername(),
            "session_id": user.session_id,
            "message": user_message
        })
        self.logs.append(log)
        print(log)
        self.to(user.getRoomId()).emit(json.dumps({"username": user.getUsername(), "message": user_message}))


    def emit(self, s: str):
        for member in self.rooms[self.target_room].getMembers():
            try:
                member.recv_sock.send_message(s)
            except Exception:
                self.leave_room(member, None)
        self.target_room = None

    def to(self, room_id) -> Server:
        for key, room in self.rooms.items():
            if key == room_id:
                self.target_room = room_id
        return self

    def join(self, user: "User", *data):
        try:
            room_id = data[0]
            if not user or not room_id:
                raise Exception

            # User can only join 1 room at a time
            old_room_id = user.getRoomId()
            if old_room_id:
                old_room = self.rooms[old_room_id]
                if old_room:
                    old_room.removeMember(user)

            self.rooms[room_id].addMember(user)
            user.room_id = room_id
            user.send_sock.send_message(ROOM_JOINED)
        except Exception:
            user.send_sock.send_message(" ")




class User:
    def __init__(self, username, server_info):
        self.session_id = None
        self.room_id = None
        self.username = username
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
        if res == ROOM_JOINED:
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

    def leaveRoom(self):
        self.send_sock.send_message(f"LEAVE")
        res = self.send_sock.listen_to_message()
        if res == LEFT_ROOM:
            self.room_id = None
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

        send_sock.send_message(f"INIT:{self.username}")
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
        self.close_event.set()

        try:
            if self.send_sock:
                self.send_sock.send_message("DISCONNECT")
        except OSError:
            pass

        if self.send_sock:
            disconnect_sockets(self.send_sock.sock)

        if self.recv_sock:
            disconnect_sockets(self.recv_sock.sock)

        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)

        self.send_sock = None
        self.recv_sock = None
        self.connected = False
        self.room_id = None


    def fetch_rooms(self) -> list | None:
        self.send_sock.send_message(f"FETCH_ROOMS")
        res = self.send_sock.listen_to_message()
        if res == NO_ROOMS_FOUND or not res or res == "":
            return None

        rooms = json.loads(res)
        return rooms
    def sendMessage(self, message):
        if self.send_sock:
            self.send_sock.send_message(f"MESSAGE:{message}")

    def __str__(self):
        return f"USERNAME: {self.username}, SESSION_ID: {self.session_id}"