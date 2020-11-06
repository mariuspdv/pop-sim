
class World:
    PRICE_INC = 0.0001
    EPS = 0.001

    def __init__(self, firms, pops, prices):
        self.prices = prices
        self.firms = firms
        self.pops = pops
        self.tot_demand = {}
        self.tot_supply = {}
        self.history = []

    def add_to_history(self):
        for firm in self.firms:
            firm.add_to_history()
        self.pops.add_to_history()
        self.history.append({'tot_demand': self.tot_demand, 'tot_supply': self.tot_supply})

    def clear_goods_market(self):
        goods = self.prices.keys()
        max_prices = {good: price * 1.2 for good, price in self.prices.items()}
        min_prices = {good: price * 0.8 for good, price in self.prices.items()}
        tot_supply = {good: 0 for good in goods}
        for firm in self.firms:
            firm.add_to_total_supply(tot_supply)
        tot_demand = self.pops.set_demand(self.prices)

        # sum(abs(tot_demand[good] - tot_supply[good]) for good in goods) >= EPS
        loop = True
        while loop:
            loop = False
            for good in goods:
                if abs(tot_demand[good] - tot_supply[good]) <= self.EPS:
                    continue
                if tot_demand[good] > tot_supply[good] and self.prices[good] < max_prices[good]:
                    self.prices[good] += self.PRICE_INC
                    loop = True
                elif tot_demand[good] < tot_supply[good] and self.prices[good] > min_prices[good]:
                    self.prices[good] -= self.PRICE_INC
                    loop = True
            #        print(prices)
            tot_demand = self.pops.set_demand(self.prices)

        self.tot_demand = tot_demand
        self.tot_supply = tot_supply
        print(f'Prices: {self.prices}')

    def clear_labor_market(self):
        for firm in self.firms:
            firm.update_firm(self.tot_demand, self.prices, self.pops)
            print(firm)

    def tick(self, t):
        self.clear_goods_market()
        self.clear_labor_market()
        self.add_to_history()

    def summary(self):
        for firm in self.firms:
            l = []
            w = []
            for i in range(0, len(self.history)):
                l.append(firm.get_from_history("profits", i))
                w.append(firm.get_from_history("workers", i))
            print(f'Profits of {firm.product}: {l};')
            print(f'total profits: {sum(l)}')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
