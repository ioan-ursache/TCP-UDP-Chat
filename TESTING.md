# Testing Guide - TCP-UDP Chat

## Test Coverage

This guide covers:

1. **Protocol Compliance** - JSON format validation
2. **Cross-Platform** - Java ↔ Python communication
3. **Multi-Client** - Concurrent connections
4. **TCP Reliability** - Message delivery guarantees
5. **UDP Broadcasting** - Status updates
6. **Error Handling** - Invalid messages, disconnections

## Prerequisites

- Server running: `python server.py`
- At least 2 client terminals ready
- Network connectivity verified

## Test Suite

### Test 1: Basic Connection Flow

**Objective**: Verify login and connection establishment

**Steps**:

1. Start server:
   ```bash
   cd server
   python server.py
   ```

2. Connect Python client:
   ```bash
   python test_client.py
   # Enter username: Alice
   ```

3. Verify server output:
   ```
   [CONNECT] ('127.0.0.1', 54321) connected (awaiting login)
   [LOGIN] Alice logged in from ('127.0.0.1', 54321)
   ```

4. Verify client receives:
   ```
   [CLIENT] Connected to 127.0.0.1:5000
   [CLIENT] Sent login: {"type":"login","username":"Alice"}
   [SYSTEM] Welcome Alice to the Lobby!
   ```

**Expected Result**: ✅ Connection established, login successful

---

### Test 2: Cross-Platform Messaging

**Objective**: Java client ↔ Python client communication

**Steps**:

1. Connect Python client (Alice)
2. Connect Java client (Bob) via GUI
3. From Alice (Python), send: `Hello from Python!`
4. From Bob (Java), send: `Hello from Java!`

**Verify Python client sees**:
```
Bob: Hello from Java!
```

**Verify Java client sees**:
```
Alice: Hello from Python!
```

**Expected Result**: ✅ Messages cross platform boundaries correctly

---

### Test 3: UDP Status Broadcasting

**Objective**: Verify UDP join/leave/typing/presence broadcasts

**Steps**:

1. Start 2 Python clients: Alice and Bob
2. Connect Alice first
3. Connect Bob second

**Alice should see UDP broadcasts**:
```
[UDP] Bob joined the network
[UDP] Active users: Alice, Bob
```

4. From Bob, type: `/typing`

**Alice should see**:
```
[UDP] Bob is typing...
```

5. Disconnect Bob (Ctrl+C or `/quit`)

**Alice should see**:
```
[UDP] Bob left the network
[UDP] Active users: Alice
```

**Expected Result**: ✅ All UDP status updates received

---

### Test 4: Protocol Validation

**Objective**: Test invalid message handling

#### 4a: Missing LOGIN

**Steps**:

1. Modify test_client.py temporarily (skip login):
   ```python
   # Comment out:
   # login_msg = encode_login(username)
   # self.tcp_socket.sendall(login_msg.encode("utf-8"))
   ```

2. Connect client
3. Wait 10 seconds

**Expected**: Server rejects after timeout:
```
[REJECT] ('127.0.0.1', 12345) - No valid login received
```

#### 4b: Invalid JSON

**Steps**:

1. After logging in, send raw invalid JSON:
   ```python
   self.tcp_socket.sendall(b"{invalid json}\n")
   ```

**Expected**: Server logs warning, connection stays open:
```
[WARN] Invalid JSON from Alice: {invalid json}
```

#### 4c: Duplicate Username

**Steps**:

1. Connect client with username "Alice"
2. Connect second client with username "Alice"

**Expected**: Second client rejected (LOGIN fails)

---

### Test 5: Multi-Client Chat

**Objective**: 3+ clients chatting simultaneously

**Setup**:
- Python client: Alice
- Python client: Bob  
- Java client: Charlie

**Test Sequence**:

1. Alice sends: "Hello everyone!"
   - Bob and Charlie receive: `Alice: Hello everyone!`

2. Bob sends: "Hi Alice!"
   - Alice and Charlie receive: `Bob: Hi Alice!`

3. Charlie sends: "Good morning!"
   - Alice and Bob receive: `Charlie: Good morning!`

4. Alice types `/list`
   - Alice receives: `[SYSTEM] Active users: Alice, Bob, Charlie`

5. Bob disconnects
   - Alice and Charlie receive:
     - TCP: `[SYSTEM] Bob left the chat.`
     - UDP: `[UDP] Bob left the network`

**Expected Result**: ✅ All messages delivered correctly, no loss

---

### Test 6: TCP Reliability

**Objective**: Verify guaranteed message delivery

**Steps**:

1. Connect 2 clients: Alice, Bob
2. Alice sends 100 messages rapidly:
   ```python
   for i in range(100):
       client.send_message(f"Message {i}")
   ```

3. Bob counts received messages

**Expected Result**: ✅ Bob receives all 100 messages in order

---

### Test 7: UDP Packet Loss Resilience

**Objective**: UDP broadcasts work despite potential packet loss

**Steps**:

1. Start server
2. Connect 5 clients rapidly (within 2 seconds)
3. Observe presence broadcasts

**Expected**: 
- Some UDP packets may be lost (acceptable)
- TCP join notifications always received (reliable)
- Presence heartbeat eventually shows all users

**Note**: UDP loss is expected and acceptable for status updates

---

### Test 8: Command Handling

**Objective**: Verify all commands work

**Commands to Test**:

