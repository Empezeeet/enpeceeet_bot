import threading
import time
import requests
import json
import websocket
import datetime
import modules.logging

with open("config.json", "r") as config:
    TOKEN = json.load(config)["token"]


class GatewayHandler(threading.Thread):
    def __init__(self):
        print("[GATEWAY] Initializing...")
        self.ws = websocket.WebSocket()
        self.ws.connect('wss://gateway.discord.gg/?v=6&encording=json') 
        event = self.receive_json_response(self.ws) # Receive Hello Event
        # Identify 
        identifyJSON = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "intents": 513,
                "properties": {
                    "os": "linux",
                    "browser": "Safari",
                    "device": "BDB"
                },
                "presence": {
                    "activities": [{
                        "name": "Rewriting...",
                        "type": 0
                    }],
                    "status": "online",
                    "since": time.time(),
                    "afk": False
                },
            }
        }
        self.send_json_request(self.ws, identifyJSON)
        
        
        
        self.start_heartbeating(self.ws, event['d']['heartbeat_interval']/1000) # I divide by 1000 because python sleep is in seconds
        
    def receive_json_response(self, ws):
        response = ws.recv()
        try:
            if response:
                return json.loads(response)
        except ConnectionError as e:
            ws.close()
            print("[ERROR] Connection Error")
            breakpoint()
            exit()
    def send_json_request(self, ws, request):
        ws.send(json.dumps(request))
        
    def start_heartbeating(self, ws, interval):
        print("[HEART] Heartbeat Begin...")
        while True:
            time.sleep(interval)
            print("\n")
            heartbeatJSON = {
                "op":1,
                "d": "null"
            }
            self.send_json_request(ws, heartbeatJSON)
            print(f'[HEART] Heartbeat sent @ {datetime.datetime.now().time()}')
            ack = self.receive_json_response(ws)
            try:
                if ack:
                        print(f'[HEART] Heartbeat ACK received @ {datetime.datetime.now().time()}')
            except TypeError as e:
                pass
            while not (ack and ack['op'] == 11):
                ack = self.receive_json_response(ws)
                print('[HEART] Waiting for ACK...', end='\r')
                if ack and ack['op'] == 11:
                    print(f'[HEART] Heartbeat ACK received @ {datetime.datetime.now().time()}')
                    break
                
if __name__ == "__main__":
    hanlder = GatewayHandler()
    
    while True:
        pass