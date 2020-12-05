# Definition of a Firm
from historizor import Historizor
import random
import math


class Firm(Historizor):

    THROUGHPUT_FLOOR = 0.9
    WAGE_HIKE = 1.15
    WAGE_LOSS = 0.01
    SUPPLY_CHANGE = 0.05
    WHITE_RATIO = 0.15
    SAVINGS_RATE = 0.5
    POACHED_BONUS = 1.05
    INCREASE_CEILING = 1.3
    UNEMP_MALUS = .95

    def __init__(self, id_firm, product, blue_workers, white_workers, blue_wages, white_wages, productivity, profits=0,
                 account=0):
        super().__init__()
        self.id_firm = id_firm
        self.product = product
        self.workers = {0: blue_workers, 1: white_workers}
        self.wages = {0: blue_wages, 1: white_wages}
        self.productivity = productivity
        self.supply_goal = blue_workers * productivity
        self.supply = 0
        self.profits = profits
        self.account = account
        self.dividends = 0
        self._world = None

    def __str__(self):
        return f'Employees: {self.workers}'

    def set_world(self, world):
        self._world = world

    def workers_for(self, pop_level):
        return self.workers[pop_level]

    def adjust_workers_for(self, pop_level, delta):
        self.workers[pop_level] += delta

    def wages_of(self, pop_level):
        return self.wages[pop_level]

    def set_wages_of(self, pop_level, wage):
        self.wages[pop_level] = wage

    def hire(self, pop_level, new_wage, delta=1):
        self.workers[pop_level] += delta
        average_wage = (self.wages_of(pop_level) * (self.workers[pop_level] - delta) + new_wage * delta) \
                       / self.workers[pop_level]
        self.set_wages_of(pop_level, average_wage)

    def set_supply(self):
        """Updates the supply of one firm, given previous profits"""
        prev_profit = self.get_from_history('profits', -2, 0) if len(self.history) > 1 else 0
        if self.profits > prev_profit and self.profits > 0:
            self.supply_goal *= (1 + self.SUPPLY_CHANGE)
        elif self.profits < prev_profit or self.profits < 0:
            self.supply_goal *= (1 - self.SUPPLY_CHANGE)
        return {self.product: self.supply_goal}

    def set_blue_labor_demand(self, pops):
        max_supply = self.workers[0] * self.productivity
        lab_demand = self.workers[0]
        if self.supply_goal > max_supply:
            lab_demand = math.ceil(self.supply_goal / self.productivity)
        # Firm fires if under 90% production capacity and no savings, as long as firing still leaves desired
        # output possible and at least 1 worker (no dying firm yet).
        elif self.supply_goal <= self.THROUGHPUT_FLOOR * max_supply and self.workers[0] > 1 and self.account <= 0:
            lab_demand -= 1
            if self.supply_goal > lab_demand * self.productivity:
                lab_demand = self.workers[0]

        while lab_demand < self.workers[0]:
            # Fire a random worker from a POP
            workers = {id_pop: pop.employed_by(self.id_firm) for id_pop, pop in pops.items() if pop.pop_type == 0}
            [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
            pops[fired].fired_by(self.id_firm, 1)
            self.workers[0] -= 1

        return lab_demand

    def set_white_labor_demand(self, pops):
        ideal_demand = self.workers[0] * (self.WHITE_RATIO / (1 - self.WHITE_RATIO))
        while ideal_demand < self.workers[1]:
            # Fire a random worker from a POP
            workers = {id_pop: pop.employed_by(self.id_firm) for id_pop, pop in pops.items() if pop.pop_type == 1}
            [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
            pops[fired].fired_by(self.id_firm, 1)
            self.workers[1] -= 1

        return int(ideal_demand)

    def set_labor_demand_for(self, pop_level):
        pops = self._world.get_pops()
        if pop_level == 0:
            return self.set_blue_labor_demand(pops)
        return self.set_white_labor_demand(pops)

    def try_to_match_labor_demand(self, pop_level, labor_demand):
        # Each Firm will try to hire workers to match its target workforce
        # lab_demand represents the target headcount including the current employees

        # Hire one by one until target is reached
        if labor_demand <= self.workers_for(pop_level):
            return "give_up", None
        # a Firm will try first to poach firms that pay less or to hire unemployed workers
        labor_pool = self._world.labor_pool_for(self.id_firm, pop_level, self.wages_of(pop_level))

        if len(labor_pool) == 0:
            # If labor pool empty, then fill with higher-wage firms up to a ceiling
            labor_pool = self._world.labor_pool_for(self.id_firm, pop_level, self.wages_of(pop_level) * self.INCREASE_CEILING)
            if len(labor_pool) == 0:
                # Wages are too expensive : the firm gives up and will not reach its recruitment target
                return "give_up", None

        # Randomly select someone in the labor pool
        [id_firm_to_poach] = random.choices(list(labor_pool.keys()), weights=labor_pool.values(), k=1)

        if id_firm_to_poach == 'unemployed':
            # Hire at the firm's current wage less a malus
            return 'hire_unemployed', self.wages_of(pop_level) * self.UNEMP_MALUS
        # Poach the worker by offering a bonus to his/her current salary
        return "poach", (id_firm_to_poach, self.POACHED_BONUS)

    def max_wage(self, employees, price, pop_level):
        def revenue():
            if pop_level == 0:
                return min(self.supply_goal, employees * self.productivity) * self.productivity_for(self.workers[1]) * price
            elif pop_level == 1:
                return min(self.supply_goal, self.workers[0] * self.productivity) * self.productivity_for(employees) * price

        def costs():
            cost = 0
            for i in range(2):
                if i == pop_level:
                    cost += (employees - 1) * self.wages[pop_level]
                else:
                    cost += self.workers[i] * self.wages[i]
            return cost

        if self.profits < 0:
            return self.wages[pop_level]
        else:
            wage_cap = revenue() - costs() - self.profits
            return min(self.wages[pop_level] * self.WAGE_HIKE, wage_cap)

    def productivity_for(self, white_workers):
        ratio = white_workers / (white_workers + self.workers[0]) if white_workers != 0 else 0

        def productivity_boost(x):
            if x < self.WHITE_RATIO:
                return math.log(1 + 4 * x - 10 * x**2)
            else:
                return math.log(1 + 4 * self.WHITE_RATIO - 10 * self.WHITE_RATIO**2)

        return 1 + productivity_boost(ratio)

    def wage_turnover(self):
        for id_wage in self.wages:
            self.wages[id_wage] *= (1 - self.WAGE_LOSS)

    def adjust_supply(self):
        # Capping supply
        self.supply_goal = max(min(self.supply_goal, (self.workers[0] * self.productivity)), 0)
        # Adjusting to productivity
        self.supply = self.supply_goal * self.productivity_for(self.workers[1])

    def raise_wages(self, rate, pop_level):
        self.wages[pop_level] *= (1 + (rate/100))

    def update_profits(self, sold, prices):
        """changes the firm's state using sales data"""
        costs = sum(self.wages[i] * self.workers[i] for i in range(2))
        revenues = sold[self.product] * prices[self.product]
        self.profits = revenues - costs
        # If no debt and profits, then save some. If in debt or losses, all profits/losses in account.
        self.dividends = 0
        if self.profits > 0 and self.account >= 0:
            to_keep = self.SAVINGS_RATE * self.profits
            to_distribute = self.profits - to_keep
            self.account += to_keep
            self.dividends += to_distribute
        else:
            self.account += self.profits
