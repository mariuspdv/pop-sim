# What is this unruly mob? What are they doing here? They smell!
# Err... These are *your* people, majesty.
from historizor import Historizor
from goodsvector import GoodsVector


class Pop(Historizor):

    def __init__(self, id_pop, pop_type, goods, needs, population, employed, savings, thrift):
        super().__init__()
        self.id_pop = id_pop
        self.pop_type = pop_type
        self.goods = goods
        self.needs = needs
        self._levels = sorted(list(set(l for _, l, _ in needs)))
        self.population = population
        self.income = 0
        self.available_income = self.income
        self.demand = GoodsVector(self.goods)
        self.consumption = GoodsVector(self.goods)
        self.employed = employed
        self.savings = savings
        self.thrift = thrift
        self._world = None

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

    def set_world(self, world):
        self._world = world

    def unemployed(self):
        return self.population - sum(v for _, v in self.employed.items())

    def employed_by(self, id_firm):
        return self.employed[id_firm]

    def fired_by(self, id_firm, employees):
        self.employed[id_firm] -= employees

    def hired_by(self, id_firm, employees):
        self.employed[id_firm] += employees

    def poached_by_from(self, id_firm, poached_firm, employees):
        self.employed[id_firm] += employees
        self.employed[poached_firm] -= employees

    def set_income_from_salary_and_dividends(self, firms, dividends):
        income_from_work = sum(workers * firms[id_firm].wages_of(self.pop_type)
                               for id_firm, workers in self.employed.items())
        income_from_shares = dividends[self.id_pop]
        self.income = income_from_work + income_from_shares
        self.available_income = self.income

    def save(self):
        self.savings += self.income * self.thrift
        self.income *= (1 - self.thrift)

    def compute_demand(self, prices):
        """finds maximal demand within the bounds of income"""

        demand = GoodsVector(self.goods)
        income = self.income
        for level in self._levels:
            if level == 1:
                income *= (1 - self.thrift)
            value_level = sum(prices[good] * qty for good, l, qty in self.needs if l == level)
            if value_level <= income:
                demand += {good: qty for good, l, qty in self.needs if l == level}
                income -= value_level
                continue
            if level == 0:
                # Use savings
                need = value_level - income
                complement = min(self.savings, need)
                income += complement
            discount = income / value_level
            demand += {good: qty * discount for good, l, qty in self.needs if l == level}
            break
        return {good: qty * self.population for good, qty in demand.items()}

    def buy_good(self, good, level, qty, price):
        if self.income < (price * qty):
            if level == 0:
                if self.savings > ((price * qty) - self.income):
                    self.savings -= (price * qty) - self.income
                    self.income = 0
                    self.consumption[good] += qty
                    return 1
            discount = self.income / (price * qty)
            self.income = 0
            self.consumption[good] += qty * discount
            return discount

        self.income -= price * qty
        self.consumption[good] += qty
        return 1
