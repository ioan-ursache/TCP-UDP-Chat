# Setup Guide - TCP-UDP Chat

## Complete Installation Instructions

### System Requirements

**Server (Python)**:
- Python 3.7 or higher
- Operating System: Windows, Linux, or macOS
- No external packages required

**Client (Java)**:
- Java Development Kit (JDK) 11 or higher
- Maven (included via wrapper)
- JavaFX (auto-downloaded by Maven)
- Operating System: Windows, Linux, or macOS

### Step 1: Clone Repository

```bash
git clone https://github.com/ioan-ursache/TCP-UDP-Chat.git
cd TCP-UDP-Chat
git checkout tcp-udp-enhancement
```

### Step 2: Setup Python Server

#### On Windows

```cmd
cd server
python --version  # Verify Python 3.7+
python server.py
```

#### On Linux/macOS

```bash
cd server
python3 --version  # Verify Python 3.7+
python3 server.py
```

**Expected Output**:
```
[SERVER] TCP listening on 0.0.0.0:5000
[SERVER] UDP broadcasting on port 5001
```

### Step 3: Setup Java Client

#### On Windows

```cmd
cd client
mvnw.cmd clean javafx:run
```

#### On Linux/macOS

```bash
cd client
chmod +x mvnw  # Make wrapper executable (first time only)
./mvnw clean javafx:run
```

**First Run**: Maven will download dependencies (~50MB). This takes 2-5 minutes.

### Step 4: Configure Firewall

#### Windows Firewall

1. Open "Windows Defender Firewall"
2. Click "Allow an app or feature"
3. Click "Change settings" → "Allow another app"
4. Add Python and Java
5. Allow on both Private and Public networks

**Or via Command Line** (Admin):

```cmd
netsh advfirewall firewall add rule name="Chat Server TCP" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Chat Server UDP" dir=in action=allow protocol=UDP localport=5001
```

#### Linux Firewall (UFW)

```bash
sudo ufw allow 5000/tcp
sudo ufw allow 5001/udp
sudo ufw reload
```

#### Linux Firewall (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=5001/udp
sudo firewall-cmd --reload
```

#### macOS Firewall

System Preferences → Security & Privacy → Firewall → Firewall Options  
Add Python and Java to allowed apps.

### Step 5: Test Connection

#### Local Test (Same Machine)

1. Start server: `python server.py`
2. Start client: `./mvnw javafx:run`
3. In client GUI:
   - Server IP: `localhost`
   - Port: `5000`
   - Username: `TestUser`
   - Click "Conectare"

#### Network Test (Different Machines)

1. **On Server Machine**:
   - Find IP address:
     - Windows: `ipconfig`
     - Linux/macOS: `ip addr` or `ifconfig`
   - Start server: `python server.py`

2. **On Client Machine**:
   - Start client
   - Enter server's IP address (e.g., `192.168.1.100`)
   - Port: `5000`
   - Username: `ClientUser`
   - Click "Conectare"

## Running Multiple Clients

### Multiple Java Clients

**Terminal 1**:
```bash
./mvnw javafx:run
```

**Terminal 2** (separate terminal):
```bash
./mvnw javafx:run
```

Each client needs a unique username.

### Python Client + Java Client

**Terminal 1** (Python):
```bash
cd server
python test_client.py
# Enter username: Alice
```

**Terminal 2** (Java):
```bash
cd client
./mvnw javafx:run
# Enter username: Bob
```

## Environment-Specific Setup

### Corporate Network / Behind Proxy

If Maven fails to download dependencies:

```bash
# Set proxy in ~/.m2/settings.xml
<settings>
  <proxies>
    <proxy>
      <host>proxy.company.com</host>
      <port>8080</port>
    </proxy>
  </proxies>
</settings>
```

### Linux: Java not found

```bash
# Install OpenJDK
sudo apt install openjdk-11-jdk  # Debian/Ubuntu
sudo dnf install java-11-openjdk # Fedora/RHEL

