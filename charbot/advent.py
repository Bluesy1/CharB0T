# -*- coding: utf-8 -*-
"""Query extension."""
import datetime
from typing import TYPE_CHECKING, cast

import discord
from discord.ext import commands

from . import Config

if TYPE_CHECKING:
    from charbot import CBot


class AdventOfCode(commands.Cog):
    def __init__(self, bot: "CBot"):
        self.bot = bot
        self.data = {}
        self.last_fetched = discord.utils.utcnow() - datetime.timedelta(days=1)

    async def cog_load(self) -> None:
        """Load the cog."""
        self.data = self.bot.holder.get("advent_data", None) or self.data
        self.last_fetched = self.bot.holder.get("advent_last_fetched", None) or self.last_fetched

    async def cog_unload(self) -> None:
        """Unload the cog."""
        self.bot.holder["advent_data"] = self.data
        self.bot.holder["advent_last_fetched"] = self.last_fetched

    async def get_leaderboard(self):
        """Get the leaderboard, or return the cached data"""
        if (discord.utils.utcnow() - self.last_fetched).total_seconds() < 900:
            return self.data
        cookies = cast(dict[str, str], Config.get("advent"))
        async with self.bot.session.get(
            "https://adventofcode.com/2022/leaderboard/private/view/1900458.json", cookies=cookies
        ) as resp:
            if resp.status == 200:
                self.data = await resp.json()
                self.last_fetched = discord.utils.utcnow()
                return self.data
            else:
                raise Exception(f"Failed to get leaderboard, got status {resp.status}, {await resp.text()}")

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def advent(self, ctx: commands.Context):
        """Advent of Code."""
        data = await self.get_leaderboard()
        members = list(data["members"].values())
        members.sort(key=lambda d: d["local_score"], reverse=True)
        embed = discord.Embed(
            title=f"{cast(discord.Guild, ctx.guild).name} Private Leaderboard", timestamp=discord.utils.utcnow()
        )
        for member in members:
            base = f"• Local Score:{member['local_score']}"
            for i in range(1, 26):
                day = member["completion_day_level"].get(str(i))
                if day is not None:
                    base += f"\n•Day {f'0{i}' if i < 10 else i}:\n◦ Part 1: <t:{day['1']['get_star_ts']}:f>"
                    part2 = day.get("2")
                    if part2 is not None:
                        base += f"\n◦ Part 2: <t:{part2['get_star_ts']}:f>"
            embed.add_field(name=member["name"], value=base)
        await ctx.send(embed=embed)


async def setup(bot: "CBot"):
    await bot.add_cog(AdventOfCode(bot))
