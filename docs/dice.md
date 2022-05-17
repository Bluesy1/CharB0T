---
layout: default
title: Dice Module
permalink: /docs/dice
---

# Dice Module

## Checks

```python
def check(self, ctx):
    if ctx.guild is None:
        return False
    author = ctx.author
    assert isinstance(author, discord.Member)
    return any(role.id in (0, 1, 2) for role in author.roles)
```

 - Must be a mod
 - Must be in a guild

## Roll

```python
async def roll(self, ctx, *, dice: str):
    rolls = dice.split("+")
    for roll in rolls:
        # do rolling stuff, append to results
    rolled=discord.Embed(...)
    await ctx.send(embed=rolled)
```

 - One parameter, **dice**, which is a string of the dice to roll
 - Returns a message with the rolled results

## Back to [features](.)
