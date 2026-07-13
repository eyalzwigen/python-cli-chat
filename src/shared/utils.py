import hashlib
import re
import socket


def disconnect_sockets(*sockets):
    """
    Disconnect all sockets given
    :param sockets: sockets to disconnect
    :return: None
    """
    for sock in sockets:
        if sock is None:
            continue

        if hasattr(sock, "sock"):
            sock = sock.sock

        if not isinstance(sock, socket.socket):
            continue

        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except OSError:
            pass

def sanitize_text(text):
    """
    Sanitizes a text
    :param text: the text to sanitize
    :return: the sanitized text
    """
    text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    text = text.replace('\n', ' ').replace('\r', '')
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    return text

def generate_user_session_id() -> str:
    """
    Generate a session id for a user
    :return: the session id
    """
    return hashlib.md5().hexdigest()
