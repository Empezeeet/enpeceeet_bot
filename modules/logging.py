import datetime
import time
class Logger:
    
    def __init__(self, filename, name):
        self.filepath = f"{filename}_{hex(int(time.time()))}.log"
        self.name = name
        with open(self.filepath, "a") as logfile:
            logfile.write(f"====================\n")
            logfile.write(f"Initializing Logger\n")
            logfile.write(f"Date: {datetime.datetime.now()}\n")
            logfile.write(f"Name: {name}\n")
            logfile.write(f"====================\n")
    def log(self, level, message):
        with open(self.filepath, "a") as logfile:
            logfile.write(f"[ {level} @ {hex(int(time.time()))} ]: {message}\n")
            
if __name__ == "__main__":
    logger = Logger("dev", "DevTest")
    logger.log("DEBUG", "Test message from code")