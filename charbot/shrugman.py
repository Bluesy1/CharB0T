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
"""Shrugman minigame."""
import random
from enum import Enum

import discord
from discord import ui
from discord.ext import commands

from main import CBot

FailStates = Enum(
    "FailStates",
    r"<:KHattip:896043110717608009> ¯ ¯\\ ¯\\_ ¯\\_( ¯\\_(ツ ¯\\_(ツ) ¯\\_(ツ)_ ¯\\_(ツ)_/ ¯\\_(ツ)_/¯",
    start=0,
)

with open("hangman_words.csv") as f:
    __words__ = [word.replace("\n", "") for word in f.readlines()]

__valid_guesses__ = (
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
)


class Shrugman(commands.Cog):
    def __init__(self, bot: CBot):
        self.bot = bot

    @commands.command(name="shrugman", aliases=["sm"])
    async def shrugman(self, ctx: commands.Context):
        if ctx.channel.id != 839690221083820032:
            return
        if ctx.guild is None:
            return
        if not any(338173415527677954 == role.id for role in ctx.author.roles):  # type: ignore
            return
        word = random.choice(__words__)
        embed = discord.Embed(
            title="Shrugman",
            description=f"Guess the word: `{''.join(['-' for _ in word])}`",
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="Type !shrugman or !sm to play")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed, view=ShrugmanGame(self.bot, ctx, word))


class ShrugmanGame(ui.View):
    def __init__(self, bot: CBot, ctx: commands.Context, word, *, fail_enum=FailStates):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = ctx.author
        self.word = word or random.choice(__words__)
        self.fail_enum = fail_enum
        self.guess_count = 0
        self.guesses: list[str] = []
        self.mistakes = 0
        self.dead = False
        self.guess_word_list = ["-" for _ in self.word]
        self.length = len(word)

    # noinspection PyUnusedLocal
    @ui.button(label="Guess", style=discord.ButtonStyle.success)
    async def guess_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the invoker of the game can guess.", ephemeral=True)
            return
        if self.dead:
            await interaction.response.send_message("You're dead, you can't guess anymore.", ephemeral=True)
            await self.disable()
            await interaction.message.edit(view=self)  # type: ignore
            return
        await interaction.response.send_modal(GuessModal(self))

    # noinspection PyUnusedLocal
    @ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the invoker of the game can stop it.", ephemeral=True)
            return
        await self.disable()
        embed = discord.Embed(
            title="**Cancelled** Shrugman",
            description=f"Guess the word: `{''.join(self.guess_word_list)}`",
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="Type !shrugman or !sm to play")
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.add_field(name="Shrugman", value=self.fail_enum(self.mistakes).name, inline=True)
        embed.add_field(name="Guesses", value=f"{self.guess_count}", inline=True)
        embed.add_field(name="Mistakes", value=f"{self.mistakes}", inline=True)
        embed.add_field(name="Word", value=f"{self.word}", inline=True)
        embed.add_field(name="Guesses", value=f"{', '.join(self.guesses) or 'None'}", inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    async def disable(self):
        self.guess_button.disabled = True
        self.stop_button.disabled = True
        self.stop()


class GuessModal(ui.Modal, title="Shrugman Guess"):
    guess = ui.TextInput(
        label="What letter are you guessing?",
        style=discord.TextStyle.short,
        required=True,
        min_length=0,
        max_length=1,
    )

    def __init__(self, game: ShrugmanGame):
        super().__init__(title="Shrugman Guess")
        self.game = game

    # noinspection DuplicatedCode
    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.guess.value.lower() not in __valid_guesses__:  # type: ignore
            await interaction.response.send_message("Invalid guess.", ephmeral=True)
            return
        if self.guess.value.lower() in self.game.guesses:  # type: ignore
            await interaction.response.send_message(
                f"You already guessed {self.guess.value.lower()}.", ephmeral=True  # type: ignore
            )
            return
        self.game.guesses.append(self.guess.value.lower())  # type: ignore
        self.game.guess_count += 1
        if self.guess.value.lower() not in self.game.word:  # type: ignore
            self.game.mistakes += 1
        if self.game.mistakes >= len(self.game.fail_enum) - 1:
            self.game.dead = True
            await self.game.disable()
            embed = discord.Embed(
                title="**Failed** Shrugman",
                description=f"You got: `{''.join(self.game.guess_word_list)}`",
                color=discord.Color.red(),
            )
            embed.set_footer(text="Type !shrugman or !sm to play again")
            embed.set_author(name=self.game.author.display_name, icon_url=self.game.author.display_avatar.url)
            embed.add_field(name="Shrugman", value=self.game.fail_enum(self.game.mistakes).name, inline=True)
            embed.add_field(name="Guesses", value=f"{self.game.guess_count}", inline=True)
            embed.add_field(name="Mistakes", value=f"{self.game.mistakes}", inline=True)
            embed.add_field(name="Word", value=f"{self.game.word}", inline=True)
            embed.add_field(name="Guesses", value=f"{', '.join(self.game.guesses)}", inline=True)
            await interaction.response.edit_message(embed=embed, view=self)
            return
        for i, letter in enumerate(self.game.word):
            if letter == self.guess.value.lower():  # type: ignore
                self.game.guess_word_list[i] = letter
        if "-" not in self.game.guess_word_list:
            await self.game.disable()
        embed = discord.Embed(
            title=f"{f'**{self.game.author.display_name} Won!!!**  ' if '-' not in self.game.guess_word_list else ''}"
            f"Shrugman",
            description=f"{'Congrats!' if '-' not in self.game.guess_word_list else 'Guess the word:'}"
            f" `{''.join(self.game.guess_word_list)}`",
            color=discord.Color.green() if "-" not in self.game.guess_word_list else discord.Color.red(),
        )
        embed.set_footer(
            text=f"Type !shrugman or !sm to play {'again' if '-' not in self.game.guess_word_list else ''}"
        )
        embed.set_author(name=self.game.author.display_name, icon_url=self.game.author.display_avatar.url)
        embed.add_field(name="Shrugman", value=self.game.fail_enum(self.game.mistakes).name, inline=True)
        embed.add_field(name="Guesses", value=f"{self.game.guess_count}", inline=True)
        embed.add_field(name="Mistakes", value=f"{self.game.mistakes}", inline=True)
        embed.add_field(
            name="Word",
            value=f"{self.game.word if True or'-' not in self.game.guess_word_list else '???'}",
            inline=True,
        )
        embed.add_field(name="Guesses", value=f"{', '.join(self.game.guesses)}", inline=True)
        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot: CBot):
    await bot.add_cog(Shrugman(bot))
