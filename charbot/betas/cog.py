# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Betas cog file."""
import asyncio
import datetime
import logging
from io import BytesIO
from pathlib import Path
from typing import Final, cast

import asyncpg
import discord
from PIL import Image
from discord import app_commands, utils
from discord.ext import commands

from . import ColorOpts, views
from .banner import generate_banner
from ._types import BannerStatus, BannerStatusPoints
from .. import GuildInteraction as Interaction, CBot


BASE_PATH: Final[Path] = Path(__file__).parent / "user_assets"


class Betas(commands.Cog):
    """Banners."""

    def __init__(self, bot: CBot):  # pragma: no cover
        self.bot = bot

    beta = app_commands.Group(
        name="beta",
        description="Beta testing commands",
        guild_only=True,
    )
    banner = app_commands.Group(name="banner", description="Base group for managing the user banner", parent=beta)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle messages."""
        if message.author.bot or message.guild is None:
            return
        member = cast(discord.Member, message.author)
        if "my banner" in message.content.lower() and message.channel.id == 225345178955808768:
            async with self.bot.pool.acquire() as conn:
                banner_rec: BannerStatusPoints | None = await conn.fetchrow(
                    "SELECT banners.user_id as user_id, quote, banners.color as color, cooldown, approved,"
                    "u.points as POINTS FROM banners JOIN users u on banners.user_id = u.id WHERE banners.user_id = $1",
                    member.id,
                )
                if (
                    banner_rec is not None
                    and banner_rec["cooldown"] < utils.utcnow()
                    and banner_rec["approved"]
                    and banner_rec["points"] > 50
                ):
                    banner_bytes = await generate_banner(banner_rec, member)
                    banner_file = discord.File(banner_bytes, filename="banner.png")
                    await message.reply(file=banner_file)
                    await conn.execute(
                        "UPDATE banners SET cooldown = $1 WHERE user_id = $2",
                        utils.utcnow() + datetime.timedelta(days=7),
                        member.id,
                    )
                    # await conn.execute("UPDATE users SET points = points - 50 WHERE id = $1", member.id)

    @banner.command()  # pyright: ignore[reportGeneralTypeIssues]
    @app_commands.checks.cooldown(2, 60 * 60 * 24 * 7 * 4, key=lambda i: i.user.id)  # pragma: no branch
    async def request(
        self,
        interaction: Interaction[CBot],
        quote: app_commands.Range[str, 0, 100],
        base: discord.Attachment | None = None,
        color: ColorOpts | None = None,
    ) -> None:
        """Request a banner or an edit to an existing banner if an update is rejected, you will need to reapply

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        quote: str
            The quote to use for the banner
        base: discord.Attachment | None, default None
            The base image to use for the banner, leave empty if you want a gradient or solid color banner
        color: ColorOpts | None, default None
            The color to use for the banner, leave empty if you want an image banner
        """
        await interaction.response.defer(ephemeral=True)
        conn: asyncpg.pool.PoolConnectionProxy
        async with interaction.client.pool.acquire() as conn, conn.transaction():
            points: int | None = await conn.fetchval("SELECT points FROM users WHERE id = $1", interaction.user.id)
            if points is None:
                await interaction.followup.send("You don't have any rep yet, earn some first!")
                return
            if points < 350:
                await interaction.followup.send(
                    f"You don't have enough rep to request a banner! (Have: {points}, Need: 350)"
                )
                return
            if base is None and color is None:
                await interaction.followup.send("You need to specify a base image or color!")
                return
            if base is not None and color is not None:
                await interaction.followup.send("You can't specify both a base image and a color!")
                return
            if base is not None:
                content_type = base.content_type
                if content_type not in ("image/png", "image/jpeg"):
                    await interaction.followup.send("The base image must be a PNG or JPEG!")
                    return
                try:

                    def sync_code(img: bytes, path: Path):
                        """Blocking code to run in an executor"""
                        image = Image.open(BytesIO(img))
                        image.save(path, format="PNG")

                    await asyncio.to_thread(
                        sync_code,
                        await base.read(),
                        BASE_PATH / f"{interaction.user.id}.png",
                    )
                except (discord.DiscordException, OSError, ValueError, TypeError):
                    await interaction.followup.send("Failed to grab image, try again.")
                    logging.getLogger("charbot.betas.banner").exception(
                        "Grabbing image raised an exception, content type: %s", content_type
                    )
                    return
                insert_color: str | None = None
            else:
                if color is None:
                    await interaction.followup.send("If you don't specify a base image, a banner color is required.")
                    return
                insert_color: str | None = str(color.value.value)
            await conn.execute(
                "INSERT INTO banners (user_id, quote, color) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET"
                " quote = EXCLUDED.quote, color = EXCLUDED.color, approved = FALSE",
                interaction.user.id,
                quote,
                insert_color,
            )
            remaining: int = await conn.fetchval(
                "UPDATE users SET points = points - 350 WHERE id = $1 RETURNING points", interaction.user.id
            )
            await interaction.followup.send(f"You now have {remaining} rep remaining.\nYou have requested a banner!")

    @banner.command()  # pyright: ignore[reportGeneralTypeIssues]
    async def status(self, interaction: Interaction[CBot]) -> None:
        """Check the status of your banner request.

        Parameters
        ----------
        interaction : Interaction
            The interaction object for the current context
        """
        await interaction.response.defer(ephemeral=True)
        banner_rec: BannerStatusPoints | None = await interaction.client.pool.fetchrow(
            "SELECT banners.user_id as user_id, quote, banners.color as color, cooldown, approved,"
            "u.points as POINTS FROM banners JOIN users u on banners.user_id = u.id WHERE banners.user_id = $1",
            interaction.user.id,
        )
        if banner_rec is None:
            await interaction.followup.send("You don't have a banner_rec, or haven't requested one!")
            return
        if banner_rec["approved"] is False:
            await interaction.followup.send("Your banner_rec is still pending approval!")
            return
        banner_bytes = await generate_banner(banner_rec, interaction.user)
        banner_file = discord.File(banner_bytes, filename="banner.png")
        await interaction.followup.send(
            f"Your banner has been approved and is as follows! Cooldown until: "
            f"{utils.format_dt(banner_rec['cooldown'], 'R')}",
            file=banner_file,
        )

    @commands.command(name="approve")
    @commands.guild_only()
    async def approve_cmd(self, ctx: commands.Context[CBot]):
        """Approve a banner request"""
        member = cast(discord.Member, ctx.author)
        if not member.guild_permissions.manage_roles:
            return
        banner_rec: BannerStatus | None = await ctx.bot.pool.fetchrow(
            "SELECT banners.user_id as user_id, quote, banners.color as color, cooldown, approved,"
            "u.points as POINTS FROM banners JOIN users u on banners.user_id = u.id WHERE banners.approved = FALSE "
            "ORDER BY cooldown LIMIT 1",
        )
        if banner_rec is None:
            await ctx.reply("There are currently no banner awaiting approval!")
            return
        guild = cast(discord.Guild, ctx.guild)
        requester = guild.get_member(banner_rec["user_id"]) or await guild.fetch_member(banner_rec["user_id"])
        banner_bytes = await generate_banner(banner_rec, requester)
        await ctx.reply(
            "Approve, deny, or cancel?",
            file=discord.File(banner_bytes, filename="banner.png"),
            view=views.banner.ApprovalView(banner_rec, member.id),
        )
        banner_bytes.close()
