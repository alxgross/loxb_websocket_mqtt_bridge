#test LoxBerry MQTT connection

import asyncio
import logging
import json

from QMessage import QMessage
from settings import Env
from LoxBerry import LoxBerry
from aiofile import AIOFile

# Get the config 
env_lox = Env("LOX_")
env_lb = Env("MQTT_")

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

# Get Structure File
async def getStruct():
    async with AIOFile(".cache/loxAPP3.json", "r") as file:
        structure_file = json.loads(await file.read())
    return structure_file
    

async def produce_messages(queue: asyncio.Queue()):
    structure_file = await getStruct()
    while True:
        message = QMessage(origin = "miniserver", loxDict = structure_file, loxUuid = "1374af94-0188-55fb-ffff7ba5fa36c093", loxValue = "1")
        await queue.put(message)
        await asyncio.sleep(1)

        message = QMessage(origin = "miniserver", loxDict = structure_file, loxUuid = "14654822-0067-ac01-ff007ba5fa36c093", loxValue = "off")
        await queue.put(message)

        message = QMessage(origin = "this_bridge", loxDict = structure_file, loxUuid = "14654822-0067-ac01-ff007ba5fa36c093", loxValue = "off")
        await asyncio.sleep(1)

queue = asyncio.Queue() # Creates a FIFO queue for messages
tasks = set()

loxBerry = LoxBerry(env_lb.broker_host, env_lb.broker_port, client_id = "alx_sender1", miniserver = env_lox.miniserver_name)
loop = asyncio.get_event_loop()

loop.create_task(loxBerry.connect(queue))
loop.create_task(produce_messages(queue))

loop.run_forever()
