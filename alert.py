import notifications
import price
import rule

class Alert():
    def __init__(self, config, data = None):
        self.price = price.Price()
        self.rule = rule.Rule(config)
        self.config = config

    def handle_ticker(self, symbol, last_price):
        if symbol.lower() == self.config['symbol'].lower():
            self.price.update_price(last_price)
            if self.rule.should_notify(self.price) is True:
                notifications.Notifications(self.config, self.price).send_notifications()
                self.price.previous = self.price.current
