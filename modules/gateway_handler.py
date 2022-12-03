import time
import modules.logging
import websocket
import threading
import requests
import json
import datetime
# ----------------------------------------------------------------------------------------------------------------------
# DiscordAPI Gateway handler
# by Empezeeet 2022

class GatewayHandler(threading.Thread):
    def __init__(self, token, appid, activity):
        self.ACTIVITY_STATUS = activity['status']
        self.ACTIVITY_NAME = activity['name']
        self.ACTIVITY_TYPE = activity['type']
        self.activity = activity
        self.TOKEN = token
        self.APPID = appid
        self.AHEAD = {"Authorization": f"Bot {self.TOKEN}"}
        self.start_time = time.time()
        self.logger = modules.logging.Logger(f"logs/log", "Enpeceeet")
        
        
        self.logger.log("GATEWAY", "Initializing...")
        self.ws = websocket.WebSocket()
        self.ws.connect('wss://gateway.discord.gg/?v=6&encording=json') 
        event = self.receive_json_response(self.ws) # Receive Hello Event
        # Identify 
        identifyJSON = {
            "op": 2,
            "d": {
                "token": self.TOKEN,
                "intents": 513,
                "properties": {
                    "os": "linux",
                    "browser": "Safari",
                    "device": "BDB"
                },
                "presence": {
                    "activities": [{
                        "name": self.ACTIVITY_NAME,
                        "type": self.ACTIVITY_TYPE,
                        "url": self.activity["url"],
                        "created_at": self.start_time,
                        "details": "Details",
                        "buttons": self.activity["buttons"]
                    }],
                    "status": "offline",
                    "since": time.time(),
                    "afk": False
                }
            }
        }
        
        
        self.send_json_request(self.ws, identifyJSON)
        self.logger.log("GATEWAY", f"Starting heartbeating at {(event['d']['heartbeat_interval']/1000) / 60} per minute")
        self.heartbeating = threading.Thread(target=self.start_heartbeating, args=(self.ws, event['d']['heartbeat_interval']/1000)) # I divide by 1000 because python sleep is in seconds
        self.heartbeating.start()
        # Set commands
        self.delete_commands()
        self.setup_commands()
        self.logger.log("GATEWAY", f"Initialized ({time.time() - self.start_time})")
        self.logger.log("GATEWAY", "                                              ")
    def delete_commands(self):
        url = f"https://discord.com/api/v10/applications/{self.APPID}/commands"
        r = requests.get(url, headers={"Authorization": f"Bot {self.TOKEN}"})
        start = time.time()
        self.logger.log("DELCOM", f"Deleting commands... ({start})")
        for command in r.json():
            r = requests.delete(f"{url}/{command['id']}", headers=self.AHEAD)
            if r.status_code == 429:
                self.logger.log("DELCOM", f"Rate limited, wait {r.json()['retry_after']/1000} seconds")
                time.sleep(r.json()['retry_after']/1000)
            self.logger.log("DELCOM", f"Deleted command {command['name']}. Response: {r.status_code}. ({time.time() - start})")
            
    def make_online(self):
        self.send_json_request(self.ws, {
            "op": 3,
            "d": {
                "since": time.time(),
                "activities": [{
                    "name": self.ACTIVITY_NAME,
                    "type": self.ACTIVITY_TYPE,
                    "url": self.activity["url"],
                    "created_at": self.start_time,
                    "details": "Details",
                    "buttons": self.activity["buttons"]
                }],
                "status": "online",
                "afk": False
            }
        })
        self.logger.log("GATEWAY", "Bot is now online")
    
    def setup_commands(self):
        url = f"https://discord.com/api/v10/applications/{self.APPID}/commands"
        headers = {
            "Authorization": f"Bot {self.TOKEN}"
        }
        with open("modules/commands/commands.json", "r") as file:
            loaded = json.load(file)
            for command in loaded["commands"]:
                self.logger.log("CLOADER", f"Loading command {command['name']}")
                r = requests.post(url, headers=headers, json=command)
                with open(r"rundata.json", "r") as file:
                   data = json.load(file)
                    
                self.logger.log("CLOADER", f"Loaded Command with result: {r.status_code}")
                
    def handle_command(self, command):
        match command['data']['name']:
            case "pingu":
                return "Pong!"
            case "uptime":
                return f"Uptime: {time.time() - self.start_time}"
            case "hello":
                return f"Hello, {command['member']['user']['username']}!"
            case _:
                return "Unknown command"

    def receive_json_response(self, ws):
        try: 
            
            response = ws.recv()
        except websocket.WebSocketConnectionClosedException as e:
            self.logger.log("GATEWAY", "Connection Closed")
            ws.close()
            exit()
        try:
            if response:
                try:
                    return json.loads(response)
                except AttributeError as ae:
                    self.logger.log("GATEWAY-WARN", f"Attribute Error: {ae}\n Response: \n{response}\n")
                    return response
        except ConnectionError as e:
            ws.close()
            self.logger.log("ERROR", "Connection Error")
            breakpoint()
            exit()
    def send_json_request(self, ws, request):
        ws.send(json.dumps(request))
    def closeConnection(self):
        pass
    def start_heartbeating(self, ws, interval):
        self.logger.log("HEART", "Heartbeat Begin...")
        while True:
            time.sleep(interval)
            heartbeatJSON = {
                "op":1,
                "d": "null"
            }
            self.send_json_request(ws, heartbeatJSON)
            self.logger.log("HEART", f'Heartbeat sent @ {datetime.datetime.now().time()}')
            ack = self.receive_json_response(ws)
            try:
                if ack:
                        self.logger.log('HEART', f'Heartbeat ACK received @ {datetime.datetime.now().time()}')
            except TypeError as e:
                pass
            while not (ack and ack['op'] == 11):
                ack = self.receive_json_response(ws)
                if ack and ack['op'] == 11:
                    self.logger.log('HEART', f'Heartbeat ACK received @ {datetime.datetime.now().time()}')
                    break