#helper reading a stateTable and trying to decode it
import logging
import asyncio
import loxMessages 
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

async def main(message):
    await loxMessages.LoxTextState.parseTable(message)


with open(".cache/textStates.bin", "rb") as file:
    message = file.read()
    
print(message)



loop = asyncio.get_event_loop()
loop.run_until_complete(main(message))