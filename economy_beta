import datetime
import json
import os
import random
import time
import typing
from decimal import Decimal
from typing import Final

import asyncpg
import hikari
import lightbulb
from hikari import Embed
from hikari.commands import CommandChoice
from lightbulb import commands
from lightbulb.checks import guild_only
from numpy import ceil  # pylint: disable=no-name-in-module
from pytz import timezone

EPHEMERAL: Final[int] = 64
MODVADMIN: Final[str] = "A  role marked as mod is ignored by autopunishments. A role marked as admin can edit the " \
                        "bot's settings along with the benefits of being a mod. "
DISABLER: Final[str] = "A role marked as disabling will mean that a user with this role cannot use this portion of " \
                       "the bot, even if they have another role that would allow it. A role marked as enabling will " \
                       "allow a user to use this portion of the bot," \
                       " as long as they don't have any role listed under " \
                       "disabling. Users listed with a mod role are not immune to disabling roles, but Users with an " \
                       "admin role are. If the everyone role is set as an enabling role, all users without a " \
                       "disabling role can use the bot (not recommended on servers that already have a levelling " \
                       "system). If the everyone role is set as a disabling role, the system will be disabled " \
                       "completely. "
ECONOMYSETTINGS: Final[str] = "Minimum Gain, Maximum Gain, and Step dictate how random numbers are generated for the " \
                              "/work system - a number between the minimum and maximum, both inclusive with steps of " \
                              "size step from the minimum. i.e., for a (min,max,step) of (800,1200,5), which are the " \
                              "default settings, the random number possibilities would be (800,805,810,815,...,1190," \
                              "1195,1200). Gain cooldown is the number of seconds between work uses for a user, " \
                              "default 11.5 hours, it's recommended to set this slightly under the time you " \
                              "advertise. i.e., for a 12-hour cycle, it's suggested using a cycle of 11.5 hours so " \
                              "people don't have to be perfect. Coin name and symbol allow you to customize the name " \
                              "and symbol of the coin if you don't like the default name of EchoCoin with the symbol " \
                              "<:Echocoin:928020676751814656>. Default starting balance allows people to start " \
                              "investing without having to do a couple of work cycles first. The default is 10,000, " \
                              "but you can change this if you want." \
                              " All currencies, regardless of name and symbol are " \
                              "always a 1:1 vs USD for simplicity. "
MODERATIONSETTINGS: Final[str] = "Nitro Scan and Crypto Scan respectively refer to whether the Nitro and Crypto Scam " \
                                 "Detections are active. Mute Role is the role that the bot will assign if the bot " \
                                 "believes that a message has a high probability of" \
                                 " a scam but is not 100% sure. Main " \
                                 "Log is where punishments are logged, and Message/Secondary log is for when there's " \
                                 "a very log probability there's a scam. Its suggested to set the secondary/message " \
                                 "logging to your message log channel if you have one, but it gets triggered very " \
                                 "infrequently in most servers where it would be used. "
DEFAULTNAME: Final[str] = "EchoCoin"
DEFAULTSYMBOL: Final[str] = "<:Echocoin:928020676751814656>"
Economy = lightbulb.Plugin("Economy", default_enabled_guilds=225345178955808768)


async def get_db() -> asyncpg.Connection:
    """Opens a PostgreSQL Connection"""
    with open('sqlinfo.json', encoding='utf8') as file:
        sqlinfo = json.load(file)
    return await asyncpg.connect(host=sqlinfo['host'], user=sqlinfo['user'], password=sqlinfo['password'],
                                 database=sqlinfo['database'])


@lightbulb.Check
async def check_author_work_allowed(context: lightbulb.Context) -> bool:
    """Checks if command user can work"""
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", context.guild_id)
    role_ids = context.member.role_ids
    possible = False
    for sub_result in result:
        if context.guild_id == sub_result[1] and bool(sub_result['disabling']):
            await mydb.close()
            return False
        if context.guild_id == sub_result[1] and not bool(sub_result['disabling']):
            possible = True
        elif sub_result[1] in role_ids and bool(sub_result['disabling']):
            await mydb.close()
            return False
        elif sub_result[1] in role_ids and not bool(sub_result['disabling']):
            possible = True
    await mydb.close()
    return possible


