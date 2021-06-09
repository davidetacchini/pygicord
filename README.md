# Pygicord
An easy-to-use pagination wrapper for discord.py

<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Lint/badge.svg" alt="Lint">
</a>
<a href="https://github.com/davidetacchini/pygicord/actions" traget="_blank">
	<img src="https://github.com/davidetacchini/pygicord/workflows/Deploy/badge.svg" alt="Deploy">
</a>
<a href="https://pypi.org/project/pygicord" traget="_blank">
   <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pygicord"> 
</a>
<a href="https://pypi.org/project/pygicord" traget="_blank">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/pygicord">
</a>
<a href="https://pepy.tech/project/pygicord" traget="_blank">
	<img alt="PePy - Downloads" src="https://pepy.tech/badge/pygicord">
</a>

## Notes

* Make sure your bot has `Manage Messages` permission to take full advantage from the paginator.
* It is recommended using the latest stable version of <a href="https://discordpy.readthedocs.io/en/stable/">discord.py</a>.

## Installing

```shell
pip install pygicord
```

or via git: to download the latest version available (if not deployed already).

```shell
pip install git+https://github.com/davidetacchini/pygicord
```

## Basic example

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

## Attributes
| Name      | Description                                                                      | Type                               | Default |
| --------- | -------------------------------------------------------------------------------- | ---------------------------------- | ------- |
| pages     | A list of embeds to paginate or an embed instance. 					           | List[discord.Embed], discord.Embed | None    |
| timeout   | The timeout to wait before stopping the paginator session.                       | float                              | 90.0    |
| compact   | Whether to use three reactions: previous, stop and next.  					   | bool                               | False   |
| has_input | Whether to add a reaction to enter a page number to go to.            	       | bool                               | True    |
| has_lock  | Whether to add a reaction to lock/unlock the session to other members.       	   | bool                               | False   |
