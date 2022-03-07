# coding=utf-8
import json

import discord
import hikari
from discord import ui
from hikari import Permissions, PermissionOverwrite, PermissionOverwriteType

MOD_SENSITIVE = PermissionOverwrite(
    id=338173415527677954,
    type=PermissionOverwriteType.ROLE,
    allow=Permissions.NONE,
    deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)

MOD_GENERAL = PermissionOverwrite(
    id=338173415527677954,
    type=PermissionOverwriteType.ROLE,
    allow=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
)

EVERYONE_MODMAIL = PermissionOverwrite(
    id=225345178955808768,
    type=PermissionOverwriteType.ROLE,
    deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
)


def user_perms(user_id: hikari.Snowflakeish):
    """Creates a permission overwrite for a user with the given ID"""
    return PermissionOverwrite(
        id=user_id,
        type=PermissionOverwriteType.MEMBER,
        allow=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
    )


_MOD_SUPPORT_PRIVATE_OPTIONS = [
    discord.SelectOption(label="Admins Only", value="146285543146127361"),
    discord.SelectOption(label="Bluesy", value="363095569515806722"),
    discord.SelectOption(label="Krios", value="138380316095021056"),
    discord.SelectOption(label="Mike Takumi", value="162833689196101632"),
    discord.SelectOption(label="Kaitlin", value="82495450153750528"),
]


class ModSupportButtons(ui.View):
    """Creates a button row"""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="General", style=discord.ButtonStyle.success, custom_id="Modmail_General", emoji="❔", row=0)
    async def general(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('This is green.', ephemeral=True)

    @ui.button(label="Important", style=discord.ButtonStyle.primary, custom_id="Modmail_Important", emoji="❗", row=0)
    async def important(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('This is green.', ephemeral=True)

    @ui.button(label="Emergency", style=discord.ButtonStyle.danger, custom_id="Modmail_Emergency", emoji="‼", row=0)
    async def emergency(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('This is green.', ephemeral=True)

    @ui.select(placeholder="Private", custom_id="Modmail_Private", max_values=5, options=_MOD_SUPPORT_PRIVATE_OPTIONS,
               row=1)
    async def private(self, select: discord.ui.Select, interaction: discord.Interaction):
        await interaction.response.send_message('This is green.', ephemeral=True)



def check_not_modmail_blacklisted(user_id: hikari.Snowflakeish) -> bool:
    """
    Checks if a user is in the blacklist
    Returns True if a user is allowed to use modmail buttons, False if not.
    """
    with open("modmail_blacklist.json", "r", encoding="utf8") as file:
        modmail_blacklist = json.load(file)
    return user_id not in modmail_blacklist["blacklisted"]
