import sys
import logging
from time import sleep
import datetime
import websockets
from websockets.exceptions import ConnectionClosed
import asyncio
import json
import requests
import http.client, urllib
import notifications
import alert

alert_objects = []

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("binance.log"),
        logging.StreamHandler()
    ]
)

# load config parameters to memory
with open("config.json") as f:
    config = json.load(f)


async def capture_data(uri):
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    try:
                        data = await websocket.recv()
                        data = json.loads(data)
                        logging.info(data)
                        callback_fn(data)
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed): 
                        logging.warning("Connection is closed.")
                        try:
                            logging.warning("Reconnecting...")
                            pong = await websocket.ping()
                            await asyncio.wait_for(pong, timeout=3)
                            continue
                        except:
                            logging.warning("Sleeping...")
                            await asyncio.sleep(2)
                            continue

        except ConnectionRefusedError:
            logging.error("ConnectionRefusedError", exc_info=True)
            continue
        except Exception as e:
            logging.error("Exception websocket occurred", exc_info=True)
            continue

def get_stream_uri():
    uri = "wss://stream.binance.com:9443/stream?streams="
    for config_alert in config["alerts"]:
        uri = uri + config_alert['symbol'] + "@ticker"
        if config_alert != config["alerts"][-1]:
            uri = uri + "/"

    return uri

def get_alert_objects():
    l = []
    for config_alert in config["alerts"]:
        config_alert['tokens'] = config['tokens']
        l.append(alert.Alert(config_alert))

    return l

def callback_fn(data):
    #global alert_object
    for alert_object in alert_objects:
        alert_object.handle_ticker(data['data']['s'], data['data']['c'])

try:
    alert_objects = get_alert_objects()
    uri = get_stream_uri()
    asyncio.get_event_loop().run_until_complete(capture_data(uri))
    asyncio.get_event_loop().run_forever()
except Exception as e:
    logging.error("Exception asyncio occurred", exc_info=True)
