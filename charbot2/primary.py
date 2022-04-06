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
"""
This is the primary module for charbot2.
"""
import re
from datetime import datetime, timedelta, timezone

import discord
from discord import Embed, Color
from discord.ext import commands, tasks
from discord.ext.commands import Cog, Context
from discord.utils import utcnow


async def time_string_from_seconds(delta: float) -> str:
    """Convert seconds to a string

    Parameters
    ----------
    delta : float
        The number of seconds to convert to a string
    """
    minutes, sec = divmod(delta, 60)
    hour, minutes = divmod(minutes, 60)
    day, hour = divmod(hour, 24)
    year, day = divmod(day, 365)
    return (
        f"{year} Year(s), {day} Day(s), {hour} Hour(s),"
        f" {minutes} Min(s), {sec:.2f} Sec(s)"
    )


class PrimaryFunctions(Cog):
    """Primary CharBot2 class"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.timeouts = {}
        self.members: dict[int, datetime] = {}

    async def cog_load(self) -> None:
        """Cog load function

        This is called when the cog is loaded, and initializes the
        log_untimeout task and the members cache

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        self.log_untimeout.start()
        guild = await self.bot.fetch_guild(225345178955808768)
        generator = guild.fetch_members(limit=None)
        self.members.update(
            {user.id: user.joined_at async for user in generator}  # type: ignore
        )

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Called when cog is unloaded

        This stops the log_untimeout task

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        self.log_untimeout.cancel()

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands

        This checks if the runner is a moderator

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        ctx : Context
            The context of the command

        Returns
        -------
        bool
            Whether the command should be run

        Raises
        ------
        commands.CheckFailure
            If the user is not a moderator
        """
        return any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles  # type: ignore
        )

    @commands.command()
    async def ping(self, ctx):
        """Ping command to check if the bot is alive

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        ctx : Context
            The context of the command
        """
        await ctx.send(f"Pong! Latency: {self.bot.latency * 1000:.2f}ms")

    @tasks.loop(seconds=30)
    async def log_untimeout(self) -> None:
        """Untimeout Report Task

        This task runs every 30 seconds and checks if any users that have been timed out have had their timeouts
        expired. If they have, it will send a message to the mod channel.

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        """
        removeable = []
        for i, j in self.timeouts.copy().items():
            if j < datetime.now(tz=timezone.utc):
                member = await (
                    await self.bot.fetch_guild(225345178955808768)
                ).fetch_member(i)
                if not member.is_timed_out():
                    embed = Embed(color=Color.green())
                    embed.set_author(
                        name=f"[UNTIMEOUT] {member.name}#{member.discriminator}"
                    )
                    embed.add_field(name="User", value=member.mention, inline=True)
                    channel = await self.bot.fetch_channel(426016300439961601)
                    await channel.send(  # type: ignore
                        embed=embed
                    )  # type: ignore
                    removeable.append(i)
                elif member.is_timed_out():
                    self.timeouts.update({i: member.timed_out_until})
        for i in removeable:
            self.timeouts.pop(i)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Processes when a member joins the server and adds them to the members cache

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        member : discord.Member
            The member that joined the server
        """
        if member.guild.id == 225345178955808768:
            self.members.update({member.id: utcnow()})

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handles when a message is sent
        If the message is a dm, it redirects them to the mod support page
        If the message is a ping in the #goodbye channel, it deletes the message and
        sends a message to that channel with the goodbye message

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        message : discord.Message
            The message that was sent
        """
        if (
            not message.author.bot
            and message.channel.type is discord.ChannelType.private
        ):
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail,"
                " that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>"
            )
        elif message.channel.id == 430197357100138497 and (
            len(message.mentions) == 1 or re.search(r"<@!?(\d+)>\B", message.content)
        ):
            member = message.mentions[0] if message.mentions else None
            mentioned_id = None
            search = re.search(r"<@!?(\d+)>\B", message.content)
            if search:
                mentioned_id = int(search.groups()[0])  # type: ignore
            if member and member.joined_at:  # type: ignore
                delta = (utcnow() - member.joined_at).total_seconds()  # type: ignore
                time_string = await time_string_from_seconds(abs(delta))
                self.members.pop(member.id, None)
            elif member and member.id in self.members:
                delta = (utcnow() - self.members.pop(member.id)).total_seconds()
                time_string = await time_string_from_seconds(abs(delta))
            elif mentioned_id and mentioned_id in self.members:
                time = self.members.pop(mentioned_id)  # type: ignore
                delta = (utcnow() - time).total_seconds()
                time_string = await time_string_from_seconds(abs(delta))
            else:
                time_string = "None Found"
            print(member)
            member = (
                member
                if member
                else await self.bot.fetch_user(mentioned_id)
                if mentioned_id
                else None
            )
            print(member)
            if member:
                await (
                    await self.bot.fetch_channel(430197357100138497)
                ).send(  # type: ignore
                    f"**{member.name}#{member.discriminator}** has left the server. "
                    f"ID:{member.id}. Time on Server: {time_string}"
                )
                await message.delete()

    # noinspection PyBroadException
    @Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Processes when a member is timed out or untimed out
        If the member is timed out, it adds them to the timeouts cache
        If the member is untimed out, it removes them from the timeouts cache
        In both cases, it logs the action to the mod log

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        before : discord.Member
            The member before the update
        after : discord.Member
            The member after the update
        """
        try:
            if after.timed_out_until != before.timed_out_until:
                if after.is_timed_out():
                    await self.parse_timeout(after)
                else:
                    embed = Embed(color=Color.green())
                    embed.set_author(
                        name=f"[UNTIMEOUT] {after.name}#{after.discriminator}"
                    )
                    embed.add_field(name="User", value=after.mention, inline=True)
                    channel = await self.bot.fetch_channel(426016300439961601)
                    await channel.send(  # type: ignore
                        embed=embed
                    )  # type: ignore
                    self.timeouts.pop(after.id)
        except Exception:  # skipcq: PYL-W0703
            if after.is_timed_out():
                await self.parse_timeout(after)

    async def parse_timeout(self, after: discord.Member):
        """Parse the timeout and logs it to the mod log

        Parameters
        ----------
        self : PrimaryFunctions
            The PrimaryFunctions object
        after : discord.Member
            The member after the update
        """
        time_delta = (
            after.timed_out_until  # type: ignore
            + timedelta(seconds=1)
            - datetime.now(tz=timezone.utc)
        )
        time_string = ""
        if time_delta.days // 7 != 0:
            time_string += (
                f"{time_delta.days // 7} Week{'s' if time_delta.days // 7 > 1 else ''}"
            )
        if time_delta.days % 7 != 0:
            time_string += (
                f"{', ' if bool(time_string) else ''}{time_delta.days % 7} Day(s) "
            )
        if time_delta.seconds // 3600 > 0:
            time_string += (
                f"{', ' if bool(time_string) else ''}"
                f"{time_delta.seconds // 3600} Hour(s) "
            )
        if (time_delta.seconds % 3600) // 60 != 0:
            time_string += (
                f"{', ' if bool(time_string) else ''}"
                f"{(time_delta.seconds % 3600) // 60} Minute(s) "
            )
        if (time_delta.seconds % 3600) % 60 != 0:
            time_string += (
                f"{', ' if bool(time_string) else ''}"
                f"{(time_delta.seconds % 3600) % 60} Second(s) "
            )
        embed = Embed(color=Color.red())
        embed.set_author(name=f"[TIMEOUT] {after.name}#{after.discriminator}")
        embed.add_field(name="User", value=after.mention, inline=True)
        embed.add_field(name="Duration", value=time_string, inline=True)
        channel = await self.bot.fetch_channel(426016300439961601)
        await channel.send(embed=embed)  # type: ignore
        self.timeouts.update({after.id: after.timed_out_until})


async def setup(bot: commands.Bot):
    """Sets up the cog

    Parameters
    ----------
    bot : commands.Bot
        The bot object
    """
    await bot.add_cog(PrimaryFunctions(bot))
