import asyncio
import logging
from gmqtt import Client as MQTTClient #https://github.com/wialon/gmqtt
from QMessage import QMessage #our interchange format

class LoxBerry:
    """ Class representing the LoxBerry - attached via MQTT 

    Instance Attributes:
        broker_host
        broker_port
        mqtt_client
        
        receiverQ Queue for messages received on subscribed topics
    """
    #class attribute

    def on_subscribe(self, client, mid, qos, properties):
        logging.info('Subscribed: {} '.format(client._client_id))
        
        
    async def on_message(self, client, topic, payload, qos, properties):
        logging.info('RECV MSG: {} {}'.format(topic, payload))
        await self.receiverQ.put(QMessage(topic, payload))


    def on_connect(self, client, flags, rc, properties):
        logging.info('[CONNECTED {}]'.format(client._client_id))
    
### Instance Methods
    async def connect(self):
        try:
            await self.mqtt_client.connect(self.broker_host,self.broker_port)            #establish connection
        except:
            raise ConnectionError("Connection to Broker could not be setup")
        
        
    # Takes anything coming on the queue passed and publishes to MQTT
    async def MQTTsender(self, queue: asyncio.Queue):
        while True:
            msg = await queue.get()     #get Message to publish from Queue
            #msg.appliance msg.value
            self.mqtt_client.publish(msg.appliance, msg.value)  
            
    
    
    # Subscribes to a topic and then fills a given queue with messages
    async def MQTTreceiver(self, queue: asyncio.Queue):
        self.mqtt_client.subscribe('ALX/Command/#')
        logging.info("Subscribed to Topic")
        self.receiverQ = queue
        
        
        
    
    # Constructor
    def __init__(self, host, port, client_id):
        self.broker_host, self.broker_port = host, port
        self.client_id = client_id
        self.mqtt_client = MQTTClient(self.client_id, session_expiry_interval=60)       #create client object
        
        # Assign callback functions
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect
        
        
        