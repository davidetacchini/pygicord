from enum import Enum

__all__ = ("StopAction", "Config")


class StopAction(Enum):
    DO_NOTHING = 0
    DELETE_MESSAGE = 1
    CLEAR_REACTIONS = 2


class Config(Enum):
    DEFAULT = 0  # controller: first, previous, stop, next, last, input
    MINIMAL = 1  # controller: previous, stop, next
    PLAIN = 2  # controller: first, previous, stop, next
    RICH = 3  # controller: all defaults + lock
