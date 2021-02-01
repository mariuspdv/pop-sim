from firm import Firm
from pop import Pop
from blue_collar import BlueCollar
from white_collar import WhiteCollar
from capitalist import Capitalist
from world import World
from goodsvector import GoodsVector


def write_to_csv(file_name, data):
    import csv
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in data:
            writer.writerow(line)


def nice_print(data):
    keys = data[0].keys()
    print(",".join(keys))
    for line in data:
        def nicer(x):
            if type(x) is str:
                return x
            return f"{x:.3f}"
        print(",".join([nicer(line[k]) for k in keys]))


goods = {'food', 'lodging', 'clothes', 'luxury'}
firm_1 = Firm(id_firm=1, product='food', blue_wages=1.3, white_wages=1.65, productivity=3)
firm_2 = Firm(id_firm=2, product='lodging', blue_wages=1.21, white_wages=1.55, productivity=3)
firm_3 = Firm(id_firm=3, product='clothes', blue_wages=1.41, white_wages=1.52, productivity=2)
firm_4 = Firm(id_firm=4, product='luxury', blue_wages=1, white_wages=1.3, productivity=0.5)
firm_5 = Firm(id_firm=5, product='food', blue_wages=1.1, white_wages=1.69, productivity=3)
needs_1 = [('food', 0, 0.6), ('lodging', 0, 0.5), ('clothes', 0, 0.2),
           ('food', 1, 0.2), ('lodging', 1, 0.2), ('clothes', 1, 0.6), ('luxury', 1, 0.1),
           ('luxury', 2, 10)]
needs_2 = [('food', 0, 0.6), ('lodging', 0, 0.6), ('clothes', 0, 0.3),
           ('food', 1, 0.2), ('lodging', 1, 0.3), ('clothes', 1, 0.5), ('luxury', 1, 0.15),
           ('luxury', 2, 10)]
needs_3 = [('food', 0, 0.6), ('lodging', 0, 0.5), ('clothes', 0, 0.3),
           ('food', 1, 0.3), ('lodging', 1, 0.3), ('clothes', 1, 0.5), ('luxury', 1, 0.1),
           ('luxury', 2, 10)]
needs_4 = [('food', 0, 0.8), ('lodging', 0, 0.7), ('clothes', 0, 0.6), ('luxury', 0, 0.1),
           ('food', 1, 0.3), ('lodging', 1, 0.4), ('clothes', 1, 0.4), ('luxury', 1, 0.7),
           ('luxury', 2, 10)]
needs_5 = [('food', 0, 0.8), ('lodging', 0, 0.7), ('clothes', 0, 1), ('luxury', 0, 1),
           ('food', 1, 0.4), ('lodging', 1, 0.6), ('clothes', 1, 0.6), ('luxury', 1, 2),
           ('luxury', 2, 10)]
employ_1 = {1: 9, 2: 6, 3: 3, 4: 7, 5: 0}
employ_2 = {1: 0, 2: 3, 3: 7, 4: 0, 5: 2}
employ_3 = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0}
employ_4 = {1: 1, 2: 1, 3: 1, 4: 0, 5: 0}
f = 10
employ_1 = {k: f * v for k, v in employ_1.items()}
employ_2 = {k: f * v for k, v in employ_2.items()}
employ_3 = {k: f * v for k, v in employ_3.items()}
employ_4 = {k: f * v for k, v in employ_4.items()}

pop_1 = BlueCollar(id_pop=1, goods=goods, needs=needs_1, population=30 * f, employed=employ_1, savings=3)
pop_2 = BlueCollar(id_pop=2, goods=goods, needs=needs_2, population=12 *f, employed=employ_2, savings=1)
pop_3 = BlueCollar(id_pop=3, goods=goods, needs=needs_3, population=3 * f, employed=employ_3, savings=2)
pop_4 = WhiteCollar(id_pop=4, goods=goods, needs=needs_4, population=5 * f, employed=employ_4, savings=0)
pop_5 = Capitalist(id_pop=5, goods=goods, needs=needs_5, population=1, employed={}, savings=3)
firms = [firm_1, firm_2, firm_3, firm_4, firm_5]
initial_shares = {1: 0, 2: 0, 3: 0, 4: 0, 5: 10}

world = World(goods=goods,
              firms=firms,
              pops=[pop_1, pop_2, pop_3, pop_4, pop_5],
              depositary={id_firm: initial_shares for id_firm in range(1, len(firms) + 1)}
              )

for i in range(200):
    world.tick()

full_table = world.export()

write_to_csv('export_run.csv', full_table)
# nice_print(full_table)

cum_needs = GoodsVector(goods)
for pop in world.pops.values():
    cum_needs += pop.cumulated_needs({0, 1})

prod_capacity = GoodsVector(goods)
for firm in world.firms.values():
    bc = firm.workers_for(0)
    productivity = firm.adjusted_productivity()
    good = firm.product
    # print(firm.id_firm, bc, good, productivity, bc * productivity)
    prod_capacity[good] += bc * productivity

print('needs')
print(cum_needs)
print('production_capacity')
print(prod_capacity)

