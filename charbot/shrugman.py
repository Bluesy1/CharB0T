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

FailStates = Enum("FailStates", r"ツ ¯ ¯\\ ¯\\_ ¯\\_( ¯\\_(ツ ¯\\_(ツ) ¯\\_(ツ)_ ¯\\_(ツ)_/ ¯\\_(ツ)_/¯", start=0)

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

        await ctx.send(
            f"Try it out! (`{''.join(['_' for _ in word if _ != ' '])}`)", view=ShrugmanGame(self.bot, ctx, word)
        )


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
        self.guess_word_list = ["_" for _ in self.word if _ != " "]

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

    @ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the invoker of the game can stop it.", ephemeral=True)
            return
        await self.disable()
        await interaction.response.edit_message(
            content=f"***The game has been cancelled., the word was {self.word}***"
            f"\n {interaction.message.content}",  # type: ignore
            view=None,
        )

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

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.guess.value.lower() not in __valid_guesses__:  # type: ignore
            await interaction.followup.send("Invalid guess.")
            return
        if self.guess.value.lower() in self.game.guesses:  # type: ignore
            await interaction.followup.send(f"You already guessed {self.guess.value.lower()}.")  # type: ignore
            return
        self.game.guesses.append(self.guess.value.lower())  # type: ignore
        self.game.guesses.sort()
        self.game.guess_count += 1
        if self.guess.value.lower() not in self.game.word:  # type: ignore
            self.game.mistakes += 1
        if self.game.mistakes >= len(self.game.fail_enum) - 1:
            self.game.dead = True
            message = await interaction.original_message()
            await self.game.disable()
            await message.edit(
                content=f"{self.game.author.mention} is dead.\nThe word was {self.game.word}.\nYou guessed "
                f"{self.game.guess_count} times.\nYou guessed {', '.join(self.game.guesses)}.\nYou had "
                f"{self.game.mistakes} mistakes.\nYou failed with {self.game.fail_enum(self.game.mistakes)}.\n"
                f"Your final guess was {self.guess.value.lower()}, and you ended with this much solved:"  # type: ignore
                f" `{''.join(self.game.guess_word_list)}`",
                view=self.game,
            )
            return
        for i, letter in enumerate(self.game.word):
            if letter == self.guess.value.lower():  # type: ignore
                self.game.guess_word_list[i] = letter
        message = await interaction.original_message()
        await message.edit(
            content=f"{self.game.author.mention} is still alive.\n "
            f"You guessed {self.guess.value.lower()}. \n"  # type: ignore
            f"You've guessed {', '.join(self.game.guesses)}.\nYou've had {self.game.mistakes} mistakes.\n "
            f"Your shrugman is currently at {self.game.fail_enum(self.game.mistakes)}.\nYour current "
            f"guess is `{''.join(self.game.guess_word_list)}`, with {self.game.guess_count} guesses so far.",
        )


async def setup(bot: CBot):
    await bot.add_cog(Shrugman(bot))
