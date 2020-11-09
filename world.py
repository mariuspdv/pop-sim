# It says hello
from goodsvector import GoodsVector


class World:
    PRICE_INC = 0.0001
    EPS = 0.001
    PRICE_CHANGE_CEILING = 1.2
    PRICE_CHANGE_FLOOR = 0.8

    def __init__(self, goods, firms, pops, prices):
        # Core properties
        self.goods = set(goods)
        self.firms = firms
        self.pops = pops
        self.prices = prices

        # Check consistency between prices and goods
        if not (set(prices) <= goods):
            raise KeyError()

        # Computed aggregates
        self.tot_demand = {}
        self.tot_supply = {}
        self.tot_population = 0

        # Technical logistics
        self.history = []

    def add_to_history(self):
        for firm in self.firms:
            firm.add_to_history()
        for pop in self.pops:
            pop.add_to_history()
        self.history.append({'tot_demand': self.tot_demand, 'tot_supply': self.tot_supply,
                             'prices': self.prices})

    def compute_tot_population(self):
        self.tot_population = sum(pop.population for pop in self.pops)

    def clear_goods_market(self):
        """Sets aggregate supply, demand, and finds equilibria
           on goods markets through an iterative process,
           with price floors and ceilings to limit changes."""

        def aggregate_supply():
            supply = GoodsVector(self.goods)
            for firm in self.firms:
                supply[firm.product] += firm.supply
            return supply

        def aggregate_demand(prices):
            demand = GoodsVector(self.goods)
            for pop in self.pops:
                demand += pop.set_demand(prices)
            return demand

        # Limit price changes in one tick to a range between PRICE_CHANGE_FLOOR and CEILING
        max_prices = {good: price * self.PRICE_CHANGE_CEILING for good, price in self.prices.items()}
        min_prices = {good: price * self.PRICE_CHANGE_FLOOR for good, price in self.prices.items()}

        # Compute the aggregated supply of goods over all the firms
        tot_supply = aggregate_supply()

        # Compute the aggregated demand over all the pops, given a set of prices
        tot_demand = aggregate_demand(self.prices)

        # Main loop logic :
        #   Adjust iteratively goods' prices then adjust demand accordingly until all
        #   goods' demands and supplies are equal or until prices are at their limits

        loop = True
        while loop:
            loop = False
            for good in self.goods:
                # Because prices chang by a discrete increment, mathematical equality cannot be reached
                # We tolerate a difference of a small number EPS
                if abs(tot_demand[good] - tot_supply[good]) <= self.EPS:
                    continue
                if tot_demand[good] > tot_supply[good] and self.prices[good] < max_prices[good]:
                    self.prices[good] += self.PRICE_INC
                    loop = True
                elif tot_demand[good] < tot_supply[good] and self.prices[good] > min_prices[good]:
                    self.prices[good] -= self.PRICE_INC
                    loop = True

            # Adjust the new demand given the new set of prices, over all the pops
            tot_demand = aggregate_demand(self.prices)

        self.tot_demand = tot_demand
        self.tot_supply = tot_supply

    def clear_labor_market(self):
        """Adjust aggregated demand, supply and prices on labor market"""
        for firm in self.firms:
            firm.set_labor_demand()

    def tick(self, t: int):
        # Compute useful aggregate(s)
        self.compute_tot_population()

        # Core mechanisms
        for firm in self.firms:
            firm.set_supply()
        self.clear_labor_market()
        self.clear_goods_market()
        for firm in self.firms:
            firm.update_profits(self.tot_demand, self.prices)

        # Technical logistics
        self.add_to_history()

    def summary(self):
        for firm in self.firms:
            l = []
            w = []
            s = []
            t = []
            for i in range(0, len(self.history)):
                l.append(round(firm.get_from_history("profits", i), 2))
                w.append(round(firm.get_from_history("workers", i), 2))
                s.append(round(firm.get_from_history("supply", i), 2))
                t.append((firm.get_from_history("workers", i), firm.get_from_history("supply", i),
                          round(firm.get_from_history("profits", i), 2)))
            print(f'Profits of {firm.product}: {l}; total profits: {round(sum(l), 2)}')
            print(f'Supply of {firm.product}: {s};')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
            print(f'{t}')
            print(f'')
