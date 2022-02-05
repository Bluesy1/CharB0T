import json
import os
import re

import fpdf
import hikari
import lightbulb
from cryptography.fernet import Fernet
from lightbulb import commands
from lightbulb.commands.base import OptionModifier

with open('filekey.key', 'rb') as file:
    key = file.read()
    fernet = Fernet(key)


def strip_non_ascii(string):
    """ Returns the string without non ASCII characters"""
    stripped = [c for c in string if 0 < ord(c) < 255]
    return ''.join(stripped)


def add_message(ctx, message, user_id):
    """Adds message to json"""
    with open('tickets.json', "rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    for sub_ticket in list(tickets.keys()):
        if tickets[str(sub_ticket)]['starter'] == user_id:
            break
    messages = tickets[sub_ticket]['messages']  # pylint: disable=undefined-loop-variable
    num_messages = len(list(messages.keys()))  # pylint: disable=undefined-loop-variable
    messages.update({str(num_messages): str(ctx.author.username) + ": " + str(message)})
    tickets[sub_ticket]['messages'] = messages  # pylint: disable=undefined-loop-variable
    with open('tickets.json', 'wb') as file_a:
        file_a.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))


def check_modmail_channel(context):
    """Channel Check"""
    return context.channel_id in [906578081496584242, 687817008355737606]


Modmail_Plugin = lightbulb.Plugin("Modmail_Plugin")


@Modmail_Plugin.command
@lightbulb.add_checks(lightbulb.Check(check_modmail_channel) | lightbulb.owner_only)
@lightbulb.command("ticket", "modmail group", hidden=True, guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommandGroup)
async def ticket(ctx) -> None:
    """Ticket command group"""
    await ctx.respond("invoked ticket")


