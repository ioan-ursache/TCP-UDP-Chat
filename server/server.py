import socket
import threading
import json
from client_handler import ClientHandler
from chat_room import ChatRoom

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
        self.clients = []
        self.lock = threading.Lock()
        self.lobby = ChatRoom("Lobby")

    def start(self):
        """Start the TCP and UDP server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port}")

        # UDP socket for broadcasts
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind((self.host, self.udp_port))

        threading.Thread(target=self.udp_status_broadcaster, daemon=True).start()

        try:
            while True:
                client_sock, client_addr = self.server_socket.accept()
                print(f"[CONNECT] {client_addr} connected.")
                handler = ClientHandler(client_sock, client_addr, self)
                handler.start()
                with self.lock:
                    self.clients.append(handler)
                self.lobby.join(handler)
                self.broadcast_udp_status("join", handler.username)
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.stop()

    def broadcast(self, msg_dict, exclude_client=None):
        """Send a message to all clients in the lobby (TCP)."""
        message = json.dumps(msg_dict).encode("utf-8")
        with self.lock:
            for client in self.clients:
                if client is not exclude_client:
                    try:
                        client.sock.sendall(message + b"\n")
                    except Exception:
                        pass  # Ignore send failures for now

    def broadcast_udp_status(self, status_type, username):
        """Broadcast status (join/leave/typing/presence) to network via UDP."""
        msg = json.dumps({"type": "status", "status": status_type, "user": username})
        self.udp_socket.sendto(msg.encode("utf-8"), ("<broadcast>", self.udp_port))

    def udp_status_broadcaster(self):
        """Periodically broadcast presence of active users."""
        import time
        while True:
            with self.lock:
                users = [c.username for c in self.clients if c.alive]
            msg = json.dumps({"type": "status", "status": "presence", "users": users})
            self.udp_socket.sendto(msg.encode("utf-8"), ("<broadcast>", self.udp_port))
            time.sleep(5)

    def remove_client(self, handler):
        """Remove disconnected client from server and lobby."""
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)
        self.lobby.leave(handler)
        self.broadcast_udp_status("leave", handler.username)

    def stop(self):
        """Cleanly close server socket."""
        for client in self.clients:
            client.close()
        if self.server_socket:
            self.server_socket.close()
        if self.udp_socket:
            self.udp_socket.close()
        print("[SERVER] Closed.")

if __name__ == "__main__":
    server = Server()
    server.start()
