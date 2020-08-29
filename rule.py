class Rule():
    def __init__(self, config):
        self.rule_type = config['rule']['type']
        self.value = float(config['rule']['change'])

    def should_notify(self, price):
        
        if price.previous is None:
            return True
        previous = float(price.previous)
        current = float(price.current)
        change = float(price.change())
        value = float(self.value)
        if previous != current and (change >= self.value or change <= self.value*-1):
            return True

        return False
        