"""Mod Support cog."""

import logging
import pathlib
from datetime import timedelta

import discord
import orjson
from discord import Interaction, PermissionOverwrite, Permissions, app_commands, ui
from discord.ext import tasks
from discord.ext.commands import GroupCog
from discord.utils import utcnow

from . import CBot, constants


_BLACKLIST = pathlib.Path.cwd() / "mod_support_blacklist.json"
_MOD_ROLE = 725377514414932030
_EVERYONE = 225345178955808768
_PERMS_HIDE_CHANNEL = PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False)
_PERMS_SHOW_CHANNEL = PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none())


async def edit_check(interaction: Interaction[CBot]) -> bool:
    """Check for if a user is allowed to edit the blacklist.

    Parameters
    ----------
    interaction : Interaction
        The interaction to check.

    Returns
    -------
    bool
        Whether the user is allowed to edit the blacklist.
    """
    user = interaction.user
    assert isinstance(user, discord.Member)  # skipcq: BAN-B101
    return any(role.id in constants.MOD_ROLE_IDS for role in user.roles)


@app_commands.guilds(constants.GUILD_ID)
@app_commands.default_permissions(moderate_members=True)
class ModSupport(GroupCog, name="modsupport", description="mod support command group"):
    """Mod Support Cog.

    This cog contains all the commands for the mod support system.

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
        super().__init__()
        self.bot = bot

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload func."""
        self.check_mod_support_channels.cancel()

    async def cog_load(self) -> None:
        """Cog load func."""
        self.check_mod_support_channels.start()
        self.bot.add_view(ModSupportLayout())

    @tasks.loop(hours=8)
    async def check_mod_support_channels(self):
        """Remove stale modmail channels."""
        guild = self.bot.get_guild(constants.GUILD_ID) or await self.bot.fetch_guild(constants.GUILD_ID)
        channels = await guild.fetch_channels()
        cared: list[discord.TextChannel] = [
            channel
            for channel in channels
            if channel.name.endswith("mod-support") and isinstance(channel, discord.TextChannel)
        ]
        for channel in cared:
            last = channel.last_message_id
            if last:
                last_time = discord.utils.snowflake_time(last)
                delta = utcnow() - last_time
                if delta.total_seconds() > 3 * 24 * 60 * 60:
                    await channel.delete(reason="Mod Support Channel Inactivity")
                else:
                    continue
            else:
                count = 0
                async for _ in channel.history(after=utcnow() - timedelta(days=3)):
                    count += 1
                    break
                if count == 0:
                    await channel.delete()

    @app_commands.command(name="query", description="queries list of users banned from mod support")
    async def query(self, interaction: Interaction[CBot]):
        """Modmail blacklist query command.

        This command is used to query the mod support blacklist.

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the command.
        """
        if await edit_check(interaction):
            blacklisted = [f"<@{item}>" for item in orjson.loads(_BLACKLIST.read_bytes())["blacklisted"]]
            await interaction.response.send_message(
                f"# Blacklisted users \n{'\n'.join(blacklisted)}",
                ephemeral=True,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)

    @app_commands.command(
        name="edit",
        description="adds or removes a user from the list of users banned from mod support",
    )
    async def edit(self, interaction: Interaction[CBot], add: bool, user: discord.Member):
        """Modmail edit blacklist command.

        Parameters
        ----------
        interaction: Interaction
            Interaction object invoking the command
        add: bool
            True to add to blacklist, False to remove
        user: discord.Member
            User to change
        """
        if await edit_check(interaction):
            successful = False
            modmail_blacklist = orjson.loads(_BLACKLIST.read_bytes())
            if add:
                if user.id not in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].append(user.id)
                    _BLACKLIST.write_bytes(orjson.dumps(modmail_blacklist))
                    successful = True
            elif user.id in modmail_blacklist["blacklisted"]:
                modmail_blacklist["blacklisted"].remove(user.id)
                _BLACKLIST.write_bytes(orjson.dumps(modmail_blacklist))
                successful = True
            if add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully added to the blacklist", ephemeral=True
                )
            elif add:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist or was not able to be added to.",
                    ephemeral=True,
                )
            elif successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully removed from the blacklist",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was not able to be removed from it.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)


MOD_SUPPORT_HEADER = """\
# Mod Support
Use the buttons provided to open a modmail text channel, selecting a suitable level of importance. \
You can make the modmail private to only admins, Charlie and up to 5 mods of your choosing. \
Upon selecting an option, you will be prompted to provide some information in a modal form. \
We have detailed each category below.\
"""
MOD_SUPPORT_ADMIN_DESCRIPTION = """\
For sensitive matters, this goes to admins only. This could increase wait time. \
We respect private matters unless they are important enough to inform our mod team about potential issues.
This should only be used for truly private information or if this has to do with one of our mods.\
"""


class ModSupportButton(ui.Button):
    """A button component for mod support requests.

    This button is used in the mod support UI to allow users to initiate different types of modmail requests
    (General, Important, Emergency, Private). When clicked, it checks if the user is blacklisted and, if not,
    presents a modal form for the user to provide additional information. If the user is blacklisted, an
    ephemeral message is sent denying access.
    """

    async def callback(self, interaction: Interaction[CBot]):
        """Just general and important and emergency callback helper."""
        if interaction.user.id not in orjson.loads(_BLACKLIST.read_bytes())["blacklisted"]:
            await interaction.response.send_modal(ModSupportModal(f"{self.label}-{interaction.user.name}-mod-support"))
        else:
            await interaction.response.send_message("You are not allowed to use this.", ephemeral=True)


