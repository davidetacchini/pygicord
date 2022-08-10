from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, Any, Mapping, Optional

from discord import HTTPException
from discord.utils import cached_property

from .base import Base, StopAction, StopPagination
from .enums import Config
from .control import control

if TYPE_CHECKING:
    from .control import Control

__all__ = ("Paginator",)


class Paginator(Base):
    """The default implementation of the Base class.

    Attributes
    ----------
    pages : Union[Any, List[Any]]
        A list of objects to paginate or just one.
    timeout : float, default: 90.0
        The timeout to wait before stopping the paginator session.
    emojis : dict
        The custom emojis to use.
    config : Config, default: Config.DEFAULT
        The configuration to use.
    force_lock : bool, default: False
        Whether to force adding the lock. By default
        it's added only when using Config.RICH.

    Note
    ----
    The reactions are automatically added if, and only if, the
    pages length is greater than 1.
    """

    def __init__(
        self,
        *,
        emojis: Optional[Mapping[str, str]] = None,
        config: Config = Config.DEFAULT,
        force_lock: bool = False,
        **kwargs: Any,
    ) -> None:
        self.emojis = emojis
        self.config = config
        self.force_lock = force_lock
        super().__init__(**kwargs)

    @cached_property
    def controller(self) -> Mapping[str, Control]:
        """Override base controller property to use custom_emojis (if any)."""
        if self.emojis:
            for old, new in self.emojis.items():
                try:
                    self._controller[old].emoji = new
                except KeyError:
                    pass
        sorted_ = sorted(self._controller.values(), key=lambda c: c.position)
        return {str(c): c for c in sorted_ if c.should_display(self)}

    @control(emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}", position=0)
    async def first_page(self, payload) -> None:
        """Go to first page."""
        await self.show_page(0)

    @first_page.display_if
    def first_page_display_if(self) -> bool:
        """Only displays when the pages are atleast 4."""
        return len(self) > 3 and self.config != Config.MINIMAL

    @control(emoji="\N{BLACK LEFT-POINTING TRIANGLE}", position=1)
    async def previous(self, payload) -> None:
        """Go to previous page."""
        await self.show_page(self.index - 1)

    @control(emoji="\N{BLACK SQUARE FOR STOP}", position=2)
    async def stop(self, payload) -> None:
        """Stop pagination."""
        raise StopPagination(StopAction.DELETE_MESSAGE)

    @stop.invoke_if
    def stop_invoke_if(self, payload) -> bool:
        """Only the author can stop the session."""
        return self.ctx.author.id == payload.user_id

    @control(emoji="\N{BLACK RIGHT-POINTING TRIANGLE}", position=3)
    async def next(self, payload) -> None:
        """Go to next page."""
        await self.show_page(self.index + 1)

    @control(emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}", position=4)
    async def last_page(self, payload) -> None:
        """Go to last page."""
        await self.show_page(len(self) - 1)

    @last_page.display_if
    def last_page_display_if(self) -> bool:
        """Only displays when the pages are atleast 4."""
        return len(self) > 3 and self.config != Config.MINIMAL

    @control(emoji="\N{INPUT SYMBOL FOR NUMBERS}", position=5)
    async def input_number(self, payload) -> None:
        """Enter a page number to jump to."""
        lock = self.__dict__.setdefault("lock", asyncio.Lock())

        # prevent spamming
        if lock.locked():
            return

        async with lock:
            prompt = await self.ctx.send("What page do you want to go to?")

            def check(m):
                return (
                    self.author is None
                    or m.author.id == self.author.id
                    and m.channel.id == self.ctx.channel.id
                    and m.content.isdigit()
                )

            try:
                message = await self.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await self.ctx.send("Took too long.", delete_after=5.0)
            else:
                index = int(message.content) - 1
                # jump to the last page if the index is
                # greater than the maximum pages. UX purpose
                index = index if index < len(self) else len(self) - 1
                await self.show_page(index)
            try:
                await prompt.delete()
                await message.delete()  # type: ignore # here the message will always be bound
            except (HTTPException, UnboundLocalError):
                pass

    @input_number.display_if
    def input_number_display_if(self) -> bool:
        """Only displays when the pages are atleast 4."""
        return len(self) > 3 and self.config == Config.DEFAULT or self.config == Config.RICH

    @control(emoji="\N{LOCK}", position=6)
    async def lock_unlock(self, payload) -> None:
        """Allows other members to interact with the paginator."""
        lock = self.__dict__.setdefault("lock", asyncio.Lock())

        # prevent spamming
        if lock.locked():
            return

        async with lock:
            if self.author is None:
                self.author = self.ctx.author
                await self.ctx.send("Locked. Only you can interact with it.", delete_after=5.0)
            else:
                self.author = None
                await self.ctx.send("Unlocked. Everyone can interact with it.", delete_after=5.0)

    @lock_unlock.display_if
    def lock_unlock_display_if(self) -> bool:
        """Hide in DMs."""
        return self.ctx.guild is not None and self.force_lock or self.config == Config.RICH

    @lock_unlock.invoke_if
    def lock_unlock_invoke_if(self, payload) -> bool:
        """Only the author can invoke this."""
        return self.ctx.author.id == payload.user_id
