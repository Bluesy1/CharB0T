# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from typing import Literal as _Literal

def translate(locale: _Literal["en-US", "es-ES", "fr", "nl"], key: str, args: dict[str, int | float | str]) -> str:
    """Translate a string into the given locale.

    Parameters
    ----------
    locale : {'en-US', 'es-ES', 'fr', 'nl'}
        The locale to translate to, e.g. 'en-US'. If the locale exists, but the key does not,
         en-US will be used if the key exists there.
    key : str
        The key to translate.
    args : dict[str, int | float | str]
        The arguments to format the string with. If no arguments, pass an empty dict, ie ``{}``.

    Returns
    -------
    str
        The translated string.

    Raises
    ------
    KeyError
        If the key does not exist in the given locale.
    ValueError
        If the key exists in the given locale, but the string cannot be interpreted, or translation fails.
    TypeError
        If a non string, int, or float is passed as an arg value.
    """
    ...
