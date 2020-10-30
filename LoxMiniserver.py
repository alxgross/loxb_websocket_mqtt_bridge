# Class representing the miniserver with associated methods to connect
import asyncio
from QMessage import QMessage


class LoxMiniserver:
    """
    Instance Attributes:
        IP-Address of Miniserver
        Port
        User
        Password
    """
    
    async def connect(self):
        pass
    
    async def receiver(self, queue: asyncio.Queue):
        i = 0
        while True:
            await queue.put(QMessage("Act{}".format(i), "Message 1"))
            await asyncio.sleep(2)
            await queue.put(QMessage("Act{}".format(i), "Message 2"))
            await asyncio.sleep(1)
            await queue.put(QMessage("Act{}".format(i), "Message 3"))
            i += 1
    
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password