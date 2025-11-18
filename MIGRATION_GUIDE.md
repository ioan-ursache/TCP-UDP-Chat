# Migration Guide: `addition` → `tcp-udp-enhancement`

## Overview of Changes

This guide helps you transition from the `addition` branch to the `tcp-udp-enhancement` branch.

## What Changed

### 🔴 BREAKING CHANGES

#### 1. Protocol Format

**Old (addition branch)**:
- Server used IP addresses as user identifiers
- Inconsistent message formats
- No login handshake

**New (tcp-udp-enhancement branch)**:
- **LOGIN required**: Clients must send `{"type":"login","username":"Name"}` immediately after connecting
- **Username-based**: All messages use usernames, not IP addresses
- **Strict JSON**: All TCP messages must be valid JSON + newline
- **Message types**: `login`, `message`, `command`, `system`

#### 2. Client Connection Flow

**Old**:
```python
# Just send messages immediately
sock.sendall(b"Hello\n")
```

**New**:
```python
# MUST send LOGIN first
login = json.dumps({"type": "login", "username": "Alice"})
sock.sendall((login + "\n").encode())

# Then send messages
msg = json.dumps({"type": "message", "from": "Alice", "text": "Hello"})
sock.sendall((msg + "\n").encode())
```

#### 3. Server Behavior

**Old**:
- Accepted any message immediately
- Used `address[0]:address[1]` as identifier

**New**:
- Waits for LOGIN (10s timeout)
- Rejects duplicate usernames
- Validates all JSON messages
- Broadcasts using usernames

### ✅ Non-Breaking Enhancements

- UDP status broadcasting (new feature)
- Better error handling
- Thread-safe operations
- Comprehensive logging

## Migration Steps

### For Existing Java Client Users

**Old Code** (addition branch):
```java
public boolean connect(String host, int port, String username) {
    socket = new Socket(host, port);
    output = new PrintWriter(socket.getOutputStream(), true);
    output.println(username);  // Just sent plain username
    // ...
}
```

**New Code** (tcp-udp-enhancement):
```java
public boolean connect(String host, int port, String username) {
    socket = new Socket(host, port);
    output = new PrintWriter(socket.getOutputStream(), true);
    
    // Send JSON LOGIN message
    JSONObject loginMsg = new JSONObject();
    loginMsg.put("type", "login");
    loginMsg.put("username", username);
    output.println(loginMsg.toString());
    // ...
}
```

### For Existing Python Client Users

**Old Code**:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))
# Start sending messages immediately
```

**New Code**:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))

# Send LOGIN first
login = json.dumps({"type": "login", "username": username})
sock.sendall((login + "\n").encode())

# Wait for welcome message
welcome = sock.recv(1024)
print(welcome.decode())

# Now send messages
```

### For Custom Client Implementations

If you built a custom client, update it to:

1. **Send LOGIN immediately after connecting**:
   ```json
   {"type": "login", "username": "YourName"}\n
   ```

2. **Format all messages as JSON**:
   ```json
   {"type": "message", "from": "YourName", "text": "Hello"}\n
   ```

3. **Parse incoming messages as JSON**:
   ```json
   {"type": "system", "text": "Welcome!"}\n
   {"type": "message", "from": "Alice", "text": "Hi!"}\n
   ```

4. **Optionally: Listen for UDP broadcasts on port 5001**

## Compatibility Matrix

| Client Version | Server: `addition` | Server: `tcp-udp-enhancement` |
|----------------|-------------------|------------------------------|
| `addition` | ✅ Works | ❌ **INCOMPATIBLE** |
| `tcp-udp-enhancement` | ❌ **INCOMPATIBLE** | ✅ Works |

**Recommendation**: Migrate all clients and server together.

## Testing Your Migration

### Quick Test

1. Start new server:
   ```bash
   git checkout tcp-udp-enhancement
   cd server
   python server.py
   ```

2. Connect with new Python client:
   ```bash
   python test_client.py
   # Enter username: TestUser
   ```

3. If successful, you should see:
   ```
   [CLIENT] Connected to 127.0.0.1:5000
   [CLIENT] Sent login: {"type":"login","username":"TestUser"}
   [SYSTEM] Welcome TestUser to the Lobby!
   ```

### Verify Old Client Fails Gracefully

1. Try connecting old client (from `addition` branch)
2. Server should reject after 10s:
   ```
   [REJECT] ('127.0.0.1', 12345) - No valid login received
   ```

## Common Migration Issues

### Issue 1: Client Immediately Disconnects

**Cause**: Not sending LOGIN message

**Fix**: Add LOGIN as first message after connecting

### Issue 2: Messages Not Appearing

**Cause**: Wrong JSON format or missing newline

**Fix**: Ensure format is `{"type":"message","from":"...","text":"..."}\n`

### Issue 3: "Invalid JSON" Warnings in Server

**Cause**: Sending non-JSON data

**Fix**: Wrap all messages in JSON structure

### Issue 4: Username Shows as IP Address

**Cause**: Server didn't receive valid LOGIN

**Fix**: Check LOGIN message format and ensure it's sent first

## Feature Comparison

| Feature | `addition` | `tcp-udp-enhancement` |
|---------|-----------|----------------------|
| **Connection** | Direct | Login required |
| **User ID** | IP:Port | Username |
| **Message Format** | Flexible | Strict JSON |
| **Protocol Docs** | None | PROTOCOL.md |
| **UDP Status** | Basic | Full (join/leave/typing/presence) |
| **Error Handling** | Minimal | Comprehensive |
| **Cross-Platform** | Partial | Fully tested |
| **Commands** | Limited | /quit, /list, /typing |

## Rollback Plan

If you need to rollback:

```bash
# Switch back to old branch
git checkout addition

# Restart server
cd server
python server.py

# Use old clients
```

**Note**: You cannot mix old and new clients.

## Gradual Migration Strategy

### Phase 1: Test Environment

1. Deploy `tcp-udp-enhancement` server on test machine
2. Update one client for testing
3. Verify all features work

### Phase 2: Parallel Deployment

1. Run old server on port 5000
2. Run new server on port 5002
3. Gradually move clients to new port

### Phase 3: Full Migration

1. Announce migration schedule
2. Switch all clients to new version
3. Shut down old server

## New Features to Leverage

### 1. UDP Status Listener (Java)

```java
UDPStatusListener udpListener = new UDPStatusListener(5001, this::handleStatus);
udpListener.start();
```

Receive real-time join/leave/typing notifications.

### 2. Commands

```bash
/list   # See active users
/quit   # Disconnect
/typing # Send typing indicator
```

### 3. Typing Indicators

Send when user is typing:
```python
client.send_typing_indicator()
```

## Protocol Documentation

See [PROTOCOL.md](PROTOCOL.md) for complete specification.

## Getting Help

If you encounter issues:

1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Review [TESTING.md](TESTING.md)
3. Enable debug logging (see SETUP_GUIDE.md)
4. Open GitHub issue with logs

## Summary

**Key Takeaways**:

1. ⚠️ **Breaking change**: LOGIN message now required
2. ⚠️ **Incompatible**: Cannot mix old/new clients
3. ✅ **Better**: Usernames, validation, error handling
4. ✅ **Tested**: Cross-platform, multi-client
5. ✅ **Documented**: Complete protocol spec

**Migration Time**: ~30 minutes per client

**Recommended**: Migrate all at once for clean transition.
