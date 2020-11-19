# Definition of a Firm
from historizor import Historizor
import random
import math


class Firm(Historizor):

    THROUGHPUT_FLOOR = 0.9
    WAGE_HIKE = 1.15
    WAGE_LOSS = 0.01
    SUPPLY_CHANGE = 0.05

    def __init__(self, id_firm, product, workers, wages, productivity, profits=0):
        super().__init__()
        self.id_firm = id_firm
        self.product = product
        self.workers = workers
        self.wages = wages
        self.productivity = productivity
        self.supply = workers * productivity
        self.profits = profits

    def __str__(self):
        return f'Employees: {self.workers}'

    def set_supply(self):
        """Updates the supply of one firm, given previous profits"""
        prev_profit = self.get_from_history('profits', -2, 0) if len(self.history) > 1 else 0
        if self.profits > prev_profit and self.profits > 0:
            self.supply *= (1 + self.SUPPLY_CHANGE)
        elif self.profits < prev_profit or self.profits < 0:
            self.supply *= (1 - self.SUPPLY_CHANGE)
        return {self.product: self.supply}

    def set_labor_demand(self, pops):
        max_supply = self.workers * self.productivity
        lab_demand = self.workers
        if self.supply > max_supply:
            lab_demand = math.ceil(self.supply / self.productivity)
        # Firm fires if under 90% production capacity, as long as firing still leaves desired output possible
        # and at least 1 worker (no dying firm yet).
        elif self.supply <= self.THROUGHPUT_FLOOR * max_supply and self.workers > 1:
            lab_demand -= 1
            if self.supply > lab_demand * self.productivity:
                lab_demand = self.workers

        while lab_demand < self.workers:
            # Fire a random worker from a POP
                workers = {id_pop: pop.employed_by(self.id_firm) for id_pop, pop in pops.items()}
                [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
                pops[fired].fired_by(self.id_firm, 1)
                self.workers -= 1

        return lab_demand

    def max_wage(self, employees, price):

        if self.profits < 0:
            return self.wages
        else:
            wage_cap = (min(self.supply, employees * self.productivity) * price) - ((employees - 1) * self.wages) \
                       - max(self.profits, 0)
            return min(self.wages * self.WAGE_HIKE, wage_cap)

    def wage_turnover(self):
        self.wages = self.wages * (1 - self.WAGE_LOSS)

    def cap_supply(self):
        self.supply = max(min(self.supply, (self.workers * self.productivity)), 0)

    def raise_wages(self, rate):
        self.wages = (1 + (rate/100)) * self.wages

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
