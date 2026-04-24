"""XCOM Stuff"""

import logging
from typing import Literal

import discord
from discord import app_commands, ui
from discord.app_commands import Choice, Range
from discord.ext.commands import Cog

from . import CBot, constants


_LOGGER = logging.getLogger(__name__)
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

#     details = ui.TextDisplay("""\
# Please fill out the following form to request a character.
# The more information you provide, the better!
# Once you submit the form, it will be reviewed by one of our volunteers on a first-come, first-served basis.
# """)
# first_name = ui.Label(
#     text="First Name",
#     description="Enter the first name of the character you want to request.",
#     component=ui.TextInput(placeholder="Enter the first name of the character you want to request.", max_length=25),
# )
# last_name = ui.Label(
#     text="Last Name",
#     description="Enter the last name of the character you want to request.",
#     component=ui.TextInput(placeholder="Enter the last name of the character you want to request.", max_length=25),
# )
# nickname = ui.Label(
#     text="Nickname",
#     description="Enter a nickname for the character (optional).",
#     component=ui.TextInput(
#         placeholder="Enter a nickname for the character (optional).", max_length=25, required=False
#     ),
# )


class CharacterRequestModal(ui.Modal, title="Character Request"):
    """Modal for requesting a character."""

    name = ui.Label(
        text="Name",
        description="Enter the full name of the character you want to request, in the form \"First 'Nick' Last\".",
        component=ui.TextInput(placeholder="Enter the full name of the character you want to request.", max_length=100),
    )
    country = ui.Label(
        text="Country",
        description="Enter the country of origin for the character.",
        component=ui.TextInput(placeholder="Enter the country of origin for the character.", max_length=50),
    )
    sex = ui.Label(
        text="Select your character's sex",
        component=ui.RadioGroup(
            options=[
                discord.RadioGroupOption(label="Male", value="male"),
                discord.RadioGroupOption(label="Female", value="female"),
            ]
        ),
    )
    description = ui.Label(
        text="Description",
        description="Enter a brief description of the character.",
        component=ui.TextInput(
            placeholder="Enter a brief description of the character.", style=discord.TextStyle.paragraph, max_length=500
        ),
    )
    bio = ui.Label(
        text="Biography",
        description="Optional: Enter a detailed biography of the character.",
        component=ui.TextInput(
            placeholder="Enter a detailed biography of the character.",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=False,
        ),
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle the form submission."""
        await interaction.response.send_message(
            "Thank you for your character request! Your request has been submitted and will be reviewed by our volunteers. You will be notified once a decision has been made.",
            ephemeral=True,
        )


class DemoButton(ui.View):
    """A simple view with a button to demonstrate the character request modal."""

    def __init__(
        self,
    ):
        super().__init__(timeout=None)

    @ui.button(label="Request a Character", style=discord.ButtonStyle.primary)
    async def request_character(self, interaction: discord.Interaction, button: ui.Button) -> None:
        """Show the character request modal when the button is clicked."""
        await interaction.response.send_modal(CharacterRequestModal())


class EditRequestButton(ui.Button):
    """A button to for the edit request layout."""

    def __init__(
        self, first_name: str, last_name: str, nickname: str, gender: str, country: str, race: str, attitude: str
    ):
        super().__init__(label="Edit Request", style=discord.ButtonStyle.primary)
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.country = country
        self.race = race
        self.attitude = attitude

    async def callback(self, interaction: discord.Interaction[CBot]) -> None:
        """Handle the button click."""
        await interaction.response.send_message(
            "You clicked the edit request button! This would show the edit request modal, but that hasn't been implemented yet.",
            ephemeral=True,
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
                accessory=EditRequestButton(first_name, last_name, nickname, gender, country, race, attitude),
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

    async def country_autocomplete(self, interaction: discord.Interaction, current: str) -> list[Choice[str]]:
        """Autocomplete for the country field."""
        return [
            Choice(name=value, value=key) for key, value in XCOM_COUNTRIES.items() if current.lower() in value.lower()
        ][:25]

    @character.command(name="request", description="Request a character to be added to the XCOM roster.")
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
                return
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
                return


async def setup(bot: CBot) -> None:
    """Add the XCOM cog to the bot."""
    await bot.add_cog(XCOM(bot))
