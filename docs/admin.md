---
layout: default
title: Admin Module
permalink: /docs/admin
---

# Admin Module

## Checks

```python
def check(self, ctx):
    if ctx.guild is None:
        return False
    author = ctx.author
    assert isinstance(author, discord.Member)
    return any(role.id in (0, 1, 2) for role in author.roles)
#=> Forces the user to be a mod and be in a guild
```

 - Must be a mod
 - Must be in a guild

## Ping

```python
async def ping(self, ctx):
    await ctx.send(f'Pong! {round(self.latency * 1000)}ms')
#=> sends a message with the websocket latency
```

 - No parameters
 - Returns a message with the websocket latency

## Sensitive

- Hybrid Group Parent of sensitive words command settings
- Can be invoked as a slash **\\** or prefix **!** command

### Common Code

```python
mode =  "r" or "w" # r for read, w for write
with open("sensitive_settings.json", mode, encooding="utf8") as file:
    if mode == "r":
        settings = json.load(file)
    else:
        json.dump(settings, file)
#=> Opens a file and reads or writes the settings
```

 - Opens a file and reads or writes the settings
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires

### add

```python
async def add(self, ctx, *, word):
    common("read")
    if word in settings["sensitive_words"]:
        await ctx.send("Word already exists")
    else:
        settings["sensitive_words"].append(word)
        await ctx.send("Word added")
        common("write")
#=> Adds a word to the sensitive words list
```

 - Adds a word to the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to add
 - Responds with a message with the full list of words

### remove

```python
async def remove(self, ctx, *, word):
    common("read")
    if word not in settings["sensitive_words"]:
        await ctx.send("Word does not exist")
    else:
        settings["sensitive_words"].remove(word)
        await ctx.send("Word removed")
        common("write")
#=> Removes a word from the sensitive words list
```

 - Removes a word from the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to remove
 - Responds with a message with the full list of words

### query

```python
async def query(self, ctx):
    common("read")
    await ctx.send(f"Sensitive words: {settings['sensitive_words']}")
#=> Responds with a message with the full list of words
```

 - Responds with a message with the full list of words
 - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - No parameters

## Int to Time Delta

- This class is a [discord.app_commands.Transformer](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.Transformer)
- It is used to convert an integer to a time-delta, which is used to set the expiry time of a win,
  to remove it from the function and do autocomplete in one spot.

```python
class IntTimeDelta(app_commands.Transformer):

    @classmethod
    def type(cls) -> AppCommandOptionType:
        return AppCommandOptionType.integer

    @classmethod
    def min_value(cls) -> int:
        return 1

    @classmethod
    def max_value(cls) -> int:
        return 60

    @classmethod
    async def transform( 
        cls, interaction: discord.Interaction, value: str | int | float
    ) -> datetime.timedelta:
        if value is None:
            return datetime.timedelta(days=1)
        return datetime.timedelta(days=int(value))

    @classmethod
    async def autocomplete(
        cls, interaction: discord.Interaction, value: str | int | float
    ) -> list[app_commands.Choice[int]]:
        try:
            _value = int(value)
        except ValueError:
            return [Choice(value=i, name=f"{i} days") for i in range(1, 26)]
        else:
            if _value <= 13:
                return [
                    Choice(value=i, name=f"{i} days") for i in range(1, 26)
                ]
            if _value > 47:
                return [
                    Choice(value=i, name=f"{i} days") for i in range(36, 61)
                ]
            return [
                Choice(value=i, name=f"{i} days")
                  for i in range(_value - 12, _value + 13)
            ]
```

- This class is used to convert an integer to a time-delta, which is used to set the expiry time of a win,
  to remove it from the function and do autocomplete in one spot.
   - the type method is used to tell the bot what type of value this transformer is expecting.
   - the min_value method is used to set the minimum value that can be passed to the transformer.
   - the max_value method is used to set the maximum value that can be passed to the transformer.
   - the transform method is used to convert the value to a time-delta.
   - the autocomplete method is used to provide autocomplete for the value.

## Confirm Command

```python
  async def confirm(
      self,
      interaction: discord.Interaction,
      user: discord.Member,
      time: Optional[Transform[datetime.timedelta, IntTimeDelta]] = None,
  ) -> None:
      if interaction.user.id != OWNER_ID:
          await respond("Only the owner can confirm a winner.", ephemeral=True)
          return
      await self.bot.pool.execute(
          "INSERT INTO winners (id, expiry) VALUES ($1, $2)"
          "ON CONFLICT (id) DO UPDATE SET expiry = $2",
          user.id,
          self.bot.TIME() + (time or datetime.timedelta(days=1)),
      )
      await interaction.response.send_message("Confirmed.", ephemeral=True)
```

- This command is used to confirm a winner.
- It can only be used by the guild owner.
- The time parameter is used to set the expiry time of the win.
- If no time is provided, the win will expire in 6 days.

## Back to [top](./admin) / [features](.)
