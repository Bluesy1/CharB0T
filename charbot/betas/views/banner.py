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
"""Banner approval flow."""
import discord
from discord import ui

from .._types import BannerStatus
from ... import GuildComponentInteraction as Interaction, CBot


class ApprovalView(ui.View):
    """Approve or deny a banner.

    Parameters
    ----------
    banner: BannerStatus
        The banner to approve or deny.
    mod: int
        The ID of the moderator who requested teh approval session.
    """

    def __init__(self, banner: BannerStatus, mod: int):
        super().__init__()
        self.requester = banner["user_id"]
        self.mod = mod

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid."""
        return interaction.user.id == self.mod

    @ui.button(label="Approve", style=discord.ButtonStyle.green)  # pyright: ignore[reportGeneralTypeIssues]
    async def approve(self, interaction: Interaction[CBot], _: ui.Button):
        """Approve the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute(
            "UPDATE banners SET approved = TRUE, cooldown = now() WHERE user_id = $1", self.requester
        )
        await interaction.edit_original_response(content="Banner approved.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)  # pyright: ignore[reportGeneralTypeIssues]
    async def deny(self, interaction: Interaction[CBot], _: ui.Button):
        """Deny the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.client.pool.execute("DELETE FROM banners WHERE user_id = $1", self.requester)
        await interaction.edit_original_response(content="Banner denied.", attachments=[], view=None)
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.blurple)  # pyright: ignore[reportGeneralTypeIssues]
    async def cancel(self, interaction: Interaction[CBot], _: ui.Button):
        """Cancel the banner."""
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(
            content="Banner approval session cancelled.", attachments=[], view=None
        )
        self.stop()
