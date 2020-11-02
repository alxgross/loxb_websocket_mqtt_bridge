class QMessage:
    """ QMessage shall include the data structure to interchange between the Miniserver Connection
        and the MQTT Instance
    
    Instance Attributes
    
    Appliance (Sensor/Actuator)
    Value
    
    loxCommand: The Loxone Command
    
    """
    
    def __init__(self, appliance: str, value: str):
        self.appliance = appliance
        self.value = value
        
    async def setLoxCommand(self, command):
        self.loxCommand = command
        
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