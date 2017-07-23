import random
from math import log, exp
from stat_objects import Stat, StatsOwner, parse_rules, load_rules_from_file
from errors import StatNotFoundError

MAX_LVL = 80


def main():
    import matplotlib.pyplot as plt
    lvls = 80
    so = StatsOwner()
    so.load_rules(load_rules_from_file("rules.cfg"))
    p = []
    for lvl in range(lvls):
        v1 = so.get_next_lvl_target()
        so.lvl += 1
        r = so.get_next_lvl_target() - v1
        p.append(r)
    print(p)
    y = [y for y in range(lvls)]
    plt.plot(y, p)
    plt.xlabel("level")
    plt.ylabel("value")
    plt.show()


def lvl_scale_exp(i, lvl, scale=1):
    return i * pow(10 * scale, lvl / MAX_LVL)


def lvl_scale_flat(i, lvl, scale=1):
    return i + lvl * scale


def scale(i, scale=0.5):
    return i * exp(scale)

if __name__ == "__main__":
    main()
