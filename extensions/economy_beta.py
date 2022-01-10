import datetime
import json
import time
from typing import Final

import hikari
from hikari import Embed
from hikari import permissions
from hikari.commands import CommandChoice
import lightbulb
from lightbulb import commands
import random
from lightbulb.checks import (has_roles,guild_only)
import asyncpg
import asyncio

EPHEMERAL:Final[int] = 64
MODVADMIN:Final[str] = "A role marked as mod is simply ignored by any autopunishments enabled in this bot on the server. A role marked as admin has the ability to edit the bot's settings on the server, as well as the benefits of being marked as a mod."
DISABLER:Final[str] = "A role marked as disabling will mean that a user with this role cannot use this portion of the bot, even if they have another role that would allow it. A role marked as enabling will allow a user to use this portion of the bot, as long as they don't have any role listed under disabling. Users listed with a mod role are not immune to disabling roles, but Users with an admin role are. If the everyone role is set as an enabling role, all users without a disabling role can use the bot (not recommended on servers that already have a leveling system). If the everyone role is set as a disabling role, the system will be disabled completely."
ECONOMYSETTINGS:Final[str] = "Minimum Gain, Maximum Gain, and Step dictate how random numbers are generated for the /work system - a number between the minimum and maximum, both inclusive with steps of size step from the minimum. i.e., for a (min,max,step) of (800,1200,5), which are the default settings, the random number possibilities would be (800,805,810,815,...,1190,1195,1200). Gain cooldown is the number of seconds between work uses for a user, default 11.5 hours, it's recommended to set this slightly under the time you advertise. i.e., for a 12-hour cycle, it's suggested using a cycle of 11.5 hours so people don't have to be perfect. Coin name and symbol allow you to customize the name and symbol of the coin if you don't like the default name of EchoCoin with the symbol <:Echocoin:928020676751814656>. Default starting balance allows people to start investing without having to do a couple of work cycles first. The default is 10,000, but you can change this if you want. All currencies, regardless of name and symbol are always a 1:1 vs USD for simplicity."
Economy = lightbulb.Plugin("Economy", default_enabled_guilds=225345178955808768)

#loop = asyncio.get_event_loop()

async def get_db() -> asyncpg.Connection:
    with open('sqlinfo.json') as t:
        sqlinfo = json.load(t)
    return await asyncpg.connect(host=sqlinfo['host'],user=sqlinfo['user'],password=sqlinfo['password'],database=sqlinfo['database'])


#loop.run_until_complete(init())



