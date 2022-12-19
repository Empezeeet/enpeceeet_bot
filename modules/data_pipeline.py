import random
import json
import time


class Pipeline:
    
    def __init__(self, websocket, logger):
        self.active_connections = {}
        self.active_connections_count = 0
        self.websocket = websocket
        self.logger = logger
        
        self.__run()
    def join(self, data_to_recv):
        """
            Data To recv: Here is for example OP Code
            After join() you need to call listen() to start receiveing for data
            
             Returns:
                - your ID for listening
        """
        self.active_connections_count += 1
        id = random.randint(0, 10000)
        if id in self.active_connections.values():
            while id in self.active_connections.values():
                id = random.randint(0, 10000)
        self.active_connections[f"{id}"] = data_to_recv
        
    def leave(self, id):
        self.active_connections.pop(id)
        self.active_connections_count -= 1
        
    def listener(self, id):
        """If your data is received by pipeline, you will receive it here"""
        
        data = ""
        return data
    
    def __send(self, id, data):
        """
        #### DO NOT CALL THIS FUNCTION OUTSIDE OF THIS CLASS
        Returns: 
            - 0 - if success, 
            - 1 - if failed
        """
        
        pass
    def __run(self):
        while True:
            data = json.loads(self.socket.recv())
            try:
                match data['op']:
                    case 6:
                        # Heartbeat ACK
                        self.logger.log("VC-HEART", "Heartbeat ACK")
                        for id, data_to_recv in self.active_connections.items():
                            if data_to_recv == 6:
                                self.__send(id, data)
            except KeyError:
            # Probaly wrong data was received.
                continue
            
        