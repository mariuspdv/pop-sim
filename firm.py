# Definition of firms

class Firm:

    def __init__(self, workers, wages, productivity, profits=0):
        self.workers = workers
        self.wages = wages
        self.productivity = productivity
        self.profits = profits
        self.history = []
        self.add_to_history()

    def __str__(self):
        return f'Employés: {self.workers}'

    def add_to_history(self):
        self.history.append({k: v for k, v in vars(self).items() if k != 'history'})

    def get_from_history(self, thing, index, default=None):
        if len(self.history) == 0:
            return default
        return self.history[index][thing]

    def set_supply(self):
        '''offre totale'''
        return self.workers * self.productivity

    def update_firm(self, sold, prices, pops):
        '''changer l'état de la firme'''
        costs = self.wages * self.workers
        revenues = sold * prices
        self.profits = revenues - costs
        prev_profit = self.get_from_history('profits', -1, 0)
        if self.profits > prev_profit and pops.population > self.workers:
            self.workers += 1
        elif self.profits < prev_profit and self.workers > 1:
            self.workers -= 1


if __name__ == '__main__':
    f = Firm(workers=15, wages=1, productivity=1)
    print(f.set_supply())
    f.add_to_history()
    f.add_to_history()
    print(f.history)
    print(f)