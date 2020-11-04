# Loxone LoxBerry Module bridging Websockets sent/received from Miniserver and MQTT Telegrams
 Connect to the Miniserver via websockets and receive mqtt telegrams

## Usage
First, create a .env-File in the directory of this program with the necessary config.
run python3 loxb_websocket_mqtt_bridge

OR start it as a service (look here: https://github.com/torfsen/python-systemd-tutorial)


## Make me Happy
Let me know if you like what you see and PLEASE, PLEASE don't hesitate if you see ugly code or errors to create a PULL-request


## MQTT Conventions

Bridge will publish on /miniservers/<miniserver_name>/<room>/<category>/<device name>/<UUID>

It subscribes on:
    /miniservers/.../command
    /miniservers/.../announce -> will trigger an announce-message with details from the structure-file
    /miniservers/.../update -> will trigger bridge to get current state of appliance via rest-api and publish to mqtt
    
    
## Dependencies

Developed on Python 3.7.7

Packages necessary to be installed
    aiofile
    requests
    attr
    gmqtt
    websockets
    