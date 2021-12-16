from hikari.embeds import Embed
import lightbulb



class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context):
        # Override this method to change the message sent when the help command
        # is run without any arguments.
        await context.respond(f"{self.app.slash_commands}")


    async def send_plugin_help(self, context, plugin):
        # Override this method to change the message sent when the help command
        # argument is the name of a plugin.
        embed = Embed(title=f"Commands in plugin {plugin.name}")
        for command in plugin.all_commands:
            if command is lightbulb.commands.slash.SlashCommand:
                embed.add_field(command.name,command.options,inline=True)
            elif command is lightbulb.commands.slash.SlashSubCommand:
                for subcommand in command.subcommands:
                    if subcommand is lightbulb.commands.slash.SlashSubCommand:
                        embed.add_field(subcommand.name,subcommand.options,inline=True)
                    else:
                        for subsubcommand in subcommand.subcommands:
                            embed.add_field(subsubcommand.name,subsubcommand.options,inline=True)
        await context.respond(embed=embed)

    async def send_command_help(self, context, command):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command.
        embed = Embed(title=f"Commands in plugin {command.name}")
        embed.add_field("Options",command.options, inline=True)
        await context.respond(embed=embed)

    async def send_group_help(self, context, group):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command group.
        embed = Embed(title=f"Commands in group {group.name}")
        for command in group.subcommands:
            if command is lightbulb.commands.slash.SlashSubCommand:
                embed.add_field(command.name,command.options,inline=True)
            else:
                for subcommand in command.subcommands:
                    embed.add_field(subcommand.name,subcommand.options,inline=True)
        await context.respond(embed=embed)

    """async def object_not_found(self, context, obj):
        # Override this method to change the message sent when help is
        # requested for an object that does not exist
        ..."""

def load(bot):
    bot.d.old_help_command = bot.help_command
    bot.help_command = CustomHelp(bot)

def unload(bot):
    bot.help_command = bot.d.old_help_command
    del bot.d.old_help_command