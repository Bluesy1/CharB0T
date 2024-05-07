from typing import Literal, cast

from discord import Locale, app_commands
from discord.app_commands import TranslationContextLocation, TranslationContextTypes, locale_str

from charbot_rust import translate


_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]


class Translator(app_commands.Translator):
    """Custom translator class for Charbot"""

    def __init__(self):
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
        if (
            locale not in self.supported_locales and context.location is not TranslationContextLocation.other
        ):  # pragma: no cover
            return None
        if context.location is TranslationContextLocation.command_name:
            key = f"{context.data.qualified_name.replace(' ', '-')}-name"
        elif context.location is TranslationContextLocation.command_description:
            key = f"{context.data.qualified_name.replace(' ', '-')}-description"
        elif context.location is TranslationContextLocation.group_name:
            key = f"{context.data.qualified_name.replace(' ', '-')}-name"
        elif context.location is TranslationContextLocation.group_description:
            key = f"{context.data.qualified_name.replace(' ', '-')}-description"
        elif context.location is TranslationContextLocation.parameter_name:
            key = f"{context.data.command.qualified_name.replace(' ', '-')}-parameter-{context.data.name}-name"
        elif context.location is TranslationContextLocation.parameter_description:
            key = f"{context.data.command.qualified_name.replace(' ', '-')}-parameter-{context.data.name}-description"
        elif context.location is TranslationContextLocation.choice_name:
            key = f"choice-{context.data.name}-name"
        elif context.location is TranslationContextLocation.other:
            key = f"{string.message.replace(' ', '-')}"
        else:
            raise RuntimeError("Unreachable code: non translation context location passed as location")
        try:
            if isinstance(context.data, dict):
                translated = translate(
                    cast(_LanguageTag, locale.value),
                    key,
                    {k: v for k, v in context.data.items() if isinstance(v, (int, float, str))}
                    | {k: v for k, v in string.extras.items() if isinstance(v, (int, float, str))},
                )
            else:
                translated = translate(
                    cast(_LanguageTag, locale.value),
                    key,
                    {k: v for k, v in string.extras.items() if isinstance(v, (int, float, str))},
                )
            return None if translated == key or translated is None else translated
        except RuntimeError:
            return None
