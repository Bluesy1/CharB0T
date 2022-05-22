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

Normally, when i need to reload the giveaway module, I use [Jishaku] to store the giveaway in a local [REPL] session 
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

I think, and i have no way to confirm this, that because when i went to do step 2, I initially got a syntax error i had
to fix, and after i fixed that i forgot to confirm i copied in the correct references to the [REPL] session, so when i 
reloaded the module and tried to load the giveaway from the [REPL] session, i lost the giveaway and loaded in `...`
ellipses placeholders instead.

# How am I going to fix this and prevent it from happening again?

First, I am going to remove all other commands and code not required for the giveaway view and task from the module.
This will prevent the giveaway module from having to be reloaded as often, limit chances for failure. Second, I am
going to store the giveaways in a bot variable during reloading automatically instead of a cog variable
to make the state of the giveaway not based off of a [REPL] session. This will make it easier to reload the module 
without losing the giveaway. Finally, i'm going to add a [Class Method] as a Factory Method to the GiveawayView
class to allow me to reconstruct a giveaway easier from a channel and message ID should a giveaway be lost in the
future.

## Back to [Top](./giveaway-error-postmortem) / [Home](../../../../index.html)

[Jishaku]: https://jishaku.readthedocs.io/en/latest/
[REPL]: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
[Class Method]: https://docs.python.org/3/library/functions.html#classmethod