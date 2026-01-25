"""Level system."""

import asyncio
import datetime
import time
from collections import defaultdict, deque

import discord
from discord import Interaction, app_commands
from discord.ext import commands, tasks

from . import CBot, constants


XP_PER_LEVEL = 10
XP_CAP = (XP_PER_LEVEL * 5) + 1
INTERVAL_LENGTH = 600
LEVEL_1_ROLE = discord.Object(constants.LEVEL_1_ID, type=discord.Role)
LEVEL_2_ROLE = discord.Object(constants.LEVEL_2_ID, type=discord.Role)
LEVEL_3_ROLE = discord.Object(constants.LEVEL_3_ID, type=discord.Role)
LEVEL_4_ROLE = discord.Object(constants.LEVEL_4_ID, type=discord.Role)
LEVEL_5_ROLE = discord.Object(constants.LEVEL_5_ID, type=discord.Role)
LEVEL_6_ROLE = discord.Object(constants.LEVEL_6_ID, type=discord.Role)


class Leveling(commands.Cog):
    """Level system."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self.buckets: dict[int, deque[tuple[datetime.datetime, int]]] = self.bot.holder.pop("leveling_buckets", {})
        self.cooldown: commands.CooldownMapping[discord.Message] = self.bot.holder.pop(
            "leveling_bucket_cooldown",
            commands.CooldownMapping.from_cooldown(1, 600, lambda message: (message.channel.id, message.author.id)),
        )
        self.bucket_previous: defaultdict[int, defaultdict[int, float]] = self.bot.holder.pop(
            "leveling_bucket_previous", defaultdict(lambda: defaultdict(lambda: 0))
        )
        self.lock = asyncio.Lock()
        self.drain.start()

    async def cog_unload(self):
        self.drain.cancel()
        self.bot.holder["leveling_buckets"] = self.buckets
        self.bot.holder["leveling_bucket_cooldown"] = self.cooldown
        self.bot.holder["leveling_bucket_previous"] = self.bucket_previous

    async def proc_xp(self, message: discord.Message):
        """Add XP to the user when they send a message.

        Parameters
        ----------
        message : discord.Message
            The message that was sent.
        """
        if message.author.bot or message.guild is None:
            return
        
        if message.is_system():
            return

        guild = message.guild
        channel_id = message.channel.id
        created_at = message.created_at
        # member = message.author
        author_id = message.author.id

        async with self.lock, self.bot.pool.acquire() as conn, conn.transaction():
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", guild.id)
            if no_xp is None or message.channel.id in no_xp["channels"]:
                return

            await conn.execute(
                "INSERT INTO levels (id, xp, last_message) VALUES ($1, 0, $2) "
                "ON CONFLICT (id) DO UPDATE SET last_message = EXCLUDED.last_message",
                author_id,
                created_at,
            )
            message_tuple = (created_at, author_id)

            if channel_id not in self.buckets:
                self.buckets[channel_id] = deque([message_tuple])
                return
            bucket = self.buckets[channel_id]
            bucket.append(message_tuple)

            oldest_allowed = created_at - datetime.timedelta(seconds=INTERVAL_LENGTH)

            while bucket:
                first_dt, *_ = bucket[0]
                if first_dt < oldest_allowed:
                    bucket.popleft()
                else:
                    break

            oldest_allowed = created_at - datetime.timedelta(seconds=INTERVAL_LENGTH // 2)

            unique_accounts = {author for _, author in bucket}

            if (num_unique := len(unique_accounts)) < 2:
                return

            messages: list[str] = []
            no_xp_roles: frozenset[int] = frozenset(no_xp["roles"])
            for user in unique_accounts:
                if max(ts for ts, usr in bucket if usr == user) < oldest_allowed:
                    continue
                try:
                    this_member = guild.get_member(user) or await guild.fetch_member(user)
                except discord.HTTPException:
                    continue

                if any(role.id in no_xp_roles for role in this_member.roles):
                    continue

                old_xp: int = await conn.fetchval("SELECT xp FROM levels WHERE id = $1", user) or 0
                if (old_level := old_xp // XP_PER_LEVEL) >= 2 and num_unique == 2:
                    continue

                at_ts = created_at.timestamp()
                if user == author_id:
                    cooldown = self.cooldown.get_bucket(message)
                    off_cooldown = cooldown is None or cooldown.update_rate_limit(at_ts) is None
                else:
                    self.cooldown._verify_cache_integrity()
                    key = (channel_id, user)
                    if key not in self.cooldown._cache:
                        cooldown = self.cooldown.create_bucket(message)
                        self.cooldown._cache[key] = cooldown
                        off_cooldown = cooldown.update_rate_limit(at_ts) is None or True
                    else:
                        cooldown = self.cooldown._cache[key]
                        off_cooldown = cooldown.update_rate_limit(at_ts) is None

                if off_cooldown:
                    last_author_time = self.bucket_previous[channel_id][user]
                    self.bucket_previous[channel_id][user] = this_author_time = time.monotonic()
                    diff = this_author_time - last_author_time
                    xp_to_add = 3 if diff <= INTERVAL_LENGTH * 1.5 else 1
                    new_xp: int = await conn.fetchval(
                        "INSERT INTO levels (id, xp, last_message) VALUES ($1, $2, $3) "
                        "ON CONFLICT (id) DO UPDATE SET "
                        "xp = EXCLUDED.xp, last_message = EXCLUDED.last_message "
                        "RETURNING xp",
                        user,
                        min(XP_CAP, old_xp + xp_to_add),
                        created_at,
                    )
                    if old_level < (level := new_xp // XP_PER_LEVEL):
                        match level:
                            case 1:
                                await this_member.add_roles(LEVEL_1_ROLE, reason="Level 1 reached")
                            case 2:
                                await this_member.add_roles(LEVEL_2_ROLE, reason="Level 2 reached")
                                await this_member.remove_roles(LEVEL_1_ROLE)
                            case 3:
                                await this_member.add_roles(LEVEL_3_ROLE, reason="Level 3 reached")
                                await this_member.remove_roles(LEVEL_2_ROLE)
                            case 4:
                                await this_member.add_roles(LEVEL_4_ROLE, reason="Level 4 reached")
                                await this_member.remove_roles(LEVEL_3_ROLE)
                            case 5:
                                await this_member.add_roles(LEVEL_5_ROLE, reason="Level 5 reached")
                                await this_member.remove_roles(LEVEL_4_ROLE)
                        messages.append(f"Congratulations {this_member.mention}, you have reached level **{level}**!")
                    # await self.bot.error_logs.send(
                    #     f"{this_member.mention} got `{old_xp} + {xp_to_add} => {new_xp}`  (level {old_level} => {level}) in channel <#{channel_id}>\n"
                    #     f" - `{cooldown=!r}`\n"
                    #     f" - `this_author_time - last_author_time = {this_author_time} - {last_author_time} = {diff}`\n"
                    #     f" - `{off_cooldown=}`\n"
                    #     f" - `{unique_accounts=}`\n - `{at_ts=}`"
                    # )
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
                    await member.add_roles(LEVEL_1_ROLE, reason="Rejoined at level 1")
                case 2:
                    await member.add_roles(LEVEL_2_ROLE, reason="Rejoined at level 2")
                case 3:
                    await member.add_roles(LEVEL_3_ROLE, reason="Rejoined at level 3")
                case 4:
                    await member.add_roles(LEVEL_4_ROLE, reason="Rejoined at level 4")
                case 5:
                    await member.add_roles(LEVEL_5_ROLE, reason="Rejoined at level 5")

    @app_commands.command()
    @app_commands.guilds(constants.GUILD_ID)
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
                "UPDATE levels SET xp = xp - 1 "
                "WHERE xp > $1 AND last_message < (CURRENT_TIMESTAMP - '3 days'::interval) "
                "RETURNING id, xp",
                XP_PER_LEVEL * 2,
            )
            guild = self.bot.get_guild(constants.GUILD_ID) or await self.bot.fetch_guild(constants.GUILD_ID)
            for user in users:
                xp: int = user["xp"]
                if (xp % XP_PER_LEVEL) >= XP_PER_LEVEL-1:
                    new_level: int = xp // XP_PER_LEVEL
                    member = guild.get_member(user["id"]) or await guild.fetch_member(user["id"])
                    if new_level == 2:
                        await member.add_roles(LEVEL_2_ROLE, reason="Dropped to Level 2")
                        await member.remove_roles(LEVEL_3_ROLE, LEVEL_4_ROLE, LEVEL_5_ROLE)
                    elif new_level == 3:
                        await member.add_roles(LEVEL_3_ROLE, reason="Dropped to Level 3")
                        await member.remove_roles(LEVEL_4_ROLE, LEVEL_5_ROLE)
                    elif new_level == 4:
                        await member.add_roles(LEVEL_4_ROLE, reason="Dropped to Level 4")
                        await member.remove_roles(LEVEL_5_ROLE)


async def setup(bot: CBot):
    """Load cog."""
    await bot.add_cog(Leveling(bot))
