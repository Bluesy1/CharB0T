import asyncio
import json
import os
import time

import lightbulb
from lightbulb.commands.slash import SlashCommand
from lightbulb.decorators import implements
from lightbulb.errors import LightbulbError
import pandas as pd
import sfsutils
from auxone import URL, checks, ksptime, render_mpl_table, userInfo
from hikari.channels import ChannelType, PermissionOverwriteType
from hikari.commands import CommandChoice, OptionType
from hikari.embeds import Embed
from hikari.events.interaction_events import InteractionCreateEvent
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle
from hikari.permissions import Permissions
from lightbulb import commands
from lightbulb.checks import has_roles

AdminPlugin = lightbulb.Plugin("AdminPlugin")
AdminPlugin.add_checks(lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,mode=any)))

@AdminPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.check_publisher))
@lightbulb.option("logo", "use logo?", type=OptionType.BOOLEAN, required=True)
@lightbulb.option('channel', 'channel to post embed to', type=OptionType.CHANNEL, required=True, channel_types=[ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS])
@lightbulb.option("time","This is the publishing time info (Must include Published at: if you want that to show up.)", required=True)
@lightbulb.option("color","Embed color", choices=[
    CommandChoice(name="Breaking News",value="#FEE75C"),
    CommandChoice(name="Financial",value="#57F287"),
    CommandChoice(name="Patents/Info Sector Updates",value="#5865F2"),
    CommandChoice(name="Other",value="#BCC0C0")],required=True)
