

class StatError(Exception):
    pass


class StatNotFoundError(StatError):
    pass


class OrphanStatError(StatError):
    pass


class RuleError(Exception):
    pass

