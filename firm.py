# Definition of a Firm
from historizor import Historizor


class Firm(Historizor):

    THROUGHPUT_FLOOR = 0.9

    def __init__(self, product, workers, wages, productivity, profits=0):
        super().__init__()
        self.product = product
        self.workers = workers
        self.wages = wages
        self.productivity = productivity
        self.supply = workers * productivity
        self.profits = profits
        self.add_to_history()

    def __str__(self):
        return f'Employees: {self.workers}; ' \
               f'Profits: {self.profits}'

    def set_supply(self):
        """Updates the supply of one firm, given previous profits"""
        prev_profit = self.get_from_history('profits', -2, 0) if len(self.history) > 1 else 0
        if prev_profit is None:
            pass
        elif self.profits > prev_profit and self.profits > 0:
            self.supply += 0.25
        elif self.profits < prev_profit or self.profits < 0:
            self.supply -= 0.25
        return {self.product: self.supply}

    def set_labor_demand(self):
        max_supply = self.workers * self.productivity
        if self.supply > max_supply:
            self.workers += 1
        # Firm fires if under 90% production capacity, as long as firing still leaves desired output possible
        # and at least 1 worker (no dying firm yet).
        elif self.THROUGHPUT_FLOOR * max_supply >= self.supply and self.workers > 1:
            self.workers -= 1
            if self.supply > self.workers * self.productivity:
                self.workers += 1

    def update_profits(self, sold, prices):
        """changes the firm's state using sales data"""
        costs = self.wages * self.workers
        revenues = sold[self.product] * prices[self.product]
        self.profits = revenues - costs


if __name__ == '__main__':
    f = Firm(workers=15, wages=1, productivity=1)
    print(f.set_supply())
    f.add_to_history()
    f.add_to_history()
    print(f.history)
    print(f)
