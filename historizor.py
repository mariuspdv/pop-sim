# The most boring superhero

class Historizor:

    def __init__(self):
        self.history = {}

    def add_to_history(self, time):
        self.history[time] = {k: v.copy() if type(v) is dict or type(v) is list else v
                             for k, v in vars(self).items() if not (k == 'history' or k.startswith('_'))}

    def get_from_history(self, thing, index, default=None):
        if len(self.history) == 0:
            return default
        # For positive index, return the absolute time. For negative, start from the end
        # Actually, it works like the "list"
        if index >= 0:
            line = self.history.get(index)
        else:
            last_time = max(self.history.keys())
            line = self.history.get(last_time + index + 1)
        if line is None:
            return None
        return line[thing]
