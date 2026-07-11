import threading

from SocketUtils.client import TCP_Client
from SocketUtils.general import ServerInfo
from shared.entities import Server, log_user_in

SERVER_ADD = "127.0.0.1"
SERVER_PORT = 8080
SERVER_INFO = ServerInfo(SERVER_ADD, SERVER_PORT)

def main():
    server = None
    try:
        login_threads = []
        users = {}
        awaiting_login: list[TCP_Client] = []
        server = Server(server_info=SERVER_INFO)
        server.start_server(awaiting_login)
        print(f"Listening on port {SERVER_PORT}")
        while True:
            for socket in awaiting_login:
                if not socket:
                    continue
                print("New Connection: ", socket.get_server_info())
                t = threading.Thread(target=log_user_in, args=(server, socket, users, server.getCloseEvent(),))
                t.start()
                login_threads.append(t)
                awaiting_login.remove(socket)
    except KeyboardInterrupt:
        print("Shutting down...")
        if server:
            server.close_server()
        exit(0)
    except Exception as err:
        print(err.with_traceback(None))
        if server:
            server.close_server()
        exit(1)

if __name__ == "__main__":
    main()