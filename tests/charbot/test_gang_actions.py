# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncio

import asyncpg
import discord
import pytest
from pytest_mock import MockerFixture

from charbot.gangs.actions import banner, join, create
from charbot.gangs import utils


@pytest.mark.parametrize(
    "base,color,gradient,expected",
    [
        (
            None,
            None,
            True,
            "You need to specify a base image, or if you want a gradient, you must specify the second color!",
        ),
        (None, None, False, None),
        ("Test", "Test", False, "You can't specify both a base image and a color!"),
        ("Test", None, False, None),
        (None, "Test", False, None),
    ],
)
def test_check_parameters(base: str | None, color: str | None, gradient: bool, expected: str | None):
    assert banner.check_parameters(base, color, gradient) == expected  # type: ignore


@pytest.mark.asyncio
async def test_download_banner_bg_not_image(mocker: MockerFixture):
    """Check that an error is raised returned the background is not an image"""
    file = mocker.AsyncMock(spec=discord.Attachment, content_type="text/plain")
    assert await banner.download_banner_bg(file, mocker.AsyncMock(), 1) == "The base image must be a PNG or JPEG!"


@pytest.mark.asyncio
async def test_download_banner_bg_image(mocker: MockerFixture, monkeypatch):
    """Check that an error is raised returned the background is an image"""
    mocked = mocker.AsyncMock(spec=asyncio.to_thread)
    monkeypatch.setattr(banner.asyncio, "to_thread", mocked)
    file = mocker.AsyncMock(spec=discord.Attachment, content_type="image/png")
    assert await banner.download_banner_bg(file, mocker.AsyncMock(), 1) is None
    mocked.assert_awaited_once()
    file.read.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_banner_bg_image_fail(mocker: MockerFixture, monkeypatch):
    """Check that an error is raised returned the background fails to download"""
    mocked = mocker.AsyncMock(spec=asyncio.to_thread, side_effect=ValueError)
    monkeypatch.setattr(banner.asyncio, "to_thread", mocked)
    file = mocker.AsyncMock(spec=discord.Attachment, content_type="image/png")
    assert await banner.download_banner_bg(file, mocker.AsyncMock(), 1) == "Failed to grab image, try again."
    mocked.assert_awaited_once()
    file.read.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "val,expected",
    [
        (None, "You are not in a gang!"),
        ({"leader": False, "leadership": False}, "You are not the leadership of your gang!"),
        ({"leader": True, "points": 400}, "You don't have enough rep to request a banner! (Have: 400, Need: 500)"),
        ({"leader": True, "points": 500}, None),
    ],
)
async def test_allowed_banner_check(mocker: MockerFixture, val: dict[str, bool | int] | None, expected: str | None):
    """Check that the banner check works as expected"""
    assert (
        await banner.allowed_banner(
            mocker.AsyncMock(spec=asyncpg.Connection, fetchrow=mocker.AsyncMock(return_value=val)), 1
        )
        == expected
    )


@pytest.mark.asyncio
async def test_join_gang_no_exist(mocker: MockerFixture):
    """Check that the join gang check works as expected"""
    assert (
        await join.try_join(
            mocker.AsyncMock(spec=asyncpg.Connection, fetchval=mocker.AsyncMock(return_value=None)),
            "Any",
            1,
        )
        == "That gang doesn't exist!"
    )


@pytest.mark.asyncio
async def test_join_gang_no_points(mocker: MockerFixture):
    """Check that the join gang check works as expected"""
    assert (
        await join.try_join(
            mocker.AsyncMock(
                spec=asyncpg.Connection,
                fetchval=mocker.AsyncMock(side_effect=["Any", None]),
            ),
            "Any",
            1,
        )
        == "You have never gained any points, try gaining some first!"
    )


