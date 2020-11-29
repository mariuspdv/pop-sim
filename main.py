from firm import Firm
from pop import Pop
from blue_collar import BlueCollar
from white_collar import WhiteCollar
from world import World

goods = {'food', 'lodging', 'clothes', 'luxury'}
firm_1 = Firm(id_firm=1, product='food', blue_workers=19, white_workers=0, blue_wages=1, white_wages=1, productivity=2)
firm_2 = Firm(id_firm=2, product='lodging', blue_workers=15, white_workers=0, blue_wages=1, white_wages=1, productivity=2)
firm_3 = Firm(id_firm=3, product='clothes', blue_workers=10, white_workers=0, blue_wages=1, white_wages=1, productivity=1.5)
firm_4 = Firm(id_firm=4, product='luxury', blue_workers=3, white_workers=0, blue_wages=1, white_wages=1, productivity=1)
needs_1 = [('food', 0, 0.6), ('lodging', 0, 0.5), ('clothes', 1, 0.3), ('luxury', 2, 0.6)]
needs_2 = [('food', 0, 0.6), ('lodging', 0, 0.6), ('clothes', 1, 0.4), ('luxury', 2, 2)]
needs_3 = [('food', 0, 0.6), ('lodging', 0, 0.7), ('clothes', 0, 0.6), ('luxury', 1, 5)]
needs_4 = [('food', 0, 0.9), ('lodging', 0, 0.9), ('clothes', 0, 0.9), ('luxury', 1, 10)]
employ_1 = {1: 18, 2: 8, 3: 2, 4: 2}
employ_2 = {1: 0, 2: 6, 3: 4, 4: 0}
employ_3 = {1: 1, 2: 1, 3: 0, 4: 1}
employ_4 = {1: 0, 2: 0, 3: 0, 4: 0}
pop_1 = BlueCollar(id_pop=1, goods=goods, needs=needs_1, population=30, employed=employ_1, savings=3)
pop_2 = BlueCollar(id_pop=2, goods=goods, needs=needs_2, population=10, employed=employ_2, savings=1)
pop_3 = BlueCollar(id_pop=3, goods=goods, needs=needs_3, population=3, employed=employ_3, savings=2)
pop_4 = WhiteCollar(id_pop=4, goods=goods, needs=needs_3, population=3, employed=employ_4, savings=0)

world = World(goods=goods,
              firms=[firm_1, firm_2, firm_3, firm_4],
              prices={'food': 0.95, 'lodging': 0.96, 'clothes': 1.2, 'luxury': 3},
              pops=[pop_1, pop_2, pop_3]
              )


for i in range(30):
    world.tick(i)

world.summary()
