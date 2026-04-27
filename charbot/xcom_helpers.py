"""Helpers for xcom.py"""

import pathlib


__all__ = ("XCOM_COUNTRIES", "COUNTRIES_BY_NAME", "RACES", "ATTITUDES", "create_base_bin_file")

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
PADDING = b"\x00" * 4


def _cp1521(text: str) -> bytes:
    return text.encode("cp1251")


# Size (4), Padding, Value
def _write_int_prop(prop: int) -> bytes:
    return b"\x04\x00\x00\x00" + PADDING + prop.to_bytes(4, byteorder="little")


# Size + 4, Padding, Size, Value
def _write_str_prop(prop: str | bytes) -> bytes:
    if isinstance(prop, str):
        prop = _cp1521(prop)

    if not prop.endswith(b"\x00"):
        prop += b"\x00"

    prop = prop.replace(b"\n", b"\r")
    prop_len = len(prop)
    return (prop_len + 4).to_bytes(4, byteorder="little") + PADDING + prop_len.to_bytes(4, byteorder="little") + prop


# Similar to str: Size + 8, Padding, Size, Value, Padding
def _write_name_prop(prop: str | bytes) -> bytes:
    if isinstance(prop, str):
        prop = _cp1521(prop)

    if not prop.endswith(b"\x00"):
        prop += b"\x00"

    prop = prop.replace(b"\n", b"\r")
    prop_len = len(prop)
    return (
        (prop_len + 8).to_bytes(4, byteorder="little")
        + PADDING
        + prop_len.to_bytes(4, byteorder="little")
        + prop
        + PADDING
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
):
    if gender == "male":
        result = _MALE_TEMPLATE
        FILENAME_BYTESTRING = _MALE_FILENAME_BYTESTRING
    else:
        result = _FEMALE_TEMPLATE
        FILENAME_BYTESTRING = _FEMALE_FILENAME_BYTESTRING
    result = result.replace(
        FILENAME_BYTESTRING, _write_str_prop(b"CharacterPool\\Importable\\" + _cp1521(first_name.upper()) + b".bin")
    )

    # Names
    result = result.replace(_FIRST_NAME_BYTESTRING, _write_str_prop(first_name))
    result = result.replace(_LAST_NAME_BYTESTRING, _write_str_prop(last_name))
    result = result.replace(_NICK_NAME_BYTESTRING, _write_str_prop(nickname))

    # Character Properties
    result = result.replace(_COUNTRY_BYTESTRING, _write_name_prop(XCOM_COUNTRIES[country]))
    result = result.replace(_RACE_HEADER + _RACE_BYTESTRING, _RACE_HEADER + _write_int_prop(RACES.index(race)))
    result = result.replace(
        _ATTITUDE_HEADER + _ATTITUDE_BYTESTRING, _ATTITUDE_HEADER + _write_int_prop(ATTITUDES.index(attitude))
    )

    # Bio
    result = result.replace(_BIO_BYTESTRING, _write_str_prop(backstory))

    return result
