# coding=utf-8
import json
from datetime import datetime, timedelta

import discord
from discord import Embed, app_commands, Interaction
from discord.ext import commands, tasks
from discord.ext.commands import Cog


class ModSupport(Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # noinspection PyUnresolvedReferences
        self.tree: app_commands = bot.tree

    @tasks.loop(hours=24)
    async def check_modmail_channels(self):
        """Remove stale modmail channels"""
        channels = (await self.bot.fetch_guild(225345178955808768)).channels
        cared = []
        for channel in channels:
            if channel.category.category_id == 942578610336837632 and channel.id != 906578081496584242:
                cared.append(channel)
        for channel in cared:
            # noinspection PyBroadException
            try:
                if channel.history(after=(datetime.now() - timedelta(days=3))) == 0:
                    await channel.send("Deleting now")
                    await channel.delete()
            except:  # pylint: disable=bare-except
                print("Error")

    check_modmail_channels.start()

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and message.channel.type is discord.ChannelType.private:
            await message.channel.send(
                "Hi! If this was an attempt to reach the mod team through modmail, that has been removed, in favor of "
                "mod support, which you can find in <#398949472840712192>")


class Modsupport(app_commands.Group):
    """App commands for mod support"""
    @app_commands.command(name="query", description="queries list of users banned from mod support")
    async def query(self, interaction: Interaction):
        """Modmail blacklist query command"""
        if any(role.id in (225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954) for role in
               interaction.user.roles):
            with open("modmail_blacklist.json", "r", encoding="utf8") as file:
                blacklisted = [f"<@{item}>" for item in json.load(file)["blacklisted"]]
            await interaction.response.send_message(embed=Embed(title="Blacklisted users",
                                                                description="\n".join(blacklisted)))
        else:
            await interaction.response.send_message("You are not authorized to use this command")

    @app_commands.command(name="edit", description="adds or removes a user from the list of users banned from mod"
                                                   " support")
    @app_commands.describe(add="True to add to blacklist, False to remove",
                           user="user to change")
    async def edit(self, interaction: Interaction, add: bool, user: discord.Member):
        """Modmail edit blacklist command"""
        if any(role.id in (225413350874546176, 253752685357039617, 725377514414932030, 338173415527677954) for role in
               interaction.user.roles):
            if add:
                successful = False
                with open("modmail_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id not in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].append(user.id)
                    with open("modmail_blacklist.json", "w", encoding="utf8") as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            else:
                successful = False
                with open("modmail_blacklist.json", "r", encoding="utf8") as file:
                    modmail_blacklist = json.load(file)
                if user.id in modmail_blacklist["blacklisted"]:
                    modmail_blacklist["blacklisted"].remove(user.id)
                    with open("modmail_blacklist.json", "w", encoding="utf8") as file:
                        json.dump(modmail_blacklist, file)
                    successful = True
            if add and successful:
                await interaction.response.send_message(f"<@{user.id}> successfully added to the blacklist")
            elif add and not successful:
                await interaction.response.send_message(
                    f"Error: <@{user.id}> was already on the blacklist or was not able to be added to.")
            elif not add and successful:
                await interaction.response.send_message(f"<@{user.id}> successfully removed from the blacklist")
            elif not add and not successful:
                await interaction.response.send_message(
                    f"<@{user.id}> was not on the blacklist or was not able to be removed from it.")
            else:
                await interaction.response.send_message(
                    "Error: unkown issue occured. If you're seeing this, ping bluesy, something has gone very wrong.")
        else:
            await interaction.response.send_message("You are not authorized to use this command")


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(ModSupport(bot))
