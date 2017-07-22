import random
from math import log, exp
from stat_objects import Stat, StatsOwner
from errors import StatNotFoundError

MAX_LVL = 80


def main():
    import matplotlib.pyplot as plt
    lvls = 80
    p1 = [lvl_scale_exp(15, x, scale=1) for x in range(lvls)]
    p2 = [lvl_scale_flat(15, x, scale=1) for x in range(lvls)]
    p3 = [lvl_scale_exp(15, x, scale=1.15) for x in range(lvls)]
    y = [y for y in range(lvls)]
    plt.plot(y, p1)
    plt.plot(y, p2)
    plt.plot(y, p3)
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
