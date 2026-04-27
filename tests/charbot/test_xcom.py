"""Tests for various xcom pure helper functions"""

import pathlib

import pytest

from charbot import xcom_helpers


MEDIA_BASE = pathlib.Path(__file__).parent / "media/xcom"


@pytest.mark.parametrize("file", ["BAD.bin", "MULTI.bin"])
def test_validate_pool_reject_bad_bins(file):
    assert xcom_helpers.validate_pool(pathlib.Path(MEDIA_BASE, file).read_bytes()) is False


@pytest.mark.parametrize("file", ["MALE.bin", "FEMALE.bin"])
def test_validate_pool_accept_good_bins(file):
    assert isinstance(xcom_helpers.validate_pool(pathlib.Path(MEDIA_BASE, file).read_bytes()), str)


@pytest.mark.parametrize(
    ("gender", "expected"), [("male", "RET_MALE.bin"), ("female", "RET_FEMALE.bin")], ids=("male", "female")
)
def test_create_base_bins(gender, expected):
    expected_bytes = pathlib.Path(MEDIA_BASE, expected).read_bytes()
    actual = xcom_helpers.create_base_bin_file(
        "FOO",
        "BAR",
        "'BAZ'",
        gender,
        "Country_Canada",
        "Asian",
        "Happy-Go-Lucky",
        "Backstory\nwith\nnewlines\rand\rcarriage returns",
    )
    assert actual == expected_bytes
