# coding=utf-8
from discord.ext import commands
from discord.ext.commands import Cog, Context

from roller import roll as aroll


class Roll(Cog):
    """Roll cog"""

    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands"""
        return any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles
        )

    @commands.command()
    async def roll(
        self, ctx: Context, *, dice: str
    ):
        """Dice roller"""
        if any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles
        ):
            await ctx.send(
                f"{ctx.author.mention} {aroll(dice)}",
                reference=ctx.message,
                mention_author=True,
            )
        else:
            await ctx.send(
                "You are not authorized to use this command",
                reference=ctx.message,
                mention_author=True,
            )


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Roll(bot))