@lightbulb.option("body","This is the body of the command", required=True)
@lightbulb.option("title","This is the title of the embed",required=True)
@lightbulb.option("author", "Article Author, default Author Kerman", default="Author Kerman", required=False)
@lightbulb.option("image", "URL of image to use as logo.", default=None, required=False)
@lightbulb.command("publish", "publishes and embed to passed channel",guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    publishTo=ctx.options.channel.id;morePars=True;body1=ctx.options.body;title=ctx.options.title;color=ctx.options.color
    addImage = False; author=ctx.options.author; time=ctx.options.time; image = ctx.options.image; footer=True; hasAuthor=True
    hasLogo = ctx.options.logo
    embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
    if ctx.options.logo:embed.set_thumbnail(image)
    YesNoButtons=AdminPlugin.bot.rest.build_action_row()
    YesNoButtons.add_button(ButtonStyle.SUCCESS, "Yes").set_label("Yes").set_emoji("✅").add_to_container()
    YesNoButtons.add_button(ButtonStyle.DANGER, "No").set_label("No").set_emoji("❌").add_to_container()
    while morePars:
        await ctx.respond("Do you want to add another paragraph?", embed=embed, components=[YesNoButtons, ])
        try:
            async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(('interaction.user.id', ctx.author.id)) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                    key = event.interaction.custom_id
                    if key == "Yes":
                        await ctx.edit_last_response("Please enter your next paragraph:", embed=None, components=[])
                        try:
                            async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                async for event2 in stream2:
                                    add = " \n \n "+(str(event2.message.content))
                                    await event2.message.delete()
                                    if (len(body1+add)>4096):
                                        await ctx.edit_last_response("Error, too long. ignoring last entry.", embed=None, components=[])
                                        await asyncio.sleep(5)
                                        break
                                    body1 += add
                                    embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
                                    if ctx.options.logo:embed.set_thumbnail(image)
                                    msg = await ctx.edit_last_response("Paragraph added.", embed=embed, components=[])
                                    await asyncio.sleep(5)
                                    if len(body1) >=3950:
                                        await ctx.edit_last_response("Max length Reached, No more paragraphs allowed", embed=None, components=[])
                                        await asyncio.sleep(5)
                                        break
                                    continue
                        except asyncio.TimeoutError:
                            await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
                    elif key == "No":
                        await ctx.edit_last_response("Done adding paragraphs.",embed=None, components=[])
                        await asyncio.sleep(5)
                        morePars=False
        except asyncio.TimeoutError:
            await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
    await ctx.edit_last_response("Add Image?",embed=None, components=[YesNoButtons, ])
    try:
        async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                if key == "No":
                    await ctx.edit_last_response("No Image.",embed=None, components=[])
                    await asyncio.sleep(5)
                elif key== "Yes":
                    await ctx.edit_last_response("Please upload the photo:",embed=None, components=[])
                    try:
                        async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                            async for event2 in stream2:
                                addedImage = event2.message.attachments[0].url
                                addImage = True
                                await event2.message.delete()
                    except asyncio.TimeoutError:
                            await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
    except asyncio.TimeoutError:
        await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
    embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
    if ctx.options.logo:embed.set_thumbnail(image)
    if addImage:embed.set_image(addedImage)
    EditMenu = AdminPlugin.bot.rest.build_action_row()
    (EditMenu.add_select_menu("Editing")
        .add_option("Yes", "Yes").set_emoji("✅").set_description("Use this to publish Embed").add_to_menu()
        .add_option("No, remove image", "rImg").set_emoji("❌").set_description("Use this to remove the embedded image").add_to_menu()
        .add_option("No, remove logo", "rLogo").set_emoji("❌").set_description("Use this to remove the embedded logo").add_to_menu()
        .add_option("No, remove author", "rAuth").set_emoji("❌").set_description("Use this to remove the author of the embed").add_to_menu()
        .add_option("No, remove footer", "rFoot").set_emoji("❌").set_description("Use this to remove the footer of the embed").add_to_menu()
        .add_option("No, edit text", "Text").set_emoji("❌").set_description("Use this to edit the description of the embed").add_to_menu()
        .add_option("No, edit title", "Title").set_emoji("❌").set_description("Use this to edit the title of the embed").add_to_menu()
        .add_option("No, edit author", "eAuth").set_emoji("❌").set_description("Use this to edit the author of the embed").add_to_menu()
        .add_option("No, edit footer", "eFoot").set_emoji("❌").set_description("Use this to edit the footer of the embed").add_to_menu()
        .add_option("CANCEL, cancel publishing", "CANCEL").set_emoji("❌").set_description("Use this to cancel the command").add_to_menu()
        .add_to_container()
    )   
    while True:
        embed=Embed(title=title, description=body1, color=color)
        if hasAuthor:embed.set_author(name=author)
        if footer:embed.set_footer(text=time)
        if hasLogo:embed.set_thumbnail(image)
        if addImage:embed.set_image(addedImage)
        await ctx.edit_last_response("Is this good?",embed=embed, components=[EditMenu, ])
        try:
            async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(('interaction.user.id', ctx.author.id)) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                    key = event.interaction.values[0]
                    if key=="Yes":
                        await ctx.edit_last_response("Sent.",embed=None, components=[])
                        publish = await AdminPlugin.bot.rest.fetch_channel(publishTo)
                        await publish.send(embed=embed)
                        return; break
                    elif key=="CANCEL":
                        await ctx.edit_last_response("CANCELED.",embed=None, components=[])
                        return
                    elif key=="rImg":
                        addImage=False
                        await ctx.edit_last_response("Removed.",embed=None, components=[])
                        await asyncio.sleep(5)
                        continue
                    elif key=="rLogo":
                        hasLogo=False
                        await ctx.edit_last_response("Removed.",embed=None, components=[])
                        await asyncio.sleep(5)
                        continue
                    elif key=="rAuth":
                        hasAuthor=False
                        await ctx.edit_last_response("Removed.",embed=None, components=[])
                        await asyncio.sleep(5)
                        continue
                    elif key=="rFoot":
                        footer=False
                        await ctx.edit_last_response("Removed.",embed=None, components=[])
                        await asyncio.sleep(5)
                        continue
                    elif key=="Title":
                        await ctx.edit_last_response("Please send new title",embed=None, components=[])
                        try:
                            async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                async for event2 in stream2:
                                    await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                                    if event2.content is not None:
                                        title = event2.content
                                    else:
                                        await ctx.edit_last_response("Error: No text found in message.",embed=None, components=[])
                                        await asyncio.sleep(5)
                                    await event2.message.delete()
                                    continue
                        except asyncio.TimeoutError:await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[]);continue
                    elif key=="Text":
                        await ctx.edit_last_response("Please send first paragraph",embed=None, components=[]); morePars=True
                        try:
                            async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                async for event2 in stream2:
                                    await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                                    body1 = event2.content
                                    await event2.message.delete()
                                    continue
                        except asyncio.TimeoutError:await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
                        while morePars:
                            await ctx.edit_last_response("Do you want to add another paragraph?", embed=embed, components=[YesNoButtons, ])
                            try:
                                async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(('interaction.user.id', ctx.author.id)) as stream:
                                    async for event in stream:
                                        await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                                        key = event.interaction.custom_id
                                        if key == "Yes":
                                            await ctx.edit_last_response("Please enter your next paragraph:", embed=None, components=[])
                                            try:
                                                async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                                    async for event2 in stream2:
                                                        add = " \n \n "+(str(event2.message.content))
                                                        await event2.message.delete()
                                                        if (len(body1+add)>4096):
                                                            await ctx.edit_last_response("Error, too long. ignoring last entry.", embed=None, components=[])
                                                            await asyncio.sleep(5)
                                                            break
                                                        body1 += add
                                                        embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
                                                        if ctx.options.logo:embed.set_thumbnail(image)
                                                        msg = await ctx.edit_last_response("Paragraph added.", embed=embed, components=[])
                                                        await asyncio.sleep(5)
                                                        if len(body1) >=3950:
                                                            await ctx.edit_last_response("Max length Reached, No more paragraphs allowed", embed=None, components=[])
                                                            await asyncio.sleep(5)
                                                            break
                                                        continue
                                            except asyncio.TimeoutError:
                                                await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
                                        elif key == "No":
                                            await ctx.edit_last_response("Done adding paragraphs.",embed=None, components=[])
                                            await asyncio.sleep(5)
                                            morePars=False
                            except asyncio.TimeoutError:await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])
                    elif key=="eAuth":
                        await ctx.edit_last_response("Please send new author",embed=None, components=[])
                        try:
                            async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                async for event2 in stream2:
                                    await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                                    if event2.content is not None:
                                        hasAuthor=True
                                        author = event2.content
                                    else:
                                        await ctx.edit_last_response("Error: No text found in message.",embed=None, components=[])
                                        await asyncio.sleep(5)
                                    await event2.message.delete()
                                    continue
                        except asyncio.TimeoutError:await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[]);continue
                    elif key=="eFoot":
                        await ctx.edit_last_response("Please send new footer",embed=None, components=[])
                        try:
                            async with AdminPlugin.bot.stream(GuildMessageCreateEvent, timeout=15).filter(('author_id', ctx.author.id)) as stream2:
                                async for event2 in stream2:
                                    await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                                    if event2.content is not None:
                                        footer=True
                                        time = event2.content
                                    else:
                                        await ctx.edit_last_response("Error: No text found in message.",embed=None, components=[])
                                        await asyncio.sleep(5)
                                    await event2.message.delete()
                                    continue
                        except asyncio.TimeoutError:await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[]);continue
        except asyncio.TimeoutError:
            await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])

