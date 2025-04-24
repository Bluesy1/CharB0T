import asyncio
import os
import pathlib
from typing import cast

import asyncpg
import asyncpg.cluster
import pytest
import pytest_asyncio


if os.name != "nt":
    import uvloop

    # Also test uvloop on non windows OSes
    @pytest.fixture(
        scope="session",
        params=(
            asyncio.DefaultEventLoopPolicy(),
            uvloop.EventLoopPolicy(),
        ),
    )
    def event_loop_policy(request):
        return request.param


from sys import modules

import niquests
import niquests.adapters
from niquests.packages import urllib3  # pyright: ignore


# responses is tied to Requests
# and Niquests is entirely compatible with it.
# we can fool it without effort.
modules["requests"] = niquests
modules["requests.adapters"] = niquests.adapters
modules["requests.models"] = niquests.models
modules["requests.exceptions"] = niquests.exceptions
modules["requests.packages.urllib3"] = urllib3


@pytest.fixture(scope="session")
def cluster() -> asyncpg.cluster.TempCluster:  # pyright: ignore[reportInvalidTypeForm]
    """Create the temp database cluster"""
    test_cluster = asyncpg.cluster.TempCluster()
    test_cluster.init()
    test_cluster.start(port="dynamic")
    yield test_cluster  # pyright: ignore[reportReturnType]
    test_cluster.stop()


@pytest_asyncio.fixture
async def database(cluster) -> asyncpg.Pool:  # pyright: ignore[reportInvalidTypeForm]
    """Create a database pool for a test."""
    pool = cast(asyncpg.Pool, await asyncpg.create_pool(**cluster.get_connection_spec(), database="postgres"))
    await pool.execute((pathlib.Path(__file__).parent.parent.parent / "schema.sql").read_text())
    await pool.execute("INSERT INTO users (id, points) VALUES (001, 50) ON CONFLICT DO NOTHING")
    await pool.execute(
        "INSERT INTO banners (user_id, quote, color, cooldown, approved) VALUES (001, $1, $2, now(), FALSE)"
        " ON CONFLICT DO NOTHING",
        "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
        str(0x3498DB),
    )
    yield pool  # pyright: ignore[reportReturnType]
    await pool.close()
