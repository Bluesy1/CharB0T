# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import pytest
from discord import Locale
from discord.app_commands import (
    locale_str,
    TranslationContext,
    TranslationContextLocation,
    Command,
    Group,
    Parameter,
    Choice,
)

# noinspection PyProtectedMember
from discord.app_commands.transformers import CommandParameter
from pytest_mock import MockerFixture

from charbot.translator import Translator


@pytest.fixture()
def translator() -> Translator:
    """Get a translator instance."""
    return Translator()


@pytest.fixture()
def locale() -> Locale:
    """Get a locale."""
    return Locale.american_english


@pytest.mark.asyncio
async def test_translate_with_data(translator: Translator, locale: Locale):
    """Test the translate method with data"""
    context: TranslationContext = TranslationContext(TranslationContextLocation.other, data={"awarded": 5})
    key: locale_str = locale_str("minesweeper-win-description")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "You gained 5 points." in result, "Should say awarded 5 points"


@pytest.mark.asyncio
async def test_translate_command_name(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test that the command name is translated"""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.command_name, data=mocker.AsyncMock(spec=Command, qualified_name="programs sudoku")
    )
    key: locale_str = locale_str("sudoku")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "sudoku" == result, "Should say Sudoku"


@pytest.mark.asyncio
async def test_translate_command_description(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test that the command description is translated"""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.command_description,
        data=mocker.AsyncMock(spec=Command, qualified_name="programs sudoku"),
    )
    key: locale_str = locale_str("Play minesweeper")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "Play a Sudoku puzzle" == result, "Should say Play a Sudoku puzzle"


@pytest.mark.asyncio
async def test_translate_group_name(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test that the group name is translated"""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.group_name, data=mocker.AsyncMock(spec=Group, qualified_name="programs")
    )
    key: locale_str = locale_str("programs")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "programs" == result, "Should say programs"


@pytest.mark.asyncio
async def test_translate_group_description(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test that the group description is translated."""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.group_description, data=mocker.AsyncMock(spec=Group, qualified_name="programs")
    )
    key: locale_str = locale_str("programs")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "Programs to gain you rep." == result, "Should say Programs to gain you rep."


@pytest.mark.asyncio
async def test_translate_parameter_name(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test translating parameter name."""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.parameter_name,
        data=Parameter(CommandParameter(name="mobile"), command=mocker.Mock(qualified_name="programs sudoku")),
    )
    key: locale_str = locale_str("mobile")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "mobile" == result, "Should say mobile"


@pytest.mark.asyncio
async def test_translate_parameter_description(translator: Translator, locale: Locale, mocker: MockerFixture):
    """Test that the parameter description is translated."""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.parameter_description,
        data=Parameter(CommandParameter(name="mobile"), command=mocker.Mock(qualified_name="programs sudoku")),
    )
    key: locale_str = locale_str("mobile")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert (
        "Whether to turn off formatting that only works on desktop." == result
    ), "Should say Whether to turn off formatting that only works on desktop"


@pytest.mark.asyncio
async def test_translate_choice_name(translator: Translator, locale: Locale):
    """Test that the choice name is translated."""
    context: TranslationContext = TranslationContext(
        TranslationContextLocation.choice_name, data=Choice(name="EASY", value="EASY")
    )
    key: locale_str = locale_str("EASY")
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "EASY" == result, "Should say EASY"


@pytest.mark.asyncio
async def test_translate_bad_key(translator: Translator, locale: Locale):
    """Test that a bad key returns None."""
    context: TranslationContext = TranslationContext(TranslationContextLocation.other, {})
    key: locale_str = locale_str("bad-key")
    result: str | None = await translator.translate(key, locale, context)
    assert result is None, "Result should be None"


@pytest.mark.asyncio
async def test_translate_unreachable_code(translator: Translator, locale: Locale):
    """Test that unreachable code raises."""
    context: TranslationContext = TranslationContext("a", {})  # type: ignore
    key: locale_str = locale_str("unreachable-code")
    with pytest.raises(RuntimeError) as exc:
        await translator.translate(key, locale, context)
    assert exc.value.args[0] == "Unreachable code: non translation context location passed as location"
