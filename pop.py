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
        self.demand = GoodsVector(self.goods)
        self.employed = employed
        self.savings = savings
        self.thrift = thrift

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

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

    def compute_income(self, firms, dividends):
        income_from_work = sum(workers * firms[id_firm].wages_of(self.pop_type)
                               for id_firm, workers in self.employed.items())
        income_from_shares = dividends[self.id_pop]
        self.income = (income_from_work + income_from_shares) / self.population

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

    def buy_goods(self, prices):
        self.demand = GoodsVector(self.goods, self.compute_demand(prices))
        spendings = sum(prices[good] * qty for good, qty in self.demand.items())
        self.savings += self.income - spendings / self.population
        if self.savings < -0.01:
            print(self.savings)
            raise Exception("A pud'sous")


