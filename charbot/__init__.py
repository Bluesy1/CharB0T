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
from typing import Any


__all__ = ("CBot", "Tree", "Config")


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
    _file: str = "config.toml"

    def __new__(cls):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super(_Config, cls).__new__(cls)
        return cls.__instance__

    def __getitem__(self, item: str) -> Any | dict[str, Any]:
        try:
            import tomllib  # type: ignore
        except ImportError:
            import tomli as tomllib
        with open(self._file, "rb") as f:
            return tomllib.load(f)[item]

    def __call__(self, *args, **kwargs):
        try:
            import tomllib  # type: ignore
        except ImportError:
            import tomli as tomllib
        with open(self._file, "rb") as f:
            config = tomllib.load(f)
        for item in args:
            config = config[item]
        return config


Config = _Config()

from .bot import CBot, Tree  # noqa: E402
