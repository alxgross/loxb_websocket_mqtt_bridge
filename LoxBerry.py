import asyncio

class LoxBerry:
    """
    Instance Attributes:
        ip
        port
    """
    def __init__(self, ip, port):
        self.ip, self.port = ip, port
    
    async def MQTTsender(self, queue: asyncio.Queue):
        while True:
            msg = await queue.get()
            print("MQTT sender: ", msg.appliance, msg.value)
            await asyncio.sleep(2)
        