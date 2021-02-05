# It says hello
from goodsvector import GoodsVector
import random


class World:
    TO_HISTORIZE = {'tot_population', 'unemployment_rate', 'gdp', 'gdp_per_capita',
                    'price_level', 'indexed_price_level', 'inflation', 'adjusted_gdp'}
    INTEREST_RATE = 0.01         #TODO @Marius check


    def __init__(self, goods, firms, pops, depositary):
        # Core properties
        self.goods = set(goods)
        self.firms = {firm.id_firm: firm for firm in firms}
        self.pops = {pop.id_pop: pop for pop in pops}
        for pop in self.pops.values():
            pop.set_world(self)

        for firm in self.firms.values():
            firm.set_world(self)
            firm.init_workers()

        self.depositary = depositary

        # Computed aggregates
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
            if pop.pop_type == 3:
                employed += pop.population
            employed += sum(pop.employed.values())
        self.unemployment_rate = (1 - (employed / self.tot_population)) * 100

    def compute_gdp(self):
        """ Compute GDP at transaction prices """
        self.gdp = sum([(firm.sold * firm.price) for firm in self.firms.values()])

    def compute_gdp_per_capita(self):
        """ GDP per person """
        self.gdp_per_capita = self.gdp / self.tot_population

    def compute_price_level(self):
        """ price_level: Computes the price of basic necessities for the average
                         person by (1) taking the average of level 0 needs across
                         the population and (2) computes an average price for this
                         basket of goods.
            indexed_price_level: price_level normalized to the first computed price_level,
                                 starting at 100
            inflation: percentage change between 2 consecutive price_level """

        previous_price_level = self.price_level

        # Create the total needs of level 0 for each good
        survival_goods = {}
        for pop in self.pops.values():
            for good, level, qty in pop.needs:
                if level == 0:
                    if good in survival_goods:
                        survival_goods[good] += qty * pop.population
                    else:
                        survival_goods[good] = qty * pop.population

        # Finds an average sale price in a period for each goods and adds it
        prices = {good: [] for good in self.goods}
        for firm in self.firms.values():
            prices[firm.product].append((firm.sold, firm.price))
        for good in self.goods:
            good_gdp = sum([qty * price for qty, price in prices[good]])
            good_sold = sum([qty for qty, price in prices[good]])
            if good_sold != 0:
                self.average_price[good] = good_gdp / good_sold

        # Price levels formulas
        self.price_level = sum(qty * self.average_price[good] for good, qty in survival_goods.items()) / self.tot_population
        if self.initial_price_level is None:
            self.initial_price_level = self.price_level
        self.indexed_price_level = self.price_level / self.initial_price_level * 100
        if previous_price_level is not None:
            self.inflation = (self.price_level / previous_price_level - 1) * 100

    def compute_adjusted_gdp(self):
        """ To interpret as the value of total production in terms of average basic needs,
            e.g. how many people could my economy feed and clothe? """
        self.adjusted_gdp = self.gdp / self.price_level

    def compute_aggregates(self):
        """ Compute aggregated indicators """
        self.compute_tot_population()
        self.compute_unemployment_rate()
        self.compute_gdp()
        self.compute_gdp_per_capita()
        self.compute_price_level()
        self.compute_adjusted_gdp()

    def set_target_supply_and_price(self):
        """ Each Firm defines its target production goal and price"""
        for firm in self.firms.values():
            firm.set_target_supply_and_price()

    def labor_pool_for(self, hiring_id_firm, pop_level, max_wage):
        """ A Firm can ask the World to give a view of the labor pool currently paid under a certain level """
        # Start with employees paid under the level
        labor_pool = {id_f: firm.workers_for(pop_level) for id_f, firm in self.firms.items()
                      if firm.wages_of(pop_level) <= max_wage and id_f != hiring_id_firm}

        # Then add the unemployed
        agg_lab_supply = {id_pop: pop.unemployed() for id_pop, pop in self.pops.items() if pop.pop_type == pop_level}
        labor_pool['unemployed'] = sum(agg_lab_supply.values())
        return {k: v for k, v in labor_pool.items() if v > 0}

    def clear_labor_market_for(self, pop_level):
        """ Adjust aggregated demand, supply and wages on labor market """

        # Compute ideal workforce
        for id_firm, firm in self.firms.items():
            firm.set_labor_demand_for(pop_level)

        # Fire worker to match ideal workforce
        for id_firm, firm in self.firms.items():
            firm.fire_to_match_labor_demand_for(pop_level)

        # Start of the hiring phase
        target_demand = {id_firm: firm.get_labor_demand_for(pop_level) for id_firm, firm in self.firms.items()}
        # lab_demand represents the target headcount including the current employees

        # Hire one by one until target is reached
        # Firms are processed in a random order to ensure equal access to labor market
        hiring_id_firm = None
        while len(target_demand) > 0:
            if hiring_id_firm is None or hiring_id_firm not in target_demand:
                hiring_id_firm = random.choice(list(target_demand.keys()))
                hiring_firm = self.firms[hiring_id_firm]

            # The Firm tries to find somebody to recruit on the market in its wage range
            action, parameters = hiring_firm.try_to_match_labor_demand(pop_level)
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

    def get_workers_for(self, id_firm):
        workforce = {}
        for id_pop, pop in self.pops.items():
            w = pop.employed_by(id_firm)
            if w > 0:
                workforce[id_pop] = (pop.pop_type, w)
        return workforce

    def pay_salaries(self):
        for id_firm, firm in self.firms.items():
            # Each firm will pay salaries
            salaries = firm.pay_salaries()
            # The world distributes the salaries
            for id_pop, salary in salaries.items():
                self.pops[id_pop].cash_in_salary(salary)

    def pay_dividends(self):
        # Iterate through firms to find dividends
        for id_firm, firm in self.firms.items():
            # Each firm will pay dividends
            tot_dividends = firm.pay_dividends()
            if tot_dividends > 0:
                # Find the shares and normalise
                all_shares = sum(self.depositary[id_firm].values())
                firm_dividends = {id_pop: (tot_dividends * shares / all_shares)
                                  for id_pop, shares in self.depositary[id_firm].items() if shares != 0}
                # Distribute the cash according to the dividends
                for id_pop, cash in firm_dividends.items():
                    self.pops[id_pop].cash_in_dividends(cash)

    def produce_goods(self):
        for firm in self.firms.values():
            firm.produce_goods()

    def clear_goods_market(self):
        """ Works like a giant supermarket queue: needs are sorted by levels and split up in increments,
            then matched randomly (with weights on prices) with the products and the transaction happens """

        def prices_for_goods():
            """ Creates a dictionary with firms' supply and prices indexed by goods """
            supply = {good: {} for good in self.goods}
            for id_firm, firm in self.firms.items():
                supply[firm.product][id_firm] = firm.get_price()
            return supply

        def market_queue(level):
            """ Splits up needs of all the pops in increments, with smaller ones to fill,
                create the queue and shuffle """
            queue = []
            chunk = sum(pop.population for pop in self.pops.values()) / 100
            for id_pop, pop in self.pops.items():
                if pop.income > 0:
                    for need in pop.needs:
                        good, l, qty = need
                        if l == level:
                            q, r = divmod(qty * pop.population, chunk)
                            for x in range(int(q)):
                                queue.append((id_pop, good, chunk))
                            if r != 0:
                                queue.append((id_pop, good, r))

            random.shuffle(queue)
            return queue

        # Gather market prices for goods
        market_prices = prices_for_goods()

        for level in range(3):
            # Once basic needs are met, people save a portion of their income
            if level == 1:
                for id_pop, pop in self.pops.items():
                    pop.save()

            level_demand = market_queue(level)
            broke_pops = set()
            sold_out_goods = set()
            for id_pop, good, qty in level_demand:
                # If pop has no money, or no more of a good, then don't get stuck in an infinite loop
                if id_pop in broke_pops or good in sold_out_goods:
                    continue
                pop = self.pops[id_pop]
                # Add pop to broke-pops if no more money
                while qty != 0:
                    if level != 0 and pop.income == 0:
                        broke_pops.add(id_pop)
                        break

                    # Choose a seller randomly in tot_supply, with weights inversely proportional to price
                    # if multiple choices so that cheaper goods are picked more quickly
                    firm_pool = [id_firm for id_firm in market_prices[good] if self.firms[id_firm].has_stock()]
                    if len(firm_pool) == 0:
                        sold_out_goods.add(good)
                        break
                    elif len(firm_pool) == 1:
                        [id_f] = firm_pool
                    else:
                        prices_pool = [1 / (p ** 2) for id_firm, p in market_prices[good].items()
                                       if self.firms[id_firm].has_stock()]
                        [id_f] = random.choices(firm_pool, weights=prices_pool, k=1)

                    selling_firm = self.firms[id_f]
                    # Check if the firm has enough stock, else finish the stock
                    sold = min(selling_firm.stock, qty)
                    # Check if pop has enough money to buy the whole thing, if not only buy until no money
                    discount = pop.buy_good(good, level, sold, selling_firm.price)
                    qty -= sold * discount
                    # Do the transaction
                    selling_firm.sell_goods(sold * discount)

                    # If no more money, on to the next one
                    if discount != 1:
                        break

    def decide_dividend_to_distribute(self):
        for firm in self.firms.values():
            firm.decide_dividend_to_distribute()

    def start_period(self):
        for firm in self.firms.values():
            firm.start_period()
        for pop in self.pops.values():
            pop.start_period()

    def account_for_interests(self):
        #TODO @Marius check
        for firm in self.firms.values():
            firm.add_interest(self.INTEREST_RATE)
        for pop in self.pops.values():
            pop.add_interest(self.INTEREST_RATE)

    def end_period(self):
        # Technical logistics
        self.add_to_history()
        # Compute useful aggregate(s)
        self.compute_aggregates()
        # Close period
        for firm in self.firms.values():
            firm.end_period()
        for pop in self.pops.values():
            pop.end_period()

    def tick(self):
        self.start_period()

        # Firms set their target production goals and price
        self.set_target_supply_and_price()

        # Labor market clearing for BlueCollars
        self.clear_labor_market_for(0)
        # Labor market clearing for WhiteCollars
        self.clear_labor_market_for(1)

        # Distribute money from firms to pops
        self.pay_salaries()
        self.pay_dividends()

        # Produce goods
        self.produce_goods()

        # Buy goods
        self.clear_goods_market()

        self.decide_dividend_to_distribute()

        #TODO @Marius Check
        self.account_for_interests()

        self.end_period()

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

            for id_firm, firm in self.firms.items():
                firm_name = f"firm{id_firm}"
                for key in {'profits', 'product', 'sold', 'stock', 'price', 'productivity', 'account', 'dividends', "capital"}:
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

    def high_level_analysis(self):
        #TODO @marius je sais pas si tu as vu cette fonction. J'essaie de synthétiser les données clés "humainement" compréhensibles
        # Production analysis
        cum_needs = GoodsVector(self.goods)
        cum_needs01 = GoodsVector(self.goods)
        for pop in self.pops.values():
            cum_needs += pop.cumulated_needs()
            cum_needs01 += pop.cumulated_needs({0, 1})

        prod_capacity = GoodsVector(self.goods)
        for firm in self.firms.values():
            bc = firm.workers_for(0)
            productivity = firm.adjusted_productivity()
            good = firm.product
            # print(firm.id_firm, bc, good, productivity, bc * productivity)
            prod_capacity[good] += bc * productivity

        ratio_needs_prod = GoodsVector(self.goods)
        ratio_needs_prod_01 = GoodsVector(self.goods)
        for good in self.goods:
            ratio_needs_prod[good] = prod_capacity[good] / cum_needs[good]
            ratio_needs_prod_01[good] = prod_capacity[good] / cum_needs01[good]

        analysis = {'cumulated_needs_01': cum_needs01,
                    'cumulated_needs': cum_needs,
                    'production': prod_capacity,
                    'ratio_needs_prod': ratio_needs_prod,
                    'ratio_needs_prod_01': ratio_needs_prod_01}
        to_display = {'unemployment_rate', 'gdp', 'gdp_per_capita', 'indexed_price_level','adjusted_gdp'}
        at_i = self.history[-1]
        analysis.update({k: at_i[k] for k in to_display})

        wages = [sum(firm.wages_of(i) * firm.workers_for(i) for firm in self.firms.values()) for i in range(2)]
        workers = [sum(firm.workers_for(i) for firm in self.firms.values()) for i in range(2)]
        average_wages = [wages[i] / workers[i] for i in range(2)]
        average_wages.append(sum(wages) / sum(workers))
        analysis.update({'average_wages': average_wages})
        return analysis
