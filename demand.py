class Demand:
    def __init__(self, goods, demand=None):
        self.goods = set(goods)
        if demand is None:
            self.demand = {good: 0 for good in self.goods}
        else:
            self.demand = demand
            if goods != set(self.demand.keys()):
                # We chose a strict policy here: goods should be declared in the list of goods in the world
                raise KeyError()
            if any(qty < 0 for qty in self.demand.values()):
                # Quantities should be positive
                raise ValueError()

    def is_empty(self):
        if len(self.goods) == 0:
            return True
        return sum(qty for qty in self.demand.values()) == 0

    def __repr__(self):
        goods_str = ",".join(f"'{good}'" for good in self.goods)
        if self.is_empty():
            return f'Demand({{{goods_str}}})'
        demand_str = ",".join(f"'{good}':'{qty}'" for good, qty in self.demand.items())
        return f'Demand({{{goods_str}}}, {{{demand_str}}})'

    # Representations
    def __str__(self):
        return ",".join(f"{good}:{qty}" for good, qty in self.demand.items())

    # Container access
    def __len__(self):
        return len(self.demand)

    def __getitem__(self, good):
        if good in self.demand:
            return self.demand[good]
        # We chose a strict policy here: goods should be declared in the list of goods in the world
        raise KeyError()

    def __setitem__(self, good, qty):
        if good in self.demand:
            if qty >= 0:
                # Quantities should be positive
                self.demand[good] = qty
            else:
                raise ValueError()
        else:
            # We chose a strict policy here: goods should be declared in the list of goods in the world
            raise KeyError()

    def __contains__(self, key):
        return key in self.demand

    def __iter__(self):
        return self.demand.__iter__()

    def keys(self):
        return self.demand.keys()

    def values(self):
        return self.demand.values()

    def items(self):
        return self.demand.items()

    # Comparisons
    def __eq__(self, other):
        if self.goods != other.goods:
            raise KeyError()
        return all(self.demand[good] == other[good] for good in self.goods)

    def __lt__(self, other):
        if self.goods != other.goods:
            raise KeyError()
        return all(self.demand[good] < other[good] for good in self.goods)

    def __le__(self, other):
        if self.goods != other.goods:
            raise KeyError()
        return all(self.demand[good] <= other[good] for good in self.goods)

    def __add__(self, other):
        # Operator +
        if self.goods != other.goods:
            raise KeyError()
        tot_demand = {good: self.demand[good] + other[good] for good in self.goods}
        return Demand(self.goods, tot_demand)

    def __iadd__(self, other):
        # Operator += : in place change
        if self.goods != other.goods:
            raise KeyError()
        self.demand = {good: self.demand[good] + other[good] for good in self.goods}
        return self


if __name__ == '__main__':

    world_goods = {'food', "lodging"}
    d = Demand(world_goods, {'food': 12, 'lodging': 5})
    d1 = Demand(world_goods, {'food': 11, 'lodging': 4})
    d4 = Demand(world_goods, {'food': 12, 'lodging': 4})
    d2 = Demand(world_goods, {'food': 1, 'lodging': 8})
    d3 = Demand(world_goods)

    print(d < d1)
    print(d1 < d)
    print(d > d1)
    print(d4 < d)
    print(d4 <= d)

    print(repr(d))
    print(repr(d3))
    print(repr(d + d2))
    d += d2
    print(repr(d))

    d += d2
    print(repr(d))

