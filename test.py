import discord
from discord.ext import commands
import numpy
import pandas
import scipy


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == '>ping':
            await message.channel.send('pong')
        
        if message.content == 

client = MyClient()
client.run('token')

bot = commands.Bot(command_prefix='>')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')
@bot.command()
async def addmod(user):
    await user.send('pong')

bot.run('token')

#Bot stuff

mods = [225344348903047168, 363095569515806722, 138380316095021056, 138380316095021056, 137240557280952321, 146285543146127361, 162833689196101632, 247950431630655488, 244529987510599680]

def addmod(user):
     mods.append(user.id)


