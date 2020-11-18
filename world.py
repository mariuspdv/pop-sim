# It says hello
from goodsvector import GoodsVector
import random


class World:
    PRICE_INC = 0.0001
    EPS = 0.001
    PRICE_CHANGE_CEILING = 1.2
    PRICE_CHANGE_FLOOR = 0.8
    WAGE_RISE = 5

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

        # Technical logistics
        self.history = []

    def add_to_history(self):
        for firm in self.firms.values():
            firm.add_to_history()
        for pop in self.pops.values():
            pop.add_to_history()
        self.history.append({'tot_demand': self.tot_demand, 'tot_supply': self.tot_supply,
                             'prices': self.prices})

    def compute_tot_population(self):
        self.tot_population = sum(pop.population for pop in self.pops.values())

    def price_of(self, firm_or_product):
        if firm_or_product in self.prices:
            return self.prices[firm_or_product]
        elif firm_or_product in self.firms:
            return self.prices[self.firms[firm_or_product].product]

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
                pop.set_demand(prices)

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

    def clear_labor_market(self):
        """Adjust aggregated demand, supply and wages on labor market"""

        def set_labor_demand():
            """Returns a dictionary with the demand for each firms"""
            tot_lab_demand = {id_firm: 0 for id_firm in self.firms}
            for id_firm, firm in self.firms.items():
                tot_lab_demand[id_firm] += firm.set_labor_demand(self.pops)
            return tot_lab_demand

        def randomise_demand(agg_demand):
            randomizer = [id_firm for id_firm in agg_demand.keys()]
            random.shuffle(randomizer)
            return {id_firm: agg_demand[id_firm] for id_firm in randomizer}

        def set_labor_supply():
            """Ideally returns a dictionary/class with the number of unemployed
               people of each type in a region. Atm, one unified type."""
            lab_supply = {id_pop: 0 for id_pop in self.pops}
            for id_pop, pop in self.pops.items():
                lab_supply[id_pop] += pop.unemployed()
            return lab_supply

        agg_lab_demand = randomise_demand(set_labor_demand())
        agg_lab_supply = set_labor_supply()

        # If no market saturation, everyone hires at actual wage
        loop = True
        while set(agg_lab_supply.values()) != {0} and loop:
            for id_firm, lab_demand in agg_lab_demand.items():
                while lab_demand > self.firms[id_firm].workers:
                    [hired] = random.choices(list(agg_lab_supply.keys()), weights=agg_lab_supply.values(), k=1)
                    agg_lab_supply[hired] -= 1
                    self.pops[hired].hired_by(id_firm, 1)
                    self.firms[id_firm].workers += 1
            loop = False

        # That's where it gets complicated
        # If the market is saturated, then we will compute the max wage at ideal supply for every firm,
        # then rank them this way. Then, starting from the bottom, try to poach other firms by matching their max wage.
        # Finally, update the poached and poachee firms' max wages.
        else:
            list_of_firms = []
            for id_firm, firm in self.firms.items():
                max_wage = max(firm.max_wage(agg_lab_demand[id_firm], self.prices[firm.product]), firm.wages)
                list_of_firms.append((id_firm, max_wage))
            list_of_firms.sort(key=lambda x: x[1])
            max_wages = {id_firm: max_wage for id_firm, max_wage in list_of_firms}
            ordrered_firms = [id_firm for id_firm, _ in list_of_firms]

            for id_firm in ordrered_firms:
                max_wage = max_wages[id_firm]
                while agg_lab_demand[id_firm] > self.firms[id_firm].workers:
                    lower_wage_firms = {id_f: self.firms[id_f].workers for id_f, max_salary in max_wages.items()
                                        if max_salary <= max_wage and id_f != id_firm}
                    if len(lower_wage_firms) == 0:
                        break
                    else:
                        [poached_firm] = random.choices(list(lower_wage_firms.keys()),
                                                        weights=lower_wage_firms.values(), k=1)
                        # Update the hiring and firing firms' data and randomly pick a pop in the poached firm
                        self.firms[id_firm].workers += 1
                        self.firms[poached_firm].workers -= 1

                        # Update the pops data by choosing randomly
                        workers = {id_pop: pop.employed_by(poached_firm) for id_pop, pop in self.pops.items()}
                        [fired] = random.choices(list(workers.keys()), weights=workers.values(), k=1)
                        self.pops[fired].poached_by_from(id_firm, poached_firm, 1)

                        # ... and update the wages and max_wages
                        self.firms[id_firm].wages = max(self.firms[poached_firm].max_wage(agg_lab_demand[id_firm],
                                                                                          self.price_of(poached_firm)),
                                                        self.firms[id_firm].wages)
                        max_wages[poached_firm] = self.firms[poached_firm].max_wage(self.firms[poached_firm].workers,
                                                                                    self.price_of(poached_firm))

    def cap_all_supply(self):
        for firm in self.firms.values():
            firm.cap_supply()

    def set_goods_supply(self):
        for firm in self.firms.values():
            firm.set_supply()

    def update_firms_profits(self):
        for firm in self.firms.values():
            firm.update_profits(self.tot_demand, self.prices)

    def tick(self, t: int):
        # Compute useful aggregate(s)
        self.compute_tot_population()

        # Core mechanisms
        self.set_goods_supply()
        self.clear_labor_market()
        self.cap_all_supply()
        self.clear_goods_market()
        self.update_firms_profits()

        # Technical logistics
        self.add_to_history()

    def summary(self):
        for firm in self.firms.values():
            p = []
            w = []
            wage = []
            s = []
            t = []
            for i in range(0, len(self.history)):
                p.append(round(firm.get_from_history("profits", i), 2))
                w.append(round(firm.get_from_history("workers", i), 2))
                wage.append(round(firm.get_from_history("wages", i), 2))
                s.append(round(firm.get_from_history("supply", i), 2))
                t.append((firm.get_from_history("workers", i), firm.get_from_history("supply", i),
                          round(firm.get_from_history("profits", i), 2)))
            print(f'Profits of {firm.product}: {p};'
                  f'total profits: {round(sum(p), 2)}')
            print(f'Supply of {firm.product}: {s};')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
            print(f'Wages of {firm.product}: {wage}')
            print(f'{t}')
            print(f'')

        for pop in self.pops.values():
            print(pop.employed)
            print(pop.income)
