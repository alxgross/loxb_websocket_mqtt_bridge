# LoxBerry Service to Connect to your Miniserver via Websockets and send mqtt telegrams
# Name: loxb_websocket_mqtt_bridge
# Author: Alx G
# Licence: Apache 2.0
import asyncio
from settings import Env
from LoxMiniserver import LoxMiniserver
from LoxBerry import LoxBerry

env_lox = Env("LOX_")
env_lb = Env("MQTT_")

if __name__ == '__main__':
    myLox = LoxMiniserver(env_lox.ip, env_lox.port, env_lox.user, env_lox.password)
    loxBerry = LoxBerry(env_lb.ip, env_lb.port)
    print(env_lb.ip, env_lb.port)
    messageQueue = asyncio.Queue() # Creates a FIFO queue for messages
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(myLox.connect()) # Connect to Miniserver via Websockets

    # Start listener and heartbeat 
    tasks = [
        asyncio.ensure_future(myLox.receiver(messageQueue)), # Start the receiver for Loxone messages
        asyncio.ensure_future(loxBerry.MQTTsender(messageQueue)) # Start the MQTT sender
    ]

    loop.run_until_complete(asyncio.wait(tasks))

