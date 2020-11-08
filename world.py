# It says hello
from markets import Markets


class World:
    PRICE_INC = 0.0001
    EPS = 0.001
    PRICE_CHANGE_CEILING = 1.2
    PRICE_CHANGE_FLOOR = 0.8

    def __init__(self, goods, firms, pops, prices):
        # Core properties
        self.goods = goods
        self.firms = firms
        self.pops = pops
        self.prices = prices

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
        self.history.append({'tot_demand': self.tot_demand, 'tot_supply': self.tot_supply})

    def compute_tot_population(self):
        self.tot_population = sum(pop.population for pop in self.pops)

    def clear_goods_market(self):
        """Adjust aggregated demand, supply and prices on good markets"""

        def aggregate_supply():
            supply = Markets(self.goods)
            for firm in self.firms:
                supply += firm.set_supply()
            return supply

        def aggregate_demand(prices):
            demand = Markets(self.goods)
            for pop in self.pops:
                demand += pop.set_demand(prices)
            return demand

        # Limit price changes in one tick to a band between PRICE_CHANGE_FLOOR and CEILING
        max_prices = {good: price * self.PRICE_CHANGE_CEILING for good, price in self.prices.items()}
        min_prices = {good: price * self.PRICE_CHANGE_FLOOR for good, price in self.prices.items()}

        # Compute the aggregated supply of goods over all the firms
        tot_supply = aggregate_supply()

        #
        # Adjust iteratively goods' prices to equilibrate goods demand and supply
        # within acceptable price movement

        # Compute the aggregated demand over all the pops, given a set of prices
        tot_demand = aggregate_demand(self.prices)
        loop = True
        while loop:
            # The loop will end when all goods market are at equilibrium (supply == demand)
            # or if the prices have stopped changing from iteration to another (which happens
            # when they have reached their floor or ceiling for the tick
            loop = False
            # Each market good is considered. We stop when all price adjustments have reached their finish condition
            for good in self.goods:
                # Because prices chang by a discrete increment, mathematical equality spply==demand can not be reached
                # We tolerate a difference of a small number EPS
                if abs(tot_demand[good] - tot_supply[good]) <= self.EPS:
                    # supply == demand : no need to change price change
                    continue
                if tot_demand[good] > tot_supply[good] and self.prices[good] < max_prices[good]:
                    # Adjust price if we are still in the acceptable rang
                    self.prices[good] += self.PRICE_INC
                    loop = True
                elif tot_demand[good] < tot_supply[good] and self.prices[good] > min_prices[good]:
                    # Adjust price if we are still in the acceptable rang
                    self.prices[good] -= self.PRICE_INC
                    loop = True
            # Compute the aggregated demand over all the pops, given the new set of prices
            tot_demand = aggregate_demand(self.prices)

        self.tot_demand = tot_demand
        self.tot_supply = tot_supply

    def clear_labor_market(self):
        """Adjust aggregated demand, supply and prices on labor market"""
        for firm in self.firms:
            firm.update_firm(self.tot_demand, self.prices, self)

    def tick(self, t: int):
        # Compute useful aggregate(s)
        self.compute_tot_population()

        # Core mechanism
        self.clear_goods_market()
        self.clear_labor_market()

        # Technical logistics
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
