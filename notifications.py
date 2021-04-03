import requests
import http.client, urllib
import logging

class Notifications():

    def __init__(self, config, price):
        self.config = config
        self.message = None
        self.current = price.current
        self.previous = price.previous
        self.change = price.change
        self.title = "Starting..."

    def _format_message(self):
        current_f = self._truncate(float(self.current), self.config['width'])
        if self.previous is None:
            return f"Starting {self.config['label'].upper()} ({self.config['exchange']['label']}) alert @ {current_f}"

        if float(self.current) > float(self.previous):
            up_or_down = "up"
            emoji = "🟢"
        else:
            up_or_down = "down"
            emoji = "🔴"

        change_f = "{:.2f}".format(float(self.change()))
        self.title = self.config['label'].upper() + " " + emoji

        return f"{self.config['exchange']['label']}: {self.config['label'].upper()} {up_or_down} @ {current_f} (%{change_f})"

    def _send_to_pushover(self):
        devices = self.config['tokens']["pushover"]
        for device in devices:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": device["token"],
                "user": device["user"],
                "message": self.message,
                "title": self.title,
                "html": 1,
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
            logging.warning(f"Pushover sent: {self.message}")

    def _send_to_slack(self):
        API_ENDPOINT = self.config['tokens']["slack"]["endpoint"]
        data = {'payload':'{"text": "' + self.message + '"}'}
        requests.post(url=API_ENDPOINT, data=data)
        logging.warning(f"Slack sent: {self.message}")

    def _send_to_telegram(self):
        
        bot_token = self.config['tokens']["telegram"]["bot_token"]
        chat_ids = self.config['tokens']["telegram"]["chat_ids"]
        for chat_id in chat_ids:
            send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={self.message}"
            response = requests.get(send_text)
            logging.warning(response.json())

    def _truncate(self, number, position):
        width = "{:." + str(position) + "f}"
        '''Return number with dropped decimal places past specified position.'''
        return width.format(number)

    def send_notifications(self):
        self.message = self._format_message()
        self._send_to_pushover()
        self._send_to_telegram()