@AdminPlugin.command
@lightbulb.command("maketime","makes a unix time constructor for use with discord's unix time feature",guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
    TimeMenu = AdminPlugin.bot.rest.build_action_row()
    (TimeMenu.add_select_menu("Editing")
        .add_option("Done", "Done").set_emoji("✅").set_description("Use this to get the final options").add_to_menu()
        .add_option("+30 minutes", "+m").set_emoji("➡️").set_description("Use this to increase the time by 30 minutes").add_to_menu()
        .add_option("-30 minutes", "-m").set_emoji("⬅️").set_description("Use this to decrease the time by 30 minutes").add_to_menu()
        .add_option("+1 hour", "+h").set_emoji("➡️").set_description("Use this to increase the time by 1 hour").add_to_menu()
        .add_option("-1 hour", "-h").set_emoji("◀️").set_description("UsUse this to decrease the time by 1 hout=r").add_to_menu()
        .add_option("-1 day", "-d").set_emoji("⬅️").set_description("Use this to decrease the time by 1 day").add_to_menu()
        .add_option("+1 day", "+d").set_emoji("▶️").set_description("Use this to increase the time by 1 day").add_to_menu()
        .add_option("+1 week", "+w").set_emoji("➡️").set_description("Use this to increase the time by 1 week").add_to_menu()
        .add_option("-1 week", "-w").set_emoji("◀️").set_description("Use this to decrease the time by 1 week").add_to_menu()
        .add_to_container()
    )
    AddButtons=AdminPlugin.bot.rest.build_action_row()
    AddButtons.add_button(ButtonStyle.SUCCESS, "+w").set_label("+1 week").set_emoji("▶️").add_to_container()
    AddButtons.add_button(ButtonStyle.SUCCESS, "+d").set_label("+1 day").set_emoji("▶️").add_to_container()
    AddButtons.add_button(ButtonStyle.SUCCESS, "+h").set_label("+1 hour").set_emoji("▶️").add_to_container()
    AddButtons.add_button(ButtonStyle.SUCCESS, "+m").set_label("+30 minutes").set_emoji("▶️").add_to_container()
    AddButtons.add_button(ButtonStyle.PRIMARY, "Done").set_label("Done").set_emoji("✅").add_to_container()
    SubButtons=AdminPlugin.bot.rest.build_action_row()
    SubButtons.add_button(ButtonStyle.DANGER, "-w").set_label("-1 week").set_emoji("◀️").add_to_container()
    SubButtons.add_button(ButtonStyle.DANGER, "-d").set_label("-1 day").set_emoji("◀️").add_to_container()
    SubButtons.add_button(ButtonStyle.DANGER, "-h").set_label("-1 hour").set_emoji("◀️").add_to_container()
    SubButtons.add_button(ButtonStyle.DANGER, "-m").set_label("-30 minutes").set_emoji("◀️").add_to_container()
    os.environ['TZ'] = 'US/Eastern'
    time.tzset() 
    ts = round(time.time())
    ts -=ts%1800
    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
    await ctx.respond("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
    try:
        async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(('interaction.user.id', ctx.author.id)) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                    key = event.interaction.custom_id
                    if key == "Done":
                        embed = (Embed(title="Final times", description=f"timestamp: {ts}: <t:{ts}:F>")
                            .add_field(f"Default: `<t:{ts}>`",f"<t:{ts}>")
                            .add_field(f"Short Time: `<t:{ts}:t>`",f"<t:{ts}:t>")
                            .add_field(f"Long Time: `<t:{ts}:T>`",f"<t:{ts}:t>")
                            .add_field(f"Short Date: `<t:{ts}:d>`",f"<t:{ts}:d>")
                            .add_field(f"Long Date: `<t:{ts}:D>`",f"<t:{ts}:D>")
                            .add_field(f"Short Date/Time: `<t:{ts}:f>`",f"<t:{ts}:f>")
                            .add_field(f"Long Date/Time: `<t:{ts}:F>`",f"<t:{ts}:F>")
                            .add_field(f"Relative Time: `<t:{ts}:R>`",f"<t:{ts}:R>")
                        )
                        await ctx.edit_last_response(f"<t:{ts}",embed=embed, components=[])
                        return
                    elif key == "+w":
                        ts +=604800
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "+d":
                        ts +=86400 
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "+h":
                        ts +=3600
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "+m":
                        ts +=1800
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "-w":
                        ts -=604800
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "-d":
                        ts -=86400 
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "-h":
                        ts -=3600
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
                    elif key == "-m":
                        ts -=1800
                        embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                        await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed, components=[AddButtons,SubButtons])
    except asyncio.TimeoutError:
        await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])

def load(bot):bot.add_plugin(AdminPlugin)
def unload(bot):bot.remove_plugin(AdminPlugin)
