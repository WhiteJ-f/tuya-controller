import tinytuya, json, asyncio
from PIL import ImageGrab

with open('deviceData.json') as file:
    config = json.load(file)
    print

bulb = tinytuya.BulbDevice(config[0]['id'], config[0]['last_ip'], config[0]['key'])
bulb.set_version(3.3)

bulb.turn_on()
bulb.turn_off()