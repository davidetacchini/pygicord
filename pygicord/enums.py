from enum import Enum

__all__ = ("StopAction", "Config")


class StopAction(Enum):
    DO_NOTHING = 0
    DELETE_MESSAGE = 1
    CLEAR_REACTIONS = 2


class Config(Enum):
    DEFAULT = 1  # controller: first, previous, stop, next, last, input
    MINIMAL = 2  # controller: previous, stop, next
    PLAIN = 3  # controller: first, previous, stop, next
    RICH = 4  # controller: all defaults + lock
