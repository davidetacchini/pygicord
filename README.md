# Pygicord
<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Lint/badge.svg" alt="Lint">
</a>
<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Deploy/badge.svg" alt="Deploy">
</a>
<a href="https://pypi.org/project/pygicord" traget="_blank">
	<img alt="PyPI - Downloads" src="https://pepy.tech/badge/pygicord">
</a>
<a href="https://pypi.org/project/pygicord" traget="_blank">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/pygicord">
</a>

An easy-to-use pagination wrapper for discord.py

## Installing

```shell
pip install pygicord
```

## Getting started

The following examples help you understand how pygicord works.

### Basic paginator

```py
import discord
from discord.ext import commands

from pygicord import Paginator


bot = commands.Bot(command_prefix=".")


def get_pages():
    pages = []
    # Generate a list of 5 embeds
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


@bot.command()
async def test(ctx):
    paginator = Paginator(pages=get_pages())
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("I'm ready!")


bot.run("token")
```

### Custom paginator

```py
import discord
from discord.ext import commands

from pygicord import Paginator


bot = commands.Bot(command_prefix=".")


def get_pages():
    pages = []
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages


@bot.command()
async def test(ctx):
    paginator = Paginator(
        pages=get_pages(),
        timeout=60.0,
        has_input=False,
    )
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("I'm ready!")


bot.run("token")
```

## Attributes
| Name      | Description                                                                      | Type                               | Default |
| --------- | -------------------------------------------------------------------------------- | ---------------------------------- | ------- |
| pages     | A list of embeds you want the paginator to paginate or a discord.Embed instance. | List[discord.Embed], discord.Embed | None    |
| timeout   | The timeout to wait before stopping the paginator session.                       | float                              | 90.0    |
| compact   | Whether the paginator should only use three reactions: previous, stop and next.  | bool                               | False   |
| has_input | Whether the paginator should add a reaction for taking input numbers.            | bool                               | True    |