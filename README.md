# TCP-UDP Chat Application

A cross-platform chat application demonstrating **hybrid TCP/UDP network architecture**:

- **TCP (Reliable)**: Chat messages, login, commands - guaranteed delivery
- **UDP (Fast)**: Status broadcasts - join/leave/typing/presence indicators

## Features

### Core Functionality

✅ **Username-based messaging** (not IP addresses)  
✅ **Cross-platform support** (Java client ↔ Python server/client)  
✅ **Reliable chat delivery** via TCP  
✅ **Fast status updates** via UDP broadcast  
✅ **JSON protocol** for interoperability  
✅ **Multi-client support** with thread-safe operations  

### Status Features (UDP)

- 🟢 **User joined** - Instant network broadcast
- 🔴 **User left** - Disconnect notifications
- ✏️ **Typing indicators** - Real-time typing status
- 👥 **Presence heartbeat** - Active user list (every 5s)

## Architecture

```
┌─────────────┐         TCP (5000)          ┌─────────────┐
│   Client    │◄──────────────────────────►│   Server    │
│  (Java/Py)  │   Reliable Messages         │  (Python)   │
└─────────────┘                              └─────────────┘
       ▲                                            │
       │              UDP (5001)                    │
       └────────────────────────────────────────────┘
              Fast Status Broadcasts
```

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

Output:
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
{"type": "login", "username": "Alice"}

// Chat message
{"type": "message", "from": "Alice", "text": "Hello!"}

// System notification
{"type": "system", "text": "Alice joined the chat."}

// Command
{"type": "command", "cmd": "quit", "args": []}
```

**UDP Messages** (JSON, no newline):

```json
// Status update
{"type": "status", "status": "join", "user": "Alice"}

// Presence heartbeat
{"type": "status", "status": "presence", "users": ["Alice", "Bob"]}
```

## Usage

### Java Client GUI

1. Enter server IP (default: `localhost`)
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

## Testing

### Test Scenario 1: Cross-Platform Communication

1. Start Python server
2. Connect with Java client (User: Alice)
3. Connect with Python client (User: Bob)
4. Send messages between clients
5. Observe UDP status updates

### Test Scenario 2: Multiple Clients

1. Start server
2. Connect 3+ clients with different usernames
3. Send messages from any client
4. Verify all clients receive messages
5. Disconnect one client
6. Verify others receive leave notification

### Test Scenario 3: Protocol Validation

1. Connect client without sending LOGIN
   - ✅ Server should reject after timeout
2. Send invalid JSON
   - ✅ Server should log warning, continue
3. Send duplicate username
   - ✅ Server should reject LOGIN

## Troubleshooting

### "Connection refused"

- Ensure server is running
- Check firewall settings
- Verify port 5000 is not in use

### "Address already in use" (WinError 10048)

```bash
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# On Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### Messages not appearing

- Check protocol format (see PROTOCOL.md)
- Verify JSON is valid
- Ensure newline termination for TCP
- Check server logs for errors

### UDP broadcasts not received

- Verify UDP port 5001 is open
- Check firewall allows UDP broadcast
- Ensure clients bind to correct UDP port

## Cross-Platform Compatibility

✅ **Windows ↔ Linux** - Fully tested  
✅ **Java ↔ Python** - Protocol-compliant  
✅ **IPv4 networks** - Full support  
⚠️ **IPv6** - Not yet tested  

## Features Implemented

### Phase 1 (Completed)

- [x] TCP reliable message delivery
- [x] UDP fast status broadcasting
- [x] Username-based messaging
- [x] Protocol enforcement across platforms
- [x] Cross-platform testing (Java/Python, Windows/Linux)
- [x] Proper connection/disconnection handling
- [x] Thread-safe client management
- [x] JSON protocol with validation

### Future Enhancements

- [ ] Private messaging
- [ ] Multiple chat rooms
- [ ] Message history
- [ ] File transfer
- [ ] TLS/DTLS encryption
- [ ] User authentication
- [ ] GUI improvements (emoji, formatting)

## Development

### Running Tests

**Server tests**:
```bash
cd server
python -m pytest tests/  # (when test suite is added)
```

**Client tests**:
```bash
cd client
./mvnw test
```

### Building Java Client JAR

```bash
cd client
./mvnw clean package
java -jar target/client-1.0-SNAPSHOT.jar
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built as a network programming learning project
- Demonstrates TCP vs UDP trade-offs in real applications
- Cross-platform compatibility showcase

## Version History

### v2.0.0 (tcp-udp-enhancement branch)

- ✨ Implemented username-based messaging
- ✨ Added strict JSON protocol
- ✨ UDP status broadcasting
- 🐛 Fixed message validation issues
- 🐛 Fixed cross-platform compatibility
- 📚 Complete protocol documentation

### v1.0.0 (addition branch)

- ✅ Basic TCP/UDP structure
- ✅ Initial Java and Python clients
- ✅ Connection establishment
