from io import BytesIO
import json
import os
import re

import auxone as a
import fpdf
import hikari
import lightbulb
from cryptography.fernet import Fernet
from lightbulb import commands
from lightbulb.commands.base import OptionModifier

with open('filekey.key','rb') as file:
    key = file.read()
    fernet = Fernet(key)
    
Modmail_Plugin = lightbulb.Plugin("Modmail_Plugin")

@Modmail_Plugin.command
@lightbulb.add_checks(lightbulb.Check(a.checks.check_modmail_channel)|lightbulb.owner_only)
@lightbulb.command("ticket", "modmail group",hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommandGroup)
async def ticket(ctx) -> None: await ctx.respond("invoked ticket")

@ticket.child
@lightbulb.option("member", "Ticket ID to reply to",type=hikari.Member,required=True)
@lightbulb.option("message", "Message to reply with", type=str, required=True, modifier=OptionModifier.CONSUME_REST)
@lightbulb.command("reply", "reply to an open ticket", inherit_checks=True,hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    modnames={
        363095569515806722:"[Moderator] Bluesy",247950431630655488:"[Moderator] Doffey",82495450153750528:"[Moderator] Kaitlin",146285543146127361:"[Admin] Jazmine",138380316095021056:"[Moderator] Krios",
        162833689196101632:"[Moderator] Mike Takumi", 137240557280952321:"[Admin] Pet",137240557280952321:"[Moderator] Melethya",225344348903047168:"[Owner] Charlie"
    }
    a.add_message(ctx,ctx.options.message,ctx.options.member.id)
    await ctx.respond("Sent.")
    await ctx.options.member.send("Message from "+str(modnames[ctx.author.id])+": "+ctx.options.message)


@ticket.child
@lightbulb.option("ticket", "ticket to query", type=str, default=None)
@lightbulb.command("history", "displays history of one or all tickets", inherit_checks=True,hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def history(ctx):
    ticket = ctx.options.ticket
    if ticket is not None:
        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        for message in list(tickets[ticket]["messages"].keys()):
            pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
            pdf.ln()
        pdfName = "ticket_"+ticket+".pdf"
        pdf.output(pdfName)
        await ctx.respond('see here:')
        await ctx.edit_last_response(attachment=pdfName)
        os.remove(pdfName)
    elif ticket is None:
        pdf = fpdf.FPDF(format='letter')
        pdf.set_font("Arial", size=12)
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        for ticket in list(tickets.keys()):
            pdf.add_page()
            pdf.set_font("Arial", size=24)
            pdf.write(10,a.strip_non_ascii(str(ticket)))
            pdf.set_font("Arial", size=12)
            pdf.ln()
            for message in list(tickets[ticket]["messages"].keys()):
                pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
                pdf.ln()
        pdf.output("all_tickets.pdf")
        await ctx.respond('see here:')
        await ctx.edit_last_response(attachment="all_tickets.pdf")
        os.remove("all_tickets.pdf")


@ticket.child
@lightbulb.command("list", "Displays all open tickets in modmail", inherit_checks=True, ephemeral=True,hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
        with open('tickets.json',"rb") as t:
            temp = fernet.decrypt(t.read())
        tickets = json.loads(temp)
        openTickets = list()
        for ticket in list(tickets.keys()):
            if tickets[ticket]["open"] == "True":
                author = "<@!"+str(tickets[ticket]['starter'])+">"
                appender = str(ticket)+" (Profile: " +author+")"
                openTickets.append(appender)
        tempStr = ", "
        tempOut = tempStr.join(openTickets)
        outString = "Open tickets are tickets numbered: " + tempOut
        await ctx.respond(outString, flags=64)

@ticket.child
@lightbulb.option("ticket", "ticket to close", type=str, default=None)
@lightbulb.command("name", "displays history of one or all tickets", inherit_checks=True,hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    ticket = ctx.options.ticket;name = ctx.options.name
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for message in list(tickets[ticket]["messages"].keys()):
        pdf.write(5,a.strip_non_ascii(str(tickets[ticket]["messages"][message])))
        pdf.ln()
    pdfName = "ticket "+re.sub(r':',"",a.strip_non_ascii(ticket))+".pdf"
    pdf.output(pdfName)
    tickets[ticket]["open"]="False"
    tickets[name] = tickets.pop(ticket)
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    await ctx.respond("Ticket Closed.")
    await ctx.edit_last_response(attachment=pdfName)
    os.remove(pdfName) 


@ticket.child
@lightbulb.option("member", "member to open ticket with",type=hikari.Member,required=True)
@lightbulb.option("message", "Message to send", type=str, required=True, modifier=OptionModifier.CONSUME_REST)
@lightbulb.command("open", "open a ticket", inherit_checks=True,hidden=True,guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    member = ctx.options.member;message = ctx.options.message
    with open('tickets.json',"rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    newTicketNum = len(list(tickets.keys()))
    newTicket = {
            "open":"True","time":0,"starter":int(member.id), "messages":{
                "0":str(ctx.author)+": "+str(message)
            }
        }
    tickets.update({str(newTicketNum):newTicket})
    with open('tickets.json','wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    modnames={
        363095569515806722:"[Moderator] Bluesy",247950431630655488:"[Moderator] Doffey",82495450153750528:"[Moderator] Kaitlin",146285543146127361:"[Admin] Jazmine",162833689196101632:"[Moderator] Krios",
        162833689196101632:"[Moderator] Mike Takumi", 137240557280952321:"[Admin] Pet",137240557280952321:"[Moderator] Melethya",225344348903047168:"[Owner] Charlie"
    }
    await member.send("Message from "+str(modnames[ctx.author.id])+": "+message)
    await ctx.respond("Sent.")

def load(bot):bot.add_plugin(Modmail_Plugin)
def unload(bot):bot.remove_plugin(Modmail_Plugin)
