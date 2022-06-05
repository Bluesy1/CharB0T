# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
"""Level system."""
import datetime
import functools
import os
import random
from io import BytesIO
from typing import Callable, Optional

import aiohttp
import asyncpg
import discord
from discord import Interaction, app_commands
from discord.ext import commands, tasks
from discord.utils import utcnow
from disrank.generator import Generator

from . import CBot


async def update_level_roles(member: discord.Member, new_level: int) -> None:
    """Update the level roles of the user.

    Parameters
    ----------
    member : discord.Member
        The member to update the level roles of.
    new_level : int
        The new level of the user.
    """
    if new_level == 1:
        await member.add_roles(discord.Object(969626979353632790), reason="Level 1")
    elif new_level == 5:
        await member.remove_roles(discord.Object(969626979353632790), reason="Level 5")
        await member.add_roles(discord.Object(969627321239760967), reason="Level 5")
    elif new_level == 10:
        await member.remove_roles(discord.Object(969627321239760967), reason="Level 10")
        await member.add_roles(discord.Object(969628342733119518), reason="Level 10")
    elif new_level == 20:
        await member.remove_roles(discord.Object(969628342733119518), reason="Level 20")
        await member.add_roles(discord.Object(969629632028614699), reason="Level 20")
    elif new_level == 25:
        await member.remove_roles(discord.Object(969629632028614699), reason="Level 25")
        await member.add_roles(discord.Object(969629628249563166), reason="Level 25")
    elif new_level == 30:
        await member.remove_roles(discord.Object(969629628249563166), reason="Level 30")
        await member.add_roles(discord.Object(969629622453039104), reason="Level 30")


