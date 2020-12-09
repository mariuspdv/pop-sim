# Self-employed workers
from pop import Pop


class SelfEmployed(Pop):

    def __init__(self, id_pop, goods, needs, population, employed):
        super().__init__(id_pop, -1, goods, needs, population, employed)

    def __str__(self):
        return f'{self.id_pop}: {self.population} self employed'