# The most boring superhero

class Historizor:

    def __init__(self):
        self.history = []

    def add_to_history(self):
        self.history.append({k: v.copy() if type(v) is dict or type(v) is list else v
                             for k, v in vars(self).items() if not (k == 'history' or k.startswith('_'))})

    def get_from_history(self, thing, index, default=None):
        if len(self.history) == 0:
            return default
        return self.history[index][thing]
