import argparse
from datetime import datetime
import threading
from SocketUtils.client import TCP_Client
from SocketUtils.general import ServerInfo
from shared.entities import Server, log_user_in
import sys

def save_logs(logs):
    with open(f"SERVER_LOGS-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt", "w") as f:
        for log in logs:
            f.write(log + "\n")


def main(ps: argparse.ArgumentParser, address, port):
    server_address = address
    server_port = port
    if not server_port or not server_address:
        ps.print_help()
        exit(1)
    server_info = ServerInfo(server_address, server_port)
    logs = []
    server = None
    try:
        login_threads = []
        awaiting_login: list[TCP_Client] = []
        server = Server(server_info=server_info, logs=logs)
        server.start_server(awaiting_login)
        print(f"Listening on tcp://{server_address}:{server_port}")
        while True:
            for socket in awaiting_login:
                if not socket:
                    continue
                t = threading.Thread(target=log_user_in, args=(server, socket, server.getCloseEvent(),))
                t.start()
                login_threads.append(t)
                awaiting_login.remove(socket)
    except KeyboardInterrupt:
        print("Shutting down...")
        save_logs(logs)
        if server:
            server.close_server()
        sys.exit(0)
    except Exception as err:
        save_logs(logs)
        print(err.with_traceback(None))
        if server:
            server.close_server()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Welcome to the server program of PythonChatApp!")
    parser.add_argument("-p", "--port", default=8080, type=int)
    parser.add_argument("--address", default="localhost", type=str)
    parsed_args = parser.parse_args()
    main(parser, parsed_args.server, parsed_args.port)