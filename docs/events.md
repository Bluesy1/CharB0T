---
layout: default
title: Events Module
permalink: /docs/events
---

# Events Module

## Checks

> No Command Checks, this module processes events and not commands.

## On member join

{% highlight python %}
async def on_member_join(self, member: discord.Member):
    if member.guild.id == 0:
        self.members.update({member.id: utcnow()})
#=> Add the members join time to the mapping
{% endhighlight %}

 - One parameter, **member**, which is a discord.Member object

## On member leave

{% highlight python %}
async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent):
    if payload.guild_id == 0:
        user = payload.user
        if isinstance(user, discord.Member):
            self.members.pop(user.id, None)
            time_string = await time_str(...)
        elif isinstance(user, discord.User) and user.id in self.members:
            time_string = await time_str(...)
        else:
            time_string = "Unknown"
        channel = await self.bot.fetch_channel(1)
        assert isinstance(channel, discord.TextChannel)
        await channel.send(f"... Time on Server: {time_string}")
{% endhighlight %}

  - One parameter, **payload**, which is a discord.RawMemberRemoveEvent object
  - Processes member leave events
  - Removes the member from the mapping
  - Sends a message to the appropriate channel
  - Logs the member's time on the server
  - Raw Event is used as to capture leave events when the member isn't cached


## On member update

{% highlight python %}
async def on_member_update(self, before: discord.Member, after):
    try:
        if after.timed_out_until != before.timed_out_until:
            if after.is_timed_out():
                await self.parse_timeout(after)
            else:
                embed = Embed(...)
                with open("settings.json", encoding="utf8") as file:
                    webhook = await self.bot.fetch_webhook(...)
                bot_user = self.bot.user
                assert isinstance(bot_user, discord.ClientUser)
                await webhook.send(..., embed=embed)
                self.timeouts.pop(after.id)
    except Exception:
        if after.is_timed_out():
            await self.parse_timeout(after)
{% endhighlight %}

  - Two parameters, **before** and **after**, which are discord.Member objects
  - Processes member update events
  - Checks for timed out members
  - Sends a message to the appropriate channel
  - Logs the member's time on the server
  - Raw Event is used as to capture update events when the member isn't cached

## On Message

{% highlight python %}
async def on_message(self, message: discord.Message):
    if message.content is not None and not message.author.bot:
        # remove empty messages and bot messages
        await sensitive_scan(message)
        # scan for sensitive words, too complex to show here
        if message.guild is not None:
            await redirect(message)
            # redirect messages to the appropriate channel
            return
        # check for everyone ping, bad strings due to formatting:
        if bad_things(message):
            await log(message)
            # log bad messages
            await message.delete()
{% endhighlight %}

  - No parameters
  - Processes messages
  - Checks for bad messages
  - Checks for sensitive words
  - Redirects messages to the appropriate channel
  - Logs bad messages

## Back to [top](./events) / [features](.)
