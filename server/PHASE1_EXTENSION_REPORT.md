# Main extension report for phase1 TCP-UDP Chat system

## TCP Reliable Message Delivery
- TCP by protocol ensures ordered, reliable delivery of all sent bytes.
- Application-level message reliability preserved by careful message framing (newline/JSON delimiter), decoding, and user/command parsing.
- Any client chat message, login, or command will always be received in order and completely or not at all.

## UDP Fast, Connectionless Status Broadcasting
- UDP socket added to server, set to broadcast for low-latency multicast.
- Server broadcasts status signals:
    - "join" and "leave": trigger on connection/disconnection, sent to all clients
    - "presence": periodic (5s) broadcast of active usernames
    - "typing": triggered when client sends _typing_ indicator
- Client UDP socket listens for broadcasts; output status updates on console.

## Example Usage
- Start server: `python3 server.py`
- Start client: `python3 test_client.py`
- Type messages for reliable chat over TCP
- Type `_typing_` to trigger typing status (UDP)
- Client receives both real-time chat and all status events

## Caveats & Recommendations
- UDP status broadcasts are best-effort and not guaranteed to land at each client, but are fast and lightweight.
- If upgrading to a GUI client, status events can be bound to indicators (typing, online lists, join/leave splash).
- Cross-platform/OS support retained, and backward compatibility for phase1 clients possible if status ignored.

## Further Extension Plans
- Add UDP presence detection and NAT traversal for internet-scale/lobbies
- Secure command authentication for TCP reliability and UDP status integrity
- More UDP signals (e.g., room lists, direct pings)

---

*This report documents the design and implementation choices of the TCP reliable messaging / UDP status architecture as completed, and is suitable for distribution, code review, or cross-team syncs.*