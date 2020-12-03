# It says hello
from goodsvector import GoodsVector
import random


class World:
    PRICE_INC = 0.0001
    EPS = 0.001
    PRICE_CHANGE_CEILING = 1.2
    PRICE_CHANGE_FLOOR = 0.8
    WAGE_RISE = 5
    WAGE_DECAY = 0.01
    UNEMP_MALUS = .95
    POACHED_BONUS = 1.05

    def __init__(self, goods, firms, pops, prices):
        # Core properties
        self.goods = set(goods)
        self.firms = {firm.id_firm: firm for firm in firms}
        self.pops = {pop.id_pop: pop for pop in pops}
        self.prices = prices

        # Check consistency between prices and goods
        if not (set(prices) <= goods):
            raise KeyError()

        # Computed aggregates
        self.tot_demand = {}
        self.tot_supply = {}
        self.tot_population = 0
        self.unemployment_rate = 0
        self.gdp = 0
        self.gdp_per_capita = 0
        self.price_level = None
        self.adjusted_gdp = 0
        self.initial_price_level = None
        self.indexed_price_level = None
        self.inflation = 0

        # Technical logistics
        self.history = []

    def add_to_history(self):
        for firm in self.firms.values():
            firm.add_to_history()
        for pop in self.pops.values():
            pop.add_to_history()
        self.history.append({'tot_demand': self.tot_demand,
                             'tot_supply': self.tot_supply,
                             'tot_population': self.tot_population,
                             'prices': self.prices,
                             'unemployment': self.unemployment_rate,
                             'gdp': self.gdp,
                             'gdp_per_capita': self.gdp_per_capita,
                             'price_level': self.price_level,
                             'indexed_price_level': self.indexed_price_level,
                             'inflation': self.inflation,
                             'adjusted_gdp': self.adjusted_gdp})

    def compute_tot_population(self):
        self.tot_population = sum(pop.population for pop in self.pops.values())

    def find_unemployment_rate(self):
        employed = 0
        for pop in self.pops.values():
            employed += sum(pop.employed.values())
        self.unemployment_rate = 1 - (employed / self.tot_population)

    def compute_gdp(self):
        self.gdp = sum(qty * self.prices[good] for good, qty in self.tot_demand.items())

    def compute_gdp_per_capita(self):
        self.gdp_per_capita = self.gdp / self.tot_population

    def compute_price_level(self):
        """Computes the price of basic necessities for the average
           person by taking the average of level 0 needs across
           the population and computes a price level from there"""
        previous_price_level = self.price_level
        survival_goods = {}
        for pop in self.pops.values():
            for good, level, qty in pop.needs:
                if level == 0:
                    if good in survival_goods:
                        survival_goods[good] += qty * pop.population
                    else:
                        survival_goods[good] = qty * pop.population
        self.price_level = sum(qty * self.prices[good] for good, qty in survival_goods.items()) / self.tot_population
        if self.initial_price_level is None:
            self.initial_price_level = self.price_level
        self.indexed_price_level = self.price_level / self.initial_price_level * 100
        if previous_price_level is not None:
            self.inflation = self.price_level / previous_price_level - 1

    def compute_adjusted_gdp(self):
        """To interpret as the number of average basic needs produced in terms of value"""
        self.adjusted_gdp = self.gdp / self.price_level

    def compute_aggregates(self):
        self.compute_tot_population()
        self.find_unemployment_rate()
        self.compute_gdp()
        self.compute_gdp_per_capita()
        self.compute_price_level()
        self.compute_adjusted_gdp()

    def price_of(self, firm_or_product):
        if firm_or_product in self.prices:
            return self.prices[firm_or_product]
        elif firm_or_product in self.firms:
            return self.prices[self.firms[firm_or_product].product]

    def wage_decay(self):
        for firm in self.firms.values():
            firm.wages *= (1 - self.WAGE_DECAY)

    def clear_goods_market(self):
        """Sets aggregate supply, demand, and finds equilibria
           on goods markets through an iterative process,
           with price floors and ceilings to limit changes."""

        def aggregate_supply():
            supply = GoodsVector(self.goods)
            for firm in self.firms.values():
                supply += {firm.product: firm.supply}
            return supply

        def aggregate_demand(prices):
            demand = GoodsVector(self.goods)
            for pop in self.pops.values():
                demand += pop.compute_demand(prices)
            return demand

        def set_demand(prices):
            for pop in self.pops.values():
                pop.buy_goods(prices)

        def compute_incomes():
            for pop in self.pops.values():
                pop.compute_income(self.firms)

        # Limit price changes in one tick to a range between PRICE_CHANGE_FLOOR and CEILING
        max_prices = {good: price * self.PRICE_CHANGE_CEILING for good, price in self.prices.items()}
        min_prices = {good: price * self.PRICE_CHANGE_FLOOR for good, price in self.prices.items()}

        # Compute the aggregated supply of goods over all the firms
        tot_supply = aggregate_supply()

        # Compute the aggregated demand over all the pops, given a set of prices and incomes
        compute_incomes()
        tot_demand = aggregate_demand(self.prices)

        # Main loop logic :
        #   Adjust iteratively goods' prices then adjust demand accordingly until all
        #   goods' demands and supplies are equal or until prices are at their limits

        loop = True
        while loop:
            loop = False
            for good in self.goods:
                # Because prices change by a discrete increment, mathematical equality cannot be reached
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

        set_demand(self.prices)
        self.tot_demand = tot_demand
        self.tot_supply = tot_supply

    def clear_labor_market_for(self, pop_level):
        """Adjust aggregated demand, supply and wages on labor market"""

        def set_labor_demand():
            """Returns a dictionary with the demand for each firms"""
            tot_lab_demand = {id_firm: 0 for id_firm in self.firms}
            for id_firm, firm in self.firms.items():
                tot_lab_demand[id_firm] += firm.set_labor_demand_for(pop_level, self.pops)
            return tot_lab_demand

        def randomise_demand(agg_demand):
            randomizer = [id_firm for id_firm in agg_demand.keys()]
            random.shuffle(randomizer)
            return {id_firm: agg_demand[id_firm] for id_firm in randomizer}

        def set_labor_supply():
            """Ideally returns a dictionary/class with the number of unemployed
               people of each type in a region. Atm, one unified type."""
            lab_supply = {id_pop: 0 for id_pop, pop in self.pops.items() if pop.pop_type == pop_level}
            for id_pop, pop in self.pops.items():
                if pop.pop_type == pop_level:
                    lab_supply[id_pop] += pop.unemployed()
            return lab_supply

        agg_lab_demand = randomise_demand(set_labor_demand())
        agg_lab_supply = set_labor_supply()

        for id_firm, lab_demand in agg_lab_demand.items():
            hiring_firm = self.firms[id_firm]
            while lab_demand > hiring_firm.workers[pop_level]:
                labor_pool = {id_f: firm.workers_for(pop_level) for id_f, firm in self.firms.items()
                              if firm.wages_of(pop_level) <= hiring_firm.wages_of(pop_level) and firm != hiring_firm}
                labor_pool['unemployed'] = sum(agg_lab_supply.values())

                # If labor pool empty, then fill with higher-wage firms up to a ceiling (30%?)
                if set(labor_pool.values()) == {0}:
                    labor_pool = {id_f: firm.workers_for(pop_level) for id_f, firm in self.firms.items()
                                  if firm.wages_of(pop_level) <= (hiring_firm.wages_of(pop_level) * 1.3)
                                  and firm != hiring_firm}
                    if set(labor_pool.values()) == {0}:
                        break

                # Randomly select someone in the labor pool
                [hired] = random.choices(list(labor_pool.keys()), weights=labor_pool.values(), k=1)

                if hired == 'unemployed':
                    # Randomly select the origin pop
                    [hired_pop] = random.choices(list(agg_lab_supply.keys()), weights=agg_lab_supply.values(), k=1)

                    # Then hire the right workers, and update wages
                    hiring_firm.adjust_workers_for(pop_level, +1)
                    self.pops[hired_pop].hired_by(id_firm, 1)
                    agg_lab_supply[hired_pop] -= 1
                    hiring_firm.wages[pop_level] = (hiring_firm.wages_of(pop_level) * (hiring_firm.workers[pop_level] - 1)
                                                    + hiring_firm.wages_of(pop_level) * self.UNEMP_MALUS) \
                                                   / hiring_firm.workers[pop_level]

                else:
                    poached_firm = self.firms[hired]
                    # Randomly select the origin pop inside the selected firm
                    employed = {id_pop: pop.employed_by(hired) for id_pop, pop in self.pops.items()
                                if pop.pop_type == pop_level}
                    [hired_pop] = random.choices(list(employed.keys()), weights=employed.values(), k=1)

                    # Poach the worker and update wages and pop data
                    hiring_firm.adjust_workers_for(pop_level, +1)
                    poached_firm.adjust_workers_for(pop_level, -1)
                    self.pops[hired_pop].poached_by_from(id_firm, hired, 1)
                    hiring_firm.wages[pop_level] = (hiring_firm.wages_of(pop_level) * (hiring_firm.workers[pop_level] - 1)
                                                    + hiring_firm.wages_of(pop_level) * self.POACHED_BONUS) \
                                                   / hiring_firm.workers[pop_level]

    def adjust_all_supply(self):
        for firm in self.firms.values():
            firm.adjust_supply()

    def set_goods_supply(self):
        for firm in self.firms.values():
            firm.set_supply()

    def update_firms_profits(self):
        for firm in self.firms.values():
            firm.update_profits(self.tot_demand, self.prices)

    def tick(self, t: int):
        # Compute useful aggregate(s)
        self.compute_aggregates()

        # Core mechanisms
