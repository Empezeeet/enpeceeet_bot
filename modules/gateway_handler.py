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
    def __init__(self, token, appid, activity, version, show_limit_warning):
        self.connected = False
        self.ACTIVITY_STATUS = activity['status']
        self.ACTIVITY_NAME = activity['name']
        self.ACTIVITY_TYPE = activity['type']
        self.activity = activity
        self.TOKEN = token
        self.APPID = appid
        self.AHEAD = {"Authorization": f"Bot {self.TOKEN}"}
        self.start_time = time.time()
        self.logger = modules.logging.Logger(f"logs/log", "Enpeceeet", version)
        if show_limit_warning:
            self.logger.log("GATEWAY-WARN", colored("\n\tThis gateway handler is created for once-in-a-while launch.\n\tRate limits will occur if gateway is restarted too often.\n\tTo disable this message change \"show_rate_limit_warning\" to False.", "yellow"))
        self.last_sequence = None
        self.rate_limit_sum = 0
        self.logger.log("GATEWAY", "Initializing...")
        self.ws = websocket.WebSocket()
        self.ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
        self.VC_HANDLER = None 
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
                    "since": time.time(),
                    "activities": [{
                        "name": self.ACTIVITY_NAME,
                        "type": self.ACTIVITY_TYPE,
                        "url": self.activity["url"]
                    }],
                    "status": "online",
                    "afk": False
                }
            },
            "s": self.last_sequence,
            "t": None
        }
        
        
        self.send_json_request(self.ws, identifyJSON)
        self.logger.log("GATEWAY", f"Starting heartbeating at {(event['d']['heartbeat_interval']/1000) / 60} per minute")
        self.hb_interval = event['d']['heartbeat_interval']/1000
        self.heartbeating = threading.Thread(target=self.start_heartbeating, args=(self.ws, self.hb_interval)) # I divide by 1000 because python sleep is in seconds
        self.heartbeating.start()
        self.active_commands = []
        
        self.logger.log("GATEWAY", colored(f"Initialized after {time.time() - self.start_time} ({(time.time() - self.start_time) - self.rate_limit_sum})\n", "green"))
        self.logger.log("GATEWAY", "                                              ")
    def setup_commands2(self):
        url = f"https://discord.com/api/v10/applications/{self.APPID}/commands"
        headers = {
            "Authorization": f"Bot {self.TOKEN}"
        }
        COMMANDS = requests.get(url, headers={"Authorization": f"Bot {self.TOKEN}"}).json()
        
        with open("configs/commands.json", "r") as file:
            for loaded_command in json.load(file)['commands']:
                self.active_commands.append(loaded_command["name"])
                while True:
                    if loaded_command["name"] in [command["name"] for command in COMMANDS]:
                        self.logger.log("CLOADER", f"Command {loaded_command['name']} already exists. Updating...")
                        # Update command.
                        r = requests.patch(url, headers=headers, json=loaded_command)
                        if r.status_code == 429:
                            # Rate limited,
                            self.logger.log("CLOADER", colored(f"Rate limited, wait {r.json()['retry_after']} seconds", "yellow"))
                            time.sleep(r.json()['retry_after'])
                            self.rate_limit_sum += r.json()['retry_after']
                            pass
                    else:
                        self.logger.log("CLOADER", f"Creating command {loaded_command['name']}")
                        r = requests.post(url, headers=headers, json=loaded_command)
                        self.logger.log("CLOADER", f"Loaded Command with result: {r.status_code}")

                        if r.status_code == 429:
                            # Rate limited
                            self.logger.log("CLOADER", colored(f"Rate limited. Waiting {r.json()['retry_after']} seconds", "yellow"))
                            time.sleep(r.json()['retry_after'])
                            self.rate_limit_sum += r.json()['retry_after']
                            pass
                        
                        if r.status_code > 204 and r.status_code != 429:
                            # Error
                            self.logger.log("CLOADER", colored(f"Error: {r.json()}", "red"))
                            break
                    
                    break
                        # Commands does not exist. Create it.
            
            for command in COMMANDS:
                while True:
                    if command['name'] not in self.active_commands:
                        self.logger.log("CLOADER", f"Command {command['name']} does not exist in the loaded commands. Deleting...")
                        r = requests.delete(f"{url}/{command['id']}", headers=headers)
                        if r.status_code == 429:
                            # Rate limited
                            self.logger.log("CLOADER", colored(f"Rate limited. Waiting {r.json()['retry_after']} seconds", "yellow"))
                            time.sleep(r.json()['retry_after'])
                            self.rate_limit_sum += r.json()['retry_after']
                            pass
                    else:
                        self.logger.log("CLOADER", f"Command {command['name']} exists in the loaded commands. Skipping...")
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
    def hello_message(self, event):
        channel_id = 1051570042367651940
        r = requests.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=self.AHEAD, json={"content": f"Witaj, <@{event['d']['request']['user_id']}>!"})   
    

    
    def receive_json_response(self, ws):
        response = None
        try: 
            response = ws.recv()
        except websocket.WebSocketConnectionClosedException as e:
            self.logger.log("GATEWAY", "Connection Closed")
            self.logger.log(colored("GERROR", "red"), e)
            ws.close()
            breakpoint()
            
        try:
            self.last_sequence = json.loads(response)['s']
            return json.loads(response)
        
        except AttributeError as ae:
            self.logger.log("GATEWAY-WARN", f"Attribute Error: {ae}\n Response: \n{response}\n")
            return response
        
        except json.JSONDecodeError as jde:
            self.logger.log("ERROR", "JSON DECODE ERROR")
            self.logger.log("ERROR", f"\n{jde}\n{response}\n")
            
        except ConnectionError as e:
            ws.close()
            self.logger.log("ERROR", "Connection Error")
            breakpoint()
    def send_json_request(self, ws, request):
        ws.send(json.dumps(request))
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