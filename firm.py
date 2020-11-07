# Definition of a Firm
from historizor import Historizor


class Firm(Historizor):

    def __init__(self, product, workers, wages, productivity, profits=0):
        super().__init__()
        self.product = product
        self.workers = workers
        self.wages = wages
        self.productivity = productivity
        self.profits = profits
        self.add_to_history()

    def __str__(self):
        return f'Employés: {self.workers}; ' \
               f'Profits: {self.profits}'

    def set_supply(self):
        """computes the supply of one firm"""
        return self.workers * self.productivity

    def add_to_total_supply(self, tot_supply):
        if self.product not in tot_supply:
            tot_supply[self.product] = 0
        tot_supply[self.product] += self.set_supply()

    def update_firm(self, sold, prices, world):
        """changes the firm's state using sales data"""
        costs = self.wages * self.workers
        revenues = sold[self.product] * prices[self.product]
        self.profits = revenues - costs
        prev_profit = self.get_from_history('profits', -1, 0)
        if self.profits > prev_profit and self.profits > 0 and world.tot_population > self.workers:
            self.workers += 1
        elif (self.profits < prev_profit or self.profits < 0) and self.workers > 1:
            self.workers -= 1


if __name__ == '__main__':
    f = Firm(workers=15, wages=1, productivity=1)
    print(f.set_supply())
    f.add_to_history()
    f.add_to_history()
    print(f.history)
    print(f)
