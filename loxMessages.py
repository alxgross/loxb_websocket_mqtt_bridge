# loxMessages.py
# Collection of Classes to handle the messages coming from the miniserver
# Author: Alx G
# Licence: Apache 2.0
import logging
from aiofile import AIOFile 
from bitstring import ConstBitStream #install bistring --> necessary to deal with Bit-Messages


#Description of a Loxone Header message (page 14)
class LoxHeader:
#    typedef struct {
#      BYTE cBinType; // fix 0x03 --> fixed marking a header, raise exception if not there
#      BYTE cIdentifier; // 8-Bit Unsigned Integer (little endian) --> Kind of message following the header
#            0: Text  1: Binary  2,3,4: Event Tables  5: out-of-service   6: Keep-alive  7: Wheather
#      BYTE cInfo; // Info
#      BYTE cReserved; // reserved
#      UINT nLen; // 32-Bit Unsigned Integer (little endian)

# The following attributes are set
#   msg_type : Defining the Message to follow this one
#   exact2Follow : Defining if another header will follow instead of a data-message

    def __init__(self, header_msg: bytes):
        #First byte
        if header_msg[0:1] != bytes.fromhex('03'):
            raise ValueError("This is not a header message")
        self.msg_type = self.__setIdentifier(header_msg[1:2])
        self.exact2Follow = self.__setExact2Follow(header_msg[2:3])
        #Bytes 4-8 could be decoded some other time --> would allow prediction of load times
        
        
    def __setIdentifier(self, secondByte: bytes):
        switch_dict = {
            b'\x00': 'text', #"Text-Message"
            b'\x01': 'bin', #"Binary File"
            b'\x02': 'valueStateTab', #"Event-Table of Value-States
            b'\x03': 'textStateTab', # Event-Table of Text-States
            b'\x04': 'daytimerTab', #Event-Table of Daytimer-States
            b'\x05': 'out-of-service', #e.g. Firmware-Upgrade - no following message at all. Connection closes
            b'\x06': 'still_alive', #response to keepalive-message
            b'\x07': 'weatherTab' # Event-Table of Wheather-States
            }
        return switch_dict.get(secondByte, "invalid")
    
    def __setExact2Follow(self, thirdByte: bytes):
        bitstream = ConstBitStream(thirdByte)
        bitstream.pos = 0
        if bitstream.read('bin:1') == '1':
            return True
        else:
            return False
            
# Base Class for State Messages
class LoxState:
    
    @staticmethod
    def decodeUUID(uuid: bytes) -> str:
        #     Binary-Structure of a UUID 16Byte
        # typedef struct _UUID {
        #  unsigned long Data1; // 32-Bit Unsigned Integer (little endian)
        #  unsigned short Data2; // 16-Bit Unsigned Integer (little endian)
        #  unsigned short Data3; // 16-Bit Unsigned Integer (little endian)
        #  unsigned char Data4[8]; // 8-Bit Uint8Array [8] (little endian)
        #Example from the structure-file in json however:
        # UUID: "12c3abc1-024e-1135-ffff7ba5fa36c093","name":"Gästezimmer UG Süd"
        # The strings are the hex representations of the numbers! in lowercase!
        #Decode UUID
        bitstream = ConstBitStream(uuid)
        data1, data2, data3, data41, data42, data43, data44, data45, data46, data47, data48 = bitstream.unpack('uintle:32, uintle:16, uintle:16, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8')
        uuid = "{:08x}-{:04x}-{:04x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(data1, data2, data3, data41, data42, data43, data44, data45, data46, data47, data48)
        return uuid
   
    def setUUID(self, uuid: bytes):
        self.uuid  = "" #UUID as String

        self.uuid = LoxState.decodeUUID(uuid)
   
