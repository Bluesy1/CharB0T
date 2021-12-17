import random

import lightbulb
from hikari.embeds import Embed
from lightbulb import commands
from lightbulb.checks import has_roles

DicePlugin = lightbulb.Plugin("DicePlugin")



@DicePlugin.command
@lightbulb.add_checks(lightbulb.Check(has_roles(338173415527677954,253752685357039617,225413350874546176,914969502037467176,mode=any)))
@lightbulb.command("roll", "roll group")
@lightbulb.implements(commands.SlashCommandGroup)
async def roll(ctx) -> None: await ctx.respond("invoked roll")

@roll.child
@lightbulb.option("name", "name for roll", type=str, required=True)
@lightbulb.option("amount", "How many dice to roll, min 3", type=int, required=True)
@lightbulb.option("success", "Minimum value to get a success", type=int, choices=[5,6,7,8,9,10], required=True)
@lightbulb.option("failure", "Maximum value to count as a failure", type=int, choices=[1,2,3,4], required=True)
@lightbulb.option("tag", "Tag of RPO roll is for", type=str, required=True)
@lightbulb.command("wod", "rolls WOD style with custom paramters", inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    amount = ctx.options.amount;failure = ctx.options.failure;name = ctx.options.name;tag = ctx.options.tag;success = ctx.options.success
    if amount <= 3:ctx.respond("<:KSplodes:896043440872235028>: Minimum amount of dice to roll is 3.")
    i=0
    successes=0
    failures=0
    rolls = list()
    while i<amount:
        roll = random.randint(1,10)
        if roll <= int(failure):
            failures+=1
        elif roll >= int(success):
            successes+=1
        rolls.append(roll)
        i+=1
    numTens = 0
    for i in rolls:
        if i==10:
            numTens+=1
    CritSuccesses = (numTens-(numTens%2))
    netSuccesses = successes-failures+CritSuccesses
    output = '`'
    for x in rolls:
        output += str(x) + ', '
    output = output[:-2]
    output+='`'
    embed = None
    if netSuccesses>0:
        embed=Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color="0x00ff00").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url) 
    elif netSuccesses<0:
        embed=Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color="0xff0000").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url) 
    elif netSuccesses==0:
        embed=Embed(title=name+" Roll", description="**"+str(tag).upper()+"** rolled "+str(amount)+"d10s, getting "+output+", totaling `"+str(successes)+"` successes, `"+str(CritSuccesses)+"` crit successes and `"+ str(failures) +"` failures, for a net of **`"+str(netSuccesses)+"`** successes.", color="0x0000ff").set_footer(text=f"Requested by {ctx.member.display_name}",icon=ctx.member.avatar_url) 
    else:
        return
    await ctx.respond(embed=embed)

@roll.child
@lightbulb.option("dice","Dice to roll, accepts d2s, d4s, d6s, d8s, d10s, d12s, d20s, and d100s.",required=True)
@lightbulb.command("standard", "D&D Standard Array 7 Dice roller, plus coin flips", inherit_checks=True)
@lightbulb.implements(commands.SlashSubCommand)
async def command(ctx):
    arg = ctx.options.dice
    if "+" in arg:dice = arg.split("+")
    else:dice = [str(arg)]
    try:
        sum = 0
        rolls = list()
        allowedDice = [2,4,6,8,10,12,20,100]
        for die in dice:
            if 'd' in die:
                if int(die[die.find('d')+1:]) not in allowedDice:
                    await ctx.respond("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
                try:numRolls = int(die[:die.find('d')])
                except:numRolls = 1
                i = 1
                roll = 0
                while i <= numRolls:
                    roll += random.randint(1, int(die[die.find('d')+1:]))
                    i += 1
                sum += roll
                rolls.append(roll)
            else:
                try:
                    rolls.append(int(die))
                    sum += int(die)
                except:
                    await ctx.respond("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                    return
        output = '`'
        for x in rolls:
            output += str(x) + ', '
        output = output[:-2]
        await ctx.respond(ctx.author.mention+": Rolled `" +arg+"` got "+output+"` for a total value of: "+str(sum))        
    except:
        await ctx.respond("<:KSplodes:896043440872235028> Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
        return

"""
@DicePlugin.command
@lightbulb.option("message","message to start after", type=int)
@lightbulb.option("count","number to pick", type=int)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("giveaway", "picks a message")
@lightbulb.implements(commands.PrefixCommand)
async def command(ctx):
    channel = await DicePlugin.bot.rest.fetch_channel(687817008355737606)
    messages = channel.fetch_history(after=ctx.options.message)
    message = await messages.enumerate()
    i=0;counts=ctx.options.count
    while i<counts:
        num=random.randrange(0,len(message)-1,1)
        message2 = message[num]
        (count, messageR) = message2
        await messageR.respond(f"Chosen User: {messageR.author.mention}", reply=messageR.id)
        await ctx.respond(f"Chosen message was count: {count+1}, author: {messageR.author.mention}, link: {messageR.make_link(ctx.guild_id)}")
        message.pop(num)
        i+=1
        await asyncio.sleep(5)
"""

def load(bot):bot.add_plugin(DicePlugin)
def unload(bot):bot.remove_plugin(DicePlugin)
