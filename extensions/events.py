import datetime
import random
import re
import time
from hikari import embeds
from hikari.messages import ButtonStyle
from lightbulb import utils

from lightbulb.utils.nav import ComponentButton

import auxone as a
import hikari
import lightbulb
from auxone import userInfo as user
from hikari import Embed
from lightbulb import commands
from lightbulb.checks import has_roles

def find_embedded_urls(data):
    regex = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    return re.finditer(regex,data,flags=re.M|re.I)

def find_embedded_phones(data):
    regex = r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]+(\d{3})[-. ]+(\d{4})(?: *x(\d+))?\s*$"
    return re.finditer(regex,data,flags=re.M|re.I)

EventsPlugin = lightbulb.Plugin("EventsPlugin")

@EventsPlugin.listener(hikari.DMMessageCreateEvent)
async def on_DMmessage(event):
    if event.is_human:
        if event.content is not None:
            if str(event.message.content).startswith("!"):
                await event.author.send("Commands do not work in dms.")
                return
            ticket = a.add_onmessage(event.message)
            if ticket == None:
                return
            else:
                channel = await EventsPlugin.bot.rest.fetch_channel(906578081496584242)
                #channel = guild.get_channel(906578081496584242)
                await channel.send("Message from "+str(event.message.author.username)+" "+str(event.message.author.id)+", Ticket: `"+str(ticket[0])+"`):")
                if ticket[1] == "new":
                    await event.author.send("Remember to check our FAQ to see if your question/issue is addressed there: https://cpry.net/discordfaq")
                message= await channel.send('message: '+event.message.content)
                await message.edit(attachments=event.message.attachments)

