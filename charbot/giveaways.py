"""Giveaway Handling"""

import logging
import random
import secrets
from collections import Counter
from datetime import datetime, time

import discord
from discord import app_commands, ui
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.utils import format_dt, utcnow

from . import CBot, constants


_LOGGER = logging.getLogger(__name__)
LOG_CHANNEL = 687817008355737606


class GiveawaySetupModal(ui.Modal, title="Giveaway Setup"):
    """Modal for setting up giveaways.

    Parameters
    ----------
    game : str
        The title of the giveaway.
    winners : int
        The number of winners for the giveaway.
    deliverer : discord.Member
        The member who is delivering the giveaway.
    end_time : datetime
        The end time of the giveaway.
    min_level : int
        The minimum level required to enter the giveaway for non supporters.
    """

    def __init__(self, game: str, winners: int, deliverer: discord.Member, end_time: datetime, min_level: int):
        super().__init__()
        self.game = game
        self.winners = winners
        self.deliverer = deliverer
        self.end_time = end_time
        self.min_level = min_level

        detail_text = f"# Base Details:\nGame: {self.game}\nWinners: {self.winners}\nDeliverer: {self.deliverer.display_name}\nEnd Time: {format_dt(self.end_time, style='F')}"
        if self.min_level > 0:
            detail_text += f"\nMinimum Level (non-supporters): {self.min_level}"
        detail_text += "\n\nPlease fill out the description and select the giveaway entry method (important details provided already will be added to the sent description)."

        self.details = ui.TextDisplay(detail_text)
        self.add_item(self.details)

        self.description = ui.Label(
            text="Description",
            description="Giveaway Description",
            component=ui.TextInput(max_length=3000, style=discord.TextStyle.paragraph),
        )
        self.add_item(self.description)

        self.specifics = ui.Label(
            text="Design Specifics",
            component=ui.Select(
                placeholder="Select giveaway entry method",
                options=[
                    discord.SelectOption(label="Select random number (1-100)", value="number"),
                    discord.SelectOption(label="Select winners by shuffling entries", value="shuffle"),
                ],
            ),
        )
        self.add_item(self.specifics)

        self.category = ui.Label(
            text="Category",
            component=ui.Select(
                placeholder="Select giveaway category",
                options=[
                    discord.SelectOption(label="General", value="general"),
                    discord.SelectOption(label="VIP", value="vip"),
                ],
            ),
        )
        self.add_item(self.category)

    async def on_submit(self, interaction: discord.Interaction[CBot]):
        await interaction.response.defer(ephemeral=True)
        interaction.response.is_done()

        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.specifics.component, ui.Select)
        assert isinstance(self.category.component, ui.Select)

        description = self.description.component.value
        entry_method = self.specifics.component.values[0]
        random_number = entry_method == "number"
        category_value = self.category.component.values[0]

        guild = interaction.guild
        assert isinstance(guild, discord.Guild)
        if category_value == "general":
            category = guild.get_channel(constants.GENERAL_CATEGORY)
        else:
            category = guild.get_channel(constants.VIP_CATEGORY)
        assert isinstance(category, discord.CategoryChannel)
        channel = await category.create_text_channel(
            "giveaway",
            position=100,
            topic=f"Giveaway for {self.game}",
            slowmode_delay=21600,
        )

        async with interaction.client.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO giveaway (channel, game, winners, distributor, end_dt, min_level, random_num)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                channel.id,
                self.game,
                self.winners,
                self.deliverer.id,
                self.end_time,
                self.min_level,
                random_number,
            )
            await conn.execute(
                "UPDATE no_xp SET channels = array_append(channels, $1) WHERE guild = $2",
                channel.id,
                interaction.guild_id,
            )

            enter_by = "Enter by sending a *single* message in this channel."
            if random_number:
                enter_by = "Enter by sending a *single* message with a number between 1 and 100 in this channel."

            enter_by += " **Messages that are edited after being sent will not count as valid entries.**"

            if self.min_level > 0:
                enter_by += f"\n\nAt the time of the draw, **you must either be at least level {self.min_level} or be a channel supporter**. See <#338734957251788803> for more details on our leveling system."

        msg = await channel.send(f"""**NEW GIVEAWAY** for **{self.game}** available to everyone! <@&605419188873330739> 

{description}

{self.winners} winners will be chosen on {format_dt(self.end_time)}.

{enter_by}

**GOOD LUCK TO ALL!!!**
------------------------------""")
        await interaction.followup.send(f"The giveaway for {self.game} has begun in <#{channel.id}>.", ephemeral=True)
        await msg.pin()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if interaction.response.is_done():
            await interaction.followup.send("Oops! Something went wrong.", ephemeral=True)
        else:
            await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)
        _LOGGER.exception("Error in GiveawaySetupModal: %s", error)


