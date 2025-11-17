import socket
import threading
import json
from client_handler import ClientHandler
from chat_room import ChatRoom

HOST = "0.0.0.0"
PORT = 5000

class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.lock = threading.Lock()
        self.lobby = ChatRoom("Lobby")

    def start(self):
        """Start the TCP server and accept incoming clients."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port}")

        try:
            while True:
                client_sock, client_addr = self.server_socket.accept()
                print(f"[CONNECT] {client_addr} connected.")
                handler = ClientHandler(client_sock, client_addr, self)
                handler.start()
                with self.lock:
                    self.clients.append(handler)
                self.lobby.join(handler)
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.stop()

    def broadcast(self, msg_dict, exclude_client=None):
        """Send a message to all clients in the lobby."""
        message = json.dumps(msg_dict).encode("utf-8")
        with self.lock:
            for client in self.clients:
                if client is not exclude_client:
                    try:
                        client.sock.sendall(message + b"\n")
                    except Exception:
                        pass  # Ignore send failures for now

    def remove_client(self, handler):
        """Remove disconnected client from server and lobby."""
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)
        self.lobby.leave(handler)

    def stop(self):
        """Cleanly close server socket."""
        for client in self.clients:
            client.close()
        if self.server_socket:
            self.server_socket.close()
        print("[SERVER] Closed.")

if __name__ == "__main__":
    server = Server()
    server.start()
