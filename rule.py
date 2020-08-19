class Rule():
    def __init__(self, rule_type, value):
        self.rule_type = rule_type
        self.value = value

    def should_notify(self, current, previous, change):
        if previous is None:
            return True
        if float(previous) != float(current) and (float(change) >= float(self.value) or float(change) <= (float(self.value)*-1)):
            return True

        return False
        