import websocket
import json
import threading
import time
import datetime
import requests

with open("config.json", "r") as config:
    TOKEN = json.load(config)["token"]



print("\n\n\n\n\n\n\n\n\n\n")


def send_json_request(ws, request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    try:
        if response:
            return json.loads(response)
    except ConnectionError as e:
        ws.close()
        print("[ERROR] Connection Error")
        breakpoint()
        exit()

def heartbeat(interval, ws):
    print("[HEART] Heartbeat Begin...")
    while True:
        time.sleep(interval)
        print("\n")
        heartbeatJSON = {
            "op":1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)
        print(f'[HEART] Heartbeat sent @ {datetime.datetime.now().time()}')
        ack = receive_json_response(ws)
        try:
            if ack:
                    print(f'[HEART] Heartbeat ACK received @ {datetime.datetime.now().time()}')
        except TypeError as e:
            pass
        while not (ack and ack['op'] == 11):
            ack = receive_json_response(ws)
            print('[HEART] Waiting for ACK...', end='\r')
            if ack and ack['op'] == 11:
                print(f'[HEART] Heartbeat ACK received @ {datetime.datetime.now().time()}')
                 
                break

        
            
            
    
        
# ----------------------------------------------------------------------------------------------------------------------
event = None
ws = websocket.WebSocket()

ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = receive_json_response(ws) # Recv hello 


print(f"[HEART] Heartbeat Interval: {event['d']['heartbeat_interval']}({event['d']['heartbeat_interval'] / 1000})")
heartbeat_interval = event['d']['heartbeat_interval'] / 1000
Heartbeating_Thread = threading.Thread(target=heartbeat, args=(heartbeat_interval, ws), name="Heartbeating")
Heartbeating_Thread.start()


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
send_json_request(ws, identifyJSON)
event = receive_json_response(ws)

#print(f"[MAIN] Session ID: {session_id}")

print("\n==========================================================\n")

# Rest of code...

while True:
    pass