@lightbulb.Check
async def check_author_work_allowed(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result=await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids;possible = False
    for x in result:
        if context.guild_id in x and bool(x['disabling']):return False
        elif context.guild_id in x and not bool(x['disabling']):return True
        elif x[1] in roles and x[2] > 0:return False
        elif x[1] in roles and x[2] == 0: possible = True
    return possible

@lightbulb.Check
async def check_author_is_admin(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids
    for x in result:
        if x[1] in roles and x[2] > 0:return True
    return False

@lightbulb.Check
async def check_author_is_mod(context: lightbulb.Context) -> bool:
    mydb = await get_db()
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",context.guild_id)
    roles = context.member.role_ids
    for x in result:
        if x[1] in roles:return True
    return False

@Economy.listener(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent):
    mydb = await get_db()
    result = await mydb.fetch("SELECT id FROM guilds")
    for x in result:
        if event.guild_id in x:return
    id = event.guild.id
    roles = event.guild.get_roles()
    muted_role = 0
    for roleid in roles:
        if 'mute' in roles[roleid].name.lower():muted_role = int(roleid);break
    await mydb.execute("INSERT INTO guilds (id, nitro_enabled, crypto_enabled, mute_role) VALUES ($1, $2, $3, $4)", id, False, False, muted_role)
    admins = list(); workers = list()
    for roleid in roles:
        role = roles[roleid]
        if role.permissions.any(permissions.Permissions.ADMINISTRATOR):admins.append(tuple((event.guild_id,roleid,1)));workers.append(tuple((event.guild_id,roleid,0)))
        elif role.permissions.any(permissions.Permissions.MANAGE_CHANNELS,permissions.Permissions.MANAGE_EMOJIS_AND_STICKERS,permissions.Permissions.MANAGE_GUILD,permissions.Permissions.MANAGE_MESSAGES,permissions.Permissions.MANAGE_NICKNAMES,permissions.Permissions.MANAGE_ROLES,permissions.Permissions.MANAGE_THREADS,permissions.Permissions.MANAGE_WEBHOOKS,permissions.Permissions.MODERATE_MEMBERS):admins.append(tuple((event.guild_id,roleid,0)));workers.append(tuple((event.guild_id,roleid,0)))
    await mydb.executemany("INSERT INTO guild_mod_roles (guild_id, role_id) VALUES ($1, $2)", admins)
    await mydb.executemany("INSERT INTO guild_feature_work_roles (guild_id, role_id, disabling) VALUES ($1, $2s, $3)", workers)
    await mydb.execute("INSERT INTO guild_feature_work guild_id VALUES $1",int(event.guild_id))
    
    

@Economy.command()
@lightbulb.add_checks(check_author_is_admin,guild_only)
@lightbulb.command("config", "configuration group")
@lightbulb.implements(commands.SlashCommandGroup)
async def config(ctx: lightbulb.Context) -> None:await ctx.respond("invoked config")

@config.child
@lightbulb.command("mods", "mod/admin role config group", inherit_checks=True)
@lightbulb.implements(commands.SlashSubGroup)
async def mods(ctx: lightbulb.Context) -> None:await ctx.respond("invoked config mods")

@config.child
@lightbulb.option("group", "settings group to query",type=int, choices = [CommandChoice(name="Mod Roles",value=1),CommandChoice(name="Work Roles",value=2),CommandChoice(name="Work settings",value=3)])
@lightbulb.command("query","querys guild settings for the bot",inherit_checks=True, auto_defer = True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_mods_query(ctx: lightbulb.Context):
    mydb = await get_db()
    queryier = ctx.options.group
    if queryier==1:
        result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",ctx.guild_id)
        embed = Embed(title="Moderator and Admin Roles registered in the bot",description=MODVADMIN,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x0000ff")
        for x in result:
            embed.add_field(f"<@&{x[1]}>","Admin" if x[2] else "Mod", inline=True)
    elif queryier==2:
        result = await mydb.fetch("SELECT * FROM guild_feature_work_roles WHERE guild_id = $1",ctx.guild_id)
        embed = Embed(title="Work Enabler and Disabler roles in the bot",description=DISABLER,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x0000ff")
        for x in result:
            embed.add_field(f"<@&{x['role_id']}>","Disabling Role" if x['disabling'] else "Enabling Role", inline=True)
    elif queryier==3:
        result = await mydb.fetchrow("SELECT * FROM guild_feature_work WHERE guild_id = $1",ctx.guild_id)
        embed = Embed(title="Economy settings in the bot",description=ECONOMYSETTINGS,timestamp=datetime.datetime.now(tz=datetime.timezone.utc),color="0x0000ff").add_field("Minimum Gain", f"{result['min_gain']} {result['coin_symbol']}",inline=True).add_field("Maximum Gain", f"{result['max_gain']} {result['coin_symbol']}",inline=True).add_field("Step", f"{result['gain_step']} {result['coin_symbol']}",inline=True).add_field("Gain Cooldown",f"{result['gain_cooldown']} Seconds ({result['gain_cooldown']/3600} Hours)",inline=True).add_field("Coin Name",result['coin_name'],inline=True).add_field("Coin Symbol",result['coin_symbol'],inline=True).add_field("Starting Balance",f"{int(result['starting_bal'])} {result['coin_symbol']}",inline=True)
    else:return
    await ctx.respond(embed=embed,flags=EPHEMERAL)

@mods.child
@lightbulb.option("admin", "should the role have administrative permissions in the bot", type=bool, required=True)
@lightbulb.option("add","True to add or edit, False to remove", type=bool, required=True)
@lightbulb.option("role","role to add/remove from mod list", type=hikari.Role, required=True)
@lightbulb.command("set","adds, edits, or removes a role from consideration as a mod or admin", inherit_checks=True, auto_defer = True)
@lightbulb.implements(commands.SlashSubCommand)
async def config_mods_set(ctx: lightbulb.Context):
    mydb = await get_db()
    role:Final[hikari.Role] = ctx.options.role;add:Final[bool]=ctx.options.add;admin:Final[bool]=ctx.options.admin;new=True
    result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",ctx.guild_id)
    for x in result:
        if role.id in x:new=False
    if add and not new:
        await mydb.execute("UPDATE guild_mod_roles set is_admin = $1 WHERE guild_id = $2 and role_id = $3", admin,ctx.guild_id,role.id)
        result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",ctx.guild_id)
    elif add and new:
        result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",ctx.guild_id)
        await mydb.execute("INSERT INTO guild_mod_roles (guild_id, role_id, is_admin) VALUES ($1,$2, $3)", ctx.guild_id,role.id,admin)
    else:
        await mydb.execute("DELETE FROM guild_mod_roles WHERE role_id = $1", role.id)
        result = await mydb.fetch("SELECT * FROM guild_mod_roles WHERE guild_id = $1",ctx.guild_id)
    embed = Embed(title="New List of Moderator and Admin Roles",description=MODVADMIN,color = "0x00ff00" if add and new else "0x0000ff" if add and not new else "0xff0000",timestamp=datetime.datetime.now(tz=datetime.timezone.utc))
    if add and new:embed.add_field(f"<@&{role.id}>","**NEW** Admin" if bool(admin) else "**NEW** Mod",inline=True)
    elif add and not new: embed.add_field(f"<@&{role.id}>","**CHANGED TO** Admin" if bool(admin) else "**CHANGED TO** Mod",inline=True)
    for x in result:
        if int(x[1])==int(role.id):continue
        embed.add_field(f"<@&{x[1]}>","Admin" if x['is_admin'] else "Mod", inline=True)
    await ctx.respond(embed=embed,flags=EPHEMERAL)



"""@Generating_Plugin.command()
@lightbulb.add_checks(lightbulb.Check(has_roles(837812373451702303,837812586997219372,837812662116417566,837812728801525781,837812793914425455,400445639210827786,685331877057658888,337743478190637077,837813262417788988,338173415527677954,253752685357039617,mode=any)),lightbulb.Check(a.checks.check_econ_channel),lightbulb.Check(a.checks.Punished))
@lightbulb.add_cooldown(3600,5,lightbulb.UserBucket)
@lightbulb.command("work", "work command")
@lightbulb.implements(commands.SlashCommand)
async def work(ctx):
    if str(ctx.author.id) not in list(a.userInfo.readUserInfo().index): #makes sure user isn't already in an RPO
        a.undeclared(ctx)
    df = a.userInfo.readUserInfo()
    lastWork = df.loc[str(ctx.author.id), 'lastWork']
    currentUse = round(time.time(),0)
    timeDifference = currentUse - lastWork
    if timeDifference < 41400:
        await ctx.respond("🚫 Error: **" + ctx.author.mention + "** You need to wait " + str(datetime.timedelta(seconds=41400-timeDifference)) + " more to use this command.")
    elif timeDifference > 41400:
        df.loc[str(ctx.author.id), 'lastWork'] = currentUse
        amount = random.randrange(800, 1200, 5) #generates random number from 800 to 1200, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
        lastamount = int(df.loc[str(ctx.author.id), 'lastWorkAmount'])
        df.loc[str(ctx.author.id), 'lastWorkAmount'] = amount
        a.userInfo.writeUserInfo(df)
        a.userInfo.editCoins(ctx.author.id,lastamount)
        df.loc[str(ctx.author.id), 'lastWorkAmount'] = amount
        embed = Embed(description= ctx.author.mention + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `!work`', color="60D1F6").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url)
        await ctx.respond(embed=embed)"""

def load(bot:lightbulb.BotApp):
    bot.add_plugin(Economy)

def unload(bot):
    bot.remove_plugin(Economy)