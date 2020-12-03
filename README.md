# Pygicord
<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Lint/badge.svg" alt="Lint">
</a>
<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Deploy/badge.svg" alt="Deploy">
</a>
<a href="https://pypi.org/project/pygicord" traget="_blank">
	<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/pygicord">
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
    # Generate a list of 5 embed instances
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


LOADING_MESSAGE = "Loading reactions..."
FAILED_MESSAGE = "Can't add reactions :("

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
        compact=True,
        timeout=60.0,
        load_message=LOADING_MESSAGE,
        fail_message=FAILED_MESSAGE,
    )
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("I'm ready!")


bot.run("token")
```

## Available attributes
| Attribute    | Description                                                                                                                                     | Type                               | Default | Property |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------- | -------- |
| pages        | A list of embeds you want the paginator to paginate or a discord.Embed instance.                                                                | List[discord.Embed], discord.Embed | None    | No       |
| timeout      | The timeout to wait before stopping the paginator session.                                                                                      | float                              | 90.0    | No       |
| compact      | Whether the paginator should use a compact version of itself having only three reactions: previous, close and next.                             | bool                               | False   | No       |
| indicator    | Whether to display an indicator. It is used to display a message when reactions are loading or when the bot lacks ``Add Reactions`` permission. | bool                               | True    | No       |
| load_message | The message displayed when reactions are loading.                                                                                               | str                                | Custom  | Yes      |
| fail_message | The message displayed when the bot lacks `Add Reactions` permission in the channel.                                                             | str                                | Custom  | Yes      |

## Custom attributes
A list with all the default custom values of the attributes. These values can be overwritten.

### Loading message
```
Adding reactions...
```

### Failed message
```
I can't add reactions in this channel!
Please grant me `Add Reactions` permission.
```