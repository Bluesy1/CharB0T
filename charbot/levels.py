"""Level system."""

import collections
import datetime
import time

import discord
from discord import Interaction, app_commands
from discord.ext import commands, tasks

from . import CBot


XP_PER_LEVEL = 20
XP_CAP = (XP_PER_LEVEL * 5) + 2
INTERVAL_LENGTH = 600
LEVEL_1 = discord.Object(969626979353632790, type=discord.Role)
LEVEL_2 = discord.Object(969627321239760967, type=discord.Role)
LEVEL_3 = discord.Object(969628342733119518, type=discord.Role)
LEVEL_4 = discord.Object(969629632028614699, type=discord.Role)
LEVEL_5 = discord.Object(969629628249563166, type=discord.Role)


class Leveling(commands.Cog):
    """Level system."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self.buckets: dict[int, collections.deque[discord.Message]] = {}
        self.bucket_cooldown: dict[int, float] = {}
        self.bucket_previous: dict[int, set[int]] = {}
        self.drain.start()

    async def cog_unload(self):
        self.drain.cancel()

    async def proc_xp(self, message: discord.Message):
        """Add XP to the user when they send a message.

        Parameters
        ----------
        message : discord.Message
            The message that was sent.
        """
        if message.author.bot or message.guild is None:
            return

        guild = message.guild
        channel_id = message.channel.id

        async with self.bot.pool.acquire() as conn, conn.transaction():
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", guild.id)
            if no_xp is None or message.channel.id in no_xp["channels"]:
                return

            await conn.execute(
                "UPDATE levels SET last_message = $1 WHERE id = $2", message.created_at, message.author.id
            )

            if channel_id not in self.buckets:
                self.buckets[channel_id] = collections.deque([message])
                return
            bucket = self.buckets[channel_id]
            bucket.appendleft(message)

            if (
                channel_id in self.bucket_cooldown
                and time.monotonic() - self.bucket_cooldown[channel_id] < INTERVAL_LENGTH
            ):  # bucket too soon after previous, exit
                return

            oldest_allowed = message.created_at - datetime.timedelta(minutes=10)
            first = bucket[0]
            if first.created_at > oldest_allowed:  # bucket too small, less than 10 mins
                return

            while bucket:
                first_dt = bucket[0].created_at
                if first_dt < oldest_allowed:
                    bucket.popleft()
                else:
                    break

            unique_accounts = {message.author.id for message in bucket}

            if len(unique_accounts) < 3:
                return

            bucket.clear()
            new_cooldown = time.monotonic()
            prev_cooldown = self.bucket_cooldown.get(channel_id, 0)
            self.bucket_cooldown[channel_id] = new_cooldown
            if new_cooldown - prev_cooldown > (
                INTERVAL_LENGTH * 1.5
            ):  # no bonus awarded if over half a bucket of downtime elapsed
                self.bucket_previous[channel_id] = bonus_users = set()
            bonus_users = self.bucket_previous.get(channel_id, set())
            messages: list[str] = []
            for user in unique_accounts:
                try:
                    member = guild.get_member(user) or await guild.fetch_member(user)
                except discord.HTTPException:
                    pass
                else:
                    if any(role.id in no_xp["roles"] for role in member.roles):
                        continue
                    old_xp: int = await conn.fetchval("SELECT xp FROM levels WHERE id = $1", member.id) or 0
                    xp_to_add = 3 if user in bonus_users else 1
                    new_xp: int = await conn.fetchval(
                        "INSERT INTO levels (id, xp, last_message) VALUES ($1, $2, $3) "
                        "ON CONFLICT (id) DO UPDATE SET "
                        "xp = EXCLUDED.xp, last_message = EXCLUDED.last_message "
                        "RETURNING xp",
                        member.id,
                        min(XP_CAP, old_xp + xp_to_add),
                        message.created_at,
                    )
                    if (old_xp // XP_PER_LEVEL) < (level := new_xp // XP_PER_LEVEL):
                        match level:
                            case 1:
                                await member.add_roles(LEVEL_1, reason="Level 1 reached")
                            case 2:
                                await member.add_roles(LEVEL_2, reason="Level 2 reached")
                                await member.remove_roles(LEVEL_1, reason="Level 2 reached")
                            case 3:
                                await member.add_roles(LEVEL_3, reason="Level 3 reached")
                                await member.remove_roles(LEVEL_2, reason="Level 3 reached")
                            case 4:
                                await member.add_roles(LEVEL_4, reason="Level 4 reached")
                                await member.remove_roles(LEVEL_3, reason="Level 4 reached")
                            case 5:
                                await member.add_roles(LEVEL_5, reason="Level 5 reached")
                                await member.remove_roles(LEVEL_4, reason="Level 5 reached")
                        messages.append(f"{member.mention} has reached level **{level}** congratulations!")
            if messages:
                await message.channel.send("\n".join(messages))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Check if they are rejoining and should get a rank role back.

        Parameters
        ----------
        member : discord.Member
            The member that joined.
        """
        async with self.bot.pool.acquire() as conn:
            xp: int | None = await conn.fetchval("SELECT xp FROM levels WHERE id = $1", member.id)
            if xp is None:
                return
            match xp // XP_PER_LEVEL:
                case 1:
                    await member.add_roles(LEVEL_1, reason="Rejoined at level 1")
                case 2:
                    await member.add_roles(LEVEL_2, reason="Rejoined at level 2")
                case 3:
                    await member.add_roles(LEVEL_3, reason="Rejoined at level 3")
                case 4:
                    await member.add_roles(LEVEL_4, reason="Rejoined at level 4")
                case 5:
                    await member.add_roles(LEVEL_5, reason="Rejoined at level 5")

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 900, key=lambda interaction: interaction.user.id)
    async def rank(self, interaction: Interaction[CBot]):
        """Check your someone's level.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send("This Must be used in a guild")
            return

        async with self.bot.pool.acquire() as conn:
            xp: int | None = await conn.fetchval("SELECT xp FROM levels WHERE id = $1", interaction.user.id)
            if xp is None:
                await interaction.followup.send("You haven't interacted on the server yet.")
            else:
                await interaction.followup.send(f"You are level **{xp // XP_PER_LEVEL}**.")

    @tasks.loop(time=datetime.time(hour=0, tzinfo=datetime.UTC))
    async def drain(self):
        async with self.bot.pool.acquire() as conn, conn.transaction():
            users = await conn.fetch(
                "UPDATE levels SET xp = xp - 2 "
                "WHERE xp > $1 AND last_message < (CURRENT_TIMESTAMP - '3 days'::interval) "
                "RETURNING id, xp",
                XP_PER_LEVEL * 2,
            )
            guild = self.bot.get_guild(225345178955808768) or await self.bot.fetch_guild(225345178955808768)
            for user in users:
                xp: int = user["xp"]
                if (xp % XP_PER_LEVEL) < 2:
                    new_level: int = xp // XP_PER_LEVEL
                    member = guild.get_member(user["id"]) or await guild.fetch_member(user["id"])
                    if new_level == 2:
                        await member.add_roles(LEVEL_2, reason="Dropped to Level 2")
                        await member.remove_roles(LEVEL_3, reason="Dropped to Level 2")
                    elif new_level == 3:
                        await member.add_roles(LEVEL_3, reason="Dropped to Level 3")
                        await member.remove_roles(LEVEL_4, reason="Dropped to Level 3")
                    elif new_level == 4:
                        await member.add_roles(LEVEL_4, reason="Dropped to Level 4")
                        await member.remove_roles(LEVEL_5, reason="Dropped to Level 4")


async def setup(bot: CBot):
    """Load cog."""
    await bot.add_cog(Leveling(bot))
