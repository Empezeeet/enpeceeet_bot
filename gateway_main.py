import threading
import time
import requests
import json
import websocket
import datetime
import modules.logging
import modules.gateway_handler as gh
from termcolor import colored
import colorama
# Change Activity settings in config.json


colorama.just_fix_windows_console()

with open("config.json", "r") as config:
    loaded = json.load(config)
    TOKEN = loaded["token"]
    APPID = loaded["appid"]
    AUTH_HEADER = {"Authorization": "Bot " + TOKEN}
    ACTIVITY = loaded['activity']




handler = None
try:
          
    if __name__ == "__main__":
        handler = gh.GatewayHandler(TOKEN, APPID, ACTIVITY)
        # Read lines 2-7 from fonts.txt and print them using handler.logger.log("GATEWAY", "message")
        lines = [
            "░██╗░░░░░░░██╗███████╗██╗░░░░░░█████╗░░█████╗░███╗░░░███╗███████╗",
            "░██║░░██╗░░██║██╔════╝██║░░░░░██╔══██╗██╔══██╗████╗░████║██╔════╝",
            "░╚██╗████╗██╔╝█████╗░░██║░░░░░██║░░╚═╝██║░░██║██╔████╔██║█████╗░░",
            "░░████╔═████║░██╔══╝░░██║░░░░░██║░░██╗██║░░██║██║╚██╔╝██║██╔══╝░░",
            "░░╚██╔╝░╚██╔╝░███████╗███████╗╚█████╔╝╚█████╔╝██║░╚═╝░██║███████╗",
            "░░░╚═╝░░░╚═╝░░╚══════╝╚══════╝░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚══════╝"
        ]
        print("\n\n")
        for line in lines:
            print(line)
        print("\n\n")
        
        
        ready_event = handler.receive_json_response(handler.ws)
        if (ready_event) and ready_event['t'] == "READY":
            handler.logger.log("MAIN", "Initialization successfully completed.")
            handler.logger.log("MAIN", "Connected to Discord API.")
            handler.logger.log(
                "MAIN", 
                f"Connection Info:\n\n\tAPI Version: {ready_event['d']['v']}\n\tSessionID: {ready_event['d']['session_id']}\n\tSee more info in rundata.json\n"
            )
            with open("rundata.json", "w") as file:
                r = requests.get(f"https://discord.com/api/v10/applications/{APPID}/commands", headers=AUTH_HEADER).json()
                commands = []
                for command in r:
                    commands.append(command['id'])
                data = {
                    "time": str(datetime.datetime.now()),
                    "api_version": ready_event['d']['v'],
                    "session_id": ready_event['d']['session_id'],
                    "user": ready_event['d']['user'],
                    "resume_gateway_url": ready_event['d']['resume_gateway_url'],
                    "guilds": ready_event['d']['guilds'],
                    "commands":commands
                    
                }
                file.write(json.dumps(data, indent=4))
        handler.logger.log("MAIN", f"Initialization completed. ({round(time.time() - handler.start_time, 4)})")
        handler.logger.log("MAIN", colored("Everything OK", "green"))
        handler.logger.log("MAIN", "Starting event loop...")
        while True:
            recv = handler.receive_json_response(handler.ws)
            if not recv:
                continue
            try:
                
                handler.logger.log("MAIN", f"Event Received: {recv['t']}")
                match recv['t']:
                    case "MESSAGE_CREATE":
                        if recv['d']['content'] == "!ping":
                            handler.logger.log("MAIN", "Updating Presence...")
                            payload = {
                                "op": 3,
                                "d": {
                                    "since": time.time(),
                                    "activities": [{
                                        "name": "Rewriting...",
                                        "type": 1
                                    }],
                                    "status": "online",
                                    "afk": False
                                }
                                }
                            handler.send_json_request(handler.ws, payload)
                    case "INTERACTION_CREATE":
                        try:
                            commandIDs = json.load(open("rundata.json", "r"))["commands"]
                            if recv['d']['type'] == 2 and recv['d']['data']['id'] in commandIDs:
                                recv = recv['d']
                                
                                url = f"https://discord.com/api/v10/interactions/{recv['id']}/{recv['token']}/callback"
                                
                                # This is slash command.
                                payload = {
                                    "type":4,
                                    "data": {
                                        "content":"Command Received"
                                    }
                                }
                                handler.logger.log("MAIN", "Command Received")
                                url = f"https://discord.com/api/v10/interactions/{recv['id']}/{recv['token']}/callback"
                                handler.logger.log("MAIN", f"Responsing to: {url}")
                                req = requests.post(url, json=payload)
                                handler.logger.log("MAIN", f"Command Response: {req.status_code}")
                                
                            else:
                                handler.logger.log("MAIN", "Unknown Interaction Type")
                        except KeyError as e:
                            handler.logger.log(colored("ERROR", "red"), "KeyError @ INTERACTION_CREATE")
                            handler.logger.log(colored("ERROR", "red"), recv)
                            handler.logger.log(colored("ERROR", "red"), e)
                            pass
                    
                    case _:
                        handler.logger.log("MAIN", "Event not handled")         
            except TypeError as e:
                handler.logger.log(colored("ERROR", "red"), f"TypeError[main]: {e}")
                pass
            
            
            
except KeyboardInterrupt:
    handler.logger.log("MAIN", "User Interrupted program with Ctrl+C. Safe Exit initiated...")
    handler.closeConnection()