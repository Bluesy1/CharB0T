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
import json
import sys
import traceback
from datetime import timedelta

import discord
from discord import Embed, app_commands, Interaction, ui, PermissionOverwrite
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from discord.utils import utcnow


async def edit_check(interaction: Interaction) -> bool:
    """Check for if a user is allowed to edit the blacklist"""
    return any(
        role.id
        in (
            225413350874546176,
            253752685357039617,
            725377514414932030,
            338173415527677954,
        )
        for role in interaction.user.roles
    )


class ModSupport(
    Cog, app_commands.Group, name="modsupport", description="mod support command group"
):
    """Mod Support Cog"""

    def __init__(self, bot: commands.Bot):
        super().__init__(name="modsupport", description="mod support command group")
        self.bot = bot
        # noinspection PyUnresolvedReferences

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload func"""
        self.check_mod_support_channels.cancel()

    async def cog_load(self) -> None:
        """Cog load func"""
        self.check_mod_support_channels.start()
        guild = await self.bot.fetch_guild(225345178955808768)
        everyone = guild.default_role
        mod_roles = guild.get_role(338173415527677954)
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
        """Remove stale modmail channels"""
        guild = await self.bot.fetch_guild(225345178955808768)
        channels = await guild.fetch_channels()
        cared: list[discord.TextChannel] = []
        for channel in channels:
            if channel.name.endswith("mod-support") and isinstance(
                channel, discord.TextChannel
            ):
                cared.append(channel)
        for channel in cared:
            temp = False
            async for message in channel.history(after=utcnow() - timedelta(days=3)):
                if message.author.id == self.bot.user.id:
                    continue
                temp = True
                break
            if temp:
                await channel.delete()

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        """On message event"""
        if (
            not message.author.bot
            and message.channel.type is discord.ChannelType.private
        ):
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail,"
                " that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>"
            )

    @app_commands.command(
        name="query", description="queries list of users banned from mod support"
    )
    async def query(self, interaction: Interaction):
        """Modmail blacklist query command"""
        if await edit_check(interaction):
            with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                blacklisted = [f"<@{item}>" for item in json.load(file)["blacklisted"]]
            await interaction.response.send_message(
                embed=Embed(
                    title="Blacklisted users", description="\n".join(blacklisted)
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "You are not authorized to use this command", ephemeral=True
            )

    @app_commands.command(
        name="edit",
        description="adds or removes a user from the list of users banned from mod"
        " support",
    )
    @app_commands.describe(
        add="True to add to blacklist, False to remove", user="user to change"
    )
    async def edit(self, interaction: Interaction, add: bool, user: discord.Member):
        """Modmail edit blacklist command"""
        if await edit_check(interaction):
            if add:
                successful = False
                with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id not in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].append(user.id)
                    with open(
                        "mod_support_blacklist.json", "w", encoding="utf8"
                    ) as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            else:
                successful = False
                with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].remove(user.id)
                    with open(
                        "mod_support_blacklist.json", "w", encoding="utf8"
                    ) as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            if add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully added to the blacklist", ephemeral=True
                )
            elif add and not successful:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist"
                    f" or was not able to be added to.",
                    ephemeral=True,
                )
            elif not add and successful:
                await interaction.response.send_message(
                    f"<@{user.id}> successfully removed from the blacklist",
                    ephemeral=True,
                )
            elif not add and not successful:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was"
                    f" not able to be removed from it.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Error: unkown issue occured. If you're seeing this,"
                    " ping bluesy, something has gone very wrong.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "You are not authorized to use this command", ephemeral=True
            )


class ModSupportButtons(ui.View):
    """Creates a button row"""

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
        """Check to run for all interaction instances"""
        with open(self.filename, "r", encoding="utf8") as file:
            return interaction.user.id not in json.load(file)["blacklisted"]

    async def standard_callback(
        self, button: discord.ui.Button, interaction: Interaction
    ):
        """Just general and important and ememgrency callback helper"""
        await interaction.response.send_modal(
            ModSupportModal(
                {
                    self.mod_role: PermissionOverwrite(
                        view_channel=True, send_messages=True, read_messages=True
                    ),
                    self.everyone: PermissionOverwrite(
                        view_channel=False, send_messages=False, read_messages=False
                    ),
                    interaction.user: PermissionOverwrite(
                        view_channel=True, send_messages=True, read_messages=True
                    ),
                },
                f"{button.label}-{interaction.user.name}-mod-support",
            )
        )

    @ui.button(
        label="General",
        style=discord.ButtonStyle.success,
        custom_id="Modmail_General",
        emoji="❔",
        row=0,
    )
    async def general(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """General mod support callback"""
        await self.standard_callback(button, interaction)

    @ui.button(
        label="Important",
        style=discord.ButtonStyle.primary,
        custom_id="Modmail_Important",
        emoji="❗",
        row=0,
    )
    async def important(self, button: discord.ui.Button, interaction: Interaction):
        """Important mod support callback"""
        await self.standard_callback(button, interaction)

    @ui.button(
        label="Emergency",
        style=discord.ButtonStyle.danger,
        custom_id="Modmail_Emergency",
        emoji="‼",
        row=0,
    )
    async def emergency(self, button: discord.ui.Button, interaction: Interaction):
        """Emergency mod support callback"""
        await self.standard_callback(button, interaction)

    @ui.select(
        placeholder="Private",
        custom_id="Modmail_Private",
        max_values=5,
        options=_PRIVATE_OPTIONS,
        row=1,
    )
    async def private(self, select: discord.ui.Select, interaction: Interaction):
        """Private mod support callback"""
        perms = {
            self.mod_role: PermissionOverwrite(
                view_channel=False, send_messages=False, read_messages=False
            ),
            self.everyone: PermissionOverwrite(
                view_channel=False, send_messages=False, read_messages=False
            ),
            interaction.user: PermissionOverwrite(
                view_channel=True, send_messages=True, read_messages=True
            ),
        }
        for uid in select.values:
            perms.update(
                {
                    self.mods[uid]: PermissionOverwrite(
                        view_channel=True, send_messages=True, read_messages=True
                    )
                }
            )
        await interaction.response.send_modal(
            ModSupportModal(perms, f"{select.placeholder}-{interaction.user.name}")
        )


class ModSupportModal(ui.Modal, title="Mod Support Form"):
    """Mod Support Modal Class"""

    def __init__(
        self,
        perm_overrides: dict[
            discord.Role | discord.Member, discord.PermissionOverwrite
        ],
        channel_name: str,
    ):
        super().__init__(title="Mod Support Form")
        self.perm_overrides = perm_overrides
        self.channel_name = channel_name
        self.filename = "mod_support_blacklist.json"

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check to run for all interaction instances"""
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
        """Callback for when a modal is submitted"""
        channel = await interaction.guild.create_text_channel(
            self.channel_name,
            category=await interaction.guild.fetch_channel(942578610336837632),
            overwrites=self.perm_overrides,
            topic=self.short_description.value,
        )
        long_desc = self.full_description.value not in (
            self.full_description.placeholder,
            None,
        )
        await channel.send(
            f"{interaction.user.mention} has a new issue/question/request:\n"
            f"{self.short_description.value}."
            f"{'     They supplied a longer description: ' if long_desc else ''}",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
        if long_desc:
            await channel.send(self.full_description.value)
        await interaction.response.send_message(
            f"Channel Created: {channel.mention}", ephemeral=True
        )

    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        """Callback for when an error happens on a modal"""
        await interaction.response.send_message(
            "Oh no! Something went wrong. Please ask for a mod's help in this "
            "channel and let Bluesy know.",
            ephemeral=True,
        )
        print(f"Ignoring exception in modal {self}:", file=sys.stderr)
        traceback.print_exception(
            error.__class__, error, error.__traceback__, file=sys.stderr
        )


async def setup(bot: commands.Bot):
    """Loads Plugin"""
    await bot.add_cog(
        ModSupport(bot), override=True, guild=discord.Object(id=225345178955808768)
    )
