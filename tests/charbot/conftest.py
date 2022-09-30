# -*- coding: utf-8 -*-
import pathlib
from typing import cast

import asyncpg
import asyncpg.cluster
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def cluster() -> asyncpg.cluster.TempCluster:  # pyright: ignore[reportGeneralTypeIssues]
    """Create the temp database cluster"""
    test_cluster = asyncpg.cluster.TempCluster()
    test_cluster.init()
    test_cluster.start(port="dynamic")
    yield test_cluster
    cluster.stop()


@pytest_asyncio.fixture
async def database(cluster) -> asyncpg.Pool:  # pyright: ignore[reportGeneralTypeIssues]
    """Create a database pool for a test."""
    pool = cast(asyncpg.Pool, await asyncpg.create_pool(**cluster.get_connection_spec(), database="postgres"))
    with open(pathlib.Path(__file__).parent.parent.parent / "schema.sql", "r") as schema:
        await pool.execute(schema.read())
    await pool.execute("INSERT INTO users (id, points) VALUES (001, 50)")
    yield pool
    await pool.close()