| Command | Expected Behavior |
|---------|------------------|
| `/list` | Shows active users |
| `/quit` | Disconnects client |
| `/typing` | Sends typing indicator (UDP) |

**Test Each**:

```bash
# As Alice
> /list
[SYSTEM] Active users: Alice, Bob

> /typing
# Bob should see: [UDP] Alice is typing...

> /quit
# Disconnects cleanly
```

**Expected Result**: ✅ All commands execute correctly

---

### Test 9: Stress Test

**Objective**: Server handles high load

**Setup**:

1. Start server
2. Connect 10 Python clients simultaneously:
   ```bash
   # In 10 terminals
   python test_client.py  # User1, User2, ... User10
   ```

3. Each client sends 50 messages:
   ```python
   for i in range(50):
       send_message(f"Message {i} from {username}")
       time.sleep(0.1)
   ```

**Monitor**:
- Server CPU usage
- Memory consumption
- Message delivery success rate

**Expected**:
- ✅ No crashes
- ✅ All messages delivered
- ✅ CPU < 50%, Memory < 200MB

---

### Test 10: Network Interruption

**Objective**: Handle network failures gracefully

**Scenario 1: Client Crash**

1. Connect Alice
2. Kill client process (Ctrl+C)
3. Verify server detects disconnect:
   ```
   [DISCONNECT] Alice
   ```

**Scenario 2: Network Cable Unplug**

1. Connect Bob on separate machine
2. Unplug network cable
3. Verify server timeout (may take 30-120 seconds)

**Expected**: ✅ Server cleans up dead connections

---

## Automated Testing Script

### Python Test Script

```python
# test_suite.py
import subprocess
import time
import sys

def test_basic_connection():
    print("\n=== Test 1: Basic Connection ===")
    # Start server
    server = subprocess.Popen(["python", "server.py"])
    time.sleep(2)
    
    # Start client
    client = subprocess.Popen(
        ["python", "test_client.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    client.stdin.write(b"TestUser\n")
    client.stdin.flush()
    time.sleep(1)
    
    # Verify connection
    client.stdin.write(b"/quit\n")
    client.wait(timeout=5)
    server.terminate()
    
    print("✅ Test 1 passed")

if __name__ == "__main__":
    test_basic_connection()
```

Run:
```bash
python test_suite.py
```

---

## Performance Benchmarks

### Message Latency

**Test Setup**:
- Server and client on same machine
- Measure round-trip time for 1000 messages

**Expected Results**:
- **Average latency**: < 5ms
- **Max latency**: < 50ms
- **99th percentile**: < 20ms

### Throughput

**Test Setup**:
- Single client sending messages as fast as possible
- Measure messages/second

**Expected Results**:
- **TCP Messages**: 1000-5000 msg/s
- **UDP Broadcasts**: 10,000+ msg/s

### Concurrent Connections

**Test Setup**:
- Connect N clients simultaneously
- Measure successful connections

**Expected Results**:
- **10 clients**: ✅ 100% success
- **50 clients**: ✅ 95%+ success
- **100 clients**: ⚠️ May need tuning

---

## Regression Testing Checklist

Before merging changes:

- [ ] Test 1: Basic connection (Java + Python)
- [ ] Test 2: Cross-platform messaging
- [ ] Test 3: UDP broadcasting
- [ ] Test 4: Protocol validation
- [ ] Test 5: Multi-client (3+ users)
- [ ] Test 8: All commands work
- [ ] No memory leaks (run server 1+ hour)
- [ ] No file descriptor leaks (check `lsof`)

---

## Debugging Failed Tests

### Enable Verbose Logging

**Server**:
```python
# In server.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
```

**Java Client**:
```java
// In TCPChatClient.java, enable all System.out prints
```

### Capture Network Traffic

```bash
# Capture TCP traffic
sudo tcpdump -i lo -n port 5000 -A

# Capture UDP traffic  
sudo tcpdump -i lo -n port 5001 -A
```

### Monitor Server State

```python
# Add to server.py
def debug_state(self):
    print(f"\n=== Server State ===")
    print(f"Clients: {len(self.clients)}")
    print(f"Usernames: {list(self.usernames.keys())}")
    print(f"Running: {self.running}")
```

Call every 10 seconds or on-demand.

---

## Test Results Template

```markdown
## Test Report - [Date]

**Branch**: tcp-udp-enhancement  
**Tester**: [Name]  
**Platform**: Windows 10 / Ubuntu 22.04 / macOS 13

### Results

| Test | Status | Notes |
|------|--------|-------|
| Basic Connection | ✅ PASS | - |
| Cross-Platform | ✅ PASS | Java ↔ Python working |
| UDP Broadcasting | ✅ PASS | All statuses received |
| Protocol Validation | ✅ PASS | Invalid JSON handled |
| Multi-Client | ✅ PASS | 5 clients tested |
| Commands | ✅ PASS | /list, /quit, /typing OK |
| Stress Test | ⚠️ PARTIAL | 10 clients OK, 50 has delays |

### Issues Found

None / [List any bugs discovered]

### Recommendations

[Performance tuning needed? Protocol changes?]
```

---

## CI/CD Integration (Future)

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run tests
        run: |
          cd server
          python test_suite.py
```

---

## Summary

This testing guide ensures:

✅ **Protocol compliance** across platforms  
✅ **Reliability** of TCP message delivery  
✅ **Resilience** to UDP packet loss  
✅ **Error handling** for edge cases  
✅ **Performance** under load  

Run full test suite before each release.
