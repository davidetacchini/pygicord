import asyncio

from enum import IntFlag

from discord import HTTPException

from .base import Base, StopAction, StopPagination
from .control import control

__all__ = ("Paginator", "Config")


class Config(IntFlag):
    DEFAULT = 0x1  # controller: first, previous, stop, next, last, input
    MINIMAL = 0x2  # controller: previous, stop, next
    PLAIN = 0x4  # controller: first, previous, stop, next
    RICH = 0x8  # controller: all defaults + lock


class Paginator(Base):
    """The default implementation of the Base class.

    Attributes
    ----------
    pages : Union[Any, List[Any]]
        A list of objects to paginate or just one.
    timeout : float, default: 90.0
        The timeout to wait before stopping the paginator session.
    emojis : Union[list, tuple]
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
        self, *, config: Config = Config.DEFAULT, force_lock: bool = False, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.force_lock = force_lock

    @control(emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}", position=0)
    async def first_page(self, payload):
        """Go to first page."""
        await self.show_page(0)

    @first_page.display_if
    def first_page_display_if(self):
        """Only displays when the pages are atleast 4."""
        return len(self) > 3 and self.config ^ Config.MINIMAL

    @control(emoji="\N{BLACK LEFT-POINTING TRIANGLE}", position=1)
    async def previous(self, payload):
        """Go to previous page."""
        await self.show_page(self.index - 1)

    @control(emoji="\N{BLACK SQUARE FOR STOP}", position=2)
    async def stop(self, payload):
        """Stop pagination session."""
        raise StopPagination(StopAction.DELETE_MESSAGE)

    @control(emoji="\N{BLACK RIGHT-POINTING TRIANGLE}", position=3)
    async def next(self, payload):
        """Go to next page."""
        await self.show_page(self.index + 1)

    @control(emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}", position=4)
    async def last_page(self, payload):
        """Go to last page."""
        await self.show_page(len(self) - 1)

    @last_page.display_if
    def last_page_display_if(self):
        """Only displays when the pages are atleast 4."""
        return len(self) > 3 and self.config ^ Config.MINIMAL

    @control(emoji="\N{INPUT SYMBOL FOR NUMBERS}", position=5)
    async def input_number(self, payload):
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
                await message.delete()
            except HTTPException:
                pass

    @input_number.display_if
    def input_number_display_if(self):
        """Only displays when the pages are atleast 4."""
        return (
            len(self) > 3 and self.config & Config.DEFAULT or self.config & Config.RICH
        )

    @control(emoji="\N{LOCK}", position=6)
    async def lock_unlock(self, payload):
        """Allows other members to interact with the paginator."""
        lock = self.__dict__.setdefault("lock", asyncio.Lock())

        # prevent spamming
        if lock.locked():
            return

        async with lock:
            if self.author is None:
                self.author = self.ctx.author
                await self.ctx.send(
                    "Locked. Only you can interact with it.", delete_after=5.0
                )
            else:
                self.author = None
                await self.ctx.send(
                    "Unlocked. Everyone can interact with it.", delete_after=5.0
                )

    @lock_unlock.display_if
    def lock_unlock_display_if(self):
        """Hide in DMs."""
        return (
            self.ctx.guild is not None and self.force_lock or self.config & Config.RICH
        )

    @lock_unlock.invoke_if
    def lock_unlock_invoke_if(self, payload):
        """Only the author can invoke this."""
        return self.ctx.author.id == payload.user_id
