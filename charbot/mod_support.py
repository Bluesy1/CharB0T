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
"""Mod Support cog."""
import json
import sys
import traceback
from datetime import timedelta

import discord
from discord import Embed, Interaction, PermissionOverwrite, app_commands, ui
from discord.ext import tasks
from discord.ext.commands import GroupCog
from discord.utils import utcnow

from bot import CBot


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

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload func."""
        self.check_mod_support_channels.cancel()

    async def cog_load(self) -> None:
        """Cog load func."""
        self.check_mod_support_channels.start()
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
        guild = await self.bot.fetch_guild(225345178955808768)
        channels = await guild.fetch_channels()
        cared: list[discord.TextChannel] = []
        for channel in channels:
            if channel.name.endswith("mod-support") and isinstance(channel, discord.TextChannel):
                cared.append(channel)
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
    async def query(self, interaction: Interaction):
        """Modmail blacklist query command.

        This command is used to query the mod support blacklist.

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the command.
        """
        if await edit_check(interaction):
            with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                blacklisted = [f"<@{item}>" for item in json.load(file)["blacklisted"]]
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
    @app_commands.describe(add="True to add to blacklist, False to remove", user="user to change")
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
            if add:
                successful = False
                with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id not in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].append(user.id)
                    with open("mod_support_blacklist.json", "w", encoding="utf8") as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            else:
                successful = False
                with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].remove(user.id)
                    with open("mod_support_blacklist.json", "w", encoding="utf8") as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            if add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully added to the blacklist", ephemeral=True
                )
            elif add and not successful:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist" f" or was not able to be added to.",
                    ephemeral=True,
                )
            elif not add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully removed from the blacklist",
                    ephemeral=True,
                )
            elif not add and not successful:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was" f" not able to be removed from it.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Error: unkown issue occured. If you're seeing this,"
                    " ping bluesy, something has gone very wrong.",
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
        The everyone role for the guild.
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
        self.filename = "mod_support_blacklist.json"

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
        with open(self.filename, "r", encoding="utf8") as file:
            return interaction.user.id not in json.load(file)["blacklisted"]

    async def standard_callback(self, button: discord.ui.Button, interaction: Interaction):
        """Just general and important and ememgrency callback helper.

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
                    self.mod_role: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
                    self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
                    user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
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
            user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
        }
        for uid in select.values:
            perms.update(
                {self.mods[uid]: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)}
            )
        await interaction.response.send_modal(ModSupportModal(perms, f"{select.placeholder}-{user.name}-mod-support"))


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

    def __init__(
        self,
        perm_overrides: dict[discord.Role | discord.Member, discord.PermissionOverwrite],
        channel_name: str,
    ):
        super().__init__(title="Mod Support Form")
        self.perm_overrides = perm_overrides
        self.channel_name = channel_name
        self.filename = "mod_support_blacklist.json"

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
        with open(self.filename, "r", encoding="utf8") as file:
            return interaction.user.id not in json.load(file)["blacklisted"]

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
        custom_id="Long_Desription",
    )

    async def on_submit(self, interaction: Interaction):
        """Submit callback.

        This is where the mod support form is actually submitted.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        """
        _channel = await interaction.client.fetch_channel(942578610336837632)
        _guild = interaction.guild
        topic = self.short_description.value
        assert isinstance(_channel, discord.CategoryChannel)  # skipcq: BAN-B101
        assert isinstance(_guild, discord.Guild)  # skipcq: BAN-B101
        assert isinstance(topic, str)  # skipcq: BAN-B101
        channel = await _guild.create_text_channel(
            self.channel_name, category=_channel, overwrites=self.perm_overrides, topic=topic
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

    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        """Error handler for modal.

        Parameters
        ----------
        error : Exception
            The error that was raised.
        interaction : Interaction
            The interaction instance.
        """
        await interaction.response.send_message(
            "Oh no! Something went wrong. Please ask for a mod's help in this " "channel and let Bluesy know.",
            ephemeral=True,
        )
        print(f"Ignoring exception in modal {self}:", file=sys.stderr)
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)


async def setup(bot: CBot):
    """Load Plugin."""
    await bot.add_cog(ModSupport(bot), override=True, guild=discord.Object(id=225345178955808768))
