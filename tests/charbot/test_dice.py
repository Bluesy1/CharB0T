# -*- coding: utf-8 -*-
import random
from unittest.mock import Mock

import discord
import pytest
from discord.ext import commands

from charbot import dice


@pytest.fixture()
def not_random(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda *args: 1)


class TestDice:
    def test_valid_roll(self, not_random):
        assert dice.roll("1d4+5") == "rolled `1d4+5` got `1, 5` for a total value of: 6"

    def test_valid_implicit_roll(self, not_random):
        assert dice.roll("d4+5") == "rolled `d4+5` got `1, 5` for a total value of: 6"

    def test_valid_implicit_roll_no_bonus(self, not_random):
        assert dice.roll("d4") == "rolled `d4` got `1` for a total value of: 1"

    def test_valid_implicit_roll_only_bonus(self, not_random):
        assert dice.roll("5") == "rolled `5` got `5` for a total value of: 5"

    def test_invalid_roll(self, not_random):
        assert dice.roll("1e4+5") == (
            "Error invalid argument: specified dice can only be d<int>, or if a constant modifier must be a perfect"
            " integer, positive or negative, connected with `+`, and no spaces."
        )

    def test_invalid_die(self, not_random):
        assert dice.roll("1de+5") == (
            "Error invalid argument: specified dice can only be d<int>, or if a constant modifier must be a perfect"
            " integer, positive or negative, connected with `+`, and no spaces."
        )

    @pytest.mark.asyncio
    async def test_valid_roll_async(self, not_random):
        mock_ctx = Mock(spec=commands.Context)
        mock_bot = Mock(spec=commands.Bot)
        mock_ctx.author.mention = "mock"
        cog = dice.Roll(mock_bot)
        await cog.roll.__call__(mock_ctx, mock_ctx, dice="1d4+5")
        mock_ctx.reply.assert_called_once_with(
            "mock rolled `1d4+5` got `1, 5` for a total value of: 6", mention_author=True
        )

    @pytest.mark.asyncio
    async def test_invalid_roll_async(self, not_random):
        mock_ctx = Mock(spec=commands.Context)
        mock_bot = Mock(spec=commands.Bot)
        mock_ctx.author.mention = "mock"
        cog = dice.Roll(mock_bot)
        await cog.roll.__call__(mock_ctx, mock_ctx, dice="1e4+5")
        mock_ctx.reply.assert_called_once_with(
            "mock Error invalid argument: specified dice can only be d<int>, or if a constant"
            " modifier must be a perfect integer, positive or negative, connected with `+`, and no spaces.",
            mention_author=True,
        )

    def test_cog_check_no_guild(self):
        mock_ctx = Mock(spec=commands.Context)
        mock_ctx.guild = None
        mock_bot = Mock(spec=commands.Bot)
        cog = dice.Roll(mock_bot)
        assert cog.cog_check(mock_ctx) is False

    def test_cog_check_not_allowed(self):
        mock_ctx = Mock(spec=commands.Context)
        mock_ctx.guild = Mock(spec=discord.Guild)
        mock_ctx.author = Mock(spec=discord.Member)
        mock_role = Mock(spec=discord.Role)
        mock_role.id = 0
        mock_ctx.author.roles = [mock_role]
        mock_bot = Mock(spec=commands.Bot)
        cog = dice.Roll(mock_bot)
        assert cog.cog_check(mock_ctx) is False

    def test_cog_check_allowed(self):
        mock_ctx = Mock(spec=commands.Context)
        mock_ctx.guild = Mock(spec=discord.Guild)
        mock_ctx.author = Mock(spec=discord.Member)
        mock_role = Mock(spec=discord.Role)
        mock_role.id = 338173415527677954
        mock_ctx.author.roles = [mock_role]
        mock_bot = Mock(spec=commands.Bot)
        cog = dice.Roll(mock_bot)
        assert cog.cog_check(mock_ctx) is True

    @pytest.mark.asyncio
    async def test_cog_load(self):
        mock_bot = Mock(spec=commands.Bot)
        await dice.setup(mock_bot)
        mock_bot.add_cog.assert_called_once()
