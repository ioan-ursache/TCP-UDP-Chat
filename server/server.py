import socket
import threading
import json
import time
from client_handler import ClientHandler
from chat_room import ChatRoom
from utils.protocol import encode_udp_status

HOST = "0.0.0.0"
PORT = 5000
UDP_PORT = 5001


class Server:
    def __init__(self, host=HOST, port=PORT, udp_port=UDP_PORT):
        self.host = host
        self.port = port
        self.udp_port = udp_port
        self.server_socket = None
        self.udp_socket = None
        self.clients = []  # List of ClientHandler instances
        self.usernames = {}  # username -> ClientHandler mapping
        self.lock = threading.Lock()
        self.lobby = ChatRoom("Lobby")
        self.running = False

    def start(self):
        """Start the TCP and UDP server."""
        self.running = True

        # Setup TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] TCP listening on {self.host}:{self.port}")

        # Setup UDP socket for broadcasts
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind((self.host, self.udp_port))
        print(f"[SERVER] UDP broadcasting on port {self.udp_port}")

        # Start UDP status broadcaster
        threading.Thread(target=self.udp_status_broadcaster, daemon=True).start()

        try:
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_sock, client_addr = self.server_socket.accept()
                    print(f"[CONNECT] {client_addr} connected (awaiting login)")

                    # Create handler for new client
                    handler = ClientHandler(client_sock, client_addr, self)
                    handler.start()

                    with self.lock:
                        self.clients.append(handler)

                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.stop()

    def register_username(self, username, handler):
        """Register a username. Returns True if successful, False if taken."""
        with self.lock:
            if username in self.usernames:
                return False
            self.usernames[username] = handler
            self.lobby.join(handler)
            print(f"[LOGIN] {username} logged in from {handler.address}")
            return True

    def broadcast(self, message, exclude_client=None):
        """Send a message to all authenticated clients via TCP."""
        if isinstance(message, str):
            message = message.encode("utf-8")
        if not message.endswith(b"\n"):
            message += b"\n"

        with self.lock:
            for client in self.clients:
                if client is not exclude_client and client.authenticated and client.alive:
                    try:
                        client.sock.sendall(message)
                    except Exception as e:
                        print(f"[BROADCAST ERROR] {client.username}: {e}")

    def broadcast_udp_status(self, status_type, username=None):
        """Broadcast status (join/leave/typing) to network via UDP."""
        try:
            msg = encode_udp_status(status_type, user=username)
            self.udp_socket.sendto(msg.encode("utf-8"), ("<broadcast>", self.udp_port))
        except Exception as e:
            print(f"[UDP ERROR] {e}")

    def udp_status_broadcaster(self):
        """Periodically broadcast presence of active users."""
        while self.running:
            time.sleep(5)
            with self.lock:
                users = [c.username for c in self.clients if c.authenticated and c.alive]

            if users:
                try:
                    msg = encode_udp_status("presence", users=users)
                    self.udp_socket.sendto(msg.encode("utf-8"), ("<broadcast>", self.udp_port))
                except Exception as e:
                    print(f"[UDP PRESENCE ERROR] {e}")

    def get_active_users(self):
        """Get list of active usernames."""
        with self.lock:
            return [c.username for c in self.clients if c.authenticated and c.alive]

    def remove_client(self, handler):
        """Remove disconnected client from server and lobby."""
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)
            if handler.username and handler.username in self.usernames:
                del self.usernames[handler.username]

        self.lobby.leave(handler)

    def stop(self):
        """Cleanly close server socket."""
        self.running = False

        # Close all client connections
        with self.lock:
            for client in self.clients[:]:
                client.close()

        # Close server sockets
        if self.server_socket:
            self.server_socket.close()
        if self.udp_socket:
            self.udp_socket.close()

        print("[SERVER] Closed.")


if __name__ == "__main__":
    server = Server()
    server.start()
