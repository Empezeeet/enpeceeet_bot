import socket
import threading
import time
import select
import sys
import os
import json
from colorama import just_fix_windows_console
from termcolor import colored


log = lambda x: print(colored(f"[LOCAL] {x}", "blue"))
response = lambda x: print(colored(f"[SERVER] {x}", "cyan"))

just_fix_windows_console()
# Clear console and change title
os.system('cls' if os.name == 'nt' else 'clear')
os.system('title CS_Client')

# Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Nickname does nothing but password is required as basic authentication for server
NICKNAME = input(colored("[LOCAL] Enter nickname: ", "blue"))
PASSWORD = input(colored("[LOCAL] Enter password: ", "blue"))
server.connect(("192.168.0.110", 8080))
tdict = json.dumps({"type": "login", "nickname": NICKNAME, "password": PASSWORD})
server.sendall(bytes(tdict, encoding="utf-8"))
log("Your nickname: " + NICKNAME)
hello_response = server.recv(4096)
if hello_response.decode() == "Wrong password!":
    log('Wrong password!')
    input("Press any key to continue...")
    exit()
log("Connected to server.")
try:
    while True:

        uinput = input("> ")
        
        match uinput[0]:
            case ":":
                # Local command
                if uinput[1] == "q":
                    # Exit
                    server.send(":q".encode())
                    server.close()
                    log("Disconnected.")
                    input("Press any key to continue...")
                    sys.exit()
                break
            case "/":
                # Any message or command. Server will handle it.
                # Messages are useless.
                server.send(uinput.encode())
                
                response(server.recv(64))
except ConnectionResetError as cre:
    log("Remote host forcefully closed connection.")
except KeyboardInterrupt as ki:
    log('Use ":q" to exit.')
server.close()
