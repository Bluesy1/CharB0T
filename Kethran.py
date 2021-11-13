from discord import client
from discord.ext import commands
import random
import json
import re

from discord.gateway import EventListener

with open("KethranToken.json") as t:
    token = json.load(t)['Token']
regex = r"kethran"
client = commands.Bot(command_prefix='k')
@client.event
async def on_message(ctx):
    await client.process_commands(ctx)
    if ctx.author != client.user:
        if ctx.channel.id in [901325983838244865, 878434694713188362]:
            if bool(re.search(regex,ctx.content,re.IGNORECASE|re.MULTILINE)):
                rand = random.randint(1,100)
                if rand <4:
                    await ctx.channel.send("Bork!")
                elif rand <8:
                    await ctx.channel.send("WOOF!")
                elif rand <12:
                    await ctx.channel.send("AROOOF!")
                elif rand <16:
                    await ctx.channel.send("HOOOWL!")
                elif rand <20:
                    await ctx.channel.send("Aroof")
                elif rand <24:
                    await ctx.channel.send("*Sniff Sniff Sniff*")
                elif rand <28:
                    await ctx.channel.send("*Does not care*")
                elif rand <32:
                    await ctx.channel.send("*I want scritches*")
                elif rand <36:
                    await ctx.channel.send("*is busy*")
                elif rand <40:
                    await ctx.channel.send("snuffles")
                elif rand <44:
                    await ctx.channel.send("snuffles apologetically")
                elif rand <48:
                    await ctx.channel.send("sits")
                elif rand <52:
                    await ctx.channel.send("lays down")
                elif rand <56:
                    await ctx.channel.send("chuffs")
                elif rand <60:
                    await ctx.channel.send("pants")
                elif rand <64:
                    await ctx.channel.send("plays dead")
                elif rand <68:
                    await ctx.channel.send("gives paw")
                elif rand <72:
                    await ctx.channel.send("rolls over")
                elif rand <76:
                    await ctx.channel.send("is adorable")
                elif rand <80:
                    await ctx.channel.send("whimpers")
                elif rand <84:
                    await ctx.channel.send("licks face")
                elif rand <88:
                    await ctx.channel.send("*Sits*")
                elif rand <92:
                    await ctx.channel.send("*is adorable*")
                elif rand <96:
                    await ctx.channel.send("pants")
                elif rand <=100:
                    await ctx.channel.send("**HOLY SHIT!**")
                    await ctx.channel.send("**HOLY SHIT!**")
                    await ctx.channel.send("**HOLY SHIT!**")

@client.command()
async def roll(ctx, dice):
    arg = dice
    if "+" in arg:
        dice = arg.split("+")
    #elif arg == 'patent':
    #    dice = ['','','']
    else:
        dice = [str(arg)]
    try:
        sum = 0
        rolls = list()
        allowedDice = [4,6,8,10,12,20,100]
        for die in dice:
            if 'd' in die:
                if int(die[die.find('d')+1:]) not in allowedDice:
                    await ctx.send("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
                try:
                    numRolls = int(die[:die.find('d')])
                except:
                    numRolls = 1
                i = 1
                while i <= numRolls:
                    roll = random.randint(1, int(die[die.find('d')+1:]))
                    rolls.append(roll)
                    sum += roll
                    i += 1
            else:
                try:
                    rolls.append(int(die))
                    sum += int(die)
                except:
                    await ctx.send("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
        output = '`'
        for x in rolls:
            output += str(x) + ', '
        output = output[:-2]
        await ctx.send("Kethran rolled `" +arg+"` got "+output+"` for a total value of: "+str(sum))        
    except:
        await ctx.send("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
        return

client.run(token)