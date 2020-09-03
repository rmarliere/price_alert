
from datetime import datetime
import hmac
import hashlib
import requests
import asyncio
import logging
import json
import alert
from time import sleep

alert_objects = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("newdex.log"),
        logging.StreamHandler()
    ]
)

# load config parameters to memory
with open("config.json") as f:
    config = json.load(f)

async def capture_data():
    while True:
        try:
            await asyncio.sleep(1)
            loop = asyncio.get_event_loop()
            url = get_newdex_url()
            request = loop.run_in_executor(None, requests.get, url)
            response = await request
            data = json.loads(response.text)
            logging.info(data)
            callback_fn(data)
        except (asyncio.TimeoutError): 
            logging.warning("async error")
            await asyncio.sleep(2)
            continue
        except (requests.ConnectionError):
            logging.warning("Connection is closed.")
            await asyncio.sleep(2)
            continue

def get_newdex_url():
    timestamp = int(datetime.now().timestamp())

    api_key = "cntsinh0fn39hjl7"
    secret = b"fihtrsbkv2ew1jh6tlyvy2zjw68skvdq"
    params = f"api_key={api_key}&symbol=token.defi-box-eos&timestamp={timestamp}"
    sign = hmac.new(secret, params.encode('utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    url = f"https://api.newdex.io/v1/ticker?{params}&sign={sign}"

    return url

def get_alert_objects():
    l = []
    for config_alert in config["alerts_newdex"]:
        config_alert['tokens'] = config['tokens']
        l.append(alert.Alert(config_alert))

    return l

def callback_fn(data):
    #global alert_object
    if data['code'] != 200:
        logging.error("Exception asyncio occurred", exc_info=True)
        return None
    for alert_object in alert_objects:
        alert_object.handle_ticker(data['data']['symbol'], data['data']['last'])

try:
    alert_objects = get_alert_objects()
    asyncio.get_event_loop().run_until_complete(capture_data())
    asyncio.get_event_loop().run_forever()
except Exception as e:
    logging.error("Exception asyncio occurred", exc_info=True)
