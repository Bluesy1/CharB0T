# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""Gang war."""
from __future__ import annotations

from typing import cast

import asyncpg

import discord
from discord import ui

from .. import GuildComponentInteraction as CInteraction, CBot
from . import GANGS, utils


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
                    f"{details['upkeep']:.0f} rep to pay your dues."
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
            await conn.execute(
                "UPDATE gangs SET control = control + $2 WHERE name = $1",
                self.gang,
                utils.rep_to_control(
                    await conn.fetchval(
                        "SELECT "
                        "(SELECT upkeep_base + (upkeep_slope * (SELECT COUNT(*) FROM gang_members WHERE gang = $1)) "
                        "FROM gangs WHERE name = $1) AS upkeep",
                        self.gang,
                    )
                ),
            )
            await interaction.followup.send(
                f"You have paid your dues for {self.gang} Gang! You now have {remaining} rep remaining."
            )