@pytest.mark.asyncio
async def test_join_gain_not_enough_points(mocker: MockerFixture):
    """Check that the join gang check works as expected"""
    assert (
        await join.try_join(
            mocker.AsyncMock(
                spec=asyncpg.Connection,
                fetchval=mocker.AsyncMock(side_effect=["Any", 10, 50]),
            ),
            "Any",
            1,
        )
        == "You don't have enough rep to join that gang! You need at least 50 rep to join that gang, and you have 10."
    )


@pytest.mark.asyncio
async def test_join_gang_success(mocker: MockerFixture):
    """Check that the join gang check works as expected"""
    assert await join.try_join(
        mocker.AsyncMock(
            spec=asyncpg.Connection,
            fetchval=mocker.AsyncMock(side_effect=["Any", 50, 10, 40]),
        ),
        "Any",
        1,
    ) == (40, 10)


@pytest.mark.asyncio
async def test_create_discord_objects(mocker: MockerFixture):
    """Check that the creation of discord objects is done correctly"""
    guild = mocker.AsyncMock(spec=discord.Guild)
    user = mocker.AsyncMock(spec=discord.Member)
    category = mocker.AsyncMock(spec=discord.CategoryChannel)
    color = utils.ColorOpts.White
    await create.create_gang_discord_objects(guild, user, category, color)
    guild.create_role.assert_awaited_once()
    guild.create_text_channel.assert_awaited_once()
    user.add_roles.assert_awaited_once()
    role_kwargs = guild.create_role.await_args.kwargs
    channel_args, channel_kwargs = guild.create_text_channel.await_args
    user_kwargs = user.add_roles.await_args.kwargs
    assert role_kwargs["name"] == "White Gang"
    assert role_kwargs["color"] == color.value
    assert channel_args[0] == "white-gang"
    assert channel_kwargs["category"] is category
    assert user_kwargs["reason"] == f"New gang created by {user}"


@pytest.mark.asyncio
async def test_check_gang_conditions_duplicate_name(mocker: MockerFixture):
    """Check that the creation of a gang fails if the name is a duplicate"""
    assert (
        await create.check_gang_conditions(
            mocker.AsyncMock(spec=asyncpg.Connection, fetchval=mocker.AsyncMock(return_value=1)),
            1,
            utils.ColorOpts.White,
            1,
            1,
        )
        == "A gang with that name/color already exists!"
    )


@pytest.mark.asyncio
async def test_check_gang_conditions_no_points(mocker: MockerFixture):
    """Check that the creation of a gang fails if the user doesn't have enough points"""
    assert (
        await create.check_gang_conditions(
            mocker.AsyncMock(spec=asyncpg.Connection, fetchval=mocker.AsyncMock(side_effect=[0, None])),
            1,
            utils.ColorOpts.White,
            1,
            1,
        )
        == "You have never gained any points, try gaining some first!"
    )


@pytest.mark.asyncio
async def test_check_gang_conditions_not_enough_points(mocker: MockerFixture):
    """Check that the creation of a gang fails if the user doesn't have enough points"""
    assert (
        await create.check_gang_conditions(
            mocker.AsyncMock(spec=asyncpg.Connection, fetchval=mocker.AsyncMock(side_effect=[0, 10])),
            1,
            utils.ColorOpts.White,
            1,
            1,
        )
        == "You don't have enough rep to create a gang! You need at least 102 rep to create a gang. (100 combined with "
        "the baseline join and recurring costs are required to form a gang)"
    )


@pytest.mark.asyncio
async def test_check_gang_conditions_success(database: asyncpg.Pool):
    """Check that the creation of a gang succeeds if the user has enough points"""
    await database.execute("INSERT INTO users (id, points) VALUES (1, 200) ON CONFLICT(id) DO UPDATE SET points = 200")
    async with database.acquire() as conn:
        assert await create.check_gang_conditions(conn, 1, utils.ColorOpts.White, 1, 1) == 98
    await database.execute("DELETE FROM users WHERE id = 1")
