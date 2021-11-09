"""
@ui.slash.subcommand(base_names="start", name="vote", description="Starts a new vote on a part values in a node, and ends the previous one",options=[
    SlashOption(str, name="override", description="Optional. Use to choose a specific node")], guild_ids=[225345178955808768], guild_permissions={
    225345178955808768: SlashPermission(allowed={
            "225413350874546176": SlashPermission.ROLE,
            "253752685357039617": SlashPermission.ROLE,
            "338173415527677954": SlashPermission.ROLE},forbidden={
            "225345178955808768": SlashPermission.ROLE})})
async def command(ctx, override=None):
    channel = client.get_channel(906643670168653835)
    node = ""
    data2 = sfs.parse_savefile('persistent.sfs')
    UnlockedTech = data2['GAME']['SCENARIO'][6]['Tech'] #6 current, 7 new
    data2 = sfs.parse_savefile('completed.sfs')
    Alltech = data2['GAME']['SCENARIO'][7]['Tech'] #6 current, 7 new
    length = len(Alltech)
    i = 0
    techdict = {}
    while i < length:
        if Alltech[i]['id'] not in ['tremendousEfficiencyPropulsion', 'veryHighEfficiencyPropulsion', 'advColonization', 'exoticRadiators', 'microwavePowerTransmission', 'exoticElectricalSystems', 'experimentalElectricalSystems', 'highPowerElectricalSystems', 'exoticPlasmaPropulsion', 'appliedHighEnergyPhysics', 'highEnergyScience', 'scientificOutposts', 'resourceExploitation', 'advOffworldMining', 'advAerospaceEngineering', 'expAircraftEngines', 'offworldManufacturing', 'extremeFuelStorage', 'colossalRocketry', 'giganticRocketry', 'fusionRockets', 'ultraHighEnergyPhysics', 'unifiedFieldTheory', 'antimatterPower', 'quantumReactions', 'exoticReactions', 'advFusionReactions', 'fusionPower', 'experimentalMotors']:
            i2 = 0
            length2 = len(UnlockedTech)
            notUnlocked = True
            while i2 < length2:
                if UnlockedTech[i2]['id'] == Alltech[i]['id']:
                    notUnlocked = False
                i2+=1
            if notUnlocked:
                techdict.update({Alltech[i]['id']:Alltech[i]['part']})
        i += 1
    length = len(UnlockedTech)
    nodes = len(techdict)-1
    if override != None:
        node = techdict[override]
        with open('votes.json') as v:
            votes = json.load(v)
        with open('parts.json') as p:
            partsDict = json.load(p)
        innerdict = {}
        partList = list()
        for i in node:
            if re.search(r'rocket', i, re.MULTILINE|re.IGNORECASE) or re.search(r'engine', i, re.MULTILINE|re.IGNORECASE) or re.search(r'bosters', i, re.MULTILINE|re.IGNORECASE) or re.search(r'thrusters', i, re.MULTILINE|re.IGNORECASE) or re.search(r'procedural', i, re.MULTILINE|re.IGNORECASE):
                i
            else:
                try:name = partsDict[i]['name']
                except:name=i
                innerdict.update({name:{}})
        votes.update({override:innerdict})
        votes['open'] = override
        await channel.send("Community opinion now on parts in node: " + str(override))
        with open('votes.json','w') as v:
            json.dump(votes,v)
    elif override == None:
        nodenum = random.randint(0,nodes)
        node = techdict[list(techdict.keys())[nodenum]]
        with open('votes.json') as v:
            votes = json.load(v)
        with open('parts.json') as p:
            partsDict = json.load(p)
        innerdict = {}
        partList = list()
        for i in node:
            if re.search(r'rocket', i, re.MULTILINE|re.IGNORECASE) or re.search(r'engine', i, re.MULTILINE|re.IGNORECASE) or re.search(r'bosters', i, re.MULTILINE|re.IGNORECASE) or re.search(r'thrusters', i, re.MULTILINE|re.IGNORECASE) or re.search(r'procedural', i, re.MULTILINE|re.IGNORECASE):
                i
            else:
                try:name = partsDict[i]['name']
                except:name=i
                innerdict.update({name:{}})
        votes.update({list(techdict.keys())[nodenum]:innerdict})
        votes['open'] = list(techdict.keys())[nodenum]
        await channel.send("Community opinion now on parts in node: " + str(list(techdict.keys())[nodenum]))
        await channel.send("Parts in the node: "+str(techdict[str(list(techdict.keys())[nodenum])]))
        with open('votes.json','w') as v:
            json.dump(votes,v)
  
@ui.slash.command(name='vote', description="Give your opinion on the value of the parts in the current node.", guild_ids=[225345178955808768]
    ,guild_permissions={225345178955808768: SlashPermission(allowed={"225345178955808768": SlashPermission.ROLE},forbidden={"684936661745795088":SlashPermission.ROLE,"676250179929636886":SlashPermission.ROLE})})
async def vote(ctx):
    if a.channel_check(ctx,[906643670168653835])!=True:
        return
    with open('votes.json') as v:
        votes = json.load(v)
    nodeDict = votes[votes['open']]
    if a.author_check2(ctx, list(map(int, list(nodeDict[list(nodeDict.keys())[0]].keys())))):
        return
    msg = await ctx.send("Reminder: You have to go on the same difficulty as everyone else here. Vote with that in mind.")
    await asyncio.sleep(2)
    for i in list(nodeDict.keys()):
        await msg.edit("Part **"+str(i)+"**: What do you think the difficulty of the part is is from 1 to 1000?")
        msg2 = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
        await msg2.delete()
        try:
            cont = int(''.join(list(filter(str.isdigit, msg2.content))))
            if cont <1:
                cont = 1
            elif cont>1000:
                cont = 1000
        except:
            cont='nan'
        await asyncio.sleep(1)
        nodeDict[i].update({str(msg2.author.id):cont})
    votes[votes['open']] = nodeDict
    with open('votes.json','w') as v:
        json.dump(votes,v)
    df = pd.read_csv(UserListURL)
    df['userID'] = df['userID'].astype(str)
    df['new'] = df['userID']
    df = df.set_index('new');
    df.loc[str(ctx.author.id), 'Coin Amount'] += 200
    gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
    # APPEND DATA TO SHEET 
    set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
    await msg.edit("Thank you for your time, you have been rewarded 200 coins.")

@client.command()
async def vote(ctx):
    if a.channel_check(ctx,[906643670168653835])!=True:
        return
    elif a.role_check(ctx, [676250179929636886,684936661745795088]):
        return
    with open('votes.json') as v:
        votes = json.load(v)
    nodeDict = votes[votes['open']]
    if a.author_check2(ctx, list(map(int, list(nodeDict[list(nodeDict.keys())[0]].keys())))):
        return
    msg = await ctx.send("Reminder: You have to go on the same difficulty as everyone else here. Vote with that in mind.")
    await asyncio.sleep(2)
    for i in list(nodeDict.keys()):
        await msg.edit("Part **"+str(i)+"**: What do you think the difficulty of the part is is from 1 to 1000?")
        msg2 = await client.wait_for("message", check=a.author_check(ctx.author), timeout=180)
        await msg2.delete()
        try:
            cont = int(''.join(list(filter(str.isdigit, msg2.content))))
            if cont <1:
                cont = 1
            elif cont>1000:
                cont = 1000
        except:
            cont='nan'
        await asyncio.sleep(1)
        nodeDict[i].update({str(msg2.author.id):cont})
    votes[votes['open']] = nodeDict
    with open('votes.json','w') as v:
        json.dump(votes,v)
    try:
        df = pd.read_csv(UserListURL)
        df['userID'] = df['userID'].astype(str)
        df['new'] = df['userID']
        df = df.set_index('new');
        df.loc[str(ctx.author.id), 'Coin Amount'] += 200
        gc = gspread.oauth(credentials_filename='credentials.json', authorized_user_filename='authorized_user.json') #gets credentials
        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
        # APPEND DATA TO SHEET 
        set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
    finally: await msg.edit("Thank you for your time, you have been rewarded 200 coins, if eligible.")

@client.command()
async def graph(ctx, node=None):
    if not a.role_check(ctx,[338173415527677954,253752685357039617,225413350874546176]):
        return
    with open('votes.json') as v:
        votes = json.load(v)
    if node is None:
        ctx.send("The list of nodes are:"+str(list(votes.keys())[1:]))
        return
    try:trueVotes = votes[node]
    except: await ctx.send("Error, that node is not an option. The list of nodes are:"+str(list(votes.keys())[1:]))
    name = node+".pdf"
    gh.graph(name,trueVotes)
    await ctx.send(file=discord.File(name))
"""