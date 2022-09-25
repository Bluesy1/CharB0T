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
"""Charbot Module."""
import logging
import functools as _functools
import pathlib as _pathlib
import sys as _sys
from typing import Any, Generic, TypeVar
from pkgutil import iter_modules

import discord

__all__ = (
    "EXTENSIONS",
    "CBot",
    "Tree",
    "Config",
    "Interaction",
    "GuildInteraction",
    "ComponentInteraction",
    "GuildComponentInteraction",
)
__blacklist__ = [f"{__package__}.{item}" for item in ("__main__", "bot", "card", "errors", "types", "translator")]

EXTENSIONS = [module.name for module in iter_modules(__path__, f"{__package__}.") if module.name not in __blacklist__]
T = TypeVar("T", bound="CBot")


class _Config:
    """Config Class.

    This class is used to access the config file.

    You can access the config _file by using the following syntax:

    Config["section"]["key"]

    or by calling the config object:

    Config("section", "subsection", "key")

    Both of these will return the value of the key in the config _file, or raise the appropriate error as if trying to
        access a nonexistent key in a dict, or incorrect slicing of a str/int.
    """

    __instance__: "_Config"
    _file: _pathlib.Path = _pathlib.Path(__file__).parent / "config.toml"
    logger = logging.getLogger("charbot.config")

    def clear_cache(self):
        """Clear the config cache if a config has changed"""
        self.__call__.cache_clear()

    def __new__(cls):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super(_Config, cls).__new__(cls)
        return cls.__instance__

    def __getitem__(self, item: str) -> dict[str, Any]:
        return self(item)  # pyright: ignore[reportGeneralTypeIssues]

    @_functools.cache
    def __call__(self, *args: str) -> str | int | dict[str, Any]:
        if _sys.version_info >= (3, 11):
            import tomllib  # type: ignore
        else:
            import tomli as tomllib
        with open(self._file, "rb") as f:
            config = tomllib.load(f)
        badkey: Any = ""
        try:
            for item in args:
                if not isinstance(item, str):
                    badkey = item
                    raise TypeError(f"Config keys must be strings, {item!r} is a {type(item)}.")
                config = config[item]
            return config
        except KeyError:
            self.logger.exception("Tried to get key %s from config file, but it was not found.", ":".join(args))
            raise
        except TypeError:
            self.logger.exception(
                "Tried to get key %s from config file, but a non string key %r of type %s was passed.",
                ":".join([str(arg) for arg in args]),
                badkey,
                type(badkey),
            )
            raise
        finally:
            self.logger.info("Got key %s from config file.", ":".join(args))


class Interaction(discord.Interaction, Generic[T]):  # skipcq: PY-D0002
    client: T


class GuildInteraction(Interaction[T]):  # skipcq: PY-D0002
    client: T
    guild: discord.Guild
    user: discord.Member


class ComponentInteraction(Interaction[T]):  # skipcq: PY-D0002
    client: T
    message: discord.Message


class GuildComponentInteraction(Interaction[T]):  # skipcq: PY-D0002
    client: T
    guild: discord.Guild
    message: discord.Message
    user: discord.Member


Config = _Config()

from .bot import CBot, Tree  # noqa: E402
