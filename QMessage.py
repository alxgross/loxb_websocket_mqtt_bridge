class QMessage:
    """ QMessage shall include the data structure to interchange between the Miniserver Connection
        and the MQTT Instance
    
    Instance Attributes
    
    Appliance (Sensor/Actuator)
    Value
    
    """
    
    def __init__(self, appliance: str, value: str):
        self.appliance = appliance
        self.value = value