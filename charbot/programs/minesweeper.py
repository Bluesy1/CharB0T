# -*- coding: utf-8 -*-
"""Minesweeper game."""
import string
from io import BytesIO
from typing_extensions import Self

import discord
from PIL import Image
from discord import ButtonStyle, ui, SelectOption

from .. import GuildComponentInteraction as Interaction, CBot
from charbot_rust import minesweeper


class Minesweeper(ui.View):
    """Minesweeper view for rust.

    This is a view for the minesweeper game. It is a subclass of discord.ui.View, and it is used to display the game
    board and handle user input.

    Parameters
    ----------
    game : minesweeper.Game
        The game to display and run.
    """

    def __init__(self, game: minesweeper.Game):  # pyright: ignore[reportGeneralTypeIssues]
        super().__init__()
        self.game = game
        x = self.game.x
        y = self.game.y
        # f"{i}" is significantly faster than str(i), as it doesn't make a command to CALL_FUNCTION internally.
        self.row.options = [
            SelectOption(
                label=f"Row {letter}",
                value=f"{i}",
                emoji=chr(0x1F1E6 + i),
                default=i == y,
                description=f"Change the row to {letter}",
            )
            for i, letter in enumerate(string.ascii_uppercase[: self.game.height])
        ]
        self.column.options = [
            SelectOption(
                label=f"Column {letter}",
                value=f"{i}",
                emoji=chr(0x1F1E6 + i),
                default=i == x,
                description=f"Change the column to {letter}",
            )
            for i, letter in enumerate(string.ascii_uppercase[: self.game.width])
        ]

    async def draw(self) -> discord.File:
        """Draw the game board.

        This method is called every time the view is drawn. It draws the game board and returns it as a discord.File.

        Returns
        -------
        discord.File
            The game board as a discord.File.
        """
        board, size = self.game.draw()
        img = Image.frombytes("RGB", size, bytes(board))
        bytesio = BytesIO()
        img.save(bytesio, "PNG")
        bytesio.seek(0)
        file = discord.File(bytesio, filename="minesweeper.png", description="Minesweeper board")  # skipcq: PYL-E1123
        return file

    async def handle_lose(self, interaction: Interaction[CBot]):
        """Handle a loss.

        This method is called when the game is lost. It displays a message to the user and stops the game.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        """
        await interaction.response.defer(ephemeral=True)
        points = self.game.points
        awarded = sum(points)
        # awarded = await interaction.client.give_game_points(interaction.user, "minesweeper", *points)
        embed = discord.Embed(
            title="You lost!",
            description=f"You revealed a mine and lost the game. If not for beta testing, you would have gained "
            f"{awarded} points. {'Hit daily cap' if awarded != sum(points) else ''}",
            color=discord.Color.red(),
        ).set_image(url="attachment://minesweeper.png")
        file = await self.draw()
        await interaction.edit_original_response(attachments=[file], embed=embed, view=None)
        self.stop()

    async def handle_win(self, interaction: Interaction[CBot]):
        """Handle a win.

        This method is called when the game is won. It displays a message to the user and stops the game.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        """
        await interaction.response.defer(ephemeral=True)
        points = self.game.points
        awarded = sum(points)
        # awarded = await interaction.client.give_game_points(interaction.user, "minesweeper", *points)
        embed = discord.Embed(
            title="You won!",
            description=f"You revealed all the safe tiles and won the game. If not for beta testing, you would have "
            f"gained {awarded} points. {'Hit daily cap' if awarded != sum(points) else ''}",
            color=discord.Color.green(),
        ).set_image(url="attachment://minesweeper.png")
        file = await self.draw()
        await interaction.edit_original_response(attachments=[file], embed=embed, view=None)
        self.stop()

    @ui.select(placeholder="Select a row")  # pyright: ignore[reportGeneralTypeIssues]
    async def row(self, interaction: Interaction[CBot], select: ui.Select[Self]):
        """Change the row.

        This method is called when the user changes the row. It changes the row of the game and redraws the board.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        select : ui.Select[Self]
            The select.
        """
        val = select.values[0]
        self.game.change_row(int(val))
        file = await self.draw()
        for opt in select.options:
            opt.default = opt.value == val
        await interaction.response.edit_message(attachments=[file], view=self)

    @ui.select(placeholder="Select a column")  # pyright: ignore[reportGeneralTypeIssues]
    async def column(self, interaction: Interaction[CBot], select: ui.Select[Self]):
        """Change the column.

        This method is called when the user changes the column. It changes the column of the game and redraws the

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        select : ui.Select[Self]
            The select.
        """
        val = select.values[0]
        self.game.change_col(int(val))
        file = await self.draw()
        for opt in select.options:
            opt.default = opt.value == val
        await interaction.response.edit_message(attachments=[file], view=self)

    @ui.button(label="Reveal", style=ButtonStyle.primary, emoji="\u26cf")  # pyright: ignore[reportGeneralTypeIssues]
    async def reveal(self, interaction: Interaction[CBot], _button: ui.Button[Self]):
        """Reveal a tile.

        This method is called when the user clicks the reveal button. It reveals a tile and redraws the board.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        _button : ui.Button[Self]
            The button.
        """
        res = self.game.reveal()
        if res == minesweeper.RevealResult.Mine:  # pyright: ignore[reportGeneralTypeIssues]
            await self.handle_lose(interaction)
        elif self.game.is_win():
            await self.handle_win(interaction)
        else:
            file = await self.draw()
            await interaction.response.edit_message(attachments=[file], view=self)
            if res == minesweeper.RevealResult.Flagged:  # pyright: ignore[reportGeneralTypeIssues]
                await interaction.followup.send(
                    "WARNING: you tried to reveal a flagged cell. Instead of revealing it, it was unflagged. "
                    "If you meant to reveal it, press reveal again.",
                    ephemeral=True,
                )

    # noinspection GrazieInspection
    @ui.button(label="Chord", style=ButtonStyle.primary, emoji="\u2692")  # pyright: ignore[reportGeneralTypeIssues]
    async def chord(self, interaction: Interaction[CBot], _button: ui.Button[Self]):
        """Chord a tile.

        This method is called when the user clicks the chord button. It chords a tile and redraws the board.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        _button : ui.Button[Self]
            The button.
        """
        res = self.game.chord()
        if res == minesweeper.ChordResult.Failed:  # pyright: ignore[reportGeneralTypeIssues]
            await interaction.response.send_message(
                "WARNING: you tried to chord a cell that was not revealed, not a number, or didn't have the "
                "appropriate number of surrounding tiles marked.",
                ephemeral=True,
            )
        elif res == minesweeper.ChordResult.Success:  # pyright: ignore[reportGeneralTypeIssues]
            if self.game.is_win():
                await self.handle_win(interaction)
            else:
                file = await self.draw()
                await interaction.response.edit_message(attachments=[file], view=self)
        else:
            await self.handle_lose(interaction)

    @ui.button(label="Flag", style=ButtonStyle.success, emoji="\U0001f6a9")  # pyright: ignore[reportGeneralTypeIssues]
    async def flag(self, interaction: Interaction[CBot], _button: ui.Button[Self]):
        """Flag a tile.

        This method is called when the user clicks the flag button. It flags a tile and redraws the board.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        _button : ui.Button[Self]
            The button.
        """
        self.game.toggle_flag()
        file = await self.draw()
        await interaction.response.edit_message(attachments=[file], view=self)

    @ui.button(label="Quit", style=ButtonStyle.danger, emoji="\u2620")  # pyright: ignore[reportGeneralTypeIssues]
    async def quit(self, interaction: Interaction[CBot], _button: ui.Button[Self]):
        """Quit the game.

        This method is called when the user clicks the quit button. It stops the game and displays a message to the
        user.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        _button : ui.Button[Self]
            The button.
        """
        self.game.quit()
        embed = discord.Embed(
            title="You quit!", description="You quit the game without completing it.", color=discord.Color.red()
        ).set_image(url="attachment://minesweeper.png")
        file = await self.draw()
        await interaction.response.edit_message(attachments=[file], embed=embed, view=None)
        self.stop()

    @ui.button(label="Help", style=ButtonStyle.secondary, emoji="\u2049")  # pyright: ignore[reportGeneralTypeIssues]
    async def help(self, interaction: Interaction[CBot], _button: ui.Button[Self]):
        """Display the help message.

        This method is called when the user clicks the help button. It displays a help message to the user.

        Parameters
        ----------
        interaction : Interaction[CBot]
            The interaction with the user.
        _button : ui.Button[Self]
            The button.
        """
        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(
            title="Minesweeper",
            description="How to play minesweeper:",
            color=0x00FF00,
        ).set_image(url="attachment://help.gif")
        embed.add_field(name="Reveal \u26cf", value="Reveal a covered tile.", inline=False)
        embed.add_field(
            name="Chord \u2692",
            value="Reveal all tiles around an exposed number that has the correct number of flagged tiles around it. "
            "This will explode mines.",
            inline=False,
        )
        embed.add_field(
            name="Flag \U0001f6a9", value="Flag a tile, or remove the flag from a flagged tile.", inline=False
        )
        embed.add_field(name="Quit \u2620", value="Quit the game.", inline=False)
        embed.add_field(name="Help \u2049", value="Show this help.", inline=False)
        await interaction.followup.send(
            embed=embed,
            file=discord.File(  # skipcq: PYL-E1123
                fp="charbot/media/minesweeper/help.gif",
                filename="help.gif",
                description="Example playthrough of Minesweeper.",
            ),
        )
