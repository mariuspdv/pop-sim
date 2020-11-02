# This is the main loop
from firm import Firm

PRICE_INC = 0.0001
EPS = 0.001

firm_1 = Firm(workers=15, wages=1, productivity=1)
pop = {'needs': 0.8, 'population': 20, 'income': 1}
prev_prices = 0.95


def value_goods(goods, prices):
    return goods * prices


def set_demand(pops, prices):
    '''demande initiale calculée sans les salaires'''
    income = pops['income']
    expense = value_goods(pops['needs'], prices)
    if income >= expense:
        demand = pops['needs']
    else:
        demand = income/prices
    return demand * pops['population']


def tick(t, firm, prices, pop):
    supply = firm.set_supply()
    tot_demand = set_demand(pop, prices)

    while abs(tot_demand - supply) >= EPS:
        if tot_demand > supply:
            prices += PRICE_INC
        else:
            prices -= PRICE_INC
#        print(prices)
        tot_demand = set_demand(pop, prices)

    print(f"prix: {prices}, quantité: {tot_demand}")

    firm.update_firm(tot_demand, prices, pop)
    firm.add_to_history()
    print(firm)
    return prices


prev_prices = tick(0, firm_1, prev_prices, pop)
prev_prices = tick(0, firm_1, prev_prices, pop)
prev_prices = tick(0, firm_1, prev_prices, pop)
prev_prices = tick(0, firm_1, prev_prices, pop)
