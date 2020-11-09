# What is this unruly mob? What are they doing here? They smell!
# Err... These are *your* people, majesty.
from historizor import Historizor
from goodsvector import GoodsVector


class Pop(Historizor):

    def __init__(self, goods, needs, population, income):
        super().__init__()
        self.goods = goods
        self.needs = needs
        self._levels = sorted(list(set(l for _, l, _ in needs)))
        self.population = population
        self.income = income
        self.demand = GoodsVector(self.goods)
        self.add_to_history()

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

    def compute_demand(self, prices):
        """finds maximal demand within the bounds of income"""
        demand = {good: 0 for good in self.goods}
        income = self.income
        for level in self._levels:
            value_level = sum(prices[good] * qty for good, l, qty in self.needs if l == level)
            if value_level <= income:
                demand.update({good: qty for good, l, qty in self.needs if l == level})
                income -= value_level
                continue
            discount = income / value_level
            demand.update({good: qty * discount for good, l, qty in self.needs if l == level})
            break
        return {good: qty * self.population for good, qty in demand.items()}

    def set_demand(self, prices):
        self.demand = GoodsVector(self.goods, self.compute_demand(prices))
