from enum import Enum, auto


class ProxyStrategy(Enum):
    IF_ZERO_APPROVALS_NEEDED = auto()
    NEVER = auto()
    ALWAYS = auto()
