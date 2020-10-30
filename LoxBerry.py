import asyncio
from gmqtt import Client as MQTTClient #https://github.com/wialon/gmqtt

class LoxBerry:
    """ Class representing the LoxBerry - attached via MQTT 

    Instance Attributes:
        broker_host
        broker_port
        mqtt_client 
    """
    #class attribute

    def on_subscribe(self, client, mid, qos, properties):
        print("Subscription setup")
        
        
    def on_message(self, client, topic, payload, qos, properties):
        print("message received")
        
    def on_connect(self, client, flags, rc, properties):
        print('[CONNECTED {}]'.format(client._client_id))
    
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
            ret = self.mqtt_client.publish('ALXTEST/A', msg.value)  
            print("MQTT sender: ", msg.appliance, msg.value, ret)
            await asyncio.sleep(2)
            
    
    
    # Subscribes to a topic and then fills a given queue with messages
    async def MQTTreceiver(self, queue: asyncio.Queue):
        self.mqtt_client.subscribe('ALXTEST/A')
        print("Subscribed")
        
    
    # Constructor
    def __init__(self, host, port, client_id):
        self.broker_host, self.broker_port = host, port
        self.client_id = client_id
        self.mqtt_client = MQTTClient(self.client_id)       #create client object
        
        # Assign callback functions
        self.on_subscribe = self.on_subscribe
        self.on_message = self.on_message
        self.on_connect = self.on_connect
        
        
        