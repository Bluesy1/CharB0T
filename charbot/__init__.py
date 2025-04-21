"""Charbot Module."""

import functools as _functools
import logging
import os as _os
import pathlib as _pathlib
from importlib import metadata as _metadata
from pkgutil import iter_modules
from typing import Any


__title__ = "charbot"
__author__ = "Bluesy1"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present Bluesy1"
__version__ = _metadata.version(__title__)

__all__ = (
    "EXTENSIONS",
    "CBot",
    "Tree",
    "Config",
)
__blacklist__ = [f"{__package__}.{item}" for item in ("__main__", "bot", "card", "errors", "types", "rust", "programs")]

EXTENSIONS = [module.name for module in iter_modules(__path__, f"{__package__}.") if module.name not in __blacklist__]


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
    if path := _os.getenv("CHARBOT_CONFIG_FILE"):
        _file = _pathlib.Path(path).resolve(strict=True)
    else:
        _file: _pathlib.Path = _pathlib.Path(__file__).parent.parent / "config.toml"
    logger = logging.getLogger("charbot.config")

    def clear_cache(self):  # pragma: no cover
        """Clear the config cache if a config has changed"""
        self.logger.info(
            "Clearing config cache, this can cause previously expected values to disappear. Cache stats: %r",
            self.get.cache_info(),
        )
        self.get.cache_clear()

    def __new__(cls):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super().__new__(cls)
        return cls.__instance__

    def __getitem__(self, item: str) -> dict[str, Any]:
        return self.get(item)  # pyright: ignore[reportReturnType]

    @_functools.cache
    def get(self, *args: str) -> str | int | dict[str, Any]:
        """Get a config key"""
        import tomllib

        with self._file.open("rb") as f:
            config = tomllib.load(f)
        badkey: Any = ""
        try:
            for item in args:
                if not isinstance(item, str):
                    badkey = item
                    raise TypeError(f"Config keys must be strings, {item!r} is a {type(item)}.")
                config = config[item]
            self.logger.info("Got key %s from config file.", ":".join(args))
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


Config = _Config()

from .bot import CBot, Tree  # noqa: E402
