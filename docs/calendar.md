---
layout: default
title: Google Calendar Module
permalink: /docs/cal
---

# Google Calendar Module

## Checks

> No Command Checks, this module processes uses a webhook to keep an embed up to date with a
> linked public google calendar.
 
## On Load

```python
async def cog_load(self):
    webhook_id = os.getenv("WEBHOOK_ID")
    assert isinstance(webhook_id, str)
    self.webhook = await self.bot.fetch_webhook(int(webhook_id))
    self.calendar.start()
```

 - No parameters
 - Fetches the webhook from the API using the ID from the environment variable
 - Starts the calendar task

## Calendar Task

```python
async def calendar(self):
    mint = datetime.now(tz=...)
    maxt = datetime.now(tz=...) + timedelta(weeks=1)
    async with ...n.get(getUrl(minte, maxt)) as response:
        items = await response.json()
    fields: dict[int, EmbedField] = {}
    cancelled_times = []
    times: set[datetime] = set()
    for item in items["items"]:
        # process item, add to correct mapping(s)
    for time in cancelled_times:
        fields.pop(timegm(time.utctimetuple()), None)
        times.discard(time)
    # create embed from fields
    embed = discord.Embed(...).set_footer(text=...)
    #send message to webhook
    if self.message is None or week_end:
        if self.message:
            await self.message.delete()
        self.message = await self.webhook.send(..., embed=embed)
    else:
        await self.message.edit(embed=embed)
```

 - Runs 30 minutes on half hour intervals
 - Updates the calendar embed
 - Sends the embed to the webhook
 - Removes the old message and sends a new one if over a week old to avoid ratelimit issues

## Back to [top](./cal) / [features](.)
