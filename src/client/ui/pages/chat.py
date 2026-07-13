import json
import threading
from SocketUtils.client import TCP_Client
from textual.binding import Binding
from textual.events import ScreenResume
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Footer, Static
from shared.entities import User, LEFT_ROOM
from ui.components.button import Button
from ui.components.message_log import MessageLog


class Chat(Screen):
    messages = reactive([])
    BINDINGS = [
        Binding("escape", "leve_room", "Leave Room"),
    ]
    def __init__(self):
        super().__init__()
        self.running = False
        self.thread = None

    def on_screen_resume(self, event: ScreenResume) -> None:
        self.running = True

        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(
                target=self.listen_for_messages,
                daemon=True,
            )
            self.thread.start()

        self.query_one("#message-input", Input).focus()
    def compose(self) -> ComposeResult:
        with Vertical(id="chat-page"):
            yield MessageLog(id="message-log")
            with Horizontal(id="message-composer"):
                yield Input(placeholder="Send a message...", id="message-input")
                yield Button("Send", onclick=self.send_message, id="send-message")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted):
        self.send_message()

    def action_leve_room(self):
        self.running = False
        self.app.user.leaveRoom()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.thread = None
        self.messages = []
        self.app.switch_screen("rooms")

    def send_message(self):
        message_input = self.query_one("#message-input", Input)
        message = message_input.value
        if not message:
            return

        user: User | None = None
        if hasattr(self.app, "user"):
            user = self.app.user

        if not user:
            self.running = False
            self.app.push_screen("setup")

        user.sendMessage(message)
        message_input.clear()
    def listen_for_messages(self):
        user: User | None = None
        recv_sock: TCP_Client | None = None
        if hasattr(self.app, "user"):
            user = self.app.user
        if user:
            recv_sock = user.getSockets()["recv_sock"]
        while self.running:
            if not recv_sock:
                if not self.app.user.getRoomId():
                    return
                self.running = False
                self.app.switch_screen("setup")
                self.app.notify("Error Connecting To Server", severity="error")
            try:
                new_message = recv_sock.listen_to_message()
                if new_message:
                    if new_message == LEFT_ROOM:
                        raise Exception
                    else:
                        message_data = json.loads(new_message)
                        message = f"[ansi_blue]{message_data['username']}:[/ansi_blue] {message_data['message']}"
                        self.app.call_from_thread(self.add_message, message)

            except Exception:
                if not self.running:
                    return
                recv_sock = None
                continue

    def add_message(self, message: str):
        self.messages = self.messages + [message]

    def on_unmount(self) -> None:
        self.running = False
        user = self.app.user

        if user and user.recv_sock:
            try:
                user.recv_sock.disconnect()
            except Exception:
                pass

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        self.thread = None