@lightbulb.Check
async def check_author_is_admin(context: lightbulb.Context) -> bool:
    """Checks if command user has admin perms"""
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1", context.guild_id)
    role_ids = context.member.role_ids
    for sub_result in result:
        if sub_result[1] in role_ids and sub_result[2] > 0:
            return True
    await mydb.close()
    return False


@lightbulb.Check
async def check_author_is_mod(context: lightbulb.Context) -> bool:
    """Checks if command user has mod perms"""
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1", context.guild_id)
    role_ids = context.member.role_ids
    for sub_result in result:
        if sub_result[1] in role_ids:
            return True
    await mydb.close()
    return False


@Economy.command()
@lightbulb.add_checks(check_author_is_admin, guild_only)
@lightbulb.command("config", "configuration group")
@lightbulb.implements(commands.SlashCommandGroup)
async def config(ctx: lightbulb.Context) -> None:
    """Config Group"""
    await ctx.respond("invoked config")


@config.child
@lightbulb.command("roles", "config role group", inherit_checks=True)
@lightbulb.implements(commands.SlashSubGroup)
async def roles(ctx: lightbulb.Context) -> None:
    """Config Roles Group"""
    await ctx.respond("invoked config mods")


@config.child
@lightbulb.option("group", "settings group to query", type=int,
                  choices=[CommandChoice(name="Work Roles", value=1), CommandChoice(name="Work settings", value=2)])
@lightbulb.command("query", "querys guild settings for the bot", inherit_checks=True, auto_defer=True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_mods_query(ctx: lightbulb.Context):
    """Mod Role Config Display"""
    mydb = await get_db()
    queryier = ctx.options.group
    if queryier == 1:
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", ctx.guild_id)
        embed = Embed(
            title="Work Enabler and Disabler roles in the bot",
            description=DISABLER,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc), color="0x0000ff")
        for sub_result in result:
            embed.add_field(
                "Disabling Role" if sub_result['disabling'] else "Enabling Role", f"<@&{sub_result['role_id']}>",
                inline = True)
    elif queryier == 2:
        result = await mydb.fetchrow("SELECT * FROM guild_feature_work WHERE guild_id = $1", ctx.guild_id)
        embed = Embed(
            title=f"Economy settings in {ctx.get_guild().name}", description=ECONOMYSETTINGS,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc), color="0x0000ff")
        embed.add_field("Minimum Gain", f"{result['min_gain']} {result['coin_symbol']}", inline=True)
        embed.add_field("Maximum Gain", f"{result['max_gain']} {result['coin_symbol']}", inline=True)
        embed.add_field("Step", f"{result['gain_step']} {result['coin_symbol']}", inline=True)
        embed.add_field(
            "Gain Cooldown", f"{result['gain_cooldown']} Seconds ({result['gain_cooldown'] / 3600} Hours)",
            inline=True)
        embed.add_field("Coin Name", result['coin_name'], inline=True)
        embed.add_field("Coin Symbol", result['coin_symbol'], inline=True)
        embed.add_field("Starting Balance", f"{int(result['starting_bal'])} {result['coin_symbol']}", inline=True)
    else:
        return
    await ctx.respond(embed=embed, flags=EPHEMERAL)
    await mydb.close()


