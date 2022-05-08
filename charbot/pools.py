# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
"""Reputation pools."""
import functools
import math
from io import BytesIO
from typing import Final, Literal

import asyncpg
import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.utils import MISSING
from PIL import Image, ImageDraw, ImageFont

from main import CBot


ALLOWED_ROLES: Final = (
    337743478190637077,
    685331877057658888,
    969629622453039104,
    969629628249563166,
    969629632028614699,
    969628342733119518,
    969627321239760967,
)

CHANNEL_ID: Final[int] = 687817008355737606

MESSAGE: Final = "You must be at least level 5 to participate in the giveaways system and be in <#969972085445238784>."


@app_commands.default_permissions(manage_messages=True)
@app_commands.guilds(225345178955808768)
class Pools(commands.GroupCog, name="pools", description="Reputation pools for certain features."):
    """Reputation pools.

    This cog is used to display reputation pools for certain features.

    The pools are displayed in a card format, and are dynamically listed for the user to choose from based on what is
     available to them.

    The user can then choose a pool and receive a card with the pool's information, or add rep to the pool.

    Parameters
    ----------
    bot : CBot
        The bot object.

    Attributes
    ----------
    bot : CBot
        The bot object.
    default_bg : str
        The default background image.
    default_profile : str
        The default profile image.
    online : str
        The online image.
    offline : str
        The offline image.
    idle : str
        The idle image.
    dnd : str
        The dnd image.
    streaming : str
        The streaming image.
    font1 : str
        The font 1.
    font2 : str
        The font 2.
    """

    def __init__(self, bot: CBot):
        self.bot = bot
        self.default_bg = "media/pools/card.png"
        self.default_profile = "media/pools/profile.png"
        self.online = "media/pools/online.png"
        self.offline = "media/pools/offline.png"
        self.idle = "media/pools/idle.png"
        self.dnd = "media/pools/dnd.png"
        self.streaming = "media/pools/streaming.png"
        self.font1 = "media/pools/font.ttf"
        self.font2 = "media/pools/font2.ttf"

        @self.add.autocomplete("pool")
        async def add_pool_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            """Autocomplete a pool name.

            Parameters
            ----------
            interaction : Interaction
                The interaction object.
            current : str
                The current string.
            """
            return await self.pool_autocomplete(interaction, current)

        @self.query.autocomplete("pool")
        async def query_pool_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            """Autocomplete a pool name.

            Parameters
            ----------
            interaction : Interaction
                The interaction object.
            current : str
                The current string.
            """
            return await self.pool_autocomplete(interaction, current)

    def generate_card(
        self,
        *,
        bg_image: BytesIO = MISSING,
        profile_image: BytesIO = MISSING,
        level: int = 1,
        base_rep: int = 0,
        current_rep: int = 20,
        completed_rep: int = 100,
        pool_name: str = "Unknown",
        pool_status: Literal["online", "offline", "idle", "streaming", "dnd"] = "offline",
    ):
        """Generate a card.

        This is adapted from the disrank library.

        Parameters
        ----------
        bg_image: BytesIO = MISSING
            The background image. Defaults to the default background image.
        profile_image: BytesIO = MISSING
            The profile image. Defaults to the default profile image.
        level: int = 1
            The level of the pool.
        base_rep: int = 0
            The base rep of the pool.
        current_rep: int = 20
            The current rep in the pool.
        completed_rep: int = 100
            The rep needed to complete the pool.
        pool_name: str = "Unknown"
            The name of the pool. Defaults to "Unknown".
        pool_status: Literal['online', 'offline', 'idle', 'streaming', 'dnd'] = "offline"
            The discord status color to roughtly indicate the status of the pool. Defaults to "offline" (grey).

        Returns
        -------
        BytesIO
            The card image as a buffered stream of I/O Bytes.
        """
        if bg_image is MISSING:
            card = Image.open(self.default_bg).convert("RGBA")
        else:
            card = Image.open(bg_image).convert("RGBA")

            width, height = card.size
            if width == 900 and height == 238:
                pass
            else:
                x1 = 0
                y1 = 0
                x2 = width
                nh = math.ceil(width * 0.264444)
                y2 = 0

                if nh < height:
                    y1 = (height // 2) - 119
                    y2 = nh + y1

                card = card.crop((x1, y1, x2, y2)).resize((900, 238))

        profile_bytes: BytesIO | str = profile_image if profile_image is not MISSING else self.default_profile
        profile = Image.open(profile_bytes).convert("RGBA").resize((180, 180))

        if pool_status == "online":
            status = Image.open(self.online)
        elif pool_status == "offline":
            status = Image.open(self.offline)
        elif pool_status == "idle":
            status = Image.open(self.idle)
        elif pool_status == "streaming":
            status = Image.open(self.streaming)
        elif pool_status == "dnd":
            status = Image.open(self.dnd)
        else:
            raise ValueError(f"Unknown status: {pool_status}")

        status = status.convert("RGBA").resize((40, 40))

        profile_pic_holder = Image.new("RGBA", card.size, (255, 255, 255, 0))  # Is used for a blank image for a mask

        # Mask to crop image
        mask = Image.new("RGBA", card.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((29, 29, 209, 209), fill=(255, 25, 255, 255))  # The part need to be cropped

        # Editing stuff here

        # ======== Fonts to use =============
        font_normal = ImageFont.truetype(self.font1, 36)
        font_small = ImageFont.truetype(self.font1, 20)
        # noinspection PyUnusedLocal
        font_signa = ImageFont.truetype(self.font2, 25)  # noqa: F841

        # ======== Colors ========================
        # noinspection PyUnusedLocal
        WHITE = (189, 195, 199)  # noqa: F841
        DARK = (252, 179, 63)
        # noinspection PyUnusedLocal
        YELLOW = (255, 234, 167)  # noqa: F841

        get_str = (
            lambda xp: str(xp) if xp < 1000 else f"{xp / 1000:.1f}k" if xp < 1000000 else f"{xp / 1000000:.1f}M"
        )  # noqa: F731

        draw = ImageDraw.Draw(card)
        draw.text((245, 22), pool_name, DARK, font=font_normal)
        # draw.text((245, 98), f"Rank #{user_position}", DARK, font=font_small)  # skipcq: PY-W0069
        draw.text((245, 123), f"Pool Level {level}", DARK, font=font_small)
        draw.text(
            (245, 150),
            f"Rep {get_str(current_rep)}/{get_str(completed_rep)}",
            DARK,
            font=font_small,
        )

        # Adding another blank layer for the progress bar
        # Because drawing on card doesn't make their background transparent
        blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
        blank_draw = ImageDraw.Draw(blank)
        blank_draw.rectangle((245, 185, 750, 205), fill=(255, 255, 255, 0), outline=DARK)

        xpneed = completed_rep - base_rep
        xphave = current_rep - base_rep

        current_percentage = (xphave / xpneed) * 100
        length_of_bar = (current_percentage * 4.9) + 248

        blank_draw.rectangle((248, 188, length_of_bar, 202), fill=DARK)
        blank_draw.ellipse((20, 20, 218, 218), fill=(255, 255, 255, 0), outline=DARK)

        profile_pic_holder.paste(profile, (29, 29, 209, 209))

        pre = Image.composite(profile_pic_holder, card, mask)
        pre = Image.alpha_composite(pre, blank)

        # Status badge
        # Another blank
        blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))
        blank.paste(status, (169, 169))

        final = Image.alpha_composite(pre, blank)
        final.show()
        final_bytes = BytesIO()
        final.save(final_bytes, "png")
        final_bytes.seek(0)
        return final_bytes

    async def pool_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete a pool name.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        current : str
            The current string.

        Returns
        -------
        list[app_commands.Choice[str]]
            The list of choices.
        """
        member = interaction.user
        assert isinstance(member, discord.Member)  # skipcq: BAN-B101
        return [
            app_commands.Choice(name=pool["pool"], value=pool["pool"])
            for pool in await self.bot.pool.fetch("SELECT pool, required_roles FROM pools")
            if current.lower() in pool["pool"].lower()
            and any(role.id in pool["required_roles"] for role in member.roles)
        ]

    @app_commands.command(name="add", description="Add reputation to an active pool.")
    @app_commands.describe(pool="The pool to add to.", amount="The amount to add.")
    async def add(self, interaction: Interaction, pool: str, amount: int):
        """Add reputation to an active pool.

        If the pool would be overfilled by the addition, it only fills it to the maximum.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The pool to add to.
        amount : int
            The amount to add.
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in ALLOWED_ROLES for role in user.roles) or interaction.channel_id != CHANNEL_ID:
            await interaction.response.send_message(MESSAGE, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            pool_record = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if pool is None:
                await interaction.followup.send("Pool not found. Please choose one from the autocomplete.")
                return
            assert isinstance(pool_record, asyncpg.Record)  # skipcq: BAN-B101
            if not any(role.id in pool_record["required_roles"] for role in user.roles):
                await interaction.followup.send(f"You don't have the required roles to add to {pool_record['pool']}.")
                return
            user_record = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
            if user_record is None:
                await interaction.followup.send("You haven't gained any rep yet.")
                return
            assert isinstance(user_record, asyncpg.Record)  # skipcq: BAN-B101
            if user_record["points"] < amount:
                await interaction.followup.send(
                    f"You don't have enough rep to add {amount} to the pool. you have {user_record['points']} rep."
                )
                return
            if pool_record["current"] + amount > pool_record["cap"]:
                amount = pool_record["cap"] - pool_record["current"]
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", amount, user.id
            )
            after = await conn.fetchval(
                "UPDATE pools SET current = current + $1 WHERE pool = $2 returning current", amount, pool
            )
        completed_ratio = round(after / pool_record["cap"], 2)
        status: Literal["online", "offline", "idle", "streaming", "dnd"] = "offline"
        if completed_ratio < 0.34:
            status = "dnd"
        elif 0.34 <= completed_ratio < 0.67:
            status = "idle"
        elif 0.67 <= completed_ratio < 1:
            status = "streaming"
        elif completed_ratio == 1:
            status = "online"
        image_generator: functools.partial[BytesIO] = functools.partial(
            self.generate_card,
            level=pool_record["level"],
            base_rep=pool_record["start"],
            current_rep=after,
            completed_rep=pool_record["cap"],
            pool_name=pool,
            pool_status=status,
        )
        image_bytes: BytesIO = await self.bot.loop.run_in_executor(None, image_generator)
        image = discord.File(image_bytes, filename=f"{pool}.png")
        await interaction.followup.send(
            f"You have added {amount} rep to {pool} you now have {remaining} rep remaining.", file=image
        )
        clientuser = self.user
        assert isinstance(clientuser, discord.ClientUser)  # skipcq: BAN-B101
        await self.bot.program_logs.send(
            f"{user.mention} added {amount} rep to {pool} ({after}/{pool_record['cap']}).",
            username=clientuser.name,
            avatar_url=clientuser.display_avatar.url,
            allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
        )
        if after == pool_record["cap"]:
            await self.bot.program_logs.send(
                f"{pool} has been filled.",
                username=clientuser.name,
                avatar_url=clientuser.display_avatar.url,
                allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
            )
            image_generator: functools.partial[BytesIO] = functools.partial(
                self.generate_card,
                level=pool_record["level"],
                base_rep=pool_record["start"],
                current_rep=after,
                completed_rep=pool_record["cap"],
                pool_name=f"[COMPLETED] {pool}",
                pool_status=status,
            )
            image_bytes: BytesIO = await self.bot.loop.run_in_executor(None, image_generator)
            image = discord.File(image_bytes, filename=f"{pool}.png")
            channel = interaction.channel
            assert isinstance(channel, discord.abc.Messageable)  # skipcq: BAN-B101
            await channel.send(f"{user.mention} has filled {pool}!", file=image)

    @app_commands.command(name="query", description="Check the status of an active pool.")
    @app_commands.describe(pool="The pool to check.")
    async def query(self, interaction: Interaction, pool: str):
        """Check the status of an active pool.

        Parameters
        ----------
        interaction : Interaction
            The interaction object.
        pool : str
            The pool to check.
        """
        user = interaction.user
        assert isinstance(user, discord.Member)  # skipcq: BAN-B101
        if not any(role.id in ALLOWED_ROLES for role in user.roles) or interaction.channel_id != CHANNEL_ID:
            await interaction.response.send_message(MESSAGE, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            pool_record = await conn.fetchrow("SELECT * FROM pools WHERE pool = $1", pool)
            if pool is None:
                await interaction.followup.send("Pool not found. Please choose one from the autocomplete.")
                return
            assert isinstance(pool_record, asyncpg.Record)  # skipcq: BAN-B101
            if not any(role.id in pool_record["required_roles"] for role in user.roles):
                await interaction.followup.send("Pool not found. Please choose one from the autocomplete.")
                return
        completed = round(pool_record["current"] / pool_record["cap"], 2)
        status: Literal["online", "offline", "idle", "streaming", "dnd"] = "offline"
        if completed < 0.34:
            status = "dnd"
        elif 0.34 <= completed < 0.67:
            status = "idle"
        elif 0.67 <= completed < 1:
            status = "streaming"
        elif completed == 1:
            status = "online"
        image_generator: functools.partial[BytesIO] = functools.partial(
            self.generate_card,
            level=pool_record["level"],
            base_rep=pool_record["start"],
            current_rep=pool_record["current"],
            completed_rep=pool_record["cap"],
            pool_name=pool,
            pool_status=status,
        )
        image_bytes: BytesIO = await self.bot.loop.run_in_executor(None, image_generator)
        await interaction.followup.send(file=discord.File(image_bytes, filename=f"{pool}.png"))


async def setup(bot: CBot):
    """Load the cog."""
    await bot.add_cog(Pools(bot))
