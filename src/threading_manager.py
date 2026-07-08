from SocketUtils.client import TCP_Client
from entities import User
import threading

from src.entities import Server
from utils import generate_user_session_id, sanitize_text, disconnect_sockets
    
def manage_client(server: Server, user, close_event):
    """
    Where the magic happens: This functions manages
    a conversation with each socket (concurrently).
    Here the functions listens for messages and commands
    from the client and does stuff.

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
                break
            data = message.split(":")
            server.execute(data, user)
        disconnect_sockets(send_sock, recv_sock)
    except Exception:
        disconnect_sockets(send_sock, recv_sock)


def log_user_in(client_soc: TCP_Client, users, close_event):
    client_soc.send_message("START")
    message = client_soc.listen_to_message()
    if message:
        items = message.split(":")
        if items[0] == "INIT":
            username, paraphrase = items[1:]
            if username in users:
                client_soc.send_message(" ")
            session_id = generate_user_session_id(paraphrase)
            client_soc.sendall(session_id.encode())

            user: User = User(username, paraphrase, None)
            user.connected = True
            user.send_sock = client_soc
            users[session_id] = {
                "user": user,
                "thread": None
            }
            client_thread = threading.Thread(target=manage_client, args=(users[session_id]["user"], close_event))
            users[session_id]["thread"] = client_thread
        elif items[0] == "RECV_SOC":
            session_id = items[1]
            if session_id in users.keys() and not users[session_id]["user"].recv_sock:
                users[session_id]["user"].recv_sock = client_soc

    client_soc.sendall(f" ".encode())

def listen_for_sockets(listen_sock, awaiting_login: list[TCP_Client], close_event):
    while not close_event.is_set():
        if listen_sock:
            listen_sock.listen(1)
            client_soc, _ = listen_sock.accept()
            tcp_client = TCP_Client(None)
            tcp_client.socket = client_soc
            awaiting_login.append(tcp_client)
