import socket
from src.utils import disconnect_sockets
from threading_manager import listen_for_sockets
import threading
from SocketUtils.client import TCP_Client
from SocketUtils.server import TCP_Server


class Room:
    def __init__(self, room_id: str, users: list[User] | None = None):
        self.room_id = room_id
        self.members = users

    def getRoomId(self):
        return self.room_id

    def getMembers(self):
        return self.members
    def addMember(self, user: User):
        if self.members:
            self.members.append(user)
    def removeMember(self, user: User):
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

    def start_server(self, awaiting_login: list[socket.socket] | []):
        self.listen_sock.bind(self.server_info.get_info())
        listen_thread = threading.Thread(target=listen_for_sockets, args=(self.listen_sock, awaiting_login, self.close_event))
        listen_thread.start()
        self.listen_thread = listen_thread

    def close_server(self):
        self.listener["event"].set()
        self.listen_sock.close()
        self.listen_sock = None

        for key, value in self.users.items():
            for thread in value["thread"]:
                thread.join()
                self.users.pop(key)

    def execute(self, data: list[str], user: User):
        message_types = {
            "JOIN": self.join,
            "LEAVE": ...,
            "MESSAGE": ...,
            "DISCONNECT": ...,
        }

        action = data[0]
        if action not in message_types:
            user.getSockets()["send_sock"].send_message(" ")

        message_types[data[0]](user, *data[:1])

    def emit(self, s: str):
        for room in self.rooms:
            for member in room.getMembers():
                member.recv_sock.send_message(s)
    def to(self, room_id) -> Server:
        for key, room in self.rooms.items():
            if key == room_id:
                self.target_room = room_id
        return self

    def join(self, user: User, room_id: str):
        if not user or not room_id:
            return

        # User can only join 1 room at a time
        old_room = user.getRoomId()
        self.rooms[old_room].removeMember(user)
        self.rooms[room_id].addMember(user)
        user.setRoomId(room_id)




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
    def setRoomId(self, room_id):
        self.send_sock.send_message(f"JOIN:{room_id}")
        res = self.send_sock.listen_to_message()
        if res != " ":
            self.room_id = room_id

    def connect(self):
        if self.connected:
            return

        send_sock = TCP_Client(self.server_info)
        recv_sock = TCP_Client(self.server_info)

        self.send_sock = send_sock
        self.recv_sock = recv_sock
        send_sock.connect()
        send_sock.listen_to_message()
        recv_sock.connect()
        recv_sock.listen_to_message()

        send_sock.send_message(f"INIT:{self.username}:{self.paraphrase}")
        self.session_id = send_sock.listen_to_message()
        if self.session_id.isspace():
            send_sock.disconnect()
            recv_sock.disconnect()
            self.send_sock = None
            self.recv_sock = None
            print("Can't connect to server with username :(")
            return

        recv_sock.send_message(f"RECV_SOC:{self.session_id}")
        self.connected = True

    def disconnect(self):
        self.send_sock.send_message(f"DISCONNECT")

        disconnect_sockets(self.send_sock, self.recv_sock)
        self.send_sock = None
        self.recv_sock = None
        self.connected = False



    def sendMessage(self, message):
        if self.send_sock:
            self.send_sock.send_message(f"{self.session_id}:{message}")