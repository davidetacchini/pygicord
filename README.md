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

## Contents
* [Installing](#installing)
* [Getting Started](#getting-started)
* [Basic Paginator](#basic-paginator)
* [Attributes](#attributes)
* [Custom Emojis](#custom-emojis)
* [Configuration](#configuration)
* [Custom Paginator](#custom-paginator)
* [New Paginator](#new-paginator)

## Installing

```shell
pip install pygicord
```

or via git:

```shell
pip install git+https://github.com/davidetacchini/pygicord
```

### Note

It is recommended using the latest stable version of <a href="https://discordpy.readthedocs.io/en/stable/">discord.py</a>.

## Getting Started

### Basic Paginator

```py
from pygicord import Paginator

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
```

### Attributes

| Name       | Description                                                 | Type                  | Default         |
|------------|-------------------------------------------------------------|-----------------------|-----------------|
| pages      | A list of objects to paginate or just one.                  | Union[Any, List[Any]] |                 |
| timeout    | The timeout to wait before stopping the pagination session. | float                 | 90.0            |
| emojis     | The custom emojis to use.                                   | dict                  | Discord natives |
| config     | The configuration to use.                                   | pygicord.Config       | Config.DEFAULT  |
| force_lock | Whether to force adding the lock.                           | bool                  | False           |

Supported emojis formats:
* Emoji: "🚀" (not recommended)
* Unicode: "\U0001F680"
* Unicode name: "\N{ROCKET}"
* Custom emoji: ":custom_emoji:123456"

### Custom Emojis

```py
from pygicord import Paginator

# copy this and replace the values.
custom_emojis = { 
    "\U000023EA": "REPLACE (first page)",
    "\U000025C0": "REPLACE (previous page)",
    "\U000023F9": "REPLACE (stop session)",
    "\U000025B6": "REPLACE (next page)",
    "\U000023E9": "REPLACE (last page)",
    "\U0001F522": "REPLACE (input numbers)",
    "\U0001F512": "REPLACE (lock unlock)",
}


@bot.command
async def test(ctx):
    paginator = Paginator(pages=pages, emojis=custom_emojis)
    await paginator.start(ctx)
```

### Configuration

Config.RICH is the only config to have the lock set by default.
You must set `force_lock` to True if you want to add it to all other configurations.

| Type           | Buttons                                        |
|----------------|------------------------------------------------|
| Config.DEFAULT | first, previous, stop, next, last, input       |
| Config.MINIMAL |        previous, stop, next                    |
| Config.PLAIN   | first, previous, stop, next, last              |
| Config.RICH    | first, previous, stop, next, last, input, lock |

```py
from pygicord import Config, Paginator


@bot.command()
async def test(ctx):
    paginator = Paginator(pages=pages, config=Config.MINIMAL)
    await paginator.start(ctx)
```

### Custom Paginator

```py
from pygicord import Paginator, control


class CustomPaginator(Paginator):
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
```

### New Paginator

```py
from pygicord import Base, StopAction, StopPagination, control


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
```
