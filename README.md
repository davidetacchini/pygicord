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

## Attributes

| Name       | Description                                                | Type                  | Default        |
|------------|------------------------------------------------------------|-----------------------|----------------|
| pages      | A list of objects to paginate or just one.                 | Union[Any, List[Any]] | /              |
| timeout    | The timeout to wait before stopping the paginator session. | float                 | 90.0           |
| emojis     | The custom emojis to use.                                  | Union[list, tuple]    | /              |
| config     | The configuration to use.                                  | pygicord.Config       | Config.DEFAULT |
| force_lock | Whether to force adding the lock.                          | bool                  | False          |

## Config

| Type           | Buttons                                        |
|----------------|------------------------------------------------|
| Config.DEFAULT | first, previous, stop, next, last, input       |
| Config.MINIMAL |        previous, stop, next                    |
| Config.PLAIN   | first, previous, stop, next, last              |
| Config.RICH    | first, previous, stop, next, last, input, lock |

### Note

Config.RICH is the only config to have the lock set by default. You must set `force_lock` to True if you want to add it to all other configurations.

### Example

```py
from pygicord import Config, Paginator

@bot.command()
async def test(ctx):
	paginator = Paginator(pages=pages, config=Config.MINIMAL)
	await paginator.start(ctx)
```

## Custom Emojis

### Note

Emojis must be passed in their respective order. The order is computed by the position of the control in the controller.

```py
from pygicord import Paginator

# this will only change the "stop" emoji
custom_emojis = (None, None, "\N{ROCKET}", None, None, None, None)

@bot.command
async def test(ctx):
	paginator = Paginator(pages=pages, emojis=custom_emojis)
	await paginator.start(ctx)
```

To only change one or few emojis, you must set others to None.

## Custom Paginator

```py
from pygicord import Base, StopAction, StopPagination, control

class MyPaginator(Base):

    @control(emoji="\N{ROCKET}", position=0)
    async def stop(self, payload):
		"""Stops pagination."""
        raise StopPagination(StopAction.DELETE_MESSAGE)

    @stop.invoke_if
    def stop_invoke_if(self, payload):
        """Invocable only from the author."""
        return self.ctx.author.id == payload.user_id
```

Then, when you want to use it:

```py
pages = ["Page no. 1", "Page no. 2"]

@bot.command()
async def test(ctx):
    paginator = MyPaginator(pages=pages)
    await paginator.start(ctx)
```
