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
"""Admin commands for the reputation system."""
import asyncio
import datetime
from typing import Optional

import asyncpg
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import utcnow

from . import CBot, GuildInteraction as Interaction
from .card import generate_card


_ALLOWED_MENTIONS = discord.AllowedMentions(roles=False, users=False, everyone=False)


@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_any_role(225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954)
@app_commands.guild_only()
class ReputationAdmin(
    commands.GroupCog, group_name="admin", group_description="Administration commands for the reputation system."
):
    """Reputation Admin Commands.

    These commands are used to manage the reputation system.

    Parameters
    ----------
    bot : CBot
        The bot object.
    """

    def __init__(self, bot: CBot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Check User's Reputation",
            callback=self.check_reputation_context,  # pyright: ignore[reportGeneralTypeIssues]
        )
        self.bot.tree.add_command(self.ctx_menu)
        self._allowed_roles: list[int | str] = [
            225413350874546176,
            253752685357039617,
            725377514414932030,
            338173415527677954,
        ]

        # noinspection PyUnusedLocal
        @self.edit_pool.autocomplete("pool")
        @self.pool_role.autocomplete("pool")
        @self.check_pool.autocomplete("pool")
        @self.delete_pool.autocomplete("pool")  # pyright: ignore[reportGeneralTypeIssues]
        async def pool_autocomplete(
            interaction: Interaction[CBot], current: str  # skipcq: PYL-W0613
        ) -> list[app_commands.Choice[str]]:
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
            return [
                app_commands.Choice(name=pool["pool"], value=pool["pool"])
                for pool in await self.bot.pool.fetch("SELECT pool FROM pools")
                if current.lower() in pool["pool"].lower()
            ]

    @property
    def allowed_roles(self) -> list[int | str]:
        """Allow roles."""
        return self._allowed_roles

    async def cog_load(self) -> None:
        """Load the cog."""
        self._del_role.start()

    async def cog_unload(self) -> None:
        """Unload the cog."""
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        self._del_role.cancel()

    pools = app_commands.Group(name="pools", description="Administration commands for the reputation pools.")
    reputation = app_commands.Group(name="reputation", description="Administration commands for the reputation system.")
    levels = app_commands.Group(name="levels", description="Administration commands for the leveling system.")

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is allowed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.

        Returns
        -------
        bool
            Whether the interaction is allowed.
        """
        try:
            member = interaction.user
            assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        except AssertionError:
            raise app_commands.NoPrivateMessage("This command can't be used in DMs.")
        else:
            if not any(role.id in self.allowed_roles for role in member.roles):
                raise app_commands.MissingAnyRole(self.allowed_roles)
            return True

    @pools.command(name="create")  # pyright: ignore[reportGeneralTypeIssues]
    async def create_pool(
        self,
        interaction: Interaction[CBot],
        name: str,
        capacity: int,
        reward: str,
        role: discord.Role,
        level: app_commands.Range[int, 1] = 1,
        current: app_commands.Range[int, 0] = 0,
        start: app_commands.Range[int, 0] = 0,
        role1: Optional[discord.Role] = None,
        role2: Optional[discord.Role] = None,
        role3: Optional[discord.Role] = None,
        role4: Optional[discord.Role] = None,
        role5: Optional[discord.Role] = None,
        role6: Optional[discord.Role] = None,
        role7: Optional[discord.Role] = None,
        role8: Optional[discord.Role] = None,
        role9: Optional[discord.Role] = None,
        role10: Optional[discord.Role] = None,
        role11: Optional[discord.Role] = None,
        role12: Optional[discord.Role] = None,
        role13: Optional[discord.Role] = None,
        role14: Optional[discord.Role] = None,
        role15: Optional[discord.Role] = None,
        role16: Optional[discord.Role] = None,
        role17: Optional[discord.Role] = None,
        role18: Optional[discord.Role] = None,
    ):
        """Create a new reputation pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction to use.
        name : str
            The name of the pool. Must be unique.
        capacity : int
            How many reputation points the pool can hold.
        reward : str
            The reward for completing the pool. Max 65 characters.
        role : discord.Role
            A role to whitelist to participate in the pool. role1 to 19 allow additional roles to participate.
        level : app_commands.Range[int, 1]
            Level of the pool. Default is 1. If set to a number other than 1, current and start are required.
        current : app_commands.Range[int, 0]
            The current reputation points in the pool. Default is 0. Must be above 0 if level is not 1
        start : app_commands.Range[int, 0]
            The base reputation for the pool level. Default is 0. Must be above 0 if level is not 1
        role1 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role2 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role3 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role4 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role5 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role6 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role7 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role8 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role9 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role10 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role11 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role12 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role13 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role14 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role15 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role16 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role17 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        role18 : discord.Role
            [OPTIONAL] Additional slot for a role to whitelist to participate in the pool.
        """
        if level != 1 and 0 in (current, start):
            await interaction.response.send_message(
                "Error: Level is not 1, but current and start are not set.", ephemeral=True
            )
            return
        if len(name) > 32:
            await interaction.response.send_message("Error: Name must be 32 characters or less.", ephemeral=True)
            return
        if len(reward) > 65:
            await interaction.response.send_message("Error: Reward must be 65 characters or less.", ephemeral=True)
            return
        _pool = await self.bot.pool.fetchrow("SELECT * FROM pools WHERE pool = $1", name)
        if _pool is not None:
            await interaction.response.send_message("Error: Pool already exists.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        _roles = [
            role,
            role1,
            role2,
            role3,
            role4,
            role5,
            role6,
            role7,
            role8,
            role9,
            role10,
            role11,
            role12,
            role13,
            role14,
            role15,
            role16,
            role17,
            role18,
        ]
        roles = list({r.id for r in filter(lambda x: x is not None, _roles)})
        await self._finish_pool_create(interaction, name, reward, capacity, level, current, start, roles)

    async def _finish_pool_create(
        self,
        interaction: Interaction[CBot],
        name: str,
        reward: str,
        capacity: int,
        level: int,
        current: int,
        start: int,
        roles: list[int],
    ):
        """Finish the pool creation process.

        Parameters
        ----------
        interaction : Interaction
            The interaction to respond to.
        name : str
            The name of the pool.
        reward : str
            The reward for the pool.
        capacity : int
            The capacity of the pool.
        level : int
            The level of the pool.
        current : int
            The current reputation of the pool.
        start : int
            The starting reputation of the pool.
        roles : list[int]
            The roles that can participate in the pool.
        """
        await self.bot.pool.execute(
            "INSERT INTO pools (pool, cap, reward, required_roles, level, current, start)"
            " VALUES ($1, $2, $3, $4, $5, $6, $7)",
            name,
            capacity,
            reward,
            roles,
            level,
            current,
            start,
        )
        image_bytes = await asyncio.to_thread(
            generate_card,
            level=level,
            base_rep=start,
            current_rep=current,
            completed_rep=capacity,
            pool_name=name,
            reward=reward,
        )
        image = discord.File(image_bytes, f"{name}.png")
        await interaction.followup.send(f"Pool {name} created with reward {reward}!", file=image)
        clientuser = self.bot.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        await self.bot.program_logs.send(
            f"Pool {name} created with reward {reward} by {interaction.user.mention}.",
            allowed_mentions=_ALLOWED_MENTIONS,
            username=clientuser.name,
            avatar_url=clientuser.display_avatar.url,
        )

    @pools.command(name="edit")  # pyright: ignore[reportGeneralTypeIssues]
    async def edit_pool(
        self,
        interaction: Interaction[CBot],
        pool: str,
        name: Optional[str] = None,
        capacity: Optional[app_commands.Range[int, 0]] = None,
        reward: Optional[str] = None,
        level: Optional[app_commands.Range[int, 1]] = None,
        current: Optional[app_commands.Range[int, 0]] = None,
        start: Optional[app_commands.Range[int, 0]] = None,
    ):
        """Edit a pool. Options left out will not be changed.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The name of the pool to edit. Use the autocomplete feature to find the pool.
        name : str
            The new name of the pool. Must be 32 characters or fewer.
        capacity : int
            The new capacity of the pool.
        reward : str
            The new reward of the pool. Must be 65 characters or fewer.
        level : int
            The new level of the pool. Must be at least 1 if supplied, current and start must be supplied.
        current : int
            The new current rep of the pool. Must be at least 0 and set above 0 if level is 1.
        start : int
            The new base rep for the pool level. Must be at least 0 and set above 0 if level is 1.
        """
        if level is not None and level > 1 and any(i in (current, start) for i in (0, None)):
            await interaction.response.send_message(
                "Error: Current and start must be supplied and greater than 0 if level is 1.", ephemeral=True
            )
            return
        if (name is not None and len(name) > 32) or (reward is not None and len(reward) > 65):
            await interaction.response.send_message(
                "Error: Name must be 32 or less and/or reward must be 65 or less characters", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            _pool = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if name is not None and await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", name) is not None:
                await interaction.followup.send(f"Error: Pool {name} already exists, try again.")
                return
        if _pool is None:
            await interaction.followup.send(f"Error: Pool {pool} does not exist.")
        else:
            await self._finish_pool_edit(interaction, _pool, pool, name, capacity, reward, level, current, start)
            clientuser = self.bot.user
            assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
            await self.bot.program_logs.send(
                f"Pool {name or pool}{f' (formerly {pool})' if name is not None else ''}"
                f" edited by {interaction.user.mention}.",
                allowed_mentions=_ALLOWED_MENTIONS,
                username=clientuser.name,
                avatar_url=clientuser.display_avatar.url,
            )

    async def _finish_pool_edit(
        self,
        interaction: Interaction[CBot],
        previous: asyncpg.Record,
        pool: str,
        name: str | None,
        capacity: int | None,
        reward: str | None,
        level: int | None,
        current: int | None,
        start: int | None,
    ):
        """Finish the pool edit process.

        Parameters
        ----------
        interaction : Interaction
            The interaction to respond to.
        previous : asyncpg.Record
            The previous pool record.
        pool : str
            The name of the pool.
        name : str | None
            The new name of the pool.
        capacity : int | None
            The new capacity of the pool.
        reward : str | None
            The new reward of the pool.
        level : int | None
            The new level of the pool.
        current : int | None
            The new current rep of the pool.
        start : int | None
            The new base rep for the pool level.
        """
        await self.bot.pool.execute(
            "UPDATE pools SET pool = $1, cap = $2, reward = $3, level = $4, current = $5, start = $6"
            " WHERE pool = $7",
            name or pool,
            capacity if capacity is not None else previous["cap"],
            reward or previous["reward"],
            level if level is not None else previous["level"],
            current if current is not None else previous["current"],
            start if start is not None else previous["start"],
            pool,
        )
        image_bytes = await asyncio.to_thread(
            generate_card,
            level=level if level is not None else previous["level"],
            base_rep=start if start is not None else previous["start"],
            current_rep=current if current is not None else previous["current"],
            completed_rep=capacity if capacity is not None else previous["cap"],
            pool_name=name or pool,
            reward=reward or previous["reward"],
        )
        image = discord.File(image_bytes, f"{previous['pool']}.png")
        await interaction.followup.send(
            f"Pool {name or pool}{f' (formerly {pool})' if name is not None else ''} edited!", file=image
        )

    @pools.command(name="list")  # pyright: ignore[reportGeneralTypeIssues]
    async def list_pools(self, interaction: Interaction[CBot]):
        """List all pools.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            pools = [pool["pool"] for pool in await conn.fetch("SELECT pool FROM pools")]
            await interaction.followup.send(f"Pools: {', '.join(pools)}")

    @pools.command(name="role")  # pyright: ignore[reportGeneralTypeIssues]
    async def pool_role(self, interaction: Interaction[CBot], pool: str, role: discord.Role):
        """Toggle a role's ability to participate in a pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The name of the pool. Use the autocomplete feature to find the pool.
        role : discord.Role
            The role to toggle.
        """
        await interaction.response.defer(ephemeral=True)
        clientuser = self.bot.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        async with self.bot.pool.acquire() as conn, conn.transaction():
            _pool = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if _pool is None:
                await interaction.followup.send(f"Error: Pool `{pool}` not found.")
            else:
                if role.id in _pool["required_roles"]:
                    await conn.execute(
                        "UPDATE pools SET required_roles = array_remove(required_roles, $1) WHERE pool = $2",
                        role.id,
                        pool,
                    )
                    await interaction.followup.send(f"Role `{role.name}` removed from pool `{pool}`.")
                    await self.bot.program_logs.send(
                        f"Role `{role.name}` removed from pool `{pool}` by {interaction.user.mention}.",
                        allowed_mentions=_ALLOWED_MENTIONS,
                        username=clientuser.name,
                        avatar_url=clientuser.display_avatar.url,
                    )
                else:
                    await conn.execute(
                        "UPDATE pools SET required_roles = array_append(required_roles, $1) WHERE pool = $2",
                        role.id,
                        pool,
                    )
                    await interaction.followup.send(f"Role `{role.name}` added to pool `{pool}`.")
                    await self.bot.program_logs.send(
                        f"Role `{role.name}` added to pool `{pool}` by {interaction.user.mention}.",
                        allowed_mentions=_ALLOWED_MENTIONS,
                        username=clientuser.name,
                        avatar_url=clientuser.display_avatar.url,
                    )

    @pools.command(name="delete")  # pyright: ignore[reportGeneralTypeIssues]
    async def delete_pool(self, interaction: Interaction[CBot], pool: str):
        """Delete a pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The name of the pool. Use the autocomplete feature to find the pool.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            _pool = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if _pool is None:
                await interaction.followup.send(f"Error: Pool `{pool}` not found.")
            else:
                await conn.execute("DELETE FROM pools WHERE pool = $1", pool)
                await interaction.followup.send(f"Pool `{pool}` deleted.")
                clientuser = self.bot.user
                assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
                await self.bot.program_logs.send(
                    f"Pool `{pool}` deleted by {interaction.user.mention}.",
                    allowed_mentions=_ALLOWED_MENTIONS,
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                )

    @pools.command(name="check")  # pyright: ignore[reportGeneralTypeIssues]
    async def check_pool(self, interaction: Interaction[CBot], pool: str):
        """Check a pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The name of the pool. Use the autocomplete feature to find the pool.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            _pool = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if _pool is None:
                await interaction.followup.send(f"Error: Pool `{pool}` not found.")
            else:
                image_bytes = await asyncio.to_thread(
                    generate_card,
                    level=_pool["level"],
                    base_rep=_pool["start"],
                    current_rep=_pool["current"],
                    completed_rep=_pool["cap"],
                    pool_name=pool,
                    reward=_pool["reward"],
                )
                image = discord.File(image_bytes, f"{_pool['pool']}.png")
                await interaction.followup.send(
                    f"Pool `{pool}`: {_pool['level']} level pool with {_pool['start']} base rep, {_pool['current']}"
                    f" current rep, {_pool['cap']} completed rep, and {_pool['reward']} reward. "
                    f"and allowed for roles: <@&{'>, <@&'.join(str(role) for role in _pool['required_roles'])}>",
                    file=image,
                    allowed_mentions=_ALLOWED_MENTIONS,
                )

    @reputation.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def add_reputation(self, interaction: Interaction[CBot], user: discord.User, amount: int):
        """Add reputation to a user.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : discord.User
            The user to add reputation to.
        amount : int
            The amount of reputation to add.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            _user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
            if _user is None:
                await interaction.followup.send(f"Error: User `{user.name}` not found as active.")
            else:
                new_points: int = await conn.fetchval(
                    "UPDATE users SET points = points + $1 WHERE id = $2 RETURNING points", amount, user.id
                )
                await interaction.followup.send(f"User `{user.name}` now has {new_points} reputation.")
                clientuser = self.bot.user
                assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
                await self.bot.program_logs.send(
                    f"{user.mention} now has {new_points} reputation by {interaction.user.mention} ({amount} added).",
                    allowed_mentions=_ALLOWED_MENTIONS,
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                )

    @reputation.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def remove_reputation(self, interaction: Interaction[CBot], user: discord.User, amount: int):
        """Remove reputation from a user.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : discord.User
            The user to remove reputation from.
        amount : int
            The amount of reputation to remove.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            _user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
            if _user is None:
                await interaction.followup.send(f"Error: User `{user.name}` not found as active.")
            else:
                if amount > _user["points"]:
                    overflow = amount - _user["points"]
                    amount = _user["points"]
                else:
                    overflow = 0
                new_points: int = await conn.fetchval(
                    "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", amount, user.id
                )
                await interaction.followup.send(
                    f"User `{user.name}` now has {new_points} reputation. {overflow} reputation overflow."
                )
                clientuser = self.bot.user
                assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
                await self.bot.program_logs.send(
                    f"{user.mention} now has {new_points} reputation by {interaction.user.mention} ({amount} removed).",
                    allowed_mentions=_ALLOWED_MENTIONS,
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                )

    @reputation.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def check_reputation(self, interaction: Interaction[CBot], user: discord.User):
        """Check a user's reputation.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : discord.User
            The user to check.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            _user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
            if _user is None:
                await interaction.followup.send(f"Error: User `{user.name}` not found as active.")
            else:
                await interaction.followup.send(f"User `{user.name}` has {_user['points']} reputation.")

    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_any_role(225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954)
    async def check_reputation_context(self, interaction: Interaction[CBot], user: discord.User):
        """Check a user's reputation.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : discord.User
            The user to check.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            _user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
            if _user is None:
                await interaction.followup.send(f"Error: User `{user.name}` not found as active.")
            else:
                await interaction.followup.send(f"User `{user.name}` has {_user['points']} reputation.")

    @levels.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def noxp_role(self, interaction: Interaction[CBot], role: discord.Role):
        """Toggles a roles ability to block xp gain.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        role : discord.Role
            The role to toggle.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            noxp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", interaction.guild_id)
            if noxp is None:
                await interaction.followup.send("Xp is not set up??.")
            else:
                if role.id in noxp["roles"]:
                    await conn.execute(
                        "UPDATE no_xp SET roles = array_remove(roles, $1) WHERE guild = $2",
                        role.id,
                        interaction.guild_id,
                    )
                    await interaction.followup.send(f"Role `{role.name}` removed from noxp.")
                else:
                    await conn.execute(
                        "UPDATE no_xp SET roles = array_append(roles, $1) WHERE guild = $2",
                        role.id,
                        interaction.guild_id,
                    )
                    await interaction.followup.send(f"Role `{role.name}` added to noxp.")

    @levels.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def noxp_channel(self, interaction: Interaction[CBot], channel: discord.TextChannel | discord.VoiceChannel):
        """Toggles a chanels ability to block xp gain.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        channel: discord.TextChannel | discord.VoiceChannel
            The role to toggle.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            noxp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", interaction.guild_id)
            if noxp is None:
                await interaction.followup.send("Xp is not set up??.")
            else:
                if channel.id in noxp["channels"]:
                    await conn.execute(
                        "UPDATE no_xp SET channels = array_remove(channels, $1) WHERE guild = $2",
                        channel.id,
                        interaction.guild_id,
                    )
                    await interaction.followup.send(f"{channel.mention} removed from noxp.")
                else:
                    await conn.execute(
                        "UPDATE no_xp SET channels = array_append(channels, $1) WHERE guild = $2",
                        channel.id,
                        interaction.guild_id,
                    )
                    await interaction.followup.send(f"{channel.mention} added to noxp.")

    @levels.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def noxp_query(self, interaction: Interaction[CBot]):
        """Sees the channels and roles that are banned from gaining xp.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            noxp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", interaction.guild_id)
            if noxp is None:
                await interaction.followup.send("Xp is not set up??.")
            else:
                guild = interaction.guild
                assert isinstance(guild, discord.Guild)  # skipcq: BAN-B101
                embed = discord.Embed(title="Noxp", description="", timestamp=utcnow())
                embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}",
                    icon_url=interaction.user.avatar.url
                    if interaction.user.avatar
                    else interaction.user.default_avatar.url,
                )
                embed.add_field(name="Channels", value=", ".join(f"<#{c}>" for c in noxp["channels"]), inline=False)
                embed.add_field(name="Roles", value=", ".join(f"<@&{r}>" for r in noxp["roles"]), inline=False)
                await interaction.followup.send(embed=embed)

    @app_commands.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def deal_role(
        self,
        interaction: Interaction[CBot],
        user: discord.Member,
        color: str,
        days: app_commands.Range[int, 1, 28],
        above: discord.Role,
        hoist: bool = False,
    ):
        """Give a user a role that lasts for a certain amount of days.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : discord.Member
            The user to give the role to.
        color : str
            The color of the role.
        days : app_commands.Range[int, 0, 28]
            The amount of days the role lasts.
        above : discord.Role
            The role that the new role should be moved above.
        hoist : bool
            Whether the role should be hoisted.
        """
        await interaction.response.defer(ephemeral=True)
        try:
            _color = discord.Color.from_str(color)
        except ValueError:
            await interaction.followup.send("Invalid color, it is being ignored.")
            _color = discord.utils.MISSING
        role = await interaction.guild.create_role(
            name=f"{user.name}'s deal",
            color=_color,
            hoist=hoist,
            permissions=discord.Permissions(139589959744),
            reason=f"{interaction.user} (id: {interaction.user.id}) requested a deal or no deal role role for"
            f" {user.name} (id: {user.id})",
        )
        await interaction.guild.edit_role_positions({role: above.position + 1}, reason="Correct placement of deal role")
        await self.bot.pool.execute(
            "INSERT INTO deal_no_deal (user_id, role_id, until) VALUES ($1, $2, $3)",
            user.id,
            role.id,
            utcnow() + datetime.timedelta(days=days),
        )
        await interaction.followup.send(
            f"{user.mention} has been given their deal role for {days} days.", ephemeral=True
        )
        try:
            self._del_role.start()
        except RuntimeError:
            pass

    @tasks.loop(hours=1)
    async def _del_role(self):
        """Removes the deal role from users who have it."""
        async with self.bot.pool.acquire() as conn, conn.transaction():
            rle = await conn.fetchrow("SELECT * FROM deal_no_deal ORDER BY until LIMIT 1")
            if rle is None:
                self._del_role.stop()
                return
            guild = self.bot.get_guild(225345178955808768) or await self.bot.fetch_guild(225345178955808768)
            role = guild.get_role(rle["role_id"])
            if role is not None:
                await role.delete(reason="Deal role expired")
            await conn.execute("DELETE FROM deal_no_deal WHERE role_id = $1", rle["id"])
            if len(await conn.fetch("SELECT * FROM deal_no_deal")) == 0:
                self._del_role.stop()


async def setup(bot: CBot):
    """Initialize the cog."""
    await bot.add_cog(ReputationAdmin(bot))
