import socket
import time
import datetime
from termcolor import colored
import random
import threading
import json
import modules.exceptions as cexceptions

socket_commands = None

with open("configs/socket_commands.json", "r") as file:
    socket_commands = json.load(file)


class CommandServer:
    
    def __init__(self, IP, PORT, handler, password):
        self.handler = handler
        self.logger = handler.logger
        self.start_time = time.time()
        self.log = lambda msg: self.logger.log("CMDS", colored(msg, "blue"))
        self.log("Initializing Command Server...")
        self.IP = IP
        self.PORT = PORT
        self.passw = password
        self.log("Created Password: " + self.passw)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((str(IP), int(PORT)))
        
        
        
        
        self.server.listen(2)
        self.connected_clients = []
        self.threads = {}
        self.log("Command Server initialized.")
        self.mainThread = threading.Thread(target=self.run, name="CommandServerMainThread")
        self.mainThread.start()
    def clientThread(self, conn, addr):
            conn.send("Welcome!".encode())
            while True:
                try:
                    message = conn.recv(4096)
                    if message is None:
                        self.log(f"{addr[0]} disconnected. MESSAGE IS NONE")
                        self.remove(conn)
                        break
                    if message == b'':
                        continue
                    self.log(f"<{addr[0]}> {message}")
                    if message.decode() == ":q":
                        self.log(f"{addr[0]} disconnected.")
                        self.remove(conn)
                        break
                    if message.decode()[0] == "/":
                        # This is command
                        # Available commands are in readme.md 
                        
                        # Check is command in self.socket_commands
                        
                        for index, cmd_obj in enumerate(socket_commands["cmds"]):
                            if cmd_obj['name'] == message.decode()[1:]:
                                global command
                                command = (cmd_obj["name"], index)
                                break
                            if index == len(socket_commands["cmds"]) - 1:
                                conn.send("Wrong command!".encode())
                                raise cexceptions.WrongCommand("Wrong command!")
                        match command[0]:
                            case "online":
                                # Set bot's status to online
                                conn.send("Making bot online...".encode())
                                self.handler.make_online()
                                
                            case "dnd":
                                # Set bot's status to dnd
                                conn.send("Making bot DND...".encode())
                                pass
                                
                            case "stop":
                                conn.send("Making bot stop.".encode())
                                pass
                                
                            case "uptime":
                                # Get bot's uptime
                                with open("configs/rundata.json", "r") as file:
                                    start_time = json.load(file)['start_timestamp']
                                    conn.send(f"Uptime: {time.time() - start_time}s".encode())
                            case _:
                                raise cexceptions.UnknownError("Unknown error!")    
                except Exception as e:
                    self.log(f"Exception occured: {e}\n")
                    continue
    def remove(self, connection):
        if connection in self.connected_clients:
            self.connected_clients.remove(connection)
 
    def run(self):
        
        while True:
            # Accept connection
            conn, addr = self.server.accept()
            # Check password provided by client
            # If true accept client else close connction
            try:
                global hello
                hello = conn.recv(184)
                hello = json.loads(hello.decode())
                if hello["password"] != self.passw:
                    conn.send("Wrong password!".encode())
                    conn.close()
                    del conn, addr, hello
                    continue
            except Exception as e:
                self.log(f"Error: \n{e}\n")
                
            
            self.connected_clients.append(conn)
            self.log(f"{addr[0]} connected. ({hello['nickname']})")
            thread = threading.Thread(target=self.clientThread, args=(conn, addr), name=f"ClientThread-{addr[0]}")
            thread.start()
            self.threads[addr[0]] = thread
            del conn, addr        

