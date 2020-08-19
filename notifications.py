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

    def _format_message(self):
        current_f = self.truncate(float(self.current), self.config['pos'])
        if self.previous is None:
            return f"Starting {self.config['tkr']} alert @ {current_f}"

        if float(self.current) > float(self.previous):
            up_or_down = "up"
        else:
            up_or_down = "down"

        change_f = "{:.2f}".format(float(self.change))

        return f"Alert {self.config['tkr']} {up_or_down} @ {current_f} (%{change_f})"

    def _send_to_pushover(self):
        print(self.config)
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": self.config['tokens']["pushover"]["token"],
            "user": self.config['tokens']["pushover"]["user"],
            "message": "Binance: " + self.message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        logging.warning(f"Pushover sent: {self.message}")

    def _send_to_slack(self):
        API_ENDPOINT = self.config['tokens']["slack"]["endpoint"]
        data = {'payload':'{"text": "' + self.message + '"}'}
        requests.post(url=API_ENDPOINT, data=data)

    def send_notifications(self):
        self.message = self._format_message()
        self._send_to_pushover()

    def truncate(self, number, position):
        width = "{:." + str(position) + "f}"
        '''Return number with dropped decimal places past specified position.'''
        return width.format(number)
