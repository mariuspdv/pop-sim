# Self-employed workers
from pop import Pop


class SelfEmployed(Pop):

    def __init__(self, id_pop, goods, needs, population, employed):
        super().__init__(id_pop, -1, goods, needs, population, employed)

    def __str__(self):
        return f'Self employed {self.id_pop}: the {self.population} of this town'