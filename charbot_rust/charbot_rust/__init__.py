# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT
# noinspection PyUnresolvedReferences
from .charbot_rust import *  # pyright: ignore[reportMissingImports] # noqa: F403,F401

# noinspection PyUnresolvedReferences
from . import charbot_rust

# noinspection PyUnresolvedReferences
__doc__ = charbot_rust.__doc__
