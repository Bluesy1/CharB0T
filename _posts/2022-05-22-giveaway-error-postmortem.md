---
layout: post
title:  "What went wrong with the giveaway?"
date:   2022-05-22 08:30:00 -0700
categories: postmortem
tags: giveaway mistake error postmortem
author:  Bluesy
excerpt_separator: <!--more-->
---

When reloading the giveaway module after updating the `/confirm` command yesterday to allow
setting the number of days to confirm for, I accidentally de-linked the giveaway from any code references, causing
it to not be automatically ended from the timer. This postmortem is to help me figure out what went wrong, and how
to avoid this happening again.

<!--more-->

# What happened?

Normally, when I need to reload the giveaway module, I use [Jishaku] to store the giveaway in a local [REPL] session 
in the bot that maintains the variables passed to it, and then reload the module. I thought this would be a good way to
avoid the issue, but it turns out that this method is prone to errors, and the error is not always obvious, until it is
too late. The process is as follows:
1. The current and past giveaways are stored in the bot's [REPL] session:

```markdown
!jsk py
current = _bot.get_cog("Giveaway").current_giveaway
yesterday = _bot.get_cog("Giveaway").yesterdays_giveaway
```

2. I reload the module:

```markdown
!jsk reload giveaway
```

3. The current and past giveaways are loaded from the bot's [REPL] session:

```markdown
!jsk py
_bot.get_cog("Giveaway").current_giveaway = current
_bot.get_cog("Giveaway").yesterdays_giveaway = yesterday
```

Now, most of the time, this works, and the giveaway is reloaded. However, when the error occurs, the error is not
obvious until it is too late and the giveaway is reloaded, de-linking the Giveaway View (the buttons and embed that are
the giveaway's interface) from the code that is handling the giveaway task.

# What went wrong?

I think, and I have no way to confirm this, that when I went to do step 2, because I initially got a syntax error I had
to fix and after I fixed that I forgot to confirm I copied in the correct references to the [REPL] session, so when I 
reloaded the module and tried to load the giveaway from the [REPL] session, I lost the giveaway and loaded in `...`
ellipses placeholders instead.

# How am I going to fix this and prevent it from happening again?

First, I am going to remove all other commands and code not required for the giveaway view and task from the module.
This will prevent the giveaway module from having to be reloaded as often, limit chances for failure. Second, I am
going to store the giveaways in a bot variable during reloading automatically instead of a cog variable
to make the state of the giveaway not based off of a [REPL] session. This will make it easier to reload the module 
without losing the giveaway. Finally, I'm going to add a [Class Method] as a Factory Method to the GiveawayView
class to allow me to reconstruct a giveaway easier from a channel and message ID should a giveaway be lost in the
future.

## How do I do this?

### The mentioned class/factory method
```python
class GiveawayView:
	...
    @classmethod
    def recreate_from_message(cls, message: discord.Message, bot: CBot):
        try:
            embed = message.embeds[0]
            game = embed.title
            url = embed.url
            channel = message.channel
            assert isinstance(channel, discord.TextChannel)
            assert isinstance(game, str)
            view = cls(bot, channel, embed, game, url)
            view.message = message
            bid = embed.fields[4].value
            assert isinstance(bid, str)
            view.top_bid = int(bid)
            total = embed.fields[3].value
            assert isinstance(total, str)
            view.total_entries = int(total)
        except IndexError | ValueError | TypeError | AssertionError as e:
            raise KeyError("Invalid giveaway embed.") from e
        return view
```
 - The class method is a factory method that creates a view from a message.

### Moving out of the REPL

#### The holder class for the bot variable
```python
_VT = TypeVar("_VT")
class Holder(dict):
    def __getitem__(self, k: Any) -> _VT:
        if k not in self:
            return MISSING
        return super().__getitem__(k)

    def __delitem__(self, key: Any) -> None:
        if key not in self:
            return
        super().__delitem__(key)

    def pop(self, __key: Any, default: _VT = MISSING) -> _VT:
        if __key not in self:
            return default
        return super().pop(__key)

    def get(self, __key: Any, default: _VT = MISSING) -> _VT:
        if __key not in self:
            return default
        return super().get(__key)

    def setdefault(self, __key: Any, default: _VT = MISSING) -> _VT:
        if __key not in self:
            self[__key] = default
        return self[__key]
```
 - The [TypeVars][TypeVar] here are special types used in the standard python implementation of the [dict] class.
 - The [MISSING] type is the missing Sentinel value for the discord.py library, to avoid NoneType issues.
 - The **_VT** are the type variables for the key and value types.
 - It is implemented in the bot class as `self.holder = Holder()`, as a public var open to access anywhere.
 - The holder class is a subclass of the [dict] class, and is used to store the bot variable.
 - It is implemented as follows:

```python
class Giveaway(commands.Cog)
    def __init__(self, bot: CBot):
        self.bot = bot
        self.yesterday: GiveawayView = bot.holder.pop("yesterday")
        self.current: GiveawayView = bot.holder.pop("current")

    async def cog_unload(self) -> None:
        self.daily_giveaway.cancel()
        self.bot.holder["yesterday"] = self.yesterday
        self.bot.holder["current"] = self.current
```

 - The cog_unload method is called when the cog is unloaded.
 - The `__init__` method is called when the cog is constructed.
 - They transfer the method between the bot class and the cog class to keep them in the smallest possible state.
   - The cog is the smaller state, as it is self contained and doesn't require reaching above its own level.


## Back to [Top](./giveaway-error-postmortem) / [Home](../../../../index.html)

[Jishaku]: https://jishaku.readthedocs.io/en/latest/
[REPL]: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
[Class Method]: https://docs.python.org/3/library/functions.html#classmethod
[TypeVar]: https://docs.python.org/3.10/library/typing.html#typing.TypeVar
[dict]: https://docs.python.org/3/library/stdtypes.html#dict
[MISSING]: https://discordpy.readthedocs.io/en/latest/api.html#discord.discord.utils.MISSING