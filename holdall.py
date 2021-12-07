
@client.command()
async def all(ctx):
    data2 = sfs.parse_savefile('completed.sfs')
    tech = data2['GAME']['SCENARIO'][7]['Tech'] #6 current, 7 new
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
        maxLen = max(maxLen, len(techdict[i]))
    for i in list(techdict.keys()):
        if techdict[i] != None:
            if type(techdict[i]) == str:
                techdict[i] = [techdict[i]]
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
                        if bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
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
                if bool(re.search(r"Aerodynamics",dfOut.iloc[onRow,onCol],re.IGNORECASE|re.MULTILINE)):
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
                onCol+=1
            onCol=0
            onRow+=1
            colorList.append(tempList)
        render_mpl_table_colors_pdf(export_pdf, dfOut[:-1],Colors=colorList, header_columns=0, col_width=7.5)
        await ctx.author.send(file=discord.File(r'Tables.pdf'))
    plt.close('all')

