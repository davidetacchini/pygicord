import discord

from pygicord import Paginator
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=intents)

# Supported emojis format:
# Emoji: "🚀" <-- this format is not recommended, use it at your own risk
# Unicode: "\U0001F680"
# Unicode name: "\N{ROCKET}"
# Custom emoji: ":custom_emoji:123456"

custom_emojis = {
    "\U000023EA": "\U000021A9",
    "\U000025C0": "\U00002B05",
    "\U000023F9": "\U0000274C",
    "\U000025B6": "\U000027A1",
    "\U000023E9": "\U000021AA",
    "\U0001F522": "\U0001F504",
    "\U0001F512": "\U0001F465",
}

# from -> to
# ⏪ -> ↩️
# ◀️  -> ⬅️
# ⏹️ -> ❌
# ▶️  -> ➡️
# ⏩ -> ↪️
# 🔢 -> 🔄
# 🔒 -> 👥

pages = [f"Page no. {i}" for i in range(1, 6)]


@bot.command()
async def test(ctx):
    paginator = Paginator(pages=pages, emojis=custom_emojis)
    await paginator.start(ctx)


# to avoid passing custom_emojis everytime:
class MyPaginator(Paginator):
    def __init__(self, **kwargs):
        super().__init__(emojis=custom_emojis, **kwargs)


# then:
@bot.command()
async def test2(ctx):
    paginator = MyPaginator(pages=pages)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
