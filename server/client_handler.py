import threading
import json

class ClientHandler(threading.Thread):
    def __init__(self, sock, address, server):
        super().__init__(daemon=True)
        self.sock = sock
        self.address = address
        self.server = server
        self.username = f"{address[0]}:{address[1]}"
        self.alive = True

    def run(self):
        try:
            welcome_msg = {"type": "system", "text": f"Welcome {self.username} to the Lobby!"}
            self.sock.sendall((json.dumps(welcome_msg) + "\n").encode("utf-8"))
            join_notice = {"type": "system", "text": f"{self.username} joined the chat."}
            self.server.broadcast(join_notice, exclude_client=self)

            while self.alive:
                data = self.sock.recv(1024)
                if not data:
                    break
                messages = data.decode("utf-8").strip().splitlines()
                for msg in messages:
                    self.handle_message(msg)

        except Exception as e:
            print(f"[ERROR] {self.address}: {e}")
        finally:
            self.disconnect()

    def handle_message(self, raw_msg):
        try:
            msg = json.loads(raw_msg)
            text = msg.get("text", "")
            if text.startswith("/quit"):
                self.disconnect()
                return
            broadcast_msg = {"type": "message", "from": self.username, "text": text}
            self.server.broadcast(broadcast_msg, exclude_client=self)
        except json.JSONDecodeError:
            print(f"[WARN] Invalid message from {self.address}")

    def disconnect(self):
        if not self.alive:
            return
        self.alive = False
        print(f"[DISCONNECT] {self.address} disconnected.")
        self.server.remove_client(self)
        try:
            self.sock.close()
        except Exception:
            pass
        leave_notice = {"type": "system", "text": f"{self.username} left the chat."}
        self.server.broadcast(leave_notice)

    def close(self):
        """Force close connection."""
        self.alive = False
        try:
            self.sock.close()
        except Exception:
            pass
