# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import io
import pathlib
import sys
from datetime import timedelta
from os import environ

import asyncpg
import discord
import pytest
from PIL import Image
from discord.utils import utcnow
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.gangs import banner
from charbot.gangs.types import BannerStatus


def test_interpolate():
    """Test the interpolate function"""
    for actual, expected in zip(
        banner.interpolate((0, 0, 0), (255, 255, 255), 10),
        [
            (0, 0, 0),
            (26, 26, 26),
            (51, 51, 51),
            (76, 76, 76),
            (102, 102, 102),
            (128, 128, 128),
            (153, 153, 153),
            (178, 178, 178),
            (204, 204, 204),
            (230, 230, 230),
        ],
        strict=True,
    ):
        assert tuple(actual) == expected, f"Got {actual} but expected {expected}"


def test_interpolate_low_interval():
    """Test the interpolate function with no slices"""
    with pytest.raises(ValueError, match="Interval must be greater than 1, got 0"):
        for ret in banner.interpolate((0, 0, 0), (255, 255, 255), 0):
            assert False, f"Expected no return but got {ret}"


def test_interpolate_bad_color():
    """Test the interpolate function with an invalid color"""
    with pytest.raises(ValueError, match=r"Invalid start color: \(-1, 0, 0\)"):
        for _ in banner.interpolate((-1, 0, 0), (255, 255, 255), 10):
            pass
    with pytest.raises(ValueError, match=r"Invalid end color: \(-1, 255, 255\)"):
        for _ in banner.interpolate((0, 0, 0), (-1, 255, 255), 10):
            pass


@pytest.mark.parametrize("prestige", [0, 5, 10, 15, 20])
def test_prestige_positions(prestige: int):
    """Test that the prestige starts get positioned correctly"""
    for actual, expected in zip(
        banner.prestige_positions(prestige),
        ((955 - (x * 50), 220, 25) for x in range(prestige) if x < 19),
        strict=True,
    ):
        assert actual == expected, f"Got {actual} but expected {expected}"


@pytest.mark.xfail(
    sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons", strict=True
)
def test_static_color_banner():
    """Check the banner gets created properly with a solid color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_solid_color.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                discord.Color.blue(),
                "Name",
                profile,
                "Blue",
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                "dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.xfail(
    sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons", strict=True
)
def test_gradient_color_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_gradient_color.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                (discord.Color.blue(), discord.Color.red()),
                "Name",
                profile,
                "Blue",
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                "dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.xfail(
    sys.platform == "win32" or environ.get("pythonLocation", "").startswith("/opt/hostedtoolcache"),
    reason="PIL not consistent between platforms due to various reasons",
    strict=True,
)
def test_image_background_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_image_background.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                pathlib.Path(__file__).parent / "media/test_image.jpeg",
                "Name",
                profile,
                "Blue",
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                "dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.asyncio
async def test_banner_approval_view(mocker: MockerFixture, database):
    """Check the banner approval view gets created properly"""
    # noinspection SpellCheckingInspection
    status: BannerStatus = {
        "user_id": 1,
        "quote": "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
        "color": "0x3498DB",
        "cooldown": utcnow() + timedelta(days=7),
        "approved": False,
        "gradient": False,
        "gang_color": 0x3498DB,
        "prestige": 3,
        "name": "Blue",
    }
    view = banner.ApprovalView(status, 2)
    mock_bot = mocker.AsyncMock(spec=CBot)
    mock_bot.pool = database
    mock_member = mocker.AsyncMock(spec=discord.Member)
    mock_member.id = 2
    mock_interaction = mocker.AsyncMock(spec=discord.Interaction)
    mock_interaction.user = mock_member
    mock_interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    mock_interaction.client = mock_bot
    assert await view.interaction_check(mock_interaction) is True, "Interaction check should return True"
    await view.cancel.callback(mock_interaction)
    mock_interaction.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_interaction.edit_original_response.assert_awaited_once_with(
        content="Banner approval session cancelled.", attachments=[], view=None
    )
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.approve.callback(mock_interaction)
    mock_interaction.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_interaction.edit_original_response.assert_awaited_once_with(
        content="Banner approved.", attachments=[], view=None
    )
    assert (
        await database.fetchval("SELECT approved FROM banners WHERE user_id = 1") is True
    ), "Banner should be approved"
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.deny.callback(mock_interaction)
    mock_interaction.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_interaction.edit_original_response.assert_awaited_once_with(
        content="Banner denied.", attachments=[], view=None
    )
    assert await database.fetchrow("SELECT * FROM banners WHERE user_id = 1") is None, "Banner should not exist"


@pytest.mark.asyncio
async def test_gen_banner_fail(mocker: MockerFixture, monkeypatch, database: asyncpg.Pool):
    """Test the gen banner command works as expected"""
    monkeypatch.setattr(banner, "generate_banner", mocker.AsyncMock(side_effect=Exception("Test")))
    assert await banner.gen_banner(database, mocker.AsyncMock(spec=discord.Member)) is None


@pytest.mark.asyncio
async def test_gen_banner_success(mocker: MockerFixture, monkeypatch, database: asyncpg.Pool):
    """Test the gen banner command works as expected"""
    gen_banner_mock = mocker.AsyncMock(return_value=io.BytesIO(b"test"))
    monkeypatch.setattr(banner, "generate_banner", gen_banner_mock)
    member: discord.Member = discord.Object(1)  # type: ignore
    await database.execute("INSERT INTO users (id, points) VALUES (1, 100) ON CONFLICT (id) DO UPDATE SET points = 100")
    await database.execute(
        "INSERT INTO gangs (name, color, leader, role, channel, control, join_base, join_slope, upkeep_base, "
        "upkeep_slope, all_paid) VALUES ('White', 0, 1, 1, 1, 1, 1, 1, 1, 1, FALSE) ON CONFLICT DO NOTHING",
    )
    await database.execute("INSERT INTO gang_members (user_id, gang, leadership) VALUES (1, 'White', TRUE)")
    await database.execute(
        "INSERT INTO banners (user_id, quote, color, cooldown, approved, gradient) VALUES "
        "(1, 'test', 0, $1, TRUE, FALSE) ON CONFLICT DO NOTHING",
        utcnow() - timedelta(days=1),
    )
    val = await banner.gen_banner(database, member)
    await database.execute("DELETE FROM banners WHERE user_id = 1")
    await database.execute("DELETE FROM gang_members WHERE user_id = 1")
    await database.execute("DELETE FROM gangs WHERE name = 'White'")
    await database.execute("DELETE FROM users WHERE id = 1")
    assert val is not None, "Should return a file"


if __name__ == "__main__":
    with open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as f, io.BytesIO(f.read()) as b:
        # noinspection SpellCheckingInspection
        Image.open(
            banner.banner(
                (discord.Color.blue()),
                "Name",
                b,
                "Blue",
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        ).show()
