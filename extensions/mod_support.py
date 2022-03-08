# coding=utf-8
import json
import sys
import traceback
from datetime import datetime, timedelta

import discord
from discord import Embed, app_commands, Interaction, ui, PermissionOverwrite
from discord.ext import commands, tasks
from discord.ext.commands import Cog


@tasks.loop(hours=24)
async def check_modmail_channels(bot: commands.Bot):
    """Remove stale modmail channels"""
    channels = (await bot.fetch_guild(225345178955808768)).channels
    cared = []
    for channel in channels:
        if channel.category.category_id == 942578610336837632 and channel.id != 906578081496584242:
            cared.append(channel)
    for channel in cared:
        # noinspection PyBroadException
        try:
            if channel.history(after=(datetime.now() - timedelta(days=3))) == 0:
                await channel.send("Deleting now")
                await channel.delete()
        except:  # pylint: disable=bare-except
            print("Error")


class ModSupport(Cog):
    """Mod Support Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # noinspection PyUnresolvedReferences
        self.tree: app_commands = bot.tree
        self.mod_support_buttons_added = False

    @Cog.listener()
    async def on_ready(self):
        """On ready event"""
        if not self.mod_support_buttons_added:
            guild = await self.bot.fetch_guild(225345178955808768)
            everyone = guild.default_role
            mod_roles = guild.get_role(338173415527677954)
            mods = {
                "146285543146127361": await guild.fetch_member(146285543146127361),
                "363095569515806722": await guild.fetch_member(363095569515806722),
                "138380316095021056": await guild.fetch_member(138380316095021056),
                "162833689196101632": await guild.fetch_member(162833689196101632),
                "82495450153750528": await guild.fetch_member(82495450153750528)
            }
            self.bot.add_view(ModSupportButtons(everyone, mod_roles, mods))
            self.mod_support_buttons_added = True

    @Cog.listener()
    async def on_message(self, message: discord.Message):  # pylint: disable=no-self-use
        """on message event"""
        if not message.author.bot and message.channel.type is discord.ChannelType.private:
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail, that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>")


class Modsupport(app_commands.Group):
    """App commands for mod support"""

    @app_commands.command(name="query", description="queries list of users banned from mod support")
    async def query(self, interaction: Interaction):  # pylint: disable=no-self-use
        """Modmail blacklist query command"""
        if any(role.id in (225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954) for role in
               interaction.user.roles):
            with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
                blacklisted = [f"<@{item}>" for item in json.load(file)["blacklisted"]]
            await interaction.response.send_message(embed=Embed(title="Blacklisted users",
                                                                description="\n".join(blacklisted)), ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)

    @app_commands.command(name="edit", description="adds or removes a user from the list of users banned from mod"
                                                   " support")
    @app_commands.describe(add="True to add to blacklist, False to remove",
                           user="user to change")  # pylint: disable=no-self-use
    async def edit(self, interaction: Interaction, add: bool, user: discord.Member):  # pylint: disable=no-self-use
        """Modmail edit blacklist command"""
        if any(role.id in (225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954) for role in
               interaction.user.roles):
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
                await interaction.response.send_message(f"<@{user.id}> successfully added to the blacklist",
                                                        ephemeral=True)
            elif add and not successful:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist or was not able to be added to.", ephemeral=True)
            elif not add and successful:
                await interaction.response.send_message(f"<@{user.id}> successfully removed from the blacklist",
                                                        ephemeral=True)
            elif not add and not successful:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was not able to be removed from it.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Error: unkown issue occured. If you're seeing this, ping bluesy, something has gone very wrong.",
                    ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)


class ModSupportButtons(ui.View):
    """Creates a button row"""

    _PRIVATE_OPTIONS = [
        discord.SelectOption(label="Admins Only", value="146285543146127361"),
        discord.SelectOption(label="Bluesy", value="363095569515806722"),
        discord.SelectOption(label="Krios", value="138380316095021056"),
        discord.SelectOption(label="Mike Takumi", value="162833689196101632"),
        discord.SelectOption(label="Kaitlin", value="82495450153750528"),
    ]

    def __init__(self, everyone: discord.Role, mod_role: discord.Role, mods: dict[str, discord.Member]):
        super().__init__(timeout=None)
        self.everyone = everyone
        self.mod_role = mod_role
        self.mods = mods

    async def interaction_check(self, interaction: Interaction) -> bool:  # pylint: disable=no-self-use
        with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
            return interaction.user.id not in json.load(file)["blacklisted"]

    @ui.button(label="General", style=discord.ButtonStyle.success, custom_id="Modmail_General", emoji="❔",
               row=0)  # pylint: disable=no-self-use
    async def general(self, button: discord.ui.Button, interaction: discord.Interaction):  # pylint: disable=no-self-use
        """General mod support callback"""
        await interaction.response.send_modal(ModSupportModal({
            self.mod_role: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            interaction.user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }, f"{button.label}-{interaction.user.name}"))

    @ui.button(label="Important", style=discord.ButtonStyle.primary, custom_id="Modmail_Important", emoji="❗", row=0)
    async def important(self, button: discord.ui.Button, interaction: Interaction):  # pylint: disable=no-self-use
        """Important mod support callback"""
        await interaction.response.send_modal(ModSupportModal({
            self.mod_role: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            interaction.user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }, f"{button.label}-{interaction.user.name}"))

    @ui.button(label="Emergency", style=discord.ButtonStyle.danger, custom_id="Modmail_Emergency", emoji="‼", row=0)
    async def emergency(self, button: discord.ui.Button, interaction: Interaction):  # pylint: disable=no-self-use
        """Emergency mod support callback"""
        await interaction.response.send_modal(ModSupportModal({
            self.mod_role: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            interaction.user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }, f"{button.label}-{interaction.user.name}"))

    @ui.select(placeholder="Private", custom_id="Modmail_Private", max_values=5, options=_PRIVATE_OPTIONS,
               row=1)
    async def private(self, select: discord.ui.Select, interaction: Interaction):  # pylint: disable=no-self-use
        """Private mod support callback"""
        perms = {
            self.mod_role: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            self.everyone: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
            interaction.user: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)}
        for uid in select.values:
            perms.update({self.mods[uid]: PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
                          })
        await interaction.response.send_modal(ModSupportModal(perms, f"{select.placeholder}-{interaction.user.name}"))


class ModSupportModal(ui.Modal, title="Mod Support Form"):
    """Mod Support Modal Class"""

    def __init__(self, perm_overrides: dict[discord.Role | discord.Member, discord.PermissionOverwrite],
                 channel_name: str):
        super().__init__(title="Mod Support Form")
        self.perm_overrides = perm_overrides
        self.channel_name = channel_name

    async def interaction_check(self, interaction: Interaction) -> bool:  # pylint: disable=no-self-use
        with open("mod_support_blacklist.json", "r", encoding="utf8") as file:
            return interaction.user.id not in json.load(file)["blacklisted"]

    short_description = ui.TextInput(
        label='Short Description of your problem/query',
        style=discord.TextStyle.short,
        placeholder="Short description of your problem/query here ...",
        required=True,
        custom_id="Short_Description"
    )

    full_description = ui.TextInput(
        label="Full description of problem/query.",
        style=discord.TextStyle.paragraph,
        placeholder="Put your full description here ...",
        required=False,
        custom_id="Long_Desription"
    )

    async def on_submit(self, interaction: Interaction):
        channel = await interaction.guild.create_text_channel(
            self.channel_name,
            category=await interaction.guild.fetch_channel(942578610336837632),
            overwrites=self.perm_overrides,
            topic=self.short_description.value
        )
        long_desc = self.full_description.value not in (self.full_description.placeholder, None)
        await channel.send(f"{interaction.user.mention} has a new issue/question/request:\n"
                           f"{self.short_description.value}."
                           f"{'     They supplied a longer description: ' if long_desc else ''}",
                           allowed_mentions=discord.AllowedMentions(users=True))
        if long_desc:
            await channel.send(self.full_description.value)
        await interaction.response.send_message(f"Channel Created: {channel.mention}", ephemeral=True)

    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        await interaction.response.send_message("Oh no! Something went wrong. Please ask for a mod's help in this "
                                                "channel and let Bluesy know.", ephemeral=True)
        print(f'Ignoring exception in modal {self}:', file=sys.stderr)
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)


def setup(bot: commands.Bot):
    """Loads Plugin"""
    check_modmail_channels.start(bot)
    bot.add_cog(ModSupport(bot))


def teardown(bot: commands.Bot):  # pylint: disable=unused-argument
    """Unloads Plugin"""
    check_modmail_channels.stop()
