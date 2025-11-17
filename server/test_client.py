import socket
import threading
import json
import sys

SERVER = "127.0.0.1"
PORT = 5000
UDP_PORT = 5001
USERNAME = None


def listen(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(data.decode().strip())

def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.bind(("", UDP_PORT))
    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            msg = json.loads(data.decode("utf-8"))
            if msg["type"] == "status":
                status = msg["status"]
                if status == "typing":
                    print(f"[UDP] {msg['user']} is typing...")
                elif status == "join":
                    print(f"[UDP] {msg['user']} joined (broadcast).")
                elif status == "leave":
                    print(f"[UDP] {msg['user']} left (broadcast).")
                elif status == "presence":
                    print(f"[UDP] Active users: {', '.join(msg['users'])}")
        except Exception:
            pass

def main():
    global USERNAME
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    try:
        USERNAME = input("Username: ")
    except KeyboardInterrupt:
        sys.exit(0)
    threading.Thread(target=listen, args=(sock,), daemon=True).start()
    threading.Thread(target=udp_listener, daemon=True).start()
    try:
        while True:
            msg = input("> ")
            if msg == "/quit":
                sock.sendall(json.dumps({"text": "/quit"}).encode() + b"\n")
                break
            if msg == "_typing_":
                sock.sendall(json.dumps({"text": "_typing_"}).encode() + b"\n")
                continue
            sock.sendall(json.dumps({"text": msg}).encode() + b"\n")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
