"""Banner approval flow."""

import discord
from discord import Interaction, ui

from ... import CBot
from .._types import BannerStatus


class ApprovalView(ui.View):
    """Approve or deny a banner.

    Parameters
    ----------
    banner: BannerStatus
        The banner to approve or deny.
    mod: int
        The ID of the moderator who requested teh approval session.
    """

    __slots__ = ("banner", "mod")

    def __init__(self, banner: BannerStatus, mod: int):
        super().__init__()
        self.requester = banner["user_id"]
        self.mod = mod

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid."""
        return interaction.user.id == self.mod

    @ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: Interaction[CBot], _: ui.Button):
        """Approve the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute(
            "UPDATE banners SET approved = TRUE, cooldown = now() WHERE user_id = $1", self.requester
        )
        await interaction.edit_original_response(content="Banner approved.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: Interaction[CBot], _: ui.Button):
        """Deny the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute("DELETE FROM banners WHERE user_id = $1", self.requester)
        await interaction.edit_original_response(content="Banner denied.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.blurple)
    async def cancel(self, interaction: Interaction[CBot], _: ui.Button):
        """Cancel the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(
            content="Banner approval session cancelled.", attachments=[], view=None
        )
        self.stop()
