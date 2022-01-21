import asyncio
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
from lightbulb.checks import guild_only, has_roles
from numpy import ceil
from pytz import timezone
import yahoo_finance_async as yf

EPHEMERAL:Final[int] = 64
MODVADMIN:Final[str] = "A  role marked as mod is ignored by autopunishments. A role marked as admin can edit the bot's settings along with the benefits of being a mod."
DISABLER:Final[str] = "A role marked as disabling will mean that a user with this role cannot use this portion of the bot, even if they have another role that would allow it. A role marked as enabling will allow a user to use this portion of the bot, as long as they don't have any role listed under disabling. Users listed with a mod role are not immune to disabling roles, but Users with an admin role are. If the everyone role is set as an enabling role, all users without a disabling role can use the bot (not recommended on servers that already have a levelling system). If the everyone role is set as a disabling role, the system will be disabled completely."
ECONOMYSETTINGS:Final[str] = "Minimum Gain, Maximum Gain, and Step dictate how random numbers are generated for the /work system - a number between the minimum and maximum, both inclusive with steps of size step from the minimum. i.e., for a (min,max,step) of (800,1200,5), which are the default settings, the random number possibilities would be (800,805,810,815,...,1190,1195,1200). Gain cooldown is the number of seconds between work uses for a user, default 11.5 hours, it's recommended to set this slightly under the time you advertise. i.e., for a 12-hour cycle, it's suggested using a cycle of 11.5 hours so people don't have to be perfect. Coin name and symbol allow you to customize the name and symbol of the coin if you don't like the default name of EchoCoin with the symbol <:Echocoin:928020676751814656>. Default starting balance allows people to start investing without having to do a couple of work cycles first. The default is 10,000, but you can change this if you want. All currencies, regardless of name and symbol are always a 1:1 vs USD for simplicity."
MODERATIONSETTINGS:Final[str] = "Nitro Scan and Crypto Scan respectively refer to whether the Nitro and Crypto Scam Detections are active. Mute Role is the role that the bot will assign if the bot believes that a message has a high probability of a scam but is not 100% sure. Main Log is where punishments are logged, and Message/Secondary log is for when there's a very log probability there's a scam. Its suggested to set the secondary/message logging to your message log channel if you have one, but it gets triggered very infrequently in most servers where it would be used."
DEFAULTNAME:Final[str]="EchoCoin";DEFAULTSYMBOL:Final[str]="<:Echocoin:928020676751814656>"
Economy = lightbulb.Plugin("Economy", default_enabled_guilds=225345178955808768)

async def get_db() -> asyncpg.Connection:
    with open('sqlinfo.json') as t:
        sqlinfo = json.load(t)
    return await asyncpg.connect(host=sqlinfo['host'],user=sqlinfo['user'],password=sqlinfo['password'],database=sqlinfo['database'])

