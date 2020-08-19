import notifications
import price
import rule

class Alert():
    def __init__(self, config, data = None):
        self.price = price.Price()
        self.rule = rule.Rule(config['rule']['type'], config['rule']['change'])
        self.ticker = config['symbol']
        self.config = config

    def handle_ticker(self, data):
        _ticker = data['data']['s']
        if _ticker.lower() == self.ticker.lower():
            self.price.current = data['data']['c']
            self.price.change = self.price.get_percentage_change()
            should_notify = self.rule.should_notify(self.price.current, self.price.previous, self.price.change)
            if should_notify is True:
                notifications.Notifications(self.config, self.price).send_notifications()
                self.price.previous = float(self.price.current)
