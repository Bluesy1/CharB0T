"""Admin commands for charbot."""

import pathlib
from time import perf_counter
from typing import Final, cast

import discord
from discord import Color, Interaction, PermissionOverwrite, Permissions, app_commands
from discord.ext import commands

from . import CBot


class Admin(commands.Cog):
    """Admin Cog."""

    XCOM_MESSAGE: Final[str] = (
        "**You have been recruited into XCOM**. Welcome! You'll find you have access to new channels reserved for those"
        " in the barracks. For the most up-to-date information on the state of the campaign, **CHECK THE PINS!** "
        "<:CheckPins:907814529319202836> There's a chance also that you are tagged in these updates. It means that you "
        "may have information I require of you (like for promotions). Please try to respond to those requests within 24"
        " hours. I will proceed and make a decision without you if you don't, but if you don't plan to, please tell me "
        "that instead so I can play on faster.\n\nInfo is secret...\nWe ask that information that's in the barracks "
        "stay in the barracks, including all conversations related to the events of the videos that are not yet public."
        " You also have access to these videos now. **__DO NOT SHARE THESE VIDEOS WITH ANYONE PLEASE__**. "
        "If I see any of these leak ahead of schedule, advanced access to them will immediately cease. - Comments on "
        "the video are disabled while they are in this channel. When they publish, THAT would be a great time to try "
        "and boost the series a little bit with YouTube by leaving a comment on the video then. Comments on the"
        " videos themselves ALWAYS help substantially more than remarks made here on Discord."
    )
    EMBED = discord.Embed(title="Welcome to XCOM!", description=XCOM_MESSAGE, color=Color.dark_blue()).set_footer(
        text="I am a bot, and this action was taken automatically. If you think this was done by accident,"
        " please reply to this message."
    )

    def __init__(self, bot: CBot):
        self.bot = bot
        self.settings: pathlib.Path = pathlib.Path(__file__).parent / "sensitive_settings.json"
        self.base_overrides = {}

    async def cog_load(self) -> None:  # pragma: no cover
        """Make sure the guild stuff is loaded."""
        guild = cast(
            discord.Guild, self.bot.get_guild(225345178955808768) or await self.bot.fetch_guild(225345178955808768)
        )
        self.base_overrides = {
            cast(discord.Role, guild.get_role(338173415527677954)): PermissionOverwrite.from_pair(
                Permissions(139586817088), Permissions.none()
            ),
            guild.default_role: PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False),
        }

    def cog_check(self, ctx: commands.Context) -> bool:
        """Check to make sure runner is a moderator.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.

        Returns
        -------
        bool
            True if the user is a moderator, False otherwise.

        Raises
        ------
        commands.CheckFailure
            If the user is not a moderator.
        """
        if ctx.guild is None:
            return False
        author = ctx.author
        assert isinstance(author, discord.Member)  # skipcq: BAN-B101
        return any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in author.roles)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Ping Command TO Check Bot Is Alive.

        This command is used to check if the bot is alive.

        Parameters
        ----------
        self : Admin
            The Admin cog object.
        ctx : Context
            The context of the command.
        """
        start = perf_counter()
        await ctx.typing()
        end = perf_counter()
        typing = end - start
        start = perf_counter()
        await self.bot.pool.fetchrow("SELECT * FROM users WHERE id = $1", ctx.author.id)
        end = perf_counter()
        database = end - start
        start = perf_counter()
        message = await ctx.send("Ping ...")
        end = perf_counter()
        await message.edit(
            content=f"Pong!\n\nPing: {(end - start) * 100:.2f}ms\nTyping: {typing * 1000:.2f}ms\nDatabase: "
            f"{database * 1000:.2f}ms\nWebsocket: {self.bot.latency * 1000:.2f}ms"
        )

    @commands.command(hidden=True)
    async def recruit(self, ctx: commands.Context[CBot], *members: discord.Member):  # pragma: no cover
        """Recruit a member to XCOM.

        Parameters
        ----------
        ctx : Context
            The context of the command.
        *members : Member
            The members to recruit.
        """
        if not await ctx.bot.is_owner(ctx.author):  # pragma: no cover
            return  # ignore if not from bot owner
        ret = 0
        for member in members:
            try:
                await member.add_roles(discord.Object(1042837754104533075), reason="New recruit")
            except discord.HTTPException:
                await ctx.send("I cannot add the XCOM role.")
                return
            try:
                await member.send(embed=self.EMBED)
            except discord.HTTPException:
                guild = cast(discord.Guild, ctx.guild)
                category = cast(
                    discord.CategoryChannel,
                    guild.get_channel(942578610336837632) or await guild.fetch_channel(942578610336837632),
                )
                channel = await ctx.guild.create_text_channel(  # pyright: ignore
                    name=f"xcom-{member.name}-mod-support",
                    category=category,
                    overwrites=self.base_overrides  # pyright: ignore[reportArgumentType]
                    | {
                        member: PermissionOverwrite.from_pair(Permissions(139586817088), Permissions.none()),
                    },
                )
                await channel.send(
                    f"{member.mention} welcome to XCOM! because you have DMs disabled, please acknowledge the "
                    f"onboarding information here:",
                    embed=self.EMBED,
                )
            else:
                ret += 1
        await ctx.reply(f"{ret}/{len(members)} members were added to XCOM and recruited.")

    @app_commands.command(name="confirm", description="[Charlie only] confirm a winner")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 3600, key=lambda i: i.namespace.member)
    async def confirm(self, interaction: Interaction[CBot], member: discord.Member) -> None:
        """Confirm a winner.

        Parameters
        ----------
        interaction: charbot.Interaction[CBot]
            The interaction of the command invocation. At runtime, this is a discord.Interaction object, buy for
            typechecking, it's a charbot.Interaction object to help infer the properties of the object.
        member : discord.Member
            The user to confirm as a winner.
        """
        if interaction.user.id != 225344348903047168:
            await interaction.response.send_message("Only Charlie can confirm a winner.", ephemeral=True)
            return
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO winners (id, wins) VALUES ($1, 1) ON CONFLICT (id) DO UPDATE SET wins = winners.wins + 1",
                member.id,
            )
            wins = await conn.fetchrow("SELECT wins FROM winners WHERE id = $1", member.id)
        await interaction.response.send_message(
            f"Confirmed {member} (ID: {member.id}) as having won a giveaway, ({wins}/3 this month for them)",
            ephemeral=True,
        )


async def setup(bot: CBot):
    """Add the Admin cog to the bot.

    Parameters
    ----------
    bot : commands.Bot
        The bot object.
    """
    await bot.add_cog(Admin(bot))
