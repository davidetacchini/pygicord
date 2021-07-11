import discord

from pygicord import Paginator, control
from discord.ext import commands

bot = commands.Bot(command_prefix=".")


class CustomPaginator(Paginator):

    # Adds a new control to the paginator.
    # Position 4.5 means that it will be placed before
    # the input_numbers emojis, which comes in position 5.
    @control(emoji="\N{INFORMATION SOURCE}", position=4.5)
    async def show_info(self, payload):
        """Shows this message."""
        desc = []
        for emoji, control_ in self.controller.items():
            desc.append(f"{emoji}: {control_.callback.__doc__}")
        embed = discord.Embed()
        embed.description = "\n".join(desc)
        embed.set_footer(text="Press any reaction to go back.")
        await self.message.edit(content=None, embed=embed)


pages = [f"Page no. {i}" for i in range(1, 6)]


@bot.command()
async def test(ctx):
    paginator = CustomPaginator(pages=pages)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
