import time
import modules.logging
import websocket
import threading
import requests
import json
import datetime
import random
from termcolor import colored

# ----------------------------------------------------------------------------------------------------------------------
# DiscordAPI Gateway handler
# by Empezeeet 2022

class GatewayHandler(threading.Thread):
    def __init__(self, token, appid, activity, version):
        self.ACTIVITY_STATUS = activity['status']
        self.ACTIVITY_NAME = activity['name']
        self.ACTIVITY_TYPE = activity['type']
        self.activity = activity
        self.TOKEN = token
        self.APPID = appid
        self.AHEAD = {"Authorization": f"Bot {self.TOKEN}"}
        self.start_time = time.time()
        self.logger = modules.logging.Logger(f"logs/log", "Enpeceeet", version)
        self.last_sequence = None
        self.rate_limit_sum = 0
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
        self.hb_interval = event['d']['heartbeat_interval']/1000
        self.heartbeating = threading.Thread(target=self.start_heartbeating, args=(self.ws, self.hb_interval)) # I divide by 1000 because python sleep is in seconds
        self.heartbeating.start()
        # Set commands
        self.setup_commands2()
        self.logger.log("GATEWAY", colored(f"Initialized after {time.time() - self.start_time} ({(time.time() - self.start_time) - self.rate_limit_sum})", "green"))
        self.logger.log("GATEWAY", "                                              ")
    def setup_commands2(self):
        url = f"https://discord.com/api/v10/applications/{self.APPID}/commands"
        headers = {
            "Authorization": f"Bot {self.TOKEN}"
        }
        COMMANDS = requests.get(url, headers={"Authorization": f"Bot {self.TOKEN}"}).json()

        with open("modules/commands/commands.json", "r") as file:
            
            
            for command in json.load(file)['commands']:
                for cmd in COMMANDS:
                    while True:
                        self.logger.log("CLOADER", f"Loading command {command['name']}")
                    
                        if cmd['name'] == command['name']:
                            self.logger.log("CLOADER", f"Command {command['name']} already exists. Updating...\n")
                            r = requests.patch(url, headers=headers, json=command)
                            if r.status_code == 429:
                                self.logger.log("CLOADER", colored(f"Rate limited, wait {r.json()['retry_after']} seconds", "yellow"))
                                time.sleep(r.json()['retry_after'])
                                self.rate_limit_sum += r.json()['retry_after']
                                pass
                        else: 
                            self.logger.log("CLOADER", f"Creating command {command['name']}")
                            r = requests.post(url, headers=headers, json=command)
                            self.logger.log("CLOADER", f"Loaded Command with result: {r.status_code}")
                            if r.status_code == 429:
                                self.logger.log("CLOADER", colored(f"Rate limited. Waiting {r.json()['retry_after']} seconds", "yellow"))
                                time.sleep(r.json()['retry_after'])
                                self.rate_limit_sum += r.json()['retry_after']
                                pass
                            if r.status_code > 204 and r.status_code != 429:
                                self.logger.log("CLOADER", colored(f"Error: {r.json()}", "red"))
                                break
                            break
                        break
                    break
                        
                    
    
    def setup_commands(self):
        url = f"https://discord.com/api/v10/applications/{self.APPID}/commands"
        headers = {
            "Authorization": f"Bot {self.TOKEN}"
        }
        with open("modules/commands/commands.json", "r") as file:
            loaded = json.load(file)
            
            for command in loaded["commands"]:
                while True:
                    self.logger.log("CLOADER", f"Loading command {command['name']}")
                    r = requests.post(url, headers=headers, json=command)
                        
                    self.logger.log("CLOADER", f"Loaded Command with result: {r.status_code}")
                    if r.status_code == 429:
                        self.logger.log("CLOADER", colored(f"Rate limited. Waiting {r.json()['retry_after']} seconds", "yellow"))
                        time.sleep(r.json()['retry_after'])
                        self.rate_limit_sum += r.json()['retry_after']
                        pass
                    if r.status_code > 204:
                        self.logger.log("CLOADER", colored(f"Error: {r.json()}", "red"))
                        break
                    break
                
    def handle_command(self, command):
        match command['data']['name']:
            # Picks wich command to run and returns the response
            case "pingu":
                payload = { 
                    "type": 4,
                    "data": {
                        "content": "Pong!"
                    }
                }
                return payload
                        
            case "uptime":
                payload = {
                    "type":4,
                    "data": {
                        "content": f"Uptime: {datetime.timedelta(seconds=time.time() - self.start_time)}"
                    }
                }
                return payload
            case "hello":
                payload = {
                    "type":4,
                    "data": {
                        "content": f"Hello, {command['member']['user']['username']}!",
                    }
                }
                return payload
            case "cytat":
                self.logger.log("CHANDLER", "Running 'cytat' command")
                
                payload = {
                    "type":9,
                    "data": {
                        "title": "Dodaj Nowy Cytat!",
                        "custom_id": "cool_modal",
                        "components": [
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 4,
                                        "custom_id": "name",
                                        "label": "Cytat",
                                        "style": 1,
                                        "min_length": 1,
                                        "max_length": 4000,
                                        "placeholder": "",
                                        "required": True
                                    }
                                ]
                            },
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 4,
                                        "custom_id": "user",
                                        "label": "Użytkownik",
                                        "style": 1,
                                        "min_length": 1,
                                        "max_length": 4000,
                                        "placeholder": "",
                                        "required": True
                                    }
                                ]
                            }
                        ]
                    }
                }
                return payload
            case _:
                self.logger.log("CHANDLER", f"Unknown command {command['data']['name']}")
                return {"type":1, "data": {"content": "Unknown command"}}

    def receive_json_response(self, ws):
        try: 
            
            response = ws.recv()
            
        except websocket.WebSocketConnectionClosedException as e:
            self.logger.log("GATEWAY", "Connection Closed")
            self.logger.log(colored("GERROR", "red"), e)
            ws.close()
            exit()
        try:
            if response:
                try:
                    if response['op'] == 11:
                        self.logger.log("HEART", "Received heartbeat ack")
                        self.logger.log("HEART", response)
                        return response
                except TypeError:
                    pass
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
        self.logger.log("HEART", "Heartbeating Began...")
        # Sleep for interval * random value betweeen 0, 1
        time.sleep(interval * random.random())
        
        heartbeatJSON = {
                "op":1,
                "d": "null"
            }
        self.send_json_request(ws, heartbeatJSON)
        while True:
            time.sleep(interval)
            heartbeatJSON = {
                "op":1,
                "d": self.last_sequence
            }
            self.send_json_request(ws, heartbeatJSON)
            self.logger.log("HEART", f'Heartbeat sent @ {datetime.datetime.now().time()}')
            # while not (ack and ack['op'] == 11):
            #     ack = self.receive_json_response(ws)
            #     if ack and ack['op'] == 11:
            #         self.logger.log('HEART', f'Heartbeat ACK received @ {datetime.datetime.now().time()}')
            #         break