class Leveling(commands.Cog):
    """Level system."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self._min_xp = 11
        self._max_xp = 18
        self._xp_function: Callable[[int], int] = lambda x: (5 * x**2) + (50 * x) + 100
        self.off_cooldown: dict[int, datetime.datetime] = {}
        self.generator = Generator()
        self.generator.default_bg = "charbot/media/pools/card.png"
        self.default_profile = "https://raw.githubusercontent.com/Bluesy1/CharB0T/main/charbot/media/pools/profile.png"
        _token = os.getenv("GITHUB_TOKEN")
        assert isinstance(_token, str)  # skipcq: BAN-B101
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(login="Bluesy1", password=_token),
            headers={"accept": "application/vnd.github.v3+json"},
        )
        self._post_url = "https://api.github.com/repos/bluesy1/charb0t/actions/workflows/leaderboard.yml/dispatches"
        self._upload: bool = False

    async def cog_load(self) -> None:
        """Load the cog."""
        self.off_cooldown = self.bot.holder.pop("off_xp_cooldown", {})

        self.update_pages.start()

    async def cog_unload(self) -> None:
        """Unload the cog."""
        self.bot.holder["off_xp_cooldown"] = self.off_cooldown
        self.update_pages.cancel()

    @tasks.loop(time=[datetime.time(i) for i in range(0, 24)])
    async def update_pages(self) -> None:
        """Update the page."""
        if self._upload:
            async with self.session.post(self._post_url, json={"ref": "gh-pages"}) as resp:
                print(resp)
        self._upload = False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Add XP to the user when they send a message.

        Parameters
        ----------
        message : discord.Message
            The message that was sent.
        """
        if message.author.bot:
            return
        if message.guild is None:
            return
        async with self.bot.pool.acquire() as conn, conn.transaction():
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", message.guild.id)
            if no_xp is None:
                return
            if message.channel.id in no_xp["channels"]:
                return
            member = message.author
            assert isinstance(member, discord.Member)  # skipcq: BAN-B101
            if any(role.id in no_xp["roles"] for role in member.roles):
                return
            last_time = self.off_cooldown.get(message.author.id)
            if last_time is None or last_time < utcnow():
                self._upload = True
                self.off_cooldown[message.author.id] = utcnow() + datetime.timedelta(minutes=1)
                user = await conn.fetchrow("SELECT * FROM xp_users WHERE id = $1", message.author.id)
                gained = random.randint(self._min_xp, self._max_xp)
                if user is None:
                    await conn.execute(
                        "INSERT INTO xp_users "
                        "(id, username, discriminator, xp, detailed_xp, level, messages, avatar, gang, prestige)"
                        " VALUES ($1, $2, $3, $4, $5, 0, 1, $6, null, 0) ON CONFLICT (id) DO NOTHING",
                        message.author.id,
                        message.author.name,
                        message.author.discriminator,
                        gained,
                        [gained, self._xp_function(0), gained],
                        message.author.avatar.key if message.author.avatar else None,
                    )
                    return
                if gained + user["detailed_xp"][0] >= self._xp_function(user["level"]):
                    new_level = user["level"] + 1
                    new_detailed = [0, self._xp_function(new_level), user["xp"] + gained]
                    new_xp = new_detailed[2]
                    await conn.execute(
                        "UPDATE xp_users SET level = $1, detailed_xp = $2, xp = $3, messages = messages + 1,"
                        " avatar = $4 WHERE id = $5",
                        new_level,
                        new_detailed,
                        new_xp,
                        message.author.avatar.key if message.author.avatar else None,
                        message.author.id,
                    )
                    await message.channel.send(
                        f"{message.author.mention} has done some time, and is now level **{new_level}**."
                    )
                    await update_level_roles(member, new_level)
                    return
                await conn.execute(
                    "UPDATE xp_users SET xp = xp + $1, detailed_xp = $2, messages = messages + 1, avatar = $3"
                    " WHERE id = $4",
                    gained,
                    [user["detailed_xp"][0] + gained, user["detailed_xp"][1], user["detailed_xp"][2] + gained],
                    message.author.avatar.key if message.author.avatar else None,
                    message.author.id,
                )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """CHeck if they are rejoining and should get a rank role back.

        Parameters
        ----------
        member : discord.Member
            The member that joined.
        """
        async with self.bot.pool.acquire() as conn:
            level: int | None = await conn.fetchval("SELECT level FROM xp_users WHERE id = $1", member.id)
            if level is None:
                return
            await conn.execute(
                "UPDATE xp_users SET username = $1, discriminator = $2, avatar = $3 WHERE id = $4",
                member.name,
                member.discriminator,
                member.avatar.key if member.avatar else None,
                member.id,
            )
            if 0 < level < 5:
                await member.add_roles(discord.Object(969626979353632790), reason=f"Rejoined at level {level}")
            elif 5 <= level < 10:
                await member.add_roles(discord.Object(969627321239760967), reason=f"Rejoined at level {level}")
            elif 10 <= level < 20:
                await member.add_roles(discord.Object(969628342733119518), reason=f"Rejoined at level {level}")
            elif 20 <= level < 25:
                await member.add_roles(discord.Object(969629632028614699), reason=f"Rejoined at level {level}")
            elif 25 <= level < 30:
                await member.add_roles(discord.Object(969629628249563166), reason=f"Rejoined at level {level}")
            elif level >= 30:
                await member.add_roles(discord.Object(969629622453039104), reason=f"Rejoined at level {level}")

    @app_commands.command(name="rank")
    @app_commands.guilds(225345178955808768)
    @app_commands.checks.cooldown(1, 3600, key=lambda interaction: interaction.user.id)
    async def rank_command(self, interaction: Interaction, user: Optional[discord.Member] = None):
        """Check your or someone's level and rank.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : Optional[discord.Member]
            The user to check the level and rank of.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send("This Must be used in a guild")
            return
        member = user or interaction.user
        assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        async with self.bot.pool.acquire() as conn:
            users = await conn.fetch("SELECT *, ROW_NUMBER() OVER(ORDER BY xp DESC) AS rank FROM xp_users")
            try:
                user_record: asyncpg.Record = list(filter(lambda x: x["id"] == member.id, users))[0]
            except IndexError:
                await interaction.followup.send("🚫 You aren't ranked yet. Send some messages first, then try again.")
                return
        card: Callable[[], BytesIO] = functools.partial(
            self.generator.generate_profile,
            profile_image=interaction.user.avatar.url if interaction.user.avatar is not None else self.default_profile,
            level=user_record["level"],
            current_xp=user_record["detailed_xp"][2] - user_record["detailed_xp"][0],
            user_xp=user_record["xp"],
            next_xp=user_record["detailed_xp"][2] - user_record["detailed_xp"][0] + user_record["detailed_xp"][1],
            user_position=user_record["rank"],
            user_name=f"{member.name}#{member.discriminator}",
            user_status=member.status.value if not isinstance(member.status, str) else "offline",
        )
        image = await self.bot.loop.run_in_executor(None, card)
        await interaction.followup.send(file=discord.File(image, "profile.png"))


async def setup(bot: CBot):
    """Load cog."""
    await bot.add_cog(Leveling(bot))
