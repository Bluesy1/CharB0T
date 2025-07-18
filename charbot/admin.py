"""Admin commands for the reputation system."""

from datetime import timedelta
from typing import cast

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.utils import format_dt, utcnow

from . import CBot, constants


SEVEN_DAYS = timedelta(days=7)
MOD_ROLE = discord.Object(338173415527677954)


@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_any_role(*constants.MOD_ROLE_IDS)
@app_commands.guilds(constants.GUILD_ID)
class Admin(
    commands.GroupCog,
    group_name="admin",
    group_description="Administration commands for the server/bot.",
):
    """Reputation Admin Commands.

    These commands are used to manage the the server/bot.

    Parameters
    ----------
    bot : CBot
        The bot object.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    tags = app_commands.Group(
        name="tags",
        description="Administration commands for moderating guild tags.",
        guild_ids=constants.GUILD_IDS,
    )
    levels = app_commands.Group(
        name="levels",
        description="Administration commands for the leveling system.",
        guild_ids=constants.GUILD_IDS,
    )

    @tags.command()
    async def check(self, interaction: Interaction[CBot]):
        """Lists tags members with a tag on the server, that is not present on a moderator's account.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        """
        await interaction.response.defer()
        guild = cast(discord.Guild, interaction.guild)
        members = [
            member for member in guild.members if member.primary_guild.identity_enabled and member.primary_guild.tag
        ]
        mod_tags = {
            member.primary_guild.id
            for member in members
            if any(member.get_role(role) for role in constants.MOD_ROLE_IDS)
        }
        tags = {member.primary_guild.id for member in members} - mod_tags
        message = "\n".join(
            f"- {member.mention} ({member.id}): `{member.primary_guild.tag.casefold()}`"  # pyright: ignore[reportOptionalMemberAccess]
            for member in members
            if member.primary_guild.id in tags
        )
        await interaction.followup.send(f"Users with tags not shared by a moderator:\n{message}", allowed_mentions=discord.AllowedMentions.none())

    @tags.command()
    async def warn(
        self,
        interaction: Interaction[CBot],
        member: discord.Member,
    ):
        """Sends a user a warning that they have an unacceptable server tag active.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        member : discord.Member
            The member to warn.
        """
        await interaction.response.defer()
        guild = cast(discord.Guild, interaction.guild)
        deadline = utcnow() + SEVEN_DAYS
        tag = member.primary_guild.tag
        warn_msg = (
            f"Hi {member.mention}, we noticed that you have an inappropriate Server Tag active, ``{tag}``.\n"
            f"Please remove or change your tag by {format_dt(deadline)} ({format_dt(deadline, 'R')}) "
            f"or we will have to kick you from {guild.name}.\n"
            "Thanks in advance for your cooperation."
        )
        try:
            await member.send(warn_msg)
        except discord.HTTPException:
            # Cannot DM the user, blocked | left server? Create a mod support ticket instead....
            category: discord.CategoryChannel = discord.Object(942578610336837632, type=discord.CategoryChannel)  # pyright: ignore[reportAssignmentType]
            permissions = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False, send_messages=False, read_messages=False
                ),
                MOD_ROLE: discord.PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
                member: discord.PermissionOverwrite.from_pair(
                    discord.Permissions(139586817088), discord.Permissions.none()
                ),
            }
            channel = await guild.create_text_channel(
                f"Tag-{member.name}-mod-support", category=category, overwrites=permissions
            )
            await channel.send(warn_msg)
        await interaction.followup.send(
            f"{member.mention} has successfully been warned about their selected server tag."
        )

    @tags.command()
    async def kick(
        self,
        interaction: Interaction[CBot],
        member: discord.Member,
    ):
        """Kick a member for having an unacceptable server tag active.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        member : discord.Member
            The member to kick.
        """
        await interaction.response.defer()
        allowed = interaction.permissions.kick_members or await interaction.client.is_owner(interaction.user)
        tag = member.primary_guild.tag
        if not allowed:
            await interaction.followup.send(
                f"Cannot kick {member}: you do not have kick members and are not a bot owner."
            )
            return
        guild = cast(discord.Guild, interaction.guild)
        kick_msg = (
            f"Hi {member.mention}, we noticed that you have an inappropriate Server Tag active, ``{tag}``.\n"
            f"We have had to kick you from {guild.name}, feel free to rejoin once you change or remove your tag: "
            "http://cpry.net/discord"
        )
        try:
            await member.send(kick_msg)
        except discord.HTTPException:
            notified = False
        else:
            notified = True
        try:
            await member.kick(reason=f"User had an inappropriate tag: {tag}")
        except discord.HTTPException:
            await interaction.followup.send(
                f"Failed to kick {member.mention} (id {member.id}) was kicked for their tag ``{tag}``. (Notified of kick successfully: {notified})."
            )
        else:
            await interaction.followup.send(
                f"{member} (id {member.id}) was kicked for their tag ``{tag}`` successfully. (Notified of kick successfully: {notified})."
            )

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
                embed.add_field(
                    name="Channels",
                    value=", ".join(f"<#{c}>" for c in noxp["channels"]),
                    inline=False,
                )
                embed.add_field(name="Roles", value=", ".join(f"<@&{r}>" for r in noxp["roles"]), inline=False)
                await interaction.followup.send(embed=embed)


async def setup(bot: CBot):
    """Initialize the cog."""
    await bot.add_cog(Admin(bot))
