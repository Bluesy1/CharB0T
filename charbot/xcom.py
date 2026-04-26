"""XCOM Stuff"""

import asyncio
import logging
from typing import Literal

import discord
from discord import app_commands, ui
from discord.app_commands import Choice, Range
from discord.ext.commands import Cog

from . import CBot, constants
from .xcom_helpers import XCOM_COUNTRIES, COUNTRIES_BY_NAME, RACES, ATTITUDES, create_base_bin_file

_LOGGER = logging.getLogger(__name__)
_REQUESTS_CHANNEL_ID: int = ...


class CharacterRequestModal(ui.Modal, title="Character Request"):
    """Modal for requesting a character."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        nickname: str,
        gender: str,
        country: str,
        race: str,
        attitude: str,
    ):
        super().__init__(timeout=1200)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.attitude = attitude
        self.desc = ui.TextDisplay(f"""\
You are initiating a request for a character with the following details. Please provide a description of what you want the character to look like, provide a backstory if you wish, and then hit submit below to confirm.
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {country}
**Race**: {race}
**Attitude**: {attitude}
""")
        self.add_item(self.desc)
        self.description = ui.Label(
            text="Description",
            description="Enter a brief description of the character.",
            component=ui.TextInput(
                placeholder="Enter a brief description of the character.",
                style=discord.TextStyle.paragraph,
                max_length=500,
            ),
        )
        self.add_item(self.description)
        self.bio = ui.Label(
            text="Biography",
            description="Optional: Enter a detailed biography of the character.",
            component=ui.TextInput(
                placeholder="Enter a detailed biography of the character.",
                style=discord.TextStyle.paragraph,
                max_length=2000,
                required=False,
            ),
        )
        self.add_item(self.bio)

    async def on_submit(self, interaction: discord.Interaction[CBot]) -> None:
        await interaction.response.defer(ephemeral=True)
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.bio.component, ui.TextInput)
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            await conn.execute(
                """\
INSERT INTO xcom_character_request (requestor, first_name, last_name, nickname, country, gender, race, attitude, details, biography)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
""",
                interaction.user.id,
                self.first_name,
                self.last_name,
                self.nickname,
                self.country,
                self.gender,
                self.race,
                self.attitude,
                self.description.component.value,
                self.bio.component.value,
            )
        await interaction.followup.send("Your character request has been submitted!")


class CreateRequestButton(ui.Button):
    """A button to for the create request layout."""

    def __init__(
        self, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str, attitude: str
    ):
        super().__init__(label="Request Character", style=discord.ButtonStyle.primary)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.attitude = attitude

    async def callback(self, interaction: discord.Interaction[CBot]) -> None:
        """Handle the button click."""
        await interaction.response.send_modal(
            CharacterRequestModal(
                self.first_name, self.last_name, self.nickname, self.gender, self.country, self.race, self.attitude
            )
        )


class CreateRequestLayout(ui.LayoutView):
    """A layout view to demonstrate editing an existing character request."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        nickname: str,
        gender: str,
        country: str,
        race: str,
        attitude: str,
    ):
        super().__init__()
        self.add_item(
            ui.Section(
                ui.TextDisplay("## Confirm your request"),
                ui.TextDisplay(
                    "Please review your submitted details below, then press the request character button."
                    + " Doing so will set the following properties automatically, and you will be prompted to fill out provide a description and optionally backstory for your character:\n"
                    + f"- **Name**: {first_name} '{nickname}' {last_name} \n"
                    + f"- **Sex**: {gender.capitalize()} \n"
                    + f"- **Country**: {country} \n"
                    + f"- **Race**: {race} \n"
                    + f"- **Attitude**: {attitude} \n"
                ),
                accessory=CreateRequestButton(first_name, last_name, nickname, gender, country, race, attitude),
            )
        )


class CharacterEditModal(ui.Modal, title="Edit Character Request"):
    """Modal for editing a request for a character."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        nickname: str,
        gender: str,
        country: str,
        race: str,
        attitude: str,
        existing_details: str,
        existing_backstory: str,
    ):
        super().__init__(timeout=600)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.attitude = attitude
        self.existing_details = existing_details
        self.existing_backstory = existing_backstory
        self.desc = ui.TextDisplay(f"""\
You are currently editing a character with the following details. Hit submit below to confirm.
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {country}
**Race**: {race}
**Attitude**: {attitude}
""")
        self.add_item(self.desc)
        self.description = ui.Label(
            text="Description",
            description="Enter a brief description of the character.",
            component=ui.TextInput(
                placeholder="Enter a brief description of the character.",
                style=discord.TextStyle.paragraph,
                max_length=500,
                default=self.existing_details,
            ),
        )
        self.add_item(self.description)
        self.bio = ui.Label(
            text="Biography",
            description="Optional: Enter a detailed biography of the character.",
            component=ui.TextInput(
                placeholder="Enter a detailed biography of the character.",
                style=discord.TextStyle.paragraph,
                max_length=2000,
                required=False,
                default=self.existing_backstory,
            ),
        )
        self.add_item(self.bio)

    async def on_submit(self, interaction: discord.Interaction[CBot]) -> None:
        await interaction.response.defer(ephemeral=True)
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.bio.component, ui.TextInput)
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            await conn.execute(
                """\
