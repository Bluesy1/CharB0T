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
"""Tictactoe cog."""
from typing import Final

import discord
from discord import app_commands
from discord.ext import commands

from _tictactoe import TicTacView
from main import CBot


ALLOWED_ROLES: Final = (
    337743478190637077,
    685331877057658888,
    969629622453039104,
    969629628249563166,
    969629632028614699,
    969628342733119518,
    969627321239760967,
    969626979353632790,
)

CHANNEL_ID: Final = 969972085445238784

MESSAGE: Final = "You must be at least level 1 to participate in the giveaways system and be in <#969972085445238784>."


class TicTacCog(commands.Cog):
    """Tic Tac Toe cog.

    Parameters
    ----------
    bot : CBot
        The bot instance.

    Attributes
    ----------
    bot : CBot
        The bot instance.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    @app_commands.command(name="tictactoe", description="Play a game of Tic Tac Toe!")
    @app_commands.describe(
        easy="Set this to false for a harder variant of the AI.", letter="Do you want to play as X or O?"
    )
    @app_commands.choices(
        letter=[
            app_commands.Choice(name="X", value="X"),
            app_commands.Choice(name="O", value="O"),
        ]
    )
    @app_commands.guilds(225345178955808768)
    async def tictaccommand(self, interaction: discord.Interaction, letter: app_commands.Choice[str], easy: bool):
        """Tic Tac Toe! command.

        This command is for playing a game of Tic Tac Toe.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object for the command.
        letter : app_commands.Choice[str]
            The letter to play as.
        easy : bool
            Whether to use the easy AI.
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in ALLOWED_ROLES for role in user.roles) or interaction.channel_id != CHANNEL_ID:
            await interaction.response.send_message(MESSAGE, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        game = TicTacView(self.bot, letter.value, easy)
        if not easy:
            move = await self.bot.loop.run_in_executor(None, game.puzzle.next)
            # noinspection PyProtectedMember
            game._buttons[move[0] * 3 + move[1]].disabled = True  # skipcq: PYL-W0212
        image = await self.bot.loop.run_in_executor(None, game.puzzle.display)
        await interaction.followup.send(file=image, view=game)


async def setup(bot: CBot):
    """Initialize the cog.

    Parameters
    ----------
    bot: CBot
        The bot to attach the cog to.
    """
    await bot.add_cog(TicTacCog(bot), guild=discord.Object(id=225345178955808768), override=True)
