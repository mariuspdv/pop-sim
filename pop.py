# What is this unruly mob? What are they doing here? They smell!
# Err... These are *your* people, majesty.
from historizor import Historizor

# needs = [('food', 0, 0.4), ('lodging', 0, 0.2), ('clothes', 1, 0.3), ('luxury', 2, 0.5)]
class Pop(Historizor):

    def __init__(self, needs, population, income):
        super().__init__()
        self.needs = needs
        self._levels = sorted(list(set(l for _, l, _ in needs)))
        self.population = population
        self.income = income
        self.add_to_history()

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

    def value_goods(self, goods, prices):
        return goods * prices

    def set_demand(self, prices):
        '''demande initiale calculée sans les salaires'''
        demand = {}
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
