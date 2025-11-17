from tkinter.font import names


class ChatRoom:
    """Simple container for clients in a chat room."""
    def __init__(self, name):
        self.name = name
        self.clients = []

    def join(self, client_handler):
        self.clients.append(client_handler)

    def leave(self, client_handler):
        if client_handler in self.clients:
            self.clients.remove(client_handler)

    def broadcast(self, message, exclude = None):
        for client in self.clients:
            if client is not exclude:
                client.send(message)