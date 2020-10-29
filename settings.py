# Settings.py for loxb_websocket_mqtt_bridge.py
# Author: Alx G

# Helps you read the configuration 

#Either you have a .env-File with the following settings 
#LOX_USER = "user1"
#LOX_PASSWORD = "passwordxyz"
#LOX_IP = "192.168.1.1"
#LOX_PORT = "80"
#
# OR Fill your own values in the script and pass as dict struct
# 
myConfig = {
    'user': 'user2',
    'password' : 'dkdk',
    'ip' : '192.168.2.1',
    'port' : '8080'
    }

# Usage
# from settings import Env  # your settings.py
# env = Env("LOX_")         # Create an instance with your prefix
# env.setDefaults(myConfig) # pass Defaults-Dict 

from dotenv import load_dotenv, find_dotenv   #install package python-dotenv
import os        #to access environment variables in .env

class Env:
    prefix = None
    defaults = {}
    
    # Provide a prefix to be used, else ""
    def __init__(self, prefix):
        load_dotenv(find_dotenv())
        self.prefix = prefix
    
    def setDefaults(self, new_defaults: dict):
        self.defaults = new_defaults
    
    def __getattr__(self, name):
    # will only get called for undefined attributes
        env_found = os.getenv("{}{}".format(self.prefix, name.upper()))
        if env_found:
            return env_found
        else:
            if self.defaults[name]:
                return self.defaults[name]
            else:
                return "nothing"
        