UPDATE xcom_character_request 
SET req_dt=CURRENT_TIMESTAMP, fulfiller=NULL, first_name=$1, last_name=$2,
    nickname=$3, country=$4, gender=$5, race=$6, attitude=$7, details=$8, biography=$9
WHERE requestor=$10;
""",
                self.first_name,
                self.last_name,
                self.nickname,
                self.country,
                self.gender,
                self.race,
                self.attitude,
                self.description.component.value,
                self.bio.component.value,
                interaction.user.id,
            )
        await interaction.followup.send("Your character request has been updated!")


class EditRequestButton(ui.Button):
    """A button to for the edit request layout."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        nickname: str,
        gender: str,
        country: str,
        race: str,
        attitude: str,
        existing_details: str,
        existing_backstory: str,
    ):
        super().__init__(label="Edit Request", style=discord.ButtonStyle.primary)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.attitude = attitude
        self.existing_details = existing_details
        self.existing_backstory = existing_backstory

    async def callback(self, interaction: discord.Interaction[CBot]) -> None:
        """Handle the button click."""
        await interaction.client.pool.execute(
            "UPDATE xcom_character_request SET fulfiller=$1 WHERE requestor=$1", interaction.user.id
        )
        await interaction.response.send_modal(
            CharacterEditModal(
                self.first_name,
                self.last_name,
                self.nickname,
                self.gender,
                self.country,
                self.race,
                self.attitude,
                self.existing_details,
                self.existing_backstory,
            )
        )


class EditRequestLayout(ui.LayoutView):
    """A layout view to demonstrate editing an existing character request."""

    def __init__(
        self,
        existing: dict,
        first_name: str,
        last_name: str,
        nickname: str,
        gender: str,
        country: str,
        race: str,
        attitude: str,
    ):
        super().__init__()
        self.add_item(
            ui.TextDisplay(
                "# Request Already Submitted\n"
                + "You already have a pending character request. Here are the details of your request:\n"
                + f"- **Name:** {existing['first_name']} '{existing['nickname']}' {existing['last_name']}\n"
                + f"- **Sex:** {existing['sex'].capitalize()}\n"
                + f"- **Country:** {COUNTRIES_BY_NAME.get(existing['country'], existing['country'])}\n"
                + f"- **Race:** {RACES[existing['race']]}\n"
                + f"- **Attitude:** {ATTITUDES[existing['attitude']]}\n"
                + f"- **Details:** {existing['existing']}\n"
                + f"- **Biography:** {existing['biography'] if existing['biography'] else 'N/A'}\n\n"
                + "Your request is currently awaiting review by our volunteers."
            )
        )
        self.add_item(
            ui.Section(
                ui.TextDisplay("## Change your request"),
                ui.TextDisplay(
                    "If you want to change your request while its still awaiting review, you may do so."
                    + " Doing so will set the following properties automatically, and you will be prompted to fill out the rest of the details of your request again:\n"
                    + f"- **Name**: {first_name} '{nickname}' {last_name} \n"
                    + f"- **Sex**: {gender.capitalize()} \n"
                    + f"- **Country**: {country} \n"
                    + f"- **Race**: {race} \n"
                    + f"- **Attitude**: {attitude} \n"
                ),
                accessory=EditRequestButton(
                    first_name,
                    last_name,
                    nickname,
                    gender,
                    country,
                    race,
                    attitude,
                    existing["details"],
                    existing["biography"],
                ),
            )
        )


