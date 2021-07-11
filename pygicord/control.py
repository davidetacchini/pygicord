from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Callable

from .utils import ensure_coroutine

if TYPE_CHECKING:
    from discord import RawReactionActionEvent

    from .base import Base

    DisplayPredicate = Callable[[Base], bool]
    InvokePredicate = Callable[[Base, RawReactionActionEvent], bool]

__all__ = ("Control", "control")


class Control:
    """Represent an abstract Control class.

    Consider using :func:`control` to create a control.

    Attributes
    ----------
    emoji : str
        The emoji to use as the control.
    callback : Callable[[pygicord.Base, discord.RawReactionActionEvent], None]
        A function that is called when the control is pressed.
        Implicitly converted to coroutine if it's not.
    position : Union[int, float]
        The positon of the control. Starts from 0.
    """

    __slots__ = (
        "emoji",
        "callback",
        "position",
        "_display_preds",
        "_invoke_preds",
    )

    # used in Base metaclass to ensure that the value is a control
    __ensure_control__ = ...

    def __init__(
        self,
        *,
        emoji: str,
        callback: Callable[[Base, RawReactionActionEvent], None],
        position: Union[int, float]
    ) -> None:
        self.emoji = emoji
        self.callback = ensure_coroutine(callback)
        self.position = position

        self._display_preds: List[DisplayPredicate] = []
        self._invoke_preds: List[InvokePredicate] = []

    def __str__(self) -> str:
        """Returns the control emoji."""
        return self.emoji

    async def __call__(self, base: Base, payload: RawReactionActionEvent) -> None:
        """|coro|

        Calls the internal control callback.
        """
        for pred in self._invoke_preds:
            if not pred(base, payload):
                return
        await self.callback(base, payload)

    def display_if(self, predicate: DisplayPredicate) -> DisplayPredicate:
        """A decorator that registers a predicate that
        determine whether the control should be displayed.
        """
        self._display_preds.append(predicate)
        return predicate

    def invoke_if(self, predicate: InvokePredicate) -> InvokePredicate:
        """A decorator that registers a predicate that
        determine whether the control should be invoked.
        """
        self._invoke_preds.append(predicate)
        return predicate

    def should_display(self, base: Base) -> bool:
        """Returns whether a control should be displayed."""
        for pred in self._display_preds:
            if not pred(base):
                return False
        return True


def control(*, emoji: str, position: Union[int, float]):
    """Shorthand decorator for control creation.

    Supported emojis formats:
        - Emoji: "🚀" (not recommended)
        - Unicode: "\U0001F680"
        - Unicode name: "\N{ROCKET}"
        - Custom emoji: ":custom_emoji:123456"

    Parameters
    ----------
    emoji : str
        The emoji to use as the control.
    position : Union[int, float]
        The positon of the control. 0-based.

    Example
    -------
    class Paginator(Base):
        @control(emoji="\N{BLACK SQUARE FOR STOP}", position=0)
        async def stop(self, payload):
            '''Stop pagination.'''
            self.stop()

        @stop.invoke_if
        async def stop_invoke_if(self, payload):
            '''Only the author can invoke it.'''
            return self.ctx.author.id == payload.user_id
    """

    def decorator(coro):
        return Control(emoji=emoji, callback=coro, position=position)

    return decorator
