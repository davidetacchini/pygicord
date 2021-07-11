import discord

from pygicord import Paginator
from discord.ext import commands

bot = commands.Bot(command_prefix=".")


def make_embeds():
    pages = []
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


def make_contents():
    return ["Page no. {i}" for i in range(1, 6)]


def make_both():
    pages = []
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = "Embed no. {i}"
        content = "Page no. {i}"
        dict_ = {"content": content, "embed": embed}
        pages.append(dict_)
    return pages


@bot.command()
async def embeds(ctx):
    embeds = make_embeds()
    paginator = Paginator(pages=embeds)
    await paginator.start(ctx)


@bot.command()
async def contents(ctx):
    contents = make_contents()
    paginator = Paginator(pages=contents)
    await paginator.start(ctx)


@bot.command()
async def both(ctx):
    both = make_both()
    paginator = Paginator(pages=both)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
