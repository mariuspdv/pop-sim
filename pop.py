# What is this unruly mob? What are they doing here? They smell!
# Err... These are *your* people, majesty.
from historizor import Historizor


class Pop(Historizor):

    def __init__(self, needs, population, income):
        super().__init__()
        self.needs = needs
        self.population = population
        self.income = income
        self.add_to_history()

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

    def value_goods(self, goods, prices):
        return goods * prices

    def set_demand(self, prices):
        '''demande initiale calculée sans les salaires'''
        expense = self.value_goods(self.needs, prices)
        if self.income >= expense:
            demand = self.needs
        else:
            demand = self.income / prices
        return demand * self.population
