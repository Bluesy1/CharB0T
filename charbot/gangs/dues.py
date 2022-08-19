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
"""Gang war."""
from typing import cast

import asyncpg

import discord
from discord import ui

from .. import GuildComponentInteraction as CInteraction, CBot
from . import GANGS


class DuesButton(ui.Button):
    """Dues button."""

    def __init__(self, gang: GANGS) -> None:
        """Init."""
        super().__init__(style=discord.ButtonStyle.success, custom_id=f"dues_{gang}", label="Pay", emoji="\U0001F4B0")
        self.gang = gang

    async def callback(self, interaction: CInteraction[CBot]):
        """Buttons callback."""
        await interaction.response.defer(ephemeral=True)
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            paid: bool = await conn.fetchval("SELECT paid FROM gang_members WHERE user_id = $1", interaction.user.id)
            if paid:
                await interaction.followup.send("You have already paid your dues for this month.")
                return
            if not await conn.fetchval(
                "SELECT CASE"
                " WHEN (SELECT points FROM users WHERE id = $1) >= (SELECT upkeep_base + (upkeep_slope * ("
                "SELECT COUNT(*) FROM gang_members WHERE gang = $2)) FROM gangs WHERE name = $2)"
                " THEN TRUE ELSE FALSE END",
                interaction.user.id,
                self.gang,
            ):
                details = cast(
                    asyncpg.Record,
                    await conn.fetchrow(
                        "SELECT "
                        "(SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
                        " FROM gangs WHERE name = $1) AS upkeep,"
                        " (SELECT points FROM users WHERE id = $2) AS points",
                        self.gang,
                        interaction.user.id,
                    ),
                )
                await interaction.followup.send(
                    f"You do not have enough rep to pay your dues, you have {details['points']} rep and need "
                    f"{details['upkeep']} rep to pay your dues."
                )
                return
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - ("
                "SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1))"
                " FROM gangs WHERE name = $1) WHERE id = $2 RETURNING points",
                self.gang,
                interaction.user.id,
            )
            await conn.execute("UPDATE gang_members SET paid = TRUE WHERE user_id = $1", interaction.user.id)
            await interaction.followup.send(
                f"You have paid your dues for {self.gang} Gang! You now have {remaining} rep remaining."
            )
