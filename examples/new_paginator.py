import discord

from pygicord import Base, StopAction, StopPagination, control
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=intents)


class MyPaginator(Base):
    @control(emoji="\N{BLACK SQUARE FOR STOP}", position=2)
    async def stop(self, payload):
        """Stop pagination."""
        raise StopPagination(StopAction.DELETE_MESSAGE)

    @stop.display_if
    def stop_display_if(self):
        """Only displays when pages are atleast 2."""
        return len(self) > 1

    @stop.invoke_if
    def stop_invoke_if(self, payload):
        """Only the author can stop the session."""
        return self.ctx.author.id == payload.user_id


pages = [f"Page no. {i}" for i in range(1, 6)]


@bot.command()
async def test(ctx):
    paginator = MyPaginator(pages=pages)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
