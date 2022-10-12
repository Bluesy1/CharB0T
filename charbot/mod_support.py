# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
"""Mod Support cog."""
import logging
import pathlib
from datetime import timedelta
from typing import Final, Any

import discord
import orjson
from discord import Embed, Interaction, PermissionOverwrite, Permissions, app_commands, ui
from discord.ext import tasks
from discord.ext.commands import GroupCog
from discord.ui import Item
from discord.utils import utcnow

from . import CBot


async def edit_check(interaction: Interaction) -> bool:
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
    return any(
        role.id in (225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954)
        for role in user.roles
    )


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
        super(ModSupport, self).__init__()
        self.bot = bot
        self.blacklist_path: Final[pathlib.Path] = pathlib.Path(__file__).parent / "mod_support_blacklist.json"

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload func."""
        self.check_mod_support_channels.cancel()

    async def cog_load(self) -> None:
        """Cog load func."""
        self.check_mod_support_channels.start()
        guild = self.bot.get_guild(225345178955808768)
        if guild is None:
            guild = await self.bot.fetch_guild(225345178955808768)
        everyone = guild.default_role
        mod_roles = guild.get_role(338173415527677954)
        assert isinstance(mod_roles, discord.Role)  # skipcq: BAN-B101
        mods = {
            "146285543146127361": await guild.fetch_member(146285543146127361),
            "363095569515806722": await guild.fetch_member(363095569515806722),
            "138380316095021056": await guild.fetch_member(138380316095021056),
            "162833689196101632": await guild.fetch_member(162833689196101632),
            "82495450153750528": await guild.fetch_member(82495450153750528),
        }
        self.bot.add_view(ModSupportButtons(everyone, mod_roles, mods))

    @tasks.loop(hours=8)
    async def check_mod_support_channels(self):
        """Remove stale modmail channels."""
        guild = self.bot.get_guild(225345178955808768)
        if guild is None:
            guild = await self.bot.fetch_guild(225345178955808768)
        channels = await guild.fetch_channels()
        cared: list[discord.TextChannel] = [
            channel
            for channel in channels
            if channel.name.endswith("mod-support") and isinstance(channel, discord.TextChannel)
        ]
        for channel in cared:
            temp = True
            async for message in channel.history(after=utcnow() - timedelta(days=3)):
                user = self.bot.user
                assert isinstance(user, discord.ClientUser)  # skipcq: BAN-B101
                if message.author.id == user.id:
                    continue
                temp = False
                break
            if temp:
                await channel.delete()

    @app_commands.command(name="query", description="queries list of users banned from mod support")
    @app_commands.guild_only()
    async def query(self, interaction: Interaction):
        """Modmail blacklist query command.

        This command is used to query the mod support blacklist.

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the command.
        """
        if await edit_check(interaction):
            with open(self.blacklist_path, "rb") as file:
                blacklisted = [f"<@{item}>" for item in orjson.loads(file.read())["blacklisted"]]
            await interaction.response.send_message(
                embed=Embed(title="Blacklisted users", description="\n".join(blacklisted)),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)

    @app_commands.command(
        name="edit",
        description="adds or removes a user from the list of users banned from mod" " support",
    )
    @app_commands.guild_only()
    async def edit(self, interaction: Interaction, add: bool, user: discord.Member):
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
            with open(self.blacklist_path, "rb") as file:
                modmail_blacklist = orjson.loads(file.read())
            if add:
                if user.id not in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].append(user.id)
                    with open(self.blacklist_path, "wb") as file:
                        file.write(orjson.dumps(modmail_blacklist))
                    successful = True
            elif user.id in modmail_blacklist["blacklisted"]:
                modmail_blacklist["blacklisted"].remove(user.id)
                with open(self.blacklist_path, "wb") as file:
                    file.write(orjson.dumps(modmail_blacklist))
                successful = True
            if add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully added to the blacklist", ephemeral=True
                )
            elif add:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist" f" or was not able to be added to.",
                    ephemeral=True,
                )
            elif successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully removed from the blacklist",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was" f" not able to be removed from it.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)


class ModSupportButtons(ui.View):
    """Creates a mod support buttons view.

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

    _PRIVATE_OPTIONS = [
        discord.SelectOption(label="Admins Only", value="146285543146127361"),
        discord.SelectOption(label="Bluesy", value="363095569515806722"),
        discord.SelectOption(label="Krios", value="138380316095021056"),
        discord.SelectOption(label="Mike Takumi", value="162833689196101632"),
        discord.SelectOption(label="Kaitlin", value="82495450153750528"),
    ]

    def __init__(
        self,
        everyone: discord.Role,
        mod_role: discord.Role,
        mods: dict[str, discord.Member],
    ):
        super().__init__(timeout=None)
        self.everyone = everyone
        self.mod_role = mod_role
        self.mods = mods
        self.filename: Final[pathlib.Path] = pathlib.Path(__file__).parent / "mod_support_blacklist.json"

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check to run for all interaction instances.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance to check.

        Returns
        -------
        bool
            True if the interaction should be run, False otherwise.
        """
        with open(self.filename, "rb") as file:
            return interaction.user.id not in orjson.loads(file.read())["blacklisted"]

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        """On error logger"""
        logging.getLogger("charbot.mod_support").error(
            "Ignoring exception in view %r for item %r, with user %s", self, item, interaction.user, exc_info=error
        )

    async def standard_callback(self, button: discord.ui.Button, interaction: Interaction):
        """Just general and important and emergency callback helper.

        This is the callback for all buttons.

        Parameters
        ----------
        button : discord.ui.Button
            The button that was pressed
        interaction : Interaction
            The interaction instance
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        await interaction.response.send_modal(
            ModSupportModal(
                {
                    self.mod_role: PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none()),
                    self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
                    user: PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none()),
                },
                f"{button.label}-{user.name}-mod-support",
            )
        )

    @ui.button(
        label="General",
        style=discord.ButtonStyle.success,
        custom_id="Modmail_General",
        emoji="❔",
        row=0,
    )
    async def general(self, interaction: Interaction, button: discord.ui.Button):
        """General mod support callback.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance
        button : discord.ui.Button
            The button instance
        """
        await self.standard_callback(button, interaction)

    @ui.button(
        label="Important",
        style=discord.ButtonStyle.primary,
        custom_id="Modmail_Important",
        emoji="❗",
        row=0,
    )
    async def important(self, interaction: Interaction, button: discord.ui.Button):
        """Mod support callback for important issues.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance
        button : discord.ui.Button
            The button instance
        """
        await self.standard_callback(button, interaction)

    @ui.button(
        label="Emergency",
        style=discord.ButtonStyle.danger,
        custom_id="Modmail_Emergency",
        emoji="‼",
        row=0,
    )
    async def emergency(self, interaction: Interaction, button: discord.ui.Button):
        """Emergency mod support callback.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance
        button : discord.ui.Button
            The button instance
        """
        await self.standard_callback(button, interaction)

    @ui.select(
        placeholder="Private",
        custom_id="Modmail_Private",
        max_values=5,
        options=_PRIVATE_OPTIONS,
        row=1,
    )
    async def private(self, interaction: Interaction, select: discord.ui.Select):
        """Private mod support callback.

        This is the only callback does not use the standard_callback helper

        Parameters
        ----------
        interaction : Interaction
            The interaction instance
        select : discord.ui.Select
            The select instance
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        perms = {
            self.mod_role: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            user: PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none()),
        }
        for uid in select.values:
            perms[self.mods[uid]] = PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none())
        await interaction.response.send_modal(ModSupportModal(perms, f"Private-{user.name}-mod-support"))


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
    perm_overrides: dict[discord.Role | discord.Member | discord.User, discord.PermissionOverwrite]
        A dictionary of role, member, and user to permission overrides.
    channel_name: str
        The name of the channel to be created on modal submit.
    filename: str
        The name of the file to be used to store the blacklist.
    """

    logger = logging.getLogger("charbot.mod_support")

    def __init__(
        self,
        perm_overrides: dict[discord.Role | discord.Member, discord.PermissionOverwrite],
        channel_name: str,
    ):
        super().__init__(title="Mod Support Form")
        self.perm_overrides = perm_overrides
        self.channel_name = channel_name
        self.filename = "charbot/mod_support_blacklist.json"

    async def interaction_check(self, interaction: Interaction) -> bool:
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
        with open(self.filename, "rb") as file:
            return interaction.user.id not in orjson.loads(file.read())["blacklisted"]

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

    async def on_submit(self, interaction: Interaction):
        """Submit callback.

        This is where the mod support form is actually submitted.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        """
        category = await interaction.client.fetch_channel(942578610336837632)
        guild = interaction.guild
        topic = self.short_description.value
        assert isinstance(category, discord.CategoryChannel)  # skipcq: BAN-B101
        assert isinstance(guild, discord.Guild)  # skipcq: BAN-B101
        assert isinstance(topic, str)  # skipcq: BAN-B101
        channel = await guild.create_text_channel(
            self.channel_name, category=category, overwrites=self.perm_overrides, topic=topic
        )
        long = "     They supplied a longer description: "
        await channel.send(
            f"{interaction.user.mention} has a new issue/question/request:\n"
            f"{self.short_description.value}."
            f"{long if self.full_description.value else ''}",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
        if self.full_description.value:
            await channel.send(self.full_description.value)
        await interaction.response.send_message(f"Channel Created: {channel.mention}", ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        """Error handler for modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        error : Exception
            The error that was raised.
        """
        await interaction.response.send_message(
            "Oh no! Something went wrong. Please ask for a mod's help in this " "channel and let Bluesy know.",
            ephemeral=True,
        )
        self.logger.error("Ignoring exception in modal %r.", self, exc_info=error)


async def setup(bot: CBot):
    """Load Plugin."""
    await bot.add_cog(ModSupport(bot), override=True)
