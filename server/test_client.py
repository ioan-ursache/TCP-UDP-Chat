"""Python Test Client for TCP-UDP Chat

Demonstrates proper protocol usage:
- TCP for reliable messages (login, chat, commands)
- UDP for fast status updates (typing, presence)
"""

import socket
import threading
import json
import sys
import time
from utils.protocol import (
    encode_login, encode_chat_message, encode_command,
    decode_message, MSG_SYSTEM, MSG_MESSAGE
)

SERVER = "127.0.0.1"
PORT = 5000
UDP_PORT = 5001


class PythonChatClient:
    def __init__(self, server=SERVER, port=PORT, udp_port=UDP_PORT):
        self.server = server
        self.port = port
        self.udp_port = udp_port
        self.username = None
        self.tcp_socket = None
        self.udp_socket = None
        self.running = False

    def connect(self, username):
        """Connect to server with username."""
        try:
            self.username = username
            self.running = True

            # Setup TCP connection
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.server, self.port))
            print(f"[CLIENT] Connected to {self.server}:{self.port}")

            # Send LOGIN message
            login_msg = encode_login(username)
            self.tcp_socket.sendall(login_msg.encode("utf-8"))
            print(f"[CLIENT] Sent login as '{username}'")

            # Setup UDP socket for receiving broadcasts
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(("", self.udp_port))

            # Start receiver threads
            threading.Thread(target=self.tcp_receiver, daemon=True).start()
            threading.Thread(target=self.udp_receiver, daemon=True).start()

            return True

        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def tcp_receiver(self):
        """Receive TCP messages from server."""
        buffer = ""
        try:
            while self.running:
                data = self.tcp_socket.recv(4096)
                if not data:
                    print("[CLIENT] Server closed connection")
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        self.handle_tcp_message(line)

        except Exception as e:
            if self.running:
                print(f"[ERROR] TCP receiver: {e}")
        finally:
            self.disconnect()

    def handle_tcp_message(self, raw_msg):
        """Handle incoming TCP message."""
        msg = decode_message(raw_msg)
        if not msg:
            print(f"[TCP] {raw_msg}")  # Fallback for non-JSON
            return

        msg_type = msg.get("type")

        if msg_type == MSG_SYSTEM:
            print(f"[SYSTEM] {msg.get('text', '')}")
        elif msg_type == MSG_MESSAGE:
            sender = msg.get("from", "Unknown")
            text = msg.get("text", "")
            print(f"{sender}: {text}")
        else:
            print(f"[TCP] {raw_msg}")

    def udp_receiver(self):
        """Receive UDP status broadcasts."""
        try:
            while self.running:
                data, addr = self.udp_socket.recvfrom(1024)
                msg = decode_message(data.decode("utf-8"))

                if msg and msg.get("type") == "status":
                    status = msg.get("status")
                    if status == "typing":
                        user = msg.get("user", "Someone")
                        print(f"[UDP] {user} is typing...")
                    elif status == "join":
                        user = msg.get("user", "Someone")
                        print(f"[UDP] {user} joined the network")
                    elif status == "leave":
                        user = msg.get("user", "Someone")
                        print(f"[UDP] {user} left the network")
                    elif status == "presence":
                        users = msg.get("users", [])
                        print(f"[UDP] Active users: {', '.join(users)}")

        except Exception as e:
            if self.running:
                print(f"[ERROR] UDP receiver: {e}")

    def send_message(self, text):
        """Send chat message."""
        if not self.running:
            return

        try:
            # Encode as MESSAGE
            msg = encode_chat_message(self.username, text)
            self.tcp_socket.sendall(msg.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Send failed: {e}")

    def send_typing_indicator(self):
        """Send typing indicator (special message)."""
        if not self.running:
            return
        try:
            msg = encode_chat_message(self.username, "_typing_")
            self.tcp_socket.sendall(msg.encode("utf-8"))
        except Exception:
            pass

    def send_command(self, cmd, args=None):
        """Send command to server."""
        if not self.running:
            return
        try:
            msg = encode_command(cmd, args)
            self.tcp_socket.sendall(msg.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Command failed: {e}")

    def disconnect(self):
        """Disconnect from server."""
        if not self.running:
            return

        self.running = False
        print("[CLIENT] Disconnecting...")

        try:
            if self.tcp_socket:
                self.tcp_socket.close()
            if self.udp_socket:
                self.udp_socket.close()
        except Exception:
            pass

    def run_interactive(self):
        """Run interactive chat session."""
        print("\n=== Chat Commands ===")
        print("/quit - Disconnect")
        print("/list - Show active users")
        print("/typing - Send typing indicator")
        print("=====================\n")

        try:
            while self.running:
                msg = input("> ")
                msg = msg.strip()

                if not msg:
                    continue

                if msg.startswith("/"):
                    # Command
                    parts = msg[1:].split()
                    cmd = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []

                    if cmd == "quit":
                        self.send_command("quit")
                        break
                    elif cmd == "list":
                        self.send_command("list")
                    elif cmd == "typing":
                        self.send_typing_indicator()
                    else:
                        print(f"Unknown command: {cmd}")
                else:
                    # Regular message
                    self.send_message(msg)

        except KeyboardInterrupt:
            print("\n[CLIENT] Interrupted")
        finally:
            self.disconnect()


def main():
    """Main entry point."""
    print("=== Python TCP-UDP Chat Client ===")

    # Get username
    try:
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty")
            return
    except KeyboardInterrupt:
        print("\nCancelled")
        return

    # Connect
    client = PythonChatClient()
    if client.connect(username):
        # Run interactive session
        time.sleep(0.5)  # Give time for welcome message
        client.run_interactive()
    else:
        print("Failed to connect to server")


if __name__ == "__main__":
    main()
