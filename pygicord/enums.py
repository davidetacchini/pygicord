from enum import IntFlag

__all__ = ("StopAction", "Config")


class StopAction(IntFlag):
    DO_NOTHING = 0x0
    DELETE_MESSAGE = 0x1
    CLEAR_REACTIONS = 0x2


class Config(IntFlag):
    DEFAULT = 0x1  # controller: first, previous, stop, next, last, input
    MINIMAL = 0x2  # controller: previous, stop, next
    PLAIN = 0x4  # controller: first, previous, stop, next
    RICH = 0x8  # controller: all defaults + lock
