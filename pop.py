# What is this unruly mob? What are they doing here? They smell!
# Err... These are *your* people, majesty.

class Pop:

    def __init__(self, needs, population, income):
        self.needs = needs
        self.population = population
        self.income = income
        self.history = []

    def __str__(self):
        return f'Hello, we are {self.population}'

    def add_to_history(self):
        self.history.append({'needs': self.needs,
                             'population': self.population,
                             'income': self.income})

    def get_from_history(self, thing, index, default=None):
        if len(self.history) == 0:
            return default
        return self.history[index][thing]

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
