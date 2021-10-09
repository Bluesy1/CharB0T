import discord
from discord.ext import commands

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

client = MyClient()
client.run('ODk2NDQ3NTgxNDM2MTI5MzIx.YWHP3g.VRn9KHBv5p8-yH2vFNEOzMNiAG0')

bot = commands.Bot(command_prefix='>')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run('ODk2NDQ3NTgxNDM2MTI5MzIx.YWHP3g.VRn9KHBv5p8-yH2vFNEOzMNiAG0')

#Bot stuff


