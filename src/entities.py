from threading_manager import listen_for_users
import threading
from SocketUtils.client import TCP_Client
from SocketUtils.server import TCP_Server



class Server(TCP_Server):
    def __init__(self, server_info):
        super().__init__(server_info)
        self.listen_sock.bind(self.server_info.get_info())
        self.listener = None
        self.users = {}


    def start_server(self):
        close_event = threading.Event()
        listen_thread = threading.Thread(target=listen_for_users, args=(self.listen_sock, close_event))
        listen_thread.start()
        self.listener = {"thread": listen_thread, "event": close_event}


    def close_server(self):
        self.listener["event"].set()
        self.listen_sock.close()
        self.listen_sock = None

        for key, value in self.users.items():
            for thread in value["thread"]:
                thread.join()
                self.users.pop(key)


class User:
    def __init__(self, username, paraphrase, server_info):
        self.sessionId = None
        self.roomId = None
        self.username = username
        self.paraphrase = paraphrase
        self.server_info = server_info
        self.send_sock = None
        self.connected = False
        self.recv_sock = None

    def getUsername(self):
        return self.username
    def setUsername(self, username):
        self.username = username

    def getServerInfo(self):
        return self.server_info
    def setServerInfo(self, server_info):
        self.server_info = server_info

    def getRoomId(self):
        return self.roomId
    def setRoomId(self, roomId):
        self.send_sock.send_message(f"{self.sessionId}:change_room:{roomId}")

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
        self.sessionId = send_sock.listen_to_message()
        if self.sessionId.isspace():
            send_sock.disconnect()
            recv_sock.disconnect()
            self.send_sock = None
            self.recv_sock = None
            print("Can't connect to server with username :(")
            return

        recv_sock.recv_message(f"RECV_SOC:{self.sessionId}")
        self.connected = True

    def disconnect(self):
        self.send_sock.send_message(f"{self.sessionId}:disconnect")

        self.send_sock.disconnect()
        self.recv_sock.disconnect()
        self.send_sock = None
        self.recv_sock = None
        self.connected = False



    def sendMessage(self, message):
        if self.send_sock:
            self.send_sock.send_message(f"{self.sessionId}:{message}")