# Class representing the miniserver with associated methods to connect
import asyncio
import logging
from QMessage import QMessage #own Class 
import requests   #lib for GET, POST, PUT etc.
import websockets

#Install pyCryptoDome NOT pyCrypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
import hashlib   #Hashing
import hmac      #Key-Hashing

import urllib    #necessary to encode URI-compliant
import base64    #necessary to encode in Base64
import secrets   #helpful to produce hashes and random bytes
import binascii  #hexlify/unhexlify allows to get HEX-Strings out of bytes-variables
import json      #work with json

import loxMessages  # Decoding of Bits and Bytes of Loxone Messages


class LoxMiniserver:
    """
    Instance Attributes:
        IP-Address of Miniserver
        Port
        User
        Password
        client UUID
        
        rsa_pub_key : Miniserver's public RSA key
        AES Key and IV : Generated and set at instance
        sessionkey : (client generated AES Key and IV) encrypted via the Miniserver's RSA public key
        sha1_key and salt : Miniserver delivers them via jdev/sys/getkey2/{user.name}
        
        websocket : after connection been established and token aquired
    """
    
    
    # Get the RSA public key from the miniserver and format it so that it is compliant with a .PEM file 
    def prepareRsaKey(self):
        try:
            response = requests.get("http://{}:{}/jdev/sys/getPublicKey".format(self.ip, self.port))
            rsa_key_malformed = response.json()["LL"]["value"]
            #fix the malformed public key
            rsa_key_malformed = rsa_key_malformed.replace("-----BEGIN CERTIFICATE-----", "-----BEGIN PUBLIC KEY-----\n")
            self.rsa_pub_key = rsa_key_malformed.replace("-----END CERTIFICATE-----", "\n-----END PUBLIC KEY-----")
            logging.info("RSA Public Key set for Instance: {}".format(self.rsa_pub_key))
        except:
            logging.error("Could not get RSA public key via /jdev/sys/getPublicKey")
    
    
    #get Sha1 Key and Salt
    def getSha1KeySalt(self):
        try:
            # Get the key to be used for the HMAC-Hashing and the Salt to be used for the SHA1 hashing
            response = requests.get("http://{}:{}/jdev/sys/getkey2/{}".format(self.ip, self.port, self.user))
            self.sha1_key = response.json()["LL"]["value"]["key"]
            self.sha1_salt = response.json()["LL"]["value"]["salt"]
            logging.info("Set SHA1 Key and Salt in session")
        except:
            logging.error("Could not get SHA1 Key and Salt via jdev/sys/getkey2/\{user.name\} from Miniserver")
            
    
    #Encrypt the AES Key and IV with RSA (page 7, step 6)
    def setSessionKey(self):
        # Generate AES Key and IV
        self.aes_key = binascii.hexlify(Random.get_random_bytes(32)).decode().upper()
        self.aes_iv = binascii.hexlify(Random.get_random_bytes(16)).decode().upper()
        
        
        # Function to RSA encrypt the AES key and iv
        payload = self.aes_key + ":" + self.aes_iv
        payload_bytes = payload.encode()
        #RSA Encrypt the String containing the AES Key and IV
        #https://8gwifi.org/rsafunctions.jsp
        #RSA/ECB/PKCS1Padding
        pub_key = RSA.importKey(self.rsa_pub_key)
        encryptor = PKCS1_v1_5.new(pub_key)
        sessionkey = encryptor.encrypt(payload_bytes)
        #https://www.base64encode.org/ to compare

        self.sessionkey = base64.standard_b64encode(sessionkey).decode()
    
        logging.info("Secret AES Key and IV set")
        
    # AES encrypt with the shared AES Key and IV    
    async def aes_enc(self, text):
        key = binascii.unhexlify(self.aes_key)
        iv = binascii.unhexlify(self.aes_iv)
        encoder = AES.new(key, AES.MODE_CBC, iv=iv)
        encrypted_msg = encoder.encrypt(await self.pad(text.encode()))
        b64encoded = base64.standard_b64encode(encrypted_msg)
        return urllib.parse.quote(b64encoded, safe="") #Return url-Encrypted
     

    # ZeroBytePadding to AES block size (16 byte) to allow encryption 
    async def pad(self, byte_msg):
        return byte_msg + b"\0" * (AES.block_size - len(byte_msg) % AES.block_size) #ZeroBytePadding / Zero Padding


    # Key-Hash the User and Password HMAC-SHA1 (page 22)
    async def hashUserPw(self, user, password):
        pwHash = await self.hash_Password(password)
        userHash = await self.digest_hmac_sha1("{}:{}".format(user, pwHash), self.sha1_key)
        #The userHash shall be left like it is
        return userHash
        

    # Hash the Password plain and simple: SHA1 (page 22)
    async def hash_Password(self, password):
        #check if result is this: https://passwordsgenerator.net/sha1-hash-generator/
        tobehashed = password + ":" + self.sha1_salt
        hash_alx = hashlib.sha1(tobehashed.encode())
        #according to the Loxone Doc, the password Hash shall be upper case
        hashstring = hash_alx.hexdigest()
        logging.info("Password successfully hashed.")
        return hashstring.upper()
        

    # HMAC-SHA1 hash something with a given key
    async def digest_hmac_sha1(self, message, key):
        #https://gist.github.com/heskyji/5167567b64cb92a910a3
        #compare: https://www.liavaag.org/English/SHA-Generator/HMAC/  -- key type: text, output: hex
        hex_key = binascii.unhexlify(key)
        message = bytes(message, 'UTF-8')
        
        digester = hmac.new(hex_key, message, hashlib.sha1)
        signature1 = digester.digest()
        
        signature2 = binascii.hexlify(signature1)    
        logging.info("hmac-sha1 output: {}".format(signature2.decode()))
        #return a hex string
        return signature2.decode()
        
        
    
    async def encryptCommand(self, command):
        #A ramdom salt of 2 bytes is generated (page 8, step 8)
        aes_salt = binascii.hexlify(secrets.token_bytes(2)).decode()
        
        to_encrypt = "salt/{}/{}".format(aes_salt, command)
        
        #Now encrypt the command with AES (page 21 step 1 & 2)
        encrypted_command = await self.aes_enc(to_encrypt)
        message_to_ws = "jdev/sys/enc/{}".format(encrypted_command) # page 21, step 3
        logging.info("Message to be sent: {}".format(message_to_ws))
        
        return message_to_ws
        
        
        
    # Request a Json webtoken
    async def getToken(self):
        
        #Check if valid token is existant
        #... read file ... /to be done
        # if not...
        getTokenCommand = "jdev/sys/getjwt/{}/{}/{}/{}/{}".format(await self.hashUserPw(self.user, self.password), self.user, self.permission, self.client_uuid, self.client_id)
        logging.info("GetToken Command built: {}".format(getTokenCommand))
        return getTokenCommand
    

    
    # Connect and setup websocket
    async def receiver(self, queue: asyncio.Queue):
            
