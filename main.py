# This is the main loop
from firm import Firm
from pop import Pop

PRICE_INC = 0.0001
EPS = 0.001

firm_1 = Firm(workers=15, wages=1, productivity=1)
pop_1 = Pop(needs=0.8, population=20, income=1)
prev_prices = 0.95


def tick(t, firm, prices, pop):
    supply = firm.set_supply()
    tot_demand = pop.set_demand(prices)

    while abs(tot_demand - supply) >= EPS:
        if tot_demand > supply:
            prices += PRICE_INC
        else:
            prices -= PRICE_INC
#        print(prices)
        tot_demand = pop.set_demand(prices)

    print(f"prix: {prices}, quantité: {tot_demand}")

    firm.update_firm(tot_demand, prices, pop)
    firm.add_to_history()
    pop.add_to_history()
    print(firm, pop)
    return prices


prev_prices = tick(0, firm_1, prev_prices, pop_1)
prev_prices = tick(0, firm_1, prev_prices, pop_1)
prev_prices = tick(0, firm_1, prev_prices, pop_1)
prev_prices = tick(0, firm_1, prev_prices, pop_1)
