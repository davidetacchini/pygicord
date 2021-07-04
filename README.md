# Pygicord
An easy-to-use feature-rich pagination wrapper for discord.py

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

* It is recommended using the latest stable version of <a href="https://discordpy.readthedocs.io/en/stable/">discord.py</a>.

## Installing

```shell
pip install pygicord
```

or via git:

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
    for i in range(1, 6):
        embed = discord.Embed()
        embed.title = f"Embed no. {i}"
        pages.append(embed)
    return pages


@bot.command()
async def test(ctx):
    pages = get_pages()
    paginator = Paginator(pages=pages)
    await paginator.start(ctx)


@bot.event
async def on_ready():
    print("Ready!")


bot.run("token")
```

## Attributes

| Name    | Description                                                | Type                  | Default |
|---------|------------------------------------------------------------|-----------------------|---------|
| pages   | A list of objects to paginate or just one.                 | Union[Any, List[Any]] | /       |
| timeout | The timeout to wait before stopping the paginator session. | float                 | 90.0    |
