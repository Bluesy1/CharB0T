# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncio
import pathlib
from typing import cast

import asyncpg
import asyncpg.cluster
import pytest
import pytest_asyncio
import uvloop

from charbot import setup_custom_datatypes


@pytest.fixture(scope="session")
def cluster() -> asyncpg.cluster.TempCluster:  # pyright: ignore[reportGeneralTypeIssues]
    """Create the temp database cluster"""
    test_cluster = asyncpg.cluster.TempCluster()
    test_cluster.init()
    test_cluster.start(port="dynamic")
    yield test_cluster
    test_cluster.stop()


@pytest.fixture(scope="session")
def event_loop():
    """Create the event loop"""
    uvloop.install()
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def database(cluster) -> asyncpg.Pool:  # pyright: ignore[reportGeneralTypeIssues]
    """Create a database pool for a test."""
    conn = await asyncpg.connect(**cluster.get_connection_spec(), database="postgres")
    with open(pathlib.Path(__file__).parent.parent.parent / "schema.sql", "r") as schema:
        await conn.execute(schema.read())
    await conn.close()
    pool = cast(
        asyncpg.Pool,
        await asyncpg.create_pool(**cluster.get_connection_spec(), database="postgres", init=setup_custom_datatypes),
    )
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
