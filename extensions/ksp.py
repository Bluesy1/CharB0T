import asyncio
import json
import os
import re
from hikari.commands import CommandChoice, OptionType
from hikari.events.interaction_events import InteractionCreateEvent
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle

import lightbulb
import matplotlib.pyplot as plt
import pandas as pd
import sfsutils as sfs
from auxone import (author_check, checks, part_check, render_mpl_table_colors,
                    render_mpl_table_colors_pdf)
from hikari import Embed
from lightbulb import commands
from matplotlib.backends.backend_pdf import PdfPages

KSPPlugin = lightbulb.Plugin("KSPPlugin")



@KSPPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.Punished))
@lightbulb.command("parts", "parts group")
@lightbulb.implements(commands.SlashCommandGroup)
async def parts(ctx) -> None: await ctx.respond("invoked parts")

@parts.child
@lightbulb.command("key","key for parts table", inherit_checks=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    df = pd.DataFrame()
    colors = ["dark teal","rose","chartreuse","blue","goldenrod","grape","kelly green","ocean blue","puke green","light violet","robin's egg blue","puce","neon green","canary yellow","light navy","bright pink","rust","grey","periwinkle","dark red"]
    df['Color'] = colors
    df['Type'] = ["Aerodynamics","Balloon","Camera","Capsule","Comms","Control","Coupling","Engine","Equipment","Landing","Lights","Mining","Parachute","Power","Probe","Science","Storage","Structure","Tank","Thermal"]
    colorList = list()
    for i in colors:
        subList = ["xkcd:"+i,"xkcd:"+i]
        colorList.append(subList)
    render_mpl_table_colors(df,Colors=colorList, header_columns=0, col_width=5.0, alpha=0.5)
    message = await ctx.author.send("see attached:")
    await message.edit(attachment='table.png')
    os.remove('table.png')

@parts.child
@lightbulb.command("all","All parts in the game, only unlocked ones will be highlighted.", inherit_checks=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    await ctx.defer(hidden=True)
    with open('parts.json') as p:
        partsDict = json.load(p)
    tech = sfs.parse_savefile('completed.sfs')['GAME']['SCENARIO'][7]['Tech'] #6 current, 7 new
    tech2 = sfs.parse_savefile('persistent.sfs')['GAME']['SCENARIO'][6]['Tech']
    length = len(tech)
    i = 0
    techdict = {}
    while i < length:
        if tech[i]['id'] not in ['tremendousEfficiencyPropulsion', 'veryHighEfficiencyPropulsion', 'advColonization', 'exoticRadiators', 'microwavePowerTransmission', 'exoticElectricalSystems', 'experimentalElectricalSystems', 'highPowerElectricalSystems', 'exoticPlasmaPropulsion', 'appliedHighEnergyPhysics', 'highEnergyScience', 'scientificOutposts', 'resourceExploitation', 'advOffworldMining', 'advAerospaceEngineering', 'expAircraftEngines', 'offworldManufacturing', 'extremeFuelStorage', 'colossalRocketry', 'giganticRocketry', 'fusionRockets', 'ultraHighEnergyPhysics', 'unifiedFieldTheory', 'antimatterPower', 'quantumReactions', 'exoticReactions', 'advFusionReactions', 'fusionPower', 'experimentalMotors']:
            techdict.update({tech[i]['id']:tech[i]['part']})
        i += 1
    dfOut=pd.DataFrame()
    maxLen = 0
    for i in list(techdict.keys()):
        #techdict[i] = [re.sub(r".v[1-9]","",item) for item in techdict[i]]
        if i in ["highEfficiencyPropulsion","heatManagementSystems","expGriddedThrusters","longTermScienceTech","heavyLanders","specializedLanders","exoticNuclearPropulsion","exoticNuclearPower","advNuclearPower","largeNuclearPower","nuclearPower","aerospaceTech"]:
            techdict[i] = [techdict[i]]
        elif type(techdict[i])==list:
            techdict[i] = list(set(techdict[i]))
        elif type(techdict[i])==str:
            techdict[i] = [techdict[i]]
        maxLen = max(maxLen, len(techdict[i]))
    for i in list(techdict.keys()):
        if techdict[i] != None:
            diff = maxLen-len(techdict[i])
            while diff >0:
                techdict[i].append('')
                diff = maxLen-len(techdict[i])
    columns = 0
    with PdfPages(r'Tables.pdf') as export_pdf:
        for i in list(techdict.keys()):
            dfOut[i] = techdict[i]
            columns +=1
            if columns==5:
                dfOut.drop_duplicates(inplace=True)
                colDepth = len(dfOut.columns.tolist())
                rowDepth = len(dfOut.index.tolist())-1
                onRow = 0
                onCol = 0
                colorList = list()
                while onRow<rowDepth:
                    tempList = list()
                    while onCol<colDepth:
                        if part_check(tech2,dfOut.iloc[onRow,onCol]):
                            tempList.append("w")
                        elif bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:dark teal")
                        elif bool(re.search(r"balloon",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:rose")
                        elif bool(re.search(r"Camera",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:chartreuse")
                        elif bool(re.search(r"Capsule ",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:blue")
                        elif bool(re.search(r"antenna",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:goldenrod")
                        elif bool(re.search(r"comms",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:goldenrod")
                        elif bool(re.search(r"Control",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:grape")
                        elif bool(re.search(r"Coupling",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:kelly green")
                        elif bool(re.search(r"Engine",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:ocean blue")
                        elif bool(re.search(r"Equipment",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:puke green")
                        elif bool(re.search(r"Landing",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:light violet")
                        elif bool(re.search(r"Lights",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:robin's egg blue")
                        elif bool(re.search(r"Mining",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:puce")
                        elif bool(re.search(r"Parachute",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:neon green")
                        elif bool(re.search(r"Power",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:canary yellow")
                        elif bool(re.search(r"Probe",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:light navy")
                        elif bool(re.search(r"Science",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:bright pink")
                        elif bool(re.search(r"Sensor",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:bright pink")
                        elif bool(re.search(r"Storage",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:rust")
                        elif bool(re.search(r"Structure",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:grey")
                        elif bool(re.search(r"Tank",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:periwinkle")
                        elif bool(re.search(r"Thermal",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                            tempList.append("xkcd:dark red")
                        else:
                            tempList.append('xkcd:cloudy blue')
                        try:dfOut.iloc[onRow,onCol] = partsDict[dfOut.iloc[onRow,onCol]]['name']
                        except:dfOut.iloc[onRow,onCol]=dfOut.iloc[onRow,onCol]
                        onCol+=1
                    onCol=0
                    onRow+=1
                    colorList.append(tempList)
                render_mpl_table_colors_pdf(export_pdf, dfOut[:-1],colorList, header_columns=0, col_width=7.5)
                dfOut = pd.DataFrame(None)
                columns = 0
        dfOut.drop_duplicates(inplace=True)
        colDepth = len(dfOut.columns.tolist())
        rowDepth = len(dfOut.index.tolist())-1
        onRow = 0
        onCol = 0
        colorList = list()
        while onRow<rowDepth:
            tempList = list()
            while onCol<colDepth:
                if part_check(tech2,dfOut.iloc[onRow,onCol]):
                    tempList.append("w")
                elif bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:dark teal")
                elif bool(re.search(r"balloon",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:rose")
                elif bool(re.search(r"Camera",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:chartreuse")
                elif bool(re.search(r"Capsule ",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:blue")
                elif bool(re.search(r"antenna",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:goldenrod")
                elif bool(re.search(r"comms",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:goldenrod")
                elif bool(re.search(r"Control",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:grape")
                elif bool(re.search(r"Coupling",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:kelly green")
                elif bool(re.search(r"Engine",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:ocean blue")
                elif bool(re.search(r"Equipment",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:puke green")
                elif bool(re.search(r"Landing",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:light violet")
                elif bool(re.search(r"Lights",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:robin's egg blue")
                elif bool(re.search(r"Mining",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:puce")
                elif bool(re.search(r"Parachute",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:neon green")
                elif bool(re.search(r"Power",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:canary yellow")
                elif bool(re.search(r"Probe",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:light navy")
                elif bool(re.search(r"Science",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:bright pink")
                elif bool(re.search(r"Sensor",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:bright pink")
                elif bool(re.search(r"Storage",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:rust")
                elif bool(re.search(r"Structure",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:grey")
                elif bool(re.search(r"Tank",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:periwinkle")
                elif bool(re.search(r"Thermal",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
                    tempList.append("xkcd:dark red")
                else:
                    tempList.append('xkcd:cloudy blue')
                try:dfOut.iloc[onRow,onCol] = partsDict[dfOut.iloc[onRow,onCol]]['name']
                except:dfOut.iloc[onRow,onCol]=dfOut.iloc[onRow,onCol]
                onCol+=1
            onCol=0
            onRow+=1
            colorList.append(tempList)
        render_mpl_table_colors_pdf(export_pdf, dfOut[:-1],Colors=colorList, header_columns=0, col_width=10)
    plt.close('all')
    message = await ctx.author.send("See attached:")
    await message.edit(attachement='Tables.pdf')

@parts.child
@lightbulb.command("upgrades","All unlocked upgrades", inherit_checks=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    tech = sfs.parse_savefile('persistent.sfs')['GAME']['SCENARIO'][2]['UPGRADES']['Unlocks']
    length = len(tech);i=0;embed = Embed(title="Upgrades", description="Unlocked Upgrades"); keys = list(tech.keys())
    while i < length:
        #techdict.update({tech[i]['id']:tech[i]['part']})
        embed = embed.add_field(f"Upgrade {i+1}",keys[i],inline=True)
        i += 1
    #await ctx.respond(str(list(tech.keys()))[1:-1].replace("'", ''),hidden=True)
    await ctx.author.send(embed=embed)

@parts.child
@lightbulb.command("nodes","All researched nodes", inherit_checks=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    tech = sfs.parse_savefile('persistent.sfs')['GAME']['SCENARIO'][6]['Tech']
    length = len(tech)
    i = 0
    #techdict = {}
    embed = Embed(title="Nodes", description="Unlocked Nodes")
    while i < length:
        #techdict.update({tech[i]['id']:tech[i]['part']})
        embed = embed.add_field(f"Node {i+1}",tech[i]['part'],inline=True)
        i += 1
    #strlist = str(techdict.keys())[11:-2]
    #strlist = strlist.replace("'", '')
    #print(strlist)
    #await ctx.respond(strlist,hidden=True)
    await ctx.author.send(embed=embed)

@KSPPlugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("test","test")
@lightbulb.implements(commands.PrefixCommand)
async def command(ctx):
    YesNoButtons=KSPPlugin.bot.rest.build_action_row()
    YesNoButtons.add_button(ButtonStyle.SUCCESS, "Yes").set_label("Yes").set_emoji("✅").add_to_container()
    YesNoButtons.add_button(ButtonStyle.DANGER, "No").set_label("No").set_emoji("❌").add_to_container()
    EditMenu = KSPPlugin.bot.rest.build_action_row()
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
        .add_to_container
    )
    await ctx.respond("choose an option:", components=[YesNoButtons,])
    try:
        async with KSPPlugin.bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
            print(event)
    except asyncio.TimeoutError:
        await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])


"""
@KSPPlugin.command
@lightbulb.add_checks(lightbulb.Check(checks.check_publisher))
@lightbulb.option("title","This is the title of the embed",required=True)
@lightbulb.option("Body","This is the body of the command", required=True)
@lightbulb.option("Color","Embed color", choices=[
    CommandChoice(name="Breaking News",value="#FEE75C"),
    CommandChoice(name="Financial",value="#57F287"),
    CommandChoice(name="Patents/Info Sector Updates",value="#5865F2"),
    CommandChoice(name="Other",value="#BCC0C0")],required=True)
@lightbulb.option("time","This is the publishing time info (Must include Published at: if you want that to show up.)", required=True)
@lightbulb.option('channel', 'channel to post embed to', type=OptionType.CHANNEL, required=True)
@lightbulb.option("logo", "use logo?", type=OptionType.BOOLEAN, requied=True)
@lightbulb.option("author", "Article Author, default Author Kerman", default="Author Kerman", required=False)
@lightbulb.option("image", "URL of image to use as logo.", default=None, required=False)
async def command(ctx):
    publishTo=ctx.options.channel;morePars=True;body1=ctx.options.body;title=ctx.options.title;color=ctx.options.color
    addImage = False; author=ctx.options.author; time=ctx.options.time; image = ctx.options.image; footer=True; hasAuthor=True
    hasLogo = ctx.options.logo
    embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
    if ctx.options.logo:embed.set_thumbnail(image)
    YesNoButtons=KSPPlugin.bot.rest.build_action_row()
    YesNoButtons.add_button(ButtonStyle.SUCCESS, "Yes").set_label("Yes").set_emoji("✅").add_to_container()
    YesNoButtons.add_button(ButtonStyle.DANGER, "No").set_label("No").set_emoji("❌").add_to_container()
    while morePars:
        await ctx.respond("Do you want to add another paragraph?", embed=embed, components=[YesNoButtons, ])
        try:
            async with KSPPlugin.bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                key = event.interaction.custom_id
                if key == "Yes":
                    await ctx.edit_last_response("Please enter your next paragraph:, embed=None, components=[]")
                    try:
                        async with KSPPlugin.bot.stream(GuildMessageCreateEvent, timeout=60).filter(('author_id', ctx.author.id)) as stream2:
                            async for event2 in stream2:
                                await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                            add = " \n \n "+(str(event2.message.content))
                            if (len(body1+add)>4096):
                                await ctx.edit_last_response("Error, too long. ignoring last entry.", embed=None, components=[])
                                await asyncio.sleep(5)
                                break
                            body1 += add
                            embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
                            if ctx.options.logo:embed.set_thumbnail(image)
                            msg = await ctx.send("Paragraph added.", embed=embed, components=[])
                            await asyncio.sleep(5)
                            if len(body1) >=3900:
                                await ctx.edit_last_response("Max length Reached, No more paragraphs allowed", embed=None, components=[])
                                await asyncio.sleep(5)
                                break
                    except asyncio.TimeoutError:
                         await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])
                elif key == "No":
                    await ctx.edit_last_response("Done adding paragraphs.",embed=None, components=[])
                    await asyncio.sleep(5)
                    morePars=False
        except asyncio.TimeoutError:
            await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])
    await ctx.edit_last_response("Add Image?",embed=None, components=[YesNoButtons, ])
    try:
        async with KSPPlugin.bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
            key = event.interaction.custom_id
            if key == "No":
                await ctx.edit_last_response("No Image.",embed=None, components=[])
                await asyncio.sleep(5)
            elif key== "Yes":
                await ctx.edit_last_response("Please upload the photo:",embed=None, components=[])
                try:
                    async with KSPPlugin.bot.stream(GuildMessageCreateEvent, timeout=60).filter(('author_id', ctx.author.id)) as stream2:
                        async for event2 in stream2:
                            await event2.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                        addedImage = event2.message.attachments[0].url
                        addImage = True
                except asyncio.TimeoutError:
                        await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])
                # msg = await client.wait_for("message", check=author_check(ctx.author), timeout=180)
    except asyncio.TimeoutError:
        await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])
    embed=Embed(title=title, description=body1, color=color).set_author(name=author).set_footer(text=time)
    if ctx.options.logo:embed.set_thumbnail(url=image)
    if addImage:embed.set_image(url=addedImage)
    EditMenu = KSPPlugin.bot.rest.build_action_row()
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
        .add_to_container
    )   
    while True:
        embed=Embed(title=title, description=body1, color=color)
        if hasAuthor:embed.set_author(name=author)
        if footer:embed.set_footer(text=time)
        if hasLogo:embed.set_thumbnail(url=image)
        if addImage:embed.set_image(url=addedImage)
        await ctx.edit_last_response("Is this good?",embed=embed, components=[EditMenu, ])
        try:
            async with KSPPlugin.bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                key = event.interaction.custom_id
        except asyncio.TimeoutError:
            await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])
        if btn.label == "Yes":
            await publishTo.send(embed=embed)
            break
        elif btn.label == "No":
            btn = await (
                await ctx.send(content = "What to change?", components=[
                    Button("Title", "Title", color='blurple'), Button("Body", "Body", color='blurple'), Button("Footer", "Footer", color='blurple'), Button("Author", "Author", color='blurple')
                ])
            ).wait_for("button", client)
        if btn.label == "Title":
            await ctx.send("Please enter the new Title:")
            msg = await client.wait_for("message", check=author_check(ctx.author), timeout=180)
            title = msg.content
            embed=discord.Embed(title=title, description=body1, color=color)
            embed.set_author(name=author)
            embed.set_thumbnail(url=image)
            if addImage:
                embed.set_image(url=addedImage)
            embed.set_footer(text=time)
        elif btn.label == "Body":
            await ctx.send("Re-adding paragraphs")
            body1 = str()
            while True:
                btn = await (
                    await ctx.send("Do you want to add another paragraph?", components=[
                        Button("another", "Yes", color='green'), Button("done", "No", color='red')
                    ])
                ).wait_for("button", client)
                if btn.author.id != ctx.author.id:
                    await ctx.send("Error: wrong user. User <@!" +str(ctx.author.id)+"> expected. Cancelling operation.")
                    return
                elif btn.author.id == ctx.author.id:
                    if btn.label == "No":
                        await ctx.send("Done adding paragraphs")
                        break
                    elif btn.label == "Yes":
                        await ctx.send("Please enter your next paragraph:")
                        msg = await client.wait_for("message", check=author_check(ctx.author), timeout=180)
                        add = " \n \n "+(str(msg.content))
                        if (len(body1+add)>4096):
                            await ctx.send("Error, too long. ignoring last entry.")
                            break
                        body1 += add
                        msg = await msg.channel.send("Paragraph added.")
                        if len(body1) >=4000:
                            await msg.edit("Max length Reached")
                            break
            embed=discord.Embed(title=title, description=body1, color=color)
            embed.set_author(name=author)
            embed.set_thumbnail(url=image)
            if addImage:
                embed.set_image(url=addedImage)
            embed.set_footer(text=time)
        elif btn.label == "Footer":
            await ctx.send("Please enter new footer:")
            msg = await client.wait_for("message", check=author_check(ctx.author), timeout=180)
            time = msg.content
            embed.set_footer(text=time)
        elif btn.label == "Author":
            await ctx.send("Please enter new author:")
            msg = await client.wait_for("message", check=author_check(ctx.author), timeout=180)
            author = msg.content
            embed.set_author(name=author)
    await ctx.send("Complete.")
"""
def load(bot):bot.add_plugin(KSPPlugin)
def unload(bot):bot.remove_plugin(KSPPlugin)
