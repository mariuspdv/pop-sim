# This is the main loop
PRICE_INC = 0.0001
EPS = 0.001

firm = {'workers': 15, 'productivity': 1, 'profits': [], 'wages': 1.2}
pop = {'needs': 0.8, 'population': 20, 'income': 1}
prev_prices = 0.95


def set_supply(firms):
    '''offre totale à partir des firms'''
    return firms['workers'] * firms['productivity']


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


def update_firm(firms, sold, prices):
    '''changer l'état de la firme'''
    costs = firms['wages'] * firms['workers']
    revenues = sold * prices
    profit = revenues - costs
    firms['profits'].append(profit)


def tick(t, firm, prev_prices, pop):
    supply = set_supply(firm)
    prices = prev_prices
    tot_demand = set_demand(pop, prices)

    while abs(tot_demand - supply) >= EPS:
        if tot_demand > supply:
            prices += PRICE_INC
        else:
            prices -= PRICE_INC
        print(prices)
        tot_demand = set_demand(pop, prices)

    print(f"prix: {prices}, quantité: {tot_demand}")

    update_firm(firm, tot_demand, prices)
    print(firm)
    return prices


prev_prices = tick(0, firm, prev_prices, pop)
prev_prices = tick(0, firm, prev_prices, pop)
prev_prices = tick(0, firm, prev_prices, pop)
