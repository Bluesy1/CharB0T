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
"""Program classses and functions."""
import asyncio
import datetime
import random
import re
from typing import Final, Literal

import aiohttp
import discord
from discord import Interaction, app_commands
from discord.ext import commands

from . import CBot, errors, shrugman, sudoku, tictactoe


MESSAGE: Final = "You must be at least level 1 to participate in the giveaways system and be in <#969972085445238784>."


@app_commands.guilds(225345178955808768)
class Reputation(commands.Cog, name="Programs"):
    """Programs."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.sudoku_regex = re.compile(r"(\d{81}).*([01]{81})")

    async def interaction_check(self, interaction: Interaction):  # skipcq: PYL-W0221
        """Check if the user is allowed to use the cog."""
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage("Programs can't be used in direct messages.")
        if interaction.guild.id != 225345178955808768:
            raise app_commands.NoPrivateMessage("Programs can't be used in this server.")
        channel = interaction.channel
        assert isinstance(channel, discord.abc.GuildChannel)  # skipcq: BAN-B101
        if channel.id != self.bot.CHANNEL_ID:
            raise errors.WrongChannelError(self.bot.CHANNEL_ID)
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in self.bot.ALLOWED_ROLES for role in user.roles):
            raise errors.MissingProgramRole(self.bot.ALLOWED_ROLES)
        return True

    programs = app_commands.Group(
        name="programs", description="Programs to gain you rep.", guild_ids=[225345178955808768]
    )

    @programs.command(name="sudoku", description="Play a Sudoku puzzle")
    async def sudoku(self, interaction: discord.Interaction, mobile: bool):
        """Generate a sudoku puzzle.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command.
        mobile: bool
            Whether to turn off formatting that only works on desktop.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.session.get("https://nine.websudoku.com/?level=2") as response:
            vals, hidden = self.sudoku_regex.search(str(await response.content.read())).group(1, 2)
        board: list[list[int]] = [[] for _ in range(9)]
        for i, num in enumerate(vals):
            board[i // 9].append(int(num) if int(hidden[i]) == 0 else 0)
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        view = sudoku.Sudoku(sudoku.Puzzle(board, mobile), user, self.bot)
        await interaction.followup.send(embed=view.block_choose_embed(), view=view)

    @programs.command(name="tictactoe", description="Play a game of Tic Tac Toe!")
    async def tictactoe(self, interaction: discord.Interaction, letter: Literal["X", "O"], easy: bool):
        """Tic Tac Toe! command.

        This command is for playing a game of Tic Tac Toe.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object for the command.
        letter : app_commands.Choice[str]
            Do you want to play as X or O?
        easy : bool
            Set this to false for a harder variant of the AI.
        """
        await interaction.response.defer(ephemeral=True)
        game = tictactoe.TicTacView(self.bot, letter, easy)
        if not easy:
            move = await self.bot.loop.run_in_executor(None, game.puzzle.next)
            # noinspection PyProtectedMember
            game._buttons[move[0] * 3 + move[1]].disabled = True  # skipcq: PYL-W0212
        image = await self.bot.loop.run_in_executor(None, game.puzzle.display)
        await interaction.followup.send(file=image, view=game)

    @programs.command(name="shrugman", description="Play the shrugman minigame. (Hangman clone)")
    async def shrugman(self, interaction: discord.Interaction) -> None:
        """Play a game of Shrugman.

        This game is a hangman-like game.

        The game is played by guessing letters.

        The game ends when the word is guessed or the player runs out of guesses.

        The game is won by guessing the word.

        The game is lost by running out of guesses.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command.
        """
        await interaction.response.defer(ephemeral=True)
        word = random.choice(shrugman.words)
        embed = discord.Embed(
            title="Shrugman",
            description=f"Guess the word: `{''.join(['-' for _ in word])}`",
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="Type /shrugman to play")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        view = shrugman.Shrugman(self.bot, word)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="rollcall", description="Claim your daily reputation bonus")
    @app_commands.guilds(225345178955808768)
    async def rollcall(self, interaction: discord.Interaction):
        """Get a daily reputation bonus.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command invocation.
        """
        clientuser = self.bot.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        await interaction.response.defer(ephemeral=True)
        giveaway_user = await self.bot.giveaway_user(interaction.user.id)
        if giveaway_user is None:
            async with self.bot.pool.acquire() as conn:
                await conn.execute("INSERT INTO users (id, points) VALUES ($1, 20)", interaction.user.id)
                await conn.execute(
                    "INSERT INTO daily_points (id, last_claim, last_particip_dt, particip, won) VALUES "
                    "($1, $2, $3, 0, 0)",
                    interaction.user.id,
                    self.bot.TIME(),
                    self.bot.TIME() - datetime.timedelta(days=1),
                )
                await conn.execute("INSERT INTO bids (id, bid) VALUES ($1, 0)", interaction.user.id)
                await interaction.followup.send("You got some Rep today, inmate")
                await self.bot.program_logs.send(
                    f"{interaction.user.mention} has claimed their daily reputation bonus.",
                    allowed_mentions=discord.AllowedMentions(users=False),
                    username=clientuser.name,
                    avatar_url=clientuser.display_avatar.url,
                )
            return
        if giveaway_user["daily"] >= self.bot.TIME():
            await interaction.followup.send("No more Rep for you yet, get back to your cell")
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE users SET points = points + 20 WHERE id = $1", interaction.user.id)
            await conn.execute(
                "UPDATE daily_points SET last_claim = $1 WHERE id = $2", self.bot.TIME(), interaction.user.id
            )
        await interaction.followup.send("You got some Rep today, inmate")
        await self.bot.program_logs.send(
            f"{interaction.user.mention} has claimed their daily reputation bonus.",
            allowed_mentions=discord.AllowedMentions(users=False),
            username=clientuser.name,
            avatar_url=clientuser.display_avatar.url,
        )

    @app_commands.command(name="reputation", description="Check your reputation")
    @app_commands.guilds(225345178955808768)
    async def query_points(self, interaction: discord.Interaction):
        """Query your reputation.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction of the command invocation.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            points = await conn.fetchval("SELECT points from users where id = $1", interaction.user.id) or 0
            limits = await conn.fetchrow("SELECT * from daily_points where id = $1", interaction.user.id) or {
                "last_claim": 0,
                "last_particip_dt": 0,
                "particip": 0,
            }
        claim = "have" if limits["last_claim"] == self.bot.TIME() else "haven't"
        particip = (
            "have" if (limits["last_particip_dt"] == self.bot.TIME()) and (limits["particip"] >= 10) else "haven't"
        )
        await interaction.followup.send(
            f"You have {points} reputation, you {claim} claimed your daily bonus, and you {particip} hit"
            f" your daily program cap.",
            ephemeral=True,
        )


async def setup(bot: CBot):
    """Load the cog.

    Parameters
    ----------
    bot : CBot
    """
    await bot.add_cog(Reputation(bot), guild=discord.Object(id=225345178955808768), override=True)


async def teardown(bot: CBot):
    """Unload the cog.

    Parameters
    ----------
    bot : CBot
    """
    # noinspection PyProtectedMember
    while bot.process_pool._shutdown_lock.locked():  # skipcq: PYL-W0212
        await asyncio.sleep(1)
    await bot.remove_cog("Programs", guild=discord.Object(id=225345178955808768))