#        self.wage_decay()
        self.set_goods_supply()
        self.clear_labor_market_for(0)
        self.clear_labor_market_for(1)
        self.adjust_all_supply()
        self.clear_goods_market()
        self.update_firms_profits()

        # Technical logistics
        self.add_to_history()

    def export(self):
        def flatten_dict(prefix, a_dict):
            return {f"{prefix}_{key}": value for key, value in a_dict.items()}

        full_table = []
        for i in range(0, len(self.history)):
            at_i = self.history[i]
            d = {'t': i, 'population': at_i['tot_population'], 'unemployment': at_i['unemployment'],
                 'gdp': at_i['gdp'], 'gdp_per_capita': at_i['gdp_per_capita'], 'price_level': at_i['price_level'],
                 'indexed_price_level': at_i['indexed_price_level'], 'inflation': at_i['inflation'],
                 'adjusted_gdp': at_i['adjusted_gdp']}
            d.update(flatten_dict('supply', at_i['tot_supply']))
            d.update(flatten_dict('demand', at_i['tot_demand']))

            for id_firm, firm in self.firms.items():
                firm_name = f"firm{id_firm}"
                for key in {'profits', 'product', 'supply', 'productivity'}:
                    d[f"{firm_name}_{key}"] = firm.get_from_history(key, i)
                for pop_level in range(2):
                    d[f"{firm_name}_workers_{pop_level}"] = firm.get_from_history('workers', i)[pop_level]
                    d[f"{firm_name}_wages_{pop_level}"] = firm.get_from_history('wages', i)[pop_level]

            for id_pop, pop in self.pops.items():
                pop_name = f"pop{id_pop}"
                for key in {'pop_type', 'population', 'income', 'savings', 'thrift'}:
                    d[f"{pop_name}_{key}"] = pop.get_from_history(key, i)
                d.update(flatten_dict(f"{pop_name}_demand", pop.get_from_history('demand', i)))

            full_table.append(d)

        return full_table

    def summary(self):
        for id_firm, firm in self.firms.items():
            p = []
            w = []
            wage = []
            s = []
            t = []
            for i in range(0, len(self.history)):
                p.append(round(firm.get_from_history("profits", i), 2))
                w.append(round(firm.get_from_history("workers", i)[0], 2))
                wage.append(round(firm.get_from_history("wages", i)[0], 2))
                s.append(round(firm.get_from_history("supply", i), 2))
                t.append((firm.get_from_history("workers", i), firm.get_from_history("supply", i),
                          round(firm.get_from_history("profits", i), 2)))
            print(f'Profits of {firm.product}: {p};'
                  f'total profits: {round(sum(p), 2)}')
            print(f'Supply of {firm.product}: {s};')
            print(f'Price of {firm.product}: {self.price_of(id_firm)};')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
            print(f'Wages of {firm.product}: {wage}')
            print(f'{t}')
            print(f'')

        for pop in self.pops.values():
            print(pop.employed)
            print(pop.income)

