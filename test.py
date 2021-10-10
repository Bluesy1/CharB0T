import discord
from discord.ext import commands
import numpy
import pandas as pd
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

mods = [225344348903047168, 363095569515806722, 138380316095021056, 138380316095021056, 137240557280952321, 146285543146127361, 162833689196101632, 247950431630655488, 244529987510599680]

#RPO_temp = {'RPO_Name': [], 'YT_names': [], 'Discord_ids': []}
RPO_df = pd.DataFrame([[],[],[]], columns=['RPO_Name', 'YT_names', 'Discord_ids'], index = []) #Initializes dataframe for RPO members
@bot.command()
async def addRPO(ctx, RPO_Tag, RPO_Name, YT_Name, Discord_Name):
    if ctx.author.id() in mods: #Checks if command user is a mod
        if RPO_Tag in RPO_df['RPO_Tags'].drop_duplicates: #checks if the RPO already exists
            if YT_Name in RPO_df['YT_names'].drop_duplicates: #Checks if YT name is already on list
                await ctx.channel.send('YT name : ' + YT_Name + ' is already in an RPO.')
            else:
                if ctx.raw_mentions()[0] in RPO_df['Discord_ids']: #Checks if discord account is already in an RPO 
                    await ctx.channel.send('Discord name: ' + Discord_Name + ' is already in an RPO.')
                else: #If the RPO already exists, the YT name and Discord name both aren't in an RPO already, adds them to an existing RPO
                    RPO_df.append([[RPO_Name],[YT_Name],[Discord_Name.id]], columns=['RPO_Name', 'YT_names', 'Discord_ids'], index = [])
    else: #If the command user is not a mod, error out and cancel the command
        await ctx.channel.send(ctx.author.mention + "🚫You are not authorized to use that command.")