class MessageEditModal(ui.Modal, title="Edit Giveaway Message"):
    """Modal for editing giveaway messages.

    Parameters
    ----------
    original_message : str
        The original giveaway message content.
    """

    def __init__(self, original_message: discord.Message):
        super().__init__()
        self.original_message = original_message

        self.new_content = ui.Label(
            text="New Giveaway Message",
            description="Edit the giveaway message content (max 3000 characters).",
            component=ui.TextInput(
                max_length=3000, style=discord.TextStyle.paragraph, default=original_message.content
            ),
        )
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction[CBot]):
        await interaction.response.defer(ephemeral=True)
        interaction.response.is_done()

        assert isinstance(self.new_content.component, ui.TextInput)
        new_content = self.new_content.component.value

        try:
            await self.original_message.edit(content=new_content)
            await interaction.followup.send("Giveaway message updated successfully!", ephemeral=True)
        except Exception as e:
            _LOGGER.exception("Error editing giveaway message: %s", e)
            await interaction.followup.send("Failed to update giveaway message.", ephemeral=True)


class Giveaways(Cog):
    """Giveaway Cog.

    This cog handles all giveaways functionality.

    Parameters
    ----------
    bot : CBot
        The bot instance.

    Attributes
    ----------
    bot : CBot
        The bot instance.
    """

    def __init__(self, bot: CBot):
        self.bot = bot

    async def cog_load(self):
        self.do_finish_giveaways.start()
        self.edit_giveaway_message_cmd = app_commands.ContextMenu(
            name="Edit Giveaway Message", callback=self.edit_giveaway_message
        )
        self.bot.tree.add_command(self.edit_giveaway_message_cmd)

    async def cog_unload(self) -> None:
        self.do_finish_giveaways.cancel()
        self.bot.tree.remove_command(self.edit_giveaway_message_cmd.name, type=self.edit_giveaway_message_cmd.type)

    @app_commands.command(name="create_giveaway", description="Create a new giveaway")
    @app_commands.guilds(constants.GUILD_ID)
    @app_commands.default_permissions(manage_channels=True)
    async def create_giveaway(
        self,
        interaction: discord.Interaction[CBot],
        game: app_commands.Range[str, 5, 255],
        winners: app_commands.Range[int, 1],
        deliverer: discord.Member,
        end_time: app_commands.Timestamp,
        min_level: app_commands.Range[int, 0, 5],
    ):
        """Create a new giveaway.

        Parameters
        ----------
        interaction : discord.Interaction[CBot]
            The interaction that triggered the command.
        game : str
            The title of the giveaway (5-255 characters).
        winners : int
            The number of winners for the giveaway (minimum 1).
        deliverer : discord.Member
            The member who is delivering the giveaway.
        end_time : datetime
            The end time of the giveaway (must be in the future).
        min_level : int
            The minimum level required to enter the giveaway for non supporters (0-5).
        """
        if end_time <= utcnow():
            await interaction.response.send_message("End time must be in the future.", ephemeral=True)
            return
        is_deliverer_mod = any(deliverer.get_role(role_id) for role_id in constants.MOD_ROLE_IDS)
        if deliverer.bot or not is_deliverer_mod:
            await interaction.response.send_message(
                "Deliverer must be a non-bot member with a moderator role.", ephemeral=True
            )
            return
        await interaction.response.send_modal(GiveawaySetupModal(game, winners, deliverer, end_time, min_level))

    @app_commands.guilds(constants.GUILD_ID)
    @app_commands.default_permissions(manage_channels=True)
    async def edit_giveaway_message(self, interaction: discord.Interaction[CBot], message: discord.Message):
        """Context menu command to edit giveaway messages."""
        if message.author.id != self.bot.user.id:
            await interaction.response.send_message(
                "This command can only be used on bot-sent giveaway messages.", ephemeral=True
            )
            return
        async with self.bot.pool.acquire() as conn:
            giveaway = conn.fetchrow("SELECT * FROM giveaway WHERE channel = $1", message.channel.id)
            if not giveaway:
                await interaction.response.send_message(
                    "This command can only be used on giveaway messages.", ephemeral=True
                )
                return

        await interaction.response.send_modal(MessageEditModal(message))

    @tasks.loop(time=[time(hour) for hour in range(24)])
    async def do_finish_giveaways(self):
        """Task loop to finish giveaways."""
        log_channel = self.bot.get_channel(LOG_CHANNEL) or await self.bot.fetch_channel(LOG_CHANNEL)
        assert isinstance(log_channel, discord.TextChannel)
        async with self.bot.pool.acquire() as conn:
            giveaways = await conn.fetch("SELECT * FROM giveaway WHERE end_dt <= $1 AND complete = FALSE", utcnow())
            for giveaway in giveaways:
                channel_id = giveaway["channel"]
                num_winners = giveaway["winners"]
                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                if not isinstance(channel, discord.TextChannel):
                    _LOGGER.warning("Channel with ID %s not found for giveaway ID %s", channel_id, channel_id)
                    continue
                guild = channel.guild
                deliverer_id = giveaway["distributor"]

                ## Update Channel Overwrites to only allow the deliverer to send messages, preventing any further entries in the giveaway while winners are being selected

                deliverer = guild.get_member(deliverer_id) or await guild.fetch_member(deliverer_id)
                everyone = guild.default_role
                overwrites = channel.overwrites
                everyone_overwrite = overwrites.get(everyone, discord.PermissionOverwrite())
                everyone_overwrite.send_messages = False
                overwrites[everyone] = everyone_overwrite
                deliverer_overwrite = overwrites.get(deliverer, discord.PermissionOverwrite())
                deliverer_overwrite.send_messages = True
                overwrites[deliverer] = deliverer_overwrite
                await channel.edit(overwrites=overwrites)

                entries = [
                    message
                    async for message in channel.history(limit=None)
                    if not message.edited_at and isinstance(message.author, discord.Member)
                ]
                # Eliminate bots and messages from the giveaway deliverer
                entries = [entry for entry in entries if not entry.author.bot and entry.author.id != deliverer_id]
                author_counts = Counter(entry.author.id for entry in entries)
                duplicate_authors = {author_id for author_id, count in author_counts.items() if count > 1}

                entries = [entry for entry in entries if entry.author.id not in duplicate_authors]

                await log_channel.send(f"Finishing giveaway for {giveaway['game']} with {len(entries)} valid entries.")

                if (min_level := giveaway["min_level"]) > 0:
                    # Filter entries based on minimum level requirement for non-supporters
                    required_roles = (
                        frozenset(constants.LEVEL_ROLE_IDS_LIST[min_level - 1 :])
                        | constants.SUPPORTER_ROLE_IDS
                        | constants.MOD_ROLE_IDS
                        | constants.LEGACY_ROLE_IDS
                    )
                    entries = [
                        entry
                        for entry in entries
                        if any(entry.author.get_role(role_id) for role_id in required_roles)  # pyright: ignore[reportAttributeAccessIssue]
                    ]

                REMINDER_TEXT = f"Remember to DM {deliverer.mention} **within 48 hours** to claim your prize!"

                if giveaway["random_num"]:
                    # Select winners by random number method
                    winning_number = secrets.randbelow(100) + 1

                    def get_entry(msg: discord.Message):
                        try:
                            return int(msg.content.strip())
                        except ValueError:
                            return -1

                    entry_numbers = [(entry, val) for entry in entries if 1 <= (val := get_entry(entry)) <= 100]

                    if not entry_numbers:
                        await channel.send("No valid entries were submitted. No winners can be selected.")
                        await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)
                        continue

                    if len(entry_numbers) < num_winners:
                        await channel.send(f"""There were less valid entries than winners for this giveaway. The winning number was **{winning_number}**. The following {len(entry_numbers)} participant(s) win by default:
{", ".join(entry[0].author.mention for entry in entry_numbers)}

{REMINDER_TEXT}""")
                        await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)
                        continue

                    sorted_entries = sorted(entry_numbers, key=lambda x: abs(x[1] - winning_number))
                    winners = sorted_entries[:num_winners]
                    await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)

                    winner_mentions = ", ".join(entry[0].author.mention for entry in winners)
                    await channel.send(
                        f"The winning number is **{winning_number}**! Congratulations to the winner(s):\n{winner_mentions}!\n\n{REMINDER_TEXT}"
                    )
                    backups = sorted_entries[num_winners : (num_winners * 3)]
                    if backups:
                        backup_mentions = ", ".join(entry[0].author.mention for entry in backups)
                        backup_message = f"In case any winners fail to claim their prize, the following {len(backups)} participant(s) are backups:\n{backup_mentions}"
                        await deliverer.send(
                            f"In case any winners fail to claim their prize, the following {len(backups)} participant(s) are backups:\n{backup_mentions}"
                        )
                        await log_channel.send(f"Backups for giveaway {giveaway['game']}: {backup_mentions}")
                else:
                    # Select winners by shuffle method
                    if not entries:
                        await channel.send("No entries were submitted. No winners can be selected.")
                        await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)
                        continue

                    if len(entries) < num_winners:
                        winner_mentions = ", ".join(entry.author.mention for entry in entries)
                        await channel.send(
                            f"There were less entries than winners for this giveaway. The following {len(entries)} participant(s) win by default:\n{winner_mentions}\n\n{REMINDER_TEXT}"
                        )
                        await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)
                        continue

                    random.shuffle(entries)
                    winners = entries[:num_winners]
                    winner_mentions = ", ".join(entry.author.mention for entry in winners)
                    await channel.send(f"Congratulations to the winner(s):\n{winner_mentions}!\n\n{REMINDER_TEXT}")
                    await conn.execute("UPDATE giveaway SET complete = TRUE WHERE channel = $1", channel_id)

                    backups = entries[num_winners : (num_winners * 3)]
                    if backups:
                        backup_mentions = ", ".join(entry.author.mention for entry in backups)
                        backup_message = f"In case any winners fail to claim their prize, the following {len(backups)} participant(s) are backups:\n{backup_mentions}"
                        await deliverer.send(backup_message)
                        await log_channel.send(f"Backups for giveaway {giveaway['game']}: {backup_mentions}")


async def setup(bot: CBot):  # pragma: no cover
    """Load the event handler for the bot.

    Parameters
    ----------
    bot : CBot
        The bot to load the event handler for.
    """
    await bot.add_cog(Giveaways(bot))
