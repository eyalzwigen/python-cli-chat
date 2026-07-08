from SocketUtils.server import TCP_Server
from SocketUtils.general import ServerInfo
from threading_manager import log_user_in

SERVER_ADD = "127.0.0.1"
SERVER_PORT = 8080
SERVER_INFO = ServerInfo(SERVER_ADD, SERVER_PORT)

def main():
    users = {}
    awaiting_login = []
    server = TCP_Server(server_info=SERVER_INFO)
    server.start_server(awaiting_login)

    while True:
        for socket in awaiting_login:
            log_user_in(socket, users, server.getCloseEvent())

if __name__ == "__main__":
    main()