def main():
    import json
    import os
    import random
    import re

    import hikari
    import lightbulb
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from lightbulb import commands

    if os.name != "nt":
        import uvloop
        uvloop.install()

    with open("KethranToken.json") as file:
        token = json.load(file)['Token']
    regex = r"kethran"

    bot = lightbulb.BotApp(token=token, prefix="k", help_class=None, owner_ids=363095569515806722,case_insensitive_prefix_commands=True)
    sched = AsyncIOScheduler()
    sched.start()


    @bot.listen(hikari.GuildMessageCreateEvent)
    async def on_guild_message(event: hikari.GuildMessageCreateEvent):
        if event.is_human:
            if event.channel_id in [901325983838244865, 878434694713188362]:
                if re.search(regex,event.content,re.IGNORECASE|re.MULTILINE) is not None:
                    rand = random.randint(1,100)
                    if rand <4:
                        await event.get_channel().send("Bork!",reply=event.message_id,mentions_reply=True)
                    elif rand <8:
                        await event.get_channel().send("WOOF!",reply=event.message_id,mentions_reply=True)
                    elif rand <12:
                        await event.get_channel().send("AROOOF!",reply=event.message_id,mentions_reply=True)
                    elif rand <16:
                        await event.get_channel().send("HOOOWL!",reply=event.message_id,mentions_reply=True)
                    elif rand <20:
                        await event.get_channel().send("Aroof",reply=event.message_id,mentions_reply=True)
                    elif rand <24:
                        await event.get_channel().send("*Sniff Sniff Sniff*",reply=event.message_id,mentions_reply=True)
                    elif rand <28:
                        await event.get_channel().send("*Does not care*",reply=event.message_id,mentions_reply=True)
                    elif rand <32:
                        await event.get_channel().send("*I want scritches*",reply=event.message_id,mentions_reply=True)
                    elif rand <36:
                        await event.get_channel().send("*is busy*",reply=event.message_id,mentions_reply=True)
                    elif rand <40:
                        await event.get_channel().send("snuffles",reply=event.message_id,mentions_reply=True)
                    elif rand <44:
                        await event.get_channel().send("snuffles apologetically",reply=event.message_id,mentions_reply=True)
                    elif rand <48:
                        await event.get_channel().send("sits",reply=event.message_id,mentions_reply=True)
                    elif rand <52:
                        await event.get_channel().send("lays down",reply=event.message_id,mentions_reply=True)
                    elif rand <56:
                        await event.get_channel().send("chuffs",reply=event.message_id,mentions_reply=True)
                    elif rand <60:
                        await event.get_channel().send("pants",reply=event.message_id,mentions_reply=True)
                    elif rand <64:
                        await event.get_channel().send("plays dead",reply=event.message_id,mentions_reply=True)
                    elif rand <68:
                        await event.get_channel().send("gives paw",reply=event.message_id,mentions_reply=True)
                    elif rand <72:
                        await event.get_channel().send("rolls over",reply=event.message_id,mentions_reply=True)
                    elif rand <76:
                        await event.get_channel().send("is adorable",reply=event.message_id,mentions_reply=True)
                    elif rand <80:
                        await event.get_channel().send("whimpers",reply=event.message_id,mentions_reply=True)
                    elif rand <84:
                        await event.get_channel().send("licks face",reply=event.message_id,mentions_reply=True)
                    elif rand <88:
                        await event.get_channel().send("*Sits*",reply=event.message_id,mentions_reply=True)
                    elif rand <92:
                        await event.get_channel().send("*is adorable*",reply=event.message_id,mentions_reply=True)
                    elif rand <96:
                        await event.get_channel().send("pants",reply=event.message_id,mentions_reply=True)
                    elif rand <=100:
                        message = await event.get_channel().send("**HOLY SHIT!**",reply=event.message_id,mentions_reply=True)
                        message = await event.get_channel().send("**HOLY SHIT!**",reply=message.id)
                        await event.get_channel().send("**HOLY SHIT!**",reply=message.id)

    @bot.listen(hikari.DMMessageCreateEvent)
    async def on_dm_message(event: hikari.DMMessageCreateEvent):
        if event.is_human and event.content is not None and event.author_id==184524255197659136:
            channel = await bot.rest.fetch_channel(878434694713188362)
            await channel.send(event.content)

    @bot.command()
    @lightbulb.option("dice", "dice to roll", required=True)
    @lightbulb.command("roll", "diceroller")
    @lightbulb.implements(commands.PrefixCommand)
    async def roll(ctx: lightbulb.Context):
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
                        await ctx.respond("Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                        return
                    try:numRolls = int(die[:die.find('d')])
                    except:numRolls = 1
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
                        await ctx.respond("Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.")
                        return
            output = '`'
            for x in rolls:output += str(x) + ', '
            output = output[:-2]
            await ctx.respond("Kethran rolled `" +arg+"` got "+output+"` for a total value of: "+str(sum),reply=True)        
        except:
            await ctx.respond("Error invalid argument: specified dice can only be d2s, d4s, d6s, d8s, d10s, d12s, d20s,  or d100s, or if a constant modifier must be a perfect integer, positive or negative, connexted with `+`, and no spaces.",reply=True)
            return

    @sched.scheduled_job(CronTrigger(day_of_week="sat",hour="1"),id="1")
    async def friday_5() -> None:
        rand = random.randint(1,100)
        if rand <4:
            await bot.rest.create_message(878434694713188362,"Bork!")
        elif rand <8:
            await bot.rest.create_message(878434694713188362,"WOOF!")
        elif rand <12:
            await bot.rest.create_message(878434694713188362,"AROOOF!")
        elif rand <16:
            await bot.rest.create_message(878434694713188362,"HOOOWL!")
        elif rand <20:
            await bot.rest.create_message(878434694713188362,"Aroof")
        elif rand <24:
            await bot.rest.create_message(878434694713188362,"*Sniff Sniff Sniff*")
        elif rand <28:
            await bot.rest.create_message(878434694713188362,"*Does not care*")
        elif rand <32:
            await bot.rest.create_message(878434694713188362,"*I want scritches*")
        elif rand <36:
            await bot.rest.create_message(878434694713188362,"*is busy*")
        elif rand <40:
            await bot.rest.create_message(878434694713188362,"snuffles")
        elif rand <44:
            await bot.rest.create_message(878434694713188362,"snuffles apologetically")
        elif rand <48:
            await bot.rest.create_message(878434694713188362,"sits")
        elif rand <52:
            await bot.rest.create_message(878434694713188362,"lays down")
        elif rand <56:
            await bot.rest.create_message(878434694713188362,"chuffs")
        elif rand <60:
            await bot.rest.create_message(878434694713188362,"pants")
        elif rand <64:
            await bot.rest.create_message(878434694713188362,"plays dead")
        elif rand <68:
            await bot.rest.create_message(878434694713188362,"gives paw")
        elif rand <72:
            await bot.rest.create_message(878434694713188362,"rolls over")
        elif rand <76:
            await bot.rest.create_message(878434694713188362,"is adorable")
        elif rand <80:
            await bot.rest.create_message(878434694713188362,"whimpers")
        elif rand <84:
            await bot.rest.create_message(878434694713188362,"licks face")
        elif rand <88:
            await bot.rest.create_message(878434694713188362,"*Sits*")
        elif rand <92:
            await bot.rest.create_message(878434694713188362,"*is adorable*")
        elif rand <96:
            await bot.rest.create_message(878434694713188362,"pants")
        elif rand <=100:
            message = await bot.rest.create_message(878434694713188362,"**HOLY SHIT!**")
            message = await bot.rest.create_message(878434694713188362,"**HOLY SHIT!**",reply=message.id)
            await bot.rest.create_message(878434694713188362,"**HOLY SHIT!**",reply=message.id) 

    bot.run()
    
if __name__ == "__main__":
    main()
