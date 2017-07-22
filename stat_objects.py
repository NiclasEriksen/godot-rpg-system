from errors import OrphanStatError
MAX_LVL = 80


class StatsOwner:

    def __init__(self):
        self.stat_objects = dict()
        self.lvl = 1

    def load_rules(self, config=None):
        pass

    def get(self, name):
        if name not in self.stat_objects:
            raise StatNotFoundError("No such stat: \"{}\"".format(name))

    def add(self, stat):
        if isinstance(stat, list):
            for s in stat:
                if not isinstance(s, Stat):
                    raise TypeError(
                        "list contains an object which is not a Stat"
                    )
                self.claim(s)
                self.stat_objects[s.name] = s
        else:
            if not isinstance(stat, Stat):
                raise TypeError(
                    "'stat' should be a Stat object or list of Stat objects."
                )
            self.claim(stat)
            self.stat_objects[stat.name] = stat

    def claim(self, stat):
        if isinstance(stat, list):
            for s in stat:
                if not isinstance(s, Stat):
                    raise TypeError(
                        "list contains an object which is not a Stat"
                    )
                s.owner = self
        else:
            if not isinstance(stat, Stat):
                raise TypeError(
                    "'stat' should be a Stat object or a list of Stat objects."
                )
            stat.owner = self

    @property
    def stats(self):
        return [v for k, v in self.stat_objects.items()]

    def set_lvl(self, lvl):
        if not isinstance(lvl, int):
            if isinstance(lvl, float):
                lvl = int(lvl)
            else:
                raise TypeError("'lvl' should be a number.")
        self.lvl = lvl

    def get_flat_modifiers(self, stat):
        return []

    def get_scalar_modifiers(self, stat):
        return []


class Stat:

    def __init__(self, name, value=0):
        self.owner = None
        self.name = name
        self.base_value = self.value = value
        self.lvl_scale = self.lvl_scale_exp
        self.lvl_scale_amount = 1

    def get_value(self, raw=False):
        if raw:
            return self.base_value
        return self.value   # Final value, after modifiers.

    def lvl_scale_exp(self):
        v = self.base_value * pow(
            10 * self.lvl_scale_amount, self.owner.lvl / MAX_LVL
        )
        return v

    def lvl_scale_flat(self):
        return self.base_value + (self.owner.lvl - 1) * self.lvl_scale_amount

    def update(self):
        if not self.owner:
            raise OrphanStatError("No owner for stat '{}'".format(self.name))

        new_val = self.lvl_scale()

        flat = self.owner.get_flat_modifiers(self.name)
        scalar = self.owner.get_scalar_modifiers(self.name)

        for v in flat:
            new_val += v

        change = 0.0
        for v in scalar:
            change += new_val * v
        new_val += change

        self.value = int(round(new_val))
