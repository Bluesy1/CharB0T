import json
import random
import re

import hikari
import lightbulb
from lightbulb import commands

with open("KethranToken.json") as t:
    token = json.load(t)['Token']
regex = r"kethran"

bot = lightbulb.BotApp(token=token, prefix="k", help_class=None, owner_ids=363095569515806722,case_insensitive_prefix_commands=True)



@bot.listen(hikari.GuildMessageCreateEvent)
async def on_message(event):
    if event.is_human:
        if event.channel_id in [901325983838244865, 878434694713188362]:
            if bool(re.search(regex,event.content,re.IGNORECASE|re.MULTILINE)):
                rand = random.randint(1,100)
                if rand <4:
                    await event.get_channel().send("Bork!")
                elif rand <8:
                    await event.get_channel().send("WOOF!")
                elif rand <12:
                    await event.get_channel().send("AROOOF!")
                elif rand <16:
                    await event.get_channel().send("HOOOWL!")
                elif rand <20:
                    await event.get_channel().send("Aroof")
                elif rand <24:
                    await event.get_channel().send("*Sniff Sniff Sniff*")
                elif rand <28:
                    await event.get_channel().send("*Does not care*")
                elif rand <32:
                    await event.get_channel().send("*I want scritches*")
                elif rand <36:
                    await event.get_channel().send("*is busy*")
                elif rand <40:
                    await event.get_channel().send("snuffles")
                elif rand <44:
                    await event.get_channel().send("snuffles apologetically")
                elif rand <48:
                    await event.get_channel().send("sits")
                elif rand <52:
                    await event.get_channel().send("lays down")
                elif rand <56:
                    await event.get_channel().send("chuffs")
                elif rand <60:
                    await event.get_channel().send("pants")
                elif rand <64:
                    await event.get_channel().send("plays dead")
                elif rand <68:
                    await event.get_channel().send("gives paw")
                elif rand <72:
                    await event.get_channel().send("rolls over")
                elif rand <76:
                    await event.get_channel().send("is adorable")
                elif rand <80:
                    await event.get_channel().send("whimpers")
                elif rand <84:
                    await event.get_channel().send("licks face")
                elif rand <88:
                    await event.get_channel().send("*Sits*")
                elif rand <92:
                    await event.get_channel().send("*is adorable*")
                elif rand <96:
                    await event.get_channel().send("pants")
                elif rand <=100:
                    await event.get_channel().send("**HOLY SHIT!**")
                    await event.get_channel().send("**HOLY SHIT!**")
                    await event.get_channel().send("**HOLY SHIT!**")

@bot.listen(hikari.DMMessageCreateEvent)
async def on_DMmessage(event):
    if event.is_human and event.content is not None and event.author_id==184524255197659136:
        channel = await bot.rest.fetch_channel(878434694713188362)
        await channel.send(event.content)

@bot.command()
@lightbulb.option("dice", "dice to roll", required=True)
@lightbulb.command("roll", "diceroller")
@lightbulb.implements(commands.PrefixCommand)
async def roll(ctx):
    arg = ctx.options.dice
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
                    await ctx.respond("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
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
                    await ctx.respond("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
        output = '`'
        for x in rolls:
            output += str(x) + ', '
        output = output[:-2]
        await ctx.respond("Kethran rolled `" +arg+"` got "+output+"` for a total value of: "+str(sum))        
    except:
        await ctx.respond("Error invalid argument: specified dice can only be d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
        return









bot.run()
