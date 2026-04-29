"""XCOM Stuff"""
# cspell: ignore LWOTC

import asyncio
import csv
import io
import logging
import sys
import zipfile
from typing import Literal

import discord
from discord import app_commands, ui
from discord.app_commands import Choice, Range
from discord.ext import commands
from discord.ext.commands import Cog

from . import CBot, constants, xcom_helpers


_LOGGER = logging.getLogger(__name__)
_SUBMISSION_CHANNEL_ID: int = 1497045860301934714

SUBMISSION_TIER_1 = {  # Supporter High Tier (Ridiculous/Gold Patreon, Youtube Ten Gallon Fedora/Hat Lair, Silver Lifetime VIP, XCOM Helpers)
    225414953820094465,
    225414600101724170,
    842631203965501481,
    842631203965501480,
    970819808784441435,
    1497043311859466260,
}
SUBMISSION_TIER_2 = {  # All other supporters (Patreon, Youtube, Twitch, Bronze Lifetime VIP)
    338870051853697033,
    733541021488513035,
    926150286098194522,
    244673486121861120,
}


class CharacterRequestModal(ui.Modal, title="Character Request"):
    """Modal for requesting a character."""

    def __init__(self, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str):
        super().__init__(timeout=1200)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.desc = ui.TextDisplay(f"""\
You are initiating a request for a character with the following details. Please provide a description of what you want the character to look like, provide a backstory if you wish, and then hit submit below to confirm.
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {xcom_helpers.XCOM_COUNTRIES.get(country, country)}
**Race**: {race}
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
INSERT INTO xcom_character_request (requestor, first_name, last_name, nickname, country, gender, race, details, biography)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
""",
                interaction.user.id,
                self.first_name,
                self.last_name,
                self.nickname,
                self.country,
                self.gender,
                self.race,
                self.description.component.value,
                self.bio.component.value,
            )
        await interaction.followup.send("Your character request has been submitted!", ephemeral=True)


class CreateRequestButton(ui.Button):
    """A button to for the create request layout."""

    def __init__(self, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str):
        super().__init__(label="Request Character", style=discord.ButtonStyle.primary)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race

    async def callback(self, interaction: discord.Interaction[CBot]) -> None:
        """Handle the button click."""
        await interaction.response.send_modal(
            CharacterRequestModal(self.first_name, self.last_name, self.nickname, self.gender, self.country, self.race)
        )
        self.disabled = True
        view = self.view
        assert isinstance(view, ui.LayoutView)
        assert interaction.message
        try:
            await interaction.edit_original_response(view=view)
        finally:
            view.stop()


class CreateRequestLayout(ui.LayoutView):
    """A layout view to demonstrate editing an existing character request."""

    def __init__(self, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str):
        super().__init__()
        self.add_item(
            ui.Section(
                ui.TextDisplay("## Confirm your request"),
                ui.TextDisplay(
                    "Please review your submitted details below, then press the request character button."
                    + " Doing so will set the following properties automatically, and you will be prompted to fill out provide a description and optionally backstory for your character:\n"
                    + f"- **Name**: {first_name} '{nickname}' {last_name} \n"
                    + f"- **Sex**: {gender.capitalize()} \n"
                    + f"- **Country**: {xcom_helpers.XCOM_COUNTRIES.get(country, country)} \n"
                    + f"- **Race**: {race} \n"
                ),
                accessory=CreateRequestButton(first_name, last_name, nickname, gender, country, race),
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
        existing_details: str,
        existing_backstory: str,
        bot: CBot,
        user_id: int,
    ):
        super().__init__(timeout=600)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.existing_details = existing_details
        self.existing_backstory = existing_backstory
        self.bot = bot
        self.user_id = user_id
        self.desc = ui.TextDisplay(f"""\
You are currently editing a character with the following details. Hit submit below to confirm.
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {xcom_helpers.XCOM_COUNTRIES.get(country, country)}
**Race**: {race}
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
    nickname=$3, country=$4, gender=$5, race=$6, details=$7, biography=$8
WHERE requestor=$10;
""",
                self.first_name,
                self.last_name,
                self.nickname,
                self.country,
                self.gender,
                self.race,
                self.description.component.value,
                self.bio.component.value,
                interaction.user.id,
            )
        await interaction.followup.send("Your character request has been updated!", ephemeral=True)

    async def on_timeout(self) -> None:
        await self.bot.pool.execute(
            "UPDATE xcom_character_request SET fulfiller=NULL WHERE requestor=$1;", self.user_id
        )


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
                self.existing_details,
                self.existing_backstory,
                interaction.client,
                interaction.user.id,
            )
        )
        self.disabled = True
        view = self.view
        assert isinstance(view, ui.LayoutView)
        assert interaction.message
        try:
            await interaction.edit_original_response(view=view)
        finally:
            view.stop()


