import socket, json, threading

SERVER = "127.0.0.1"
PORT = 5000

def listen(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(data.decode().strip())

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    threading.Thread(target=listen, args=(sock,), daemon=True).start()
    try:
        while True:
            msg = input("> ")
            if msg == "/quit":
                sock.sendall(json.dumps({"text": "/quit"}).encode() + b"\n")
                break
            sock.sendall(json.dumps({"text": msg}).encode() + b"\n")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