@ticket.child
@lightbulb.option("member", "Ticket ID to reply to", type=hikari.Member, required=True)
@lightbulb.option("message", "Message to reply with", type=str, required=True, modifier=OptionModifier.CONSUME_REST)
@lightbulb.command("reply", "reply to an open ticket", inherit_checks=True, hidden=True, guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    """Replies to a ticket"""
    modnames = {
        363095569515806722: "[Moderator] Bluesy", 247950431630655488: "[Moderator] Doffey",
        82495450153750528: "[Moderator] Kaitlin", 146285543146127361: "[Admin] Jazmine",
        138380316095021056: "[Moderator] Krios",
        162833689196101632: "[Moderator] Mike Takumi", 244529987510599680: "[Admin] Pet",
        137240557280952321: "[Moderator] Melethya", 225344348903047168: "[Owner] Charlie"
    }
    add_message(ctx, ctx.options.message, ctx.options.member.id)
    await ctx.respond("Sent.")
    await ctx.options.member.send("Message from " + str(modnames[ctx.author.id]) + ": " + ctx.options.message)


@ticket.child
@lightbulb.option("ticket", "ticket to query", type=str, default=None)
@lightbulb.command("history", "displays history of one or all tickets", inherit_checks=True, hidden=True,
                   guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def history(ctx):
    """Queries a ticket"""
    opt_ticket = ctx.options.ticket
    if opt_ticket is not None:
        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        with open('tickets.json', "rb") as temp_a:
            temp = fernet.decrypt(temp_a.read())
        tickets = json.loads(temp)
        for message in list(tickets[opt_ticket]["messages"].keys()):
            pdf.write(5, strip_non_ascii(str(tickets[opt_ticket]["messages"][message])))
            pdf.ln()
        pdf_name = "ticket_" + opt_ticket + ".pdf"
        pdf.output(pdf_name)
        await ctx.respond('see here:')
        await ctx.edit_last_response(attachment=pdf_name)
        os.remove(pdf_name)
    elif opt_ticket is None:
        pdf = fpdf.FPDF(format='letter')
        pdf.set_font("Arial", size=12)
        with open('tickets.json', "rb") as temp_a:
            temp = fernet.decrypt(temp_a.read())
        tickets = json.loads(temp)
        for opt_ticket in list(tickets.keys()):
            pdf.add_page()
            pdf.set_font("Arial", size=24)
            pdf.write(10, strip_non_ascii(str(opt_ticket)))
            pdf.set_font("Arial", size=12)
            pdf.ln()
            for message in list(tickets[opt_ticket]["messages"].keys()):
                pdf.write(5, strip_non_ascii(str(tickets[opt_ticket]["messages"][message])))
                pdf.ln()
        pdf.output("all_tickets.pdf")
        await ctx.respond('see here:')
        await ctx.edit_last_response(attachment="all_tickets.pdf")
        os.remove("all_tickets.pdf")


@ticket.child
@lightbulb.command("list", "Displays all open tickets in modmail", inherit_checks=True, ephemeral=True, hidden=True,
                   guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def list_command(ctx):
    """Lists all open tickets"""
    with open('tickets.json', "rb") as temp:
        temp = fernet.decrypt(temp.read())
    tickets = json.loads(temp)
    open_tickets = []
    for sub_ticket in list(tickets.keys()):
        if tickets[sub_ticket]["open"] == "True":
            author = "<@!" + str(tickets[sub_ticket]['starter']) + ">"
            appender = str(sub_ticket) + " (Profile: " + author + ")"
            open_tickets.append(appender)
    temp_str = ", "
    temp_out = temp_str.join(open_tickets)
    out_string = "Open tickets are tickets numbered: " + temp_out
    await ctx.respond(out_string, flags=64)


@ticket.child
@lightbulb.option("ticket", "ticket to close", type=str, default=None)
@lightbulb.command("name", "displays history of one or all tickets", inherit_checks=True, hidden=True,
                   guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    """Closes a modmail ticket"""
    opt_ticket = ctx.options.ticket
    name = ctx.options.name
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    with open('tickets.json', "rb") as temp_a:
        temp = fernet.decrypt(temp_a.read())
    tickets = json.loads(temp)
    for message in list(tickets[opt_ticket]["messages"].keys()):
        pdf.write(5, strip_non_ascii(str(tickets[opt_ticket]["messages"][message])))
        pdf.ln()
    pdf_name = "ticket " + re.sub(r':', "", strip_non_ascii(opt_ticket)) + ".pdf"
    pdf.output(pdf_name)
    tickets[opt_ticket]["open"] = "False"
    tickets[name] = tickets.pop(opt_ticket)
    with open('tickets.json', 'wb') as temp_a:
        temp_a.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    await ctx.respond("Ticket Closed.")
    await ctx.edit_last_response(attachment=pdf_name)
    os.remove(pdf_name)


@ticket.child
@lightbulb.option("member", "member to open ticket with", type=hikari.Member, required=True)
@lightbulb.option("message", "Message to send", type=str, required=True, modifier=OptionModifier.CONSUME_REST)
@lightbulb.command("open", "open a ticket", inherit_checks=True, hidden=True, guilds=[225345178955808768])
@lightbulb.implements(commands.SlashSubCommand)
async def open_command(ctx):
    """Opens a modmail ticket"""
    member = ctx.options.member
    message = ctx.options.message
    with open('tickets.json', "rb") as t:
        temp = fernet.decrypt(t.read())
    tickets = json.loads(temp)
    new_ticket_num = len(list(tickets.keys()))
    new_ticket = {
        "open": "True", "time": 0, "starter": int(member.id), "messages": {
            "0": str(ctx.author) + ": " + str(message)
        }
    }
    tickets.update({str(new_ticket_num): new_ticket})
    with open('tickets.json', 'wb') as t:
        t.write(fernet.encrypt(json.dumps(tickets).encode('utf-8')))
    modnames = {
        363095569515806722: "[Moderator] Bluesy", 247950431630655488: "[Moderator] Doffey",
        82495450153750528: "[Moderator] Kaitlin", 146285543146127361: "[Admin] Jazmine",
        138380316095021056: "[Moderator] Krios",
        162833689196101632: "[Moderator] Mike Takumi", 244529987510599680: "[Admin] Pet",
        137240557280952321: "[Moderator] Melethya", 225344348903047168: "[Owner] Charlie"
    }
    await member.send("Message from " + str(modnames[ctx.author.id]) + ": " + message)
    await ctx.respond("Sent.")


def load(bot):
    """Loads the plugin"""
    bot.add_plugin(Modmail_Plugin)


def unload(bot):
    """Unloads the plugin"""
    bot.remove_plugin(Modmail_Plugin)