@EventsPlugin.listener(hikari.GuildMessageCreateEvent)
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is not None and event.is_human:
        nums = find_embedded_phones(event.content)
        nums = [match[0] for match in nums]
        has_nums = True if not nums else False
        has_whatsapp = "whatsapp" in event.content.lower()
        has_dollarsign = "$" in event.content
        allowed_roles = [225413350874546176,253752685357039617,725377514414932030,338173415527677954,387037912782471179,406690402956083210,729368484211064944]
        role_check = not any(role in event.member.role_ids for role in allowed_roles)
        if any([has_whatsapp,has_dollarsign,has_nums])and event.channel_id==926532222398369812:
            if all(has_whatsapp,has_dollarsign,has_nums):
                embed = Embed(title="Ban Level Event - WhatsApp Cryptoscam - all triggers hit:",description=event.content,color="0xff0000").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:","Triggered: Found Regex Match(s)" if has_nums else "No Regex Matches Present",inline=True).add_field("`$` Check:","Triggered: Found symbol" if has_dollarsign else "Symbol Not Present",inline=True).add_field("Role Check:","Triggered: No allowed roles" if role_check else "Allowed role present",inline=True).add_field("Result:","Ban" if role_check else "Log",inline=False).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id).add_field("CHannel:",event.get_channel().mention,inline=True)
                await event.message.respond(embed=embed)
                #await event.message.delete()
                #if role_check:await EventsPlugin.app.rest.ban_user(225345178955808768,event.member.id,delete_message_days=0,reason="CryptoScam")
            elif any([has_dollarsign and has_nums,has_nums and has_whatsapp, has_whatsapp and has_dollarsign]):
                embed = Embed(title="Mute Level Event - Possible WhatsApp Cryptoscam - 2/3 triggers hit:",description=event.content,color="0xff0000").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:","Triggered: Found Regex Match(s)" if has_nums else "No Regex Matches Present",inline=True).add_field("`$` Check:","Triggered: Found symbol" if has_dollarsign else "Symbol Not Present",inline=True).add_field("Role Check:","Triggered: No allowed roles" if role_check else "Allowed role present",inline=True).add_field("Result:","Mute" if role_check else "Log",inline=False).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id).add_field("CHannel:",event.get_channel().mention,inline=True)
                await event.message.respond(embed=embed)
                #await event.message.delete()
                #if role_check:await EventsPlugin.app.rest.add_role_to_member(225345178955808768,event.member.id,684936661745795088,reason="CryptoScam")
                #if role_check:await EventsPlugin.app.rest.add_role_to_member(225345178955808768,event.member.id,676250179929636886,reason="CryptoScam")
            elif any([has_nums,has_whatsapp]):
                embed = Embed(title="Log Level Event - Vauge Possibility of WhatsApp Cryptoscam - 1/3 triggers hit:",description=event.content,color="0x0000ff").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:","Triggered: Found Regex Match(s)" if has_nums else "No Regex Matches Present",inline=True).add_field("`$` Check:","Triggered: Found symbol" if has_dollarsign else "Symbol Not Present",inline=True).add_field("Role Check:","Triggered: No allowed roles" if role_check else "Allowed role present",inline=True).add_field("Result:","Mute" if role_check else "Log",inline=False).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id).add_field("CHannel:",event.get_channel().mention,inline=True)
                await event.message.respond(embed=embed)
        del nums;del has_nums;del has_dollarsign;del has_whatsapp;del role_check;del allowed_roles
        if not user.roleCheck(event.message.member, [338173415527677954,253752685357039617,225413350874546176,387037912782471179,406690402956083210,729368484211064944]):
            if "<@&225345178955808768>" in event.content or "@everyone" in event.content or "@here" in event.content:
                await event.message.member.add_role(676250179929636886)
                await event.message.member.add_role(684936661745795088)
                await event.message.delete()
                channel = await EventsPlugin.app.rest.fetch_channel(426016300439961601)
                embed = Embed(description=event.content, title="Mute: Everyone/Here Ping sent by non mod", color="0xff0000").set_footer(text=f"Sent by {event.message.member.display_name}-{event.message.member.id}",icon=event.message.member.avatar_url)
                await channel.send(embed=embed)
        if event.is_bot or not event.content:
            return
        elif re.search(r"bruh", event.content, re.MULTILINE|re.IGNORECASE):
            await event.message.delete()
        elif re.search(r"~~:.|:;~~", event.content, re.MULTILINE|re.IGNORECASE) or re.search(r"tilde tilde colon dot vertical bar colon semicolon tilde tilde", event.content, re.MULTILINE|re.IGNORECASE):
            await event.message.delete()
        elif event.message.content.startswith('daily') or event.message.content.startswith('Daily'):
            if event.author_id not in [82495450153750528,755539532924977262]:
                return
            elif event.channel_id not in [893867549589131314, 687817008355737606, 839690221083820032]:
                return
            await event.message.delete()
            if user.role_check(event.author, ['733541021488513035','225414319938994186','225414600101724170','225414953820094465','377254753907769355','338173415527677954','253752685357039617']):
                df = user.readUserInfo()
                lastWork = df.loc[str(event.author_id), 'lastDaily']
                currentUse = round(time.time(),0)%100
                timeDifference = currentUse - lastWork
                if timeDifference < 71700:
                    await event.author.send("<:KSplodes:896043440872235028> Error: **" + event.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=71700-timeDifference)) + " more to use this command.")
                elif timeDifference > 71700:
                    df.loc[str(event.author_id), 'lastDaily'] = currentUse
                    amount = 1500 #assigned number for daily
                    user.writeUserInfo(df)
                    user.editCoins(event.author_id,amount)
                    await event.author.send(embed=Embed(description= event.author.mention +', here is your daily reward: 1500 <:HotTips2:465535606739697664>', color="60D1F6").set_footer(text=f"Requested by {event.member.display_name}",icon=event.member.avatar_url))
            else:
                await event.author.send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")

        elif event.message.content.startswith('work') or event.message.content.startswith('Work'):
            if event.author_id not in [82495450153750528,755539532924977262]:
                return
            elif event.channel_id not in [893867549589131314, 687817008355737606, 839690221083820032]:
                return
            if a.role_check(event.author, ['837812373451702303','837812586997219372','837812662116417566','837812728801525781','837812793914425455','400445639210827786','685331877057658888','337743478190637077','837813262417788988','338173415527677954','253752685357039617']):
                await event.message.delete()
                df = user.readUserInfo()
                lastWork = df.loc[str(event.author_id), 'lastWork']
                currentUse = round(time.time(),0)%100
                timeDifference = currentUse - lastWork
                if timeDifference < 41400:
                    await event.get_channel().send("<:KSplodes:896043440872235028> Error: **" + event.author.mention + "** You need to wait " + str(datetime.timedelta(seconds=41400-timeDifference)) + " more to use this command.")
                elif timeDifference > 41400:
                    df.loc[str(event.author_id), 'lastWork'] = currentUse
                    amount = random.randrange(800, 1200, 5) #generates random number from 800 to 1200, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
                    lastamount = int(df.loc[str(event.author_id), 'lastWorkAmount'])
                    df.loc[str(event.author_id), 'lastWorkAmount'] = amount
                    user.writeUserInfo(df)
                    user.editCoins(event.author_id,lastamount)
                    df.loc[str(event.author_id), 'lastWorkAmount'] = amount
                    await event.get_channel().send(embed=Embed(description= event.author.mention + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `!work`', color="60D1F6").set_footer(text=f"Requested by {event.member.display_name}",icon=event.member.avatar_url))
            else:
                await event.get_channel().send("<:KSplodes:896043440872235028> Error: You are not allowed to use that command.")

        elif event.message.content.startswith('coins') or event.message.content.startswith('Coins') or event.message.content.startswith('!coins') or event.message.content.startswith('!Coins'):
            await event.message.delete()
            if event.author_id not in [82495450153750528,755539532924977262]:
                return
            elif event.channel_id not in [893867549589131314, 687817008355737606, 839690221083820032]:
                return
            funds = user.getCoins(event.author_id)
            await event.author.send(embed=Embed(description= event.author.mention + ' has ' + str(funds) + '<:HotTips2:465535606739697664>', color="60D1F6").set_footer(text=f"Requested by {event.member.display_name}",icon=event.member.avatar_url))

@EventsPlugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`. Dev has been notified, but check for case sensitive components. Do not spam.")
        channel = await event.app.rest.fetch_channel(687817008355737606)
        me = await event.app.rest.fetch_user(363095569515806722)
        await channel.send(embed = Embed(title=f"Invocation Error in <#{event.context.channel_id}>", description=event.exception))
        embed = Embed(title=f"Invocation Error in <#{event.context.channel_id}>", description=event.exception)
        try: embed= embed.add_field("Traceback:", value=event.exception.__cause__)
        finally:await me.send(embed = embed)
        raise event.exception
    exception = event.exception.__cause__ or event.exception # Unwrap the exception to get the original cause
    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.")
    elif isinstance(exception, lightbulb.CheckFailure):
        if "check_econ_channel" in str(exception) or "check_modmail_channel" in str(exception) or "check_invest_channel" in str(exception):
            await event.context.respond("Wrong Channel.")
        if "check_author_is_me" in str(exception) or "Punished" in str(exception) or "check_publisher" in str(exception):
            await event.context.respond("You are not authorized to use this command")
    elif isinstance(exception, lightbulb.MissingRequiredRole):
        await event.context.respond("You are not authorized to use this command")
    elif isinstance(exception, lightbulb.CommandNotFound):None
    else:
        await event.context.respond(str(exception))
        raise exception

def load(bot):bot.add_plugin(EventsPlugin)
def unload(bot):bot.remove_plugin(EventsPlugin)