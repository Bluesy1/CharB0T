import json
import os
import re

import lightbulb
import matplotlib.pyplot as plt
import pandas as pd
import sfsutils as sfs
from auxone import (checks, part_check, render_mpl_table_colors,
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
    await ctx.respond(Embed(title="Key").set_image('table.png'),flags=64)
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

def load(bot):bot.add_plugin(KSPPlugin)
def unload(bot):bot.remove_plugin(KSPPlugin)
