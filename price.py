class Price():
    def __init__(self, current=0, previous=None, change=0):
        self.current = current
        self.previous = previous
        self.change = change

    def get_percentage_change(self):
        current = self.current
        previous = self.previous
        if current == previous or previous is None:
            return float(0)

        try:
            change = (abs(float(current) - float(previous)) / float(previous)) * 100.0
            if (float(previous) > float(current)):
                return float(change * -1)

            return float(change)

        except ZeroDivisionError:
            return float(0)

    def get_value_change(self):
        current = self.current
        previous = self.previous
        if current == previous or previous is None:
            return float(0)

        try:
            change = (abs(float(current) - float(previous)) / float(previous)) * 100.0
            if (previous > current):
                return float(change * -1)

            return float(change)

        except ZeroDivisionError:
            return float(0)