import io
import pathlib
import sys
from datetime import timedelta
from os import environ

import discord
import pytest
from discord.utils import utcnow
from PIL import Image
from pytest_mock import MockerFixture

from charbot import CBot
from charbot.betas import banner
from charbot.betas._types import BannerStatus
from charbot.betas.views.banner import ApprovalView


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


@pytest.mark.parametrize("interval", [0, 1])
def test_interpolate_low_interval(interval):
    """Test the interpolate function with 0 or 1 slices"""
    with pytest.raises(ValueError, match=f"Interval must be greater than 1, got {interval}"):
        _ = list(banner.interpolate((0, 0, 0), (255, 255, 255), interval))


def test_interpolate_bad_color():
    """Test the interpolate function with an invalid color"""
    with pytest.raises(ValueError, match=r"Invalid start color: \(-1, 0, 0\)"):
        _ = list(banner.interpolate((-1, 0, 0), (255, 255, 255), 10))
    with pytest.raises(ValueError, match=r"Invalid end color: \(-1, 255, 255\)"):
        _ = list(banner.interpolate((0, 0, 0), (-1, 255, 255), 10))


@pytest.mark.parametrize("prestige", [0, 5, 10, 15, 20])
def test_prestige_positions(prestige: int):
    """Test that the prestige starts get positioned correctly"""
    for actual, expected in zip(
        banner.prestige_positions(prestige),
        ((955 - (x * 50), 220, 25) for x in range(prestige) if x < 19),
        strict=True,
    ):
        assert actual == expected, f"Got {actual} but expected {expected}"


@pytest.mark.xfail(sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons")
def test_static_color_banner():
    """Check the banner gets created properly with a solid color background"""
    with (
        io.BytesIO((pathlib.Path(__file__).parent / "media/test_avatar.png").read_bytes()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_solid_color.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                discord.Color.blue(),
                "Name",
                profile,
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.xfail(sys.platform == "win32", reason="PIL not consistent between platforms due to various reasons")
def test_gradient_color_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        io.BytesIO((pathlib.Path(__file__).parent / "media/test_avatar.png").read_bytes()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_gradient_color.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                (discord.Color.blue(), discord.Color.red()),
                "Name",
                profile,
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.xfail(
    sys.platform == "win32" or environ.get("PYTHONLOCATION", "").startswith("/opt/hostedtoolcache"),
    reason="PIL not consistent between platforms due to various reasons",
)
def test_image_background_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        io.BytesIO((pathlib.Path(__file__).parent / "media/test_avatar.png").read_bytes()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_image_background.png") as expected,
    ):
        got = Image.open(
            banner.banner(
                pathlib.Path(__file__).parent / "media/test_image.jpeg",
                "Name",
                profile,
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        )
        assert got == expected, "Got unexpected banner"


@pytest.mark.asyncio
async def test_banner_approval_view(mocker: MockerFixture, database):
    """Check the banner approval view gets created properly"""
    status: BannerStatus = {
        "user_id": 1,
        "quote": "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
        "color": "0x3498DB",
        "cooldown": utcnow() + timedelta(days=7),
        "approved": False,
    }
    view = ApprovalView(status, 2)
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
    assert await database.fetchval("SELECT approved FROM banners WHERE user_id = 1") is True, (
        "Banner should be approved"
    )
    mock_interaction.reset_mock()
    mock_interaction.response.reset_mock()
    await view.deny.callback(mock_interaction)
    mock_interaction.response.defer.assert_awaited_once_with(ephemeral=True)
    mock_interaction.edit_original_response.assert_awaited_once_with(
        content="Banner denied.", attachments=[], view=None
    )
    assert await database.fetchrow("SELECT * FROM banners WHERE user_id = 1") is None, "Banner should not exist"


if __name__ == "__main__":
    with io.BytesIO((pathlib.Path(__file__).parent / "media/test_avatar.png").read_bytes()) as b:
        Image.open(
            banner.banner(
                pathlib.Path(__file__).parent / "media/test_image.jpeg",
                "Name",
                b,
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        ).show()
