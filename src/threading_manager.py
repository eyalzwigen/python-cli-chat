from entities import User
import socket
import threading
from utils import generate_user_session_id, sanitize_text

MAX_BYTES = 1024

MESSAGE_TYPES = {
    "JOIN": ...,
    "LEAVE": ...,
    "MESSAGE": ...,
}

def join_room(user: User, data):
    if len(data) < 1:
        return
    

def manage_client(user_data, close_event):
    send_soc = user_data["send_soc"]
    recv_soc = user_data["recv_soc"]
    try:
        while not close_event.is_set():
            message = send_soc.recv(MAX_BYTES).decode()
            if not message:
                break
            items = message.split(":")
            if not items[0] in MESSAGE_TYPES:
                send_soc.sendall(" ".encode())
            MESSAGE_TYPES[items[0]](user_data)
        send_soc.shutdown(socket.SHUT_RDWR)
        send_soc.close()
        recv_soc.shutdown(socket.SHUT_RDWR)
        recv_soc.close()
    except Exception:
        send_soc.shutdown(socket.SHUT_RDWR)
        send_soc.close()
        recv_soc.shutdown(socket.SHUT_RDWR)
        recv_soc.close()


def log_user_in(client_soc: socket.socket, users, close_event):
    client_soc.sendall(f"START".encode())
    message = client_soc.recv(MAX_BYTES).decode()
    if message:
        items = message.split(":")
        if items[0] == "INIT":
            username, paraphrase = items[1:]
            if username in users:
                client_soc.sendall(" ".encode())
            session_id = generate_user_session_id(paraphrase)
            client_soc.sendall(session_id.encode())

            user: User = User(username, paraphrase, None)
            user.connected = True
            user.send_sock = client_soc
            users[session_id] = {
                "user": user,
            }
            client_thread = threading.Thread(target=client_soc.send, args=(users[session_id]["user"], close_event))
            users[session_id]["thread"] = client_thread
        elif items[0] == "RECV_SOC":
            session_id = items[1]
            if session_id in users.keys() and not users[session_id]["user"].recv_sock:
                users[session_id]["user"].recv_sock = client_soc

    client_soc.sendall(f" ".encode())

def listen_for_users(listen_sock, users, close_event):
    while not close_event.is_set():
        if listen_sock:
            listen_sock.listen(1)
            client_soc, _ = listen_sock.accept()
            log_user_in(client_soc, users, close_event)