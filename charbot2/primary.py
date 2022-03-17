# coding=utf-8
import re
import time
from datetime import datetime, timedelta, timezone

import discord
from discord import Embed, Color
from discord.ext import commands, tasks
from discord.ext.commands import Cog, Context


async def time_string_from_seconds(delta: float) -> str:
    """Converts time float to str"""
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
        """Init func"""
        self.bot = bot
        self.timeouts = {}

    async def cog_load(self) -> None:
        """Cog load hook"""
        self.log_untimeout.start()

    async def cog_unload(self) -> None:  # skipcq: PYL-W0236
        """Cog close function"""
        self.log_untimeout.cancel()

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands"""
        return any(
            role.id in (338173415527677954, 253752685357039617, 225413350874546176)
            for role in ctx.author.roles
        )

    @commands.command()
    async def ping(self, ctx):
        """Ping command"""
        await ctx.send(f"Pong! Latency: {self.bot.latency * 1000:.2f}ms")

    @tasks.loop(seconds=30)
    async def log_untimeout(self) -> None:
        """Untimeout Report Method"""
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
                    await (await self.bot.fetch_channel(426016300439961601)).send(
                        embed=embed
                    )
                    removeable.append(i)
                elif member.is_timed_out():
                    self.timeouts.update({i: member.timed_out_until})
        for i in removeable:
            self.timeouts.pop(i)

    async def uncached_time_search(
        self, message: discord.Message, member: discord.Member
    ) -> str:
        """Tries to find a join time by channel"""
        channel = await self.bot.fetch_channel(225345178955808768)
        messages = channel.history(before=datetime.utcnow())
        mentioned_id = None
        if re.search(r"<@!?(\d+)>\B", message.content) and not member:
            mentioned_id = int(re.search(r"<@!?(\d+)>\B", message.content).groups()[0])
        try:
            async for item in messages:
                if not item.author.bot:
                    continue
                is_mentioned = False
                if member:
                    if str(member.id) in message.content:
                        is_mentioned = True
                elif mentioned_id:
                    if str(mentioned_id) in message.content:
                        is_mentioned = True
                if is_mentioned:
                    delta = time.mktime(item.created_at.utctimetuple()) - time.time()
                    return await time_string_from_seconds(delta)
        except TypeError:
            return "None Found"

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message func"""
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
            print("detected")
            member = message.mentions[0] if message.mentions else None
            mentioned_id = None
            if member and member.joined_at:
                delta = time.time() - time.mktime(member.joined_at.utctimetuple())
                time_string = await time_string_from_seconds(delta)
            else:
                print("not cached")
                time_string = await self.uncached_time_search(message, member)
            print(member)
            if re.search(r"<@!?(\d+)>\B", message.content):
                mentioned_id = int(re.search(r"<@!?(\d+)>\B", message.content).groups()[0])
            member = (
                member
                if member
                else await self.bot.fetch_user(mentioned_id)
                if mentioned_id
                else None
            )
            print(member)
            if member:
                await (await self.bot.fetch_channel(430197357100138497)).send(
                    f"**{member.name}#{member.discriminator}** has left the server. "
                    f"ID:{member.id}. Time on Server: {time_string}"
                )
                await message.delete()

    # noinspection PyBroadException
    @Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """On member update func"""
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
                    await (await self.bot.fetch_channel(426016300439961601)).send(
                        embed=embed
                    )
                    self.bot.timeouts.pop(after.id)
        except Exception:  # skipcq: PYL-W0703
            if after.is_timed_out():
                await self.parse_timeout(after)

    async def parse_timeout(self, after: discord.Member):
        """Parses timeouts"""
        time_delta = (
            after.timed_out_until + timedelta(seconds=1) - datetime.now(tz=timezone.utc)
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
        await (await self.bot.fetch_channel(426016300439961601)).send(embed=embed)
        self.timeouts.update({after.id: after.timed_out_until})


async def setup(bot: commands.Bot):
    """Setup"""
    await bot.add_cog(PrimaryFunctions(bot))
