# pylint: disable=invalid-name
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timedelta

import hikari
import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from lightbulb import commands

RETRIES = 0


# noinspection PyBroadException
def main():  # pylint: disable = too-many-statements
    """Main"""
    global RETRIES
    """Main"""
    if os.name != "nt":
        import uvloop  # pylint: disable=import-outside-toplevel
        uvloop.install()

    token = json.load(open("KethranToken.json"))['Token']

    bot = lightbulb.BotApp(token=token, prefix="k", help_class=None,
                           owner_ids=[363095569515806722], case_insensitive_prefix_commands=True)
    scheduler = AsyncIOScheduler()
    scheduler.start()
    bot.d.responses = [
        "Bork!", "Bork!", "Bork!", "Bork!", "Bork!",
        "WOOF!", "WOOF!", "WOOF!", "WOOF!",
        "AROOOF!", "AROOOF!", "AROOOF!", "AROOOF!",
        "HOOOWL!", "HOOOWL!", "HOOOWL!", "HOOOWL!", "HOOOWL!",
        "Aroof", "Aroof", "Aroof", "Aroof",
        "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*",
        "*Does not care*", "*Does not care*", "*Does not care*", "*Does not care*",
        "*I want scritches*", "*I want scritches*", "*I want scritches*",
        "*I want scritches*", "*I want scritches*",
        "*is busy*", "*is busy*", "*is busy*", "*is busy*",
        "snuffles", "snuffles", "snuffles", "snuffles",
        "snuffles apologetically", "snuffles apologetically",
        "snuffles apologetically", "snuffles apologetically",
        "sits", "sits", "sits", "sits",
        "lays down", "lays down", "lays down", "lays down",
        "chuffs", "chuffs", "chuffs", "chuffs",
        "pants", "pants", "pants", "pants",
        "plays dead", "plays dead", "plays dead", "plays dead",
        "gives paw", " gives paw", "gives paw", "gives paw",
        "rolls over", "rolls over", "rolls over", "rolls over",
        "is adorable", "is adorable", "is adorable", "is adorable",
        "whimpers", "whimpers", "whimpers", "whimpers",
        "licks face", " licks face", "licks face", "licks face",
        "*Sits*", "*Sits*", "*Sits*", "*Sits*",
        "*is adorable*", "*is adorable*", "*is adorable*", "*is adorable*",
        "pants", "pants", "pants", "pants",
        "**HOLY SHIT!** \n**HOLY SHIT!**\n**HOLY SHIT!**",
    ]
    bot.d.roll_error = ("Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s, "
                        "or d100s, or if a constant modifier must be a perfect integer, positive or negative, "
                        "connexted with `+`, and no spaces.")
    bot.load_extensions("lightbulb.ext.filament.exts.superuser")

    @bot.listen(hikari.GuildMessageCreateEvent)
    async def on_guild_message(event: hikari.GuildMessageCreateEvent):  # pylint: disable=unused-variable
        """Checks guild messages in correct channels for regex trigger"""
        if event.is_human:
            if event.channel_id in [901325983838244865, 878434694713188362]:
                if "kethran" in event.content.lower():
                    await event.get_channel().send(
                        bot.d.responses[random.randint(0, 99)], reply=event.message_id, mentions_reply=True)

    @bot.listen(hikari.DMMessageCreateEvent)
    async def on_dm_message(event: hikari.DMMessageCreateEvent):  # pylint: disable=unused-variable
        """Checks for DMs from a specific user to forward"""
        if event.is_human and event.content is not None and event.author_id == 184524255197659136:
            channel = await bot.rest.fetch_channel(878434694713188362)
            await channel.send(event.content)

    @bot.command()
    @lightbulb.option("dice", "dice to roll", required=True)
    @lightbulb.command("roll", "diceroller")
    @lightbulb.implements(commands.PrefixCommand)
    async def roll(ctx: lightbulb.Context):  # pylint: disable=unused-variable
        """Dice roller"""
        arg = ctx.options.dice
        if "+" in arg:
            dice = arg.split("+")
        else:
            dice = [str(arg)]
        try:
            sums = 0
            rolls = list()
            allowed_dice = [2, 4, 6, 8, 10, 12, 20, 100]
            for die in dice:
                if 'd' in die:
                    if int(die[die.find('d') + 1:]) not in allowed_dice:
                        await ctx.respond(bot.d.roll_error)
                        return
                    try:
                        num_rolls = int(die[:die.find('d')])
                    except ValueError:
                        num_rolls = 1
                    i = 1
                    while i <= num_rolls:
                        roll1 = random.randint(1, int(die[die.find('d') + 1:]))
                        rolls.append(roll1)
                        sums += roll1
                        i += 1
                else:
                    try:
                        rolls.append(int(die))
                        sums += int(die)
                    except ValueError:
                        await ctx.respond(bot.d.roll_error,reply=True)
                        return
            output = '`'
            for roll1 in rolls:
                output += str(roll1) + ', '
            output = output[:-2]
            await ctx.respond(f"Kethran rolled `{arg}` got {output}` for a total value of: {str(sums)}", reply=True)
        except Exception:  # pylint: disable=broad-except
            await ctx.respond(bot.d.roll_error, reply=True)

    @scheduler.scheduled_job(CronTrigger(day_of_week="sat", hour="1"), id="1")
    async def friday_5() -> None:  # pylint: disable=unused-variable
        """IDK, it's a thing"""
        await bot.rest.create_message(878434694713188362, bot.d.responses[random.randint(0, 99)])

    RETRIES = 0

    def remove_retry():
        """Removes a Retry"""
        global RETRIES
        RETRIES -= 1

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
    except:   # pylint: disable=bare-except
        if RETRIES < 11:
            time.sleep(10)
            RETRIES += 1
            scheduler.add_job(remove_retry, DateTrigger(datetime.utcnow() + timedelta(minutes=30)))
            print(f"Bot Closed, Trying to restart, try {RETRIES}/10")
            main()
        else:
            traceback.print_exc()
            sys.exit()


if __name__ == "__main__":
    main()
