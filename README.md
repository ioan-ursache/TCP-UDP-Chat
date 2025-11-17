# TCP-UDP-Chat
An introductory TCP/UDP server application for study purposes.

A cross-platform, multi-protocol chat system using **TCP** and **UDP**.

## Features
- Python Server (TCP chat + UDP presence)
- Java Client with GUI
- Cross-OS Support: Windows 11 & Ubuntu 24.04 as of 12.11.2025

## Communication
- **TCP:** text messages, room management
- **UDP:** presence announcements (join/leave)

## Project Layout
See `/server`, `/client`

## Setup
### Server (Python)
```bash
cd server
python3 server.py
```
### Test Client (Python)
```bash
cd server
python3 test_client.py
# /quit to test disconnect
```
