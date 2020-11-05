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
    go_back_timeout: :class:`float`
        The amount of seconds that redirects to the previously visited page
        when using :attr:`help_embed` section.
        Defaults to ``30.0``.
    indicator: :class:`bool`
        Whether to display an indicator. It is used to display a message
        when reactions are loading or when the bot lacks ``Add Reactions``
        permission. Defaults to ``True``.
    load_message: :class:`str`
        The message displayed when reactions are loading.
    fail_message: :class:`str`
        The message displayed when the bot can't add reactions in the channel.
    has_help: :class:`bool`
        Whether to add a new reaction for the help section.
        Defaults to ``True``.
    help_embed: Optional[:class:`discord.Embed`]
        A custom embed for the paginator help section.
    """

    __slots__ = (
        "pages",
        "timeout",
        "compact",
        "go_back_timeout",
        "indicator",
        "_load_message",
        "_fail_message",
        "has_help",
        "_help_embed",
        "embeds",
        "embed",
        "loop",
        "current",
        "previous",
        "end",
        "__pagination",
        "__timed_out",
        "__reactions",
    )

    def __init__(
        self,
        *,
        pages: Optional[Union[list, discord.Embed]] = None,
        compact: bool = False,
        timeout: float = 90.0,
        go_back_timeout: float = 30.0,
        indicator: bool = True,
        has_help: bool = True,
        **kwargs
    ):
        self.pages = pages
        self.compact = compact
        self.timeout = timeout
        self.go_back_timeout = go_back_timeout
        self.indicator = indicator
        self.has_help = has_help

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

        try:
            help_embed = kwargs["help_embed"]
        except KeyError:
            pass
        else:
            self.help_embed = help_embed

        self.embeds = []
        self.embed = None
        self.loop = None
        self.current = 0
        self.previous = 0
        self.end = 0
        self.__pagination = None
        self.__timed_out = False
        self.__reactions = {
            "⏮": 0.0,
            "◀": -1,
            "⏹️": "close",
            "▶": +1,
            "⏭": None,
            "❔": "help",
        }

        if self.compact is True:
            del self.__reactions["⏮"]
            del self.__reactions["⏭"]

        if self.has_help is False:
            del self.__reactions["❔"]

    @property
    def load_message(self):
        default = "**Adding reactions...**"
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

    def default_help_embed(self):
        embed = discord.Embed(color=discord.Colour.blurple())
        embed.title = "Paginator Help"
        embed.description = "Welcome to the paginator help!"
        reactions_help = (
            "⏮: Go to the first page\n"
            "◀: Go to the previous page\n"
            "⏹️: Close the paginator\n"
            "▶: Go to the next page\n"
            "⏭: Go to the last page\n"
            "❔: Shows this page"
        )
        embed.add_field(name="Reactions", value=reactions_help)
        return embed

    @property
    def help_embed(self):
        default = self.default_help_embed()
        return getattr(self, "_help_embed", default)

    @help_embed.setter
    def help_embed(self, value):
        if isinstance(value, discord.Embed):
            self._help_embed = value
        else:
            raise ValueError(
                "help_embed must be an instance of <class 'discord.Embed'> not %s"
                % value.__class__.__name__
            )

    async def go_back(self):
        await asyncio.sleep(self.go_back_timeout)
        with suppress(discord.HTTPException, discord.NotFound):
            await self.embed.edit(embed=self.embeds[self.current])

    async def reference(self, ctx, react):
        if react == "close":
            self.loop.create_task(self.close_paginator(self.embed))

        elif react == "help":
            await self.embed.edit(embed=self.help_embed)
            self.loop.create_task(self.go_back())

        elif isinstance(react, int):
            self.current += react
            if self.current < 0 or self.current > self.end:
                self.current -= react
        else:
            self.current = int(react)

    async def paginator(self, ctx):
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
                # Remove loading message after every reaction has been added
                await self.embed.edit(content=None)

        def check(r, u):
            if u.id == ctx.bot.user.id or r.message.id != self.embed.id:
                return False
            elif str(r) not in self.__reactions.keys():
                return False
            elif u.id != ctx.author.id:
                return False
            return True

        while True:
            try:
                react, user = await ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                self.__timed_out = True
                return self.loop.create_task(self.close_paginator(self.embed))

            reaction = self.__reactions.get(str(react))

            with suppress(discord.HTTPException):
                await self.embed.remove_reaction(react, user)

            self.previous = self.current
            await self.reference(ctx, reaction)

            if self.previous == self.current:
                continue

            with suppress(KeyError):
                await self.embed.edit(embed=self.embeds[self.current])

    async def close_paginator(self, message):
        with suppress(discord.HTTPException, discord.Forbidden):
            if self.__timed_out:
                await message.clear_reactions()
            else:
                await message.delete()

        with suppress(Exception):
            self.__pagination.cancel()

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
        self.__pagination = self.loop.create_task(self.paginator(ctx))
