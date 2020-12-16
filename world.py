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
    TO_HISTORIZE = {'tot_demand', 'tot_supply', 'tot_population', 'unemployment_rate', 'gdp', 'gdp_per_capita',
                    'price_level', 'indexed_price_level', 'inflation', 'adjusted_gdp'}

    def __init__(self, goods, firms, pops, depositary):
        # Core properties
        self.goods = set(goods)
        self.firms = {firm.id_firm: firm for firm in firms}
        self.pops = {pop.id_pop: pop for pop in pops}
        for firm in self.firms.values():
            firm.set_world(self)
        for pop in self.pops.values():
            pop.set_world(self)

        self.depositary = depositary

        # Computed aggregates
        self.tot_demand = {}
        self.tot_supply = {}
        self.tot_population = 0
        self.unemployment_rate = 0
        self.gdp = 0
        self.gdp_per_capita = 0
        self.average_price = {good: 0 for good in self.goods}
        self.price_level = None
        self.adjusted_gdp = 0
        self.initial_price_level = None
        self.indexed_price_level = None
        self.inflation = 0

        # Technical logistics
        self.history = []

    def get_pops(self):
        return self.pops

    def add_to_history(self):
        """ Historicize World indicators. Cascades to Firms and Pops"""
        for firm in self.firms.values():
            firm.add_to_history()
        for pop in self.pops.values():
            pop.add_to_history()
        self.history.append({k: self.__getattribute__(k) for k in self.TO_HISTORIZE})

    def compute_tot_population(self):
        """ Compute total population"""
        self.tot_population = sum(pop.population for pop in self.pops.values())

    def compute_unemployment_rate(self):
        """ Compute a percentage of unemployment (0-100)"""
        employed = 0
        for pop in self.pops.values():
            employed += sum(pop.employed.values())
        self.unemployment_rate = (1 - (employed / self.tot_population)) * 100

    def compute_gdp(self):
        """ Compute the total value of demanded good"""
        self.gdp = sum([(firm.sold * firm.price) for firm in self.firms.values()])

    def compute_gdp_per_capita(self):
        """ GDP per person"""
        self.gdp_per_capita = self.gdp / self.tot_population

    def compute_price_level(self):
        """price_level : Computes the price of basic necessities for the average
           person by taking the average of level 0 needs across
           the population and computes a price level from there.
           indexed_price_level: price_level normalized to the first computed price_level being 100
           inflation = percentage of change between 2 consecutive price_level
           """
        previous_price_level = self.price_level
        survival_goods = {}
        for pop in self.pops.values():
            for good, level, qty in pop.needs:
                if level == 0:
                    if good in survival_goods:
                        survival_goods[good] += qty * pop.population
                    else:
                        survival_goods[good] = qty * pop.population

        prices = {good: [] for good in self.goods}
        for firm in self.firms.values():
            prices[firm.product].append((firm.sold, firm.price))
        for good in self.goods:
            good_gdp = sum([qty * price for qty, price in prices[good]])
            good_sold = sum([qty for qty, price in prices[good]])
            if good_sold != 0:
                self.average_price[good] = good_gdp / good_sold

        self.price_level = sum(qty * self.average_price[good] for good, qty in survival_goods.items()) / self.tot_population
        if self.initial_price_level is None:
            self.initial_price_level = self.price_level
        self.indexed_price_level = self.price_level / self.initial_price_level * 100
        if previous_price_level is not None:
            self.inflation = (self.price_level / previous_price_level - 1) * 100

    def compute_adjusted_gdp(self):
        """To interpret as the number of average basic needs produced in terms of value"""
        self.adjusted_gdp = self.gdp / self.price_level

    def compute_aggregates(self):
        """ Compute aggregated indicators """
        self.compute_tot_population()
        self.compute_unemployment_rate()
        self.compute_gdp()
        self.compute_gdp_per_capita()
        self.compute_price_level()
        self.compute_adjusted_gdp()

    def reset_consumption(self):
        for pop in self.pops.values():
            pop.consumption = GoodsVector(self.goods)

    def set_goods_supply(self):
        """ Each Firm defines its target production goal"""
        for firm in self.firms.values():
            firm.set_supply()

    def labor_pool_for(self, hiring_id_firm, pop_level, max_wage):
        """ A Firm can ask the World to give a view of the labour pool currently paid under a certain level"""
        agg_lab_supply = {id_pop: pop.unemployed() for id_pop, pop in self.pops.items() if pop.pop_type == pop_level}
        # a Firm will try first to poach firms that pay less or to hire unemployed workers
        labor_pool = {id_f: firm.workers_for(pop_level) for id_f, firm in self.firms.items()
                      if firm.wages_of(pop_level) <= max_wage and id_f != hiring_id_firm}
        labor_pool['unemployed'] = sum(agg_lab_supply.values())
        return {k: v for k, v in labor_pool.items() if v > 0}

    def clear_labor_market_for(self, pop_level):
        """Adjust aggregated demand, supply and wages on labor market"""
        target_demand = {id_firm: firm.set_labor_demand_for(pop_level) for id_firm, firm in self.firms.items()}
        # lab_demand represents the target headcount including the current employees

        # Hire one by one until target is reached
        # Firms are processed in a random order to ensure equal access to labor market
        hiring_id_firm = None
        while len(target_demand) > 0:
            if hiring_id_firm is None or hiring_id_firm not in target_demand:
                hiring_id_firm = random.choice(list(target_demand.keys()))
                hiring_firm = self.firms[hiring_id_firm]

            # The Firm tries to find somebody to recruit on the market in its wage range
            action, parameters = hiring_firm.try_to_match_labor_demand(pop_level, target_demand[hiring_id_firm])
            if action == "give_up":
                del target_demand[hiring_id_firm]
                continue

            if action == "hire_unemployed":
                wage = parameters
                # Find a random Pop with unemployed workers
                agg_lab_supply = {id_pop: pop.unemployed() for id_pop, pop in self.pops.items() if pop.pop_type == pop_level}
                [hired_pop] = random.choices(list(agg_lab_supply.keys()), weights=agg_lab_supply.values(), k=1)
                # Hiring firm hires the worker
                hiring_firm.hire(pop_level, wage, 1)
                # Log that in the Pop
                self.pops[hired_pop].hired_by(hiring_id_firm, 1)

            if action == "poach":
                id_firm_to_poach, poached_bonus = parameters
                firm_to_poach = self.firms[id_firm_to_poach]
                # Randomly select the origin pop inside the selected firm
                employed = {id_pop: pop.employed_by(id_firm_to_poach) for id_pop, pop in self.pops.items() if pop.pop_type == pop_level}
                [hired_pop] = random.choices(list(employed.keys()), weights=employed.values(), k=1)
                # Hiring firm hires the worker
                hiring_firm.hire(pop_level, firm_to_poach.wages_of(pop_level) * poached_bonus, 1)
                # Log that in the Pop
                self.pops[hired_pop].poached_by_from(hiring_id_firm, id_firm_to_poach, 1)
                # Poached firm let the worker flee
                firm_to_poach.adjust_workers_for(pop_level, -1)

    def adjust_all_supply(self):
        for firm in self.firms.values():
            firm.adjust_supply()

    def pay_salaries_and_dividends(self):
        dividends = {id_pop: 0 for id_pop, pop in self.pops.items()}
        for id_firm, firm in self.firms.items():
            """
            if firm.profits > 0 and firm.account >= (firm.profits * (1 - firm.SAVINGS_RATE)):
                tot_dividends = firm.profits * (1 - firm.SAVINGS_RATE)
            """
            tot_dividends = firm.dividends
            if tot_dividends > 0:
                all_shares = sum(self.depositary[id_firm].values())
                firm_dividends = {id_pop: (tot_dividends * shares / all_shares)
                                  for id_pop, shares in self.depositary[id_firm].items() if shares != 0}
                for id_pop, cash in firm_dividends.items():
                    dividends[id_pop] += cash
        for pop in self.pops.values():
            pop.set_income_from_salary_and_dividends(self.firms, dividends)

    def clear_goods_market(self):
        """Sets aggregate supply, demand, and finds equilibria
           on goods markets through an iterative process,
           with price floors and ceilings to limit changes."""

        def aggregate_supply():
            supply = {good: {} for good in self.goods}
            for id_firm, firm in self.firms.items():
                qty, price = firm.market_supply()
                supply[firm.product][id_firm]= price
            return supply

        def market_queue(level):
            queue = []
            for id_pop, pop in self.pops.items():
                if pop.income > 0:
                    for need in pop.needs:
                        good, l, qty = need
                        if l == level:
                            q, r = divmod(qty * pop.population, 0.5)
                            for x in range(int(q)):
                                queue.append((id_pop, good, 0.5))
                            if r != 0:
                                queue.append((id_pop, good, r))

            random.shuffle(queue)
            return queue

        # Compute the aggregated supply of goods over all the firms
        tot_supply = aggregate_supply()

        for level in range(3):
            if level == 1:
                for id_pop, pop in self.pops.items():
                    # TODO mettre un méthode "mettre de coté" dans Pop
                    pop.savings += pop.income * pop.thrift
                    pop.income *= (1 - pop.thrift)

            level_demand = market_queue(level)
            broke_pops = set()
            sold_out_goods = set()
            for id_pop, good, qty in level_demand:
                if id_pop in broke_pops or good in sold_out_goods:
                    continue
                pop = self.pops[id_pop]
                while qty != 0:
                    if level != 0 and pop.income == 0:
                        broke_pops.add(id_pop)
                        break

                    # choose a seller in tot_supply
                    firm_pool = [id_firm for id_firm in tot_supply[good] if self.firms[id_firm].has_stock()]
                    if len(firm_pool) == 0:
                        sold_out_goods.add(good)
                        break
                    elif len(firm_pool) == 1:
                        [id_f] = firm_pool
                    else:
                        prices_pool = [1 / (p ** 2) for id_firm, p in tot_supply[good].items()
                                       if self.firms[id_firm].has_stock()]
                        [id_f] = random.choices(firm_pool, weights=prices_pool, k=1)

                    selling_firm = self.firms[id_f]
                    sold = min(selling_firm.stock, qty)
                    discount = pop.buy_good(good, level, sold, selling_firm.price)
                    qty -= sold * discount
                    selling_firm.sell_goods(sold * discount)

                    if discount != 1:
                        break

        self.tot_supply = tot_supply

    def update_firms_profits(self):
        for firm in self.firms.values():
            firm.update_profits()

    def tick(self, t: int):

        # Core mechanisms

        # Firms set their target production goals
        self.set_goods_supply()
        # Labor market clearing for BlueCollars
        self.clear_labor_market_for(0)
        # Labor market clearing for WhiteCollars
        self.clear_labor_market_for(1)

        # self.adjust_all_supply()
        self.pay_salaries_and_dividends()
        self.clear_goods_market()
        self.update_firms_profits()

        # Technical logistics
        self.add_to_history()

        # Compute useful aggregate(s)
        self.compute_aggregates()

        # Temporary logistics
        self.reset_consumption()

    def export(self):
        def flatten_dict(prefix, a_dict):
            return {f"{prefix}_{key}": value for key, value in a_dict.items()}

        to_display = {'tot_population', 'unemployment_rate', 'gdp', 'gdp_per_capita', 'price_level',
                      'indexed_price_level', 'inflation', 'adjusted_gdp'}
        full_table = []
        for i in range(0, len(self.history)):
            at_i = self.history[i]
            d = {'t': i}
            d.update({k: at_i[k] for k in to_display})
            #d.update(flatten_dict('supply', at_i['tot_supply']))
            #d.update(flatten_dict('demand', at_i['tot_demand']))

            for id_firm, firm in self.firms.items():
                firm_name = f"firm{id_firm}"
                for key in {'profits', 'product', 'sold', 'stock', 'price', 'productivity', 'account'}:
                    d[f"{firm_name}_{key}"] = firm.get_from_history(key, i)
                for pop_level in range(2):
                    d[f"{firm_name}_workers_{pop_level}"] = firm.get_from_history('workers', i)[pop_level]
                    d[f"{firm_name}_wages_{pop_level}"] = firm.get_from_history('wages', i)[pop_level]

            for id_pop, pop in self.pops.items():
                pop_name = f"pop{id_pop}"
                for key in {'pop_type', 'population', 'available_income', 'savings', 'thrift'}:
                    d[f"{pop_name}_{key}"] = pop.get_from_history(key, i)
                d.update(flatten_dict(f"{pop_name}_consumption", pop.get_from_history('consumption', i)))

            full_table.append(d)

        return full_table

    def summary(self):
        def price_of(firm_or_product):
            if firm_or_product in self.prices:
                return self.prices[firm_or_product]
            elif firm_or_product in self.firms:
                return self.prices[self.firms[firm_or_product].product]

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
            print(f'Price of {firm.product}: {price_of(id_firm)};')
            print(f'Workers of {firm.product}: {w}; max: {max(w)}; min: {min(w)}')
            print(f'Wages of {firm.product}: {wage}')
            print(f'{t}')
            print(f'')

        for pop in self.pops.values():
            print(pop.employed)
            print(pop.income)

