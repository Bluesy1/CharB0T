# coding=utf-8
# pylint: disable=invalid-name
import datetime
import json
import logging
import os
import random
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands, tasks

from roller import roll as aroll


# noinspection PyBroadException
def main():  # pylint: disable = too-many-statements
    """Main"""
    if os.name != "nt":
        import uvloop  # pylint: disable=import-outside-toplevel
        uvloop.install()

    with open("KethranToken.json", encoding='utf8') as file:
        token = json.load(file)['Token']
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = RotatingFileHandler(filename='kethran.log', encoding='utf-8', mode='w', maxBytes=2000000, backupCount=10)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    bot = commands.Bot(command_prefix="k", owner_id=363095569515806722, case_insensitive=True, help_command=None,
                       intents=discord.Intents.message_content)
    responses = [
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

    @bot.event
    async def on_message(message: discord.Message):  # pylint: disable=unused-variable
        """Checks guild messages in correct channels for regex trigger"""
        if not message.author.bot and message.channel.type is not discord.ChannelType.private:
            if message.channel.id in [901325983838244865, 878434694713188362]:
                if "kethran" in message.content.lower():
                    await message.channel.send(random.choice(responses), reference=message, mention_author=True)
        elif message.author.id == 184524255197659136:
            channel = await bot.fetch_channel(878434694713188362)
            await channel.send(message.content)

    @bot.command()
    async def roll(ctx: commands.Context, *, arg: str):  # pylint: disable=unused-variable
        """Dice roller"""
        await ctx.send(f"Kethran {aroll(arg)}")

    @tasks.loop(minutes=1)
    async def friday_5() -> None:  # pylint: disable=unused-variable
        """IDK, it's a thing"""
        if datetime.datetime.now(tz=datetime.timezone.utc).date().weekday() == 6 and \
                datetime.datetime.now(tz=datetime.timezone.utc).hour == 1 and \
                datetime.datetime.now(tz=datetime.timezone.utc).minute == 0:
            await (await bot.fetch_channel(878434694713188362)).send(random.choice(responses))
        else:
            print("Test")

    async def on_connect():
        print("Logged In!")

    friday_5.start()
    bot.on_connect = on_connect
    bot.load_extension('jishaku')
    bot.run(token)


if __name__ == "__main__":
    main()
