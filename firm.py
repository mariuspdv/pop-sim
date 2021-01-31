# Definition of a Firm
from historizor import Historizor
import random
import math
import blue_collar
import white_collar


class Firm(Historizor):

    SUPPLY_CHANGE = 0.05
    WHITE_RATIO = 0.15
    SAVINGS_RATE = 0.5
    POACHED_BONUS = 1.05
    INCREASE_CEILING = 1.3
    UNEMP_MALUS = .95

    def __init__(self, id_firm, product, blue_wages, white_wages, productivity, profits=0,
                 account=0, stock=0):
        super().__init__()
        self.id_firm = id_firm
        self.product = product
        self.workers = {0: 0, 1: 0}
        self.wages = {0: blue_wages, 1: white_wages}
        self.productivity = productivity
        self.supply_goal = 0
        self.lab_demand = {0: 0, 1: 0}

        #self.supply = 0
        self.revenue = 0
        self.sold = 0

        # Accounting
        self.profits = profits  # Shluld be called  'income' in accounting parlance
        self.account = account
        self.dividends = 0
        self.capital = 0
        self.stock = stock

        self._world = None
        self.target_margin = 0.20
        self.price = 0

    def __str__(self):
        return f'Employees: {self.workers}'

    def set_world(self, world):
        self._world = world

    def init_workers(self):
        for pop in self._world.get_pops().values():
            workers = pop.employed_by(self.id_firm)
            if type(pop) is blue_collar.BlueCollar:
                self.adjust_workers_for(0, workers)
            if type(pop) is white_collar.WhiteCollar:
                self.adjust_workers_for(1, workers)
        # Initialize price objective at Unit cost plus target margin
        self.price = (sum(self.wages[i] * self.workers[i] for i in range(2))) \
                     / (self.workers_for(0) * self.adjusted_productivity()) * (1 + self.target_margin)

    def workers_for(self, pop_level):
        return self.workers[pop_level]

    def adjust_workers_for(self, pop_level, delta):
        self.workers[pop_level] += delta

    def wages_of(self, pop_level):
        return self.wages[pop_level]

    def set_wages_of(self, pop_level, wage):
        self.wages[pop_level] = wage

    def get_price(self):
        return self.price

    def start_period(self):
        self.revenue = 0
        self.sold = 0

    def end_period(self):
        # Close accounting period
        self.capital += self.profits - self.dividends
        self.profits = 0

    def hire(self, pop_level, new_wage, delta=1):
        self.workers[pop_level] += delta
        average_wage = (self.wages_of(pop_level) * (self.workers[pop_level] - delta) + new_wage * delta) \
                       / self.workers[pop_level]
        self.set_wages_of(pop_level, average_wage)

    def set_target_supply_and_price(self):
        """ Firm chooses supply and price depending on its previous profits, stock and margin """
        #TODO: revoir cette fonction

        # just in case: prev_profit = self.get_from_history('profits', -2, 0) if len(self.history) > 1 else 0

        # Compute basic values, before hiring
        production = self.workers_for(0) * self.adjusted_productivity()
        anticipated_costs = sum(self.wages[i] * self.workers[i] for i in range(2))
        prev_profit = self.get_from_history('profits', -1, 0)
        # If sell-out and profits, increase production and, if prices too low, prices too
        if self.stock == 0 and prev_profit >= 0:
            self.supply_goal = production * (1 + self.SUPPLY_CHANGE)
            unit_cost = anticipated_costs / self.supply_goal if self.supply_goal != 0 else 0
            if self.price < (unit_cost * (1 + self.target_margin)):
                self.price *= 1.05
            return

        # If sell-out and losses, increase prices
        if self.stock == 0 and prev_profit < 0:
            unit_cost = anticipated_costs / production if self.supply_goal != 0 else 0
            self.supply_goal = production
            self.price = max(unit_cost, self.price * 1.10)
            return

        # If stock still there and profits, do nothing (but increase prices if need be) ???? Need to change
        if prev_profit >= 0:
            self.supply_goal = production
            unit_cost = anticipated_costs / self.supply_goal if self.supply_goal != 0 else 0
            if self.price < (unit_cost * (1 + self.target_margin)):
                self.price *= 1.05
            return

        # If losses and stock left, decrease supply and price if possible --> needs a rethink
        if prev_profit < 0:
            self.supply_goal = production * (1 - self.SUPPLY_CHANGE)
            unit_cost = anticipated_costs / self.supply_goal if self.supply_goal != 0 else 0
            self.price = max(unit_cost, self.price * 0.95)
            return

    def set_blue_labor_demand(self):
        productivity = self.adjusted_productivity()
        max_supply = self.workers_for(0) * productivity
        if self.supply_goal > max_supply:
            lab_demand = math.ceil(self.supply_goal / productivity)
        # Firm fires if under production capacity and no savings, as long as firing still leaves desired
        # output possible and at least 1 worker (no dying firm yet).
        elif self.supply_goal < max_supply and self.workers_for(0) > 1 and self.account <= 0:
            lab_demand = math.ceil(self.supply_goal / productivity)
        else:
            lab_demand = self.workers_for(0)
        self.lab_demand[0] = lab_demand

    def set_white_labor_demand(self):
        # TODO revoir cette fonction (pour éviter croissance des salaires abusive?)
        ideal_demand = self.workers[0] * (self.WHITE_RATIO / (1 - self.WHITE_RATIO))
        self.lab_demand[1] = int(ideal_demand)

    def set_labor_demand_for(self, pop_level):
        if pop_level == 0:
            return self.set_blue_labor_demand()
        return self.set_white_labor_demand()

    def get_labor_demand_for(self, pop_level):
        return self.lab_demand[pop_level]

    def fire_to_match_labor_demand_for(self, pop_level):
        pops = self._world.get_pops()
        while self.workers_for(pop_level) > self.lab_demand[pop_level]:
            # Fire a random worker from a POP
            workers = {id_pop: pop.employed_by(self.id_firm) for id_pop, pop in pops.items() if pop.pop_type == pop_level}
            [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
            pops[fired].fired_by(self.id_firm, 1)
            self.adjust_workers_for(pop_level, -1)

    def try_to_match_labor_demand(self, pop_level):
        # Each Firm will try to hire workers to match its target workforce
        # lab_demand represents the target headcount including the current employees
        labor_demand = self.get_labor_demand_for(pop_level)
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

    def adjusted_productivity(self):
        def productivity_boost(x):
            if x < self.WHITE_RATIO:
                return math.log(1 + 4 * x - 10 * x**2)
            return math.log(1 + 4 * self.WHITE_RATIO - 10 * self.WHITE_RATIO**2)

        white_workers = self.workers_for(1)
        ratio = white_workers / (white_workers + self.workers_for(0)) if white_workers != 0 else 0
        return (1 + productivity_boost(ratio)) * self.productivity

    def produce_goods(self):
        self.stock += self.workers_for(0) * self.adjusted_productivity()
        #return self.stock, self.price

    def has_stock(self):
        return self.stock > 0

    def raise_wages(self, rate, pop_level):
        self.wages[pop_level] *= (1 + (rate/100))

    def sell_goods(self, qty):
        amount = self.price * qty
        self.stock -= qty
        self.sold += qty
        self.revenue += amount

        # Accounting
        self.profits += amount
        self.account += amount

    def pay_salaries(self):
        salaries = {}
        for id_pop, (pop_level, workers) in self._world.get_workers_for(self.id_firm).items():
            salary = workers * self.wages_of(pop_level)
            # Accounting
            self.account -= salary
            self.profits -= salary
            salaries[id_pop] = salary
        return salaries

    def pay_dividends(self):
        dividends = self.dividends
        # Accounting
        self.dividends -= dividends
        self.account -= dividends
        return dividends

    def decide_dividend_to_distribute(self):
        """changes the firm's state using sales data"""
        #costs = sum(self.wages[i] * self.workers[i] for i in range(2))
        #self.profits = self.revenue - costs
        # If no debt and profits, then save some. If in debt or losses, all profits/losses in account.
        if self.profits > 0 and self.account >= 0:
            to_keep = self.SAVINGS_RATE * self.profits
            self.dividends = min(self.profits - to_keep, self.account)
        else:
            # self.account += self.profits
            self.dividends = 0
