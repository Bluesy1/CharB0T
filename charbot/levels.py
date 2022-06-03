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
import random
from typing import Callable

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.utils import utcnow
from disrank.generator import Generator

from . import CBot


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
        last_time = self.off_cooldown.get(message.author.id, None)
        if last_time is None or last_time < utcnow():
            self.off_cooldown[message.author.id] = utcnow() + datetime.timedelta(minutes=1)
            async with self.bot.pool.acquire() as conn, conn.transaction():
                user = await conn.fetchrow("SELECT * FROM xp_users WHERE id = $1", message.author.id)
                gained = random.randint(self._min_xp, self._max_xp)
                if user is None:
                    await conn.execute(
                        "INSERT INTO xp_users (id, username, discriminator, xp, detailed_xp, level, messages, avatar)"
                        " VALUES ($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT (id) DO NOTHING",
                        message.author.id,
                        message.author.name,
                        message.author.discriminator,
                        gained,
                        [gained, self._xp_function(0), gained],
                        0,
                        1,
                        message.author.avatar.key if message.author.avatar else None,
                    )
                    return
                if gained + user["detailed_xp"][0] >= self._xp_function(user["detailed_xp"][1]):
                    new_level = user["level"] + 1
                    new_detailed = [0, self._xp_function(new_level), user["xp"] + gained]
                    new_xp = new_detailed[2]
                    await conn.execute(
                        "UPDATE xp_users SET level = $1, detailed_xp = $2, xp = $3, messages = messages + 1 WHERE"
                        " id = $4",
                        new_level,
                        new_detailed,
                        new_xp,
                        message.author.id,
                    )
                    await message.channel.send(
                        f"{message.author.mention} has done some time, and is now level **{new_level}**."
                    )
                    return

    @app_commands.command(name="rank")
    async def rank_command(self, interaction: Interaction):
        """Check your level and rank.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM xp_users WHERE id = $1", interaction.user.id)
        if user is None:
            await interaction.followup.send("🚫 You aren't ranked yet. Send some messages first, then try again.")
            return

        card = functools.partial(
            self.generator.generate_profile,
            profile_image=interaction.user.avatar.url if interaction.user.avatar is not None else self.default_profile,
            level=0,
            current_xp=user["detailed_xp"][2] - user["detailed_xp"][0],
            user_xp=user["xp"],
            next_xp=user["detailed_xp"][2] - user["detailed_xp"][0] + user["detailed_xp"][1],
            user_name=f"{interaction.user.name}#{interaction.user.discriminator}",
            user_status=interaction.user.status.value if not isinstance(interaction.user.status, str) else "offline",
        )
        card = self.bot.loop.run_in_executor(card)


async def setup(bot: CBot):
    """Setup."""
    await bot.add_cog(Leveling(bot))
