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
"""Sudoko minigame."""
import asyncio
import functools
from typing import Final

import discord
from discord import app_commands
from discord.ext import commands

from _sudoku import Puzzle
from _sudoku import Sudoku as SudokuGame
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


class Sudoku(commands.Cog):
    """Sudoku commands.

    This cog contains commands for playing Sudoku.

    Parameters
    ----------
    bot : CBot
        The bot instance.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    @app_commands.command(name="sudoku", description="Play a Sudoku puzzle")
    @app_commands.describe(mobile="Set this to true on mobile to turn off formatting that only works on desktop")
    @app_commands.guilds(225345178955808768)
    async def sudoku(self, interaction: discord.Interaction, mobile: bool):
        """Generate a sudoku puzzle.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command.
        mobile: bool
            Whether to turn off formatting that only works on desktop.
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in ALLOWED_ROLES for role in user.roles) or interaction.channel_id != CHANNEL_ID:
            await interaction.response.send_message(MESSAGE, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        puzzle = await self.bot.loop.run_in_executor(self.bot.process_pool, functools.partial(Puzzle.random, mobile))
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        view = SudokuGame(puzzle, user, self.bot)
        await interaction.followup.send(embed=view.block_choose_embed(), view=view)


async def setup(bot: CBot):
    """Load the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.add_cog(Sudoku(bot), guild=discord.Object(id=225345178955808768), override=True)


async def teardown(bot: CBot):
    """Unload the cog.

    Parameters
    ----------
    bot : CBot
    """
    # noinspection PyProtectedMember
    while bot.process_pool._shutdown_lock.locked():  # skipcq: PYL-W0212
        await asyncio.sleep(1)
    await bot.remove_cog("Sudoku", guild=discord.Object(id=225345178955808768))
