import json
import re
from collections import Counter
import time
from typing import Union
from cryptography import fernet

from hikari import undefined
import validators

import hikari
import lightbulb
from hikari import Embed

with open('filekey.key','rb') as file:
    key = file.read()
fernet = fernet.Fernet(key)

def add_onmessage(message):
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

def find_embedded_urls(data):
    regex = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    return re.finditer(regex,data,flags=re.M|re.I)

def find_embedded_phones(data):
    regex = r"\s*(?:\+?(\d{1,3}))?[-. (/]*(\d{3,4})[-. )/]+(\d{3})[-. /]+(\d{3,4})(?: *x(\d+))?\s*"
    return re.finditer(regex,data,flags=re.M|re.I)

EventsPlugin = lightbulb.Plugin("EventsPlugin")

async def nitroScan(event: Union[hikari.GuildMessageUpdateEvent,hikari.GuildMessageCreateEvent]):
    allowed_roles = [225413350874546176,253752685357039617,725377514414932030,338173415527677954,387037912782471179,406690402956083210,729368484211064944]
    role_check = not any(role in event.member.role_ids for role in allowed_roles)
    listDelinked = event.content.lower().split();links = list()
    for item in listDelinked:
        if "http" not in item:item = "https://"+item
        if validators.url(item): links.append(item)
    if bool(links) and not any([any("discord.gift/" in link for link in links),any("discord.com/" in link for link in links)]):
        counted = Counter(listDelinked);nitro=False
        for element in counted.elements():
            if 'nitro' in element:nitro=True;break
        if nitro:
            keywords = set();joiner = ", ";reportlevel = ['Ban',"Log"];nitro = 0;none_found="None Found"
            for element in counted.elements():
                if element in ['airdrop', 'steam', 'free', 'gift', 'left', 'some','got','accidentally','other']:
                    keywords.add(element)
                elif 'nitro' in element: nitro+=1
            embed = Embed(title=f"{reportlevel[0] if keywords else reportlevel[1]} Event: Nitro Scam",description=event.content,color="0xff0000"if keywords else "0x0000ff").add_field("Links",joiner.join(links),inline=True).add_field("Nitro Keyword Count",nitro,inline=True).add_field("Secondary Keyword Count",f"{len(keywords)}: {joiner.join(keywords) if keywords else none_found}",inline=True).add_field("Role Check:","Failed" if role_check else "Passed",inline=True).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id,inline=True).add_field("Channel:",event.get_channel().mention,inline=True)
            if keywords:
                try:await event.message.delete()
                finally:await EventsPlugin.app.rest.create_message(426016300439961601,content="**LOG ONLY**"if not role_check else undefined.UNDEFINED,embed=embed)
                if role_check:
                    await event.member.send("Hey! The bot caught a message from you it thinks is a scam beyond a threshold of doubt. If you believe this is an error, reach out to us here: : https://cpry.net/banned. or if that is broken, tweet @CharliePryor at https://twitter.com/CharliePryor. If able, you can also try replying to this message.")
                    await EventsPlugin.app.rest.ban_user(event.guild_id,event.member.id,delete_message_days=0,reason="NitroScam")
                    return "Ban"
                else: return None
            else:
                await EventsPlugin.app.rest.create_message(682559641930170379,embed=embed)
                return None
    return None

