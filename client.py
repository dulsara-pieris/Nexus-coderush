import socket
import threading
import time
import readline
import ipaddress
import sys

# ===== COLORS =====
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ===== UTILS =====
def is_public_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
        return not addr.is_private
    except:
        return False

def banner():
    print(GREEN + BOLD)
    print("=================================")
    print("     NEXUS RETRO CHAT TERMINAL    ")
    print("=================================")
    print(RESET)

# ===== START =====
banner()

username = input("username> ").strip()
if not username:
    print("username required")
    sys.exit(1)

SERVER_IP = input("relay ip> ").strip()
PORT = 5555

# ===== CONNECT =====
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((SERVER_IP, PORT))
except Exception as e:
    print(RED + "connection failed:" + RESET, e)
    sys.exit(1)

# ===== MODE DETECTION =====
if is_public_ip(SERVER_IP):
    MODE = "GLOBAL"
    VISIBILITY = "PUBLIC"
else:
    MODE = "LOCAL"
    VISIBILITY = "PRIVATE"

print(CYAN + "[CONNECTED TO RELAY NODE]" + RESET)
print(YELLOW + f"[MODE: {MODE} CHAT]" + RESET)
print(f"[RELAY IP: {SERVER_IP}]")
print(f"[RELAY VISIBILITY: {VISIBILITY}]")
print("[TYPE /help FOR COMMANDS]\n")

# ===== LISTENER =====
def listen():
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(GREEN + msg + RESET)
        except:
            break

threading.Thread(target=listen, daemon=True).start()

# ===== INPUT LOOP =====
while True:
    try:
        text = input("> ").strip()
    except KeyboardInterrupt:
        break

    if not text:
        continue

    if text == "/exit":
        print("disconnecting...")
        break

    if text == "/help":
        print("""
/help        show commands
/exit        quit chat
/me <msg>    action message
        """)
        continue

    timestamp = time.strftime("%H:%M")

    if text.startswith("/me "):
        msg = f"[{timestamp}] * {username} {text[4:]}"
    else:
        msg = f"[{timestamp}] {username}> {text}"

    try:
        sock.send(msg.encode())
    except:
        print("connection lost")
        break

sock.close()
print("bye 👋")
