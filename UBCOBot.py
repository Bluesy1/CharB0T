import datetime
import json
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

import hikari
import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from hikari.embeds import Embed
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.intents import Intents
from lightbulb import commands
from lightbulb.checks import has_roles


def main():
    global retries

    if os.name != "nt":
        import uvloop
        uvloop.install()

    token = json.load(open('UBCbot.json'))['Token']
    # Instantiate a Bot instance
    bot = lightbulb.BotApp(token=token, prefix=";", help_class=None, owner_ids=[363095569515806722], logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
        }, }, case_insensitive_prefix_commands=True, intents=Intents.ALL, delete_unbound_commands=False)

    scheduler = AsyncIOScheduler()
    scheduler.start()

    @bot.command()
    @lightbulb.option("word", "Word to remove")
    @lightbulb.add_checks(has_roles(832521484378308660, 832521484378308659, 832521484378308658, mode=any))
    @lightbulb.command("add", "adds a word to the slur filter")
    @lightbulb.implements(commands.PrefixCommand)
    async def add(ctx: lightbulb.Context):
        if ctx.guild_id != 832521484340953088: return
        with open('UBCbot.json') as t:
            fulldict = json.load(t)
        joinstring = ", "
        if ctx.options.word.lower() not in fulldict['Words']:
            fulldict['Words'].append(ctx.options.word.lower())
            with open('UBCbot.json', 'w') as t:
                json.dump(fulldict, t)
            await ctx.respond(embed=Embed(title="New list of words defined as slurs",
                                          description=f"||{joinstring.join(fulldict['Words'])}||", color="0x00ff00",
                                          timestamp=datetime.datetime.now(tz=datetime.timezone.utc)))
        else:
            await ctx.respond(embed=Embed(title="Word already in list of words defined as slurs",
                                          description=f"||{joinstring.join(fulldict['Words'])}||", color="0x0000ff",
                                          timestamp=datetime.datetime.now(tz=datetime.timezone.utc)))

    @bot.command()
    @lightbulb.add_checks(has_roles(832521484378308660, 832521484378308659, 832521484378308658, mode=any))
    @lightbulb.command("query", "querys the slur filter list")
    @lightbulb.implements(commands.PrefixCommand)
    async def query(ctx: lightbulb.Context):
        if ctx.guild_id != 832521484340953088: return
        with open('UBCbot.json') as t:
            fulldict = json.load(t)
        joinstring = ", "
        await ctx.respond(
            embed=Embed(title="List of words defined as slurs", description=f"||{joinstring.join(fulldict['Words'])}||",
                        color="0x0000ff", timestamp=datetime.datetime.now(tz=datetime.timezone.utc)))

    @bot.command()
    @lightbulb.option("word", "Word to remove")
    @lightbulb.add_checks(has_roles(832521484378308660, 832521484378308659, 832521484378308658, mode=any))
    @lightbulb.command("remove", "removes a word from the slur filter")
    @lightbulb.implements(commands.PrefixCommand)
    async def remove(ctx: lightbulb.Context):
        if ctx.guild_id != 832521484340953088: return
        with open('UBCbot.json') as t:
            fulldict = json.load(t)
        joinstring = ", "
        if ctx.options.word.lower() in fulldict['Words']:
            for i in range(len(fulldict['Words'])):
                if fulldict['Words'][i] == ctx.options.word.lower():
                    fulldict['Words'].pop(i)
                    await ctx.respond(embed=Embed(title="New list of words defined as slurs",
                                                  description=f"||{joinstring.join(fulldict['Words'])}||",
                                                  color="0x00ff00",
                                                  timestamp=datetime.datetime.now(tz=datetime.timezone.utc)))
                    with open('UBCbot.json', 'w') as t:
                        json.dump(fulldict, t)
                    break
        else:
            await ctx.respond(embed=Embed(title="Word not in list of words defined as slurs",
                                          description=f"||{joinstring.join(fulldict['Words'])}||", color="0x0000ff",
                                          timestamp=datetime.datetime.now(tz=datetime.timezone.utc)))

    @bot.listen(GuildMessageCreateEvent)
    async def on_guild_message(event: GuildMessageCreateEvent):
        if event.guild_id != 832521484340953088 or event.content is None: return
        with open('UBCbot.json') as t:
            words: list[str] = json.load(t)['Words']
        content = event.content.lower().split();
        used_slurs = set();
        joinstring = ", "
        for word in content:
            if word in words:
                used_slurs.add(word)
        if used_slurs != set() and not any(
                rid in event.member.role_ids for rid in [832521484378308660, 832521484378308659, 832521484378308658]):
            await event.message.delete()
            await bot.rest.add_role_to_member(832521484340953088, event.member.id, 900612423332028416,
                                              reason="Used a Slur")
            await bot.rest.add_role_to_member(832521484340953088, event.member.id, 930953847411736598,
                                              reason="Used a Slur")
            await bot.rest.create_message(832521484828147741, embed=Embed(
                title=f"[SLUR] {event.member.username}#{event.member.discriminator}", color="0xff0000",
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc)).add_field("User", event.member.mention,
                                                                                     inline=True).add_field(
                "Slurs Used", f"||{joinstring.join(used_slurs)}||", inline=True).add_field("Channel",
                                                                                           f"<#{event.channel_id}>",
                                                                                           inline=True).add_field(
                "Message", event.content, inline=True))

    @scheduler.scheduled_job(DateTrigger(run_date=datetime(2022, 2, 5, 12, 0, 0, 0, timezone(-timedelta(hours=8)))))
    async def meh() -> None:
        """Thing"""
        user = await bot.rest.fetch_user(318794104110710787)
        await user.send("Pack some SATA Cables for Ankkit")

    """@bot.listen(hikari.InteractionCreateEvent)
    async def test(event: hikari.InteractionCreateEvent):
        await bot.rest.create_message(885390293405425734,
                                      embed=Embed(title="Interaction Found")
                                      .add_field("id", str(event.interaction.id), inline=True)
                                      .add_field("Type", str(event.interaction.type), inline=True)
                                      .add_field("Time", str(event.interaction.created_at.strftime()), inline=True)
                                      .add_field("Custom ID", str(event.interaction.custom_id), inline=True))
    """

    retries = 0

    def remove_retry():
        """Removes a Retry"""
        global retries
        retries -= 1

    try:
        bot.run()
    except KeyboardInterrupt:
        traceback.print_exc()
        sys.exit()
    except hikari.ComponentStateConflictError:
        traceback.print_exc()
        sys.exit()
    except TypeError:
        traceback.print_exc()
        sys.exit()
    except:
        if retries < 11:
            time.sleep(10)
            retries += 1
            scheduler.add_job(remove_retry, DateTrigger(datetime.utcnow() + timedelta(minutes=30)))
            print(f"Bot Closed, Trying to restart, try {retries}/10")
            main()
        else:
            traceback.print_exc()
            sys.exit()


if __name__ == "__main__":
    main()
