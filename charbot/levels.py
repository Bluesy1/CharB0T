"""Level system."""

import asyncio
import datetime
import random
from collections.abc import Callable
from typing import Literal, Optional, cast

import aiohttp
import asyncpg
import discord
from discord import Interaction, app_commands
from discord.ext import commands, tasks
from discord.utils import utcnow
from disrank.generator import Generator

from . import CBot, Config, translate


_LanguageTag = Literal["en-US", "es-ES", "fr", "nl"]


async def update_level_roles(member: discord.Member, new_level: int) -> None:
    """Update the level roles of the user.

    Parameters
    ----------
    member : discord.Member
        The member to update the level roles of.
    new_level : int
        The new level of the user.
    """
    if new_level == 1:
        await member.add_roles(discord.Object(969626979353632790), reason="Level 1")
    elif new_level == 5:
        await member.remove_roles(discord.Object(969626979353632790), reason="Level 5")
        await member.add_roles(discord.Object(969627321239760967), reason="Level 5")
    elif new_level == 10:
        await member.remove_roles(discord.Object(969627321239760967), reason="Level 10")
        await member.add_roles(discord.Object(969628342733119518), reason="Level 10")
    elif new_level == 20:
        await member.remove_roles(discord.Object(969628342733119518), reason="Level 20")
        await member.add_roles(discord.Object(969629632028614699), reason="Level 20")
    elif new_level == 25:
        await member.remove_roles(discord.Object(969629632028614699), reason="Level 25")
        await member.add_roles(discord.Object(969629628249563166), reason="Level 25")
    elif new_level == 30:
        await member.remove_roles(discord.Object(969629628249563166), reason="Level 30")
        await member.add_roles(discord.Object(969629622453039104), reason="Level 30")


