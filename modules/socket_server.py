import socket
import time
import datetime
from termcolor import colored
import random
import threading

class CommandServer:
    
    def __init__(self, IP, PORT, logger):
        self.logger = logger
        self.start_time = time.time()
        self.log = lambda msg: self.logger.log("CMDS", colored(msg, "blue"))
        self.log("Initializing Command Server...")
        self.IP = IP
        self.PORT = PORT
        self.passw = f"{random.randint(100000, 999999)}-{random.randint(100000, 999999)}"
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
        conn.send("Welcome!")
        while True:
            try:
                message = conn.recv(4096)
                if message:
                    self.log(f"<{addr[0]}> {message}")
                    self.broadcast(f"<{addr[0]}> {message}", addr) 
                else:
                    self.log(f"{addr[0]} disconnected.")
                    self.remove(conn)
            except:
                continue
    def broadcast(self, message, connection):
        for clients in self.connected_clients:
            if clients!=connection:
                try:
                    clients.send(message)
                except:
                    clients.close()
    
                    # if the link is broken, we remove the client
                    self.remove(clients)
    def remove(self, connection):
        if connection in self.connected_clients:
            self.connected_clients.remove(connection)
 
    def run(self):
        
        while True:
            conn, addr = self.server.accept()
            self.connected_clients.append(conn)
            self.log(f"{addr[0]} connected.")
            thread = threading.Thread(self.clientThread, args=(conn, addr), name=f"ClientThread-{addr[0]}")
            thread.start()
            self.thread[addr[0]] = thread
            
        
