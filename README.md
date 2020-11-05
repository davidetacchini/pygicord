# Pygicord
<img src="https://github.com/davidetacchini/pygicord/workflows/CI/badge.svg" alt="Build">

An easy-to-use pagination wrapper for discord.py library.

## Installing

```shell
pip install pygicord
```

## Getting started

The following examples help you understand how pygicord works.

### Basic paginator:

```py
import discord
from discord.ext import commands

from pygicord import Paginator

bot = commands.Bot(command_prefix=".")


def make_pages():
    pages = []
    # Generate a list of 5 embeds
    for i in range(1, 6):
        embed = discord.Embed()
        embed.color = discord.Color.blurple()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


@bot.command()
async def test(ctx):
    paginator = Paginator(pages=make_pages())
    await paginator.paginate(ctx)


@bot.event
async def on_ready():
    print("I'm ready!")


bot.run("token")
```

### Customized paginator:

```py
import discord
from discord.ext import commands

from pygicord import Paginator

bot = commands.Bot(command_prefix=".")
LOADING_MESSAGE = "Loading reactions..."
FAILED_MESSAGE = "Can't add reactions :("


def make_pages():
    pages = []
    for i in range(1, 6):
        embed = discord.Embed()
        embed.color = discord.Color.blurple()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


def new_help_embed():
    embed = discord.Embed()
    embed.color = discord.Color.green()
    embed.title = "I'm the new help embed!"
    return embed


@bot.command()
async def test(ctx):
    async with ctx.typing():
        paginator = Paginator(
            pages=make_pages(),
            compact=True,
            has_help=False,
            load_message=LOADING_MESSAGE,
            fail_message=FAILED_MESSAGE,
            help_embed=new_help_embed(),
        )
        await paginator.paginate(ctx)


@bot.event
async def on_ready():
    print("I'm ready!")


bot.run("token")
```

## Available attributes

| Attribute       | Description                                                                                                                         | Type                | Default | Property |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------- | -------- |
| pages           | A list of embeds you want the paginator to paginate or a discord.Embed instance.                                                    | list, discord.Embed | None    | No       |
| timeout         | The timeout before the paginator's reactions will be cleared.                                                                       | float               | 90.0    | No       |
| compact         | Whether the paginator should use a compact version of itself having only three reactions: previous, close and next.                 | bool                | False   | No       |
| go_back_timeout | The amount of seconds that redirects to the previously visited page when using :attr:`help_embed` section.                          | float               | 30.0    | No       |
| indicator       | Whether to display an indicator. It is used to display a message when reactions are loading or when the bot lacks ``Add Reactions`` | bool                | True    | No       |
| load_message    | The message displayed when reactions are loading.                                                                                   | str                 | Custom  | Yes      |
| fail_message    | The message displayed when the bot can't add reactions in the channel.                                                              | str                 | Custom  | Yes      |
| has_help        | Whether to add a new reaction for the help section.                                                                                 | bool                | True    | No       |
| help_embed      | A custom embed for the paginator help section.                                                                                      | discord.Embed       | Custom  | Yes      |

## Custom attributes
A list with all the default values of the attributes. These values can be overwritten.

### Help embed

```py
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
```

### Loading message
```
**Adding reactions**
```

### Failed message
```
**I can't add reactions in this channel!
Please grant me `Add Reactions` permission.**
```