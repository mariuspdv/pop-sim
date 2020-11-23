# Definition of a Firm
from historizor import Historizor
import random
import math


class Firm(Historizor):

    THROUGHPUT_FLOOR = 0.9
    WAGE_HIKE = 1.15
    WAGE_LOSS = 0.01
    SUPPLY_CHANGE = 0.05

    def __init__(self, id_firm, product, blue_workers, white_workers, blue_wages, white_wages, productivity, profits=0):
        super().__init__()
        self.id_firm = id_firm
        self.product = product
        self.workers = {0: blue_workers, 1: white_workers}
        self.wages = {0: blue_wages, 1: white_wages}
        self.productivity = productivity
        self.supply = blue_workers * productivity
        self.profits = profits

    def __str__(self):
        return f'Employees: {self.workers}'

    def workers_for(self, pop_level):
        return self.workers[pop_level]

    def adjust_workers_for(self, pop_level, delta):
        self.workers[pop_level] += delta

    def wages_for(self, pop_level):
        return self.wages[pop_level]

    def set_supply(self):
        """Updates the supply of one firm, given previous profits"""
        prev_profit = self.get_from_history('profits', -2, 0) if len(self.history) > 1 else 0
        if self.profits > prev_profit and self.profits > 0:
            self.supply *= (1 + self.SUPPLY_CHANGE)
        elif self.profits < prev_profit or self.profits < 0:
            self.supply *= (1 - self.SUPPLY_CHANGE)
        return {self.product: self.supply}

    def set_blue_labor_demand(self, pops):
        max_supply = self.workers[0] * self.productivity
        lab_demand = self.workers[0]
        if self.supply > max_supply:
            lab_demand = math.ceil(self.supply / self.productivity)
        # Firm fires if under 90% production capacity, as long as firing still leaves desired output possible
        # and at least 1 worker (no dying firm yet).
        elif self.supply <= self.THROUGHPUT_FLOOR * max_supply and self.workers[0] > 1:
            lab_demand -= 1
            if self.supply > lab_demand * self.productivity:
                lab_demand = self.workers[0]

        while lab_demand < self.workers[0]:
            # Fire a random worker from a POP
                workers = {id_pop: pop.employed_by(self.id_firm) for id_pop, pop in pops.items() if pop.pop_type == 0}
                [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
                pops[fired].fired_by(self.id_firm, 1)
                self.workers[0] -= 1

        return lab_demand

    def set_white_labor_demand(self, pops):
        # TODO : add firm behavior for white collars
        return 0

    def set_labor_demand_for(self, pop_level, pops):
        if pop_level == 0:
            return self.set_blue_labor_demand(pops)
        return self.set_white_labor_demand(pops)

    def max_wage(self, employees, price, pop_level):
        if self.profits < 0:
            return self.wages[pop_level]
        else:
            wage_cap = (min(self.supply, employees * self.productivity) * price) \
                       - ((employees - 1) * self.wages[pop_level]) - max(self.profits, 0)
            return min(self.wages[pop_level] * self.WAGE_HIKE, wage_cap)

    def wage_turnover(self):
        for id_wage in self.wages:
            self.wages[id_wage] *= (1 - self.WAGE_LOSS)

    def cap_supply(self):
        self.supply = max(min(self.supply, (self.workers[0] * self.productivity)), 0)

    def raise_wages(self, rate, pop_level):
        self.wages[pop_level] *= (1 + (rate/100))

    def update_profits(self, sold, prices):
        """changes the firm's state using sales data"""
        costs = sum(self.wages[i] * self.workers[i] for i in range(2))
        revenues = sold[self.product] * prices[self.product]
        self.profits = revenues - costs
