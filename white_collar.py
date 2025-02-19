# White collar workers
from pop import Pop


class WhiteCollar(Pop):
    THRIFT = 0.3
    INVEST_PROP = 0.05

    def __init__(self, id_pop, goods, needs, population, employed, savings):
        super().__init__(id_pop, 1, goods, needs, population, employed, savings, self.THRIFT, self.INVEST_PROP)

    def __str__(self):
        return f'{self.id_pop}: {self.population} white collar'
