# coding=utf-8
import os
import time

from discord.ext import commands
from discord.ext.commands import Cog, Context


class Query(Cog):
    """Query cog"""

    # noinspection PyUnresolvedReferences
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return not any(role.id in (684936661745795088, 676250179929636886) for role in ctx.author.roles) or \
               any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in ctx.author.roles)

    @commands.command()
    async def time(self, ctx: Context):  # pylint: disable=no-self-use
        """Returns eastern time"""
        os.environ['TZ'] = 'US/Eastern'
        time.tzset()
        await ctx.send("Charlie's time is: " + time.strftime('%X %x %Z'), reference=ctx.message)


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Query(bot))
