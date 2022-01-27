#pylint: disable=invalid-name
import json
import os
from hikari.intents import Intents
from hikari.presences import Activity, ActivityType

import lightbulb
from lightbulb import commands

def main():
    """Main"""
    if os.name != "nt":
        import uvloop#pylint: disable=import-outside-toplevel
        uvloop.install()

    with open('bottoken.json') as file:
        token = json.load(file)['Token']
    # Instantiate a Bot instance
    bot = lightbulb.BotApp(token=token, prefix="!", help_slash_command=True,
                           owner_ids=[225344348903047168, 363095569515806722], logs={
                               "version": 1,
                               "incremental": True,
                               "loggers": {
                                   "hikari": {"level": "INFO"},
                                   "hikari.ratelimits": {"level": "TRACE_HIKARI"},
                                   "lightbulb": {"level": "INFO"},
                               },}, case_insensitive_prefix_commands=True, intents=Intents.ALL)

    @bot.command()
    @lightbulb.option("module", "module to reload", required=True)
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command("reload", "reloads extensions")
    @lightbulb.implements(commands.PrefixCommand)
    async def reload(ctx) -> None:#pylint: disable=unused-variable
        """Live Module Reloading Command"""
        # Send a message to the channel the command was used in
        bot.reload_extensions("extensions."+ctx.options.module)
        await ctx.respond("Reloaded!")

    @bot.command()
    @lightbulb.option("module", "module to load", required=True)
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command("load", "loads given extensions")
    @lightbulb.implements(commands.PrefixCommand)
    async def load(ctx) -> None:#pylint: disable=unused-variable
        """Live Module Loading Command"""
        # Send a message to the channel the command was used in
        bot.load_extensions("extensions."+ctx.options.module)
        await ctx.respond("Loaded!")

    @bot.command()
    @lightbulb.option("module", "module to unload", required=True)
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command("unload", "unloads given extensions")
    @lightbulb.implements(commands.PrefixCommand)
    async def unload(ctx) -> None:#pylint: disable=unused-variable
        """Live Module Unloading Command"""
        # Send a message to the channel the command was used in
        bot.unload_extensions("extensions."+ctx.options.module)
        await ctx.respond("Unloaded!")

    @bot.command()
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command("ping", "Checks that the bot is alive")
    @lightbulb.implements(commands.PrefixCommand)
    async def ping(ctx):#pylint: disable=unused-variable
        """Ping Command TO Check Bot Is Alive"""
        await ctx.event.message.delete()
        await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")

    bot.load_extensions_from("extensions")
    bot.load_extensions("extensions.__help")

    # Run the bot
    # Note that this is blocking meaning no code after this line will run
    # until the bot is shut off
    bot.run(activity=Activity(name="for scammers", type=ActivityType.WATCHING))

if __name__ == "__main__":
    main()
