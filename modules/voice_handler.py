# Author: Empezeeet
# This will not work below v3 Version



import requests
import websocket
import json
import datetime
import random
import random
from termcolor import colored
import time
import threading
import sys
import nacl.utils
import nacl.secret
import socket



raise Exception("This module is discontinued. See more info in file")
# This file was discontinued because i cant make it now.
# I should delete it but i can use reworked version of it in future.
#
#               ██████╗░██╗░██████╗░█████╗░░█████╗░███╗░░██╗████████╗██╗███╗░░██╗██╗░░░██╗███████╗██████╗░
#               ██╔══██╗██║██╔════╝██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██║████╗░██║██║░░░██║██╔════╝██╔══██╗
#               ██║░░██║██║╚█████╗░██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░██║██╔██╗██║██║░░░██║█████╗░░██║░░██║
#               ██║░░██║██║░╚═══██╗██║░░██╗██║░░██║██║╚████║░░░██║░░░██║██║╚████║██║░░░██║██╔══╝░░██║░░██║
#               ██████╔╝██║██████╔╝╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░██║██║░╚███║╚██████╔╝███████╗██████╔╝
#               ╚═════╝░╚═╝╚═════╝░░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝╚═════╝░



class VoiceHandler(threading.Thread):
    def __init__(self, logger, token, guild_id, endpoint, session_id):
        self.start_time = time.time()
        logger.log("VC ", colored("[0/7] Initialzing Voice Handler", "cyan"))
        self.connected = False
        self.logger = logger
        
        self.socket = websocket.WebSocket()
        self.endpoint = endpoint
        logger.log("VC ", colored("[1/7] Establisihing Connection with WebSocket endpoint...", "cyan"))
        self.socket.connect(f"wss://{endpoint}/?v=4&encoding=json")
        self.token = token
        self.guild_id = guild_id
        logger.log("VC ", colored("[2/7] Sending Hello Event", "cyan"))
        # Send Hello
        hello_event = json.loads(self.socket.recv())
        with open("configs/rundata.json", "r+") as file:
            prev_file = json.load(file)
            
            prev_file['vc_heartbeat_interval'] = hello_event['d']['heartbeat_interval']
            self.heartbeat_interval = hello_event['d']['heartbeat_interval']/1000
            
            # Clear file content
            file.seek(0)
            file.truncate()
            
            
            file.write(json.dumps(prev_file, indent=4))
            logger.log("VC ", colored(f"[3/7] Starting VC_HEARTBEAT Thread @ {hello_event['d']['heartbeat_interval']/1000}", "cyan"))
            self.heartbeat_thread = threading.Thread(target=self.start_heartbeating, args=(self.heartbeat_interval, self.socket), name="VC_Heartbeat")
            self.heartbeat_thread.start()
            self.logger.log("VC ", colored("[4/8] Heartbeat Thread Started", "cyan"))
        logger.log("VC ", colored("[5/8] Successfully saved data to rundata.json", "cyan"))
        with open("configs/rundata.json", "r") as file:
            data = json.load(file)
            identify = {    
                "op": 0,
                "d": {
                    "server_id": guild_id,
                    "user_id": data["user"]["id"],
                    "session_id": session_id,
                    "token": self.token
                }
            }
            self.socket.send(json.dumps(identify))
            logger.log("VC ", colored("[6/8] Successfully sent Identify Event", "cyan"))
            
        # Wait for ready
        logger.log("VC ", colored("[7/8] Waiting for Ready Event", "cyan"))
        ready_event = json.loads(self.socket.recv())
        self.modes = ready_event['d']['modes']
        self.ip_and_port = (ready_event['d']['ip'], ready_event['d']['port'])
        logger.log("VC ", colored("[8/8] Ready Event received.", "cyan"))
        
        # Establish UDP Connection
        self.socket.send(json.dumps(
            {
                "op": 1,
                "d":{
                    "protocol":"udp",
                    "data":{
                        "address":self.ip_and_port[0],
                        "port":self.ip_and_port[1],
                        "mode":"xsalsa20_poly1305"
                    }
                }
            }
        ))
        # Wait for Session Description
        logger.log('VC ', colored("Waiting for Session Description...", "cyan"))
        session_desription = json.loads(self.socket.recv())
        if session_desription['op'] != 4:
            logger.log("VC ", colored("RECEIVED WRONG PACKET!", "red"))
            while session_desription['op'] != 4:
                session_desription = json.loads(self.socket.recv())
        logger.log('VC ', colored("Session Description received", "cyan"))
        logger.log('VC ', colored(session_desription, "cyan"))
        self.session_key = session_desription['d']['secret_key']

        # Start playing audio 
        logger.log("VC ", colored("Starting Audio Thread...", "cyan"))
        logger.log("VC ", colored(f"CONNECTION IP: {self.ip_and_port[0]}", "cyan"))
        logger.log("VC ", colored(f"CONNECTION PORT: {self.ip_and_port[1]}", "cyan"))
        self.socket.send(json.dumps(
                {
                    "op":5,
                    "d":{
                        "speaking": 5,
                        "delay": 0,
                        "ssrc": 1
                    }
                }
        ))
        with open(r"C:\Users\pawel\Desktop\drill_encoded.opus", "rb") as file:
            encoded_audio = file.read()
            box = nacl.secret.SecretBox(bytes(self.session_key))
            encoded_audio = box.encrypt(encoded_audio)
            # Send Audio to the self.ip_and_port using UDP and https://discord.com/developers/docs/topics/voice-connections#encrypting-and-sending-voice
             
        
        # Re
        self.receiver_thread = threading.Thread(target=self.receiver, name="VC_Receiver")
        self.receiver_thread.start()
        
        
        
    
    def receiver(self):
        while True:
            data = json.loads(self.socket.recv())
            try:
                match data["op"]:
                    case 6:
                        # Heartbeat ACK
                        self.logger.log("VCH", colored("HEARTBEAT ACK RECEIVED", "cyan"))
                    case 5:
                        # User Speaking
                        pass
                    case _:
                        self.logger.log("VC", colored(f"EVENT NOT HANDLED. OP: {data['op']}", "cyan"))
                        self.logger.log("VC", colored(data, "cyan"))
            except KeyError:
                self.logger.log("VC", colored("WRONG DATA!!!", "red"))
                self.logger.log("VC", colored(data, "red"))

                
                    
    
    
    def start_heartbeating(self, interval, ws):
        self.logger.log("VCH", colored("HEARTBEAT ACTIVATION CONFIRMATION\n", "cyan"))
        while True:
            time.sleep(interval)
            ws.send(json.dumps({"op": 3, "d": time.time() + random.randint(0, 1000)}))
            self.logger.log("VCH", colored("HEARTBEAT SENT", "cyan"))