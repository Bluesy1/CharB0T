import datetime
import json
import re
import time
import traceback
from cryptography import fernet

from hikari import GuildChannel

import hikari
import lightbulb
from lightbulb import commands
from hikari import Embed

with open('filekey.key','rb') as file:
    key = file.read()
fernet = fernet.Fernet(key)


def add_onmessage(message):
    """Adds a messag dmed to the bot to modlog logs"""
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for ticket in list(tickets.keys()):
        if tickets[ticket]["open"] == "True":
            if tickets[ticket]['starter'] == message.author.id:
                if (int(round(time.time(),0))-int(tickets[ticket]['time'])) < 5:
                    return None
                messages = tickets[ticket]['messages']
                numMessages = len(list(messages.keys()))
                messages.update({str(numMessages):str(message.author.username)+": "+str(message.content)})
                for attachment in message.attachments:
                    numMessages = len(list(messages.keys()))
                    messages.update({str(numMessages):str(message.author)+": "+str(attachment.url)})
                tickets[ticket]['messages'] = messages
                tickets[ticket]['time'] = round(time.time(),0)
                with open('tickets.json','wb') as t:
                    t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
                return [ticket,"old"]
    newTicketNum = len(list(tickets.keys()))
    newTicket = {
            "open":"True","time":round(time.time(),0),"starter":message.author.id, "messages":{
                "0":str(message.author)+": "+str(message.content)
            }
        }
    tickets.update({str(newTicketNum):newTicket})
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    return [str(newTicketNum)+": "+str(message.author.username),"new"]

EventsPlugin = lightbulb.Plugin("EventsPlugin")

@EventsPlugin.listener(hikari.DMMessageCreateEvent)
async def on_DMmessage(event:hikari.DMMessageCreateEvent):
    try: await EventsPlugin.app.rest.fetch_member(225345178955808768,event.author_id)
    except: return
    if event.is_human:
        if event.content is not None:
            if str(event.message.content).startswith("!"):
                await event.author.send("Commands do not work in dms.")
                return
            ticket = add_onmessage(event.message)
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
        if event.guild_id==225345178955808768 and not any(role in [338173415527677954,253752685357039617,225413350874546176,387037912782471179,406690402956083210,729368484211064944] for role in event.member.role_ids):
            if f"<@&{event.guild_id}>" in event.content or "@everyone" in event.content or "@here" in event.content:
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

@EventsPlugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`. Dev has been notified, but check for case sensitive components. Do not spam.")
        me = await event.app.rest.fetch_user(363095569515806722)
        try:raise event.exception
        except Exception as e:
            embed = Embed(title=f"Invocation Error in {f'{event.context.get_channel().name} in guild {event.context.get_guild().name} ((Guild,Channel) ID pair) ({event.context.guild_id},{event.context.channel_id})' if event.context.get_channel() is GuildChannel else 'DMs' if event.context.get_channel() is None else f'<@{event.context.channel_id}>'}",timestamp=datetime.datetime.now(tz=datetime.timezone.utc), description=f"```{traceback.format_exc()}```")
            await me.send(embed = embed)
            raise e
    exception = event.exception.__cause__ or event.exception # Unwrap the exception to get the original cause
    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.")
    elif isinstance(exception, lightbulb.CheckFailure):
        if "check_econ_channel" in str(exception) or "check_modmail_channel" in str(exception) or "check_invest_channel" in str(exception):
            await event.context.respond("Wrong Channel.")
        if any(substring in str(exception) for substring in ["check_author_is_me","Punished","check_publisher","check_author_work_allowed","check_author_is_admin","check_author_is_mod"]):
            await event.context.respond("You are not authorized to use this command")
    elif isinstance(exception, lightbulb.MissingRequiredRole):
        await event.context.respond("You are not authorized to use this command")
    elif isinstance(exception, lightbulb.CommandNotFound):None
    else:
        await event.context.respond(str(exception))
        me = await event.app.rest.fetch_user(363095569515806722)
        try:raise event.exception
        except Exception as e:
            embed = Embed(title=f"Error in {f'{event.context.get_channel().name} in guild {event.context.get_guild().name} ((Guild,Channel) ID pair) ({event.context.guild_id},{event.context.channel_id})' if event.context.get_channel() is  GuildChannel else 'DMs' if event.context.get_channel() is None else f'<@{event.context.channel_id}>'}", timestamp=datetime.datetime.now(tz=datetime.timezone.utc), description=f"```{traceback.format_exc()}```")
            await me.send(embed = embed)
            raise e

@EventsPlugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("error", "Checks that the bot is alive")
@lightbulb.implements(commands.PrefixCommand)
async def error(ctx:lightbulb.Context):
    test = (1,2)
    test[1] = 3

def load(bot):bot.add_plugin(EventsPlugin)
def unload(bot):bot.remove_plugin(EventsPlugin)