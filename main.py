from firm import Firm
from pop import Pop
from world import World

goods = {'food', 'lodging', 'clothes', 'luxury'}
firm_1 = Firm(id_firm=1, product='food', workers=9, wages=1, productivity=1)
firm_2 = Firm(id_firm=2, product='lodging', workers=7, wages=1, productivity=1)
firm_3 = Firm(id_firm=3, product='clothes', workers=4, wages=1, productivity=1)
firm_4 = Firm(id_firm=4, product='luxury', workers=3, wages=1, productivity=1)
needs_1 = [('food', 0, 0.4), ('lodging', 0, 0.2), ('clothes', 1, 0.3), ('luxury', 2, 0.5)]
needs_2 = [('food', 0, 0.4), ('lodging', 0, 0.3), ('clothes', 1, 0.4), ('luxury', 2, 1)]
needs_3 = [('food', 0, 0.4), ('lodging', 0, 0.4), ('clothes', 0, 0.6), ('luxury', 1, 5)]
employ_1 = {1: 9, 2: 4, 3: 1, 4: 2}
employ_2 = {1: 0, 2: 3, 3: 3, 4: 0}
employ_3 = {1: 0, 2: 0, 3: 0, 4: 1}
pop_1 = Pop(id_pop=1, goods=goods, needs=needs_1, population=20, income=1, employed=employ_1)
pop_2 = Pop(id_pop=2, goods=goods, needs=needs_2, population=6, income=2, employed=employ_2)
pop_3 = Pop(id_pop=3, goods=goods, needs=needs_3, population=1, income=6, employed=employ_3)

world = World(goods=goods,
              firms=[firm_1, firm_2, firm_3, firm_4],
              prices={'food': 0.95, 'lodging': 0.96, 'clothes': 1.2, 'luxury': 3},
              pops=[pop_1, pop_2, pop_3]
              )


for i in range(12):
    world.tick(i)

world.summary()
