# Quick Reference - TCP-UDP Chat

## Commands Cheat Sheet

### Start Server

```bash
cd server
python server.py
```

### Start Java Client

```bash
cd client
./mvnw clean javafx:run   # Linux/macOS
mvnw.cmd clean javafx:run  # Windows
```

### Start Python Client

```bash
cd server
python test_client.py
```

## In-Chat Commands

| Command | Description | Example |
|---------|-------------|----------|
| `/quit` | Disconnect from server | `/quit` |
| `/list` | Show active users | `/list` |
| `/typing` | Send typing indicator (Python) | `/typing` |

## Protocol Quick Reference

### TCP Messages (Port 5000)

**LOGIN** (Client → Server):
```json
{"type": "login", "username": "Alice"}
```

**MESSAGE** (Bidirectional):
```json
{"type": "message", "from": "Alice", "text": "Hello!"}
```

**SYSTEM** (Server → Client):
```json
{"type": "system", "text": "Alice joined the chat."}
```

**COMMAND** (Client → Server):
```json
{"type": "command", "cmd": "list", "args": []}
```

### UDP Messages (Port 5001)

**STATUS** (Server → All):
```json
{"type": "status", "status": "join", "user": "Alice"}
{"type": "status", "status": "leave", "user": "Bob"}
{"type": "status", "status": "typing", "user": "Charlie"}
```

**PRESENCE** (Server → All, every 5s):
```json
{"type": "status", "status": "presence", "users": ["Alice", "Bob"]}
```

## Code Snippets

### Python: Connect to Server

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5000))

# Send LOGIN
login = json.dumps({"type": "login", "username": "Alice"})
sock.sendall((login + "\n").encode())

# Send message
msg = json.dumps({"type": "message", "from": "Alice", "text": "Hi!"})
sock.sendall((msg + "\n").encode())
```

### Python: Listen for UDP

```python
import socket
import json

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(("", 5001))

while True:
    data, addr = udp_sock.recvfrom(1024)
    msg = json.loads(data.decode())
    print(f"UDP: {msg}")
```

### Java: Send Message

```java
import org.json.JSONObject;

JSONObject msg = new JSONObject();
msg.put("type", "message");
msg.put("from", username);
msg.put("text", "Hello!");

output.println(msg.toString());
```

## Troubleshooting

### Connection Refused

```bash
# Check server is running
netstat -an | grep 5000

# Start server
python server.py
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Messages Not Appearing

1. Check JSON format (valid JSON + `\n`)
2. Verify LOGIN was sent first
3. Check server logs for errors

### UDP Not Working

1. Check firewall allows UDP 5001
2. Verify client binds to port 5001
3. Test with Python client first

## File Structure

```
TCP-UDP-Chat/
├── server/
│   ├── server.py              # Main server
│   ├── client_handler.py      # Client logic
│   ├── test_client.py         # Python client
│   └── utils/protocol.py      # Protocol definitions
│
├── client/
│   ├── src/main/java/com/chat/
│   │   ├── client/TCPChatClient.java
│   │   ├── client/UDPStatusListener.java
│   │   └── controller/ChatController.java
│   └── pom.xml
│
├── PROTOCOL.md            # Full protocol spec
├── README.md              # Project overview
├── SETUP_GUIDE.md         # Installation guide
└── TESTING.md             # Test suite
```

## Ports

| Port | Protocol | Purpose |
|------|----------|----------|
| 5000 | TCP | Chat messages, login, commands |
| 5001 | UDP | Status broadcasts |

## Environment Variables

```bash
# Optional: Change default ports
export CHAT_TCP_PORT=5000
export CHAT_UDP_PORT=5001
```

## Logs

### Server Logs

```
[SERVER] TCP listening on 0.0.0.0:5000
[SERVER] UDP broadcasting on port 5001
[CONNECT] ('127.0.0.1', 54321) connected (awaiting login)
[LOGIN] Alice logged in from ('127.0.0.1', 54321)
[DISCONNECT] Alice
```

### Client Logs

```
[CLIENT] Connected to 127.0.0.1:5000
[CLIENT] Sent login: {"type":"login","username":"Alice"}
[SYSTEM] Welcome Alice to the Lobby!
[UDP] Bob joined the network
[UDP] Active users: Alice, Bob
```

## Performance Tips

### Server

- Increase `listen()` backlog for many clients:
  ```python
  self.server_socket.listen(50)  # Default: 5
  ```

- Adjust buffer size:
  ```python
  data = self.sock.recv(8192)  # Default: 4096
  ```

### Client

- Batch messages when sending many:
  ```python
  # Instead of 100 send() calls
  messages = "\n".join([msg1, msg2, ...]) + "\n"
  sock.sendall(messages.encode())
  ```

## Security Considerations

⚠️ **Current Version**: No encryption or authentication

**For production**:

1. Use TLS for TCP:
   ```python
   import ssl
   context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
   secure_sock = context.wrap_socket(sock, server_side=True)
   ```

2. Validate usernames (prevent injection)
3. Rate limit messages
4. Add password authentication

## Testing Checklist

- [ ] Server starts without errors
- [ ] Python client connects
- [ ] Java client connects
- [ ] Messages sent between clients
- [ ] UDP broadcasts received
- [ ] `/list` command works
- [ ] `/quit` disconnects cleanly
- [ ] Multiple clients (3+) work

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Server not running | Start server |
| `Address already in use` | Port 5000 occupied | Kill process or change port |
| `Invalid JSON` | Malformed message | Check JSON syntax |
| `No valid login received` | Missing LOGIN | Send LOGIN first |
| `Unknown command` | Invalid command | Use `/list`, `/quit`, `/typing` |

## Version Info

**Branch**: `tcp-udp-enhancement`  
**Protocol Version**: 2.0  
**Python**: 3.7+  
**Java**: 11+  
**Compatible with**: Windows, Linux, macOS

## Links

- [Full Documentation](README.md)
- [Protocol Specification](PROTOCOL.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Testing Guide](TESTING.md)
- [Migration Guide](MIGRATION_GUIDE.md)

## Support

**Issues**: [GitHub Issues](https://github.com/ioan-ursache/TCP-UDP-Chat/issues)  
**Discussions**: [GitHub Discussions](https://github.com/ioan-ursache/TCP-UDP-Chat/discussions)
