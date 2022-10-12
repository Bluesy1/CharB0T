# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
import pytest

from discord import Locale
from discord.app_commands import locale_str, TranslationContext, TranslationContextLocation

from charbot.translator import Translator


@pytest.fixture()
def translator() -> Translator:
    return Translator()


@pytest.fixture()
def locale() -> Locale:
    return Locale.american_english


@pytest.mark.asyncio
async def test_translate_with_data(translator: Translator, locale: Locale):
    context: TranslationContext = TranslationContext(TranslationContextLocation.other, data={"awarded": 5})
    key: locale_str = locale_str("minesweeper-win-description")
    # If translate returns None, set result to empty string for assert comparison.
    result: str | None = await translator.translate(key, locale, context)
    assert result is not None, "Result should not be None"
    assert "You gained 5 points." in result, "Should say awarded 5 points"
