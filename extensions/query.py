# coding=utf-8
import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import Cog, Context

from roller import roll as aroll


class Dice(app_commands.Group):
    """Dice parent"""

    @app_commands.command(description="D&D Standard Array 7 Dice roller, plus coin flips")
    @app_commands.describe(dice="Dice to roll, accpets d<int>s and integers")
    async def roll(self, interaction: Interaction, dice: str):  # pylint: disable=unused-variable,no-self-use
        """Dice roller"""
        if any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in
               interaction.user.roles):
            await interaction.response.send_message(f"{interaction.user.mention} {aroll(dice)}")
        else:
            await interaction.response.send_message("You are not authorized to use this command")


class Roll(Cog):
    """Roll cog"""
    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree: app_commands.CommandTree = bot.tree
        self.tree.add_command(Dice(), guild=discord.Object(id=225345178955808768))

    def cog_check(self, ctx: Context) -> bool:
        return not any(role.id in (684936661745795088, 676250179929636886) for role in ctx.author.roles) or \
            any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in ctx.author.roles)

    @commands.Command()
    async def time(self, ctx: Context):
        """Returns eastern time"""
        os.environ['TZ'] = 'US/Eastern'
        time.tzset()
        await ctx.respond("Charlie's time is: " + time.strftime('%X %x %Z'))

def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Roll(bot))
