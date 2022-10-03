# -*- coding: utf-8 -*-
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
    context = TranslationContext(TranslationContextLocation.other, data={"awarded": 5})
    key = locale_str("minesweeper-win-description")
    result = await translator.translate(key, locale, context)
    assert "You gained 5 points." in result, "Should say awarded 5 points"