@lightbulb.Check
async def check_author_work_allowed(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result=await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids;possible = False
    for x in result:
        if context.guild_id == x[1] and bool(x['disabling']):await mydb.close();return False
        elif context.guild_id == x[1] and not bool(x['disabling']):possible = True
        elif x[1] in roles and bool(x['disabling']):await mydb.close();return False
        elif x[1] in roles and not bool(x['disabling']):possible = True
    await mydb.close()
    return possible

@lightbulb.Check
async def check_author_is_admin(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids
    for x in result:
        if x[1] in roles and x[2] > 0:return True
    await mydb.close()
    return False

@lightbulb.Check
async def check_author_is_mod(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids
    for x in result:
        if x[1] in roles:return True
    await mydb.close()
    return False

@Economy.command()
@lightbulb.add_checks(check_author_is_admin,guild_only)
@lightbulb.command("config", "configuration group")
@lightbulb.implements(commands.SlashCommandGroup)
async def config(ctx: lightbulb.Context) -> None:await ctx.respond("invoked config")

@config.child
@lightbulb.command("roles", "config role group", inherit_checks=True)
@lightbulb.implements(commands.SlashSubGroup)
async def roles(ctx: lightbulb.Context) -> None:await ctx.respond("invoked config mods")

@config.child
@lightbulb.option("group", "settings group to query",type=int, choices = [CommandChoice(name="Work Roles",value=1),CommandChoice(name="Work settings",value=2)])
@lightbulb.command("query","querys guild settings for the bot",inherit_checks=True, auto_defer = True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_mods_query(ctx: lightbulb.Context):
    mydb = await get_db()
    queryier = ctx.options.group
    if queryier==1:
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
        embed = Embed(title="Work Enabler and Disabler roles in the bot",description=DISABLER,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x0000ff")
        for x in result:embed.add_field("Disabling Role" if x['disabling'] else "Enabling Role",f"<@&{x['role_id']}>",inline=True)
    elif queryier==2:
        result = await mydb.fetchrow("SELECT * FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id)
        embed = Embed(title=f"Economy settings in {ctx.get_guild().name}",description=ECONOMYSETTINGS,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x0000ff").add_field("Minimum Gain", f"{result['min_gain']} {result['coin_symbol']}",inline=True).add_field("Maximum Gain", f"{result['max_gain']} {result['coin_symbol']}",inline=True).add_field("Step", f"{result['gain_step']} {result['coin_symbol']}",inline=True).add_field("Gain Cooldown",f"{result['gain_cooldown']} Seconds ({result['gain_cooldown']/3600} Hours)",inline=True).add_field("Coin Name",result['coin_name'],inline=True).add_field("Coin Symbol",result['coin_symbol'],inline=True).add_field("Starting Balance",f"{int(result['starting_bal'])} {result['coin_symbol']}",inline=True)
    else:return
    await ctx.respond(embed=embed,flags=EPHEMERAL)
    await mydb.close()


@roles.child
@lightbulb.option("disabling", "should the role be disabling", type=bool, required=True)
@lightbulb.option("add","True to add or edit, False to remove", type=bool, required=True)
@lightbulb.option("role","role to add/edit/remove from work list", type=hikari.Role, required=True)
@lightbulb.command("work","adds, edits, or removes a role from consideration as a work role", inherit_checks=True, auto_defer = True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_roles_work(ctx: lightbulb.Context):
    mydb = await get_db()
    role:Final[hikari.Role] = ctx.options.role;add:Final[bool]=ctx.options.add;disabling:Final[bool]=ctx.options.disabling;new=True
    result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
    for x in result:
        if int(role.id) == int(x[1]):new=False
    if add and not new:
        await mydb.execute("UPDATE guild_feature_work_roles set disabling = $1 WHERE guild_id = $2 and role_id = $3", disabling,ctx.guild_id,role.id)
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
    elif add and new:
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
        await mydb.execute("INSERT INTO guild_feature_work_roles (guild_id, role_id, disabling) VALUES ($1,$2, $3)", ctx.guild_id,role.id,disabling)
    else:
        await mydb.execute("DELETE FROM guild_feature_work_roles WHERE role_id = $1", role.id)
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
    embed = Embed(title="New List of enabling and disabling roles",description=MODVADMIN,color = "0x00ff00" if add and new else "0x0000ff" if add and not new else "0xff0000",timestamp=datetime.datetime.now(tz=datetime.timezone.utc))
    if add and new:embed.add_field("**NEW** Disabling Role" if bool(disabling) else "**NEW** Enabling Role",f"<@&{role.id}>",inline=True)
    elif add and not new: embed.add_field("**CHANGED TO** Disabling Role" if bool(disabling) else "**CHANGED TO** Enabling Role",f"<@&{role.id}>",inline=True)
    for x in result:
        if int(x[1])==int(role.id):continue
        embed.add_field("Disabling Role" if x['disabling'] else "Enabling Role",f"<@&{x['role_id']}>",inline=True)
    await ctx.respond(embed=embed,flags=EPHEMERAL)

@config.child
@lightbulb.option("starting_bal","balance to start all new users of the bot on the server with",type=int,default=1,min_value=1,required=False)
@lightbulb.option("symbol","default to reset, send one emoji to use a custom one, bot must be in emote's server if server emote",type=str, default="",required=False)
@lightbulb.option("name","custom name for the coin, put 'default' (without the quotes) to reset to the default name",type=str, default="",required=False)
@lightbulb.option("cooldown","cooldown between allowed uses of /work by a single user, in seconds. i.e. 3600 is one hour",type=int,default = 3599,min_value=3599,required=False)
@lightbulb.option("step","step between numbers possible to randomly generate",type=int,default = 1,min_value=1,max_value=100,required=False)
@lightbulb.option("maximum","maximum possible gain for a use of /work",type=int,default = 1,min_value=1,required=False)
@lightbulb.option("minimum","minimum possible gain for a use of /work",type=int,default = 0,min_value=0,required=False)
@lightbulb.command("work","edits guild settings for the work module. leave option default to leave unchanged", inherit_checks=True, auto_defer = True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_work(ctx: lightbulb.Context):
    if all(thing is None for thing in [ctx.options.minimum,ctx.options.maximum,ctx.options.step,ctx.options.cooldown,ctx.options.name,ctx.options.symbol,ctx.options.starting_bal]):
        await ctx.respond(embed=Embed(title="**ERROR** No Settings changed",description="If you want to check settings, see `/config query` and select the work settings",color="0xff0000",timestamp=datetime.datetime.now(tz=datetime.timezone.utc)),flags=EPHEMERAL)
        return
    minimum = ctx.options.minimum if ctx.options.minimum is not None else 0
    maximum = ctx.options.maximum if ctx.options.maximum is not None else 1
    step = ctx.options.step if ctx.options.step is not None else 1
    cooldown = ctx.options.cooldown if ctx.options.cooldown is not None else 3599
    name = ctx.options.name if ctx.options.name is not None else ""
    symbol = ctx.options.symbol if ctx.options.symbol is not None else ""
    starting_bal = ctx.options.starting_bal if ctx.options.starting_bal is not None else 1
    mydb = await get_db();result = await mydb.fetchrow("SELECT * FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id)
    curr_min = minimum if minimum else result['min_gain'];curr_max = maximum if maximum!=1 else result['max_gain']
    if curr_min > curr_max:
        await ctx.respond(embed=Embed(title="**ERROR** Unbounded range for work",description=f"Minimum generated value of {curr_min} is greater than the maximum generated value of {curr_max}. The maximum must be greater to or equal to the minimum.",color="0xff0000",timestamp=datetime.datetime.now(tz=datetime.timezone.utc)),flags=EPHEMERAL)
        await mydb.close()
        return
    embed = Embed(title=f"**New** Economy settings in {ctx.get_guild().name}",description=ECONOMYSETTINGS,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x00ff00")
    if minimum: await mydb.execute("UPDATE guild_feature_work set min_gain = $1 WHERE guild_id = $2",minimum,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if minimum else ''} Minimum Gain", f"{minimum if minimum else result['min_gain']} {symbol if symbol else result['coin_symbol']}",inline=True)
    if maximum != 1:await mydb.execute("UPDATE guild_feature_work set max_gain = $1 WHERE guild_id = $2",maximum,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if maximum !=1 else ''} Maximum Gain", f"{maximum if maximum !=1 else result['max_gain']} {symbol if symbol else result['coin_symbol']}",inline=True)
    if step !=1: await mydb.execute("UPDATE guild_feature_work set gain_step = $1 WHERE guild_id = $2",step,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if step !=1 else ''} Step", f"{step if step !=1 else result['gain_step']} {symbol if symbol else result['coin_symbol']}",inline=True)
    if cooldown != 3599:await mydb.execute("UPDATE guild_feature_work set gain_cooldown = $1 WHERE guild_id = $2",cooldown,ctx.guild_id)
    try:embed.add_field(f"{'**NEW**' if cooldown != 3599 else ''} Gain Cooldown",f"{cooldown if cooldown != 3599 else result['gain_cooldown']} Seconds ({(cooldown if cooldown != 3599 else result['gain_cooldown'])/3600} Hours)",inline=True)
    except:embed.add_field(f"{'**NEW**' if cooldown != 3599 else ''} Gain Cooldown",f"{cooldown if cooldown != 3599 else result['gain_cooldown']} Seconds",inline=True)
    if name and name !='default':await mydb.execute("UPDATE guild_feature_work set coin_name = $1 WHERE guild_id = $2",name,ctx.guild_id)
    if name and name !='default':await mydb.execute("UPDATE guild_feature_work set coin_name = $1 WHERE guild_id = $2",name,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if name else ''} Coin Name",name if name and name!="default" else DEFAULTNAME if name=='default' else result['coin_name'],inline=True)
    if symbol and symbol !='default':await mydb.execute("UPDATE guild_feature_work set coin_symbol = $1 WHERE guild_id = $2",symbol,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if symbol else ''} Coin Symbol",symbol if symbol and symbol !='default' else DEFAULTSYMBOL if symbol=='default' else result['coin_symbol'],inline=True)
    if starting_bal !=1:await mydb.execute("UPDATE guild_feature_work set starting_bal = $1 WHERE guild_id = $2",starting_bal,ctx.guild_id)
    embed.add_field(f"{'**NEW**' if starting_bal !=1 else ''} Starting Balance",f"{starting_bal if starting_bal !=1 else int(result['starting_bal'])} {symbol if symbol else result['coin_symbol']}",inline=True)
    await ctx.respond(embed=embed, flags=EPHEMERAL)
    await mydb.close()


@Economy.command()
@lightbulb.add_checks(check_author_work_allowed)
@lightbulb.command("work", "work command",auto_defer = True,ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def work(ctx:lightbulb.Context):
    mydb = await get_db()
    if await mydb.fetchrow("SELECT * FROM users WHERE id = $1",ctx.member.id) is None:
        await mydb.execute("INSERT INTO users (id) VALUES ($1)",ctx.member.id)
    if await mydb.fetchrow("SELECT * FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2",ctx.member.id,ctx.guild_id) is None:
        temp = await mydb.fetchrow("SELECT starting_bal FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id)
        await mydb.execute("INSERT INTO user_guild_balance (user_id,guild_id,balance,next_work_amount) VALUES ($1,$2,$3,$4)",ctx.member.id,ctx.guild_id,int(temp[0]),0)
        del temp
    workinfo = await mydb.fetchrow("SELECT balance,next_work_amount,last_gain_time FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2",ctx.member.id,ctx.guild_id)
    balance = float(workinfo[0]);lastamount = int(workinfo[1]);lastWork:typing.Union[datetime.datetime,None] = workinfo[2]
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    currentUse = datetime.datetime.now(tz=timezone('US/Eastern'))
    guild_info = await mydb.fetchrow("SELECT min_gain,max_gain,gain_step,gain_cooldown,coin_symbol FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id)
    seconds = int(guild_info[3]);min_gain=int(guild_info[0]);max_gain = int(guild_info[1]);step = int(guild_info[2]);symbol = guild_info[4]
    timeDifference = (currentUse - lastWork.astimezone(timezone('US/Eastern'))) if lastWork is not None else datetime.timedelta(seconds=seconds)
    if timeDifference < datetime.timedelta(seconds=seconds):
        lastWork:datetime.datetime
        await ctx.respond(f"🚫 Error: **{ctx.author.mention}** come back <t:{round(time.mktime((lastWork.astimezone(tz=timezone('US/Eastern')) + datetime.timedelta(seconds=seconds)).timetuple()))}:R> to use this command.",flags=EPHEMERAL)
    elif timeDifference >= datetime.timedelta(seconds=seconds):
        amount = random.randrange(min_gain, max_gain+1, step) #generates random number from min to max inclusive, in incrememnts of step, the +1 to make it inclusive
        balance += lastamount
        await mydb.execute("UPDATE user_guild_balance SET balance = $1,next_work_amount = $2,last_gain_time = $3 WHERE user_id = $4 AND guild_id = $5",Decimal(balance),amount,currentUse,ctx.member.id,ctx.guild_id)
        if lastWork is not None:embed = Embed(description= f"{ctx.author.mention}, you started working again. You gain  {str(lastamount)} {symbol} from your last work. Come back in **{int(ceil(seconds/3600))} hours** to claim your paycheck of {str(amount)} {symbol} and start working again with `/work`", color="60D1F6")
        else: embed = Embed(description= f"{ctx.author.mention}, you started working. Come back in **{int(ceil(seconds/3600))} hours** to claim your paycheck of {str(amount)} {symbol} and start working again with `/work`", color="60D1F6")
        await ctx.respond(embed=embed,flags=EPHEMERAL)
        await mydb.close()

@Economy.command()
@lightbulb.add_checks(check_author_work_allowed)
@lightbulb.command("balance", "checks your balance",auto_defer = True,ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def balance(ctx:lightbulb.Context):
    mydb = await get_db()
    balance = (await mydb.fetchrow("SELECT balance FROM user_guild_balance WHERE user_id = $1 AND guild_id = $2",ctx.member.id,ctx.guild_id))[0]
    symbol = (await mydb.fetchrow("SELECT coin_symbol FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id))[0]
    await ctx.respond(embed=Embed(description=f"{ctx.member.display_name}, your current balance is {balance} {symbol}", color="60D1F6"),flags=EPHEMERAL)
    await mydb.close()
"""
@Economy.command()
@lightbulb.add_checks(check_author_work_allowed)
@lightbulb.option("comments","any comments on the stock and why you want it added, if you want to explain",required=False,default="None")
@lightbulb.option("stock","symbol for stock/crypto. if a crypto, it should be like `BTC-USD`")
@lightbulb.command("request", "requests a new stock to be tracked and included in the simulation",auto_defer = True,ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def balance(ctx:lightbulb.Context):
    try: await yf.OHLC.fetch(ctx.options.stock.upper())
    except:
        await ctx.respond("🚫 Error: Stock Not Found. Check Spelling.")
        return
    mydb = await get_db()
    accepted = await mydb.fetch("SELECT symbol FROM stocks");accepted = [item[0] for item in accepted]
    if ctx.options.stock.upper() in accepted:
        await ctx.respond("🚫 Error: Stock Already Available.")
        return
    pending = await mydb.fetch("SELECT symbol FROM requested_stocks");pending = [item[0] for item in pending]
    if ctx.options.stock.upper() in pending:
        await ctx.respond("🚫 Error: Stock Already Requested, please be patient until Bluesy#8150 has time to review open requests. He has been renotified of this request.")
        me = await Economy.bot.rest.fetch_user(363095569515806722)
        stock_request = await mydb.fetchrow("SELECT * FROM requested_stocks WHERE symbol = $1",ctx.options.stock.upper())
        requester = await Economy.bot.rest.fetch_user(stock_request['requester'])
        await me.send(embed=Embed(title="Reminder of stock request",description=f"""#Old Comments: {stock_request['comments']}
        #New Comments: {ctx.options.comments}""").add_field("Requested Stock",ctx.options.stock.upper(),inline=True).add_field("id",stock_request['id'],inline=True).add_field("initial requester",f"{requester.username}#{requester.discriminator}",inline=True).add_field("this requester",f"{ctx.author.username}#{ctx.author.discriminator}",inline=True).add_field("comments",stock_request['id'],inline=True))
        #return

def load(bot:lightbulb.BotApp):
    bot.add_plugin(Economy)

def unload(bot):
    bot.remove_plugin(Economy)