async def whatsappScan(event: Union[hikari.GuildMessageUpdateEvent,hikari.GuildMessageCreateEvent]):
    nums = find_embedded_phones(event.content)
    nums = [match[0] for match in nums]
    has_nums = True if nums else False
    has_whatsapp = any(app in event.content.lower() for app in ["whatsapp","whats app","whats.app","what'sapp","telegram","cash.app","cash app"])
    has_dollarsign = any(currency in event.content.lower() for currency in ["btc", "bitcoin", "eth", "ethereum", "xrp", "ripple", "usdt", "tether","usdc", "usd coin","doge","dogecoin","ada","cardano","zec","zcash","btz","bitcoinz","bnb","binance coin","shib", "shiba inu","ltc","litecoin","bch","bitcoin cash","xmr","monero","cake","pancakeswap token","€",  "£", "$", "¥", "eur", "gbp",  "usd", "cad"])
    allowed_roles = [225413350874546176,253752685357039617,725377514414932030,338173415527677954,387037912782471179,406690402956083210,729368484211064944]
    role_check = not any(role in event.member.role_ids for role in allowed_roles)
    if any([has_whatsapp,has_dollarsign,has_nums]):
        if all([has_whatsapp,has_dollarsign,has_nums]):
            embed = Embed(title="Ban Level Event - WhatsApp Cryptoscam - all triggers hit:",description=event.content,color="0xff0000").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:",f"Triggered: Found Regex Match(s):{nums}" if has_nums else "No Regex Matches Present",inline=True).add_field("`$` Check:","Triggered: Found symbol" if has_dollarsign else "Symbol Not Present",inline=True).add_field("Role Check:","Triggered: No allowed roles" if role_check else "Allowed role present",inline=True).add_field("Result:","Ban" if role_check else "Log",inline=True).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id,inline=True).add_field("Channel:",event.get_channel().mention,inline=True)
            await EventsPlugin.app.rest.create_message(426016300439961601,embed=embed)
            await event.message.delete()
            if role_check:
                await event.member.send("Hey! The bot caught a message from you it thinks is a scam beyond a threshold of doubt. If you believe this is an error, reach out to us here: : https://cpry.net/banned. or if that is broken, tweet @CharliePryor at https://twitter.com/CharliePryor. If able, you can also try replying to this message.")
                await EventsPlugin.app.rest.ban_user(event.guild_id,event.member.id,delete_message_days=0,reason="CryptoScam")
            return "Ban"
        elif any([has_dollarsign and has_nums,has_nums and has_whatsapp, has_whatsapp and has_dollarsign]):
            embed = Embed(title="Mute Level Event - Possible WhatsApp Cryptoscam - 2/3 triggers hit:",description=event.content,color="0xff0000").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:",f"Triggered: Found Regex Match(s):{nums}" if has_nums else "No Regex Matches Present",inline=True).add_field("`$` Check:","Triggered: Found symbol" if has_dollarsign else "Symbol Not Present",inline=True).add_field("Role Check:","Triggered: No allowed roles" if role_check else "Allowed role present",inline=True).add_field("Result:","Mute" if role_check else "Log",inline=True).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id,inline=True).add_field("Channel:",event.get_channel().mention,inline=True)
            await EventsPlugin.app.rest.create_message(426016300439961601,embed=embed)
            await event.message.delete()
            if role_check:await EventsPlugin.app.rest.add_role_to_member(event.guild_id,event.member.id,684936661745795088,reason="CryptoScam")
            return "Mute"
        elif has_nums or has_whatsapp:
            embed = Embed(title="Log Level Event - Phone Number or WhatsApp like trigger hit:",description=event.content,color="0x0000ff").add_field("Whatsapp Check:","Triggered: Found keyword" if has_whatsapp else "Keyword Not Present",inline=True).add_field("Phone Number Check:",f"Triggered: Found Regex Match(s):{nums}" if has_nums else "No Regex Matches Present",inline=True).add_field("Member",f"Username: {event.member.username}, Discriminator: {event.member.discriminator}",inline=True).add_field("Member ID",event.member.id,inline=True).add_field("Channel:",event.get_channel().mention,inline=True)
            await EventsPlugin.app.rest.create_message(682559641930170379,embed=embed)
    return None

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

@EventsPlugin.listener(hikari.GuildMessageUpdateEvent)
async def on_message(event: hikari.GuildMessageUpdateEvent) -> None:
    if event.content is not None and event.is_human and event.guild_id==225345178955808768:
        result = await whatsappScan(event)
        if result: return
        result1 = await nitroScan(event)
        if result1: return

@EventsPlugin.listener(hikari.GuildMessageCreateEvent)
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is not None and event.is_human and event.guild_id==225345178955808768:
        result = await whatsappScan(event)
        if result: return
        result1 = await nitroScan(event)
        if result1: return
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