class EditRequestLayout(ui.LayoutView):
    """A layout view to demonstrate editing an existing character request."""

    def __init__(
        self, existing: dict, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str
    ):
        super().__init__()
        self.add_item(
            ui.TextDisplay(
                "# Request Already Submitted\n"
                + "You already have a pending character request. Here are the details of your request:\n"
                + f"- **Name:** {existing['first_name']} '{existing['nickname']}' {existing['last_name']}\n"
                + f"- **Sex:** {existing['gender'].capitalize()}\n"
                + f"- **Country:** {xcom_helpers.XCOM_COUNTRIES.get(existing['country'], existing['country'])}\n"
                + f"- **Race:** {existing['race']}\n"
                + f"- **Details:** {existing['details']}\n"
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
                    + f"- **Country**: {xcom_helpers.XCOM_COUNTRIES.get(country, country)} \n"
                    + f"- **Race**: {race} \n"
                ),
                accessory=EditRequestButton(
                    first_name,
                    last_name,
                    nickname,
                    gender,
                    country,
                    race,
                    existing["details"],
                    existing["biography"],
                ),
            )
        )


class ConfirmReplaceSubmissionView(ui.View):
    def __init__(
        self, contents: bytes, fname: str, old_message: discord.Message, details: str, user: int, preferred_class: str
    ):
        super().__init__()
        self.bin = contents
        self.fname = fname
        self.old_message = old_message
        self.details = details
        self.user = user
        self.preferred_class = preferred_class

    @ui.button(label="Replace Existing Submission", style=discord.ButtonStyle.green)
    async def replace_button(self, interaction: discord.Interaction[CBot], _: ui.Button):
        if interaction.user.id != self.user:
            await interaction.response.send_message("This is not for you!")
            return
        self.replace_button.disabled = True
        self.cancel_button.disabled = True
        await interaction.response.edit_message(content="Your previous submission will be replaced.", view=self)
        self.stop()
        await self.old_message.delete()
        with io.BytesIO(self.bin) as f:
            msg = await interaction.followup.send(interaction.user.mention, file=discord.File(f, self.fname), wait=True)
        await interaction.client.pool.execute(
            "UPDATE xcom_character_submission SET message_id = $1, preferred_class=$2 WHERE submitter = $3;",
            msg.id,
            self.preferred_class,
            interaction.user.id,
        )
        await interaction.followup.send(
            "Your submission of a character with the following details has been successful:"
            f"\nPreferred Class: {self.preferred_class}\n{self.details[:1850]}",
            ephemeral=True,
        )
        self.bin = b""

    @ui.button(label="Keep Existing Submission", style=discord.ButtonStyle.blurple)
    async def cancel_button(self, interaction: discord.Interaction, _: ui.Button):
        if interaction.user.id != self.user:
            await interaction.response.send_message("This is not for you!")
            return
        self.replace_button.disabled = True
        self.cancel_button.disabled = True
        await interaction.response.edit_message(content="Your previous submission has been maintained.", view=self)
        self.stop()
        self.bin = b""


