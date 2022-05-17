---
layout: default
title: Admin Module
permalink: /docs/admin
---

# Admin Module

## Checks

{% highlight python %}
def check(self, ctx):
    if ctx.guild is None:
        return False
    author = ctx.author
    assert isinstance(author, discord.Member)
    return any(role.id in (0, 1, 2) for role in author.roles)
#=> Forces the user to be a mod and be in a guild
{% endhighlight %}

 - Must be a mod
 - Must be in a guild

## Ping

{% highlight python %}
async def ping(self, ctx):
    await ctx.send(f'Pong! {round(self.latency * 1000)}ms')
#=> sends a message with the websocket latency
{% endhighlight %}

 - No parameters
 - Returns a message with the websocket latency

## Sensitive

- Hybrid Group Parent of sensitive words command settings
- Can be invoked as a slash **\\** or prefix **!** command

### Common Code

{% highlight python %}
mode =  "r" or "w" # r for read, w for write
with open("sensitive_settings.json", mode, encooding="utf8") as file:
    if mode == "r":
        settings = json.load(file)
    else:
        json.dump(settings, file)
#=> Opens a file and reads or writes the settings
{% endhighlight %}

 - Opens a file and reads or writes the settings
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires

### add

{% highlight python %}
async def add(self, ctx, *, word):
    common("read")
    if word in settings["sensitive_words"]:
        await ctx.send("Word already exists")
    else:
        settings["sensitive_words"].append(word)
        await ctx.send("Word added")
        common("write")
#=> Adds a word to the sensitive words list
{% endhighlight %}

 - Adds a word to the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to add
 - Responds with a message with the full list of words

### remove

{% highlight python %}
async def remove(self, ctx, *, word):
    common("read")
    if word not in settings["sensitive_words"]:
        await ctx.send("Word does not exist")
    else:
        settings["sensitive_words"].remove(word)
        await ctx.send("Word removed")
        common("write")
#=> Removes a word from the sensitive words list
{% endhighlight %}

 - Removes a word from the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to remove
 - Responds with a message with the full list of words

### query

{% highlight python %}
async def query(self, ctx):
    common("read")
    await ctx.send(f"Sensitive words: {settings['sensitive_words']}")
#=> Responds with a message with the full list of words
{% endhighlight %}

 - Responds with a message with the full list of words
 - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - No parameters

## Back to [top](./admin) / [features](.)
