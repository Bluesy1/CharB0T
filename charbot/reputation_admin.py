"""Admin commands for the reputation system."""

from typing import cast

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.utils import utcnow

from . import CBot


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
        self.ctx_menu = app_commands.ContextMenu(name="Check User's Reputation", callback=self.check_reputation_context)
        self.bot.tree.add_command(self.ctx_menu)
        self._allowed_roles: list[int | str] = [
            225413350874546176,
            253752685357039617,
            725377514414932030,
            338173415527677954,
        ]

    @property
    def allowed_roles(self) -> list[int | str]:
        """Allow roles."""
        return self._allowed_roles

    async def cog_unload(self) -> None:
        """Unload the cog."""
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

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
        member = interaction.user
        if not isinstance(member, discord.Member):
            raise app_commands.NoPrivateMessage("This command can't be used in DMs.")
        if all(role.id not in self.allowed_roles for role in member.roles):
            raise app_commands.MissingAnyRole(self.allowed_roles)
        return True

    @reputation.command()
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
                client_user = cast(discord.ClientUser, self.bot.user)
                await self.bot.program_logs.send(
                    f"{user.mention} now has {new_points} reputation by {interaction.user.mention} ({amount} added).",
                    allowed_mentions=_ALLOWED_MENTIONS,
                    username=client_user.name,
                    avatar_url=client_user.display_avatar.url,
                )

    @reputation.command()
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
                client_user = cast(discord.ClientUser, self.bot.user)
                await self.bot.program_logs.send(
                    f"{user.mention} now has {new_points} reputation by {interaction.user.mention} ({amount} removed).",
                    allowed_mentions=_ALLOWED_MENTIONS,
                    username=client_user.name,
                    avatar_url=client_user.display_avatar.url,
                )

    @reputation.command()
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

    @levels.command()
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
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", interaction.guild_id)
            if no_xp is None:
                await interaction.followup.send("Xp is not set up??.")
            elif role.id in no_xp["roles"]:
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

    @levels.command()
    async def no_xp_channel(self, interaction: Interaction[CBot], channel: discord.TextChannel | discord.VoiceChannel):
        """Toggles a channels ability to block xp gain.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        channel: discord.TextChannel | discord.VoiceChannel
            The role to toggle.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn, conn.transaction():
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", interaction.guild_id)
            if no_xp is None:
                await interaction.followup.send("Xp is not set up??.")
            elif channel.id in no_xp["channels"]:
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

    @levels.command()
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
                guild = cast(discord.Guild, interaction.guild)
                embed = discord.Embed(title="Noxp", description="", timestamp=utcnow())
                embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}",
                    icon_url=(
                        interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                    ),
                )
                embed.add_field(name="Channels", value=", ".join(f"<#{c}>" for c in noxp["channels"]), inline=False)
                embed.add_field(name="Roles", value=", ".join(f"<@&{r}>" for r in noxp["roles"]), inline=False)
                await interaction.followup.send(embed=embed)


async def setup(bot: CBot):
    """Initialize the cog."""
    await bot.add_cog(ReputationAdmin(bot))
