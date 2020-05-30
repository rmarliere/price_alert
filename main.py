import logging
from time import sleep
import datetime
import websockets
from websockets.exceptions import ConnectionClosed
import asyncio
import json
import requests
import http.client, urllib
import logging

previous = None

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def capture_data():
    uri = "wss://www.bitmex.com/realtime?subscribe=instrument:XBTUSD"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    try:
                        data = await websocket.recv()
                        data = json.loads(data)
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed): 
                        logging.info("Connection is closed.")
                        try:
                            logging.info("Reconnecting...")
                            pong = await websocket.ping()
                            await asyncio.wait_for(pong, timeout=10)
                            continue
                        except:
                            logging.info("Sleeping...")
                            await asyncio.sleep(2)
                            break              
                        
                    if "data" in data:
                        logging.info(data)
                        price = data.get('data')[0].get('lastPrice')
                        if price:
                            global previous
                            price = data.get('data')[0].get('lastPrice')
                            handle_price(price)

        except ConnectionRefusedError:
            logging.info("ConnectionRefusedError", exc_info=True)
            continue
        except Exception as e:
            logging.error("Exception websocket occurred", exc_info=True)
            continue

def handle_price(current):
    global previous
    change = get_change(current, previous)
    message = format_message(current, previous, change)
    if previous is None:
        send_to_pushover(message)
        previous = current
        return
    if previous != current and (change >= 0.5 or change <= -0.5):
        send_to_pushover(message)
        previous = current

        # currentDT = datetime.datetime.now()
        # change_f = "{:.2f}".format(change)
        # date_f = currentDT.strftime("%Y-%m-%d %H:%M:%S")

        # print("#############################")
        # print(f'Current: {current} USD')
        # print(f'Previous: {previous} USD')
        # print(f'Change: {change_f}%')
        # print(date_f)
        # print('#############################\n\n')
        # send_to_slack(message)

def send_to_pushover(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "ak35kuephhqysw65b1n6fqxvhost62",
        "user": "uuj1gq3wyx2aedh2cnbnksxqt2o2wv",
        "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    logging.info(f"Pushover sent: {message}")

def send_to_slack(message):
    API_ENDPOINT = "https://hooks.slack.com/services/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"
    data = {'payload':'{"text": "' + message + '"}'}
    requests.post(url = API_ENDPOINT, data = data) 

def format_message(current, previous, change):
    if previous is None:
        return f"Starting alert @ {current}"

    if current > previous:
        up_or_down = "up"
    else:
        up_or_down = "down"

    change_f = "{:.2f}".format(change)

    return f"Alert XBTUSD {up_or_down} @ {current} (%{change_f})"

def get_change(current, previous):
    if current == previous or previous is None:
        return 0

    try:
        change = (abs(current - previous) / previous) * 100.0
        if (previous > current):
            return change * -1

        return change

    except ZeroDivisionError:
        return 0

try:
    asyncio.get_event_loop().run_until_complete(capture_data())
    asyncio.get_event_loop().run_forever()
except Exception as e:
    logging.error("Exception asyncio occurred", exc_info=True)
