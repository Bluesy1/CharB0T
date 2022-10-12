# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
import pathlib

from discord import app_commands, Locale
from discord.app_commands import TranslationContextLocation, TranslationContextTypes, locale_str
from fluent.runtime import FluentResourceLoader, FluentLocalization


class Translator(app_commands.Translator):
    """Custom translator class for Charbot"""

    def __init__(self):
        self.loader = FluentResourceLoader("i18n/{locale}")
        self.supported_locales = [Locale.american_english, Locale.spain_spanish, Locale.french]

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

        translated = fluent.format_value(key, context.data)
        return None if translated == key or translated is None else translated
