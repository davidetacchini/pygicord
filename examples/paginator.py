import discord

from pygicord import Paginator
from discord.ext import commands

bot = commands.Bot(command_prefix=".")


def make_pages():
    pages = []
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


@bot.command()
async def test(ctx):
    pages = make_pages()
    paginator = Paginator(pages=pages)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