#         try:
            #start websocket connection (page 7, step 3 - protocol does not need to be specified apparently)
            async with websockets.connect("ws://{}:{}/ws/rfc6455".format(self.ip, self.port)) as myWs:
                
                #Send Session Key (page 8, step 7)
                await myWs.send("jdev/sys/keyexchange/{}".format(self.sessionkey))
                lox_header = loxMessages.LoxHeader(await myWs.recv())
                logging.info("Received Loxone Header Type: {}".format(lox_header.msg_type))
                if lox_header.msg_type != "text":
                    logging.error("Answer from Miniserver not expected: should be text-header")
                    raise ConnectionAbortedError("We stop here as the keyexchange failed already")
                response = json.loads(await myWs.recv())
                if response["LL"]["Code"] == "200":
                    logging.info("Keyexchange successful")
                else:
                    logging.info("Keyexchange failed with Code :{}".format(response["LL"]["Code"]))


                #Get token (as encrypted command)
                #Send message to get a JSON webtoken
                await myWs.send(await self.encryptCommand(await self.getToken()))
                lox_header = loxMessages.LoxHeader(await myWs.recv())
                if lox_header.msg_type != "text":
                    logging.error("Answer from Miniserver not expected: should be text-header")
                    raise ConnectionAbortedError("We stop here as the getToken failed already")
                response = json.loads(await myWs.recv())
                logging.info("Answer to getToken: {}".format(response))
                
                #EERROR handling missing
                
                logging.info("getToken successful")
     

#                 else:
#                     logging.info("getToken failed with Code :{}".format(response["LL"]["Code"]))
                
#         except:
#             logging.error("Websocket connection could not be established")
    
    
    
                #Receive Messages from Miniserver and send to Queue as QMessage
   
                            
                #Enable State update and start receiving
                await myWs.send("jdev/sps/enablebinstatusupdate")

                #Receive Messages from Miniserver
                while True:
                    
                    #Process header
                    header = loxMessages.LoxHeader(await myWs.recv())
                    if header.exact2Follow == True:
                        header = loxMessages.LoxHeader(await myWs.recv())

                    #Process Message/Decode it
                    if header.msg_type == 'value':
                        message = await myWs.recv()
                        #KAPUTT statesDict = await loxMessages.LoxValueState.parseTable(message)
                    
                        #HIER fehlt ein async for über alle messages
                        valueState = loxMessages.LoxValueState(message)
                        logging.info("UUID: {} Value: {}".format(valueState.uuid, valueState.value))
                        
                        #Translate --> to be implemented
                    
                
                        #Put it on queue to be sent to MQTT
                        await queue.put(QMessage("ALX/{}".format(valueState.uuid), valueState.value)) #Put the Message on the Queue
                    else:
                        logging.info("Unknown Miniserver Message received: {}".format(await myWs.recv()))
            
            
    
    
    # Send Messages to Miniserver
    async def sender(self, queue: asyncio.Queue):
        # take message from queue
        
        # translate to Lox-Message
        
        # send to Loxone Miniserver
        
        pass
    
    
    #Constructor
    def __init__(self, ip, port, user, password, client_uuid):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.client_uuid = client_uuid
        
        self.client_id =  "loxb_websocket_mqtt_bridge_by_alx_g"
        self.permission = "4" #2 for short period, 4 for long period
        
        self.prepareRsaKey()
        self.getSha1KeySalt()
        self.setSessionKey()