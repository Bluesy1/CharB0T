"""Admin commands for the reputation system."""

from datetime import timedelta
from typing import cast

import discord
from discord import Interaction, app_commands, ui
from discord.ext import commands
from discord.utils import format_dt, utcnow

from . import CBot, constants

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

    levels = app_commands.Group(
        name="levels",
        description="Administration commands for the leveling system.",
        guild_ids=constants.GUILD_IDS,
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
                view = ui.LayoutView()
                view.add_item(
                    ui.Container(
                        ui.TextDisplay(f"# {guild.name} NoXP Configuration"),
                        ui.TextDisplay(f"## Channels\n{'\n'.join(f'<#{c}> (`{c}`)' for c in noxp['channels'])}"),
                        ui.TextDisplay(f"## Roles\n{'\n'.join(f'<@&{r}> (`{r}`)' for r in noxp['roles'])}"),
                        ui.Separator(),
                        ui.TextDisplay(
                            f"-# Requested by {interaction.user.name} ({interaction.user.id}) at {format_dt(utcnow())}"
                        ),
                    )
                )
                await interaction.followup.send(view=view)


async def setup(bot: CBot):
    """Initialize the cog."""
    await bot.add_cog(Admin(bot))
