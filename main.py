from bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep
import datetime
import websockets
from websockets.exceptions import ConnectionClosed
import asyncio
import json
import requests

previous = 8900


async def capture_data():
    uri = "wss://www.bitmex.com/realtime?subscribe=instrument:XBTUSD"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                data = await websocket.recv()
                data = json.loads(data)
            except (ConnectionClosed):
                print("Connection is Closed")
                send_to_slack("Connection is Closed")
                data = None
                sleep(10)
                continue
            if "data" in data:
                price = data.get('data')[0].get('lastPrice')
                if price:
                    global previous
                    print(price)
                    print(get_change(price, previous))
                    price = data.get('data')[0].get('lastPrice')
                    set_price(price)


def set_price(current):
    global previous
    change = get_change(current, previous)
    if previous != current and (change >= 0.5 or change <= -0.5):
        currentDT = datetime.datetime.now()
        change_f = "{:.2f}".format(change)
        date_f = currentDT.strftime("%Y-%m-%d %H:%M:%S")

        print("#############################")
        print(f'Current: {current} USD')
        print(f'Previous: {previous} USD')
        print(f'Change: {change_f}%')
        print(date_f)
        print('#############################\n\n')
        message = format_message(current, previous, change)
        send_to_slack(message)

        previous = current

def send_to_slack(message):
    API_ENDPOINT = "https://hooks.slack.com/services/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"
    data = {'payload':'{"text": "' + message + '"}'} 

    return requests.post(url = API_ENDPOINT, data = data) 

def format_message(current, previous, change):
    change_f = "{:.2f}".format(change)
    message = f"${previous} to ${current}  {change_f}%"

    return message

def get_change(current, previous):
    if current == previous:
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
except:
    send_to_slack("Exception")
    print(Exception.__cause__)
