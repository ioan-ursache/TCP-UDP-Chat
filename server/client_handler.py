import threading
import json
from utils.protocol import (
    decode_message, encode_system_message, encode_chat_message,
    validate_message, MSG_LOGIN, MSG_MESSAGE, MSG_COMMAND
)


class ClientHandler(threading.Thread):
    def __init__(self, sock, address, server):
        super().__init__(daemon=True)
        self.sock = sock
        self.address = address
        self.server = server
        self.username = None  # Will be set during login
        self.alive = True
        self.authenticated = False

    def run(self):
        try:
            # Wait for LOGIN message
            if not self.wait_for_login():
                print(f"[REJECT] {self.address} - No valid login received")
                self.disconnect()
                return

            # Send welcome message
            welcome = encode_system_message(f"Welcome {self.username} to the Lobby!")
            self.send(welcome)

            # Notify others
            join_notice = encode_system_message(f"{self.username} joined the chat.")
            self.server.broadcast(join_notice, exclude_client=self)

            # Broadcast UDP join status
            self.server.broadcast_udp_status("join", self.username)

            # Main message loop
            buffer = ""
            while self.alive:
                data = self.sock.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        self.handle_message(line)

        except Exception as e:
            print(f"[ERROR] {self.username or self.address}: {e}")
        finally:
            self.disconnect()

    def wait_for_login(self, timeout=10):
        """Wait for LOGIN message with timeout."""
        self.sock.settimeout(timeout)
        try:
            data = self.sock.recv(1024)
            if not data:
                return False

            # Handle potential multiple lines
            lines = data.decode("utf-8").strip().split("\n")
            for line in lines:
                msg = decode_message(line)
                if msg and msg.get("type") == MSG_LOGIN:
                    username = msg.get("username", "").strip()
                    if username and self.server.register_username(username, self):
                        self.username = username
                        self.authenticated = True
                        self.sock.settimeout(None)  # Remove timeout
                        return True

            # No valid login found
            error = encode_system_message("ERROR: Invalid login. Please send {\"type\":\"login\",\"username\":\"YourName\"}")
            self.send(error)
            return False

        except socket.timeout:
            return False
        except Exception as e:
            print(f"[LOGIN ERROR] {self.address}: {e}")
            return False

    def handle_message(self, raw_msg):
        """Handle incoming message from client."""
        msg = decode_message(raw_msg)
        if not msg:
            print(f"[WARN] Invalid JSON from {self.username}: {raw_msg[:50]}")
            return

        msg_type = msg.get("type")

        # Handle different message types
        if msg_type == MSG_MESSAGE:
            self.handle_chat_message(msg)
        elif msg_type == MSG_COMMAND:
            self.handle_command(msg)
        elif msg_type == MSG_LOGIN:
            # Already logged in
            error = encode_system_message("ERROR: Already logged in")
            self.send(error)
        else:
            print(f"[WARN] Unknown message type from {self.username}: {msg_type}")

    def handle_chat_message(self, msg):
        """Handle chat message."""
        text = msg.get("text", "").strip()

        # Special typing indicator
        if text == "_typing_":
            self.server.broadcast_udp_status("typing", self.username)
            return

        if not text:
            return

        # Broadcast message to all clients
        broadcast_msg = encode_chat_message(self.username, text)
        self.server.broadcast(broadcast_msg, exclude_client=self)

    def handle_command(self, msg):
        """Handle command message."""
        cmd = msg.get("cmd", "").lower()

        if cmd == "quit":
            self.disconnect()
        elif cmd == "list":
            users = self.server.get_active_users()
            user_list = encode_system_message(f"Active users: {', '.join(users)}")
            self.send(user_list)
        else:
            error = encode_system_message(f"Unknown command: {cmd}")
            self.send(error)

    def send(self, message):
        """Send message to this client."""
        try:
            if isinstance(message, str):
                message = message.encode("utf-8")
            if not message.endswith(b"\n"):
                message += b"\n"
            self.sock.sendall(message)
        except Exception as e:
            print(f"[SEND ERROR] {self.username}: {e}")
            self.disconnect()

    def disconnect(self):
        """Disconnect client cleanly."""
        if not self.alive:
            return

        self.alive = False
        print(f"[DISCONNECT] {self.username or self.address}")

        # Remove from server
        self.server.remove_client(self)

        # Notify others if authenticated
        if self.authenticated and self.username:
            leave_notice = encode_system_message(f"{self.username} left the chat.")
            self.server.broadcast(leave_notice)
            self.server.broadcast_udp_status("leave", self.username)

        # Close socket
        try:
            self.sock.close()
        except Exception:
            pass

    def close(self):
        """Force close connection."""
        self.alive = False
        try:
            self.sock.close()
        except Exception:
            pass
