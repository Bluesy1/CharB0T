import datetime
import json
import re
import time
import traceback

import hikari
import lightbulb
from cryptography import fernet
from hikari import Embed, GuildChannel, HikariError

with open('filekey.key', 'rb') as file:
    FERNET = fernet.Fernet(file.read())


def add_onmessage(message):
    """Adds a messag dmed to the bot to modlog logs"""
    with open('tickets.json',"rb") as ticket_file:
        tickets = json.loads(FERNET.decrypt(ticket_file.read()))
    for ticket in list(tickets.keys()):
        if tickets[ticket]["open"] == "True":
            if tickets[ticket]['starter'] == message.author.id:
                if (int(round(time.time(), 0))-int(tickets[ticket]['time'])) < 5:
                    return None
                messages = tickets[ticket]['messages']
                num_messages = len(list(messages.keys()))
                messages.update({str(num_messages):str(message.author.username)+": "+str(message.content)})
                for attachment in message.attachments:
                    num_messages = len(list(messages.keys()))
                    messages.update({str(num_messages):str(message.author)+": "+str(attachment.url)})
                tickets[ticket]['messages'] = messages
                tickets[ticket]['time'] = round(time.time(), 0)
                with open('tickets.json', 'wb') as ticket_file:
                    ticket_file.write(FERNET.encrypt(json.dumps(tickets).encode('utf-8')))
                return [ticket,"old"]
    new_ticket_num = len(list(tickets.keys()))
    new_ticket = {
            "open":"True", "time":round(time.time(),0), "starter":message.author.id, "messages":{
                "0":str(message.author)+": "+str(message.content)
            }
        }
    tickets.update({str(new_ticket_num):new_ticket})
    with open('tickets.json', 'wb') as ticket_file:
        ticket_file.write(FERNET.encrypt(json.dumps(tickets).encode('utf-8')))
    return [str(new_ticket_num)+": "+str(message.author.username), "new"]

EVENTS = lightbulb.Plugin("EVENTS")

@EVENTS.listener(hikari.DMMessageCreateEvent)
async def on_dm_message(event: hikari.DMMessageCreateEvent):
    """DM Message Create Handler ***DO NOT CALL MANUALLY***"""
    try:
        await EVENTS.app.rest.fetch_member(225345178955808768, event.author_id)
    except HikariError:
        return
    if event.is_human:
        if event.content is not None:
            if str(event.message.content).startswith("!"):
                await event.author.send("Commands do not work in dms.")
                return
            ticket = add_onmessage(event.message)
            if ticket is None:
                return
            channel = await EVENTS.bot.rest.fetch_channel(906578081496584242)
            await channel.send(f"Message from {str(event.message.author.username)} `{str(event.message.author.id)}`, Ticket: `{str(ticket[0])}`):")#pylint: disable=line-too-long
            if ticket[1] == "new":
                await event.author.send("Remember to check our FAQ to see if your question/issue is addressed there: https://cpry.net/discordfaq")#pylint: disable=line-too-long
            message = await channel.send(f"message: {event.message.content}")
            await message.edit(attachments=event.message.attachments)

@EVENTS.listener(hikari.GuildMessageCreateEvent)
async def on_guild_message(event: hikari.GuildMessageCreateEvent) -> None:
    """Guild Message Create Handler ***DO NOT CALL MANUALLY***"""
    if event.content is not None and event.is_human:
        if (int(event.guild_id) == 225345178955808768 and
                not any(role in [338173415527677954, 253752685357039617, 225413350874546176,
                                     387037912782471179, 406690402956083210, 729368484211064944])
                for role in event.member.role_ids):
            if f"<@&{event.guild_id}>" in event.content or "@everyone" in event.content or "@here" in event.content:
                await event.message.member.add_role(676250179929636886)
                await event.message.member.add_role(684936661745795088)
                await event.message.delete()
                channel = await EVENTS.app.rest.fetch_channel(426016300439961601)
                embed = (Embed(description=event.content, title="Mute: Everyone/Here Ping sent by non mod",
                               color="0xff0000")
                         .set_footer(text=f"Sent by {event.message.member.display_name}-{event.message.member.id}",
                                     icon=event.message.member.avatar_url))
                await channel.send(embed=embed)
        if event.is_bot or not event.content:
            return
        if re.search(r"bruh", event.content, re.MULTILINE|re.IGNORECASE):
            await event.message.delete()
        elif (re.search(r"~~:.|:;~~", event.content, re.MULTILINE|re.IGNORECASE)
              or re.search(r"tilde tilde colon dot vertical bar colon semicolon tilde tilde",
                           event.content, re.MULTILINE|re.IGNORECASE)):
            await event.message.delete()

@EVENTS.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    """Error Handler ***DO NOT CALL MANUALLY***"""
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong while running command `{event.context.command.name}`. Bluesy#8150 has been notified.", flags=64)# pylint: disable=line-too-long
        bluesy = await event.app.rest.fetch_user(363095569515806722)
        try:
            raise event.exception
        except event.exception:
            embed = (Embed(title=f"Invocation Error in {f'{event.context.get_channel().name} in guild {event.context.get_guild().name} ((Guild,Channel) ID pair) ({event.context.guild_id},{event.context.channel_id})' if event.context.get_channel() is GuildChannel else 'DMs' if event.context.get_channel() is None else f'<@{event.context.channel_id}>'}",# pylint: disable=line-too-long
                           timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                           description=f"```{traceback.format_exc()}```"))
            await bluesy.send(embed=embed)
            traceback.print_exc()
    exception = event.exception.__cause__ or event.exception # Unwrap the exception to get the original cause
    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.", flags=64)
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.", flags=64)# pylint: disable=line-too-long
    elif isinstance(exception, lightbulb.CheckFailure):
        if any(substring in str(exception) for substring in
               ["check_author_is_me", "Punished", "check_author_work_allowed",
                "check_author_is_admin", "check_author_is_mod"]):
            await event.context.respond("You are not authorized to use this command", flags=64)
    elif isinstance(exception, lightbulb.MissingRequiredRole):
        await event.context.respond("You are not authorized to use this command", flags=64)
    elif isinstance(exception, lightbulb.CommandNotFound):
        return
    else:
        await event.context.respond(str(exception), flags=64)
        bluesy = await event.app.rest.fetch_user(363095569515806722)
        try:
            raise exception
        except exception:
            embed = (Embed(title=f"Error in {f'{event.context.get_channel().name} in guild {event.context.get_guild().name} ((Guild,Channel) ID pair) ({event.context.guild_id},{event.context.channel_id})' if event.context.get_channel() is  GuildChannel else 'DMs' if event.context.get_channel() is None else f'<@{event.context.channel_id}>'}",# pylint: disable=line-too-long
                           timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                           description=f"```{traceback.format_exc()}```"))
            await bluesy.send(embed=embed)
            traceback.print_exc()

def load(bot):
    """Loads Plugin"""
    bot.add_plugin(EVENTS)
def unload(bot):
    """Unloads Plugin"""
    bot.remove_plugin(EVENTS)
