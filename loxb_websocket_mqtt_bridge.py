# LoxBerry Service to Connect to your Miniserver via Websockets and send mqtt telegrams
# Name: loxb_websocket_mqtt_bridge
# Author: Alx G
# Licence: Apache 2.0
import asyncio
#import signal
from settings import Env
from LoxMiniserver import LoxMiniserver
from LoxBerry import LoxBerry

env_lox = Env("LOX_")
env_lb = Env("MQTT_")

def ask_exit(*args):
    STOP.set()

if __name__ == '__main__':
    myLox = LoxMiniserver(env_lox.ip, env_lox.port, env_lox.user, env_lox.password)
    loxBerry = LoxBerry(env_lb.broker_host, env_lb.broker_port, "alx_sender1")
    loxBerry_listen = LoxBerry(env_lb.broker_host, env_lb.broker_port, "alx_listener1")
    msgQ_lox2lb = asyncio.Queue() # Creates a FIFO queue for messages
    msgQ_lb2lox = asyncio.Queue() # Creates a FIFO queue for messages

    STOP = asyncio.Event()

    loop = asyncio.get_event_loop()
    
#     loop.add_signal_handler(signal.SIGINT, ask_exit)
#     loop.add_signal_handler(signal.SIGTERM, ask_exit)
    
    loop.run_until_complete(myLox.connect()) # Connect to Miniserver via Websockets
    loop.run_until_complete(loxBerry.connect())
    loop.run_until_complete(loxBerry_listen.connect())

    # Start listener and heartbeat 
    tasks = [
        asyncio.ensure_future(myLox.receiver(msgQ_lox2lb)), # Start the receiver for Loxone messages
        asyncio.ensure_future(loxBerry.MQTTsender(msgQ_lox2lb)), # Start the MQTT sender
        asyncio.ensure_future(loxBerry_listen.MQTTreceiver(msgQ_lb2lox))
    ]

    loop.run_until_complete(asyncio.wait(tasks))