class XCOM(Cog):
    """XCOM related commands and utilities."""

    character = app_commands.Group(
        name="character",
        description="Commands related to character requests.",
        guild_ids=constants.GUILD_IDS,
        default_permissions=discord.Permissions(manage_permissions=True),
    )

    def __init__(self, bot: CBot) -> None:
        self.bot = bot
        self.reserve_lock = asyncio.Lock()

    async def cog_unload(self) -> None:
        async with self.reserve_lock:
            return await super().cog_unload()

    async def country_autocomplete(self, interaction: discord.Interaction, current: str) -> list[Choice[str]]:
        """Autocomplete for the country field."""
        return [
            Choice(name=value, value=key) for key, value in XCOM_COUNTRIES.items() if current.lower() in value.lower()
        ][:25]

    @character.command(name="request")
    @app_commands.choices(
        race=[Choice(name=race, value=i) for i, race in enumerate(RACES)],
        attitude=[Choice(name=attitude, value=i) for i, attitude in enumerate(ATTITUDES)],
    )
    @app_commands.autocomplete(country=country_autocomplete)
    async def request_character(
        self,
        interaction: discord.Interaction,
        first_name: Range[str, None, 25],
        last_name: Range[str, None, 25],
        nickname: Range[str, None, 25],
        gender: Literal["male", "female"],
        country: str,  # autocomplete for this.....
        race: Choice[int],  # Choices decorator
        attitude: Choice[int],  # Choices decorator
    ) -> None:
        """Request a character to be added to the XCOM roster.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction instance for the command.
        first_name: str
            The first name for the character being requested.
        last_name: str
            The last name for the character being requested.
        nickname: str
            The nickname for the character being requested.
        gender: Literal["male", "female"]
            The gender of the character being requested.
        country: str
            The country of origin for the character being requested.
        race: int
            The race of the character being requested.
        attitude: int
            The personality of the character being requested.
        """

        if country not in COUNTRIES_BY_NAME:
            await interaction.response.send_message(
                "Invalid country. Please choose a valid country from the autocomplete suggestions.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT fulfiller FROM xcom_character_request WHERE requestor = $1",
                interaction.user.id,
            )
            if existing and existing["fulfiller"] is not None:
                await interaction.followup.send(
                    "You already have a pending character request that is in the process of being designed or has been designed."
                    + " If that design has not been finalized, you can request changes to it through the designated thread for your request,"
                    + " otherwise please contact the mod team if there is a reason for further changes.",
                    ephemeral=True,
                )
            elif existing:
                details = await conn.fetchrow(
                    "SELECT * FROM xcom_character_request WHERE requestor = $1", interaction.user.id
                )
                assert details is not None
                view = EditRequestLayout(
                    existing=dict(details),
                    first_name=first_name,
                    last_name=last_name,
                    nickname=nickname,
                    gender=gender,
                    country=country,
                    race=race.name,
                    attitude=attitude.name,
                )
                await interaction.followup.send(view=view, ephemeral=True)
            else:
                view = CreateRequestLayout(
                    first_name=first_name,
                    last_name=last_name,
                    nickname=nickname,
                    gender=gender,
                    country=country,
                    race=race.name,
                    attitude=attitude.name,
                )
                await interaction.followup.send(view=view, ephemeral=True)

    @character.command(name="reserve")
    async def reserve_request(self, interaction: discord.Interaction):
        """Reserve the next request in the character request queue for creation.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction instance for the command.
        """
        await interaction.response.defer(ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if not (member := interaction.user).get_role(constants.HELPER_ROLE_ID):
            await interaction.followup.send(
                "You are not allowed to use this command! Reach out to the mod team to become an XCOM helper."
            )
            return
        guild = member.guild
        async with self.reserve_lock, self.bot.pool.acquire() as conn:
            next_req = discord.utils.MISSING
            while True:
                next_req = await conn.fetchrow("""\
    SELECT requestor, first_name, last_name, nickname, gender, country, race, attitude, details, biography
    FROM xcom_character_request
    WHERE fulfiller IS NULL
    ORDER BY req_dt DESC""")
                if next_req is None:
                    await interaction.followup.send("There are no unassigned character requests at this time!")
                    return
                requestor_id = next_req["requestor"]
                requestor = guild.get_member(requestor_id)
                if requestor is not None:
                    break
                try:
                    requestor = await guild.fetch_member(requestor_id)
                except discord.NotFound, discord.Forbidden:
                    await conn.execute("DELETE FROM xcom_character_request WHERE requestor=$1;", requestor_id)
                    _LOGGER.debug("Deleting request from user %s: Could not find user on server.", requestor_id)
                else:
                    break
            first_name: str = next_req["first_name"]
            last_name = next_req["last_name"]
            nickname = next_req["nickname"]
            gender = next_req["gender"]
            country = next_req["country"]
            race = next_req["race"]
            attitude = next_req["attitude"]
            biography = next_req["biography"]
            bin_bytes = create_base_bin_file(
                first_name, last_name, nickname, gender, country, race, attitude, biography
            )
            channel: discord.TextChannel = guild.get_channel(_REQUESTS_CHANNEL_ID)  # pyright: ignore[reportAssignmentType]
            thread = await channel.create_thread(name=f"Character Request for {member}")
            await thread.add_user(member)
            await thread.add_user(requestor)
            starter_msg = await thread.send(
                f"""\
Hi {member.mention}, here are the details of the character {requestor.mention} has requested:
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {country}
**Race**: {race}
**Attitude**: {attitude}

Here is the details of the requested appearance to use to modify the attached bin:
{next_req["details"]}""",
                file=discord.File(bin_bytes, f"{first_name.upper()}.bin"),
            )
            await thread.send(f"Character Biography (Info Only):\n{biography}")
            await starter_msg.pin()
            await interaction.followup.send(
                f"You have been assigned the request from {requestor.mention}!"
                f" Please see {thread.mention}: {starter_msg.jump_url}."
            )
            await conn.execute(
                "UPDATE xcom_character_request SET fulfiller=$1, fulfill_thread=$2 WHERE requestor=$3",
                member.id,
                thread.id,
                requestor_id,
            )


async def setup(bot: CBot) -> None:
    """Add the XCOM cog to the bot."""
    await bot.add_cog(XCOM(bot))
