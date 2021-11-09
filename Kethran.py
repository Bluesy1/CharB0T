from discord import client
from discord.ext import commands
import random
import json
import re

from discord.gateway import EventListener

with open("KethranToken.json") as t:
    token = json.load(t)['Token']
regex = r"kethran"
client = commands.Bot(command_prefix='!')
@client.event
async def on_message(ctx):
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

client.run(token)