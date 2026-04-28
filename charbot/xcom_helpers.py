"""Helpers for xcom.py"""

import io
import pathlib
from typing import Literal

from .xcfp import CharacterPool  # https://github.com/gnutrino/xcfp


__all__ = (
    "XCOM_COUNTRIES",
    "COUNTRIES_BY_NAME",
    "RACES",
    "ATTITUDES",
    "create_base_bin_file",
    "get_bin_name",
    "merge_bin_files",
    "validate_pool",
)

_MEDIA_BASE = pathlib.Path(__file__).parent / "media/xcom"
_MALE_TEMPLATE = pathlib.Path(_MEDIA_BASE, "MALE.bin").read_bytes()
_FEMALE_TEMPLATE = pathlib.Path(_MEDIA_BASE, "FEMALE.bin").read_bytes()
_MALE_FILENAME_BYTESTRING = b"\x26\x00\x00\x00\x00\x00\x00\x00\x22\x00\x00\x00CharacterPool\\Importable\\MALE.bin\x00"
_FEMALE_FILENAME_BYTESTRING = (
    b"\x28\x00\x00\x00\x00\x00\x00\x00\x24\x00\x00\x00CharacterPool\\Importable\\FEMALE.bin\x00"
)
_FIRST_NAME_BYTESTRING = b"\x0b\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00RFirst\x00"
_LAST_NAME_BYTESTRING = b"\x0a\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00RLast\x00"
_NICK_NAME_BYTESTRING = b"\x0c\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00'RNick'\x00"
_BIO_BYTESTRING = b"\x09\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00RBIO\x00"  # cspell: disable-line
_COUNTRY_BYTESTRING = b"\x14\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00Country_USA\x00\x00\x00\x00\x00"
# Race:: 0: Caucasian, 1: African, 2: Asian, 3: Hispanic
_RACE_HEADER = b"iRace\x00\x00\x00\x00\x00\x0c\x00\x00\x00IntProperty\x00\x00\x00\x00\x00"
_RACE_BYTESTRING = b"\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
# Attitude:: 0: By The Book, 1: Laid Back, 2: Normal, 3: Twitchy, 4: Happy-Go-Lucky, 5: Hard Luck, 6: Intense
_ATTITUDE_HEADER = b"iAttitude\x00\x00\x00\x00\x00\x0c\x00\x00\x00IntProperty\x00\x00\x00\x00\x00"
_ATTITUDE_BYTESTRING = b"\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
_PADDING = b"\x00" * 4
_NONE_PROP = b"\x05\x00\x00\x00None\x00" + _PADDING

XCOM_COUNTRIES = {
    "Country_USA": "United States",
    "Country_Russia": "Russia",
    "Country_China": "China",
    "Country_UK": "United Kingdom",
    "Country_Germany": "Germany",
    "Country_France": "France",
    "Country_Japan": "Japan",
    "Country_India": "India",
    "Country_Australia": "Australia",
    "Country_Italy": "Italy",
    "Country_SouthKorea": "South Korea",
    "Country_Turkey": "Turkey",
    "Country_Indonesia": "Indonesia",
    "Country_Spain": "Spain",
    "Country_Pakistan": "Pakistan",
    "Country_Canada": "Canada",
    "Country_Iran": "Iran",
    "Country_Israel": "Israel",
    "Country_Egypt": "Egypt",
    "Country_Brazil": "Brazil",
    "Country_Argentina": "Argentina",
    "Country_Mexico": "Mexico",
    "Country_SouthAfrica": "South Africa",
    "Country_Poland": "Poland",
    "Country_Ukraine": "Ukraine",
    "Country_Nigeria": "Nigeria",
    "Country_Venezuela": "Venezuela",
    "Country_Greece": "Greece",
    "Country_Columbia": "Colombia",
    "Country_Portugal": "Portugal",
    "Country_Sweden": "Sweden",
    "Country_Ireland": "Ireland",
    "Country_Scotland": "Scotland",
    "Country_Norway": "Norway",
    "Country_Netherlands": "Netherlands",
    "Country_Belgium": "Belgium",
}
COUNTRIES_BY_NAME = {v: k for k, v in XCOM_COUNTRIES.items()}
RACES = ("Caucasian", "African", "Asian", "Hispanic")
ATTITUDES = ("By The Book", "Laid Back", "Normal", "Twitchy", "Happy-Go-Lucky", "Hard Luck", "Intense")


# Size (4), Padding, Value
def _write_int_prop(prop: int) -> bytes:
    return b"\x04\x00\x00\x00" + _PADDING + prop.to_bytes(4, byteorder="little")


