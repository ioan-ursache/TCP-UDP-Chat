# TCP-UDP Chat Application

A cross-platform chat application demonstrating **hybrid TCP/UDP network architecture**:

- **TCP (Reliability)**: Chat messages, login, commands
- **UDP (Speed)**: Status broadcasts - join/leave/typing/presence indicators

## Features

### Core Functionality

**Username-based messaging** (not IP addresses)  
**Cross-platform support** (Java client ↔ Python server/client)  
**Reliable chat delivery** via TCP  
**Fast status updates** via UDP broadcast  
**JSON protocol** for interoperability  
**Multi-client support** with thread-safe operations  

### Status Features (UDP)

- **User joined** - Instant network broadcast
- **User left** - Disconnect notifications
- **Typing indicators** - Real-time typing status
- **Presence heartbeat** - Active user list (every 5s)

### TCP Channel (Port 5000)

**Purpose**: Reliable, ordered message delivery  
**Used for**:
- User login/authentication
- Chat messages
- Commands (/quit, /list)
- System notifications

### UDP Channel (Port 5001)

**Purpose**: Fast, connectionless broadcasts  
**Used for**:
- Join/leave notifications
- Typing indicators
- Presence heartbeats
- Real-time status updates

## Quick Start

### Prerequisites

**Server (Python)**:
- Python 3.7+
- No external dependencies (uses standard library)

**Client (Java)**:
- Java 11+
- Maven
- JavaFX (included in dependencies)

### Running the Server

```bash
cd server
python server.py
```

Expected Output:
```
[SERVER] TCP listening on 0.0.0.0:5000
[SERVER] UDP broadcasting on port 5001
```

### Running the Java Client

```bash
cd client
./mvnw clean javafx:run
```

Or on Windows:
```cmd
cd client
mvnw.cmd clean javafx:run
```
###### Though, I recommend just running it directly in IntelliJ

### Running the Python Test Client

```bash
cd server
python test_client.py
```

## Protocol Specification

See [PROTOCOL.md](PROTOCOL.md) for complete protocol documentation.

### Quick Reference

**TCP Messages** (JSON + newline):

```json
// Login
{"type": "login", "username": "Ioan"}

// Chat message
{"type": "message", "from": "Ioan", "text": "Hello!"}

// System notification
{"type": "system", "text": "Ioan joined the chat."}

// Command
{"type": "command", "cmd": "quit", "args": []}
```

**UDP Messages** (JSON, no newline):

```json
// Status update
{"type": "status", "status": "join", "user": "Ioan"}

// Presence heartbeat
{"type": "status", "status": "presence", "users": ["Ioan", "Ionut"]}
```

## Usage

### Java Client GUI

1. Enter server IP (default: `localhost`) - use ipconfig (Windows) or ifconfig (Linux), depending on where the server is hosted.
2. Enter port (default: `5000`)
3. Enter your username
4. Click "Conectare"
5. Type messages and press Enter

**Commands**:
- `/quit` - Disconnect
- `/list` - Show active users

### Python Client CLI

```bash
python test_client.py
```

Enter username when prompted, then type messages.

**Commands**:
- `/quit` - Disconnect
- `/list` - Show active users
- `/typing` - Send typing indicator

## Project Structure

```
TCP-UDP-Chat/
├── server/                 # Python server
│   ├── server.py          # Main server (TCP + UDP)
│   ├── client_handler.py  # Client connection handler
│   ├── chat_room.py       # Chat room management
│   ├── test_client.py     # Python test client
│   └── utils/
│       └── protocol.py    # Protocol definitions
│
├── client/                # Java client
│   ├── src/main/java/com/chat/
│   │   ├── client/
│   │   │   ├── TCPChatClient.java    # TCP client implementation
│   │   │   └── UDPStatusListener.java # UDP status receiver
│   │   └── controller/
│   │       └── ChatController.java   # JavaFX controller
│   └── pom.xml            # Maven dependencies
│
└── PROTOCOL.md            # Protocol documentation
```
###### - generated for ease of reference

## Testing

The following present some test scenarios that I've found interesting.

### Test Scenario 1: Cross-Platform Communication

1. Start Python server
2. Connect with Java client (User: Alice)
3. Connect with Python client (User: Bob)
4. Send messages between clients
5. Observe UDP status updates

### Test Scenario 2: Multiple Clients

1. Start server
2. Connect 2+ clients with different usernames
3. Send messages from any client
4. Verify all clients receive messages
5. Disconnect one client
6. Verify others receive leave notification

## Troubleshooting

### "Connection refused"

- Ensure server is running
- Check firewall settings
- Verify port 5000 is not in use

### UDP broadcasts not received

- Verify UDP port 5001 is open
- Check firewall allows UDP broadcast
- Ensure clients bind to correct UDP port

## Cross-Platform Compatibility

**Windows ↔ Linux** - Fully tested  
**Java ↔ Python** - Protocol-compliant

## Features Implemented

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built as a network programming learning project
- Demonstrates TCP vs UDP trade-offs in real applications
- Cross-platform compatibility showcase
