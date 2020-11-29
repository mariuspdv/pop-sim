# Blue collar workers
from pop import Pop


class BlueCollar(Pop):
    THRIFT = 0.2

    def __init__(self, id_pop, goods, needs, population, employed, savings):
        super().__init__(id_pop, 0, goods, needs, population, employed, savings, self.THRIFT)

    def __str__(self):
        return f'Blue collar {self.id_pop}: the {self.population} of this town'
