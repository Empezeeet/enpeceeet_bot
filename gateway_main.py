import time
import requests
import json
import datetime
from termcolor import colored
import console.utils as utils
import os
import sys
import socket
import threading
from colorama import just_fix_windows_console

# OWN MODULES
import modules.gateway_handler as gh
import modules.socket_server as ss







# Change Activity settings in config.json
start_time = time.time()
just_fix_windows_console()
handler = None
with open("config.json", "r") as config:
    loaded = json.load(config)
    TOKEN = loaded["token"]
    APPID = loaded["appid"]
    AUTH_HEADER = {"Authorization": "Bot " + TOKEN}
    ACTIVITY = loaded['activity']
    VERSION = loaded['version']
    
    handler = gh.GatewayHandler(TOKEN, APPID, ACTIVITY, VERSION, loaded["show_rate_limit_warning"])
    
    utils.set_title(f"{loaded['name']} v{VERSION} | Gateway Handler by Empezeeet#8540")

# Initalize Command Server
command_server_Thread = threading.Thread(target=ss.CommandServer, args=("192.168.0.110", "8080", handler.logger), name="CommandServer")
command_server_Thread.start()
ready_event = handler.receive_json_response(handler.ws)
if (ready_event) and ready_event['t'] == "READY":
    handler.logger.log("MAIN", "Connected to Discord API.")
    handler.logger.log(
        "MAIN", 
        f"Connection Info:\n\n\tAPI Version: {ready_event['d']['v']}\n\tSessionID: {ready_event['d']['session_id']}\n\tSee more info in rundata.json\n"
    )
    # Set commands
    
    with open("rundata.json", "w") as file:
        r = requests.get(f"https://discord.com/api/v10/applications/{APPID}/commands", headers=AUTH_HEADER).json()
        commands = []
        for command in r:
            commands.append(command['id'])
        data = {
            "time": str(datetime.datetime.now()),
            "api_version": ready_event['d']['v'],
            "app_version": VERSION,
            "session_id": ready_event['d']['session_id'],
            "heartbeat_interval": handler.hb_interval,
            "user": ready_event['d']['user'],
            "resume_gateway_url": ready_event['d']['resume_gateway_url'],
            "guilds": ready_event['d']['guilds'],
            "commands":commands
            
        }
        file.write(json.dumps(data, indent=4))
        handler.connected = True
    handler.setup_commands2()

try:
        
    if __name__ == "__main__":
        # Inform user that initialization is complete
        handler.logger.log("MAIN", colored(f"Initialization completed. ({round(time.time() - start_time, 4)})", "green"))
        handler.logger.log("MAIN", "Starting event loop...")
        
        
        while True:
            handler.logger.log("MAIN", "Waiting for event...")
            
            recv = handler.receive_json_response(handler.ws)
            if not recv:
                handler.logger.log("MAIN", "recv in None...")
                continue
                
            try:
                handler.last_sequence = recv['s']
                handler.logger.log("MAIN", f"Event Received: {recv['t']}")
                match recv['t']:   
                    case "INTERACTION_CREATE":
                        try:            
                            match recv['d']['type']:
                                case 2:
                                    # COMMAND
                                    if recv['d']['data']['name'] in handler.active_commands:
                                        recv = recv['d']
                                        handler.logger.log("MAIN", "Command Received")
                                        url = f"https://discord.com/api/v10/interactions/{recv['id']}/{recv['token']}/callback"
                                        dzejson = handler.handle_command(recv)
                                        req = requests.post(url, json=dzejson, headers={"Content-Type": "application/json"})
                                        handler.logger.log("MAIN", f"Command Response: {req.status_code}")
                                        if req.status_code > 204:
                                            handler.logger.log("MAIN", f"Command Response: {req.json()}")
                                        
                                    else:
                                        handler.logger.log("MAIN", colored("Unknown Interaction Type", "red"))
                                        handler.logger.log("MAIN", colored(recv, "red"))
                                case 5:
                                    # MODAL SUBMIT
                                    # There is only one modal and its for "cytaty"
                                    recv = recv['d']
                                    handler.logger.log("MAIN", "Modal Submit Received")
                                    message = {
                                        "content": f"~ {recv['data']['components'][0]['components'][0]['value']} ~\n\t\t- {recv['data']['components'][1]['components'][0]['value']}"
                                    }
                                    r = requests.post(f"https://discord.com/api/v10/channels/1012458745248358461/messages", json=message, headers=AUTH_HEADER)
                                    r = requests.post(f"https://discord.com/api/v10/interactions/{recv['id']}/{recv['token']}/callback", json={"type": 1, "data": {"content": "Wysłano!"}}, headers={"Content-Type": "application/json"})                          
                        except KeyError as e:
                            handler.logger.log(colored("ERROR", "red"), "KeyError @ INTERACTION_CREATE")
                            handler.logger.log(colored("ERROR", "red"), recv)
                            handler.logger.log(colored("ERROR", "red"), e)
                    case "GUILD_JOIN_REQUEST_UPDATE":
                        handler.hello_message(recv)
                    case "VOICE_SERVER_UPDATE":
                        with open("VOICE_SERVER_UPDATE.json", "a") as file:
                            file = json.dumps(recv)
                            handler.logger.log("MAIN", "Voice Server Update Received. Created file")
                    case _:
                        if recv['op'] == 11:
                            handler.logger.log("MAIN", "Heartbeat Acknowledged")
                        else:
                            handler.logger.log("MAIN", "Event not handled")     
                            if recv['t'] != "GUILD_CREATE":
                                handler.logger.log("MAIN", colored(recv, "yellow"))
            except KeyError as e:
                handler.logger.log(colored("ERROR", "red"), f"TypeError[main]: {e}")
            
            
            
except KeyboardInterrupt:
    handler.logger.log("MAIN", "User Interrupted program with Ctrl+C. Safe Exit initiated...")
    handler.closeConnection()
    exit()

