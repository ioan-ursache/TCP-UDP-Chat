# TCP-UDP Chat Protocol

## Overview

This chat system uses a **hybrid TCP/UDP architecture**:

- **TCP (Reliable)**: Chat messages, login, commands, system notifications
- **UDP (Fast)**: Status broadcasts (join/leave/typing/presence)

## Protocol Specification

### TCP Messages (Port 5000)

All TCP messages are JSON-encoded, newline-terminated (`\n`).

#### 1. LOGIN (Client → Server)

Sent immediately after connection to register username.

```json
{
  "type": "login",
  "username": "Alice"
}
```

**Response**: Server sends SYSTEM message welcoming the user.

#### 2. MESSAGE (Bidirectional)

Chat message from user to server, or server broadcast to clients.

```json
{
  "type": "message",
  "from": "Alice",
  "text": "Hello everyone!"
}
```

#### 3. SYSTEM (Server → Client)

System notifications (join/leave/errors).

```json
{
  "type": "system",
  "text": "Alice joined the chat."
}
```

#### 4. COMMAND (Client → Server)

Special commands like `/quit`, `/list`, etc.

```json
{
  "type": "command",
  "cmd": "quit",
  "args": []
}
```

### UDP Messages (Port 5001)

All UDP messages are JSON-encoded (no newline required).

#### 1. STATUS - Join/Leave/Typing

Broadcast to all clients on the network.

```json
{
  "type": "status",
  "status": "join",  // or "leave", "typing"
  "user": "Alice"
}
```

#### 2. STATUS - Presence (Heartbeat)

Periodic broadcast of active users (every 5 seconds).

```json
{
  "type": "status",
  "status": "presence",
  "users": ["Alice", "Bob", "Charlie"]
}
```

## Message Flow

### Connection Flow

1. **Client connects to TCP port 5000**
2. Client sends `LOGIN` message with username
3. Server validates username and stores mapping
4. Server sends `SYSTEM` welcome message
5. Server broadcasts `SYSTEM` notification to other clients
6. Server broadcasts UDP `STATUS join` to network

### Chat Message Flow

1. Client sends `MESSAGE` via TCP
2. Server validates and relays to all connected clients
3. Messages include sender's username (not IP)

### Disconnect Flow

1. Client sends `COMMAND quit` or closes connection
2. Server broadcasts `SYSTEM` leave notification via TCP
3. Server broadcasts UDP `STATUS leave` to network
4. Server removes client from active list

## Protocol Rules

### TCP (Reliable Channel)

- **Guaranteed delivery** of all messages
- **Ordered delivery** within a connection
- **Error handling** with retries
- Used for critical data: login, chat messages, commands

### UDP (Fast Channel)

- **No delivery guarantee** - packets may be lost
- **No ordering** - messages may arrive out of order
- **Broadcast capable** - reaches all clients on network
- Used for non-critical status: typing indicators, presence updates

## Implementation Notes

### Java Client (TCPChatClient.java)

- Must send LOGIN message immediately after connecting
- Must encode all messages as JSON + newline
- Should parse incoming JSON and display appropriately

### Python Server (server.py)

- Must accept LOGIN before processing other messages
- Must map TCP connections to usernames
- Must broadcast using usernames, not IP addresses
- Must validate all incoming JSON messages

### Cross-Platform Compatibility

- **Encoding**: UTF-8 for all text
- **Line endings**: `\n` (Unix-style) for TCP messages
- **JSON**: Standard format, no trailing commas
- **Ports**: TCP 5000, UDP 5001 (configurable)

## Example Session

```
Client                          Server                          Other Clients
  |                               |                                    |
  |---TCP CONNECT--------------->|                                    |
  |                               |                                    |
  |---LOGIN {"username":"Alice"}->|                                    |
  |                               |                                    |
  |<--SYSTEM "Welcome Alice"------|                                    |
  |                               |--SYSTEM "Alice joined"------------>|
  |                               |--UDP STATUS join (broadcast)------>|
  |                               |                                    |
  |---MESSAGE "Hi!"-------------->|                                    |
  |                               |--MESSAGE from:Alice "Hi!"--------->|
  |                               |                                    |
  |---COMMAND quit--------------->|                                    |
  |                               |--SYSTEM "Alice left"-------------->|
  |                               |--UDP STATUS leave (broadcast)----->|
  |<--TCP CLOSE-------------------|                                    |
```

## Error Handling

### Invalid JSON

- Server logs warning
- Connection remains open
- No response sent

### Missing Required Fields

- Server sends SYSTEM error message
- Connection remains open

### Username Conflict

- Server rejects LOGIN
- Sends SYSTEM error message
- Client must reconnect with different username

## Future Extensions

- Private messaging: `{"type": "private", "to": "Bob", "text": "..."}`
- Room support: `{"type": "join_room", "room": "general"}`
- File transfer: Separate TCP port for binary data
- Encryption: TLS for TCP, DTLS for UDP
