# This is the main loop
from firm import Firm
from pop import Pop

PRICE_INC = 0.0001
EPS = 0.001

#1
needs = [('food', 0, 0.4), ('lodging', 0, 0.2), ('clothes', 1, 0.3), ('luxury', 2, 0.5)]

firm_1 = Firm(product='food', workers=14, wages=1, productivity=1)
firm_2 = Firm(product='lodging', workers=14, wages=1, productivity=1)
firm_3 = Firm(product='clothes', workers=3, wages=1, productivity=1)
firm_4 = Firm(product='luxury', workers=1, wages=1, productivity=1)
firms = [firm_1, firm_2, firm_3, firm_4]

pop_1 = Pop(needs=needs, population=20, income=1)
prev_prices = {'food': 0.95, 'lodging': 0.96, 'clothes': 1.2, 'luxury': 3}


def tick(t, firms, prices, pop):
    goods = prices.keys()
    tot_supply = {good: 0 for good in goods}
    for firm in firms:
        firm.add_to_total_supply(tot_supply)
    tot_demand = pop.set_demand(prices)

# sum(abs(tot_demand[good] - tot_supply[good]) for good in goods) >= EPS
    loop = True
    while loop:
        loop = False
        for good in goods:
            if abs(tot_demand[good] - tot_supply[good]) <= EPS:
                continue
            if tot_demand[good] > tot_supply[good] and prices[good] < 100:
                prices[good] += PRICE_INC
                loop = True
            elif tot_demand[good] < tot_supply[good] and prices[good] > 0.1:
                prices[good] -= PRICE_INC
                loop = True
#        print(prices)
        tot_demand = pop.set_demand(prices)

    print(f'Prices: {prices}')

    for firm in firms:
        firm.update_firm(tot_demand, prices, pop)
        firm.add_to_history()
    pop.add_to_history()
    print(firms, pop)
    return prices


prev_prices = tick(0, firms, prev_prices, pop_1)
prev_prices = tick(0, firms, prev_prices, pop_1)
prev_prices = tick(0, firms, prev_prices, pop_1)
prev_prices = tick(0, firms, prev_prices, pop_1)
