# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import pathlib
from typing import cast

import asyncpg
import asyncpg.cluster
import pytest
import pytest_asyncio

from charbot import setup_custom_datatypes


@pytest.fixture(scope="session")
def cluster() -> asyncpg.cluster.TempCluster:  # pyright: ignore[reportGeneralTypeIssues]
    """Create the temp database cluster"""
    test_cluster = asyncpg.cluster.TempCluster()
    test_cluster.init()
    test_cluster.start(port="dynamic")
    yield test_cluster
    test_cluster.stop()


@pytest_asyncio.fixture
async def database(cluster) -> asyncpg.Pool:  # pyright: ignore[reportGeneralTypeIssues]
    """Create a database pool for a test."""
    pool = cast(
        asyncpg.Pool,
        await asyncpg.create_pool(**cluster.get_connection_spec(), database="postgres"),
    )
    with open(pathlib.Path(__file__).parent.parent.parent / "schema.sql", "r") as schema:
        await pool.execute(schema.read())
    pool._init = setup_custom_datatypes
    await pool.execute("INSERT INTO users (id, points) VALUES (001, 50) ON CONFLICT DO NOTHING")
    await pool.execute(
        "INSERT INTO banners (user_id, quote, gradient, color, cooldown, approved) VALUES"
        " (001, $1, $2, $3, now(), FALSE) ON CONFLICT DO NOTHING",
        "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
        False,
        str(0x3498DB),
    )
    yield pool
    await pool.close()
