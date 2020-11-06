import asyncio
import logging
from asyncio_mqtt import Client, MqttError
from QMessage import QMessage #our interchange format

class LoxBerry:
    """ Class representing the LoxBerry - attached via MQTT 

    Instance Attributes:
        broker_host
        broker_port
        mqtt_client
        
        receiverQ Queue for messages received on subscribed topics
    """
      
    # Takes anything coming on the queue passed and publishes to MQTT
    async def connect(self, inQ: asyncio.Queue):
        reconnect_interval = 5

        while True:
            try:
                #establish connection
                async with Client(self.broker_host) as client:
                    await asyncio.create_task(self.poster(client, inQ)) # Add a poster coroutine 
                
            except:
                raise MqttError("Connection to Broker could not be setup")

            finally:
                logging.warning("MQTT Connection lost. Reconnecting in {}".format(reconnect_interval))
                await asyncio.sleep(reconnect_interval)

    # coroutine postng what is found on the queue
    async def poster(self, client: Client, queue: asyncio.Queue):
      
        while True:
            msg = await queue.get()     #get Message to publish from Queue
            logging.debug("Get messagage from queue. Now publishing MQTT: topic: {}, payload: {}".format(msg.mqttTopic, msg.mqttPayload))
            await client.publish(msg.mqttTopic, msg.mqttPayload, qos=1)
            
    
    
    # Constructor
    def __init__(self, host, port, client_id, miniserver: str):
        self.broker_host, self.broker_port = host, port
        self.client_id = client_id
        self.miniserver = miniserver
        

        
        
        