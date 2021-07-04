from typing import TYPE_CHECKING, Callable

from discord import RawReactionActionEvent

from .utils import ensure_coroutine

if TYPE_CHECKING:
    from .base import Base

__all__ = ("Button", "button")

CallbackT = Callable[["Base", RawReactionActionEvent], None]


class Button:
    """Represent a Button class for the paginator.

    Consider using :func:button to create a button.

    Attributes
    ----------
    emoji : str
        The emoji to use as the button.
    callback : Callable[[pygicord.Base, discord.RawReactionActionEvent], None]
        A function that is called when the button is pressed.
        Implicitly converted to coroutine if it's not.
    position : int
        The positon of the button. Starts from 0.
    """

    __slots__ = (
        "emoji",
        "callback",
        "position",
        "_display_preds",
        "_invoke_preds",
    )

    # used in Base metaclass to ensure that the value is a button
    __ensure_button__ = ...

    def __init__(self, *, emoji: str, callback: CallbackT, position: int):
        self.emoji = emoji
        self.callback = ensure_coroutine(callback)
        self.position = position

        self._display_preds = []
        self._invoke_preds = []

    def __str__(self):
        return self.emoji

    async def __call__(self, base: "Base", payload: RawReactionActionEvent):
        for pred in self._invoke_preds:
            if not pred(base, payload):
                return
        await self.callback(base, payload)

    def display_if(self, predicate):
        self._display_preds.append(predicate)
        return predicate

    def invoke_if(self, predicate):
        self._invoke_preds.append(predicate)
        return predicate

    def should_display(self, base):
        for pred in self._display_preds:
            if not pred(base):
                return False
        return True


def button(*, emoji: str, position: int):
    """Shorthand decorator for button creation.

    Example
    -------
    class Paginator(Base):
        @button(emoji="\N{BLACK SQUARE FOR STOP}", position=0)
        async def close(self, payload):
            '''stop pagination session.'''
            self.stop()

        @close.invoke_if
        async def close_invoke_if(self, payload):
            '''only the author can invoke it.'''
            return self.ctx.author.id == payload.user_id

    Parameters
    ----------
    emoji : str
        The emoji to use as the button.
    position : int
        The positon of the button. 0-based.
    """

    def decorator(coro):
        return Button(emoji=emoji, callback=coro, position=position)

    return decorator
