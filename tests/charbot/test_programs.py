# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock

import aiohttp
import discord
import pytest

from charbot import errors, programs


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_bot():
    """Mock discord.Client."""
    mock_bot = AsyncMock(spec=programs.CBot)
    mock_bot.CHANNEL_ID = programs.CBot.CHANNEL_ID
    mock_bot.ALLOWED_ROLES = programs.CBot.ALLOWED_ROLES
    return mock_bot


async def test_programs_init(mock_bot):
    """Test the initialization of the programs' module."""
    cog = programs.Reputation(mock_bot)
    assert cog.bot is mock_bot
    assert isinstance(cog.session, aiohttp.ClientSession)
    assert cog.sudoku_regex.pattern == r"(\d{81}).*([01]{81})"
    await cog.cog_unload()
    assert cog.session.closed


async def test_interaction_check_no_guild(mock_bot):
    """Test the interaction check when the interaction is not in a guild."""
    cog = programs.Reputation(mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = None
    cog = programs.Reputation(mock_bot)
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value.args[0] == "Programs can't be used in direct messages."


async def test_interaction_check_wrong_guild(mock_bot):
    """Test the interaction check when the interaction is in the wrong guild."""
    cog = programs.Reputation(mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 0
    with pytest.raises(discord.app_commands.NoPrivateMessage) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value.args[0] == "Programs can't be used in this server."


async def test_interaction_check_wrong_channel(mock_bot):
    """Test the interaction check when the interaction is in the wrong channel."""
    cog = programs.Reputation(mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 225345178955808768
    mock_interaction.channel = AsyncMock(spec=discord.TextChannel)
    mock_interaction.channel.id = 0
    with pytest.raises(errors.WrongChannelError) as exc:
        await cog.interaction_check(mock_interaction)
    assert exc.value._channel == 969972085445238784
    assert str(exc.value) == "This command can only be run in the channel <#969972085445238784> ."


async def test_interaction_check_no_allowed_roles(mock_bot):
    """Test the interaction check when the interaction is in the wrong channel."""
    cog = programs.Reputation(mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 225345178955808768
    mock_interaction.channel = AsyncMock(spec=discord.TextChannel)
    mock_interaction.channel.id = 969972085445238784
    mock_interaction.user = AsyncMock(spec=discord.Member)
    with pytest.raises(errors.MissingProgramRole) as exc:
        await cog.interaction_check(mock_interaction)
    assert (
        exc.value.args[0]
        == "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', "
        "'969627321239760967', or '969626979353632790'"
    )
    assert exc.value.missing_roles == [
        337743478190637077,
        685331877057658888,
        969629622453039104,
        969629628249563166,
        969629632028614699,
        969628342733119518,
        969627321239760967,
        969626979353632790,
    ]
    assert str(exc.value) == (
        "You are missing at least one of the required roles: '337743478190637077', '685331877057658888', "
        "'969629622453039104', '969629628249563166', '969629632028614699', '969628342733119518', '969627321239760967', "
        "or '969626979353632790' - you must be at least level 1 to use this command/button."
    )


async def test_interaction_check_allowed(mock_bot):
    """Test the interaction check when the interaction is in the right channel and guild."""
    cog = programs.Reputation(mock_bot)
    mock_interaction = AsyncMock(spec=discord.Interaction)
    mock_interaction.guild = AsyncMock(spec=discord.Guild)
    mock_interaction.guild.id = 225345178955808768
    mock_interaction.channel = AsyncMock(spec=discord.TextChannel)
    mock_interaction.channel.id = 969972085445238784
    mock_interaction.user = AsyncMock(spec=discord.Member)
    mock_interaction.user.roles = [
        discord.Object(id=337743478190637077),
        discord.Object(id=685331877057658888),
    ]
    assert await cog.interaction_check(mock_interaction)
