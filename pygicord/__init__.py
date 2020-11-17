"""
MIT License

Copyright (c) 2020 Smyile

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
from typing import Union, Optional
from contextlib import suppress

import discord


class PaginatorException(Exception):
    """Base exception class for Pygicord."""

    pass


class EmptyPages(PaginatorException):
    """Exception raised when trying to paginate an empty list."""

    def __init__(self):
        super().__init__("Can't paginate an empty list.")


class Paginator:
    """A pagination wrapper that allows to move between multiple embeds by using reactions.

    Attributes
    ------------
    pages: Optional[Union[:class:`list`, :class:`discord.Embed`]]
        A list of embeds you want the paginator to paginate.
        Passing a discord.Embed instance will still work as if you are
        using: await ctx.send(embed=embed).
    timeout: :class:`float`.
        The timeout before the paginator's reactions will be cleared.
        Defaults to ``90.0``.
    compact: :class:`bool`.
        Whether the paginator should use a compact version of itself
        having only three reactions: previous, close and next.
        Defaults to ``False``.
    indicator: :class:`bool`
        Whether to display an indicator. It is used to display a message
        when reactions are loading or when the bot lacks ``Add Reactions``
        permission. Defaults to ``True``.
    load_message: :class:`str`
        The message displayed when reactions are loading.
    fail_message: :class:`str`
        The message displayed when the bot can't add reactions in the channel.
    """

    __slots__ = (
        "pages",
        "timeout",
        "compact",
        "indicator",
        "_load_message",
        "_fail_message",
        "embeds",
        "embed",
        "loop",
        "current",
        "previous",
        "end",
        "__tasks",
        "__is_running",
        "__reactions",
    )

    def __init__(
        self,
        *,
        pages: Optional[Union[list[discord.Embed], discord.Embed]] = None,
        compact: bool = False,
        timeout: float = 90.0,
        indicator: bool = True,
        **kwargs,
    ):
        self.pages = pages
        self.compact = compact
        self.timeout = timeout
        self.indicator = indicator

        try:
            load_message = kwargs["load_message"]
        except KeyError:
            pass
        else:
            self.load_message = load_message

        try:
            fail_message = kwargs["fail_message"]
        except KeyError:
            pass
        else:
            self.fail_message = fail_message

        self.embeds = []
        self.embed = None
        self.loop = None
        self.current = 0
        self.previous = 0
        self.end = 0
        self.__tasks = []
        self.__is_running = True
        self.__reactions = {
            "⏮": 0.0,
            "◀": -1,
            "⏹️": "close",
            "▶": +1,
            "⏭": None,
            "🔢": "input",
        }

        if self.pages is not None:
            if len(self.pages) == 2:
                self.compact = True

        if self.compact is True:
            del self.__reactions["⏮"]
            del self.__reactions["⏭"]
            del self.__reactions["🔢"]

    @property
    def load_message(self):
        default = "Adding reactions..."
        return getattr(self, "_load_message", default)

    @load_message.setter
    def load_message(self, value):
        if isinstance(value, str):
            self._load_message = value
        else:
            raise ValueError(
                "load_message must be an instance of <class 'str'> not %s"
                % value.__class__.__name__
            )

    @property
    def fail_message(self):
        default = (
            "I can't add reactions in this channel!\n"
            "Please grant me `Add Reactions` permission."
        )
        return getattr(self, "_fail_message", default)

    @fail_message.setter
    def fail_message(self, value):
        if isinstance(value, str):
            self._fail_message = value
        else:
            raise ValueError(
                "fail_message must be an instance of <class 'str'> not %s"
                % value.__class__.__name__
            )

    def got_to_page(self, number):
        if number > int(self.end) + 1:
            page = int(self.end) + 1
        else:
            page = number
        self.current = page - 1

    async def controller(self, ctx, react):
        if react == "close":
            await self.close_paginator(self.embed)

        elif react == "input":
            to_delete = []
            to_delete.append(
                await ctx.send(
                    f"What page do you want to go to? *Choose between 1 and {int(self.end) + 1}*"
                )
            )

            def check(m):
                return (
                    m.author.id == ctx.author.id
                    and ctx.channel.id == m.channel.id
                    and m.content.isdigit()
                )

            try:
                message = await ctx.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                to_delete.append(
                    await ctx.send("You took too long to choose a number.")
                )
                await asyncio.sleep(5)
            else:
                to_delete.append(message)
                self.got_to_page(int(message.content))

            with suppress(Exception):
                await ctx.channel.delete_messages(to_delete)

        elif isinstance(react, int):
            self.current += react
            if self.current < 0 or self.current > self.end:
                self.current -= react
        else:
            self.current = int(react)

    async def paginator(self, ctx):
        with suppress(discord.HTTPException, discord.Forbidden, IndexError):
            self.embed = await ctx.send(embed=self.embeds[0])

        if len(self.embeds) > 1:
            if self.indicator is True:
                # Adding loading message indicator
                await self.embed.edit(content=self.load_message)
            for reaction in self.__reactions:
                try:
                    await self.embed.add_reaction(reaction)
                except discord.Forbidden:
                    # Can't add reactions
                    if self.indicator is True:
                        await self.embed.edit(content=self.fail_message)
                    return
                except discord.HTTPException:
                    # Failed to add reactions
                    return
            if self.indicator is True:
                # Remove indicator
                await self.embed.edit(content=None)

        def check(r, u):
            if u.id == ctx.bot.user.id:
                return False
            if r.message.id != self.embed.id:
                return False
            elif str(r) not in self.__reactions.keys():
                return False
            elif u.id != ctx.author.id:
                return False
            return True

        while self.__is_running:
            try:
                react, user = await ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await self.close_paginator(self.embed, timed_out=True)

            reaction = self.__reactions.get(str(react))

            with suppress(discord.HTTPException):
                await self.embed.remove_reaction(react, user)

            self.previous = self.current
            await self.controller(ctx, reaction)

            if self.previous == self.current:
                continue

            with suppress(KeyError):
                await self.embed.edit(embed=self.embeds[self.current])

    async def close_paginator(self, message, timed_out=False):
        with suppress(discord.HTTPException, discord.Forbidden):
            if timed_out:
                await message.clear_reactions()
            else:
                await message.delete()

        with suppress(Exception):
            self.__is_running = False
            for task in self.__tasks:
                task.cancel()
            self.__tasks.clear()

    async def paginate(self, ctx):
        """Start paginator session.

        Parameters
        -----------
        ctx: :class:`Context`
            The invocation context to use.
        """
        self.loop = ctx.bot.loop

        if isinstance(self.pages, discord.Embed):
            return await ctx.send(embed=self.pages)

        if self.pages is not None:
            for embed in self.pages:
                if isinstance(embed, discord.Embed):
                    self.embeds.append(embed)

        if self.embeds is None:
            raise EmptyPages()

        self.end = float(len(self.embeds) - 1)
        if self.compact is False:
            self.__reactions["⏭"] = self.end
        self.__tasks.append(self.loop.create_task(self.paginator(ctx)))
