from errors import OrphanStatError, RuleError, StatNotFoundError
MAX_LVL = 80
SCALES = ["exp", "log", "flat", "custom_dps"]


def parse_rules(rules):
    parsed = dict()
    for section in rules:
        parsed[section] = dict()
        for o in rules[section]:
            value = rules[section][o]

            if o == "scale_stat":
                value = value.split(",")

            elif o == "scale_method":
                if value not in SCALES:
                    raise RuleError("No such scale method: " + value)

            elif o == "cap":
                try:
                    value = int(value)
                except ValueError:
                    raise RuleError("{0}/{1} not an integer.".format(o, v))

            elif o == "scale_amount":
                if "." in value:
                    try:
                        value = float(value)
                    except ValueError:
                        raise RuleError("{0}/{1} not a number.".format(o, v))
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        raise RuleError("{0}/{1} not a number.".format(o, v))

            else:
                print("'{0}' option not handled, passing as string.".format(o))

            parsed[section][o] = value

    return parsed
    

class StatsOwner:

    def __init__(self):
        self.stat_objects = dict()
        self.lvl = 1
        self.rules = dict()

    def load_rules(self, rules):
        if isinstance(rules, dict):
            self.rules = rules
        else:
            raise TypeError("Rules should be a dict.")

    def get(self, name):
        if name not in self.stat_objects:
            raise StatNotFoundError("No such stat: \"{}\"".format(name))
        return self.stat_objects[name]

    def add(self, stat):
        if isinstance(stat, list):
            for s in stat:
                if not isinstance(s, Stat):
                    raise TypeError(
                        "list contains an object which is not a Stat"
                    )
                self.claim(s)
                if self.rules:
                    s.apply_rules(self.rules)
                self.stat_objects[s.name] = s
        else:
            if not isinstance(stat, Stat):
                raise TypeError(
                    "'stat' should be a Stat object or list of Stat objects."
                )
            self.claim(stat)
            if self.rules:
                stat.apply_rules(self.rules)
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
        self.scale_method = self.lvl_scale_exp
        self.scale_amount = 1
        self.scale_stat = None
        self.cap = 10000

    def apply_rules(self, rules):
        if self.name not in rules:
            raise RuleError("No '{}' section in rules.".format(self.name))

        r = rules[self.name]

        if r["scale_method"] == "exp":
            self.scale_method = self.lvl_scale_exp
        elif r["scale_method"] == "flat":
            self.scale_method = self.scale_flat
        else:
            print("Missing scaling method for '{}'".format(r["scale_method"]))
            self.scale_method = self.lvl_scale_exp

        self.scale_amount = r["scale_amount"]
        self.scale_stat = r["scale_stat"]

    def get_value(self, raw=False):
        if raw:
            return self.base_value
        return self.value   # Final value, after modifiers.

    def lvl_scale_exp(self):
        v = self.base_value * pow(
            10 * self.scale_amount, self.owner.lvl / MAX_LVL
        )
        return v

    def stat_scale_exp(self):
        stat = self.owner.get(self.scale_stat)
        v = max(
            self.base_value * pow(
                10 * self.scale_amount, stat.get_value() / stat.cap
            ), self.cap
        )
        return v

    def scale_flat(self):
        if self.scale_stat == "lvl":
            scalar = self.owner.lvl - 1
        else:
            scalar = self.owner.get(self.scale_stat).get_value()
        return self.base_value + scalar * self.scale_amount

    def update(self):
        if not self.owner:
            raise OrphanStatError("No owner for stat '{}'".format(self.name))

        new_val = self.scale_method()

        flat = self.owner.get_flat_modifiers(self.name)
        scalar = self.owner.get_scalar_modifiers(self.name)

        for v in flat:
            new_val += v

        change = 0.0
        for v in scalar:
            change += new_val * v
        new_val += change

        self.value = int(round(new_val))
