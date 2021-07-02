import asyncio

from typing import Any, List, Union

import discord

from discord.ext import commands

from .exceptions import (
    CannotEmbedLinks,
    CannotAddReactions,
    CannotSendMessages,
    CannotUseExternalEmojis,
    CannotReadMessageHistory,
)

__all__ = ("Paginator",)


class Paginator:
    """An interactive pagination session.

    Attributes
    ----------
    pages: Union[Any, List[Any]]
        A list of elements or just one.
    timeout: float
        The timeout to wait before stopping the paginator session.
        Defaults to ``90.0``.
    is_compact: bool
        Whether to use a compact version. Automatically set to `True`
        whenever the length of the pages are <= 3. Defaults to `False`.
    """

    __slots__ = (
        "pages",
        "timeout",
        "_is_compact",
        "ctx",
        "bot",
        "message",
        "_index",
        "_author",
        "_reactions",
        "_is_running",
        "__tasks",
        "__lock",
    )

    def __init__(
        self,
        *,
        pages: Union[Any, List[Any]],
        is_compact: bool = False,
        timeout: float = 90.0
    ):
        self.pages = pages
        self._is_compact = is_compact
        self.timeout = timeout

        self.ctx = None
        self.bot = None
        self.message = None

        self._index = 0
        self._author = None
        # TODO: add custom emojis
        self._reactions = {
            "⏮": "first",
            "◀": "previous",
            "⏹️": "stop",
            "▶": "next",
            "⏭": "last",
            "🔢": "input",
            "🔒": "lock",
        }

        self._is_running = False
        self.__tasks = []
        self.__lock = asyncio.Lock()

        if not isinstance(self.pages, list):
            self.pages = [self.pages]

    def __len__(self):
        return len(self.pages)

    @property
    def max_pages(self):
        return len(self.pages) - 1

    @property
    def is_compact(self):
        return self._is_compact or len(self) <= 3

    def _prepare_reactions(self):
        if self.is_compact is True:
            keys = ("⏮", "⏭", "🔢")
            for key in keys:
                del self._reactions[key]

    def check(self, payload):
        return (
            self._author is None
            or payload.user_id == self._author.id
            and payload.message_id == self.message.id
            and str(payload.emoji) in self._reactions
        )

    async def _run(self):
        while self._is_running:
            future_add = self.bot.wait_for("raw_reaction_add", check=self.check)
            future_remove = self.bot.wait_for("raw_reaction_remove", check=self.check)
            tasks = [
                asyncio.ensure_future(future_add),
                asyncio.ensure_future(future_remove),
            ]

            done, pending = await asyncio.wait(
                tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            if len(done) == 0:
                return await self.stop()

            payload = done.pop().result()
            self.bot.loop.create_task(self.controller(payload))

    def should_add_reactions(self):
        return len(self) > 1

    async def add_reactions(self):
        for emoji in self._reactions:
            await self.message.add_reaction(emoji)

    def _get_page_kwargs(self, index: int = 0):
        value = self.pages[index]
        if isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"content": None, "embed": value}
        else:
            raise TypeError("Invalid type for pages.")

    async def stop(self):
        self._is_running = False
        for task in self.__tasks:
            task.cancel()
        self.__tasks.clear()

        try:
            await self.message.delete()
        except discord.HTTPException:
            pass

    async def get_input(self):
        if self.__lock.locked():
            return

        async with self.__lock:
            msg = await self.ctx.send(
                "What page do you want to go to?", delete_after=30.0
            )

            def check(m):
                return (
                    self._author is None
                    or m.author.id == self._author.id
                    and m.channel.id == self.ctx.channel.id
                    and m.content.isdigit()
                )

            try:
                message = await self.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await self.ctx.send(
                    "You took too long to enter a number.", delete_after=5.0
                )
            else:
                index = int(message.content) - 1
                if 0 <= index <= self.max_pages:
                    self._index = index
                elif index > self.max_pages:
                    self._index = self.max_pages
            try:
                await msg.delete()
                await message.delete()
            except discord.HTTPException:
                pass

    async def lock_or_unlock(self, user_id):
        if self.__lock.locked():
            return

        # only the author can (un)lock the session
        if self.ctx.author.id != user_id:
            return

        async with self.__lock:
            # guarded from the check before, don't need to check again
            if self._author is None:
                self._author = self.ctx.author
                await self.ctx.send(
                    "Locked. Only you can interact with it.", delete_after=5.0
                )
            else:
                self._author = None
                await self.ctx.send(
                    "Unlocked. Everyone can interact with it.", delete_after=5.0
                )

    async def controller(self, payload):
        fallback = self._index
        control = self._reactions.get(str(payload.emoji))

        if control == "stop":
            return await self.stop()
        elif control == "first":
            self._index = 0
        elif control == "previous":
            self._index -= 1
        elif control == "next":
            self._index += 1
        elif control == "last":
            self._index = self.max_pages
        elif control == "input":
            await self.get_input()
        elif control == "lock":
            await self.lock_or_unlock(payload.user_id)

        if self._index < 0 or self._index > self.max_pages:
            self._index = fallback

        if self._index == fallback:
            return

        kwargs = self._get_page_kwargs(self._index)
        await self.message.edit(**kwargs)

    def _check_permissions(self, permissions):
        if not permissions.send_messages:
            raise CannotSendMessages()

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

    async def start(self, ctx: commands.Context):
        """|coro|

        Start pagination session.

        Parameters
        ----------
        ctx: commands.Context
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
        self._author = ctx.author
        permissions = ctx.channel.permissions_for(ctx.me)
        self._check_permissions(permissions)

        kwargs = self._get_page_kwargs()
        self.message = await ctx.send(**kwargs)

        if self.should_add_reactions():
            self._prepare_reactions()
            self._is_running = True
            self.__tasks.append(self.bot.loop.create_task(self._run()))
            self.__tasks.append(self.bot.loop.create_task(self.add_reactions()))