class XCOM(Cog):
    """XCOM related commands and utilities."""

    character = app_commands.Group(
        name="character",
        description="Commands related to character requests and submissions.",
        guild_ids=constants.GUILD_IDS,
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
            Choice(name=value, value=key)
            for key, value in xcom_helpers.XCOM_COUNTRIES.items()
            if current.lower() in value.lower()
        ][:25]

    @character.command(name="request")
    @app_commands.autocomplete(country=country_autocomplete)
    async def request_character(
        self,
        interaction: discord.Interaction,
        first_name: Range[str, None, 25],
        last_name: Range[str, None, 25],
        nickname: Range[str, None, 25],
        gender: Literal["male", "female"],
        country: str,  # autocomplete for this.....
        race: Literal["Caucasian", "African", "Asian", "Hispanic"],
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
        race: Literal["Caucasian", "African", "Asian", "Hispanic"]
            The race of the character being requested.
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT fulfiller FROM xcom_character_request WHERE requestor = $1",
                interaction.user.id,
            )
            if existing and existing["fulfiller"] is not None:
                await interaction.followup.send(
                    "You already have a pending character request that is in the process of being designed or has been designed. "
                    + "If that design has not been finalized, you can request changes to it through the designated thread for your request, "
                    + "otherwise please contact the mod team if there is a reason for further changes.",
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
                    race=race,
                )
                await interaction.followup.send(view=view, ephemeral=True)
            else:
                view = CreateRequestLayout(
                    first_name=first_name,
                    last_name=last_name,
                    nickname=nickname,
                    gender=gender,
                    country=country,
                    race=race,
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

        def sort_key(req: dict) -> int:
            member = guild.get_member(req["requestor"])
            if member is None:
                return 99999  # Not cached so likely left the server, put at the end of the queue and will be cleaned up eventually
            elif any(member.get_role(role_id) for role_id in SUBMISSION_TIER_1):
                return 0
            elif any(member.get_role(role_id) for role_id in SUBMISSION_TIER_2):
                return 1
            else:
                return 2

        async with self.reserve_lock, self.bot.pool.acquire() as conn:
            unassigned = await conn.fetch("""\
SELECT requestor, first_name, last_name, nickname, gender, country, race, details, biography
FROM xcom_character_request
WHERE fulfiller IS NULL
ORDER BY req_dt DESC""")
            next_req = sorted((dict(req) for req in unassigned), key=sort_key)[0] if unassigned else None
            if next_req is None:
                await interaction.followup.send("There are no unassigned character requests at this time!")
                return
            requestor_id = next_req["requestor"]
            requestor = guild.get_member(requestor_id)
            if requestor is None:
                try:
                    requestor = await guild.fetch_member(requestor_id)
                except (discord.NotFound, discord.Forbidden):
                    await conn.execute("DELETE FROM xcom_character_request WHERE requestor=$1;", requestor_id)
                    _LOGGER.debug("Deleting request from user %s: Could not find user on server.", requestor_id)
                    await interaction.followup.send("There are no unassigned character requests at this time!")
                    return

            first_name: str = next_req["first_name"]
            last_name = next_req["last_name"]
            nickname = next_req["nickname"]
            gender = next_req["gender"]
            country = next_req["country"]
            race = next_req["race"]
            biography = next_req["biography"]
            bin_bytes = xcom_helpers.create_base_bin_file(
                first_name, last_name, nickname, gender, country, race, biography
            )
            channel: discord.TextChannel = guild.get_channel(_SUBMISSION_CHANNEL_ID)  # pyright: ignore[reportAssignmentType]
            thread = await channel.create_thread(name=f"Character Request for {requestor.name}")
            await thread.add_user(member)
            await thread.add_user(requestor)
            with io.BytesIO(bin_bytes) as file:
                starter_msg = await thread.send(
                    f"""\
    Hi {member.mention}, here are the details of the character {requestor.mention} has requested:
**Name**: {first_name} '{nickname}' {last_name}
**Sex**: {gender.capitalize()}
**Country**: {xcom_helpers.XCOM_COUNTRIES.get(country, country)}
**Race**: {race}

Here is the details of the requested appearance to use to modify the attached bin:
{next_req["details"]}""",
                    file=discord.File(file, "TEMPLATE.bin"),
                )
            await thread.send(f"Character Biography (Info Only):\n{biography[:1900]}")
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

    @character.command(name="submit")
    async def submit_file(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment,
        preferred_class: Literal[
            "Assault",
            "Grenadier",
            "Gunner",
            "Ranger",
            "Sharpshooter",
            "Shinobi",
            "Specialist",
            "Technical",
            "Psi Operative",
            "SPARK",
        ],
    ):
        """Submit your character for consideration for inclusion into Charlie's LWOTC campaign.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction instance for the command.
        file: discord.Attachment
            The character pool to validate
        preferred_class: Literal["Assault", "Grenadier", "Gunner", "Ranger", "Sharpshooter", "Shinobi", "Specialist", "Technical", "Psi Operative", "SPARK"]
            The preferred class for the character, does not guarantee the character will be added as that class.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.channel_id != _SUBMISSION_CHANNEL_ID:
            await interaction.followup.send(f"You must use this command in <#{_SUBMISSION_CHANNEL_ID}>!")
            return
        channel = interaction.channel
        user = interaction.user
        assert isinstance(channel, discord.TextChannel)
        if not (fname := file.filename).endswith(".bin"):
            await interaction.followup.send("You must submit a `.bin` file!")
            return
        try:
            contents = await file.read()
        except discord.HTTPException:
            await interaction.followup.send("Could not read the submitted `.bin` file, please try again!")
            _LOGGER.warning("Failed to read submitted .bin file named %s from user with id %s.", fname, user.id)
            return
        if not (details := xcom_helpers.validate_pool(contents)):
            await interaction.followup.send(
                "Submitted `.bin` file failed validation! Make sure it only has a single character and is a named pool."
                "\n If the character you wish to submit is not a base soldier (i.e., is a Spark or Faction Soldier), "
                "please reach out to Charlie or the Mod Team directly to discuss your request."
            )
            return
        async with self.bot.pool.acquire() as conn:
            message_id: int | None = await conn.fetchval(
                "SELECT message_id FROM xcom_character_submission WHERE submitter = $1;", user.id
            )
            if message_id is not None:
                try:
                    message = await channel.fetch_message(message_id)
                except discord.HTTPException:
                    await interaction.followup.send(
                        "An unexpected error has occurred, please open a mod support ticket!"
                    )
                    _LOGGER.warning(
                        "An error occurred while attempting to fetch a previous submission for user with id %s.",
                        user.id,
                    )
                else:
                    await interaction.followup.send(
                        f"You have a previous submission here: {message.jump_url}, do you want to replace it?",
                        view=ConfirmReplaceSubmissionView(contents, fname, message, details, user.id, preferred_class),
                        ephemeral=True,
                    )
            else:
                await interaction.followup.send("Processing your submission now.")
                with io.BytesIO(contents) as contents:
                    msg = await interaction.followup.send(
                        interaction.user.mention, file=discord.File(contents, fname), wait=True
                    )
                await conn.execute(
                    "INSERT INTO xcom_character_submission (submitter, message_id, preferred_class) VALUES ($1, $2, $3);",
                    user.id,
                    msg.id,
                    preferred_class,
                )
                await interaction.followup.send(
                    f"Your submission of a character with the following details has been successful:\nPreferred Class: {preferred_class}\n{details[:1850]}",
                    ephemeral=True,
                )

    @character.command(name="validate")
    async def validate_file(self, interaction: discord.Interaction, file: discord.Attachment):
        """Validate a character pool .bin file to ensure it meets the requirements for submission.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction instance for the command.
        file: discord.Attachment
            The character pool to validate
        """
        await interaction.response.defer(ephemeral=True)
        if not file.filename.endswith(".bin"):
            await interaction.followup.send("Only `.bin` files can be validated!")
            return
        try:
            contents = await file.read()
        except discord.HTTPException:
            await interaction.followup.send("Could not read the submitted `.bin` file, please try again!")
            return
        if not (details := xcom_helpers.validate_pool(contents)):
            await interaction.followup.send(
                "Submitted `.bin` file failed validation! Make sure it only has a single character and is a named pool.\n"
                "If the character you wish to submit is not a base soldier (i.e., is a Spark or Faction Soldier), "
                "please reach out to Charlie or the Mod Team directly to discuss your request.\n"
                "**If you believe this is an error, please open a mod support ticket via <#398949472840712192> so we can investigate further!**"
            )
        else:
            await interaction.followup.send(
                f"The provided `.bin` file is valid for submission! Here are the details of the character:\n{details}"
            )

    @commands.command(name="rollup", hidden=True)
    @commands.is_owner()
    async def rollup(self, ctx: commands.Context[CBot], after: discord.Message | None = None):
        """Rollup all character requests into a single message for easier viewing by the mod team and for final import.

        Parameters
        ----------
        ctx: commands.Context
            The context instance for the command.
        after: discord.Message | None
            If provided, only messages after this message will be included in the rollup.
        """
        submissions: dict[int, tuple[int, str]] = {
            message: (submitter, preferred_class)
            for submitter, message, preferred_class in await self.bot.pool.fetch(
                "SELECT submitter, message_id, preferred_class FROM xcom_character_submission;"
            )
        }
        vip1_bins = []
        vip2_bins = []
        general_bins = []
        preference_details = []
        valid_submitters: list[int] = []
        channel = self.bot.get_channel(_SUBMISSION_CHANNEL_ID) or await self.bot.fetch_channel(_SUBMISSION_CHANNEL_ID)
        assert isinstance(channel, discord.TextChannel)
        messages = [
            msg
            async for msg in channel.history(limit=None, after=after)
            if msg.attachments
            and msg.attachments[0].filename.endswith(".bin")
            and msg.application_id == self.bot.user.id
        ]
        issues = []
        for message in messages:
            int_meta = message.interaction_metadata
            assert int_meta is not None
            submitter_id = int_meta.user.id
            mentioned_id = message.mentions[0].id if message.mentions else None
            if mentioned_id != submitter_id:
                _LOGGER.debug(
                    "Message with id %s has interaction user id %s but mentions user id %s, skipping.",
                    message.id,
                    submitter_id,
                    mentioned_id,
                )
                issues.append(
                    f"Message {message.jump_url} has interaction user id {submitter_id} but mentions user id {mentioned_id}, skipping."
                )
                continue

            bin_contents = await message.attachments[0].read()
            submitter = message.mentions[0]
            submission_details = submissions[message.id]
            character_name = xcom_helpers.get_bin_name(bin_contents)
            preference_details.append(f"{character_name}: {submission_details[1]}")
            valid_submitters.append(submitter_id)
            if after:
                general_bins.append(bin_contents)
                continue
            if not isinstance(submitter, discord.Member):
                general_bins.append(bin_contents)
                continue
            if any(submitter.get_role(role_id) for role_id in SUBMISSION_TIER_1):
                vip1_bins.append(bin_contents)
            elif any(submitter.get_role(role_id) for role_id in SUBMISSION_TIER_2):
                vip2_bins.append(bin_contents)
            else:
                general_bins.append(bin_contents)

        rolled_up_vip1 = rolled_up_vip2 = rolled_up_general = None
        if vip1_bins:
            rolled_up_vip1 = xcom_helpers.merge_bin_files("VIP_TIER_1.bin", vip1_bins)
        if vip2_bins:
            rolled_up_vip2 = xcom_helpers.merge_bin_files("VIP_TIER_2.bin", vip2_bins)
        if general_bins:
            rolled_up_general = xcom_helpers.merge_bin_files("GENERAL.bin", general_bins)

        enhanced_metadata = await self.bot.pool.fetch(
            "SELECT requestor, first_name, last_name, nickname, country, "
            "gender, race, details, biography, fulfiller, fulfill_thread "
            "FROM xcom_character_request WHERE requestor = ANY($1);",
            valid_submitters,
        )

        if sys.version_info >= (3, 14):
            try:
                import compression.zstd

                compression = zipfile.ZIP_ZSTANDARD
            except ImportError:
                compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_DEFLATED
        with io.BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "w", compression=compression) as zip_file:
                if rolled_up_vip1:
                    zip_file.writestr("VIP_TIER_1.bin", rolled_up_vip1)
                if rolled_up_vip2:
                    zip_file.writestr("VIP_TIER_2.bin", rolled_up_vip2)
                if rolled_up_general:
                    zip_file.writestr("GENERAL.bin", rolled_up_general)
                zip_file.writestr("character_preferences.txt", "\n".join(preference_details))
                with io.StringIO() as csv_buffer:
                    fieldnames = [
                        "requestor",
                        "first_name",
                        "last_name",
                        "nickname",
                        "country",
                        "gender",
                        "race",
                        "details",
                        "biography",
                        "fulfiller",
                        "fulfill_thread",
                    ]
                    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in enhanced_metadata:
                        writer.writerow({field: row[field] for field in fieldnames})
                    zip_file.writestr("enhanced_metadata.csv", csv_buffer.getvalue())
            zip_buffer.seek(0)
            file = discord.File(zip_buffer, "submissions.zip")
            await ctx.reply(
                f"Total of {len(valid_submitters)} valid submissions rolled up. {len(issues)} issues encountered.",
                file=file,
            )
            if issues:
                issues_message = "\n".join(issues)
                if len(issues_message) > 1900:
                    issues_message = issues_message[:1900] + "\n... (truncated)"
                await ctx.send(f"Issues encountered during rollup:\n{issues_message}")


async def setup(bot: CBot) -> None:
    """Add the XCOM cog to the bot."""
    import importlib

    global xcom_helpers
    sys.modules["charbot.xcom_helpers"] = xcom_helpers = importlib.reload(xcom_helpers)
    await bot.add_cog(XCOM(bot))
