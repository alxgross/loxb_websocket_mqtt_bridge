class QMessage:
    """ QMessage shall include the data structure to interchange between the Miniserver Connection
        and the MQTT Instance
    
    Instance Attributes
    
    origin (miniserver, this_bridge or mqtt)
    appliance: unique identifier
    value: set after translation
    
    mqttTopic (Sensor/Actuator)
    mqttPayloadd
    
    loxCommand: The Loxone Command
    
    """
    
    def __init__(self, origin: str, loxUuid: str = "", loxCommand: str = "", loxValue: str = "", mqttTopic: str = "miniservers", mqttPayload: str = ""):
        self.origin = origin
        self.appliance = loxUuid
        
        self.loxCommand = loxCommand
        #Logic is missing yet
        if loxValue == False:
            self.value = mqttPayload
        else:
            self.value = loxValue
        
        self.mqttTopic = mqttTopic
        self.mqttPayload = mqttPayload
        
    #Steps to be done
        #identify what value type it is
        # translate
        # use structure file to get more infos
        
    #Get the Structure file from Miniserver with all the descriptions
#     @classmethod
#     async def getStructureFile(cls):
#         #Get the structure file from the Miniserver (page 18)
#         command = "data/LoxAPP3.json"
#         header = LoxHeader(await myWs.recv())
#         print(header.msg_type)
#         #print("Structure File: ", json.dumps(structure_file))
#         print(await myWs.recv())
#         structure_file = await myWs.recv()
#         struct_dict = json.loads(structure_file)