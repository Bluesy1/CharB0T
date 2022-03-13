# coding=utf-8
import random
import sys

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from discord.utils import utcnow

sys.path.append("..")
from helpers import roller  # skipcq: FLK-E402


class Primary(Cog):
    """Kethran's Primary Functions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.responses = [
            "Bork!",
            "Bork!",
            "Bork!",
            "Bork!",
            "Bork!",
            "WOOF!",
            "WOOF!",
            "WOOF!",
            "WOOF!",
            "AROOOF!",
            "AROOOF!",
            "AROOOF!",
            "AROOOF!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "HOOOWL!",
            "Aroof",
            "Aroof",
            "Aroof",
            "Aroof",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Sniff Sniff Sniff*",
            "*Does not care*",
            "*Does not care*",
            "*Does not care*",
            "*Does not care*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*I want scritches*",
            "*is busy*",
            "*is busy*",
            "*is busy*",
            "*is busy*",
            "snuffles",
            "snuffles",
            "snuffles",
            "snuffles",
            "snuffles apologetically",
            "snuffles apologetically",
            "snuffles apologetically",
            "snuffles apologetically",
            "sits",
            "sits",
            "sits",
            "sits",
            "lays down",
            "lays down",
            "lays down",
            "lays down",
            "chuffs",
            "chuffs",
            "chuffs",
            "chuffs",
            "pants",
            "pants",
            "pants",
            "pants",
            "plays dead",
            "plays dead",
            "plays dead",
            "plays dead",
            "gives paw",
            " gives paw",
            "gives paw",
            "gives paw",
            "rolls over",
            "rolls over",
            "rolls over",
            "rolls over",
            "is adorable",
            "is adorable",
            "is adorable",
            "is adorable",
            "plops head on lap",
            "whimpers",
            "whimpers",
            "whimpers",
            "licks face",
            "licks face",
            "licks face",
            "licks face",
            "*Sits*",
            "*Sits*",
            "*Sits*",
            "*Sits*",
            "*is adorable*",
            "*is adorable*",
            "*is adorable*",
            "*is adorable*",
            "pants",
            "pants",
            "pants",
            "pants",
            "**HOLY SHIT!** \n**HOLY SHIT!**\n**HOLY SHIT!**",
        ]
        self.friday_5.start()

    def cog_unload(self) -> None:
        """Cog unload handling"""
        self.friday_5.cancel()

    @tasks.loop(minutes=1)
    async def friday_5(self) -> None:
        """IDK, it's a thing"""
        if (
            utcnow().date().weekday() == 5
            and utcnow().hour == 1
            and utcnow().minute == 0
        ):
            await (await self.bot.fetch_channel(878434694713188362)).send(
                random.choice(self.responses)
            )

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        """Checks guild messages in correct channels for regex trigger"""
        if (
            not message.author.bot
            and message.channel.type is not discord.ChannelType.private
        ):
            if (
                message.channel.id in [901325983838244865, 878434694713188362]
                and "kethran" in message.content.lower()
            ):
                await message.channel.send(
                    random.choice(self.responses),
                    reference=message,
                    mention_author=True,
                )
        elif message.author.id == 184524255197659136:
            channel = await self.bot.fetch_channel(878434694713188362)
            await channel.send(message.content)

    @commands.command()
    async def roll(self, ctx: commands.Context, *, arg: str):
        """Dice roller"""
        await ctx.send(f"Kethran {roller.roll(arg)}", reference=ctx.message)


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Primary(bot))
