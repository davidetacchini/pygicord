from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, Any, List, Union, Mapping, Optional, Sequence

import discord

from discord.ext import commands

from .enums import StopAction
from .control import Control
from .exceptions import *

if TYPE_CHECKING:

    PageT = Union[discord.Embed, str, Sequence[Union[discord.Embed, str]]]

__all__ = ("Base", "StopPagination")


class StopPagination(Exception):
    """Raised to stop a pagination session.

    Attributes
    ----------
    action : StopAction
        A custom cleanup action.
    """

    __slots__ = "action"

    def __init__(self, action: StopAction) -> None:
        self.action = action


class _BaseMeta(type):
    def __new__(cls, name, bases, attrs):
        cls.__controls__: List[Control]  # this fixes generalTypeIssue
        controls = []
        cls_ = super().__new__(cls, name, bases, attrs)

        for base in reversed(cls_.__mro__):
            for elem, value in base.__dict__.items():
                if isinstance(value, Control):
                    controls.append(value)

        cls_.__controls__ = controls
        return cls_

    def get_controller(cls) -> Mapping[str, Control]:
        controller = {}
        for control in cls.__controls__:
            controller[str(control)] = control
        return controller


class Base(metaclass=_BaseMeta):
    """Represent the base class for a paginator.

    Inherit from this class whenever you create a paginator.

    Attributes
    ----------
    pages : Union[discord.Embed, str, Sequence[Union[discord.Embed, str]]]]
        A list of objects to paginate or just one.
    embed_links : bool, default: True
        Whether to check for Embed Links permission as well.
    timeout : float, default: 90.0
        The timeout to wait before stopping the paginator session.

    Note
    ----
    The reactions are automatically added if, and only if, the
    pages length is greater than 1.
    """

    __slots__ = (
        "pages",
        "timeout",
        "embed_links",
        "ctx",
        "bot",
        "message",
        "author",
        "_index",
        "_controller",
        "_is_running",
        "__tasks",
    )

    def __init__(self, *, pages: PageT, embed_links: bool = True, timeout: float = 90.0) -> None:
        if isinstance(pages, (discord.Embed, str)):
            pages = [pages]

        if not len(pages):
            raise ValueError("Cannot paginate an empty list.")

        self.pages = pages
        self.embed_links = embed_links
        self.timeout = timeout

        self.ctx: Optional[commands.Context] = None
        self.bot: Optional[discord.Client] = None
        self.message: Optional[discord.Message] = None
        self.author: Optional[Union[discord.User, discord.Member]] = None

        self._index: int = 0
        self._controller: Mapping[str, Control] = self.__class__.get_controller()

        self._is_running: bool = False
        self.__tasks: List[asyncio.Task] = []

    def __len__(self) -> int:
        """Returns the max number of pages."""
        return len(self.pages)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Returns the bot event loop."""
        return self.bot.loop

    @property
    def index(self) -> int:
        """Get current page index."""
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        """Set page index."""
        if 0 <= index < len(self):
            self._index = index

    @discord.utils.cached_property
    def controller(self) -> Mapping[str, Control]:
        """Get the controller.

        Hidden controls are not included.

        Returns
        -------
        Mapping[str, Control]
            A mapping of control emoji to the Control instance.
        """
        sorted_ = sorted(self._controller.values(), key=lambda c: c.position)
        return {str(c): c for c in sorted_ if c.should_display(self)}

    def _check(self, payload: discord.RawReactionActionEvent) -> bool:
        return (
            self.author is None
            or payload.user_id == self.author.id
            and payload.user_id != self.bot.user.id
            and payload.message_id == self.message.id
            and str(payload.emoji) in self.controller.keys()
        )

    async def _run(self) -> None:
        """|coro|

        Runs the main logic of the pagination.
        """
        try:
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
                    raise StopPagination(StopAction.CLEAR_REACTIONS)

                payload = done.pop().result()
                await self.dispatch(payload)
        except StopPagination as e:
            if e.action == StopAction.DO_NOTHING:
                return
            elif e.action == StopAction.DELETE_MESSAGE:
                try:
                    await self.message.delete()
                except discord.HTTPException:
                    return
            elif e.action == StopAction.CLEAR_REACTIONS:
                try:
                    await self.message.clear_reactions()
                except discord.HTTPException:
                    return
        finally:
            # stop session and cleanup all tasks
            self._is_running = False
            self._tasks_cleanup()

    def _tasks_cleanup(self) -> None:
        for task in self.__tasks:
            task.cancel()
        self.__tasks.clear()

    async def dispatch(self, payload: discord.RawReactionActionEvent) -> None:
        """|coro|

        Dispatches a reaction and executes the control's coroutine.

        Parameters
        ----------
        payload : discord.RawReactionActionEvent
            The payload containing all the information needed
            for the control coroutine to work properly.
        """
        if payload.message_id != self.message.id:
            return

        if self._is_running:
            emoji = str(payload.emoji)
            control = self.controller.get(emoji)
            await control(self, payload)

    def _get_kwargs_from_page(self, index: int = 0) -> dict[str, Any]:
        value = self.pages[index]
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"content": None, "embed": value}
        else:
            raise TypeError("Invalid type for pages.")

    def _ensure_permissions(self, permissions: discord.Permissions) -> None:
        if not permissions.send_messages:
            raise CannotSendMessages()

        if self.embed_links and not permissions.embed_links:
            raise CannotEmbedLinks()

        if self.should_add_reactions():
            if not permissions.add_reactions:
                raise CannotAddReactions()
            if not permissions.use_external_emojis:
                raise CannotUseExternalEmojis()
            if not permissions.read_message_history:
                raise CannotReadMessageHistory()

    def should_add_reactions(self) -> bool:
        return len(self) > 1

    async def add_reactions(self) -> None:
        for emoji in self.controller.keys():
            await self.message.add_reaction(emoji)

    async def show_page(self, index: int) -> None:
        """|coro|

        Shows a specific page at given index.

        Parameters
        ----------
        index : int
            The the page's index to jump to.
        """
        self.index = index
        kwargs = self._get_kwargs_from_page(self.index)
        await self.message.edit(**kwargs)

    async def start(self, ctx: commands.Context) -> None:
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
        ValueError
            Pages is an empty list.
        """
        try:
            del self.controller
        except AttributeError:
            pass

        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author

        if ctx.guild is not None:  # if DMs don't check for permissions
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            self._ensure_permissions(permissions)

        if self.message is None:
            kwargs = self._get_kwargs_from_page()
            self.message = await ctx.send(**kwargs)

        if self.should_add_reactions():
            self._tasks_cleanup()
            self._is_running = True
            self.__tasks.append(self.loop.create_task(self._run()))
            self.__tasks.append(self.loop.create_task(self.add_reactions()))
