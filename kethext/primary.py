# coding=utf-8
import datetime
import random

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog

import roller


@tasks.loop(minutes=1)
async def friday_5(bot: commands.Bot) -> None:  # pylint: disable=unused-variable
    """IDK, it's a thing"""
    if datetime.datetime.now(tz=datetime.timezone.utc).date().weekday() == 6 and \
            datetime.datetime.now(tz=datetime.timezone.utc).hour == 1 and \
            datetime.datetime.now(tz=datetime.timezone.utc).minute == 0:
        await (await bot.fetch_channel(878434694713188362)).send(random.choice([
            "Bork!", "Bork!", "Bork!", "Bork!", "Bork!", "WOOF!", "WOOF!", "WOOF!", "WOOF!", "AROOOF!", "AROOOF!",
            "AROOOF!", "AROOOF!", "HOOOWL!", "HOOOWL!", "HOOOWL!", "HOOOWL!", "HOOOWL!", "Aroof", "Aroof", "Aroof",
            "Aroof", "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*", "*Sniff Sniff Sniff*",
            "*Does not care*", "*Does not care*", "*Does not care*", "*Does not care*", "*I want scritches*",
            "*I want scritches*", "*I want scritches*", "*I want scritches*", "*I want scritches*", "*is busy*",
            "*is busy*", "*is busy*", "*is busy*", "snuffles", "snuffles", "snuffles", "snuffles",
            "snuffles apologetically", "snuffles apologetically", "snuffles apologetically", "snuffles apologetically",
            "sits", "sits", "sits", "sits", "lays down", "lays down", "lays down", "lays down", "chuffs", "chuffs",
            "chuffs", "chuffs", "pants", "pants", "pants", "pants", "plays dead", "plays dead", "plays dead",
            "plays dead", "gives paw", " gives paw", "gives paw", "gives paw", "rolls over", "rolls over", "rolls over",
            "rolls over", "is adorable", "is adorable", "is adorable", "is adorable", "whimpers", "whimpers",
            "whimpers", "whimpers", "licks face", " licks face", "licks face", "licks face", "*Sits*", "*Sits*",
            "*Sits*", "*Sits*", "*is adorable*", "*is adorable*", "*is adorable*", "*is adorable*", "pants", "pants",
            "pants", "pants", "**HOLY SHIT!** \n**HOLY SHIT!**\n**HOLY SHIT!**", ]))
    else:
        print("Test")


class Primary(Cog):
    """Kethran's Primary Functions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.responses = [
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

    @Cog.listener()
    async def on_message(self, message: discord.Message):  # pylint: disable=unused-variable
        """Checks guild messages in correct channels for regex trigger"""
        if not message.author.bot and message.channel.type is not discord.ChannelType.private:
            if message.channel.id in [901325983838244865, 878434694713188362]:
                if "kethran" in message.content.lower():
                    await message.channel.send(random.choice(self.responses), reference=message, mention_author=True)
        elif message.author.id == 184524255197659136:
            channel = await self.bot.fetch_channel(878434694713188362)
            await channel.send(message.content)

    @commands.command()
    async def roll(self, ctx: commands.Context, *, arg: str):  # pylint: disable=unused-variable,no-self-use
        """Dice roller"""
        await ctx.send(f"Kethran {roller.roll(arg)}", reference=ctx.message)


def setup(bot: commands.Bot):
    """Loads Plugin"""
    friday_5.start(bot)
    bot.add_cog(Primary(bot))


def teardown(bot: commands.Bot):
    """Unloads Plugin"""
    friday_5.stop()
