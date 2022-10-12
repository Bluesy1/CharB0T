# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import io
import pathlib

import discord
import pytest
from PIL import Image

from charbot.betas import banner


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


def test_static_color_banner():
    """Check the banner gets created properly with a solid color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_solid_color.png") as expected,
    ):
        assert (
            Image.open(
                banner.banner(
                    discord.Color.blue(),
                    "Name",
                    profile,
                    "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                    "dolo",
                    3,
                )
            )
            == expected
        ), "Got unexpected banner"


def test_gradient_color_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_gradient_color.png") as expected,
    ):
        assert (
            Image.open(
                banner.banner(
                    (discord.Color.blue(), discord.Color.red()),
                    "Name",
                    profile,
                    "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                    "dolo",
                    3,
                )
            )
            == expected
        ), "Got unexpected banner"


def test_image_background_banner():
    """Check the banner gets created properly with a gradient color background"""
    with (
        open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as file,
        io.BytesIO(file.read()) as profile,
        Image.open(pathlib.Path(__file__).parent / "media/test_banner_image_background.png") as expected,
    ):
        assert (
            Image.open(
                banner.banner(
                    pathlib.Path(__file__).parent / "media/test_image.jpeg",
                    "Name",
                    profile,
                    "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et "
                    "dolo",
                    3,
                )
            )
            == expected
        ), "Got unexpected banner"


if __name__ == "__main__":
    with open(pathlib.Path(__file__).parent / "media/test_avatar.png", "rb") as f, io.BytesIO(f.read()) as b:
        Image.open(
            banner.banner(
                pathlib.Path(__file__).parent / "media/test_image.jpeg",
                "Name",
                b,
                "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolo",
                3,
            )
        ).show()
