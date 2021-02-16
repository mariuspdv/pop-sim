from historizor import Historizor
from goodsvector import GoodsVector


class Pop(Historizor):

    def __init__(self, id_pop, pop_type, goods, needs, population, employed, savings, thrift, investment_propensity):
        super().__init__()
        self.id_pop = id_pop
        self.pop_type = pop_type
        self.goods = goods
        self.needs = needs
        self._levels = sorted(list(set(l for _, l, _ in needs)))
        self.population = population
        self.demand = GoodsVector(self.goods)
        self.consumption = GoodsVector(self.goods)
        self.employed = employed

        # Cash accounts
        self.income = 0
        self.savings = savings

        self.available_income = self.income
        self.thrift = thrift
        self.investment_propensity = investment_propensity
        self._world = None

    def __str__(self):
        return f'PoP: Hello, we are {self.population}'

    def set_world(self, world):
        self._world = world

    def cumulated_needs(self, levels=None):
        cum_needs = {good: 0 for good in self.goods}
        for good, l, qty in self.needs:
            if levels is None:
                cum_needs[good] += self.population * qty
            elif l in levels:
                cum_needs[good] += self.population * qty
        return GoodsVector(self.goods, cum_needs)

    def unemployed(self):
        return self.population - sum(v for _, v in self.employed.items())

    def employed_by(self, id_firm):
        return self.employed.get(id_firm, 0)

    def start_period(self):
        self.available_income = 0
        self.consumption = GoodsVector(self.goods)

    def end_period(self):
        pass

    def fired_by(self, id_firm, employees):
        self.employed[id_firm] -= employees

    def hired_by(self, id_firm, employees):
        self.employed[id_firm] += employees

    def poached_by_from(self, id_firm, poached_firm, employees):
        self.employed[id_firm] += employees
        self.employed[poached_firm] -= employees

    def set_income_from_salary_and_dividends(self, firms, dividends):
        income_from_work = sum(workers * firms[id_firm].wages_of(self.pop_type)
                               for id_firm, workers in self.employed.items())
        income_from_shares = dividends[self.id_pop]
        self.income = income_from_work + income_from_shares
        self.available_income = self.income

    def cash_in_salary(self, salary):
        self.income += salary
        self.available_income += salary

    def cash_in_dividends(self, dividends):
        self.income += dividends
        self.available_income += dividends

    def use_savings(self):
        if self.savings > 3 * self.income:
            income_supplement = 0.1 * self.savings
            self.savings -= income_supplement
            self.income += income_supplement

    def save(self):
        if self.savings < (-3 * self.income):
            self.savings += self.income
            self.income = 0
        else:
            self.savings += self.income * self.thrift
            self.income *= (1 - self.thrift)

    def add_interest(self, r):
        self.savings *= (1 + r)

    def buy_good(self, good, level, qty, price):
        """ Takes care of the transaction on the buyer's side, changing income and consumption """

        # If lack of money, compute the proportion of the increment bought...
        if self.income < (price * qty):
            # ... except if basic need, in which case use savings (or borrow, added small constraint)
            if level == 0:
                if -(self.savings * 0.1) < self.available_income:
                    from_savings = (price * qty) - self.income
                    from_income = self.income
                    self.savings -= from_savings
                    self.income -= from_income
                    self.consumption[good] += qty
                    return 1
            # Accounting
            discount = self.income / (price * qty)

            amount = self.income
            self.income -= amount
            self.consumption[good] += qty * discount
            return discount

        # Accounting
        amount = price * qty
        self.income -= amount
        self.consumption[good] += qty
        return 1
