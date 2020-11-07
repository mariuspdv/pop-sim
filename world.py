# It says hello

class World:
    PRICE_INC = 0.0001
    EPS = 0.001

    def __init__(self, goods, firms, pops, prices):
        self.goods = goods
        self.firms = firms
        self.pops = pops
        self.prices = prices

        self.tot_demand = {}
        self.tot_supply = {}
        self.tot_population = 0

        self.history = []

    def add_to_history(self):
        for firm in self.firms:
            firm.add_to_history()
        for pop in self.pops:
            pop.add_to_history()
        self.history.append({'tot_demand': self.tot_demand, 'tot_supply': self.tot_supply})

    def compute_tot_population(self):
        self.tot_population = sum(pop.population for pop in self.pops)

    def clear_goods_market(self):
        max_prices = {good: price * 1.2 for good, price in self.prices.items()}
        min_prices = {good: price * 0.8 for good, price in self.prices.items()}
        tot_supply = {good: 0 for good in self.goods}
        tot_demand = {good: 0 for good in self.goods}
        for firm in self.firms:
            firm.add_to_total_supply(tot_supply)
        for pop in self.pops:
            pop.add_to_total_demand(tot_demand, pop.set_demand(self.prices))

        # sum(abs(tot_demand[good] - tot_supply[good]) for good in goods) >= EPS
        loop = True
        while loop:
            loop = False
            for good in self.goods:
                if abs(tot_demand[good] - tot_supply[good]) <= self.EPS:
                    continue
                if tot_demand[good] > tot_supply[good] and self.prices[good] < max_prices[good]:
                    self.prices[good] += self.PRICE_INC
                    loop = True
                elif tot_demand[good] < tot_supply[good] and self.prices[good] > min_prices[good]:
                    self.prices[good] -= self.PRICE_INC
                    loop = True
            #        print(prices)
            tot_demand = {good: 0 for good in self.goods}
            for pop in self.pops:
                pop.add_to_total_demand(tot_demand, pop.set_demand(self.prices))

        self.tot_demand = tot_demand
        self.tot_supply = tot_supply

    def clear_labor_market(self):
        for firm in self.firms:
            firm.update_firm(self.tot_demand, self.prices, self)

    def tick(self, t):
        self.compute_tot_population()
        self.clear_goods_market()
        self.clear_labor_market()
        self.add_to_history()

    def summary(self):
        for firm in self.firms:
            l = []
            w = []
            for i in range(0, len(self.history)):
                l.append(round(firm.get_from_history("profits", i), 2))
                w.append(round(firm.get_from_history("workers", i), 2))
            print(f'Profits of {firm.product}: {l};')
            print(f'total profits: {round(sum(l), 2)}')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
