# Blue collar workers
from pop import Pop


class BlueCollar(Pop):

    def __init__(self, id_pop, goods, needs, population, employed):
        super().__init__(id_pop, 0, goods, needs, population, employed)

    def __str__(self):
        return f'Blue collar {self.id_pop}: the {self.population} of this town'