@roles.child
@lightbulb.option("disabling", "should the role be disabling", type=bool, required=True)
@lightbulb.option("add", "True to add or edit, False to remove", type=bool, required=True)
@lightbulb.option("role", "role to add/edit/remove from work list", type=hikari.Role, required=True)
@lightbulb.command("work", "adds, edits, or removes a role from consideration as a work role", inherit_checks=True,
                   auto_defer=True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_roles_work(ctx: lightbulb.Context):
    """Work Roles Config"""
    mydb = await get_db()
    role: Final[hikari.Role] = ctx.options.role
    add: Final[bool] = ctx.options.add
    disabling: Final[bool] = ctx.options.disabling
    new = True
    result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", ctx.guild_id)
    for sub_result in result:
        if int(role.id) == int(sub_result[1]):
            new = False
    if add and not new:
        await mydb.execute("UPDATE guild_feature_work_roles set disabling = $1 WHERE guild_id = $2 and role_id = $3",
                           disabling, ctx.guild_id, role.id)
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", ctx.guild_id)
    elif add and new:
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", ctx.guild_id)
        await mydb.execute("INSERT INTO guild_feature_work_roles (guild_id, role_id, disabling) VALUES ($1,$2, $3)",
                           ctx.guild_id, role.id, disabling)
    else:
        await mydb.execute("DELETE FROM guild_feature_work_roles WHERE role_id = $1", role.id)
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1", ctx.guild_id)
    embed = Embed(title="New List of enabling and disabling roles", description=MODVADMIN,
                  color="0x00ff00" if add and new else "0x0000ff" if add and not new else "0xff0000",
                  timestamp=datetime.datetime.now(tz=datetime.timezone.utc))
    if add and new:
        embed.add_field("**NEW** Disabling Role" if bool(disabling) else "**NEW** Enabling Role", f"<@&{role.id}>",
                        inline=True)
    elif add and not new:
        embed.add_field("**CHANGED TO** Disabling Role" if bool(disabling) else "**CHANGED TO** Enabling Role",
                        f"<@&{role.id}>", inline=True)
    for sub_result in result:
        if int(sub_result[1]) == int(role.id):
            continue
        embed.add_field(
            "Disabling Role" if sub_result['disabling'] else "Enabling Role", f"<@&{sub_result['role_id']}>",
            inline = True)
    await ctx.respond(embed=embed, flags=EPHEMERAL)


# noinspection PyBroadException
@config.child
@lightbulb.option("starting_bal", "balance to start all new users of the bot on the server with", type=int, default=1,
                  min_value=1, required=False)
@lightbulb.option("symbol",
                  "default to reset, send one emoji to use a custom one, bot must be in emote's server if server emote",
                  type=str, default="", required=False)
@lightbulb.option("name", "custom name for the coin, put 'default' (without the quotes) to reset to the default name",
                  type=str, default="", required=False)
@lightbulb.option("cooldown",
                  "cooldown between allowed uses of /work by a single user, in seconds. i.e. 3600 is one hour",
                  type=int, default=3599, min_value=3599, required=False)
@lightbulb.option("step", "step between numbers possible to randomly generate", type=int, default=1, min_value=1,
                  max_value=100, required=False)
@lightbulb.option("maximum", "maximum possible gain for a use of /work", type=int, default=1, min_value=1,
                  required=False)
@lightbulb.option("minimum", "minimum possible gain for a use of /work", type=int, default=0, min_value=0,
                  required=False)
@lightbulb.command("work", "edits guild settings for the work module. leave option default to leave unchanged",
                   inherit_checks=True, auto_defer=True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_work(ctx: lightbulb.Context):
    """Work Config Command"""
    if all(thing is None for thing in
           [ctx.options.minimum, ctx.options.maximum, ctx.options.step, ctx.options.cooldown, ctx.options.name,
            ctx.options.symbol, ctx.options.starting_bal]):
        await ctx.respond(
            embed=Embed(
                title="**ERROR** No Settings changed",
                description="If you want to check settings, see `/config query` and select the work settings",
                color="0xff0000", timestamp=datetime.datetime.now(tz=datetime.timezone.utc)),
            flags=EPHEMERAL)
        return
    minimum = ctx.options.minimum if ctx.options.minimum is not None else 0
    maximum = ctx.options.maximum if ctx.options.maximum is not None else 1
    step = ctx.options.step if ctx.options.step is not None else 1
    cooldown = ctx.options.cooldown if ctx.options.cooldown is not None else 3599
    name = ctx.options.name if ctx.options.name is not None else ""
    symbol = ctx.options.symbol if ctx.options.symbol is not None else ""
    starting_bal = ctx.options.starting_bal if ctx.options.starting_bal is not None else 1
    mydb = await get_db()
    result = await mydb.fetchrow("SELECT * FROM guild_feature_work WHERE guild_id = $1", ctx.guild_id)
    curr_min = minimum if minimum else result['min_gain']
    curr_max = maximum if maximum != 1 else result['max_gain']
    if curr_min > curr_max:
        await ctx.respond(
            embed=Embed(
                title="**ERROR** Unbounded range for work",
                description=f"Minimum generated value of {curr_min} is greater than the maximum generated value of"
                            f"{curr_max}. The maximum must be greater to or equal to the minimum.",
                color="0xff0000", timestamp=datetime.datetime.now(tz=datetime.timezone.utc)),
            flags=EPHEMERAL)
        await mydb.close()
        return
    embed = Embed(title=f"**New** Economy settings in {ctx.get_guild().name}", description=ECONOMYSETTINGS,
                  timestamp=datetime.datetime.now(tz=datetime.timezone.utc), color="0x00ff00")
    if minimum:
        await mydb.execute(
            "UPDATE guild_feature_work set min_gain = $1 WHERE guild_id = $2", minimum, ctx.guild_id)
    embed.add_field(f"{'**NEW**' if minimum else ''} Minimum Gain",
                    f"{minimum if minimum else result['min_gain']} {symbol if symbol else result['coin_symbol']}",
                    inline=True)
    if maximum != 1:
        await mydb.execute("UPDATE guild_feature_work set max_gain = $1 WHERE guild_id = $2", maximum, ctx.guild_id)
    embed.add_field(f"{'**NEW**' if maximum != 1 else ''} Maximum Gain",
                    f"{maximum if maximum != 1 else result['max_gain']} {symbol if symbol else result['coin_symbol']}",
                    inline=True)
    if step != 1:
        await mydb.execute("UPDATE guild_feature_work set gain_step = $1 WHERE guild_id = $2", step, ctx.guild_id)
    embed.add_field(f"{'**NEW**' if step != 1 else ''} Step",
                    f"{step if step != 1 else result['gain_step']} {symbol if symbol else result['coin_symbol']}",
                    inline=True)
    if cooldown != 3599:
        await mydb.execute(
            "UPDATE guild_feature_work set gain_cooldown = $1 WHERE guild_id = $2", cooldown, ctx.guild_id)
    try:
        embed.add_field(
            f"{'**NEW**' if cooldown != 3599 else ''} Gain Cooldown",
            f"{cooldown if cooldown != 3599 else result['gain_cooldown']} Seconds ("
            f"{(cooldown if cooldown != 3599 else result['gain_cooldown']) / 3600} Hours)",
            inline=True)
    except:  # pylint: disable=bare-except
        embed.add_field(f"{'**NEW**' if cooldown != 3599 else ''} Gain Cooldown",
                        f"{cooldown if cooldown != 3599 else result['gain_cooldown']} Seconds", inline=True)
    if name and name != 'default':
        await mydb.execute("UPDATE guild_feature_work set coin_name = $1 WHERE guild_id = $2", name, ctx.guild_id)
    if name and name != 'default':
        await mydb.execute("UPDATE guild_feature_work set coin_name = $1 WHERE guild_id = $2", name, ctx.guild_id)
    embed.add_field(f"{'**NEW**' if name else ''} Coin Name",
                    name if name and name != "default" else DEFAULTNAME if name == 'default' else result['coin_name'],
                    inline=True)
    if symbol and symbol != 'default':
        await mydb.execute("UPDATE guild_feature_work set coin_symbol = $1 WHERE guild_id = $2", symbol, ctx.guild_id)
    embed.add_field(f"{'**NEW**' if symbol else ''} Coin Symbol",
                    symbol if symbol and symbol != 'default' else DEFAULTSYMBOL if symbol == 'default' else result[
                        'coin_symbol'], inline=True)
    if starting_bal != 1:
        await mydb.execute(
            "UPDATE guild_feature_work set starting_bal = $1 WHERE guild_id = $2", starting_bal, ctx.guild_id)
    embed.add_field(
        f"{'**NEW**' if starting_bal != 1 else ''} Starting Balance",
        f"{starting_bal if starting_bal != 1 else int(result['starting_bal'])}"
        f"{symbol if symbol else result['coin_symbol']}",
        inline=True)
    await ctx.respond(embed=embed, flags=EPHEMERAL)
    await mydb.close()


@Economy.command()
@lightbulb.add_checks(check_author_work_allowed)
@lightbulb.command("work", "work command", auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def work(ctx: lightbulb.Context):  # pylint: disable=too-many-locals
    """Work Command"""
    mydb = await get_db()
    if await mydb.fetchrow("SELECT * FROM users WHERE id = $1", ctx.member.id) is None:
        await mydb.execute("INSERT INTO users (id) VALUES ($1)", ctx.member.id)
    if await mydb.fetchrow("SELECT * FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2", ctx.member.id,
                           ctx.guild_id) is None:
        temp = await mydb.fetchrow("SELECT starting_bal FROM guild_feature_work WHERE guild_id = $1", ctx.guild_id)
        await mydb.execute(
            "INSERT INTO user_guild_balance (user_id,guild_id,balance,next_work_amount) VALUES ($1,$2,$3,$4)",
            ctx.member.id, ctx.guild_id, int(temp[0]), 0)
        del temp
    workinfo = await mydb.fetchrow(
        "SELECT balance,next_work_amount,last_gain_time FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2",
        ctx.member.id, ctx.guild_id)
    user_guild_balance = float(workinfo[0])
    lastamount = int(workinfo[1])
    last_work: typing.Union[datetime.datetime, None] = workinfo[2]
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    current_use = datetime.datetime.now(tz=timezone('US/Eastern'))
    guild_info = await mydb.fetchrow(
        "SELECT min_gain,max_gain,gain_step,gain_cooldown,coin_symbol FROM guild_feature_work WHERE guild_id = $1",
        ctx.guild_id)
    seconds = int(guild_info[3])
    min_gain = int(guild_info[0])
    max_gain = int(guild_info[1])
    step = int(guild_info[2])
    symbol = guild_info[4]
    time_difference = (current_use - last_work.astimezone(
        timezone('US/Eastern'))) if last_work is not None else datetime.timedelta(seconds=seconds)
    if time_difference < datetime.timedelta(seconds=seconds):
        last_work: datetime.datetime
        time_pre_tuple = last_work.astimezone(tz=timezone('US/Eastern')) + datetime.timedelta(seconds=seconds)
        await ctx.respond(
            f"🚫 Error: **{ctx.author.mention}** come back <t:"
            f"{round(time.mktime(time_pre_tuple.timetuple()))}:R> to use this command.",
            flags=EPHEMERAL)
    elif time_difference >= datetime.timedelta(seconds=seconds):
        amount = random.randrange(min_gain, max_gain + 1,
                                  step)
        user_guild_balance += lastamount
        await mydb.execute(
            "UPDATE user_guild_balance SET balance = $1,next_work_amount = $2,last_gain_time = $3 WHERE user_id = $4 "
            "AND guild_id = $5",
            Decimal(user_guild_balance), amount, current_use, ctx.member.id, ctx.guild_id)
        if last_work is not None:
            embed = Embed(
                description=f"{ctx.author.mention}, you started working again. You gain  {str(lastamount)} {symbol}"
                            f"from your last work. Come back in **{int(ceil(seconds / 3600))} hours** to claim your"
                            f" paycheck of {str(amount)} {symbol} and start working again with `/work`",
                color="60D1F6")
        else:
            embed = Embed(
                description=f"{ctx.author.mention}, you started working. Come back in **{int(ceil(seconds / 3600))}"
                            f" hours** to claim your paycheck of {str(amount)} {symbol} and start working again with "
                            f"`/work`",
                color="60D1F6")
        await ctx.respond(embed=embed, flags=EPHEMERAL)
        await mydb.close()


@Economy.command()
@lightbulb.add_checks(check_author_work_allowed)
@lightbulb.command("balance", "checks your balance", auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def balance(ctx: lightbulb.Context):
    """Command to check balance"""
    mydb = await get_db()
    user_guild_balance = (await mydb.fetchrow(
        "SELECT balance FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2",
        ctx.member.id, ctx.guild_id))[0]
    symbol = (await mydb.fetchrow("SELECT coin_symbol FROM guild_feature_work WHERE guild_id = $1", ctx.guild_id))[0]
    await ctx.respond(
        embed=Embed(description=f"{ctx.member.display_name}, your current balance is {user_guild_balance} {symbol}",
                    color="60D1F6"), flags=EPHEMERAL)
    await mydb.close()


def load(bot: lightbulb.BotApp):
    """Loads Module"""
    bot.add_plugin(Economy)


def unload(bot):
    """Unloads Module"""
    bot.remove_plugin(Economy)
