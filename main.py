from firm import Firm
from pop import Pop
from world import World

needs = [('food', 0, 0.4), ('lodging', 0, 0.2), ('clothes', 1, 0.3), ('luxury', 2, 0.5)]
firm_1 = Firm(product='food', workers=9, wages=1, productivity=1)
firm_2 = Firm(product='lodging', workers=7, wages=1, productivity=1)
firm_3 = Firm(product='clothes', workers=4, wages=1, productivity=1)
firm_4 = Firm(product='luxury', workers=3, wages=1, productivity=1)

world = World(firms=[firm_1, firm_2, firm_3, firm_4],
              prices={'food': 0.95, 'lodging': 0.96, 'clothes': 1.2, 'luxury': 3},
              pops=Pop(needs=needs, population=20, income=1)
              )

for i in range(10):
    world.tick(i)

world.summary()