# Size + 4, Padding, Size, Value
def _write_str_prop(prop: str | bytes) -> bytes:
    if isinstance(prop, str):
        prop = prop.encode("cp1251")

    if not prop.endswith(b"\x00"):
        prop += b"\x00"

    prop = prop.replace(b"\n", b"\r")
    prop_len = len(prop)
    return (prop_len + 4).to_bytes(4, byteorder="little") + _PADDING + prop_len.to_bytes(4, byteorder="little") + prop


# Similar to str: Size + 8, Padding, Size, Value, Padding
def _write_name_prop(prop: str | bytes) -> bytes:
    if isinstance(prop, str):
        prop = prop.encode("cp1251")

    if not prop.endswith(b"\x00"):
        prop += b"\x00"

    prop = prop.replace(b"\n", b"\r")
    prop_len = len(prop)
    return (
        (prop_len + 8).to_bytes(4, byteorder="little")
        + _PADDING
        + prop_len.to_bytes(4, byteorder="little")
        + prop
        + _PADDING
    )


def create_base_bin_file(
    first_name: str,
    last_name: str,
    nickname: str,
    gender: str,
    country: str,
    race: str,
    attitude: str,
    backstory: str,
) -> bytes:
    if gender == "male":
        result = _MALE_TEMPLATE
        FILENAME_BYTESTRING = _MALE_FILENAME_BYTESTRING
    else:
        result = _FEMALE_TEMPLATE
        FILENAME_BYTESTRING = _FEMALE_FILENAME_BYTESTRING
    result = result.replace(FILENAME_BYTESTRING, _write_str_prop(b"CharacterPool\\Importable\\TEMPLATE.bin"))

    # Names
    result = result.replace(_FIRST_NAME_BYTESTRING, _write_str_prop(first_name))
    result = result.replace(_LAST_NAME_BYTESTRING, _write_str_prop(last_name))
    if not (nickname.startswith("'") and nickname.endswith("'")):
        nickname = f"'{nickname}'"
    result = result.replace(_NICK_NAME_BYTESTRING, _write_str_prop(nickname))

    # Character Properties
    if country not in XCOM_COUNTRIES and country in COUNTRIES_BY_NAME:
        country = COUNTRIES_BY_NAME[country]
    result = result.replace(_COUNTRY_BYTESTRING, _write_name_prop(country))
    result = result.replace(_RACE_HEADER + _RACE_BYTESTRING, _RACE_HEADER + _write_int_prop(RACES.index(race)))
    result = result.replace(
        _ATTITUDE_HEADER + _ATTITUDE_BYTESTRING, _ATTITUDE_HEADER + _write_int_prop(ATTITUDES.index(attitude))
    )

    # Bio
    result = result.replace(_BIO_BYTESTRING, _write_str_prop(backstory))

    return result


def validate_pool(pool: bytes) -> Literal[False] | str:
    with io.BytesIO(pool) as b:
        p = CharacterPool(b)
        try:
            chars = list(p.characters())
            if len(chars) != 1:
                return False
        except Exception:
            return False
        else:
            char = chars[0]
            if char.characterTemplate != "Soldier":
                return False
            details = chars[0].details()
            details = "".join(
                line for line in details.splitlines(keepends=True) if not line.startswith(("appearance:", "timestamp:"))
            )
            return details.rstrip()


def get_bin_name(pool: bytes) -> str:
    with io.BytesIO(pool) as b:
        p = CharacterPool(b)
        chars = list(p.characters())
        if len(chars) != 1:
            raise ValueError("Pool must contain exactly one character.")
        char = chars[0]
        return f"{char.firstName} {char.nickName} {char.lastName}"


def merge_bin_files(name: str, pools: list[bytes]) -> bytes:
    if not pools:
        raise ValueError("No pools provided.")
    num_pools = len(pools)
    file = b"\xff" * 4  # Start of file is 4 bytes of FF
    file += b"\x0e\x00\x00\x00CharacterPool\x00" + _PADDING
    file += b"\x0e\x00\x00\x00ArrayProperty\x00" + _PADDING
    file += _write_int_prop(num_pools)
    file += b"\x0d\x00\x00\x00PoolFileName\x00" + _PADDING
    file += b"\x0c\x00\x00\x00StrProperty\x00" + _PADDING
    file += _write_str_prop(b"CharacterPool\\Importable\\" + name.encode("cp1251"))
    file += _NONE_PROP
    file += num_pools.to_bytes(4, byteorder="little")

    SPLIT_ON = _NONE_PROP + b"\x01\x00\x00\x00"

    for pool in pools:
        _, character = pool.split(SPLIT_ON, 1)
        file += character

    return file
