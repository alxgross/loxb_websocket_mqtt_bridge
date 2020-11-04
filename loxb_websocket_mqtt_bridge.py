# LoxBerry Service to Connect to your Miniserver via Websockets and send mqtt telegrams
# Name: loxb_websocket_mqtt_bridge
# Author: Alx G
# Licence: Apache 2.0
import asyncio
import signal
import logging

from settings import Env
from LoxMiniserver import LoxMiniserver
from LoxBerry import LoxBerry

# Get the config 
env_lox = Env("LOX_")
env_lb = Env("MQTT_")

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logging.warning(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    

def main():
    myLox = LoxMiniserver(env_lox.ip, env_lox.port, env_lox.user, env_lox.password, env_lox.client_uuid)
    loxBerry = LoxBerry(env_lb.broker_host, env_lb.broker_port, client_id = "alx_sender1", miniserver = env_lox.miniserver_name)
    loxBerry_listen = LoxBerry(env_lb.broker_host, env_lb.broker_port, "alx_listener1", miniserver = env_lox.miniserver_name)
    msgQ_lox2lb = asyncio.Queue() # Creates a FIFO queue for messages
    msgQ_lb2lox = asyncio.Queue() # Creates a FIFO queue for messages


    loop = asyncio.get_event_loop()

    #Preparing to gracefully exit
    # May want to catch other signals too
    #signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT) - POSIX/LINUX
    signals = (signal.SIGTERM, signal.SIGINT) # Windows
    try:
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(s, loop)))
    except NotImplementedError:
        logging.error("No Signalhandler added...")
        
        
    try:
        loop.run_until_complete(loxBerry.connect())
        loop.run_until_complete(loxBerry_listen.connect())

#         # Start listener and heartbeat 
#         tasks = [
#             asyncio.ensure_future(myLox.receiver(msgQ_lox2lb)), # Start the receiver for Loxone messages
#             asyncio.ensure_future(loxBerry.MQTTsender(msgQ_lox2lb)), # Start the MQTT sender
#             asyncio.ensure_future(loxBerry_listen.MQTTreceiver(msgQ_lb2lox))
#         ]

   #     loop.run_until_complete(asyncio.wait(tasks))
        loop.create_task(myLox.plugWebsocket(msgQ_lox2lb, msgQ_lb2lox)) # Startup websocket connection and listen
        loop.create_task(loxBerry.MQTTsender(msgQ_lox2lb))
        loop.create_task(loxBerry_listen.MQTTreceiver(msgQ_lb2lox))
        loop.run_forever()

    finally:
        loop.close()
        logging.info("Successfully shutdown the Loxone-Loxberry-Bridge service.")


if __name__ == '__main__':
    main()