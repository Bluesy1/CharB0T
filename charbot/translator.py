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
from discord.app_commands import TranslationContextLocation, TranslationContextTypes, locale_str
from fluent.runtime import FluentResourceLoader, FluentLocalization


class Translator(app_commands.Translator):
    """Custom translator class for Charbot"""

    def __init__(self):
        self.loader = FluentResourceLoader("i18n/{locale}")
        self.supported_locales = [Locale.american_english]

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> str | None:
        """Translate a string using the Fluent syntax

        Parameters
        ----------
        string: locale_str
            The string to translate
        locale: Locale
            The locale to translate to
        context: TranslationContextTypes
            The context to use for translation

        Returns
        -------
        str | None
            The translated string or None if the string is not found
        """
        if locale not in self.supported_locales:
            return None
        path = pathlib.Path(__file__).parent.parent / "i18n" / locale.value
        if not path.exists():
            return None
        fluent = FluentLocalization(
            [locale.value],
            ["dice.ftl", "minesweeper.ftl", "programs.ftl", "errors.ftl", "giveaway.ftl", "levels.ftl"],
            self.loader,
        )
        if context.location is TranslationContextLocation.command_name:
            key = f"{context.data.qualified_name.replace(' ', '-')}-name"
        elif context.location is TranslationContextLocation.command_description:
            key = f"{context.data.qualified_name.replace(' ', '-')}-description"
        elif context.location is TranslationContextLocation.group_name:
            key = f"{context.data.qualified_name.replace(' ', '-')}-name"
        elif context.location is TranslationContextLocation.group_description:
            key = f"{context.data.qualified_name.replace(' ', '-')}-description"
        elif context.location is TranslationContextLocation.parameter_name:
            # noinspection PyUnresolvedReferences
            key = f"{context.data.command.qualified_name.replace(' ', '-')}-parameter-{context.data.name}-name"
        elif context.location is TranslationContextLocation.parameter_description:
            # noinspection PyUnresolvedReferences
            key = f"{context.data.command.qualified_name.replace(' ', '-')}-parameter-{context.data.name}-description"
        elif context.location is TranslationContextLocation.choice_name:
            key = f"choice-{context.data.name}-name"
        elif context.location is TranslationContextLocation.other:
            key = f"{string.message.replace(' ', '-')}"
        else:
            return None
        translated = fluent.format_value(key, string.extras)
        if translated == key or translated is None:
            return None
        return translated
