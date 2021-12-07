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
async def on_message(event) -> None:
    if event.content is not None and event.is_human:
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
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")
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