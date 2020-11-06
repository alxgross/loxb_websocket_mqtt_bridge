import logging

class QMessage:
    """ QMessage shall include the data structure to interchange between the Miniserver Connection
        and the MQTT Instance
    
    Instance Attributes
    
    origin (miniserver, this_bridge or mqtt)
    
    loxDict: Structure file - necessary infos to translate
    loxUuid: UUID in state-table
    loxValue: Value out of State-Table
    loxCommand: a command that should be sent to Miniserver
       
    mqttTopic (Sensor/Actuator)
    mqttPayload
    mqttDict : dictionary defining the rules 
    
    
    """
    
    #prepare the MQTT telegram accordingly
    def computeMqtt(self):
        
        #Compute for sensible controls - global states etc... maybe later...
        
        server_serial = self.loxDict["msInfo"]["serialNr"]
        
        try:
        
            # Get name and links to cat and room for control
            control_uuid = self.loxUuid
            control_name = self.loxDict["controls"][control_uuid]["name"]
            room_uuid = self.loxDict["controls"][control_uuid]["room"]
            cat_uuid = self.loxDict["controls"][control_uuid]["cat"]
            room_name = self.loxDict["rooms"][room_uuid]["name"]
            cat_name = self.loxDict["cats"][cat_uuid]["name"]
            
            #build the topic
            # structure miniservers/<miniserver-serial>/<room>/<category>/<name>/<uuid>
            self.mqttTopic = "miniservers/{}/{}/{}/{}/{}".format(server_serial, room_name, cat_name, control_name, control_uuid)
            logging.debug("MQTT Topic computed: {}".format(self.mqttTopic))
        
        except KeyError as exc:
            logging.debug("Not possible to compute MQTT for uuid {}. Error: {}".format(self.loxUuid, exc))
            self.mqttTopic = "miniservers/{}/not_mapped/{}".format(server_serial, self.loxUuid)


        #build the payload
        self.mqttPayload = self.loxValue
        logging.debug("MQTT Payload set: {}".format(self.mqttPayload))
        
        
    def computeLoxCommand(self):
        uuidFound = "12c3ac9b-00fa-1235-ffff7ba5fa36c093"
        value: str = self.mqttPayload
        self.loxCommand = "jdev/sps/io/{}/{}".format(uuidFound, value)
    
    def __init__(self, origin: str, loxDict: dict = {}, loxUuid: str = "", loxValue: str = "", loxCommand: str = "", mqttTopic: str = "", mqttPayload: str = ""):
        self.origin = origin
        
        QMessage.loxDict = loxDict #set as a class attribute, awailable to any instance
        
        if loxUuid:
            self.loxUuid = loxUuid
            self.loxValue = loxValue
            self.computeMqtt()
            
        if loxCommand:
            self.loxCommand = loxCommand
        
        if mqttTopic:
            self.mqttTopic = mqttTopic
            self.mqttPayload = mqttPayload
            self.computeLoxCommand()
        
    
    #Steps to be done
        #identify what value type it is
        # translate
        # use structure file to get more infos
        