class LoxValueState(LoxState):
    #Consists of UUID (16 byte) and Value 64-Bit Float (little endian) value
    # Each State-Entry in the table is consequently 24 byte long
    #

    
    def __init__(self, valueStateMsg: bytes):
        #for BitStream: https://bitstring.readthedocs.io/en/latest/constbitstream.html?highlight=read#bitstring.ConstBitStream.read
        
        if len(valueStateMsg) != 24:
            raise ValueError("Wrong message length for a ValueState Message")
        
        self.value = 0  #Value as Float
        
        LoxState.__init__(self)
        
        self.setUUID(valueStateMsg[0:16])
        
        #Decode Value
        bitstream = ConstBitStream(valueStateMsg[16:24])
        value_list = bitstream.unpack('floatle:64')
        self.value = str("{:g}".format(value_list[0]))
        
           
        
    @classmethod #cls is a "keyword" for the class itself. Hence, parseTable is not bound to an instance  
    async def parseTable(cls, eventTable: bytes) -> list:
        # take a longer message and split it and create ValueState-Instances
        # Return a dict with UUIDs and values
        instances = list()
        
        num_Values = len(eventTable) / 24
        logging.debug("Received {} State-Value-Messages in a table".format(num_Values))

        for i in range(0, len(eventTable), 24):
            instances.append( cls(eventTable[i:i+24]) ) # cls() creates an instance of the class itself
            
        return instances
    
    
# Text State - derived from LoxState
class LoxTextState(LoxState):
    #instance variables: uuid, uuid_icon, textLength and text
    
    #page 17/16 in Loxone Guide
    #typedef​ ​struct​ { ​// starts at multiple of 4
    #   PUUID​ ​uuid​; // 128-Bit uuid
    #   PUUID​ ​uuidIcon​; // 128-Bit uuid of icon
    # ​  unsigned long ​textLength;  // 32-Bit Unsigned Integer (little endian)
    #      // text follows here
    # } ​PACKED​ ​EvDataText​;
    
    def __init__(self, message):
        LoxState.__init__(self)
        
        self.msgLength: int = self.decode(message)
       
        
    def decode(self, message) -> int:
        # return length of the message decoded
        #logging.debug("Message length: {}, Message: {}".format(len(message), message))
        
        while len(message) < 36:
            logging.debug("Message too short: {} bytes actually, padding out with 0x00".format(len(message)))
            message += b"\x00"
            
         # extract UUID
        self.setUUID(message[0:16])
        
        # extract icon UUID
        self.uuid_icon = LoxState.decodeUUID(message[16:32])
        
        # calculate Text length
        bitstream = ConstBitStream(message[32:36])
        self.textLength: int = bitstream.read('uintle:32')
        
        # extract Text
        endPos = 36 + self.textLength
        
        self.text: str = message[36:endPos].decode("utf8")
       
        #return correct endPos after adding padding-bytes implicitly added            
        if self.textLength % 4 > 0:
            padding = 4 - self.textLength % 4 #padding bytes used when text length is not a multiple of 4
        else:
            padding = 0
        endPos += padding
        
        return endPos
        
    @classmethod #cls is a "keyword" for the class itself. Hence, parseTable is not bound to an instance  
    async def parseTable(cls, eventTable: bytes, writeFile = False) -> list:
        # take a longer message and split it and create ValueState-Instances
        instances = list() # List of instances created
        
        #write to Debugfile-file for now
        if writeFile:
            async with AIOFile(".cache/textStates.bin", "wb") as file:
                await file.write(eventTable)
                await file.fsync()
        
        
        totalLength = len(eventTable)
        logging.debug("State-Table received. Length: {}".format(totalLength))
        pos = 0
        i = 0
        while pos < totalLength:
            #logging.debug("Processing message part {}".format(i))
            textState = cls(eventTable[pos:])
            instances.append( textState )
            #logging.debug("Text State: UUID: {}, UUID-Icon: {}, Text-Length: {}, Text: {}".format( textState.uuid, textState.uuid_icon, textState.textLength, textState.text ))
            
            i += 1
            pos += textState.msgLength
                
        logging.debug("Received {} State-Text-Messages in a table. Created {} instances.".format(i, len(instances)))
        return instances

                                           