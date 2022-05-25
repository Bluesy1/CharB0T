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
"""Shrugman modal."""
import discord
from discord import ui
from discord.utils import utcnow

from . import view


__all__ = ("GuessModal",)

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


class GuessModal(ui.Modal, title="Shrugman Guess"):
    """Letter input for shrugman game.

    This modal is used to input a letter for the game.

    Parameters
    ----------
    game : ShrugmanGame
        The game to use for the modal.

    Attributes
    ----------
    game: ShrugmanGame
        The game the modal is used for.
    """

    guess = ui.TextInput(
        label="What letter are you guessing?",
        style=discord.TextStyle.short,
        required=True,
        min_length=0,
        max_length=1,
    )

    def __init__(self, game: view.Shrugman):
        super().__init__(title="Shrugman Guess")
        self.game = game

    # noinspection DuplicatedCode
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Invoke when the user submits the modal.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object.
        """
        _value = self.guess.value
        assert isinstance(_value, str)  # skipcq: BAN-B101
        value: str = _value.lower()
        if value not in __valid_guesses__:
            await interaction.response.send_message("Invalid guess.", ephemeral=True)
            return
        if value in self.game.guesses:
            await interaction.response.send_message(f"You already guessed {value}.", ephemeral=True)
            return
        await interaction.response.defer()
        self.game.guesses.append(value)
        self.game.guess_count += 1
        if value not in self.game.word:
            self.game.mistakes += 1
        if self.game.mistakes >= len(self.game.fail_enum) - 1:
            self.game.dead = True
            await self.game.disable()
            embed = discord.Embed(
                title="**Failed** Shrugman",
                description=f"You got: `{''.join(self.game.guess_word_list)}`",
                color=discord.Color.red(),
            )
            embed.set_footer(text="Type /shrugman to play")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(
                name="Shrugman",
                value=self.game.fail_enum(min(len(self.game.fail_enum) - 1, self.game.mistakes)).name,
                inline=True,
            )
            embed.add_field(name="Guesses", value=f"{self.game.guess_count}", inline=True)
            embed.add_field(name="Mistakes", value=f"{self.game.mistakes}", inline=True)
            embed.add_field(name="Word", value=f"{self.game.word}", inline=True)
            embed.add_field(name="Guesses", value=f"{', '.join(self.game.guesses)}", inline=True)
            time_taken = utcnow().replace(microsecond=0) - self.game.start_time.replace(microsecond=0)
            embed.add_field(name="Time Taken", value=f"{time_taken}", inline=True)
            points = await self.game.bot.give_game_points(interaction.user, "shrugman", 2, 0)
            embed.add_field(
                name="Reputation gained",
                value="2 Reputation" if points == 2 else f"{points} Reputation (Daily Cap Hit)",
                inline=True,
            )
            await interaction.edit_original_message(embed=embed, view=self.game)
            return
        for i, letter in enumerate(self.game.word):
            if letter == value:
                self.game.guess_word_list[i] = letter
        embed = discord.Embed(
            title=f"{f'**{interaction.user.display_name} Won!!!**  ' if '-' not in self.game.guess_word_list else ''}"
            f"Shrugman",
            description=f"{'Congrats!' if '-' not in self.game.guess_word_list else 'Guess the word:'}"
            f" `{''.join(self.game.guess_word_list)}`",
            color=discord.Color.green() if "-" not in self.game.guess_word_list else discord.Color.red(),
        )
        embed.set_footer(text=f"Type /shrugman to play {'again' if '-' not in self.game.guess_word_list else ''}")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(
            name="Shrugman",
            value=self.game.fail_enum(min(len(self.game.fail_enum) - 1, self.game.mistakes)).name,
            inline=True,
        )
        embed.add_field(name="Guesses", value=f"{self.game.guess_count}", inline=True)
        embed.add_field(name="Mistakes", value=f"{self.game.mistakes}", inline=True)
        embed.add_field(
            name="Word",
            value=f"{self.game.word if '-' not in self.game.guess_word_list else '???'}",
            inline=True,
        )
        embed.add_field(name="Guesses", value=f"{', '.join(self.game.guesses)}", inline=True)
        if "-" not in self.game.guess_word_list:
            await self.game.disable()
            time_taken = utcnow().replace(microsecond=0) - self.game.start_time.replace(microsecond=0)
            embed.add_field(name="Time Taken", value=f"{time_taken}", inline=True)
            bonus = -(-((len(self.game.fail_enum) - 1) - self.game.mistakes) // 2)
            points = await self.game.bot.give_game_points(interaction.user, "shrugman", 2, bonus)
            embed.add_field(
                name="Reputation gained",
                value=f"{points} Reputation" if points == (2 + bonus) else f"{points} Reputation (Daily Cap Hit)",
                inline=True,
            )
        await interaction.edit_original_message(embed=embed, view=self.game)
