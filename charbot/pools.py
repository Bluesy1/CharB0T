# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
"""Reputation pools."""
import asyncio
from typing import Final

import asyncpg
import discord
from discord import Interaction, app_commands
from discord.ext import commands

from . import CBot, errors
from .card import generate_card


CHANNEL_ID: Final[int] = 969972085445238784

MESSAGE: Final = "You must be in <#969972085445238784> to participate in the pools system."


@app_commands.guild_only()
class Pools(commands.GroupCog, name="pools", description="Reputation pools for certain features."):
    """Reputation pools.

    This cog is used to display reputation pools for certain features.

    The pools are displayed in a card format, and are dynamically listed for the user to choose from based on what is
     available to them.

    The user can then choose a pool and receive a card with the pool's information, or add rep to the pool.

    Parameters
    ----------
    bot : CBot
        The bot object.

    Attributes
    ----------
    bot : CBot
        The bot object.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    async def pool_autocomplete(self, interaction: Interaction[CBot], current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete a pool name.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        current : str
            The current string.

        Returns
        -------
        list[app_commands.Choice[str]]
            The list of choices.
        """
        member = interaction.user
        assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        return [
            app_commands.Choice(name=pool["pool"], value=pool["pool"])
            for pool in await self.bot.pool.fetch("SELECT pool, required_roles FROM pools")
            if current.lower() in pool["pool"].lower()
            and any(role.id in pool["required_roles"] for role in member.roles)
        ]

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.

        Returns
        -------
        bool
            Whether the interaction is valid.

        Raises
        ------
        errors.MissingProgramRole
            If the user has no role on the list of roles.
        errors.WrongChannelError
            If the user is not in the correct channel.
        """
        member = interaction.user
        assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        roles: list[int | str] | None = await self.bot.pool.fetchval(
            "SELECT required_roles FROM pools WHERE pool = $1", interaction.namespace["pool"]
        )
        if roles is None:
            raise errors.NoPoolFound(interaction.namespace["pool"], interaction.locale)
        if all(role.id not in roles for role in member.roles):
            raise errors.NoPoolFound(interaction.namespace["pool"], interaction.locale)
        if interaction.channel_id != 969972085445238784:
            raise errors.WrongChannelError(969972085445238784, interaction.locale)
        return True

    @app_commands.command(name="add", description="Add reputation to an active pool.")
    @app_commands.autocomplete(pool=pool_autocomplete)
    @app_commands.describe(pool="The pool to add to.", amount="The amount to add.")
    async def add(self, interaction: Interaction[CBot], pool: str, amount: app_commands.Range[int, 1]):
        """Add reputation to an active pool.

        If the pool overflowed by the addition, it only fills it to the maximum.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The pool to add to.
        amount : int
            The amount to add.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            pool_record = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            assert isinstance(pool_record, asyncpg.Record)  # skipcq: BAN-B101
            if pool_record["current"] == pool_record["cap"]:
                await interaction.followup.send(f"The pool {pool} is already full. You can't add any more rep to it.")
                return
            user_record = await conn.fetchrow("SELECT * FROM users WHERE id = $1", interaction.user.id)
            if user_record is None:
                await interaction.followup.send("You haven't gained any rep yet.")
                return
            assert isinstance(user_record, asyncpg.Record)  # skipcq: BAN-B101
            if user_record["points"] < amount:
                await interaction.followup.send(
                    f"You don't have enough rep to add {amount} to the pool. you have {user_record['points']} rep."
                )
                return
            if pool_record["current"] + amount > pool_record["cap"]:
                amount = pool_record["cap"] - pool_record["current"]
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", amount, interaction.user.id
            )
            after = await conn.fetchval(
                "UPDATE pools SET current = current + $1 WHERE pool = $2 returning current", amount, pool
            )
        image_bytes = await asyncio.to_thread(
            generate_card,
            level=pool_record["level"],
            base_rep=pool_record["start"],
            current_rep=after,
            completed_rep=pool_record["cap"],
            pool_name=pool,
            reward=pool_record["reward"],
        )
        image = discord.File(image_bytes, filename=f"{pool}.png")
        await interaction.followup.send(
            f"You have added {amount} rep to {pool} you now have {remaining} rep remaining.", file=image
        )
        if after == pool_record["cap"]:
            image_bytes = await asyncio.to_thread(
                generate_card,
                level=pool_record["level"],
                base_rep=pool_record["start"],
                current_rep=after,
                completed_rep=pool_record["cap"],
                pool_name=pool,
                reward=pool_record["reward"],
            )
            image = discord.File(image_bytes, filename=f"{pool}.png")
            channel = interaction.channel
            assert isinstance(channel, discord.abc.Messageable)  # skipcq: BAN-B101
            await channel.send(f"{interaction.user.mention} has filled {pool}!", file=image)

    @app_commands.command(name="query", description="Check the status of an active pool.")
    @app_commands.autocomplete(pool=pool_autocomplete)
    @app_commands.describe(pool="The pool to check.")
    async def query(self, interaction: Interaction[CBot], pool: str):
        """Check the status of an active pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The pool to check.
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if interaction.channel_id != CHANNEL_ID:
            await interaction.response.send_message(MESSAGE, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            pool_record = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if pool is None:
                await interaction.followup.send("Pool not found. Please choose one from the autocomplete.")
                return
            assert isinstance(pool_record, asyncpg.Record)  # skipcq: BAN-B101
            if all(role.id not in pool_record["required_roles"] for role in user.roles):
                await interaction.followup.send("Pool not found. Please choose one from the autocomplete.")
                return
        image_bytes = await asyncio.to_thread(
            generate_card,
            level=pool_record["level"],
            base_rep=pool_record["start"],
            current_rep=pool_record["current"],
            completed_rep=pool_record["cap"],
            pool_name=pool,
            reward=pool_record["reward"],
        )
        await interaction.followup.send(file=discord.File(image_bytes, filename=f"{pool}.png"))


async def setup(bot: CBot):
    """Load the cog."""
    await bot.add_cog(Pools(bot))
