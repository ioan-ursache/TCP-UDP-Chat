"""Chat Protocol Definition

TCP Messages (Reliable):
- LOGIN: {"type": "login", "username": "<name>"}
- MESSAGE: {"type": "message", "from": "<username>", "text": "<content>"}
- COMMAND: {"type": "command", "cmd": "<command>", "args": [...]}
- SYSTEM: {"type": "system", "text": "<notification>"}

UDP Messages (Fast, connectionless):
- STATUS: {"type": "status", "status": "<type>", "user": "<username>"}
  Status types: "join", "leave", "typing", "presence"
- PRESENCE: {"type": "status", "status": "presence", "users": ["user1", "user2", ...]}
"""

import json

# TCP Message Types
MSG_LOGIN = "login"
MSG_MESSAGE = "message"
MSG_COMMAND = "command"
MSG_SYSTEM = "system"

# UDP Status Types
STATUS_JOIN = "join"
STATUS_LEAVE = "leave"
STATUS_TYPING = "typing"
STATUS_PRESENCE = "presence"


def encode_tcp_message(msg_type, **kwargs):
    """Encode a TCP message (reliable delivery)."""
    msg = {"type": msg_type}
    msg.update(kwargs)
    return json.dumps(msg) + "\n"


def encode_login(username):
    """Create LOGIN message."""
    return encode_tcp_message(MSG_LOGIN, username=username)


def encode_chat_message(username, text):
    """Create CHAT MESSAGE."""
    return encode_tcp_message(MSG_MESSAGE, **{"from": username, "text": text})


def encode_system_message(text):
    """Create SYSTEM message."""
    return encode_tcp_message(MSG_SYSTEM, text=text)


def encode_command(cmd, args=None):
    """Create COMMAND message."""
    return encode_tcp_message(MSG_COMMAND, cmd=cmd, args=args or [])


def encode_udp_status(status_type, user=None, users=None):
    """Encode a UDP status broadcast (fast, connectionless)."""
    msg = {"type": "status", "status": status_type}
    if user:
        msg["user"] = user
    if users:
        msg["users"] = users
    return json.dumps(msg)


def decode_message(raw):
    """Decode JSON message."""
    try:
        return json.loads(raw.strip())
    except (json.JSONDecodeError, AttributeError):
        return None


def validate_message(msg, required_fields):
    """Validate message has required fields."""
    if not isinstance(msg, dict):
        return False
    return all(field in msg for field in required_fields)