# Verify
java -version
```

### Windows: Python not in PATH

1. Search "Environment Variables" in Start Menu
2. Edit "Path" under User Variables
3. Add Python installation directory (e.g., `C:\Python39`)
4. Restart terminal

## Troubleshooting Setup

### Issue: "Port 5000 already in use"

**Windows**:
```cmd
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Linux/macOS**:
```bash
lsof -i :5000
kill -9 <PID>
```

**Change port** (if needed):
```python
# In server.py
PORT = 5002  # Use different port
```

### Issue: "Module not found" in Python

The project uses only standard library - no `pip install` needed.  
If error persists, verify Python 3.7+:

```bash
python --version
# or
python3 --version
```

### Issue: Maven download fails

```bash
# Clear Maven cache and retry
rm -rf ~/.m2/repository
./mvnw clean install
```

### Issue: JavaFX not loading on Linux

```bash
# Install JavaFX dependencies
sudo apt install openjfx  # Debian/Ubuntu
```

### Issue: "Connection refused" between machines

1. **Verify network connectivity**:
   ```bash
   ping <server_ip>
   ```

2. **Test port connectivity**:
   ```bash
   # On client machine
   telnet <server_ip> 5000
   # or
   nc -zv <server_ip> 5000
   ```

3. **Check server binding**:
   - Server must bind to `0.0.0.0`, not `127.0.0.1`
   - Verify in server.py: `HOST = "0.0.0.0"`

4. **Check firewall** (see Step 4)

## Performance Tuning

### For High-Traffic Scenarios

**Increase thread pool** (server.py):
```python
self.server_socket.listen(50)  # Increase from 5
```

**Adjust buffer sizes** (client_handler.py):
```python
data = self.sock.recv(8192)  # Increase from 4096
```

### For Low-Latency Networks

**Reduce UDP heartbeat interval** (server.py):
```python
time.sleep(2)  # Reduce from 5 seconds
```

## Development Setup

### IDE Configuration

#### IntelliJ IDEA (Java)

1. Open `client` folder as Maven project
2. File → Project Structure → SDK: Java 11+
3. Enable annotation processing
4. Run configuration: Main class = `com.chat.Launcher`

#### VS Code (Python)

1. Open `server` folder
2. Install Python extension
3. Select Python interpreter (3.7+)
4. Run: F5 or `python server.py`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature tcp-udp-enhancement

# Make changes, commit
git add .
git commit -m "Add feature"

# Push to remote
git push origin feature/my-feature
```

## Deployment

### Deploy Server on Linux VPS

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip

# Clone repository
git clone https://github.com/ioan-ursache/TCP-UDP-Chat.git
cd TCP-UDP-Chat/server

# Run with systemd (auto-restart)
sudo nano /etc/systemd/system/chatserver.service
```

**chatserver.service**:
```ini
[Unit]
Description=TCP-UDP Chat Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/TCP-UDP-Chat/server
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable chatserver
sudo systemctl start chatserver
sudo systemctl status chatserver
```

### Package Java Client as Executable

```bash
cd client
./mvnw clean package

# Creates: target/client-1.0-SNAPSHOT.jar

# Run:
java -jar target/client-1.0-SNAPSHOT.jar
```

## Next Steps

After setup:

1. Read [PROTOCOL.md](PROTOCOL.md) to understand message format
2. Try connecting multiple clients
3. Test cross-platform (Java ↔ Python)
4. Experiment with commands (`/list`, `/quit`)
5. Monitor server logs for debugging

## Support

If you encounter issues:

1. Check server console for errors
2. Enable debug logging (see below)
3. Verify protocol compliance
4. Test with Python client first (simpler)

### Enable Debug Logging

**Server** (server.py):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Java Client** (ChatController.java):
```java
System.setProperty("javafx.verbose", "true");
```