class ModSupportLayout(ui.LayoutView):
    """Creates a mod buttons view (components v2 style).

    This view is used to create a mod support buttons view.

    Parameters
    ----------
    everyone : discord.Role
        The @everyone role for the guild.
    mod_role : discord.Role
        The mod role for the guild.
    mods : dict
        A dict of the mods in the guild.
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    container = ui.Container(
        ui.TextDisplay(MOD_SUPPORT_HEADER),
        ui.Separator(visible=True),
        ui.Section(
            ui.TextDisplay("## General"),
            ui.TextDisplay(
                "This should be where most requests go, for inquiries and requests. There is no time guarantee for this option."
            ),
            accessory=ModSupportButton(
                label="General", style=discord.ButtonStyle.success, custom_id="mod_mail_General", emoji="❔"
            ),
        ),
        ui.Section(
            ui.TextDisplay("## Important"),
            ui.TextDisplay("This is for requests that have a level of time importance, but are not urgent."),
            accessory=ModSupportButton(
                label="Important", style=discord.ButtonStyle.primary, custom_id="mod_mail_Important", emoji="❗"
            ),
        ),
        ui.Section(
            ui.TextDisplay("## Emergency"),
            ui.TextDisplay("This is for requests that need a response as soon as possible."),
            accessory=ModSupportButton(
                label="Emergency", style=discord.ButtonStyle.danger, custom_id="mod_mail_Emergency", emoji="‼"
            ),
        ),
        ui.Section(
            ui.TextDisplay("## Private (Admins Only)"),
            ui.TextDisplay(MOD_SUPPORT_ADMIN_DESCRIPTION),
            accessory=ModSupportButton(
                label="Private", style=discord.ButtonStyle.blurple, custom_id="mod_mail_Admin", emoji="🔒"
            ),
        ),
        ui.Separator(visible=True),
        ui.TextDisplay("-# Mod Support V3"),
        accent_color=0x0000FF,
    )


class ModSupportModal(ui.Modal, title="Mod Support Form"):
    """Mod Support Modal Class.

    This class is used to create a mod support modal.

    Parameters
    ----------
    perm_overrides: dict[discord.Role | discord.Member | discord.User, discord.PermissionOverwrite]
        A dictionary of role, member, and user to permission overrides.
    channel_name: str
        The name of the channel to be created on modal submit.

    Attributes
    ----------
    perm_overrides: dict[discord.Role | discord.Member | discord.Object, discord.PermissionOverwrite]
        A dictionary of role, member, and user to permission overrides.
    channel_name: str
        The name of the channel to be created on modal submit.
    filename: str
        The name of the file to be used to store the blacklist.
    """

    logger = logging.getLogger("charbot.mod_support")

    def __init__(self, channel_name: str):
        super().__init__(title="Mod Support Form")
        self.channel_name = channel_name

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check to run for all interaction instances.

        This is used to check if the interaction user is allowed to use this modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance to check.

        Returns
        -------
        bool
            Whether or not the interaction user is allowed to use this modal.
        """
        return interaction.user.id not in orjson.loads(_BLACKLIST.read_bytes())["blacklisted"]

    short_description = ui.TextInput(
        label="Short Description of your problem/query",
        style=discord.TextStyle.short,
        placeholder="Short description here ...",
        required=True,
        custom_id="Short_Description",
        max_length=100,
    )

    full_description = ui.TextInput(
        label="Full description of problem/query.",
        style=discord.TextStyle.paragraph,
        placeholder="Put your full description here ...",
        required=False,
        custom_id="Long_Description",
    )

    async def on_submit(self, interaction: Interaction[CBot]):
        """Submit callback.

        This is where the mod support form is actually submitted.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        """
        category: discord.CategoryChannel = interaction.client.get_channel(
            942578610336837632
        ) or await interaction.client.fetch_channel(942578610336837632)  # pyright: ignore[reportAssignmentType]
        guild: discord.Guild = interaction.guild  # pyright: ignore[reportAssignmentType]
        perms = {guild.get_role(_EVERYONE): _PERMS_HIDE_CHANNEL, interaction.user: _PERMS_SHOW_CHANNEL}
        if self.channel_name.startswith("Private"):
            perms[guild.get_role(_MOD_ROLE)] = _PERMS_HIDE_CHANNEL
        else:
            perms[guild.get_role(_MOD_ROLE)] = _PERMS_SHOW_CHANNEL
        channel = await guild.create_text_channel(
            self.channel_name, category=category, overwrites=perms, topic=self.short_description.value
        )
        long = "     They supplied a longer description: "
        await channel.send(
            f"{interaction.user.mention} has a new issue/question/request:\n"
            f"{self.short_description.value}."
            f"{long if self.full_description.value else ''}",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
        await interaction.response.send_message(f"Channel Created: {channel.mention}", ephemeral=True)
        if self.full_description.value:
            await channel.send(self.full_description.value)

    async def on_error(self, interaction: Interaction[CBot], error: Exception) -> None:
        """Error handler for modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        error : Exception
            The error that was raised.
        """
        await interaction.response.send_message(
            "Oh no! Something went wrong. Please ask for a mod's help in this channel and let Bluesy know.",
            ephemeral=True,
        )
        self.logger.error("Ignoring exception in modal %r.", self, exc_info=error)


async def setup(bot: CBot):
    """Load Plugin."""
    await bot.add_cog(ModSupport(bot), override=True)
