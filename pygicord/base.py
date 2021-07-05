import asyncio

from typing import TYPE_CHECKING, Any, Dict, List, Union, Optional

import discord

from discord.ext import commands

from .exceptions import *

if TYPE_CHECKING:
    from .button import Button

__all__ = ("Base",)


# TODO: review
class _BaseMeta(type):
    def __new__(cls, name, bases, attrs):
        cls_ = super().__new__(cls, name, bases, attrs)
        buttons = []

        for base in reversed(cls_.__mro__):
            for elem, value in base.__dict__.items():
                try:
                    value.__ensure_button__
                except AttributeError:
                    continue
                else:
                    buttons.append(value)

        cls_.__buttons__ = buttons
        return cls_

    def get_buttons(cls):
        buttons = {}
        for button in cls.__buttons__:
            buttons[str(button)] = button
        return buttons


class Base(metaclass=_BaseMeta):
    """Represent the base class for a paginator.

    Inherit from this class whenever you create a paginator.

    Attributes
    ----------
    pages : Union[Any, List[Any]]
        A list of objects to paginate or just one.
    timeout : float
        The timeout to wait before stopping the paginator session.
        Defaults to ``90.0``.

    Note
    ----
    The reactions are automatically added if, and only if, the
    pages length is greater than 1.
    """

    __slots__ = (
        "pages",
        "timeout",
        "ctx",
        "bot",
        "message",
        "_index",
        "_buttons",
        "author",
        "_is_running",
        "__tasks",
        "__lock",
    )

    def __init__(
        self,
        *,
        pages: Union[Any, List[Any]],
        timeout: float = 90.0,
    ):
        self.pages = pages
        self.timeout = timeout

        self.ctx: Optional[commands.Context] = None
        self.bot: Optional[discord.Client] = None
        self.message: Optional[discord.Message] = None

        self._index: int = 0

        # override on startup if should_add_reactions
        self._buttons: Dict[str, "Button"] = {}

        self.author: Optional[discord.Member] = None

        self._is_running: bool = False
        self.__tasks: List[asyncio.Task] = []

        if not isinstance(self.pages, list):
            self.pages = [self.pages]

    def __len__(self):
        """Returns the max number of pages."""
        return len(self.pages)

    @property
    def loop(self):
        """Returns the bot event loop."""
        return self.bot.loop

    @property
    def index(self):
        """Get current page index."""
        return self._index

    @index.setter
    def index(self, index):
        """Set page index."""
        if 0 <= index < len(self):
            self._index = index

    @property
    def buttons(self):
        """Returns the buttons to show in the pagination.

        Hidden buttons are not returned.

        Returns
        -------
        Dict[str, Button]
            A dictionary of Button instances with their
            respective emoji as key.
        """
        sorted_ = sorted(self._buttons.values(), key=lambda b: b.position)
        return {str(b): b for b in sorted_ if b.should_display(self)}

    def _check(self, payload: discord.RawReactionActionEvent):
        return (
            self.author is None
            or payload.user_id == self.author.id
            and payload.message_id == self.message.id
            and str(payload.emoji) in self.buttons
        )

    async def _run(self):
        while self._is_running:
            add = self.bot.wait_for("raw_reaction_add", check=self._check)
            remove = self.bot.wait_for("raw_reaction_remove", check=self._check)
            tasks = [asyncio.ensure_future(add), asyncio.ensure_future(remove)]

            done, pending = await asyncio.wait(
                tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            if len(done) == 0:
                self.stop()
                return

            payload = done.pop().result()
            self.loop.create_task(self.dispatch(payload))

    async def dispatch(self, payload: discord.RawReactionActionEvent):
        """|coro|

        Dispatches a reaction and executes the button's coroutine.

        Parameters
        ----------
        payload : discord.RawReactionActionEvent
            The payload containing all the information needed
            from the button coroutine to work properly.
        """
        emoji = str(payload.emoji)
        button = self.buttons[emoji]
        await button(self, payload)

    def _get_page_kwargs(self, index: int = 0):
        value = self.pages[index]
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"content": None, "embed": value}
        else:
            raise TypeError("Invalid type for pages.")

    def _ensure_permissions(self, permissions):
        if not permissions.send_messages:
            raise CannotSendMessages()

        # TODO: restrictive; maybe refactor
        embed_links = any(isinstance(p, discord.Embed) for p in self.pages)

        if embed_links and not permissions.embed_links:
            raise CannotEmbedLinks()

        if self.should_add_reactions():
            if not permissions.add_reactions:
                raise CannotAddReactions()
            if not permissions.use_external_emojis:
                raise CannotUseExternalEmojis()
            if not permissions.read_message_history:
                raise CannotReadMessageHistory()

    def should_add_reactions(self):
        return len(self) > 1

    async def add_reactions(self):
        for emoji in self.buttons:
            await self.message.add_reaction(emoji)

    async def show_page(self, index: int):
        """|coro|

        Shows a specific page at given index.

        Parameters
        ----------
        index : int
            The the page's index to jump to.
        """
        self.index = index
        kwargs = self._get_page_kwargs(self.index)
        await self.message.edit(**kwargs)

    def stop(self):
        """Stops pagination session."""
        self._is_running = False
        for task in self.__tasks:
            task.cancel()
        self.__tasks.clear()

    async def start(self, ctx: commands.Context):
        """|coro|

        Start pagination session.

        Parameters
        ----------
        ctx : commands.Context
            The invocation context to use.

        Raises
        ------
        PaginationError
            Bot does not have proper permissions.
        TypeError
            Invalid type for pages.
        """
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author
        permissions = ctx.channel.permissions_for(ctx.me)
        self._ensure_permissions(permissions)

        if self.message is None:
            kwargs = self._get_page_kwargs()
            self.message = await ctx.send(**kwargs)

        if self.should_add_reactions():
            self._buttons = self.__class__.get_buttons()
            self._is_running = True
            self.__tasks.append(self.loop.create_task(self._run()))
            self.__tasks.append(self.loop.create_task(self.add_reactions()))