class Leveling(commands.Cog):
    """Level system."""

    def __init__(self, bot: CBot):
        self.bot = bot
        self._min_xp = 11
        self._max_xp = 18
        self._xp_function: Callable[[int], int] = lambda x: (5 * x**2) + (50 * x) + 100
        self.off_cooldown: dict[int, datetime.datetime] = {}
        self.generator = Generator()
        self.generator.default_bg = "charbot/media/pools/card.png"
        self.default_profile = "https://raw.githubusercontent.com/Bluesy1/CharB0T/main/charbot/media/pools/profile.png"
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(login="Bluesy1", password=Config["github"]["token"]),
            headers=Config["github"]["headers"],
        )
        self._post_url = "https://api.github.com/repos/bluesy1/charb0t/actions/workflows/leaderboard.yml/dispatches"
        self._upload: bool = False
        self.cooldown: commands.CooldownMapping[discord.Message] = commands.CooldownMapping.from_cooldown(
            1, 60, commands.BucketType.user
        )

    async def cog_load(self) -> None:
        """Load the cog."""
        self.off_cooldown = self.bot.holder.pop("off_xp_cooldown", {})
        self.update_pages.start()

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Unload the cog."""
        self.bot.holder["off_xp_cooldown"] = self.off_cooldown
        self.update_pages.cancel()
        await self.session.close()

    @tasks.loop(time=[datetime.time(i) for i in range(24)])  # skipcq: PYL-E1123
    async def update_pages(self) -> None:
        """Update the page."""
        if self._upload:
            async with self.session.post(self._post_url, json={"ref": "gh-pages"}) as _:
                pass
        self._upload = False

    async def proc_xp(self, message: discord.Message):
        """Add XP to the user when they send a message.

        Parameters
        ----------
        message : discord.Message
            The message that was sent.
        """
        if message.author.bot or message.guild is None:
            return
        async with self.bot.pool.acquire() as conn, conn.transaction():
            no_xp = await conn.fetchrow("SELECT * FROM no_xp WHERE guild = $1", message.guild.id)
            if no_xp is None or message.channel.id in no_xp["channels"]:
                return
            member = cast(discord.Member, message.author)
            if any(role.id in no_xp["roles"] for role in member.roles):
                return
            cooldown = self.cooldown.get_bucket(message)
            if cooldown is None or cooldown.update_rate_limit() is None:
                self._upload = True
                self.off_cooldown[message.author.id] = utcnow() + datetime.timedelta(minutes=1)
                user = await conn.fetchrow("SELECT * FROM xp_users WHERE id = $1", message.author.id)
                gained = random.randint(self._min_xp, self._max_xp)
                if user is None:
                    await conn.execute(
                        "INSERT INTO xp_users "
                        "(id, username, discriminator, xp, detailed_xp, level, messages, avatar, prestige)"
                        " VALUES ($1, $2, $3, $4, $5, 0, 1, $6, 0) ON CONFLICT (id) DO NOTHING",
                        member.id,
                        member.name,
                        member.discriminator,
                        gained,
                        [gained, self._xp_function(0), gained],
                        member.avatar.key if member.avatar else None,
                    )
                    return
                if gained + user["detailed_xp"][0] >= self._xp_function(user["level"]):
                    new_level = user["level"] + 1
                    detailed = [0, self._xp_function(new_level), user["xp"] + gained]
                    new_xp = detailed[2]
                    await message.channel.send(
                        f"{message.author.mention} has done some time, and is now level **{new_level}**."
                    )
                    await update_level_roles(member, new_level)
                else:
                    detailed = user["detailed_xp"]
                    detailed[0] += gained
                    detailed[2] += gained
                    new_level = user["level"]
                    new_xp = user["xp"] + gained
                await conn.execute(
                    "UPDATE xp_users SET level = $1, detailed_xp = $2, xp = $3, messages = messages + 1,"
                    " avatar = $4 WHERE id = $5",
                    new_level,
                    detailed,
                    new_xp,
                    member.avatar.key if member.avatar else None,
                    member.id,
                )

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        """Update a user's info for xp data when they have updated their discord info.

        Parameters
        ----------
        before : discord.User
            The updated user`s old info.
        after: discord.User
            The updated user`s updated info.
        """
        async with self.bot.pool.acquire() as conn:
            exists: int | None = await conn.fetchval("SELECT 1 FROM xp_users WHERE id = $1", after.id)
            if exists is None:
                return
            await conn.execute(
                "UPDATE xp_users SET username = $1, discriminator = $2, avatar = $3 WHERE id = $4",
                after.name,
                getattr(after, "discriminator", "0"),
                after.avatar.key if after.avatar else None,
                after.id,
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Check if they are rejoining and should get a rank role back.

        Parameters
        ----------
        member : discord.Member
            The member that joined.
        """
        async with self.bot.pool.acquire() as conn:
            level: int | None = await conn.fetchval("SELECT level FROM xp_users WHERE id = $1", member.id)
            if level is None:
                return
            await conn.execute(
                "UPDATE xp_users SET username = $1, discriminator = $2, avatar = $3 WHERE id = $4",
                member.name,
                getattr(member, "discriminator", "0"),
                member.avatar.key if member.avatar else None,
                member.id,
            )
            if 0 < level < 5:
                await member.add_roles(discord.Object(969626979353632790), reason=f"Rejoined at level {level}")
            elif 5 <= level < 10:
                await member.add_roles(discord.Object(969627321239760967), reason=f"Rejoined at level {level}")
            elif 10 <= level < 20:
                await member.add_roles(discord.Object(969628342733119518), reason=f"Rejoined at level {level}")
            elif 20 <= level < 25:
                await member.add_roles(discord.Object(969629632028614699), reason=f"Rejoined at level {level}")
            elif 25 <= level < 30:
                await member.add_roles(discord.Object(969629628249563166), reason=f"Rejoined at level {level}")
            elif level >= 30:
                await member.add_roles(discord.Object(969629622453039104), reason=f"Rejoined at level {level}")

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 900, key=lambda interaction: interaction.user.id)
    async def rank(self, interaction: Interaction[CBot], user: Optional[discord.Member] = None):
        """Check your or someone's level and rank.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        user : Optional[discord.Member]
            The user to check the level and rank of.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.followup.send("This Must be used in a guild")
            return
        member = user or interaction.user
        guild = interaction.guild
        assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        assert isinstance(guild, discord.Guild)  # skipcq: BAN-B101
        cached_member = guild.get_member(member.id) or member
        async with self.bot.pool.acquire() as conn:
            users = await conn.fetch("SELECT *, ROW_NUMBER() OVER(ORDER BY xp DESC) AS rank FROM xp_users")
            try:
                user_record: asyncpg.Record = next(filter(lambda x: x["id"] == member.id, users))
            except IndexError:
                await interaction.followup.send(
                    translate(cast(_LanguageTag, interaction.locale.value), "rank-error", {})
                )
                return
        image = await asyncio.to_thread(
            self.generator.generate_profile,
            profile_image=member.avatar.url if member.avatar is not None else self.default_profile,
            level=user_record["level"],
            current_xp=user_record["detailed_xp"][2] - user_record["detailed_xp"][0],
            user_xp=user_record["xp"],
            next_xp=user_record["detailed_xp"][2] - user_record["detailed_xp"][0] + user_record["detailed_xp"][1],
            user_position=user_record["rank"],
            user_name=str(member),
            user_status="offline" if isinstance(cached_member.status, str) else cached_member.status.value,
        )

        await interaction.followup.send(file=discord.File(image, "profile.png"))


async def setup(bot: CBot):
    """Load cog."""
    await bot.add_cog(Leveling(bot))
