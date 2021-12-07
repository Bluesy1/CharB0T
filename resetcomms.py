import discord
import discord.ext
import discord_slash
bot = discord.Client()

async def on_connect():
    print(await discord_slash.manage_commands.remove_all_commands(406885177281871902, "NDA2ODg1MTc3MjgxODcxOTAy.WmzLWQ.DojjMinMjnm2UVPrDFamnS1p4HA", [225345178955808768]))
bot.on_connect = on_connect

bot.run("NDA2ODg1MTc3MjgxODcxOTAy.WmzLWQ.DojjMinMjnm2UVPrDFamnS1p4HA")