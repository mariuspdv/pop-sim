# Blue collar workers
from pop import Pop


class BlueCollar(Pop):
    THRIFT = 0.2
    INVEST_PROP = 0.03

    def __init__(self, id_pop, goods, needs, population, employed, savings):
        super().__init__(id_pop, 0, goods, needs, population, employed, savings, self.THRIFT, self.INVEST_PROP)

    def __str__(self):
        return f'{self.id_pop}: {self.population} blue collar'
