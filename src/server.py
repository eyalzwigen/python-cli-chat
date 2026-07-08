from SocketUtils.server import TCP_Server
from SocketUtils.general import ServerInfo

SERVER_ADD = "127.0.0.1"
SERVER_PORT = 8080
SERVER_INFO = ServerInfo(SERVER_ADD, SERVER_PORT)

def listen_for_clients(server: TCP_Server):
    while True:
        server.start_listener()

def main():
    server = TCP_Server(server_info=SERVER_INFO)