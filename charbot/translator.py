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
import pathlib

from discord import app_commands, Locale
from discord.app_commands import locale_str, TranslationContext
from fluent.runtime import FluentResourceLoader, FluentLocalization


class Translator(app_commands.Translator):
    def __init__(self):
        self.loader = FluentResourceLoader("i18n")

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> str | None:
        if locale is Locale.american_english:
            return string.message
        path = pathlib.Path(f"i18n/{locale.value}")
        if not path.exists():
            return None
        translator = FluentLocalization([locale.value], ["dice.ftl", "minesweeper.ftl", "programs.ftl"], self.loader)
        suffix = ""
        if context is TranslationContext.command_name:
            suffix = "_name"
        elif context is TranslationContext.command_description:
            suffix = "_description"
        elif context is TranslationContext.parameter_name:
            suffix = "_option_name"
        elif context is TranslationContext.parameter_description:
            suffix = "_option_description"
        elif context is TranslationContext.choice_name:
            suffix = "_choice_name"
        translated = translator.format_value(f"{string.message}{suffix}")
        if translated == f"{string.message}{suffix}" or translated is None:
            return None
        return translated
