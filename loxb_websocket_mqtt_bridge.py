# LoxBerry Service to Connect to your Miniserver via Websockets and send mqtt telegrams
# Name: loxb_websocket_mqtt_bridge
# Author: Alx G
# Licence: Apache 2.0

from settings import Env
env = Env("LOX_")


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete()
    loop.run_forever()


