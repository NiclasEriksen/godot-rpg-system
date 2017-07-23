import pytest
from stat_objects import Stat, StatsOwner, parse_rules, load_rules_from_file
from errors import OrphanStatError


def test_stat_value_type():
    s = Stat("int")
    assert (
        isinstance(s.get_value(), int) and
        isinstance(s.get_value(raw=True), int)
    )


def test_stat_owner_error():
    s = Stat("int")
    with pytest.raises(OrphanStatError):
        s.update()


def test_statowner_add_stat():
    s = Stat("int")
    so = StatsOwner()
    so.add(s)
    assert s in so.stats


def test_statowner_add_multiple_stats():
    s1 = Stat("int")
    s2 = Stat("str")
    so = StatsOwner()
    so.add([s1, s2])
    assert s1 in so.stats and s2 in so.stats


def test_statowner_no_duplicate():
    s1 = Stat("int")
    s2 = Stat("int")
    so = StatsOwner()
    so.add([s1, s2])
    assert len(so.stats) == 1


def test_statsowner_claim():
    so = StatsOwner()
    s1 = Stat("str")
    s2 = Stat("int")
    so.claim(s2)
    assert not s1.owner and s2.owner == so


def test_statsowner_claim_multiple():
    so = StatsOwner()
    s1 = Stat("str")
    s2 = Stat("int")
    so.claim([s1, s2])
    assert s1.owner == so and s2.owner == so


def test_statsowner_get_stats():
    so = StatsOwner()
    s1 = Stat("str")
    s2 = Stat("int")
    so.add(s1)
    so.add(s2)
    assert s1 in so.stats and s2 in so.stats


def test_stat_scale_flat():
    owner = StatsOwner()
    s = Stat("int")
    s.base_value = 10
    s.scale_method = s.scale_flat
    s.scale_stat = "lvl"
    s.scale_amount = 1
    owner.claim(s)
    owner.set_lvl(1)
    s.update()
    lvl1 = s.get_value()
    owner.set_lvl(10)
    s.update()
    lvl10 = s.get_value()
    assert lvl1 == 10 and lvl10 == 19


def test_stat_scale_stat():
    owner = StatsOwner()
    s1 = Stat("sta")
    s2 = Stat("hp")
    s1.value = 10
    s2.base_value = 100
    s2.scale_stat = "sta"
    s2.scale_method = s2.scale_flat
    s2.scale_amount = 10
    owner.add([s1, s2])
    owner.get("hp").update()
    assert s2.get_value() == 200


def test_stat_scale_exp():
    owner = StatsOwner()
    s = Stat("int")
    s.base_value = 10
    s.scale_method = s.lvl_scale_exp
    s.scale_amount = 1
    owner.claim(s)
    owner.set_lvl(1)
    s.update()
    lvl1 = s.get_value()
    owner.set_lvl(20)
    s.update()
    lvl20 = s.get_value()
    assert lvl1 == 10 and lvl20 == 18


def test_load_rules():
    import configparser
    rules = configparser.ConfigParser()
    rules.read("rules.cfg")
    assert "DEFAULT" in rules


def test_validate_rules():
    import configparser
    rules = configparser.ConfigParser()
    rules.read("rules.cfg")
    required = ["scale_stat", "scale_method"]
    for section in rules.sections():
        for r in required:
            assert r in rules.options(section)


def test_parse_rule_section():
    import configparser
    rules = configparser.ConfigParser()
    rules.read("rules.cfg")
    s = rules["str"]
    s["cap"] = "10000"
    s["scale_amount"] = "1.2"
    s["scale_stat"] = "dmg,crit,aspd"
    d = parse_rules(rules)
    assert (
        d["str"]["cap"] == 10000 and
        d["str"]["scale_stat"][2] == "aspd" and
        d["str"]["scale_amount"] == 1.2
    )


def test_build_stat():
    import configparser
    rules = configparser.ConfigParser()
    rules.read("rules.cfg")
    rules["str"]["scale_method"] = "flat"
    d = parse_rules(rules)
    so = StatsOwner()
    so.load_rules(d)
    s = Stat("str")
    so.add(s)
    s = so.stat_objects["str"]
    assert s.scale_method == s.scale_flat


def test_lvlup():
    owner = StatsOwner()
    owner.lvl = 1
    owner.xp = 0
    owner.load_rules(load_rules_from_file("rules.cfg"))
    owner.award_xp(150)
    assert owner.lvl > 1
